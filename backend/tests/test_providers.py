import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app as fastapi_app
from app.core.database import get_db
from app.db.base import Base

# Setup test in-memory SQLite database using StaticPool
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)
fastapi_app.dependency_overrides[get_db] = override_get_db

client = TestClient(fastapi_app)

@pytest.fixture
def auth_headers():
    reg_payload = {"email": "provider_test@example.com", "password": "TestPassword123"}
    resp = client.post("/api/auth/register", json=reg_payload)
    if resp.status_code == 201:
        token = resp.json()["access_token"]
    else:
        resp = client.post("/api/auth/login", json=reg_payload)
        token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_providers_initial_status(auth_headers):
    resp = client.get("/api/providers", headers=auth_headers)
    assert resp.status_code == 200
    providers = resp.json()
    assert len(providers) == 8
    provider_names = [p["provider"] for p in providers]
    assert "anthropic" in provider_names
    assert "gemini" in provider_names
    assert "openai" in provider_names
    assert "deepseek" in provider_names
    for p in providers:
        assert p["status"] == "NOT_CONNECTED"
        assert p["is_connected"] is False
        assert p["is_healthy"] is False

@patch("app.adapters.anthropic.AnthropicAdapter.validate_credentials", return_value=True)
@patch("app.adapters.anthropic.AnthropicAdapter.discover_models", return_value=["claude-3-5-sonnet-20241022"])
@patch("app.adapters.anthropic.AnthropicAdapter.get_health")
def test_connect_and_test_anthropic_provider(mock_get_health, mock_discover, mock_validate, auth_headers):
    from app.adapters.base import ProviderHealth
    mock_get_health.return_value = ProviderHealth(
        provider="anthropic",
        is_healthy=True,
        status_message="Operational Mock",
        latency_ms=88.5,
        discovered_models=["claude-3-5-sonnet-20241022"]
    )

    # 1. Connect (Marks CREDENTIALS_SAVED)
    payload = {"api_key": "sk-ant-testkey123456789"}
    resp = client.post("/api/providers/anthropic/connect", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "anthropic"
    assert data["status"] == "CREDENTIALS_SAVED"
    assert data["is_connected"] is True
    assert data["is_healthy"] is False
    assert "api_key" not in data

    # 2. Test Connection (Marks HEALTHY)
    resp = client.post("/api/providers/anthropic/test", headers=auth_headers)
    assert resp.status_code == 200
    test_data = resp.json()
    assert test_data["provider"] == "anthropic"
    assert test_data["is_successful"] is True
    assert test_data["status"] == "HEALTHY"
    assert test_data["latency_ms"] == 88.5

    # Verify status reflects HEALTHY
    resp = client.get("/api/providers", headers=auth_headers)
    ant = next(p for p in resp.json() if p["provider"] == "anthropic")
    assert ant["status"] == "HEALTHY"
    assert ant["is_healthy"] is True

    # 3. Disconnect
    resp = client.delete("/api/providers/anthropic", headers=auth_headers)
    assert resp.status_code == 200
    assert "Successfully disconnected" in resp.json()["message"]

    # 4. Verify disconnected status
    resp = client.get("/api/providers", headers=auth_headers)
    ant = next(p for p in resp.json() if p["provider"] == "anthropic")
    assert ant["status"] == "NOT_CONNECTED"
    assert ant["is_connected"] is False

@patch("app.adapters.openai.OpenAIAdapter.validate_credentials", return_value=False)
def test_connect_invalid_credentials_fails(mock_validate, auth_headers):
    payload = {"api_key": "invalid-key"}
    resp = client.post("/api/providers/openai/connect", json=payload, headers=auth_headers)
    assert resp.status_code == 400
    assert "Credential validation failed" in resp.json()["detail"]
