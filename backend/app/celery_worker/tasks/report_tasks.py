import logging
import uuid
from datetime import date, datetime
import asyncio # Added import

from celery import shared_task

from app.celery_worker.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.services.report_service import ReportService
from app.repositories.report import ReportRepository # Import repository

logger = logging.getLogger(__name__)

@shared_task(name="generate_report", bind=True, max_retries=3, default_retry_delay=60)
def generate_report_task(self, client_id_str: str, report_date_iso: str | None = None):
    """
    Generate a report for a client.

    Args:
        client_id_str: Client profile ID as a string.
        report_date_iso: Optional report date in ISO format string (YYYY-MM-DD).
    """
    client_id = uuid.UUID(client_id_str)
    report_date = date.fromisoformat(report_date_iso) if report_date_iso else None
    # Variable to hold report ID in case of mid-process failure
    report_id_for_error_update: uuid.UUID | None = None

    logger.info(f"Starting report generation task for client: {client_id}, date: {report_date}")

    async def _generate_report_async():
        nonlocal report_id_for_error_update # Allow modification
        async with AsyncSessionLocal() as db:
            report_service = ReportService(db)
            report_repo = ReportRepository(db)
            client_repo = ClientProfileRepository(db)

            try:
                # First, verify the client exists
                client_profile = await client_repo.get(id=client_id)
                if not client_profile:
                    logger.error(f"Client profile not found: {client_id}")
                    return {"error": "Client profile not found"}
                
                # Check if we already have relevant articles for this client
                relevance_repo = ArticleRelevanceRepository(db)
                
                # Get date range - looking for articles from the previous day by default
                report_date_obj = report_date or date.today()
                start_date = datetime.combine(report_date_obj - timedelta(days=1), time.min)
                end_date = datetime.combine(report_date_obj, time.min)
                
                relevances = await relevance_repo.get_by_client_id_and_date_range(
                    client_id=client_id,
                    date_from=start_date,
                    date_to=end_date,
                    min_score=0.6  # Threshold for inclusion
                )
                
                # If no relevances, trigger relevance calculation for recent articles
                if not relevances:
                    logger.info(f"No relevant articles found for client {client_id}. Triggering relevance calculation.")
                    
                    # Get recent articles from the date range
                    article_repo = ArticleRepository(db)
                    articles, _ = await article_repo.get_multi(
                        filters={"date_from": start_date, "date_to": end_date},
                        limit=50
                    )
                    
                    # Process each article for relevance
                    ai_service = AIService(db)
                    for article in articles:
                        await ai_service.process_article(article.id)
                        logger.info(f"Processed article {article.id} for client {client_id}")
                
                # Now generate the report
                result = await report_service.generate_daily_report(
                    client_id=client_id,
                    report_date=report_date_obj
                )

                # Store report ID if the service method returned one
                if result.get("report") and hasattr(result["report"], "id"):
                    report_id_for_error_update = result["report"].id

                if result["success"]:
                    report = result["report"]
                    logger.info(f"Successfully generated report {report.id} for client {client_id}")
                    return {"report_id": str(report.id), "status": report.status}
                else:
                    # Service handled the error gracefully, log and potentially update status
                    error_message = result.get('message', 'Unknown error during report generation')
                    logger.error(f"Report generation failed for client {client_id}: {error_message}")
                    if report_id_for_error_update:
                        logger.info(f"Attempting to mark report {report_id_for_error_update} as error due to service failure.")
                        await report_repo.update_status(report_id_for_error_update, "error")
                    return {"error": error_message}

            except Exception as e:
                # --- Catch unexpected exceptions during generate_daily_report ---
                logger.exception(f"Unhandled exception generating report for client {client_id}: {e}")
                if report_id_for_error_update:
                    # Attempt to mark the report as failed if we know its ID
                    try:
                        logger.info(f"Attempting to mark report {report_id_for_error_update} as error after exception.")
                        await report_repo.update_status(report_id_for_error_update, "error")
                        # Explicitly commit the status update if session is still active
                        await db.commit()
                    except Exception as update_err:
                        logger.error(f"Failed to update report status to error after exception: {update_err}")
                        await db.rollback() # Rollback if status update failed
                
                # Re-raise to trigger task retry
                raise

    try:
        # Run the async function
        return asyncio.run(_generate_report_async())
    except Exception as task_exc:
        # Retry the task
        logger.error(f"Celery task failed for client {client_id}: {task_exc}")
        self.retry(exc=task_exc)
        return {"error": f"Task execution failed: {task_exc}"}

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