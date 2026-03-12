"""
API endpoints для оценки валютных форвардов.
"""
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
async def valuate_forward(http_request: Request, request: ForwardValuationRequest):
    """
    Выполняет оценку форварда различных типов.
    """
    return calculate_forward_valuation(
        forward_type=request.forwardType,
        spot_price=request.spotPrice,
        time_to_maturity=request.timeToMaturity,
        market_forward_price=request.marketForwardPrice,
        contract_size=request.contractSize,
        # Cost-of-Carry параметры
        dividend_yield=request.dividendYield,
        carrying_cost=request.carryingCost,
        convenience_yield=request.convenienceYield,
        risk_free_rate=request.riskFreeRate,
        repo_rate=request.repoRate,
        # Bond параметры
        accrued_interest=request.accruedInterest,
        coupon_rate=request.couponRate,
        coupon_frequency=request.couponFrequency,
        face_value=request.faceValue,
        last_coupon_date=request.lastCouponDate,
        maturity_date=request.maturityDate,
        day_count_convention=request.dayCountConvention or "ACT/365",
        yield_curve_tenors=request.yieldCurveTenors,
        yield_curve_rates=request.yieldCurveRates,
        auto_calculate_ai=request.autoCalculateAI if request.autoCalculateAI is not None else True,
        # FX параметры
        buy_currency=request.buyCurrency,
        sell_currency=request.sellCurrency,
        buy_amount=request.buyAmount,
        sell_amount=request.sellAmount,
        deal_date=request.dealDate,
        valuation_date=request.valuationDate,
        expiration_date=request.expirationDate,
        settlement_currency=request.settlementCurrency,
        internal_rate=request.internalRate,
        external_rate=request.externalRate
    )


@router.get("/health")
async def health_check():
    """Health check для сервиса форвардов."""
    return {"status": "ok", "service": "forward"}
