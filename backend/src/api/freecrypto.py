"""
API endpoints для FreeCryptoAPI — бесплатные крипто-данные.

Используется для узкоспециализированного crypto-дашборда/бота.
Без API-ключа.
"""

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.freecrypto_service import freecrypto_price, freecrypto_prices
from src.utils.error_handler import service_endpoint

router = APIRouter()


class FreeCryptoBatchRequest(BaseModel):
    """Запрос на пакетные крипто-цены."""
    symbols: list[str] = Field(
        ..., max_length=50, description="Список символов (BTC, ETH, SOL)"
    )


@router.get("/price/{symbol}", response_model=dict[str, Any])
@limiter.limit("60/minute")
@service_endpoint("FreeCrypto Price")
async def get_price(request: Request, symbol: str):
    """Получить текущую цену криптовалюты."""
    return await freecrypto_price(symbol)


@router.post("/prices", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("FreeCrypto Batch Prices")
async def get_batch_prices(request: Request, body: FreeCryptoBatchRequest):
    """Получить цены нескольких криптовалют (до 50)."""
    return await freecrypto_prices(body.symbols)


@router.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "service": "freecrypto", "provider": "freecryptoapi.com"}
