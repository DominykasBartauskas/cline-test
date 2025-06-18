from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.schemas.base import BaseAPIResponse
from app.models.schemas.genre import GenreCreate, GenreResponse, GenreUpdate
from app.services.genre_service import GenreService, get_genre_service

router = APIRouter()


@router.get("", response_model=List[GenreResponse])
async def get_genres(
    type: Optional[str] = Query(None, description="Filter by type (movie or tv)"),
    genre_service: GenreService = Depends(get_genre_service),
):
    """
    Get a list of genres.
    
    - **type**: Filter by type (movie or tv)
    """
    genres = await genre_service.get_genres(type=type)
    return [GenreResponse.model_validate(genre) for genre in genres]


@router.get("/{genre_id}", response_model=GenreResponse)
async def get_genre(
    genre_id: UUID,
    genre_service: GenreService = Depends(get_genre_service),
):
    """
    Get a genre by ID.
    
    - **genre_id**: Genre ID
    """
    genre = await genre_service.get_genre_by_id(genre_id)
    return GenreResponse.model_validate(genre)


@router.post("", response_model=GenreResponse, status_code=status.HTTP_201_CREATED)
async def create_genre(
    genre_data: GenreCreate,
    genre_service: GenreService = Depends(get_genre_service),
):
    """
    Create a new genre.
    
    - **genre_data**: Genre data
    """
    genre = await genre_service.create_genre(genre_data)
    return GenreResponse.model_validate(genre)


@router.put("/{genre_id}", response_model=GenreResponse)
async def update_genre(
    genre_id: UUID,
    genre_data: GenreUpdate,
    genre_service: GenreService = Depends(get_genre_service),
):
    """
    Update a genre.
    
    - **genre_id**: Genre ID
    - **genre_data**: Genre data
    """
    genre = await genre_service.update_genre(genre_id, genre_data)
    return GenreResponse.model_validate(genre)


@router.delete("/{genre_id}", response_model=BaseAPIResponse)
async def delete_genre(
    genre_id: UUID,
    genre_service: GenreService = Depends(get_genre_service),
):
    """
    Delete a genre.
    
    - **genre_id**: Genre ID
    """
    await genre_service.delete_genre(genre_id)
    return BaseAPIResponse(message="Genre deleted successfully")
