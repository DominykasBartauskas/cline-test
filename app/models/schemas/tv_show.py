from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.models.schemas.base import BaseSchema
from app.models.schemas.genre import GenreResponse


class TVShowBase(BaseSchema):
    """Base schema for TV show data."""
    
    name: str
    original_name: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    first_air_date: Optional[date] = None
    popularity: Optional[float] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    original_language: Optional[str] = None
    number_of_seasons: Optional[int] = None
    number_of_episodes: Optional[int] = None
    status: Optional[str] = None
    type: Optional[str] = None  # TV show, anime, etc.


class TVShowCreate(TVShowBase):
    """Schema for creating a TV show."""
    
    tmdb_id: int
    genre_ids: Optional[List[int]] = None


class TVShowUpdate(BaseSchema):
    """Schema for updating a TV show."""
    
    name: Optional[str] = None
    original_name: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    first_air_date: Optional[date] = None
    popularity: Optional[float] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    original_language: Optional[str] = None
    number_of_seasons: Optional[int] = None
    number_of_episodes: Optional[int] = None
    status: Optional[str] = None
    type: Optional[str] = None
    genre_ids: Optional[List[int]] = None


class TVShowResponse(TVShowBase):
    """Schema for TV show response."""
    
    id: UUID
    tmdb_id: int
    genres: List[GenreResponse] = []
    
    # Add computed fields
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    
    def model_post_init(self, __context):
        """Post-init processing."""
        from app.core.config import settings
        
        # Generate full URLs for images
        if self.poster_path:
            self.poster_url = f"{settings.TMDB_IMAGE_BASE_URL}/w500{self.poster_path}"
        if self.backdrop_path:
            self.backdrop_url = f"{settings.TMDB_IMAGE_BASE_URL}/original{self.backdrop_path}"


class TVShowSearchParams(BaseSchema):
    """Schema for TV show search parameters."""
    
    query: Optional[str] = None
    genre_id: Optional[int] = None
    year: Optional[int] = None
    sort_by: Optional[str] = "popularity.desc"
    page: int = 1
    size: int = 20
