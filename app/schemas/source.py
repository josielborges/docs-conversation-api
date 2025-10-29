from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import uuid as uuid_pkg

class SourceCreate(BaseModel):
    name: str
    type: str
    view_url: Optional[str] = None

class LinkRequest(BaseModel):
    url: str

class EstanteLivro(BaseModel):
    id: str
    nome: str
    driveId: str
    webViewLink: str

class EstanteLivrosRequest(BaseModel):
    livros: List[EstanteLivro]

class SourceResponse(BaseModel):
    public_id: uuid_pkg.UUID
    name: str
    type: str
    view_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
