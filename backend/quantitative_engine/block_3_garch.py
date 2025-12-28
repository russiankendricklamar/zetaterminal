# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from arch import arch_model
from typing import Dict, Tuple, List
import warnings

warnings.filterwarnings('ignore')

def estimate_garch(returns: pd.DataFrame) -> Tuple[Dict[str, float], Dict]:
    """
    БЛОК 3: GARCH(1,1) моделирование волатильности.
    Принимает очищенные доходности.
    Возвращает: (vols_final, full_results)
    """
    
    ANNUALIZATION_FACTOR = np.sqrt(252)
    MIN_OBS = 100
    PERSISTENCE_THRESHOLD = 0.995
    ALPHA_MIN_THRESHOLD = 1e-8
    
    # Расчитываем sample vol для fallback (нужен для сравнения и если GARCH упадет)
    sample_vols_annual = returns.std() * ANNUALIZATION_FACTOR

    garch_params = {}
    long_run_vols = {}
    conditional_vols = {}
    failed_tickers = []
    volatilities_final = {}
    garch_usage = {}

    for ticker in returns.columns:
        try:
            r = returns[ticker].dropna()

            # Проверка на минимальное кол-во данных
            if len(r) < MIN_OBS:
                raise ValueError("Недостаточно данных")

            # Инициализация и подгонка модели
            model = arch_model(r, vol='Garch', p=1, q=1, rescale=False)
            fitted = model.fit(disp='off', show_warning=False)

            # Проверка сходимости
            if fitted.convergence_flag != 0:
                raise ValueError(f"Не сошлась оптимизация (флаг {fitted.convergence_flag})")

            # Извлечение параметров
            omega = fitted.params['omega']
            alpha = fitted.params['alpha[1]']
            beta = fitted.params['beta[1]']
            persistence = alpha + beta

            # Проверка адекватности параметров
            if omega <= 0 or alpha < -1e-10 or beta < -1e-10:
                raise ValueError("Некорректные параметры (отрицательные значения)")
            
            if alpha < ALPHA_MIN_THRESHOLD:
                raise ValueError("Альфа практически нулевая")
            
            if persistence >= PERSISTENCE_THRESHOLD:
                raise ValueError("Нестационарность (устойчивость >= 0.995)")

            # Если все проверки пройдены — считаем волатильность GARCH
            long_run_vol = np.sqrt(omega / (1 - persistence)) * ANNUALIZATION_FACTOR
            
            long_run_vols[ticker] = long_run_vol
            conditional_vols[ticker] = fitted.conditional_volatility.mean() * ANNUALIZATION_FACTOR
            garch_params[ticker] = {'omega': omega, 'alpha': alpha, 'beta': beta, 'persistence': persistence}
            
            volatilities_final[ticker] = long_run_vol
            garch_usage[ticker] = "GARCH"

        except Exception:
            # Fallback на простую историческую волатильность
            failed_tickers.append(ticker)
            long_run_vols[ticker] = np.nan
            volatilities_final[ticker] = sample_vols_annual[ticker]
            garch_usage[ticker] = "Sample"

    # Формируем итоговый объект с результатами для аналитики
    garch_results = {
        'params': pd.DataFrame(garch_params).T if garch_params else pd.DataFrame(),
        'volatilities_final': pd.Series(volatilities_final),
        'garch_usage': garch_usage,
        'failed_tickers': failed_tickers
    }

    # Возвращаем словарь финальных волатильностей и полный отчет
    return volatilities_final, garch_results