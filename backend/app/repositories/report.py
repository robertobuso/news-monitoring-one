"""
Report repository for report-related database operations.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report
from app.models.report_article import ReportArticle
from app.repositories.base import BaseRepository
from app.schemas.report import ReportArticleCreate, ReportArticleUpdate, ReportCreate, ReportUpdate


class ReportRepository(BaseRepository[Report, ReportCreate, ReportUpdate]):
    """
    Repository for Report model operations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize report repository.
        
        Args:
            db: SQLAlchemy async session
        """
        super().__init__(Report, db)

    async def get_by_user_id(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """
        Get reports by user ID.
        
        Args:
            user_id: User ID
            skip: Number of reports to skip
            limit: Maximum number of reports to return
            
        Returns:
            List[Report]: List of reports
        """
        query = select(Report).where(
            Report.user_id == user_id
        ).order_by(
            Report.created_at.desc()
        ).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_client_id(
        self, client_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """
        Get reports by client ID.
        
        Args:
            client_id: Client ID
            skip: Number of reports to skip
            limit: Maximum number of reports to return
            
        Returns:
            List[Report]: List of reports
        """
        query = select(Report).where(
            Report.client_id == client_id
        ).order_by(
            Report.created_at.desc()
        ).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_pending_reports(self) -> List[Report]:
        """
        Get pending reports.
        
        Returns:
            List[Report]: List of pending reports
        """
        query = select(Report).where(Report.status == "pending")
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_user_id_and_date_range(
            self,
            user_id: uuid.UUID,
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None,
            skip: int = 0,
            limit: int = 100
        ) -> Tuple[List[Report], int]:
            """
            Get reports by user ID, filtered by date range and paginated.
            Also returns the total count of matching reports before pagination.

            Args:
                user_id: The ID of the user whose reports are to be fetched.
                date_from: Optional start date filter (inclusive).
                date_to: Optional end date filter (inclusive).
                skip: Number of reports to skip for pagination.
                limit: Maximum number of reports to return.

            Returns:
                Tuple[List[Report], int]: A tuple containing the list of reports
                                        and the total count of matching reports.
            """
            # --- Query for the paginated list of reports ---
            select_stmt = select(Report).where(
                Report.user_id == user_id
            )

            # Apply date filters if provided
            if date_from:
                # Assuming report_date is a Date column, compare appropriately
                # If it's DateTime, the comparison is fine. If Date, ensure comparison logic matches.
                # For simplicity, assuming comparison works directly or adjust as needed (e.g., cast)
                select_stmt = select_stmt.where(Report.report_date >= date_from)
            if date_to:
                select_stmt = select_stmt.where(Report.report_date <= date_to)

            # Apply ordering and pagination
            select_stmt = select_stmt.order_by(
                Report.created_at.desc()  # Or Report.report_date.desc() if preferred
            ).offset(skip).limit(limit)

            result = await self.db.execute(select_stmt)
            reports_list = result.scalars().all()

            # --- Query for the total count (without pagination) ---
            from sqlalchemy import func # Ensure func is imported

            count_stmt = select(func.count()).select_from(Report).where(
                Report.user_id == user_id
            )

            # Apply the same date filters as the main query
            if date_from:
                count_stmt = count_stmt.where(Report.report_date >= date_from)
            if date_to:
                count_stmt = count_stmt.where(Report.report_date <= date_to)

            count_result = await self.db.execute(count_stmt)
            total_count = count_result.scalar_one_or_none() or 0 # Get count, default to 0 if None

            return reports_list, total_count

    async def create_for_user(
        self, user_id: uuid.UUID, obj_in: ReportCreate
    ) -> Report:
        """
        Create a report for a user.
        
        Args:
            user_id: User ID
            obj_in: Report creation data
            
        Returns:
            Report: Created report
        """
        db_obj = Report(
            user_id=user_id,
            client_id=obj_in.client_id,
            report_date=obj_in.report_date,
            recipient_email=obj_in.recipient_email,
            status="pending",
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update_status(
        self, report_id: uuid.UUID, status: str, pdf_path: Optional[str] = None
    ) -> Optional[Report]:
        """
        Update report status.
        
        Args:
            report_id: Report ID
            status: New status
            pdf_path: Optional PDF path
            
        Returns:
            Optional[Report]: Updated report if found, None otherwise
        """
        report = await self.get(id=report_id)
        if not report:
            return None
            
        report.status = status
        if pdf_path:
            report.pdf_path = pdf_path
            
        if status == "sent":
            report.sent_at = datetime.utcnow()
            
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report


class ReportArticleRepository:
    """
    Repository for ReportArticle model operations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize report article repository.
        
        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def get(self, id: uuid.UUID) -> Optional[ReportArticle]:
        """
        Get a report article by ID.
        
        Args:
            id: Report article ID
            
        Returns:
            Optional[ReportArticle]: Report article if found, None otherwise
        """
        query = select(ReportArticle).where(ReportArticle.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_report_id(self, report_id: uuid.UUID) -> List[ReportArticle]:
        """
        Get report articles by report ID.
        
        Args:
            report_id: Report ID
            
        Returns:
            List[ReportArticle]: List of report articles
        """
        query = select(ReportArticle).where(
            ReportArticle.report_id == report_id
        ).order_by(
            ReportArticle.position
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: ReportArticleCreate, report_id: uuid.UUID) -> ReportArticle:
        """
        Create a new report article.
        
        Args:
            obj_in: Report article creation data
            report_id: Report ID
            
        Returns:
            ReportArticle: Created report article
        """
        db_obj = ReportArticle(
            report_id=report_id,
            article_id=obj_in.article_id,
            summary=obj_in.summary,
            position=obj_in.position,
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, db_obj: ReportArticle, obj_in: ReportArticleUpdate
    ) -> ReportArticle:
        """
        Update a report article.
        
        Args:
            db_obj: Report article to update
            obj_in: Report article update data
            
        Returns:
            ReportArticle: Updated report article
        """
        update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
            
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def remove(self, id: uuid.UUID) -> Optional[ReportArticle]:
        """
        Remove a report article.
        
        Args:
            id: Report article ID
            
        Returns:
            Optional[ReportArticle]: Removed report article if found, None otherwise
        """
        obj = await self.get(id=id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
        return obj

    async def reorder_articles(
        self, report_id: uuid.UUID, article_ids: List[uuid.UUID]
    ) -> List[ReportArticle]:
        """
        Reorder report articles.
        
        Args:
            report_id: Report ID
            article_ids: Ordered list of article IDs
            
        Returns:
            List[ReportArticle]: List of updated report articles
        """
        report_articles = await self.get_by_report_id(report_id)
        article_map = {str(ra.article_id): ra for ra in report_articles}
        
        updated_articles = []
        for position, article_id in enumerate(article_ids):
            article_id_str = str(article_id)
            if article_id_str in article_map:
                report_article = article_map[article_id_str]
                report_article.position = position
                self.db.add(report_article)
                updated_articles.append(report_article)
                
        await self.db.commit()
        for article in updated_articles:
            await self.db.refresh(article)
            
        return updated_articles
    
    async def get_by_client_id_and_date_range(
        self, 
        client_id: uuid.UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Report]:
        """
        Get reports by client ID and date range.
        
        Args:
            client_id: Client ID
            date_from: Optional start date filter
            date_to: Optional end date filter
            skip: Number of reports to skip
            limit: Maximum number of reports to return
            
        Returns:
            List[Report]: List of reports
        """
        query = select(Report).where(
            Report.client_id == client_id
        )
        
        if date_from:
            query = query.where(Report.report_date >= date_from)
        if date_to:
            query = query.where(Report.report_date <= date_to)
        
        query = query.order_by(
            Report.created_at.desc()
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count_by_client_id_and_date_range(
        self, 
        client_id: uuid.UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> int:
        """
        Count reports by client ID and date range.
        
        Args:
            client_id: Client ID
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            int: Count of reports
        """
        from sqlalchemy import func
        
        query = select(func.count()).select_from(Report).where(
            Report.client_id == client_id
        )
        
        if date_from:
            query = query.where(Report.report_date >= date_from)
        if date_to:
            query = query.where(Report.report_date <= date_to)
        
        result = await self.db.execute(query)
        return result.scalar()