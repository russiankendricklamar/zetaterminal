"""
API router for managing third-party API keys stored in the database.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.client import get_session
from src.services import secrets_service

router = APIRouter()


class SetKeyRequest(BaseModel):
    service: str
    key_value: str
    description: str = ""


class SetKeyResponse(BaseModel):
    success: bool
    service: str


@router.get("/keys")
async def list_keys(session: AsyncSession = Depends(get_session)):
    """List all API keys (values masked)."""
    keys = await secrets_service.list_keys(session)
    known = secrets_service.KNOWN_SERVICES
    return {
        "keys": keys,
        "available_services": [
            {"service": k, "description": v}
            for k, v in known.items()
        ],
    }


@router.post("/keys", response_model=SetKeyResponse)
async def set_key(req: SetKeyRequest, session: AsyncSession = Depends(get_session)):
    """Create or update an API key."""
    await secrets_service.set_key(req.service, req.key_value, req.description, session)
    return SetKeyResponse(success=True, service=req.service)


@router.delete("/keys/{service}")
async def delete_key(service: str, session: AsyncSession = Depends(get_session)):
    """Delete an API key."""
    deleted = await secrets_service.delete_key(service, session)
    return {"success": deleted, "service": service}


@router.post("/reload")
async def reload_keys(session: AsyncSession = Depends(get_session)):
    """Force reload all keys from DB into memory cache."""
    await secrets_service.load_all(session)
    return {"success": True, "count": len(secrets_service._cache)}
