"""
DaData Router — Russian company and bank data.

Prefix: /api/dadata
"""


from fastapi import APIRouter, HTTPException, Query

from src.services.dadata_service import (
    dadata_find_bank,
    dadata_find_company,
    dadata_suggest_company,
)
from src.utils.error_handler import service_endpoint

router = APIRouter()


import re

_INN_RE = re.compile(r'^\d{10,13}$')
_BIK_RE = re.compile(r'^\d{9}$')


@router.get("/company/{inn}")
@service_endpoint("Find Company")
async def find_company(inn: str):
    """Find company by INN or OGRN."""
    if not _INN_RE.match(inn):
        raise HTTPException(status_code=400, detail="Invalid INN/OGRN format (10-13 digits)")
    return await dadata_find_company(inn)
@router.get("/suggest/company")
@service_endpoint("Suggest Company")
async def suggest_company(
    q: str = Query(..., max_length=200, description="Company name or partial INN"),
    count: int = Query(10, ge=1, le=50),
):
    """Suggest companies by name."""
    return await dadata_suggest_company(q, count)
@router.get("/suggest/bank")
@service_endpoint("Find Bank")
async def find_bank(
    bik: str = Query(..., description="Bank BIK code"),
):
    """Find bank by BIK."""
    if not _BIK_RE.match(bik):
        raise HTTPException(status_code=400, detail="Invalid BIK format (9 digits)")
    return await dadata_find_bank(bik)
@router.get("/health")
async def health():
    return {"status": "ok", "service": "dadata"}
