"""phases 7, 8, 9 schema: competitors, review topics, cross references, industry events

Revision ID: 003_phases_7_8_9_schema
Revises: 002_ingestion_checkpoints
Create Date: 2026-11-23 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql, sqlite

revision: str = '003_phases_7_8_9_schema'
down_revision: Union[str, None] = '002_ingestion_checkpoints'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSONType = sa.JSON().with_variant(postgresql.JSONB, 'postgresql').with_variant(sqlite.JSON, 'sqlite')


def upgrade() -> None:
    # 1. game_competitors
    op.create_table(
        'game_competitors',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('game_id', sa.String(36), sa.ForeignKey('games.id', ondelete='CASCADE'), nullable=False),
        sa.Column('competitor_game_id', sa.String(36), sa.ForeignKey('games.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reason_type', sa.String(50), nullable=False),
        sa.Column('similarity_score', sa.Numeric(5, 4), nullable=True),
        sa.Column('notes', JSONType, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('game_id', 'competitor_game_id', 'reason_type', name='uq_game_competitor_reason')
    )
    op.create_index('ix_game_competitors_game_id', 'game_competitors', ['game_id'])
    op.create_index('ix_game_competitors_competitor_game_id', 'game_competitors', ['competitor_game_id'])

    # 2. review_topic_extractions
    op.create_table(
        'review_topic_extractions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('review_item_id', sa.String(36), sa.ForeignKey('review_items.id', ondelete='CASCADE'), nullable=True),
        sa.Column('game_id', sa.String(36), sa.ForeignKey('games.id', ondelete='CASCADE'), nullable=False),
        sa.Column('topic', sa.String(50), nullable=False),
        sa.Column('sentiment', sa.String(20), nullable=False, server_default='neutral'),
        sa.Column('confidence', sa.Numeric(5, 2), nullable=True, server_default='0.85'),
        sa.Column('evidence_excerpt', sa.Text(), nullable=False),
        sa.Column('source_review_id', sa.String(120), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('ix_review_topic_extractions_game_id', 'review_topic_extractions', ['game_id'])
    op.create_index('ix_review_topic_extractions_topic', 'review_topic_extractions', ['topic'])
    op.create_index('ix_review_topic_extractions_source_review_id', 'review_topic_extractions', ['source_review_id'])

    # 3. game_cross_references
    op.create_table(
        'game_cross_references',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('game_id', sa.String(36), sa.ForeignKey('games.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform_code', sa.String(40), nullable=False),
        sa.Column('external_id', sa.String(120), nullable=False),
        sa.Column('external_title', sa.Text(), nullable=True),
        sa.Column('store_url', sa.Text(), nullable=True),
        sa.Column('match_confidence', sa.String(20), nullable=True, server_default='high_confidence'),
        sa.Column('match_method', sa.String(40), nullable=True, server_default='steam_appid_link'),
        sa.Column('metadata_payload', JSONType, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('game_id', 'platform_code', 'external_id', name='uq_game_cross_ref')
    )
    op.create_index('ix_game_cross_references_game_id', 'game_cross_references', ['game_id'])
    op.create_index('ix_game_cross_references_platform_code', 'game_cross_references', ['platform_code'])
    op.create_index('ix_game_cross_references_external_id', 'game_cross_references', ['external_id'])

    # 4. industry_events
    op.create_table(
        'industry_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('code', sa.String(60), nullable=False, unique=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('event_type', sa.String(40), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('source_ref', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('historical_impact', JSONType, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('ix_industry_events_code', 'industry_events', ['code'])
    op.create_index('ix_industry_events_start_date', 'industry_events', ['start_date'])
    op.create_index('ix_industry_events_end_date', 'industry_events', ['end_date'])


def downgrade() -> None:
    op.drop_table('industry_events')
    op.drop_table('game_cross_references')
    op.drop_table('review_topic_extractions')
    op.drop_table('game_competitors')
