from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.domain.base import Base


class Genre(Base):
    """Genre model."""
    
    # TMDB ID
    tmdb_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Name
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    # Type (movie, tv)
    type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<Genre(id={self.id}, name={self.name}, type={self.type})>"
