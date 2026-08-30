import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from jose import jwt
from app.main import app as fastapi_app
from app.core.database import get_db
from app.db.base import Base
from app.core.config import settings

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

def test_unauthenticated_protected_endpoint():
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
    assert "credentials were not provided" in resp.json()["detail"]

def test_invalid_token_handling():
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token_xyz"})
    assert resp.status_code == 401
    assert "Invalid or expired" in resp.json()["detail"]

def test_expired_jwt_handling():
    # Construct expired token manually using current secret
    expired_payload = {
        "sub": "some_user_id",
        "email": "expired@example.com",
        "exp": datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
    }
    expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401
    assert "Invalid or expired" in resp.json()["detail"]

def test_user_registration_and_login_flow():
    # 0. Login with non-existent user email -> 401
    resp = client.post("/api/auth/login", json={"email": "nonexistent@example.com", "password": "somepassword123"})
    assert resp.status_code == 401
    assert "No account found with this email address" in resp.json()["detail"]

    reg_payload = {"email": "verifier@example.com", "password": "VerificationPassword123"}
    
    # 1. Signup
    resp = client.post("/api/auth/register", json=reg_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "verifier@example.com"
    token = data["access_token"]

    # Verify security: no plaintext password or hash in output
    assert "password_hash" not in data["user"]
    assert "password" not in data["user"]

    # 2. Duplicate signup
    resp = client.post("/api/auth/register", json=reg_payload)
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"]

    # 3. Login incorrect password
    resp = client.post("/api/auth/login", json={"email": "verifier@example.com", "password": "WrongPassword"})
    assert resp.status_code == 401
    assert "Incorrect password" in resp.json()["detail"]

    # 4. Login correct password
    resp = client.post("/api/auth/login", json=reg_payload)
    assert resp.status_code == 200
    login_data = resp.json()
    assert "access_token" in login_data
    login_token = login_data["access_token"]

    # 5. Authenticated /api/auth/me
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {login_token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "verifier@example.com"

    # 6. Logout
    resp = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {login_token}"})
    assert resp.status_code == 200
    assert resp.json()["message"] == "Successfully logged out"
