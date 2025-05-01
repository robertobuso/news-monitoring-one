"""
Article repository for article-related database operations.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Tuple, Union

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.article_relevance import ArticleRelevance
from app.repositories.base import BaseRepository
from app.schemas.article import ArticleCreate, ArticleRelevanceCreate, ArticleRelevanceUpdate, ArticleUpdate


class ArticleRepository(BaseRepository[Article, ArticleCreate, ArticleUpdate]):
    """
    Repository for Article model operations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize article repository.
        
        Args:
            db: SQLAlchemy async session
        """
        super().__init__(Article, db)

    async def get_by_url(self, url: str) -> Optional[Article]:
        """
        Get an article by URL.
        
        Args:
            url: Article URL
            
        Returns:
            Optional[Article]: Article if found, None otherwise
        """
        query = select(Article).where(Article.url == url)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_feed_id(self, feed_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Article]:
        """
        Get articles by feed ID.
        
        Args:
            feed_id: Feed ID
            skip: Number of articles to skip
            limit: Maximum number of articles to return
            
        Returns:
            List[Article]: List of articles
        """
        query = select(Article).where(Article.feed_id == feed_id).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_recent_articles(
        self, days: int = 7, skip: int = 0, limit: int = 100
    ) -> List[Article]:
        """
        Get recent articles.
        
        Args:
            days: Number of days to look back
            skip: Number of articles to skip
            limit: Maximum number of articles to return
            
        Returns:
            List[Article]: List of recent articles
        """
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)
        query = select(Article).where(
            Article.published_at >= cutoff_date
        ).order_by(
            Article.published_at.desc()
        ).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def search_articles(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Article], int]:
        """
        Search articles by content.
        
        Args:
            search_term: Search term
            skip: Number of articles to skip
            limit: Maximum number of articles to return
            
        Returns:
            Tuple[List[Article], int]: List of articles and total count
        """
        # Using PostgreSQL full-text search
        search_query = f"%{search_term}%"
        
        # Count total results
        count_query = select(func.count()).where(
            or_(
                Article.title.ilike(search_query),
                Article.content.ilike(search_query)
            )
        )
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar()
        
        # Get paginated results
        query = select(Article).where(
            or_(
                Article.title.ilike(search_query),
                Article.content.ilike(search_query)
            )
        ).order_by(
            Article.published_at.desc()
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all(), total_count


class ArticleRelevanceRepository:
    """
    Repository for ArticleRelevance model operations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize article relevance repository.
        
        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def get(self, id: uuid.UUID) -> Optional[ArticleRelevance]:
        """
        Get an article relevance by ID.
        
        Args:
            id: Article relevance ID
            
        Returns:
            Optional[ArticleRelevance]: Article relevance if found, None otherwise
        """
        query = select(ArticleRelevance).where(ArticleRelevance.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_article_and_client(
        self, article_id: uuid.UUID, client_id: uuid.UUID
    ) -> Optional[ArticleRelevance]:
        """
        Get an article relevance by article ID and client ID.
        
        Args:
            article_id: Article ID
            client_id: Client ID
            
        Returns:
            Optional[ArticleRelevance]: Article relevance if found, None otherwise
        """
        query = select(ArticleRelevance).where(
            and_(
                ArticleRelevance.article_id == article_id,
                ArticleRelevance.client_id == client_id
            )
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_client_id(
        self, client_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[ArticleRelevance]:
        """
        Get article relevances by client ID.
        
        Args:
            client_id: Client ID
            skip: Number of article relevances to skip
            limit: Maximum number of article relevances to return
            
        Returns:
            List[ArticleRelevance]: List of article relevances
        """
        query = select(ArticleRelevance).where(
            ArticleRelevance.client_id == client_id
        ).order_by(
            ArticleRelevance.relevance_score.desc()
        ).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: ArticleRelevanceCreate) -> ArticleRelevance:
        """
        Create a new article relevance.
        
        Args:
            obj_in: Article relevance creation data
            
        Returns:
            ArticleRelevance: Created article relevance
        """
        db_obj = ArticleRelevance(
            article_id=obj_in.article_id,
            client_id=obj_in.client_id,
            relevance_score=obj_in.relevance_score,
            summary=obj_in.summary,
            is_included=obj_in.is_included,
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, db_obj: ArticleRelevance, obj_in: ArticleRelevanceUpdate
    ) -> ArticleRelevance:
        """
        Update an article relevance.
        
        Args:
            db_obj: Article relevance to update
            obj_in: Article relevance update data
            
        Returns:
            ArticleRelevance: Updated article relevance
        """
        update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
            
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def remove(self, id: uuid.UUID) -> Optional[ArticleRelevance]:
        """
        Remove an article relevance.
        
        Args:
            id: Article relevance ID
            
        Returns:
            Optional[ArticleRelevance]: Removed article relevance if found, None otherwise
        """
        obj = await self.get(id=id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
        return obj
    
    async def get_unprocessed_articles(self, limit: int = 50) -> List[Article]:
        """
        Get articles that haven't been processed for relevance yet.
        
        Args:
            limit: Maximum number of articles to return
            
        Returns:
            List[Article]: List of unprocessed articles
        """
        # Find articles that don't have any relevance records
        # This requires a LEFT JOIN with article_relevances
        from sqlalchemy import outerjoin, func
        from app.models.article_relevance import ArticleRelevance
        
        query = select(Article).outerjoin(
            ArticleRelevance, 
            Article.id == ArticleRelevance.article_id
        ).group_by(
            Article.id
        ).having(
            func.count(ArticleRelevance.id) == 0
        ).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_client_id_and_date_range(
        self, 
        client_id: uuid.UUID,
        date_from: Optional[Union[datetime, str]] = None,
        date_to: Optional[Union[datetime, str]] = None,
        min_score: float = 0.0,
        is_included: Optional[bool] = None,
        limit: int = 50
    ) -> List[ArticleRelevance]:
        """
        Get article relevances by client ID and date range.
        
        Args:
            client_id: Client ID
            date_from: Optional start date filter
            date_to: Optional end date filter
            min_score: Minimum relevance score
            is_included: Optional filter for included status
            limit: Maximum number of article relevances to return
            
        Returns:
            List[ArticleRelevance]: List of article relevances
        """
        from sqlalchemy import and_
        from app.models.article import Article
        
        # Convert string dates to datetime if needed
        if isinstance(date_from, str):
            date_from = datetime.fromisoformat(date_from)
        if isinstance(date_to, str):
            date_to = datetime.fromisoformat(date_to)
        
        # Build query conditions
        conditions = [ArticleRelevance.client_id == client_id]
        
        if min_score > 0:
            conditions.append(ArticleRelevance.relevance_score >= min_score)
        
        if is_included is not None:
            conditions.append(ArticleRelevance.is_included == is_included)
        
        # Join with Article to apply date filters
        query = select(ArticleRelevance).join(
            Article, 
            ArticleRelevance.article_id == Article.id
        )
        
        # Add date filters if provided
        if date_from:
            query = query.where(Article.published_at >= date_from)
        if date_to:
            query = query.where(Article.published_at <= date_to)
        
        # Add other conditions and ordering
        query = query.where(and_(*conditions)).order_by(
            ArticleRelevance.relevance_score.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()