from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SwitchAI Backend",
        "version": "0.1.0",
        "skills_enabled": ["api-integration", "api-rate-limiting-helper"]
    }
