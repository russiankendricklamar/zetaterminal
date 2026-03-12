"""
Historical crisis scenarios for stress testing.

Real market data from MOEX, CBR, and Bloomberg sources for
major Russian and global market crises.
"""

from typing import TypedDict


class AssetClassImpact(TypedDict, total=False):
    """Impact on asset classes as percentage change."""
    equities: float
    bonds: float
    commodities: float
    fx: float
    real_estate: float
    options: float


class HistoricalScenario(TypedDict):
    """Full specification of a historical crisis scenario."""
    name: str
    description: str
    period_start: str
    period_end: str
    duration_days: int
    severity: str  # 'critical' | 'high' | 'medium'
    shocks: dict[str, float]
    asset_class_impacts: AssetClassImpact
    correlation_regime: str


HISTORICAL_SCENARIOS: dict[str, HistoricalScenario] = {
    "covid_2020": {
        "name": "COVID-19 Crash",
        "description": (
            "Global pandemic triggered the fastest bear market in history. "
            "MOEX lost 34% in one month, oil futures went negative. "
            "CBR intervened with FX sales and repo operations."
        ),
        "period_start": "2020-02-20",
        "period_end": "2020-03-23",
        "duration_days": 32,
        "severity": "critical",
        "shocks": {
            "moex_return": -0.34,
            "rts_return": -0.45,
            "usdrub_change": 0.22,
            "brent_return": -0.65,
            "ofz_10y_bp": 150.0,
            "credit_spread_bp": 300.0,
            "volatility_pp": 25.0,
        },
        "asset_class_impacts": {
            "equities": -34.0,
            "bonds": -8.0,
            "commodities": -45.0,
            "fx": -18.0,
            "options": -60.0,
        },
        "correlation_regime": "crisis",
    },
    "sanctions_2022": {
        "name": "Sanctions Crisis 2022",
        "description": (
            "Unprecedented Western sanctions after Feb 24, 2022. "
            "MOEX halted trading for nearly a month. "
            "Foreign investors frozen, CBR doubled key rate to 20%."
        ),
        "period_start": "2022-02-24",
        "period_end": "2022-03-10",
        "duration_days": 14,
        "severity": "critical",
        "shocks": {
            "moex_return": -0.45,
            "rts_return": -0.50,
            "usdrub_change": 0.30,
            "gas_return": 1.00,
            "ofz_10y_bp": 500.0,
            "credit_spread_bp": 500.0,
            "key_rate_pp": 10.5,
        },
        "asset_class_impacts": {
            "equities": -45.0,
            "bonds": -25.0,
            "commodities": 15.0,
            "fx": -30.0,
            "options": -80.0,
        },
        "correlation_regime": "crisis",
    },
    "crimea_2014": {
        "name": "Crimea Annexation 2014",
        "description": (
            "Geopolitical shock from Crimea annexation in March 2014. "
            "First round of Western sanctions. Capital outflows accelerated. "
            "CBR spent $11.3B defending the ruble."
        ),
        "period_start": "2014-03-01",
        "period_end": "2014-03-25",
        "duration_days": 24,
        "severity": "high",
        "shocks": {
            "moex_return": -0.15,
            "rts_return": -0.20,
            "usdrub_change": 0.10,
            "brent_return": -0.05,
            "ofz_10y_bp": 200.0,
            "credit_spread_bp": 150.0,
            "volatility_pp": 10.0,
        },
        "asset_class_impacts": {
            "equities": -15.0,
            "bonds": -10.0,
            "commodities": -3.0,
            "fx": -8.0,
        },
        "correlation_regime": "stressed",
    },
    "lehman_2008": {
        "name": "Lehman Brothers / GFC 2008",
        "description": (
            "Global financial crisis following Lehman Brothers bankruptcy. "
            "MOEX lost 55% from peak to trough. RTS collapsed 70%. "
            "Massive margin calls and forced liquidations across EM."
        ),
        "period_start": "2008-09-15",
        "period_end": "2008-11-20",
        "duration_days": 66,
        "severity": "critical",
        "shocks": {
            "moex_return": -0.55,
            "rts_return": -0.70,
            "usdrub_change": 0.25,
            "brent_return": -0.55,
            "credit_spread_bp": 400.0,
            "volatility_pp": 30.0,
        },
        "asset_class_impacts": {
            "equities": -55.0,
            "bonds": -15.0,
            "commodities": -40.0,
            "fx": -20.0,
            "real_estate": -25.0,
            "options": -70.0,
        },
        "correlation_regime": "crisis",
    },
    "ruble_crisis_2014": {
        "name": "Ruble Crisis Dec 2014",
        "description": (
            "Black Tuesday: ruble lost 20% in a single day (Dec 16). "
            "CBR emergency rate hike from 10.5% to 17%. "
            "Oil collapse compounded by sanctions and capital flight."
        ),
        "period_start": "2014-12-01",
        "period_end": "2014-12-31",
        "duration_days": 30,
        "severity": "critical",
        "shocks": {
            "moex_return": -0.20,
            "usdrub_change": 0.85,
            "key_rate_pp": 11.5,
            "ofz_10y_bp": 600.0,
            "credit_spread_bp": 350.0,
            "volatility_pp": 20.0,
        },
        "asset_class_impacts": {
            "equities": -20.0,
            "bonds": -30.0,
            "commodities": -10.0,
            "fx": -46.0,
        },
        "correlation_regime": "crisis",
    },
}


def get_scenario_keys() -> list[str]:
    """Return all available historical scenario keys."""
    return list(HISTORICAL_SCENARIOS.keys())


def get_scenario(key: str) -> HistoricalScenario:
    """
    Get a single historical scenario by key.

    Args:
        key: Scenario identifier (e.g. 'covid_2020').

    Returns:
        Full scenario specification.

    Raises:
        ValueError: If key is not found.
    """
    if key not in HISTORICAL_SCENARIOS:
        available = ", ".join(HISTORICAL_SCENARIOS.keys())
        raise ValueError(
            f"Unknown historical scenario '{key}'. "
            f"Available: {available}"
        )
    return HISTORICAL_SCENARIOS[key]


def get_all_scenarios() -> list[dict]:
    """
    Return all scenarios as a list of dicts with their keys included.

    Returns:
        List of scenario dicts, each with an added 'key' field.
    """
    result = []
    for key, scenario in HISTORICAL_SCENARIOS.items():
        entry = dict(scenario)
        entry["key"] = key
        result.append(entry)
    return result


def map_historical_to_stress_params(
    scenario_key: str,
    n_assets: int,
    base_mu: list[float],
    base_cov: list[list[float]],
) -> tuple[list[float], list[list[float]]]:
    """
    Map historical scenario shocks to mu/cov modifications for MC simulation.

    The mapping applies:
    - Equity return shocks to mu vector
    - Volatility increase to diagonal of covariance matrix
    - Crisis correlation regime: push off-diagonal correlations toward 1.0

    Args:
        scenario_key: Historical scenario identifier.
        n_assets: Number of assets in portfolio.
        base_mu: Base expected returns vector.
        base_cov: Base covariance matrix.

    Returns:
        Tuple of (shocked_mu, shocked_cov) as lists.
    """
    import numpy as np

    scenario = get_scenario(scenario_key)
    shocks = scenario["shocks"]

    mu = np.array(base_mu, dtype=float)
    cov = np.array(base_cov, dtype=float)

    # Apply return shock from MOEX index as a broad equity shock
    equity_shock = shocks.get("moex_return", 0.0)
    # Scale mu: if MOEX dropped 34%, shift expected returns down
    # Annualize the shock over the crisis duration
    duration_years = max(scenario["duration_days"] / 252, 0.01)
    annualized_shock = equity_shock / duration_years
    mu = mu + annualized_shock

    # Apply volatility increase
    vol_increase_pp = shocks.get("volatility_pp", 0.0)
    if vol_increase_pp > 0:
        # Convert percentage points to multiplier on variance
        # If base vol ~25% and shock adds 25pp, new vol ~50%, variance multiplier ~4
        diag = np.diag(cov)
        base_vols = np.sqrt(np.maximum(diag, 1e-10))
        avg_base_vol = float(np.mean(base_vols))
        if avg_base_vol > 0:
            new_avg_vol = avg_base_vol + vol_increase_pp / 100.0
            vol_multiplier = (new_avg_vol / avg_base_vol) ** 2
            cov = cov * vol_multiplier

    # Apply crisis correlation regime
    corr_regime = scenario["correlation_regime"]
    if corr_regime in ("crisis", "stressed"):
        # Push correlations toward 1.0 (crisis convergence)
        blend = 0.7 if corr_regime == "crisis" else 0.4
        diag = np.diag(cov)
        safe_diag = np.maximum(diag, 1e-10)
        d_sqrt = np.sqrt(safe_diag)
        d_inv = 1.0 / d_sqrt

        # Extract correlation matrix
        corr = cov * np.outer(d_inv, d_inv)
        np.fill_diagonal(corr, 1.0)
        corr = np.clip(corr, -1.0, 1.0)

        # Blend toward perfect correlation
        ones_matrix = np.ones_like(corr)
        corr_crisis = (1 - blend) * corr + blend * ones_matrix
        np.fill_diagonal(corr_crisis, 1.0)
        corr_crisis = np.clip(corr_crisis, -0.999, 0.999)
        np.fill_diagonal(corr_crisis, 1.0)

        # Reconstruct covariance
        d_mat = np.diag(d_sqrt)
        cov = d_mat @ corr_crisis @ d_mat

        # Ensure positive semi-definite
        cov = (cov + cov.T) / 2
        eigvals = np.linalg.eigvalsh(cov)
        if np.min(eigvals) < 0:
            cov += np.eye(n_assets) * (abs(np.min(eigvals)) + 1e-6)

    return mu.tolist(), cov.tolist()
