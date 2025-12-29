from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from typing_extensions import Annotated


FlexList = Annotated[list, Field(json_schema_extra={'type': 'array'})]

class CalculationRequest(BaseModel):
    initial_capital: float = 1_000_000
    gamma: float = 3.0
    n_paths: int = 5000
    time_horizon: float = 1.0
    run_stress_test: bool = False

class BacktestRequest(BaseModel):
    tickers: List[str]
    start_date: str
    end_date: str
    initial_capital: float = 1_000_000

class VaRMetrics(BaseModel):
    capital_95: float
    loss_pct_95: float
    cvar_pct_95: float
    capital_99: float
    loss_pct_99: float
    cvar_pct_99: float
    avg_loss: float
    max_loss: float
    std_loss: float
    is_conservative: Optional[bool] = None

class StressScenarioResult(BaseModel):
    scenario_name: str
    expected_capital: float
    max_drawdown: float
    prob_of_loss: Optional[float] = None

class ChartData(BaseModel):
    timestamps: FlexList
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
    mean_loss: float
    max_loss: float
    std_loss: float
    var_metrics: VaRMetrics
    stress_tests: Optional[Dict[str, StressScenarioResult]] = None
    chart_data: ChartData
    asset_distributions: Optional[Dict[str, Any]] = None
    status: str = "success"

class BacktestResponse(BaseModel):
    total_return: float
    max_drawdown: float
    var_breaches: int
    history: Dict[str, List[Any]]