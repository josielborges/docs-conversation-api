from pydantic import BaseModel
from datetime import datetime
from typing import List
import uuid as uuid_pkg


class ChatMessageCreate(BaseModel):
    role: str
    content: str
    sources: List[str] = []


class ChatRequest(BaseModel):
    message: str
    enabled_sources: List[str] = []


class ChatResponse(BaseModel):
    response: str
    sources: List[str]


class ChatMessageResponse(BaseModel):
    public_id: uuid_pkg.UUID
    role: str
    content: str
    sources: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
