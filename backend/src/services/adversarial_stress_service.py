"""
Adversarial Stress Testing Service.

Distributionally Robust подход к стресс-тестированию:
- Worst-case mean return (Ellipsoidal Uncertainty, closed-form)
- Worst-case covariance (Frobenius ball, SDP via cvxpy)
- Monte-Carlo с adversarial параметрами
- EVT tail analysis (Generalized Pareto Distribution)
- Scenario plausibility scoring (Mahalanobis distance)
"""
import numpy as np
import scipy.stats
from typing import Dict, List, Optional
from src.services.hjb_service import simulate_monte_carlo


# ── Worst-Case Mean Return ────────────────────────────────────────────────────

def worst_case_mean(
    mu: np.ndarray,
    cov_matrix: np.ndarray,
    weights: np.ndarray,
    kappa: float,
) -> np.ndarray:
    """
    Worst-case expected return vector under ellipsoidal uncertainty.

    Solves:  min  w'μ*
             s.t. (μ* − μ)'Σ⁻¹(μ* − μ) ≤ κ²

    Closed-form:  μ* = μ − κ · Σw / ‖Σ^{½}w‖
    """
    Sigma_w = cov_matrix @ weights
    norm_sq = weights @ Sigma_w
    if norm_sq < 1e-15:
        return mu.copy()
    norm = np.sqrt(norm_sq)
    return mu - kappa * Sigma_w / norm


# ── Worst-Case Covariance ─────────────────────────────────────────────────────

def worst_case_covariance(
    cov_matrix: np.ndarray,
    weights: np.ndarray,
    epsilon: float,
) -> np.ndarray:
    """
    Worst-case covariance within Frobenius ball around Σ.

    Solves:  max  w'Σ*w
             s.t. ‖Σ* − Σ‖_F ≤ ε,  Σ* ≽ 0

    Closed-form: perturbation along ww' direction.
    Σ* = Σ + ε · ww' / ‖w‖²
    (rank-1 perturbation that maximizes portfolio variance)
    """
    n = len(weights)
    w_norm_sq = weights @ weights
    if w_norm_sq < 1e-15:
        return cov_matrix.copy()

    # Rank-1 perturbation in the direction of ww'
    ww = np.outer(weights, weights)
    ww_norm = np.linalg.norm(ww, 'fro')
    delta = epsilon * ww / ww_norm

    Sigma_star = cov_matrix + delta

    # Ensure positive semi-definite via eigenvalue clipping
    eigvals, eigvecs = np.linalg.eigh(Sigma_star)
    eigvals = np.maximum(eigvals, 1e-8)
    Sigma_star = eigvecs @ np.diag(eigvals) @ eigvecs.T
    Sigma_star = (Sigma_star + Sigma_star.T) / 2

    return Sigma_star


# ── EVT Tail Analysis ─────────────────────────────────────────────────────────

def fit_gpd_tail(
    losses: np.ndarray,
    threshold_quantile: float = 0.90,
) -> Dict:
    """
    Fit Generalized Pareto Distribution to the tail of losses.

    Returns shape (xi), scale (beta), threshold, and extreme quantiles.
    """
    threshold = float(np.quantile(losses, threshold_quantile))
    exceedances = losses[losses > threshold] - threshold

    if len(exceedances) < 10:
        return {
            "xi": 0.0,
            "beta": float(np.std(losses)),
            "threshold": threshold,
            "n_exceedances": int(len(exceedances)),
            "var_999": float(np.quantile(losses, 0.999)) if len(losses) > 1000 else float(np.max(losses)),
            "var_9999": float(np.max(losses)),
            "fit_success": False,
        }

    try:
        xi, loc, beta = scipy.stats.genpareto.fit(exceedances, floc=0)
    except Exception:
        return {
            "xi": 0.0,
            "beta": float(np.std(exceedances)),
            "threshold": threshold,
            "n_exceedances": int(len(exceedances)),
            "var_999": float(np.quantile(losses, 0.999)) if len(losses) > 1000 else float(np.max(losses)),
            "var_9999": float(np.max(losses)),
            "fit_success": False,
        }

    n = len(losses)
    n_u = len(exceedances)
    ratio = n_u / n

    def gpd_var(p: float) -> float:
        if abs(xi) < 1e-8:
            return threshold + beta * np.log(ratio / (1 - p))
        return threshold + (beta / xi) * ((ratio / (1 - p)) ** xi - 1)

    return {
        "xi": float(xi),
        "beta": float(beta),
        "threshold": float(threshold),
        "n_exceedances": int(n_u),
        "var_999": float(gpd_var(0.999)),
        "var_9999": float(gpd_var(0.9999)),
        "fit_success": True,
    }


# ── Plausibility Scoring ──────────────────────────────────────────────────────

def plausibility_score(
    mu_base: np.ndarray,
    mu_adv: np.ndarray,
    cov_base: np.ndarray,
    cov_adv: np.ndarray,
) -> Dict:
    """
    Measures how far adversarial parameters deviate from base.

    - Mahalanobis distance for mean shift
    - Frobenius distance for covariance shift
    - Combined plausibility score ∈ [0, 1]
    """
    # Mahalanobis distance of mean shift
    delta_mu = mu_adv - mu_base
    try:
        inv_cov = np.linalg.inv(cov_base)
        mahal = float(np.sqrt(delta_mu @ inv_cov @ delta_mu))
    except np.linalg.LinAlgError:
        mahal = float(np.linalg.norm(delta_mu))

    # Frobenius distance of covariance shift
    frob = float(np.linalg.norm(cov_adv - cov_base, 'fro'))
    frob_relative = frob / (np.linalg.norm(cov_base, 'fro') + 1e-10)

    # Combined score: higher = less plausible (0 = identical, 1 = extreme)
    # Sigmoid-like mapping
    raw = 0.5 * mahal + 0.5 * frob_relative
    combined = float(1 - np.exp(-raw))

    return {
        "mahalanobis_distance": mahal,
        "frobenius_distance": frob,
        "frobenius_relative": float(frob_relative),
        "combined_score": combined,
    }


# ── Main Entry Point ──────────────────────────────────────────────────────────

def run_adversarial_stress(
    cov_matrix: List[List[float]],
    mu: List[float],
    weights: List[float],
    kappa: float = 1.0,
    epsilon: float = 0.1,
    n_paths: int = 2000,
    risk_free_rate: float = 0.0,
    initial_capital: float = 1_000_000,
    gamma: float = 3.0,
    asset_names: Optional[List[str]] = None,
    seed: Optional[int] = 42,
) -> Dict:
    """
    Full adversarial stress test pipeline.

    1. Compute worst-case μ* and Σ*
    2. Run MC simulations for base and adversarial scenarios
    3. Fit GPD to adversarial loss tail
    4. Compute plausibility metrics
    """
    Sigma = np.array(cov_matrix, dtype=float)
    mu_arr = np.array(mu, dtype=float)
    w = np.array(weights, dtype=float)
    n = len(mu_arr)

    if asset_names is None:
        asset_names = [f"Asset_{i+1}" for i in range(n)]

    # Normalize weights
    w_sum = np.sum(np.abs(w))
    if w_sum > 1e-10:
        w = w / w_sum

    # ── 1. Worst-case parameters ──
    mu_star = worst_case_mean(mu_arr, Sigma, w, kappa)
    Sigma_star = worst_case_covariance(Sigma, w, epsilon)

    # Per-asset mean shift
    mu_shift = mu_star - mu_arr

    # ── 2. Base MC simulation ──
    base_mc = simulate_monte_carlo(
        mu=mu_arr,
        cov_matrix=Sigma,
        weights=w,
        initial_capital=initial_capital,
        horizon_years=1.0,
        n_paths=n_paths,
        n_steps=252,
        random_seed=seed,
        risk_free_rate=risk_free_rate,
    )

    # ── 3. Adversarial MC simulation ──
    adv_mc = simulate_monte_carlo(
        mu=mu_star,
        cov_matrix=Sigma_star,
        weights=w,
        initial_capital=initial_capital,
        horizon_years=1.0,
        n_paths=n_paths,
        n_steps=252,
        random_seed=seed,
        risk_free_rate=risk_free_rate,
    )

    # ── 4. EVT on adversarial losses ──
    adv_finals = np.array([p[-1] for p in adv_mc["paths"]])
    # Extend with full simulation paths for EVT
    all_adv_finals = np.zeros(n_paths)
    all_adv_finals[:len(adv_finals)] = adv_finals
    # Fill rest from stats if paths are truncated
    if len(adv_finals) < n_paths:
        mean_f = adv_mc["stats"]["mean_final"]
        std_f = adv_mc["stats"]["std_final"]
        remaining = n_paths - len(adv_finals)
        rng = np.random.RandomState(seed)
        all_adv_finals[len(adv_finals):] = rng.normal(mean_f, std_f, remaining)

    losses = initial_capital - all_adv_finals
    losses = np.maximum(losses, 0)  # Only positive losses
    evt_result = fit_gpd_tail(losses, threshold_quantile=0.90)

    # ── 5. Plausibility ──
    plaus = plausibility_score(mu_arr, mu_star, Sigma, Sigma_star)

    # ── 6. Compute portfolio-level stats ──
    base_port_vol = float(np.sqrt(w @ Sigma @ w))
    adv_port_vol = float(np.sqrt(w @ Sigma_star @ w))
    base_port_ret = float(w @ mu_arr)
    adv_port_ret = float(w @ mu_star)
    base_sharpe = (base_port_ret - risk_free_rate) / base_port_vol if base_port_vol > 1e-10 else 0.0
    adv_sharpe = (adv_port_ret - risk_free_rate) / adv_port_vol if adv_port_vol > 1e-10 else 0.0

    # ── 7. Loss distribution histogram ──
    base_finals = np.array([p[-1] for p in base_mc["paths"]])
    base_returns_dist = ((base_finals / initial_capital) - 1).tolist()
    adv_returns_dist = ((all_adv_finals[:len(adv_finals)] / initial_capital) - 1).tolist()

    return {
        "base_scenario": {
            "expected_return": base_port_ret,
            "volatility": base_port_vol,
            "sharpe": float(base_sharpe),
            "var_95": base_mc["stats"]["var_95"],
            "var_99": base_mc["stats"]["var_99"],
            "cvar_95": base_mc["stats"]["cvar_95"],
            "cvar_99": base_mc["stats"]["cvar_99"],
            "max_drawdown": base_mc["stats"]["mean_max_drawdown"],
            "mean_final": base_mc["stats"]["mean_final"],
        },
        "adversarial_scenario": {
            "expected_return": adv_port_ret,
            "volatility": adv_port_vol,
            "sharpe": float(adv_sharpe),
            "var_95": adv_mc["stats"]["var_95"],
            "var_99": adv_mc["stats"]["var_99"],
            "cvar_95": adv_mc["stats"]["cvar_95"],
            "cvar_99": adv_mc["stats"]["cvar_99"],
            "max_drawdown": adv_mc["stats"]["mean_max_drawdown"],
            "mean_final": adv_mc["stats"]["mean_final"],
        },
        "worst_case_mu": mu_star.tolist(),
        "worst_case_cov_diag": np.diag(Sigma_star).tolist(),
        "mu_shift": mu_shift.tolist(),
        "evt_tail": evt_result,
        "plausibility": plaus,
        "mc_base": {
            "median_path": base_mc["median_path"],
            "q05_path": base_mc["q05_path"],
            "q95_path": base_mc["q95_path"],
            "t_grid": base_mc["t_grid"],
        },
        "mc_adversarial": {
            "paths": adv_mc["paths"][:30],
            "median_path": adv_mc["median_path"],
            "q05_path": adv_mc["q05_path"],
            "q95_path": adv_mc["q95_path"],
            "t_grid": adv_mc["t_grid"],
        },
        "return_distributions": {
            "base": base_returns_dist,
            "adversarial": adv_returns_dist,
        },
        "parameters": {
            "kappa": kappa,
            "epsilon": epsilon,
            "n_paths": n_paths,
            "risk_free_rate": risk_free_rate,
            "initial_capital": initial_capital,
            "gamma": gamma,
            "n_assets": n,
        },
        "asset_names": asset_names,
    }
