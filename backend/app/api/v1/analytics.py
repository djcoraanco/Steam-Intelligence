from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.rollups import GameMetricRollup, MarketSegmentRollup
from app.schemas.analytics import GameMetricRollupResponse, MarketSegmentRollupResponse
from app.services.analytics_engine import AnalyticsEngine

router = APIRouter()


@router.get("/rollups/{game_platform_id}", response_model=List[GameMetricRollupResponse])
def get_game_rollups(
    game_platform_id: uuid.UUID,
    period_type: str = Query("day", pattern="^(day|week|month)$"),
    limit: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    rollups = (
        db.query(GameMetricRollup)
        .filter(
            GameMetricRollup.game_platform_id == game_platform_id,
            GameMetricRollup.period_type == period_type
        )
        .order_by(desc(GameMetricRollup.period_start))
        .limit(limit)
        .all()
    )
    return rollups


@router.get("/segments", response_model=List[MarketSegmentRollupResponse])
def get_segment_rollups(
    segment_type: str = Query("genre"),
    db: Session = Depends(get_db)
):
    rollups = (
        db.query(MarketSegmentRollup)
        .filter(MarketSegmentRollup.segment_type == segment_type)
        .order_by(desc(MarketSegmentRollup.period_start), desc(MarketSegmentRollup.game_count))
        .all()
    )
    return rollups


@router.post("/compute-rollups")
def compute_rollups(period_type: str = Query("day"), db: Session = Depends(get_db)):
    """Triggers deterministic aggregation calculation across segments and games."""
    engine = AnalyticsEngine(db=db)
    segment_rollups = engine.compute_all_market_segment_rollups(period_type=period_type)
    return {
        "success": True,
        "segments_computed": len(segment_rollups),
        "period_type": period_type
    }
