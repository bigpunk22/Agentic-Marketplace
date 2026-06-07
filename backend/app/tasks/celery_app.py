"""Celery application configuration."""

from __future__ import annotations

from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "agentic_marketplace",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.workflow_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_default_queue="default",
    task_routes={
        "app.tasks.workflow_tasks.execute_workflow_task": {"queue": "workflows"},
    },
)
