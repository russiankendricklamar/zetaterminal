"""
API endpoints для Stooq — исторические рыночные данные (CSV).

Используется как исторический слой для бэктест-движка
и оффлайн-хранилище котировок. Без API-ключа.
"""

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.services.stooq_service import (
    stooq_bulk_download,
    stooq_history,
    stooq_search_tickers,
)
from src.utils.error_handler import service_endpoint

router = APIRouter()


class StooqHistoryRequest(BaseModel):
    """Запрос на получение исторических данных из Stooq."""
    ticker: str = Field(..., description="Тикер (AAPL.US, EURUSD, BTC.V, ^SPX)")
    date_from: str | None = Field(None, description="Начальная дата YYYY-MM-DD")
    date_to: str | None = Field(None, description="Конечная дата YYYY-MM-DD")
    interval: str = Field(
        "daily",
        description="Интервал: daily, weekly, monthly, quarterly, yearly",
    )


class StooqBulkRequest(BaseModel):
    """Запрос на пакетную загрузку данных."""
    tickers: list[str] = Field(
        ..., max_length=50, description="Список тикеров (макс. 50)"
    )
    date_from: str | None = Field(None, description="Начальная дата YYYY-MM-DD")
    date_to: str | None = Field(None, description="Конечная дата YYYY-MM-DD")
    interval: str = Field("daily", description="Интервал")


@router.post("/history", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("Stooq History")
async def get_stooq_history(request: Request, body: StooqHistoryRequest):
    """
    Загрузить исторические OHLCV-данные из Stooq.

    Stooq предоставляет бесплатные исторические данные через CSV.
    Поддерживает акции, ETF, FX, крипто, индексы, облигации.
    """
    return await stooq_history(
        ticker=body.ticker,
        date_from=body.date_from,
        date_to=body.date_to,
        interval=body.interval,
    )


@router.post("/bulk", response_model=dict[str, Any])
@limiter.limit("10/minute")
@service_endpoint("Stooq Bulk Download")
async def get_stooq_bulk(request: Request, body: StooqBulkRequest):
    """
    Пакетная загрузка исторических данных для нескольких тикеров.

    Максимум 50 тикеров за запрос. Используется для наполнения
    оффлайн-хранилища котировок бэктест-движка.
    """
    return await stooq_bulk_download(
        tickers=body.tickers,
        date_from=body.date_from,
        date_to=body.date_to,
        interval=body.interval,
    )


@router.get("/search", response_model=list[dict[str, str]])
@limiter.limit("30/minute")
@service_endpoint("Stooq Search")
async def search_stooq_tickers(request: Request, query: str):
    """
    Поиск тикеров Stooq по названию или символу.

    Возвращает до 20 совпадений из курированного списка.
    """
    return await stooq_search_tickers(query)


@router.get("/health")
async def health():
    """Health check для Stooq сервиса."""
    return {"status": "ok", "service": "stooq", "provider": "stooq.com"}
