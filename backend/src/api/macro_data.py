"""
Macro Data Router — FRED, Frankfurter (ECB), Bank of Russia, SEC EDGAR, OpenFIGI

Prefix: /api/macro-data
"""


from fastapi import APIRouter, Body, Query

from src.services.macro_data_service import (
    cbr_daily_rates,
    cbr_deposit_rates,
    cbr_key_rate,
    cbr_precious_metals,
    cbr_repo_rates,
    cbr_ruonia,
    ecb_historical_rates,
    ecb_latest_rates,
    fred_search,
    fred_series_observations,
    openfigi_map,
    sec_company_facts,
    sec_company_filings,
    sec_full_text_search,
)
from src.utils.error_handler import service_endpoint

router = APIRouter()


# ─── FRED ─────────────────────────────────────────────────────────────────────

@router.get("/fred/series")
@service_endpoint("Fred Series")
async def fred_series(
    series_id: str = Query(..., description="FRED series ID (e.g. GDP, CPIAUCSL, UNRATE)"),
    limit: int = Query(100),
    sort_order: str = Query("desc"),
    observation_start: str | None = Query(None),
    observation_end: str | None = Query(None),
):
    """Get observations for a FRED economic series."""
    return await fred_series_observations(series_id, limit, sort_order, observation_start, observation_end)
@router.get("/fred/search")
@service_endpoint("Fred Search Endpoint")
async def fred_search_endpoint(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20),
):
    """Search FRED series by keyword."""
    return await fred_search(q, limit)
# ─── Frankfurter (ECB) ───────────────────────────────────────────────────────

@router.get("/ecb/latest")
@service_endpoint("Ecb Latest")
async def ecb_latest(
    base: str = Query("EUR", description="Base currency"),
):
    """Latest ECB exchange rates via Frankfurter."""
    return await ecb_latest_rates(base)
@router.get("/ecb/history")
@service_endpoint("Ecb History")
async def ecb_history(
    base: str = Query("EUR"),
    start: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    symbols: str | None = Query(None, description="Comma-separated currencies"),
):
    """Historical ECB exchange rates via Frankfurter."""
    return await ecb_historical_rates(base, start, end, symbols)
# ─── Bank of Russia ───────────────────────────────────────────────────────────

@router.get("/cbr/rates")
@service_endpoint("Cbr Rates")
async def cbr_rates():
    """CBR daily FX rates (XML→JSON)."""
    return await cbr_daily_rates()
@router.get("/cbr/key-rate")
async def cbr_key():
    """CBR key rate current value and history."""
    return await cbr_key_rate()
@router.get("/cbr/ruonia")
@service_endpoint("Cbr Ruonia Endpoint")
async def cbr_ruonia_endpoint(
    from_date: str = Query("2024-01-01"),
    to_date: str = Query("2026-12-31"),
):
    """CBR RUONIA interbank rate history."""
    return await cbr_ruonia(from_date, to_date)
@router.get("/cbr/metals")
@service_endpoint("Cbr Metals Endpoint")
async def cbr_metals_endpoint(
    from_date: str = Query("2024-01-01"),
    to_date: str = Query("2026-12-31"),
):
    """CBR precious metals prices (gold, silver, platinum, palladium)."""
    return await cbr_precious_metals(from_date, to_date)
@router.get("/cbr/deposit-rates")
@service_endpoint("Cbr Deposit Endpoint")
async def cbr_deposit_endpoint(
    from_date: str = Query("2024-01-01"),
    to_date: str = Query("2026-12-31"),
):
    """CBR average deposit rates."""
    return await cbr_deposit_rates(from_date, to_date)
@router.get("/cbr/repo-rates")
@service_endpoint("Cbr Repo Endpoint")
async def cbr_repo_endpoint(
    from_date: str = Query("2024-01-01"),
    to_date: str = Query("2026-12-31"),
):
    """CBR repo debt data."""
    return await cbr_repo_rates(from_date, to_date)
# ─── SEC EDGAR ────────────────────────────────────────────────────────────────

@router.get("/sec/filings/{cik}")
@service_endpoint("Sec Filings")
async def sec_filings(cik: str):
    """SEC company filings by CIK number."""
    return await sec_company_filings(cik)
@router.get("/sec/search")
async def sec_search_endpoint(
    q: str = Query(..., description="Full-text search query"),
    forms: str | None = Query(None, description="Form types (e.g. '10-K,10-Q')"),
    limit: int = Query(20),
):
    """Full-text search of SEC EDGAR filings."""
    return await sec_full_text_search(q, forms=forms or "", limit=limit)
@router.get("/sec/company-facts/{cik}")
@service_endpoint("Sec Facts")
async def sec_facts(cik: str):
    """SEC XBRL company facts by CIK number."""
    return await sec_company_facts(cik)
# ─── OpenFIGI ─────────────────────────────────────────────────────────────────

@router.post("/openfigi/map")
@service_endpoint("Figi Map")
async def figi_map(
    jobs: list[dict[str, str]] = Body(..., description='[{"idType": "ID_ISIN", "idValue": "US0378331005"}]')
):
    """Map financial identifiers via OpenFIGI."""
    return await openfigi_map(jobs)
@router.get("/health")
async def health():
    return {"status": "ok", "service": "macro-data"}
