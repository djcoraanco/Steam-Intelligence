import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, BigInteger, DateTime, Numeric,
    ForeignKey, PrimaryKeyConstraint
)
from app.core.database import Base, GUID, UniversalJSON


def now_utc():
    return datetime.now(timezone.utc)


class GameMetricRollup(Base):
    __tablename__ = "game_metric_rollups"
    __table_args__ = (
        PrimaryKeyConstraint("game_platform_id", "period_start", "period_type", "calculation_version", name="pk_game_metric_rollups"),
    )

    game_platform_id = Column(GUID, ForeignKey("game_platforms.id", ondelete="CASCADE"), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_type = Column(String(16), nullable=False)  # hour, day, week, month
    avg_players = Column(Numeric(10, 2), nullable=True)
    max_players = Column(Integer, nullable=True)
    min_players = Column(Integer, nullable=True)
    player_observation_count = Column(Integer, default=0)
    review_delta = Column(Integer, nullable=True)
    price_min_minor = Column(BigInteger, nullable=True)
    price_max_minor = Column(BigInteger, nullable=True)
    discount_days = Column(Integer, default=0)
    data_coverage = Column(Numeric(5, 2), default=100.0)
    calculation_version = Column(String(32), default="v1.0")


class MarketSegmentRollup(Base):
    __tablename__ = "market_segment_rollups"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    segment_type = Column(String(30), nullable=False, index=True)  # genre, tag, genre_combo, price_band, release_cohort
    segment_key = Column(UniversalJSON, nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_type = Column(String(16), nullable=False)
    game_count = Column(Integer, default=0)
    active_game_count = Column(Integer, default=0)
    player_sum = Column(BigInteger, nullable=True)
    review_delta = Column(BigInteger, nullable=True)
    median_price_minor = Column(BigInteger, nullable=True)
    new_release_count = Column(Integer, default=0)
    top_game_concentration = Column(Numeric(5, 4), nullable=True)
    data_coverage = Column(Numeric(5, 2), default=100.0)
    calculation_version = Column(String(32), default="v1.0")
