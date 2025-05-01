from celery import Celery
from app.core.config import settings # Your settings

# Example: Assuming Redis broker URL is in settings
# Ensure this URL is correctly configured for your Redis instance
# e.g., redis://localhost:6379/0
broker_url = getattr(settings, "CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = getattr(settings, "CELERY_RESULT_BACKEND", "redis://localhost:6379/1")


celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=result_backend,
    include=["app.celery_worker.tasks.report_tasks"] # IMPORTANT: Include your tasks module
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],  # Accept json content
    result_serializer="json",
    timezone="UTC", # Or your preferred timezone
    enable_utc=True,
    # Add other Celery configurations if needed
    # task_track_started=True,
    # broker_connection_retry_on_startup=True,
)

# Optional: If you want Celery Beat for scheduling the relevance calculation
# celery_app.conf.beat_schedule = {
#    'process-daily-articles-every-hour': {
#        'task': 'app.celery_worker.tasks.relevance_tasks.process_daily_articles_task', # Assumes you create this task
#        'schedule': 3600.0, # Run every hour (in seconds)
#    },
# }