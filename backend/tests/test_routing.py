import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app as fastapi_app
from app.core.database import get_db
from app.db.base import Base
from app.services.routing import classify_prompt_task

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
    reg_payload = {"email": "routing_test@example.com", "password": "TestPassword123"}
    resp = client.post("/api/auth/register", json=reg_payload)
    if resp.status_code == 201:
        token = resp.json()["access_token"]
    else:
        resp = client.post("/api/auth/login", json=reg_payload)
        token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_task_classification():
    assert classify_prompt_task("Write a Python function to solve 2sum") == "coding"
    assert classify_prompt_task("Summarize this document") == "summarization"
    assert classify_prompt_task("Why is asynchronous architecture scalable?") == "reasoning"
    assert classify_prompt_task("Here is a 500 word report document analyzing quarterly financials") == "long_context"

def test_routing_preview_endpoint(auth_headers):
    # 1. Preview long context prompt -> Gemini
    payload = {"message": "Analyze this 400 page document report", "priority": "balanced"}
    resp = client.post("/api/router/preview", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["task_category"] == "long_context"
    assert data["selected_provider"] == "gemini"
    assert "long-context" in data["rationale"]

    # 2. Preview coding prompt -> OpenAI or primary
    payload = {"message": "Write an API endpoint function in FastAPI", "priority": "quality"}
    resp = client.post("/api/router/preview", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["task_category"] == "coding"

def test_auto_routing_message_dispatch(auth_headers):
    resp = client.post("/api/conversations", json={"title": "Auto Routing Test"}, headers=auth_headers)
    assert resp.status_code == 201
    conv_id = resp.json()["id"]

    # Send message with provider="auto"
    msg = {"content": "Analyze this 400 word long document report", "provider": "auto"}
    resp = client.post(f"/api/conversations/{conv_id}/messages", json=msg, headers=auth_headers)
    assert resp.status_code == 200
    res = resp.json()
    assert res["provider"] in ("gemini", "rag_engine")
    assert "Auto Routed" in res["content"] or "RAG Engine" in res["content"]
