# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List

def filter_portfolio(returns: pd.DataFrame, cov_matrix: pd.DataFrame, vols: Dict[str, float]) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    БЛОК 4: Фильтрация портфеля.
    Исключает активы с высокой волатильностью, малым числом данных и мультиколлинеарностью.
    
    Returns:
        Tuple[returns_filtered, cov_filtered, assets_filtered]
    """
    
    # Константы фильтрации (соответствуют вашему ноутбуку)
    MIN_OBSERVATIONS = 100
    MAX_VOLATILITY = 0.50
    MAX_CORRELATION = 0.98
    MIN_PORTFOLIO_SIZE = 3

    initial_assets = returns.columns.tolist()
    asset_to_keep = []
    
    # 1. Фильтрация по волатильности и кол-ву данных
    for ticker in initial_assets:
        n_obs = len(returns[ticker].dropna())
        raw_vol = vols.get(ticker, 9.99)
        vol = raw_vol / 100.0 if raw_vol > 1.0 else raw_vol
        
        if n_obs >= MIN_OBSERVATIONS and vol <= MAX_VOLATILITY:
            asset_to_keep.append(ticker)
        else:
            # Логируем (в терминал бэкенда), почему удалили
            reason = "мало данных" if n_obs < MIN_OBSERVATIONS else f"высокая волатильность ({vol:.2f}%)"
            print(f"   ✗ {ticker} исключен: {reason}")

    # 2. Удаление дубликатов по корреляции
    if len(asset_to_keep) >= 2:
        corr_matrix = returns[asset_to_keep].corr()
        to_remove = set()
        
        for i in range(len(asset_to_keep)):
            for j in range(i + 1, len(asset_to_keep)):
                t1, t2 = asset_to_keep[i], asset_to_keep[j]
                if t1 in to_remove or t2 in to_remove:
                    continue
                    
                if abs(corr_matrix.loc[t1, t2]) > MAX_CORRELATION:
                    # Удаляем тот, у которого волатильность выше (более рискованный)
                    v1, v2 = vols.get(t1, 0), vols.get(t2, 0)
                    removed = t1 if v1 > v2 else t2
                    to_remove.add(removed)
                    print(f"   ✗ {removed} исключен: высокая корреляция с {t2 if removed==t1 else t1}")

        asset_to_keep = [a for a in asset_to_keep if a not in to_remove]

    # 3. Проверка на минимальный размер портфеля
    if len(asset_to_keep) < MIN_PORTFOLIO_SIZE:
        raise ValueError(f"После фильтрации осталось слишком мало активов ({len(asset_to_keep)}). "
                         f"Минимум нужно {MIN_PORTFOLIO_SIZE}. Проверьте критерии фильтрации.")

    # Создаем отфильтрованные объекты
    returns_filtered = returns[asset_to_keep].copy()
    cov_filtered = cov_matrix.loc[asset_to_keep, asset_to_keep].copy()
    
    return returns_filtered, cov_filtered, asset_to_keep