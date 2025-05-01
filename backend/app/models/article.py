"""
Article model for storing news articles.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import text

from app.db.base import Base


class Article(Base):
    """
    Article model representing news articles collected from feeds.
    """
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feed_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("news_feeds.id"), nullable=False)
    title: Mapped[str] = Column(String, nullable=False)
    url: Mapped[str] = Column(String, nullable=False, unique=True)
    source: Mapped[str] = Column(String, nullable=False)
    published_at: Mapped[datetime] = Column(DateTime, nullable=False)
    author: Mapped[Optional[str]] = Column(String)
    content: Mapped[str] = Column(Text, nullable=False)
    
    # Changed from 'metadata' to 'meta_data' to avoid conflict with SQLAlchemy's reserved name
    meta_data: Mapped[Dict] = Column(JSONB, default={})
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)

    # Relationships
    feed: Mapped["NewsFeed"] = relationship("NewsFeed", back_populates="articles")
    article_relevances: Mapped[List["ArticleRelevance"]] = relationship("ArticleRelevance", back_populates="article", cascade="all, delete-orphan")
    report_articles: Mapped[List["ReportArticle"]] = relationship("ReportArticle", back_populates="article", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of the Article model."""
        return f"<Article {self.title}>"

    # Create indexes with proper operator class
    __table_args__ = (
        # GIN index for full-text search - add gin_trgm_ops operator class
        Index("ix_articles_content_gin", text("content gin_trgm_ops"), postgresql_using="gin"),
        
        # B-tree index on published_at for efficient date filtering
        Index("ix_articles_published_at", "published_at"),
    )