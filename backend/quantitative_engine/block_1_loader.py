# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import requests
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

# Константы (можно вынести в отдельный config.py, но пока оставим здесь)
TICKERS = ['SBER', 'GAZP', 'YDEX', 'TATN', 'MOEX', 'PHOR', 'NVTK', 'LKOH', 'PLZL', 'VTBR']
START_DATE = '2024-11-01'
END_DATE = '2025-12-01'
CACHE_DIR = Path('./data_cache')
FORCE_RELOAD = False # В бэкенде лучше поставить False, чтобы не качать данные при каждом перезапуске

# Вспомогательные функции (уже есть в вашем коде)
def get_cache_path(ticker: str) -> Path:
    return CACHE_DIR / f"{ticker}_{START_DATE}_{END_DATE}.parquet"

def load_from_cache(ticker: str) -> Optional[pd.DataFrame]:
    cache_path = get_cache_path(ticker)
    if cache_path.exists():
        try:
            return pd.read_parquet(cache_path)
        except:
            return None
    return None

def save_to_cache(ticker: str, df: pd.DataFrame) -> None:
    CACHE_DIR.mkdir(exist_ok=True)
    try:
        df.to_parquet(get_cache_path(ticker))
    except:
        pass

def fetch_from_moex_complete(ticker: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    url = f"https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
    all_rows, start_idx = [], 0
    columns = None
    
    while True:
        params = {'from': start_date, 'till': end_date, 'sort_order': 'asc', 'start': start_idx}
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            if 'history' not in data or 'data' not in data['history']: break
            rows = data['history']['data']
            if columns is None: columns = data['history']['columns']
            if len(rows) == 0: break
            all_rows.extend(rows)
            start_idx += len(rows)
        except:
            return None

    if not all_rows: return None
    
    df = pd.DataFrame(all_rows, columns=columns)
    df = df[['TRADEDATE', 'CLOSE']].copy()
    df.columns = ['Date', 'Close']
    df['Date'] = pd.to_datetime(df['Date'])
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    return df.drop_duplicates(subset=['Date']).dropna().sort_values('Date').reset_index(drop=True)

# ГЛАВНАЯ ФУНКЦИЯ ИНТЕГРАЦИИ
def load_all_tickers() -> Tuple[pd.DataFrame, List[str]]:
    """
    Основная функция для вызова из engine.py.
    Загружает данные по всем тикерам, синхронизирует даты и возвращает priced_df.
    """
    if FORCE_RELOAD and CACHE_DIR.exists():
        shutil.rmtree(CACHE_DIR)
    CACHE_DIR.mkdir(exist_ok=True)

    all_data = {}
    for ticker in TICKERS:
        df = load_from_cache(ticker)
        if df is None:
            df = fetch_from_moex_complete(ticker, START_DATE, END_DATE)
            if df is not None:
                save_to_cache(ticker, df)
        
        if df is not None:
            all_data[ticker] = df

    if not all_data:
        raise ValueError("Никакие данные не были загружены с MOEX!")

    # Синхронизация дат (пересечение всех доступных дат)
    valid_tickers = list(all_data.keys())
    all_dates = set(all_data[valid_tickers[0]]['Date'])
    for ticker in valid_tickers[1:]:
        all_dates = all_dates.intersection(set(all_data[ticker]['Date']))

    # Сборка финального DataFrame
    priced_df = None
    for ticker in valid_tickers:
        df_ticker = all_data[ticker]
        df_ticker = df_ticker[df_ticker['Date'].isin(all_dates)].sort_values('Date')
        
        temp = df_ticker[['Date', 'Close']].copy()
        temp.columns = ['Date', ticker]
        
        if priced_df is None:
            priced_df = temp
        else:
            priced_df = priced_df.merge(temp, on='Date', how='inner')

    priced_df = priced_df.set_index('Date').sort_index()
    asset_names = list(priced_df.columns)
    
    return priced_df, asset_names