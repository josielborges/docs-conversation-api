from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services import DatabaseService
from app.core import settings


async def verify_api_key(
    x_api_key: str = Header(...),
    db: AsyncSession = Depends(get_db)
) -> str:
    """Verify API key for authentication."""
    if not await DatabaseService.validate_api_key(db, x_api_key):
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    
    return x_api_key


async def verify_master_key(
    x_master_key: str = Header(...)
) -> str:
    """Verify master key for administrative operations."""
    if x_master_key != settings.MASTER_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid master key")
    
    return x_master_key
