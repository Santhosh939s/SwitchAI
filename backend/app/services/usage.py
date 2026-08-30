from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.usage import UsageEvent, ProviderEvent
from app.services.providers import SUPPORTED_PROVIDERS
from app.schemas.usage import ProviderUsageMetrics, UsageDashboardResponse

def get_usage_metrics(db: Session, user_id: str) -> UsageDashboardResponse:
    events = db.query(UsageEvent).filter(UsageEvent.user_id == user_id).all()
    prov_events = db.query(ProviderEvent).all()

    provider_metrics: List[ProviderUsageMetrics] = []
    tot_requests = len(events)
    tot_fallbacks = sum(1 for e in events if e.is_fallback)
    tot_latencies = [e.latency_ms for e in events if e.latency_ms]
    avg_sys_latency = (sum(tot_latencies) / len(tot_latencies)) if tot_latencies else 0.0

    for p in SUPPORTED_PROVIDERS:
        p_events = [e for e in events if e.provider.lower() == p]
        p_prov_events = [pe for pe in prov_events if pe.provider.lower() == p]

        p_reqs = len(p_events)
        p_success = sum(1 for e in p_events if e.is_success)
        p_failed = p_reqs - p_success
        p_rl = sum(1 for pe in p_prov_events if pe.error_type == "RATE_LIMIT") + sum(1 for e in p_events if e.error_code and "RATE_LIMIT" in str(e.error_code))
        p_fallbacks = sum(1 for e in p_events if e.is_fallback)
        p_latencies = [e.latency_ms for e in p_events if e.latency_ms]
        p_avg_lat = (sum(p_latencies) / len(p_latencies)) if p_latencies else 0.0
        p_tokens = sum(e.estimated_tokens or 0 for e in p_events)

        provider_metrics.append(ProviderUsageMetrics(
            provider=p,
            total_requests=p_reqs,
            successful_requests=p_success,
            failed_requests=p_failed,
            rate_limit_events=p_rl,
            fallback_count=p_fallbacks,
            avg_latency_ms=round(p_avg_lat, 1),
            total_estimated_tokens=p_tokens
        ))

    return UsageDashboardResponse(
        tracked_by="SwitchAI Internal Telemetry",
        total_requests=tot_requests,
        total_fallbacks=tot_fallbacks,
        avg_system_latency_ms=round(avg_sys_latency, 1),
        providers=provider_metrics
    )
