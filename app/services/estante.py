import requests
import base64
from app.core import settings
from fastapi import HTTPException
from typing import List


class EstanteService:
    """Service for interacting with Estante de Livros API."""
    
    def __init__(self):
        self.base_url = settings.ESTANTE_BASE_URL
        self.username = settings.ESTANTE_USERNAME
        self.password = settings.ESTANTE_PASSWORD
    
    def _get_headers(self) -> dict:
        """Get authorization headers."""
        if not self.username or not self.password:
            raise HTTPException(
                status_code=500, 
                detail="Credenciais da Estante não configuradas"
            )
        
        auth = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        return {"Authorization": f"Basic {auth}"}
    
    async def get_areas(self) -> List[dict]:
        """Get all technological areas."""
        try:
            response = requests.get(
                f"{self.base_url}/areasTecnologicas",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Erro ao buscar áreas: {str(e)}"
            )
    
    async def get_modalidades(self, area_id: int) -> List[dict]:
        """Get modalities for a technological area."""
        try:
            response = requests.get(
                f"{self.base_url}/areaTecnologica/{area_id}/modalidades",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Erro ao buscar modalidades: {str(e)}"
            )
    
    async def get_livros(self, area_id: int, modalidade_id: int) -> List[dict]:
        """Get books for an area and modality."""
        try:
            response = requests.get(
                f"{self.base_url}/areaTecnologica/{area_id}/modalidade/{modalidade_id}/livros",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Erro ao buscar livros: {str(e)}"
            )
    
    def download_book(self, drive_id: str) -> bytes:
        """Download a book by drive ID."""
        response = requests.get(
            f"{self.base_url}/livros/{drive_id}/download",
            headers=self._get_headers(),
            timeout=30
        )
        response.raise_for_status()
        return response.content


estante_service = EstanteService()
