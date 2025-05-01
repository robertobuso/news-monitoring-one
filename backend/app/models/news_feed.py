"""
News feed model for managing news sources.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.db.base import Base


class NewsFeed(Base):
    """
    News feed model representing news sources to monitor.
    """
    __tablename__ = "news_feeds"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = Column(String, nullable=False)
    url: Mapped[str] = Column(String, nullable=False)
    type: Mapped[str] = Column(Enum("rss", "api", "web", name="feed_type"), nullable=False)
    check_frequency: Mapped[int] = Column(Integer, nullable=False)  # in minutes
    is_active: Mapped[bool] = Column(Boolean, default=True)
    last_checked: Mapped[Optional[datetime]] = Column(DateTime)
    health_status: Mapped[str] = Column(Enum("healthy", "warning", "error", name="health_status"), default="healthy")
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    articles: Mapped[List["Article"]] = relationship("Article", back_populates="feed", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of the NewsFeed model."""
        return f"<NewsFeed {self.name}>"