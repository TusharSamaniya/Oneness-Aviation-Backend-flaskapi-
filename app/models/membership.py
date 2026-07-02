import enum
from datetime import datetime, date
from sqlalchemy import String, Text, Integer, Boolean, Float, DateTime, Date, ForeignKey, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


class MembershipTier(str, enum.Enum):
    silver = "silver"
    gold = "gold"
    platinum = "platinum"


class MembershipStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"
    pending = "pending"   # payment not yet confirmed


class MembershipPlan(Base):
    """Pricing / feature config per tier — admin can update prices without code changes."""
    __tablename__ = "membership_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    tier: Mapped[MembershipTier] = mapped_column(Enum(MembershipTier), unique=True)
    tagline: Mapped[str] = mapped_column(Text)
    annual_fee: Mapped[int] = mapped_column(Integer)         # in INR paise (for Razorpay)
    annual_fee_display: Mapped[str] = mapped_column(String(30))  # e.g. ₹2,50,000
    flight_credit: Mapped[int] = mapped_column(Integer)      # in INR paise
    flight_credit_display: Mapped[str] = mapped_column(String(30))
    discount_pct: Mapped[int] = mapped_column(Integer)       # e.g. 5, 10, 15
    color: Mapped[str] = mapped_column(String(10))
    features: Mapped[list] = mapped_column(JSON, default=list)
    not_included: Mapped[list] = mapped_column(JSON, default=list)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Membership(Base):
    """One membership record per user."""
    __tablename__ = "memberships"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    tier: Mapped[MembershipTier] = mapped_column(Enum(MembershipTier))
    status: Mapped[MembershipStatus] = mapped_column(Enum(MembershipStatus), default=MembershipStatus.pending)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    flight_credit_balance: Mapped[int] = mapped_column(Integer, default=0)  # in INR paise
    card_number: Mapped[str | None] = mapped_column(String(20))   # e.g. •••• 4829

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="membership")  # noqa: F821
