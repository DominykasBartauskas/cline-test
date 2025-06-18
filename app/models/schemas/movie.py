from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.models.schemas.base import BaseSchema
from app.models.schemas.genre import GenreResponse


class MovieBase(BaseSchema):
    """Base schema for movie data."""
    
    title: str
    original_title: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: Optional[date] = None
    popularity: Optional[float] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    adult: bool = False
    original_language: Optional[str] = None


class MovieCreate(MovieBase):
    """Schema for creating a movie."""
    
    tmdb_id: int
    genre_ids: Optional[List[int]] = None
    director_name: Optional[str] = None
    director_tmdb_id: Optional[int] = None
    actor1_name: Optional[str] = None
    actor1_tmdb_id: Optional[int] = None
    actor2_name: Optional[str] = None
    actor2_tmdb_id: Optional[int] = None
    actor3_name: Optional[str] = None
    actor3_tmdb_id: Optional[int] = None


class MovieUpdate(BaseSchema):
    """Schema for updating a movie."""
    
    title: Optional[str] = None
    original_title: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: Optional[date] = None
    popularity: Optional[float] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    adult: Optional[bool] = None
    original_language: Optional[str] = None
    genre_ids: Optional[List[int]] = None
    director_name: Optional[str] = None
    director_tmdb_id: Optional[int] = None
    actor1_name: Optional[str] = None
    actor1_tmdb_id: Optional[int] = None
    actor2_name: Optional[str] = None
    actor2_tmdb_id: Optional[int] = None
    actor3_name: Optional[str] = None
    actor3_tmdb_id: Optional[int] = None


class MovieResponse(MovieBase):
    """Schema for movie response."""
    
    id: UUID
    tmdb_id: int
    genres: List[GenreResponse] = []
    director_name: Optional[str] = None
    director_tmdb_id: Optional[int] = None
    actor1_name: Optional[str] = None
    actor1_tmdb_id: Optional[int] = None
    actor2_name: Optional[str] = None
    actor2_tmdb_id: Optional[int] = None
    actor3_name: Optional[str] = None
    actor3_tmdb_id: Optional[int] = None
    
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


class MovieSearchParams(BaseSchema):
    """Schema for movie search parameters."""
    
    query: Optional[str] = None
    genre_id: Optional[int] = None
    year: Optional[int] = None
    sort_by: Optional[str] = "popularity.desc"
    page: int = 1
    size: int = 20
