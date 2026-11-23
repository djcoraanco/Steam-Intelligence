import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Boolean, Date, DateTime, Numeric,
    ForeignKey, UniqueConstraint, PrimaryKeyConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base, GUID


def now_utc():
    return datetime.now(timezone.utc)


class Platform(Base):
    __tablename__ = "platforms"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    code = Column(String(40), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    website_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    game_links = relationship("GamePlatform", back_populates="platform")


class Game(Base):
    __tablename__ = "games"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    canonical_name = Column(Text, nullable=False, index=True)
    slug = Column(Text, nullable=True, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(Text, nullable=True)
    release_date = Column(Date, nullable=True)
    release_date_precision = Column(String(20), default="unknown")  # day, month, year, unknown
    release_status = Column(String(30), default="released")  # announced, coming_soon, released, cancelled, unknown
    game_type = Column(String(30), default="game")  # game, dlc, demo, tool, soundtrack, unknown
    is_early_access = Column(Boolean, default=False)
    cover_image_url = Column(Text, nullable=True)
    website_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    platforms = relationship("GamePlatform", back_populates="game", cascade="all, delete-orphan")


class GamePlatform(Base):
    __tablename__ = "game_platforms"
    __table_args__ = (
        UniqueConstraint("platform_id", "external_id", name="uq_game_platform_external"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    game_id = Column(GUID, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_id = Column(GUID, ForeignKey("platforms.id", ondelete="RESTRICT"), nullable=False, index=True)
    external_id = Column(String(120), nullable=False, index=True)  # e.g. Steam appid as string
    store_url = Column(Text, nullable=True)
    first_seen_at = Column(DateTime(timezone=True), default=now_utc)
    last_seen_at = Column(DateTime(timezone=True), default=now_utc)
    is_primary = Column(Boolean, default=True)

    game = relationship("Game", back_populates="platforms")
    platform = relationship("Platform", back_populates="game_links")


class Organization(Base):
    """Developers and Publishers."""
    __tablename__ = "organizations"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    canonical_name = Column(Text, nullable=False, index=True)
    website_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)


class GameDeveloper(Base):
    __tablename__ = "game_developers"
    __table_args__ = (
        PrimaryKeyConstraint("game_id", "organization_id", name="pk_game_developers"),
    )

    game_id = Column(GUID, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(GUID, nullable=True)
    observed_at = Column(DateTime(timezone=True), default=now_utc)


class GamePublisher(Base):
    __tablename__ = "game_publishers"
    __table_args__ = (
        PrimaryKeyConstraint("game_id", "organization_id", name="pk_game_publishers"),
    )

    game_id = Column(GUID, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(GUID, nullable=True)
    observed_at = Column(DateTime(timezone=True), default=now_utc)


class TaxonomyItem(Base):
    """Genres, tags, categories across taxonomies."""
    __tablename__ = "taxonomy_items"
    __table_args__ = (
        UniqueConstraint("taxonomy_source", "external_id", "language_code", name="uq_taxonomy_source_item"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    canonical_name = Column(Text, nullable=False, index=True)
    slug = Column(Text, nullable=True)
    taxonomy_source = Column(String(40), nullable=False)  # steam_genre, steam_tag, steam_category, igdb_genre, internal
    external_id = Column(String(120), nullable=True)
    language_code = Column(String(16), default="en")


class GameTaxonomy(Base):
    __tablename__ = "game_taxonomies"
    __table_args__ = (
        PrimaryKeyConstraint("game_id", "taxonomy_id", name="pk_game_taxonomies"),
    )

    game_id = Column(GUID, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    taxonomy_id = Column(GUID, ForeignKey("taxonomy_items.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(GUID, nullable=True)
    observed_at = Column(DateTime(timezone=True), default=now_utc)
    rank_value = Column(Numeric, nullable=True)
    weight = Column(Numeric, nullable=True)
