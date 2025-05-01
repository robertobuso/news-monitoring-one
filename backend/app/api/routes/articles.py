import uuid
from datetime import datetime, timedelta # Ensure datetime is imported
from typing import List, Optional, Dict, Any # Add Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
# Import the model if needed for type hints, otherwise schema is enough
# from app.models.article import Article as ArticleModel
from app.repositories.article import ArticleRepository
# Ensure you import the correct Pydantic schema for the response
from app.schemas.article import Article as ArticleSchema

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("", response_model=List[ArticleSchema])
async def get_articles(
    # Use Depends for DB and User
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    # Query parameters
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of articles to return"), # Adjusted default limit
    source: Optional[str] = Query(None, description="Filter by source"),
    feed_id: Optional[uuid.UUID] = Query(None, description="Filter by feed ID"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from (inclusive)"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to (inclusive)"),
    search: Optional[str] = Query(None, description="Search term for title or content"),
) -> List[ArticleSchema]: # Return type matches response_model
    """
    Get articles with combined filters and pagination.
    """
    article_repo = ArticleRepository(db)

    # Build filters dictionary from query parameters
    filters: Dict[str, Any] = {}
    if feed_id:
        filters["feed_id"] = feed_id
    if source:
        filters["source"] = source
    if date_from:
        filters["date_from"] = date_from
    if date_to:
        filters["date_to"] = date_to
    if search:
        # Use a specific key that your repository's get_multi understands
        filters["search"] = search

    # Call the enhanced get_multi method from ArticleRepository
    # This method should handle combining the filters in the WHERE clause
    # and return a tuple (list_of_articles, total_count)
    articles_list, total_count = await article_repo.get_multi(
        skip=skip,
        limit=limit,
        filters=filters if filters else None # Pass None if no filters
    )

    # TODO: Consider adding X-Total-Count header to the response for frontend pagination
    # e.g., from fastapi import Response
    # response.headers["X-Total-Count"] = str(total_count)

    return articles_list


@router.get("/{article_id}", response_model=ArticleSchema)
async def get_article(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any: # Return Any and let FastAPI handle Pydantic conversion from model
    """
    Get an article by ID.
    """
    article_repo = ArticleRepository(db)
    article = await article_repo.get(id=article_id)

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )

    # Let FastAPI convert the SQLAlchemy model instance (article)
    # to the ArticleSchema response_model.
    return article