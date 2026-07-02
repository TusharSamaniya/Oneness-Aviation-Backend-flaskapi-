from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List
from app.models.membership import MembershipTier, MembershipStatus


class MembershipPlanResponse(BaseModel):
    id: int
    tier: MembershipTier
    tagline: str
    annual_fee: int
    annual_fee_display: str
    flight_credit: int
    flight_credit_display: str
    discount_pct: int
    color: str
    features: List[str]
    not_included: List[str]
    is_popular: bool

    class Config:
        from_attributes = True


class MembershipResponse(BaseModel):
    id: int
    tier: MembershipTier
    status: MembershipStatus
    start_date: Optional[date]
    end_date: Optional[date]
    flight_credit_balance: int
    card_number: Optional[str]

    class Config:
        from_attributes = True


class MembershipPurchaseRequest(BaseModel):
    tier: MembershipTier


class MembershipUpgradeRequest(BaseModel):
    new_tier: MembershipTier
