"""
API endpoints для оценки свопов (IRS, CDS, Basis Swaps).
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from src.services.swap_service import calculate_swap_valuation

router = APIRouter()


class SwapValuationRequest(BaseModel):
    """Запрос на оценку свопа."""
    notional: float = Field(..., description="Номинал (млн)")
    tenor: float = Field(..., description="Срок (годы)")
    fixedRate: float = Field(..., description="Фиксированная ставка (%)")
    floatingRate: float = Field(..., description="Индекс плавающей ставки (%)")
    spread: float = Field(0.0, description="Спред (bp)")
    couponsPerYear: int = Field(2, description="Купонов в год")
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


@router.get("/health")
async def health_check():
    """Health check для сервиса свопов."""
    return {"status": "ok", "service": "swap"}
