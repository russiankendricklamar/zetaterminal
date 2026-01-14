"""
API endpoints для оценки облигаций (DCF).
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from src.services.bond_service import calculate_bond_valuation, get_market_yield_from_moex
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class BondValuationRequest(BaseModel):
    """Запрос на оценку облигации."""
    secid: str = Field(..., description="ISIN облигации (например, RU000A10AU99)")
    valuationDate: str = Field(..., description="Дата оценки (YYYY-MM-DD)")
    discountYield1: float = Field(..., description="Ставка дисконтирования для сценария 1 (доходность аналога) в процентах")
    discountYield2: float = Field(..., description="Ставка дисконтирования для сценария 2 (доходность индекса) в процентах")
    dayCount: Optional[int] = Field(None, description="Базис расчета: 365 (ACT/365) или 360 (30/360) - устаревший параметр")
    dayCountConvention: Optional[str] = Field(None, description="Базис расчета: 'Actual/365F', 'Actual/360', 'Actual/Actual (ISDA)', '30/360 (US)', '30E/360 (ISDA)', '30E/360', 'Actual/Actual (ISMA)'")


@router.post("/valuate", response_model=Dict[str, Any])
async def valuate_bond(request: BondValuationRequest):
    """
    Выполняет оценку облигации для двух сценариев доходности.
    """
    try:
        result = calculate_bond_valuation(
            secid=request.secid,
            valuation_date=request.valuationDate,
            discount_yield1=request.discountYield1,
            discount_yield2=request.discountYield2,
            day_count=request.dayCount,
            day_count_convention=request.dayCountConvention
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/market-yield", response_model=Dict[str, Any])
async def get_market_yield(
    secid: str = Query(..., description="ISIN облигации"),
    date: str = Query(..., description="Дата оценки (YYYY-MM-DD)")
):
    """
    Получает рыночную доходность облигации из MOEX API на указанную дату.
    
    Args:
        secid: ISIN облигации
        date: Дата оценки в формате YYYY-MM-DD
        
    Returns:
        Словарь с рыночной доходностью (в процентах)
    """
    try:
        yield_value = get_market_yield_from_moex(secid, date)
        return {
            "secid": secid,
            "date": date,
            "yield": yield_value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting market yield for {secid} on {date}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
