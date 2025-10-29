from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.schemas.notebook import NotebookCreate, NotebookUpdate
from app.schemas.source import LinkRequest, EstanteLivrosRequest
from app.services import DatabaseService, vector_store, llm_service
from app.utils.text_extraction import extract_text, chunk_text
from app.utils.web_scraper import scrape_url
from app.api.dependencies import verify_api_key
from app.services.estante import estante_service
from typing import List
import uuid as uuid_pkg

router = APIRouter()


@router.post("")
async def create_notebook(
    notebook: NotebookCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    nb = await DatabaseService.create_notebook(db, notebook)
    vector_store.get_or_create_collection(str(nb.public_id))
    return nb


@router.get("")
async def list_notebooks(
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    return await DatabaseService.get_all_notebooks(db)


@router.put("/{notebook_id}")
async def update_notebook(
    notebook_id: str,
    notebook: NotebookUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    public_id = uuid_pkg.UUID(notebook_id)
    if notebook.name:
        return await DatabaseService.update_notebook(db, public_id, notebook.name)
    if notebook.summary:
        await DatabaseService.update_notebook_summary(db, public_id, notebook.summary)
    nb = await DatabaseService.get_notebook(db, public_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return nb


@router.delete("/{notebook_id}")
async def delete_notebook(
    notebook_id: str,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    public_id = uuid_pkg.UUID(notebook_id)
    vector_store.delete_collection(notebook_id)
    await DatabaseService.delete_notebook(db, public_id)
    return {"message": "Notebook deleted"}


@router.post("/{notebook_id}/upload")
async def upload_files(
    notebook_id: str,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    public_id = uuid_pkg.UUID(notebook_id)
    notebook = await DatabaseService.get_notebook(db, public_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    for file in files:
        content = await file.read()
        text = extract_text(content, file.filename)
        if not text:
            continue
        
        chunks = chunk_text(text)
        vector_store.add_documents(notebook_id, chunks, file.filename)
        await DatabaseService.add_source(db, notebook.id, file.filename, "file")
    
    return {"message": f"{len(files)} arquivo(s) processado(s) com sucesso"}


@router.post("/{notebook_id}/add-link")
async def add_link(
    notebook_id: str,
    link: LinkRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    public_id = uuid_pkg.UUID(notebook_id)
    notebook = await DatabaseService.get_notebook(db, public_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    text = scrape_url(link.url)
    if not text:
        raise HTTPException(status_code=400, detail="No content extracted from URL")
    
    chunks = chunk_text(text)
    vector_store.add_documents(notebook_id, chunks, link.url)
    await DatabaseService.add_source(db, notebook.id, link.url, "link", link.url)
    
    return {"message": "Link adicionado com sucesso"}


@router.post("/{notebook_id}/add-estante-livros")
async def add_estante_livros(
    notebook_id: str,
    request: EstanteLivrosRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    public_id = uuid_pkg.UUID(notebook_id)
    notebook = await DatabaseService.get_notebook(db, public_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    processed_count = 0
    
    for livro in request.livros:
        try:
            content = estante_service.download_book(livro['driveId'])
            text = extract_text(content, f"{livro['nome']}.pdf")
            if not text:
                continue
            
            chunks = chunk_text(text)
            vector_store.add_documents(notebook_id, chunks, livro['nome'])
            await DatabaseService.add_source(db, notebook.id, livro['nome'], "estante", livro['webViewLink'])
            processed_count += 1
        except Exception as e:
            print(f"Erro ao processar livro {livro['nome']}: {str(e)}")
            continue
    
    return {"message": f"{processed_count} livro(s) adicionado(s) com sucesso"}


@router.get("/{notebook_id}/summary")
async def get_summary(
    notebook_id: str,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    public_id = uuid_pkg.UUID(notebook_id)
    notebook = await DatabaseService.get_notebook(db, public_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return {"summary": notebook.summary or ""}


@router.post("/{notebook_id}/generate-summary")
async def generate_summary(
    notebook_id: str,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    public_id = uuid_pkg.UUID(notebook_id)
    notebook = await DatabaseService.get_notebook(db, public_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    count = vector_store.get_count(notebook_id)
    if count == 0:
        summary_text = "Nenhuma fonte adicionada ainda. Adicione documentos ou links para gerar um resumo."
        await DatabaseService.update_notebook_summary(db, public_id, summary_text)
        return {"summary": summary_text}
    
    results = vector_store.query(notebook_id, "resumo geral conteúdo principal", min(10, count))
    context = "\n\n".join(results['documents'][0]) if results['documents'][0] else ""
    sources = list(set([meta['filename'] for meta in results['metadatas'][0]])) if results['metadatas'] else []
    
    summary_text = llm_service.generate_summary(context, sources)
    await DatabaseService.update_notebook_summary(db, public_id, summary_text)
    
    return {"summary": summary_text, "sources": sources}
