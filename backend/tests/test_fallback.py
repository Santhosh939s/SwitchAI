import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app as fastapi_app
from app.core.database import get_db
from app.db.base import Base
from app.services.fallback import reset_circuit_breaker

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

@pytest.fixture(autouse=True)
def clean_circuit_breaker():
    reset_circuit_breaker()
    yield
    reset_circuit_breaker()

@pytest.fixture
def auth_headers():
    reg_payload = {"email": "fallback_test@example.com", "password": "TestPassword123"}
    resp = client.post("/api/auth/register", json=reg_payload)
    if resp.status_code == 201:
        token = resp.json()["access_token"]
    else:
        resp = client.post("/api/auth/login", json=reg_payload)
        token = resp.json()["access_token"]
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Inject mock provider connections so they don't fail the 'missing API key' validation
    client.post("/api/providers/anthropic/connect", json={"api_key": "mock_ant_key"}, headers=headers)
    client.post("/api/providers/gemini/connect", json={"api_key": "mock_gemini_key_123"}, headers=headers)
    client.post("/api/providers/openai/connect", json={"api_key": "mock_openai_sk_key"}, headers=headers)
    
    return headers

@patch("app.adapters.anthropic.AnthropicAdapter.generate", side_effect=Exception("429 Too Many Requests: Rate limit exceeded"))
def test_rate_limit_fallback_to_secondary_provider(mock_ant, auth_headers):
    resp = client.post("/api/conversations", json={"title": "Fallback Test"}, headers=auth_headers)
    assert resp.status_code == 201
    conv_id = resp.json()["id"]

    resp = client.post(f"/api/conversations/{conv_id}/messages", json={"content": "Hello", "provider": "anthropic"}, headers=auth_headers)
    assert resp.status_code == 200
    msg = resp.json()
    assert msg["sender_role"] == "assistant"
    assert msg["provider"] == "gemini"
    assert "Provider Switched" in msg["content"]
    assert "RATE_LIMIT" in msg["content"]

@patch("app.adapters.anthropic.AnthropicAdapter.generate", side_effect=Exception("504 Gateway Timeout"))
def test_timeout_fallback_to_secondary_provider(mock_ant, auth_headers):
    resp = client.post("/api/conversations", json={"title": "Timeout Test"}, headers=auth_headers)
    conv_id = resp.json()["id"]

    resp = client.post(f"/api/conversations/{conv_id}/messages", json={"content": "Check timeout", "provider": "anthropic"}, headers=auth_headers)
    assert resp.status_code == 200
    msg = resp.json()
    assert msg["provider"] == "gemini"
    assert "Provider Switched" in msg["content"]

@patch("app.adapters.anthropic.AnthropicAdapter.generate", side_effect=Exception("401 Unauthorized API key"))
def test_auth_error_triggers_fallback(mock_ant, auth_headers):
    resp = client.post("/api/conversations", json={"title": "Auth Error Test"}, headers=auth_headers)
    conv_id = resp.json()["id"]

    resp = client.post(f"/api/conversations/{conv_id}/messages", json={"content": "Check auth error", "provider": "anthropic"}, headers=auth_headers)
    assert resp.status_code == 200
    msg = resp.json()
    assert "Provider Switched" in msg["content"]
    assert "gemini" in msg["provider"] or "openai" in msg["provider"]

@patch("app.adapters.anthropic.AnthropicAdapter.generate", side_effect=Exception("429 Rate limit"))
@patch("app.adapters.gemini.GeminiAdapter.generate", side_effect=Exception("429 Quota exceeded"))
@patch("app.adapters.openai.OpenAIAdapter.generate", side_effect=Exception("429 Rate limit"))
@patch("app.adapters.deepseek.DeepSeekAdapter.generate", side_effect=Exception("429 Rate limit"))
@patch("app.adapters.groq.GroqAdapter.generate", side_effect=Exception("429 Rate limit"))
@patch("app.adapters.mistral.MistralAdapter.generate", side_effect=Exception("429 Rate limit"))
@patch("app.adapters.cohere.CohereAdapter.generate", side_effect=Exception("429 Rate limit"))
@patch("app.adapters.local.LocalAdapter.generate", side_effect=Exception("Local AI server offline"))
def test_all_providers_failing_graceful_error(m8, m7, m6, m5, m4, m3, m2, m1, auth_headers):
    resp = client.post("/api/conversations", json={"title": "All Fail Test"}, headers=auth_headers)
    conv_id = resp.json()["id"]

    resp = client.post(f"/api/conversations/{conv_id}/messages", json={"content": "Check all fail", "provider": "anthropic"}, headers=auth_headers)
    assert resp.status_code == 200
    msg = resp.json()
    assert "Error" in msg["content"]
