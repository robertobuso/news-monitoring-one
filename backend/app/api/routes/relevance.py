"""
API routes for article relevance and AI analysis.
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.article import ArticleRepository, ArticleRelevanceRepository
from app.repositories.client_profile import ClientProfileRepository
from app.schemas.article import Article, ArticleRelevance
from app.services.ai_service import AIService

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("/relevant", response_model=List[dict])
async def get_relevant_articles(
    client_id: uuid.UUID,
    min_score: float = Query(0.6, ge=0.0, le=1.0),
    limit: int = Query(20, ge=1, le=100),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get articles relevant to a specific client profile.
    
    Args:
        client_id: Client profile ID
        min_score: Minimum relevance score (0.0 to 1.0)
        limit: Maximum number of articles to return
        date_from: Optional start date filter
        date_to: Optional end date filter
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[dict]: List of relevant articles with their relevance data
    """
    # Verify client profile exists and belongs to user
    client_repo = ClientProfileRepository(db)
    client_profile = await client_repo.get(id=client_id)
    
    if not client_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found"
        )
    
    if client_profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this client profile"
        )
    
    # Get relevant articles
    ai_service = AIService(db)
    relevant_articles = await ai_service.get_relevant_articles_for_client(
        client_id=client_id,
        min_score=min_score,
        limit=limit,
        date_from=date_from.isoformat() if date_from else None,
        date_to=date_to.isoformat() if date_to else None
    )
    
    return relevant_articles


@router.get("/by-client/{client_id}", response_model=List[Article])
async def get_articles_by_client(
    client_id: uuid.UUID,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get articles matched to a specific client profile.
    
    Args:
        client_id: Client profile ID
        date_from: Optional start date filter
        date_to: Optional end date filter
        limit: Maximum number of articles to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[Article]: List of articles
    """
    # Verify client profile exists and belongs to user
    client_repo = ClientProfileRepository(db)
    client_profile = await client_repo.get(id=client_id)
    
    if not client_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found"
        )
    
    if client_profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this client profile"
        )
    
    # Get articles by client
    relevance_repo = ArticleRelevanceRepository(db)
    article_repo = ArticleRepository(db)
    
    # Set default date range if not provided
    if not date_from:
        date_from = datetime.utcnow() - timedelta(days=30)
    if not date_to:
        date_to = datetime.utcnow()
    
    # Get relevances for client
    relevances = await relevance_repo.get_by_client_id_and_date_range(
        client_id=client_id,
        date_from=date_from,
        date_to=date_to,
        is_included=True,
        limit=limit
    )
    
    # Get articles
    articles = []
    for relevance in relevances:
        article = await article_repo.get(id=relevance.article_id)
        if article:
            articles.append(article)
    
    return articles


@router.post("/{article_id}/analyze", status_code=status.HTTP_200_OK)
async def analyze_article(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze an article with AI to determine relevance to client profiles.
    
    Args:
        article_id: Article ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Analysis results
    """
    # Verify article exists
    article_repo = ArticleRepository(db)
    article = await article_repo.get(id=article_id)
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Process article with AI
    ai_service = AIService(db)
    result = await ai_service.process_article(article_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Failed to analyze article")
        )
    
    return result


@router.get("/{article_id}/summary", status_code=status.HTTP_200_OK)
async def get_article_summary(
    article_id: uuid.UUID,
    client_id: Optional[uuid.UUID] = None,
    max_length: int = Query(200, ge=50, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a summary of an article, optionally tailored to a client profile.
    
    Args:
        article_id: Article ID
        client_id: Optional client profile ID
        max_length: Maximum summary length in words
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Summary result
    """
    # Verify article exists
    article_repo = ArticleRepository(db)
    article = await article_repo.get(id=article_id)
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # If client_id provided, verify it belongs to user
    if client_id:
        client_repo = ClientProfileRepository(db)
        client_profile = await client_repo.get(id=client_id)
        
        if not client_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client profile not found"
            )
        
        if client_profile.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this client profile"
            )
    
    # Generate summary
    ai_service = AIService(db)
    result = await ai_service.generate_article_summary(
        article_id=article_id,
        client_id=client_id,
        max_length=max_length
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Failed to generate summary")
        )
    
    return result


@router.post("/executive-summary", status_code=status.HTTP_200_OK)
async def generate_executive_summary(
    client_id: uuid.UUID,
    article_ids: Optional[List[uuid.UUID]] = None,
    max_length: int = Query(400, ge=100, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate an executive summary of multiple articles for a client.
    
    Args:
        client_id: Client profile ID
        article_ids: Optional list of specific article IDs
        max_length: Maximum summary length in words
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Executive summary result
    """
    # Verify client profile exists and belongs to user
    client_repo = ClientProfileRepository(db)
    client_profile = await client_repo.get(id=client_id)
    
    if not client_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found"
        )
    
    if client_profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this client profile"
        )
    
    # Generate executive summary
    ai_service = AIService(db)
    result = await ai_service.generate_executive_summary(
        client_id=client_id,
        article_ids=article_ids,
        max_length=max_length
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Failed to generate executive summary")
        )
    
    return result