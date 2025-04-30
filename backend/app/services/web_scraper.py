"""
Web scraper service for scraping websites without RSS feeds.
"""
import logging
from datetime import datetime
from typing import Dict, Optional, Union

from playwright.async_api import async_playwright
from pydantic import BaseModel

from app.utils.url_helpers import extract_source_from_url
from app.utils.html_cleaner import clean_html
from app.services.rss_parser import parse_date

logger = logging.getLogger(__name__)


class SelectorConfig(BaseModel):
    """Configuration for CSS selectors to extract content from websites."""
    title: str = "h1"
    content: str = "article, .article, .post, .content, main"
    author: Optional[str] = ".author, .byline"
    date: Optional[str] = ".date, .published, time"


DEFAULT_SELECTORS = SelectorConfig()


async def scrape_website(url: str, selector_config: Optional[Dict] = None) -> Dict[str, Union[bool, str, Dict]]:
    """
    Scrape a website to extract article content.
    
    Args:
        url: URL of the website to scrape
        selector_config: Optional custom CSS selectors
        
    Returns:
        Dict: Result with success status and article data or error message
    """
    browser = None
    try:
        logger.info(f"Scraping website: {url}")
        
        # Use default or custom selectors
        selectors = DEFAULT_SELECTORS
        if selector_config:
            selectors = SelectorConfig(**selector_config)
        
        # Launch browser
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set timeout and navigate to URL
            page.set_default_timeout(30000)  # 30 seconds
            await page.goto(url, wait_until="networkidle")
            
            # Extract title
            title_element = await page.query_selector(selectors.title)
            title = await title_element.inner_text() if title_element else "Unknown Title"
            
            # Extract content
            content_element = await page.query_selector(selectors.content)
            content = await content_element.inner_html() if content_element else ""
            
            # Extract author if available
            author = None
            if selectors.author:
                author_element = await page.query_selector(selectors.author)
                if author_element:
                    author = await author_element.inner_text()
            
            # Extract date if available
            date_str = None
            date = datetime.utcnow()
            if selectors.date:
                date_element = await page.query_selector(selectors.date)
                if date_element:
                    date_str = await date_element.inner_text()
                    date = parse_date(date_str) if date_str else datetime.utcnow()
            
            # Clean content
            cleaned_content = clean_html(content)
            
            # Create article dict
            article = {
                "title": title,
                "url": url,
                "published_at": date,
                "author": author,
                "content": cleaned_content,
                "source": extract_source_from_url(url)
            }
            
            await browser.close()
            browser = None
            
            logger.info(f"Successfully scraped article from {url}")
            return {"success": True, "article": article}
    
    except Exception as e:
        logger.error(f"Error scraping website {url}: {e}")
        if browser:
            await browser.close()
        return {"success": False, "message": str(e)}