from pydantic import BaseModel
from datetime import datetime

class ConversationCreate(BaseModel):
    id: str
    notebook_id: str
    title: str

class ConversationResponse(BaseModel):
    id: str
    notebook_id: str
    title: str
    created_at: datetime

    class Config:
        from_attributes = True
