from typing import Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.domain.genre import Genre
from app.models.schemas.genre import GenreCreate, GenreUpdate
from app.services.tmdb_service import tmdb_service


class GenreService:
    """Service for genre-related operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_genre_by_id(self, genre_id: UUID) -> Genre:
        """Get a genre by ID."""
        query = select(Genre).where(Genre.id == genre_id)
        result = await self.db.execute(query)
        genre = result.scalar_one_or_none()
        
        if not genre:
            raise HTTPException(status_code=404, detail="Genre not found")
        
        return genre
    
    async def get_genre_by_tmdb_id(self, tmdb_id: int, type: str) -> Optional[Genre]:
        """Get a genre by TMDB ID and type."""
        query = select(Genre).where(Genre.tmdb_id == tmdb_id, Genre.type == type)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_genres(self, type: Optional[str] = None) -> List[Genre]:
        """Get a list of genres."""
        query = select(Genre)
        
        if type:
            query = query.where(Genre.type == type)
        
        query = query.order_by(Genre.name)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_genre(self, genre_data: GenreCreate) -> Genre:
        """Create a new genre."""
        # Check if genre already exists
        existing_genre = await self.get_genre_by_tmdb_id(
            genre_data.tmdb_id, genre_data.type
        )
        if existing_genre:
            return existing_genre
        
        # Create new genre
        genre = Genre(
            tmdb_id=genre_data.tmdb_id,
            name=genre_data.name,
            type=genre_data.type,
        )
        
        self.db.add(genre)
        await self.db.commit()
        await self.db.refresh(genre)
        
        return genre
    
    async def update_genre(self, genre_id: UUID, genre_data: GenreUpdate) -> Genre:
        """Update a genre."""
        genre = await self.get_genre_by_id(genre_id)
        
        # Update fields
        for field, value in genre_data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(genre, field, value)
        
        await self.db.commit()
        await self.db.refresh(genre)
        
        return genre
    
    async def delete_genre(self, genre_id: UUID) -> None:
        """Delete a genre."""
        genre = await self.get_genre_by_id(genre_id)
        await self.db.delete(genre)
        await self.db.commit()
    
    async def sync_genres_from_tmdb(self) -> Tuple[List[Genre], List[Genre]]:
        """Sync genres from TMDB."""
        # Get movie genres from TMDB
        tmdb_movie_genres = await tmdb_service.get_movie_genres()
        
        # Get TV genres from TMDB
        tmdb_tv_genres = await tmdb_service.get_tv_genres()
        
        # Sync movie genres
        movie_genres = []
        for tmdb_genre in tmdb_movie_genres:
            genre_data = GenreCreate(
                tmdb_id=tmdb_genre["id"],
                name=tmdb_genre["name"],
                type="movie",
            )
            genre = await self.create_genre(genre_data)
            movie_genres.append(genre)
        
        # Sync TV genres
        tv_genres = []
        for tmdb_genre in tmdb_tv_genres:
            genre_data = GenreCreate(
                tmdb_id=tmdb_genre["id"],
                name=tmdb_genre["name"],
                type="tv",
            )
            genre = await self.create_genre(genre_data)
            tv_genres.append(genre)
        
        return movie_genres, tv_genres


async def get_genre_service(db: AsyncSession = Depends(get_db)) -> GenreService:
    """Dependency for getting the genre service."""
    return GenreService(db)
