"""
Script to recreate the database from scratch.
This will drop all tables and recreate them.
"""
import asyncio
import logging
import sys

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy import text

from app.db.base import Base
from app.core.config import settings
from app.db.session import engine

# Import all models here to ensure they are registered with Base.metadata
from app.models.user import User
from app.models.client_profile import ClientProfile
from app.models.news_feed import NewsFeed 
from app.models.article import Article
from app.models.article_relevance import ArticleRelevance
from app.models.report import Report
from app.models.report_article import ReportArticle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_postgres_extensions():
    """Set up required PostgreSQL extensions."""
    try:
        logger.info("Enabling pg_trgm extension...")
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        logger.info("pg_trgm extension enabled successfully")
    except Exception as e:
        logger.error(f"Error setting up PostgreSQL extensions: {e}")
        raise


async def reset_database():
    """Reset database by dropping and recreating all tables."""
    try:
        # First set up PostgreSQL extensions
        await setup_postgres_extensions()
        
        logger.info("Dropping all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("All tables dropped successfully")

        logger.info("Creating all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("All tables created successfully")

        # Now import and run the seed script
        try:
            from scripts.seed_database import seed_database
            logger.info("Seeding database...")
            await seed_database()
            logger.info("Database seeded successfully")
        except ImportError:
            logger.warning("Seed script not found. Skipping database seeding.")
        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            raise

        logger.info("Database reset completed successfully")

    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise


if __name__ == "__main__":
    logger.info("Starting database reset...")
    asyncio.run(reset_database())