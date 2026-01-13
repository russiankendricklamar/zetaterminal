"""
Сервис для оценки облигаций (DCF).
Использует bond_pricing.py для расчетов.
"""
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

# Добавляем корневую директорию backend в путь для импорта bond_pricing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

try:
    from bond_pricing import BondPricer, DayCountConvention
except ImportError:
    # Fallback если модуль не найден
    BondPricer = None
    DayCountConvention = None


def calculate_bond_valuation(
    secid: str,
    valuation_date: str,
    discount_yield1: float,
    discount_yield2: float,
    day_count: Optional[int] = None,
    day_count_convention: Optional[str] = None
) -> Dict:
    """
    Рассчитывает оценку облигации для двух сценариев доходности.
    
    Args:
        secid: ISIN облигации
        valuation_date: Дата оценки (YYYY-MM-DD)
        discount_yield1: Ставка дисконтирования для сценария 1 (доходность аналога) в процентах
        discount_yield2: Ставка дисконтирования для сценария 2 (доходность индекса) в процентах
        day_count: Базис расчета (365 или 360) - устаревший параметр, используется для обратной совместимости
        day_count_convention: Базис расчета (например, "Actual/365F", "Actual/360", "Actual/Actual (ISDA)")
    
    Returns:
        Результаты оценки для обоих сценариев
    """
    if BondPricer is None:
        raise ValueError("Модуль bond_pricing не найден. Убедитесь, что файл bond_pricing.py находится в корне backend.")
    
    # Определяем базис расчета
    if day_count_convention:
        # Парсим строку в DayCountConvention
        try:
            convention = DayCountConvention(day_count_convention)
        except (ValueError, TypeError):
            # Если не удалось распарсить, используем по умолчанию
            convention = DayCountConvention.ACTUAL_365F
    elif day_count:
        # Обратная совместимость: преобразуем старый параметр
        if day_count == 360:
            convention = DayCountConvention.ACTUAL_360
        else:
            convention = DayCountConvention.ACTUAL_365F
    else:
        convention = DayCountConvention.ACTUAL_365F  # По умолчанию
    
    # Для fetch_bond_data используем day_count для определения частоты выплат (обратная совместимость)
    day_count_for_fetch = 365 if day_count is None else day_count
    
    # Конвертируем дату
    valuation_date_ts = pd.to_datetime(valuation_date)
    
    # Загружаем данные облигации
    from_date = "2000-01-01"  # Начальная дата для загрузки данных
    bond_data = BondPricer.fetch_bond_data(secid, from_date=from_date, day_count=day_count_for_fetch)
    
    # Определяем период купона в месяцах для ISMA базиса
    coupon_period_months = None
    if convention == DayCountConvention.ACTUAL_ACTUAL_ISMA:
        if len(bond_data["coupon_dates_full"]) >= 2:
            period_days = (bond_data["coupon_dates_full"][1] - bond_data["coupon_dates_full"][0]).days
            # Примерная оценка периода в месяцах
            coupon_period_months = round(period_days / 30.44)  # Среднее количество дней в месяце
    
    # Конвертируем доходности из процентов в доли (для формулы)
    # В bond_pricing используется формула с годовыми процентами, поэтому передаем как есть
    yield1_decimal = discount_yield1 / 100.0
    yield2_decimal = discount_yield2 / 100.0
    
    # Рассчитываем метрики для обоих сценариев
    metrics1 = BondPricer.calculate_metrics(
        bond_data=bond_data,
        valuation_date=valuation_date_ts,
        discount_yield=yield1_decimal,
        day_count_convention=convention,
        coupon_period_months=coupon_period_months
    )
    
    metrics2 = BondPricer.calculate_metrics(
        bond_data=bond_data,
        valuation_date=valuation_date_ts,
        discount_yield=yield2_decimal,
        day_count_convention=convention,
        coupon_period_months=coupon_period_months
    )
    
    # Формируем результат
    return {
        "secid": secid,
        "faceValue": float(bond_data["face_value"]),
        "couponPercent": float(bond_data["coupon_percent"]),
        "issueDate": bond_data["issue_date"].isoformat(),
        "maturityDate": bond_data["mat_date"].isoformat(),
        "paymentsPerYear": int(bond_data["payments_per_year"]),
        "accruedInterest": metrics1["accruedInterest"],  # НКД одинаковый для обоих сценариев
        "scenario1": {
            "dirtyPrice": metrics1["dirtyPrice"],
            "cleanPrice": metrics1["cleanPrice"],
            "pricePercent": metrics1["pricePercent"],
            "currentYield": metrics1.get("currentYield", 0.0),
            "adjustedCurrentYield": metrics1.get("adjustedCurrentYield", 0.0),
            "simpleYield": metrics1.get("simpleYield", 0.0),
            "ytm": metrics1.get("ytm", 0.0),
            "ytmPercent": metrics1.get("ytmPercent", 0.0),
            "nominalYield": metrics1.get("nominalYield", 0.0),
            "duration": metrics1["duration"],
            "modifiedDuration": metrics1.get("modifiedDuration", 0.0),
            "convexity": metrics1.get("convexity", 0.0),
            "pvbp": metrics1.get("pvbp", 0.0),
            "pvbpAbsolute": metrics1.get("pvbpAbsolute", 0.0),
            "sensitivityScenarios": metrics1.get("sensitivityScenarios", []),
            "discountMargin": metrics1.get("discountMargin")
        },
        "scenario2": {
            "dirtyPrice": metrics2["dirtyPrice"],
            "cleanPrice": metrics2["cleanPrice"],
            "pricePercent": metrics2["pricePercent"],
            "currentYield": metrics2.get("currentYield", 0.0),
            "adjustedCurrentYield": metrics2.get("adjustedCurrentYield", 0.0),
            "simpleYield": metrics2.get("simpleYield", 0.0),
            "ytm": metrics2.get("ytm", 0.0),
            "ytmPercent": metrics2.get("ytmPercent", 0.0),
            "nominalYield": metrics2.get("nominalYield", 0.0),
            "duration": metrics2["duration"],
            "modifiedDuration": metrics2.get("modifiedDuration", 0.0),
            "convexity": metrics2.get("convexity", 0.0),
            "pvbp": metrics2.get("pvbp", 0.0),
            "pvbpAbsolute": metrics2.get("pvbpAbsolute", 0.0),
            "sensitivityScenarios": metrics2.get("sensitivityScenarios", []),
            "discountMargin": metrics2.get("discountMargin")
        },
        "cashFlows1": metrics1["cashFlows"],
        "cashFlows2": metrics2["cashFlows"],
        "allCoupons": metrics1["allCoupons"]  # График купонов одинаковый для обоих сценариев
    }
