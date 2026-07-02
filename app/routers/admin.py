from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional, List
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.models.user import User
from app.models.enquiry import Enquiry, CharterRequest, EnquiryStatus
from app.models.aircraft import Aircraft
from app.models.blog import BlogPost, FAQ, Testimonial
from app.models.membership import Membership, MembershipStatus
from app.models.payment import Payment, PaymentStatus
from app.schemas.enquiry import EnquiryDetail, CharterRequestResponse, EnquiryStatusUpdate
from app.schemas.fleet import AircraftResponse, AircraftCreate, AircraftUpdate
from app.schemas.blog import (
    BlogPostResponse, BlogPostCreate, BlogPostUpdate,
    FAQResponse, TestimonialResponse,
)
from app.services.fleet_service import create_aircraft, update_aircraft
from app.middleware.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Dashboard ─────────────────────────────────────────────────────────────────
@router.get("/dashboard/stats")
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    today = datetime.now(timezone.utc)
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)

    total_enquiries  = (await db.execute(select(func.count(Enquiry.id)))).scalar_one()
    new_today        = (await db.execute(select(func.count(Enquiry.id)).where(Enquiry.created_at >= today_start))).scalar_one()
    total_users      = (await db.execute(select(func.count(User.id)))).scalar_one()
    active_members   = (await db.execute(select(func.count(Membership.id)).where(Membership.status == MembershipStatus.active))).scalar_one()
    total_revenue    = (await db.execute(select(func.sum(Payment.amount)).where(Payment.status == PaymentStatus.captured))).scalar_one() or 0
    new_charter_reqs = (await db.execute(select(func.count(CharterRequest.id)).where(CharterRequest.status == EnquiryStatus.new))).scalar_one()

    return {
        "total_enquiries":     total_enquiries,
        "new_today":           new_today,
        "total_users":         total_users,
        "active_members":      active_members,
        "total_revenue_paise": total_revenue,
        "new_charter_requests": new_charter_reqs,
    }


# ── Enquiries ─────────────────────────────────────────────────────────────────
@router.get("/enquiries")
async def list_all_enquiries(
    status: Optional[EnquiryStatus] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = select(Enquiry)
    if status:
        q = q.where(Enquiry.status == status)
    if search:
        q = q.where(Enquiry.name.ilike(f"%{search}%") | Enquiry.email.ilike(f"%{search}%"))
    q = q.order_by(Enquiry.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.patch("/enquiries/{enquiry_id}/status")
async def update_enquiry_status(
    enquiry_id: int,
    data: EnquiryStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(Enquiry).where(Enquiry.id == enquiry_id))
    enquiry = result.scalar_one_or_none()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    enquiry.status = data.status
    if data.admin_notes:
        enquiry.admin_notes = data.admin_notes
    if data.assigned_to:
        enquiry.assigned_to = data.assigned_to
    db.add(enquiry)
    return {"message": f"Enquiry #{enquiry_id} updated to {data.status}"}


@router.get("/charter-requests")
async def list_charter_requests(
    status: Optional[EnquiryStatus] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = select(CharterRequest)
    if status:
        q = q.where(CharterRequest.status == status)
    q = q.order_by(CharterRequest.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.patch("/charter-requests/{req_id}/status")
async def update_charter_status(
    req_id: int,
    data: EnquiryStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(CharterRequest).where(CharterRequest.id == req_id))
    charter = result.scalar_one_or_none()
    if not charter:
        raise HTTPException(status_code=404, detail="Charter request not found")
    charter.status = data.status
    if data.admin_notes:
        charter.admin_notes = data.admin_notes
    db.add(charter)
    return {"message": f"Charter request #{req_id} updated"}


# ── Fleet Management ──────────────────────────────────────────────────────────
@router.post("/fleet", response_model=AircraftResponse, status_code=201)
async def add_aircraft(
    data: AircraftCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await create_aircraft(db, data)


@router.put("/fleet/{aircraft_id}", response_model=AircraftResponse)
async def edit_aircraft(
    aircraft_id: int,
    data: AircraftUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await update_aircraft(db, aircraft_id, data)


@router.patch("/fleet/{aircraft_id}/availability")
async def toggle_availability(
    aircraft_id: int,
    is_available: bool,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(Aircraft).where(Aircraft.id == aircraft_id))
    aircraft = result.scalar_one_or_none()
    if not aircraft:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    aircraft.is_available = is_available
    db.add(aircraft)
    return {"message": f"Aircraft availability set to {is_available}"}


@router.delete("/fleet/{aircraft_id}")
async def delete_aircraft(
    aircraft_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(Aircraft).where(Aircraft.id == aircraft_id))
    aircraft = result.scalar_one_or_none()
    if not aircraft:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    aircraft.is_active = False  # Soft delete
    db.add(aircraft)
    return {"message": "Aircraft removed from fleet"}


# ── Blog Management ───────────────────────────────────────────────────────────
@router.post("/blog", response_model=BlogPostResponse, status_code=201)
async def create_post(
    data: BlogPostCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    post = BlogPost(**data.model_dump())
    db.add(post)
    await db.flush()
    await db.refresh(post)
    return post


@router.put("/blog/{post_id}", response_model=BlogPostResponse)
async def update_post(
    post_id: int,
    data: BlogPostUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(BlogPost).where(BlogPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(post, field, value)
    db.add(post)
    return post


@router.patch("/blog/{post_id}/publish")
async def toggle_publish(
    post_id: int,
    publish: bool,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(BlogPost).where(BlogPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    post.is_published = publish
    if publish and not post.published_at:
        post.published_at = datetime.now(timezone.utc)
    db.add(post)
    return {"message": f"Post {'published' if publish else 'unpublished'}"}


@router.delete("/blog/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(BlogPost).where(BlogPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await db.delete(post)
    return {"message": "Post deleted"}


# ── Users ─────────────────────────────────────────────────────────────────────
@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = select(User)
    if search:
        q = q.where(User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    q = q.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()
