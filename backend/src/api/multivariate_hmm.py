"""
API endpoints для многомерной HMM модели анализа рыночных режимов.

Endpoints:
- POST /multivariate-hmm/fit - Обучение модели на многомерных данных
- GET /multivariate-hmm/predict - Предсказание состояний
- GET /multivariate-hmm/statistics - Статистика режимов
- GET /multivariate-hmm/regime-at-time - Информация о режиме в момент времени
- POST /multivariate-hmm/simulate - Симуляция траекторий
- GET /multivariate-hmm/export - Экспорт результатов в DataFrame
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import numpy as np
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class FitRequest(BaseModel):
    """Запрос на обучение модели."""
    data: Optional[List[List[float]]] = Field(None, description="(T, K) массив доходностей. Если None, загружаются данные портфеля")
    asset_names: Optional[List[str]] = Field(None, description="Названия активов")
    bank_reg_number: Optional[str] = Field(None, description="Регистрационный номер банка для загрузки портфеля")
    n_regimes: Optional[int] = Field(None, ge=2, le=5, description="Число режимов (2-5). Если None, определяется автоматически")
    auto_optimize: bool = Field(True, description="Автоматически определить оптимальное количество режимов")
    criterion: str = Field('aicc', description="Критерий для выбора количества режимов: 'aic', 'bic', или 'aicc'")
    max_iterations: int = Field(50, ge=10, le=200, description="Максимальное число итераций")
    tol: float = Field(1e-6, ge=1e-10, le=1e-3, description="Tolerance для сходимости")
    random_state: int = Field(42, description="Random seed")
    period_days: int = Field(252, ge=30, le=2520, description="Период исторических данных в днях")


class FitResponse(BaseModel):
    """Ответ после обучения модели."""
    success: bool
    n_regimes: int
    n_assets: int
    n_samples: int
    asset_names: List[str]
    log_likelihood_history: List[float]
    iterations: int
    message: str


class PredictRequest(BaseModel):
    """Запрос на предсказание состояний."""
    data: Optional[List[List[float]]] = Field(None, description="(T, K) массив данных. Если None, используется обученный ряд")


class PredictResponse(BaseModel):
    """Ответ с предсказанными состояниями."""
    states: List[int]
    probabilities: List[List[float]]
    time_indices: List[int]


class RegimeStatisticsResponse(BaseModel):
    """Ответ со статистикой режимов."""
    statistics: List[Dict[str, Any]]


class RegimeAtTimeResponse(BaseModel):
    """Ответ с информацией о режиме в момент времени."""
    time_index: int
    regime_probabilities: List[float]
    most_likely_regime: int
    confidence: float
    entropy: float


class SimulateRequest(BaseModel):
    """Запрос на симуляцию."""
    n_steps: int = Field(100, ge=1, le=1000, description="Количество шагов симуляции")


class SimulateResponse(BaseModel):
    """Ответ с симулированными траекториями."""
    trajectories: List[List[float]]
    n_steps: int
    n_assets: int


# Глобальное хранилище обученных моделей (в production лучше использовать Redis или БД)
_trained_models: Dict[str, Any] = {}


def _get_model_key(asset_names: List[str], n_regimes: int) -> str:
    """Генерировать ключ для хранения модели."""
    assets_str = "_".join(sorted(asset_names))
    return f"{assets_str}_{n_regimes}"


@router.post("/multivariate-hmm/fit", response_model=FitResponse)
async def fit_model(request: FitRequest = Body(...)):
    """
    Обучение многомерной HMM модели на данных.
    
    Parameters:
        data: (T, K) массив доходностей. Если None, загружаются данные портфеля банка
        asset_names: Названия активов
        bank_reg_number: Регистрационный номер банка для загрузки портфеля
        n_regimes: Число режимов. Если None и auto_optimize=True, определяется автоматически
        auto_optimize: Автоматически определить оптимальное количество режимов
        criterion: Критерий для выбора количества режимов
        max_iterations: Максимальное число итераций EM
        tol: Tolerance для сходимости
        random_state: Random seed
        period_days: Период исторических данных в днях
    
    Returns:
        Информация об обученной модели
    """
    try:
        from src.services.multivariate_hmm_service import MultivariateHMMRegimeAnalyzer
        from src.services.yfinance_service import get_stock_history
        import yfinance as yf
        from datetime import datetime, timedelta
        
        # Если данные не предоставлены, загружаем портфель банка
        if request.data is None:
            if not request.bank_reg_number:
                raise HTTPException(
                    status_code=400,
                    detail="Необходимо указать bank_reg_number или предоставить data"
                )
            
            # Получаем портфель банка (используем ту же логику, что и в frontend)
            portfolio_key = int(request.bank_reg_number) % 5
            portfolio_templates = {
                0: ['SBER.ME', 'GAZP.ME', 'LKOH.ME', 'GMKN.ME', 'YNDX.ME', 'ROSN.ME', 'NVTK.ME', 'TATN.ME', 'ALRS.ME', 'MGNT.ME'],
                1: ['SBER.ME', 'NLMK.ME', 'RTKM.ME', 'AFKS.ME', 'FIVE.ME', 'PHOR.ME', 'HYDR.ME', 'IRAO.ME', 'FEES.ME', 'SNGS.ME'],
                2: ['GAZP.ME', 'LKOH.ME', 'GMKN.ME', 'YNDX.ME', 'ROSN.ME', 'NVTK.ME', 'TATN.ME', 'ALRS.ME', 'MGNT.ME', 'MOEX.ME'],
                3: ['SBER.ME', 'RTKM.ME', 'AFKS.ME', 'FIVE.ME', 'PHOR.ME', 'HYDR.ME', 'IRAO.ME', 'FEES.ME', 'SNGS.ME', 'SNGSP.ME'],
                4: ['LKOH.ME', 'GMKN.ME', 'YNDX.ME', 'ROSN.ME', 'NVTK.ME', 'TATN.ME', 'ALRS.ME', 'MGNT.ME', 'MOEX.ME', 'POLY.ME']
            }
            
            tickers = portfolio_templates.get(portfolio_key, portfolio_templates[0])
            asset_names = request.asset_names or tickers
            
            # Загружаем исторические данные для всех активов
            end_date = datetime.now()
            start_date = end_date - timedelta(days=request.period_days)
            
            all_data = []
            valid_tickers = []
            valid_asset_names = []
            
            for ticker, asset_name in zip(tickers, asset_names):
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(start=start_date, end=end_date, interval='1d')
                    
                    if hist.empty or len(hist) < 30:
                        logger.warning(f"Недостаточно данных для {ticker}, пропускаем")
                        continue
                    
                    # Вычисляем доходности
                    prices = hist['Close'].values
                    returns = np.diff(prices) / prices[:-1]
                    
                    if len(returns) > 0:
                        all_data.append(returns)
                        valid_tickers.append(ticker)
                        valid_asset_names.append(asset_name)
                except Exception as e:
                    logger.warning(f"Ошибка загрузки данных для {ticker}: {e}")
                    continue
            
            if len(all_data) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Не удалось загрузить данные ни для одного актива"
                )
            
            # Выравниваем длины временных рядов (берем минимальную длину)
            min_length = min(len(d) for d in all_data)
            all_data = [d[:min_length] for d in all_data]
            
            # Преобразуем в (T, K) массив
            y = np.array(all_data).T
            asset_names = valid_asset_names
            
        else:
            # Используем предоставленные данные
            y = np.array(request.data, dtype=np.float64)
            
            if y.ndim != 2:
                raise HTTPException(
                    status_code=400,
                    detail=f"Данные должны быть 2D массивом (T, K), получен shape: {y.shape}"
                )
            
            T, K = y.shape
            
            if T <= K:
                raise HTTPException(
                    status_code=400,
                    detail=f"Число наблюдений ({T}) должно быть больше числа активов ({K})"
                )
            
            # Определяем названия активов
            asset_names = request.asset_names or [f"Asset_{i+1}" for i in range(K)]
            
            if len(asset_names) != K:
                raise HTTPException(
                    status_code=400,
                    detail=f"asset_names должен содержать {K} элементов, получено {len(asset_names)}"
                )
        
        T, K = y.shape
        
        # Создаем модель
        model = MultivariateHMMRegimeAnalyzer(
            n_regimes=request.n_regimes or 2,  # Временное значение, будет переопределено при auto_optimize
            random_state=request.random_state
        )
        
        # Автоматическое определение количества режимов или использование заданного
        if request.auto_optimize and request.n_regimes is None:
            optimal_n_regimes, best_criterion_value = model.find_optimal_n_regimes(
                y=y,
                asset_names=asset_names,
                min_regimes=2,
                max_regimes=5,
                criterion=request.criterion,
                max_iterations=request.max_iterations,
                tol=request.tol
            )
            n_regimes_used = optimal_n_regimes
        else:
            n_regimes_used = request.n_regimes or 2
            model.n_regimes = n_regimes_used
            model.fit(
                y=y,
                asset_names=asset_names,
                max_iterations=request.max_iterations,
                tol=request.tol
            )
        
        # Сохраняем модель
        model_key = _get_model_key(asset_names, n_regimes_used)
        _trained_models[model_key] = model
        
        return FitResponse(
            success=True,
            n_regimes=n_regimes_used,
            n_assets=K,
            n_samples=T,
            asset_names=asset_names,
            log_likelihood_history=model.log_likelihood_history,
            iterations=len(model.log_likelihood_history),
            message=f"Модель успешно обучена на {T} наблюдениях для {K} активов с {n_regimes_used} режимами"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обучения модели: {str(e)}"
        )


@router.post("/multivariate-hmm/predict", response_model=PredictResponse)
async def predict_states(request: PredictRequest = Body(...)):
    """
    Предсказать наиболее вероятные состояния.
    
    Parameters:
        data: (T, K) массив данных. Если None, используется обученный ряд
    
    Returns:
        Предсказанные состояния и вероятности
    """
    try:
        from src.services.multivariate_hmm_service import MultivariateHMMRegimeAnalyzer
        
        # Получаем последнюю обученную модель (в production нужна более сложная логика)
        if not _trained_models:
            raise HTTPException(
                status_code=400,
                detail="Нет обученных моделей. Сначала вызовите /fit"
            )
        
        # Берем последнюю модель
        model = list(_trained_models.values())[-1]
        
        if request.data is not None:
            y = np.array(request.data, dtype=np.float64)
            states = model.predict_states(y=y)
            # Вычисляем вероятности для новых данных
            alpha, beta = model.forward_backward((y - model.y_mean) / model.y_std)
            gamma, _ = model.forward_backward_posterior(
                (y - model.y_mean) / model.y_std, alpha, beta
            )
            probabilities = gamma.tolist()
        else:
            states = model.predict_states()
            probabilities = model.gamma.tolist()
        
        return PredictResponse(
            states=states.tolist(),
            probabilities=probabilities,
            time_indices=list(range(len(states)))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка предсказания: {str(e)}"
        )


@router.get("/multivariate-hmm/statistics", response_model=RegimeStatisticsResponse)
async def get_regime_statistics():
    """
    Получить статистику для каждого режима.
    
    Returns:
        Статистика режимов
    """
    try:
        if not _trained_models:
            raise HTTPException(
                status_code=400,
                detail="Нет обученных моделей. Сначала вызовите /fit"
            )
        
        model = list(_trained_models.values())[-1]
        statistics = model.get_regime_statistics()
        
        return RegimeStatisticsResponse(statistics=statistics)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения статистики: {str(e)}"
        )


@router.get("/multivariate-hmm/regime-at-time", response_model=RegimeAtTimeResponse)
async def get_regime_at_time(
    t: int = Query(..., ge=0, description="Индекс времени")
):
    """
    Получить информацию о режиме в момент времени t.
    
    Parameters:
        t: Индекс времени
    
    Returns:
        Информация о режиме в момент t
    """
    try:
        if not _trained_models:
            raise HTTPException(
                status_code=400,
                detail="Нет обученных моделей. Сначала вызовите /fit"
            )
        
        model = list(_trained_models.values())[-1]
        regime_info = model.get_regime_at_time(t)
        
        return RegimeAtTimeResponse(**regime_info)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения информации о режиме: {str(e)}"
        )


@router.post("/multivariate-hmm/simulate", response_model=SimulateResponse)
async def simulate_trajectories(request: SimulateRequest = Body(...)):
    """
    Симулировать будущие траектории.
    
    Parameters:
        n_steps: Количество шагов симуляции
    
    Returns:
        Симулированные траектории
    """
    try:
        if not _trained_models:
            raise HTTPException(
                status_code=400,
                detail="Нет обученных моделей. Сначала вызовите /fit"
            )
        
        model = list(_trained_models.values())[-1]
        trajectories = model.simulate(n_steps=request.n_steps)
        
        return SimulateResponse(
            trajectories=trajectories.tolist(),
            n_steps=request.n_steps,
            n_assets=model.n_assets
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка симуляции: {str(e)}"
        )


@router.get("/multivariate-hmm/export")
async def export_to_dataframe():
    """
    Экспортировать результаты в DataFrame формат.
    
    Returns:
        DataFrame с вероятностями режимов и предсказанными состояниями
    """
    try:
        if not _trained_models:
            raise HTTPException(
                status_code=400,
                detail="Нет обученных моделей. Сначала вызовите /fit"
            )
        
        model = list(_trained_models.values())[-1]
        df = model.export_to_dataframe()
        
        return {
            "success": True,
            "data": df.to_dict(orient="records"),
            "columns": df.columns.tolist()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка экспорта: {str(e)}"
        )


@router.get("/multivariate-hmm/transition-matrix")
async def get_transition_matrix():
    """
    Получить матрицу переходов.
    
    Returns:
        Матрица переходов
    """
    try:
        if not _trained_models:
            raise HTTPException(
                status_code=400,
                detail="Нет обученных моделей. Сначала вызовите /fit"
            )
        
        model = list(_trained_models.values())[-1]
        
        return {
            "success": True,
            "transition_matrix": model.transition_matrix.tolist(),
            "n_regimes": model.n_regimes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения матрицы переходов: {str(e)}"
        )


@router.get("/multivariate-hmm/chart-data")
async def get_chart_data():
    """
    Получить данные для визуализации на фронтенде.
    
    Returns:
        Данные для графиков: цены, режимы, волатильность
    """
    try:
        if not _trained_models:
            raise HTTPException(
                status_code=400,
                detail="Нет обученных моделей. Сначала вызовите /fit"
            )
        
        model = list(_trained_models.values())[-1]
        
        # Получаем предсказанные состояния
        states = model.predict_states()
        
        # Восстанавливаем исходные данные (для визуализации цены)
        y_original = model.y_normalized * model.y_std + model.y_mean
        
        # Вычисляем волатильность (скользящее окно 20 дней)
        T = len(y_original)
        volatility = np.zeros(T)
        window = min(20, T)
        
        for t in range(T):
            start = max(0, t - window + 1)
            window_data = y_original[start:t+1]
            if len(window_data) > 1:
                # Берем среднюю волатильность по всем активам
                volatility[t] = np.std(window_data, axis=0).mean() * np.sqrt(252)  # Годовая волатильность
            else:
                volatility[t] = 0.0
        
        # Строим цену из доходностей
        # Для многомерного случая берем среднюю доходность по активам
        if y_original.shape[1] > 1:
            mean_returns = y_original.mean(axis=1)
        else:
            mean_returns = y_original.flatten()
        
        # Кумулятивное произведение для построения цены
        prices = np.cumprod(1 + mean_returns) * 100  # Начальная цена 100
        
        # Формируем данные для фронтенда
        chart_data = []
        for t in range(T):
            chart_data.append({
                "price": float(prices[t]),
                "regime": int(states[t]),
                "vol": float(volatility[t]),
                "time_index": t
            })
        
        return {
            "success": True,
            "data": chart_data,
            "n_samples": T,
            "n_regimes": model.n_regimes,
            "asset_names": model.asset_names
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения данных для графиков: {str(e)}"
        )
