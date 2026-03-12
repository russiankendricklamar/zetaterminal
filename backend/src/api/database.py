"""
API endpoints for database operations.
"""
import asyncio
import logging
import os
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.client import get_session
from src.database.models import (
    BondValuationRecord,
    CalculationHistory,
    FileRecord,
    MarketDataDaily,
    PortfolioRecord,
)
from src.database.repositories import (
    BondValuationRepository,
    CalculationHistoryRepository,
    FileRepository,
    MarketDataRepository,
    PortfolioRepository,
)
from src.middleware.auth import require_auth
from src.middleware.rate_limit import limiter
from src.utils.jwt_utils import TokenPayload

logger = logging.getLogger(__name__)

router = APIRouter()

_SAFE_FILENAME_RE = re.compile(r'^[\w.\-]+$')


def _sanitize_filename(name: str) -> str:
    """Strip path components and validate filename characters."""
    name = os.path.basename(name)
    if not _SAFE_FILENAME_RE.match(name):
        raise HTTPException(status_code=400, detail="Invalid file name characters")
    return name


# Bond Valuation endpoints
@router.post("/bond-valuations", response_model=dict)
@limiter.limit("20/minute")
async def create_bond_valuation(
    request: Request,
    record: BondValuationRecord,
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    repo = BondValuationRepository(session)
    result = await repo.create(record)
    return {"success": True, "data": result}


@router.get("/bond-valuations/{record_id}", response_model=dict)
@limiter.limit("30/minute")
async def get_bond_valuation(
    request: Request,
    record_id: int,
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    repo = BondValuationRepository(session)
    result = await repo.get_by_id(record_id)
    if not result:
        raise HTTPException(status_code=404, detail="Record not found")
    if result.get("user_id") and result["user_id"] != user.sub:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"success": True, "data": result}


@router.get("/bond-valuations", response_model=dict)
@limiter.limit("30/minute")
async def get_bond_valuations(
    request: Request,
    secid: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    repo = BondValuationRepository(session)
    if secid:
        results = await repo.get_by_secid(secid, limit)
    elif start_date and end_date:
        results = await repo.get_by_date_range(start_date, end_date, limit)
    else:
        results = await repo.get_by_date_range(
            datetime.now().replace(day=1).strftime("%Y-%m-%d"),
            datetime.now().strftime("%Y-%m-%d"),
            limit,
        )
    # Filter by user ownership (IDOR protection)
    results = [r for r in results if not r.get("user_id") or r["user_id"] == user.sub]
    return {"success": True, "data": results, "count": len(results)}


@router.put("/bond-valuations/{record_id}", response_model=dict)
@limiter.limit("20/minute")
async def update_bond_valuation(
    request: Request,
    record_id: int,
    record: BondValuationRecord,
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    repo = BondValuationRepository(session)
    existing = await repo.get_by_id(record_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Record not found")
    if existing.get("user_id") and existing["user_id"] != user.sub:
        raise HTTPException(status_code=404, detail="Record not found")
    result = await repo.update(record_id, record)
    return {"success": True, "data": result}


@router.delete("/bond-valuations/{record_id}", response_model=dict)
@limiter.limit("20/minute")
async def delete_bond_valuation(
    request: Request,
    record_id: int,
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    repo = BondValuationRepository(session)
    existing = await repo.get_by_id(record_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Record not found")
    if existing.get("user_id") and existing["user_id"] != user.sub:
        raise HTTPException(status_code=404, detail="Record not found")
    await repo.delete(record_id)
    return {"success": True, "message": "Record deleted"}


# Portfolio endpoints
@router.post("/portfolios", response_model=dict)
@limiter.limit("20/minute")
async def create_portfolio(
    request: Request,
    record: PortfolioRecord,
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    repo = PortfolioRepository(session)
    result = await repo.create(record)
    return {"success": True, "data": result}


@router.get("/portfolios", response_model=dict)
@limiter.limit("30/minute")
async def get_portfolios(
    request: Request,
    limit: int = Query(100, ge=1, le=1000),
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    repo = PortfolioRepository(session)
    results = await repo.get_all(limit)
    results = [r for r in results if not r.get("user_id") or r["user_id"] == user.sub]
    return {"success": True, "data": results, "count": len(results)}


@router.get("/portfolios/{portfolio_id}", response_model=dict)
@limiter.limit("30/minute")
async def get_portfolio(
    request: Request,
    portfolio_id: int,
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    repo = PortfolioRepository(session)
    result = await repo.get_by_id(portfolio_id)
    if not result:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if result.get("user_id") and result["user_id"] != user.sub:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return {"success": True, "data": result}


# Calculation History endpoints
@router.post("/calculation-history", response_model=dict)
@limiter.limit("20/minute")
async def create_calculation_history(
    request: Request,
    record: CalculationHistory,
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    repo = CalculationHistoryRepository(session)
    result = await repo.create(record)
    return {"success": True, "data": result}


@router.get("/calculation-history", response_model=dict)
@limiter.limit("30/minute")
async def get_calculation_history(
    request: Request,
    calculation_type: str | None = None,
    limit: int = Query(50, ge=1, le=1000),
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    repo = CalculationHistoryRepository(session)
    results = await repo.get_recent(calculation_type, limit)
    results = [r for r in results if not r.get("user_id") or r["user_id"] == user.sub]
    return {"success": True, "data": results, "count": len(results)}


# Market Data endpoints
@router.get("/market-data", response_model=dict)
@limiter.limit("30/minute")
async def get_market_data(
    request: Request,
    ticker: str | None = None,
    data_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    repo = MarketDataRepository(session)
    if ticker:
        results = await repo.get_by_ticker(ticker, data_type, start_date, end_date, limit)
    else:
        results = []
    return {"success": True, "data": results, "count": len(results)}


@router.post("/market-data/daily", response_model=dict)
@limiter.limit("20/minute")
async def create_market_data(
    request: Request,
    record: MarketDataDaily,
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    repo = MarketDataRepository(session)
    result = await repo.create_or_update(record)
    return {"success": True, "data": result}


# File endpoints
@router.get("/files", response_model=dict)
@limiter.limit("30/minute")
async def get_files(
    request: Request,
    file_type: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    repo = FileRepository(session)
    if file_type:
        results = await repo.get_by_type(file_type, limit)
    else:
        results = await repo.get_all(limit)
    results = [r for r in results if not r.get("user_id") or r["user_id"] == user.sub]
    return {"success": True, "data": results, "count": len(results)}


@router.get("/files/{file_id}", response_model=dict)
@limiter.limit("30/minute")
async def get_file(
    request: Request,
    file_id: int,
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    repo = FileRepository(session)
    result = await repo.get_by_id(file_id)
    if not result:
        raise HTTPException(status_code=404, detail="File not found")
    return {"success": True, "data": result}


# Registry export endpoints
class RegistryParquetRequest(BaseModel):
    registry_type: str
    data: list[dict]
    file_name: str | None = None

    @field_validator("data")
    @classmethod
    def validate_data_size(cls, v: list[dict]) -> list[dict]:
        if len(v) > 10000:
            raise ValueError("Maximum 10000 records per export")
        return v


@router.post("/export/registry/parquet", response_model=dict)
@limiter.limit("5/minute")
async def export_registry_parquet(
    request: Request,
    req: RegistryParquetRequest,
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Export registry data to Parquet format and save locally."""
    import pandas as pd

    data = req.data
    if not data:
        raise HTTPException(status_code=400, detail="Registry data is empty")

    df = pd.DataFrame(data)

    file_name = req.file_name
    if not file_name:
        date_str = datetime.now().strftime("%Y%m%d")
        file_name = f"registry_{req.registry_type}_{date_str}.parquet"

    file_name = _sanitize_filename(file_name)

    export_dir = os.path.join(os.getcwd(), "exports", "registers")
    await asyncio.to_thread(os.makedirs, export_dir, exist_ok=True)
    file_path = os.path.join(export_dir, file_name)

    await asyncio.to_thread(df.to_parquet, file_path, engine="pyarrow", compression="snappy", index=False)
    file_size = await asyncio.to_thread(os.path.getsize, file_path)

    repo = FileRepository(session)
    file_record = FileRecord(
        file_name=file_name,
        file_path=file_name,  # store name only, not full server path
        file_type="register",
        file_size=file_size,
        mime_type="application/octet-stream",
        description=f"Registry export: {req.registry_type} ({len(data)} records)",
        metadata={
            "registry_type": req.registry_type,
            "records_count": len(data),
            "format": "parquet",
            "compression": "snappy",
        },
    )
    await repo.create(file_record)

    return {
        "success": True,
        "data": {
            "file_name": file_name,
            "file_size": file_size,
            "records_count": len(data),
        },
    }


@router.post("/export/market-data/parquet", response_model=dict)
@limiter.limit("5/minute")
async def export_market_data_parquet(
    request: Request,
    ticker: str | None = None,
    data_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    file_name: str | None = None,
    user: TokenPayload = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
):
    """Export market data to Parquet format."""
    import pandas as pd

    repo = MarketDataRepository(session)
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")

    records = await repo.get_by_ticker(ticker, data_type, start_date, end_date, limit=10000)
    if not records:
        raise HTTPException(status_code=404, detail="No data found for export")

    df = pd.DataFrame(records)

    if not file_name:
        date_str = datetime.now().strftime("%Y%m%d")
        file_name = f"market_{ticker}_{date_str}.parquet"

    file_name = _sanitize_filename(file_name)

    export_dir = os.path.join(os.getcwd(), "exports", "market_data")
    await asyncio.to_thread(os.makedirs, export_dir, exist_ok=True)
    file_path = os.path.join(export_dir, file_name)

    await asyncio.to_thread(df.to_parquet, file_path, engine="pyarrow", compression="snappy", index=False)
    file_size = await asyncio.to_thread(os.path.getsize, file_path)

    return {
        "success": True,
        "data": {
            "file_name": file_name,
            "file_size": file_size,
            "records_count": len(records),
        },
    }
