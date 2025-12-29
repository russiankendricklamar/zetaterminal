# -*- coding: utf-8 -*-

import numpy as np
from scipy.stats import norm as scipy_norm
from typing import Dict, List, Optional

def analyze_results(X_paths: np.ndarray, t_grid: np.ndarray, X_0: float,
                   rf: float, asset_names: List[str], 
                   asset_paths: Optional[Dict] = None) -> Dict:
    """
    БЛОК 8: Анализ результатов симуляции.
    Поддерживает анализ портфеля и отдельных активов.
    
    Args:
        X_paths: массив траекторий портфеля (n_paths, n_times)
        t_grid: временная сетка
        X_0: начальный капитал
        rf: безрисковая ставка (%)
        asset_names: список названий активов (например, ['GAZP', 'SBER', 'LKOH'])
        asset_paths: словарь с траекториями активов {'GAZP': (n_paths, n_times), ...}
    """
    
    final_capitals = X_paths[:, -1]
    T_years = t_grid[-1] - t_grid[0]
    n_paths = len(X_paths)
    rf_decimal = rf / 100.0 if rf > 1.0 else rf
    
    # ============ ОСНОВНЫЕ МЕТРИКИ ПОРТФЕЛЯ ============
    mean_final = np.mean(final_capitals)
    median_final = np.median(final_capitals)
    std_final = np.std(final_capitals, ddof=1)
    
    # VaR и CVaR
    def calc_risk_metrics(capitals, level):
        alpha = 1 - level
        var_capital = np.quantile(capitals, alpha)
        loss_var_abs = X_0 - var_capital
        
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
    
    # Доходность и волатильность
    path_returns = (final_capitals / X_0) ** (1 / T_years) - 1
    mean_return = np.mean(path_returns)
    std_return = np.std(path_returns, ddof=1)
    
    # Sharpe Ratio
    sharpe = (mean_return - rf_decimal) / std_return if std_return > 1e-6 else 0.0
    
    # Maximum Drawdown
    def get_mdd(path):
        running_max = np.maximum.accumulate(path)
        drawdowns = (running_max - path) / running_max
        return np.max(drawdowns)
    
    sample_mdd_idx = np.random.choice(n_paths, min(500, n_paths), replace=False)
    mdds = [get_mdd(X_paths[i]) for i in sample_mdd_idx]
    mean_mdd = np.mean(mdds)
    
    # Потери
    returns_pct = path_returns * 100
    losses = returns_pct[returns_pct < 0]
    avg_loss = float(np.mean(losses)) if len(losses) > 0 else 0.0
    max_loss = float(np.min(returns_pct))
    std_loss = float(np.std(losses)) if len(losses) > 0 else 0.0
    
    # ============ ФУНКЦИЯ ДЛЯ РАСЧЕТА РАСПРЕДЕЛЕНИЯ ============
    def calc_asset_distribution(asset_data, asset_name):
        """
        Расчет гистограммы и статистики для актива.
        asset_data: массив итоговых стоимостей (n_paths,)
        """
        asset_returns = (asset_data / X_0) ** (1 / T_years) - 1
        
        mean_asset = np.mean(asset_returns)
        std_asset = np.std(asset_returns)
        
        # Гистограмма
        n_bins = 30
        hist, bin_edges = np.histogram(asset_returns, bins=n_bins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Нормальная кривая
        x_normal = np.linspace(asset_returns.min(), asset_returns.max(), 100)
        y_normal = scipy_norm.pdf(x_normal, mean_asset, std_asset) * len(asset_returns) * (bin_edges[1] - bin_edges[0])
        
        # Квантили и моменты
        q_05 = np.quantile(asset_returns, 0.05)
        q_95 = np.quantile(asset_returns, 0.95)
        
        skewness = np.mean((asset_returns - mean_asset)**3) / std_asset**3 if std_asset > 0 else 0
        kurtosis = np.mean((asset_returns - mean_asset)**4) / std_asset**4 - 3 if std_asset > 0 else 0
        
        return {
            'histogram': {
                'bin_centers': bin_centers.tolist(),
                'bin_heights': hist.tolist(),
                'bin_width': float(bin_edges[1] - bin_edges[0])
            },
            'normal_curve': {
                'x': x_normal.tolist(),
                'y': y_normal.tolist()
            },
            'statistics': {
                'mean': float(mean_asset),
                'std': float(std_asset),
                'q_05': float(q_05),
                'q_95': float(q_95),
                'skewness': float(skewness),
                'kurtosis': float(kurtosis)
            }
        }
    
    # ============ РАСЧЕТ РАСПРЕДЕЛЕНИЙ ДЛЯ ПОРТФЕЛЯ И АКТИВОВ ============
    asset_distributions = {}
    
    # ПОРТФЕЛЬ
    asset_distributions['ПОРТФЕЛЬ'] = calc_asset_distribution(final_capitals, 'ПОРТФЕЛЬ')
    
    # ОТДЕЛЬНЫЕ АКТИВЫ
    if asset_paths is not None:
        for asset_name in asset_names:
            if asset_name in asset_paths:
                asset_final = asset_paths[asset_name][:, -1]
                asset_distributions[asset_name] = calc_asset_distribution(asset_final, asset_name)
    
    # ============ ВРЕМЕННЫЕ РЯДЫ ДЛЯ ГРАФИКОВ ============
    step = max(1, len(t_grid) // 50)
    
    # Траектории активов для frontend
    trajectories_data = {
        'ПОРТФЕЛЬ': {
            'mean': np.mean(X_paths, axis=0)[::step].tolist(),
            'q25': np.quantile(X_paths, 0.25, axis=0)[::step].tolist(),
            'q75': np.quantile(X_paths, 0.75, axis=0)[::step].tolist(),
            'q05': np.quantile(X_paths, 0.05, axis=0)[::step].tolist(),
            'q95': np.quantile(X_paths, 0.95, axis=0)[::step].tolist(),
        }
    }
    
    # Траектории отдельных активов
    if asset_paths is not None:
        for asset_name in asset_names:
            if asset_name in asset_paths:
                asset_data = asset_paths[asset_name]
                trajectories_data[asset_name] = {
                    'mean': np.mean(asset_data, axis=0)[::step].tolist(),
                    'q25': np.quantile(asset_data, 0.25, axis=0)[::step].tolist(),
                    'q75': np.quantile(asset_data, 0.75, axis=0)[::step].tolist(),
                    'q05': np.quantile(asset_data, 0.05, axis=0)[::step].tolist(),
                    'q95': np.quantile(asset_data, 0.95, axis=0)[::step].tolist(),
                }
    
    return {
        'mean_final_capital': float(mean_final),
        'median_final_capital': float(median_final),
        'sharpe_ratio': float(sharpe),
        'mean_return': float(mean_return),
        'volatility': float(std_return),
        'max_drawdown': float(mean_mdd),
        'mean_loss': avg_loss,
        'max_loss': max_loss,
        'std_loss': std_loss,
        'var_metrics': {
            **risk_95, 
            **risk_99, 
            'avg_loss': avg_loss, 
            'max_loss': max_loss, 
            'std_loss': std_loss
        },
        'asset_distributions': asset_distributions,  # ✅ Гистограммы для всех активов
        'trajectories': trajectories_data,             # ✅ Траектории для всех активов
        'chart_data': {
            'timestamps': t_grid[::step].tolist(),
            'capital_mean': np.mean(X_paths, axis=0)[::step].tolist(),
            'capital_q25': np.quantile(X_paths, 0.25, axis=0)[::step].tolist(),
            'capital_q75': np.quantile(X_paths, 0.75, axis=0)[::step].tolist(),
        },
        'status': 'success'
    }