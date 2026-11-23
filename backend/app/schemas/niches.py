from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid
from pydantic import BaseModel, ConfigDict


class NicheOpportunityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    segment_definition: Dict[str, Any]
    demand_score: float
    growth_score: float
    competitive_space_score: float
    commercial_feasibility_score: float
    evidence_quality_score: float
    opportunity_score: float
    score_version: str
    confidence_band: str
    limitations: List[str] = []
    created_at: datetime
    updated_at: datetime


class NicheAnalyzeResponse(BaseModel):
    analyzed_niches_count: int
    niches: List[NicheOpportunityResponse]
    executed_at: datetime
