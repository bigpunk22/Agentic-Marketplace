"""Authentication endpoints — register, login, logout, refresh, OAuth, MFA."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.db.base import get_db
from app.models import User, UserStatus

settings = get_settings()
router = APIRouter()


# ── Request/Response Schemas ──────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict[str, Any]


class MessageResponse(BaseModel):
    message: str


# ── Endpoints ─────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    # Check if user exists
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "user_type": user.user_type.value if user.user_type else None,
            "is_super_admin": user.is_super_admin,
        },
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and receive JWT tokens."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.status == UserStatus.SUSPENDED:
        raise HTTPException(status_code=403, detail="Account suspended")

    user.last_login_at = datetime.utcnow()
    await db.flush()

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "user_type": user.user_type.value if user.user_type else None,
            "is_super_admin": user.is_super_admin,
        },
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: dict[str, str]):
    """Refresh access token using a valid refresh token."""
    token = body.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="Refresh token required")

    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload["sub"]
    access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user={"id": user_id},
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(user=Depends(get_current_user)):
    """Logout (client should discard tokens)."""
    # In a more advanced setup, add tokens to a blocklist in Redis
    return MessageResponse(message="Logged out successfully")


@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    """Get current authenticated user profile."""
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "user_type": user.user_type.value if user.user_type else None,
        "is_super_admin": user.is_super_admin,
        "mfa_enabled": user.mfa_enabled,
        "status": user.status.value,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.post("/magic-link", response_model=MessageResponse)
async def send_magic_link(body: dict[str, str], db: AsyncSession = Depends(get_db)):
    """Send a magic link email for passwordless login."""
    email = body.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        # Generate magic link token and send email
        # Implementation depends on email service
        pass

    # Always return success to prevent email enumeration
    return MessageResponse(message="If the email exists, a magic link has been sent")
