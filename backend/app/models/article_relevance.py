"""
Article relevance model for tracking article relevance to clients.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.db.base import Base


class ArticleRelevance(Base):
    """
    ArticleRelevance model representing the relevance of articles to client profiles.
    """
    __tablename__ = "article_relevances"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
    client_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("client_profiles.id"), nullable=False)
    relevance_score: Mapped[float] = Column(Float, nullable=False)
    summary: Mapped[Optional[str]] = Column(Text)
    is_included: Mapped[bool] = Column(Boolean, default=False)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)

    # Relationships
    article: Mapped["Article"] = relationship("Article", back_populates="article_relevances")
    client_profile: Mapped["ClientProfile"] = relationship("ClientProfile", back_populates="article_relevances")

    def __repr__(self) -> str:
        """String representation of the ArticleRelevance model."""
        return f"<ArticleRelevance article_id={self.article_id} client_id={self.client_id} score={self.relevance_score}>"

    # Create composite index
    __table_args__ = (
        Index("ix_article_relevances_client_id_relevance_score", "client_id", "relevance_score"),
    )