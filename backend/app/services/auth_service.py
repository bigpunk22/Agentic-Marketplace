"""Authentication service — business logic."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.models import User, UserStatus


class AuthService:
    """Handles authentication business logic."""

    @staticmethod
    async def register(
        db: AsyncSession,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> tuple[User, str, str]:
        """Register a new user. Returns (user, access_token, refresh_token)."""
        # Check existing
        existing = await db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise ValueError("Email already registered")

        user = User(
            id=str(uuid4()),
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            status=UserStatus.ACTIVE,
        )
        db.add(user)
        await db.flush()

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return user, access_token, refresh_token

    @staticmethod
    async def authenticate(
        db: AsyncSession,
        email: str,
        password: str,
    ) -> tuple[User, str, str]:
        """Authenticate user credentials. Returns (user, access_token, refresh_token)."""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not user.password_hash:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        if user.status == UserStatus.SUSPENDED:
            raise ValueError("Account suspended")

        user.last_login_at = datetime.utcnow()
        await db.flush()

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return user, access_token, refresh_token

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
