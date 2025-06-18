from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

import logfire
from fastapi import Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.domain.genre import Genre
from app.models.domain.tv_show import TVShow
from app.models.schemas.tv_show import TVShowCreate, TVShowSearchParams, TVShowUpdate
from app.services.tmdb_service import tmdb_service


class TVShowService:
    """Service for TV show-related operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_tv_show_by_id(self, tv_show_id: UUID) -> TVShow:
        """Get a TV show by ID."""
        query = (
            select(TVShow)
            .options(selectinload(TVShow.genres))
            .where(TVShow.id == tv_show_id)
        )
        result = await self.db.execute(query)
        tv_show = result.scalar_one_or_none()
        
        if not tv_show:
            raise HTTPException(status_code=404, detail="TV show not found")
        
        return tv_show
    
    async def get_tv_show_by_tmdb_id(self, tmdb_id: int) -> Optional[TVShow]:
        """Get a TV show by TMDB ID."""
        query = (
            select(TVShow)
            .options(selectinload(TVShow.genres))
            .where(TVShow.tmdb_id == tmdb_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_tv_shows(
        self, skip: int = 0, limit: int = 100, sort_by: str = "popularity"
    ) -> Tuple[List[TVShow], int]:
        """Get a list of TV shows."""
        # Count total
        count_query = select(func.count()).select_from(TVShow)
        total = await self.db.scalar(count_query)
        
        # Get TV shows
        query = select(TVShow).options(selectinload(TVShow.genres))
        
        # Apply sorting
        if sort_by == "popularity":
            query = query.order_by(TVShow.popularity.desc())
        elif sort_by == "name":
            query = query.order_by(TVShow.name)
        elif sort_by == "first_air_date":
            query = query.order_by(TVShow.first_air_date.desc())
        elif sort_by == "vote_average":
            query = query.order_by(TVShow.vote_average.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        tv_shows = result.scalars().all()
        
        return tv_shows, total
    
    async def search_tv_shows(
        self, params: TVShowSearchParams
    ) -> Tuple[List[TVShow], int]:
        """Search for TV shows."""
        query = select(TVShow).options(selectinload(TVShow.genres))
        
        # Apply filters
        if params.query:
            query = query.filter(TVShow.name.ilike(f"%{params.query}%"))
        
        if params.genre_id:
            query = query.join(TVShow.genres).filter(Genre.tmdb_id == params.genre_id)
        
        if params.year:
            query = query.filter(
                func.extract("year", TVShow.first_air_date) == params.year
            )
        
        # Count total
        count_query = query.with_only_columns(func.count())
        total = await self.db.scalar(count_query)
        
        # Apply sorting
        if params.sort_by:
            sort_field, sort_dir = params.sort_by.split(".")
            if sort_field == "popularity":
                if sort_dir == "desc":
                    query = query.order_by(TVShow.popularity.desc())
                else:
                    query = query.order_by(TVShow.popularity)
            elif sort_field == "name":
                if sort_dir == "desc":
                    query = query.order_by(TVShow.name.desc())
                else:
                    query = query.order_by(TVShow.name)
            elif sort_field == "first_air_date":
                if sort_dir == "desc":
                    query = query.order_by(TVShow.first_air_date.desc())
                else:
                    query = query.order_by(TVShow.first_air_date)
            elif sort_field == "vote_average":
                if sort_dir == "desc":
                    query = query.order_by(TVShow.vote_average.desc())
                else:
                    query = query.order_by(TVShow.vote_average)
        
        # Apply pagination
        skip = (params.page - 1) * params.size
        query = query.offset(skip).limit(params.size)
        
        result = await self.db.execute(query)
        tv_shows = result.scalars().all()
        
        return tv_shows, total
    
    async def create_tv_show(self, tv_show_data: TVShowCreate) -> TVShow:
        """Create a new TV show."""
        # Check if TV show already exists
        existing_tv_show = await self.get_tv_show_by_tmdb_id(tv_show_data.tmdb_id)
        if existing_tv_show:
            return existing_tv_show
        
        # Create new TV show
        tv_show = TVShow(
            tmdb_id=tv_show_data.tmdb_id,
            name=tv_show_data.name,
            original_name=tv_show_data.original_name,
            overview=tv_show_data.overview,
            poster_path=tv_show_data.poster_path,
            backdrop_path=tv_show_data.backdrop_path,
            first_air_date=tv_show_data.first_air_date,
            popularity=tv_show_data.popularity,
            vote_average=tv_show_data.vote_average,
            vote_count=tv_show_data.vote_count,
            original_language=tv_show_data.original_language,
            number_of_seasons=tv_show_data.number_of_seasons,
            number_of_episodes=tv_show_data.number_of_episodes,
            status=tv_show_data.status,
            type=tv_show_data.type,
        )
        
        # Add genres if provided
        if tv_show_data.genre_ids:
            query = select(Genre).where(
                Genre.tmdb_id.in_(tv_show_data.genre_ids),
                Genre.type == "tv",
            )
            result = await self.db.execute(query)
            genres = result.scalars().all()
            tv_show.genres = genres
        
        self.db.add(tv_show)
        await self.db.commit()
        await self.db.refresh(tv_show)
        
        return tv_show
    
    async def update_tv_show(
        self, tv_show_id: UUID, tv_show_data: TVShowUpdate
    ) -> TVShow:
        """Update a TV show."""
        tv_show = await self.get_tv_show_by_id(tv_show_id)
        
        # Update fields
        for field, value in tv_show_data.model_dump(exclude_unset=True).items():
            if field != "genre_ids" and value is not None:
                setattr(tv_show, field, value)
        
        # Update genres if provided
        if tv_show_data.genre_ids:
            query = select(Genre).where(
                Genre.tmdb_id.in_(tv_show_data.genre_ids),
                Genre.type == "tv",
            )
            result = await self.db.execute(query)
            genres = result.scalars().all()
            tv_show.genres = genres
        
        await self.db.commit()
        await self.db.refresh(tv_show)
        
        return tv_show
    
    async def delete_tv_show(self, tv_show_id: UUID) -> None:
        """Delete a TV show."""
        tv_show = await self.get_tv_show_by_id(tv_show_id)
        await self.db.delete(tv_show)
        await self.db.commit()
    
    async def sync_tv_show_from_tmdb(self, tmdb_id: int) -> TVShow:
        """Sync a TV show from TMDB."""
        # Check if TV show already exists
        existing_tv_show = await self.get_tv_show_by_tmdb_id(tmdb_id)
        
        # Get TV show data from TMDB
        tmdb_tv_show = await tmdb_service.get_tv_show(tmdb_id)
        
        # Parse first air date
        first_air_date = None
        if tmdb_tv_show.get("first_air_date"):
            try:
                first_air_date = datetime.strptime(
                    tmdb_tv_show["first_air_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                logfire.warning(
                    "Invalid first air date format",
                    first_air_date=tmdb_tv_show["first_air_date"],
                )
        
        # Determine type (TV show or anime)
        show_type = "tv"
        if "Animation" in [genre.get("name") for genre in tmdb_tv_show.get("genres", [])]:
            # Check if it's likely an anime (Japanese animation)
            if tmdb_tv_show.get("original_language") == "ja":
                show_type = "anime"
        
        # Create TV show data
        tv_show_data = TVShowCreate(
            tmdb_id=tmdb_tv_show["id"],
            name=tmdb_tv_show["name"],
            original_name=tmdb_tv_show.get("original_name"),
            overview=tmdb_tv_show.get("overview"),
            poster_path=tmdb_tv_show.get("poster_path"),
            backdrop_path=tmdb_tv_show.get("backdrop_path"),
            first_air_date=first_air_date,
            popularity=tmdb_tv_show.get("popularity"),
            vote_average=tmdb_tv_show.get("vote_average"),
            vote_count=tmdb_tv_show.get("vote_count"),
            original_language=tmdb_tv_show.get("original_language"),
            number_of_seasons=tmdb_tv_show.get("number_of_seasons"),
            number_of_episodes=tmdb_tv_show.get("number_of_episodes"),
            status=tmdb_tv_show.get("status"),
            type=show_type,
            genre_ids=[genre["id"] for genre in tmdb_tv_show.get("genres", [])],
        )
        
        if existing_tv_show:
            # Update existing TV show
            for field, value in tv_show_data.model_dump().items():
                if field != "genre_ids":
                    setattr(existing_tv_show, field, value)
            
            # Update genres
            if tv_show_data.genre_ids:
                query = select(Genre).where(
                    Genre.tmdb_id.in_(tv_show_data.genre_ids),
                    Genre.type == "tv",
                )
                result = await self.db.execute(query)
                genres = result.scalars().all()
                existing_tv_show.genres = genres
            
            await self.db.commit()
            await self.db.refresh(existing_tv_show)
            
            return existing_tv_show
        else:
            # Create new TV show
            return await self.create_tv_show(tv_show_data)
    
    async def sync_popular_tv_shows(self) -> List[TVShow]:
        """Sync popular TV shows from TMDB."""
        # Get popular TV shows from TMDB
        tmdb_tv_shows = await tmdb_service.get_popular_tv_shows()
        
        # Sync each TV show
        tv_shows = []
        for tmdb_tv_show in tmdb_tv_shows.get("results", []):
            try:
                tv_show = await self.sync_tv_show_from_tmdb(tmdb_tv_show["id"])
                tv_shows.append(tv_show)
            except Exception as e:
                logfire.error(
                    "Error syncing TV show",
                    tmdb_id=tmdb_tv_show["id"],
                    error=str(e),
                )
        
        return tv_shows


async def get_tv_show_service(db: AsyncSession = Depends(get_db)) -> TVShowService:
    """Dependency for getting the TV show service."""
    return TVShowService(db)
