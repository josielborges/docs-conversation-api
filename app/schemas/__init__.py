from app.schemas.notebook import NotebookCreate, NotebookResponse, NotebookUpdate
from app.schemas.source import SourceCreate, SourceResponse
from app.schemas.conversation import ConversationCreate, ConversationResponse
from app.schemas.chat_message import ChatMessageCreate, ChatMessageResponse
from app.schemas.api_key import ApiKeyCreate, ApiKeyResponse, ApiKeyCreateResponse

# Additional schemas
from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    message: str
    enabled_sources: List[str] = []

class ChatResponse(BaseModel):
    response: str
    sources: List[str]

class LinkRequest(BaseModel):
    url: str

class EstanteLivrosRequest(BaseModel):
    livros: List[dict]

__all__ = [
    "NotebookCreate", "NotebookResponse", "NotebookUpdate",
    "SourceCreate", "SourceResponse",
    "ConversationCreate", "ConversationResponse",
    "ChatMessageCreate", "ChatMessageResponse",
    "ApiKeyCreate", "ApiKeyResponse", "ApiKeyCreateResponse",
    "ChatRequest", "ChatResponse", "LinkRequest", "EstanteLivrosRequest"
]
