import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Numeric, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base, GUID, UniversalJSON


def now_utc():
    return datetime.now(timezone.utc)


class GameCompetitor(Base):
    """
    Direct and recommended competitor links between games.
    Tracks why they are competitors (tag_overlap, genre_overlap, mechanic_overlap, etc.)
    """
    __tablename__ = "game_competitors"
    __table_args__ = (
        UniqueConstraint("game_id", "competitor_game_id", "reason_type", name="uq_game_competitor_reason"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    game_id = Column(GUID, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    competitor_game_id = Column(GUID, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    reason_type = Column(String(50), nullable=False)  # tag_overlap, genre_overlap, mechanic_overlap, audience_overlap, manual_selection, semantic_similarity
    similarity_score = Column(Numeric(5, 4), nullable=True)  # Jaccard index or score (0.0 to 1.0)
    notes = Column(UniversalJSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    game = relationship("Game", foreign_keys=[game_id])
    competitor = relationship("Game", foreign_keys=[competitor_game_id])


class ReviewTopicExtraction(Base):
    """
    Topic and sentiment extraction from parsed user reviews.
    Taxonomy conforming strictly to Master Spec Section 9.3:
    bugs/crashes, performance/optimization, controls, ui/ux, difficulty/balance,
    content/replayability, price/value, multiplayer/network, progression,
    monetization, accessibility, localization, community/support,
    positive_gameplay_loop, art/audio/story.
    """
    __tablename__ = "review_topic_extractions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    review_item_id = Column(GUID, ForeignKey("review_items.id", ondelete="CASCADE"), nullable=True, index=True)
    game_id = Column(GUID, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(50), nullable=False, index=True)
    sentiment = Column(String(20), nullable=False, default="neutral")  # positive, negative, mixed, neutral
    confidence = Column(Numeric(5, 2), default=0.85)
    evidence_excerpt = Column(Text, nullable=False)
    source_review_id = Column(String(120), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)
