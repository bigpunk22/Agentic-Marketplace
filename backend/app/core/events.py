"""Startup and shutdown event handlers."""

from __future__ import annotations

import logging

from app.db.base import close_db

logger = logging.getLogger(__name__)


async def startup_event() -> None:
    """Run on application startup."""
    logger.info("Running startup events...")
    # Initialize connections, warm caches, etc.
    logger.info("Startup complete.")


async def shutdown_event() -> None:
    """Run on application shutdown."""
    logger.info("Running shutdown events...")
    await close_db()
    logger.info("Shutdown complete.")
