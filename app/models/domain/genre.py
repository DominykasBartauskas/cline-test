from sqlalchemy import Column, Integer, String

from app.models.domain.base import Base


class Genre(Base):
    """Genre model."""
    
    # TMDB ID
    tmdb_id = Column(Integer, nullable=False, index=True)
    
    # Name
    name = Column(String, nullable=False, index=True)
    
    # Type (movie, tv)
    type = Column(String, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<Genre(id={self.id}, name={self.name}, type={self.type})>"
