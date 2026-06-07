"""Tenant management endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_current_user, require_admin
from app.db.base import get_db
from app.models import Tenant, TenantPlan, TenantStatus, Workspace, WorkspaceMember, MemberRole

router = APIRouter()


class CreateTenantRequest(BaseModel):
    name: str
    slug: str


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    plan: str
    status: str
    branding_config: dict
    created_at: str | None


@router.get("/current", response_model=TenantResponse)
async def get_current_tenant(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's active tenant."""
    from app.models import WorkspaceMember

    result = await db.execute(
        select(WorkspaceMember).where(WorkspaceMember.user_id == user.id)
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="No workspace membership found")

    workspace = await db.execute(
        select(Workspace).where(Workspace.id == membership.workspace_id)
    )
    workspace = workspace.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    tenant = await db.execute(select(Tenant).where(Tenant.id == workspace.tenant_id))
    tenant = tenant.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return _tenant_to_response(tenant)


@router.post("", response_model=TenantResponse, status_code=201)
async def create_tenant(
    body: CreateTenantRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new tenant with default workspace."""
    existing = await db.execute(select(Tenant).where(Tenant.slug == body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slug already taken")

    tenant = Tenant(
        name=body.name,
        slug=body.slug,
        plan=TenantPlan.FREE,
        status=TenantStatus.TRIALING,
    )
    db.add(tenant)
    await db.flush()

    workspace = Workspace(
        tenant_id=tenant.id,
        name="Default Workspace",
        description="Your first workspace",
    )
    db.add(workspace)
    await db.flush()

    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user.id,
        role=MemberRole.ADMIN,
    )
    db.add(member)
    await db.flush()
    await db.refresh(tenant)

    return {
        "id": str(tenant.id),
        "name": tenant.name,
        "slug": tenant.slug,
        "plan": tenant.plan.value,
        "status": tenant.status.value,
        "branding_config": tenant.branding_config,
        "created_at": tenant.created_at.isoformat() if tenant.created_at else None,
    }


@router.get("/{tenant_id}/usage")
async def get_tenant_usage(
    tenant_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get usage statistics for a tenant."""
    from datetime import datetime

    return {
        "tenant_id": tenant_id,
        "executions_this_month": 0,
        "total_cost_this_month": 0,
        "period_start": datetime.utcnow().replace(day=1).isoformat(),
    }


def _tenant_to_response(tenant):
    return {
        "id": str(tenant.id),
        "name": tenant.name,
        "slug": tenant.slug,
        "plan": tenant.plan.value,
        "status": tenant.status.value,
        "branding_config": tenant.branding_config,
        "created_at": tenant.created_at.isoformat() if tenant.created_at else None,
    }
