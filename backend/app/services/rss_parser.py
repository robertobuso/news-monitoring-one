"""
RSS feed parser service for fetching and parsing RSS feeds.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

import feedparser
from feedparser import FeedParserDict

logger = logging.getLogger(__name__)


def parse_date(date_str: str) -> datetime:
    """
    Parse date string from RSS feed into datetime object.
    
    Args:
        date_str: Date string from RSS feed
        
    Returns:
        datetime: Parsed datetime object
    """
    try:
        # Try to parse using feedparser's internal date parser
        parsed_time = feedparser.datetimes.parse_datetime(date_str)
        if parsed_time:
            return parsed_time
    except Exception as e:
        logger.warning(f"Error parsing date {date_str}: {e}")
    
    # Default to current time if parsing fails
    return datetime.utcnow()


def extract_content(entry: FeedParserDict) -> str:
    """
    Extract content from a feed entry.
    
    Args:
        entry: Feed entry from feedparser
        
    Returns:
        str: Extracted content
    """
    if hasattr(entry, "content") and entry.content:
        return entry.content[0].value
    elif hasattr(entry, "summary"):
        return entry.summary
    elif hasattr(entry, "description"):
        return entry.description
    else:
        return ""


def parse_rss_feed(feed_url: str) -> Dict[str, Union[bool, str, List[Dict]]]:
    """
    Parse an RSS feed and extract articles.
    
    Args:
        feed_url: URL of the RSS feed
        
    Returns:
        Dict: Result with success status and articles or error message
    """
    try:
        logger.info(f"Parsing RSS feed: {feed_url}")
        feed_data = feedparser.parse(feed_url)
        
        if feed_data.bozo and feed_data.bozo_exception:
            logger.error(f"Error parsing feed {feed_url}: {feed_data.bozo_exception}")
            return {"success": False, "message": str(feed_data.bozo_exception)}

        articles = []
        for entry in feed_data.entries:
            # Extract published date
            published_at = datetime.utcnow()
            if hasattr(entry, "published"):
                published_at = parse_date(entry.published)
            elif hasattr(entry, "updated"):
                published_at = parse_date(entry.updated)
            
            # Extract author
            author = None
            if hasattr(entry, "author"):
                author = entry.author
            elif hasattr(entry, "creator"):
                author = entry.creator
            
            # Create article dict
            article = {
                "title": entry.title,
                "url": entry.link,
                "published_at": published_at,
                "author": author,
                "content": extract_content(entry),
                "source": feed_data.feed.title if hasattr(feed_data.feed, "title") else feed_url
            }
            articles.append(article)

        logger.info(f"Successfully parsed {len(articles)} articles from {feed_url}")
        return {"success": True, "articles": articles}
    except Exception as e:
        logger.error(f"Error parsing feed {feed_url}: {e}")
        return {"success": False, "message": str(e)}