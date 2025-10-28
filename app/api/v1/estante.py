from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import requests
import base64
from app.db.base import get_db
from app.schemas import EstanteLivrosRequest
from app.services import DatabaseService, vector_store
from app.utils import extract_text, chunk_text
from app.api.dependencies import verify_api_key
from app.core import settings
import uuid as uuid_pkg

router = APIRouter()

def get_estante_headers():
    """Get authentication headers for Estante API."""
    if not settings.ESTANTE_USERNAME or not settings.ESTANTE_PASSWORD:
        raise HTTPException(status_code=500, detail="Credenciais da Estante não configuradas")
    
    auth = base64.b64encode(f"{settings.ESTANTE_USERNAME}:{settings.ESTANTE_PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {auth}"}


@router.get("/areas")
async def get_estante_areas():
    """Get all technological areas from Estante."""
    try:
        headers = get_estante_headers()
        response = requests.get(
            "https://api-recursosdidaticos.senai.br/api/estante/areasTecnologicas",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao buscar áreas: {str(e)}")


@router.get("/areas/{area_id}/modalidades")
async def get_estante_modalidades(area_id: int):
    """Get all modalities for a technological area."""
    try:
        headers = get_estante_headers()
        response = requests.get(
            f"https://api-recursosdidaticos.senai.br/api/estante/areaTecnologica/{area_id}/modalidades",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao buscar modalidades: {str(e)}")


@router.get("/areas/{area_id}/modalidades/{modalidade_id}/livros")
async def get_estante_livros(area_id: int, modalidade_id: int):
    """Get all books for a modality."""
    try:
        headers = get_estante_headers()
        response = requests.get(
            f"https://api-recursosdidaticos.senai.br/api/estante/areaTecnologica/{area_id}/modalidade/{modalidade_id}/livros",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao buscar livros: {str(e)}")


@router.post("/notebooks/{public_id}/add-livros")
async def add_estante_livros(
    public_id: uuid_pkg.UUID,
    request: EstanteLivrosRequest,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Add books from Estante to a notebook."""
    db_notebook = await DatabaseService.get_notebook(db, public_id)
    if not db_notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    headers = get_estante_headers()
    processed_count = 0
    
    try:
        for livro in request.livros:
            try:
                response = requests.get(
                    f"https://api.recursosdidaticos.senai.br/api/estante/livros/{livro['driveId']}/download",
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                
                text = extract_text(response.content, f"{livro['nome']}.pdf")
                if not text:
                    continue
                
                chunks = chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
                vector_store.add_documents(public_id, chunks, livro['nome'])
                await DatabaseService.add_source(db, db_notebook.id, livro['nome'], "estante", livro['webViewLink'])
                processed_count += 1
            except Exception as e:
                print(f"Erro ao processar livro {livro['nome']}: {str(e)}")
                continue
        
        return {"message": f"{processed_count} livro(s) adicionado(s) com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar livros: {str(e)}")
