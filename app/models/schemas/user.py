from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.schemas.base import BaseSchema
from app.models.schemas.movie import MovieResponse
from app.models.schemas.tv_show import TVShowResponse


class UserBase(BaseSchema):
    """Base schema for user data."""
    
    email: EmailStr
    username: str
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """Schema for creating a user."""
    
    password: str


class UserUpdate(BaseSchema):
    """Schema for updating a user."""
    
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    
    id: UUID


class UserWithWatchlistResponse(UserResponse):
    """Schema for user response with watchlist."""
    
    watchlist_movies: List[MovieResponse] = []
    watchlist_tv_shows: List[TVShowResponse] = []


class Token(BaseModel):
    """Schema for token."""
    
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Schema for token payload."""
    
    sub: Optional[UUID] = None


class MovieRatingBase(BaseSchema):
    """Base schema for movie rating."""
    
    rating: float
    comment: Optional[str] = None


class MovieRatingCreate(MovieRatingBase):
    """Schema for creating a movie rating."""
    
    movie_id: UUID


class MovieRatingUpdate(BaseSchema):
    """Schema for updating a movie rating."""
    
    rating: Optional[float] = None
    comment: Optional[str] = None


class MovieRatingResponse(MovieRatingBase):
    """Schema for movie rating response."""
    
    id: UUID
    user_id: UUID
    movie_id: UUID
    movie: Optional[MovieResponse] = None


class TVShowRatingBase(BaseSchema):
    """Base schema for TV show rating."""
    
    rating: float
    comment: Optional[str] = None


class TVShowRatingCreate(TVShowRatingBase):
    """Schema for creating a TV show rating."""
    
    tv_show_id: UUID


class TVShowRatingUpdate(BaseSchema):
    """Schema for updating a TV show rating."""
    
    rating: Optional[float] = None
    comment: Optional[str] = None


class TVShowRatingResponse(TVShowRatingBase):
    """Schema for TV show rating response."""
    
    id: UUID
    user_id: UUID
    tv_show_id: UUID
    tv_show: Optional[TVShowResponse] = None
