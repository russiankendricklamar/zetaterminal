"""
Модуль оценки облигаций через доходный подход (DCF)
Использует данные MOEX ISS API.
"""

import logging
import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

BASE_ISS = "https://iss.moex.com/iss"


class DayCountConvention(Enum):
    """Базисы расчета дней в году"""
    ACTUAL_365F = "Actual/365F"  # Fixed 365
    ACTUAL_360 = "Actual/360"
    ACTUAL_ACTUAL_ISDA = "Actual/Actual (ISDA)"
    THIRTY_360_US = "30/360 (US)"  # US Municipal Bond Basis
    THIRTY_E_360_ISDA = "30E/360 (ISDA)"  # German
    THIRTY_E_360 = "30E/360"  # Eurobond Basis
    ACTUAL_ACTUAL_ISMA = "Actual/Actual (ISMA)"


class DayCountCalculator:
    """Класс для расчета годовых долей по различным базисам"""
    
    @staticmethod
    def _is_leap_year(year: int) -> bool:
        """Проверка на високосный год"""
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    
    @staticmethod
    def _days_in_year(year: int) -> int:
        """Количество дней в году"""
        return 366 if DayCountCalculator._is_leap_year(year) else 365
    
    @staticmethod
    def _get_last_day_of_february(year: int) -> int:
        """Последний день февраля"""
        return 29 if DayCountCalculator._is_leap_year(year) else 28
    
    @staticmethod
    def actual_365f(start_date: pd.Timestamp, end_date: pd.Timestamp) -> float:
        """
        Actual/365F (Fixed)
        Base: 365 дней в году (всегда)
        Formula: days_between(d1, d2) / 365
        Usage: Российский рынок, еврооблигации
        """
        days = (end_date - start_date).days
        return days / 365.0
    
    @staticmethod
    def actual_360(start_date: pd.Timestamp, end_date: pd.Timestamp) -> float:
        """
        Actual/360
        Base: 360 дней в году
        Formula: days_between(d1, d2) / 360
        Usage: денежный рынок, еврооблигации
        """
        days = (end_date - start_date).days
        return days / 360.0
    
    @staticmethod
    def actual_actual_isda(start_date: pd.Timestamp, end_date: pd.Timestamp) -> float:
        """
        Actual/Actual (ISDA)
        Base: 366 для високосных лет, 365 для обычных
        Formula: разбить период по годам, для каждого года считать свою базу
        """
        if start_date >= end_date:
            return 0.0
        
        total_fraction = 0.0
        current = start_date
        
        while current < end_date:
            # Определяем конец текущего года
            year_end = pd.Timestamp(year=current.year + 1, month=1, day=1)
            period_end = min(year_end, end_date)
            
            # Дни в текущем году
            days_in_period = (period_end - current).days
            days_in_year = DayCountCalculator._days_in_year(current.year)
            
            total_fraction += days_in_period / days_in_year
            current = period_end
        
        return total_fraction
    
    @staticmethod
    def thirty_360_us(
        start_date: pd.Timestamp, 
        end_date: pd.Timestamp,
        maturity_date: Optional[pd.Timestamp] = None
    ) -> float:
        """
        30/360 (US Municipal Bond Basis)
        Base: 360 дней в году
        Correction rules:
        - D1 = 31 → D1 = 30
        - D2 = 31 AND (D1 = 30 OR D1 = 31) → D2 = 30
        - D1 = last day of Feb → D1 = 30
        - D1 = last day of Feb AND D2 = last day of Feb → D2 = 30
        """
        d1, m1, y1 = start_date.day, start_date.month, start_date.year
        d2, m2, y2 = end_date.day, end_date.month, end_date.year
        
        last_feb_day_d1 = DayCountCalculator._get_last_day_of_february(y1)
        last_feb_day_d2 = DayCountCalculator._get_last_day_of_february(y2)
        
        # Корректировки для D1
        if d1 == 31:
            d1 = 30
        elif m1 == 2 and d1 == last_feb_day_d1:
            d1 = 30
        
        # Корректировки для D2
        if d2 == 31 and (d1 == 30 or d1 == 31):
            d2 = 30
        elif m1 == 2 and d1 == last_feb_day_d1 and m2 == 2 and d2 == last_feb_day_d2:
            d2 = 30
        
        days = (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)
        return days / 360.0
    
    @staticmethod
    def thirty_e_360_isda(
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        maturity_date: Optional[pd.Timestamp] = None
    ) -> float:
        """
        30/360 German (30E/360 ISDA)
        Base: 360 дней в году
        Correction rules:
        - D1 = 31 → D1 = 30
        - D1 = last day of Feb → D1 = 30
        - D2 = 31 → D2 = 30
        - D2 = last day of Feb (если не день погашения) → D2 = 30
        """
        d1, m1, y1 = start_date.day, start_date.month, start_date.year
        d2, m2, y2 = end_date.day, end_date.month, end_date.year
        
        last_feb_day = DayCountCalculator._get_last_day_of_february(y1)
        
        # Корректировки для D1
        if d1 == 31:
            d1 = 30
        elif m1 == 2 and d1 == last_feb_day:
            d1 = 30
        
        # Корректировки для D2
        if d2 == 31:
            d2 = 30
        elif m2 == 2 and d2 == DayCountCalculator._get_last_day_of_february(y2):
            # Проверяем, является ли end_date датой погашения
            if maturity_date is None or end_date.date() != maturity_date.date():
                d2 = 30
        
        days = (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)
        return days / 360.0
    
    @staticmethod
    def thirty_e_360(start_date: pd.Timestamp, end_date: pd.Timestamp) -> float:
        """
        30E/360 (Eurobond Basis)
        Base: 360 дней в году
        Correction rules:
        - D1 = 31 → D1 = 30
        - D2 = 31 → D2 = 30
        """
        d1, m1, y1 = start_date.day, start_date.month, start_date.year
        d2, m2, y2 = end_date.day, end_date.month, end_date.year
        
        # Корректировки
        if d1 == 31:
            d1 = 30
        
        if d2 == 31:
            d2 = 30
        
        days = (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)
        return days / 360.0
    
    @staticmethod
    def actual_actual_isma(
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        coupon_start: Optional[pd.Timestamp] = None,
        coupon_end: Optional[pd.Timestamp] = None,
        coupon_period_months: Optional[int] = None
    ) -> float:
        """
        Actual/Actual (ISMA)
        Base: 365 или 366 дней (зависит от периода купона)
        Formula:
        days_in_coupon_period = days_between(coupon_start, coupon_end)
        coupons_per_year = 12 / coupon_period_months
        year_fraction = days_between(d1, d2) / (days_in_coupon_period * coupons_per_year)
        """
        actual_days = (end_date - start_date).days
        
        if coupon_start is not None and coupon_end is not None:
            days_in_coupon_period = (coupon_end - coupon_start).days
            if coupon_period_months:
                coupons_per_year = 12.0 / coupon_period_months
            else:
                # Пытаемся определить из периода
                period_days = (coupon_end - coupon_start).days
                if period_days > 0:
                    coupons_per_year = 365.25 / period_days
                else:
                    coupons_per_year = 2.0  # Fallback
        else:
            # Если нет информации о купоне, используем среднее
            days_in_coupon_period = 182.5  # Полгода
            coupons_per_year = 2.0
        
        if days_in_coupon_period > 0:
            year_fraction = actual_days / (days_in_coupon_period * coupons_per_year)
        else:
            year_fraction = actual_days / 365.25
        
        return year_fraction
    
    @staticmethod
    def calculate_year_fraction(
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        convention: DayCountConvention,
        **kwargs
    ) -> float:
        """
        Главная функция для расчета годовой доли по указанному базису
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            convention: Базис расчета
            **kwargs: Дополнительные параметры (maturity_date, coupon_start, coupon_end, coupon_period_months)
        
        Returns:
            Годовая доля (year fraction)
        """
        if start_date >= end_date:
            return 0.0
        
        if convention == DayCountConvention.ACTUAL_365F:
            return DayCountCalculator.actual_365f(start_date, end_date)
        
        elif convention == DayCountConvention.ACTUAL_360:
            return DayCountCalculator.actual_360(start_date, end_date)
        
        elif convention == DayCountConvention.ACTUAL_ACTUAL_ISDA:
            return DayCountCalculator.actual_actual_isda(start_date, end_date)
        
        elif convention == DayCountConvention.THIRTY_360_US:
            maturity_date = kwargs.get('maturity_date')
            return DayCountCalculator.thirty_360_us(start_date, end_date, maturity_date)
        
        elif convention == DayCountConvention.THIRTY_E_360_ISDA:
            maturity_date = kwargs.get('maturity_date')
            return DayCountCalculator.thirty_e_360_isda(start_date, end_date, maturity_date)
        
        elif convention == DayCountConvention.THIRTY_E_360:
            return DayCountCalculator.thirty_e_360(start_date, end_date)
        
        elif convention == DayCountConvention.ACTUAL_ACTUAL_ISMA:
            coupon_start = kwargs.get('coupon_start')
            coupon_end = kwargs.get('coupon_end')
            coupon_period_months = kwargs.get('coupon_period_months')
            return DayCountCalculator.actual_actual_isma(
                start_date, end_date, coupon_start, coupon_end, coupon_period_months
            )
        
        else:
            # Fallback к Actual/365F
            return DayCountCalculator.actual_365f(start_date, end_date)


class AccruedInterestCalculator:
    """Класс для расчета накопленного купонного дохода (НКД) различными методами"""
    
    @staticmethod
    def from_coupon_rate(
        coupon_rate_pct: float,
        face_value: float,
        last_coupon_date: pd.Timestamp,
        valuation_date: pd.Timestamp,
        day_count_convention: DayCountConvention,
        **kwargs
    ) -> float:
        """
        Базовая формула НКД от ставки купона
        
        A = C% * NN * (t0 - ti-1) / B
        
        где:
            C% = ставка купона (% годовых)
            NN = номинал облигации
            t0 = дата расчёта
            ti-1 = дата последнего купона
            B = база расчёта (365, 360 и т.д. в зависимости от метода)
        """
        if valuation_date <= last_coupon_date:
            return 0.0
        
        # Вычисляем годовую долю периода начисления
        year_fraction = DayCountCalculator.calculate_year_fraction(
            last_coupon_date,
            valuation_date,
            day_count_convention,
            **kwargs
        )
        
        # Конвертируем ставку из процентов в долю
        coupon_rate_decimal = coupon_rate_pct / 100.0
        
        # НКД = ставка * номинал * доля года
        accrued_interest = coupon_rate_decimal * face_value * year_fraction
        
        return accrued_interest
    
    @staticmethod
    def from_coupon_amount(
        coupon_amount: float,
        last_coupon_date: pd.Timestamp,
        next_coupon_date: pd.Timestamp,
        valuation_date: pd.Timestamp,
        day_count_convention: DayCountConvention,
        **kwargs
    ) -> float:
        """
        Альтернативная формула НКД от суммы купона
        
        A = Ci * (t0 - ti-1) / (ti - ti-1)
        
        где:
            Ci = размер купонного платежа (в денежных единицах)
            ti-1 = дата последнего купона
            t0 = дата расчёта
            ti = дата следующего купона
        """
        if valuation_date <= last_coupon_date or valuation_date >= next_coupon_date:
            return 0.0
        
        # Вычисляем долю прошедшего периода
        elapsed_fraction = DayCountCalculator.calculate_year_fraction(
            last_coupon_date,
            valuation_date,
            day_count_convention,
            **kwargs
        )
        
        # Вычисляем долю полного периода купона
        period_fraction = DayCountCalculator.calculate_year_fraction(
            last_coupon_date,
            next_coupon_date,
            day_count_convention,
            **kwargs
        )
        
        if period_fraction <= 0:
            return 0.0
        
        # НКД = сумма купона * (доля прошедшего периода / доля полного периода)
        accrued_interest = coupon_amount * (elapsed_fraction / period_fraction)
        
        return accrued_interest
    
    @staticmethod
    def floating_rate_in_advance(
        coupon_rate_pct: float,
        face_value: float,
        last_coupon_date: pd.Timestamp,
        valuation_date: pd.Timestamp,
        day_count_convention: DayCountConvention,
        **kwargs
    ) -> float:
        """
        НКД для плавающей ставки (In Advance, без усреднения)
        
        A = C% * NN * (t0 - ti-1) / B
        
        где C% определена в начале купонного периода
        """
        # Для плавающей ставки In Advance ставка известна в начале периода
        # Расчет аналогичен базовой формуле от ставки купона
        return AccruedInterestCalculator.from_coupon_rate(
            coupon_rate_pct,
            face_value,
            last_coupon_date,
            valuation_date,
            day_count_convention,
            **kwargs
        )
    
    @staticmethod
    def floating_rate_in_arrears_average(
        reference_rates: List[float],
        spread_bps: float,
        face_value: float,
        rate_dates: List[pd.Timestamp],
        last_coupon_date: pd.Timestamp,
        valuation_date: pd.Timestamp,
        day_count_convention: DayCountConvention,
        lag_days: int = 0,
        **kwargs
    ) -> float:
        """
        НКД для плавающей ставки (In Arrears, метод Average)
        
        A = NN * sum(Ri + s) / Bi  от i = (ti-1 - l + 1) до (t0 - l)
        
        где:
            Ri = значение референсной ставки на день i
            s = quoted margin (спред) в базисных пунктах
            l = лаг (смещение дня определения ставки)
            Bi = база расчёта на день i
            NN = номинал
        
        Note: Для полной реализации требуется историческая временная серия ставок
        """
        if valuation_date <= last_coupon_date:
            return 0.0
        
        # Определяем период для усреднения
        start_date = last_coupon_date - pd.Timedelta(days=lag_days) + pd.Timedelta(days=1)
        end_date = valuation_date - pd.Timedelta(days=lag_days)
        
        if end_date < start_date:
            return 0.0
        
        # Конвертируем спред из базисных пунктов в проценты
        spread_pct = spread_bps / 100.0
        
        # Усредняем ставки за период
        # Если нет исторических данных, возвращаем 0
        if not reference_rates:
            return 0.0
        
        if not rate_dates or len(rate_dates) != len(reference_rates):
            # Если нет дат или они не совпадают по длине, используем среднее всех ставок
            avg_rate = sum(reference_rates) / len(reference_rates) if reference_rates else 0.0
        else:
            # Фильтруем ставки по периоду
            filtered_rates = []
            for rate, date in zip(reference_rates, rate_dates):
                if start_date <= date <= end_date:
                    filtered_rates.append(rate)
            
            if filtered_rates:
                avg_rate = sum(filtered_rates) / len(filtered_rates)
            else:
                # Fallback: используем среднее всех доступных ставок
                avg_rate = sum(reference_rates) / len(reference_rates)
        
        # Рассчитываем НКД с усредненной ставкой
        total_rate_pct = avg_rate + spread_pct
        
        accrued_interest = AccruedInterestCalculator.from_coupon_rate(
            total_rate_pct,
            face_value,
            last_coupon_date,
            valuation_date,
            day_count_convention,
            **kwargs
        )
        
        return accrued_interest


class YTMCalculator:
    """Класс для расчета доходности к погашению (YTM) методом Ньютона"""
    
    @staticmethod
    def calculate_ytm(
        dirty_price: float,
        cash_flows: List[Dict[str, Any]],  # [{"date": pd.Timestamp, "cf": float}, ...]
        valuation_date: pd.Timestamp,
        day_count_convention: DayCountConvention,
        face_value: float,
        maturity_date: pd.Timestamp,
        coupon_period_months: Optional[int] = None,
        coupon_start: Optional[pd.Timestamp] = None,
        coupon_end: Optional[pd.Timestamp] = None,
        max_iterations: int = 100,
        tolerance: float = 1e-8,
        initial_guess: Optional[float] = None  # Начальное приближение для метода Ньютона
    ) -> float:
        """
        Рассчитывает YTM методом Ньютона
        
        Уравнение: Pd = sum [ (Ci + Ni) / (1 + YTM)^((ti - t0) / B) ]
        
        Args:
            dirty_price: Грязная цена облигации
            cash_flows: Список денежных потоков [{"date": pd.Timestamp, "cf": float}, ...]
            valuation_date: Дата расчета (t0)
            day_count_convention: Базис расчета дней
            face_value: Номинал облигации
            maturity_date: Дата погашения
            coupon_period_months: Период купона в месяцах (для ISMA)
            coupon_start: Дата начала купонного периода (для ISMA)
            coupon_end: Дата конца купонного периода (для ISMA)
            max_iterations: Максимальное количество итераций
            tolerance: Точность сходимости
            initial_guess: Начальное приближение для YTM (по умолчанию 5%)
        
        Returns:
            YTM в десятичном виде (например, 0.176371 для 17.6371%)
        """
        if not cash_flows or dirty_price <= 0:
            return 0.0
        
        # Проверка на бескупонную облигацию (ZCB)
        if len(cash_flows) == 1:
            return YTMCalculator._calculate_zcb_ytm(
                dirty_price=dirty_price,
                face_value=face_value,
                valuation_date=valuation_date,
                maturity_date=maturity_date,
                day_count_convention=day_count_convention,
                coupon_start=coupon_start,
                coupon_end=coupon_end,
                coupon_period_months=coupon_period_months
            )
        
        # Параметры для расчета базиса
        kwargs_for_basis = {
            'maturity_date': maturity_date,
            'coupon_start': coupon_start,
            'coupon_end': coupon_end,
            'coupon_period_months': coupon_period_months
        }
        
        # Начальное приближение: используем переданное значение или 5% по умолчанию
        if initial_guess is not None and -0.9 < initial_guess < 2.0:
            ytm = float(initial_guess)
        else:
            ytm = 0.05
        
        for iteration in range(max_iterations):
            # P(YTM_k) = sum [ (Ci + Ni) / (1 + YTM_k)^((ti - t0) / B) ]
            price_calculated = 0.0
            # P'(YTM_k) = -sum [ ((ti - t0) / B) * (Ci + Ni) / (1 + YTM_k)^(((ti - t0) / B) + 1) ]
            price_derivative = 0.0
            
            for cf in cash_flows:
                cf_date = cf["date"]
                cf_amount = cf["cf"]
                
                # Расчет временного коэффициента (ti - t0) / B
                time_fraction = DayCountCalculator.calculate_year_fraction(
                    valuation_date,
                    cf_date,
                    day_count_convention,
                    **kwargs_for_basis
                )
                
                # Приведенная стоимость потока
                discount_factor = (1.0 + ytm) ** time_fraction
                pv = cf_amount / discount_factor
                price_calculated += pv
                
                # Производная от PV по YTM
                # d/dYTM [CF / (1+YTM)^t] = -t * CF / (1+YTM)^(t+1)
                if discount_factor > 0:
                    pv_derivative = -time_fraction * cf_amount / ((1.0 + ytm) ** (time_fraction + 1))
                    price_derivative += pv_derivative
            
            # Ошибка: разница между расчетной и фактической ценой
            error = price_calculated - dirty_price
            
            # Условие сходимости
            if abs(error) < tolerance:
                break
            
            # Обновление YTM методом Ньютона
            # YTM_{k+1} = YTM_k - (P(YTM_k) - Pd) / P'(YTM_k)
            if abs(price_derivative) > 1e-10:  # Избегаем деления на ноль
                ytm = ytm - (error / price_derivative)
                # Ограничение: YTM не может быть отрицательным
                ytm = max(ytm, -0.99)  # Ограничение до -99%
            else:
                # Если производная слишком мала, используем небольшое приращение
                ytm = ytm + 0.001
        
        return ytm
    
    @staticmethod
    def _calculate_zcb_ytm(
        dirty_price: float,
        face_value: float,
        valuation_date: pd.Timestamp,
        maturity_date: pd.Timestamp,
        day_count_convention: DayCountConvention,
        **kwargs
    ) -> float:
        """
        Расчет YTM для бескупонной облигации (Zero Coupon Bond)
        
        Формула: YTM = [ (N / Pd)^(B / (tm - t0)) - 1 ]
        
        где:
            N = номинал
            Pd = грязная цена
            B = база расчета
            tm = дата погашения
            t0 = дата расчета
        """
        if dirty_price <= 0 or face_value <= 0:
            return 0.0
        
        if valuation_date >= maturity_date:
            return 0.0
        
        # Расчет времени до погашения в годах
        time_to_maturity = DayCountCalculator.calculate_year_fraction(
            valuation_date,
            maturity_date,
            day_count_convention,
            **kwargs
        )
        
        if time_to_maturity <= 0:
            return 0.0
        
        # YTM = [ (N / Pd)^(1 / T) - 1 ]
        ratio = face_value / dirty_price
        ytm = (ratio ** (1.0 / time_to_maturity)) - 1.0
        
        return max(ytm, -0.99)  # Ограничение до -99%
    
    @staticmethod
    def ytm_to_nominal_yield(ytm: float, payments_per_year: int) -> float:
        """
        Преобразование YTM (эффективная годовая доходность) в номинальную доходность (NY)
        
        Формула: NY = n * [ (1 + YTM)^(1/n) - 1 ] * 100%
        
        где:
            n = количество выплат купонов в год
            YTM = доходность к погашению в десятичном виде (не в процентах)
        
        Args:
            ytm: YTM в десятичном виде (например, 0.176371 для 17.6371%)
            payments_per_year: Количество выплат купонов в год
        
        Returns:
            Номинальная доходность в процентах
        """
        if payments_per_year <= 0 or ytm <= -1.0:
            return 0.0
        
        # NY = n * [ (1 + YTM)^(1/n) - 1 ] * 100%
        nominal_yield = payments_per_year * ((1.0 + ytm) ** (1.0 / payments_per_year) - 1.0) * 100.0
        
        return max(nominal_yield, -99.0)  # Ограничение до -99%
    
    @staticmethod
    def nominal_yield_to_ytm(nominal_yield: float, payments_per_year: int) -> float:
        """
        Преобразование номинальной доходности (NY) в YTM (эффективную годовую доходность)
        
        Формула: YTM = [ (1 + NY / (100 * n))^n - 1 ] * 100%
        
        где:
            NY = номинальная доходность в процентах
            n = количество выплат купонов в год
        
        Args:
            nominal_yield: Номинальная доходность в процентах (например, 17.0 для 17%)
            payments_per_year: Количество выплат купонов в год
        
        Returns:
            YTM в десятичном виде
        """
        if payments_per_year <= 0:
            return 0.0
        
        # Конвертируем процент в десятичное значение
        ny_decimal = nominal_yield / 100.0
        
        # YTM = [ (1 + NY / n)^n - 1 ]
        # где NY уже в десятичном виде, поэтому: NY / (100 * n) = ny_decimal / n
        ytm = ((1.0 + ny_decimal / payments_per_year) ** payments_per_year) - 1.0
        
        return max(ytm, -0.99)  # Ограничение до -99%


class DiscountMarginCalculator:
    """Класс для расчета Discount Margin (DM) для облигаций с плавающей ставкой методом Ньютона"""
    
    @staticmethod
    def calculate_discount_margin(
        dirty_price: float,
        cash_flows: List[Dict[str, Any]],  # [{"date": pd.Timestamp, "cf": float, "index_rate": float}, ...]
        reference_rates: List[float],  # Референсные ставки для каждого периода (%)
        valuation_date: pd.Timestamp,
        day_count_convention: DayCountConvention,
        face_value: float,
        maturity_date: pd.Timestamp,
        payments_per_year: int,
        coupon_period_months: Optional[int] = None,
        coupon_start: Optional[pd.Timestamp] = None,
        coupon_end: Optional[pd.Timestamp] = None,
        max_iterations: int = 100,
        tolerance: float = 1e-8
    ) -> float:
        """
        Рассчитывает Discount Margin (DM) методом Ньютона для плавающей ставки
        
        Уравнение: Pd = sum [ (Ci + Ni) / (1 + Indexi/100*n + DM/n)^(yfi*n) ]
        
        где:
            Indexi = значение референсной ставки для i-го периода (%)
            DM = Discount Margin (в базисных пунктах)
            n = частота выплат в год (native compounding)
            yfi = доля года для i-го платежа
            Ci = купонный платёж i-го периода
            Ni = погашение номинала в i-м периоде
        
        Args:
            dirty_price: Грязная цена облигации
            cash_flows: Список денежных потоков с референсными ставками
            reference_rates: Референсные ставки для каждого периода (%)
            valuation_date: Дата расчета
            day_count_convention: Базис расчета дней
            face_value: Номинал облигации
            maturity_date: Дата погашения
            payments_per_year: Частота выплат в год (n)
            coupon_period_months: Период купона в месяцах (для ISMA)
            coupon_start: Дата начала купонного периода (для ISMA)
            coupon_end: Дата конца купонного периода (для ISMA)
            max_iterations: Максимальное количество итераций
            tolerance: Точность сходимости
        
        Returns:
            Discount Margin в базисных пунктах (bp)
        """
        if not cash_flows or dirty_price <= 0 or payments_per_year <= 0:
            return 0.0
        
        # Параметры для расчета базиса
        kwargs_for_basis = {
            'maturity_date': maturity_date,
            'coupon_start': coupon_start,
            'coupon_end': coupon_end,
            'coupon_period_months': coupon_period_months
        }
        
        # Начальное приближение: 0 bp (0 базисных пунктов)
        dm_bps = 0.0
        
        # Конвертируем частоту выплат
        n = float(payments_per_year)
        
        for iteration in range(max_iterations):
            # P(DM) = sum [ (Ci + Ni) / (1 + Indexi/100*n + DM/n)^(yfi*n) ]
            price_calculated = 0.0
            # P'(DM) = производная по DM
            price_derivative = 0.0
            
            for i, cf in enumerate(cash_flows):
                cf_date = cf["date"]
                cf_amount = cf["cf"]
                
                # Референсная ставка для i-го периода
                if i < len(reference_rates):
                    index_rate = reference_rates[i]  # В процентах
                else:
                    index_rate = reference_rates[-1] if reference_rates else 0.0  # Используем последнюю доступную
                
                # Доля года для i-го платежа
                year_fraction = DayCountCalculator.calculate_year_fraction(
                    valuation_date,
                    cf_date,
                    day_count_convention,
                    **kwargs_for_basis
                )
                
                # Конвертируем DM из базисных пунктов в десятичное значение
                # 1 bp = 0.01%, поэтому DM_decimal = DM_bps / 10000
                dm_decimal = dm_bps / 10000.0
                
                # Ставка дисконтирования: Indexi/100*n + DM/n
                # Indexi в процентах, поэтому Indexi/100
                discount_rate = (index_rate / 100.0) / n + dm_decimal / n
                
                # Степень: yfi * n
                exponent = year_fraction * n
                
                # Приведенная стоимость потока
                discount_factor = (1.0 + discount_rate) ** exponent
                pv = cf_amount / discount_factor
                price_calculated += pv
                
                # Производная от PV по DM
                # d/dDM [CF / (1 + Indexi/100*n + DM/n)^(yfi*n)]
                # = -CF * (yfi*n) * (1/n) / (1 + Indexi/100*n + DM/n)^(yfi*n + 1)
                if discount_factor > 0:
                    pv_derivative = -cf_amount * exponent * (1.0 / n) / ((1.0 + discount_rate) ** (exponent + 1))
                    price_derivative += pv_derivative
            
            # Ошибка: разница между расчетной и фактической ценой
            error = price_calculated - dirty_price
            
            # Условие сходимости
            if abs(error) < tolerance:
                break
            
            # Обновление DM методом Ньютона
            # DM_{k+1} = DM_k - (P(DM_k) - Pd) / P'(DM_k)
            if abs(price_derivative) > 1e-10:  # Избегаем деления на ноль
                dm_bps = dm_bps - (error / price_derivative) * 10000.0  # Масштабируем обратно в bp
                # Ограничение: DM от -1000 до 10000 bp (от -10% до 100%)
                dm_bps = max(dm_bps, -1000.0)
                dm_bps = min(dm_bps, 10000.0)
            else:
                # Если производная слишком мала, используем небольшое приращение
                dm_bps = dm_bps + 10.0  # +10 bp
        
        return dm_bps


class BondPricer:
    """Класс для оценки облигаций и расчета метрик"""
    
    @staticmethod
    def fetch_bond_data(secid: str, from_date: str = "2000-01-01", day_count: int = 365) -> Dict:
        """
        Загружает параметры облигации из MOEX ISS API
        """
        try:
            # 1. Описание облигации
            desc_url = (
                f"{BASE_ISS}/securities/{secid}.json"
                "?iss.meta=off"
                "&iss.only=description"
                "&description.columns=name,title,value"
            )
            
            r = requests.get(desc_url, timeout=10)
            r.raise_for_status()
            data = r.json()
            rows = data["description"]["data"]
            params = {name: value for name, title, value in rows}
            
            if not params:
                raise ValueError(f"Облигация {secid} не найдена")

            face_value = float(params.get("FACEVALUE") or 0.0)
            coupon_percent = float(params.get("COUPONPERCENT") or 0.0)
            
            # Обработка дат
            issue_date_str = params.get("ISSUEDATE")
            mat_date_str = params.get("MATDATE")
            
            if not issue_date_str or not mat_date_str:
                raise ValueError("Не указана дата выпуска или погашения")
                
            issue_date = pd.to_datetime(issue_date_str)
            mat_date = pd.to_datetime(mat_date_str)
            
            # 2. Купоны и амортизация
            bond_url = (
                f"{BASE_ISS}/statistics/engines/stock/markets/bonds/bondization/{secid}.json"
                f"?from={from_date}"
                "&iss.only=coupons,amortizations"
                "&iss.meta=off"
            )
            
            rb = requests.get(bond_url, timeout=10)
            rb.raise_for_status()
            jb = rb.json()
            
            if "coupons" not in jb:
                raise RuntimeError("В bondization нет таблицы coupons")
            
            ctab = jb["coupons"]
            coupons_df = pd.DataFrame(ctab["data"], columns=ctab["columns"])
            
            if coupons_df.empty:
                raise RuntimeError("Нет данных по купонам")
            
            # Нормализация колонок
            date_col = "coupondate" if "coupondate" in coupons_df.columns else "date"
            
            if "value_rub" in coupons_df.columns:
                value_col = "value_rub"
            elif "value" in coupons_df.columns:
                value_col = "value"
            elif "VALUE" in coupons_df.columns:
                value_col = "VALUE"
            else:
                raise RuntimeError("Не найдена колонка с суммой купона")
            
            coupons_df[date_col] = pd.to_datetime(coupons_df[date_col])
            coupons_df[value_col] = coupons_df[value_col].astype(float)
            coupons_df = coupons_df.sort_values(date_col).reset_index(drop=True)
            
            coupons = coupons_df[date_col].tolist()
            
            # Определение частоты выплат
            if len(coupons) >= 2:
                period_days = (coupons[1] - coupons[0]).days
            else:
                period_days = 182 # Fallback to semi-annual
            
            payments_per_year = round(day_count / period_days) if period_days > 0 else 2
            
            # Генерация полных дат купонов (прошлые + будущие до погашения)
            coupon_dates_full = list(coupons)
            last = coupons[-1] if coupons else issue_date + pd.Timedelta(days=period_days)
            current = last
            
            # Достраиваем график, если API вернул не всё
            while current < mat_date:
                current = current + pd.Timedelta(days=period_days)
                if current < mat_date:
                    coupon_dates_full.append(current)
            
            # Всегда добавляем дату погашения как купонную дату (для выплаты номинала/купона)
            coupon_dates_full.append(mat_date)
            coupon_dates_full = sorted(list(set(coupon_dates_full)))
            
            # Маппинг известных значений
            coupon_map = {d.date(): v for d, v in zip(coupons_df[date_col], coupons_df[value_col])}
            last_coupon_value = coupons_df[value_col].iloc[-1] if not coupons_df.empty else 0.0
            
            # Заполняем значения
            coupon_values_full = [coupon_map.get(d.date(), last_coupon_value) for d in coupon_dates_full]
            
            return {
                "face_value": face_value,
                "coupon_percent": coupon_percent,
                "payments_per_year": payments_per_year,
                "issue_date": issue_date,
                "mat_date": mat_date,
                "coupon_dates_full": coupon_dates_full,
                "coupon_values_full": coupon_values_full,
            }

        except Exception as e:
            logger.error(f"Error fetching bond data for {secid}: {e}")
            raise

    @staticmethod
    def calculate_metrics(
        bond_data: Dict, 
        valuation_date: pd.Timestamp, 
        discount_yield: float,
        day_count_convention: DayCountConvention = DayCountConvention.ACTUAL_365F,
        coupon_period_months: Optional[int] = None,
        reference_rates: Optional[List[float]] = None  # Референсные ставки для расчета DM (в %)
    ) -> Dict:
        """
        Рассчитывает Dirty Price, Clean Price, НКД, Дюрацию
        
        Args:
            bond_data: Данные облигации
            valuation_date: Дата оценки
            discount_yield: Ставка дисконтирования
            day_count_convention: Базис расчета дней (по умолчанию Actual/365F)
            coupon_period_months: Период купона в месяцах (для Actual/Actual ISMA)
        """
        coupon_dates_full = bond_data["coupon_dates_full"]
        coupon_values_full = bond_data["coupon_values_full"]
        face_value = bond_data["face_value"]
        mat_date = bond_data["mat_date"]
        
        # 1. НКД (Accrued Interest)
        past_coupons = [d for d in coupon_dates_full if d <= valuation_date]
        future_coupons = [d for d in coupon_dates_full if d > valuation_date]
        
        nkd = 0.0
        if past_coupons and future_coupons:
            last_coupon_date = past_coupons[-1]
            next_coupon_date = future_coupons[0]
            
            # Параметры для расчета базиса
            kwargs_for_basis = {
                'maturity_date': mat_date,
                'coupon_start': last_coupon_date,
                'coupon_end': next_coupon_date,
                'coupon_period_months': coupon_period_months
            }
            
            # Находим сумму следующего купона
            try:
                last_coupon_idx = coupon_dates_full.index(last_coupon_date)
                if last_coupon_idx + 1 < len(coupon_values_full):
                    current_coupon_amount = coupon_values_full[last_coupon_idx + 1]
                else:
                    current_coupon_amount = coupon_values_full[-1] if coupon_values_full else 0.0
            except ValueError:
                current_coupon_amount = coupon_values_full[0] if coupon_values_full else 0.0
            
            # Получаем параметры облигации
            coupon_rate_pct = bond_data.get("coupon_percent", 0.0)
            
            # Предпочитаем расчет от суммы купона, если доступна
            # Это более точно, так как учитывает возможные изменения ставки
            if current_coupon_amount > 0:
                # Альтернативная формула от суммы купона
                nkd = AccruedInterestCalculator.from_coupon_amount(
                    coupon_amount=current_coupon_amount,
                    last_coupon_date=last_coupon_date,
                    next_coupon_date=next_coupon_date,
                    valuation_date=valuation_date,
                    day_count_convention=day_count_convention,
                    **kwargs_for_basis
                )
            elif coupon_rate_pct > 0 and face_value > 0:
                # Базовая формула от ставки купона (fallback)
                nkd = AccruedInterestCalculator.from_coupon_rate(
                    coupon_rate_pct=coupon_rate_pct,
                    face_value=face_value,
                    last_coupon_date=last_coupon_date,
                    valuation_date=valuation_date,
                    day_count_convention=day_count_convention,
                    **kwargs_for_basis
                )

        # 2. Денежные потоки (Cash Flows)
        # Формируем DataFrame только для будущих выплат
        future_dates = []
        future_values = []
        
        for d, v in zip(coupon_dates_full, coupon_values_full):
            if d > valuation_date:
                future_dates.append(d)
                val = v
                # Если дата совпадает с погашением, добавляем номинал
                if d == mat_date:
                    val += face_value
                future_values.append(val)
        
        cf_df = pd.DataFrame({
            "date": future_dates,
            "cf": future_values
        })
        
        # Инициализация переменных
        clean_price = 0.0  # Чистая цена (без НКД)
        dirty_price = 0.0  # Грязная цена (чистая цена + НКД)
        duration = 0.0
        cash_flows_detailed = []

        if not cf_df.empty:
            # Определяем параметры для расчета базиса (для ISMA)
            coupon_start_for_calc = past_coupons[-1] if past_coupons else None
            coupon_end_for_calc = future_coupons[0] if future_coupons else None
            
            # Используем выбранный базис для расчета временных коэффициентов
            cf_df["t"] = cf_df["date"].apply(
                lambda d: DayCountCalculator.calculate_year_fraction(
                    valuation_date,
                    d,
                    day_count_convention,
                    maturity_date=mat_date,
                    coupon_start=coupon_start_for_calc,
                    coupon_end=coupon_end_for_calc,
                    coupon_period_months=coupon_period_months
                )
            )
            cf_df["df"] = 1.0 / ((1.0 + discount_yield) ** cf_df["t"])
            cf_df["pv"] = cf_df["cf"] * cf_df["df"]
            
            # Грязная цена (Dirty Price) = сумма приведенной стоимости всех будущих денежных потоков
            # Это полная стоимость облигации на дату расчета
            dirty_price = cf_df["pv"].sum()
            
            # Чистая цена (Clean Price) = Грязная цена - НКД
            # Формула: P = Pd - A
            # где:
            #   P = чистая цена (clean_price) - цена без НКД
            #   Pd = грязная цена (dirty_price) - полная цена
            #   A = накопленный купонный доход (nkd)
            clean_price = dirty_price - nkd
            
            # Детализация для фронтенда
            for row in cf_df.itertuples(index=False):
                cash_flows_detailed.append({
                    "date": row.date.isoformat(),
                    "t": float(row.t),
                    "cf": float(row.cf),
                    "df": float(row.df),
                    "pv": float(row.pv)
                })
        
        # Полный список купонов для отображения
        all_coupons_detailed = []
        for d, v in zip(coupon_dates_full, coupon_values_full):
            all_coupons_detailed.append({
                "date": d.isoformat(),
                "value": float(v),
                "isPaid": bool(d <= valuation_date)
            })

        # Расчет чистой цены в процентах от номинала
        price_percent = float((clean_price / face_value * 100) if face_value else 0)
        
        # Расчет текущей доходности (Current Yield, CY)
        # Формула: CY = (C% / P%) * 100%
        # где:
        #   C% = годовая ставка купона (%)
        #   P% = чистая цена (% от номинала)
        coupon_percent = bond_data.get("coupon_percent", 0.0)
        current_yield = 0.0
        if price_percent > 0:
            current_yield = (coupon_percent / price_percent) * 100.0
        
        # Расчет времени до погашения (Tm) для использования в дальнейших расчетах
        time_to_maturity = 0.0
        kwargs_for_maturity = {}
        if valuation_date < mat_date:
            # Рассчитываем время до погашения в годах с учетом выбранного базиса
            kwargs_for_maturity = {
                'maturity_date': mat_date,
                'coupon_start': past_coupons[-1] if past_coupons else None,
                'coupon_end': future_coupons[0] if future_coupons else None,
                'coupon_period_months': coupon_period_months
            }
            
            time_to_maturity = DayCountCalculator.calculate_year_fraction(
                valuation_date,
                mat_date,
                day_count_convention,
                **kwargs_for_maturity
            )
        
        # Расчет скорректированной текущей доходности (Adjusted Current Yield, ACY)
        # Формула: ACY = CY + (100% - P%) / Tm
        # где:
        #   CY = текущая доходность (%)
        #   P% = чистая цена (% от номинала)
        #   Tm = лет до погашения
        acy = 0.0
        if time_to_maturity > 0:
            # ACY = CY + (100% - P%) / Tm
            price_discount = 100.0 - price_percent  # Разница между номиналом и ценой
            acy = current_yield + (price_discount / time_to_maturity)
        elif valuation_date >= mat_date:
            # Если дата оценки >= даты погашения, ACY = CY
            acy = current_yield
        
        # Расчет простой доходности к погашению (Simple Yield, SY)
        # Формула: SY = [ (sum(Ci + Ni) - Pd) / Pd ] * 100% / Tm
        # где:
        #   Ci = i-й купонный платёж
        #   Ni = i-е погашение номинала
        #   Pd = грязная цена (dirty_price)
        #   Tm = лет до погашения (time_to_maturity)
        simple_yield = 0.0
        if valuation_date < mat_date and time_to_maturity > 0 and dirty_price > 0:
            # Суммируем все будущие денежные потоки (купоны + погашения)
            # Это уже рассчитано в future_values или cf_df["cf"]
            total_future_cashflows = sum(future_values) if future_values else 0.0
            
            # Альтернативно, можно использовать сумму из cf_df
            if not cf_df.empty:
                total_future_cashflows = cf_df["cf"].sum()
            
            # SY = [ (sum(Ci + Ni) - Pd) / Pd ] * 100% / Tm
            if total_future_cashflows > 0:
                total_return = total_future_cashflows - dirty_price  # Общий доход
                return_rate = (total_return / dirty_price) * 100.0  # Доходность в процентах
                simple_yield = return_rate / time_to_maturity  # Годовая доходность
        
        # Расчет доходности к погашению (Yield To Maturity, YTM) методом Ньютона
        # Уравнение: Pd = sum [ (Ci + Ni) / (1 + YTM)^((ti - t0) / B) ]
        # Если цена была рассчитана с использованием discount_yield, то YTM должна быть близка к discount_yield
        # Поэтому используем discount_yield как начальное приближение для метода Ньютона
        ytm = discount_yield  # Используем discount_yield как начальное значение (это и есть YTM, если цена рассчитана по нему)
        
        if valuation_date < mat_date and dirty_price > 0 and not cf_df.empty:
            # Подготовка денежных потоков для расчета YTM
            ytm_cash_flows = [
                {"date": row.date, "cf": row.cf}
                for row in cf_df.itertuples(index=False)
            ]
            
            # Определяем параметры для расчета базиса (для ISMA)
            coupon_start_for_ytm = past_coupons[-1] if past_coupons else None
            coupon_end_for_ytm = future_coupons[0] if future_coupons else None
            
            # Расчет YTM (используем discount_yield как начальное приближение)
            calculated_ytm = YTMCalculator.calculate_ytm(
                dirty_price=dirty_price,
                cash_flows=ytm_cash_flows,
                valuation_date=valuation_date,
                day_count_convention=day_count_convention,
                face_value=face_value,
                maturity_date=mat_date,
                coupon_period_months=coupon_period_months,
                coupon_start=coupon_start_for_ytm,
                coupon_end=coupon_end_for_ytm,
                initial_guess=discount_yield  # Используем discount_yield как начальное приближение
            )
            
            # Если расчет успешен, используем его; иначе используем discount_yield
            if calculated_ytm > 0 or (calculated_ytm <= 0 and abs(calculated_ytm) < 1.0):
                ytm = calculated_ytm
            else:
                # Если YTM получилась слишком отрицательной или слишком большой, используем discount_yield
                ytm = discount_yield
        else:
            # Если нет денежных потоков, YTM = discount_yield
            ytm = discount_yield
        
        # Расчет дюрации Маколея (Macaulay Duration, D)
        # Формула: D = Σ[ t_i * CF_i / (1 + YTM)^t_i ] / Pd
        # где:
        #   t_i = (ti - t0) / B = годовая доля до платежа (year-fraction)
        #   CF_i = денежный поток i-го периода
        #   Pd = грязная цена (dirty_price)
        # Результат: D в годах (year-fractions используются на всех этапах)
        # Для бессрочной облигации (perpetuity): D = (1 + 1/YTM) лет
        # На международных рынках (Bloomberg) дюрацию обычно измеряют в годах
        if dirty_price > 0 and not cf_df.empty and ytm > -0.99:  # Разрешаем отрицательные YTM в разумных пределах
            # Проверка на бессрочную облигацию (perpetuity)
            # Если нет даты погашения или она очень далека в будущем (> 100 лет)
            if mat_date is None or (valuation_date < mat_date and (mat_date - valuation_date).days > 36500):
                # Для бессрочной облигации: D = (1 + 1/YTM) лет
                if abs(ytm) < 1e-10:
                    duration = float('inf')
                else:
                    duration = 1.0 + (1.0 / ytm)
            elif not cf_df.empty:
                # Базовая формула для обычной облигации
                # Параметры для расчета базиса
                kwargs_for_duration = {
                    'maturity_date': mat_date,
                    'coupon_start': coupon_start_for_calc,
                    'coupon_end': coupon_end_for_calc,
                    'coupon_period_months': coupon_period_months
                }
                
                # Формула дюрации Маколея:
                # D = Σ[ t_i * CF_i / (1 + YTM)^t_i ] / Pd
                # где t_i — year-fraction (годовая доля) до i-го платежа
                # Результат сразу в годах (year-fractions на всех этапах)
                duration_numerator = 0.0

                for row in cf_df.itertuples(index=False):
                    cf_date = row.date
                    cf_amount = row.cf

                    # Годовая доля до платежа t_i = (ti - t0) / B
                    time_fraction = DayCountCalculator.calculate_year_fraction(
                        valuation_date,
                        cf_date,
                        day_count_convention,
                        **kwargs_for_duration
                    )

                    # Дисконтированный денежный поток: CF_i / (1 + YTM)^t_i
                    if (1.0 + ytm) > 0 and time_fraction >= 0:
                        discount_factor = (1.0 + ytm) ** time_fraction
                        if discount_factor > 0:
                            discounted_cf = cf_amount / discount_factor

                            # Накопление: t_i * PV_i (year-fractions throughout)
                            duration_numerator += time_fraction * discounted_cf

                # Дюрация в годах = числитель / грязная цена
                if dirty_price > 0 and duration_numerator > 0:
                    duration = duration_numerator / dirty_price
                else:
                    duration = 0.0
                
                # Расчет выпуклости (Convexity, CONV)
                # Формула: CONV = Σ[ t_i * (t_i + 1) * CF_i / (1 + YTM)^(t_i + 2) ] / Pd
                # где:
                #   t_i = year-fraction до i-го платежа
                #   CF_i = денежный поток
                #   Pd = грязная цена
                # Получается из второй производной цены по YTM:
                #   d²P/dy² = Σ[ t_i * (t_i + 1) * CF_i / (1 + y)^(t_i + 2) ]
                #   CONV = (1/P) * d²P/dy²
                # Интерпретация: CONV показывает кривизну кривой цена-доходность
                # Улучшенная формула изменения цены: ΔPd/Pd ≈ -MD * ΔYTM + 0.5 * CONV * (ΔYTM)²
                convexity_numerator = 0.0

                for row in cf_df.itertuples(index=False):
                    cf_date = row.date
                    cf_amount = row.cf

                    # Годовая доля до платежа t_i = (ti - t0) / B
                    time_fraction = DayCountCalculator.calculate_year_fraction(
                        valuation_date,
                        cf_date,
                        day_count_convention,
                        **kwargs_for_duration
                    )

                    # CF_i / (1 + YTM)^(t_i + 2)
                    if (1.0 + ytm) > 0 and time_fraction >= 0:
                        discount_exponent = time_fraction + 2.0
                        discounted_cf = cf_amount / ((1.0 + ytm) ** discount_exponent)

                        # t_i * (t_i + 1) * PV_i  (year-fractions throughout)
                        convexity_numerator += time_fraction * (time_fraction + 1.0) * discounted_cf

                # Выпуклость = числитель / грязная цена
                convexity = convexity_numerator / dirty_price if dirty_price > 0 else 0.0
            else:
                convexity = 0.0
        else:
            convexity = 0.0
        
        # Расчет модифицированной дюрации (Modified Duration, MD)
        # Формула: MD = D / (1 + YTM)
        # где:
        #   D = дюрация Маколея (в годах)
        #   YTM = доходность к погашению (в десятичном виде)
        # Интерпретация: MD показывает относительное изменение грязной цены при изменении доходности на 1%
        # ΔPd / Pd ≈ -MD * ΔYTM, где ΔYTM = изменение доходности (в десятичном виде)
        # Модифицированная дюрация характеризует волатильность "грязной" цены облигации
        modified_duration = 0.0
        if dirty_price > 0 and abs(1.0 + ytm) > 1e-10:  # Избегаем деления на ноль
            # MD = D / (1 + YTM), где D уже в годах
            modified_duration = duration / (1.0 + ytm)
        
        # Расчет стоимости базисного пункта (PVBP / DV01 - Price Value of a Basis Point / Dollar Value of 01)
        # Формула: PVBP = (MD / 100) * (Pd / 100)
        # где:
        #   MD = модифицированная дюрация (в годах)
        #   Pd = грязная цена (% от номинала)
        # Результат: PVBP в процентах (от 1 номинального лота)
        # Интерпретация: показывает абсолютное изменение цены при изменении доходности на 1 базисный пункт (1 bp = 0.01%)
        pvbp_percent = 0.0
        pvbp_absolute = 0.0
        if modified_duration > 0 and face_value > 0:
            # Грязная цена в процентах от номинала
            dirty_price_percent = (dirty_price / face_value) * 100.0 if face_value > 0 else 0.0
            
            # PVBP = (MD / 100) * (Pd / 100)
            # Результат в процентах от номинала
            pvbp_percent = (modified_duration / 100.0) * (dirty_price_percent / 100.0)
            
            # Для номинала N денежных единиц: PVBP_absolute = PVBP * (N / 100)
            # или PVBP_absolute = (MD / 100) * Pd (где Pd в денежных единицах)
            pvbp_absolute = (modified_duration / 100.0) * dirty_price
        
        # Расчет номинальной доходности (Nominal Yield, NY)
        # Формула: NY = n * [ (1 + YTM)^(1/n) - 1 ] * 100%
        # где:
        #   n = количество выплат купонов в год (payments_per_year)
        #   YTM = доходность к погашению в десятичном виде
        nominal_yield = 0.0
        payments_per_year = bond_data.get("payments_per_year", 2)  # По умолчанию 2 (полугодовые выплаты)
        if ytm > 0 and payments_per_year > 0:
            nominal_yield = YTMCalculator.ytm_to_nominal_yield(ytm, payments_per_year)
        
        # Расчет Discount Margin (DM) для плавающей ставки
        # Уравнение: Pd = sum [ (Ci + Ni) / (1 + Indexi/100*n + DM/n)^(yfi*n) ]
        # где:
        #   Indexi = значение референсной ставки для i-го периода (%)
        #   DM = Discount Margin (в базисных пунктах)
        #   n = частота выплат в год (native compounding)
        #   yfi = доля года для i-го платежа
        discount_margin_bps = None
        if reference_rates and len(reference_rates) > 0 and dirty_price > 0 and not cf_df.empty:
            # Подготовка денежных потоков с референсными ставками для расчета DM
            dm_cash_flows = []
            for idx, row in enumerate(cf_df.itertuples(index=False)):
                # Используем соответствующую референсную ставку для периода
                if idx < len(reference_rates):
                    index_rate = reference_rates[idx]
                else:
                    index_rate = reference_rates[-1]  # Используем последнюю доступную ставку

                dm_cash_flows.append({
                    "date": row.date,
                    "cf": row.cf,
                    "index_rate": index_rate
                })
            
            # Определяем параметры для расчета базиса
            coupon_start_for_dm = past_coupons[-1] if past_coupons else None
            coupon_end_for_dm = future_coupons[0] if future_coupons else None
            
            # Расчет Discount Margin
            try:
                discount_margin_bps = DiscountMarginCalculator.calculate_discount_margin(
                    dirty_price=dirty_price,
                    cash_flows=dm_cash_flows,
                    reference_rates=reference_rates,
                    valuation_date=valuation_date,
                    day_count_convention=day_count_convention,
                    face_value=face_value,
                    maturity_date=mat_date,
                    payments_per_year=payments_per_year,
                    coupon_period_months=coupon_period_months,
                    coupon_start=coupon_start_for_dm,
                    coupon_end=coupon_end_for_dm
                )
            except Exception as e:
                logger.warning(f"Error calculating Discount Margin: {e}")
                discount_margin_bps = None
        
        # Таблица сценариев (Price Sensitivity Analysis)
        # Анализ чувствительности цены к изменению доходности
        # Формула: ΔPd% = -MD * ΔYTM_decimal + 0.5 * CONV * (ΔYTM_decimal)^2
        # где:
        #   ΔYTM_decimal = bp / 10000 (изменение доходности в десятичном виде)
        #   MD = модифицированная дюрация
        #   CONV = выпуклость
        #   ΔPd_absolute = (ΔPd% / 100) * Pd (абсолютное изменение цены)
        sensitivity_scenarios = []
        scenarios_bps = [-200, -150, -100, -50, 0, 50, 100, 150, 200]
        
        if modified_duration > 0 and dirty_price > 0:
            for bp_change in scenarios_bps:
                # 1. Конвертируем bp в десятичное значение
                # ΔYTM_decimal = bp / 10000
                dytm_decimal = bp_change / 10000.0
                
                # 2. Рассчитываем процентное изменение цены
                # ΔPd% = -MD * ΔYTM_decimal + 0.5 * CONV * (ΔYTM_decimal)^2
                price_change_percent = -modified_duration * dytm_decimal + 0.5 * convexity * (dytm_decimal ** 2)
                
                # 3. Рассчитываем абсолютное изменение цены
                # ΔPd_absolute = (ΔPd% / 100) * Pd
                price_change_absolute = (price_change_percent / 100.0) * dirty_price
                
                # 4. Новая цена после изменения доходности
                new_dirty_price = dirty_price + price_change_absolute
                new_ytm_percent = (ytm * 100.0) + bp_change
                
                sensitivity_scenarios.append({
                    "yieldChangeBps": bp_change,  # Изменение доходности (базисные пункты)
                    "yieldChangePercent": float(dytm_decimal * 100.0),  # Изменение доходности (%)
                    "priceChangePercent": float(price_change_percent),  # Изменение цены (%)
                    "priceChangeAbsolute": float(price_change_absolute),  # Изменение цены (абсолютное)
                    "newDirtyPrice": float(new_dirty_price),  # Новая грязная цена
                    "newYtmPercent": float(new_ytm_percent)  # Новая доходность (%)
                })

        return {
            "dirtyPrice": float(dirty_price),
            "accruedInterest": float(nkd),
            "cleanPrice": float(clean_price),
            "pricePercent": price_percent,
            "currentYield": float(current_yield),  # Текущая доходность (%)
            "adjustedCurrentYield": float(acy),  # Скорректированная текущая доходность (%)
            "simpleYield": float(simple_yield),  # Простая доходность к погашению (%)
            "ytm": float(ytm),  # Доходность к погашению (YTM) в десятичном виде
            "ytmPercent": float(ytm * 100.0),  # YTM в процентах
            "nominalYield": float(nominal_yield),  # Номинальная доходность (NY) в процентах
            "duration": float(duration),  # Дюрация Маколея (Macaulay Duration) в годах
            "modifiedDuration": float(modified_duration),  # Модифицированная дюрация (Modified Duration) в годах
            "convexity": float(convexity),  # Выпуклость (Convexity) - кривизна кривой цена-доходность
            "pvbp": float(pvbp_percent),  # Стоимость базисного пункта (PVBP/DV01) в процентах от номинала
            "pvbpAbsolute": float(pvbp_absolute),  # PVBP в абсолютных денежных единицах (для текущего номинала)
            "discountMargin": float(discount_margin_bps) if discount_margin_bps is not None else None,  # Discount Margin (DM) в базисных пунктах (для плавающей ставки)
            "sensitivityScenarios": sensitivity_scenarios,  # Таблица сценариев чувствительности цены
            "cashFlows": cash_flows_detailed,
            "allCoupons": all_coupons_detailed
        }

