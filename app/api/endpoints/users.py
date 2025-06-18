from datetime import timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.core.config import settings
from app.models.schemas.base import BaseAPIResponse
from app.models.schemas.movie import MovieResponse
from app.models.schemas.tv_show import TVShowResponse
from app.models.schemas.user import (
    MovieRatingCreate,
    MovieRatingResponse,
    MovieRatingUpdate,
    TVShowRatingCreate,
    TVShowRatingResponse,
    TVShowRatingUpdate,
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserWithWatchlistResponse,
)
from app.services.user_service import UserService, get_user_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")


# Helper function to get current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
):
    """Get current user from token."""
    from jose import JWTError, jwt
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[user_service.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await user_service.get_user_by_id(UUID(user_id))
    if user is None:
        raise credentials_exception
    
    return user


# Helper function to get current active user
async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user),
):
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Helper function to get current active superuser
async def get_current_active_superuser(
    current_user: UserResponse = Depends(get_current_user),
):
    """Get current active superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not enough permissions"
        )
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await user_service.authenticate_user(
        form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = user_service.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: UserResponse = Depends(get_current_active_user),
):
    """
    Get current user.
    """
    return current_user


@router.get("/me/watchlist", response_model=UserWithWatchlistResponse)
async def read_users_me_watchlist(
    current_user: UserResponse = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Get current user's watchlist.
    """
    user = await user_service.get_user_with_watchlist(current_user.id)
    return UserWithWatchlistResponse.model_validate(user)


@router.post("/me/watchlist/movies/{movie_id}", response_model=UserWithWatchlistResponse)
async def add_movie_to_watchlist(
    movie_id: UUID,
    current_user: UserResponse = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Add a movie to current user's watchlist.
    
    - **movie_id**: Movie ID
    """
    user = await user_service.add_movie_to_watchlist(current_user.id, movie_id)
    return UserWithWatchlistResponse.model_validate(user)


@router.delete("/me/watchlist/movies/{movie_id}", response_model=UserWithWatchlistResponse)
async def remove_movie_from_watchlist(
    movie_id: UUID,
    current_user: UserResponse = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Remove a movie from current user's watchlist.
    
    - **movie_id**: Movie ID
    """
    user = await user_service.remove_movie_from_watchlist(current_user.id, movie_id)
    return UserWithWatchlistResponse.model_validate(user)


@router.post("/me/watchlist/tv/{tv_show_id}", response_model=UserWithWatchlistResponse)
async def add_tv_show_to_watchlist(
    tv_show_id: UUID,
    current_user: UserResponse = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Add a TV show to current user's watchlist.
    
    - **tv_show_id**: TV show ID
    """
    user = await user_service.add_tv_show_to_watchlist(current_user.id, tv_show_id)
    return UserWithWatchlistResponse.model_validate(user)


@router.delete("/me/watchlist/tv/{tv_show_id}", response_model=UserWithWatchlistResponse)
async def remove_tv_show_from_watchlist(
    tv_show_id: UUID,
    current_user: UserResponse = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Remove a TV show from current user's watchlist.
    
    - **tv_show_id**: TV show ID
    """
    user = await user_service.remove_tv_show_from_watchlist(current_user.id, tv_show_id)
    return UserWithWatchlistResponse.model_validate(user)


@router.get("/me/ratings/movies", response_model=List[MovieRatingResponse])
async def get_user_movie_ratings(
    current_user: UserResponse = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Get current user's movie ratings.
    """
    ratings = await user_service.get_user_movie_ratings(current_user.id)
    return [MovieRatingResponse.model_validate(rating) for rating in ratings]


@router.post("/me/ratings/movies", response_model=MovieRatingResponse)
async def create_movie_rating(
    rating_data: MovieRatingCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Create a movie rating for current user.
    
    - **rating_data**: Rating data
    """
    rating = await user_service.create_movie_rating(current_user.id, rating_data)
    return MovieRatingResponse.model_validate(rating)


@router.put("/me/ratings/movies/{movie_id}", response_model=MovieRatingResponse)
async def update_movie_rating(
    movie_id: UUID,
    rating_data: MovieRatingUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Update a movie rating for current user.
    
    - **movie_id**: Movie ID
    - **rating_data**: Rating data
    """
    rating = await user_service.update_movie_rating(
        current_user.id, movie_id, rating_data
    )
    return MovieRatingResponse.model_validate(rating)


@router.delete("/me/ratings/movies/{movie_id}", response_model=BaseAPIResponse)
async def delete_movie_rating(
    movie_id: UUID,
    current_user: UserResponse = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Delete a movie rating for current user.
    
    - **movie_id**: Movie ID
    """
    await user_service.delete_movie_rating(current_user.id, movie_id)
    return BaseAPIResponse(message="Movie rating deleted successfully")


@router.get("/me/ratings/tv", response_model=List[TVShowRatingResponse])
async def get_user_tv_show_ratings(
    current_user: UserResponse = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Get current user's TV show ratings.
    """
    ratings = await user_service.get_user_tv_show_ratings(current_user.id)
    return [TVShowRatingResponse.model_validate(rating) for rating in ratings]


@router.post("/me/ratings/tv", response_model=TVShowRatingResponse)
async def create_tv_show_rating(
    rating_data: TVShowRatingCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Create a TV show rating for current user.
    
    - **rating_data**: Rating data
    """
    rating = await user_service.create_tv_show_rating(current_user.id, rating_data)
    return TVShowRatingResponse.model_validate(rating)


@router.put("/me/ratings/tv/{tv_show_id}", response_model=TVShowRatingResponse)
async def update_tv_show_rating(
    tv_show_id: UUID,
    rating_data: TVShowRatingUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Update a TV show rating for current user.
    
    - **tv_show_id**: TV show ID
    - **rating_data**: Rating data
    """
    rating = await user_service.update_tv_show_rating(
        current_user.id, tv_show_id, rating_data
    )
    return TVShowRatingResponse.model_validate(rating)


@router.delete("/me/ratings/tv/{tv_show_id}", response_model=BaseAPIResponse)
async def delete_tv_show_rating(
    tv_show_id: UUID,
    current_user: UserResponse = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Delete a TV show rating for current user.
    
    - **tv_show_id**: TV show ID
    """
    await user_service.delete_tv_show_rating(current_user.id, tv_show_id)
    return BaseAPIResponse(message="TV show rating deleted successfully")


# Admin endpoints
@router.get("", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_active_superuser),
    user_service: UserService = Depends(get_user_service),
):
    """
    Get a list of users. Only for superusers.
    
    - **skip**: Number of users to skip
    - **limit**: Maximum number of users to return
    """
    users = await user_service.get_users(skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    """
    Create a new user.
    
    - **user_data**: User data
    """
    user = await user_service.create_user(user_data)
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: UserResponse = Depends(get_current_active_superuser),
    user_service: UserService = Depends(get_user_service),
):
    """
    Get a user by ID. Only for superusers.
    
    - **user_id**: User ID
    """
    user = await user_service.get_user_by_id(user_id)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_active_superuser),
    user_service: UserService = Depends(get_user_service),
):
    """
    Update a user. Only for superusers.
    
    - **user_id**: User ID
    - **user_data**: User data
    """
    user = await user_service.update_user(user_id, user_data)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", response_model=BaseAPIResponse)
async def delete_user(
    user_id: UUID,
    current_user: UserResponse = Depends(get_current_active_superuser),
    user_service: UserService = Depends(get_user_service),
):
    """
    Delete a user. Only for superusers.
    
    - **user_id**: User ID
    """
    await user_service.delete_user(user_id)
    return BaseAPIResponse(message="User deleted successfully")
