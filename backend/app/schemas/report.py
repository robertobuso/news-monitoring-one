"""
Pydantic schemas for report data validation.
"""
import uuid
from datetime import datetime, date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class ReportGenerateRequest(BaseModel):
    client_id: uuid.UUID
    report_date: Optional[date] = None

class ReportStatus(str, Enum):
    """Enum for report status."""
    PENDING = "pending"
    GENERATING = "generating"
    READY = "ready"
    SENT = "sent"
    ERROR = "error"


class ReportArticleBase(BaseModel):
    """Base schema for report article data."""
    article_id: uuid.UUID
    summary: Optional[str] = None
    position: int


class ReportArticleCreate(ReportArticleBase):
    """Schema for report article creation."""
    pass


class ReportArticleUpdate(BaseModel):
    """Schema for report article updates."""
    summary: Optional[str] = None
    position: Optional[int] = None


class ReportArticleInDBBase(ReportArticleBase):
    """Base schema for report article in database."""
    id: uuid.UUID
    report_id: uuid.UUID

    class Config:
        orm_mode = True


class ReportArticle(ReportArticleInDBBase):
    """Schema for report article response."""
    pass


class ReportBase(BaseModel):
    """Base schema for report data."""
    client_id: uuid.UUID
    report_date: datetime
    recipient_email: Optional[EmailStr] = None


class ReportCreate(ReportBase):
    """Schema for report creation."""
    pass


class ReportUpdate(BaseModel):
    """Schema for report updates."""
    pdf_path: Optional[str] = None
    sent_at: Optional[datetime] = None
    recipient_email: Optional[EmailStr] = None
    status: Optional[ReportStatus] = None


class ReportInDBBase(ReportBase):
    """Base schema for report in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    pdf_path: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    status: ReportStatus

    class Config:
        orm_mode = True


class Report(ReportInDBBase):
    """Schema for report response."""
    pass


class ReportInDB(ReportInDBBase):
    """Schema for report in database."""
    pass


class ReportWithArticles(Report):
    """Schema for report with articles."""
    report_articles: List[ReportArticle] = []