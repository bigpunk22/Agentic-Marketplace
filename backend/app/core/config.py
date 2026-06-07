"""Core configuration for Agentic Marketplace."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, List

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    # ── Application ──────────────────────────────────────
    app_name: str = "Agentic Marketplace"
    app_env: str = "development"
    app_debug: bool = True
    app_secret_key: str = "change-me-to-a-random-secret-key-min-32-chars"
    app_url: str = "http://localhost:8000"

    # ── Database ──────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://agentic:agentic_dev_password@localhost:5432/agentic_marketplace"
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # ── Redis ─────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    redis_password: str = ""

    # ── JWT / Auth ────────────────────────────────────────
    jwt_secret_key: str = "change-me-to-a-random-secret-key-min-32-chars"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── CORS ──────────────────────────────────────────────
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"

    # ── OAuth ─────────────────────────────────────────────
    google_client_id: str = ""
    google_client_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""

    # ── AI ────────────────────────────────────────────────
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_ai_model: str = "openai/gpt-4o-mini"

    # ── Stripe ────────────────────────────────────────────
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""

    # ── Email ─────────────────────────────────────────────
    sendgrid_api_key: str = ""
    email_from: str = "noreply@agenticmarketplace.com"

    # ── Storage ───────────────────────────────────────────
    storage_endpoint: str = "localhost:9000"
    storage_access_key: str = "minioadmin"
    storage_secret_key: str = "minioadmin123"
    storage_bucket: str = "agentic-marketplace"
    storage_secure: bool = False

    # ── Qdrant ────────────────────────────────────────────
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "workflows"

    # ── Celery ────────────────────────────────────────────
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
