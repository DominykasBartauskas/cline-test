from fastapi import APIRouter

from app.api.endpoints import genres, movies, search, sync, tv_shows, users

# Create API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(movies.router, prefix="/movies", tags=["movies"])
api_router.include_router(tv_shows.router, prefix="/tv", tags=["tv_shows"])
api_router.include_router(genres.router, prefix="/genres", tags=["genres"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
