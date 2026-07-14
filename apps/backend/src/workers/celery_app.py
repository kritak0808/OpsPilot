from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "opspilot_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Celery task definitions
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "src.workers.tasks.schedule_pipeline": {"queue": "pipeline_scheduler"},
        "src.workers.tasks.execute_pipeline_job": {"queue": "pipeline_executor"},
        "src.workers.tasks.process_artifacts": {"queue": "artifact_processor"},
        "src.workers.tasks.send_notifications": {"queue": "notifications"},
        "src.workers.tasks.process_logs": {"queue": "log_processor"},
        "src.workers.tasks.run_cleanup": {"queue": "cleanup"},
        "src.workers.tasks.sync_cluster_resources": {"queue": "cluster_sync"},
        "src.workers.tasks.execute_helm_deployment": {"queue": "helm_executor"},
        "src.workers.tasks.rollback_release": {"queue": "rollback_executor"},
    }
)
