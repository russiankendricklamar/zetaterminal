"""
Сервис для Probability of Backtest Overfitting (PBO) и Deflated Sharpe Ratio (DSR).

Реализует:
- PBO через Combinatorially Symmetric Cross-Validation (CSCV, Bailey et al. 2014)
- DSR: Deflated Sharpe Ratio с поправкой на число испытаний (López de Prado 2014)
- MinBTL: минимальная длина бэктеста для достоверного SR
- IS vs OOS performance scatter (degradation curve)
- Логит-распределение OOS ранга
"""
import numpy as np
import scipy.stats
import itertools
from typing import Dict, List, Optional, Tuple


# ── Вспомогательные функции ───────────────────────────────────────────────────

def _sharpe_ratio(returns: np.ndarray, annualize: int = 1) -> float:
    """Коэффициент Шарпа (без rf) с опциональной аннуализацией."""
    mu = float(np.mean(returns))
    sigma = float(np.std(returns, ddof=1))
    if sigma < 1e-15:
        return 0.0
    return mu / sigma * np.sqrt(annualize)


def _psr(sr_hat: float, sr_star: float, T: int, skew: float, excess_kurt: float) -> float:
    """
    Probabilistic Sharpe Ratio.
    PSR(SR*) = Φ[(SR̂ − SR*)·√(T−1) / √(1 − γ₁·SR̂ + (γ₂+1)/4·SR̂²)]
    """
    denom_sq = 1.0 - skew * sr_hat + (excess_kurt + 1.0) / 4.0 * sr_hat ** 2
    if denom_sq <= 0 or T <= 1:
        return 0.5
    z = (sr_hat - sr_star) * np.sqrt(T - 1) / np.sqrt(denom_sq)
    return float(scipy.stats.norm.cdf(z))


# ── CSCV алгоритм ─────────────────────────────────────────────────────────────

def _cscv(
    returns_matrix: np.ndarray,  # T × N
    n_splits: int = 16,
    annualize: int = 1,
) -> Dict:
    """
    Combinatorially Symmetric Cross-Validation (Bailey et al. 2014).

    Алгоритм:
    1. Разбить T наблюдений на S равных подмножеств.
    2. Для каждой из C(S, S/2) комбинаций:
       IS = первые S/2 подмножеств, OOS = остальные.
    3. Для каждой комбинации: найти лучшую стратегию по IS SR.
    4. Проверить её OOS ранг → PBO = доля комбинаций, где OOS ранг ≤ N/2.
    """
    T, N = returns_matrix.shape
    S = n_splits
    # Обрезаем T до кратного S
    T_cut = (T // S) * S
    R = returns_matrix[:T_cut]
    chunk_size = T_cut // S

    # Разбиваем на S подмножеств
    chunks = [R[i * chunk_size:(i + 1) * chunk_size] for i in range(S)]

    # Все комбинации C(S, S/2)
    half = S // 2
    all_combos = list(itertools.combinations(range(S), half))

    # Ограничиваем число комбинаций для производительности
    max_combos = 256
    if len(all_combos) > max_combos:
        rng = np.random.default_rng(42)
        idx = rng.choice(len(all_combos), size=max_combos, replace=False)
        all_combos = [all_combos[i] for i in sorted(idx)]

    pbo_logit_values = []
    is_sr_best = []
    oos_sr_best = []
    oos_ranks = []
    is_sr_all_mean = []
    oos_sr_all_mean = []

    for is_indices in all_combos:
        oos_indices = [i for i in range(S) if i not in is_indices]

        is_data = np.vstack([chunks[i] for i in is_indices])   # (half*chunk) × N
        oos_data = np.vstack([chunks[i] for i in oos_indices])  # (half*chunk) × N

        # SR для каждой стратегии
        is_sr = np.array([_sharpe_ratio(is_data[:, n], annualize) for n in range(N)])
        oos_sr = np.array([_sharpe_ratio(oos_data[:, n], annualize) for n in range(N)])

        # Лучшая стратегия по IS
        best_idx = int(np.argmax(is_sr))
        best_oos_sr = float(oos_sr[best_idx])
        best_is_sr = float(is_sr[best_idx])

        # OOS ранг лучшей стратегии (от 1=лучший до N=худший)
        oos_rank = int(N - np.searchsorted(np.sort(oos_sr), best_oos_sr))
        oos_rank = max(1, min(oos_rank, N))

        # Логит OOS ранга (нормализованный на [0,1])
        relative_rank = (oos_rank - 0.5) / N
        logit = float(np.log(relative_rank / (1.0 - relative_rank + 1e-15)))

        pbo_logit_values.append(logit)
        is_sr_best.append(best_is_sr)
        oos_sr_best.append(best_oos_sr)
        oos_ranks.append(oos_rank)
        is_sr_all_mean.append(float(np.mean(is_sr)))
        oos_sr_all_mean.append(float(np.mean(oos_sr)))

    # PBO = доля комбинаций, где OOS ранг ≤ N/2 (лучшая IS стратегия не победила в OOS)
    pbo = float(np.mean([r <= N / 2 for r in oos_ranks]))

    # Логит-распределение
    logit_arr = np.array(pbo_logit_values)

    return {
        "pbo": pbo,
        "n_combinations": len(all_combos),
        "is_sr_best": is_sr_best,
        "oos_sr_best": oos_sr_best,
        "oos_ranks": oos_ranks,
        "logit_values": pbo_logit_values,
        "logit_mean": float(logit_arr.mean()),
        "logit_std": float(logit_arr.std(ddof=1)),
        "is_sr_all_mean": is_sr_all_mean,
        "oos_sr_all_mean": oos_sr_all_mean,
    }


# ── DSR и MinBTL ──────────────────────────────────────────────────────────────

def _compute_dsr_and_minbtl(
    returns_matrix: np.ndarray,  # T × N
    sr_benchmark: float = 0.0,
    annualize: int = 252,
) -> Dict:
    """
    Deflated Sharpe Ratio и Minimum Backtest Length.

    DSR = PSR(SR*) где SR* = E[max SR_n | n = 1..N] с поправкой на ненормальность.
    SR* ≈ (1 − γ_E)·Z(1 − 1/N) + γ_E·Z(1 − 1/(N·e)) + μ_SR + σ_SR·z
    MinBTL: минимальное T, при котором SR̂_max ≥ SR* (DSR > 0).
    """
    T, N = returns_matrix.shape
    euler_gamma = 0.5772156649015329

    # SR за период для каждой стратегии
    sr_list = []
    skew_list = []
    kurt_list = []
    for n in range(N):
        r = returns_matrix[:, n]
        mu, sigma = float(np.mean(r)), float(np.std(r, ddof=1))
        sr_freq = mu / sigma if sigma > 1e-15 else 0.0
        sr_list.append(sr_freq)
        skew_list.append(float(scipy.stats.skew(r)))
        kurt_list.append(float(scipy.stats.kurtosis(r)))  # excess kurtosis

    sr_arr = np.array(sr_list)
    sr_annual = sr_arr * np.sqrt(annualize)

    # Лучший SR
    best_idx = int(np.argmax(sr_arr))
    sr_hat = float(sr_arr[best_idx])
    skew_best = float(skew_list[best_idx])
    kurt_best = float(kurt_list[best_idx])

    # Expected max SR (Bailey et al. 2014, eq. 8)
    # SR* = E[max(SR_n)] ≈ μ_SR + σ_SR·[(1−γ_E)·z₁ + γ_E·z₂]
    mu_sr = float(sr_arr.mean())
    sigma_sr = float(sr_arr.std(ddof=1)) if N > 1 else 0.001

    z1 = float(scipy.stats.norm.ppf(1.0 - 1.0 / N)) if N > 1 else 0.0
    z2 = float(scipy.stats.norm.ppf(1.0 - 1.0 / (N * np.e))) if N > 1 else 0.0
    sr_star_freq = mu_sr + sigma_sr * ((1.0 - euler_gamma) * z1 + euler_gamma * z2)

    # DSR = PSR(SR*)
    dsr = _psr(sr_hat, sr_star_freq, T, skew_best, kurt_best)

    # Minimum Backtest Length (MinBTL)
    # Ищем минимальный T такой, что PSR_T(SR*) > 0.95
    # Из формулы PSR: T_min ≈ (z_{0.95} · sqrt(D) / (SR_hat - SR*))^2 + 1
    denom_sq = 1.0 - skew_best * sr_hat + (kurt_best + 1.0) / 4.0 * sr_hat ** 2
    denom_sq = max(denom_sq, 0.001)

    if abs(sr_hat - sr_star_freq) < 1e-10:
        min_btl = T  # нельзя определить
    else:
        z_95 = scipy.stats.norm.ppf(0.95)
        min_btl = int(np.ceil((z_95 * np.sqrt(denom_sq) / (sr_hat - sr_star_freq)) ** 2 + 1))
        min_btl = max(min_btl, 0)

    # Для каждой стратегии: SR, аннуализированный SR, DSR_индивидуальный
    strategy_stats = []
    for n in range(N):
        sr_n = float(sr_arr[n])
        psr_n = _psr(sr_n, sr_star_freq, T, skew_list[n], kurt_list[n])
        strategy_stats.append({
            "strategy": n + 1,
            "sr_freq": sr_n,
            "sr_annual": float(sr_annual[n]),
            "skewness": skew_list[n],
            "excess_kurtosis": kurt_list[n],
            "psr": psr_n,
        })

    return {
        "best_strategy": best_idx + 1,
        "sr_hat_annual": float(sr_hat * np.sqrt(annualize)),
        "sr_star_annual": float(sr_star_freq * np.sqrt(annualize)),
        "dsr": float(dsr),
        "min_btl": int(max(min_btl, 1)),
        "current_t": int(T),
        "btl_sufficient": bool(T >= min_btl),
        "n_strategies": int(N),
        "strategy_stats": strategy_stats,
    }


# ── Главная функция ───────────────────────────────────────────────────────────

def compute_pbo(
    strategy_returns: List[List[float]],
    n_splits: int = 16,
    annualize: int = 252,
    sr_benchmark: float = 0.0,
) -> Dict:
    """
    Полный анализ переобучения бэктеста: PBO (CSCV) + DSR + MinBTL.

    Args:
        strategy_returns: матрица T × N доходностей стратегий
                         (строки=время, столбцы=стратегии)
        n_splits: число подмножеств S для CSCV (чётное, ≥ 4)
        annualize: периодов в году для аннуализации SR
        sr_benchmark: пороговый SR для PSR (годовой)

    Returns:
        dict с PBO, DSR, MinBTL, IS/OOS scatter, logit histogram
    """
    R = np.asarray(strategy_returns, dtype=float)
    if R.ndim == 1:
        R = R[:, None]

    T, N = R.shape
    if T < 20:
        raise ValueError(f"Нужно минимум 20 наблюдений, получено T={T}")
    if N < 2:
        raise ValueError("Нужно минимум 2 стратегии для CSCV")

    # Округляем n_splits до чётного числа, не превышающего T//4
    n_splits = min(n_splits, T // 4)
    n_splits = max(4, n_splits - (n_splits % 2))

    # ── CSCV ──────────────────────────────────────────────────────────────────
    cscv = _cscv(R, n_splits=n_splits, annualize=1)  # нет аннуализации внутри CSCV

    # ── DSR + MinBTL ──────────────────────────────────────────────────────────
    dsr_result = _compute_dsr_and_minbtl(R, sr_benchmark=sr_benchmark, annualize=annualize)

    # ── Логит-гистограмма ─────────────────────────────────────────────────────
    logit_arr = np.array(cscv["logit_values"])
    hist_bins = 20
    counts, bin_edges = np.histogram(logit_arr, bins=hist_bins)

    # ── Сводная интерпретация ──────────────────────────────────────────────────
    pbo = cscv["pbo"]
    if pbo > 0.75:
        verdict = "Высокая вероятность переобучения"
        verdict_level = "danger"
    elif pbo > 0.5:
        verdict = "Умеренная вероятность переобучения"
        verdict_level = "warning"
    else:
        verdict = "Признаки переобучения слабые"
        verdict_level = "ok"

    return {
        # PBO
        "pbo": float(pbo),
        "verdict": verdict,
        "verdict_level": verdict_level,
        "n_combinations": cscv["n_combinations"],
        "n_splits": int(n_splits),
        # DSR / MinBTL
        "dsr": dsr_result["dsr"],
        "sr_hat_annual": dsr_result["sr_hat_annual"],
        "sr_star_annual": dsr_result["sr_star_annual"],
        "min_btl": dsr_result["min_btl"],
        "current_t": dsr_result["current_t"],
        "btl_sufficient": dsr_result["btl_sufficient"],
        "best_strategy": dsr_result["best_strategy"],
        "n_strategies": int(N),
        # Данные для графиков
        "scatter": {
            "is_sr": cscv["is_sr_best"],
            "oos_sr": cscv["oos_sr_best"],
        },
        "logit_hist": {
            "counts": counts.tolist(),
            "bin_edges": bin_edges.tolist(),
            "mean": float(logit_arr.mean()),
        },
        "strategy_stats": dsr_result["strategy_stats"],
    }
