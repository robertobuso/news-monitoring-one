"""
Report service for generating and managing client reports.

This service handles the generation of daily reports for clients, including
fetching relevant articles, creating PDFs, and sending emails.
"""
import logging
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional, Any, Union
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.client_profile import ClientProfile
from app.models.report import Report
from app.repositories.article import ArticleRepository, ArticleRelevanceRepository
from app.repositories.client_profile import ClientProfileRepository
from app.repositories.report import ReportRepository, ReportArticleRepository
from app.repositories.user import UserRepository
from app.schemas.report import ReportArticleCreate, ReportCreate
from app.services.pdf_service import PDFService
from app.services.email_service import EmailService
from app.services.summarization_service import SummarizationService

logger = logging.getLogger(__name__)


class ReportService:
    """
    Service for generating and managing client reports.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize report service with database session.
        
        Args:
            db: Database session
        """
        self.db = db
        self.report_repo = ReportRepository(db)
        self.report_article_repo = ReportArticleRepository(db)
        self.article_repo = ArticleRepository(db)
        self.article_relevance_repo = ArticleRelevanceRepository(db)
        self.client_profile_repo = ClientProfileRepository(db)
        self.user_repo = UserRepository(db)
        self.pdf_service = PDFService()
        self.email_service = EmailService()
        self.summarization_service = SummarizationService(db)

    async def generate_daily_report(
        self, client_id: uuid.UUID, report_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Generate a daily report for a client profile.
        
        Args:
            client_id: Client profile ID
            report_date: Optional report date (defaults to today)
            
        Returns:
            Dict: Report generation result
        """
        # Use current date if not specified
        report_date = report_date or date.today()

        # Get client profile
        client_profile = await self.client_profile_repo.get(id=client_id)
        if not client_profile:
            return {"success": False, "message": "Client profile not found"}

        # Get user
        user = await self.user_repo.get(id=client_profile.user_id)
        if not user:
            return {"success": False, "message": "User not found"}

        # Check if report already exists
        existing_reports = await self.report_repo.get_by_client_id(client_id=client_id)
        for report in existing_reports:
            if report.report_date.date() == report_date:
                return {
                    "success": True, 
                    "report": report, 
                    "message": "Report already exists"
                }

        # Get relevant articles from the past day
        start_date = datetime.combine(report_date - timedelta(days=1), time.min)
        end_date = datetime.combine(report_date, time.min)

        # Get article relevances for this client with minimum score
        relevances = await self.article_relevance_repo.get_by_client_id_and_date_range(
            client_id=client_id,
            date_from=start_date,
            date_to=end_date,
            min_score=0.6  # Threshold for inclusion
        )

        # Get the actual articles
        relevant_articles = []
        for relevance in relevances:
            article = await self.article_repo.get(id=relevance.article_id)
            if article:
                relevant_articles.append({
                    "article": article,
                    "relevance": relevance
                })

        # If no relevant articles, create empty report
        if not relevant_articles:
            report_data = ReportCreate(
                client_id=client_id,
                report_date=report_date,
                recipient_email=user.email
            )
            report = await self.report_repo.create_for_user(user.id, report_data)
            await self.report_repo.update_status(report.id, "empty")
            
            return {
                "success": True, 
                "report": report, 
                "message": "No relevant articles found"
            }

        # Generate executive summary
        articles = [item["article"] for item in relevant_articles]
        executive_summary = await self.summarization_service.generate_executive_summary(
            articles=articles,
            client_profile=client_profile
        )

        # Create report record
        report_data = ReportCreate(
            client_id=client_id,
            report_date=report_date,
            recipient_email=user.email
        )
        report = await self.report_repo.create_for_user(user.id, report_data)
        
        # Update status to generating
        await self.report_repo.update_status(report.id, "generating")

        # Create PDF
        pdf_buffer = await self.pdf_service.create_pdf_report(
            client_profile=client_profile,
            articles=relevant_articles,
            executive_summary=executive_summary,
            report_date=report_date
        )

        # Save PDF
        pdf_path = self.pdf_service.save_pdf_report(pdf_buffer, report.id)
        await self.report_repo.update_status(report.id, "ready", pdf_path)

        # Save report articles
        for i, item in enumerate(relevant_articles):
            article = item["article"]
            relevance = item["relevance"]
            report_article_data = ReportArticleCreate(
                article_id=article.id,
                summary=relevance.summary or "",
                position=i + 1
            )
            await self.report_article_repo.create(report_article_data, report.id)

        # Send email
        email_result = await self.email_service.send_report_email(
            user_email=user.email,
            client_name=client_profile.name,
            report_date=report_date,
            pdf_path=pdf_path,
            report_id=report.id
        )

        if email_result["success"]:
            await self.report_repo.update_status(report.id, "sent")
            report = await self.report_repo.get(id=report.id)  # Refresh report data

        return {"success": True, "report": report}

    async def get_report_by_id(self, report_id: uuid.UUID, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get a report by ID, ensuring it belongs to the user.
        
        Args:
            report_id: Report ID
            user_id: User ID
            
        Returns:
            Dict: Report data
        """
        report = await self.report_repo.get(id=report_id)
        
        if not report:
            return {"success": False, "message": "Report not found"}
            
        if report.user_id != user_id:
            return {"success": False, "message": "Not authorized to access this report"}
            
        # Get report articles
        report_articles = await self.report_article_repo.get_by_report_id(report_id)
        
        # Get full article data
        articles = []
        for report_article in report_articles:
            article = await self.article_repo.get(id=report_article.article_id)
            if article:
                articles.append({
                    "article": article,
                    "report_article": report_article
                })
        
        # Get client profile
        client_profile = await self.client_profile_repo.get(id=report.client_id)
        
        return {
            "success": True,
            "report": report,
            "articles": articles,
            "client_profile": client_profile
        }

    async def get_reports_for_client(
        self, 
        client_id: uuid.UUID, 
        user_id: uuid.UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get reports for a client profile.
        
        Args:
            client_id: Client profile ID
            user_id: User ID
            date_from: Optional start date filter
            date_to: Optional end date filter
            skip: Number of reports to skip
            limit: Maximum number of reports to return
            
        Returns:
            Dict: Reports data
        """
        # Verify client profile belongs to user
        client_profile = await self.client_profile_repo.get(id=client_id)
        
        if not client_profile:
            return {"success": False, "message": "Client profile not found"}
            
        if client_profile.user_id != user_id:
            return {"success": False, "message": "Not authorized to access this client profile"}
        
        # Get reports
        reports = await self.report_repo.get_by_client_id_and_date_range(
            client_id=client_id,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit
        )
        
        # Get total count
        total_count = await self.report_repo.count_by_client_id_and_date_range(
            client_id=client_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return {
            "success": True,
            "reports": reports,
            "total": total_count,
            "client_profile": client_profile
        }

    async def get_reports_for_user(
            self,
            user_id: uuid.UUID,
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None,
            skip: int = 0,
            limit: int = 20  # Or match the default from your route
        ) -> Dict[str, Any]:
            """
            Get reports associated with a specific user, potentially across
            multiple client profiles, filtered by date range and paginated.

            Args:
                user_id: The ID of the user whose reports are to be fetched.
                date_from: Optional start date filter for report creation/publish date.
                date_to: Optional end date filter for report creation/publish date.
                skip: Number of reports to skip for pagination.
                limit: Maximum number of reports to return.

            Returns:
                Dict: A dictionary containing the success status, a list of reports,
                    and the total count of matching reports.
            """
            logger.info(f"Fetching reports for user {user_id} with filters: "
                        f"date_from={date_from}, date_to={date_to}, skip={skip}, limit={limit}")

            # --- Assumption: You need to implement this method in ReportRepository ---
            # This repository method should perform the actual database query
            # filtering the 'reports' table by 'user_id' and the date range.
            try:
                reports, total_count = await self.report_repo.get_by_user_id_and_date_range(
                    user_id=user_id,
                    date_from=date_from,
                    date_to=date_to,
                    skip=skip,
                    limit=limit
                )
            except Exception as e:
                # Catch potential exceptions during the database call
                logger.error(f"Error fetching reports for user {user_id} from repository: {e}", exc_info=True)
                # You might want to return a specific error structure or raise an exception
                # depending on your error handling strategy. For consistency with other
                # methods, returning a dict might be appropriate.
                return {
                    "success": False,
                    "message": f"An error occurred while fetching reports: {e}",
                    "reports": [],
                    "total": 0
                }
            # --- End of Assumption ---

            logger.info(f"Found {len(reports)} reports (total: {total_count}) for user {user_id}")

            return {
                "success": True,
                "reports": reports,
                "total": total_count
                # Note: Unlike get_reports_for_client, there's no single 'client_profile'
                # to return here as this fetches across potentially multiple clients.
            }

    async def generate_all_daily_reports(self) -> Dict[str, Any]:
        """
        Generate daily reports for all active client profiles.
        
        Returns:
            Dict: Generation results
        """
        # Get all active client profiles
        active_profiles = await self.client_profile_repo.get_all_active()
        
        report_count = 0
        results = []
        
        for profile in active_profiles:
            try:
                result = await self.generate_daily_report(profile.id)
                results.append({
                    "client_id": str(profile.id),
                    "client_name": profile.name,
                    "success": result["success"],
                    "message": result.get("message", "")
                })
                
                if result["success"]:
                    report_count += 1
            except Exception as e:
                logger.error(f"Error generating report for client {profile.id}: {e}")
                results.append({
                    "client_id": str(profile.id),
                    "client_name": profile.name,
                    "success": False,
                    "message": str(e)
                })
        
        return {
            "success": True,
            "queued_reports": report_count,
            "total_profiles": len(active_profiles),
            "results": results
        }