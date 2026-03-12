"""
API endpoints для оценки валютных форвардов.
"""
import asyncio
from typing import Any

from fastapi import APIRouter, Request
from pydantic import Field

from src.middleware.rate_limit import limiter
from src.services.forward_service import calculate_forward_valuation
from src.utils.error_handler import service_endpoint
from src.utils.financial_validation import MAX_NOTIONAL, MAX_TENOR_YEARS, FinancialBaseModel

router = APIRouter()


class ForwardValuationRequest(FinancialBaseModel):
    """Запрос на оценку форварда."""
    forwardType: str = Field("fx", description="Тип форварда: fx, bond, commodity, equity, rate")
    # Общие параметры
    spotPrice: float = Field(..., gt=0, le=MAX_NOTIONAL, description="Спот цена базового актива")
    timeToMaturity: float = Field(..., gt=0, le=MAX_TENOR_YEARS, description="Время до экспирации (лет)")
    marketForwardPrice: float = Field(..., gt=0, le=MAX_NOTIONAL, description="Рыночная цена форварда")
    contractSize: float = Field(1.0, gt=0, le=MAX_NOTIONAL, description="Размер контракта")

    # Параметры для Cost-of-Carry (bond, commodity, equity, rate)
    dividendYield: float | None = Field(0.0, description="Дивиденды / Купоны (%)")
    carryingCost: float | None = Field(0.0, description="Стоимость хранения (%)")
    convenienceYield: float | None = Field(0.0, description="Удобство владения (Convenience Yield, %)")
    riskFreeRate: float | None = Field(None, description="Безрисковая ставка (%)")
    repoRate: float | None = Field(None, description="Репо ставка (%)")

    # Параметры для форварда на облигацию (bond)
    accruedInterest: float | None = Field(0.0, description="Накопленный купонный доход (AI)")
    couponRate: float | None = Field(None, description="Купонная ставка (годовая, %)")
    couponFrequency: int | None = Field(2, description="Частота выплаты купонов (1, 2, 4, 12 - раз в год)")
    faceValue: float | None = Field(100.0, description="Номинал облигации")
    lastCouponDate: str | None = Field(None, description="Дата последнего купона (YYYY-MM-DD)")
    maturityDate: str | None = Field(None, description="Дата погашения облигации (YYYY-MM-DD)")
    dayCountConvention: str | None = Field("ACT/365", description="Конвенция подсчета дней: ACT/ACT, ACT/365, ACT/360, 30/360")
    autoCalculateAI: bool | None = Field(True, description="Автоматически рассчитывать НКД из даты последнего купона")
    yieldCurveTenors: list[float] | None = Field(None, description="Теноры кривой доходности (в годах)")
    yieldCurveRates: list[float] | None = Field(None, description="Ставки кривой доходности (в процентах)")

    # Параметры для валютных форвардов (fx)
    buyCurrency: str | None = Field(None, description="Покупаемая валюта (для fx)")
    sellCurrency: str | None = Field(None, description="Продаваемая валюта (для fx)")
    buyAmount: float | None = Field(None, description="Сумма покупки (для fx)")
    sellAmount: float | None = Field(None, description="Сумма продажи (для fx)")
    dealDate: str | None = Field(None, description="Дата сделки (YYYY-MM-DD, для fx)")
    valuationDate: str | None = Field(None, description="Дата оценки (YYYY-MM-DD, для fx)")
    expirationDate: str | None = Field(None, description="Дата экспирации (YYYY-MM-DD, для fx)")
    settlementCurrency: str | None = Field("RUB", description="Валюта расчетов (для fx)")
    internalRate: float | None = Field(None, description="Ставка для покупаемой валюты (%) (для fx)")
    externalRate: float | None = Field(None, description="Ставка для продаваемой валюты (%) (для fx)")


@router.post("/valuate", response_model=dict[str, Any])
@limiter.limit("10/minute")
@service_endpoint("Forward valuation")
async def valuate_forward(request: Request, body: ForwardValuationRequest):
    """
    Выполняет оценку форварда различных типов.
    """
    return await asyncio.to_thread(lambda: calculate_forward_valuation(
        forward_type=body.forwardType,
        spot_price=body.spotPrice,
        time_to_maturity=body.timeToMaturity,
        market_forward_price=body.marketForwardPrice,
        contract_size=body.contractSize,
        # Cost-of-Carry параметры
        dividend_yield=body.dividendYield,
        carrying_cost=body.carryingCost,
        convenience_yield=body.convenienceYield,
        risk_free_rate=body.riskFreeRate,
        repo_rate=body.repoRate,
        # Bond параметры
        accrued_interest=body.accruedInterest,
        coupon_rate=body.couponRate,
        coupon_frequency=body.couponFrequency,
        face_value=body.faceValue,
        last_coupon_date=body.lastCouponDate,
        maturity_date=body.maturityDate,
        day_count_convention=body.dayCountConvention or "ACT/365",
        yield_curve_tenors=body.yieldCurveTenors,
        yield_curve_rates=body.yieldCurveRates,
        auto_calculate_ai=body.autoCalculateAI if body.autoCalculateAI is not None else True,
        # FX параметры
        buy_currency=body.buyCurrency,
        sell_currency=body.sellCurrency,
        buy_amount=body.buyAmount,
        sell_amount=body.sellAmount,
        deal_date=body.dealDate,
        valuation_date=body.valuationDate,
        expiration_date=body.expirationDate,
        settlement_currency=body.settlementCurrency,
        internal_rate=body.internalRate,
        external_rate=body.externalRate
    ))


@router.get("/health")
async def health_check():
    """Health check для сервиса форвардов."""
    return {"status": "ok", "service": "forward"}
