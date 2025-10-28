from pydantic import BaseModel
from datetime import datetime

class ApiKeyCreate(BaseModel):
    name: str

class ApiKeyResponse(BaseModel):
    id: str
    name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ApiKeyCreateResponse(BaseModel):
    id: str
    key: str
    name: str
    message: str
