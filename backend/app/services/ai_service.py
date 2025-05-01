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

    def __init__(self, db: AsyncSession, llm_service: Optional[LLMService] = None):
        """
        Initialize AI service with database session.
        
        Args:
            db: Database session
            llm_service: Optional LLM service to use (creates a new one if not provided)
        """
        self.db = db
        self.llm_service = llm_service or LLMService()
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

        # Update article meta_data with entities (changed from metadata to meta_data)
        meta_data = article.meta_data or {}
        meta_data["entities"] = entities
        await self.article_repo.update(db_obj=article, obj_in={"meta_data": meta_data})
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
        # Get relevance data for client with the minimum score filter
        relevances = await self.article_relevance_repo.get_by_client_id_and_date_range(
            client_id=client_id, 
            date_from=date_from,
            date_to=date_to,
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
        
        # Generate the summary using the LLM service
        context = None
        if client_profile:
            context = (f"This summary is for a client in the {client_profile.industry} industry. "
                      f"The client is interested in: {', '.join(client_profile.keywords)}.")
        
        try:
            summary = await self.llm_service.generate_summary(
                text=article.content,
                max_length=max_length,
                context=context
            )
            
            # If we have a client, store this summary in article relevance
            if client_profile:
                relevance = await self.article_relevance_repo.get_by_article_and_client(
                    article_id=article_id,
                    client_id=client_id
                )
                
                if relevance:
                    await self.article_relevance_repo.update(
                        db_obj=relevance,
                        obj_in={"summary": summary}
                    )
            
            return {
                "success": True,
                "article_id": str(article_id),
                "client_id": str(client_id) if client_id else None,
                "summary": summary
            }
        except Exception as e:
            logger.error(f"Error generating article summary: {e}")
            return {"success": False, "message": f"Error generating summary: {str(e)}"}

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
        
        # Generate individual summaries for all articles first
        article_texts = []
        for article in articles:
            # Try to get existing relevance summary
            relevance = await self.article_relevance_repo.get_by_article_and_client(
                article_id=article.id,
                client_id=client_id
            )
            
            if relevance and relevance.summary:
                summary = relevance.summary
            else:
                # Generate a new summary
                summary_result = await self.generate_article_summary(
                    article_id=article.id,
                    client_id=client_id,
                    max_length=100  # Shorter summaries for executive summary input
                )
                summary = summary_result.get("summary", "No summary available")
            
            article_texts.append(f"Title: {article.title}\nDate: {article.published_at.isoformat()}\nSummary: {summary}")
        
        # Generate the executive summary
        # Combine all article texts with client profile information
        context = (f"Client: {client_profile.name}\n"
                   f"Industry: {client_profile.industry}\n"
                   f"Keywords: {', '.join(client_profile.keywords)}")
        
        full_text = f"{context}\n\n" + "\n\n".join(article_texts)
        
        try:
            prompt = f"""
            Based on the following collection of article summaries, create an executive summary 
            specifically tailored for this client. Focus on insights relevant to their industry 
            and interests. The summary should highlight key developments, trends, and potential 
            business implications.
            
            {full_text}
            
            Create a cohesive, well-structured executive summary of approximately {max_length} words 
            that synthesizes the most important information for this client. Focus on actionable 
            insights and strategic implications.
            """
            
            exec_summary_result = await self.llm_service.call_llm(prompt)
            
            if not exec_summary_result["success"]:
                raise Exception(exec_summary_result.get("error", "Unknown error"))
                
            executive_summary = exec_summary_result["response"].strip()
            
            return {
                "success": True,
                "client_id": str(client_id),
                "article_count": len(articles),
                "executive_summary": executive_summary
            }
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return {"success": False, "message": f"Error generating executive summary: {str(e)}"}
        
    async def process_daily_articles(self) -> Dict[str, Any]:
        """
        Process all unprocessed articles to evaluate relevance for all client profiles.
        
        Returns:
            Dict: Processing results
        """
        # Get unprocessed articles (those without relevance evaluations)
        article_repo = ArticleRepository(self.db)
        unprocessed_articles = await article_repo.get_unprocessed_articles(limit=50)
        
        results = {
            "success": True,
            "processed_count": 0,
            "error_count": 0,
            "article_ids": []
        }
        
        for article in unprocessed_articles:
            try:
                result = await self.process_article(article.id)
                if result["success"]:
                    results["processed_count"] += 1
                    results["article_ids"].append(str(article.id))
                else:
                    results["error_count"] += 1
                    logger.error(f"Error processing article {article.id}: {result.get('message')}")
            except Exception as e:
                results["error_count"] += 1
                logger.error(f"Exception processing article {article.id}: {e}")
        
        return results