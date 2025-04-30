"""
Base models and imports for SQLAlchemy models.
This file is used by Alembic for migrations.
"""

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

class Base(AsyncAttrs, DeclarativeBase):
    pass

def load_models():
    from app.models import user  # ← late import avoids circular issue
    # Import all models to register them with Base.metadata
