"""
Summarization service for generating article summaries.

This service handles the generation of article summaries and executive summaries
using LLM-based analysis, with optional tailoring to specific client profiles.
"""
import logging
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.client_profile import ClientProfile
from app.repositories.article import ArticleRepository, ArticleRelevanceRepository
from app.repositories.client_profile import ClientProfileRepository
from app.services.llm_service import LLMService
from app.prompts.summarization_prompt import (
    get_article_summary_prompt,
    get_executive_summary_prompt
)

logger = logging.getLogger(__name__)


class SummarizationService:
    """
    Service for generating article summaries.
    """

    def __init__(self, db: AsyncSession, llm_service: Optional[LLMService] = None):
        """
        Initialize summarization service.
        
        Args:
            db: Database session
            llm_service: Optional LLM service instance
        """
        self.db = db
        self.llm_service = llm_service or LLMService()
        self.article_repo = ArticleRepository(db)
        self.article_relevance_repo = ArticleRelevanceRepository(db)
        self.client_profile_repo = ClientProfileRepository(db)

    async def generate_article_summary(
        self, 
        article: Article, 
        client_profile: Optional[ClientProfile] = None,
        max_length: int = 200
    ) -> str:
        """
        Generate a summary for an article, optionally tailored to a client profile.
        
        Args:
            article: Article to summarize
            client_profile: Optional client profile to tailor summary for
            max_length: Maximum summary length in words
            
        Returns:
            str: Generated summary
        """
        # Prepare prompt with article and optional client context
        prompt = get_article_summary_prompt(article, client_profile, max_length)
        
        # Call LLM
        result = await self.llm_service.call_llm(prompt)
        
        if not result["success"]:
            logger.error(f"Error generating summary: {result.get('error', 'Unknown error')}")
            return "Error generating summary."
        
        return result["response"].strip()

    async def generate_executive_summary(
        self,
        articles: List[Article],
        client_profile: ClientProfile,
        max_length: int = 400
    ) -> str:
        """
        Generate an executive summary of multiple articles for a client.
        
        Args:
            articles: List of articles to summarize
            client_profile: Client profile to tailor summary for
            max_length: Maximum summary length in words
            
        Returns:
            str: Generated executive summary
        """
        # Prepare article summaries
        article_texts = []
        for article in articles:
            # Try to get existing relevance summary
            relevance = await self.article_relevance_repo.get_by_article_and_client(
                article_id=article.id,
                client_id=client_profile.id
            )
            
            summary = relevance.summary if relevance else "No summary available"
            article_texts.append(f"Title: {article.title}\nSummary: {summary}")
        
        # Prepare prompt
        prompt = get_executive_summary_prompt(
            article_texts=article_texts,
            client_profile=client_profile,
            max_length=max_length
        )
        
        # Call LLM
        result = await self.llm_service.call_llm(prompt)
        
        if not result["success"]:
            logger.error(f"Error generating executive summary: {result.get('error', 'Unknown error')}")
            return "Error generating executive summary."
        
        return result["response"].strip()