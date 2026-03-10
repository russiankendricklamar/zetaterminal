"""
API endpoints для оценки свопов (IRS, CDS, Basis Swaps, FX Swaps).
"""
import logging

from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any, List
from pydantic import Field
from src.services.swap_service import calculate_swap_valuation, calculate_fx_swap_valuation
from src.utils.financial_validation import FinancialBaseModel, MAX_NOTIONAL, MAX_TENOR_YEARS, MAX_RATE_PCT

logger = logging.getLogger(__name__)

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
    volatility: Optional[float] = Field(None, ge=0, le=500, description="Волатильность (%)")
    swapType: str = Field("irs", description="Тип свопа: irs, cds, basis, xccy")


@router.post("/valuate", response_model=Dict[str, Any])
async def valuate_swap(request: SwapValuationRequest):
    """
    Выполняет оценку свопа.
    """
    try:
        result = calculate_swap_valuation(
            notional=request.notional,
            tenor=request.tenor,
            fixed_rate=request.fixedRate,
            floating_rate=request.floatingRate,
            spread=request.spread,
            coupons_per_year=request.couponsPerYear,
            discount_rate=request.discountRate,
            volatility=request.volatility,
            swap_type=request.swapType
        )
        return result
    except ValueError as e:
        logger.error("Swap valuation validation error: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid input parameters")
    except RuntimeError as e:
        logger.error("Swap valuation runtime error: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Calculation error")
    except Exception as e:
        logger.error("Swap valuation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


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


@router.post("/valuate-fx", response_model=Dict[str, Any])
async def valuate_fx_swap(request: FxSwapValuationRequest):
    """Выполняет оценку FX-свопа."""
    try:
        result = calculate_fx_swap_valuation(
            buy_currency_near=request.nearLeg.buyCurrency,
            sell_currency_near=request.nearLeg.sellCurrency,
            nominal_buy_near=request.nearLeg.nominalBuy,
            nominal_sell_near=request.nearLeg.nominalSell,
            date_near=request.nearLeg.date,
            buy_currency_far=request.farLeg.buyCurrency,
            sell_currency_far=request.farLeg.sellCurrency,
            nominal_buy_far=request.farLeg.nominalBuy,
            nominal_sell_far=request.farLeg.nominalSell,
            date_far=request.farLeg.date,
            valuation_date=request.valuationDate,
            settlement_currency=request.settlementCurrency,
            spot_min=request.spotMin,
            spot_max=request.spotMax,
            rate_internal=request.rateInternal,
            rate_external=request.rateExternal,
        )
        return result
    except ValueError as e:
        logger.error("FX swap valuation validation error: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid input parameters")
    except Exception as e:
        logger.error("FX swap valuation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """Health check для сервиса свопов."""
    return {"status": "ok", "service": "swap"}
