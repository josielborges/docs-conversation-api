from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core import settings
from app.api import api_router
from app.services import vector_store, DatabaseService
from app.db.base import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize vector store collections from database on startup."""
    async for db in get_db():
        notebooks = await DatabaseService.get_all_notebooks(db)
        for notebook in notebooks:
            vector_store.get_or_create_collection(notebook.id)
        break
    yield


app = FastAPI(
    title="Docs Conversation API",
    description="API for conversational document interaction using RAG",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "docs-conversation-api"}


app.include_router(api_router)
