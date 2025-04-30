"""
Pydantic schemas for article data validation.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, HttpUrl


class ArticleBase(BaseModel):
    """Base schema for article data."""
    title: str
    url: str
    source: str
    published_at: datetime
    author: Optional[str] = None
    content: str
    metadata: Dict = {}


class ArticleCreate(ArticleBase):
    """Schema for article creation."""
    feed_id: uuid.UUID


class ArticleUpdate(BaseModel):
    """Schema for article updates."""
    title: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict] = None


class ArticleInDBBase(ArticleBase):
    """Base schema for article in database."""
    id: uuid.UUID
    feed_id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True


class Article(ArticleInDBBase):
    """Schema for article response."""
    pass


class ArticleInDB(ArticleInDBBase):
    """Schema for article in database."""
    pass


class ArticleRelevanceBase(BaseModel):
    """Base schema for article relevance data."""
    article_id: uuid.UUID
    client_id: uuid.UUID
    relevance_score: float
    summary: Optional[str] = None
    is_included: bool = False


class ArticleRelevanceCreate(ArticleRelevanceBase):
    """Schema for article relevance creation."""
    pass


class ArticleRelevanceUpdate(BaseModel):
    """Schema for article relevance updates."""
    relevance_score: Optional[float] = None
    summary: Optional[str] = None
    is_included: Optional[bool] = None


class ArticleRelevanceInDBBase(ArticleRelevanceBase):
    """Base schema for article relevance in database."""
    id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True


class ArticleRelevance(ArticleRelevanceInDBBase):
    """Schema for article relevance response."""
    pass


class ArticleRelevanceInDB(ArticleRelevanceInDBBase):
    """Schema for article relevance in database."""
    pass