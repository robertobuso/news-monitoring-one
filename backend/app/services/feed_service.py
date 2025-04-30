"""
Feed service for managing news feeds and processing articles.
"""
import logging
from datetime import datetime
import uuid
from typing import Dict, List, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news_feed import NewsFeed
from app.repositories.news_feed import NewsFeedRepository
from app.repositories.article import ArticleRepository
from app.schemas.article import ArticleCreate
from app.schemas.news_feed import NewsFeedCreate, NewsFeedUpdate
from app.services.rss_parser import parse_rss_feed
from app.services.web_scraper import scrape_website
from app.services.content_extractor import extract_metadata, extract_text_from_html
from app.utils.html_cleaner import clean_html

logger = logging.getLogger(__name__)


class FeedService:
    """Service for managing news feeds and processing articles."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize feed service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.feed_repo = NewsFeedRepository(db)
        self.article_repo = ArticleRepository(db)
    
    async def create_feed(self, feed_data: NewsFeedCreate) -> NewsFeed:
        """
        Create a new feed.
        
        Args:
            feed_data: Feed creation data
            
        Returns:
            NewsFeed: Created feed
        """
        return await self.feed_repo.create(obj_in=feed_data)
    
    async def update_feed(self, feed_id: uuid.UUID, feed_data: NewsFeedUpdate) -> Optional[NewsFeed]:
        """
        Update a feed.
        
        Args:
            feed_id: Feed ID
            feed_data: Feed update data
            
        Returns:
            Optional[NewsFeed]: Updated feed if found, None otherwise
        """
        feed = await self.feed_repo.get(id=feed_id)
        if not feed:
            return None
        
        return await self.feed_repo.update(db_obj=feed, obj_in=feed_data)
    
    async def delete_feed(self, feed_id: uuid.UUID) -> bool:
        """
        Delete a feed.
        
        Args:
            feed_id: Feed ID
            
        Returns:
            bool: True if feed was deleted, False otherwise
        """
        feed = await self.feed_repo.remove(id=feed_id)
        return feed is not None
    
    async def get_feed(self, feed_id: uuid.UUID) -> Optional[NewsFeed]:
        """
        Get a feed by ID.
        
        Args:
            feed_id: Feed ID
            
        Returns:
            Optional[NewsFeed]: Feed if found, None otherwise
        """
        return await self.feed_repo.get(id=feed_id)
    
    async def get_all_feeds(self, skip: int = 0, limit: int = 100) -> List[NewsFeed]:
        """
        Get all feeds with pagination.
        
        Args:
            skip: Number of feeds to skip
            limit: Maximum number of feeds to return
            
        Returns:
            List[NewsFeed]: List of feeds
        """
        return await self.feed_repo.get_multi(skip=skip, limit=limit)
    
    async def test_feed_connection(self, url: str, feed_type: str) -> Dict[str, Union[bool, str]]:
        """
        Test connection to a feed.
        
        Args:
            url: Feed URL
            feed_type: Feed type (rss or web)
            
        Returns:
            Dict: Result with success status and message
        """
        try:
            if feed_type == "rss":
                result = parse_rss_feed(url)
                if not result["success"]:
                    return result
                
                # Check if we got any articles
                if not result.get("articles"):
                    return {"success": False, "message": "Feed parsed successfully but no articles found"}
                
                return {"success": True, "message": f"Successfully connected to RSS feed. Found {len(result['articles'])} articles."}
            
            elif feed_type == "web":
                result = await scrape_website(url)
                if not result["success"]:
                    return result
                
                return {"success": True, "message": "Successfully scraped website"}
            
            else:
                return {"success": False, "message": f"Unsupported feed type: {feed_type}"}
        
        except Exception as e:
            logger.error(f"Error testing feed connection: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    async def process_feed(self, feed_id: uuid.UUID) -> Dict[str, Union[bool, str, List]]:
        """
        Process a feed to fetch and store articles.
        
        Args:
            feed_id: Feed ID
            
        Returns:
            Dict: Result with success status, message, and saved articles
        """
        feed = await self.feed_repo.get(id=feed_id)
        if not feed:
            return {"success": False, "message": "Feed not found"}
        
        try:
            if feed.type == "rss":
                result = parse_rss_feed(feed.url)
            elif feed.type == "web":
                result = await scrape_website(feed.url)
            else:
                return {"success": False, "message": f"Unsupported feed type: {feed.type}"}
            
            if not result["success"]:
                await self.update_feed_health(feed_id, "error", result["message"])
                return result
            
            # Process articles
            articles = result.get("articles", [])
            if feed.type == "web" and "article" in result:
                articles = [result["article"]]
            
            saved_articles = []
            for article_data in articles:
                # Check for duplicates by URL
                existing = await self.article_repo.get_by_url(article_data["url"])
                if existing:
                    continue
                
                # Clean content and extract metadata
                if "<" in article_data["content"] and ">" in article_data["content"]:
                    article_data["content"] = clean_html(article_data["content"])
                
                article_data["metadata"] = extract_metadata(article_data["content"])
                
                # Create article
                article_create = ArticleCreate(
                    feed_id=feed_id,
                    title=article_data["title"],
                    url=article_data["url"],
                    source=article_data["source"],
                    published_at=article_data["published_at"],
                    author=article_data["author"],
                    content=article_data["content"],
                    metadata=article_data["metadata"]
                )
                
                article = await self.article_repo.create(obj_in=article_create)
                saved_articles.append(article)
            
            # Update feed health
            await self.update_feed_health(feed_id, "healthy")
            
            return {
                "success": True, 
                "message": f"Processed feed successfully. Saved {len(saved_articles)} new articles.",
                "articles": saved_articles
            }
        
        except Exception as e:
            logger.error(f"Error processing feed {feed_id}: {e}")
            await self.update_feed_health(feed_id, "error", str(e))
            return {"success": False, "message": f"Error: {str(e)}"}
    
    async def update_feed_health(self, feed_id: uuid.UUID, status: str, message: Optional[str] = None) -> None:
        """
        Update feed health status.
        
        Args:
            feed_id: Feed ID
            status: Health status (healthy, warning, error)
            message: Optional error message
        """
        feed = await self.feed_repo.get(id=feed_id)
        if not feed:
            return
        
        update_data = {
            "health_status": status,
            "last_checked": datetime.utcnow()
        }
        
        await self.feed_repo.update(db_obj=feed, obj_in=update_data)
        
        if message and status == "error":
            logger.error(f"Feed {feed_id} health status: {status}. Error: {message}")
        else:
            logger.info(f"Feed {feed_id} health status: {status}")