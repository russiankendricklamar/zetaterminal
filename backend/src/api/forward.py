"""
API endpoints для оценки валютных форвардов.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from src.services.forward_service import calculate_forward_valuation
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ForwardValuationRequest(BaseModel):
    """Запрос на оценку форварда."""
    forwardType: str = Field("fx", description="Тип форварда: fx, bond, commodity, equity, rate")
    # Общие параметры
    spotPrice: float = Field(..., description="Спот цена базового актива")
    timeToMaturity: float = Field(..., description="Время до экспирации (лет)")
    marketForwardPrice: float = Field(..., description="Рыночная цена форварда")
    contractSize: float = Field(1.0, description="Размер контракта")
    
    # Параметры для Cost-of-Carry (bond, commodity, equity, rate)
    dividendYield: Optional[float] = Field(0.0, description="Дивиденды / Купоны (%)")
    carryingCost: Optional[float] = Field(0.0, description="Стоимость хранения (%)")
    convenienceYield: Optional[float] = Field(0.0, description="Удобство владения (Convenience Yield, %)")
    riskFreeRate: Optional[float] = Field(None, description="Безрисковая ставка (%)")
    repoRate: Optional[float] = Field(None, description="Репо ставка (%)")
    
    # Параметры для форварда на облигацию (bond)
    accruedInterest: Optional[float] = Field(0.0, description="Накопленный купонный доход (AI)")
    couponRate: Optional[float] = Field(None, description="Купонная ставка (годовая, %)")
    couponFrequency: Optional[int] = Field(2, description="Частота выплаты купонов (1, 2, 4, 12 - раз в год)")
    faceValue: Optional[float] = Field(100.0, description="Номинал облигации")
    lastCouponDate: Optional[str] = Field(None, description="Дата последнего купона (YYYY-MM-DD)")
    maturityDate: Optional[str] = Field(None, description="Дата погашения облигации (YYYY-MM-DD)")
    dayCountConvention: Optional[str] = Field("ACT/365", description="Конвенция подсчета дней: ACT/ACT, ACT/365, ACT/360, 30/360")
    autoCalculateAI: Optional[bool] = Field(True, description="Автоматически рассчитывать НКД из даты последнего купона")
    yieldCurveTenors: Optional[list[float]] = Field(None, description="Теноры кривой доходности (в годах)")
    yieldCurveRates: Optional[list[float]] = Field(None, description="Ставки кривой доходности (в процентах)")
    
    # Параметры для валютных форвардов (fx)
    buyCurrency: Optional[str] = Field(None, description="Покупаемая валюта (для fx)")
    sellCurrency: Optional[str] = Field(None, description="Продаваемая валюта (для fx)")
    buyAmount: Optional[float] = Field(None, description="Сумма покупки (для fx)")
    sellAmount: Optional[float] = Field(None, description="Сумма продажи (для fx)")
    dealDate: Optional[str] = Field(None, description="Дата сделки (YYYY-MM-DD, для fx)")
    valuationDate: Optional[str] = Field(None, description="Дата оценки (YYYY-MM-DD, для fx)")
    expirationDate: Optional[str] = Field(None, description="Дата экспирации (YYYY-MM-DD, для fx)")
    settlementCurrency: Optional[str] = Field("RUB", description="Валюта расчетов (для fx)")
    internalRate: Optional[float] = Field(None, description="Ставка для покупаемой валюты (%) (для fx)")
    externalRate: Optional[float] = Field(None, description="Ставка для продаваемой валюты (%) (для fx)")


@router.post("/valuate", response_model=Dict[str, Any])
async def valuate_forward(request: ForwardValuationRequest):
    """
    Выполняет оценку форварда различных типов.
    """
    try:
        # ОТЛАДКА: Логируем входные параметры для диагностики бага NPV
        if request.forwardType == "fx" and request.buyAmount:
            logger.info(f"API Debug - buyAmount={request.buyAmount:,.2f}, buyCurrency={request.buyCurrency}, "
                       f"sellCurrency={request.sellCurrency}, spotPrice={request.spotPrice:.6f}, "
                       f"marketForwardPrice={request.marketForwardPrice:.6f}")
        
        result = calculate_forward_valuation(
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
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check для сервиса форвардов."""
    return {"status": "ok", "service": "forward"}
