"""
Univariate GARCH models: GARCH(1,1), GJR-GARCH, EGARCH, EWMA.

Each model supports two modes:
- params=None -> MLE fitting via L-BFGS-B
- params=dict  -> forward pass only (skip fitting)

All return log_likelihood for AIC/BIC comparison.
"""
from typing import Any

import numpy as np
from scipy.optimize import minimize

VARIANCE_FLOOR = 1e-12


def garch_11(
    returns: np.ndarray,
    params: dict[str, float] | None = None,
    initial_variance: float | None = None,
) -> dict[str, Any]:
    """Standard GARCH(1,1): sigma_t^2 = omega + alpha * r_{t-1}^2 + beta * sigma_{t-1}^2."""
    if params is None:
        fitted = _fit_mle(returns, "garch_11")
        return _forward_garch_11(returns, fitted, initial_variance)
    return _forward_garch_11(returns, params, initial_variance)


def gjr_garch(
    returns: np.ndarray,
    params: dict[str, float] | None = None,
    initial_variance: float | None = None,
) -> dict[str, Any]:
    """GJR-GARCH: sigma_t^2 = omega + alpha * r_{t-1}^2 + gamma * I(r<0) * r_{t-1}^2 + beta * sigma_{t-1}^2."""
    if params is None:
        fitted = _fit_mle(returns, "gjr_garch")
        return _forward_gjr(returns, fitted, initial_variance)
    return _forward_gjr(returns, params, initial_variance)


def egarch(
    returns: np.ndarray,
    params: dict[str, float] | None = None,
    initial_variance: float | None = None,
) -> dict[str, Any]:
    """EGARCH: log(sigma_t^2) = omega + alpha * (|z_{t-1}| - E|z|) + gamma * z_{t-1} + beta * log(sigma_{t-1}^2)."""
    if params is None:
        fitted = _fit_mle(returns, "egarch")
        return _forward_egarch(returns, fitted, initial_variance)
    return _forward_egarch(returns, params, initial_variance)


def ewma(
    returns: np.ndarray,
    lam: float = 0.94,
    initial_variance: float | None = None,
) -> dict[str, Any]:
    """EWMA (RiskMetrics): sigma_t^2 = lambda * sigma_{t-1}^2 + (1-lambda) * r_{t-1}^2."""
    n = len(returns)
    if n < 2:
        raise ValueError(f"Need >= 2 observations, got {n}")
    if not 0 < lam < 1:
        raise ValueError(f"lambda must be in (0,1), got {lam}")

    var0 = initial_variance if initial_variance is not None else float(np.var(returns))
    var0 = max(var0, VARIANCE_FLOOR)

    variances = np.zeros(n)
    variances[0] = var0
    for t in range(1, n):
        variances[t] = lam * variances[t - 1] + (1 - lam) * returns[t - 1] ** 2
        variances[t] = max(variances[t], VARIANCE_FLOOR)

    volatilities = np.sqrt(variances)
    residuals = returns / volatilities

    ll = _gaussian_log_likelihood(returns, variances)

    return {
        "model": "ewma",
        "params": {"lambda": lam},
        "variances": variances.tolist(),
        "volatilities": volatilities.tolist(),
        "residuals": residuals.tolist(),
        "log_likelihood": float(ll),
        "n_params": 1,
        "n_obs": n,
    }


# ---------- Forward passes ----------

def _forward_garch_11(
    returns: np.ndarray, params: dict[str, float], initial_variance: float | None
) -> dict[str, Any]:
    omega, alpha, beta = params["omega"], params["alpha"], params["beta"]
    _validate_garch_params(omega, alpha, beta)
    persistence = alpha + beta

    n = len(returns)
    if n < 2:
        raise ValueError(f"Need >= 2 observations, got {n}")

    if initial_variance is not None:
        var0 = max(initial_variance, VARIANCE_FLOOR)
    elif persistence < 1.0:
        var0 = omega / (1.0 - persistence)
    else:
        var0 = float(np.var(returns))
    var0 = max(var0, VARIANCE_FLOOR)

    variances = np.zeros(n)
    variances[0] = var0
    for t in range(1, n):
        variances[t] = omega + alpha * returns[t - 1] ** 2 + beta * variances[t - 1]
        variances[t] = max(variances[t], VARIANCE_FLOOR)

    volatilities = np.sqrt(variances)
    residuals = returns / volatilities
    ll = _gaussian_log_likelihood(returns, variances)

    long_run_var = omega / (1.0 - persistence) if persistence < 1.0 else None

    return {
        "model": "garch_11",
        "params": {"omega": omega, "alpha": alpha, "beta": beta},
        "variances": variances.tolist(),
        "volatilities": volatilities.tolist(),
        "residuals": residuals.tolist(),
        "log_likelihood": float(ll),
        "persistence": float(persistence),
        "long_run_variance": float(long_run_var) if long_run_var is not None else None,
        "n_params": 3,
        "n_obs": n,
    }


def _forward_gjr(
    returns: np.ndarray, params: dict[str, float], initial_variance: float | None
) -> dict[str, Any]:
    omega = params["omega"]
    alpha = params["alpha"]
    beta = params["beta"]
    gamma = params["gamma"]

    n = len(returns)
    if n < 2:
        raise ValueError(f"Need >= 2 observations, got {n}")

    persistence = alpha + beta + gamma / 2.0
    if initial_variance is not None:
        var0 = max(initial_variance, VARIANCE_FLOOR)
    elif persistence < 1.0:
        var0 = omega / (1.0 - persistence)
    else:
        var0 = float(np.var(returns))
    var0 = max(var0, VARIANCE_FLOOR)

    variances = np.zeros(n)
    variances[0] = var0
    for t in range(1, n):
        r2 = returns[t - 1] ** 2
        leverage = float(returns[t - 1] < 0) * r2
        variances[t] = omega + alpha * r2 + gamma * leverage + beta * variances[t - 1]
        variances[t] = max(variances[t], VARIANCE_FLOOR)

    volatilities = np.sqrt(variances)
    residuals = returns / volatilities
    ll = _gaussian_log_likelihood(returns, variances)

    long_run_var = omega / (1.0 - persistence) if persistence < 1.0 else None

    return {
        "model": "gjr_garch",
        "params": {"omega": omega, "alpha": alpha, "beta": beta, "gamma": gamma},
        "variances": variances.tolist(),
        "volatilities": volatilities.tolist(),
        "residuals": residuals.tolist(),
        "log_likelihood": float(ll),
        "persistence": float(persistence),
        "long_run_variance": float(long_run_var) if long_run_var is not None else None,
        "n_params": 4,
        "n_obs": n,
    }


def _forward_egarch(
    returns: np.ndarray, params: dict[str, float], initial_variance: float | None
) -> dict[str, Any]:
    omega = params["omega"]
    alpha = params["alpha"]
    beta = params["beta"]
    gamma = params["gamma"]

    n = len(returns)
    if n < 2:
        raise ValueError(f"Need >= 2 observations, got {n}")

    expected_abs_z = np.sqrt(2.0 / np.pi)

    if initial_variance is not None:
        log_var0 = np.log(max(initial_variance, VARIANCE_FLOOR))
    elif abs(beta) < 1.0:
        log_var0 = omega / (1.0 - beta)
    else:
        log_var0 = np.log(max(float(np.var(returns)), VARIANCE_FLOOR))

    log_variances = np.zeros(n)
    log_variances[0] = np.clip(log_var0, -50, 50)

    for t in range(1, n):
        vt_prev = np.exp(log_variances[t - 1])
        z = returns[t - 1] / np.sqrt(max(vt_prev, VARIANCE_FLOOR))
        log_variances[t] = np.clip(
            omega
            + alpha * (abs(z) - expected_abs_z)
            + gamma * z
            + beta * log_variances[t - 1],
            -50, 50,
        )

    variances = np.exp(log_variances)
    variances = np.maximum(variances, VARIANCE_FLOOR)
    volatilities = np.sqrt(variances)
    residuals = returns / volatilities
    ll = _gaussian_log_likelihood(returns, variances)

    return {
        "model": "egarch",
        "params": {"omega": omega, "alpha": alpha, "beta": beta, "gamma": gamma},
        "variances": variances.tolist(),
        "volatilities": volatilities.tolist(),
        "residuals": residuals.tolist(),
        "log_likelihood": float(ll),
        "persistence": float(abs(beta)),
        "long_run_variance": float(np.exp(omega / (1.0 - beta))) if abs(beta) < 1.0 else None,
        "n_params": 4,
        "n_obs": n,
    }


# ---------- MLE fitting ----------

def _fit_mle(returns: np.ndarray, model: str) -> dict[str, float]:
    """Fit model parameters via Maximum Likelihood Estimation."""
    n = len(returns)
    if n < 10:
        raise ValueError(f"MLE requires >= 10 observations, got {n}")

    sample_var = float(np.var(returns))

    if model == "garch_11":
        x0 = np.array([sample_var * 0.05, 0.08, 0.88])
        bounds = [(1e-8, sample_var * 10), (1e-6, 0.999), (1e-6, 0.999)]

        def obj(p: np.ndarray) -> float:
            if p[1] + p[2] >= 0.9999:
                return 1e10
            return _neg_ll_garch_11(p, returns)

        result = minimize(obj, x0, method="L-BFGS-B", bounds=bounds,
                          options={"maxiter": 500, "ftol": 1e-10})
        return {"omega": float(result.x[0]), "alpha": float(result.x[1]), "beta": float(result.x[2])}

    if model == "gjr_garch":
        x0 = np.array([sample_var * 0.05, 0.05, 0.85, 0.05])
        bounds = [(1e-8, sample_var * 10), (1e-6, 0.5), (1e-6, 0.999), (1e-6, 0.5)]

        def obj(p: np.ndarray) -> float:
            if p[1] + p[2] + p[3] / 2.0 >= 0.9999:
                return 1e10
            return _neg_ll_gjr(p, returns)

        result = minimize(obj, x0, method="L-BFGS-B", bounds=bounds,
                          options={"maxiter": 500, "ftol": 1e-10})
        return {
            "omega": float(result.x[0]), "alpha": float(result.x[1]),
            "beta": float(result.x[2]), "gamma": float(result.x[3]),
        }

    if model == "egarch":
        x0 = np.array([np.log(sample_var) * 0.05, 0.15, 0.95, -0.05])
        bounds = [(-10.0, 10.0), (-2.0, 2.0), (-0.999, 0.999), (-2.0, 2.0)]

        def obj(p: np.ndarray) -> float:
            return _neg_ll_egarch(p, returns)

        result = minimize(obj, x0, method="L-BFGS-B", bounds=bounds,
                          options={"maxiter": 500, "ftol": 1e-10})
        return {
            "omega": float(result.x[0]), "alpha": float(result.x[1]),
            "beta": float(result.x[2]), "gamma": float(result.x[3]),
        }

    raise ValueError(f"Unknown model: {model}")


# ---------- Negative log-likelihood functions ----------

def _neg_ll_garch_11(params_vec: np.ndarray, returns: np.ndarray) -> float:
    omega, alpha, beta = params_vec
    n = len(returns)
    var0 = omega / (1.0 - alpha - beta) if alpha + beta < 1.0 else float(np.var(returns))
    var0 = max(var0, VARIANCE_FLOOR)

    variances = np.zeros(n)
    variances[0] = var0
    for t in range(1, n):
        variances[t] = omega + alpha * returns[t - 1] ** 2 + beta * variances[t - 1]
        variances[t] = max(variances[t], VARIANCE_FLOOR)

    return -_gaussian_log_likelihood(returns, variances)


def _neg_ll_gjr(params_vec: np.ndarray, returns: np.ndarray) -> float:
    omega, alpha, beta, gamma = params_vec
    n = len(returns)
    persistence = alpha + beta + gamma / 2.0
    var0 = omega / (1.0 - persistence) if persistence < 1.0 else float(np.var(returns))
    var0 = max(var0, VARIANCE_FLOOR)

    variances = np.zeros(n)
    variances[0] = var0
    for t in range(1, n):
        r2 = returns[t - 1] ** 2
        leverage = float(returns[t - 1] < 0) * r2
        variances[t] = omega + alpha * r2 + gamma * leverage + beta * variances[t - 1]
        variances[t] = max(variances[t], VARIANCE_FLOOR)

    return -_gaussian_log_likelihood(returns, variances)


def _neg_ll_egarch(params_vec: np.ndarray, returns: np.ndarray) -> float:
    omega, alpha, beta, gamma = params_vec
    n = len(returns)
    expected_abs_z = np.sqrt(2.0 / np.pi)

    log_var0 = omega / (1.0 - beta) if abs(beta) < 1.0 else np.log(max(float(np.var(returns)), VARIANCE_FLOOR))

    log_variances = np.zeros(n)
    log_variances[0] = log_var0
    for t in range(1, n):
        # Clamp log-variance to prevent exp overflow
        log_variances[t - 1] = np.clip(log_variances[t - 1], -50, 50)
        vt_prev = np.exp(log_variances[t - 1])
        z = returns[t - 1] / np.sqrt(max(vt_prev, VARIANCE_FLOOR))
        log_variances[t] = omega + alpha * (abs(z) - expected_abs_z) + gamma * z + beta * log_variances[t - 1]

    log_variances = np.clip(log_variances, -50, 50)
    variances = np.exp(log_variances)
    variances = np.maximum(variances, VARIANCE_FLOOR)
    return -_gaussian_log_likelihood(returns, variances)


# ---------- Helpers ----------

def _gaussian_log_likelihood(returns: np.ndarray, variances: np.ndarray) -> float:
    """Gaussian log-likelihood: sum(-0.5 * (log(2*pi) + log(sigma^2) + r^2/sigma^2))."""
    n = len(returns)
    ll = -0.5 * n * np.log(2 * np.pi) - 0.5 * np.sum(np.log(variances) + returns ** 2 / variances)
    return float(ll)


def _validate_garch_params(omega: float, alpha: float, beta: float) -> None:
    if omega <= 0:
        raise ValueError(f"omega must be > 0, got {omega}")
    if alpha < 0:
        raise ValueError(f"alpha must be >= 0, got {alpha}")
    if beta < 0:
        raise ValueError(f"beta must be >= 0, got {beta}")
    if alpha + beta >= 1.0:
        raise ValueError(
            f"Stationarity requires alpha + beta < 1, got {alpha} + {beta} = {alpha + beta}"
        )
