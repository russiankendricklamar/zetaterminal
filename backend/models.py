from pydantic import BaseModel
from typing import List, Dict, Optional

class CalculationRequest(BaseModel):
    initial_capital: float = 1_000_000
    gamma: float = 3.0
    n_paths: int = 5000
    time_horizon: float = 1.0

class VaRMetrics(BaseModel):
    capital_95: float
    loss_pct_95: float
    cvar_pct_95: float
    capital_99: float
    loss_pct_99: float
    cvar_pct_99: float

class ChartData(BaseModel):
    timestamps: List[float]
    capital_mean: List[float]
    capital_q25: List[float]
    capital_q75: List[float]

class CalculationResponse(BaseModel):
    mean_final_capital: float
    median_final_capital: float
    sharpe_ratio: float
    mean_return: float
    volatility: float
    max_drawdown: float
    var_metrics: VaRMetrics
    chart_data: ChartData
    status: str = "success"