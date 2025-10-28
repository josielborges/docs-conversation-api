from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.base import get_db
from app.schemas import NotebookCreate, NotebookResponse, SourceResponse
from app.services import DatabaseService, vector_store, llm_service
from app.utils import extract_text, chunk_text
from app.api.dependencies import verify_api_key
from app.core import settings
import uuid

router = APIRouter()


@router.post("", response_model=NotebookResponse)
async def create_notebook(
    notebook: NotebookCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new notebook."""
    return await DatabaseService.create_notebook(db, notebook)


@router.get("", response_model=List[NotebookResponse])
async def list_notebooks(
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """List all notebooks."""
    return await DatabaseService.get_all_notebooks(db)


@router.put("/{notebook_id}", response_model=NotebookResponse)
async def rename_notebook(
    notebook_id: str,
    notebook: NotebookCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Rename a notebook."""
    db_notebook = await DatabaseService.get_notebook(db, notebook_id)
    if not db_notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return await DatabaseService.update_notebook(db, notebook_id, notebook.name)


@router.delete("/{notebook_id}")
async def delete_notebook(
    notebook_id: str,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete a notebook."""
    db_notebook = await DatabaseService.get_notebook(db, notebook_id)
    if not db_notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    vector_store.delete_collection(notebook_id)
    await DatabaseService.delete_notebook(db, notebook_id)
    return {"message": "Notebook deleted"}


@router.post("/{notebook_id}/upload")
async def upload_files(
    notebook_id: str,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Upload files to a notebook."""
    db_notebook = await DatabaseService.get_notebook(db, notebook_id)
    if not db_notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    try:
        for file in files:
            content = await file.read()
            text = extract_text(content, file.filename)
            if not text:
                continue
            
            chunks = chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            vector_store.add_documents(notebook_id, chunks, file.filename)
            await DatabaseService.add_source(db, notebook_id, file.filename, "file")
        
        return {"message": f"{len(files)} arquivo(s) processado(s) com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{notebook_id}/sources", response_model=List[SourceResponse])
async def get_sources(
    notebook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all sources for a notebook."""
    db_notebook = await DatabaseService.get_notebook(db, notebook_id)
    if not db_notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return await DatabaseService.get_sources(db, notebook_id)


@router.get("/{notebook_id}/summary")
async def get_summary(
    notebook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get notebook summary."""
    db_notebook = await DatabaseService.get_notebook(db, notebook_id)
    if not db_notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return {"summary": db_notebook.summary or ""}


@router.post("/{notebook_id}/generate-summary")
async def generate_summary(
    notebook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Generate a summary for the notebook."""
    db_notebook = await DatabaseService.get_notebook(db, notebook_id)
    if not db_notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    try:
        count = vector_store.get_collection_count(notebook_id)
        if count == 0:
            summary_text = "Nenhuma fonte adicionada ainda. Adicione documentos ou links para gerar um resumo."
            await DatabaseService.update_notebook_summary(db, notebook_id, summary_text)
            return {"summary": summary_text}
        
        results = vector_store.query(notebook_id, "resumo geral conteúdo principal", 
                                     min(10, count))
        
        context = "\n\n".join(results['documents'][0]) if results['documents'][0] else ""
        sources = list(set([meta['filename'] for meta in results['metadatas'][0]])) if results['metadatas'] else []
        
        summary_text = llm_service.generate_summary(context, sources)
        await DatabaseService.update_notebook_summary(db, notebook_id, summary_text)
        
        return {"summary": summary_text, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
