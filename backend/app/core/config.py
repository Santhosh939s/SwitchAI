import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate root directory containing .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ROOT_ENV = BASE_DIR / ".env"
LOCAL_ENV = Path(".env")

ENV_FILE_PATH = str(ROOT_ENV if ROOT_ENV.exists() else LOCAL_ENV)

class Settings(BaseSettings):
    PROJECT_NAME: str = "SwitchAI"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./switchai.db"
    ENCRYPTION_KEY: str
    BACKEND_CORS_ORIGINS: list = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Local AI Configuration
    LOCAL_AI_BASE_URL: str = "http://127.0.0.1:8080/v1"
    LOCAL_AI_MODEL: Optional[str] = "Qwen2.5-1.5B-Instruct-Q4_K_M"

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, extra="ignore")

settings = Settings()
