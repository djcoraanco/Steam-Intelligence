from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.pc_expansion import CrossPlatformService

router = APIRouter(prefix="/cross-platform", tags=["cross-platform"])


class LinkCrossPlatformRequest(BaseModel):
    game_id: str
    platform_code: str
    external_id: str
    external_title: str
    store_url: Optional[str] = None
    match_confidence: str = "high_confidence"
    match_method: str = "steam_appid_link"
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


@router.get("/stores", response_model=Dict[str, Any])
def get_store_registry(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns the legal, technical, and capability matrix for all PC storefronts."""
    service = CrossPlatformService(db)
    return service.get_stores_registry()


@router.get("/{game_id}", response_model=List[Dict[str, Any]])
def get_game_cross_references(
    game_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CrossPlatformService(db)
    return service.get_game_cross_references(game_id)


@router.post("/link")
def link_external_game(
    payload: LinkCrossPlatformRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CrossPlatformService(db)
    try:
        ref = service.link_external_platform(
            game_id=payload.game_id,
            platform_code=payload.platform_code,
            external_id=payload.external_id,
            external_title=payload.external_title,
            store_url=payload.store_url,
            match_confidence=payload.match_confidence,
            match_method=payload.match_method,
            metadata=payload.metadata
        )
        return {
            "status": "success",
            "id": str(ref.id),
            "game_id": str(ref.game_id),
            "platform_code": ref.platform_code,
            "external_id": ref.external_id,
            "match_confidence": ref.match_confidence
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
