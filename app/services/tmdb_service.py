import asyncio
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx
import logfire
from fastapi import HTTPException

from app.core.config import settings


class TMDBService:
    """Service for interacting with TMDB API."""
    
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_API_BASE_URL
        self.cache = {}
        self.cache_expire_minutes = settings.CACHE_EXPIRE_MINUTES
    
    async def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to the TMDB API."""
        if params is None:
            params = {}
        
        # Add API key to params
        params["api_key"] = self.api_key
        
        # Check cache if enabled
        cache_key = f"{endpoint}:{str(params)}"
        if settings.CACHE_ENABLED and cache_key in self.cache:
            cached_data, expire_time = self.cache[cache_key]
            if datetime.utcnow() < expire_time:
                logfire.debug("Cache hit", endpoint=endpoint)
                return cached_data
        
        # Make request
        url = f"{self.base_url}{endpoint}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                # Cache response if enabled
                if settings.CACHE_ENABLED:
                    expire_time = datetime.utcnow() + timedelta(minutes=self.cache_expire_minutes)
                    self.cache[cache_key] = (data, expire_time)
                
                return data
        except httpx.HTTPStatusError as e:
            logfire.error(
                "TMDB API HTTP error",
                endpoint=endpoint,
                status_code=e.response.status_code,
                detail=e.response.text,
            )
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"TMDB API error: {e.response.text}",
            )
        except httpx.RequestError as e:
            logfire.error("TMDB API request error", endpoint=endpoint, error=str(e))
            raise HTTPException(status_code=503, detail=f"TMDB API request error: {str(e)}")
    
    async def get_movie(self, movie_id: int) -> Dict[str, Any]:
        """Get movie details from TMDB."""
        endpoint = f"/movie/{movie_id}"
        params = {"append_to_response": "credits"}
        return await self._make_request(endpoint, params)
    
    async def get_popular_movies(self, page: int = 1) -> Dict[str, Any]:
        """Get popular movies from TMDB."""
        endpoint = "/movie/popular"
        params = {"page": page}
        return await self._make_request(endpoint, params)
    
    async def get_top_rated_movies(self, page: int = 1) -> Dict[str, Any]:
        """Get top rated movies from TMDB."""
        endpoint = "/movie/top_rated"
        params = {"page": page}
        return await self._make_request(endpoint, params)
    
    async def get_upcoming_movies(self, page: int = 1) -> Dict[str, Any]:
        """Get upcoming movies from TMDB."""
        endpoint = "/movie/upcoming"
        params = {"page": page}
        return await self._make_request(endpoint, params)
    
    async def get_now_playing_movies(self, page: int = 1) -> Dict[str, Any]:
        """Get now playing movies from TMDB."""
        endpoint = "/movie/now_playing"
        params = {"page": page}
        return await self._make_request(endpoint, params)
    
    async def get_tv_show(self, tv_id: int) -> Dict[str, Any]:
        """Get TV show details from TMDB."""
        endpoint = f"/tv/{tv_id}"
        return await self._make_request(endpoint)
    
    async def get_popular_tv_shows(self, page: int = 1) -> Dict[str, Any]:
        """Get popular TV shows from TMDB."""
        endpoint = "/tv/popular"
        params = {"page": page}
        return await self._make_request(endpoint, params)
    
    async def get_top_rated_tv_shows(self, page: int = 1) -> Dict[str, Any]:
        """Get top rated TV shows from TMDB."""
        endpoint = "/tv/top_rated"
        params = {"page": page}
        return await self._make_request(endpoint, params)
    
    async def get_on_the_air_tv_shows(self, page: int = 1) -> Dict[str, Any]:
        """Get on the air TV shows from TMDB."""
        endpoint = "/tv/on_the_air"
        params = {"page": page}
        return await self._make_request(endpoint, params)
    
    async def get_airing_today_tv_shows(self, page: int = 1) -> Dict[str, Any]:
        """Get TV shows airing today from TMDB."""
        endpoint = "/tv/airing_today"
        params = {"page": page}
        return await self._make_request(endpoint, params)
    
    async def search_movies(
        self, query: str, page: int = 1, year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search for movies in TMDB."""
        endpoint = "/search/movie"
        params = {"query": query, "page": page}
        if year:
            params["year"] = year
        return await self._make_request(endpoint, params)
    
    async def search_tv_shows(
        self, query: str, page: int = 1, first_air_date_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search for TV shows in TMDB."""
        endpoint = "/search/tv"
        params = {"query": query, "page": page}
        if first_air_date_year:
            params["first_air_date_year"] = first_air_date_year
        return await self._make_request(endpoint, params)
    
    async def search_multi(self, query: str, page: int = 1) -> Dict[str, Any]:
        """Search for movies and TV shows in TMDB."""
        endpoint = "/search/multi"
        params = {"query": query, "page": page}
        return await self._make_request(endpoint, params)
    
    async def get_movie_genres(self) -> List[Dict[str, Any]]:
        """Get movie genres from TMDB."""
        endpoint = "/genre/movie/list"
        response = await self._make_request(endpoint)
        return response.get("genres", [])
    
    async def get_tv_genres(self) -> List[Dict[str, Any]]:
        """Get TV show genres from TMDB."""
        endpoint = "/genre/tv/list"
        response = await self._make_request(endpoint)
        return response.get("genres", [])
    
    async def get_movie_credits(self, movie_id: int) -> Dict[str, Any]:
        """Get movie credits from TMDB."""
        endpoint = f"/movie/{movie_id}/credits"
        return await self._make_request(endpoint)
    
    async def get_tv_credits(self, tv_id: int) -> Dict[str, Any]:
        """Get TV show credits from TMDB."""
        endpoint = f"/tv/{tv_id}/credits"
        return await self._make_request(endpoint)


# Create a singleton instance
tmdb_service = TMDBService()
