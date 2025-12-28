# -*- coding: utf-8 -*-
import numpy as np
from typing import Dict, List

def analyze_results(X_paths: np.ndarray, t_grid: np.ndarray, X_0: float, 
                    rf: float, asset_names: List[str]) -> Dict:
    """
    БЛОК 8: Анализ результатов симуляции.
    Рассчитывает доходность, риск-метрики (VaR, CVaR), просадки и Sharpe Ratio.
    """
    
    final_capitals = X_paths[:, -1]
    T_years = t_grid[-1] - t_grid[0]
    n_paths = len(X_paths)

    rf_decimal = rf / 100.0 if rf > 1.0 else rf

    # 1. Базовая статистика финального капитала
    mean_final = np.mean(final_capitals)
    median_final = np.median(final_capitals)
    std_final = np.std(final_capitals, ddof=1)

    # 2. Расчет VaR и CVaR (95% и 99%)
    def calc_risk_metrics(capitals, level):
        alpha = 1 - level
        var_capital = np.quantile(capitals, alpha)
        loss_var_abs = X_0 - var_capital
        
        # CVaR (среднее значение в хвосте ниже VaR)
        tail_capitals = capitals[capitals <= var_capital]
        if len(tail_capitals) > 0:
            cvar_capital = np.mean(tail_capitals)
            loss_cvar_abs = X_0 - cvar_capital
        else:
            loss_cvar_abs = loss_var_abs
            
        return {
            f'capital_{int(level*100)}': float(var_capital),
            f'loss_pct_{int(level*100)}': float((loss_var_abs / X_0) * 100),
            f'cvar_pct_{int(level*100)}': float((loss_cvar_abs / X_0) * 100)
        }

    risk_95 = calc_risk_metrics(final_capitals, 0.95)
    risk_99 = calc_risk_metrics(final_capitals, 0.99)

    # 3. Доходность и волатильность (аннуализированная)
    # Используем формулу среднего геометрического для каждого пути
    path_returns = (final_capitals / X_0) ** (1 / T_years) - 1
    mean_return = np.mean(path_returns)
    std_return = np.std(path_returns, ddof=1)

    # 4. Sharpe Ratio
    sharpe = (mean_return - rf_decimal) / std_return if std_return > 1e-6 else 0.0

    # 5. Maximum Drawdown (средний по путям)
    def get_mdd(path):
        running_max = np.maximum.accumulate(path)
        drawdowns = (running_max - path) / running_max
        return np.max(drawdowns)

    # Для скорости считаем MDD на подвыборке путей (например, 500)
    sample_mdd_idx = np.random.choice(n_paths, min(500, n_paths), replace=False)
    mdds = [get_mdd(X_paths[i]) for i in sample_mdd_idx]
    mean_mdd = np.mean(mdds)

    # 6. Временные ряды для графиков (усредненные)
    # Сжимаем данные для передачи по сети (каждый 5-й шаг)
    step = max(1, len(t_grid) // 50)
    
    return {
        'mean_final_capital': float(mean_final),
        'median_final_capital': float(median_final),
        'sharpe_ratio': float(sharpe),
        'mean_return': float(mean_return * 100),
        'volatility': float(std_return * 100),
        'max_drawdown': float(mean_mdd * 100),
        
        'var_metrics': {**risk_95, **risk_99},
        
        # Данные для отрисовки графиков на фронтенде
        'chart_data': {
            'timestamps': t_grid[::step].tolist(),
            'capital_mean': np.mean(X_paths, axis=0)[::step].tolist(),
            'capital_q25': np.quantile(X_paths, 0.25, axis=0)[::step].tolist(),
            'capital_q75': np.quantile(X_paths, 0.75, axis=0)[::step].tolist(),
        },
        
        'status': 'success'
    }