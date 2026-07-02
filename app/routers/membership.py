from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date, timedelta
from typing import List
import secrets

from app.database import get_db
from app.models.membership import Membership, MembershipPlan, MembershipStatus, MembershipTier
from app.models.payment import Payment, PaymentStatus, PaymentPurpose
from app.models.user import User
from app.schemas.membership import (
    MembershipPlanResponse, MembershipResponse, MembershipPurchaseRequest,
)
from app.schemas.payment import CreateOrderRequest, CreateOrderResponse, VerifyPaymentRequest
from app.middleware.dependencies import get_current_user
from app.services.payment_service import create_razorpay_order, verify_and_capture_payment
from app.services.email_service import send_membership_welcome

router = APIRouter(prefix="/memberships", tags=["Membership"])


@router.get("/plans", response_model=List[MembershipPlanResponse])
async def list_plans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MembershipPlan).where(MembershipPlan.is_active == True)  # noqa: E712
    )
    return result.scalars().all()


@router.get("/my", response_model=MembershipResponse)
async def my_membership(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Membership).where(Membership.user_id == current_user.id)
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="No active membership found")
    return membership


@router.post("/purchase/create-order", response_model=CreateOrderResponse)
async def purchase_membership_create_order(
    req: MembershipPurchaseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Fetch plan pricing from DB
    result = await db.execute(
        select(MembershipPlan).where(MembershipPlan.tier == req.tier)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Membership plan not found")

    order_req = CreateOrderRequest(
        amount=plan.annual_fee,
        purpose=PaymentPurpose.membership,
        description=f"Oneness {plan.tier.capitalize()} Membership — Annual",
    )
    return await create_razorpay_order(db, current_user.id, order_req)


@router.post("/purchase/verify")
async def purchase_membership_verify(
    req: VerifyPaymentRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await verify_and_capture_payment(db, req)

    # Fetch plan to get tier
    plan_result = await db.execute(
        select(MembershipPlan).where(
            MembershipPlan.annual_fee == payment.amount
        )
    )
    plan = plan_result.scalar_one_or_none()
    tier = plan.tier if plan else MembershipTier.silver

    # Create or update membership
    m_result = await db.execute(select(Membership).where(Membership.user_id == current_user.id))
    membership = m_result.scalar_one_or_none()

    today = date.today()
    plan_credit = plan.flight_credit if plan else 0
    plan_credit_display = plan.flight_credit_display if plan else "₹0"

    if membership:
        membership.tier = tier
        membership.status = MembershipStatus.active
        membership.start_date = today
        membership.end_date = today + timedelta(days=365)
        membership.flight_credit_balance = plan_credit
    else:
        membership = Membership(
            user_id=current_user.id,
            tier=tier,
            status=MembershipStatus.active,
            start_date=today,
            end_date=today + timedelta(days=365),
            flight_credit_balance=plan_credit,
            card_number=f"•••• {secrets.token_hex(2).upper()[:4]}",
        )
        db.add(membership)

    background_tasks.add_task(
        send_membership_welcome,
        current_user.name,
        current_user.email,
        tier,
        (today + timedelta(days=365)).strftime("%d %B %Y"),
        plan_credit_display,
    )
    return {"message": f"Membership activated", "tier": tier, "end_date": str(today + timedelta(days=365))}
