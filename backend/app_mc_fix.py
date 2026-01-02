# Добавить в конец app.py

import json
from fastapi.responses import JSONResponse

class MonteCarloRequest(BaseModel):
    mu: List[float]
    sigma: List[List[float]]
    weights: List[float]
    X_0: float
    T: float
    n_paths: int = 5000

@app.post("/api/monte-carlo")
async def monte_carlo_endpoint(request: MonteCarloRequest):
    try:
        from quantitative_engine.block_7_montecarlo import simulate_montecarlo
        
        mu = np.array(request.mu)
        sigma = np.array(request.sigma)
        weights = np.array(request.weights)
        
        print(f"📊 Inputs: mu={mu}, sigma_shape={sigma.shape}, weights={weights}")
        
        X_paths, t_grid, asset_dict = simulate_montecarlo(
            mu=mu, sigma=sigma, weights=weights, 
            X_0=request.X_0, T=request.T, n_paths=request.n_paths
        )
        
        final_vals = X_paths[:, -1]
        
        # Санитизация
        mean_val = float(np.nanmean(final_vals))
        std_val = float(np.nanstd(final_vals))
        var95 = float(np.nanpercentile(final_vals, 5))
        var99 = float(np.nanpercentile(final_vals, 1))
        max_dd = float((1 - X_paths.min(axis=1) / request.X_0).max())
        
        # Проверка на inf/nan
        assert np.isfinite(mean_val), f"mean is inf: {mean_val}"
        assert np.isfinite(std_val), f"std is inf: {std_val}"
        
        result = {
            "status": "success",
            "stats": {
                "mean": mean_val,
                "std": std_val,
                "var_95": var95,
                "var_99": var99,
                "max_drawdown": max_dd,
                "paths_shape": list(X_paths.shape)
            }
        }
        
        print(f"✅ Result: {result}")
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"MC error: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=400
        )

