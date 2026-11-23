"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-23 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Platforms table
    op.create_table(
        'platforms',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('code', sa.String(40), nullable=False, unique=True),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('website_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )

    # Games table
    op.create_table(
        'games',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('canonical_name', sa.Text(), nullable=False),
        sa.Column('slug', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('short_description', sa.Text(), nullable=True),
        sa.Column('release_date', sa.Date(), nullable=True),
        sa.Column('release_date_precision', sa.String(20), nullable=True),
        sa.Column('release_status', sa.String(30), nullable=True),
        sa.Column('game_type', sa.String(30), nullable=True),
        sa.Column('is_early_access', sa.Boolean(), nullable=True),
        sa.Column('cover_image_url', sa.Text(), nullable=True),
        sa.Column('website_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('ix_games_canonical_name', 'games', ['canonical_name'])

    # Game Platforms table
    op.create_table(
        'game_platforms',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('game_id', sa.String(36), sa.ForeignKey('games.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform_id', sa.String(36), sa.ForeignKey('platforms.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('external_id', sa.String(120), nullable=False),
        sa.Column('store_url', sa.Text(), nullable=True),
        sa.Column('first_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=True),
        sa.UniqueConstraint('platform_id', 'external_id', name='uq_game_platform_external')
    )
    op.create_index('ix_game_platforms_external_id', 'game_platforms', ['external_id'])

    # Organizations (Developers & Publishers)
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('canonical_name', sa.Text(), nullable=False),
        sa.Column('website_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'game_developers',
        sa.Column('game_id', sa.String(36), sa.ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('source_id', sa.String(36), nullable=True),
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'game_publishers',
        sa.Column('game_id', sa.String(36), sa.ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('source_id', sa.String(36), nullable=True),
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=True)
    )

    # Taxonomies
    op.create_table(
        'taxonomy_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('canonical_name', sa.Text(), nullable=False),
        sa.Column('slug', sa.Text(), nullable=True),
        sa.Column('taxonomy_source', sa.String(40), nullable=False),
        sa.Column('external_id', sa.String(120), nullable=True),
        sa.Column('language_code', sa.String(16), nullable=True),
        sa.UniqueConstraint('taxonomy_source', 'external_id', 'language_code', name='uq_taxonomy_source_item')
    )

    op.create_table(
        'game_taxonomies',
        sa.Column('game_id', sa.String(36), sa.ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('taxonomy_id', sa.String(36), sa.ForeignKey('taxonomy_items.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('source_id', sa.String(36), nullable=True),
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rank_value', sa.Numeric(), nullable=True),
        sa.Column('weight', sa.Numeric(), nullable=True)
    )

    # Data Sources and Raw Payloads
    op.create_table(
        'data_sources',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('code', sa.String(60), nullable=False, unique=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('provider_type', sa.String(30), nullable=False),
        sa.Column('base_url', sa.Text(), nullable=True),
        sa.Column('documentation_url', sa.Text(), nullable=True),
        sa.Column('terms_url', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('capabilities', sa.JSON(), nullable=True),
        sa.Column('rate_limit_config', sa.JSON(), nullable=True),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'raw_payloads',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('source_id', sa.String(36), sa.ForeignKey('data_sources.id', ondelete='SET NULL'), nullable=True),
        sa.Column('request_fingerprint', sa.Text(), nullable=True),
        sa.Column('http_status', sa.Integer(), nullable=True),
        sa.Column('content_type', sa.Text(), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('payload_hash', sa.CHAR(64), nullable=True),
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('parser_version', sa.Text(), nullable=True),
        sa.Column('retention_until', sa.DateTime(timezone=True), nullable=True)
    )

    # Snapshots
    op.create_table(
        'player_snapshots',
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('game_platform_id', sa.String(36), sa.ForeignKey('game_platforms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_id', sa.String(36), sa.ForeignKey('data_sources.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('player_count', sa.Integer(), nullable=True),
        sa.Column('availability_status', sa.String(20), nullable=True),
        sa.Column('quality_score', sa.SmallInteger(), nullable=True),
        sa.Column('raw_payload_id', sa.String(36), sa.ForeignKey('raw_payloads.id', ondelete='SET NULL'), nullable=True),
        sa.PrimaryKeyConstraint('game_platform_id', 'source_id', 'observed_at', name='pk_player_snapshots')
    )

    op.create_table(
        'price_snapshots',
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('game_platform_id', sa.String(36), sa.ForeignKey('game_platforms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('country_code', sa.CHAR(2), nullable=False),
        sa.Column('currency', sa.CHAR(3), nullable=False),
        sa.Column('regular_price_minor', sa.BigInteger(), nullable=True),
        sa.Column('final_price_minor', sa.BigInteger(), nullable=True),
        sa.Column('discount_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('is_free', sa.Boolean(), nullable=True),
        sa.Column('source_id', sa.String(36), sa.ForeignKey('data_sources.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('availability_status', sa.String(20), nullable=True),
        sa.Column('raw_payload_id', sa.String(36), sa.ForeignKey('raw_payloads.id', ondelete='SET NULL'), nullable=True),
        sa.PrimaryKeyConstraint('game_platform_id', 'country_code', 'observed_at', name='pk_price_snapshots')
    )

    op.create_table(
        'review_snapshots',
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('game_platform_id', sa.String(36), sa.ForeignKey('game_platforms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('language_code', sa.String(16), nullable=False),
        sa.Column('total_reviews', sa.BigInteger(), nullable=True),
        sa.Column('positive_reviews', sa.BigInteger(), nullable=True),
        sa.Column('negative_reviews', sa.BigInteger(), nullable=True),
        sa.Column('positive_ratio', sa.Numeric(6, 5), nullable=True),
        sa.Column('review_period_days', sa.Integer(), nullable=True),
        sa.Column('source_id', sa.String(36), sa.ForeignKey('data_sources.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('availability_status', sa.String(20), nullable=True),
        sa.PrimaryKeyConstraint('game_platform_id', 'language_code', 'observed_at', name='pk_review_snapshots')
    )

    op.create_table(
        'ranking_snapshots',
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('game_platform_id', sa.String(36), sa.ForeignKey('game_platforms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ranking_type', sa.String(40), nullable=False),
        sa.Column('region_code', sa.CHAR(2), nullable=True),
        sa.Column('rank_position', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.String(36), sa.ForeignKey('data_sources.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('ranking_scope', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('game_platform_id', 'ranking_type', 'observed_at', name='pk_ranking_snapshots')
    )

    op.create_table(
        'review_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('source_id', sa.String(36), sa.ForeignKey('data_sources.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('source_review_id', sa.String(120), nullable=False),
        sa.Column('game_platform_id', sa.String(36), sa.ForeignKey('game_platforms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('language_code', sa.String(16), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('voted_up', sa.Boolean(), nullable=False),
        sa.Column('votes_up', sa.Integer(), nullable=True),
        sa.Column('votes_funny', sa.Integer(), nullable=True),
        sa.Column('playtime_forever_minutes', sa.Integer(), nullable=True),
        sa.Column('playtime_at_review_minutes', sa.Integer(), nullable=True),
        sa.Column('review_text', sa.Text(), nullable=True),
        sa.UniqueConstraint('source_id', 'source_review_id', name='uq_review_source_item')
    )

    # Rollups
    op.create_table(
        'game_metric_rollups',
        sa.Column('game_platform_id', sa.String(36), sa.ForeignKey('game_platforms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('period_type', sa.String(16), nullable=False),
        sa.Column('avg_players', sa.Numeric(10, 2), nullable=True),
        sa.Column('max_players', sa.Integer(), nullable=True),
        sa.Column('min_players', sa.Integer(), nullable=True),
        sa.Column('player_observation_count', sa.Integer(), nullable=True),
        sa.Column('review_delta', sa.Integer(), nullable=True),
        sa.Column('price_min_minor', sa.BigInteger(), nullable=True),
        sa.Column('price_max_minor', sa.BigInteger(), nullable=True),
        sa.Column('discount_days', sa.Integer(), nullable=True),
        sa.Column('data_coverage', sa.Numeric(5, 2), nullable=True),
        sa.Column('calculation_version', sa.String(32), nullable=False),
        sa.PrimaryKeyConstraint('game_platform_id', 'period_start', 'period_type', 'calculation_version', name='pk_game_metric_rollups')
    )

    op.create_table(
        'market_segment_rollups',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('segment_type', sa.String(30), nullable=False),
        sa.Column('segment_key', sa.JSON(), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('period_type', sa.String(16), nullable=False),
        sa.Column('game_count', sa.Integer(), nullable=True),
        sa.Column('active_game_count', sa.Integer(), nullable=True),
        sa.Column('player_sum', sa.BigInteger(), nullable=True),
        sa.Column('review_delta', sa.BigInteger(), nullable=True),
        sa.Column('median_price_minor', sa.BigInteger(), nullable=True),
        sa.Column('new_release_count', sa.Integer(), nullable=True),
        sa.Column('top_game_concentration', sa.Numeric(5, 4), nullable=True),
        sa.Column('data_coverage', sa.Numeric(5, 2), nullable=True),
        sa.Column('calculation_version', sa.String(32), nullable=False)
    )

    # Research & Niches
    op.create_table(
        'trend_signals',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('entity_type', sa.String(30), nullable=False),
        sa.Column('entity_id', sa.String(36), nullable=True),
        sa.Column('metric_name', sa.String(60), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('current_value', sa.Numeric(), nullable=False),
        sa.Column('baseline_value', sa.Numeric(), nullable=True),
        sa.Column('change_percent', sa.Numeric(), nullable=True),
        sa.Column('z_score', sa.Numeric(), nullable=True),
        sa.Column('trend_direction', sa.String(20), nullable=True),
        sa.Column('confidence_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('algorithm_version', sa.String(32), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'niche_opportunities',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('segment_definition', sa.JSON(), nullable=False),
        sa.Column('demand_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('growth_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('competitive_space_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('commercial_feasibility_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('evidence_quality_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('opportunity_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('score_version', sa.String(32), nullable=True),
        sa.Column('confidence_band', sa.String(20), nullable=True),
        sa.Column('limitations', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    # Users, Roles, Security
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('display_name', sa.String(120), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'roles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(40), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True)
    )

    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('role_id', sa.String(36), sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('actor_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(60), nullable=False),
        sa.Column('resource_id', sa.String(120), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True)
    )

    # Research Projects, Runs, Results
    op.create_table(
        'research_projects',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('research_type', sa.String(40), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'research_runs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('research_projects.id', ondelete='CASCADE'), nullable=True),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trigger_type', sa.String(20), nullable=True),
        sa.Column('requested_by', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('configuration_snapshot', sa.JSON(), nullable=True),
        sa.Column('total_tasks', sa.Integer(), nullable=True),
        sa.Column('completed_tasks', sa.Integer(), nullable=True),
        sa.Column('failed_tasks', sa.Integer(), nullable=True),
        sa.Column('games_processed', sa.Integer(), nullable=True),
        sa.Column('report_id', sa.String(36), nullable=True),
        sa.Column('error_summary', sa.JSON(), nullable=True)
    )

    op.create_table(
        'research_results',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('research_run_id', sa.String(36), sa.ForeignKey('research_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('result_type', sa.String(40), nullable=False),
        sa.Column('entity_type', sa.String(40), nullable=False),
        sa.Column('entity_id', sa.String(36), nullable=True),
        sa.Column('result_payload', sa.JSON(), nullable=True),
        sa.Column('evidence_refs', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('research_results')
    op.drop_table('research_runs')
    op.drop_table('research_projects')
    op.drop_table('audit_logs')
    op.drop_table('user_roles')
    op.drop_table('roles')
    op.drop_table('users')
    op.drop_table('niche_opportunities')
    op.drop_table('trend_signals')
    op.drop_table('market_segment_rollups')
    op.drop_table('game_metric_rollups')
    op.drop_table('review_items')
    op.drop_table('ranking_snapshots')
    op.drop_table('review_snapshots')
    op.drop_table('price_snapshots')
    op.drop_table('player_snapshots')
    op.drop_table('raw_payloads')
    op.drop_table('data_sources')
    op.drop_table('game_taxonomies')
    op.drop_table('taxonomy_items')
    op.drop_table('game_publishers')
    op.drop_table('game_developers')
    op.drop_table('organizations')
    op.drop_table('game_platforms')
    op.drop_table('games')
    op.drop_table('platforms')
