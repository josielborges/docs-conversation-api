from pydantic import BaseModel
from datetime import datetime
import uuid as uuid_pkg

class ApiKeyCreate(BaseModel):
    name: str

class ApiKeyResponse(BaseModel):
    public_id: uuid_pkg.UUID
    name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ApiKeyCreateResponse(BaseModel):
    public_id: uuid_pkg.UUID
    key: str
    name: str
    message: str
