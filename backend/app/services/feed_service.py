"""
Feed service for managing news feeds and processing articles.
"""
import logging
from datetime import datetime
import uuid
from typing import Dict, List, Optional, Union
import asyncio

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
from app.services.ai_service import AIService


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
        self.ai_service = AIService(db) 
    
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
        Triggers background AI analysis for new articles.

        Args:
            feed_id: Feed ID

        Returns:
            Dict: Result with success status, message, and basic info (not waiting for AI)
        """
        feed = await self.feed_repo.get(id=feed_id)
        if not feed:
            return {"success": False, "message": "Feed not found"}

        try:
            if feed.type == "rss":
                result = parse_rss_feed(feed.url)
            elif feed.type == "web":
                # Assuming scrape_website returns a similar structure
                # with potentially one article under "article" key
                result = await scrape_website(feed.url)
            else:
                return {"success": False, "message": f"Unsupported feed type: {feed.type}"}

            if not result["success"]:
                await self.update_feed_health(feed_id, "error", result.get("message", "Parsing/Scraping failed"))
                return result

            # Process articles
            articles_data = result.get("articles", [])
            if feed.type == "web" and "article" in result and result["article"]:
                 # Ensure web scraper result is wrapped in a list if needed
                 articles_data = [result["article"]] if isinstance(result["article"], dict) else []

            newly_saved_article_ids = []
            processed_count = 0
            skipped_count = 0

            for article_dict in articles_data:
                processed_count += 1
                # Check for duplicates by URL
                existing = await self.article_repo.get_by_url(article_dict["url"])
                if existing:
                    skipped_count += 1
                    continue

                # --- Prepare data for ArticleCreate ---
                # Clean content if needed (basic check)
                content = article_dict.get("content", "")
                if content and "<" in content and ">" in content:
                    cleaned_content = clean_html(content)
                else:
                    cleaned_content = content

                # Basic metadata extraction (can be improved)
                meta_data = extract_metadata(cleaned_content)

                try:
                    article_create_schema = ArticleCreate(
                        feed_id=feed_id,
                        title=article_dict.get("title", "No Title Provided"),
                        url=article_dict["url"], # URL should always exist
                        source=article_dict.get("source", feed.name), # Fallback to feed name
                        published_at=article_dict["published_at"], # Should be datetime object now
                        author=article_dict.get("author"),
                        content=cleaned_content,
                        meta_data=meta_data
                    )
                except Exception as pydantic_error:
                    logger.error(f"Pydantic validation failed for article {article_dict.get('url')}: {pydantic_error}")
                    continue # Skip this article if basic data is invalid

                # --- Save the article ---
                try:
                    article = await self.article_repo.create(obj_in=article_create_schema)
                    newly_saved_article_ids.append(article.id)
                    logger.info(f"Saved new article: {article.id} - {article.title}")

                    # --- Trigger background AI processing for the new article ---
                    # We don't await this, let it run in the background
                    asyncio.create_task(self.ai_service.process_article(article.id))
                    logger.info(f"Triggered background analysis for article: {article.id}")
                    # ------------------------------------------------------------

                except Exception as db_error:
                     logger.error(f"Database error saving article {article_dict.get('url')}: {db_error}")
                     # Consider rolling back the specific article insert if needed,
                     # although commit happens inside repo.create now.
                     # Might need transaction management at the service level for batch inserts.

            # Update feed health and last checked time
            await self.update_feed_health(feed_id, "healthy")

            saved_count = len(newly_saved_article_ids)
            message = (f"Processed {processed_count} articles from feed. "
                       f"Saved {saved_count} new articles. Skipped {skipped_count} duplicates. "
                       f"Background analysis triggered for new articles.")

            return {
                "success": True,
                "message": message,
                "saved_count": saved_count,
                "skipped_count": skipped_count,
                "total_parsed": processed_count
                # Avoid returning full article list here as analysis isn't done yet
            }

        except Exception as e:
            logger.error(f"Error processing feed {feed_id}: {e}", exc_info=True) # Add traceback
            await self.update_feed_health(feed_id, "error", str(e))
            # Ensure db session is rolled back in case of error before health update commit
            await self.db.rollback()
            # We might need to recommit the health update in a separate step/session
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