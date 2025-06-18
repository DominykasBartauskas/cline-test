"""
Test API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.database import get_db
from app.main import app

# Create test database engine
TEST_DATABASE_URL = settings.DATABASE_URI.replace(
    f"/{settings.POSTGRES_DB}", "/test_db"
)
test_engine = create_async_engine(str(TEST_DATABASE_URL), echo=False)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


# Dependency override
async def override_get_db():
    """Get test database session."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)


def test_read_main():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()
    assert "docs" in response.json()


def test_health():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_movies():
    """Test get movies endpoint."""
    response = client.get("/api/movies")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert "page" in response.json()
    assert "size" in response.json()
    assert "pages" in response.json()


@pytest.mark.asyncio
async def test_get_tv_shows():
    """Test get TV shows endpoint."""
    response = client.get("/api/tv")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert "page" in response.json()
    assert "size" in response.json()
    assert "pages" in response.json()


@pytest.mark.asyncio
async def test_get_genres():
    """Test get genres endpoint."""
    response = client.get("/api/genres")
    assert response.status_code == 200
    assert "movie_genres" in response.json()
    assert "tv_genres" in response.json()


@pytest.mark.asyncio
async def test_search_multi():
    """Test search multi endpoint."""
    response = client.get("/api/search/multi?query=test")
    assert response.status_code == 200
    assert "movies" in response.json()
    assert "tv_shows" in response.json()
    assert "total_results" in response.json()
    assert "total_pages" in response.json()
    assert "page" in response.json()
