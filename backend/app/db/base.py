"""
Base models and imports for SQLAlchemy models.
This file is used by Alembic for migrations.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs

# Create declarative base for SQLAlchemy models
Base = declarative_base(cls=AsyncAttrs)

# Import all models here for Alembic to discover
from app.models.user import User  # noqa