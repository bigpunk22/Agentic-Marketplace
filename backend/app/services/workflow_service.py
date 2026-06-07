"""Workflow service — business logic."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import (
    Workflow, WorkflowExecution, WorkflowStatus,
    ExecutionStatus, TriggerType,
)


class WorkflowService:
    """Handles workflow business logic."""

    @staticmethod
    async def create_workflow(
        db: AsyncSession,
        tenant_id: str,
        workspace_id: str,
        created_by: str,
        name: str,
        description: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
        config: dict | None = None,
    ) -> Workflow:
        workflow = Workflow(
            id=str(uuid4()),
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            created_by=created_by,
            name=name,
            description=description,
            category=category,
            tags=tags or [],
            config=config or {},
            status=WorkflowStatus.DRAFT,
        )
        db.add(workflow)
        await db.flush()
        return workflow

    @staticmethod
    async def execute_workflow(
        db: AsyncSession,
        workflow_id: str,
        triggered_by: str | None,
        trigger_type: TriggerType,
        input_data: dict | None = None,
    ) -> WorkflowExecution:
        execution = WorkflowExecution(
            id=str(uuid4()),
            workflow_id=workflow_id,
            triggered_by=triggered_by,
            trigger_type=trigger_type,
            status=ExecutionStatus.PENDING,
            input_data=input_data,
        )
        db.add(execution)
        await db.flush()
        return execution

    @staticmethod
    async def get_tenant_workflows(
        db: AsyncSession,
        tenant_id: str,
        status: WorkflowStatus | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Workflow], int]:
        query = select(Workflow).where(Workflow.tenant_id == tenant_id)
        count_query = select(func.count(Workflow.id)).where(Workflow.tenant_id == tenant_id)

        if status:
            query = query.where(Workflow.status == status)
            count_query = count_query.where(Workflow.status == status)

        query = query.order_by(Workflow.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        result = await db.execute(query)
        count_result = await db.execute(count_query)

        return result.scalars().all(), count_result.scalar()

    @staticmethod
    async def get_execution_stats(
        db: AsyncSession,
        tenant_id: str,
        days: int = 30,
    ) -> dict[str, Any]:
        from datetime import timedelta

        since = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(
                func.count(WorkflowExecution.id).label("total"),
                func.sum(WorkflowExecution.cost).label("total_cost"),
                func.avg(WorkflowExecution.duration_ms).label("avg_duration"),
            )
            .join(Workflow)
            .where(
                Workflow.tenant_id == tenant_id,
                WorkflowExecution.created_at >= since,
            )
        )
        row = result.one()

        return {
            "total_executions": row.total or 0,
            "total_cost": float(row.total_cost or 0),
            "avg_duration_ms": float(row.avg_duration or 0),
            "period_days": days,
        }
