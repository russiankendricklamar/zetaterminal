"""
DaData Router — Russian company and bank data.

Prefix: /api/dadata
"""

from fastapi import APIRouter, HTTPException, Query

from src.services.dadata_service import (
    dadata_find_company,
    dadata_suggest_company,
    dadata_find_bank,
)

router = APIRouter()


@router.get("/company/{inn}")
async def find_company(inn: str):
    """Find company by INN or OGRN."""
    try:
        return await dadata_find_company(inn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggest/company")
async def suggest_company(
    q: str = Query(..., description="Company name or partial INN"),
    count: int = Query(10),
):
    """Suggest companies by name."""
    try:
        return await dadata_suggest_company(q, count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggest/bank")
async def find_bank(
    bik: str = Query(..., description="Bank BIK code"),
):
    """Find bank by BIK."""
    try:
        return await dadata_find_bank(bik)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    return {"status": "ok", "service": "dadata"}
