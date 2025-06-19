"""
Test API endpoints.
"""
import pytest


@pytest.mark.asyncio
async def test_read_main(client):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()
    assert "docs" in response.json()


@pytest.mark.asyncio
async def test_health(client):
    """Test health endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_movies(client):
    """Test get movies endpoint."""
    response = await client.get("/api/movies")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert "page" in response.json()
    assert "size" in response.json()
    assert "pages" in response.json()


@pytest.mark.asyncio
async def test_get_tv_shows(client):
    """Test get TV shows endpoint."""
    response = await client.get("/api/tv")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert "page" in response.json()
    assert "size" in response.json()
    assert "pages" in response.json()


@pytest.mark.asyncio
async def test_get_genres(client):
    """Test get genres endpoint."""
    response = await client.get("/api/genres")
    assert response.status_code == 200
    # The genres endpoint returns a list of genres
    genres = response.json()
    assert isinstance(genres, list)


@pytest.mark.asyncio
async def test_search_multi(client):
    """Test search multi endpoint."""
    response = await client.get("/api/search/multi?query=test")
    assert response.status_code == 200
    assert "movies" in response.json()
    assert "tv_shows" in response.json()
    assert "total_results" in response.json()
    assert "total_pages" in response.json()
    assert "page" in response.json()
