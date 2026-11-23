from datetime import datetime
from typing import List, Optional, Any
import uuid
from pydantic import BaseModel


class MetricDefinition(BaseModel):
    name: str
    value: Any
    unit: Optional[str] = None
    period: str = "current"
    data_type: str = "derived"  # official, third_party, estimated, derived
    freshness_seconds: Optional[int] = None
    source: str = "Steam Intelligence"


class TopGameItem(BaseModel):
    game_id: uuid.UUID
    canonical_name: str
    steam_appid: Optional[str] = None
    cover_image_url: Optional[str] = None
    current_players: Optional[int] = None
    peak_observed: Optional[int] = None
    total_reviews: Optional[int] = None
    positive_ratio: Optional[float] = None
    price_cents: Optional[int] = None
    currency: str = "USD"
    availability_status: str = "available"


class DashboardOverviewResponse(BaseModel):
    indexed_games_count: int
    monitored_games_count: int
    active_sources_count: int
    latest_observation_at: Optional[datetime] = None
    data_freshness_status: str  # fresh, stale, unavailable
    top_games: List[TopGameItem] = []
    rising_genres: List[dict] = []
    detected_niches_count: int = 0
    active_research_runs_count: int = 0
