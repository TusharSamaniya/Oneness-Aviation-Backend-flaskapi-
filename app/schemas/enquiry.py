from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional
from app.models.enquiry import EnquiryStatus, JourneyType


# ── Contact Enquiry ───────────────────────────────────────────────────────────
class ContactEnquiryCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr
    enquiry_type: str
    departure: Optional[str] = None
    destination: Optional[str] = None
    travel_date: Optional[date] = None
    passengers: Optional[str] = None
    message: Optional[str] = None


class EnquiryResponse(BaseModel):
    id: int
    name: str
    email: str
    enquiry_type: str
    status: EnquiryStatus
    created_at: datetime

    class Config:
        from_attributes = True


class EnquiryDetail(EnquiryResponse):
    phone: str
    departure: Optional[str]
    destination: Optional[str]
    travel_date: Optional[date]
    passengers: Optional[str]
    message: Optional[str]
    admin_notes: Optional[str]
    assigned_to: Optional[str]
    updated_at: datetime


# ── Charter Request ───────────────────────────────────────────────────────────
class CharterRequestCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    service: Optional[str] = None
    journey_type: JourneyType = JourneyType.one_way
    from_city: Optional[str] = None
    to_city: Optional[str] = None
    departure_date: Optional[date] = None
    return_date: Optional[date] = None
    passengers: Optional[str] = None
    aircraft_preference: Optional[str] = None
    message: Optional[str] = None


class CharterRequestResponse(BaseModel):
    id: int
    name: str
    email: str
    service: Optional[str]
    journey_type: JourneyType
    from_city: Optional[str]
    to_city: Optional[str]
    status: EnquiryStatus
    created_at: datetime

    class Config:
        from_attributes = True


# ── Admin update ──────────────────────────────────────────────────────────────
class EnquiryStatusUpdate(BaseModel):
    status: EnquiryStatus
    admin_notes: Optional[str] = None
    assigned_to: Optional[str] = None
