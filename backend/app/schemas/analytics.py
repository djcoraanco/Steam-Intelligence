from datetime import datetime
from typing import Optional, Dict, Any
import uuid
from pydantic import BaseModel, ConfigDict


class GameMetricRollupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    game_platform_id: uuid.UUID
    period_start: datetime
    period_type: str
    avg_players: Optional[float] = None
    max_players: Optional[int] = None
    min_players: Optional[int] = None
    player_observation_count: int = 0
    review_delta: Optional[int] = None
    price_min_minor: Optional[int] = None
    price_max_minor: Optional[int] = None
    discount_days: int = 0
    data_coverage: float = 100.0
    calculation_version: str


class MarketSegmentRollupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    segment_type: str
    segment_key: Dict[str, Any]
    period_start: datetime
    period_type: str
    game_count: int
    active_game_count: int
    player_sum: Optional[int] = None
    median_price_minor: Optional[int] = None
    new_release_count: int = 0
    top_game_concentration: Optional[float] = None
    data_coverage: float = 100.0
    calculation_version: str
