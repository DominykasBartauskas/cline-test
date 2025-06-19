"""
Pytest configuration file.
"""
import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.database import get_db
from app.main import app
from app.models.domain.base import Base

# Test database URL
TEST_DATABASE_URL = str(settings.DATABASE_URI).replace(
    f"/{settings.POSTGRES_DB}", "/test_db"
)


@pytest.fixture(scope="function")
def event_loop() -> Generator:
    """Create an event loop for pytest-asyncio."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine for each test."""
    engine = create_async_engine(
        str(TEST_DATABASE_URL), 
        echo=False,
        future=True,
        # Removed pool_pre_ping to avoid event loop conflicts
        pool_recycle=300,
        pool_timeout=20
    )
    
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def setup_database(test_engine) -> AsyncGenerator:
    """Set up the test database."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Clean up after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(test_engine, setup_database) -> AsyncGenerator:
    """Get a test database session."""
    TestingSessionLocal = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestingSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator:
    """Get a test client."""
    # Override the dependency
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
