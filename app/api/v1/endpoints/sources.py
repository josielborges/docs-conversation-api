from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services import DatabaseService
from app.api.dependencies import verify_api_key
import uuid as uuid_pkg

router = APIRouter()


@router.get("/{notebook_id}/sources")
async def get_sources(
    notebook_id: str,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    public_id = uuid_pkg.UUID(notebook_id)
    notebook = await DatabaseService.get_notebook(db, public_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    return await DatabaseService.get_sources(db, notebook.id)
