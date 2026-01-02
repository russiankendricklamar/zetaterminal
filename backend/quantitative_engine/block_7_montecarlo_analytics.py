# -*- coding: utf-8 -*-

import numpy as np
from typing import Dict, Tuple

def extract_quantile_paths(X_paths: np.ndarray, quantiles: list = [0.05, 0.25, 0.5, 0.75, 0.95]) -> Dict:
    """
    Вычисляет квантильные траектории для визуализации confidence intervals
    
    Input: X_paths shape (n_paths, n_steps)
    Output: Dict с траекториями по квантилям
    """
    result = {}
    for q in quantiles:
        result[f"q_{int(q*100)}"] = np.quantile(X_paths, q, axis=0).tolist()
    
    return result

def compute_full_statistics(X_paths: np.ndarray, X_0: float) -> Dict:
    """
    Комплексная статистика для risk reporting
    """
    final_vals = X_paths[:, -1]
    
    return {
        "mean": float(np.nanmean(final_vals)),
        "median": float(np.nanmedian(final_vals)),
        "std": float(np.nanstd(final_vals)),
        "skew": float(np.nanmean(((final_vals - np.nanmean(final_vals)) / np.nanstd(final_vals))**3)),
        "kurtosis": float(np.nanmean(((final_vals - np.nanmean(final_vals)) / np.nanstd(final_vals))**4) - 3),
        "var_95": float(np.nanpercentile(final_vals, 5)),
        "var_99": float(np.nanpercentile(final_vals, 1)),
        "cvar_95": float(final_vals[final_vals <= np.percentile(final_vals, 5)].mean()),
        "max": float(final_vals.max()),
        "min": float(final_vals.min()),
        "max_drawdown": float((1 - X_paths.min(axis=1) / X_0).max()),
    }
