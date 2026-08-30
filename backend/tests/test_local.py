import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app as fastapi_app
from app.core.database import get_db
from app.db.base import Base
from app.adapters.local import LocalAdapter
from app.schemas.context import ContextPackage

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
    reg_payload = {"email": "local_test@example.com", "password": "TestPassword123"}
    resp = client.post("/api/auth/register", json=reg_payload)
    if resp.status_code == 201:
        token = resp.json()["access_token"]
    else:
        resp = client.post("/api/auth/login", json=reg_payload)
        token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_local_adapter_offline_handling():
    adapter = LocalAdapter()
    # Server offline at default endpoint
    health = adapter.get_health("")
    assert health.is_healthy is False
    assert "NOT_RUNNING" in health.status_message

    # Generate when server is offline raises RuntimeError
    pkg = ContextPackage(conversation_id="local_conv", current_message="hi")
    with pytest.raises(RuntimeError) as exc_info:
        adapter.generate(pkg, api_key="")
    assert "Local AI is offline" in str(exc_info.value)

@patch("httpx.Client.get")
def test_local_adapter_model_discovery(mock_get):
    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = {
        "data": [
            {"id": "Qwen2.5-1.5B-Instruct-Q4_K_M"},
            {"id": "Llama-3.2-1B-Instruct"}
        ]
    }
    mock_get.return_value = mock_res

    adapter = LocalAdapter()
    models = adapter.discover_models("")
    assert len(models) == 2
    assert models[0] == "Qwen2.5-1.5B-Instruct-Q4_K_M"

@patch("httpx.Client.post")
@patch("httpx.Client.get")
def test_local_adapter_generate_success(mock_get, mock_post):
    mock_get_res = MagicMock()
    mock_get_res.status_code = 200
    mock_get_res.json.return_value = {"data": [{"id": "Qwen2.5-1.5B-Instruct-Q4_K_M"}]}
    mock_get.return_value = mock_get_res

    mock_post_res = MagicMock()
    mock_post_res.status_code = 200
    mock_post_res.json.return_value = {
        "choices": [{"message": {"content": "Hello from local Qwen model!"}}],
        "usage": {"total_tokens": 42}
    }
    mock_post.return_value = mock_post_res

    adapter = LocalAdapter()
    pkg = ContextPackage(
        conversation_id="conv_local_1",
        user_goal="Test Local AI",
        current_message="Hello local model"
    )
    res = adapter.generate(pkg, api_key="")
    assert res.provider == "local"
    assert res.model == "Qwen2.5-1.5B-Instruct-Q4_K_M"
    assert res.content == "Hello from local Qwen model!"
    assert res.estimated_tokens == 42

def test_local_provider_in_settings_and_fallback(auth_headers):
    # 1. Check provider statuses
    resp = client.get("/api/providers", headers=auth_headers)
    assert resp.status_code == 200
    providers = resp.json()
    assert len(providers) == 8 # 7 cloud + 1 local
    local_p = next(p for p in providers if p["provider"] == "local")
    assert local_p["is_connected"] is True
