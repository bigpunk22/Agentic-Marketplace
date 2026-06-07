"""Marketplace endpoints — browse, purchase, publish."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.security import get_current_user
from app.db.base import get_db
from app.models import (
    User, MarketplaceListing, ListingStatus, PriceType,
    Transaction, TransactionType, TransactionStatus,
    Workflow, WorkflowStatus,
)

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────

class CreateListingRequest(BaseModel):
    workflow_id: str
    title: str
    description: str | None = None
    price_type: str = "free"
    price: float = 0
    billing_period: str | None = None
    category: str | None = None
    tags: list[str] = []


class ListingResponse(BaseModel):
    id: str
    title: str
    description: str | None
    price_type: str
    price: float
    category: str | None
    tags: list[str]
    status: str
    rating_avg: float
    rating_count: int
    purchase_count: int
    created_at: str | None


# ── Endpoints ─────────────────────────────────────────────

@router.get("/listings", response_model=list[ListingResponse])
async def browse_listings(
    category: str | None = None,
    search: str | None = None,
    sort: str = Query("popular", regex="^(popular|newest|top_rated|price_asc|price_desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Browse marketplace listings."""
    query = select(MarketplaceListing).where(
        MarketplaceListing.status == ListingStatus.APPROVED
    )

    if category:
        query = query.where(MarketplaceListing.category == category)

    if search:
        query = query.where(
            MarketplaceListing.title.ilike(f"%{search}%")
            | MarketplaceListing.description.ilike(f"%{search}%")
        )

    # Sort
    sort_map = {
        "popular": MarketplaceListing.purchase_count.desc(),
        "newest": MarketplaceListing.created_at.desc(),
        "top_rated": MarketplaceListing.rating_avg.desc(),
        "price_asc": MarketplaceListing.price.asc(),
        "price_desc": MarketplaceListing.price.desc(),
    }
    query = query.order_by(sort_map.get(sort, MarketplaceListing.purchase_count.desc()))
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    listings = result.scalars().all()
    return [_listing_to_response(l) for l in listings]


@router.get("/listings/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MarketplaceListing).where(MarketplaceListing.id == listing_id)
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return _listing_to_response(listing)


@router.post("/listings/{listing_id}/purchase", status_code=201)
async def purchase_listing(
    listing_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Purchase a marketplace listing."""
    result = await db.execute(
        select(MarketplaceListing).where(MarketplaceListing.id == listing_id)
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.status != ListingStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Listing not available")

    platform_fee = listing.price * 0.30  # 30% platform fee
    creator_amount = listing.price - platform_fee

    transaction = Transaction(
        buyer_id=str(user.id),
        seller_id=str(listing.creator_id),
        listing_id=listing_id,
        tenant_id=str(listing.tenant_id),
        type=TransactionType.PURCHASE,
        amount=listing.price,
        platform_fee=platform_fee,
        creator_amount=creator_amount,
        status=TransactionStatus.COMPLETED,  # Simplified — real: pending until payment
    )
    db.add(transaction)

    listing.purchase_count += 1
    listing.revenue_total += creator_amount
    await db.flush()

    return {
        "message": "Purchase successful",
        "transaction_id": str(transaction.id),
        "amount": listing.price,
    }


@router.get("/categories")
async def list_categories(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all marketplace categories with counts."""
    result = await db.execute(
        select(
            MarketplaceListing.category,
            func.count(MarketplaceListing.id).label("count"),
        )
        .where(MarketplaceListing.status == ListingStatus.APPROVED)
        .group_by(MarketplaceListing.category)
        .order_by(func.count(MarketplaceListing.id).desc())
    )
    categories = result.all()
    return [
        {"name": cat.category or "Uncategorized", "count": cat.count}
        for cat in categories
    ]


@router.get("/featured", response_model=list[ListingResponse])
async def get_featured(
    limit: int = Query(6, ge=1, le=20),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get featured listings."""
    result = await db.execute(
        select(MarketplaceListing)
        .where(MarketplaceListing.status == ListingStatus.APPROVED)
        .order_by(MarketplaceListing.rating_avg.desc())
        .limit(limit)
    )
    listings = result.scalars().all()
    return [_listing_to_response(l) for l in listings]


@router.post("/listings", status_code=201)
async def create_listing(
    body: CreateListingRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Publish a workflow as a marketplace listing (status: pending_review)."""
    workflow_result = await db.execute(
        select(Workflow).where(
            Workflow.id == body.workflow_id,
            Workflow.created_by == user.id,
        )
    )
    workflow = workflow_result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found or not owned by you")

    listing = MarketplaceListing(
        workflow_id=body.workflow_id,
        creator_id=str(user.id),
        tenant_id=str(workflow.tenant_id),
        title=body.title,
        description=body.description,
        price_type=PriceType(body.price_type),
        price=body.price,
        billing_period=body.billing_period,
        category=body.category,
        tags=body.tags,
        status=ListingStatus.PENDING_REVIEW,
    )
    db.add(listing)
    await db.flush()
    await db.refresh(listing)

    return _listing_to_response(listing)


@router.get("/my-listings", response_model=list[ListingResponse])
async def my_listings(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List the current user's marketplace listings."""
    result = await db.execute(
        select(MarketplaceListing)
        .where(MarketplaceListing.creator_id == user.id)
        .order_by(MarketplaceListing.created_at.desc())
    )
    listings = result.scalars().all()
    return [_listing_to_response(l) for l in listings]


# ── Helpers ────────────────────────────────────────────────

def _listing_to_response(l: MarketplaceListing) -> dict[str, Any]:
    return {
        "id": str(l.id),
        "title": l.title,
        "description": l.description,
        "price_type": l.price_type.value,
        "price": float(l.price),
        "category": l.category,
        "tags": l.tags or [],
        "status": l.status.value,
        "rating_avg": float(l.rating_avg),
        "rating_count": l.rating_count,
        "purchase_count": l.purchase_count,
        "created_at": l.created_at.isoformat() if l.created_at else None,
    }
