"""
API endpoints для работы с кривой бескупонных доходностей (КБД) из MOEX ISS API.

Endpoints:
- GET /zcyc - Получить кривую бескупонных доходностей на указанную дату
- GET /zcyc/interpolate - Интерполировать доходность для заданного срока
- GET /zcyc/dates - Получить список доступных дат
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

router = APIRouter()


class ZCYCPoint(BaseModel):
    """Точка на кривой бескупонных доходностей."""
    term: float = Field(..., description="Срок в годах")
    value: float = Field(..., description="Доходность в процентах (годовая)")


class ZCYCResponse(BaseModel):
    """Ответ с данными кривой бескупонных доходностей."""
    status: str
    date: str
    data: List[ZCYCPoint]
    count: int
    min_term: float
    max_term: float
    min_rate: float
    max_rate: float
    mean_rate: float
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "date": "2026-01-03",
                "data": [
                    {"term": 0.083, "value": 13.45},
                    {"term": 0.25, "value": 13.52},
                    {"term": 0.5, "value": 13.68}
                ],
                "count": 12,
                "min_term": 0.083,
                "max_term": 30.0,
                "min_rate": 13.45,
                "max_rate": 14.82,
                "mean_rate": 14.12
            }
        }


class InterpolateRequest(BaseModel):
    """Запрос на интерполяцию доходности."""
    term: float = Field(..., ge=0.0, description="Срок в годах")
    method: str = Field(default="linear", description="Метод интерполяции: linear или nelson_siegel")


class InterpolateResponse(BaseModel):
    """Ответ с интерполированной доходностью."""
    term: float
    value: float
    method: str
    interpolated: bool


@router.get("/zcyc", response_model=ZCYCResponse)
async def get_zcyc(
    date: Optional[str] = Query(None, description="Дата в формате YYYY-MM-DD. Если не указана, используется последняя доступная")
):
    """
    Получить кривую бескупонных доходностей из MOEX ISS API.
    
    MOEX предоставляет кривую, которая уже интерполирована методом Нельсона-Сигеля.
    Данные возвращаются в виде точек (срок в годах, доходность в процентах).
    
    Parameters:
        date: Дата кривой в формате YYYY-MM-DD (опционально)
    
    Returns:
        Данные кривой бескупонных доходностей
    """
    try:
        from src.services.zcyc_service import fetch_zcyc_from_moex
        
        # Валидация даты
        if date:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Неверный формат даты. Используйте YYYY-MM-DD"
                )
        
        result = fetch_zcyc_from_moex(date=date)
        
        if result['status'] == 'error':
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Ошибка получения данных из MOEX')
            )
        
        return ZCYCResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения кривой бескупонных доходностей: {str(e)}"
        )


@router.post("/zcyc/interpolate", response_model=InterpolateResponse)
async def interpolate_zcyc_rate(
    term: float = Query(..., ge=0.0, description="Срок в годах"),
    method: str = Query("linear", description="Метод интерполяции: linear или nelson_siegel"),
    date: Optional[str] = Query(None, description="Дата кривой в формате YYYY-MM-DD")
):
    """
    Интерполировать доходность для заданного срока.
    
    MOEX уже предоставляет интерполированную кривую методом Нельсона-Сигеля,
    но для промежуточных значений между точками можно использовать
    дополнительную линейную интерполяцию.
    
    Parameters:
        term: Срок в годах
        method: Метод интерполяции (linear или nelson_siegel)
        date: Дата кривой (опционально)
    
    Returns:
        Интерполированная доходность
    """
    try:
        from src.services.zcyc_service import fetch_zcyc_from_moex, interpolate_zcyc_rate
        
        # Получаем кривую
        zcyc_result = fetch_zcyc_from_moex(date=date)
        
        if zcyc_result['status'] == 'error':
            raise HTTPException(
                status_code=500,
                detail=zcyc_result.get('error', 'Ошибка получения данных из MOEX')
            )
        
        # Проверяем, что срок в допустимом диапазоне
        if term < zcyc_result['min_term'] or term > zcyc_result['max_term']:
            raise HTTPException(
                status_code=400,
                detail=f"Срок {term} лет вне допустимого диапазона [{zcyc_result['min_term']}, {zcyc_result['max_term']}]"
            )
        
        # Интерполируем
        interpolated_value = interpolate_zcyc_rate(
            zcyc_result['data'],
            term,
            method=method
        )
        
        if interpolated_value is None:
            raise HTTPException(
                status_code=500,
                detail="Не удалось интерполировать доходность"
            )
        
        # Проверяем, была ли это интерполяция или точное совпадение
        is_interpolated = True
        for point in zcyc_result['data']:
            if abs(point['term'] - term) < 0.0001:
                is_interpolated = False
                break
        
        return InterpolateResponse(
            term=term,
            value=interpolated_value,
            method=method,
            interpolated=is_interpolated
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка интерполяции: {str(e)}"
        )


@router.get("/zcyc/dates")
async def get_available_dates():
    """
    Получить список доступных дат для кривой бескупонных доходностей.
    
    Returns:
        Список дат в формате YYYY-MM-DD
    """
    try:
        from src.services.zcyc_service import get_available_zcyc_dates
        
        dates = get_available_zcyc_dates()
        return {
            "success": True,
            "dates": dates,
            "count": len(dates)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения списка дат: {str(e)}"
        )
