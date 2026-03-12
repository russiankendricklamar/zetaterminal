"""
Performance Attribution Service.

Implements two attribution methodologies:

1. Brinson-Fachler Attribution (Brinson, Hood & Beebower 1986):
   - Allocation effect:  (w_p - w_b) * (R_b_sector - R_b_total)
   - Selection effect:   w_b * (R_p_sector - R_b_sector)
   - Interaction effect:  (w_p - w_b) * (R_p_sector - R_b_sector)
   - Verification: sum(allocation + selection + interaction) = R_p - R_b

2. Factor Attribution (OLS regression):
   - R_p = alpha + sum(beta_i * F_i) + epsilon
   - Per-factor P&L contribution = beta_i * factor_return_i * portfolio_value
"""

import numpy as np

# -- Brinson-Fachler Attribution -----------------------------------------------


def brinson_fachler_attribution(
    portfolio_weights: list[float],
    benchmark_weights: list[float],
    portfolio_returns: list[float],
    benchmark_returns: list[float],
    sector_names: list[str] | None = None,
) -> dict:
    """
    Brinson-Fachler performance attribution decomposition.

    Decomposes excess return into allocation, selection, and interaction
    effects per sector/asset class.

    Args:
        portfolio_weights: Portfolio weights per sector (sum to 1).
        benchmark_weights: Benchmark weights per sector (sum to 1).
        portfolio_returns: Portfolio returns per sector.
        benchmark_returns: Benchmark returns per sector.
        sector_names: Names for each sector.

    Returns:
        Dict with per-sector breakdown and totals.

    Raises:
        ValueError: If input dimensions are inconsistent or weights don't sum to ~1.
    """
    w_p = np.asarray(portfolio_weights, dtype=float)
    w_b = np.asarray(benchmark_weights, dtype=float)
    r_p = np.asarray(portfolio_returns, dtype=float)
    r_b = np.asarray(benchmark_returns, dtype=float)

    n = len(w_p)
    if not (len(w_b) == n and len(r_p) == n and len(r_b) == n):
        raise ValueError(
            f"All inputs must have the same length. Got weights: {n}, {len(w_b)}, "
            f"returns: {len(r_p)}, {len(r_b)}"
        )
    if n == 0:
        raise ValueError("At least one sector is required")

    # Validate weights sum approximately to 1 (allow small tolerance for shorts)
    for label, w in [("portfolio", w_p), ("benchmark", w_b)]:
        w_sum = float(np.sum(w))
        if abs(w_sum - 1.0) > 0.05:
            raise ValueError(
                f"{label} weights sum to {w_sum:.4f}, expected ~1.0"
            )

    if sector_names is None:
        sector_names = [f"Sector_{i + 1}" for i in range(n)]
    if len(sector_names) != n:
        raise ValueError(
            f"Expected {n} sector names, got {len(sector_names)}"
        )

    # Total benchmark return
    r_b_total = float(np.sum(w_b * r_b))
    # Total portfolio return
    r_p_total = float(np.sum(w_p * r_p))
    excess_return = r_p_total - r_b_total

    # Brinson-Fachler decomposition per sector
    allocation = (w_p - w_b) * (r_b - r_b_total)
    selection = w_b * (r_p - r_b)
    interaction = (w_p - w_b) * (r_p - r_b)

    total_allocation = float(np.sum(allocation))
    total_selection = float(np.sum(selection))
    total_interaction = float(np.sum(interaction))

    # Verification: allocation + selection + interaction = excess return
    decomposition_total = total_allocation + total_selection + total_interaction
    verification_error = abs(decomposition_total - excess_return)

    sectors = []
    for i in range(n):
        sectors.append({
            "name": sector_names[i],
            "portfolio_weight": float(w_p[i]),
            "benchmark_weight": float(w_b[i]),
            "portfolio_return": float(r_p[i]),
            "benchmark_return": float(r_b[i]),
            "allocation_effect": float(allocation[i]),
            "selection_effect": float(selection[i]),
            "interaction_effect": float(interaction[i]),
            "total_effect": float(allocation[i] + selection[i] + interaction[i]),
        })

    return {
        "sectors": sectors,
        "totals": {
            "allocation": total_allocation,
            "selection": total_selection,
            "interaction": total_interaction,
            "excess_return": excess_return,
            "decomposition_total": decomposition_total,
            "verification_error": verification_error,
        },
        "portfolio_return": r_p_total,
        "benchmark_return": r_b_total,
        "n_sectors": n,
    }


# -- Factor Attribution --------------------------------------------------------


def factor_attribution(
    portfolio_returns: list[float],
    factor_returns: list[list[float]],
    factor_names: list[str] | None = None,
    portfolio_value: float = 1_000_000.0,
) -> dict:
    """
    Factor-based P&L attribution using OLS regression.

    R_p = alpha + sum(beta_i * F_i) + epsilon

    Args:
        portfolio_returns: Time series of portfolio returns (T observations).
        factor_returns: Matrix of factor returns T x K.
        factor_names: Names for each factor.
        portfolio_value: Portfolio notional value for P&L conversion.

    Returns:
        Dict with factor decomposition, betas, alpha, R-squared, residuals.

    Raises:
        ValueError: If dimensions are inconsistent or insufficient observations.
    """
    r_p = np.asarray(portfolio_returns, dtype=float)
    f_mat = np.asarray(factor_returns, dtype=float)

    if r_p.ndim != 1:
        raise ValueError("portfolio_returns must be a 1D array")
    if f_mat.ndim == 1:
        f_mat = f_mat[:, np.newaxis]
    if f_mat.ndim != 2:
        raise ValueError("factor_returns must be a 2D array (T x K)")

    t_obs = len(r_p)
    k_factors = f_mat.shape[1]

    if f_mat.shape[0] != t_obs:
        raise ValueError(
            f"portfolio_returns has {t_obs} observations but "
            f"factor_returns has {f_mat.shape[0]}"
        )
    if t_obs < k_factors + 2:
        raise ValueError(
            f"Insufficient observations: T={t_obs} for K={k_factors} factors "
            f"(need at least K+2={k_factors + 2})"
        )
    if portfolio_value <= 0:
        raise ValueError("portfolio_value must be positive")

    if factor_names is None:
        factor_names = [f"Factor_{i + 1}" for i in range(k_factors)]
    if len(factor_names) != k_factors:
        raise ValueError(
            f"Expected {k_factors} factor names, got {len(factor_names)}"
        )

    # OLS: R_p = alpha + beta' * F + epsilon
    x_mat = np.column_stack([np.ones(t_obs), f_mat])  # T x (K+1)
    coeffs, _residuals_arr, _rank, _sv = np.linalg.lstsq(x_mat, r_p, rcond=None)

    alpha = float(coeffs[0])
    betas = coeffs[1:].tolist()

    # Fitted values and residuals
    fitted = x_mat @ coeffs
    epsilon = r_p - fitted

    # R-squared
    ss_res = float(np.sum(epsilon ** 2))
    ss_tot = float(np.sum((r_p - r_p.mean()) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    # Residual standard deviation
    dof = max(t_obs - k_factors - 1, 1)
    residual_std = float(np.sqrt(ss_res / dof))

    # Per-factor P&L contribution
    # Contribution_i = beta_i * mean(F_i) * portfolio_value
    factor_means = f_mat.mean(axis=0)
    total_portfolio_return = float(r_p.sum())

    factors_result = []
    total_factor_pnl = 0.0
    for i in range(k_factors):
        beta_i = float(coeffs[i + 1])
        mean_return_i = float(factor_means[i])
        # Cumulative contribution over the period
        cumulative_contribution = float(beta_i * np.sum(f_mat[:, i]))
        pnl_contribution = cumulative_contribution * portfolio_value

        # Per-period contribution for time series
        period_contributions = (beta_i * f_mat[:, i]).tolist()

        factors_result.append({
            "name": factor_names[i],
            "beta": beta_i,
            "mean_return": mean_return_i,
            "cumulative_contribution": cumulative_contribution,
            "pnl_contribution": pnl_contribution,
            "period_contributions": period_contributions,
            "factor_volatility": float(f_mat[:, i].std(ddof=1)),
        })
        total_factor_pnl += pnl_contribution

    # Alpha P&L
    alpha_cumulative = alpha * t_obs
    alpha_pnl = alpha_cumulative * portfolio_value

    # Residual (unexplained) P&L
    residual_cumulative = float(np.sum(epsilon))
    residual_pnl = residual_cumulative * portfolio_value

    return {
        "factors": factors_result,
        "alpha": alpha,
        "alpha_annualized": alpha * 252,  # assuming daily data
        "alpha_pnl": alpha_pnl,
        "r_squared": r_squared,
        "adjusted_r_squared": 1.0 - (1.0 - r_squared) * (t_obs - 1) / dof,
        "residual_std": residual_std,
        "residual_pnl": residual_pnl,
        "total_factor_pnl": total_factor_pnl,
        "total_pnl": (total_portfolio_return * portfolio_value),
        "explained_pnl": total_factor_pnl + alpha_pnl,
        "unexplained_pnl": residual_pnl,
        "n_observations": t_obs,
        "n_factors": k_factors,
        "portfolio_value": portfolio_value,
        "betas": betas,
        "factor_names": factor_names,
    }
