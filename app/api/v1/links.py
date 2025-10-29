from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.schemas import LinkRequest
from app.services import DatabaseService, vector_store
from app.utils import scrape_url, chunk_text
from app.api.dependencies import verify_api_key
from app.core import settings
import uuid as uuid_pkg

router = APIRouter()


@router.post("/notebooks/{public_id}/add-link")
async def add_link(
    public_id: uuid_pkg.UUID,
    link: LinkRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Add a web link to a notebook."""
    db_notebook = await DatabaseService.get_notebook(db, public_id)
    if not db_notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    try:
        text = scrape_url(link.url)
        if not text:
            raise HTTPException(status_code=400, detail="No content extracted from URL")
        
        chunks = chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        await vector_store.add_documents(db, db_notebook.id, chunks, link.url)
        await DatabaseService.add_source(db, db_notebook.id, link.url, "link", link.url)
        
        return {"message": "Link adicionado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
