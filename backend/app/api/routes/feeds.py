"""
API routes for feed management.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.news_feed import NewsFeed, NewsFeedCreate, NewsFeedUpdate
from app.services.feed_service import FeedService

router = APIRouter(prefix="/feeds", tags=["Feeds"])


@router.get("", response_model=List[NewsFeed])
async def get_feeds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all feeds.
    
    Args:
        skip: Number of feeds to skip
        limit: Maximum number of feeds to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[NewsFeed]: List of feeds
    """
    feed_service = FeedService(db)
    feeds = await feed_service.get_all_feeds(skip=skip, limit=limit)
    return feeds


@router.post("", response_model=NewsFeed, status_code=status.HTTP_201_CREATED)
async def create_feed(
    feed_in: NewsFeedCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new feed.
    
    Args:
        feed_in: Feed creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        NewsFeed: Created feed
    """
    feed_service = FeedService(db)
    
    # Test connection before creating
    test_result = await feed_service.test_feed_connection(feed_in.url, feed_in.type)
    if not test_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect to feed: {test_result['message']}"
        )
    
    feed = await feed_service.create_feed(feed_in)
    return feed


@router.get("/{feed_id}", response_model=NewsFeed)
async def get_feed(
    feed_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a feed by ID.
    
    Args:
        feed_id: Feed ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        NewsFeed: Feed
    """
    feed_service = FeedService(db)
    feed = await feed_service.get_feed(feed_id)
    
    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed not found"
        )
    
    return feed


@router.put("/{feed_id}", response_model=NewsFeed)
async def update_feed(
    feed_id: uuid.UUID,
    feed_in: NewsFeedUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a feed.
    
    Args:
        feed_id: Feed ID
        feed_in: Feed update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        NewsFeed: Updated feed
    """
    feed_service = FeedService(db)
    feed = await feed_service.get_feed(feed_id)
    
    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed not found"
        )
    
    # If URL or type changed, test connection
    if (feed_in.url and feed_in.url != feed.url) or (feed_in.type and feed_in.type != feed.type):
        test_url = feed_in.url or feed.url
        test_type = feed_in.type or feed.type
        test_result = await feed_service.test_feed_connection(test_url, test_type)
        
        if not test_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to connect to feed: {test_result['message']}"
            )
    
    updated_feed = await feed_service.update_feed(feed_id, feed_in)
    return updated_feed


@router.delete("/{feed_id}", status_code=status.HTTP_200_OK)
async def delete_feed(
    feed_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a feed.
    
    Args:
        feed_id: Feed ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Success message
    """
    feed_service = FeedService(db)
    feed = await feed_service.get_feed(feed_id)
    
    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed not found"
        )
    
    success = await feed_service.delete_feed(feed_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete feed"
        )
    
    return {"success": True}


@router.post("/test-connection", status_code=status.HTTP_200_OK)
async def test_feed_connection(
    url: str,
    type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Test connection to a feed.
    
    Args:
        url: Feed URL
        type: Feed type (rss or web)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Test result
    """
    feed_service = FeedService(db)
    result = await feed_service.test_feed_connection(url, type)
    return result


@router.post("/{feed_id}/process", status_code=status.HTTP_200_OK)
async def process_feed(
    feed_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process a feed to fetch and store articles.
    
    Args:
        feed_id: Feed ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Processing result
    """
    feed_service = FeedService(db)
    feed = await feed_service.get_feed(feed_id)
    
    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed not found"
        )
    
    result = await feed_service.process_feed(feed_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    return {
        "success": True,
        "message": result["message"],
        "articles_count": len(result.get("articles", []))
    }