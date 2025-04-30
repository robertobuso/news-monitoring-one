"""
Celery tasks for AI processing of articles.
"""
import logging
import uuid

from celery import shared_task

from app.db.session import AsyncSessionLocal
from app.repositories.article import ArticleRepository
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


@shared_task(name="process_article_relevance")
def process_article_relevance_task(article_id: str):
    """
    Process article relevance for all client profiles.
    
    Args:
        article_id: Article ID
    """
    logger.info(f"Processing relevance for article {article_id}")
    
    async def _process_article():
        async with AsyncSessionLocal() as db:
            ai_service = AIService(db)
            result = await ai_service.process_article(uuid.UUID(article_id))
            
            if result["success"]:
                logger.info(f"Successfully processed article {article_id}")
                logger.info(f"Relevance results: {len(result.get('relevance_results', []))} client profiles processed")
            else:
                logger.error(f"Failed to process article {article_id}: {result.get('message', 'Unknown error')}")
    
    # Run the async function
    import asyncio
    asyncio.run(_process_article())


@shared_task(name="process_new_articles")
def process_new_articles():
    """
    Process all unprocessed articles for relevance.
    """
    logger.info("Starting processing of new articles")
    
    async def _process_articles():
        async with AsyncSessionLocal() as db:
            article_repo = ArticleRepository(db)
            
            # Get unprocessed articles
            unprocessed_articles = await article_repo.get_unprocessed_articles(limit=50)
            
            logger.info(f"Found {len(unprocessed_articles)} unprocessed articles")
            
            # Queue individual article processing
            for article in unprocessed_articles:
                process_article_relevance_task.delay(str(article.id))
                logger.info(f"Queued article {article.id} for processing")
    
    # Run the async function
    import asyncio
    asyncio.run(_process_articles())
    
    logger.info("Completed queueing of new articles for processing")


@shared_task(name="generate_article_summaries")
def generate_article_summaries(article_ids: list):
    """
    Generate summaries for multiple articles.
    
    Args:
        article_ids: List of article IDs
    """
    logger.info(f"Generating summaries for {len(article_ids)} articles")
    
    async def _generate_summaries():
        async with AsyncSessionLocal() as db:
            ai_service = AIService(db)
            
            for article_id_str in article_ids:
                try:
                    article_id = uuid.UUID(article_id_str)
                    result = await ai_service.generate_article_summary(article_id)
                    
                    if result["success"]:
                        logger.info(f"Generated summary for article {article_id}")
                    else:
                        logger.error(f"Failed to generate summary for article {article_id}: {result.get('message', 'Unknown error')}")
                
                except Exception as e:
                    logger.error(f"Error generating summary for article {article_id_str}: {e}")
    
    # Run the async function
    import asyncio
    asyncio.run(_generate_summaries())
    
    logger.info("Completed generating article summaries")