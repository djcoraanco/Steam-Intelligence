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
    release_date_precision: Optional[str] = "unknown"
    release_status: str
    game_type: str
    is_early_access: bool
    cover_image_url: Optional[str] = None
    steam_appid: Optional[str] = None
    store_url: Optional[str] = None
    current_players: Optional[int] = None
    positive_ratio: Optional[float] = None
    total_reviews: Optional[int] = None
    price_cents: Optional[int] = None
    currency: str = "USD"
    is_free: bool = False
    availability_status: str = "available"
    last_seen_at: Optional[datetime] = None


class GameListResponse(BaseModel):
    items: List[GameSummary]
    total: int
    limit: int
    offset: int


class GameDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    canonical_name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    release_date: Optional[date] = None
    release_date_precision: str = "unknown"
    release_status: str
    game_type: str
    is_early_access: bool
    cover_image_url: Optional[str] = None
    website_url: Optional[str] = None
    steam_appid: Optional[str] = None
    store_url: Optional[str] = None
    
    # Pricing info
    regular_price_cents: Optional[int] = None
    final_price_cents: Optional[int] = None
    discount_percent: Optional[float] = None
    currency: str = "USD"
    is_free: bool = False
    price_status: str = "available"
    
    # Taxonomies & Entities
    developers: List[str] = []
    publishers: List[str] = []
    genres: List[str] = []
    
    # Metadata
    created_at: datetime
    updated_at: datetime
