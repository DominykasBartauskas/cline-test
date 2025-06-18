from typing import List, Optional
from uuid import UUID

import logfire
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas.base import BaseAPIResponse, PaginatedResponse
from app.models.schemas.movie import (
    MovieCreate,
    MovieResponse,
    MovieSearchParams,
    MovieUpdate,
)
from app.services.movie_service import MovieService, get_movie_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse[MovieResponse])
async def get_movies(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("popularity", description="Field to sort by"),
    movie_service: MovieService = Depends(get_movie_service),
):
    """
    Get a list of movies.
    
    - **page**: Page number (starts at 1)
    - **size**: Number of items per page
    - **sort_by**: Field to sort by (popularity, title, release_date, vote_average)
    """
    skip = (page - 1) * size
    movies, total = await movie_service.get_movies(skip=skip, limit=size, sort_by=sort_by)
    
    # Calculate total pages
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=[MovieResponse.model_validate(movie) for movie in movies],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/search", response_model=PaginatedResponse[MovieResponse])
async def search_movies(
    query: Optional[str] = None,
    genre_id: Optional[int] = None,
    year: Optional[int] = None,
    sort_by: str = Query("popularity.desc", description="Field to sort by"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    movie_service: MovieService = Depends(get_movie_service),
):
    """
    Search for movies.
    
    - **query**: Search query
    - **genre_id**: Filter by genre ID
    - **year**: Filter by release year
    - **sort_by**: Field to sort by (format: field.direction, e.g., popularity.desc)
    - **page**: Page number (starts at 1)
    - **size**: Number of items per page
    """
    search_params = MovieSearchParams(
        query=query,
        genre_id=genre_id,
        year=year,
        sort_by=sort_by,
        page=page,
        size=size,
    )
    
    movies, total = await movie_service.search_movies(search_params)
    
    # Calculate total pages
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=[MovieResponse.model_validate(movie) for movie in movies],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(
    movie_id: UUID,
    movie_service: MovieService = Depends(get_movie_service),
):
    """
    Get a movie by ID.
    
    - **movie_id**: Movie ID
    """
    movie = await movie_service.get_movie_by_id(movie_id)
    return MovieResponse.model_validate(movie)


@router.post("", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie_data: MovieCreate,
    movie_service: MovieService = Depends(get_movie_service),
):
    """
    Create a new movie.
    
    - **movie_data**: Movie data
    """
    movie = await movie_service.create_movie(movie_data)
    return MovieResponse.model_validate(movie)


@router.put("/{movie_id}", response_model=MovieResponse)
async def update_movie(
    movie_id: UUID,
    movie_data: MovieUpdate,
    movie_service: MovieService = Depends(get_movie_service),
):
    """
    Update a movie.
    
    - **movie_id**: Movie ID
    - **movie_data**: Movie data
    """
    movie = await movie_service.update_movie(movie_id, movie_data)
    return MovieResponse.model_validate(movie)


@router.delete("/{movie_id}", response_model=BaseAPIResponse)
async def delete_movie(
    movie_id: UUID,
    movie_service: MovieService = Depends(get_movie_service),
):
    """
    Delete a movie.
    
    - **movie_id**: Movie ID
    """
    await movie_service.delete_movie(movie_id)
    return BaseAPIResponse(message="Movie deleted successfully")
