# -*- coding: utf-8 -*-

import numpy as np
from typing import List, Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .block_7_montecarlo import simulate_montecarlo
from .block_7_montecarlo_analytics import compute_full_statistics, extract_quantile_paths

async def batch_monte_carlo(
    scenarios: List[Dict],
    n_paths: int = 5000,
    executor: ThreadPoolExecutor = None
) -> List[Dict]:
    """
    Запустить MC для нескольких портфелей параллельно
    
    Input:
        scenarios: [
            {"mu": [...], "sigma": [...], "weights": [...], "X_0": ..., "T": ...},
            ...
        ]
    """
    
    if executor is None:
        executor = ThreadPoolExecutor(max_workers=4)
    
    tasks = []
    
    for i, scenario in enumerate(scenarios):
        def run_scenario(sc=scenario, idx=i):
            try:
                mu = np.array(sc['mu'])
                sigma = np.array(sc['sigma'])
                weights = np.array(sc['weights'])
                X_0 = sc['X_0']
                T = sc['T']
                
                X_paths, t_grid, _ = simulate_montecarlo(
                    mu=mu, sigma=sigma, weights=weights,
                    X_0=X_0, T=T, n_paths=n_paths
                )
                
                stats = compute_full_statistics(X_paths, X_0)
                quantiles = extract_quantile_paths(X_paths)
                
                return {
                    "scenario_id": idx,
                    "status": "success",
                    "stats": stats,
                    "paths": {
                        "time_grid": (t_grid * 252).tolist(),
                        "quantiles": quantiles
                    }
                }
            except Exception as e:
                return {
                    "scenario_id": idx,
                    "status": "error",
                    "message": str(e)
                }
        
        tasks.append(run_scenario())
    
    # Запускаем параллельно
    loop = asyncio.get_event_loop()
    results = await asyncio.gather(
        *[loop.run_in_executor(executor, lambda t=t: t) for t in tasks]
    )
    
    return results

