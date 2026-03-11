"""
API endpoints для Black-Litterman оптимизации портфеля.
"""
import logging
from datetime import datetime

import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.black_litterman_service import optimize_black_litterman

logger = logging.getLogger(__name__)

router = APIRouter()


class BLView(BaseModel):
    """Один инвестиционный взгляд."""
    assets: list[int] = Field(..., description="Индексы активов, затронутых взглядом")
    weights: list[float] = Field(..., description="Веса в pick-матрице P для этого взгляда")
    expected_return: float = Field(..., description="Ожидаемая доходность по взгляду (Q_k)")
    confidence: float = Field(default=0.5, ge=0.01, le=1.0, description="Уверенность 0..1")


class BlackLittermanRequest(BaseModel):
    """Запрос на Black-Litterman оптимизацию."""
    cov_matrix: list[list[float]] = Field(..., description="Ковариационная матрица (N x N)")
    market_weights: list[float] = Field(..., description="Рыночные капитализационные веса (N)")
    views: list[BLView] = Field(..., min_length=1, description="Список инвестиционных взглядов")
    tau: float = Field(default=0.05, gt=0, le=1, description="Скаляр масштаба неопределённости")
    delta: float = Field(default=2.5, gt=0, description="Коэффициент неприятия риска")
    risk_free_rate: float = Field(default=0.0, description="Безрисковая ставка")
    max_weight: float = Field(default=0.4, gt=0, le=1, description="Макс. вес на актив")
    asset_names: list[str] | None = Field(None, description="Названия активов")


@router.post("/optimize")
async def optimize_bl_portfolio(request: BlackLittermanRequest):
    """
    Выполняет Black-Litterman оптимизацию портфеля.
    """
    try:
        N = len(request.market_weights)
        Sigma = np.array(request.cov_matrix)
        w_mkt = np.array(request.market_weights)

        if Sigma.shape != (N, N):
            raise ValueError(
                f"Размерность ковариационной матрицы {Sigma.shape} "
                f"не соответствует количеству активов {N}"
            )

        K = len(request.views)
        P = np.zeros((K, N))
        Q = np.zeros(K)
        confidence = np.zeros(K)

        for k, view in enumerate(request.views):
            for asset_idx, weight in zip(view.assets, view.weights, strict=False):
                if asset_idx < 0 or asset_idx >= N:
                    raise ValueError(f"Индекс актива {asset_idx} вне диапазона [0, {N-1}]")
                P[k, asset_idx] = weight
            Q[k] = view.expected_return
            confidence[k] = view.confidence

        result = optimize_black_litterman(
            cov_matrix=Sigma,
            market_weights=w_mkt,
            views_P=P,
            views_Q=Q,
            tau=request.tau,
            delta=request.delta,
            risk_free_rate=request.risk_free_rate,
            confidence=confidence,
            asset_names=request.asset_names,
            max_weight=request.max_weight,
        )

        result["timestamp"] = datetime.now().isoformat()
        return result

    except ValueError as e:
        logger.error("Black-Litterman validation error: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid input parameters") from e
    except np.linalg.LinAlgError as e:
        logger.error("Black-Litterman linear algebra error: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Linear algebra error in optimization") from e
    except Exception as e:
        logger.error("Black-Litterman optimization failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/health")
async def bl_health():
    """Health check для Black-Litterman сервиса."""
    return {"status": "healthy", "service": "black-litterman"}
