"""Security utilities — JWT, password hashing, RBAC."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.db.base import get_db

if TYPE_CHECKING:
    from app.models import User, WorkspaceMember, MemberRole

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


# ── Password Hashing ──────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Tokens ────────────────────────────────────────────

def create_access_token(user_id: str, tenant_id: str | None = None, **extra: Any) -> str:
    payload = {
        "sub": str(user_id),
        "type": "access",
        "tenant_id": str(tenant_id) if tenant_id else None,
        **extra,
        "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# ── Auth Dependencies ─────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    from app.models import User  # Lazy import to avoid circular dependency

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or user.status == "suspended":
        raise HTTPException(status_code=401, detail="User not found or suspended")

    return user


async def get_current_active_user(
    user=Depends(get_current_user),
):
    if user.status != "active":
        raise HTTPException(status_code=403, detail="Account not activated")
    return user


# ── RBAC ──────────────────────────────────────────────────

def require_role(*roles):
    """Dependency factory that requires the user to have one of the specified roles."""
    from app.models import MemberRole, WorkspaceMember

    async def role_checker(
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        if user.is_super_admin:
            return user

        result = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.user_id == user.id,
                WorkspaceMember.role.in_([r.value for r in roles]),
            )
        )
        membership = result.scalar_one_or_none()
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {', '.join(r.value for r in roles)}",
            )
        return user

    return role_checker


def require_admin(user=Depends(get_current_user)):
    if not user.is_super_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ── Permission Helpers ────────────────────────────────────

ROLE_PERMISSIONS = {
    "admin": {
        "view_dashboard", "execute_workflows", "create_workflows", "delete_workflows",
        "view_analytics", "export_reports", "manage_users", "assign_roles",
        "manage_billing", "manage_api_keys", "configure_sso", "manage_branding",
        "view_audit_logs",
    },
    "operator": {
        "view_dashboard", "execute_workflows", "create_workflows",
        "view_analytics", "export_reports",
    },
    "analyst": {
        "view_dashboard", "view_analytics", "export_reports",
    },
    "billing_manager": {
        "view_dashboard", "view_analytics", "export_reports", "manage_billing",
    },
    "auditor": {
        "view_dashboard", "view_analytics", "export_reports", "view_audit_logs",
    },
}


def has_permission(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
