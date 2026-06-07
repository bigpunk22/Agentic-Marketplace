"""Auth dependencies for FastAPI endpoints."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_current_user
from app.db.base import get_db
from app.models import User, WorkspaceMember, MemberRole


async def get_current_member(
    workspace_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceMember:
    """Get the current user's membership in a specific workspace."""
    if user.is_super_admin:
        # Super admins bypass membership check
        return WorkspaceMember(
            workspace_id=workspace_id,
            user_id=str(user.id),
            role=MemberRole.ADMIN,
        )

    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == str(user.id),
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace",
        )
    return member


def require_workspace_role(*roles: str):
    """Dependency factory that requires specific workspace role."""
    async def checker(
        workspace_id: str,
        member: WorkspaceMember = Depends(lambda: None),  # Will be overridden
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> WorkspaceMember:
        if user.is_super_admin:
            return WorkspaceMember(
                workspace_id=workspace_id,
                user_id=str(user.id),
                role=MemberRole.ADMIN,
            )

        result = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == str(user.id),
                WorkspaceMember.role.in_(roles),
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {', '.join(roles)}",
            )
        return member

    return checker
