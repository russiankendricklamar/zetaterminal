# -*- coding: utf-8 -*-

import numpy as np
from typing import Dict, List

from .block_7_montecarlo import simulate_montecarlo
from .block_7_montecarlo_analytics import compute_full_statistics

def stress_test_scenarios(
    mu: np.ndarray,
    sigma: np.ndarray,
    weights: np.ndarray,
    X_0: float,
    T: float,
    n_paths: int = 5000
) -> Dict[str, Dict]:
    """
    Запустить несколько стресс-сценариев:
    1. Volatility shock (+50%)
    2. Correlation shock (все к 0.9)
    3. Drift shock (-50%)
    4. Combined shock
    """
    
    base_result = simulate_montecarlo(mu, sigma, weights, X_0, T, n_paths)
    base_stats = compute_full_statistics(base_result[0], X_0)
    
    results = {
        "baseline": {
            "stats": base_stats,
            "description": "No shock"
        }
    }
    
    # ============ STRESS 1: Volatility +50% ============
    sigma_shocked = sigma * 1.5
    X_paths, _, _ = simulate_montecarlo(mu, sigma_shocked, weights, X_0, T, n_paths)
    results["vol_shock_50pct"] = {
        "stats": compute_full_statistics(X_paths, X_0),
        "description": "Volatility +50%"
    }
    
    # ============ STRESS 2: Correlation shock (0.9) ============
    sigma_corr = sigma.copy()
    for i in range(len(sigma)):
        for j in range(len(sigma)):
            if i != j:
                sigma_corr[i, j] = 0.9 * np.sqrt(sigma[i, i] * sigma[j, j])
    
    X_paths, _, _ = simulate_montecarlo(mu, sigma_corr, weights, X_0, T, n_paths)
    results["corr_shock_09"] = {
        "stats": compute_full_statistics(X_paths, X_0),
        "description": "Correlation → 0.9"
    }
    
    # ============ STRESS 3: Drift shock (-50%) ============
    mu_shocked = mu * 0.5
    X_paths, _, _ = simulate_montecarlo(mu_shocked, sigma, weights, X_0, T, n_paths)
    results["drift_shock_50pct"] = {
        "stats": compute_full_statistics(X_paths, X_0),
        "description": "Drift -50%"
    }
    
    # ============ STRESS 4: Combined ============
    X_paths, _, _ = simulate_montecarlo(mu * 0.5, sigma * 1.5, weights, X_0, T, n_paths)
    results["combined_shock"] = {
        "stats": compute_full_statistics(X_paths, X_0),
        "description": "Vol +50%, Drift -50%"
    }
    
    return results

