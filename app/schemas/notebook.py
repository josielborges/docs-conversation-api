from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotebookCreate(BaseModel):
    id: str
    name: str

class NotebookUpdate(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None

class NotebookResponse(BaseModel):
    id: str
    name: str
    summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
