from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base


class AircraftCategory(Base):
    __tablename__ = "aircraft_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(80))
    icon: Mapped[str] = mapped_column(String(10), default="✈")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class Aircraft(Base):
    __tablename__ = "aircraft"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(60), index=True)   # matches AircraftCategory.slug
    category_label: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(120))
    tagline: Mapped[str | None] = mapped_column(Text)

    # Specs
    passengers: Mapped[int] = mapped_column(Integer)
    range_km: Mapped[int] = mapped_column(Integer)
    range_nm: Mapped[int] = mapped_column(Integer)
    speed_kmh: Mapped[int] = mapped_column(Integer)
    ceiling_ft: Mapped[int | None] = mapped_column(Integer)
    baggage_kg: Mapped[int | None] = mapped_column(Integer)

    # Pricing
    price_per_hour: Mapped[int] = mapped_column(Integer)   # in INR
    price_from_display: Mapped[str | None] = mapped_column(String(30))  # e.g. "₹2.2L / hr"

    # Media (stored as JSON arrays)
    image: Mapped[str | None] = mapped_column(Text)
    images: Mapped[list | None] = mapped_column(JSON, default=list)

    # Features (stored as JSON arrays)
    cabin_features: Mapped[list | None] = mapped_column(JSON, default=list)
    ideal_for: Mapped[list | None] = mapped_column(JSON, default=list)

    # Status
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AirportDistance(Base):
    """Distance lookup table for the flight cost estimator."""
    __tablename__ = "airport_distances"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_code: Mapped[str] = mapped_column(String(6), index=True)   # e.g. BOM
    to_code: Mapped[str] = mapped_column(String(6), index=True)     # e.g. DEL
    from_city: Mapped[str] = mapped_column(String(60))
    to_city: Mapped[str] = mapped_column(String(60))
    distance_km: Mapped[int] = mapped_column(Integer)
    is_international: Mapped[bool] = mapped_column(Boolean, default=False)
