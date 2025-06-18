from typing import List, Optional
from uuid import UUID

import logfire
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas.base import BaseAPIResponse, PaginatedResponse
from app.models.schemas.tv_show import (
    TVShowCreate,
    TVShowResponse,
    TVShowSearchParams,
    TVShowUpdate,
)
from app.services.tv_show_service import TVShowService, get_tv_show_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse[TVShowResponse])
async def get_tv_shows(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("popularity", description="Field to sort by"),
    tv_show_service: TVShowService = Depends(get_tv_show_service),
):
    """
    Get a list of TV shows.
    
    - **page**: Page number (starts at 1)
    - **size**: Number of items per page
    - **sort_by**: Field to sort by (popularity, name, first_air_date, vote_average)
    """
    skip = (page - 1) * size
    tv_shows, total = await tv_show_service.get_tv_shows(
        skip=skip, limit=size, sort_by=sort_by
    )
    
    # Calculate total pages
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=[TVShowResponse.model_validate(tv_show) for tv_show in tv_shows],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/search", response_model=PaginatedResponse[TVShowResponse])
async def search_tv_shows(
    query: Optional[str] = None,
    genre_id: Optional[int] = None,
    year: Optional[int] = None,
    sort_by: str = Query("popularity.desc", description="Field to sort by"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    tv_show_service: TVShowService = Depends(get_tv_show_service),
):
    """
    Search for TV shows.
    
    - **query**: Search query
    - **genre_id**: Filter by genre ID
    - **year**: Filter by first air date year
    - **sort_by**: Field to sort by (format: field.direction, e.g., popularity.desc)
    - **page**: Page number (starts at 1)
    - **size**: Number of items per page
    """
    search_params = TVShowSearchParams(
        query=query,
        genre_id=genre_id,
        year=year,
        sort_by=sort_by,
        page=page,
        size=size,
    )
    
    tv_shows, total = await tv_show_service.search_tv_shows(search_params)
    
    # Calculate total pages
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=[TVShowResponse.model_validate(tv_show) for tv_show in tv_shows],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{tv_show_id}", response_model=TVShowResponse)
async def get_tv_show(
    tv_show_id: UUID,
    tv_show_service: TVShowService = Depends(get_tv_show_service),
):
    """
    Get a TV show by ID.
    
    - **tv_show_id**: TV show ID
    """
    tv_show = await tv_show_service.get_tv_show_by_id(tv_show_id)
    return TVShowResponse.model_validate(tv_show)


@router.post("", response_model=TVShowResponse, status_code=status.HTTP_201_CREATED)
async def create_tv_show(
    tv_show_data: TVShowCreate,
    tv_show_service: TVShowService = Depends(get_tv_show_service),
):
    """
    Create a new TV show.
    
    - **tv_show_data**: TV show data
    """
    tv_show = await tv_show_service.create_tv_show(tv_show_data)
    return TVShowResponse.model_validate(tv_show)


@router.put("/{tv_show_id}", response_model=TVShowResponse)
async def update_tv_show(
    tv_show_id: UUID,
    tv_show_data: TVShowUpdate,
    tv_show_service: TVShowService = Depends(get_tv_show_service),
):
    """
    Update a TV show.
    
    - **tv_show_id**: TV show ID
    - **tv_show_data**: TV show data
    """
    tv_show = await tv_show_service.update_tv_show(tv_show_id, tv_show_data)
    return TVShowResponse.model_validate(tv_show)


@router.delete("/{tv_show_id}", response_model=BaseAPIResponse)
async def delete_tv_show(
    tv_show_id: UUID,
    tv_show_service: TVShowService = Depends(get_tv_show_service),
):
    """
    Delete a TV show.
    
    - **tv_show_id**: TV show ID
    """
    await tv_show_service.delete_tv_show(tv_show_id)
    return BaseAPIResponse(message="TV show deleted successfully")
