import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, BigInteger, Boolean,
    DateTime, Numeric, SmallInteger, ForeignKey, CHAR, UniqueConstraint, PrimaryKeyConstraint
)
from app.core.database import Base, GUID, UniversalJSON


def now_utc():
    return datetime.now(timezone.utc)


class PlayerSnapshot(Base):
    __tablename__ = "player_snapshots"
    __table_args__ = (
        PrimaryKeyConstraint("game_platform_id", "source_id", "observed_at", name="pk_player_snapshots"),
    )

    observed_at = Column(DateTime(timezone=True), default=now_utc, nullable=False, index=True)
    game_platform_id = Column(GUID, ForeignKey("game_platforms.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(GUID, ForeignKey("data_sources.id", ondelete="RESTRICT"), nullable=False, index=True)
    player_count = Column(Integer, nullable=True)
    availability_status = Column(String(20), default="available")  # available, unavailable, stale, unsupported
    quality_score = Column(SmallInteger, default=100)
    raw_payload_id = Column(GUID, ForeignKey("raw_payloads.id", ondelete="SET NULL"), nullable=True)


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"
    __table_args__ = (
        PrimaryKeyConstraint("game_platform_id", "country_code", "observed_at", name="pk_price_snapshots"),
    )

    observed_at = Column(DateTime(timezone=True), default=now_utc, nullable=False, index=True)
    game_platform_id = Column(GUID, ForeignKey("game_platforms.id", ondelete="CASCADE"), nullable=False, index=True)
    country_code = Column(CHAR(2), nullable=False, default="US")
    currency = Column(CHAR(3), nullable=False, default="USD")
    regular_price_minor = Column(BigInteger, nullable=True)  # in cents
    final_price_minor = Column(BigInteger, nullable=True)
    discount_percent = Column(Numeric(5, 2), nullable=True)
    is_free = Column(Boolean, default=False)
    source_id = Column(GUID, ForeignKey("data_sources.id", ondelete="RESTRICT"), nullable=False)
    availability_status = Column(String(20), default="available")
    raw_payload_id = Column(GUID, ForeignKey("raw_payloads.id", ondelete="SET NULL"), nullable=True)


class ReviewSnapshot(Base):
    __tablename__ = "review_snapshots"
    __table_args__ = (
        PrimaryKeyConstraint("game_platform_id", "language_code", "observed_at", name="pk_review_snapshots"),
    )

    observed_at = Column(DateTime(timezone=True), default=now_utc, nullable=False, index=True)
    game_platform_id = Column(GUID, ForeignKey("game_platforms.id", ondelete="CASCADE"), nullable=False, index=True)
    language_code = Column(String(16), default="all")
    total_reviews = Column(BigInteger, nullable=True)
    positive_reviews = Column(BigInteger, nullable=True)
    negative_reviews = Column(BigInteger, nullable=True)
    positive_ratio = Column(Numeric(6, 5), nullable=True)
    review_period_days = Column(Integer, nullable=True)
    source_id = Column(GUID, ForeignKey("data_sources.id", ondelete="RESTRICT"), nullable=False)
    availability_status = Column(String(20), default="available")


class RankingSnapshot(Base):
    __tablename__ = "ranking_snapshots"
    __table_args__ = (
        PrimaryKeyConstraint("game_platform_id", "ranking_type", "observed_at", name="pk_ranking_snapshots"),
    )

    observed_at = Column(DateTime(timezone=True), default=now_utc, nullable=False, index=True)
    game_platform_id = Column(GUID, ForeignKey("game_platforms.id", ondelete="CASCADE"), nullable=False, index=True)
    ranking_type = Column(String(40), nullable=False)  # top_sellers, most_played, etc.
    region_code = Column(CHAR(2), nullable=True)
    rank_position = Column(Integer, nullable=False)
    source_id = Column(GUID, ForeignKey("data_sources.id", ondelete="RESTRICT"), nullable=False)
    ranking_scope = Column(UniversalJSON, default=dict)


class ReviewItem(Base):
    __tablename__ = "review_items"
    __table_args__ = (
        UniqueConstraint("source_id", "source_review_id", name="uq_review_source_item"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    source_id = Column(GUID, ForeignKey("data_sources.id", ondelete="RESTRICT"), nullable=False)
    source_review_id = Column(String(120), nullable=False, index=True)
    game_platform_id = Column(GUID, ForeignKey("game_platforms.id", ondelete="CASCADE"), nullable=False, index=True)
    language_code = Column(String(16), default="english")
    reviewed_at = Column(DateTime(timezone=True), default=now_utc)
    voted_up = Column(Boolean, nullable=False)
    votes_up = Column(Integer, default=0)
    votes_funny = Column(Integer, default=0)
    playtime_forever_minutes = Column(Integer, default=0)
    playtime_at_review_minutes = Column(Integer, default=0)
    review_text = Column(Text, nullable=True)
