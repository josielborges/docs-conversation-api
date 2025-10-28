from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import uuid as uuid_pkg

class ChatMessageCreate(BaseModel):
    role: str
    content: str
    sources: Optional[List[str]] = None

class ChatMessageResponse(BaseModel):
    public_id: uuid_pkg.UUID
    role: str
    content: str
    sources: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True
