"""
API endpoints для оценки свопов (IRS, CDS, Basis Swaps, FX Swaps).
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from src.services.swap_service import calculate_swap_valuation, calculate_fx_swap_valuation

router = APIRouter()


class SwapValuationRequest(BaseModel):
    """Запрос на оценку свопа."""
    notional: float = Field(..., description="Номинал (млн)")
    tenor: float = Field(..., description="Срок (годы)")
    fixedRate: float = Field(..., description="Фиксированная ставка (%)")
    floatingRate: float = Field(..., description="Индекс плавающей ставки (%)")
    spread: float = Field(0.0, description="Спред (bp)")
    couponsPerYear: int = Field(2, gt=0, description="Купонов в год")
    discountRate: float = Field(..., description="Дисконт кривая (базовая ставка, %)")
    volatility: Optional[float] = Field(None, description="Волатильность (%)")
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
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


class FxSwapLeg(BaseModel):
    """Одна нога FX-свопа."""
    buyCurrency: str = Field(..., description="Валюта покупки")
    sellCurrency: str = Field(..., description="Валюта продажи")
    nominalBuy: float = Field(..., description="Сумма покупки")
    nominalSell: float = Field(..., description="Сумма продажи")
    date: str = Field(..., description="Дата расчёта (YYYY-MM-DD)")


class FxSwapValuationRequest(BaseModel):
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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check для сервиса свопов."""
    return {"status": "ok", "service": "swap"}
