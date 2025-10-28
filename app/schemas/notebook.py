from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid as uuid_pkg

class NotebookCreate(BaseModel):
    name: str

class NotebookUpdate(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None

class NotebookResponse(BaseModel):
    public_id: uuid_pkg.UUID
    name: str
    summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
