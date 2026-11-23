import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, DateTime, Numeric,
    ForeignKey
)
from app.core.database import Base, GUID, UniversalJSON


def now_utc():
    return datetime.now(timezone.utc)


class TrendSignal(Base):
    __tablename__ = "trend_signals"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(30), nullable=False)  # genre, tag, game
    entity_id = Column(GUID, nullable=True, index=True)
    metric_name = Column(String(60), nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    current_value = Column(Numeric, nullable=False)
    baseline_value = Column(Numeric, nullable=True)
    change_percent = Column(Numeric, nullable=True)
    z_score = Column(Numeric, nullable=True)
    trend_direction = Column(String(20), default="flat")  # rising, declining, flat
    confidence_score = Column(Numeric(5, 2), default=0.0)
    evidence = Column(UniversalJSON, default=dict)
    algorithm_version = Column(String(32), default="trend-v1")
    created_at = Column(DateTime(timezone=True), default=now_utc)


class NicheOpportunity(Base):
    __tablename__ = "niche_opportunities"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    segment_definition = Column(UniversalJSON, nullable=False)
    demand_score = Column(Numeric(5, 2), default=0.0)
    growth_score = Column(Numeric(5, 2), default=0.0)
    competitive_space_score = Column(Numeric(5, 2), default=0.0)
    commercial_feasibility_score = Column(Numeric(5, 2), default=0.0)
    evidence_quality_score = Column(Numeric(5, 2), default=0.0)
    opportunity_score = Column(Numeric(5, 2), default=0.0)
    score_version = Column(String(32), default="niche-v1")
    confidence_band = Column(String(20), default="low")  # low, medium, high
    limitations = Column(UniversalJSON, default=list)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    owner_user_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    research_type = Column(String(40), default="full_market")
    configuration = Column(UniversalJSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=now_utc)


class ResearchRun(Base):
    __tablename__ = "research_runs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID, ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=True, index=True)
    status = Column(String(20), default="queued")  # queued, running, completed, completed_with_warnings, failed, cancelled
    started_at = Column(DateTime(timezone=True), default=now_utc)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    trigger_type = Column(String(20), default="manual")  # manual, scheduled, system
    requested_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    configuration_snapshot = Column(UniversalJSON, default=dict)
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    games_processed = Column(Integer, default=0)
    report_id = Column(GUID, nullable=True)
    error_summary = Column(UniversalJSON, default=dict)


class ResearchResult(Base):
    __tablename__ = "research_results"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    research_run_id = Column(GUID, ForeignKey("research_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    result_type = Column(String(40), nullable=False)
    entity_type = Column(String(40), nullable=False)
    entity_id = Column(GUID, nullable=True)
    result_payload = Column(UniversalJSON, default=dict)
    evidence_refs = Column(UniversalJSON, default=list)
    created_at = Column(DateTime(timezone=True), default=now_utc)
