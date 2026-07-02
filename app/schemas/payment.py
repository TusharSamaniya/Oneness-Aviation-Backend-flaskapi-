from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.payment import PaymentStatus, PaymentPurpose


class CreateOrderRequest(BaseModel):
    amount: int           # in INR paise
    purpose: PaymentPurpose
    description: Optional[str] = None


class CreateOrderResponse(BaseModel):
    razorpay_order_id: str
    amount: int
    currency: str
    razorpay_key_id: str


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentResponse(BaseModel):
    id: int
    razorpay_order_id: Optional[str]
    razorpay_payment_id: Optional[str]
    amount: int
    currency: str
    purpose: PaymentPurpose
    status: PaymentStatus
    description: Optional[str]
    invoice_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
