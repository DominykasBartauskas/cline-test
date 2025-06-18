from datetime import date
from typing import List, Optional

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.models.domain.base import Base
from app.models.domain.genre import Genre

# Association table for tv_show-genre relationship
tv_show_genre = Table(
    "tv_show_genre",
    Base.metadata,
    Column("tv_show_id", ForeignKey("tvshow.id"), primary_key=True),
    Column("genre_id", ForeignKey("genre.id"), primary_key=True),
)


class TVShow(Base):
    """TV show model."""
    
    # TMDB ID
    tmdb_id = Column(Integer, nullable=False, index=True)
    
    # Basic info
    name = Column(String, nullable=False, index=True)
    original_name = Column(String, nullable=True)
    overview = Column(String, nullable=True)
    
    # Images
    poster_path = Column(String, nullable=True)
    backdrop_path = Column(String, nullable=True)
    
    # Air dates
    first_air_date = Column(Date, nullable=True, index=True)
    
    # Ratings
    popularity = Column(Float, nullable=True, index=True)
    vote_average = Column(Float, nullable=True, index=True)
    vote_count = Column(Integer, nullable=True)
    
    # Additional info
    original_language = Column(String, nullable=True)
    number_of_seasons = Column(Integer, nullable=True)
    number_of_episodes = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    
    # Type (tv, anime)
    type = Column(String, nullable=True, index=True)
    
    # Relationships
    genres = relationship(
        "Genre",
        secondary=tv_show_genre,
        lazy="selectin",
        backref="tv_shows",
    )
    
    def __repr__(self) -> str:
        return f"<TVShow(id={self.id}, name={self.name})>"
