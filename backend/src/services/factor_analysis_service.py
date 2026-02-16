"""
Сервис для Time-Series и Cross-Sectional факторного анализа.

TS регрессия (Fama-MacBeth шаг 1):
  R_{i,t} = αᵢ + Σ βᵢₖ·Fₖ_t + εᵢ,t  — оценка факторных нагрузок β per asset

CS регрессия (Fama-MacBeth шаг 2):
  Rt_cross = λ₀ + Σ λₖ·βᵢₖ + αᵢ     — оценка факторных премий λ за риск

Дополнительно:
  - GRS тест: H₀: все αᵢ = 0 (Gibbons, Ross & Shanken 1989)
  - Shanken correction для стандартных ошибок λ
  - Декомпозиция R²: систематический vs идиосинкратический риск
"""
import numpy as np
import scipy.stats
from typing import Dict, List, Optional, Tuple


# ── Time-Series регрессия ─────────────────────────────────────────────────────

def _ts_regression_single(r_i: np.ndarray, F: np.ndarray) -> Dict:
    """
    OLS для одного актива: R_{i,t} = αᵢ + β'Fₜ + εᵢ,t
    Returns: alpha, betas, t-stats, p-values, R², residuals
    """
    T, K = F.shape
    X = np.column_stack([np.ones(T), F])   # T × (K+1)
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ (X.T @ r_i)              # [alpha, β₁, ..., βK]

    resid = r_i - X @ b
    sigma2 = float(np.sum(resid ** 2) / (T - K - 1))
    vcov = sigma2 * XtX_inv
    se = np.sqrt(np.maximum(np.diag(vcov), 0.0))
    t_stat = b / (se + 1e-15)
    p_val = 2.0 * (1.0 - scipy.stats.t.cdf(np.abs(t_stat), df=T - K - 1))

    ss_tot = float(np.sum((r_i - r_i.mean()) ** 2))
    ss_res = float(np.sum(resid ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return {
        "alpha": float(b[0]),
        "betas": b[1:].tolist(),
        "se_alpha": float(se[0]),
        "se_betas": se[1:].tolist(),
        "t_alpha": float(t_stat[0]),
        "t_betas": t_stat[1:].tolist(),
        "p_alpha": float(p_val[0]),
        "p_betas": p_val[1:].tolist(),
        "r2": float(r2),
        "sigma2": float(sigma2),
        "residuals": resid.tolist(),
    }


def run_ts_regression(
    returns: np.ndarray,  # T × N
    factors: np.ndarray,  # T × K
    asset_names: List[str],
    factor_names: List[str],
) -> Dict:
    """
    Шаг 1 Fama-MacBeth: time-series регрессия для каждого актива.
    Возвращает матрицу нагрузок β (N × K) и GRS тест.
    """
    T, N = returns.shape
    K = factors.shape[1]

    asset_results = []
    betas = np.zeros((N, K))
    alphas = np.zeros(N)
    residuals = np.zeros((T, N))
    r2_list = []

    for i in range(N):
        res = _ts_regression_single(returns[:, i], factors)
        asset_results.append({
            "asset": asset_names[i],
            **res,
            "betas_named": {factor_names[k]: res["betas"][k] for k in range(K)},
        })
        betas[i] = res["betas"]
        alphas[i] = res["alpha"]
        residuals[:, i] = res["residuals"]
        r2_list.append(res["r2"])

    # ── GRS тест (Gibbons, Ross & Shanken 1989) ───────────────────────────────
    # F_GRS = [(T-N-K)/N] · (1 + μ_F' Σ_F⁻¹ μ_F)⁻¹ · α' Σ_ε⁻¹ α
    # H₀: αᵢ = 0 для всех i → F_GRS ~ F(N, T-N-K)
    mu_F = factors.mean(axis=0)
    Sigma_F = np.cov(factors.T)
    if K == 1:
        Sigma_F = np.array([[Sigma_F]])
    try:
        inv_Sigma_F = np.linalg.inv(Sigma_F)
    except np.linalg.LinAlgError:
        inv_Sigma_F = np.linalg.pinv(Sigma_F)

    Sigma_eps = np.cov(residuals.T)
    try:
        inv_Sigma_eps = np.linalg.inv(Sigma_eps)
    except np.linalg.LinAlgError:
        inv_Sigma_eps = np.linalg.pinv(Sigma_eps)

    sharpe_F_sq = float(mu_F @ inv_Sigma_F @ mu_F)
    alpha_quad = float(alphas @ inv_Sigma_eps @ alphas)
    df1 = N
    df2 = T - N - K
    if df2 > 0:
        grs_stat = (df2 / df1) * (1.0 / (1.0 + sharpe_F_sq)) * alpha_quad
        grs_pval = float(1.0 - scipy.stats.f.cdf(grs_stat, df1, df2))
    else:
        grs_stat, grs_pval = 0.0, 1.0

    # Декомпозиция дисперсии: систематический vs идиосинкратический
    sys_var = []
    idio_var = []
    for i in range(N):
        total_var = float(np.var(returns[:, i], ddof=1))
        idio = float(np.var(residuals[:, i], ddof=1))
        sys = max(total_var - idio, 0.0)
        sys_var.append(sys / total_var if total_var > 0 else 0.0)
        idio_var.append(idio / total_var if total_var > 0 else 0.0)

    return {
        "assets": asset_results,
        "beta_matrix": betas.tolist(),  # N × K
        "alphas": alphas.tolist(),
        "mean_r2": float(np.mean(r2_list)),
        "r2_list": r2_list,
        "grs": {
            "stat": float(grs_stat),
            "p_value": float(grs_pval),
            "df1": int(df1),
            "df2": int(df2),
            "rejects_H0": bool(grs_pval < 0.05),
        },
        "systematic_share": sys_var,
        "idiosyncratic_share": idio_var,
    }


# ── Cross-Sectional регрессия ─────────────────────────────────────────────────

def run_cs_regression(
    returns: np.ndarray,   # T × N
    betas: np.ndarray,     # N × K (из TS шага)
    factor_names: List[str],
    asset_names: List[str],
) -> Dict:
    """
    Шаг 2 Fama-MacBeth: для каждого t регрессируем Rₜ на β → λₜ.
    Итоговые λ = mean(λₜ), SE по Fama-MacBeth с Shanken correction.

    CS: Rᵢ,ₜ = λ₀,ₜ + Σₖ βᵢₖ·λₖ,ₜ + αᵢ,ₜ
    """
    T, N = returns.shape
    K = betas.shape[1]
    B = np.column_stack([np.ones(N), betas])  # N × (K+1)  [intercept, β]

    # Для каждого t: OLS λₜ = (B'B)⁻¹B' Rₜ
    BtB_inv = np.linalg.pinv(B.T @ B)
    lambdas_t = np.zeros((T, K + 1))  # T × (K+1): [λ₀, λ₁, ..., λK]
    pricing_errors_t = np.zeros((T, N))

    for t in range(T):
        lam = BtB_inv @ (B.T @ returns[t])
        lambdas_t[t] = lam
        pricing_errors_t[t] = returns[t] - B @ lam

    # Fama-MacBeth: λ_bar = mean(λₜ), SE = std(λₜ)/sqrt(T)
    lam_mean = lambdas_t.mean(axis=0)
    lam_std = lambdas_t.std(axis=0, ddof=1)
    se_fm = lam_std / np.sqrt(T)

    # Shanken correction (1992): умножает SE² на (1 + SR_F²)
    mu_F = betas.mean(axis=0)                # аппроксимация μ_F через β
    Sigma_F = np.cov(betas.T) if K > 1 else np.array([[np.var(betas[:, 0], ddof=1)]])
    try:
        inv_SF = np.linalg.inv(Sigma_F)
    except np.linalg.LinAlgError:
        inv_SF = np.linalg.pinv(Sigma_F)

    c_shanken = 1.0 + float(lam_mean[1:] @ inv_SF @ lam_mean[1:])
    se_shanken = se_fm.copy()
    se_shanken[1:] *= np.sqrt(c_shanken)   # поправка только для λ₁..λK

    t_stat = lam_mean / (se_shanken + 1e-15)
    p_val = 2.0 * (1.0 - scipy.stats.t.cdf(np.abs(t_stat), df=T - 1))

    names = ["λ₀ (intercept)"] + [f"λ_{factor_names[k]}" for k in range(K)]

    # Ценовые ошибки: mean pricing error per asset
    mean_pe = pricing_errors_t.mean(axis=0)
    r2_cs = float(1.0 - np.var(mean_pe, ddof=1) / np.var(returns.mean(axis=0), ddof=1))

    return {
        "risk_premia": [
            {
                "name": names[k],
                "lambda_mean": float(lam_mean[k]),
                "se_fm": float(se_fm[k]),
                "se_shanken": float(se_shanken[k]),
                "t_stat": float(t_stat[k]),
                "p_value": float(p_val[k]),
                "significant": bool(p_val[k] < 0.05),
            }
            for k in range(K + 1)
        ],
        "pricing_errors": mean_pe.tolist(),
        "pricing_errors_assets": asset_names,
        "r2_cs": float(max(r2_cs, 0.0)),
        "shanken_c": float(c_shanken),
        "lambdas_t": lambdas_t.tolist(),   # T × (K+1) для графика
    }


# ── Главная функция ───────────────────────────────────────────────────────────

def run_factor_analysis(
    returns: List[List[float]],
    factors: List[List[float]],
    asset_names: Optional[List[str]] = None,
    factor_names: Optional[List[str]] = None,
) -> Dict:
    """
    Полный Fama-MacBeth двухшаговый факторный анализ.

    Args:
        returns: матрица доходностей T × N (строки=время, столбцы=активы)
        factors: матрица факторов T × K
        asset_names: названия активов (N)
        factor_names: названия факторов (K)

    Returns:
        dict с результатами TS, CS регрессий и сравнительной статистикой
    """
    R = np.asarray(returns, dtype=float)
    F = np.asarray(factors, dtype=float)

    if R.ndim == 1:
        R = R[:, None]
    if F.ndim == 1:
        F = F[:, None]

    T, N = R.shape
    K = F.shape[1]

    if F.shape[0] != T:
        raise ValueError(f"returns и factors должны иметь одинаковое T: {T} vs {F.shape[0]}")
    if T < N + K + 5:
        raise ValueError(f"Недостаточно наблюдений T={T} для N={N} активов и K={K} факторов")

    if asset_names is None:
        asset_names = [f"Asset_{i+1}" for i in range(N)]
    if factor_names is None:
        factor_names = [f"F{k+1}" for k in range(K)]

    if len(asset_names) != N:
        raise ValueError(f"Ожидается {N} названий активов, получено {len(asset_names)}")
    if len(factor_names) != K:
        raise ValueError(f"Ожидается {K} названий факторов, получено {len(factor_names)}")

    # Шаг 1: TS регрессии → β
    ts_result = run_ts_regression(R, F, asset_names, factor_names)
    betas = np.array(ts_result["beta_matrix"])

    # Шаг 2: CS регрессии → λ
    cs_result = run_cs_regression(R, betas, factor_names, asset_names)

    # Сводная статистика факторов
    factor_stats = []
    for k in range(K):
        f_k = F[:, k]
        factor_stats.append({
            "name": factor_names[k],
            "mean": float(f_k.mean()),
            "vol": float(f_k.std(ddof=1)),
            "sharpe": float(f_k.mean() / (f_k.std(ddof=1) + 1e-15)),
        })

    return {
        "ts": ts_result,
        "cs": cs_result,
        "factor_stats": factor_stats,
        "n_assets": N,
        "n_factors": K,
        "n_periods": T,
        "asset_names": asset_names,
        "factor_names": factor_names,
    }
