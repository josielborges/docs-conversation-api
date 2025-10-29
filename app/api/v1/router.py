from fastapi import APIRouter
from app.api.v1.endpoints import api_keys, notebooks, conversations, estante, sources

api_router = APIRouter()

api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])
api_router.include_router(notebooks.router, prefix="/notebooks", tags=["notebooks"])
api_router.include_router(conversations.router, prefix="/notebooks", tags=["conversations"])
api_router.include_router(sources.router, prefix="/notebooks", tags=["sources"])
api_router.include_router(estante.router, prefix="/estante", tags=["estante"])
