from celery import Celery
from app.core.config import settings 

# Example: Assuming Redis broker URL is in settings
# Ensure this URL is correctly configured for your Redis instance
# e.g., redis://localhost:6379/0
broker_url = getattr(settings, "CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = getattr(settings, "CELERY_RESULT_BACKEND", "redis://localhost:6379/1")


celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=result_backend,
    include=[
        "app.celery_worker.tasks.report_tasks",
        "app.celery_worker.tasks.ai_tasks",
        "app.celery_worker.tasks.feed_tasks"
    ]  # Include all task modules
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,  # Add this for better stability
)

# Enable Celery Beat for scheduling tasks
celery_app.conf.beat_schedule = {
    # Process new articles for relevance calculation every 15 minutes
    'process-new-articles': {
        'task': 'process_new_articles',  # This matches the task name in ai_tasks.py
        'schedule': 900.0,  # Run every 15 minutes (in seconds)
    },
    # Process feeds every hour to fetch new articles
    'process-all-feeds': {
        'task': 'process_all_feeds',  # This matches the task name in feed_tasks.py
        'schedule': 3600.0,  # Run every hour (in seconds)
    },
    # Generate daily reports at midnight
    'generate-all-daily-reports': {
        'task': 'generate_all_daily_reports',  # This matches the task name in report_tasks.py
        'schedule': {'hour': 0, 'minute': 0},  # Run at midnight
    },
}