# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple

def calculate_returns(priced_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    БЛОК 2: Расчёт доходностей, очистка от сплитов и анализ матриц.
    Возвращает: (returns, cov_matrix, correlation_matrix)
    """
    
    # 1. Расчёт сырых доходностей
    returns_raw = np.log(priced_df / priced_df.shift(1)).dropna()

    # 2. Детектор сплитов
    returns = returns_raw.copy()
    split_threshold = 0.70

    for ticker in returns.columns:
        extreme_days = np.abs(returns[ticker]) > split_threshold
        if extreme_days.any():
            # Заменяем сплиты на NaN, чтобы потом заполнить
            returns.loc[extreme_days, ticker] = np.nan

    # Заполняем пустоты после удаления сплитов и удаляем строки с NaN
    returns = returns.ffill().dropna()

    # 3. Настройка параметров аннуализации
    TRADING_DAYS = 252

    # 4. Ковариационная и корреляционная матрицы
    cov_matrix_daily = returns.cov()
    cov_matrix = cov_matrix_daily * TRADING_DAYS
    correlation_matrix = returns.corr()

    # 5. Регуляризация (Shrinkage), если матрица плохая
    eigenvalues = np.linalg.eigvalsh(cov_matrix.values)
    min_eig = eigenvalues.min()

    if min_eig <= 1e-10:
        try:
            from sklearn.covariance import LedoitWolf
            lw = LedoitWolf()
            cov_matrix_shrunk = lw.fit(returns.values).covariance_
            cov_matrix = pd.DataFrame(
                cov_matrix_shrunk * TRADING_DAYS, # Не забываем про аннуализацию
                index=cov_matrix.index,
                columns=cov_matrix.columns
            )
        except ImportError:
            # Базовая регуляризация (добавление малого числа на диагональ)
            cov_matrix = cov_matrix + np.eye(len(cov_matrix)) * abs(min_eig) * 1.1

    # ВАЖНО: Мы возвращаем результаты, чтобы engine.py мог передать их дальше
    return returns, cov_matrix, correlation_matrix