"""Workspace management endpoints — list, create, invite, remove members."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_current_user
from app.db.base import get_db

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────

class CreateWorkspaceRequest(BaseModel):
    name: str
    description: str | None = None


class InviteMemberRequest(BaseModel):
    email: str


class WorkspaceResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: str | None
    settings: dict
    created_at: str | None


class WorkspaceMemberResponse(BaseModel):
    id: str
    user_id: str
    role: str
    joined_at: str | None


# ── Endpoints ─────────────────────────────────────────────

@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List workspaces for the current user (via their tenant memberships)."""
    from app.models import WorkspaceMember, Workspace

    # Get all workspace memberships for the user
    member_result = await db.execute(
        select(WorkspaceMember).where(WorkspaceMember.user_id == user.id)
    )
    memberships = member_result.scalars().all()

    workspace_ids = [m.workspace_id for m in memberships]
    if not workspace_ids:
        return []

    ws_result = await db.execute(
        select(Workspace).where(Workspace.id.in_(workspace_ids))
    )
    workspaces = ws_result.scalars().all()
    return [_workspace_to_response(w) for w in workspaces]


@router.post("", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    body: CreateWorkspaceRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new workspace in the user's tenant."""
    from app.models import Tenant, TenantPlan, TenantStatus, Workspace, WorkspaceMember, MemberRole

    # Find an existing tenant for the user, or create one
    member_result = await db.execute(
        select(WorkspaceMember).where(WorkspaceMember.user_id == user.id)
    )
    existing_membership = member_result.scalar_one_or_none()

    if existing_membership:
        # Get the tenant from the existing workspace
        ws_result = await db.execute(
            select(Workspace).where(Workspace.id == existing_membership.workspace_id)
        )
        existing_workspace = ws_result.scalar_one_or_none()
        tenant_id = existing_workspace.tenant_id if existing_workspace else None
    else:
        tenant_id = None

    if not tenant_id:
        # Create a new tenant for the user
        tenant = Tenant(
            name=f"{user.full_name or user.email}'s Organization",
            slug=str(uuid4())[:8],
            plan=TenantPlan.FREE,
            status=TenantStatus.TRIALING,
        )
        db.add(tenant)
        await db.flush()
        await db.refresh(tenant)
        tenant_id = tenant.id

    workspace = Workspace(
        tenant_id=tenant_id,
        name=body.name,
        description=body.description,
    )
    db.add(workspace)
    await db.flush()
    await db.refresh(workspace)

    # Add the creator as admin
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user.id,
        role=MemberRole.ADMIN,
    )
    db.add(member)
    await db.flush()

    return _workspace_to_response(workspace)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get workspace details."""
    from app.models import Workspace, WorkspaceMember

    ws_result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Verify membership
    member_result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user.id,
        )
    )
    if not member_result.scalar_one_or_none() and not user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")

    return _workspace_to_response(workspace)


@router.post("/{workspace_id}/invite")
async def invite_member(
    workspace_id: str,
    body: InviteMemberRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Invite a user by email (creates WorkspaceMember with 'operator' role)."""
    from app.models import Workspace, WorkspaceMember, MemberRole, User

    # Verify workspace exists and user is a member
    ws_result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    member_result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user.id,
        )
    )
    if not member_result.scalar_one_or_none() and not user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")

    # Find user by email
    user_result = await db.execute(
        select(User).where(User.email == body.email)
    )
    target_user = user_result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found with that email")

    # Check if already a member
    existing = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == target_user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="User is already a member of this workspace")

    new_member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=target_user.id,
        role=MemberRole.OPERATOR,
    )
    db.add(new_member)
    await db.flush()
    await db.refresh(new_member)

    return {
        "message": f"Invitation sent to {body.email}",
        "workspace_id": workspace_id,
        "user_id": str(target_user.id),
        "role": MemberRole.OPERATOR.value,
    }


@router.delete("/{workspace_id}/members/{user_id}")
async def remove_member(
    workspace_id: str,
    user_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a member from a workspace."""
    from app.models import Workspace, WorkspaceMember, MemberRole

    # Verify workspace exists
    ws_result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Check that the requester is an admin member
    requester_result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user.id,
        )
    )
    requester_membership = requester_result.scalar_one_or_none()
    if not requester_membership and not user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")

    # Find the target member
    target_result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    target_member = target_result.scalar_one_or_none()
    if not target_member:
        raise HTTPException(status_code=404, detail="Member not found in this workspace")

    # Cannot remove yourself if you're the last admin
    if user_id == str(user.id):
        admin_count_result = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.role == MemberRole.ADMIN.value,
            )
        )
        admins = admin_count_result.scalars().all()
        if len(admins) <= 1:
            raise HTTPException(status_code=400, detail="Cannot remove the last admin")

    await db.delete(target_member)
    await db.flush()

    return {"message": "Member removed successfully"}


# ── Helpers ────────────────────────────────────────────────

def _workspace_to_response(w: Any) -> dict[str, Any]:
    return {
        "id": str(w.id),
        "tenant_id": str(w.tenant_id),
        "name": w.name,
        "description": w.description,
        "settings": w.settings or {},
        "created_at": w.created_at.isoformat() if w.created_at else None,
    }
