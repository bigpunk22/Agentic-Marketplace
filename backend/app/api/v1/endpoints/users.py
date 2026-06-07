"""User management endpoints."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_current_user, require_admin
from app.db.base import get_db
from app.models import User

router = APIRouter()


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    avatar_url: str | None
    is_super_admin: bool
    status: str
    created_at: str | None


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user=Depends(get_current_user)):
    return _user_to_response(user)


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    body: UserUpdateRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.full_name is not None:
        user.full_name = body.full_name
    if body.avatar_url is not None:
        user.avatar_url = body.avatar_url
    await db.flush()
    return _user_to_response(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_to_response(user)


def _user_to_response(user: User) -> dict[str, Any]:
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "is_super_admin": user.is_super_admin,
        "status": user.status.value,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
