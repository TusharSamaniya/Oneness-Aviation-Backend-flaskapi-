from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    RefreshRequest, ForgotPasswordRequest, ResetPasswordRequest, MessageResponse,
)
from app.services import auth_service
from app.services.email_service import send_password_reset
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=MessageResponse, status_code=201)
async def register(
    data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.register_user(db, data)
    # Send welcome/verification email in background
    background_tasks.add_task(
        send_password_reset,  # swap with send_verification_email when implemented
        user.name, user.email,
        f"{settings.FRONTEND_URL}/account/verify",
    )
    return {"message": "Account created. Please check your email to verify your account."}


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.authenticate_user(db, data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.refresh_access_token(db, data.refresh_token)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    token = await auth_service.initiate_password_reset(db, data.email)
    if token:
        reset_link = f"{settings.FRONTEND_URL}/account/reset-password?token={token}"
        user = await auth_service.get_user_by_email(db, data.email)
        background_tasks.add_task(send_password_reset, user.name, data.email, reset_link)
    # Always return 200 — don't reveal whether the email exists
    return {"message": "If an account with this email exists, a reset link has been sent."}


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    await auth_service.reset_password(db, data.token, data.new_password)
    return {"message": "Password reset successfully. You can now log in."}
