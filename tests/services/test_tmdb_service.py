import pytest
from httpx import AsyncClient, HTTPError, Response
from datetime import datetime, timedelta, UTC
from fastapi import HTTPException

from app.services.tmdb_service import TMDBService
from app.core.config import settings

# Mock response data
MOCK_MOVIE_RESPONSE = {
    "id": 550,
    "title": "Fight Club",
    "overview": "A ticking-time-bomb insomniac...",
    "release_date": "1999-10-15",
    "credits": {
        "cast": [
            {"id": 819, "name": "Edward Norton", "character": "The Narrator"},
            {"id": 287, "name": "Brad Pitt", "character": "Tyler Durden"}
        ]
    }
}

MOCK_TV_RESPONSE = {
    "id": 1399,
    "name": "Game of Thrones",
    "overview": "Seven noble families...",
    "first_air_date": "2011-04-17"
}

MOCK_GENRE_RESPONSE = {
    "genres": [
        {"id": 28, "name": "Action"},
        {"id": 12, "name": "Adventure"}
    ]
}

@pytest.fixture
def tmdb_service():
    """Create a TMDBService instance for testing."""
    service = TMDBService()
    service.api_key = "test_api_key"
    return service

@pytest.mark.asyncio
async def test_get_movie_success(tmdb_service, respx_mock):
    """Test successful movie fetch."""
    movie_id = 550
    url = f"{settings.TMDB_API_BASE_URL}/movie/{movie_id}"
    
    # Mock the API response
    respx_mock.get(url).mock(
        return_value=Response(200, json=MOCK_MOVIE_RESPONSE)
    )
    
    # Make the request
    response = await tmdb_service.get_movie(movie_id)
    
    assert response == MOCK_MOVIE_RESPONSE
    assert response["title"] == "Fight Club"

@pytest.mark.asyncio
async def test_get_movie_error(tmdb_service, respx_mock):
    """Test error handling for movie fetch."""
    movie_id = 999999
    url = f"{settings.TMDB_API_BASE_URL}/movie/{movie_id}"
    
    # Mock a 404 error response
    respx_mock.get(url).mock(
        return_value=Response(404, json={"status_message": "Movie not found"})
    )
    
    # Test that it raises the appropriate exception
    with pytest.raises(HTTPException) as exc_info:
        await tmdb_service.get_movie(movie_id)
    assert exc_info.value.status_code == 404
    assert "Movie not found" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_search_movies(tmdb_service, respx_mock):
    """Test movie search functionality."""
    query = "inception"
    url = f"{settings.TMDB_API_BASE_URL}/search/movie"
    mock_response = {
        "page": 1,
        "results": [{"id": 27205, "title": "Inception"}],
        "total_pages": 1
    }
    
    # Mock the search response
    respx_mock.get(url).mock(
        return_value=Response(200, json=mock_response)
    )
    
    response = await tmdb_service.search_movies(query)
    assert response["results"][0]["title"] == "Inception"

@pytest.mark.asyncio
async def test_get_movie_genres(tmdb_service, respx_mock):
    """Test fetching movie genres."""
    url = f"{settings.TMDB_API_BASE_URL}/genre/movie/list"
    
    # Mock the genres response
    respx_mock.get(url).mock(
        return_value=Response(200, json=MOCK_GENRE_RESPONSE)
    )
    
    genres = await tmdb_service.get_movie_genres()
    assert len(genres) == 2
    assert genres[0]["name"] == "Action"

@pytest.mark.asyncio
async def test_caching(tmdb_service, respx_mock):
    """Test that responses are properly cached."""
    movie_id = 550
    url = f"{settings.TMDB_API_BASE_URL}/movie/{movie_id}"
    
    # Enable caching for the test
    settings.CACHE_ENABLED = True
    
    # Mock the API response
    respx_mock.get(url).mock(
        return_value=Response(200, json=MOCK_MOVIE_RESPONSE)
    )
    
    # First request should hit the API
    response1 = await tmdb_service.get_movie(movie_id)
    
    # Second request should use cache
    response2 = await tmdb_service.get_movie(movie_id)
    
    assert response1 == response2
    # Verify that only one actual request was made
    assert respx_mock.calls.call_count == 1

@pytest.mark.asyncio
async def test_cache_expiration(tmdb_service, respx_mock):
    """Test that cache properly expires."""
    movie_id = 550
    url = f"{settings.TMDB_API_BASE_URL}/movie/{movie_id}"
    
    # Enable caching with a short expiration
    settings.CACHE_ENABLED = True
    tmdb_service.cache_expire_minutes = 0  # Immediate expiration
    
    # Mock the API response
    respx_mock.get(url).mock(
        return_value=Response(200, json=MOCK_MOVIE_RESPONSE)
    )
    
    # First request
    await tmdb_service.get_movie(movie_id)
    
    # Second request should hit API again due to expired cache
    await tmdb_service.get_movie(movie_id)
    
    # Verify that two requests were made
    assert respx_mock.calls.call_count == 2 