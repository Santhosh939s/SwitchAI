import uuid
import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.provider import ProviderConnection
from app.core.security import encrypt_key, decrypt_key
from app.adapters.anthropic import AnthropicAdapter
from app.adapters.gemini import GeminiAdapter
from app.adapters.openai import OpenAIAdapter
from app.adapters.deepseek import DeepSeekAdapter
from app.adapters.groq import GroqAdapter
from app.adapters.mistral import MistralAdapter
from app.adapters.cohere import CohereAdapter
from app.adapters.local import LocalAdapter
from app.schemas.provider import ProviderStatusResponse, ProviderTestResponse

ADAPTERS = {
    "anthropic": AnthropicAdapter(),
    "gemini": GeminiAdapter(),
    "openai": OpenAIAdapter(),
    "deepseek": DeepSeekAdapter(),
    "groq": GroqAdapter(),
    "mistral": MistralAdapter(),
    "cohere": CohereAdapter(),
    "local": LocalAdapter(),
}

SUPPORTED_PROVIDERS = ["gemini", "openai", "anthropic", "deepseek", "groq", "mistral", "cohere", "local"]

def get_adapter(provider: str):
    p = provider.lower()
    if p not in ADAPTERS:
        raise ValueError(f"Unsupported provider: {provider}")
    return ADAPTERS[p]

def get_user_provider_connections(db: Session, user_id: str) -> Dict[str, ProviderConnection]:
    conns = db.query(ProviderConnection).filter(ProviderConnection.user_id == user_id).all()
    return {c.provider_name.lower(): c for c in conns}

def list_provider_statuses(db: Session, user_id: str) -> List[ProviderStatusResponse]:
    conns = get_user_provider_connections(db, user_id)
    results = []

    for provider in SUPPORTED_PROVIDERS:
        conn = conns.get(provider)
        adapter = ADAPTERS[provider]

        if provider == "local":
            health = adapter.get_health("")
            status_str = "HEALTHY" if health.is_healthy else ("RUNNING" if health.discovered_models else "NOT_RUNNING")
            discovered_models = health.discovered_models or adapter.list_models()
            results.append(ProviderStatusResponse(
                provider=provider,
                status=status_str,
                is_connected=True, # Local AI is natively available
                is_healthy=health.is_healthy,
                default_model=discovered_models[0],
                available_models=discovered_models,
                updated_at=datetime.datetime.utcnow()
            ))
        elif not conn:
            results.append(ProviderStatusResponse(
                provider=provider,
                status="NOT_CONNECTED",
                is_connected=False,
                is_healthy=False,
                available_models=adapter.list_models()
            ))
        else:
            raw_key = ""
            try:
                raw_key = decrypt_key(conn.encrypted_api_key)
            except Exception:
                pass

            discovered_models = adapter.discover_models(raw_key) if raw_key else adapter.list_models()
            current_status = conn.status if conn.status in ("CREDENTIALS_SAVED", "HEALTHY", "UNHEALTHY") else "CREDENTIALS_SAVED"
            is_healthy = (current_status == "HEALTHY")

            results.append(ProviderStatusResponse(
                provider=provider,
                status=current_status,
                is_connected=True,
                is_healthy=is_healthy,
                default_model=conn.default_model or discovered_models[0],
                available_models=discovered_models,
                updated_at=conn.updated_at
            ))

    return results

def connect_provider(db: Session, user_id: str, provider: str, api_key: str, default_model: Optional[str] = None) -> ProviderStatusResponse:
    p = provider.lower()
    if p not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported provider '{provider}'. Must be one of {SUPPORTED_PROVIDERS}")

    adapter = get_adapter(p)
    is_valid = adapter.validate_credentials(api_key)
    if not is_valid:
        raise ValueError(f"Credential validation failed for provider '{p}'. Please verify your API key.")

    encrypted = encrypt_key(api_key)
    conns = get_user_provider_connections(db, user_id)
    existing = conns.get(p)

    discovered_models = adapter.discover_models(api_key)
    selected_model = default_model if (default_model and default_model in discovered_models) else discovered_models[0]

    # Connect marks as CREDENTIALS_SAVED. Health test verifies HEALTHY.
    if existing:
        existing.encrypted_api_key = encrypted
        existing.status = "CREDENTIALS_SAVED"
        existing.default_model = selected_model
        existing.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(existing)
        conn = existing
    else:
        conn = ProviderConnection(
            id=str(uuid.uuid4()),
            user_id=user_id,
            provider_name=p,
            encrypted_api_key=encrypted,
            status="CREDENTIALS_SAVED",
            default_model=selected_model,
        )
        db.add(conn)
        db.commit()
        db.refresh(conn)

    return ProviderStatusResponse(
        provider=p,
        status="CREDENTIALS_SAVED",
        is_connected=True,
        is_healthy=False,
        default_model=conn.default_model,
        available_models=discovered_models,
        updated_at=conn.updated_at
    )

def test_provider_connection(db: Session, user_id: str, provider: str) -> ProviderTestResponse:
    p = provider.lower()
    if p not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported provider '{provider}'")

    conns = get_user_provider_connections(db, user_id)
    conn = conns.get(p)

    if not conn:
        return ProviderTestResponse(
            provider=p,
            is_successful=False,
            status="NOT_CONNECTED",
            message=f"Provider '{p}' is not connected.",
            tested_at=datetime.datetime.utcnow()
        )

    try:
        raw_key = decrypt_key(conn.encrypted_api_key)
        adapter = get_adapter(p)
        health = adapter.get_health(raw_key)

        if health.is_healthy:
            conn.status = "HEALTHY"
            conn.updated_at = datetime.datetime.utcnow()
            db.commit()
            return ProviderTestResponse(
                provider=p,
                is_successful=True,
                status="HEALTHY",
                latency_ms=health.latency_ms,
                message=health.status_message,
                validated_models=health.discovered_models,
                tested_at=datetime.datetime.utcnow()
            )
        else:
            conn.status = "UNHEALTHY"
            conn.updated_at = datetime.datetime.utcnow()
            db.commit()
            return ProviderTestResponse(
                provider=p,
                is_successful=False,
                status="UNHEALTHY",
                message=health.status_message,
                validated_models=adapter.list_models(),
                tested_at=datetime.datetime.utcnow()
            )
    except Exception as e:
        conn.status = "UNHEALTHY"
        conn.updated_at = datetime.datetime.utcnow()
        db.commit()
        return ProviderTestResponse(
            provider=p,
            is_successful=False,
            status="UNHEALTHY",
            message=f"Connection test error: {str(e)}",
            tested_at=datetime.datetime.utcnow()
        )

def disconnect_provider(db: Session, user_id: str, provider: str) -> bool:
    p = provider.lower()
    conns = get_user_provider_connections(db, user_id)
    conn = conns.get(p)
    if not conn:
        return False
    db.delete(conn)
    db.commit()
    return True
