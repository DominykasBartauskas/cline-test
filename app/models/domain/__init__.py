from app.db.database import Base
from app.models.domain.movie import Movie, movie_genre
from app.models.domain.tv_show import TVShow, tv_show_genre
from app.models.domain.genre import Genre
from app.models.domain.user import User, MovieRating, TVShowRating, user_movie_watchlist, user_tv_show_watchlist

# Import all models here to make them available for Alembic
__all__ = [
    "Base",
    "Movie",
    "TVShow",
    "Genre",
    "User",
    "MovieRating",
    "TVShowRating",
    "movie_genre",
    "tv_show_genre",
    "user_movie_watchlist",
    "user_tv_show_watchlist",
]
