from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel


class ComponentHealth(BaseModel):
    status: str  # healthy, degraded, unavailable
    details: Dict[str, Any] = {}


class HealthResponse(BaseModel):
    status: str  # ok, degraded, error
    version: str = "1.0.0"
    environment: str
    timestamp: datetime
    components: Dict[str, ComponentHealth]
