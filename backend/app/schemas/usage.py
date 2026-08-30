from pydantic import BaseModel
from typing import List, Dict, Optional

class ProviderUsageMetrics(BaseModel):
    provider: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    rate_limit_events: int
    fallback_count: int
    avg_latency_ms: float
    total_estimated_tokens: int

class UsageDashboardResponse(BaseModel):
    tracked_by: str = "SwitchAI Internal Telemetry"
    total_requests: int
    total_fallbacks: int
    avg_system_latency_ms: float
    providers: List[ProviderUsageMetrics]
