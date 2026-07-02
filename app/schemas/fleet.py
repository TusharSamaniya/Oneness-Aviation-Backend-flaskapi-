from pydantic import BaseModel
from typing import Optional, List


class AircraftResponse(BaseModel):
    id: int
    slug: str
    category: str
    category_label: str
    name: str
    tagline: Optional[str]
    passengers: int
    range_km: int
    range_nm: int
    speed_kmh: int
    ceiling_ft: Optional[int]
    baggage_kg: Optional[int]
    price_per_hour: int
    price_from_display: Optional[str]
    image: Optional[str]
    images: Optional[List[str]]
    cabin_features: Optional[List[str]]
    ideal_for: Optional[List[str]]
    is_available: bool
    is_popular: bool

    class Config:
        from_attributes = True


class AircraftCreate(BaseModel):
    slug: str
    category: str
    category_label: str
    name: str
    tagline: Optional[str] = None
    passengers: int
    range_km: int
    range_nm: int
    speed_kmh: int
    ceiling_ft: Optional[int] = None
    baggage_kg: Optional[int] = None
    price_per_hour: int
    price_from_display: Optional[str] = None
    image: Optional[str] = None
    cabin_features: List[str] = []
    ideal_for: List[str] = []
    is_popular: bool = False


class AircraftUpdate(BaseModel):
    name: Optional[str] = None
    tagline: Optional[str] = None
    passengers: Optional[int] = None
    price_per_hour: Optional[int] = None
    price_from_display: Optional[str] = None
    cabin_features: Optional[List[str]] = None
    is_available: Optional[bool] = None
    is_popular: Optional[bool] = None
    is_active: Optional[bool] = None


# ── Cost estimator ────────────────────────────────────────────────────────────
class EstimateRequest(BaseModel):
    from_code: str   # e.g. BOM
    to_code: str     # e.g. DEL
    aircraft_tier: str  # light-jet | midsize-jet | heavy-jet | turboprop
    journey_type: str = "One Way"   # One Way | Round Trip


class PriceBreakdown(BaseModel):
    base: int
    landing: int
    handling: int
    taxes: int
    total: int
    total_with_return: Optional[int]


class EstimateResponse(BaseModel):
    from_city: str
    to_city: str
    distance_km: int
    flight_time_hrs: float
    aircraft_tier: str
    breakdown: PriceBreakdown
    note: str = "Estimate only. Final price depends on exact routing, dates, and aircraft availability."
