"""
Report article model for linking articles to reports.
"""
import uuid
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.db.base import Base


class ReportArticle(Base):
    """
    ReportArticle model representing articles included in reports.
    """
    __tablename__ = "report_articles"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    article_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
    summary: Mapped[Optional[str]] = Column(Text)
    position: Mapped[int] = Column(Integer, nullable=False)

    # Relationships
    report: Mapped["Report"] = relationship("Report", back_populates="report_articles")
    article: Mapped["Article"] = relationship("Article", back_populates="report_articles")

    def __repr__(self) -> str:
        """String representation of the ReportArticle model."""
        return f"<ReportArticle report_id={self.report_id} article_id={self.article_id} position={self.position}>"