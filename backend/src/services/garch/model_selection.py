"""
Model selection and diagnostic tests for GARCH models.

- AIC/BIC comparison across fitted models
- Ljung-Box test for residual autocorrelation
- ARCH-LM test for remaining ARCH effects
"""
from typing import Any

import numpy as np
from scipy.stats import chi2


def compare_models(model_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Rank models by AIC and BIC. Lower is better."""
    rankings = []
    for result in model_results:
        ll = result["log_likelihood"]
        k = result["n_params"]
        n = result["n_obs"]

        aic = -2 * ll + 2 * k
        bic = -2 * ll + k * np.log(n)

        rankings.append({
            "model": result["model"],
            "log_likelihood": ll,
            "n_params": k,
            "aic": float(aic),
            "bic": float(bic),
            "persistence": result.get("persistence"),
        })

    rankings.sort(key=lambda x: x["aic"])

    return {
        "rankings": rankings,
        "best_aic": rankings[0]["model"],
        "best_bic": min(rankings, key=lambda x: x["bic"])["model"],
    }


def ljung_box_test(residuals: list[float], lags: int = 10) -> dict[str, Any]:
    """
    Ljung-Box Q test for autocorrelation in standardized residuals.

    H0: no autocorrelation up to lag k.
    Reject if p-value < 0.05 (residuals still have structure).
    """
    r = np.array(residuals)
    n = len(r)
    if n < lags + 1:
        raise ValueError(f"Need > {lags} observations for Ljung-Box test")

    r_demeaned = r - np.mean(r)
    c0 = float(np.sum(r_demeaned ** 2))
    if c0 == 0:
        return {"statistic": 0.0, "p_value": 1.0, "lags": lags, "reject_h0": False}

    acf_vals = []
    for k in range(1, lags + 1):
        ck = float(np.sum(r_demeaned[k:] * r_demeaned[:-k]))
        acf_vals.append(ck / c0)

    q_stat = n * (n + 2) * sum(acf_vals[k] ** 2 / (n - k - 1) for k in range(lags))
    p_value = 1.0 - chi2.cdf(q_stat, df=lags)

    return {
        "statistic": float(q_stat),
        "p_value": float(p_value),
        "lags": lags,
        "reject_h0": p_value < 0.05,
        "acf": acf_vals,
    }


def arch_lm_test(residuals: list[float], lags: int = 5) -> dict[str, Any]:
    """
    Engle's ARCH-LM test for remaining ARCH effects in standardized residuals.

    Regresses squared residuals on their lags. High R^2 => remaining ARCH effects.
    H0: no ARCH effects. Reject if p-value < 0.05.
    """
    r = np.array(residuals)
    r2 = r ** 2
    n = len(r2)
    if n < lags + 1:
        raise ValueError(f"Need > {lags} observations for ARCH-LM test")

    # Build regression matrix: r2[t] = c + sum(b_k * r2[t-k])
    y = r2[lags:]
    X = np.column_stack([r2[lags - k - 1: n - k - 1] for k in range(lags)])
    X = np.column_stack([np.ones(len(y)), X])

    # OLS via normal equations
    try:
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        y_hat = X @ beta
        ss_res = float(np.sum((y - y_hat) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    except np.linalg.LinAlgError:
        r_squared = 0.0

    lm_stat = len(y) * r_squared
    p_value = 1.0 - chi2.cdf(lm_stat, df=lags)

    return {
        "statistic": float(lm_stat),
        "p_value": float(p_value),
        "r_squared": float(r_squared),
        "lags": lags,
        "reject_h0": p_value < 0.05,
    }
