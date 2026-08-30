import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app as fastapi_app
from app.core.database import get_db
from app.db.base import Base
from app.services.fallback import reset_circuit_breaker

@pytest.fixture(autouse=True)
def clean_circuit_breaker():
    reset_circuit_breaker()
    yield
    reset_circuit_breaker()

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
    reg_payload = {"email": "memory_test@example.com", "password": "TestPassword123"}
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
    
    return headers

def test_shared_memory_extraction_retrieval_and_provider_passthrough(auth_headers):
    # 1. Create conversation
    resp = client.post("/api/conversations", json={"title": "Food Delivery App"}, headers=auth_headers)
    assert resp.status_code == 201
    conv_id = resp.json()["id"]

    # 2. Add manual memories (Goal, Tech Stack, Decision)
    mem_goal = {"category": "goal", "key": "Target App", "value": "College food delivery app", "is_pinned": True}
    resp = client.post(f"/api/conversations/{conv_id}/memory", json=mem_goal, headers=auth_headers)
    assert resp.status_code == 201

    mem_fact = {"category": "fact", "key": "Tech Stack", "value": "FastAPI, PostgreSQL, React", "is_pinned": False}
    resp = client.post(f"/api/conversations/{conv_id}/memory", json=mem_fact, headers=auth_headers)
    assert resp.status_code == 201

    mem_decision = {"category": "decision", "key": "Payment Processing", "value": "Async webhooks", "is_pinned": False}
    resp = client.post(f"/api/conversations/{conv_id}/memory", json=mem_decision, headers=auth_headers)
    assert resp.status_code == 201
    mem_dec_id = resp.json()["id"]

    # 3. Verify initial memories listed (3 items)
    resp = client.get(f"/api/conversations/{conv_id}/memory", headers=auth_headers)
    assert resp.status_code == 200
    initial_mems = resp.json()
    assert len(initial_mems) == 3

    # 4. Send message through Anthropic (triggers heuristic memory extraction)
    resp = client.post(f"/api/conversations/{conv_id}/messages", json={"content": "We decided to use FastAPI and PostgreSQL for building payment architecture", "provider": "anthropic"}, headers=auth_headers)
    assert resp.status_code == 200
    m1 = resp.json()
    assert "Anthropic" in m1["content"]

    # Verify that heuristic memory extraction automatically added new durable memories
    resp = client.get(f"/api/conversations/{conv_id}/memory", headers=auth_headers)
    mems_after_extract = resp.json()
    assert len(mems_after_extract) > len(initial_mems)

    # 5. Send message through Gemini with same shared memory
    resp = client.post(f"/api/conversations/{conv_id}/messages", json={"content": "Check payment security", "provider": "gemini"}, headers=auth_headers)
    assert resp.status_code == 200
    m2 = resp.json()
    assert "Gemini" in m2["content"]

    # 6. Edit memory (pin decision)
    resp = client.patch(f"/api/memory/{mem_dec_id}", json={"is_pinned": True}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["is_pinned"] is True

    # 7. Delete memory
    before_del_count = len(mems_after_extract)
    resp = client.delete(f"/api/memory/{mem_dec_id}", headers=auth_headers)
    assert resp.status_code == 200

    # Verify count decremented by 1
    resp = client.get(f"/api/conversations/{conv_id}/memory", headers=auth_headers)
    assert len(resp.json()) == before_del_count - 1
