"""
Script to seed the database with test data.
"""
import asyncio
import logging
from datetime import datetime, timedelta
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.client_profile import ClientProfile
from app.models.news_feed import NewsFeed
from app.models.article import Article

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_database():
    """
    Seed the database with test data.
    """
    async with AsyncSessionLocal() as db:
        # Check if data already exists - using text() for raw SQL
        user_result = await db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = user_result.scalar()
        
        if user_count > 0:
            logger.info("Database already contains users. Skipping seed.")
            return
        
        # Create test user
        test_user = User(
            email="test@example.com",
            password_hash=get_password_hash("password123"),
            first_name="Test",
            last_name="User",
            is_active=True,
        )
        db.add(test_user)
        await db.flush()
        
        logger.info(f"Created test user: {test_user.email}")
        
        # Create client profiles
        client_profiles = [
            ClientProfile(
                user_id=test_user.id,
                name="Tech Company",
                description="A leading technology company focused on AI and cloud computing",
                industry="Technology",
                keywords=["artificial intelligence", "cloud computing", "software development"],
                is_active=True,
            ),
            ClientProfile(
                user_id=test_user.id,
                name="Finance Corp",
                description="A financial services company specializing in investments and banking",
                industry="Finance",
                keywords=["banking", "investments", "fintech", "cryptocurrency"],
                is_active=True,
            ),
            ClientProfile(
                user_id=test_user.id,
                name="Green Energy Startup",
                description="A renewable energy startup focusing on solar and wind power",
                industry="Energy",
                keywords=["renewable energy", "solar power", "wind power", "sustainability"],
                is_active=True,
            ),
        ]
        
        for profile in client_profiles:
            db.add(profile)
        
        await db.flush()
        logger.info(f"Created {len(client_profiles)} client profiles")
        
        # Create news feeds
        feeds = [
            NewsFeed(
                name="Tech News",
                url="https://feeds.feedburner.com/TechCrunch",
                type="rss",
                check_frequency="60",  # Check every 60 minutes
                is_active=True,
                health_status="healthy",
            ),
            NewsFeed(
                name="Finance News",
                url="https://feeds.bloomberg.com/markets/news.rss",
                type="rss",
                check_frequency="120",  # Check every 2 hours
                is_active=True,
                health_status="healthy",
            ),
            NewsFeed(
                name="Energy News",
                url="https://feeds.reuters.com/reuters/environment",
                type="rss",
                check_frequency="180",  # Check every 3 hours
                is_active=True,
                health_status="healthy",
            ),
        ]
        
        for feed in feeds:
            db.add(feed)
        
        await db.flush()
        logger.info(f"Created {len(feeds)} news feeds")
        
        # Create sample articles - using meta_data instead of metadata
        sample_articles = [
            Article(
                feed_id=feeds[0].id,
                title="New AI Breakthrough Changes the Game",
                url="https://example.com/ai-breakthrough",
                source="Tech News",
                published_at=datetime.utcnow() - timedelta(days=1),
                author="John Smith",
                content="A new breakthrough in artificial intelligence is changing the way companies approach machine learning...",
                meta_data={"topics": ["AI", "Machine Learning"], "sentiment": "positive"},
            ),
            Article(
                feed_id=feeds[1].id,
                title="Markets React to New Financial Regulations",
                url="https://example.com/finance-regulations",
                source="Finance News",
                published_at=datetime.utcnow() - timedelta(days=2),
                author="Jane Doe",
                content="Global markets are reacting to new financial regulations announced yesterday...",
                meta_data={"topics": ["Regulations", "Markets"], "sentiment": "neutral"},
            ),
            Article(
                feed_id=feeds[2].id,
                title="Renewable Energy Investments Reach Record High",
                url="https://example.com/renewable-investments",
                source="Energy News",
                published_at=datetime.utcnow() - timedelta(days=3),
                author="Alex Johnson",
                content="Investments in renewable energy have reached a record high this quarter...",
                meta_data={"topics": ["Renewable Energy", "Investments"], "sentiment": "positive"},
            ),
        ]
        
        for article in sample_articles:
            db.add(article)
        
        await db.commit()
        logger.info(f"Created {len(sample_articles)} sample articles")
        
        logger.info("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())