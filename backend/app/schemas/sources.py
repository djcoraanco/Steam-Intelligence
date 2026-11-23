from datetime import datetime
from typing import List, Optional, Any, Dict
import uuid
from pydantic import BaseModel, ConfigDict


class DataSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    provider_type: str
    status: str
    capabilities: List[str]
    base_url: Optional[str] = None
    documentation_url: Optional[str] = None
    terms_url: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    rate_limit_config: Dict[str, Any] = {}


class DataSourceTestResult(BaseModel):
    provider_code: str
    success: bool
    status_code: Optional[int] = None
    response_time_ms: float
    message: str
    tested_at: datetime
