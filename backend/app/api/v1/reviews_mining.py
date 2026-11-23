from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.review_mining import ReviewMiningService

router = APIRouter(prefix="/reviews-mining", tags=["reviews-mining"])


@router.get("/{game_id}", response_model=Dict[str, Any])
def mine_reviews_for_game(
    game_id: str,
    limit: int = Query(150, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Executes review mining pipeline on game reviews.
    Extracts topics across the 15 standard taxonomies, calculates prevalence with sample denominator,
    and returns citations of source review IDs.
    """
    service = ReviewMiningService(db)
    try:
        return service.mine_and_extract_topics(game_id, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
