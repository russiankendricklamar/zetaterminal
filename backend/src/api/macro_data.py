"""
Macro Data Router — FRED, Frankfurter (ECB), Bank of Russia, SEC EDGAR, OpenFIGI

Prefix: /api/macro-data
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List, Dict

from src.services.macro_data_service import (
    fred_series_observations,
    fred_search,
    ecb_latest_rates,
    ecb_historical_rates,
    cbr_daily_rates,
    cbr_key_rate,
    sec_company_filings,
    sec_company_facts,
    openfigi_map,
)

router = APIRouter()


# ─── FRED ─────────────────────────────────────────────────────────────────────

@router.get("/fred/series")
async def fred_series(
    series_id: str = Query(..., description="FRED series ID (e.g. GDP, CPIAUCSL, UNRATE)"),
    limit: int = Query(100),
    sort_order: str = Query("desc"),
    observation_start: Optional[str] = Query(None),
    observation_end: Optional[str] = Query(None),
):
    """Get observations for a FRED economic series."""
    try:
        return await fred_series_observations(series_id, limit, sort_order, observation_start, observation_end)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fred/search")
async def fred_search_endpoint(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20),
):
    """Search FRED series by keyword."""
    try:
        return await fred_search(q, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Frankfurter (ECB) ───────────────────────────────────────────────────────

@router.get("/ecb/latest")
async def ecb_latest(
    base: str = Query("EUR", description="Base currency"),
):
    """Latest ECB exchange rates via Frankfurter."""
    try:
        return await ecb_latest_rates(base)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ecb/history")
async def ecb_history(
    base: str = Query("EUR"),
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    symbols: Optional[str] = Query(None, description="Comma-separated currencies"),
):
    """Historical ECB exchange rates via Frankfurter."""
    try:
        return await ecb_historical_rates(base, start, end, symbols)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Bank of Russia ───────────────────────────────────────────────────────────

@router.get("/cbr/rates")
async def cbr_rates():
    """CBR daily FX rates (XML→JSON)."""
    try:
        return await cbr_daily_rates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cbr/key-rate")
async def cbr_key():
    """CBR key rate current value and history."""
    try:
        return await cbr_key_rate()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── SEC EDGAR ────────────────────────────────────────────────────────────────

@router.get("/sec/filings/{cik}")
async def sec_filings(cik: str):
    """SEC company filings by CIK number."""
    try:
        return await sec_company_filings(cik)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sec/company-facts/{cik}")
async def sec_facts(cik: str):
    """SEC XBRL company facts by CIK number."""
    try:
        return await sec_company_facts(cik)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── OpenFIGI ─────────────────────────────────────────────────────────────────

@router.post("/openfigi/map")
async def figi_map(
    jobs: List[Dict[str, str]] = Body(..., description='[{"idType": "ID_ISIN", "idValue": "US0378331005"}]')
):
    """Map financial identifiers via OpenFIGI."""
    try:
        return await openfigi_map(jobs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    return {"status": "ok", "service": "macro-data"}
