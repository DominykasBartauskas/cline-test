from typing import Dict, List

import logfire
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.models.schemas.base import BaseAPIResponse
from app.models.schemas.genre import GenreResponse
from app.models.schemas.movie import MovieResponse
from app.models.schemas.tv_show import TVShowResponse
from app.services.genre_service import GenreService, get_genre_service
from app.services.movie_service import MovieService, get_movie_service
from app.services.tv_show_service import TVShowService, get_tv_show_service

router = APIRouter()


@router.post("/genres", response_model=Dict[str, List[GenreResponse]])
async def sync_genres(
    genre_service: GenreService = Depends(get_genre_service),
):
    """
    Sync genres from TMDB.
    """
    movie_genres, tv_genres = await genre_service.sync_genres_from_tmdb()
    
    return {
        "movie_genres": [GenreResponse.model_validate(genre) for genre in movie_genres],
        "tv_genres": [GenreResponse.model_validate(genre) for genre in tv_genres],
    }


@router.post("/movies/popular", response_model=List[MovieResponse])
async def sync_popular_movies(
    background_tasks: BackgroundTasks,
    movie_service: MovieService = Depends(get_movie_service),
):
    """
    Sync popular movies from TMDB.
    """
    # Run in background to avoid timeout
    background_tasks.add_task(movie_service.sync_popular_movies)
    
    return BaseAPIResponse(
        message="Popular movies sync started in background"
    )


@router.post("/tv/popular", response_model=List[TVShowResponse])
async def sync_popular_tv_shows(
    background_tasks: BackgroundTasks,
    tv_show_service: TVShowService = Depends(get_tv_show_service),
):
    """
    Sync popular TV shows from TMDB.
    """
    # Run in background to avoid timeout
    background_tasks.add_task(tv_show_service.sync_popular_tv_shows)
    
    return BaseAPIResponse(
        message="Popular TV shows sync started in background"
    )


@router.post("/movies/{tmdb_id}", response_model=MovieResponse)
async def sync_movie(
    tmdb_id: int,
    movie_service: MovieService = Depends(get_movie_service),
):
    """
    Sync a movie from TMDB.
    
    - **tmdb_id**: TMDB ID
    """
    try:
        movie = await movie_service.sync_movie_from_tmdb(tmdb_id)
        return MovieResponse.model_validate(movie)
    except Exception as e:
        logfire.error(
            "Error syncing movie",
            tmdb_id=tmdb_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing movie: {str(e)}",
        )


@router.post("/tv/{tmdb_id}", response_model=TVShowResponse)
async def sync_tv_show(
    tmdb_id: int,
    tv_show_service: TVShowService = Depends(get_tv_show_service),
):
    """
    Sync a TV show from TMDB.
    
    - **tmdb_id**: TMDB ID
    """
    try:
        tv_show = await tv_show_service.sync_tv_show_from_tmdb(tmdb_id)
        return TVShowResponse.model_validate(tv_show)
    except Exception as e:
        logfire.error(
            "Error syncing TV show",
            tmdb_id=tmdb_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing TV show: {str(e)}",
        )
