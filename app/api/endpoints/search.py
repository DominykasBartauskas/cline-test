from typing import List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.schemas.base import PaginatedResponse
from app.models.schemas.movie import MovieResponse
from app.models.schemas.tv_show import TVShowResponse
from app.services.movie_service import MovieService, get_movie_service
from app.services.tmdb_service import tmdb_service
from app.services.tv_show_service import TVShowService, get_tv_show_service

router = APIRouter()


@router.get("/multi", response_model=dict)
async def search_multi(
    query: str,
    page: int = Query(1, ge=1),
    movie_service: MovieService = Depends(get_movie_service),
    tv_show_service: TVShowService = Depends(get_tv_show_service),
):
    """
    Search for movies and TV shows.
    
    - **query**: Search query
    - **page**: Page number (starts at 1)
    """
    # Search in TMDB
    tmdb_results = await tmdb_service.search_multi(query, page)
    
    # Process results
    movies = []
    tv_shows = []
    
    for result in tmdb_results.get("results", []):
        media_type = result.get("media_type")
        
        if media_type == "movie":
            # Try to get movie from database
            movie = await movie_service.get_movie_by_tmdb_id(result["id"])
            
            if movie:
                movies.append(MovieResponse.model_validate(movie))
            else:
                # Movie not in database, sync from TMDB
                try:
                    movie = await movie_service.sync_movie_from_tmdb(result["id"])
                    movies.append(MovieResponse.model_validate(movie))
                except Exception as e:
                    # Skip if error
                    continue
        
        elif media_type == "tv":
            # Try to get TV show from database
            tv_show = await tv_show_service.get_tv_show_by_tmdb_id(result["id"])
            
            if tv_show:
                tv_shows.append(TVShowResponse.model_validate(tv_show))
            else:
                # TV show not in database, sync from TMDB
                try:
                    tv_show = await tv_show_service.sync_tv_show_from_tmdb(result["id"])
                    tv_shows.append(TVShowResponse.model_validate(tv_show))
                except Exception as e:
                    # Skip if error
                    continue
    
    # Return results
    return {
        "movies": movies,
        "tv_shows": tv_shows,
        "total_results": tmdb_results.get("total_results", 0),
        "total_pages": tmdb_results.get("total_pages", 0),
        "page": tmdb_results.get("page", 1),
    }


@router.get("/movies", response_model=PaginatedResponse[MovieResponse])
async def search_movies(
    query: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    year: Optional[int] = None,
    movie_service: MovieService = Depends(get_movie_service),
):
    """
    Search for movies.
    
    - **query**: Search query
    - **page**: Page number (starts at 1)
    - **size**: Number of items per page
    - **year**: Filter by release year
    """
    # Search in database first
    search_params = {
        "query": query,
        "page": page,
        "size": size,
        "year": year,
        "sort_by": "popularity.desc",
    }
    
    movies, total = await movie_service.search_movies(search_params)
    
    # If no results, search in TMDB
    if not movies:
        tmdb_results = await tmdb_service.search_movies(query, page, year)
        
        # Sync movies from TMDB
        for result in tmdb_results.get("results", []):
            try:
                movie = await movie_service.sync_movie_from_tmdb(result["id"])
                movies.append(movie)
            except Exception as e:
                # Skip if error
                continue
        
        total = tmdb_results.get("total_results", 0)
    
    # Calculate total pages
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=[MovieResponse.model_validate(movie) for movie in movies],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/tv", response_model=PaginatedResponse[TVShowResponse])
async def search_tv_shows(
    query: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    year: Optional[int] = None,
    tv_show_service: TVShowService = Depends(get_tv_show_service),
):
    """
    Search for TV shows.
    
    - **query**: Search query
    - **page**: Page number (starts at 1)
    - **size**: Number of items per page
    - **year**: Filter by first air date year
    """
    # Search in database first
    search_params = {
        "query": query,
        "page": page,
        "size": size,
        "year": year,
        "sort_by": "popularity.desc",
    }
    
    tv_shows, total = await tv_show_service.search_tv_shows(search_params)
    
    # If no results, search in TMDB
    if not tv_shows:
        tmdb_results = await tmdb_service.search_tv_shows(query, page, year)
        
        # Sync TV shows from TMDB
        for result in tmdb_results.get("results", []):
            try:
                tv_show = await tv_show_service.sync_tv_show_from_tmdb(result["id"])
                tv_shows.append(tv_show)
            except Exception as e:
                # Skip if error
                continue
        
        total = tmdb_results.get("total_results", 0)
    
    # Calculate total pages
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=[TVShowResponse.model_validate(tv_show) for tv_show in tv_shows],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )
