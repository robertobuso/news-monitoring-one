"""
Relevance service for evaluating article relevance to client profiles.

This service handles the evaluation of how relevant articles are to specific client
profiles using LLM-based analysis, and manages the storage of relevance data.
"""
import json
import logging
import re
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.client_profile import ClientProfile
from app.repositories.article import ArticleRepository, ArticleRelevanceRepository
from app.repositories.client_profile import ClientProfileRepository
from app.schemas.article import ArticleRelevanceCreate
from app.services.llm_service import LLMService
from app.prompts.relevance_prompt import get_relevance_evaluation_prompt

logger = logging.getLogger(__name__)


class RelevanceService:
    """
    Service for evaluating article relevance to client profiles.
    """

    def __init__(self, db: AsyncSession, llm_service: Optional[LLMService] = None):
        """
        Initialize relevance service.
        
        Args:
            db: Database session
            llm_service: Optional LLM service instance
        """
        self.db = db
        self.llm_service = llm_service or LLMService()
        self.article_repo = ArticleRepository(db)
        self.article_relevance_repo = ArticleRelevanceRepository(db)
        self.client_profile_repo = ClientProfileRepository(db)

    async def evaluate_relevance(
        self, article: Article, client_profile: ClientProfile
    ) -> Dict[str, Any]:
        """
        Evaluate the relevance of an article to a client profile.
        
        Args:
            article: Article to evaluate
            client_profile: Client profile to evaluate against
            
        Returns:
            Dict: Relevance evaluation result
        """
        # Prepare prompt with article and client profile information
        prompt = get_relevance_evaluation_prompt(article, client_profile)
        
        # Define expected JSON schema
        json_schema = {
            "type": "object",
            "properties": {
                "score": {"type": "number", "minimum": 0, "maximum": 1},
                "explanation": {"type": "string"}
            },
            "required": ["score", "explanation"]
        }
        
        # Call LLM with JSON response parsing
        result = await self.llm_service.call_llm_with_json_response(prompt, json_schema)
        
        if not result["success"]:
            logger.error(f"Error in relevance evaluation: {result.get('error', 'Unknown error')}")
            return {"score": 0.0, "explanation": "Error in relevance evaluation"}
        
        # Extract response
        response = result["response"]
        
        # Validate score is within bounds
        score = response.get("score", 0.0)
        if not isinstance(score, (int, float)) or score < 0 or score > 1:
            score = 0.0
        
        explanation = response.get("explanation", "No explanation provided")
        
        return {"score": score, "explanation": explanation}

    async def process_article_relevance(self, article_id: uuid.UUID) -> List[Dict[str, Any]]:
        """
        Process article relevance for all active client profiles.
        
        Args:
            article_id: Article ID
            
        Returns:
            List[Dict]: List of relevance results
        """
        article = await self.article_repo.get(id=article_id)
        if not article:
            logger.error(f"Article not found: {article_id}")
            return []
        
        # Get all active client profiles
        client_profiles = await self.client_profile_repo.get_all_active()
        
        results = []
        for profile in client_profiles:
            # Check if already evaluated
            existing = await self.article_relevance_repo.get_by_article_and_client(
                article_id=article_id, 
                client_id=profile.id
            )
            
            if existing:
                results.append({
                    "client_id": str(profile.id),
                    "client_name": profile.name,
                    "relevance_id": str(existing.id),
                    "relevance_score": existing.relevance_score,
                    "summary": existing.summary,
                    "is_included": existing.is_included,
                    "status": "existing"
                })
                continue
            
            # Evaluate relevance
            try:
                relevance_result = await self.evaluate_relevance(article, profile)
                
                # Determine if article should be included based on score
                is_included = relevance_result["score"] >= 0.6  # Threshold for inclusion
                
                # Save result
                relevance_data = ArticleRelevanceCreate(
                    article_id=article_id,
                    client_id=profile.id,
                    relevance_score=relevance_result["score"],
                    summary=relevance_result["explanation"],
                    is_included=is_included
                )
                
                relevance = await self.article_relevance_repo.create(relevance_data)
                
                results.append({
                    "client_id": str(profile.id),
                    "client_name": profile.name,
                    "relevance_id": str(relevance.id),
                    "relevance_score": relevance.relevance_score,
                    "summary": relevance.summary,
                    "is_included": relevance.is_included,
                    "status": "new"
                })
                
            except Exception as e:
                logger.error(f"Error evaluating relevance for article {article_id} and client {profile.id}: {e}")
                results.append({
                    "client_id": str(profile.id),
                    "client_name": profile.name,
                    "error": str(e),
                    "status": "error"
                })
        
        return results

    async def get_relevant_articles_for_client(
        self, 
        client_id: uuid.UUID, 
        min_score: float = 0.6,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get articles relevant to a specific client.
        
        Args:
            client_id: Client profile ID
            min_score: Minimum relevance score
            limit: Maximum number of articles to return
            
        Returns:
            List[Dict]: List of relevant articles with their relevance data
        """
        relevances = await self.article_relevance_repo.get_by_client_id(
            client_id=client_id, 
            min_score=min_score,
            limit=limit
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