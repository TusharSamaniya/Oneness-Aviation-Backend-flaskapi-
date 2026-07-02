from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    role: str
    is_verified: bool
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
