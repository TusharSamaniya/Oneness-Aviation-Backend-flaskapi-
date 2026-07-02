import hashlib
import hmac
import json
import razorpay
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.payment import Payment, PaymentStatus, PaymentPurpose
from app.schemas.payment import CreateOrderRequest, CreateOrderResponse, VerifyPaymentRequest

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


async def create_razorpay_order(
    db: AsyncSession,
    user_id: int,
    req: CreateOrderRequest,
) -> CreateOrderResponse:
    try:
        order = client.order.create({
            "amount": req.amount,
            "currency": "INR",
            "notes": {"purpose": req.purpose, "user_id": str(user_id)},
        })
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Razorpay order creation failed: {str(e)}")

    payment = Payment(
        user_id=user_id,
        razorpay_order_id=order["id"],
        amount=req.amount,
        currency="INR",
        purpose=req.purpose,
        description=req.description,
        status=PaymentStatus.created,
    )
    db.add(payment)

    return CreateOrderResponse(
        razorpay_order_id=order["id"],
        amount=req.amount,
        currency="INR",
        razorpay_key_id=settings.RAZORPAY_KEY_ID,
    )


async def verify_and_capture_payment(
    db: AsyncSession,
    req: VerifyPaymentRequest,
) -> Payment:
    # Verify Razorpay signature — NEVER trust the frontend
    msg = f"{req.razorpay_order_id}|{req.razorpay_payment_id}".encode()
    generated_sig = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(), msg, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(generated_sig, req.razorpay_signature):
        raise HTTPException(status_code=400, detail="Payment signature verification failed")

    result = await db.execute(
        select(Payment).where(Payment.razorpay_order_id == req.razorpay_order_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment order not found")

    payment.razorpay_payment_id = req.razorpay_payment_id
    payment.razorpay_signature = req.razorpay_signature
    payment.status = PaymentStatus.captured
    db.add(payment)
    return payment


async def handle_razorpay_webhook(payload: dict, signature: str) -> None:
    """Verify webhook signature and handle Razorpay events."""
    body = json.dumps(payload, separators=(",", ":")).encode()
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    # Extend here: handle payment.captured, payment.failed, refund.created etc.
    event = payload.get("event", "")
    if event == "payment.failed":
        order_id = payload.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
        # Could update payment status to failed here if needed


async def get_user_payments(db: AsyncSession, user_id: int) -> list[Payment]:
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
    )
    return result.scalars().all()
