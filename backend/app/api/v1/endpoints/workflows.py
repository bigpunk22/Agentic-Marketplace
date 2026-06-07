"""Workflow CRUD and execution endpoints."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_current_user
from app.db.base import get_db
from app.models import (
    User, Workflow, WorkflowExecution, WorkflowStatus,
    ExecutionStatus, TriggerType, WorkspaceMember, Workspace,
)

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────

class CreateWorkflowRequest(BaseModel):
    workspace_id: str
    name: str
    description: str | None = None
    category: str | None = None
    tags: list[str] = []
    config: dict = {}


class UpdateWorkflowRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    config: dict | None = None
    status: str | None = None


class ExecuteWorkflowRequest(BaseModel):
    input_data: dict = {}
    trigger_type: str = "manual"


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str | None
    category: str | None
    tags: list[str]
    config: dict
    is_published: bool = False
    status: str
    version: int
    execution_count: int
    created_at: str | None


class ExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    input_data: dict | None
    output_data: dict | None
    error_message: str | None
    token_usage: dict | None
    cost: float | None
    duration_ms: int | None
    created_at: str | None


# ── Endpoints ─────────────────────────────────────────────

@router.get("", response_model=list[WorkflowResponse])
async def list_workflows(
    workspace_id: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List workflows accessible to the current user."""
    query = select(Workflow)

    if workspace_id:
        query = query.where(Workflow.workspace_id == workspace_id)
    if status:
        query = query.where(Workflow.status == status)

    query = query.order_by(Workflow.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    workflows = result.scalars().all()
    return [_workflow_to_response(w) for w in workflows]


@router.post("", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    body: CreateWorkflowRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new workflow."""
    member_result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == body.workspace_id,
            WorkspaceMember.user_id == user.id,
        )
    )
    if not member_result.scalar_one_or_none() and not user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")

    # Derive tenant_id from workspace
    ws_result = await db.execute(
        select(Workspace).where(Workspace.id == body.workspace_id)
    )
    workspace_obj = ws_result.scalar_one_or_none()
    if not workspace_obj:
        raise HTTPException(status_code=404, detail="Workspace not found")

    workflow = Workflow(
        tenant_id=str(workspace_obj.tenant_id),
        workspace_id=body.workspace_id,
        created_by=str(user.id),
        name=body.name,
        description=body.description,
        category=body.category,
        tags=body.tags,
        config=body.config,
        status=WorkflowStatus.DRAFT,
    )
    db.add(workflow)
    await db.flush()
    await db.refresh(workflow)
    return _workflow_to_response(workflow)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _workflow_to_response(workflow)


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    body: UpdateWorkflowRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if body.name is not None:
        workflow.name = body.name
    if body.description is not None:
        workflow.description = body.description
    if body.category is not None:
        workflow.category = body.category
    if body.tags is not None:
        workflow.tags = body.tags
    if body.config is not None:
        workflow.config = body.config
        workflow.version += 1
    if body.status is not None:
        workflow.status = WorkflowStatus(body.status)

    await db.flush()
    return _workflow_to_response(workflow)


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    await db.delete(workflow)
    return None


@router.post("/{workflow_id}/execute", response_model=ExecutionResponse, status_code=202)
async def execute_workflow(
    workflow_id: str,
    body: ExecuteWorkflowRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a workflow execution."""
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.status != WorkflowStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Workflow is not active")

    execution = WorkflowExecution(
        workflow_id=workflow_id,
        triggered_by=str(user.id),
        trigger_type=TriggerType(body.trigger_type),
        status=ExecutionStatus.PENDING,
        input_data=body.input_data,
    )
    db.add(execution)
    await db.flush()

    # Queue for async execution via Celery
    try:
        from app.tasks.workflow_tasks import execute_workflow_task
        execute_workflow_task.delay(str(execution.id))
    except Exception:
        pass  # Celery may not be running in dev

    return _execution_to_response(execution)


@router.get("/{workflow_id}/executions", response_model=list[ExecutionResponse])
async def list_executions(
    workflow_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(WorkflowExecution)
        .where(WorkflowExecution.workflow_id == workflow_id)
        .order_by(WorkflowExecution.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    result = await db.execute(query)
    executions = result.scalars().all()
    return [_execution_to_response(e) for e in executions]


@router.post("/{workflow_id}/publish", response_model=WorkflowResponse)
async def publish_workflow(
    workflow_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Publish a workflow (sets is_published=True, status='active')."""
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Verify the user is the creator or a super admin
    if str(workflow.created_by) != str(user.id) and not user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not authorized to publish this workflow")

    workflow.is_published = True
    workflow.status = WorkflowStatus.ACTIVE
    await db.flush()
    return _workflow_to_response(workflow)


# ── Helpers ────────────────────────────────────────────────

def _workflow_to_response(w: Workflow) -> dict[str, Any]:
    return {
        "id": str(w.id),
        "name": w.name,
        "description": w.description,
        "category": w.category,
        "tags": w.tags or [],
        "config": w.config or {},
        "is_published": w.is_published,
        "status": w.status.value,
        "version": w.version,
        "execution_count": w.execution_count,
        "created_at": w.created_at.isoformat() if w.created_at else None,
    }


def _execution_to_response(e: WorkflowExecution) -> dict[str, Any]:
    return {
        "id": str(e.id),
        "workflow_id": str(e.workflow_id),
        "status": e.status.value,
        "input_data": e.input_data,
        "output_data": e.output_data,
        "error_message": e.error_message,
        "token_usage": e.token_usage,
        "cost": float(e.cost) if e.cost else None,
        "duration_ms": e.duration_ms,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }
