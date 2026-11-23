"""add ingestion checkpoints

Revision ID: 002_ingestion_checkpoints
Revises: 001_initial_schema
Create Date: 2026-11-23 13:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_ingestion_checkpoints'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ingestion_checkpoints',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('provider_code', sa.String(40), nullable=False),
        sa.Column('entity_type', sa.String(40), nullable=False),
        sa.Column('last_cursor', sa.Text(), nullable=True),
        sa.Column('last_modified', sa.BigInteger(), nullable=True),
        sa.Column('total_records', sa.Integer(), nullable=True, default=0),
        sa.Column('status', sa.String(20), nullable=True, default='idle'),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True)
    )
    op.create_index('ix_ingestion_checkpoints_provider_code', 'ingestion_checkpoints', ['provider_code'])


def downgrade() -> None:
    op.drop_index('ix_ingestion_checkpoints_provider_code', table_name='ingestion_checkpoints')
    op.drop_table('ingestion_checkpoints')
