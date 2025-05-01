"""
Article repository for article-related database operations.
"""
import uuid
from datetime import datetime, timedelta # Ensure timedelta is imported
from typing import List, Optional, Tuple, Union, Dict, Any

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

    # --- NEW or MODIFIED get_multi ---
    # Override the base get_multi to add filtering capabilities
    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Article], int]:
        """
        Get multiple article records with filtering, ordering, and pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            filters: Dictionary of filters to apply (e.g., {"feed_id": uuid, "source": "..."}).

        Returns:
            Tuple[List[Article], int]: List of articles and total count matching filters.
        """
        select_stmt = select(self.model)
        count_stmt = select(func.count()).select_from(self.model)

        if filters:
            conditions = []
            for key, value in filters.items():
                if value is None: # Skip None values unless explicitly handled
                    continue
                column = getattr(self.model, key, None)
                if column is not None:
                    # Handle specific filter types if needed
                    if key == "search": # Assuming 'search' is a special filter key
                         search_query = f"%{value}%"
                         search_condition = or_(
                             self.model.title.ilike(search_query),
                             self.model.content.ilike(search_query)
                         )
                         conditions.append(search_condition)
                    elif key == "date_from":
                         conditions.append(self.model.published_at >= value)
                    elif key == "date_to":
                         conditions.append(self.model.published_at <= value)
                    else:
                         conditions.append(column == value)
                else:
                    # Log or raise error for invalid filter key
                    pass # Or: logger.warning(f"Invalid filter key: {key}")

            if conditions:
                select_stmt = select_stmt.where(and_(*conditions))
                count_stmt = count_stmt.where(and_(*conditions))

        # Get total count before pagination
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one_or_none() or 0

        # Apply ordering and pagination to the select statement
        select_stmt = select_stmt.order_by(self.model.published_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(select_stmt)
        data = result.scalars().all()
        return data, total

    # Keep other specific methods like get_by_url, etc.
    async def get_by_url(self, url: str) -> Optional[Article]:
        """ Get an article by URL. """
        query = select(Article).where(Article.url == url)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_recent_articles(
        self, days: int = 7, skip: int = 0, limit: int = 100
    ) -> List[Article]:
        """ Get recent articles. """
        # Ensure timedelta is available
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = select(Article).where(
            Article.published_at >= cutoff_date
        ).order_by(
            Article.published_at.desc()
        ).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    # search_articles can potentially be merged into get_multi logic above
    # If keeping separate:
    async def search_articles(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Article], int]:
        """ Search articles by content. """
        search_query = f"%{search_term}%"
        search_filter = or_(
            Article.title.ilike(search_query),
            Article.content.ilike(search_query)
        )

        count_query = select(func.count()).select_from(Article).where(search_filter)
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar_one_or_none() or 0

        query = select(Article).where(search_filter).order_by(
            Article.published_at.desc()
        ).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all(), total_count
    
    async def get_by_article_id(
        self, 
        article_id: uuid.UUID,
        min_score: float = 0.0
    ) -> List[ArticleRelevance]:
        """
        Get article relevances for a specific article.
        
        Args:
            article_id: Article ID
            min_score: Minimum relevance score
            
        Returns:
            List[ArticleRelevance]: List of article relevances
        """
        query = select(ArticleRelevance).where(
            and_(
                ArticleRelevance.article_id == article_id,
                ArticleRelevance.relevance_score >= min_score
            )
        ).order_by(
            ArticleRelevance.relevance_score.desc()
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
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
            limit: Maximum number of articles to return (default: 50, max: 100)
            
        Returns:
            List[Article]: List of unprocessed articles
        """
        # Ensure we don't exceed server limits
        if limit > 100:
            limit = 100
            
        # Find articles that don't have any relevance records
        # This requires a LEFT JOIN with article_relevances
        from sqlalchemy import outerjoin, func
        
        query = select(Article).outerjoin(
            ArticleRelevance, 
            Article.id == ArticleRelevance.article_id
        ).group_by(
            Article.id
        ).having(
            func.count(ArticleRelevance.id) == 0
        ).order_by(
            Article.published_at.desc()  # Get newest articles first
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