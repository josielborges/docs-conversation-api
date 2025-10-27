from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SourceCreate(BaseModel):
    notebook_id: str
    name: str
    type: str
    view_url: Optional[str] = None

class SourceResponse(BaseModel):
    id: int
    notebook_id: str
    name: str
    type: str
    view_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
