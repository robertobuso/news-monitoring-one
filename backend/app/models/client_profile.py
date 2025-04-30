"""
Client profile model for managing client information.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, relationship

from app.db.base import Base


class ClientProfile(Base):
    """
    Client profile model representing client information and preferences.
    """
    __tablename__ = "client_profiles"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = Column(String, nullable=False)
    description: Mapped[Optional[str]] = Column(Text)
    industry: Mapped[str] = Column(String)
    keywords: Mapped[List[str]] = Column(ARRAY(String), nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="client_profiles")
    article_relevances: Mapped[List["ArticleRelevance"]] = relationship("ArticleRelevance", back_populates="client_profile", cascade="all, delete-orphan")
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="client_profile", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of the ClientProfile model."""
        return f"<ClientProfile {self.name}>"