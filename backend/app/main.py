from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.init_db import init_db
from app.api.router import api_router

# Ensure DB tables are initialized on module load
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    lifespan=lifespan
)

# Top-level /health route
@app.get("/health")
def root_health():
    return {
        "status": "healthy",
        "service": "SwitchAI Backend",
        "version": "0.1.0",
        "skills_enabled": ["api-integration", "api-rate-limiting-helper"]
    }

app.include_router(api_router, prefix="/api")
