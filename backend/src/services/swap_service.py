"""
Сервис для оценки свопов (IRS, CDS, Basis Swaps, FX Swaps).
Основан на логике из _SWAP для переноса на внутренний_.ipynb
"""
from datetime import datetime, timedelta

from src.services.forward_service import (
    currency_pair,
)


def calculate_swap_valuation(
    notional: float,
    tenor: float,
    fixed_rate: float,
    floating_rate: float,
    spread: float,
    coupons_per_year: int,
    discount_rate: float,
    volatility: float | None = None,
    swap_type: str = "irs"
) -> dict:
    """
    Рассчитывает справедливую стоимость свопа.
    
    Args:
        notional: Номинал (млн)
        tenor: Срок (годы)
        fixed_rate: Фиксированная ставка (%)
        floating_rate: Индекс плавающей ставки (%)
        spread: Спред (bp)
        coupons_per_year: Купонов в год
        discount_rate: Дисконт кривая (базовая ставка, %)
        volatility: Волатильность (%) (опционально)
        swap_type: Тип свопа (irs, cds, basis, xccy)
    
    Returns:
        Результаты оценки свопа
    """
    # Конвертируем проценты в доли
    fixed_rate_decimal = fixed_rate / 100.0
    floating_rate_decimal = (floating_rate + spread / 100) / 100.0
    discount_rate_decimal = discount_rate / 100.0

    # Параметры расчетов
    period_rate = discount_rate_decimal / coupons_per_year
    periods = int(tenor * coupons_per_year)

    # Расчет PV фиксированной ноги
    coupon_amount = notional * fixed_rate_decimal / coupons_per_year
    pv_fixed = 0.0

    for i in range(1, periods + 1):
        discount_factor = 1.0 / (1.0 + period_rate) ** i
        pv_fixed += coupon_amount * discount_factor

    # Добавляем номинал в конце
    final_discount = 1.0 / (1.0 + period_rate) ** periods
    pv_fixed += notional * final_discount

    # Расчет PV плавающей ноги
    # Упрощенная модель: предполагаем, что плавающая ставка равна текущей forward rate
    floating_coupon = notional * floating_rate_decimal / coupons_per_year
    pv_floating = 0.0

    for i in range(1, periods + 1):
        discount_factor = 1.0 / (1.0 + period_rate) ** i
        pv_floating += floating_coupon * discount_factor

    # Добавляем номинал в конце
    pv_floating += notional * final_discount

    # Стоимость свопа (для получателя фиксированной ноги)
    swap_value = pv_fixed - pv_floating

    # Расчет денежных потоков
    cashflows = []
    base_date = datetime.now()

    for i in range(1, periods + 1):
        payment_date = base_date + timedelta(days=int(365 / coupons_per_year * i))
        discount_factor = 1.0 / (1.0 + period_rate) ** i

        fixed_leg = coupon_amount
        floating_leg = floating_coupon
        net = fixed_leg - floating_leg
        pv = net * discount_factor

        cashflows.append({
            "period": i,
            "date": payment_date.strftime("%Y-%m-%d"),
            "fixedLeg": float(fixed_leg),
            "floatingLeg": float(floating_leg),
            "net": float(net),
            "pv": float(pv)
        })

    # Расчет метрик риска
    # Duration (Modified Duration)
    duration = 0.0
    for i in range(1, periods + 1):
        discount_factor = 1.0 / (1.0 + period_rate) ** i
        weight = (coupon_amount * discount_factor) / pv_fixed
        duration += (i / coupons_per_year) * weight

    # DV01 (Dollar Value of 01) - изменение стоимости при изменении ставки на 1bp
    dv01 = duration * pv_fixed * 0.0001

    # Spread DV01: чувствительность плавающей ноги к изменению спреда на 1bp
    # Пересчитываем PV плавающей ноги при спреде + 1bp
    spread_bump = 0.01  # 1 basis point в процентных пунктах
    floating_rate_bumped = (floating_rate + (spread + spread_bump) / 100) / 100.0
    floating_coupon_bumped = notional * floating_rate_bumped / coupons_per_year
    pv_floating_bumped = 0.0
    for i in range(1, periods + 1):
        discount_factor = 1.0 / (1.0 + period_rate) ** i
        pv_floating_bumped += floating_coupon_bumped * discount_factor
    pv_floating_bumped += notional * final_discount
    spread_dv01 = abs(pv_floating_bumped - pv_floating)

    # Convexity
    convexity = 0.0
    for i in range(1, periods + 1):
        discount_factor = 1.0 / (1.0 + period_rate) ** i
        weight = (coupon_amount * discount_factor) / pv_fixed
        time_squared = (i / coupons_per_year) ** 2
        convexity += time_squared * weight

    # Анализ сценариев
    scenarios = []
    rate_shifts = [-2.0, -1.0, 0.0, 1.0, 2.0]  # в процентных пунктах (п.п.)

    for shift in rate_shifts:
        shifted_fixed = fixed_rate + shift
        shifted_floating = floating_rate + shift

        # Пересчитываем PV для сценария
        shifted_fixed_decimal = shifted_fixed / 100.0
        shifted_floating_decimal = (shifted_floating + spread / 100) / 100.0

        scenario_pv_fixed = 0.0
        scenario_coupon = notional * shifted_fixed_decimal / coupons_per_year
        for i in range(1, periods + 1):
            discount_factor = 1.0 / (1.0 + period_rate) ** i
            scenario_pv_fixed += scenario_coupon * discount_factor
        scenario_pv_fixed += notional * final_discount

        scenario_pv_floating = 0.0
        scenario_floating_coupon = notional * shifted_floating_decimal / coupons_per_year
        for i in range(1, periods + 1):
            discount_factor = 1.0 / (1.0 + period_rate) ** i
            scenario_pv_floating += scenario_floating_coupon * discount_factor
        scenario_pv_floating += notional * final_discount

        scenario_swap_value = scenario_pv_fixed - scenario_pv_floating
        base_swap_value = swap_value
        pnl = scenario_swap_value - base_swap_value

        scenarios.append({
            "name": f"{'+' if shift >= 0 else ''}{shift:.0f}%" if shift != 0 else "Base Case",
            "fixedRate": float(shifted_fixed),
            "floatingRate": float(shifted_floating),
            "pvFixed": float(scenario_pv_fixed),
            "pvFloating": float(scenario_pv_floating),
            "swapValue": float(scenario_swap_value),
            "pnl": float(pnl),
            "isBase": shift == 0.0
        })

    return {
        "pvFixedLeg": float(pv_fixed),
        "pvFloatingLeg": float(pv_floating),
        "swapValue": float(swap_value),
        "duration": float(duration),
        "dv01": float(dv01),
        "spreadDv01": float(spread_dv01),
        "convexity": float(convexity),
        "cashflows": cashflows,
        "scenarios": scenarios
    }


def _diff_spot(spot_min: float, spot_max: float) -> float:
    """Разница между макс и мин спотом."""
    return spot_max - spot_min


def _diff_swap_points(sp_deal: float, sp_calc: float) -> float:
    """Расхождение swap points (deal vs calculated)."""
    return sp_deal - sp_calc


def _swap_points_from_rates(
    spot: float,
    rate_internal: float,
    rate_external: float,
    days: int,
) -> float:
    """
    Расчёт swap points из ставок.
    sp = spot * ((1 + r_int/100) / (1 + r_ext/100))^(T/365) - spot
    """
    t = days / 365.0
    return spot * ((1 + rate_internal / 100) / (1 + rate_external / 100)) ** t - spot


def calculate_fx_swap_valuation(
    buy_currency_near: str,
    sell_currency_near: str,
    nominal_buy_near: float,
    nominal_sell_near: float,
    date_near: str,
    buy_currency_far: str,
    sell_currency_far: str,
    nominal_buy_far: float,
    nominal_sell_far: float,
    date_far: str,
    valuation_date: str,
    settlement_currency: str,
    spot_min: float,
    spot_max: float,
    rate_internal: float,
    rate_external: float,
) -> dict:
    """
    Оценка FX-свопа (две ноги: near + far).

    Args:
        buy/sell_currency_near/far: валюты ближней/дальней ног
        nominal_buy/sell_near/far: суммы покупки/продажи
        date_near/far: даты расчёта ног (YYYY-MM-DD)
        valuation_date: дата оценки
        settlement_currency: валюта расчёта
        spot_min/max: диапазон спота
        rate_internal/external: ставки внутренней / внешней валюты (%)

    Returns:
        FV min/max, swap points deal vs calc, divergence, DFs, currency pair
    """
    if spot_min > spot_max:
        raise ValueError("spotMin must be less than or equal to spotMax")

    if buy_currency_near != sell_currency_far or sell_currency_near != buy_currency_far:
        raise ValueError(
            "FX swap legs inconsistent: near buy/sell currencies must be reversed in far leg"
        )

    val_dt = datetime.strptime(valuation_date, "%Y-%m-%d")
    near_dt = datetime.strptime(date_near, "%Y-%m-%d")
    far_dt = datetime.strptime(date_far, "%Y-%m-%d")

    days_near = max((near_dt - val_dt).days, 0)
    days_far = max((far_dt - val_dt).days, 0)

    # Discount factors: DF = 1 / (1 + rate/100 * days/365)
    df_int_near = 1.0 / (1 + rate_internal / 100 * days_near / 365)
    df_ext_near = 1.0 / (1 + rate_external / 100 * days_near / 365)
    df_int_far = 1.0 / (1 + rate_internal / 100 * days_far / 365)
    df_ext_far = 1.0 / (1 + rate_external / 100 * days_far / 365)

    # Currency pair by priority
    pair = currency_pair(buy_currency_near, sell_currency_near)

    # Deal FX rates (implied from nominal amounts)
    fx_near = nominal_sell_near / nominal_buy_near if nominal_buy_near != 0 else 0
    fx_far = nominal_sell_far / nominal_buy_far if nominal_buy_far != 0 else 0

    # Swap points deal = far rate - near rate
    sp_deal = fx_far - fx_near

    # Calculated swap points from rates (using mid spot)
    spot_mid = (spot_min + spot_max) / 2.0
    sp_calc_near = _swap_points_from_rates(spot_mid, rate_internal, rate_external, days_near)
    sp_calc_far = _swap_points_from_rates(spot_mid, rate_internal, rate_external, days_far)
    sp_calc = sp_calc_far - sp_calc_near

    divergence = _diff_swap_points(sp_deal, sp_calc)

    # Fair value for NEAR leg
    # FV = (nom_buy * DF_buy * fx_buy - nom_sell * DF_sell * fx_sell) / 1000
    # For near leg buy_currency is settlement vs foreign
    is_rub_buy_near = buy_currency_near == "RUB"

    def _fv_near(spot: float) -> float:
        if is_rub_buy_near:
            return (nominal_buy_near * df_int_near - nominal_sell_near * spot * df_ext_near) / 1000
        return (nominal_buy_near * spot * df_ext_near - nominal_sell_near * df_int_near) / 1000

    is_rub_buy_far = buy_currency_far == "RUB"

    def _fv_far(spot: float) -> float:
        if is_rub_buy_far:
            return (nominal_buy_far * df_int_far - nominal_sell_far * spot * df_ext_far) / 1000
        return (nominal_buy_far * spot * df_ext_far - nominal_sell_far * df_int_far) / 1000

    fv_near_min = _fv_near(spot_min)
    fv_near_max = _fv_near(spot_max)
    fv_far_min = _fv_far(spot_min)
    fv_far_max = _fv_far(spot_max)

    fv_total_min = fv_near_min + fv_far_min
    fv_total_max = fv_near_max + fv_far_max

    return {
        "currencyPair": pair,
        "direction": f"{buy_currency_near}/{sell_currency_near}",
        "spotMin": float(spot_min),
        "spotMax": float(spot_max),
        "spotDiff": float(_diff_spot(spot_min, spot_max)),
        "daysNear": days_near,
        "daysFar": days_far,
        "dfInternalNear": float(df_int_near),
        "dfExternalNear": float(df_ext_near),
        "dfInternalFar": float(df_int_far),
        "dfExternalFar": float(df_ext_far),
        "fxNear": float(fx_near),
        "fxFar": float(fx_far),
        "swapPointsDeal": float(sp_deal),
        "swapPointsCalc": float(sp_calc),
        "divergence": float(divergence),
        "fvNearMin": float(fv_near_min),
        "fvNearMax": float(fv_near_max),
        "fvFarMin": float(fv_far_min),
        "fvFarMax": float(fv_far_max),
        "fvTotalMin": float(fv_total_min),
        "fvTotalMax": float(fv_total_max),
        "rateInternal": float(rate_internal),
        "rateExternal": float(rate_external),
    }
