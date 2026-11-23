import asyncio
import uuid
from typing import Optional
from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.core.logging import logger
from app.services.catalog_sync import CatalogSyncService
from app.services.metadata_sync import MetadataSyncService


@celery_app.task(name="app.workers.tasks.sync_catalog", bind=True)
def sync_catalog(self, max_results: int = 10000, resume: bool = True):
    logger.info("sync_catalog_started", task_id=self.request.id, max_results=max_results, resume=resume)
    db = SessionLocal()
    try:
        service = CatalogSyncService(db=db)
        result = asyncio.run(service.sync_batch(max_results=max_results, resume=resume))
        return result
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.snapshot_current_players", bind=True)
def snapshot_current_players(self, appids: Optional[list[int]] = None):
    logger.info("snapshot_current_players_started", task_id=self.request.id, count=len(appids or []))
    # Placeholder for player snapshot worker execution
    return {"status": "completed", "processed": len(appids or [])}


@celery_app.task(name="app.workers.tasks.sync_game_metadata", bind=True)
def sync_game_metadata(self, game_id_str: str, country_code: str = "us", language: str = "english"):
    logger.info("sync_game_metadata_started", task_id=self.request.id, game_id=game_id_str)
    db = SessionLocal()
    try:
        game_id = uuid.UUID(game_id_str)
        service = MetadataSyncService(db=db)
        result = asyncio.run(service.sync_game_details(game_id=game_id, country_code=country_code, language=language))
        return result
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.sync_reviews", bind=True)
def sync_reviews(self, appid: int):
    logger.info("sync_reviews_started", task_id=self.request.id, appid=appid)
    return {"status": "completed", "appid": appid}


@celery_app.task(name="app.workers.tasks.compute_market_rollups", bind=True)
def compute_market_rollups(self):
    logger.info("compute_market_rollups_started", task_id=self.request.id)
    return {"status": "completed"}


@celery_app.task(name="app.workers.tasks.generate_export_job", bind=True)
def generate_export_job(self, export_id: str, report_id: str, format_type: str):
    logger.info("generate_export_job_started", task_id=self.request.id, export_id=export_id, format=format_type)
    return {"status": "completed", "export_id": export_id}
