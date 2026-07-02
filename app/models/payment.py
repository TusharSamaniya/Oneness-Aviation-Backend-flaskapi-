import enum
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


class PaymentStatus(str, enum.Enum):
    created = "created"
    captured = "captured"
    failed = "failed"
    refunded = "refunded"


class PaymentPurpose(str, enum.Enum):
    membership = "membership"
    charter = "charter"
    other = "other"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Razorpay fields
    razorpay_order_id: Mapped[str | None] = mapped_column(String(60), unique=True, index=True)
    razorpay_payment_id: Mapped[str | None] = mapped_column(String(60), unique=True)
    razorpay_signature: Mapped[str | None] = mapped_column(Text)

    # Amount in INR paise (Razorpay standard)
    amount: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(5), default="INR")

    purpose: Mapped[PaymentPurpose] = mapped_column(Enum(PaymentPurpose))
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.created)
    description: Mapped[str | None] = mapped_column(Text)
    invoice_url: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="payments")  # noqa: F821
