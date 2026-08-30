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
    reg_payload = {"email": "rag_test@example.com", "password": "TestPassword123"}
    resp = client.post("/api/auth/register", json=reg_payload)
    if resp.status_code == 201:
        token = resp.json()["access_token"]
    else:
        resp = client.post("/api/auth/login", json=reg_payload)
        token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@patch("app.services.conversations.execute_with_fallback", side_effect=RuntimeError("All cloud APIs exhausted"))
def test_rag_fallback_engine_response(mock_fallback, auth_headers):
    # 1. Create conversation
    resp = client.post("/api/conversations", json={"title": "RAG Test"}, headers=auth_headers)
    assert resp.status_code == 201
    conv_id = resp.json()["id"]

    # 2. Add shared memory item
    mem_goal = {"category": "goal", "key": "Target Goal", "value": "Build RAG Architecture", "is_pinned": True}
    client.post(f"/api/conversations/{conv_id}/memory", json=mem_goal, headers=auth_headers)

    # 3. Send message while all cloud APIs are failing
    resp = client.post(f"/api/conversations/{conv_id}/messages", json={"content": "Suggest payment architecture", "provider": "gemini"}, headers=auth_headers)
    assert resp.status_code == 200
    m = resp.json()
    assert m["provider"] == "rag_engine"
    assert "RAG Engine" in m["content"]
    assert "Build RAG Architecture" in m["content"]
