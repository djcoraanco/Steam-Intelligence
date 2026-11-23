from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.catalog_sync import CatalogSyncService
from app.models.checkpoints import IngestionCheckpoint

router = APIRouter()


class CatalogSyncRequest(BaseModel):
    max_results: int = 10000
    resume: bool = True
    include_games: bool = True
    include_dlc: bool = False


class CatalogStatusResponse(BaseModel):
    provider_code: str
    last_cursor: Optional[str] = None
    total_records: int
    status: str
    last_synced_at: Optional[str] = None
    error_message: Optional[str] = None


@router.get("/status")
def get_catalog_status(db: Session = Depends(get_db)):
    service = CatalogSyncService(db=db)
    checkpoint = service.get_or_create_checkpoint()
    return {
        "provider_code": checkpoint.provider_code,
        "last_cursor": checkpoint.last_cursor,
        "total_records": checkpoint.total_records,
        "status": checkpoint.status,
        "last_synced_at": checkpoint.last_synced_at.isoformat() if checkpoint.last_synced_at else None,
        "error_message": checkpoint.error_message
    }


@router.post("/sync")
async def trigger_catalog_sync(request: CatalogSyncRequest = CatalogSyncRequest(), db: Session = Depends(get_db)):
    """Trigger catalog batch synchronization step."""
    service = CatalogSyncService(db=db)
    try:
        result = await service.sync_batch(
            max_results=request.max_results,
            resume=request.resume,
            include_games=request.include_games,
            include_dlc=request.include_dlc
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Catalog sync failed: {str(exc)}"
        )
