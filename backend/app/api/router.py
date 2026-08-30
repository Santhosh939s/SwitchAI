from fastapi import APIRouter
from app.api.endpoints import health, auth, providers, conversations, memory, routing, usage, files

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(providers.router, prefix="/providers", tags=["Providers"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(memory.router, tags=["Memory"])
api_router.include_router(routing.router, prefix="/router", tags=["Routing"])
api_router.include_router(usage.router, prefix="/usage", tags=["Usage"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
