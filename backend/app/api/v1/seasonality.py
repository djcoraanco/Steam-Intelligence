from datetime import date
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.seasonality import SeasonalityEngine

router = APIRouter(prefix="/seasonality", tags=["seasonality"])


@router.get("/events", response_model=List[Dict[str, Any]])
def list_industry_events(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists documented industry events, seasonal sales, and Steam Next Fest editions."""
    engine = SeasonalityEngine(db)
    return engine.get_events(from_date=from_date, to_date=to_date)


@router.get("/cohorts", response_model=Dict[str, Any])
def get_cohorts_analysis(
    dimension: str = Query("release_year", pattern="^(release_year|early_access|release_month)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Groups historical releases into cohorts with observed metrics and disclaimers."""
    engine = SeasonalityEngine(db)
    return engine.get_cohort_analysis(cohort_dimension=dimension)


@router.get("/launch-collision", response_model=Dict[str, Any])
def analyze_launch_collision(
    target_date: date = Query(..., description="Planned release date (YYYY-MM-DD)"),
    days_window: int = Query(14, ge=3, le=60, description="Window radius in days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluates collision risk for a target launch date:
    identifies clashes with major sales, density of competing releases, and suggests cleaner windows.
    """
    engine = SeasonalityEngine(db)
    return engine.analyze_launch_collision(target_date=target_date, days_window=days_window)
