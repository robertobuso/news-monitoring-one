"""
Celery tasks for report generation and delivery.
"""
import asyncio
import logging
from datetime import date, datetime
import uuid

from celery import shared_task

from app.db.session import AsyncSessionLocal
from app.services.report_service import ReportService

logger = logging.getLogger(__name__)


@shared_task(name="generate_report")
def generate_report_task(client_id: str, report_date: str = None):
    """
    Generate a report for a client.
    
    Args:
        client_id: Client profile ID
        report_date: Optional report date (ISO format)
    """
    logger.info(f"Generating report for client {client_id}")
    
    async def _generate_report():
        async with AsyncSessionLocal() as db:
            report_service = ReportService(db)
            
            # Parse date if provided
            parsed_date = None
            if report_date:
                try:
                    parsed_date = date.fromisoformat(report_date)
                except ValueError:
                    logger.error(f"Invalid date format: {report_date}")
            
            # Generate report
            result = await report_service.generate_daily_report(
                client_id=uuid.UUID(client_id),
                report_date=parsed_date
            )
            
            if result["success"]:
                report = result["report"]
                logger.info(f"Successfully generated report {report.id} for client {client_id}")
                return {"report_id": str(report.id), "status": report.status}
            else:
                logger.error(f"Failed to generate report for client {client_id}: {result.get('message', 'Unknown error')}")
                return {"error": result.get("message", "Unknown error")}
    
    # Run the async function
    return asyncio.run(_generate_report())


@shared_task(name="generate_all_daily_reports")
def generate_all_daily_reports_task():
    """
    Generate daily reports for all active client profiles.
    """
    logger.info("Starting generation of all daily reports")
    
    async def _generate_all_reports():
        async with AsyncSessionLocal() as db:
            report_service = ReportService(db)
            result = await report_service.generate_all_daily_reports()
            
            logger.info(f"Generated {result['queued_reports']} reports out of {result['total_profiles']} active profiles")
            return {
                "generated_count": result["queued_reports"],
                "total_profiles": result["total_profiles"]
            }
    
    # Run the async function
    return asyncio.run(_generate_all_reports())


@shared_task(name="send_pending_reports")
def send_pending_reports_task():
    """
    Send all pending reports.
    """
    logger.info("Starting sending of pending reports")
    
    async def _send_pending_reports():
        async with AsyncSessionLocal() as db:
            report_service = ReportService(db)
            result = await report_service.send_pending_reports()
            
            logger.info(f"Sent {result['sent_count']} pending reports")
            return {
                "sent_count": result["sent_count"],
                "total_pending": result["total_pending"]
            }
    
    # Run the async function
    return asyncio.run(_send_pending_reports())


@shared_task(name="cleanup_old_reports")
def cleanup_old_reports_task(days_to_keep: int = 30):
    """
    Clean up old report files.
    
    Args:
        days_to_keep: Number of days to keep reports
    """
    logger.info(f"Cleaning up reports older than {days_to_keep} days")
    
    async def _cleanup_reports():
        async with AsyncSessionLocal() as db:
            report_service = ReportService(db)
            result = await report_service.cleanup_old_reports(days_to_keep)
            
            logger.info(f"Cleaned up {result['deleted_count']} old reports")
            return {
                "deleted_count": result["deleted_count"]
            }
    
    # Run the async function
    return asyncio.run(_cleanup_reports())