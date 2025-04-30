"""
API routes for article management.
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.article import ArticleRepository
from app.schemas.article import Article

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("", response_model=List[Article])
async def get_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    source: Optional[str] = None,
    feed_id: Optional[uuid.UUID] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get articles with filters.
    
    Args:
        skip: Number of articles to skip
        limit: Maximum number of articles to return
        source: Filter by source
        feed_id: Filter by feed ID
        date_from: Filter by date from
        date_to: Filter by date to
        search: Search term
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[Article]: List of articles
    """
    article_repo = ArticleRepository(db)
    
    # If search term is provided, use search function
    if search:
        articles, _ = await article_repo.search_articles(search, skip=skip, limit=limit)
        return articles
    
    # If feed_id is provided, get articles by feed
    if feed_id:
        articles = await article_repo.get_by_feed_id(feed_id, skip=skip, limit=limit)
        return articles
    
    # Default to recent articles
    articles = await article_repo.get_recent_articles(days=30, skip=skip, limit=limit)
    return articles


@router.get("/{article_id}", response_model=Article)
async def get_article(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get an article by ID.
    
    Args:
        article_id: Article ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Article: Article
    """
    article_repo = ArticleRepository(db)
    article = await article_repo.get(id=article_id)
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    return article