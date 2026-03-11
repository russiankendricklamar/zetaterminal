"""
Cashflow generation, day count fraction calculations, and accrued interest.
"""

import pandas as pd

from .bond_pricing_types import DayCountConvention


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
        maturity_date: pd.Timestamp | None = None
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
        if d1 == 31 or (m1 == 2 and d1 == last_feb_day_d1):
            d1 = 30

        # Корректировки для D2
        if (d2 == 31 and (d1 == 30 or d1 == 31)) or (m1 == 2 and d1 == last_feb_day_d1 and m2 == 2 and d2 == last_feb_day_d2):
            d2 = 30

        days = (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)
        return days / 360.0

    @staticmethod
    def thirty_e_360_isda(
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        maturity_date: pd.Timestamp | None = None
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
        if d1 == 31 or (m1 == 2 and d1 == last_feb_day):
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
        coupon_start: pd.Timestamp | None = None,
        coupon_end: pd.Timestamp | None = None,
        coupon_period_months: int | None = None
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
        reference_rates: list[float],
        spread_bps: float,
        face_value: float,
        rate_dates: list[pd.Timestamp],
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
            for rate, date in zip(reference_rates, rate_dates, strict=False):
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
