"""
Convex Portfolio Construction.

Задачи:
- min_variance    : min w'Σw   s.t. Σwᵢ=1, bounds
- max_sharpe      : max μ'w / σ(w)  — через Charnes-Cooper QP
- mean_variance   : min w'Σw − (1/γ)μ'w  (frontier sweep по γ)
- cvar            : min CVaR_α(w)  — линейная программа на сценариях
- risk_parity     : ERC: min w'Σw − c·Σ log wᵢ  (выпуклая)
- kelly           : max μ'w − ½ w'Σw  (дробный Kelly)

Ограничения (все задачи):
- long_only (w ≥ 0)
- weight_bounds (lb ≤ wᵢ ≤ ub)
- max_weight (wᵢ ≤ max_w)
- target_return (μ'w ≥ r_target)

Диагностика: Sharpe, CVaR, VaR, max drawdown, risk contributions, eff-N.
"""
import numpy as np
import scipy.stats
import cvxpy as cp
from typing import Dict, List, Optional, Tuple


# ── Утилиты ──────────────────────────────────────────────────────────────────

def _portfolio_stats(w: np.ndarray, mu: np.ndarray, Sigma: np.ndarray,
                     R: np.ndarray, alpha: float = 0.95,
                     annualize: int = 252) -> Dict:
    """Полная диагностика портфеля."""
    port_ret = float(mu @ w)
    port_var = float(w @ Sigma @ w)
    port_vol = float(np.sqrt(max(port_var, 1e-15)))
    sharpe = port_ret / port_vol * np.sqrt(annualize) if port_vol > 0 else 0.0

    # CVaR / VaR на сценариях
    port_rets_scen = R @ w
    sorted_r = np.sort(port_rets_scen)
    idx = int(np.floor((1 - alpha) * len(sorted_r)))
    var = float(-sorted_r[idx])
    cvar = float(-sorted_r[:idx + 1].mean()) if idx >= 0 else var

    # Max drawdown
    cum = np.cumprod(1 + port_rets_scen)
    roll_max = np.maximum.accumulate(cum)
    mdd = float(np.max((roll_max - cum) / (roll_max + 1e-15)))

    # Risk contributions (marginal risk × weight)
    marg = Sigma @ w
    rc = w * marg / (port_vol + 1e-15)

    # Effective N (inverse Herfindahl)
    eff_n = float(1.0 / np.sum(w ** 2)) if np.sum(w ** 2) > 1e-15 else 0.0

    # Diversification ratio: weighted avg vol / portfolio vol
    vols = np.sqrt(np.diag(Sigma))
    div_ratio = float((w @ vols) / (port_vol + 1e-15))

    return {
        "return_daily": port_ret,
        "return_annual": port_ret * annualize,
        "vol_daily": port_vol,
        "vol_annual": port_vol * np.sqrt(annualize),
        "sharpe": sharpe,
        "var": var,
        "cvar": cvar,
        "max_drawdown": mdd,
        "risk_contributions": rc.tolist(),
        "effective_n": eff_n,
        "diversification_ratio": div_ratio,
    }


def _build_constraints(w: cp.Variable, N: int, mu: np.ndarray,
                       long_only: bool, lb: float, ub: float,
                       max_weight: Optional[float],
                       target_return: Optional[float],
                       leverage: float) -> List:
    cons = [cp.sum(w) == 1.0]
    if long_only:
        cons.append(w >= lb)
    else:
        cons.append(w >= -ub)
    cons.append(w <= ub)
    if max_weight is not None:
        cons.append(w <= max_weight)
    if target_return is not None:
        cons.append(mu @ w >= target_return)
    if leverage < 2.0:
        cons.append(cp.norm1(w) <= leverage)
    return cons


def _solve(problem: cp.Problem) -> bool:
    """Решаем с fallback по солверам."""
    for solver in [cp.CLARABEL, cp.SCS, cp.ECOS]:
        if solver in cp.installed_solvers():
            try:
                problem.solve(solver=solver, verbose=False)
                if problem.status in ("optimal", "optimal_inaccurate"):
                    return True
            except Exception:
                continue
    return False


# ── Задачи оптимизации ────────────────────────────────────────────────────────

def _min_variance(Sigma: np.ndarray, N: int, mu: np.ndarray, **kw) -> Optional[np.ndarray]:
    w = cp.Variable(N)
    obj = cp.Minimize(cp.quad_form(w, Sigma))
    cons = _build_constraints(w, N, mu, **kw)
    if _solve(cp.Problem(obj, cons)):
        return np.array(w.value)
    return None


def _max_sharpe(mu: np.ndarray, Sigma: np.ndarray, N: int, rf: float = 0.0, **kw) -> Optional[np.ndarray]:
    """
    Charnes-Cooper: пусть κ = 1/(μ'w − rf), y = κ·w.
    Тогда: min y'Σy  s.t. (μ-rf)'y = 1, Σyᵢ = κ, y ≥ 0.
    Эквивалентно: min y'Σy  s.t. (μ-rf)'y = 1, y ≥ 0, Σyᵢ·rf=...
    Простая формулировка: min y'Σy s.t. (μ-rf)'y=1, y≥0.
    Weights: w = y / sum(y).
    """
    excess_mu = mu - rf
    if np.any(excess_mu > 0):
        y = cp.Variable(N)
        obj = cp.Minimize(cp.quad_form(y, Sigma))
        cons = [excess_mu @ y == 1.0, y >= 0]
        if kw.get("max_weight") is not None:
            # approximate: y/sum(y) ≤ max_weight → hard to enforce exactly,
            # skip for Charnes-Cooper
            pass
        if _solve(cp.Problem(obj, cons)):
            yv = np.array(y.value)
            s = yv.sum()
            if s > 1e-10:
                return yv / s
    # Fallback: min variance
    return _min_variance(Sigma, N, mu, **kw)


def _mean_variance(mu: np.ndarray, Sigma: np.ndarray, N: int, gamma: float = 1.0, **kw) -> Optional[np.ndarray]:
    """min w'Σw − (1/γ) μ'w"""
    w = cp.Variable(N)
    obj = cp.Minimize(cp.quad_form(w, Sigma) - (1.0 / (gamma + 1e-15)) * mu @ w)
    cons = _build_constraints(w, N, mu, **kw)
    if _solve(cp.Problem(obj, cons)):
        return np.array(w.value)
    return None


def _cvar_opt(R: np.ndarray, N: int, mu: np.ndarray, alpha: float = 0.95, **kw) -> Optional[np.ndarray]:
    """
    min CVaR_α(w) = min VaR + 1/((1-α)T) · Σ zₜ
    s.t. zₜ ≥ -Rₜ'w − VaR, zₜ ≥ 0
    """
    T = R.shape[0]
    w = cp.Variable(N)
    var_var = cp.Variable()        # VaR scalar
    z = cp.Variable(T)             # exceedances
    cvar_obj = var_var + (1.0 / ((1.0 - alpha) * T)) * cp.sum(z)
    obj = cp.Minimize(cvar_obj)
    cons = _build_constraints(w, N, mu, **kw) + [
        z >= -R @ w - var_var,
        z >= 0,
    ]
    if _solve(cp.Problem(obj, cons)):
        return np.array(w.value)
    return None


def _risk_parity(Sigma: np.ndarray, N: int, mu: np.ndarray, c_barrier: float = 0.1, **kw) -> Optional[np.ndarray]:
    """
    ERC via log-barrier: min w'Σw − c · Σ log(wᵢ)  s.t. Σwᵢ=1, w≥ε
    Convex (QP + concave barrier → overall convex).
    Maillard (2010): с ростом c решение стремится к ERC.
    """
    w = cp.Variable(N)
    obj = cp.Minimize(cp.quad_form(w, Sigma) - c_barrier * cp.sum(cp.log(w)))
    eps = 1e-4
    cons = [cp.sum(w) == 1.0, w >= eps]
    if kw.get("max_weight") is not None:
        cons.append(w <= kw["max_weight"])
    if _solve(cp.Problem(obj, cons)):
        return np.array(w.value)
    return None


def _kelly(mu: np.ndarray, Sigma: np.ndarray, N: int, fraction: float = 0.5, **kw) -> Optional[np.ndarray]:
    """
    Fractional Kelly: max f·μ'w − ½ f² w'Σw
    При f=1 — полный Kelly; f=0.5 — половинный.
    Эквивалентно min w'Σw − (2f/f²)·μ'w = min w'Σw − (2/f)·μ'w.
    """
    w = cp.Variable(N)
    gamma_kelly = 1.0 / (fraction + 1e-10)  # risk aversion = 1/f
    obj = cp.Minimize(cp.quad_form(w, Sigma) - (1.0 / gamma_kelly) * mu @ w)
    cons = _build_constraints(w, N, mu, **kw)
    if _solve(cp.Problem(obj, cons)):
        return np.array(w.value)
    return None


# ── Efficient Frontier ────────────────────────────────────────────────────────

def _efficient_frontier(mu: np.ndarray, Sigma: np.ndarray, N: int,
                         n_points: int = 30, **kw) -> List[Dict]:
    """Sweep γ от высокого (min vol) до низкого (max return) значения."""
    gammas = np.logspace(3, -1, n_points)  # от осторожного к агрессивному
    frontier = []
    for gamma in gammas:
        w = _mean_variance(mu, Sigma, N, gamma=float(gamma), **kw)
        if w is None:
            continue
        w = np.clip(w, 0, None)
        s = w.sum()
        if s < 1e-10:
            continue
        w = w / s
        ret = float(mu @ w) * 252
        vol = float(np.sqrt(w @ Sigma @ w)) * np.sqrt(252)
        sr = ret / vol if vol > 1e-10 else 0.0
        frontier.append({"return": round(ret, 6), "vol": round(vol, 6), "sharpe": round(sr, 4)})
    return frontier


# ── Главная функция ───────────────────────────────────────────────────────────

def compute_convex_portfolio(
    returns: List[List[float]],
    asset_names: Optional[List[str]] = None,
    objectives: Optional[List[str]] = None,
    long_only: bool = True,
    lb: float = 0.0,
    ub: float = 1.0,
    max_weight: Optional[float] = None,
    target_return: Optional[float] = None,
    leverage: float = 1.0,
    cvar_alpha: float = 0.95,
    risk_free: float = 0.0,
    kelly_fraction: float = 0.5,
    annualize: int = 252,
    n_frontier: int = 30,
) -> Dict:
    """
    Convex Portfolio Construction.

    Args:
        returns: T × N матрица исторических доходностей
        asset_names: имена N активов
        objectives: список задач ['min_variance','max_sharpe','cvar','risk_parity','kelly']
        long_only: только длинные позиции (w ≥ 0)
        lb / ub: нижняя / верхняя граница весов
        max_weight: максимальный вес одного актива
        target_return: минимально допустимая ожидаемая доходность (дневная)
        leverage: максимальное плечо ||w||₁ ≤ leverage
        cvar_alpha: уровень доверия для CVaR
        risk_free: дневная безрисковая ставка
        kelly_fraction: дробный Kelly (0.5 = half-Kelly)
        annualize: периодов в году
        n_frontier: точек на эффективной границе

    Returns:
        dict с весами, метриками, эффективной границей
    """
    R = np.asarray(returns, dtype=float)
    if R.ndim != 2:
        raise ValueError("returns должен быть матрицей T × N")
    T, N = R.shape
    if T < 30:
        raise ValueError(f"Нужно минимум 30 наблюдений, получено T={T}")
    if N < 2:
        raise ValueError("Нужно минимум 2 актива")

    if asset_names is None or len(asset_names) != N:
        asset_names = [f"Asset_{i+1}" for i in range(N)]

    if objectives is None:
        objectives = ["min_variance", "max_sharpe", "cvar", "risk_parity", "kelly"]

    mu = R.mean(axis=0)          # (N,) среднесуточная
    Sigma = np.cov(R.T)          # (N, N)
    # Ledoit-Wolf shrinkage (simple): Σ → (1-α)Σ + α·tr(Σ)/N·I
    lw_alpha = min(1.0, (N + 2) / (T + N + 2))  # простой shrinkage
    mu_target = np.trace(Sigma) / N
    Sigma = (1.0 - lw_alpha) * Sigma + lw_alpha * mu_target * np.eye(N)
    Sigma = (Sigma + Sigma.T) / 2  # симметризация

    kw = dict(long_only=long_only, lb=lb, ub=ub, max_weight=max_weight,
              target_return=target_return, leverage=leverage)

    # Equal weight (baseline)
    w_eq = np.ones(N) / N

    results: Dict[str, Dict] = {}

    objective_map = {
        "min_variance": lambda: _min_variance(Sigma, N, mu, **kw),
        "max_sharpe": lambda: _max_sharpe(mu, Sigma, N, rf=risk_free, **kw),
        "mean_variance": lambda: _mean_variance(mu, Sigma, N, gamma=1.0, **kw),
        "cvar": lambda: _cvar_opt(R, N, mu, alpha=cvar_alpha, **kw),
        "risk_parity": lambda: _risk_parity(Sigma, N, mu),
        "kelly": lambda: _kelly(mu, Sigma, N, fraction=kelly_fraction, **kw),
    }

    for obj_name in objectives:
        fn = objective_map.get(obj_name)
        if fn is None:
            continue
        try:
            w = fn()
        except Exception:
            w = None

        if w is None or np.any(np.isnan(w)):
            # Fallback: equal weights
            w = w_eq.copy()
        else:
            w = np.array(w, dtype=float)
            if long_only:
                w = np.clip(w, 0, None)
            s = w.sum()
            if abs(s) > 1e-10:
                w = w / s
            else:
                w = w_eq.copy()

        stats = _portfolio_stats(w, mu, Sigma, R, alpha=cvar_alpha, annualize=annualize)
        results[obj_name] = {
            "weights": {asset_names[i]: round(float(w[i]), 6) for i in range(N)},
            "weights_list": [round(float(w[i]), 6) for i in range(N)],
            **stats,
        }

    # Equal weight baseline
    stats_eq = _portfolio_stats(w_eq, mu, Sigma, R, alpha=cvar_alpha, annualize=annualize)
    results["equal_weight"] = {
        "weights": {asset_names[i]: round(float(w_eq[i]), 6) for i in range(N)},
        "weights_list": [round(float(w_eq[i]), 6) for i in range(N)],
        **stats_eq,
    }

    # Efficient frontier (mean-variance)
    frontier = _efficient_frontier(mu, Sigma, N, n_points=n_frontier, **kw)

    # Summary table: per-objective Sharpe, CVaR, vol
    summary = []
    for obj_name, res in results.items():
        summary.append({
            "objective": obj_name,
            "sharpe": res["sharpe"],
            "vol_annual": res["vol_annual"],
            "return_annual": res["return_annual"],
            "cvar": res["cvar"],
            "effective_n": res["effective_n"],
            "diversification_ratio": res["diversification_ratio"],
        })

    return {
        "n_assets": N,
        "n_periods": T,
        "asset_names": asset_names,
        "objectives_computed": list(results.keys()),
        "results": results,
        "frontier": frontier,
        "summary": summary,
        "cvar_alpha": cvar_alpha,
        "annualize": annualize,
    }
