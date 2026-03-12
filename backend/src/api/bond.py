"""
API endpoints для оценки облигаций (DCF).
"""
import asyncio
from typing import Any

from fastapi import APIRouter, Query, Request
from pydantic import Field

from src.middleware.rate_limit import limiter
from src.services.bond_service import calculate_bond_valuation, get_market_yield_from_moex
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import MAX_RATE_PCT, FinancialBaseModel

router = APIRouter()


class BondValuationRequest(FinancialBaseModel):
    """Запрос на оценку облигации."""
    secid: str = Field(..., min_length=1, max_length=50, description="ISIN облигации (например, RU000A10AU99)")
    valuationDate: str = Field(..., description="Дата оценки (YYYY-MM-DD)")
    discountYield1: float = Field(..., ge=-100, le=MAX_RATE_PCT, description="Ставка дисконтирования для сценария 1 (доходность аналога) в процентах")
    discountYield2: float = Field(..., ge=-100, le=MAX_RATE_PCT, description="Ставка дисконтирования для сценария 2 (доходность индекса) в процентах")
    dayCount: int | None = Field(None, description="Базис расчета: 365 (ACT/365) или 360 (30/360) - устаревший параметр")
    dayCountConvention: str | None = Field(None, description="Базис расчета: 'Actual/365F', 'Actual/360', 'Actual/Actual (ISDA)', '30/360 (US)', '30E/360 (ISDA)', '30E/360', 'Actual/Actual (ISMA)'")


@router.post("/valuate", response_model=dict[str, Any])
@limiter.limit("10/minute")
@service_endpoint("Bond valuation")
async def valuate_bond(request: Request, body: BondValuationRequest):
    """Выполняет оценку облигации для двух сценариев доходности."""
    return await asyncio.to_thread(
        calculate_bond_valuation,
        secid=body.secid,
        valuation_date=body.valuationDate,
        discount_yield1=body.discountYield1,
        discount_yield2=body.discountYield2,
        day_count=body.dayCount,
        day_count_convention=body.dayCountConvention,
    )


@router.get("/market-yield", response_model=dict[str, Any])
@limiter.limit("30/minute")
@service_endpoint("Market yield lookup")
async def get_market_yield(request: Request,
    secid: str = Query(..., description="ISIN облигации"),
    date: str = Query(..., description="Дата оценки (YYYY-MM-DD)")
):
    """Получает рыночную доходность облигации из MOEX API."""
    yield_value = await asyncio.to_thread(get_market_yield_from_moex, secid, date)
    return {"secid": secid, "date": date, "yield": yield_value}
