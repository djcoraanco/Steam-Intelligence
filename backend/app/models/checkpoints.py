import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, BigInteger, DateTime
from app.core.database import Base, GUID


def now_utc():
    return datetime.now(timezone.utc)


class IngestionCheckpoint(Base):
    __tablename__ = "ingestion_checkpoints"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    provider_code = Column(String(40), nullable=False, index=True)
    entity_type = Column(String(40), nullable=False, default="catalog")  # catalog, metadata, reviews
    last_cursor = Column(Text, nullable=True)  # e.g. last_appid
    last_modified = Column(BigInteger, nullable=True)  # timestamp if supported
    total_records = Column(Integer, default=0)
    status = Column(String(20), default="idle")  # idle, running, completed, failed
    last_synced_at = Column(DateTime(timezone=True), default=now_utc)
    error_message = Column(Text, nullable=True)
