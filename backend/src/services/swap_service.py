"""
Сервис для оценки свопов (IRS, CDS, Basis Swaps).
Основан на логике из _SWAP для переноса на внутренний_.ipynb
"""
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta


def calculate_swap_valuation(
    notional: float,
    tenor: float,
    fixed_rate: float,
    floating_rate: float,
    spread: float,
    coupons_per_year: int,
    discount_rate: float,
    volatility: Optional[float] = None,
    swap_type: str = "irs"
) -> Dict:
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
    
    # Spread DV01
    spread_dv01 = dv01 * 0.7  # Упрощенная оценка
    
    # Convexity
    convexity = 0.0
    for i in range(1, periods + 1):
        discount_factor = 1.0 / (1.0 + period_rate) ** i
        weight = (coupon_amount * discount_factor) / pv_fixed
        time_squared = (i / coupons_per_year) ** 2
        convexity += time_squared * weight
    
    # Анализ сценариев
    scenarios = []
    rate_shifts = [-2.0, -1.0, 0.0, 1.0, 2.0]  # в процентах
    
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
            "name": f"{'+' if shift >= 0 else ''}{shift:.0f}bp" if shift != 0 else "Base Case",
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
