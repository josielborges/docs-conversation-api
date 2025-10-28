from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid as uuid_pkg

class SourceCreate(BaseModel):
    name: str
    type: str
    view_url: Optional[str] = None

class SourceResponse(BaseModel):
    public_id: uuid_pkg.UUID
    name: str
    type: str
    view_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
