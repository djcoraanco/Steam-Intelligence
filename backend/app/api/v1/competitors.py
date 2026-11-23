from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.competitor_analyzer import CompetitorAnalyzerService

router = APIRouter(prefix="/competitors", tags=["competitors"])


class LinkCompetitorRequest(BaseModel):
    game_id: str
    competitor_game_id: str
    reason_type: str = "tag_overlap"
    similarity_score: Optional[float] = None
    notes: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


@router.get("/suggestions/{game_id}", response_model=List[Dict[str, Any]])
def get_competitor_suggestions(
    game_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CompetitorAnalyzerService(db)
    return service.suggest_competitors(game_id, limit=limit)


@router.post("/link")
def link_competitor(
    payload: LinkCompetitorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CompetitorAnalyzerService(db)
    rel = service.link_competitor(
        game_id=payload.game_id,
        competitor_game_id=payload.competitor_game_id,
        reason_type=payload.reason_type,
        similarity_score=payload.similarity_score,
        notes=payload.notes
    )
    return {
        "status": "success",
        "id": str(rel.id),
        "game_id": str(rel.game_id),
        "competitor_game_id": str(rel.competitor_game_id),
        "reason_type": rel.reason_type
    }


@router.get("/{game_id}")
def get_linked_competitors(
    game_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CompetitorAnalyzerService(db)
    return service.list_linked_competitors(game_id)


@router.get("/compare/{game_id_a}/{game_id_b}")
def compare_games(
    game_id_a: str,
    game_id_b: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CompetitorAnalyzerService(db)
    try:
        return service.compare_head_to_head(game_id_a, game_id_b)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
