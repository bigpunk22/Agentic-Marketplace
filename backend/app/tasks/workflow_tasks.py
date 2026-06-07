"""Async workflow execution tasks."""

from __future__ import annotations

import logging
from datetime import datetime

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.workflow_tasks.execute_workflow_task", max_retries=3)
def execute_workflow_task(self, execution_id: str) -> dict:
    """
    Execute a workflow asynchronously.
    
    This task:
    1. Fetches the execution record and workflow config
    2. Routes to the appropriate AI model via OpenRouter
    3. Executes the workflow steps
    4. Stores results and updates execution status
    5. Calculates cost based on token usage
    """
    import asyncio
    asyncio.run(_async_execute(self, execution_id))


async def _async_execute(task, execution_id: str) -> dict:
    """Async execution logic."""
    from app.db.base import AsyncSessionLocal
    from app.models import WorkflowExecution, Workflow, ExecutionStatus
    from sqlalchemy import select
    import httpx

    async with AsyncSessionLocal() as db:
        try:
            # Get execution
            result = await db.execute(
                select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
            )
            execution = result.scalar_one_or_none()
            if not execution:
                logger.error(f"Execution {execution_id} not found")
                return {"error": "Execution not found"}

            # Update status to running
            execution.status = ExecutionStatus.RUNNING
            execution.started_at = datetime.utcnow()
            await db.flush()

            # Get workflow
            wf_result = await db.execute(
                select(Workflow).where(Workflow.id == execution.workflow_id)
            )
            workflow = wf_result.scalar_one_or_none()
            if not workflow:
                raise Exception("Workflow not found")

            # Execute via OpenRouter
            from app.core.config import get_settings
            settings = get_settings()

            config = workflow.config
            prompt = config.get("prompt", "")
            model = config.get("model", settings.default_ai_model)

            # Replace template variables
            for key, value in (execution.input_data or {}).items():
                prompt = prompt.replace(f"{{{key}}}", str(value))

            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"{settings.openrouter_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openrouter_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": config.get("max_tokens", 2000),
                    },
                )

                if response.status_code != 200:
                    raise Exception(f"AI API error: {response.status_code} - {response.text}")

                data = response.json()
                output = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})

            # Update execution with results
            execution.output_data = {"result": output}
            execution.token_usage = {
                model: {
                    "input": usage.get("prompt_tokens", 0),
                    "output": usage.get("completion_tokens", 0),
                }
            }
            execution.status = ExecutionStatus.COMPLETED
            execution.completed_at = datetime.utcnow()

            if execution.started_at:
                delta = execution.completed_at - execution.started_at
                execution.duration_ms = int(delta.total_seconds() * 1000)

            # Calculate cost (simplified)
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            # Rough estimate: $0.000002 per token
            execution.cost = (input_tokens + output_tokens) * 0.000002

            # Update workflow stats
            workflow.execution_count += 1
            if execution.duration_ms:
                if workflow.avg_duration_ms:
                    workflow.avg_duration_ms = (workflow.avg_duration_ms + execution.duration_ms) // 2
                else:
                    workflow.avg_duration_ms = execution.duration_ms

            await db.commit()

            logger.info(f"Execution {execution_id} completed successfully")
            return {
                "execution_id": execution_id,
                "status": "completed",
                "cost": execution.cost,
                "duration_ms": execution.duration_ms,
            }

        except Exception as exc:
            logger.exception(f"Execution {execution_id} failed: {exc}")
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(exc)
            execution.completed_at = datetime.utcnow()
            await db.commit()

            # Retry
            raise task.retry(exc=exc, countdown=60)
