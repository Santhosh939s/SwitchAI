import time
import uuid
import datetime
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.usage import ProviderEvent, UsageEvent
from app.models.provider import ProviderConnection
from app.adapters.base import ProviderAdapter, ProviderResponse, NormalizedError
from app.services.providers import get_adapter, SUPPORTED_PROVIDERS, get_user_provider_connections
from app.schemas.context import ContextPackage

# Circuit Breaker state in-memory cache: provider -> failure_count
CIRCUIT_BREAKER_FAILURES: Dict[str, int] = {}
CIRCUIT_BREAKER_LAST_FAILURE: Dict[str, float] = {}

def reset_circuit_breaker():
    CIRCUIT_BREAKER_FAILURES.clear()
    CIRCUIT_BREAKER_LAST_FAILURE.clear()

FAILURE_THRESHOLD = 3
COOLDOWN_SECONDS = 30.0

def is_circuit_open(provider: str) -> bool:
    p = provider.lower()
    failures = CIRCUIT_BREAKER_FAILURES.get(p, 0)
    if failures >= FAILURE_THRESHOLD:
        last_fail = CIRCUIT_BREAKER_LAST_FAILURE.get(p, 0)
        if time.time() - last_fail < COOLDOWN_SECONDS:
            return True
        else:
            # Cooldown expired, half-open
            CIRCUIT_BREAKER_FAILURES[p] = 0
            return False
    return False

def record_provider_failure(db: Session, provider: str, status_code: Optional[int], error_type: str, latency_ms: float):
    p = provider.lower()
    CIRCUIT_BREAKER_FAILURES[p] = CIRCUIT_BREAKER_FAILURES.get(p, 0) + 1
    CIRCUIT_BREAKER_LAST_FAILURE[p] = time.time()

    event = ProviderEvent(
        id=str(uuid.uuid4()),
        provider=p,
        status_code=status_code,
        error_type=error_type,
        latency_ms=latency_ms
    )
    db.add(event)
    db.commit()

def record_provider_success(db: Session, provider: str):
    p = provider.lower()
    CIRCUIT_BREAKER_FAILURES[p] = 0

def get_fallback_chain(primary_provider: str, db: Session, user_id: str) -> List[str]:
    primary = primary_provider.lower()
    conns = get_user_provider_connections(db, user_id)

    connected = []
    for p in SUPPORTED_PROVIDERS:
        if is_circuit_open(p):
            continue
        if p == "local":
            # Only include local AI in active fallback chain if local server health check passes
            local_adapter = get_adapter("local")
            if local_adapter.get_health("").is_healthy:
                connected.append("local")
        elif p in conns and conns[p].status in ("CREDENTIALS_SAVED", "HEALTHY"):
            connected.append(p)

    if primary in connected:
        chain = [primary] + [p for p in connected if p != primary]
    elif connected:
        chain = connected
    else:
        chain = [primary] + [p for p in SUPPORTED_PROVIDERS if p != primary]

    return chain

def execute_with_fallback(
    db: Session,
    user_id: str,
    primary_provider: str,
    context_package: ContextPackage,
    model: Optional[str] = None,
    max_retries: int = 2
) -> Tuple[ProviderResponse, bool, Optional[str], Optional[str]]:
    """
    Executes request using primary provider with fallback chain.
    Returns: (ProviderResponse, is_fallback_occurred, fallback_reason, original_provider)
    """
    chain = get_fallback_chain(primary_provider, db, user_id)
    conns = get_user_provider_connections(db, user_id)

    fallback_reason = None
    original_provider = primary_provider.lower()
    is_fallback = False
    last_error_detail = "No providers available."

    for idx, provider_name in enumerate(chain):
        adapter = get_adapter(provider_name)
        conn = conns.get(provider_name)
        api_key = ""
        if conn and conn.encrypted_api_key:
            from app.core.security import decrypt_key
            try:
                api_key = decrypt_key(conn.encrypted_api_key)
            except Exception:
                api_key = ""

        # Determine the correct model for this provider in the fallback chain
        valid_models = adapter.list_models()
        if idx == 0:
            current_model = model if (model and model in valid_models) else valid_models[0]
        else:
            current_model = conn.default_model if (conn and conn.default_model and conn.default_model in valid_models) else valid_models[0]

        # Attempt bounded retry for retryable errors
        for attempt in range(max_retries):
            start_time = time.time()
            try:
                response = adapter.generate(context_package=context_package, api_key=api_key, model=current_model)
                record_provider_success(db, provider_name)

                if idx > 0:
                    is_fallback = True

                return response, is_fallback, fallback_reason, original_provider

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                normalized = adapter.normalize_error(e)
                last_error_detail = f"{provider_name.upper()} failed: {normalized.message}"

                record_provider_failure(db, provider_name, status_code=429 if normalized.code == "RATE_LIMIT" else 500, error_type=normalized.code, latency_ms=latency_ms)

                # Non-retryable errors (e.g. AUTHENTICATION_ERROR, BAD_REQUEST) break retry loop and fallback to next provider
                if not normalized.is_retryable and normalized.code != "RATE_LIMIT":
                    break

                # Rate limits, timeouts, service unavailable trigger fallback
                fallback_reason = f"{normalized.code}: {normalized.message}"

                # Bounded exponential backoff before retry
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (2 ** attempt))

    raise RuntimeError(f"All available providers failed. Last error: {last_error_detail}")
