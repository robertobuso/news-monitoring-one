from celery import Celery
from app.core.config import settings

# Create Celery instance
celery = Celery(
    "newsmonitor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.celery_worker.tasks.ai_tasks",
        "app.celery_worker.tasks.feed_tasks",
        "app.celery_worker.tasks.report_tasks"
    ]
)

# Optional configuration
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# This ensures tasks are properly registered
if __name__ == "__main__":
    celery.start()