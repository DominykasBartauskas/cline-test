from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.models.schemas.base import BaseSchema


class GenreBase(BaseSchema):
    """Base schema for genre data."""
    
    name: str
    type: str  # 'movie' or 'tv'


class GenreCreate(GenreBase):
    """Schema for creating a genre."""
    
    tmdb_id: int


class GenreUpdate(BaseSchema):
    """Schema for updating a genre."""
    
    name: Optional[str] = None
    type: Optional[str] = None


class GenreResponse(GenreBase):
    """Schema for genre response."""
    
    id: UUID
    tmdb_id: int
