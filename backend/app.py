import numpy as np
import logging
import asyncio
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List, Dict
from fastapi.responses import JSONResponse

from fastapi import FastAPI, HTTPException, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware

from models import (
    CalculationRequest, BacktestRequest, CalculationResponse, 
    VaRMetrics, StressScenarioResult, ChartData, BacktestResponse
)
from core.engine import QuantitativeRiskEngine

# Инициализация
app = FastAPI(
    title="Quantitative Risk Engine API",
    description="Портфельная оптимизация на основе HJB + Dashboard",
    version="2.0.0"
)

# CORS для связи с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

# ============================================================================
# Существующие эндпоинты (твой функционал)
# ============================================================================

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Risk Engine is running"}

class MonteCarloRequest(BaseModel):
    mu: List[float]
    sigma: List[List[float]]
    weights: List[float]
    X_0: float
    T: float
    n_paths: int = 5000


class BatchMonteCarloRequest(BaseModel):
    scenarios: List[Dict]
    n_paths: int = 5000



@app.post("/api/calculate", response_model=CalculationResponse)
async def calculate_portfolio(request: CalculationRequest):
    try:
        engine = QuantitativeRiskEngine(
            gamma=request.gamma,
            initial_capital=request.initial_capital,
            n_paths=request.n_paths,
            time_horizon=request.time_horizon
        )

        result = engine.run(run_stress=request.run_stress_test)

        if result.get('status') == 'error':
            logger.error(f"Engine execution failed: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get('error'))

        if 'metrics' not in result:
            logger.error("Engine returned success but 'metrics' key is missing")
            raise HTTPException(status_code=500, detail="Internal calculation error: metrics missing")

        metrics = result['metrics']
        vm_data = result['metrics']['var_metrics']

        validated_var_metrics = VaRMetrics(
            capital_95=float(vm_data.get('capital_95', 0)),
            loss_pct_95=float(vm_data.get('loss_pct_95', 0)),
            cvar_pct_95=float(vm_data.get('cvar_pct_95', 0)),
            capital_99=float(vm_data.get('capital_99', 0)),
            loss_pct_99=float(vm_data.get('loss_pct_99', 0)),
            cvar_pct_99=float(vm_data.get('cvar_pct_99', 0)),
            avg_loss=float(vm_data.get('avg_loss', 0)),
            max_loss=float(vm_data.get('max_loss', 0)),
            std_loss=float(vm_data.get('std_loss', 0))
        )

        asset_distributions = metrics.get('asset_distributions', {})

        print("📊 VaR METRICS:", validated_var_metrics)
        print("📊 STRESS TESTS:", result.get('stress_tests'))

        # Преобразуем результаты в ответ
        return CalculationResponse(
            status="success",
            mean_final_capital=float(metrics.get('mean_final_capital', 0)),
            median_final_capital=float(metrics.get('median_final_capital', 0)),
            sharpe_ratio=float(metrics.get('sharpe_ratio', 0)),
            mean_return=float(metrics.get('mean_return', 0)),
            volatility=float(metrics.get('volatility', 0)),
            max_drawdown=float(metrics.get('max_drawdown', 0)),
            mean_loss=validated_var_metrics.avg_loss,
            max_loss=validated_var_metrics.max_loss,
            std_loss=validated_var_metrics.std_loss,
            var_metrics=validated_var_metrics,
            chart_data=ChartData(**metrics.get('chart_data', {})),
            stress_tests=result.get('stress_tests'),
            asset_distributions=asset_distributions
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error in calculate_portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backtest", response_model=BacktestResponse)
async def run_portfolio_backtest(request: BacktestRequest):
    try:
        from quantitative_engine.backtest import Backtester

        n = len(request.tickers)
        test_weights = np.array([1/n] * n)

        results = Backtester.run_backtest(
            tickers=request.tickers,
            weights=test_weights,
            start=request.start_date,
            end=request.end_date,
            initial_capital=request.initial_capital,
            forecast_var_pct=5.0
        )

        return {
            "total_return": results["total_return"],
            "max_drawdown": results["max_drawdown"],
            "var_breaches": results["var_breaches"],
            "history": results["history"]
        }

    except Exception as e:
        logger.error(f"Backtest error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# НОВЫЕ эндпоинты для Dashboard (совместимо с фронтендом)
# ============================================================================

@app.get("/api/kpis")
async def get_kpis():
    """Получить KPI метрики портфеля"""
    return {
        "total_pnl": 125400.0,
        "var_95": -45200.0,
        "expected_shortfall": -58100.0,
        "sharpe_ratio": 1.45,
        "max_drawdown": -0.124,
        "ytd_return": 0.082
    }

@app.get("/api/price-series")
async def get_price_series(asset: str = Query("SPY"), days: int = Query(60)):
    """Получить OHLCV данные для графика"""
    def simulate_levy_process(s0, mu, sigma, alpha, t, steps):
        """Упрощённая симуляция процесса Леви"""
        dt = t / steps
        shocks = np.random.standard_cauchy(steps) * sigma * np.sqrt(dt)
        returns = (mu - 0.5 * sigma**2) * dt + shocks
        price_path = s0 * np.exp(np.cumsum(returns))
        return price_path

    now = datetime.now()
    dates = [(now - timedelta(days=i)).isoformat() for i in range(days)][::-1]
    
    s0 = 450.0
    prices = simulate_levy_process(s0, 0.05, 0.2, 1.5, days/252, days)
    
    series = []
    for i, date in enumerate(dates):
        p = float(prices[i])
        series.append({
            "date": date,
            "open": p * 0.99,
            "high": p * 1.01,
            "low": p * 0.98,
            "close": p,
            "volume": int(np.random.randint(1000000, 5000000))
        })
    
    return {"asset": asset, "series": series}

@app.get("/api/greeks")
async def get_greeks():
    """Получить Greeks для позиций"""
    return [
        {
            "position": "SPY Mar24 460C",
            "delta": 0.52,
            "gamma": 0.012,
            "vega": 0.45,
            "theta": -0.15,
            "rho": 0.02
        },
        {
            "position": "TLT Jun24 95P",
            "delta": -0.31,
            "gamma": 0.008,
            "vega": 0.22,
            "theta": -0.08,
            "rho": -0.01
        },
    ]

@app.get("/api/heatmap")
async def get_heatmap():
    """Получить данные для Bubble Chart (volatility vs correlation)"""
    return [
        {
            "asset": "SPY",
            "volatility": 0.18,
            "correlation": 1.0,
            "notional": 500000,
            "pnl": 12500,
            "pnl_pct": 0.025
        },
        {
            "asset": "TLT",
            "volatility": 0.12,
            "correlation": -0.35,
            "notional": 300000,
            "pnl": 8900,
            "pnl_pct": 0.029
        },
        {
            "asset": "GLD",
            "volatility": 0.15,
            "correlation": 0.12,
            "notional": 200000,
            "pnl": -3200,
            "pnl_pct": -0.016
        },
        {
            "asset": "BTC",
            "volatility": 0.55,
            "correlation": 0.45,
            "notional": 50000,
            "pnl": 4500,
            "pnl_pct": 0.09
        },
    ]

@app.get("/api/stress-testing")
async def get_stress_testing():
    """Получить результаты stress-testing сценариев"""
    return [
        {
            "scenario": "Black Monday 2.0",
            "description": "Equity -20%, Vol +100%",
            "pnl_impact": -250000,
            "var_change": 150000,
            "probability": 0.001
        },
        {
            "scenario": "Rates Spike",
            "description": "10Y Yield +100bps",
            "pnl_impact": -45000,
            "var_change": 12000,
            "probability": 0.02
        },
    ]

@app.get("/api/model-diagnostics")
async def get_diagnostics():
    """Получить диагностику модели (KS test, backtesting accuracy)"""
    return {
        "model_name": "Lévy Alpha-Stable",
        "ks_test_pvalue": 0.042,
        "backtesting_accuracy": 0.985,
        "parameters": {
            "alpha": 1.7,
            "beta": 0.1,
            "gamma": 1.2,
            "delta": 0.05
        }
    }

@app.get("/api/backtest-results")
async def get_backtest_results(
    start_date: str = Query("2024-01-01"),
    end_date: str = Query("2024-12-31")
):
    """Получить результаты backtesting"""
    return {
        "period": f"{start_date} to {end_date}",
        "cumulative_return": 0.125,
        "annual_return": 0.125,
        "volatility": 0.086,
        "sharpe_ratio": 1.45,
        "max_drawdown": -0.183,
        "win_rate": 0.583,
        "profit_factor": 1.78
    }

# ============================================================================
# WebSockets для Real-time обновлений
# ============================================================================

@app.websocket("/ws/live-data")
async def websocket_live_data(websocket: WebSocket):
    """WebSocket для стриминга live KPI и Greeks"""
    await websocket.accept()
    try:
        while True:
            data = {
                "timestamp": datetime.now().isoformat(),
                "total_pnl": 125400.0 + np.random.normal(0, 100),
                "var_95": -45200.0 + np.random.normal(0, 50),
                "sharpe_ratio": 1.45 + np.random.normal(0, 0.05)
            }
            await websocket.send_json(data)
            await asyncio.sleep(2)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.websocket("/ws/model-stream")
async def websocket_model_stream(websocket: WebSocket):
    """WebSocket для стриминга обновлений модели"""
    await websocket.accept()
    try:
        while True:
            data = {
                "timestamp": datetime.now().isoformat(),
                "model_name": "Lévy Alpha-Stable",
                "ks_test_pvalue": 0.042 + np.random.normal(0, 0.005),
                "backtesting_accuracy": 0.985 + np.random.normal(0, 0.01)
            }
            await websocket.send_json(data)
            await asyncio.sleep(3)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# ============================================================================
# Startup / Shutdown
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

# ============ MONTE CARLO ENDPOINT ============

# ============================================================================
# MONTE CARLO ENDPOINT (SINGLE, CLEAN VERSION)
# ============================================================================

from typing import List
from pydantic import BaseModel
from fastapi.responses import JSONResponse

@app.post("/api/monte-carlo")
async def monte_carlo_endpoint(request: MonteCarloRequest):
    """Monte Carlo с путями для визуализации"""
    try:
        from quantitative_engine.block_7_montecarlo import simulate_montecarlo
        from quantitative_engine.block_7_montecarlo_analytics import extract_quantile_paths, compute_full_statistics
        
        mu = np.array(request.mu)
        sigma = np.array(request.sigma)
        weights = np.array(request.weights)
        
        logger.info(f"MC: {request.n_paths} paths, T={request.T}")
        
        X_paths, t_grid, asset_dict = simulate_montecarlo(
            mu=mu, sigma=sigma, weights=weights, 
            X_0=request.X_0, T=request.T, n_paths=request.n_paths
        )
        
        # Compute stats
        stats = compute_full_statistics(X_paths, request.X_0)
        
        # Extract quantile paths for confidence intervals
        quantile_paths = extract_quantile_paths(X_paths)
        
        # Time grid
        time_grid = (t_grid * 252).tolist()  # Convert to days
        
        result = {
            "status": "success",
            "stats": stats,
            "paths": {
                "time_grid": time_grid,
                "quantiles": quantile_paths
            },
            "metadata": {
                "n_paths": request.n_paths,
                "n_steps": X_paths.shape[1],
                "T": request.T
            }
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"MC error: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=400
        )


# ============================================================================
# BATCH MONTE CARLO ENDPOINT
# ============================================================================

@app.post("/api/monte-carlo/batch")
async def batch_monte_carlo_endpoint(request: BatchMonteCarloRequest):
    """Batch MC симуляция для нескольких портфелей"""
    try:
        from quantitative_engine.block_7_montecarlo_batch import batch_monte_carlo
        
        logger.info(f"Batch MC: {len(request.scenarios)} scenarios, {request.n_paths} paths each")
        
        results = await batch_monte_carlo(request.scenarios, request.n_paths)
        
        return JSONResponse(content={
            "status": "success",
            "results": results,
            "metadata": {
                "n_scenarios": len(request.scenarios),
                "n_paths": request.n_paths
            }
        })
        
    except Exception as e:
        logger.error(f"Batch MC error: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=400
        )


# ============================================================================
# STRESS TEST ENDPOINT
# ============================================================================

class StressTestRequest(BaseModel):
    mu: List[float]
    sigma: List[List[float]]
    weights: List[float]
    X_0: float
    T: float
    n_paths: int = 5000

@app.post("/api/stress-test")
async def stress_test_endpoint(request: StressTestRequest):
    """Stress test scenarios"""
    try:
        from quantitative_engine.block_7_stress_tests import stress_test_scenarios
        
        mu = np.array(request.mu)
        sigma = np.array(request.sigma)
        weights = np.array(request.weights)
        
        logger.info(f"Stress tests for {len(request.mu)} assets")
        
        results = stress_test_scenarios(mu, sigma, weights, request.X_0, request.T, request.n_paths)
        
        return JSONResponse(content={
            "status": "success",
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Stress test error: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=400
        )

