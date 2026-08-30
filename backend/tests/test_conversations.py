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
    reg_payload = {"email": "persistence_audit@example.com", "password": "TestPassword123"}
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

def test_conversation_persistence_reload_search_and_provider_switch(auth_headers):
    # 1. Create conversation
    resp = client.post("/api/conversations", json={"title": "New Conversation"}, headers=auth_headers)
    assert resp.status_code == 201
    conv = resp.json()
    conv_id = conv["id"]
    assert conv["title"] == "New Conversation"

    # 2. Persist first message (auto-generates title)
    msg1 = {"content": "Design payment architecture for food app", "provider": "anthropic"}
    resp = client.post(f"/api/conversations/{conv_id}/messages", json=msg1, headers=auth_headers)
    assert resp.status_code == 200
    m1 = resp.json()
    assert m1["conversation_id"] == conv_id
    assert m1["provider"] == "anthropic"

    # Verify auto-generated title
    resp = client.get(f"/api/conversations/{conv_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert "Design payment architecture" in resp.json()["title"]

    # 3. Rename conversation
    resp = client.patch(f"/api/conversations/{conv_id}", json={"title": "Custom Payment Title"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Custom Payment Title"

    # 4. Search conversation
    resp = client.get("/api/conversations?q=Custom", headers=auth_headers)
    assert resp.status_code == 200
    search_results = resp.json()
    assert len(search_results) == 1
    assert search_results[0]["id"] == conv_id

    # Search non-matching term
    resp = client.get("/api/conversations?q=NonExistentTerm", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 0

    # 5. Reload conversation and restore full message history
    resp = client.get(f"/api/conversations/{conv_id}/messages", headers=auth_headers)
    assert resp.status_code == 200
    reloaded_msgs = resp.json()
    assert len(reloaded_msgs) == 2 # 1 user + 1 assistant

    # 6. Provider switch preserves SAME conversation ID
    msg2 = {"content": "Challenge architecture weaknesses", "provider": "gemini"}
    resp = client.post(f"/api/conversations/{conv_id}/messages", json=msg2, headers=auth_headers)
    assert resp.status_code == 200
    m2 = resp.json()
    assert m2["conversation_id"] == conv_id
    assert m2["provider"] == "gemini"

    # 7. Fallback preserves SAME conversation ID
    with patch("app.adapters.openai.OpenAIAdapter.generate", side_effect=Exception("429 Too Many Requests")):
        msg3 = {"content": "Generate spec", "provider": "openai"}
        resp = client.post(f"/api/conversations/{conv_id}/messages", json=msg3, headers=auth_headers)
        assert resp.status_code == 200
        m3 = resp.json()
        assert m3["conversation_id"] == conv_id
        assert m3["provider"] in ("gemini", "anthropic")

    # 8. Unavailable model is detected and triggers fallback
    with patch("app.adapters.gemini.GeminiAdapter.generate", side_effect=ValueError("Selected Gemini model 'gemini-1.5-pro' is unavailable or not supported for v1beta API.")):
        msg4 = {"content": "Test unavailable model", "provider": "gemini", "model": "gemini-1.5-pro"}
        resp = client.post(f"/api/conversations/{conv_id}/messages", json=msg4, headers=auth_headers)
        assert resp.status_code == 200
        assert "Provider Switched" in resp.json()["content"]

    # 9. Stale Database Model Regression Test: Sending None uses sanitized default instead of stale DB value
    # Explicitly set the active model in DB to an invalid stale one
    client.patch(f"/api/conversations/{conv_id}", json={"active_model": "gemini-1.0-stale-deprecated"}, headers=auth_headers)
    
    # Send message with model=None. The backend should reject the stale active_model and auto-correct to valid models[0]
    msg5 = {"content": "Test stale DB model", "provider": "gemini", "model": None}
    resp = client.post(f"/api/conversations/{conv_id}/messages", json=msg5, headers=auth_headers)
    assert resp.status_code == 200
    m5 = resp.json()
    assert m5["model"] != "gemini-1.0-stale-deprecated"
    assert "gemini" in m5["model"] # Should be gemini-3.5-flash or whatever is valid

    # 10. Delete conversation
    resp = client.delete(f"/api/conversations/{conv_id}", headers=auth_headers)
    assert resp.status_code == 200

    # Verify deleted
    resp = client.get(f"/api/conversations/{conv_id}", headers=auth_headers)
    assert resp.status_code == 404
