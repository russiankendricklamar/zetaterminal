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
    from bond_pricing import BondPricer
except ImportError:
    # Fallback если модуль не найден
    BondPricer = None


def calculate_bond_valuation(
    secid: str,
    valuation_date: str,
    discount_yield1: float,
    discount_yield2: float,
    day_count: int = 365
) -> Dict:
    """
    Рассчитывает оценку облигации для двух сценариев доходности.
    
    Args:
        secid: ISIN облигации
        valuation_date: Дата оценки (YYYY-MM-DD)
        discount_yield1: Ставка дисконтирования для сценария 1 (доходность аналога) в процентах
        discount_yield2: Ставка дисконтирования для сценария 2 (доходность индекса) в процентах
        day_count: Базис расчета (365 или 360)
    
    Returns:
        Результаты оценки для обоих сценариев
    """
    if BondPricer is None:
        raise ValueError("Модуль bond_pricing не найден. Убедитесь, что файл bond_pricing.py находится в корне backend.")
    
    # Конвертируем дату
    valuation_date_ts = pd.to_datetime(valuation_date)
    
    # Загружаем данные облигации
    from_date = "2000-01-01"  # Начальная дата для загрузки данных
    bond_data = BondPricer.fetch_bond_data(secid, from_date=from_date, day_count=day_count)
    
    # Конвертируем доходности из процентов в доли (для формулы)
    # В bond_pricing используется формула с годовыми процентами, поэтому передаем как есть
    yield1_decimal = discount_yield1 / 100.0
    yield2_decimal = discount_yield2 / 100.0
    
    # Рассчитываем метрики для обоих сценариев
    metrics1 = BondPricer.calculate_metrics(
        bond_data=bond_data,
        valuation_date=valuation_date_ts,
        discount_yield=yield1_decimal,
        day_count=day_count
    )
    
    metrics2 = BondPricer.calculate_metrics(
        bond_data=bond_data,
        valuation_date=valuation_date_ts,
        discount_yield=yield2_decimal,
        day_count=day_count
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
            "duration": metrics1["duration"]
        },
        "scenario2": {
            "dirtyPrice": metrics2["dirtyPrice"],
            "cleanPrice": metrics2["cleanPrice"],
            "pricePercent": metrics2["pricePercent"],
            "duration": metrics2["duration"]
        },
        "cashFlows1": metrics1["cashFlows"],
        "cashFlows2": metrics2["cashFlows"],
        "allCoupons": metrics1["allCoupons"]  # График купонов одинаковый для обоих сценариев
    }
