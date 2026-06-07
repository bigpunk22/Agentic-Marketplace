"""Shared API dependencies — avoids circular imports between endpoints and models."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status

from app.db.base import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    get_current_user,
)


def require_admin_dep(user=Depends(get_current_user)):
    """Require super admin access."""
    if not user.is_super_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# Re-export security functions for convenience
__all__ = [
    "get_db",
    "get_current_user",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "hash_password",
    "verify_password",
    "require_admin_dep",
]
