import enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20))
    hashed_password: Mapped[str] = mapped_column(Text)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.user)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    refresh_token: Mapped[str | None] = mapped_column(Text)
    reset_token: Mapped[str | None] = mapped_column(Text)
    reset_token_expires: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    enquiries: Mapped[list["Enquiry"]] = relationship("Enquiry", back_populates="user", lazy="selectin")  # noqa: F821
    charter_requests: Mapped[list["CharterRequest"]] = relationship("CharterRequest", back_populates="user", lazy="selectin")  # noqa: F821
    membership: Mapped["Membership | None"] = relationship("Membership", back_populates="user", uselist=False, lazy="selectin")  # noqa: F821
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="user", lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
