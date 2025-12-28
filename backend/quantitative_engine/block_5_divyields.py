# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import requests
from typing import Dict, List

def get_dividends_yield(ticker: str, avg_price: float, end_date: pd.Timestamp, years_back: int = 3) -> float:
    """Вспомогательная функция для получения див. доходности через MOEX API."""
    
    # Ручные корректировки (из вашего кода)
    MANUAL_DIVIDEND_YIELDS = {'VTBR': 9.9}
    STOCK_SPLITS = {'PLZL': pd.Timestamp('2025-03-26')}
    
    if ticker in MANUAL_DIVIDEND_YIELDS:
        return MANUAL_DIVIDEND_YIELDS[ticker] / 100

    try:
        url = f"http://iss.moex.com/iss/securities/{ticker}/dividends.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'dividends' not in data or not data['dividends']['data']:
            return 0.0

        df = pd.DataFrame(data['dividends']['data'], columns=data['dividends']['columns'])
        df['registryclosedate'] = pd.to_datetime(df['registryclosedate'], errors='coerce')
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['registryclosedate', 'value'])
        df = df[df['value'] > 0]

        if df.empty:
            return 0.0

        # Фильтр по периоду
        start_date = end_date - pd.DateOffset(years=years_back)
        df = df[(df['registryclosedate'] >= start_date) & (df['registryclosedate'] <= end_date)]

        if df.empty:
            return 0.0

        # Корректировка на сплиты (если были)
        if ticker in STOCK_SPLITS:
            split_date = STOCK_SPLITS[ticker]
            df_after = df[df['registryclosedate'] >= split_date]
            if not df_after.empty:
                df = df_after

        total_divs = df['value'].sum()
        if avg_price <= 0: return 0.0

        # Аннуализация див. доходности
        date_range_days = (df['registryclosedate'].max() - df['registryclosedate'].min()).days
        date_range_years = date_range_days / 365.25
        
        if date_range_years < 0.1: # Если выплата одна или за короткий срок
            date_range_years = 1.0

        return (total_divs / avg_price) / date_range_years

    except Exception:
        return 0.0

def calculate_dividend_yields(returns: pd.DataFrame, priced_df: pd.DataFrame) -> np.ndarray:
    """
    БЛОК 5: Расчёт полной ожидаемой доходности (Capital Gains + Dividends).
    Возвращает: mu (вектор ожидаемых доходностей)
    """

    asset_names = returns.columns.tolist() 
    
    YEARS_LOOKBACK = 3
    TRADING_DAYS = 252
    
    # 1. Считаем Capital Gains (аннуализированное среднее лог-доходностей)
    capital_gains = returns.mean() * TRADING_DAYS
    
    # 2. Считаем Дивидендную доходность
    # Для этого нам нужны средние цены (их можно примерно восстановить из накопленных доходностей, 
    # но лучше передать priced_df. Для бэкенда мы используем упрощение или передачу цен)
    
    dividend_yields = []
    end_date = returns.index.max()
    
    for ticker in asset_names:
        # В идеале здесь должна быть средняя цена из priced_df. 
        # Еслиpriced_df не передан, используем 1.0 (тогда вернется абсолютный процент)
        # В нашей структуре мы предполагаем, что расчет идет корректно.
        
        # Эмуляция средней цены для API (в реальности лучше передать изpriced_df)
        avg_price = priced_df[ticker].mean() # Заглушка, если нет доступа к priced_df
        
        div_y = get_dividends_yield(ticker, avg_price, end_date, YEARS_LOOKBACK)
        dividend_yields.append(div_y)
        
    # 3. Итоговое mu
    mu_total = capital_gains + pd.Series(dividend_yields, index=asset_names)
    
    return mu_total.values * 0.8 