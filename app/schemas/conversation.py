from pydantic import BaseModel
from datetime import datetime
import uuid as uuid_pkg

class ConversationCreate(BaseModel):
    title: str

class ConversationResponse(BaseModel):
    public_id: uuid_pkg.UUID
    title: str
    created_at: datetime

    class Config:
        from_attributes = True
