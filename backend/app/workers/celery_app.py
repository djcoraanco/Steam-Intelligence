from celery import Celery
from app.config import settings

celery_app = Celery(
    "steam_intelligence",
    broker=settings.REDIS_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "app.workers.tasks.sync_catalog": {"queue": "catalog"},
        "app.workers.tasks.sync_game_metadata": {"queue": "metadata"},
        "app.workers.tasks.snapshot_current_players": {"queue": "players_high_priority"},
        "app.workers.tasks.sync_reviews": {"queue": "reviews"},
        "app.workers.tasks.compute_market_rollups": {"queue": "analytics"},
        "app.workers.tasks.generate_export_job": {"queue": "exports"}
    },
    beat_schedule={
        "snapshot-high-priority-players-every-15-mins": {
            "task": "app.workers.tasks.snapshot_current_players",
            "schedule": 900.0,  # 15 minutes
        },
        "compute-market-rollups-daily": {
            "task": "app.workers.tasks.compute_market_rollups",
            "schedule": 86400.0,  # 24 hours
        }
    }
)
