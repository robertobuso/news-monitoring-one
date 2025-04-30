"""
Report model for storing generated reports.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.db.base import Base


class Report(Base):
    """
    Report model representing generated client reports.
    """
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    client_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("client_profiles.id"), nullable=False)
    report_date: Mapped[datetime] = Column(DateTime, nullable=False)
    pdf_path: Mapped[Optional[str]] = Column(String)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    sent_at: Mapped[Optional[datetime]] = Column(DateTime)
    recipient_email: Mapped[Optional[str]] = Column(String)
    status: Mapped[str] = Column(
        Enum("pending", "generating", "ready", "sent", "error", name="report_status"),
        default="pending"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reports")
    client_profile: Mapped["ClientProfile"] = relationship("ClientProfile", back_populates="reports")
    report_articles: Mapped[List["ReportArticle"]] = relationship("ReportArticle", back_populates="report", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of the Report model."""
        return f"<Report id={self.id} client_id={self.client_id} status={self.status}>"