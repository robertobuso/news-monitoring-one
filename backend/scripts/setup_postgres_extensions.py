"""
Script to set up required PostgreSQL extensions.
"""
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_postgres_extensions():
    """
    Set up required PostgreSQL extensions like pg_trgm for GIN indexes.
    """
    async with AsyncSessionLocal() as db:
        try:
            logger.info("Enabling pg_trgm extension...")
            await db.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
            await db.commit()
            logger.info("pg_trgm extension enabled successfully")
            
            # Add more extensions here if needed
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error setting up PostgreSQL extensions: {e}")
            raise


if __name__ == "__main__":
    logger.info("Setting up PostgreSQL extensions...")
    asyncio.run(setup_postgres_extensions())