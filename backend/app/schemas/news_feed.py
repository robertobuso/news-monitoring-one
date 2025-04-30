"""
Pydantic schemas for news feed data validation.
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl, validator


class FeedType(str, Enum):
    """Enum for feed types."""
    RSS = "rss"
    API = "api"
    WEB = "web"


class HealthStatus(str, Enum):
    """Enum for health status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"


class NewsFeedBase(BaseModel):
    """Base schema for news feed data."""
    name: str
    url: str
    type: FeedType
    check_frequency: int  # in minutes
    is_active: bool = True

    @validator("url")
    def url_must_be_valid(cls, v):
        """Validate URL format."""
        # Simple validation, can be enhanced
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @validator("check_frequency")
    def check_frequency_must_be_positive(cls, v):
        """Validate check frequency."""
        if v <= 0:
            raise ValueError("Check frequency must be positive")
        return v


class NewsFeedCreate(NewsFeedBase):
    """Schema for news feed creation."""
    pass


class NewsFeedUpdate(BaseModel):
    """Schema for news feed updates."""
    name: Optional[str] = None
    url: Optional[str] = None
    type: Optional[FeedType] = None
    check_frequency: Optional[int] = None
    is_active: Optional[bool] = None
    health_status: Optional[HealthStatus] = None


class NewsFeedInDBBase(NewsFeedBase):
    """Base schema for news feed in database."""
    id: uuid.UUID
    last_checked: Optional[datetime] = None
    health_status: HealthStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class NewsFeed(NewsFeedInDBBase):
    """Schema for news feed response."""
    pass


class NewsFeedInDB(NewsFeedInDBBase):
    """Schema for news feed in database."""
    pass