"""
Database initialization script.
Creates initial data for development environment.
"""
import asyncio
import logging
from datetime import datetime, timedelta
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.article import Article
from app.models.client_profile import ClientProfile
from app.models.news_feed import NewsFeed
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_initial_data() -> None:
    """
    Create initial data in the database.
    """
    async with AsyncSessionLocal() as db:
        await create_initial_users(db)
        await create_initial_feeds(db)
        await create_initial_articles(db)


async def create_initial_users(db: AsyncSession) -> None:
    """
    Create initial users and client profiles.
    
    Args:
        db: Database session
    """
    # Check if users already exist
    user = await db.get(User, uuid.uuid4())
    if user:
        logger.info("Initial data already exists. Skipping creation.")
        return

    # Create admin user
    admin_user = User(
        email="admin@example.com",
        password_hash=get_password_hash("Admin123!"),
        first_name="Admin",
        last_name="User",
        is_active=True,
    )
    db.add(admin_user)
    await db.flush()
    
    # Create demo user
    demo_user = User(
        email="demo@example.com",
        password_hash=get_password_hash("Demo123!"),
        first_name="Demo",
        last_name="User",
        is_active=True,
    )
    db.add(demo_user)
    await db.flush()
    
    # Create client profiles for demo user
    tech_profile = ClientProfile(
        user_id=demo_user.id,
        name="Tech Company",
        description="A technology company focused on AI and machine learning",
        industry="Technology",
        keywords=["artificial intelligence", "machine learning", "deep learning", "neural networks"],
        is_active=True,
    )
    db.add(tech_profile)
    
    finance_profile = ClientProfile(
        user_id=demo_user.id,
        name="Finance Corp",
        description="A financial services company",
        industry="Finance",
        keywords=["banking", "investment", "fintech", "cryptocurrency"],
        is_active=True,
    )
    db.add(finance_profile)
    
    await db.commit()
    logger.info("Initial users and client profiles created")


async def create_initial_feeds(db: AsyncSession) -> None:
    """
    Create initial news feeds.
    
    Args:
        db: Database session
    """
    feeds = [
        NewsFeed(
            name="Tech News",
            url="https://feeds.feedburner.com/TechCrunch",
            type="rss",
            check_frequency=60,  # 1 hour
            is_active=True,
            health_status="healthy",
        ),
        NewsFeed(
            name="Business News",
            url="https://feeds.bloomberg.com/markets/news.rss",
            type="rss",
            check_frequency=120,  # 2 hours
            is_active=True,
            health_status="healthy",
        ),
        NewsFeed(
            name="AI News",
            url="https://www.artificialintelligence-news.com/feed/",
            type="rss",
            check_frequency=180,  # 3 hours
            is_active=True,
            health_status="healthy",
        ),
    ]
    
    for feed in feeds:
        db.add(feed)
    
    await db.commit()
    logger.info("Initial news feeds created")


async def create_initial_articles(db: AsyncSession) -> None:
    """
    Create initial articles for development.
    
    Args:
        db: Database session
    """
    # Get the first feed
    feeds = await db.execute("SELECT id FROM news_feeds LIMIT 3")
    feed_ids = [row[0] for row in feeds.fetchall()]
    
    if not feed_ids:
        logger.warning("No feeds found. Skipping article creation.")
        return
    
    # Create sample articles
    articles = []
    for i in range(10):
        feed_index = i % len(feed_ids)
        days_ago = 10 - i
        
        article = Article(
            feed_id=feed_ids[feed_index],
            title=f"Sample Article {i+1}",
            url=f"https://example.com/article-{i+1}",
            source=f"Source {feed_index+1}",
            published_at=datetime.utcnow() - timedelta(days=days_ago),
            author="Sample Author",
            content=f"This is the content of sample article {i+1}. It contains some text that can be used for testing the application.",
            meta_data={"tags": ["sample", "test"], "word_count": 100 + i * 10},
        )
        articles.append(article)
    
    for article in articles:
        db.add(article)
    
    await db.commit()
    logger.info("Initial articles created")


async def init() -> None:
    """
    Initialize the database with initial data.
    """
    try:
        logger.info("Creating initial data")
        await create_initial_data()
        logger.info("Initial data created")
    except Exception as e:
        logger.error(f"Error creating initial data: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(init())