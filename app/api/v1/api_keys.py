from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.base import get_db
from app.schemas import ApiKeyCreate, ApiKeyResponse, ApiKeyCreateResponse
from app.services import DatabaseService
from app.api.dependencies import verify_master_key
import uuid as uuid_pkg

router = APIRouter()


@router.post("", response_model=ApiKeyCreateResponse)
async def create_api_key(
    api_key_create: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    master_key: str = Depends(verify_master_key)
):
    """Create a new API key. Requires master key."""
    api_key_response, api_key = await DatabaseService.create_api_key(db, api_key_create)
    return ApiKeyCreateResponse(
        public_id=api_key_response.public_id,
        key=api_key,
        name=api_key_response.name,
        message="Guarde esta chave, ela não será exibida novamente"
    )


@router.get("", response_model=List[ApiKeyResponse])
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    master_key: str = Depends(verify_master_key)
):
    """List all API keys. Requires master key."""
    return await DatabaseService.get_all_api_keys(db)


@router.delete("/{public_id}")
async def delete_api_key(
    public_id: uuid_pkg.UUID,
    db: AsyncSession = Depends(get_db),
    master_key: str = Depends(verify_master_key)
):
    """Delete an API key. Requires master key."""
    await DatabaseService.delete_api_key(db, public_id)
    return {"message": "API key deleted"}
