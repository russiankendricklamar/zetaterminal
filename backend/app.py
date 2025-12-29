import numpy as np
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from models import CalculationRequest, BacktestRequest, CalculationResponse, VaRMetrics, StressScenarioResult, ChartData, BacktestResponse
from core.engine import QuantitativeRiskEngine
import logging

# Инициализация
app = FastAPI(
    title="Quantitative Risk Engine API",
    description="Портфельная оптимизация на основе HJB",
    version="1.0.0"
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

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Risk Engine is running"}

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

            mean_loss=validated_var_metrics.avg_loss, # Синхронизируем корень и VaR-блок
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
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
