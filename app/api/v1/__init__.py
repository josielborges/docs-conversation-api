from fastapi import APIRouter
from . import notebooks, conversations, links, api_keys, estante

api_router = APIRouter()

api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])
api_router.include_router(notebooks.router, prefix="/notebooks", tags=["notebooks"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(conversations.router, tags=["conversations"])
api_router.include_router(links.router, tags=["links"])
api_router.include_router(estante.router, prefix="/estante", tags=["estante"])
