"""
Pydantic schemas for database records.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BondValuationRecord(BaseModel):
    """Model for storing bond valuation results."""
    id: int | None = None
    secid: str = Field(..., description="ISIN облигации")
    valuation_date: str = Field(..., description="Дата оценки (YYYY-MM-DD)")
    discount_yield1: float = Field(..., description="Ставка дисконтирования сценарий 1 (%)")
    discount_yield2: float = Field(..., description="Ставка дисконтирования сценарий 2 (%)")
    dirty_price: float = Field(..., description="Грязная цена")
    clean_price: float = Field(..., description="Чистая цена")
    ytm: float = Field(..., description="Доходность к погашению (%)")
    duration: float = Field(..., description="Дюрация Маколея (лет)")
    modified_duration: float | None = Field(None, description="Модифицированная дюрация")
    convexity: float | None = Field(None, description="Выпуклость")
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class PortfolioRecord(BaseModel):
    """Model for storing portfolio data."""
    id: int | None = None
    name: str = Field(..., description="Название портфеля")
    description: str | None = None
    positions: dict[str, Any] = Field(..., description="Позиции портфеля (JSON)")
    total_value: float = Field(..., description="Общая стоимость")
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class CalculationHistory(BaseModel):
    """Model for storing calculation history."""
    id: int | None = None
    calculation_type: str = Field(..., description="Тип расчета (bond, portfolio, stress, etc.)")
    input_data: dict[str, Any] = Field(..., description="Входные данные (JSON)")
    result_data: dict[str, Any] = Field(..., description="Результаты расчета (JSON)")
    execution_time_ms: float | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class MarketDataDaily(BaseModel):
    """Model for daily market data."""
    id: int | None = None
    ticker: str = Field(..., description="Тикер инструмента")
    data_type: str = Field(..., description="Тип данных: stock, bond, currency, index, crypto")
    date: str = Field(..., description="Дата (YYYY-MM-DD)")
    price: float | None = Field(None, description="Цена")
    volume: int | None = Field(None, description="Объем торгов")
    change_percent: float | None = Field(None, description="Изменение в %")
    metadata: dict[str, Any] | None = Field(default_factory=dict, description="Дополнительные данные")
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class FileRecord(BaseModel):
    """Model for file metadata."""
    id: int | None = None
    file_name: str = Field(..., description="Имя файла")
    file_path: str = Field(..., description="Путь в хранилище")
    file_type: str = Field(..., description="Тип файла: register, report, export, etc.")
    file_size: int = Field(..., description="Размер файла в байтах")
    mime_type: str | None = Field(None, description="MIME тип")
    description: str | None = None
    metadata: dict[str, Any] | None = Field(default_factory=dict)
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
