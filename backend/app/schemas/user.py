"""
Pydantic schemas for user data validation.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8)

    @validator("password")
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserUpdate(BaseModel):
    """Schema for user updates."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    """Base schema for user in database."""
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class User(UserInDBBase):
    """Schema for user response."""
    pass


class UserInDB(UserInDBBase):
    """Schema for user in database with password hash."""
    password_hash: str