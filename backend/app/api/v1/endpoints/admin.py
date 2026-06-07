"""Super admin endpoints — global governance."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.security import get_current_user, require_admin
from app.db.base import get_db
from app.models import (
    User, Tenant, TenantStatus, MarketplaceListing, ListingStatus,
    Transaction, TransactionStatus, AuditLog,
)

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────

class ApproveListingRequest(BaseModel):
    approved: bool
    reason: str | None = None


# ── Endpoints ─────────────────────────────────────────────

@router.get("/tenants")
async def list_all_tenants(
    status: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all tenants (super admin only)."""
    query = select(Tenant)
    if status:
        query = query.where(Tenant.status == status)
    query = query.order_by(Tenant.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    tenants = result.scalars().all()
    return [
        {
            "id": str(t.id),
            "name": t.name,
            "slug": t.slug,
            "plan": t.plan.value,
            "status": t.status.value,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in tenants
    ]


@router.get("/tenants/{tenant_id}")
async def get_tenant_detail(
    tenant_id: str,
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get counts
    from app.models import Workflow, Workspace
    ws_count = await db.execute(
        select(func.count(Workspace.id)).where(Workspace.tenant_id == tenant_id)
    )
    wf_count = await db.execute(
        select(func.count(Workflow.id)).where(Workflow.tenant_id == tenant_id)
    )

    return {
        "id": str(tenant.id),
        "name": tenant.name,
        "slug": tenant.slug,
        "plan": tenant.plan.value,
        "status": tenant.status.value,
        "branding_config": tenant.branding_config,
        "settings": tenant.settings,
        "workspace_count": ws_count.scalar(),
        "workflow_count": wf_count.scalar(),
        "created_at": tenant.created_at.isoformat() if tenant.created_at else None,
    }


@router.patch("/tenants/{tenant_id}")
async def update_tenant(
    tenant_id: str,
    body: dict[str, Any],
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if "status" in body:
        tenant.status = TenantStatus(body["status"])
    if "plan" in body:
        from app.models import TenantPlan
        tenant.plan = TenantPlan(body["plan"])

    await db.flush()
    return {"message": "Tenant updated", "id": str(tenant.id)}


@router.get("/metrics")
async def get_global_metrics(
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Global platform metrics."""
    tenant_count = await db.execute(select(func.count(Tenant.id)))
    active_tenants = await db.execute(
        select(func.count(Tenant.id)).where(Tenant.status == TenantStatus.ACTIVE)
    )
    user_count = await db.execute(select(func.count(User.id)))
    listing_count = await db.execute(
        select(func.count(MarketplaceListing.id)).where(
            MarketplaceListing.status == ListingStatus.APPROVED
        )
    )
    pending_listings = await db.execute(
        select(func.count(MarketplaceListing.id)).where(
            MarketplaceListing.status == ListingStatus.PENDING_REVIEW
        )
    )

    # Revenue
    revenue_result = await db.execute(
        select(func.sum(Transaction.platform_fee)).where(
            Transaction.status == TransactionStatus.COMPLETED
        )
    )
    total_revenue = revenue_result.scalar() or 0

    return {
        "total_tenants": tenant_count.scalar(),
        "active_tenants": active_tenants.scalar(),
        "total_users": user_count.scalar(),
        "approved_listings": listing_count.scalar(),
        "pending_listings": pending_listings.scalar(),
        "total_platform_revenue": float(total_revenue),
    }


@router.get("/marketplace/pending")
async def get_pending_listings(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get listings pending review."""
    result = await db.execute(
        select(MarketplaceListing)
        .where(MarketplaceListing.status == ListingStatus.PENDING_REVIEW)
        .order_by(MarketplaceListing.created_at.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    listings = result.scalars().all()
    return [
        {
            "id": str(l.id),
            "title": l.title,
            "description": l.description,
            "price": float(l.price),
            "category": l.category,
            "creator_id": str(l.creator_id),
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in listings
    ]


@router.post("/marketplace/{listing_id}/approve")
async def approve_listing(
    listing_id: str,
    body: ApproveListingRequest,
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Approve or reject a marketplace listing."""
    result = await db.execute(
        select(MarketplaceListing).where(MarketplaceListing.id == listing_id)
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    listing.status = ListingStatus.APPROVED if body.approved else ListingStatus.REJECTED
    if body.approved:
        from datetime import datetime
        listing.published_at = datetime.utcnow()

    await db.flush()

    # Audit log
    audit = AuditLog(
        user_id=str(user.id),
        action="listing_approved" if body.approved else "listing_rejected",
        resource_type="marketplace_listing",
        resource_id=listing_id,
        new_value={"status": listing.status.value, "reason": body.reason},
    )
    db.add(audit)

    return {
        "message": f"Listing {'approved' if body.approved else 'rejected'}",
        "listing_id": listing_id,
    }


@router.get("/payouts")
async def get_payouts(
    status: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get payout queue."""
    query = select(Transaction).where(Transaction.type == "payout")
    if status:
        query = query.where(Transaction.status == status)
    query = query.order_by(Transaction.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    payouts = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "seller_id": str(p.seller_id) if p.seller_id else None,
            "amount": float(p.creator_amount),
            "status": p.status.value,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in payouts
    ]


@router.get("/audit-logs")
async def get_audit_logs(
    tenant_id: str | None = None,
    action: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get platform audit logs."""
    query = select(AuditLog)
    if tenant_id:
        query = query.where(AuditLog.tenant_id == tenant_id)
    if action:
        query = query.where(AuditLog.action == action)
    query = query.order_by(AuditLog.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()
    return [
        {
            "id": str(log.id),
            "tenant_id": str(log.tenant_id) if log.tenant_id else None,
            "user_id": str(log.user_id) if log.user_id else None,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": str(log.resource_id) if log.resource_id else None,
            "old_value": log.old_value,
            "new_value": log.new_value,
            "ip_address": str(log.ip_address) if log.ip_address else None,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
