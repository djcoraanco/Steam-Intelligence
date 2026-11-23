import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base, GUID, UniversalJSON


def now_utc():
    return datetime.now(timezone.utc)


class GameCrossReference(Base):
    """
    Cross-platform identity mapping between canonical games and external storefronts
    such as IGDB, itch.io, GOG, and Epic Games Store.
    Preserves confidence and matching method to prevent false merges.
    """
    __tablename__ = "game_cross_references"
    __table_args__ = (
        UniqueConstraint("game_id", "platform_code", "external_id", name="uq_game_cross_ref"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    game_id = Column(GUID, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_code = Column(String(40), nullable=False, index=True)  # igdb, itch, gog, epic
    external_id = Column(String(120), nullable=False, index=True)
    external_title = Column(Text, nullable=True)
    store_url = Column(Text, nullable=True)
    match_confidence = Column(String(20), default="high_confidence")  # verified, high_confidence, candidate, manual
    match_method = Column(String(40), default="steam_appid_link")  # steam_appid_link, title_and_dev, manual_match
    metadata_payload = Column(UniversalJSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    game = relationship("Game")
