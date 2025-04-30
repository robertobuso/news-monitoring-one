"""
Pydantic schemas for client profile data validation.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ClientProfileBase(BaseModel):
    """Base schema for client profile data."""
    name: str
    description: Optional[str] = None
    industry: str
    keywords: List[str] = Field(..., min_items=1)
    is_active: bool = True


class ClientProfileCreate(ClientProfileBase):
    """Schema for client profile creation."""
    pass


class ClientProfileUpdate(BaseModel):
    """Schema for client profile updates."""
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    keywords: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ClientProfileInDBBase(ClientProfileBase):
    """Base schema for client profile in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ClientProfile(ClientProfileInDBBase):
    """Schema for client profile response."""
    pass


class ClientProfileInDB(ClientProfileInDBBase):
    """Schema for client profile in database."""
    pass