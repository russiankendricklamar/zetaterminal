from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from models import CalculationRequest, CalculationResponse, VaRMetrics, ChartData
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
    """Проверка здоровья API"""
    return {"status": "ok", "message": "Risk Engine is running"}

@app.post("/api/calculate", response_model=CalculationResponse)
async def calculate_portfolio(request: CalculationRequest):
    """
    Главный эндпоинт расчёта портфеля.
    Принимает параметры и возвращает полный анализ.
    """
    try:
        engine = QuantitativeRiskEngine(
            gamma=request.gamma,
            initial_capital=request.initial_capital,
            n_paths=request.n_paths,
            time_horizon=request.time_horizon
        )
        
        result = engine.run()

        if result.get('status') == 'error':
            logger.error(f"Engine execution failed: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        if 'metrics' not in result:
            logger.error("Engine returned success but 'metrics' key is missing")
            raise HTTPException(status_code=500, detail="Internal calculation error: metrics missing")
        
        # Преобразуем результаты в ответ
        return CalculationResponse(
            mean_final_capital=result['metrics']['mean_final_capital'],
            median_final_capital=result['metrics']['median_final_capital'],
            sharpe_ratio=result['metrics']['sharpe_ratio'],
            mean_return=result['metrics']['mean_return'],
            volatility=result['metrics']['volatility'],
            max_drawdown=result['metrics']['max_drawdown'],
            var_metrics=VaRMetrics(
                capital_95=result['metrics']['var_metrics']['capital_95'],
                loss_pct_95=result['metrics']['var_metrics']['loss_pct_95'],
                cvar_pct_95=result['metrics']['var_metrics']['cvar_pct_95'],
                capital_99=result['metrics']['var_metrics']['capital_99'],
                loss_pct_99=result['metrics']['var_metrics']['loss_pct_99'],
                cvar_pct_99=result['metrics']['var_metrics']['cvar_pct_99'],
            ),
            chart_data=ChartData(
                timestamps=result['metrics']['chart_data']['timestamps'],
                capital_mean=result['metrics']['chart_data']['capital_mean'],
                capital_q25=result['metrics']['chart_data']['capital_q25'],
                capital_q75=result['metrics']['chart_data']['capital_q75'],
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error in calculate_portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
