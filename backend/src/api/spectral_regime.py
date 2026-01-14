"""
API endpoints для комплексного анализа скрытых рыночных режимов.

Endpoints:
- POST /analyze - Запуск полного анализа спектральных режимов
- GET /assets - Получение списка доступных активов
- POST /fetch-data - Загрузка данных актива и расчёт доходностей
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import numpy as np
from datetime import datetime, timedelta

router = APIRouter()


class SpectralAnalysisRequest(BaseModel):
    """Запрос на анализ спектральных режимов."""
    returns: List[float] = Field(..., description="Временной ряд доходностей")
    n_poles: int = Field(default=5, ge=2, le=15, description="Количество полюсов (2-15)")
    window_size: int = Field(default=20, ge=5, le=100, description="Размер скользящего окна (5-100)")
    max_lag: Optional[int] = Field(default=None, description="Максимальный лаг ACF (по умолчанию T/4)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "returns": [0.01, -0.02, 0.015, 0.005, -0.01],
                "n_poles": 5,
                "window_size": 20
            }
        }


class AssetDataRequest(BaseModel):
    """Запрос на загрузку данных актива."""
    ticker: str = Field(..., description="Тикер актива")
    period_days: int = Field(default=252, ge=30, le=2520, description="Период в днях")
    source: str = Field(default="yfinance", description="Источник данных: yfinance, moex")


class SpectralAnalysisResponse(BaseModel):
    """Ответ анализа спектральных режимов."""
    success: bool
    summary: Dict[str, Any]
    visualization: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "summary": {
                    "n_regimes": 3,
                    "regime_params": {},
                    "current_metrics": {}
                },
                "visualization": {
                    "poles": [],
                    "dynamics": {}
                }
            }
        }


# Список доступных активов
AVAILABLE_ASSETS = {
    "stocks": [
        {"ticker": "SPY", "name": "S&P 500 ETF", "source": "yfinance"},
        {"ticker": "QQQ", "name": "Nasdaq 100 ETF", "source": "yfinance"},
        {"ticker": "IWM", "name": "Russell 2000 ETF", "source": "yfinance"},
        {"ticker": "DIA", "name": "Dow Jones ETF", "source": "yfinance"},
        {"ticker": "VTI", "name": "Total Stock Market ETF", "source": "yfinance"},
        {"ticker": "AAPL", "name": "Apple Inc.", "source": "yfinance"},
        {"ticker": "MSFT", "name": "Microsoft Corp.", "source": "yfinance"},
        {"ticker": "GOOGL", "name": "Alphabet Inc.", "source": "yfinance"},
        {"ticker": "AMZN", "name": "Amazon.com Inc.", "source": "yfinance"},
        {"ticker": "NVDA", "name": "NVIDIA Corp.", "source": "yfinance"},
    ],
    "crypto": [
        {"ticker": "BTC-USD", "name": "Bitcoin", "source": "yfinance"},
        {"ticker": "ETH-USD", "name": "Ethereum", "source": "yfinance"},
        {"ticker": "SOL-USD", "name": "Solana", "source": "yfinance"},
    ],
    "commodities": [
        {"ticker": "GLD", "name": "Gold ETF", "source": "yfinance"},
        {"ticker": "SLV", "name": "Silver ETF", "source": "yfinance"},
        {"ticker": "USO", "name": "Oil ETF", "source": "yfinance"},
    ],
    "bonds": [
        {"ticker": "TLT", "name": "20+ Year Treasury Bond ETF", "source": "yfinance"},
        {"ticker": "IEF", "name": "7-10 Year Treasury Bond ETF", "source": "yfinance"},
        {"ticker": "LQD", "name": "Investment Grade Corporate Bond ETF", "source": "yfinance"},
    ],
    "forex": [
        {"ticker": "EURUSD=X", "name": "EUR/USD", "source": "yfinance"},
        {"ticker": "GBPUSD=X", "name": "GBP/USD", "source": "yfinance"},
        {"ticker": "USDJPY=X", "name": "USD/JPY", "source": "yfinance"},
        {"ticker": "RUB=X", "name": "USD/RUB", "source": "yfinance"},
    ],
    "russia": [
        {"ticker": "IMOEX.ME", "name": "MOEX Russia Index", "source": "yfinance"},
        {"ticker": "SBER.ME", "name": "Sberbank", "source": "yfinance"},
        {"ticker": "GAZP.ME", "name": "Gazprom", "source": "yfinance"},
        {"ticker": "LKOH.ME", "name": "Lukoil", "source": "yfinance"},
        {"ticker": "ROSN.ME", "name": "Rosneft", "source": "yfinance"},
    ]
}


@router.get("/assets")
async def get_available_assets():
    """
    Получить список доступных активов для анализа.
    
    Returns:
        Словарь с категориями активов
    """
    return {
        "success": True,
        "data": AVAILABLE_ASSETS
    }


@router.post("/fetch-data")
async def fetch_asset_data(request: AssetDataRequest):
    """
    Загрузить исторические данные актива и рассчитать доходности.
    
    Parameters:
        request: Параметры запроса (тикер, период, источник)
    
    Returns:
        Массив дневных доходностей и метаданные
    """
    try:
        import yfinance as yf
        
        ticker = request.ticker
        period_days = request.period_days
        
        # Загрузка данных через yfinance
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days + 30)  # +30 для запаса
        
        data = yf.download(
            ticker,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            progress=False
        )
        
        if data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Не удалось загрузить данные для тикера {ticker}"
            )
        
        # Расчёт логарифмических доходностей
        prices = data['Close'].values.flatten()
        returns = np.diff(np.log(prices))
        
        # Ограничение по количеству
        if len(returns) > period_days:
            returns = returns[-period_days:]
        
        # Метаданные
        metadata = {
            "ticker": ticker,
            "start_date": str(data.index[0].date()) if len(data) > 0 else None,
            "end_date": str(data.index[-1].date()) if len(data) > 0 else None,
            "n_observations": len(returns),
            "mean_return": float(np.mean(returns)),
            "std_return": float(np.std(returns)),
            "min_return": float(np.min(returns)),
            "max_return": float(np.max(returns)),
            "last_price": float(prices[-1]) if len(prices) > 0 else None
        }
        
        return {
            "success": True,
            "returns": returns.tolist(),
            "prices": prices.tolist(),
            "metadata": metadata
        }
        
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="yfinance не установлен. Установите: pip install yfinance"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при загрузке данных: {str(e)}"
        )


@router.post("/analyze", response_model=SpectralAnalysisResponse)
async def analyze_spectral_regimes(request: SpectralAnalysisRequest):
    """
    Запустить комплексный анализ скрытых рыночных режимов.
    
    Выполняет:
    1. Вычисление ACF
    2. Идентификацию полюсов методом Prony
    3. Кластеризацию полюсов в режимы
    4. Спектральную факторизацию
    5. Анализ минимальной фазы
    6. Динамический анализ в скользящем окне
    
    Parameters:
        request: Параметры анализа
    
    Returns:
        Полные результаты анализа с данными для визуализации
    """
    try:
        from src.services.spectral_regime_service import run_spectral_regime_analysis
        
        returns = request.returns
        
        if len(returns) < 50:
            raise HTTPException(
                status_code=400,
                detail="Минимальная длина временного ряда - 50 наблюдений"
            )
        
        if len(returns) > 5000:
            raise HTTPException(
                status_code=400,
                detail="Максимальная длина временного ряда - 5000 наблюдений"
            )
        
        # Проверка на NaN и Inf
        returns_arr = np.array(returns)
        if np.any(~np.isfinite(returns_arr)):
            raise HTTPException(
                status_code=400,
                detail="Временной ряд содержит NaN или Inf значения"
            )
        
        # Запуск анализа
        result = run_spectral_regime_analysis(
            returns=returns,
            n_poles=request.n_poles,
            window_size=request.window_size,
            max_lag=request.max_lag
        )
        
        return SpectralAnalysisResponse(
            success=True,
            summary=result['summary'],
            visualization=result['visualization']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка анализа: {str(e)}"
        )


@router.post("/analyze-asset")
async def analyze_asset_regimes(
    ticker: str,
    period_days: int = 252,
    n_poles: int = 5,
    window_size: int = 20
):
    """
    Комбинированный endpoint: загрузка данных актива и анализ режимов.
    
    Parameters:
        ticker: Тикер актива
        period_days: Период в днях
        n_poles: Количество полюсов
        window_size: Размер окна
    
    Returns:
        Результаты анализа с метаданными актива
    """
    try:
        # Загрузка данных
        data_request = AssetDataRequest(ticker=ticker, period_days=period_days)
        data_response = await fetch_asset_data(data_request)
        
        if not data_response.get('success'):
            raise HTTPException(status_code=500, detail="Ошибка загрузки данных")
        
        returns = data_response['returns']
        
        # Анализ
        analysis_request = SpectralAnalysisRequest(
            returns=returns,
            n_poles=n_poles,
            window_size=window_size
        )
        analysis_response = await analyze_spectral_regimes(analysis_request)
        
        return {
            "success": True,
            "asset_metadata": data_response['metadata'],
            "prices": data_response['prices'],
            "returns": returns,
            "analysis": {
                "summary": analysis_response.summary,
                "visualization": analysis_response.visualization
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка анализа актива: {str(e)}"
        )
