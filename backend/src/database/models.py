"""
Database models and schemas for Supabase tables.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class BondValuationRecord(BaseModel):
    """Model for storing bond valuation results."""
    id: Optional[int] = None
    secid: str = Field(..., description="ISIN облигации")
    valuation_date: str = Field(..., description="Дата оценки (YYYY-MM-DD)")
    discount_yield1: float = Field(..., description="Ставка дисконтирования сценарий 1 (%)")
    discount_yield2: float = Field(..., description="Ставка дисконтирования сценарий 2 (%)")
    dirty_price: float = Field(..., description="Грязная цена")
    clean_price: float = Field(..., description="Чистая цена")
    ytm: float = Field(..., description="Доходность к погашению (%)")
    duration: float = Field(..., description="Дюрация Маколея (лет)")
    modified_duration: Optional[float] = Field(None, description="Модифицированная дюрация")
    convexity: Optional[float] = Field(None, description="Выпуклость")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PortfolioRecord(BaseModel):
    """Model for storing portfolio data."""
    id: Optional[int] = None
    name: str = Field(..., description="Название портфеля")
    description: Optional[str] = None
    positions: Dict[str, Any] = Field(..., description="Позиции портфеля (JSON)")
    total_value: float = Field(..., description="Общая стоимость")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CalculationHistory(BaseModel):
    """Model for storing calculation history."""
    id: Optional[int] = None
    calculation_type: str = Field(..., description="Тип расчета (bond, portfolio, stress, etc.)")
    input_data: Dict[str, Any] = Field(..., description="Входные данные (JSON)")
    result_data: Dict[str, Any] = Field(..., description="Результаты расчета (JSON)")
    execution_time_ms: Optional[float] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MarketDataDaily(BaseModel):
    """Model for daily market data."""
    id: Optional[int] = None
    ticker: str = Field(..., description="Тикер инструмента")
    data_type: str = Field(..., description="Тип данных: stock, bond, currency, index, crypto")
    date: str = Field(..., description="Дата (YYYY-MM-DD)")
    price: Optional[float] = Field(None, description="Цена")
    volume: Optional[int] = Field(None, description="Объем торгов")
    change_percent: Optional[float] = Field(None, description="Изменение в %")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Дополнительные данные")
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FileRecord(BaseModel):
    """Model for file metadata."""
    id: Optional[int] = None
    file_name: str = Field(..., description="Имя файла")
    file_path: str = Field(..., description="Путь в хранилище")
    file_type: str = Field(..., description="Тип файла: register, report, export, etc.")
    file_size: int = Field(..., description="Размер файла в байтах")
    mime_type: Optional[str] = Field(None, description="MIME тип")
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
