from fastapi import APIRouter, Depends
from app.services.estante import estante_service
from app.api.dependencies import verify_api_key
from typing import List

router = APIRouter()


@router.get("/areas")
async def get_areas(api_key: str = Depends(verify_api_key)) -> List[dict]:
    return await estante_service.get_areas()


@router.get("/areas/{area_id}/modalidades")
async def get_modalidades(
    area_id: int,
    api_key: str = Depends(verify_api_key)
) -> List[dict]:
    return await estante_service.get_modalidades(area_id)


@router.get("/areas/{area_id}/modalidades/{modalidade_id}/livros")
async def get_livros(
    area_id: int,
    modalidade_id: int,
    api_key: str = Depends(verify_api_key)
):
    return await estante_service.get_livros(area_id, modalidade_id)
