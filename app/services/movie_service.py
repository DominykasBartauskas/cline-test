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
from app.models.domain.movie import Movie
from app.models.schemas.movie import MovieCreate, MovieSearchParams, MovieUpdate
from app.services.tmdb_service import tmdb_service


class MovieService:
    """Service for movie-related operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_movie_by_id(self, movie_id: UUID) -> Movie:
        """Get a movie by ID."""
        query = (
            select(Movie)
            .options(selectinload(Movie.genres))
            .where(Movie.id == movie_id)
        )
        result = await self.db.execute(query)
        movie = result.scalar_one_or_none()
        
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        return movie
    
    async def get_movie_by_tmdb_id(self, tmdb_id: int) -> Optional[Movie]:
        """Get a movie by TMDB ID."""
        query = (
            select(Movie)
            .options(selectinload(Movie.genres))
            .where(Movie.tmdb_id == tmdb_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_movies(
        self, skip: int = 0, limit: int = 100, sort_by: str = "popularity"
    ) -> Tuple[List[Movie], int]:
        """Get a list of movies."""
        # Count total
        count_query = select(func.count()).select_from(Movie)
        total = await self.db.scalar(count_query)
        
        # Get movies
        query = select(Movie).options(selectinload(Movie.genres))
        
        # Apply sorting
        if sort_by == "popularity":
            query = query.order_by(Movie.popularity.desc())
        elif sort_by == "title":
            query = query.order_by(Movie.title)
        elif sort_by == "release_date":
            query = query.order_by(Movie.release_date.desc())
        elif sort_by == "vote_average":
            query = query.order_by(Movie.vote_average.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        movies = result.scalars().all()
        
        return movies, total
    
    async def search_movies(
        self, params: MovieSearchParams
    ) -> Tuple[List[Movie], int]:
        """Search for movies."""
        query = select(Movie).options(selectinload(Movie.genres))
        
        # Apply filters
        if params.query:
            query = query.filter(Movie.title.ilike(f"%{params.query}%"))
        
        if params.genre_id:
            query = query.join(Movie.genres).filter(Genre.tmdb_id == params.genre_id)
        
        if params.year:
            query = query.filter(
                func.extract("year", Movie.release_date) == params.year
            )
        
        # Count total
        count_query = query.with_only_columns(func.count())
        total = await self.db.scalar(count_query)
        
        # Apply sorting
        if params.sort_by:
            sort_field, sort_dir = params.sort_by.split(".")
            if sort_field == "popularity":
                if sort_dir == "desc":
                    query = query.order_by(Movie.popularity.desc())
                else:
                    query = query.order_by(Movie.popularity)
            elif sort_field == "title":
                if sort_dir == "desc":
                    query = query.order_by(Movie.title.desc())
                else:
                    query = query.order_by(Movie.title)
            elif sort_field == "release_date":
                if sort_dir == "desc":
                    query = query.order_by(Movie.release_date.desc())
                else:
                    query = query.order_by(Movie.release_date)
            elif sort_field == "vote_average":
                if sort_dir == "desc":
                    query = query.order_by(Movie.vote_average.desc())
                else:
                    query = query.order_by(Movie.vote_average)
        
        # Apply pagination
        skip = (params.page - 1) * params.size
        query = query.offset(skip).limit(params.size)
        
        result = await self.db.execute(query)
        movies = result.scalars().all()
        
        return movies, total
    
    async def create_movie(self, movie_data: MovieCreate) -> Movie:
        """Create a new movie."""
        # Check if movie already exists
        existing_movie = await self.get_movie_by_tmdb_id(movie_data.tmdb_id)
        if existing_movie:
            return existing_movie
        
        # Create new movie
        movie = Movie(
            tmdb_id=movie_data.tmdb_id,
            title=movie_data.title,
            original_title=movie_data.original_title,
            overview=movie_data.overview,
            poster_path=movie_data.poster_path,
            backdrop_path=movie_data.backdrop_path,
            release_date=movie_data.release_date,
            popularity=movie_data.popularity,
            vote_average=movie_data.vote_average,
            vote_count=movie_data.vote_count,
            adult=movie_data.adult,
            original_language=movie_data.original_language,
            director_name=movie_data.director_name,
            director_tmdb_id=movie_data.director_tmdb_id,
            actor1_name=movie_data.actor1_name,
            actor1_tmdb_id=movie_data.actor1_tmdb_id,
            actor2_name=movie_data.actor2_name,
            actor2_tmdb_id=movie_data.actor2_tmdb_id,
            actor3_name=movie_data.actor3_name,
            actor3_tmdb_id=movie_data.actor3_tmdb_id,
        )
        
        # Add genres if provided
        if movie_data.genre_ids:
            query = select(Genre).where(
                Genre.tmdb_id.in_(movie_data.genre_ids),
                Genre.type == "movie",
            )
            result = await self.db.execute(query)
            genres = result.scalars().all()
            movie.genres = genres
        
        self.db.add(movie)
        await self.db.commit()
        await self.db.refresh(movie)
        
        return movie
    
    async def update_movie(self, movie_id: UUID, movie_data: MovieUpdate) -> Movie:
        """Update a movie."""
        movie = await self.get_movie_by_id(movie_id)
        
        # Update fields
        for field, value in movie_data.model_dump(exclude_unset=True).items():
            if field != "genre_ids" and value is not None:
                setattr(movie, field, value)
        
        # Update genres if provided
        if movie_data.genre_ids:
            query = select(Genre).where(
                Genre.tmdb_id.in_(movie_data.genre_ids),
                Genre.type == "movie",
            )
            result = await self.db.execute(query)
            genres = result.scalars().all()
            movie.genres = genres
        
        await self.db.commit()
        await self.db.refresh(movie)
        
        return movie
    
    async def delete_movie(self, movie_id: UUID) -> None:
        """Delete a movie."""
        movie = await self.get_movie_by_id(movie_id)
        await self.db.delete(movie)
        await self.db.commit()
    
    async def sync_movie_from_tmdb(self, tmdb_id: int) -> Movie:
        """Sync a movie from TMDB."""
        # Check if movie already exists
        existing_movie = await self.get_movie_by_tmdb_id(tmdb_id)
        
        # Get movie data from TMDB
        tmdb_movie = await tmdb_service.get_movie(tmdb_id)
        
        # Extract director and actors from credits
        director_name = None
        director_tmdb_id = None
        actor1_name = None
        actor1_tmdb_id = None
        actor2_name = None
        actor2_tmdb_id = None
        actor3_name = None
        actor3_tmdb_id = None
        
        if "credits" in tmdb_movie:
            # Find director
            for crew_member in tmdb_movie["credits"].get("crew", []):
                if crew_member.get("job") == "Director":
                    director_name = crew_member.get("name")
                    director_tmdb_id = crew_member.get("id")
                    break
            
            # Find top 3 actors
            actors = tmdb_movie["credits"].get("cast", [])
            if len(actors) > 0:
                actor1_name = actors[0].get("name")
                actor1_tmdb_id = actors[0].get("id")
            if len(actors) > 1:
                actor2_name = actors[1].get("name")
                actor2_tmdb_id = actors[1].get("id")
            if len(actors) > 2:
                actor3_name = actors[2].get("name")
                actor3_tmdb_id = actors[2].get("id")
        
        # Parse release date
        release_date = None
        if tmdb_movie.get("release_date"):
            try:
                release_date = datetime.strptime(
                    tmdb_movie["release_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                logfire.warning(
                    "Invalid release date format",
                    release_date=tmdb_movie["release_date"],
                )
        
        # Create movie data
        movie_data = MovieCreate(
            tmdb_id=tmdb_movie["id"],
            title=tmdb_movie["title"],
            original_title=tmdb_movie.get("original_title"),
            overview=tmdb_movie.get("overview"),
            poster_path=tmdb_movie.get("poster_path"),
            backdrop_path=tmdb_movie.get("backdrop_path"),
            release_date=release_date,
            popularity=tmdb_movie.get("popularity"),
            vote_average=tmdb_movie.get("vote_average"),
            vote_count=tmdb_movie.get("vote_count"),
            adult=tmdb_movie.get("adult", False),
            original_language=tmdb_movie.get("original_language"),
            genre_ids=[genre["id"] for genre in tmdb_movie.get("genres", [])],
            director_name=director_name,
            director_tmdb_id=director_tmdb_id,
            actor1_name=actor1_name,
            actor1_tmdb_id=actor1_tmdb_id,
            actor2_name=actor2_name,
            actor2_tmdb_id=actor2_tmdb_id,
            actor3_name=actor3_name,
            actor3_tmdb_id=actor3_tmdb_id,
        )
        
        if existing_movie:
            # Update existing movie
            for field, value in movie_data.model_dump().items():
                if field != "genre_ids":
                    setattr(existing_movie, field, value)
            
            # Update genres
            if movie_data.genre_ids:
                query = select(Genre).where(
                    Genre.tmdb_id.in_(movie_data.genre_ids),
                    Genre.type == "movie",
                )
                result = await self.db.execute(query)
                genres = result.scalars().all()
                existing_movie.genres = genres
            
            await self.db.commit()
            await self.db.refresh(existing_movie)
            
            return existing_movie
        else:
            # Create new movie
            return await self.create_movie(movie_data)
    
    async def sync_popular_movies(self) -> List[Movie]:
        """Sync popular movies from TMDB."""
        # Get popular movies from TMDB
        tmdb_movies = await tmdb_service.get_popular_movies()
        
        # Sync each movie
        movies = []
        for tmdb_movie in tmdb_movies.get("results", []):
            try:
                movie = await self.sync_movie_from_tmdb(tmdb_movie["id"])
                movies.append(movie)
            except Exception as e:
                logfire.error(
                    "Error syncing movie",
                    tmdb_id=tmdb_movie["id"],
                    error=str(e),
                )
        
        return movies


async def get_movie_service(db: AsyncSession = Depends(get_db)) -> MovieService:
    """Dependency for getting the movie service."""
    return MovieService(db)
