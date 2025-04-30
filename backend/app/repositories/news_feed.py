"""
News feed repository for news feed-related database operations.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news_feed import NewsFeed
from app.repositories.base import BaseRepository
from app.schemas.news_feed import NewsFeedCreate, NewsFeedUpdate


class NewsFeedRepository(BaseRepository[NewsFeed, NewsFeedCreate, NewsFeedUpdate]):
    """
    Repository for NewsFeed model operations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize news feed repository.
        
        Args:
            db: SQLAlchemy async session
        """
        super().__init__(NewsFeed, db)

    async def get_active_feeds(self) -> List[NewsFeed]:
        """
        Get all active news feeds.
        
        Returns:
            List[NewsFeed]: List of active news feeds
        """
        query = select(NewsFeed).where(NewsFeed.is_active == True)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_feeds_due_for_check(self, current_time: datetime) -> List[NewsFeed]:
        """
        Get feeds that are due for checking.
        
        Args:
            current_time: Current time
            
        Returns:
            List[NewsFeed]: List of feeds due for checking
        """
        query = select(NewsFeed).where(
            NewsFeed.is_active == True,
            (
                (NewsFeed.last_checked == None) | 
                (current_time >= NewsFeed.last_checked + NewsFeed.check_frequency * 60)
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_last_checked(self, feed_id: str, status: str) -> Optional[NewsFeed]:
        """
        Update the last checked time and health status of a feed.
        
        Args:
            feed_id: Feed ID
            status: Health status
            
        Returns:
            Optional[NewsFeed]: Updated feed if found, None otherwise
        """
        feed = await self.get(id=feed_id)
        if not feed:
            return None
            
        feed.last_checked = datetime.utcnow()
        feed.health_status = status
        self.db.add(feed)
        await self.db.commit()
        await self.db.refresh(feed)
        return feed