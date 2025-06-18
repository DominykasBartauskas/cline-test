from datetime import date
from typing import List, Optional

from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.models.domain.base import Base
from app.models.domain.genre import Genre

# Association table for movie-genre relationship
movie_genre = Table(
    "movie_genre",
    Base.metadata,
    Column("movie_id", ForeignKey("movie.id"), primary_key=True),
    Column("genre_id", ForeignKey("genre.id"), primary_key=True),
)


class Movie(Base):
    """Movie model."""
    
    # TMDB ID
    tmdb_id = Column(Integer, nullable=False, index=True)
    
    # Basic info
    title = Column(String, nullable=False, index=True)
    original_title = Column(String, nullable=True)
    overview = Column(String, nullable=True)
    
    # Images
    poster_path = Column(String, nullable=True)
    backdrop_path = Column(String, nullable=True)
    
    # Release info
    release_date = Column(Date, nullable=True, index=True)
    
    # Ratings
    popularity = Column(Float, nullable=True, index=True)
    vote_average = Column(Float, nullable=True, index=True)
    vote_count = Column(Integer, nullable=True)
    
    # Additional info
    adult = Column(Boolean, nullable=True)
    original_language = Column(String, nullable=True)
    
    # Credits
    director_name = Column(String, nullable=True)
    director_tmdb_id = Column(Integer, nullable=True)
    actor1_name = Column(String, nullable=True)
    actor1_tmdb_id = Column(Integer, nullable=True)
    actor2_name = Column(String, nullable=True)
    actor2_tmdb_id = Column(Integer, nullable=True)
    actor3_name = Column(String, nullable=True)
    actor3_tmdb_id = Column(Integer, nullable=True)
    
    # Relationships
    genres = relationship(
        "Genre",
        secondary=movie_genre,
        lazy="selectin",
        backref="movies",
    )
    
    def __repr__(self) -> str:
        return f"<Movie(id={self.id}, title={self.title})>"
