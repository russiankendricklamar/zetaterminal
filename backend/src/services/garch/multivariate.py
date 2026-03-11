"""
DCC-GARCH (Dynamic Conditional Correlation) — Engle 2002.

Two-step estimation:
1. Fit univariate GARCH to each asset -> standardized residuals z_t
2. Estimate DCC parameters (a, b) from z_t:
   Q_t = (1-a-b) * Q_bar + a * z_{t-1} * z_{t-1}' + b * Q_{t-1}
   R_t = diag(Q_t)^{-1/2} * Q_t * diag(Q_t)^{-1/2}
"""
from typing import Any

import numpy as np
from scipy.optimize import minimize

from src.services.garch.univariate import (
    VARIANCE_FLOOR,
    egarch,
    ewma,
    garch_11,
    gjr_garch,
)

MODEL_MAP = {
    "garch_11": garch_11,
    "gjr_garch": gjr_garch,
    "egarch": egarch,
    "ewma": ewma,
}


def dcc_garch(
    returns_matrix: np.ndarray,
    univariate_model: str = "garch_11",
    univariate_params: list[dict[str, float]] | None = None,
    dcc_params: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Fit DCC-GARCH model to multivariate returns.

    Args:
        returns_matrix: (T, N) array of returns for N assets.
        univariate_model: which univariate model to use per asset.
        univariate_params: optional pre-fitted params per asset.
        dcc_params: optional {"a": float, "b": float} for DCC. If None, MLE fit.

    Returns:
        Dict with univariate results, DCC params, correlation matrices, covariance matrices.
    """
    if returns_matrix.ndim != 2:
        raise ValueError("returns_matrix must be 2D (T x N)")

    T, N = returns_matrix.shape
    if T < 20:
        raise ValueError(f"Need >= 20 observations, got {T}")
    if N < 2:
        raise ValueError(f"Need >= 2 assets, got {N}")
    if N > 200:
        raise ValueError(f"Max 200 assets, got {N}")

    model_fn = MODEL_MAP.get(univariate_model)
    if model_fn is None:
        raise ValueError(f"Unknown model: {univariate_model}. Use: {list(MODEL_MAP.keys())}")

    # Step 1: Fit univariate models
    univariate_results = []
    standardized_residuals = np.zeros((T, N))

    for i in range(N):
        asset_returns = returns_matrix[:, i]
        params_i = univariate_params[i] if univariate_params else None

        result = model_fn(asset_returns) if univariate_model == "ewma" else model_fn(asset_returns, params=params_i)

        univariate_results.append(result)
        standardized_residuals[:, i] = result["residuals"]

    # Step 2: DCC estimation
    Q_bar = np.corrcoef(standardized_residuals.T)
    # Ensure positive definite
    eigvals = np.linalg.eigvalsh(Q_bar)
    if np.min(eigvals) < 1e-8:
        Q_bar += np.eye(N) * 1e-6

    if dcc_params is None:
        dcc_params = _fit_dcc_mle(standardized_residuals, Q_bar)

    a = dcc_params["a"]
    b = dcc_params["b"]

    # Step 3: Compute time-varying correlations
    Q_t = Q_bar.copy()
    correlations = np.zeros((T, N, N))
    covariances = np.zeros((T, N, N))

    for t in range(T):
        if t > 0:
            z_outer = np.outer(standardized_residuals[t - 1], standardized_residuals[t - 1])
            Q_t = (1 - a - b) * Q_bar + a * z_outer + b * Q_t

        # Normalize Q_t -> R_t
        Q_diag_inv_sqrt = np.diag(1.0 / np.sqrt(np.maximum(np.diag(Q_t), VARIANCE_FLOOR)))
        R_t = Q_diag_inv_sqrt @ Q_t @ Q_diag_inv_sqrt

        # Clip to valid correlation range
        np.fill_diagonal(R_t, 1.0)
        R_t = np.clip(R_t, -1.0, 1.0)

        correlations[t] = R_t

        # Build covariance matrix: D_t * R_t * D_t
        vols_t = np.array([
            np.sqrt(max(univariate_results[i]["variances"][t], VARIANCE_FLOOR))
            for i in range(N)
        ])
        D_t = np.diag(vols_t)
        covariances[t] = D_t @ R_t @ D_t

    # Return last few correlations and summary
    last_R = correlations[-1]

    return {
        "univariate_results": univariate_results,
        "dcc_params": {"a": a, "b": b},
        "Q_bar": Q_bar.tolist(),
        "last_R": last_R.tolist(),
        "correlations_last_10": correlations[-10:].tolist() if T >= 10 else correlations.tolist(),
        "covariances_last": covariances[-1].tolist(),
        "n_assets": N,
        "n_obs": T,
    }


def _fit_dcc_mle(z: np.ndarray, Q_bar: np.ndarray) -> dict[str, float]:
    """Estimate DCC parameters (a, b) via MLE on standardized residuals."""
    T, _N = z.shape

    def neg_ll(params: np.ndarray) -> float:
        a, b = params
        if a + b >= 0.9999 or a < 0 or b < 0:
            return 1e10

        Q_t = Q_bar.copy()
        ll = 0.0
        for t in range(1, T):
            z_outer = np.outer(z[t - 1], z[t - 1])
            Q_t = (1 - a - b) * Q_bar + a * z_outer + b * Q_t

            Q_diag = np.diag(Q_t)
            Q_diag = np.maximum(Q_diag, VARIANCE_FLOOR)
            Q_diag_inv_sqrt = 1.0 / np.sqrt(Q_diag)
            R_t = Q_t * np.outer(Q_diag_inv_sqrt, Q_diag_inv_sqrt)
            np.fill_diagonal(R_t, 1.0)

            # DCC log-likelihood contribution
            try:
                sign, logdet = np.linalg.slogdet(R_t)
                if sign <= 0:
                    return 1e10
                z_t = z[t]
                ll += -0.5 * (logdet + z_t @ np.linalg.solve(R_t, z_t) - z_t @ z_t)
            except np.linalg.LinAlgError:
                return 1e10

        return -ll

    x0 = np.array([0.05, 0.90])
    bounds = [(1e-6, 0.3), (0.5, 0.999)]

    result = minimize(neg_ll, x0, method="L-BFGS-B", bounds=bounds,
                      options={"maxiter": 200, "ftol": 1e-8})

    return {"a": float(result.x[0]), "b": float(result.x[1])}
