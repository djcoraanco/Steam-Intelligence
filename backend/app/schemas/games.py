from datetime import date, datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict


class GameSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    canonical_name: str
    slug: Optional[str] = None
    release_date: Optional[date] = None
    release_status: str
    game_type: str
    is_early_access: bool
    cover_image_url: Optional[str] = None
    steam_appid: Optional[str] = None
    current_players: Optional[int] = None
    positive_ratio: Optional[float] = None
    total_reviews: Optional[int] = None
    last_seen_at: Optional[datetime] = None


class GameListResponse(BaseModel):
    items: List[GameSummary]
    total: int
    limit: int
    offset: int
