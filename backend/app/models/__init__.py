"""SQLAlchemy models for Agentic Marketplace."""

from __future__ import annotations

import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB, UUID
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

from app.db.base import Base


# ── Enums ─────────────────────────────────────────────────

class TenantPlan(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIALING = "trialing"
    CANCELLED = "cancelled"


class MemberRole(str, enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    ANALYST = "analyst"
    BILLING_MANAGER = "billing_manager"
    AUDITOR = "auditor"


class WorkflowStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ExecutionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TriggerType(str, enum.Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    API = "api"
    WEBHOOK = "webhook"


class ListingStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class PriceType(str, enum.Enum):
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"


class BillingPeriod(str, enum.Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class TransactionType(str, enum.Enum):
    PURCHASE = "purchase"
    SUBSCRIPTION = "subscription"
    REFUND = "refund"
    PAYOUT = "payout"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"


class UserType(str, enum.Enum):
    CREATOR = "creator"
    CUSTOMER = "customer"


# ── Models ────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    user_type = Column(Enum(UserType, values_callable=lambda x: [e.value for e in x]), nullable=True)
    is_super_admin = Column(Boolean, default=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    memberships = relationship("WorkspaceMember", back_populates="user", lazy="selectin")
    workflows = relationship("Workflow", back_populates="created_by_user", lazy="selectin")
    listings = relationship("MarketplaceListing", back_populates="creator", lazy="selectin")


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    plan = Column(Enum(TenantPlan), default=TenantPlan.FREE)
    status = Column(Enum(TenantStatus), default=TenantStatus.TRIALING)
    branding_config = Column(JSONB, default=dict)
    settings = Column(JSONB, default=dict)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    workspaces = relationship("Workspace", back_populates="tenant", lazy="selectin")
    workflows = relationship("Workflow", back_populates="tenant", lazy="selectin")
    api_keys = relationship("APIKey", back_populates="tenant", lazy="selectin")
    audit_logs = relationship("AuditLog", back_populates="tenant", lazy="selectin")


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    settings = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", back_populates="workspaces")
    members = relationship("WorkspaceMember", back_populates="workspace", lazy="selectin")
    workflows = relationship("Workflow", back_populates="workspace", lazy="selectin")


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    __table_args__ = (
        Index("ix_workspace_member_unique", "workspace_id", "user_id", unique=True),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(Enum(MemberRole), default=MemberRole.OPERATOR)
    permissions = Column(JSONB, default=dict)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="memberships")


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    tags = Column(ARRAY(String), default=list)
    config = Column(JSONB, nullable=False, default=dict)
    is_template = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    execution_count = Column(Integer, default=0)
    avg_duration_ms = Column(Integer, nullable=True)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", back_populates="workflows")
    workspace = relationship("Workspace", back_populates="workflows")
    created_by_user = relationship("User", back_populates="workflows")
    executions = relationship("WorkflowExecution", back_populates="workflow", lazy="selectin")
    listing = relationship("MarketplaceListing", back_populates="workflow", uselist=False, lazy="selectin")


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    triggered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    trigger_type = Column(Enum(TriggerType), default=TriggerType.MANUAL)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    token_usage = Column(JSONB, nullable=True)
    cost = Column(Numeric(10, 6), default=0)
    duration_ms = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    workflow = relationship("Workflow", back_populates="executions")


class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price_type = Column(Enum(PriceType), default=PriceType.FREE)
    price = Column(Numeric(10, 2), default=0)
    billing_period = Column(Enum(BillingPeriod), nullable=True)
    category = Column(String(100), nullable=True)
    tags = Column(ARRAY(String), default=list)
    screenshots = Column(ARRAY(String), default=list)
    status = Column(Enum(ListingStatus), default=ListingStatus.DRAFT)
    rating_avg = Column(Numeric(3, 2), default=0)
    rating_count = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    revenue_total = Column(Numeric(12, 2), default=0)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workflow = relationship("Workflow", back_populates="listing")
    creator = relationship("User", back_populates="listings")
    transactions = relationship("Transaction", back_populates="listing", lazy="selectin")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("marketplace_listings.id"), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    platform_fee = Column(Numeric(10, 2), default=0)
    creator_amount = Column(Numeric(10, 2), default=0)
    currency = Column(String(3), default="USD")
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    payment_method = Column(String(50), nullable=True)
    payment_id = Column(String(255), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    listing = relationship("MarketplaceListing", back_populates="transactions")


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    key_prefix = Column(String(8), nullable=False)
    scopes = Column(ARRAY(String), default=list)
    rate_limit = Column(Integer, default=1000)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="api_keys")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_tenant_created", "tenant_id", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="audit_logs")
