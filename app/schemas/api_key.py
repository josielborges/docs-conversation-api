from pydantic import BaseModel
from datetime import datetime

class APIKeyCreate(BaseModel):
    id: str
    key: str
    name: str

class APIKeyResponse(BaseModel):
    id: str
    name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
