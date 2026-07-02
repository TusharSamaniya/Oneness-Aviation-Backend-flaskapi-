import enum
from datetime import datetime, date
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Enum, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


class EnquiryStatus(str, enum.Enum):
    new = "new"
    in_review = "in_review"
    quoted = "quoted"
    confirmed = "confirmed"
    closed = "closed"


class JourneyType(str, enum.Enum):
    one_way = "One Way"
    round_trip = "Round Trip"
    multi_city = "Multi-City"


class Enquiry(Base):
    """General contact/enquiry form submissions (from ContactPage.jsx)."""
    __tablename__ = "enquiries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Contact details
    name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(255), index=True)
    enquiry_type: Mapped[str] = mapped_column(String(80))

    # Flight details (optional)
    departure: Mapped[str | None] = mapped_column(String(120))
    destination: Mapped[str | None] = mapped_column(String(120))
    travel_date: Mapped[date | None] = mapped_column(Date)
    passengers: Mapped[str | None] = mapped_column(String(10))
    message: Mapped[str | None] = mapped_column(Text)

    # Admin fields
    status: Mapped[EnquiryStatus] = mapped_column(Enum(EnquiryStatus), default=EnquiryStatus.new)
    admin_notes: Mapped[str | None] = mapped_column(Text)
    assigned_to: Mapped[str | None] = mapped_column(String(120))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User | None"] = relationship("User", back_populates="enquiries")  # noqa: F821


class CharterRequest(Base):
    """Full charter request form submissions (from RequestCharter.jsx)."""
    __tablename__ = "charter_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Contact
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), index=True)
    phone: Mapped[str] = mapped_column(String(20))

    # Flight details
    service: Mapped[str | None] = mapped_column(String(80))
    journey_type: Mapped[JourneyType] = mapped_column(Enum(JourneyType), default=JourneyType.one_way)
    from_city: Mapped[str | None] = mapped_column(String(120))
    to_city: Mapped[str | None] = mapped_column(String(120))
    departure_date: Mapped[date | None] = mapped_column(Date)
    return_date: Mapped[date | None] = mapped_column(Date)
    passengers: Mapped[str | None] = mapped_column(String(10))
    aircraft_preference: Mapped[str | None] = mapped_column(String(120))
    message: Mapped[str | None] = mapped_column(Text)

    # Admin
    status: Mapped[EnquiryStatus] = mapped_column(Enum(EnquiryStatus), default=EnquiryStatus.new)
    admin_notes: Mapped[str | None] = mapped_column(Text)
    assigned_to: Mapped[str | None] = mapped_column(String(120))
    quoted_amount: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User | None"] = relationship("User", back_populates="charter_requests")  # noqa: F821
