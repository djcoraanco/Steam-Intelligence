import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Date, DateTime
)
from app.core.database import Base, GUID, UniversalJSON


def now_utc():
    return datetime.now(timezone.utc)


class IndustryEvent(Base):
    """
    Industry events, Steam seasonal sales, and discovery fests.
    Used for release collision alerts and seasonal demand contextualization.
    """
    __tablename__ = "industry_events"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    code = Column(String(60), unique=True, nullable=False, index=True)
    name = Column(Text, nullable=False)
    event_type = Column(String(40), nullable=False)  # seasonal_sale, next_fest, major_convention, holiday
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    source_ref = Column(Text, nullable=False)  # official steam documentation / announcement
    description = Column(Text, nullable=True)
    historical_impact = Column(UniversalJSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=now_utc)
