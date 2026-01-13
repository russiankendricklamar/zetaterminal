"""
Сервис для расчета форварда на облигацию.
Форвард на облигацию учитывает:
- Спот цену облигации (clean price)
- Накопленный купонный доход (AI)
- Репо ставку (стоимость финансирования)
- Купоны, полученные до экспирации форварда
- Day count conventions
- Кривую доходности
- Греки (DV01, Convexity, Repo Sensitivity)
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
import logging

logger = logging.getLogger(__name__)


# Day Count Conventions
def day_count_actual_actual(start_date: datetime, end_date: datetime) -> Tuple[int, int]:
    """Actual/Actual (ISDA) - точное количество дней / точное количество дней в году."""
    days = (end_date - start_date).days
    # Определяем количество дней в году (учитываем високосные годы)
    year_start = datetime(start_date.year, 1, 1)
    year_end = datetime(start_date.year + 1, 1, 1)
    days_in_year = (year_end - year_start).days
    return days, days_in_year


def day_count_actual_365(start_date: datetime, end_date: datetime) -> Tuple[int, int]:
    """Actual/365 - точное количество дней / 365."""
    days = (end_date - start_date).days
    return days, 365


def day_count_actual_360(start_date: datetime, end_date: datetime) -> Tuple[int, int]:
    """Actual/360 - точное количество дней / 360."""
    days = (end_date - start_date).days
    return days, 360


def day_count_30_360(start_date: datetime, end_date: datetime) -> Tuple[int, int]:
    """30/360 - 30 дней в месяце, 360 дней в году."""
    d1, m1, y1 = start_date.day, start_date.month, start_date.year
    d2, m2, y2 = end_date.day, end_date.month, end_date.year
    
    # Если день = 31, считаем как 30
    if d1 == 31:
        d1 = 30
    if d2 == 31:
        d2 = 30
    
    days = (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)
    return days, 360


DAY_COUNT_FUNCTIONS = {
    "ACT/ACT": day_count_actual_actual,
    "ACT/365": day_count_actual_365,
    "ACT/360": day_count_actual_360,
    "30/360": day_count_30_360
}


def calculate_day_fraction(
    start_date: datetime,
    end_date: datetime,
    day_count_convention: str = "ACT/365"
) -> float:
    """Рассчитывает долю года по выбранной конвенции."""
    if day_count_convention not in DAY_COUNT_FUNCTIONS:
        day_count_convention = "ACT/365"
    
    func = DAY_COUNT_FUNCTIONS[day_count_convention]
    days, days_in_year = func(start_date, end_date)
    return days / days_in_year


def calculate_accrued_interest(
    last_coupon_date: datetime,
    valuation_date: datetime,
    coupon_rate: float,
    coupon_frequency: int,
    face_value: float,
    day_count_convention: str = "ACT/365"
) -> float:
    """
    Рассчитывает накопленный купонный доход (НКД).
    
    Args:
        last_coupon_date: Дата последнего купона
        valuation_date: Дата оценки
        coupon_rate: Купонная ставка (годовая, в процентах)
        coupon_frequency: Частота выплаты купонов
        face_value: Номинал облигации
        day_count_convention: Конвенция подсчета дней
    
    Returns:
        Накопленный купонный доход
    """
    if valuation_date <= last_coupon_date:
        return 0.0
    
    # Следующая дата купона
    months_to_next = 12 // coupon_frequency
    next_coupon_date = last_coupon_date
    while next_coupon_date <= valuation_date:
        next_coupon_date = next_coupon_date + timedelta(days=365 // coupon_frequency)
    
    # Дни с последнего купона
    days_since_last = (valuation_date - last_coupon_date).days
    days_in_period = (next_coupon_date - last_coupon_date).days
    
    if days_in_period == 0:
        return 0.0
    
    # Купон за период
    coupon_per_period = (coupon_rate / 100.0) * face_value / coupon_frequency
    
    # НКД пропорционален времени с последнего купона
    accrual_ratio = days_since_last / days_in_period
    accrued_interest = coupon_per_period * accrual_ratio
    
    return accrued_interest


def generate_coupon_schedule(
    last_coupon_date: datetime,
    maturity_date: datetime,
    coupon_frequency: int,
    valuation_date: datetime,
    expiration_date: datetime
) -> List[Dict]:
    """
    Генерирует расписание купонных платежей между датой оценки и экспирацией.
    
    Returns:
        Список словарей с информацией о каждом купоне
    """
    coupons = []
    months_to_next = 12 // coupon_frequency
    days_per_period = 365 // coupon_frequency
    
    # Находим первую дату купона после даты оценки
    current_coupon_date = last_coupon_date
    while current_coupon_date <= valuation_date:
        current_coupon_date = current_coupon_date + timedelta(days=days_per_period)
    
    # Генерируем купоны до даты экспирации
    coupon_num = 1
    while current_coupon_date <= expiration_date:
        days_to_payment = (current_coupon_date - valuation_date).days
        if days_to_payment > 0:
            coupons.append({
                "couponNumber": coupon_num,
                "couponDate": current_coupon_date.strftime("%Y-%m-%d"),
                "daysToPayment": days_to_payment,
                "yearsToPayment": days_to_payment / 365.0
            })
            coupon_num += 1
        current_coupon_date = current_coupon_date + timedelta(days=days_per_period)
    
    return coupons


def interpolate_yield_curve(
    tenors: List[float],
    rates: List[float],
    target_tenor: float,
    method: str = "linear"
) -> float:
    """
    Интерполирует кривую доходности для заданного тенора.
    
    Args:
        tenors: Список теноров (в годах)
        rates: Список ставок (в процентах)
        target_tenor: Целевой тенор (в годах)
        method: Метод интерполяции ("linear", "cubic")
    
    Returns:
        Интерполированная ставка (в процентах)
    """
    if len(tenors) != len(rates):
        raise ValueError("Длины списков теноров и ставок должны совпадать")
    
    if target_tenor <= min(tenors):
        return rates[0]
    if target_tenor >= max(tenors):
        return rates[-1]
    
    if method == "linear":
        f = interp1d(tenors, rates, kind='linear', fill_value='extrapolate')
    elif method == "cubic":
        f = interp1d(tenors, rates, kind='cubic', fill_value='extrapolate')
    else:
        f = interp1d(tenors, rates, kind='linear', fill_value='extrapolate')
    
    return float(f(target_tenor))


def calculate_discount_factor(
    rate: float,
    time_to_payment: float,
    compounding: str = "continuous"
) -> float:
    """
    Рассчитывает дисконт-фактор.
    
    Args:
        rate: Ставка (в процентах)
        time_to_payment: Время до платежа (в годах)
        compounding: Тип начисления ("continuous", "simple", "annual")
    
    Returns:
        Дисконт-фактор
    """
    r = rate / 100.0
    
    if compounding == "continuous":
        return np.exp(-r * time_to_payment)
    elif compounding == "simple":
        return 1 / (1 + r * time_to_payment)
    elif compounding == "annual":
        return 1 / ((1 + r) ** time_to_payment)
    else:
        return np.exp(-r * time_to_payment)


def calculate_bond_forward_price_enhanced(
    spot_clean_price: float,
    accrued_interest: float,
    repo_rate: float,
    coupon_rate: float,
    coupon_frequency: int,
    time_to_maturity: float,
    face_value: float = 100.0,
    valuation_date: Optional[str] = None,
    expiration_date: Optional[str] = None,
    last_coupon_date: Optional[str] = None,
    maturity_date: Optional[str] = None,
    day_count_convention: str = "ACT/365",
    yield_curve_tenors: Optional[List[float]] = None,
    yield_curve_rates: Optional[List[float]] = None,
    auto_calculate_ai: bool = True
) -> Dict:
    """
    Расширенная версия расчета справедливой цены форварда на облигацию.
    
    Формула: F = [(S₀ + AI₀) × (1 + r_repo × T) - Σ(Cᵢ × DFᵢ)] / DF(T) - AI_T
    
    где:
    - S₀ - спот цена (clean price)
    - AI₀ - накопленный купонный доход на текущую дату
    - r_repo - репо ставка (годовая, в процентах)
    - T - время до экспирации (лет)
    - Cᵢ - купон i
    - DFᵢ - дисконт-фактор для купона i
    - DF(T) - дисконт-фактор до экспирации
    - AI_T - накопленный купонный доход на дату экспирации
    """
    # Парсим даты
    if valuation_date:
        val_dt = datetime.strptime(valuation_date, "%Y-%m-%d")
    else:
        val_dt = datetime.now()
    
    if expiration_date:
        exp_dt = datetime.strptime(expiration_date, "%Y-%m-%d")
        days_to_maturity = (exp_dt - val_dt).days
        T = calculate_day_fraction(val_dt, exp_dt, day_count_convention)
    else:
        exp_dt = val_dt + timedelta(days=int(time_to_maturity * 365))
        days_to_maturity = (exp_dt - val_dt).days
        T = time_to_maturity
    
    # Автоматический расчет НКД, если включен
    if auto_calculate_ai and last_coupon_date:
        last_coupon_dt = datetime.strptime(last_coupon_date, "%Y-%m-%d")
        accrued_interest = calculate_accrued_interest(
            last_coupon_dt, val_dt, coupon_rate, coupon_frequency,
            face_value, day_count_convention
        )
    
    # НКД на дату экспирации
    if last_coupon_date:
        last_coupon_dt = datetime.strptime(last_coupon_date, "%Y-%m-%d")
        ai_forward = calculate_accrued_interest(
            last_coupon_dt, exp_dt, coupon_rate, coupon_frequency,
            face_value, day_count_convention
        )
    else:
        # Упрощенный расчет
        days_per_period = 365 // coupon_frequency
        days_since_last = (days_to_maturity % days_per_period)
        coupon_per_period = (coupon_rate / 100.0) * face_value / coupon_frequency
        ai_forward = (days_since_last / days_per_period) * coupon_per_period
    
    # Dirty price = Clean price + Accrued Interest
    spot_dirty_price = spot_clean_price + accrued_interest
    
    # Генерируем расписание купонов
    if maturity_date:
        mat_dt = datetime.strptime(maturity_date, "%Y-%m-%d")
    else:
        mat_dt = exp_dt + timedelta(days=365)  # Предполагаем 1 год до погашения
    
    if last_coupon_date:
        last_coupon_dt = datetime.strptime(last_coupon_date, "%Y-%m-%d")
    else:
        last_coupon_dt = val_dt - timedelta(days=365 // coupon_frequency)
    
    coupon_schedule = generate_coupon_schedule(
        last_coupon_dt, mat_dt, coupon_frequency, val_dt, exp_dt
    )
    
    # Рассчитываем приведенную стоимость купонов
    coupon_per_period = (coupon_rate / 100.0) * face_value / coupon_frequency
    pv_coupons = 0.0
    coupon_details = []
    
    # Используем кривую доходности или плоскую ставку
    use_yield_curve = yield_curve_tenors and yield_curve_rates and len(yield_curve_tenors) > 1
    
    for coupon in coupon_schedule:
        years_to_payment = coupon["yearsToPayment"]
        
        if use_yield_curve:
            # Интерполируем ставку из кривой
            discount_rate = interpolate_yield_curve(
                yield_curve_tenors, yield_curve_rates, years_to_payment, "linear"
            )
        else:
            # Используем репо ставку
            discount_rate = repo_rate
        
        # Дисконт-фактор
        df = calculate_discount_factor(discount_rate, years_to_payment, "continuous")
        pv_coupon = coupon_per_period * df
        
        coupon_details.append({
            "couponNumber": coupon["couponNumber"],
            "couponDate": coupon["couponDate"],
            "daysToPayment": coupon["daysToPayment"],
            "yearsToPayment": float(years_to_payment),
            "couponAmount": float(coupon_per_period),
            "discountRate": float(discount_rate),
            "discountFactor": float(df),
            "presentValue": float(pv_coupon)
        })
        
        pv_coupons += pv_coupon
    
    # Дисконт-фактор до экспирации
    if use_yield_curve:
        forward_discount_rate = interpolate_yield_curve(
            yield_curve_tenors, yield_curve_rates, T, "linear"
        )
    else:
        forward_discount_rate = repo_rate
    
    df_forward = calculate_discount_factor(forward_discount_rate, T, "continuous")
    
    # Справедливая цена форварда (clean forward price)
    # F = [(S₀ + AI₀) × (1 + r_repo × T) - Σ(Cᵢ × DFᵢ)] / DF(T) - AI_T
    # Упрощенная версия: F = (S + AI) × (1 + r_repo × T) - AI_forward - PV_coupons
    forward_dirty_price = (spot_dirty_price * (1 + repo_rate / 100.0 * T) - pv_coupons) / df_forward
    forward_clean_price = forward_dirty_price - ai_forward
    
    # Ограничиваем минимальную цену
    forward_clean_price = max(forward_clean_price, 0.0)
    
    return {
        "spotCleanPrice": float(spot_clean_price),
        "spotDirtyPrice": float(spot_dirty_price),
        "accruedInterest": float(accrued_interest),
        "forwardCleanPrice": float(forward_clean_price),
        "forwardDirtyPrice": float(forward_dirty_price),
        "aiForward": float(ai_forward),
        "pvCoupons": float(pv_coupons),
        "repoRate": float(repo_rate),
        "timeToMaturity": float(T),
        "daysToMaturity": int(days_to_maturity),
        "couponSchedule": coupon_details,
        "discountFactorForward": float(df_forward),
        "forwardDiscountRate": float(forward_discount_rate),
        # Детальный разбор формулы
        "formulaBreakdown": {
            "spotCleanPrice": float(spot_clean_price),
            "accruedInterestSpot": float(accrued_interest),
            "spotDirtyPrice": float(spot_dirty_price),
            "repoRate": float(repo_rate),
            "timeToMaturity": float(T),
            "financingCost": float(spot_dirty_price * repo_rate / 100.0 * T),
            "totalCouponsPV": float(pv_coupons),
            "forwardDirtyPriceBeforeAI": float(forward_dirty_price),
            "accruedInterestForward": float(ai_forward),
            "forwardCleanPrice": float(forward_clean_price)
        }
    }


def calculate_dv01(
    spot_clean_price: float,
    accrued_interest: float,
    repo_rate: float,
    coupon_rate: float,
    coupon_frequency: int,
    time_to_maturity: float,
    face_value: float = 100.0,
    valuation_date: Optional[str] = None,
    expiration_date: Optional[str] = None,
    day_count_convention: str = "ACT/365"
) -> float:
    """
    Рассчитывает DV01 (Dollar Duration) - изменение форвардной цены при сдвиге кривой на 1 bp.
    
    Returns:
        DV01 в единицах цены (на единицу номинала)
    """
    # Базовая цена
    base_result = calculate_bond_forward_price_enhanced(
        spot_clean_price, accrued_interest, repo_rate, coupon_rate,
        coupon_frequency, time_to_maturity, face_value, valuation_date,
        expiration_date, day_count_convention=day_count_convention
    )
    base_price = base_result["forwardCleanPrice"]
    
    # Цена при сдвиге на +1 bp
    shifted_result = calculate_bond_forward_price_enhanced(
        spot_clean_price, accrued_interest, repo_rate + 0.01, coupon_rate,
        coupon_frequency, time_to_maturity, face_value, valuation_date,
        expiration_date, day_count_convention=day_count_convention
    )
    shifted_price = shifted_result["forwardCleanPrice"]
    
    dv01 = (shifted_price - base_price) / 0.01  # Изменение на 1 bp
    return float(dv01)


def calculate_convexity(
    spot_clean_price: float,
    accrued_interest: float,
    repo_rate: float,
    coupon_rate: float,
    coupon_frequency: int,
    time_to_maturity: float,
    face_value: float = 100.0,
    valuation_date: Optional[str] = None,
    expiration_date: Optional[str] = None,
    day_count_convention: str = "ACT/365"
) -> float:
    """
    Рассчитывает Convexity - вторая производная цены по ставке.
    
    Returns:
        Convexity (в единицах цены)
    """
    # Цена при базовой ставке
    base_result = calculate_bond_forward_price_enhanced(
        spot_clean_price, accrued_interest, repo_rate, coupon_rate,
        coupon_frequency, time_to_maturity, face_value, valuation_date,
        expiration_date, day_count_convention=day_count_convention
    )
    base_price = base_result["forwardCleanPrice"]
    
    # Цена при +1 bp
    up_result = calculate_bond_forward_price_enhanced(
        spot_clean_price, accrued_interest, repo_rate + 0.01, coupon_rate,
        coupon_frequency, time_to_maturity, face_value, valuation_date,
        expiration_date, day_count_convention=day_count_convention
    )
    up_price = up_result["forwardCleanPrice"]
    
    # Цена при -1 bp
    down_result = calculate_bond_forward_price_enhanced(
        spot_clean_price, accrued_interest, repo_rate - 0.01, coupon_rate,
        coupon_frequency, time_to_maturity, face_value, valuation_date,
        expiration_date, day_count_convention=day_count_convention
    )
    down_price = down_result["forwardCleanPrice"]
    
    # Convexity = (P_up + P_down - 2*P_base) / (Δr)²
    # где Δr = 0.0001 (1 bp в долях)
    convexity = (up_price + down_price - 2 * base_price) / (0.0001 ** 2)
    return float(convexity)


def calculate_repo_sensitivity(
    spot_clean_price: float,
    accrued_interest: float,
    repo_rate: float,
    coupon_rate: float,
    coupon_frequency: int,
    time_to_maturity: float,
    face_value: float = 100.0,
    valuation_date: Optional[str] = None,
    expiration_date: Optional[str] = None,
    day_count_convention: str = "ACT/365"
) -> float:
    """
    Рассчитывает чувствительность к изменению репо ставки (на 1 bp).
    
    Returns:
        Изменение форвардной цены при изменении репо ставки на 1 bp
    """
    # Базовая цена
    base_result = calculate_bond_forward_price_enhanced(
        spot_clean_price, accrued_interest, repo_rate, coupon_rate,
        coupon_frequency, time_to_maturity, face_value, valuation_date,
        expiration_date, day_count_convention=day_count_convention
    )
    base_price = base_result["forwardCleanPrice"]
    
    # Цена при +1 bp репо ставки
    shifted_result = calculate_bond_forward_price_enhanced(
        spot_clean_price, accrued_interest, repo_rate + 0.01, coupon_rate,
        coupon_frequency, time_to_maturity, face_value, valuation_date,
        expiration_date, day_count_convention=day_count_convention
    )
    shifted_price = shifted_result["forwardCleanPrice"]
    
    sensitivity = shifted_price - base_price
    return float(sensitivity)


def calculate_bond_forward_valuation(
    spot_clean_price: float,
    market_forward_price: float,
    accrued_interest: float,
    repo_rate: float,
    coupon_rate: float,
    coupon_frequency: int,
    time_to_maturity: float,
    risk_free_rate: float,
    contract_size: float = 1.0,
    face_value: float = 100.0,
    valuation_date: Optional[str] = None,
    expiration_date: Optional[str] = None,
    last_coupon_date: Optional[str] = None,
    maturity_date: Optional[str] = None,
    day_count_convention: str = "ACT/365",
    yield_curve_tenors: Optional[List[float]] = None,
    yield_curve_rates: Optional[List[float]] = None,
    auto_calculate_ai: bool = True
) -> Dict:
    """
    Расширенная версия расчета справедливой стоимости форварда на облигацию.
    """
    # Рассчитываем справедливую цену форварда
    forward_data = calculate_bond_forward_price_enhanced(
        spot_clean_price=spot_clean_price,
        accrued_interest=accrued_interest,
        repo_rate=repo_rate,
        coupon_rate=coupon_rate,
        coupon_frequency=coupon_frequency,
        time_to_maturity=time_to_maturity,
        face_value=face_value,
        valuation_date=valuation_date,
        expiration_date=expiration_date,
        last_coupon_date=last_coupon_date,
        maturity_date=maturity_date,
        day_count_convention=day_count_convention,
        yield_curve_tenors=yield_curve_tenors,
        yield_curve_rates=yield_curve_rates,
        auto_calculate_ai=auto_calculate_ai
    )
    
    fair_forward_price = forward_data["forwardCleanPrice"]
    
    # Конвертируем проценты в доли
    r = risk_free_rate / 100.0
    T = time_to_maturity
    
    # Стоимость форвардного контракта для лонга
    forward_value_per_unit = (fair_forward_price - market_forward_price) / np.exp(r * T)
    forward_value = forward_value_per_unit * contract_size * (face_value / 100.0)
    
    # Внутренняя стоимость
    intrinsic_value = (spot_clean_price - market_forward_price) * contract_size * (face_value / 100.0)
    
    # Временная стоимость
    time_value = forward_value - intrinsic_value
    
    # Greeks
    delta = np.exp(-r * T)
    rho = spot_clean_price * T * np.exp(-r * T) * contract_size * (face_value / 100.0)
    net_carry = repo_rate - coupon_rate
    
    # Расширенные греки
    dv01 = calculate_dv01(
        spot_clean_price, accrued_interest, repo_rate, coupon_rate,
        coupon_frequency, T, face_value, valuation_date, expiration_date,
        day_count_convention
    )
    
    convexity = calculate_convexity(
        spot_clean_price, accrued_interest, repo_rate, coupon_rate,
        coupon_frequency, T, face_value, valuation_date, expiration_date,
        day_count_convention
    )
    
    repo_sensitivity = calculate_repo_sensitivity(
        spot_clean_price, accrued_interest, repo_rate, coupon_rate,
        coupon_frequency, T, face_value, valuation_date, expiration_date,
        day_count_convention
    )
    
    # Анализ сценариев
    scenarios = []
    spot_prices = [
        spot_clean_price * 0.95,
        spot_clean_price * 0.97,
        spot_clean_price,
        spot_clean_price * 1.03,
        spot_clean_price * 1.05
    ]
    
    for idx, spot in enumerate(spot_prices):
        scenario_forward_data = calculate_bond_forward_price_enhanced(
            spot_clean_price=spot,
            accrued_interest=accrued_interest,
            repo_rate=repo_rate,
            coupon_rate=coupon_rate,
            coupon_frequency=coupon_frequency,
            time_to_maturity=time_to_maturity,
            face_value=face_value,
            valuation_date=valuation_date,
            expiration_date=expiration_date,
            last_coupon_date=last_coupon_date,
            maturity_date=maturity_date,
            day_count_convention=day_count_convention,
            yield_curve_tenors=yield_curve_tenors,
            yield_curve_rates=yield_curve_rates,
            auto_calculate_ai=auto_calculate_ai
        )
        
        scenario_fair_forward = scenario_forward_data["forwardCleanPrice"]
        scenario_forward_value = (scenario_fair_forward - market_forward_price) / np.exp(r * T)
        scenario_forward_value_total = scenario_forward_value * contract_size * (face_value / 100.0)
        
        change = ((spot - spot_clean_price) / spot_clean_price) * 100
        pnl_long = (scenario_fair_forward - market_forward_price) * contract_size * (face_value / 100.0)
        pnl_short = (market_forward_price - scenario_fair_forward) * contract_size * (face_value / 100.0)
        
        scenarios.append({
            "id": idx,
            "name": "Base Case" if idx == 2 else ("Bear" if idx < 2 else "Bull"),
            "spotPrice": float(spot),
            "change": float(change),
            "forwardValue": float(scenario_forward_value_total),
            "pnlLong": float(pnl_long),
            "pnlShort": float(pnl_short),
            "isBase": idx == 2
        })
    
    return {
        "fairForwardPrice": float(fair_forward_price),
        "forwardValue": float(forward_value),
        "intrinsicValue": float(intrinsic_value),
        "timeValue": float(time_value),
        "totalValue": float(forward_value),
        "delta": float(delta),
        "rho": float(rho),
        "netCarry": float(net_carry),
        "scenarios": scenarios,
        # Дополнительные поля для облигаций
        "spotDirtyPrice": forward_data["spotDirtyPrice"],
        "forwardDirtyPrice": forward_data["forwardDirtyPrice"],
        "accruedInterest": float(accrued_interest),
        "aiForward": forward_data["aiForward"],
        "pvCoupons": forward_data["pvCoupons"],
        # Расширенные метрики
        "dv01": float(dv01),
        "convexity": float(convexity),
        "repoSensitivity": float(repo_sensitivity),
        "couponSchedule": forward_data["couponSchedule"],
        "formulaBreakdown": forward_data["formulaBreakdown"],
        "daysToMaturity": forward_data["daysToMaturity"]
    }
