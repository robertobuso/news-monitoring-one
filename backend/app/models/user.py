"""
User model for authentication and user management.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.db.base import Base


class User(Base):
    """
    User model representing application users.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = Column(String, nullable=False)
    first_name: Mapped[str] = Column(String, nullable=False)
    last_name: Mapped[str] = Column(String, nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    client_profiles: Mapped[List["ClientProfile"]] = relationship("ClientProfile", back_populates="user", cascade="all, delete-orphan")
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of the User model."""
        return f"<User {self.email}>"