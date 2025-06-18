import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Project info
    PROJECT_NAME: str = "TMDB API"
    PROJECT_DESCRIPTION: str = "FastAPI backend for TMDB API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    
    # API settings
    API_V1_STR: str = "/api"
    
    # Security settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Validate CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "tmdb"
    POSTGRES_PORT: str = "5432"
    DATABASE_URI: Optional[PostgresDsn] = None
    
    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> Any:
        """Assemble database connection string."""
        if isinstance(v, str):
            return v
        
        # Get values from the model
        values = info.data
        
        # Convert port to integer
        port = values.get("POSTGRES_PORT")
        if port is not None:
            port = int(port)
        
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=port,
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # TMDB API settings
    TMDB_API_KEY: str = ""
    TMDB_API_BASE_URL: str = "https://api.themoviedb.org/3"
    
    # Cache settings
    CACHE_ENABLED: bool = True
    CACHE_EXPIRE_MINUTES: int = 60  # 1 hour
    
    # Logging settings
    LOGFIRE_TOKEN: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create settings instance
settings = Settings()
