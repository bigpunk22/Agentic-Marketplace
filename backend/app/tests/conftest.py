"""Pytest fixtures and configuration."""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.base import Base, get_db

# Use a separate test database with NullPool to avoid connection pooling issues
TEST_DATABASE_URL = "postgresql+asyncpg://agentic:agentic_dev_password@localhost:5432/agentic_test"


def _create_test_engine():
    """Create a fresh test engine (call from within an async context)."""
    return create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
        pool_pre_ping=False,
    )


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional test session."""
    engine = _create_test_engine()
    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            await engine.dispose()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables once per test session."""
    engine = _create_test_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    yield


@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    """Clean data between tests."""
    yield
    engine = _create_test_engine()
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))
    await engine.dispose()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
