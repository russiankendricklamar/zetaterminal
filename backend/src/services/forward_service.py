"""
Сервис для оценки форвардов различных типов.
Основан на логике из _FORWARD для переноса на внутренний.ipynb
"""
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# Словарь приоритезации валют (из notebook)
CURRENCY_PRIORITY = {
    'XDR': 0, 'EUR': 1, 'GBP': 2, 'AUD': 3, 'NZD': 4, 'USD': 5,
    'CAD': 6, 'CHF': 7, 'TRY': 8, 'DKK': 9, 'NOK': 10, 'ZAR': 11,
    'SEK': 12, 'CNY': 13, 'CNH': 14, 'BRL': 15, 'HKD': 16, 'INR': 17,
    'CZK': 18, 'KZT': 19, 'JPY': 20, 'BYN': 21, 'SGD': 22, 'KRW': 23,
    'HUF': 24, 'RON': 25, 'AZN': 26, 'BGN': 27, 'UZS': 28, 'KGS': 29,
    'MDL': 30, 'PLN': 31, 'TMT': 32, 'TJS': 33, 'UAH': 34, 'AMD': 35,
    'GEL': 36, 'RUB': 37
}

# Кривые для валют (из notebook)
CURRENCY_CURVES = {
    'CNY': 'CNY SHIBOR REF', 'USD': 'USD SOFR REF', 'EUR': 'EUR ESTR REF',
    'AUD': 'AUD AONIA ICAA', 'CAD': 'CAD CORRA REF', 'CHF': 'CHF SARON ICAP',
    'GBP': 'GBP SONIA TWMK', 'HKD': 'HKD HONIA TRHK', 'JPY': 'JPY TONAR TKFX',
    'RUB': 'RUB RUONIA COMB', 'TRY': 'TRY TLREF REF'
}


def currency_pair(curr1: str, curr2: str) -> str:
    """Определяет валютную пару по приоритету."""
    try:
        if CURRENCY_PRIORITY.get(curr1, 99) < CURRENCY_PRIORITY.get(curr2, 99):
            return curr1 + curr2
        else:
            return curr2 + curr1
    except KeyError:
        return curr1 + curr2


def tenor_for_days(days: int) -> tuple[int, int]:
    """Определяет меньший и больший тенор для заданного количества дней."""
    if days < 7:
        return (1, 1)
    elif days <= 14:
        return (7, 14)
    elif days <= 30:
        return (14, 31)
    elif days <= 60:
        return (31, 59)
    elif days <= 90:
        return (59, 90)
    elif days <= 180:
        return (90, 180)
    elif days <= 270:
        return (180, 270)
    elif days <= 360:
        return (270, 360)
    else:
        return (360, 360)


def forward_rate_change(days: int, rate_internal: float, rate_external: float) -> float:
    """Изменение форвардного курса на основе ставок."""
    return ((1 + (rate_internal / 100)) ** (days / 365)) / ((1 + (rate_external / 100)) ** (days / 365))


def fair_value_fx(
    buy_currency: str,
    buy_amount: float,
    sell_amount: float,
    disc_internal: float,
    disc_external: float,
    spot: float
) -> float:
    """
    Справедливая стоимость валютного форварда (из notebook).
    
    Args:
        buy_currency: Покупаемая валюта
        buy_amount: Сумма покупки
        sell_amount: Сумма продажи
        disc_internal: Дисконт-фактор для внутренней валюты
        disc_external: Дисконт-фактор для внешней валюты
        spot: Спот курс
    
    Returns:
        Справедливая стоимость в тыс. расчетной валюты
    """
    if buy_currency == 'RUB':
        fv = (buy_amount * 1 * disc_internal - sell_amount * spot * disc_external) / 1000
    else:
        fv = (buy_amount * spot * disc_external - sell_amount * 1 * disc_internal) / 1000
    return fv


def calculate_fx_forward_valuation(
    buy_currency: str,
    sell_currency: str,
    buy_amount: float,
    sell_amount: float,
    deal_date: str,
    valuation_date: str,
    settlement_currency: str,
    spot_price: float,
    market_forward_price: float,
    time_to_maturity: float,
    # Ставки: передаем напрямую или используем дефолтные значения
    internal_rate: Optional[float] = None,
    external_rate: Optional[float] = None,
    expiration_date: Optional[str] = None
) -> Dict:
    """
    Рассчитывает справедливую стоимость валютного форварда по логике из notebook.
    """
    # Определяем валютную пару
    currency_pair_str = currency_pair(sell_currency, buy_currency)
    
    # КРИТИЧНО: Определяем ставки для конкретных валют
    # internal_rate - ставка для покупаемой валюты (buy_currency)
    # external_rate - ставка для продаваемой валюты (sell_currency)
    # Если ставки не переданы, используем упрощенные значения по умолчанию
    default_rates = {
        'RUB': 15.0, 'EUR': 1.7, 'USD': 4.5, 'CNY': 1.7,
        'GBP': 4.0, 'JPY': 0.1, 'CHF': 1.0, 'AUD': 4.0
    }
    
    if internal_rate is None:
        internal_rate = default_rates.get(buy_currency, 4.0)
    
    if external_rate is None:
        external_rate = default_rates.get(sell_currency, 4.0)
    
    # Определяем ставки для валютной пары
    # Валютная пара определяется по приоритету: currency_pair(sell, buy)
    # Базовая валюта (base) - первые 3 символа пары
    # Котируемая валюта (quote) - последние 3 символа пары
    base_currency = currency_pair_str[:3]
    quote_currency = currency_pair_str[3:]
    
    # Определяем ставки для базовой и котируемой валют
    if base_currency == buy_currency:
        rate_base = internal_rate
    elif base_currency == sell_currency:
        rate_base = external_rate
    else:
        rate_base = default_rates.get(base_currency, 4.0)
    
    if quote_currency == buy_currency:
        rate_quote = internal_rate
    elif quote_currency == sell_currency:
        rate_quote = external_rate
    else:
        rate_quote = default_rates.get(quote_currency, 4.0)
    
    # Для обратной совместимости с остальным кодом
    rate_buy_currency = internal_rate
    rate_sell_currency = external_rate
    
    # КРИТИЧНО: Если expiration_date предоставлен, пересчитываем T точно из дат
    if expiration_date and valuation_date:
        val_dt = datetime.strptime(valuation_date, "%Y-%m-%d")
        exp_dt = datetime.strptime(expiration_date, "%Y-%m-%d")
        days_to_maturity = (exp_dt - val_dt).days
        time_to_maturity = days_to_maturity / 365.0
    else:
        # Конвертируем время до экспирации в дни
        days_to_maturity = int(time_to_maturity * 365)
    
    # Определяем тенора
    tenor_low, tenor_high = tenor_for_days(days_to_maturity)
    
    # Упрощенная интерполяция ставок (в реальности из БД)
    # КРИТИЧНО: Если ставки переданы явно (не None), используем их без интерполяции
    # Интерполяция применяется только для дефолтных ставок
    if internal_rate is not None and external_rate is not None:
        # Используем исходные ставки без интерполяции для точного соответствия Investing.com
        interp_rate_base = rate_base
        interp_rate_quote = rate_quote
        interp_rate_buy = rate_buy_currency
        interp_rate_sell = rate_sell_currency
    else:
        # Применяем интерполяцию только для дефолтных ставок
        if days_to_maturity <= tenor_low:
            interp_rate_base = rate_base
            interp_rate_quote = rate_quote
            interp_rate_buy = rate_buy_currency
            interp_rate_sell = rate_sell_currency
        elif days_to_maturity >= tenor_high:
            interp_rate_base = rate_base * 1.1  # Упрощение
            interp_rate_quote = rate_quote * 1.05
            interp_rate_buy = rate_buy_currency * 1.1
            interp_rate_sell = rate_sell_currency * 1.05
        else:
            # Линейная интерполяция
            ratio = (days_to_maturity - tenor_low) / (tenor_high - tenor_low)
            interp_rate_base = rate_base * (1 + ratio * 0.1)
            interp_rate_quote = rate_quote * (1 + ratio * 0.05)
            interp_rate_buy = rate_buy_currency * (1 + ratio * 0.1)
            interp_rate_sell = rate_sell_currency * (1 + ratio * 0.05)
    
    # Для обратной совместимости
    interp_internal_rate = interp_rate_buy
    interp_external_rate = interp_rate_sell
    
    # Расчет дисконт-факторов (из notebook, формула 2)
    days_to_settlement = days_to_maturity
    disc_internal = 1 / (1 + interp_internal_rate / 100 * days_to_settlement / 365)
    disc_external = 1 / (1 + interp_external_rate / 100 * days_to_settlement / 365)
    
    # Расчет справедливой стоимости
    fair_value_min = fair_value_fx(
        buy_currency=buy_currency,
        buy_amount=buy_amount,
        sell_amount=sell_amount,
        disc_internal=disc_internal,
        disc_external=disc_external,
        spot=spot_price * 0.99  # Спот мин (упрощение)
    )
    
    fair_value_max = fair_value_fx(
        buy_currency=buy_currency,
        buy_amount=buy_amount,
        sell_amount=sell_amount,
        disc_internal=disc_internal,
        disc_external=disc_external,
        spot=spot_price * 1.01  # Спот макс (упрощение)
    )
    
    # Расчет справедливого форвардного курса по Covered Interest Parity
    # ПРАВИЛЬНЫЙ РАСЧЕТ: Используем ставки по валютам, а не по приоритету
    # interp_rate_buy - ставка для покупаемой валюты (внутренняя)
    # interp_rate_sell - ставка для продаваемой валюты (внешняя)
    # Формула: fair_forward = spot × (1 + r_sell × T) / (1 + r_buy × T)
    # Это верно независимо от того, EUR/RUB это или RUB/EUR
    T = time_to_maturity
    rate_buy_decimal = interp_rate_buy / 100.0  # Ставка для покупаемой валюты (в долях)
    rate_sell_decimal = interp_rate_sell / 100.0  # Ставка для продаваемой валюты (в долях)
    
    # Коэффициент изменения форвардного курса
    # fair_forward = spot × (1 + r_sell × T) / (1 + r_buy × T)
    forward_rate_change_val = (1 + rate_sell_decimal * T) / (1 + rate_buy_decimal * T)
    
    # Справедливый форвардный курс
    fair_forward_rate = spot_price * forward_rate_change_val
    
    # Расчет форвардных курсов для диапазона (MIN/MAX) - тоже используют правильную формулу
    forward_rate_min = (spot_price * 0.99) * forward_rate_change_val
    forward_rate_max = (spot_price * 1.01) * forward_rate_change_val
    
    # Сравнение с рыночным курсом
    if market_forward_price >= forward_rate_min and market_forward_price <= forward_rate_max:
        forward_diff = "В рынке"
    elif market_forward_price < forward_rate_min:
        forward_diff = market_forward_price - forward_rate_min
    else:
        forward_diff = market_forward_price - forward_rate_max
    
    # КРИТИЧНО: Расчет NPV по правильным формулам
    # 1. PnL на момент экспирации = (forwardDealRate - fairForwardRate) * notionalBuy
    #    где notionalBuy - это buy_amount в валюте покупки (buy_currency)
    #    ВАЖНО: buy_amount должен быть в валюте покупки (EUR), не в валюте расчетов (RUB)
    #    Формула: PnL = (market_forward - fair_forward) * buy_amount_eur
    #    Результат в валюте расчетов (RUB)
    
    # КРИТИЧНО: buy_amount должен быть в валюте покупки (buy_currency)
    # Формула PnL: (market_forward - fair_forward) * buy_amount_eur
    # Результат автоматически в валюте расчетов (RUB), так как курсы в ₽/EUR
    
    # ОТЛАДКА: Логируем входные параметры для диагностики бага NPV
    logger.info(f"NPV Debug - buy_amount={buy_amount:,.2f}, buy_currency={buy_currency}, "
                f"sell_currency={sell_currency}, spot_price={spot_price:.6f}, "
                f"market_forward={market_forward_price:.6f}, fair_forward={fair_forward_rate:.6f}")
    
    buy_amount_in_buy_currency = buy_amount
    
    # Расчет PnL на момент экспирации
    pnl_at_maturity = (market_forward_price - fair_forward_rate) * buy_amount_in_buy_currency
    logger.debug(f"NPV Debug - pnl_at_maturity={pnl_at_maturity:,.2f} RUB, "
                f"buy_amount_in_buy_currency={buy_amount_in_buy_currency:,.2f} {buy_currency}")
    
    # 2. NPV контракта в валюте расчетов = pnlAtMaturity / (1 + rate_settlement * T)
    #    Дисконтируем по ставке валюты расчетов (settlement_currency)
    #    Если settlement_currency = RUB, используем ставку для RUB
    #    Если settlement_currency = EUR, используем ставку для EUR
    if settlement_currency == buy_currency:
        rate_settlement = interp_rate_buy
    elif settlement_currency == sell_currency:
        rate_settlement = interp_rate_sell
    else:
        # По умолчанию используем ставку для sell_currency
        rate_settlement = interp_rate_sell
    
    rate_settlement_decimal = rate_settlement / 100.0
    npv_contract_rub = pnl_at_maturity / (1 + rate_settlement_decimal * T)
    
    # ОТЛАДКА: Логируем результат NPV
    logger.info(f"NPV Debug - rate_settlement={rate_settlement:.4f}%, T={T:.6f}, "
                f"discount_factor={1 + rate_settlement_decimal * T:.6f}, "
                f"pnl_at_maturity={pnl_at_maturity:,.2f} RUB, "
                f"npv_contract_rub={npv_contract_rub:,.2f} RUB")
    
    # 3. NPV на единицу (опционально, для справки)
    # ВАЖНО: Используем buy_amount_in_buy_currency для правильного расчета
    npv_per_unit_rub_per_eur = npv_contract_rub / buy_amount_in_buy_currency if buy_amount_in_buy_currency > 0 else 0.0
    
    # Анализ сценариев
    scenarios = []
    spot_scenarios = [spot_price * 0.8, spot_price * 0.9, spot_price, spot_price * 1.1, spot_price * 1.2]
    
    for idx, spot in enumerate(spot_scenarios):
        # Для каждого сценария пересчитываем справедливый форвардный курс по CIP
        # Формула: fair_forward = spot × (1 + r_sell × T) / (1 + r_buy × T)
        scenario_forward_rate = spot * (1 + rate_sell_decimal * T) / (1 + rate_buy_decimal * T)
        scenario_pnl_at_maturity = (market_forward_price - scenario_forward_rate) * buy_amount_in_buy_currency
        scenario_npv = scenario_pnl_at_maturity / (1 + rate_settlement_decimal * T)
        
        scenarios.append({
            "id": idx,
            "name": "Base Case" if idx == 2 else ("Bear" if idx < 2 else "Bull"),
            "spotPrice": float(spot),
            "change": float(((spot - spot_price) / spot_price) * 100),
            "forwardValue": float(scenario_npv),
            "pnlLong": float(scenario_npv),  # NPV в RUB
            "pnlShort": float(-scenario_npv),
            "isBase": idx == 2
        })
    
    return {
        "fairForwardPrice": float(fair_forward_rate),
        "forwardValue": float(npv_contract_rub),  # NPV контракта в RUB
        "intrinsicValue": float(spot_price - market_forward_price),
        "timeValue": 0.0,  # Для валютных форвардов рассчитывается иначе
        "totalValue": float(npv_contract_rub),  # NPV = totalValue
        "delta": 1.0,  # Упрощение
        "rho": 0.0,  # Упрощение
        "netCarry": float(interp_internal_rate - interp_external_rate),
        "scenarios": scenarios,
        "currencyPair": currency_pair_str,
        "forwardRateMin": float(forward_rate_min),
        "forwardRateMax": float(forward_rate_max),
        "forwardDiff": forward_diff if isinstance(forward_diff, str) else float(forward_diff),
        "fairValueMin": float(fair_value_min),
        "fairValueMax": float(fair_value_max),
        "discountFactorInternal": float(disc_internal),
        "discountFactorExternal": float(disc_external),
        # Дополнительные поля для отладки
        "pnlAtMaturity": float(pnl_at_maturity),
        "npvPerUnit": float(npv_per_unit_rub_per_eur),
        "fairForwardRate": float(fair_forward_rate)
    }


def calculate_cost_of_carry_forward(
    spot_price: float,
    dividend_yield: float,
    carrying_cost: float,
    convenience_yield: float,
    time_to_maturity: float,
    risk_free_rate: float,
    market_forward_price: float,
    contract_size: float
) -> Dict:
    """
    Рассчитывает справедливую стоимость форварда по модели Cost-of-Carry.
    Используется для облигаций, товаров, акций, ставок.
    """
    # Конвертируем проценты в доли
    r = risk_free_rate / 100.0
    d = dividend_yield / 100.0
    c = carrying_cost / 100.0
    y = convenience_yield / 100.0
    T = time_to_maturity
    
    # Справедливая цена форварда: F = S0 * e^((r + c - d - y) * T)
    net_carry = r + c - d - y
    fair_forward_price = spot_price * np.exp(net_carry * T)
    
    # Стоимость форвардного контракта для лонга: (S - K) / e^(r*T)
    K = market_forward_price
    forward_value = (spot_price - K) / np.exp(r * T)
    
    # Внутренняя стоимость
    intrinsic_value = spot_price - K
    
    # Временная стоимость
    time_value = forward_value - intrinsic_value
    
    # Greeks
    delta = np.exp(-r * T)
    rho = spot_price * T * np.exp(net_carry * T)
    
    # Анализ сценариев
    scenarios = []
    spot_prices = [
        spot_price * 0.8,
        spot_price * 0.9,
        spot_price,
        spot_price * 1.1,
        spot_price * 1.2
    ]
    
    for idx, spot in enumerate(spot_prices):
        change = ((spot - spot_price) / spot_price) * 100
        scenario_forward_value = (spot - K) / np.exp(r * T)
        pnl_long = (spot - K) * contract_size
        pnl_short = (K - spot) * contract_size
        
        scenarios.append({
            "id": idx,
            "name": "Base Case" if idx == 2 else ("Bear" if idx < 2 else "Bull"),
            "spotPrice": float(spot),
            "change": float(change),
            "forwardValue": float(scenario_forward_value),
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
        "netCarry": float(net_carry * 100),
        "scenarios": scenarios
    }


def calculate_forward_valuation(
    forward_type: str,
    spot_price: float,
    time_to_maturity: float,
    market_forward_price: float,
    contract_size: float = 1.0,
    # Cost-of-Carry параметры
    dividend_yield: Optional[float] = 0.0,
    carrying_cost: Optional[float] = 0.0,
    convenience_yield: Optional[float] = 0.0,
    risk_free_rate: Optional[float] = None,
    repo_rate: Optional[float] = None,
    # FX параметры
    buy_currency: Optional[str] = None,
    sell_currency: Optional[str] = None,
    buy_amount: Optional[float] = None,
    sell_amount: Optional[float] = None,
    deal_date: Optional[str] = None,
    valuation_date: Optional[str] = None,
    expiration_date: Optional[str] = None,
    settlement_currency: Optional[str] = "RUB",
    internal_rate: Optional[float] = None,
    external_rate: Optional[float] = None
) -> Dict:
    """
    Рассчитывает справедливую стоимость форварда различных типов.
    
    Args:
        forward_type: Тип форварда (fx, bond, commodity, equity, rate)
        spot_price: Спот цена
        time_to_maturity: Время до экспирации (лет)
        market_forward_price: Рыночная цена форварда
        contract_size: Размер контракта
        dividend_yield: Дивиденды / Купоны (%)
        carrying_cost: Стоимость хранения (%)
        convenience_yield: Удобство владения (%)
        risk_free_rate: Безрисковая ставка (%)
        buy_currency: Покупаемая валюта (для fx)
        sell_currency: Продаваемая валюта (для fx)
        buy_amount: Сумма покупки (для fx)
        sell_amount: Сумма продажи (для fx)
        deal_date: Дата сделки (для fx)
        valuation_date: Дата оценки (для fx)
        settlement_currency: Валюта расчетов (для fx)
    
    Returns:
        Результаты оценки форварда
    """
    if forward_type == "fx":
        # Валютный форвард - используем логику из notebook
        if not all([buy_currency, sell_currency, buy_amount, sell_amount]):
            raise ValueError("Для валютного форварда необходимо указать buy_currency, sell_currency, buy_amount, sell_amount")
        
        return calculate_fx_forward_valuation(
            buy_currency=buy_currency,
            sell_currency=sell_currency,
            buy_amount=buy_amount,
            sell_amount=sell_amount,
            deal_date=deal_date or datetime.now().strftime("%Y-%m-%d"),
            valuation_date=valuation_date or datetime.now().strftime("%Y-%m-%d"),
            expiration_date=expiration_date,
            settlement_currency=settlement_currency,
            spot_price=spot_price,
            market_forward_price=market_forward_price,
            time_to_maturity=time_to_maturity,
            internal_rate=internal_rate,
            external_rate=external_rate
        )
    else:
        # Остальные типы - используем Cost-of-Carry
        if risk_free_rate is None:
            raise ValueError("Для форвардов типа bond/commodity/equity/rate необходимо указать risk_free_rate")
        
        return calculate_cost_of_carry_forward(
            spot_price=spot_price,
            dividend_yield=dividend_yield or 0.0,
            carrying_cost=carrying_cost or 0.0,
            convenience_yield=convenience_yield or 0.0,
            time_to_maturity=time_to_maturity,
            risk_free_rate=risk_free_rate,
            market_forward_price=market_forward_price,
            contract_size=contract_size
        )
