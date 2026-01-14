"""
Сервис для оценки облигаций (DCF).
Использует bond_pricing.py для расчетов.
"""
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def get_market_yield_from_moex(secid: str, valuation_date: str) -> Optional[float]:
    """
    Получает рыночную доходность облигации из MOEX ISS API на указанную дату.
    
    Args:
        secid: ISIN облигации
        valuation_date: Дата оценки в формате YYYY-MM-DD
        
    Returns:
        Рыночная доходность в процентах или None, если не найдена
    """
    try:
        import requests
        import pandas as pd
        from datetime import datetime, timedelta
        
        BASE_ISS = "https://iss.moex.com/iss"
        
        # Преобразуем дату
        val_date = pd.to_datetime(valuation_date)
        
        # Ищем данные за дату оценки и несколько дней до/после (на случай выходных)
        date_from = (val_date - timedelta(days=5)).strftime("%Y-%m-%d")
        date_to = (val_date + timedelta(days=5)).strftime("%Y-%m-%d")
        
        # Получаем исторические данные по облигации
        url = (
            f"{BASE_ISS}/history/engines/stock/markets/bonds/securities/{secid}.json"
            f"?from={date_from}&till={date_to}"
            "&iss.meta=off"
            "&history.columns=TRADEDATE,CLOSE,YIELD"
        )
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "history" not in data or not data["history"]["data"]:
            return None
        
        # Преобразуем в DataFrame
        history_df = pd.DataFrame(
            data["history"]["data"],
            columns=data["history"]["columns"]
        )
        
        if history_df.empty:
            return None
        
        # Преобразуем даты
        history_df["TRADEDATE"] = pd.to_datetime(history_df["TRADEDATE"])
        
        # Ищем данные за дату оценки или ближайшую дату до неё
        history_df = history_df[history_df["TRADEDATE"] <= val_date]
        
        if history_df.empty:
            return None
        
        # Берем последнюю доступную дату
        latest_row = history_df.iloc[-1]
        
        # Проверяем наличие колонки YIELD
        if "YIELD" in latest_row and pd.notna(latest_row["YIELD"]):
            yield_value = float(latest_row["YIELD"])
            # MOEX возвращает доходность в процентах
            return yield_value
        
        # Если YIELD нет, пытаемся рассчитать из цены
        if "CLOSE" in latest_row and pd.notna(latest_row["CLOSE"]):
            # Здесь можно добавить расчет YTM из цены, но это сложнее
            # Пока возвращаем None
            return None
        
        return None
        
    except Exception as e:
        logger.error(f"Error fetching market yield from MOEX for {secid} on {valuation_date}: {e}")
        return None


def determine_market_activity(
    secid: str,
    market_yield: Optional[float] = None,
    trading_volume: Optional[float] = None,
    bid_ask_spread: Optional[float] = None,
    days_since_last_trade: Optional[int] = None
) -> str:
    """
    Определяет активность рынка для облигации.
    
    Критерии будут добавлены позже. Пока возвращает 'unknown'.
    
    Args:
        secid: ISIN облигации
        market_yield: Рыночная доходность (%)
        trading_volume: Объем торгов за период
        bid_ask_spread: Спред между bid и ask (bp)
        days_since_last_trade: Количество дней с последней сделки
        
    Returns:
        'high', 'medium', 'low', или 'unknown'
    """
    # TODO: Реализовать критерии определения активности рынка
    # Пока возвращаем 'unknown' как заглушку
    
    if market_yield is None:
        return 'unknown'
    
    # Временная логика (будет заменена на реальные критерии)
    # Пример: если есть рыночная доходность, считаем активность средней
    if market_yield > 0:
        # Здесь будут реальные критерии:
        # - Объем торгов
        # - Частота сделок
        # - Спред bid/ask
        # - Ликвидность
        return 'medium'
    
    return 'unknown'

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
