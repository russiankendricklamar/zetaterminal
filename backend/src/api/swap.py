"""
API endpoints для оценки свопов (IRS, CDS, Basis Swaps, FX Swaps).
"""
import asyncio
from typing import Any

from fastapi import APIRouter, Request
from pydantic import Field

from src.middleware.rate_limit import limiter
from src.services.swap_service import calculate_fx_swap_valuation, calculate_swap_valuation
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import MAX_NOTIONAL, MAX_RATE_PCT, MAX_TENOR_YEARS, FinancialBaseModel

router = APIRouter()


class SwapValuationRequest(FinancialBaseModel):
    """Запрос на оценку свопа."""
    notional: float = Field(..., gt=0, le=MAX_NOTIONAL, description="Номинал (млн)")
    tenor: float = Field(..., gt=0, le=MAX_TENOR_YEARS, description="Срок (годы)")
    fixedRate: float = Field(..., ge=-100, le=MAX_RATE_PCT, description="Фиксированная ставка (%)")
    floatingRate: float = Field(..., ge=-100, le=MAX_RATE_PCT, description="Индекс плавающей ставки (%)")
    spread: float = Field(0.0, ge=-10000, le=10000, description="Спред (bp)")
    couponsPerYear: int = Field(2, gt=0, le=12, description="Купонов в год")
    discountRate: float = Field(..., ge=-100, le=MAX_RATE_PCT, description="Дисконт кривая (базовая ставка, %)")
    volatility: float | None = Field(None, ge=0, le=500, description="Волатильность (%)")
    swapType: str = Field("irs", description="Тип свопа: irs, cds, basis, xccy")


@router.post("/valuate", response_model=dict[str, Any])
@limiter.limit("10/minute")
@service_endpoint("Swap valuation")
async def valuate_swap(request: Request, body: SwapValuationRequest):
    """
    Выполняет оценку свопа.
    """
    return await asyncio.to_thread(lambda: calculate_swap_valuation(
        notional=body.notional,
        tenor=body.tenor,
        fixed_rate=body.fixedRate,
        floating_rate=body.floatingRate,
        spread=body.spread,
        coupons_per_year=body.couponsPerYear,
        discount_rate=body.discountRate,
        volatility=body.volatility,
        swap_type=body.swapType
    ))


class FxSwapLeg(FinancialBaseModel):
    """Одна нога FX-свопа."""
    buyCurrency: str = Field(..., description="Валюта покупки")
    sellCurrency: str = Field(..., description="Валюта продажи")
    nominalBuy: float = Field(..., description="Сумма покупки")
    nominalSell: float = Field(..., description="Сумма продажи")
    date: str = Field(..., description="Дата расчёта (YYYY-MM-DD)")


class FxSwapValuationRequest(FinancialBaseModel):
    """Запрос на оценку FX-свопа."""
    nearLeg: FxSwapLeg = Field(..., description="Ближняя нога")
    farLeg: FxSwapLeg = Field(..., description="Дальняя нога")
    valuationDate: str = Field(..., description="Дата оценки (YYYY-MM-DD)")
    settlementCurrency: str = Field("RUB", description="Валюта расчёта")
    spotMin: float = Field(..., gt=0, description="Спот мин")
    spotMax: float = Field(..., gt=0, description="Спот макс")
    rateInternal: float = Field(..., ge=-99.0, le=200.0, description="Ставка внутренней валюты (%)")
    rateExternal: float = Field(..., ge=-99.0, le=200.0, description="Ставка внешней валюты (%)")


@router.post("/valuate-fx", response_model=dict[str, Any])
@limiter.limit("10/minute")
@service_endpoint("FX swap valuation")
async def valuate_fx_swap(request: Request, body: FxSwapValuationRequest):
    """Выполняет оценку FX-свопа."""
    return await asyncio.to_thread(lambda: calculate_fx_swap_valuation(
        buy_currency_near=body.nearLeg.buyCurrency,
        sell_currency_near=body.nearLeg.sellCurrency,
        nominal_buy_near=body.nearLeg.nominalBuy,
        nominal_sell_near=body.nearLeg.nominalSell,
        date_near=body.nearLeg.date,
        buy_currency_far=body.farLeg.buyCurrency,
        sell_currency_far=body.farLeg.sellCurrency,
        nominal_buy_far=body.farLeg.nominalBuy,
        nominal_sell_far=body.farLeg.nominalSell,
        date_far=body.farLeg.date,
        valuation_date=body.valuationDate,
        settlement_currency=body.settlementCurrency,
        spot_min=body.spotMin,
        spot_max=body.spotMax,
        rate_internal=body.rateInternal,
        rate_external=body.rateExternal,
    ))


@router.get("/health")
async def health_check():
    """Health check для сервиса свопов."""
    return {"status": "ok", "service": "swap"}
