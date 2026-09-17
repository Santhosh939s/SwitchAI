import pytest
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
    reg_payload = {"email": "usage_test@example.com", "password": "TestPassword123"}
    resp = client.post("/api/auth/register", json=reg_payload)
    if resp.status_code == 201:
        token = resp.json()["access_token"]
    else:
        resp = client.post("/api/auth/login", json=reg_payload)
        token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_usage_dashboard_aggregation(auth_headers):
    # 1. Dispatch messages to generate telemetry usage events
    resp = client.post("/api/conversations", json={"title": "Telemetry Test"}, headers=auth_headers)
    conv_id = resp.json()["id"]

    client.post(f"/api/conversations/{conv_id}/messages", json={"content": "Msg 1", "provider": "anthropic"}, headers=auth_headers)
    client.post(f"/api/conversations/{conv_id}/messages", json={"content": "Msg 2", "provider": "gemini"}, headers=auth_headers)

    # 2. Query GET /api/usage
    resp = client.get("/api/usage", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["tracked_by"] == "SwitchAI Internal Telemetry"
    assert data["total_requests"] >= 2
    assert len(data["providers"]) == 8
