from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.ai_analyst import AIAnalystService

router = APIRouter(prefix="/ai", tags=["ai"])


class AIQueryRequest(BaseModel):
    question: str
    target_genre: Optional[str] = "Action"
    target_game_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ValidateConceptRequest(BaseModel):
    concept_description: str
    genres: List[str] = ["Indie"]

    model_config = ConfigDict(from_attributes=True)


@router.post("/query", response_model=Dict[str, Any])
async def query_market_analyst(
    payload: AIQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submits a query to the AI Market Analyst layer.
    Returns structured evidence-first findings with cited metrics and confidence bands.
    """
    service = AIAnalystService(db)
    return await service.analyze_market_question(
        question=payload.question,
        target_genre=payload.target_genre,
        target_game_id=payload.target_game_id
    )


@router.post("/validate-concept", response_model=Dict[str, Any])
async def validate_game_concept(
    payload: ValidateConceptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validates a video game concept against observed market density and genre history.
    """
    service = AIAnalystService(db)
    return await service.validate_game_concept(
        concept_description=payload.concept_description,
        genres=payload.genres
    )
