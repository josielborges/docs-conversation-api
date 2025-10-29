from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.schemas.api_key import ApiKeyCreate
from app.services import DatabaseService
import uuid as uuid_pkg

router = APIRouter()


@router.post("")
async def create_api_key(
    api_key_create: ApiKeyCreate,
    db: AsyncSession = Depends(get_db)
):
    response, api_key = await DatabaseService.create_api_key(db, api_key_create)
    return {
        "id": str(response.public_id),
        "key": api_key,
        "name": response.name,
        "message": "Guarde esta chave, ela não será exibida novamente"
    }


@router.get("")
async def list_api_keys(db: AsyncSession = Depends(get_db)):
    return await DatabaseService.get_all_api_keys(db)


@router.delete("/{key_id}")
async def delete_api_key(key_id: str, db: AsyncSession = Depends(get_db)):
    public_id = uuid_pkg.UUID(key_id)
    await DatabaseService.delete_api_key(db, public_id)
    return {"message": "API key deleted"}
