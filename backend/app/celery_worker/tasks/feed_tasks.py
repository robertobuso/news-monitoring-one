"""
Celery tasks for feed processing.
"""
import logging
from datetime import datetime
import uuid

from celery import shared_task

from app.db.session import AsyncSessionLocal
from app.repositories.news_feed import NewsFeedRepository
from app.services.feed_service import FeedService

logger = logging.getLogger(__name__)


@shared_task(name="process_all_feeds")
def process_all_feeds():
    """
    Process all active feeds that are due for checking.
    """
    logger.info("Starting scheduled feed processing")
    
    async def _process_feeds():
        async with AsyncSessionLocal() as db:
            feed_repo = NewsFeedRepository(db)
            feed_service = FeedService(db)
            
            # Get feeds due for checking
            current_time = datetime.utcnow()
            feeds = await feed_repo.get_feeds_due_for_check(current_time)
            
            logger.info(f"Found {len(feeds)} feeds due for checking")
            
            for feed in feeds:
                try:
                    logger.info(f"Processing feed: {feed.name} ({feed.id})")
                    result = await feed_service.process_feed(feed.id)
                    
                    if result["success"]:
                        logger.info(f"Successfully processed feed {feed.id}. Saved {len(result.get('articles', []))} new articles.")
                    else:
                        logger.error(f"Failed to process feed {feed.id}: {result['message']}")
                
                except Exception as e:
                    logger.error(f"Error processing feed {feed.id}: {e}")
    
    # Run the async function
    import asyncio
    asyncio.run(_process_feeds())
    
    logger.info("Completed scheduled feed processing")


@shared_task(name="process_feed")
def process_feed(feed_id: str):
    """
    Process a specific feed.
    
    Args:
        feed_id: Feed ID
    """
    logger.info(f"Processing feed {feed_id}")
    
    async def _process_feed():
        async with AsyncSessionLocal() as db:
            feed_service = FeedService(db)
            result = await feed_service.process_feed(uuid.UUID(feed_id))
            
            if result["success"]:
                logger.info(f"Successfully processed feed {feed_id}. Saved {len(result.get('articles', []))} new articles.")
            else:
                logger.error(f"Failed to process feed {feed_id}: {result['message']}")
    
    # Run the async function
    import asyncio
    asyncio.run(_process_feed())


@shared_task(name="check_feed_health")
def check_feed_health():
    """
    Check the health of all feeds.
    """
    logger.info("Starting feed health check")
    
    async def _check_health():
        async with AsyncSessionLocal() as db:
            feed_repo = NewsFeedRepository(db)
            feed_service = FeedService(db)
            
            # Get all active feeds
            feeds = await feed_repo.get_active_feeds()
            
            logger.info(f"Checking health of {len(feeds)} feeds")
            
            for feed in feeds:
                try:
                    # Test connection
                    result = await feed_service.test_feed_connection(feed.url, feed.type)
                    
                    if result["success"]:
                        await feed_service.update_feed_health(feed.id, "healthy")
                        logger.info(f"Feed {feed.id} is healthy")
                    else:
                        await feed_service.update_feed_health(feed.id, "error", result["message"])
                        logger.warning(f"Feed {feed.id} is unhealthy: {result['message']}")
                
                except Exception as e:
                    await feed_service.update_feed_health(feed.id, "error", str(e))
                    logger.error(f"Error checking feed {feed.id} health: {e}")
    
    # Run the async function
    import asyncio
    asyncio.run(_check_health())
    
    logger.info("Completed feed health check")