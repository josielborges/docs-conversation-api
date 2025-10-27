from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ChatMessageCreate(BaseModel):
    conversation_id: str
    role: str
    content: str
    sources: Optional[List[str]] = None

class ChatMessageResponse(BaseModel):
    id: int
    conversation_id: str
    role: str
    content: str
    sources: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True
