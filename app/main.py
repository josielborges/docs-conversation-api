from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core import settings
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    yield


app = FastAPI(
    title=settings.PROJECT_NAME, 
    description="API for conversational document interaction using RAG",
    version=settings.VERSION,
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
