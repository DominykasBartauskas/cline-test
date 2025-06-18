from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Union
from uuid import UUID

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.db.database import get_db
from app.models.domain.movie import Movie
from app.models.domain.tv_show import TVShow
from app.models.domain.user import (
    MovieRating,
    TVShowRating,
    User,
    user_movie_watchlist,
    user_tv_show_watchlist,
)
from app.models.schemas.user import (
    MovieRatingCreate,
    MovieRatingUpdate,
    TVShowRatingCreate,
    TVShowRatingUpdate,
    UserCreate,
    UserUpdate,
)


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token settings
ALGORITHM = "HS256"


class UserService:
    """Service for user-related operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    async def get_user_by_id(self, user_id: UUID) -> User:
        """Get a user by ID."""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get a list of users."""
        query = select(User).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if email already exists
        existing_email = await self.get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )
        
        # Check if username already exists
        existing_username = await self.get_user_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="Username already taken",
            )
        
        # Create new user
        hashed_password = self.get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=user_data.is_active,
            is_superuser=user_data.is_superuser,
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update a user."""
        user = await self.get_user_by_id(user_id)
        
        # Check if email is being changed and already exists
        if user_data.email and user_data.email != user.email:
            existing_email = await self.get_user_by_email(user_data.email)
            if existing_email:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered",
                )
        
        # Check if username is being changed and already exists
        if user_data.username and user_data.username != user.username:
            existing_username = await self.get_user_by_username(user_data.username)
            if existing_username:
                raise HTTPException(
                    status_code=400,
                    detail="Username already taken",
                )
        
        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = self.get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: UUID) -> None:
        """Delete a user."""
        user = await self.get_user_by_id(user_id)
        await self.db.delete(user)
        await self.db.commit()
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    async def get_user_with_watchlist(self, user_id: UUID) -> User:
        """Get a user with watchlist."""
        query = (
            select(User)
            .options(
                selectinload(User.watchlist_movies),
                selectinload(User.watchlist_tv_shows),
            )
            .where(User.id == user_id)
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    
    async def add_movie_to_watchlist(self, user_id: UUID, movie_id: UUID) -> User:
        """Add a movie to a user's watchlist."""
        user = await self.get_user_with_watchlist(user_id)
        
        # Check if movie exists
        movie_query = select(Movie).where(Movie.id == movie_id)
        movie_result = await self.db.execute(movie_query)
        movie = movie_result.scalar_one_or_none()
        
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        # Check if movie is already in watchlist
        if any(m.id == movie_id for m in user.watchlist_movies):
            return user
        
        # Add movie to watchlist
        user.watchlist_movies.append(movie)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def remove_movie_from_watchlist(self, user_id: UUID, movie_id: UUID) -> User:
        """Remove a movie from a user's watchlist."""
        user = await self.get_user_with_watchlist(user_id)
        
        # Remove movie from watchlist
        user.watchlist_movies = [m for m in user.watchlist_movies if m.id != movie_id]
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def add_tv_show_to_watchlist(self, user_id: UUID, tv_show_id: UUID) -> User:
        """Add a TV show to a user's watchlist."""
        user = await self.get_user_with_watchlist(user_id)
        
        # Check if TV show exists
        tv_show_query = select(TVShow).where(TVShow.id == tv_show_id)
        tv_show_result = await self.db.execute(tv_show_query)
        tv_show = tv_show_result.scalar_one_or_none()
        
        if not tv_show:
            raise HTTPException(status_code=404, detail="TV show not found")
        
        # Check if TV show is already in watchlist
        if any(t.id == tv_show_id for t in user.watchlist_tv_shows):
            return user
        
        # Add TV show to watchlist
        user.watchlist_tv_shows.append(tv_show)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def remove_tv_show_from_watchlist(
        self, user_id: UUID, tv_show_id: UUID
    ) -> User:
        """Remove a TV show from a user's watchlist."""
        user = await self.get_user_with_watchlist(user_id)
        
        # Remove TV show from watchlist
        user.watchlist_tv_shows = [t for t in user.watchlist_tv_shows if t.id != tv_show_id]
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_movie_rating(
        self, user_id: UUID, movie_id: UUID
    ) -> Optional[MovieRating]:
        """Get a user's rating for a movie."""
        query = select(MovieRating).where(
            MovieRating.user_id == user_id, MovieRating.movie_id == movie_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_movie_ratings(self, user_id: UUID) -> List[MovieRating]:
        """Get all movie ratings for a user."""
        query = (
            select(MovieRating)
            .options(selectinload(MovieRating.movie))
            .where(MovieRating.user_id == user_id)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_movie_rating(
        self, user_id: UUID, rating_data: MovieRatingCreate
    ) -> MovieRating:
        """Create a movie rating."""
        # Check if movie exists
        movie_query = select(Movie).where(Movie.id == rating_data.movie_id)
        movie_result = await self.db.execute(movie_query)
        movie = movie_result.scalar_one_or_none()
        
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        # Check if rating already exists
        existing_rating = await self.get_movie_rating(user_id, rating_data.movie_id)
        if existing_rating:
            # Update existing rating
            for field, value in rating_data.model_dump(exclude={"movie_id"}).items():
                setattr(existing_rating, field, value)
            
            await self.db.commit()
            await self.db.refresh(existing_rating)
            
            return existing_rating
        
        # Create new rating
        rating = MovieRating(
            user_id=user_id,
            movie_id=rating_data.movie_id,
            rating=rating_data.rating,
            comment=rating_data.comment,
        )
        
        self.db.add(rating)
        await self.db.commit()
        await self.db.refresh(rating)
        
        return rating
    
    async def update_movie_rating(
        self, user_id: UUID, movie_id: UUID, rating_data: MovieRatingUpdate
    ) -> MovieRating:
        """Update a movie rating."""
        # Get existing rating
        rating = await self.get_movie_rating(user_id, movie_id)
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")
        
        # Update fields
        for field, value in rating_data.model_dump(exclude_unset=True).items():
            setattr(rating, field, value)
        
        await self.db.commit()
        await self.db.refresh(rating)
        
        return rating
    
    async def delete_movie_rating(self, user_id: UUID, movie_id: UUID) -> None:
        """Delete a movie rating."""
        rating = await self.get_movie_rating(user_id, movie_id)
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")
        
        await self.db.delete(rating)
        await self.db.commit()
    
    async def get_tv_show_rating(
        self, user_id: UUID, tv_show_id: UUID
    ) -> Optional[TVShowRating]:
        """Get a user's rating for a TV show."""
        query = select(TVShowRating).where(
            TVShowRating.user_id == user_id, TVShowRating.tv_show_id == tv_show_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_tv_show_ratings(self, user_id: UUID) -> List[TVShowRating]:
        """Get all TV show ratings for a user."""
        query = (
            select(TVShowRating)
            .options(selectinload(TVShowRating.tv_show))
            .where(TVShowRating.user_id == user_id)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_tv_show_rating(
        self, user_id: UUID, rating_data: TVShowRatingCreate
    ) -> TVShowRating:
        """Create a TV show rating."""
        # Check if TV show exists
        tv_show_query = select(TVShow).where(TVShow.id == rating_data.tv_show_id)
        tv_show_result = await self.db.execute(tv_show_query)
        tv_show = tv_show_result.scalar_one_or_none()
        
        if not tv_show:
            raise HTTPException(status_code=404, detail="TV show not found")
        
        # Check if rating already exists
        existing_rating = await self.get_tv_show_rating(user_id, rating_data.tv_show_id)
        if existing_rating:
            # Update existing rating
            for field, value in rating_data.model_dump(exclude={"tv_show_id"}).items():
                setattr(existing_rating, field, value)
            
            await self.db.commit()
            await self.db.refresh(existing_rating)
            
            return existing_rating
        
        # Create new rating
        rating = TVShowRating(
            user_id=user_id,
            tv_show_id=rating_data.tv_show_id,
            rating=rating_data.rating,
            comment=rating_data.comment,
        )
        
        self.db.add(rating)
        await self.db.commit()
        await self.db.refresh(rating)
        
        return rating
    
    async def update_tv_show_rating(
        self, user_id: UUID, tv_show_id: UUID, rating_data: TVShowRatingUpdate
    ) -> TVShowRating:
        """Update a TV show rating."""
        # Get existing rating
        rating = await self.get_tv_show_rating(user_id, tv_show_id)
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")
        
        # Update fields
        for field, value in rating_data.model_dump(exclude_unset=True).items():
            setattr(rating, field, value)
        
        await self.db.commit()
        await self.db.refresh(rating)
        
        return rating
    
    async def delete_tv_show_rating(self, user_id: UUID, tv_show_id: UUID) -> None:
        """Delete a TV show rating."""
        rating = await self.get_tv_show_rating(user_id, tv_show_id)
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")
        
        await self.db.delete(rating)
        await self.db.commit()


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Dependency for getting the user service."""
    return UserService(db)
