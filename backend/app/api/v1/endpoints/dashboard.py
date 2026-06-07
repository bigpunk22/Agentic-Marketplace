"""Creator dashboard endpoints — my listings, earnings, publish."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.security import get_current_user, require_admin
from app.db.base import get_db
from app.models import (
    User, UserType, MarketplaceListing, ListingStatus,
    Transaction, TransactionStatus, Workflow, WorkflowExecution,
)

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────

class PublishListingRequest(BaseModel):
    workflow_id: str
    title: str
    description: str | None = None
    price_type: str = "free"
    price: float = 0
    billing_period: str | None = None
    category: str | None = None
    tags: list[str] = []


# ── Endpoints ─────────────────────────────────────────────

@router.get("/dashboard/creator")
async def creator_dashboard(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Creator dashboard overview — earnings, listing stats, recent sales."""
    # My listings
    listings_result = await db.execute(
        select(MarketplaceListing)
        .where(MarketplaceListing.creator_id == user.id)
        .order_by(MarketplaceListing.created_at.desc())
    )
    my_listings = listings_result.scalars().all()

    total_listings = len(my_listings)
    approved_count = sum(1 for l in my_listings if l.status == ListingStatus.APPROVED)
    pending_count = sum(1 for l in my_listings if l.status == ListingStatus.PENDING_REVIEW)
    total_purchases = sum(l.purchase_count for l in my_listings)

    # Total earnings (from transactions where user is seller)
    earnings_result = await db.execute(
        select(func.sum(Transaction.creator_amount))
        .where(
            Transaction.seller_id == str(user.id),
            Transaction.status == TransactionStatus.COMPLETED,
        )
    )
    total_earnings = float(earnings_result.scalar() or 0)

    # Monthly earnings
    from datetime import datetime
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    monthly_result = await db.execute(
        select(func.sum(Transaction.creator_amount))
        .where(
            Transaction.seller_id == str(user.id),
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.created_at >= month_start,
        )
    )
    monthly_earnings = float(monthly_result.scalar() or 0)

    # Recent sales (last 5)
    recent_sales_result = await db.execute(
        select(Transaction)
        .where(
            Transaction.seller_id == str(user.id),
            Transaction.status == TransactionStatus.COMPLETED,
        )
        .order_by(Transaction.created_at.desc())
        .limit(5)
    )
    recent_sales = recent_sales_result.scalars().all()

    return {
        "stats": {
            "total_listings": total_listings,
            "approved_listings": approved_count,
            "pending_listings": pending_count,
            "total_sales": total_purchases,
            "total_earnings": total_earnings,
            "monthly_earnings": monthly_earnings,
        },
        "listings": [_listing_to_dict(l) for l in my_listings],
        "recent_sales": [
            {
                "id": str(s.id),
                "listing_id": str(s.listing_id) if s.listing_id else None,
                "buyer_id": str(s.buyer_id) if s.buyer_id else None,
                "amount": float(s.amount),
                "creator_amount": float(s.creator_amount),
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in recent_sales
        ],
    }


@router.get("/dashboard/customer")
async def customer_dashboard(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Customer dashboard overview — purchases, deployed workflows, usage."""
    # Purchases (transactions where user is buyer)
    purchases_result = await db.execute(
        select(Transaction)
        .where(
            Transaction.buyer_id == str(user.id),
            Transaction.status == TransactionStatus.COMPLETED,
        )
        .order_by(Transaction.created_at.desc())
        .limit(10)
    )
    purchases = purchases_result.scalars().all()

    # Total spent
    spent_result = await db.execute(
        select(func.sum(Transaction.amount))
        .where(
            Transaction.buyer_id == str(user.id),
            Transaction.status == TransactionStatus.COMPLETED,
        )
    )
    total_spent = float(spent_result.scalar() or 0)

    # My workflows (created by me — deployed/purchased items)
    workflows_result = await db.execute(
        select(Workflow)
        .where(Workflow.created_by == user.id)
        .order_by(Workflow.created_at.desc())
        .limit(10)
    )
    my_workflows = workflows_result.scalars().all()

    # Execution stats
    exec_result = await db.execute(
        select(
            func.count(WorkflowExecution.id).label("total"),
            func.sum(WorkflowExecution.cost).label("total_cost"),
        )
        .join(Workflow)
        .where(Workflow.created_by == user.id)
    )
    exec_stats = exec_result.one_or_none()
    total_executions = exec_stats.total if exec_stats else 0
    total_exec_cost = float(exec_stats.total_cost or 0) if exec_stats else 0

    # Monthly usage
    from datetime import datetime
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    monthly_result = await db.execute(
        select(
            func.count(WorkflowExecution.id).label("count"),
            func.sum(WorkflowExecution.cost).label("cost"),
        )
        .join(Workflow)
        .where(
            Workflow.created_by == user.id,
            WorkflowExecution.created_at >= month_start,
        )
    )
    monthly = monthly_result.one_or_none()
    monthly_executions = monthly.count if monthly else 0
    monthly_cost = float(monthly.cost or 0) if monthly else 0

    return {
        "stats": {
            "total_purchases": len(purchases),
            "total_spent": total_spent,
            "total_workflows": len(my_workflows),
            "total_executions": total_executions,
            "total_exec_cost": total_exec_cost,
            "monthly_executions": monthly_executions,
            "monthly_cost": monthly_cost,
        },
        "purchases": [
            {
                "id": str(p.id),
                "listing_id": str(p.listing_id) if p.listing_id else None,
                "amount": float(p.amount),
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in purchases
        ],
        "workflows": [
            {
                "id": str(w.id),
                "name": w.name,
                "status": w.status.value,
                "execution_count": w.execution_count,
                "category": w.category,
                "created_at": w.created_at.isoformat() if w.created_at else None,
            }
            for w in my_workflows
        ],
    }


def _listing_to_dict(l: MarketplaceListing) -> dict[str, Any]:
    return {
        "id": str(l.id),
        "title": l.title,
        "status": l.status.value,
        "price": float(l.price),
        "price_type": l.price_type.value if l.price_type else "free",
        "category": l.category,
        "tags": l.tags or [],
        "rating_avg": float(l.rating_avg),
        "rating_count": l.rating_count,
        "purchase_count": l.purchase_count,
        "revenue_total": float(l.revenue_total),
        "created_at": l.created_at.isoformat() if l.created_at else None,
    }
