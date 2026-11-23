from typing import List, Optional
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.research import NicheOpportunity
from app.schemas.niches import NicheOpportunityResponse, NicheAnalyzeResponse
from app.services.niche_finder import NicheFinderService

router = APIRouter()


@router.get("", response_model=List[NicheOpportunityResponse])
def get_niches(
    confidence: Optional[str] = Query(None, pattern="^(low|medium|high)$"),
    min_score: Optional[float] = Query(None, ge=0.0, le=100.0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(NicheOpportunity)
    if confidence:
        query = query.filter(NicheOpportunity.confidence_band == confidence)
    if min_score is not None:
        query = query.filter(NicheOpportunity.opportunity_score >= min_score)

    niches = query.order_by(desc(NicheOpportunity.opportunity_score)).limit(limit).all()
    return niches


@router.post("/analyze", response_model=NicheAnalyzeResponse)
def run_niche_analysis(db: Session = Depends(get_db)):
    """Triggers the Niche Finder algorithm across all observed categories and taxonomies."""
    service = NicheFinderService(db=db)
    results = service.analyze_and_record_all_niches()
    return NicheAnalyzeResponse(
        analyzed_niches_count=len(results),
        niches=results,
        executed_at=datetime.now(timezone.utc)
    )


@router.get("/{niche_id}", response_model=NicheOpportunityResponse)
def get_niche(niche_id: uuid.UUID, db: Session = Depends(get_db)):
    niche = db.query(NicheOpportunity).filter(NicheOpportunity.id == niche_id).first()
    if not niche:
        raise HTTPException(status_code=404, detail="Niche opportunity not found")
    return niche
