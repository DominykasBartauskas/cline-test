from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.domain.base import Base
from app.models.domain.movie import Movie
from app.models.domain.tv_show import TVShow

# Association table for user-movie watchlist
user_movie_watchlist = Table(
    "user_movie_watchlist",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("movie_id", ForeignKey("movie.id"), primary_key=True),
)

# Association table for user-tv_show watchlist
user_tv_show_watchlist = Table(
    "user_tv_show_watchlist",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("tv_show_id", ForeignKey("tvshow.id"), primary_key=True),
)


class User(Base):
    """User model."""
    
    # User info
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # User status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relationships
    watchlist_movies = relationship(
        "Movie",
        secondary=user_movie_watchlist,
        lazy="selectin",
        backref="watchlisted_by",
    )
    
    watchlist_tv_shows = relationship(
        "TVShow",
        secondary=user_tv_show_watchlist,
        lazy="selectin",
        backref="watchlisted_by",
    )
    
    movie_ratings = relationship(
        "MovieRating",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    tv_show_ratings = relationship(
        "TVShowRating",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"


class MovieRating(Base):
    """Movie rating model."""
    
    # User ID
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    
    # Movie ID
    movie_id = Column(UUID(as_uuid=True), ForeignKey("movie.id"), nullable=False)
    
    # Rating
    rating = Column(Float, nullable=False)
    
    # Comment
    comment = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="movie_ratings")
    movie = relationship("Movie", backref="ratings")
    
    def __repr__(self) -> str:
        return f"<MovieRating(user_id={self.user_id}, movie_id={self.movie_id}, rating={self.rating})>"


class TVShowRating(Base):
    """TV show rating model."""
    
    # User ID
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    
    # TV show ID
    tv_show_id = Column(UUID(as_uuid=True), ForeignKey("tvshow.id"), nullable=False)
    
    # Rating
    rating = Column(Float, nullable=False)
    
    # Comment
    comment = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tv_show_ratings")
    tv_show = relationship("TVShow", backref="ratings")
    
    def __repr__(self) -> str:
        return f"<TVShowRating(user_id={self.user_id}, tv_show_id={self.tv_show_id}, rating={self.rating})>"
