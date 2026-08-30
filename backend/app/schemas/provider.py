import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

class ProviderConnectRequest(BaseModel):
    api_key: str = Field(..., min_length=1, description="Provider API key")
    default_model: Optional[str] = None

class ProviderStatusResponse(BaseModel):
    provider: str
    status: str  # NOT_CONNECTED, CREDENTIALS_SAVED, HEALTHY, UNHEALTHY
    is_connected: bool  # True if status in (CREDENTIALS_SAVED, HEALTHY)
    is_healthy: bool    # True ONLY if status == HEALTHY
    default_model: Optional[str] = None
    available_models: List[str] = []
    last_successful_test: Optional[datetime.datetime] = None
    last_error: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

class ProviderTestResponse(BaseModel):
    provider: str
    is_successful: bool
    status: str  # HEALTHY or UNHEALTHY
    latency_ms: Optional[float] = None
    message: str
    validated_models: List[str] = []
    tested_at: datetime.datetime
