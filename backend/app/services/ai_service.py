"""
AI service for managing LLM-based operations.

This service coordinates the AI analysis of articles, including relevance evaluation,
summarization, and entity extraction. It serves as a high-level interface for the
AI capabilities of the application.
"""
import logging
from typing import Dict, List, Optional, Any, Union
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.client_profile import ClientProfile
from app.repositories.article import ArticleRepository, ArticleRelevanceRepository
from app.repositories.client_profile import ClientProfileRepository
from app.services.llm_service import LLMService
from app.services.relevance_service import RelevanceService
from app.services.summarization_service import SummarizationService
from app.utils.text_processing import extract_entities_from_text

logger = logging.getLogger(__name__)


class AIService:
    """
    Service for coordinating AI operations on articles.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize AI service with database session.
        
        Args:
            db: Database session
        """
        self.db = db
        self.llm_service = LLMService()
        self.relevance_service = RelevanceService(db, self.llm_service)
        self.summarization_service = SummarizationService(db, self.llm_service)
        self.article_repo = ArticleRepository(db)
        self.article_relevance_repo = ArticleRelevanceRepository(db)
        self.client_profile_repo = ClientProfileRepository(db)

    async def process_article(self, article_id: uuid.UUID) -> Dict[str, Any]:
        """
        Process an article with AI analysis.
        
        Args:
            article_id: Article ID
            
        Returns:
            Dict: Processing results
        """
        article = await self.article_repo.get(id=article_id)
        if not article:
            return {"success": False, "message": "Article not found"}
        
        # Extract entities from article content
        entities = extract_entities_from_text(article.content)
        
        # Update article metadata with entities
        metadata = article.metadata or {}
        metadata["entities"] = entities
        await self.article_repo.update(db_obj=article, obj_in={"metadata": metadata})
        
        # Process article relevance for all active client profiles
        relevance_results = await self.relevance_service.process_article_relevance(article_id)
        
        return {
            "success": True,
            "article_id": str(article_id),
            "entities": entities,
            "relevance_results": relevance_results
        }

    async def get_relevant_articles_for_client(
        self, 
        client_id: uuid.UUID, 
        min_score: float = 0.6,
        limit: int = 20,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get articles relevant to a specific client.
        
        Args:
            client_id: Client profile ID
            min_score: Minimum relevance score
            limit: Maximum number of articles to return
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            List[Dict]: List of relevant articles with their relevance data
        """
        # Get relevance data for client
        relevances = await self.article_relevance_repo.get_by_client_id(
            client_id=client_id, 
            min_score=min_score,
            limit=limit,
            date_from=date_from,
            date_to=date_to
        )
        
        results = []
        for relevance in relevances:
            article = await self.article_repo.get(id=relevance.article_id)
            if article:
                results.append({
                    "article": article,
                    "relevance": relevance
                })
        
        return results

    async def generate_article_summary(
        self, 
        article_id: uuid.UUID, 
        client_id: Optional[uuid.UUID] = None,
        max_length: int = 200
    ) -> Dict[str, Any]:
        """
        Generate a summary for an article, optionally tailored to a client.
        
        Args:
            article_id: Article ID
            client_id: Optional client profile ID
            max_length: Maximum summary length in words
            
        Returns:
            Dict: Summary result
        """
        article = await self.article_repo.get(id=article_id)
        if not article:
            return {"success": False, "message": "Article not found"}
        
        client_profile = None
        if client_id:
            client_profile = await self.client_profile_repo.get(id=client_id)
            if not client_profile:
                return {"success": False, "message": "Client profile not found"}
        
        summary = await self.summarization_service.generate_article_summary(
            article=article,
            client_profile=client_profile,
            max_length=max_length
        )
        
        return {
            "success": True,
            "article_id": str(article_id),
            "client_id": str(client_id) if client_id else None,
            "summary": summary
        }

    async def generate_executive_summary(
        self,
        client_id: uuid.UUID,
        article_ids: Optional[List[uuid.UUID]] = None,
        max_length: int = 400
    ) -> Dict[str, Any]:
        """
        Generate an executive summary of multiple articles for a client.
        
        Args:
            client_id: Client profile ID
            article_ids: Optional list of specific article IDs
            max_length: Maximum summary length in words
            
        Returns:
            Dict: Executive summary result
        """
        client_profile = await self.client_profile_repo.get(id=client_id)
        if not client_profile:
            return {"success": False, "message": "Client profile not found"}
        
        # If no article IDs provided, get relevant articles
        if not article_ids:
            relevant_articles = await self.get_relevant_articles_for_client(
                client_id=client_id,
                min_score=0.7,  # Higher threshold for executive summary
                limit=10
            )
            articles = [item["article"] for item in relevant_articles]
        else:
            articles = []
            for article_id in article_ids:
                article = await self.article_repo.get(id=article_id)
                if article:
                    articles.append(article)
        
        if not articles:
            return {"success": False, "message": "No articles found for summary"}
        
        executive_summary = await self.summarization_service.generate_executive_summary(
            articles=articles,
            client_profile=client_profile,
            max_length=max_length
        )
        
        return {
            "success": True,
            "client_id": str(client_id),
            "article_count": len(articles),
            "executive_summary": executive_summary
        }