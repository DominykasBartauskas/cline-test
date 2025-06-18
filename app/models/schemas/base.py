from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema for all models."""
    
    model_config = ConfigDict(from_attributes=True)


class BaseAPIResponse(BaseModel):
    """Base API response model."""
    
    success: bool = True
    message: Optional[str] = None


# Generic types for CRUD operations
T = TypeVar("T", bound=BaseSchema)
CreateT = TypeVar("CreateT", bound=BaseSchema)
UpdateT = TypeVar("UpdateT", bound=BaseSchema)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""
    
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
