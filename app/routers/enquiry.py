from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database import get_db
from app.models.enquiry import Enquiry, CharterRequest
from app.models.user import User
from app.schemas.enquiry import (
    ContactEnquiryCreate, EnquiryResponse,
    CharterRequestCreate, CharterRequestResponse,
)
from app.middleware.dependencies import get_current_user_optional
from app.services.email_service import (
    send_enquiry_confirmation,
    send_admin_enquiry_notification,
    send_charter_confirmation,
)

router = APIRouter(prefix="/enquiries", tags=["Enquiries"])


@router.post("/contact", response_model=EnquiryResponse, status_code=201)
async def submit_contact_enquiry(
    data: ContactEnquiryCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    enquiry = Enquiry(
        user_id=current_user.id if current_user else None,
        **data.model_dump(),
    )
    db.add(enquiry)
    await db.flush()
    await db.refresh(enquiry)

    # Emails in background — don't make user wait
    background_tasks.add_task(send_enquiry_confirmation, data.name, data.email, data.enquiry_type)
    background_tasks.add_task(
        send_admin_enquiry_notification,
        data.name, data.email, data.phone, data.enquiry_type, data.message or "",
    )
    return enquiry


@router.post("/charter", response_model=CharterRequestResponse, status_code=201)
async def submit_charter_request(
    data: CharterRequestCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    charter = CharterRequest(
        user_id=current_user.id if current_user else None,
        **data.model_dump(),
    )
    db.add(charter)
    await db.flush()
    await db.refresh(charter)

    background_tasks.add_task(
        send_charter_confirmation,
        data.name, data.email,
        data.from_city or "TBD",
        data.to_city or "TBD",
        str(data.departure_date) if data.departure_date else "TBD",
    )
    return charter


@router.get("/my", response_model=dict)
async def my_enquiries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    if not current_user:
        return {"enquiries": [], "charter_requests": []}

    enq_result = await db.execute(
        select(Enquiry).where(Enquiry.user_id == current_user.id).order_by(Enquiry.created_at.desc())
    )
    charter_result = await db.execute(
        select(CharterRequest).where(CharterRequest.user_id == current_user.id).order_by(CharterRequest.created_at.desc())
    )
    return {
        "enquiries": enq_result.scalars().all(),
        "charter_requests": charter_result.scalars().all(),
    }
