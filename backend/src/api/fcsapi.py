"""
API endpoints для FCS API — унифицированный FX, crypto, stocks.

Используется как унифицированный слой для простых виджетов.
"""

from typing import Any

from fastapi import APIRouter, Request

from src.middleware.rate_limit import limiter
from src.services.fcsapi_service import (
    fcs_crypto_latest,
    fcs_forex_latest,
    fcs_forex_list,
    fcs_stock_latest,
)
from src.utils.error_handler import service_endpoint

router = APIRouter()


@router.get("/forex/{symbol:path}", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("FCS Forex Quote")
async def get_forex(request: Request, symbol: str):
    """Получить котировку валютной пары (EUR/USD, GBP/JPY)."""
    return await fcs_forex_latest(symbol)


@router.get("/crypto/{symbol:path}", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("FCS Crypto Quote")
async def get_crypto(request: Request, symbol: str):
    """Получить котировку криптовалюты (BTC/USD, ETH/USD)."""
    return await fcs_crypto_latest(symbol)


@router.get("/stock/{symbol}", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("FCS Stock Quote")
async def get_stock(request: Request, symbol: str):
    """Получить котировку акции (AAPL, MSFT)."""
    return await fcs_stock_latest(symbol)


@router.get("/forex-pairs", response_model=list[dict[str, str]])
@limiter.limit("10/minute")
@service_endpoint("FCS Forex Pairs")
async def get_forex_pairs(request: Request):
    """Получить список доступных валютных пар."""
    return await fcs_forex_list()


@router.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "service": "fcs_api", "provider": "fcsapi.com"}
