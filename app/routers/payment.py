from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.payment import (
    CreateOrderRequest, CreateOrderResponse,
    VerifyPaymentRequest, PaymentResponse,
)
from app.middleware.dependencies import get_current_user
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create-order", response_model=CreateOrderResponse)
async def create_order(
    req: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await payment_service.create_razorpay_order(db, current_user.id, req)


@router.post("/verify")
async def verify_payment(
    req: VerifyPaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await payment_service.verify_and_capture_payment(db, req)
    return {"message": "Payment verified successfully", "payment_id": payment.id}


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    """Razorpay calls this URL automatically after payment events."""
    payload = await request.json()
    await payment_service.handle_razorpay_webhook(payload, x_razorpay_signature)
    return {"status": "ok"}


@router.get("/history", response_model=List[PaymentResponse])
async def payment_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await payment_service.get_user_payments(db, current_user.id)
