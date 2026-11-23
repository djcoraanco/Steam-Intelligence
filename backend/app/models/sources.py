import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, CHAR
from app.core.database import Base, GUID, UniversalJSON


def now_utc():
    return datetime.now(timezone.utc)


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    code = Column(String(60), unique=True, nullable=False, index=True)
    name = Column(Text, nullable=False)
    provider_type = Column(String(30), nullable=False)  # official_public, official_partner, third_party_public, etc.
    base_url = Column(Text, nullable=True)
    documentation_url = Column(Text, nullable=True)
    terms_url = Column(Text, nullable=True)
    status = Column(String(20), default="active")  # active, planned, unavailable, deprecated, disabled
    capabilities = Column(UniversalJSON, default=list)  # list of strings: ["catalog", "metadata", ...]
    rate_limit_config = Column(UniversalJSON, default=dict)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)


class RawPayload(Base):
    __tablename__ = "raw_payloads"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    source_id = Column(GUID, ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True, index=True)
    request_fingerprint = Column(Text, nullable=True, index=True)
    http_status = Column(Integer, nullable=True)
    content_type = Column(Text, nullable=True)
    payload = Column(UniversalJSON, nullable=False)
    payload_hash = Column(CHAR(64), nullable=True, index=True)
    fetched_at = Column(DateTime(timezone=True), default=now_utc)
    parser_version = Column(Text, default="1.0.0")
    retention_until = Column(DateTime(timezone=True), nullable=True)
