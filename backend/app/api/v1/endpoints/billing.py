"""Billing and subscription endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_current_user
from app.db.base import get_db
from app.models import User, Tenant, TenantPlan, Transaction

router = APIRouter()


class UpgradeRequest(BaseModel):
    plan: str  # pro, business, enterprise


@router.get("/subscription")
async def get_subscription(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current subscription details."""
    # Find user's tenant via workspace membership
    from app.models import WorkspaceMember, Workspace
    member_result = await db.execute(
        select(WorkspaceMember).where(WorkspaceMember.user_id == user.id)
    )
    membership = member_result.scalar_one_or_none()
    if not membership:
        return {"plan": "none", "status": "no_workspace"}

    workspace_result = await db.execute(
        select(Workspace).where(Workspace.id == membership.workspace_id)
    )
    workspace = workspace_result.scalar_one_or_none()
    if not workspace:
        return {"plan": "none", "status": "no_workspace"}

    tenant_result = await db.execute(select(Tenant).where(Tenant.id == workspace.tenant_id))
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        return {"plan": "none", "status": "no_tenant"}

    return {
        "tenant_id": str(tenant.id),
        "plan": tenant.plan.value,
        "status": tenant.status.value,
        "trial_ends_at": tenant.trial_ends_at.isoformat() if tenant.trial_ends_at else None,
    }


@router.post("/subscription/upgrade")
async def upgrade_subscription(
    body: UpgradeRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upgrade subscription plan."""
    try:
        new_plan = TenantPlan(body.plan)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {body.plan}")

    # Find tenant
    from app.models import WorkspaceMember, Workspace
    member_result = await db.execute(
        select(WorkspaceMember).where(WorkspaceMember.user_id == user.id)
    )
    membership = member_result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="No workspace found")

    workspace_result = await db.execute(
        select(Workspace).where(Workspace.id == membership.workspace_id)
    )
    workspace = workspace_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    tenant_result = await db.execute(select(Tenant).where(Tenant.id == workspace.tenant_id))
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    old_plan = tenant.plan
    tenant.plan = new_plan
    await db.flush()

    return {
        "message": f"Upgraded from {old_plan.value} to {new_plan.value}",
        "plan": new_plan.value,
    }


@router.get("/invoices")
async def list_invoices(
    page: int = 1,
    limit: int = 20,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List billing transactions/invoices."""
    from app.models import WorkspaceMember, Workspace
    member_result = await db.execute(
        select(WorkspaceMember).where(WorkspaceMember.user_id == user.id)
    )
    membership = member_result.scalar_one_or_none()
    if not membership:
        return []

    workspace_result = await db.execute(
        select(Workspace).where(Workspace.id == membership.workspace_id)
    )
    workspace = workspace_result.scalar_one_or_none()
    if not workspace:
        return []

    result = await db.execute(
        select(Transaction)
        .where(Transaction.tenant_id == workspace.tenant_id)
        .order_by(Transaction.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    transactions = result.scalars().all()

    return [
        {
            "id": str(t.id),
            "type": t.type.value,
            "amount": float(t.amount),
            "platform_fee": float(t.platform_fee),
            "status": t.status.value,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in transactions
    ]


@router.get("/usage")
async def get_usage(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed usage breakdown."""
    from app.models import WorkspaceMember, Workspace, Workflow, WorkflowExecution
    from sqlalchemy import func
    from datetime import datetime, timedelta

    member_result = await db.execute(
        select(WorkspaceMember).where(WorkspaceMember.user_id == user.id)
    )
    membership = member_result.scalar_one_or_none()
    if not membership:
        return {"error": "No workspace found"}

    workspace_result = await db.execute(
        select(Workspace).where(Workspace.id == membership.workspace_id)
    )
    workspace = workspace_result.scalar_one_or_none()
    if not workspace:
        return {"error": "Workspace not found"}

    tenant_id = workspace.tenant_id
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)

    # Executions by day
    daily_result = await db.execute(
        select(
            func.date(WorkflowExecution.created_at).label("date"),
            func.count(WorkflowExecution.id).label("count"),
            func.sum(WorkflowExecution.cost).label("cost"),
        )
        .join(Workflow)
        .where(
            Workflow.tenant_id == tenant_id,
            WorkflowExecution.created_at >= month_start,
        )
        .group_by(func.date(WorkflowExecution.created_at))
        .order_by(func.date(WorkflowExecution.created_at))
    )
    daily = daily_result.all()

    return {
        "tenant_id": str(tenant_id),
        "period": month_start.isoformat(),
        "daily_usage": [
            {"date": str(d.date), "executions": d.count, "cost": float(d.cost or 0)}
            for d in daily
        ],
    }
