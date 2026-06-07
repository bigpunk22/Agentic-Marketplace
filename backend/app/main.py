"""FastAPI application entry point."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.events import startup_event, shutdown_event
from app.api.v1.router import api_router

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    await startup_event()
    logger.info("🚀 Agentic Marketplace API started")
    yield
    await shutdown_event()
    logger.info("👋 Agentic Marketplace API stopped")


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.app_name,
        description="Multi-tenant AI workflow marketplace platform",
        version="1.0.0",
        docs_url="/api/docs" if settings.app_debug else None,
        redoc_url="/api/redoc" if settings.app_debug else None,
        openapi_url="/api/openapi.json" if settings.app_debug else None,
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request ID Middleware ─────────────────────────────
    @app.middleware("http")
    async def add_request_id(request, call_next):
        import uuid
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    # ── Routers ───────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    # ── Health Check ──────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": "1.0.0",
            "environment": settings.app_env,
        }

    return app


app = create_app()
