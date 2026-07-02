"""
SQLAlchemy ORM models — each class maps to a database table.
Import all here so Alembic can detect them during migrations.
"""
from app.models.user import User
from app.models.enquiry import Enquiry, CharterRequest
from app.models.aircraft import Aircraft, AircraftCategory, AirportDistance
from app.models.membership import Membership, MembershipPlan
from app.models.payment import Payment
from app.models.blog import BlogPost, FAQ, Testimonial

__all__ = [
    "User",
    "Enquiry",
    "CharterRequest",
    "Aircraft",
    "AircraftCategory",
    "AirportDistance",
    "Membership",
    "MembershipPlan",
    "Payment",
    "BlogPost",
    "FAQ",
    "Testimonial",
]
