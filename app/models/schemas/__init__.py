from app.models.schemas.base import BaseSchema, BaseAPIResponse, PaginatedResponse
from app.models.schemas.genre import GenreBase, GenreCreate, GenreUpdate, GenreResponse
from app.models.schemas.movie import (
    MovieBase,
    MovieCreate,
    MovieUpdate,
    MovieResponse,
    MovieSearchParams,
)
from app.models.schemas.tv_show import (
    TVShowBase,
    TVShowCreate,
    TVShowUpdate,
    TVShowResponse,
    TVShowSearchParams,
)
from app.models.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithWatchlistResponse,
    Token,
    TokenPayload,
    MovieRatingBase,
    MovieRatingCreate,
    MovieRatingUpdate,
    MovieRatingResponse,
    TVShowRatingBase,
    TVShowRatingCreate,
    TVShowRatingUpdate,
    TVShowRatingResponse,
)

# Export all schemas
__all__ = [
    "BaseSchema",
    "BaseAPIResponse",
    "PaginatedResponse",
    "GenreBase",
    "GenreCreate",
    "GenreUpdate",
    "GenreResponse",
    "MovieBase",
    "MovieCreate",
    "MovieUpdate",
    "MovieResponse",
    "MovieSearchParams",
    "TVShowBase",
    "TVShowCreate",
    "TVShowUpdate",
    "TVShowResponse",
    "TVShowSearchParams",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserWithWatchlistResponse",
    "Token",
    "TokenPayload",
    "MovieRatingBase",
    "MovieRatingCreate",
    "MovieRatingUpdate",
    "MovieRatingResponse",
    "TVShowRatingBase",
    "TVShowRatingCreate",
    "TVShowRatingUpdate",
    "TVShowRatingResponse",
]
