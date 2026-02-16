"""
Сервис для измерения реализованной волатильности с поправкой на рыночный микроструктурный шум.

Реализует:
- RV (Realized Variance) — наивный, смещённый оценщик
- BV (Bipower Variation) — устойчивый к скачкам (Barndorff-Nielsen & Shephard 2004)
- TSRV (Two-Scale RV) — поправка на шум (Zhang, Mykland, Aït-Sahalia 2005)
- MSRV (Multi-Scale RV) — улучшенный TSRV (Zhang 2006)
- RK (Realized Kernel) — ядерный оценщик (Barndorff-Nielsen et al. 2008)
- Оценка дисперсии шума ω²
- Тест на наличие скачков (BN-Shephard ratio test)
- Сигнатурный график: RV(Δ) по разным частотам дискретизации
"""
import numpy as np
import scipy.stats
from typing import Dict, List, Optional, Tuple


# ── Ядерные функции ────────────────────────────────────────────────────────────

def _parzen_kernel(x: np.ndarray) -> np.ndarray:
    """Parzen kernel: гладкий, с нулевой производной на границе."""
    k = np.zeros_like(x)
    mask1 = x <= 0.5
    mask2 = (x > 0.5) & (x <= 1.0)
    k[mask1] = 1.0 - 6.0 * x[mask1] ** 2 + 6.0 * x[mask1] ** 3
    k[mask2] = 2.0 * (1.0 - x[mask2]) ** 3
    return k


def _tukey_hanning_kernel(x: np.ndarray) -> np.ndarray:
    """Tukey-Hanning kernel: используется в BN et al. (2008)."""
    k = np.zeros_like(x)
    mask = x <= 1.0
    k[mask] = 0.5 * (1.0 + np.cos(np.pi * x[mask]))
    return k


def _bartlett_kernel(x: np.ndarray) -> np.ndarray:
    """Bartlett (triangular) kernel."""
    k = np.zeros_like(x)
    mask = x <= 1.0
    k[mask] = 1.0 - x[mask]
    return k


_KERNELS = {
    "parzen": _parzen_kernel,
    "tukey-hanning": _tukey_hanning_kernel,
    "bartlett": _bartlett_kernel,
}


# ── Вспомогательные функции ────────────────────────────────────────────────────

def _log_returns(prices: np.ndarray) -> np.ndarray:
    """Логарифмические доходности."""
    return np.log(prices[1:] / prices[:-1])


def _subsample_prices(prices: np.ndarray, step: int) -> np.ndarray:
    """Каждая k-я цена."""
    return prices[::step]


# ── Оценщики ─────────────────────────────────────────────────────────────────

def _realized_variance(returns: np.ndarray) -> float:
    """RV = Σ rᵢ² — наивный оценщик."""
    return float(np.sum(returns ** 2))


def _bipower_variation(returns: np.ndarray) -> float:
    """
    BV = (π/2) · Σ |rᵢ| |rᵢ₊₁|
    Устойчив к конечному числу скачков (BN & Shephard 2004).
    """
    if len(returns) < 2:
        return 0.0
    return float((np.pi / 2.0) * np.sum(np.abs(returns[:-1]) * np.abs(returns[1:])))


def _tsrv(prices: np.ndarray, K: int = 5) -> Tuple[float, float]:
    """
    TSRV — Two-Scale Realized Variance (Zhang, Mykland, Aït-Sahalia 2005).

    TSRV = (1/K) Σₛ RV^(slow)_s − (n̄/n) · RV^(fast)
    где RV^(slow)_s — RV на k-кратно прореженной сетке, сдвинутой на s периодов.

    Returns: (tsrv_value, noise_variance)
    """
    n = len(prices) - 1  # количество интервалов
    if n < K * 2:
        K = max(1, n // 4)

    # Быстрый: RV на полной сетке (биас от шума максимален)
    r_fast = _log_returns(prices)
    rv_fast = _realized_variance(r_fast)

    # Медленный: среднее по K сдвинутым прореженным сеткам
    rv_slow_sum = 0.0
    count = 0
    for s in range(K):
        p_sub = prices[s::K]
        if len(p_sub) > 1:
            r_sub = _log_returns(p_sub)
            rv_slow_sum += _realized_variance(r_sub)
            count += 1

    if count == 0:
        return float(rv_fast), 0.0

    rv_slow_avg = rv_slow_sum / count
    n_bar = (n - K + 1.0) / K  # среднее кол-во наблюдений в прореженной сетке

    # Дисперсия шума: ω² ≈ RV_fast / (2n)
    noise_var = rv_fast / (2.0 * n)

    # TSRV (Zhang et al. 2005, eq. 2.8):
    # TSRV = (RV_slow − (n̄/n)·RV_fast) / (1 − n̄/n)
    n_bar_ratio = n_bar / n
    denom = 1.0 - n_bar_ratio
    if abs(denom) < 1e-10:
        return float(rv_slow_avg), float(noise_var)
    tsrv = (rv_slow_avg - n_bar_ratio * rv_fast) / denom

    return float(max(tsrv, 0.0)), float(noise_var)


def _msrv(prices: np.ndarray, K_max: int = 20) -> float:
    """
    MSRV — Multi-Scale RV (Zhang 2006).

    Оптимально взвешивает TSRV на разных масштабах:
    MSRV = Σ_k a_k · RV_k,  где a_k = (12k/K²) · (1 - k/K) - bias-correction веса.

    Снижает дисперсию оценки по сравнению с TSRV за счёт
    усреднения по нескольким масштабам.
    """
    n = len(prices) - 1
    K_max = min(K_max, n // 4)
    if K_max < 2:
        return _tsrv(prices, K=1)[0]

    # Веса a_k: убывающие, положительные, нормированные
    # Основаны на оптимальной схеме Zhang (2006):
    # a_k ∝ k(K - k), нормируем до суммы = 1
    ks = np.arange(1, K_max, dtype=float)  # k = 1, ..., K_max-1
    raw_weights = ks * (K_max - ks)
    weight_sum = raw_weights.sum()
    if weight_sum == 0:
        return _tsrv(prices, K=K_max)[0]
    alpha_k = raw_weights / weight_sum

    # Вычитаем bias от шума: MSRV = Σ a_k RV_k^slow − (n_bar/n) · RV_fast
    rv_fast = _realized_variance(_log_returns(prices))
    n_total = float(n)

    msrv = 0.0
    for i, k in enumerate(ks):
        k_int = int(k)
        rv_k_sum = 0.0
        cnt = 0
        for s in range(k_int):
            p_sub = prices[s::k_int]
            if len(p_sub) > 1:
                rv_k_sum += _realized_variance(_log_returns(p_sub))
                cnt += 1
        if cnt > 0:
            n_k = n_total / k_int  # среднее наблюдений в прореженной сетке
            # bias-corrected: TSRV_k = RV_k_slow - (n_k/n) * RV_fast
            tsrv_k = rv_k_sum / cnt - (n_k / n_total) * rv_fast
            msrv += alpha_k[i] * tsrv_k

    return float(max(msrv, 0.0))


def _realized_kernel(returns: np.ndarray, H: Optional[int] = None, kernel: str = "parzen") -> float:
    """
    RK — Realized Kernel (Barndorff-Nielsen et al. 2008).

    RK = γ₀ + 2 Σ_{h=1}^{H} k(h/(H+1)) · γ_h
    γ_h = Σᵢ rᵢ · rᵢ₊h  (h-я реализованная автоковариация)

    Bandwidth: H ∝ n^(3/5) (BN et al. рекомендация для Parzen kernel)
    """
    n = len(returns)
    if n < 4:
        return float(np.sum(returns ** 2))

    kernel_fn = _KERNELS.get(kernel, _parzen_kernel)

    if H is None:
        H = max(1, int(np.ceil(n ** (3.0 / 5.0))))
    H = min(H, n - 1)

    # γ₀ = RV (диагональ)
    gamma0 = float(np.sum(returns ** 2))

    # γ_h для h = 1, ..., H
    h_vals = np.arange(1, H + 1, dtype=float)
    k_vals = kernel_fn(h_vals / (H + 1))

    rk = gamma0
    for h in range(1, H + 1):
        gamma_h = float(np.dot(returns[h:], returns[:-h]))
        rk += 2.0 * k_vals[h - 1] * gamma_h

    return float(max(rk, 0.0))


# ── Тест на скачки ────────────────────────────────────────────────────────────

def _jump_test(rv: float, bv: float, n: int) -> Dict:
    """
    BN-Shephard отношение для теста на наличие скачков.
    H₀: нет скачков → (RV − BV) / RV → 0

    Статистика Хуанга-Тауша (2005):
    z = (RV − BV) / (ω_RQ · RV)
    где ω_RQ = (π²/4 + π − 5) · max(1, RQ/BV²)
    """
    if bv <= 0 or rv <= 0:
        return {"jump_component": 0.0, "ratio": 0.0, "z_stat": 0.0, "p_value": 1.0, "has_jumps": False}

    jump_component = max(rv - bv, 0.0)
    ratio = jump_component / rv

    # Упрощённый тест: z = (1 - BV/RV) / SE
    # SE ≈ sqrt((π²/4 + π - 5) / n) — из теории
    omega = np.sqrt((np.pi ** 2 / 4.0 + np.pi - 5.0) / n)
    z_stat = ratio / omega if omega > 0 else 0.0
    p_value = float(1.0 - scipy.stats.norm.cdf(z_stat))

    return {
        "jump_component": float(jump_component),
        "continuous_component": float(bv),
        "ratio": float(ratio),
        "z_stat": float(z_stat),
        "p_value": float(p_value),
        "has_jumps": bool(p_value < 0.05),
    }


# ── Сигнатурный график ────────────────────────────────────────────────────────

def _signature_plot(prices: np.ndarray, steps: Optional[List[int]] = None) -> Dict:
    """
    Сигнатурный график: RV(Δ) для разных шагов дискретизации Δ.
    Без шума: RV(Δ) ≈ const (истинная IV)
    С шумом: RV(Δ) → ∞ при Δ → 0 (микроструктурный эффект)
    """
    n = len(prices) - 1
    if steps is None:
        max_step = min(n // 4, 120)
        steps = list(range(1, max_step + 1, max(1, max_step // 30)))

    rv_vals, step_vals = [], []
    for step in steps:
        p_sub = _subsample_prices(prices, step)
        if len(p_sub) < 3:
            continue
        r_sub = _log_returns(p_sub)
        rv_sub = _realized_variance(r_sub)
        # Аннуализируем к единому базису: умножаем на кол-во шагов в "дне"
        rv_per_period = rv_sub * step  # привести к масштабу step=1
        rv_vals.append(float(rv_per_period))
        step_vals.append(int(step))

    return {"steps": step_vals, "rv": rv_vals}


# ── Главная функция ───────────────────────────────────────────────────────────

def compute_realized_kernels(
    prices: List[float],
    kernel: str = "parzen",
    bandwidth: Optional[int] = None,
    tsrv_scales: int = 5,
    annualize: bool = True,
    periods_per_day: int = 390,  # минут в торговой сессии NYSE
) -> Dict:
    """
    Вычисляет все оценщики реализованной волатильности.

    Args:
        prices: ряд цен высокочастотных наблюдений (в хронологическом порядке)
        kernel: тип ядра для RK — "parzen", "tukey-hanning", "bartlett"
        bandwidth: H для RK (None = автоматически по n^(3/5))
        tsrv_scales: K для TSRV
        annualize: приводить ли к годовой волатильности
        periods_per_day: количество наблюдений в одном торговом дне

    Returns:
        dict со всеми оценщиками, тестом скачков и данными для графиков
    """
    p = np.asarray(prices, dtype=float)
    if len(p) < 10:
        raise ValueError("Нужно минимум 10 наблюдений цен")
    if np.any(p <= 0):
        raise ValueError("Все цены должны быть положительными")

    r = _log_returns(p)
    n = len(r)

    # Коэффициент аннуализации: 252 торговых дня
    # Для дневных данных — periods_per_day=1; для минутных — 390
    trading_days = 252
    ann_factor = trading_days * periods_per_day / n if annualize else 1.0

    # ── Оценщики ──────────────────────────────────────────────────────────────
    rv = _realized_variance(r)
    bv = _bipower_variation(r)
    tsrv_val, noise_var = _tsrv(p, K=tsrv_scales)
    msrv_val = _msrv(p)
    rk_val = _realized_kernel(r, H=bandwidth, kernel=kernel)

    # Аннуализированные волатильности: σ = sqrt(IV · ann_factor)
    def to_vol(iv: float) -> float:
        return float(np.sqrt(max(iv, 0.0) * ann_factor))

    # ── Тест на скачки ────────────────────────────────────────────────────────
    jump_stats = _jump_test(rv, bv, n)

    # ── Дисперсия шума (оценка из RV — TSRV разности) ────────────────────────
    noise_vol = float(np.sqrt(max(noise_var, 0.0)))

    # ── Сигнатурный график ───────────────────────────────────────────────────
    sig_plot = _signature_plot(p)

    # ── Оптимальная частота дискретизации (критерий MSE) ─────────────────────
    # Δ* ≈ (4ω⁴ / μ₁⁴ · IQ)^(1/5) где IQ ≈ 3·RV² (нормальность)
    # Упрощённо: оптимальный шаг = arg min MSE(Δ) на сигнатурном графике
    optimal_step = 1
    if len(sig_plot["rv"]) > 3:
        # Ищем "колено" — где RV(Δ) перестаёт убывать
        rv_arr = np.array(sig_plot["rv"])
        steps_arr = np.array(sig_plot["steps"])
        grad = np.diff(rv_arr)
        sign_changes = np.where(np.diff(np.sign(grad)))[0]
        if len(sign_changes) > 0:
            optimal_step = int(steps_arr[sign_changes[0] + 1])
        else:
            optimal_step = int(steps_arr[len(steps_arr) // 3])

    # ── Bandwidth информация ─────────────────────────────────────────────────
    auto_H = max(1, int(np.ceil(n ** (3.0 / 5.0))))
    used_H = bandwidth if bandwidth is not None else auto_H

    return {
        # Оценщики (реализованная дисперсия, не аннуализированная)
        "rv_raw": float(rv),
        "bv_raw": float(bv),
        "tsrv_raw": float(tsrv_val),
        "msrv_raw": float(msrv_val),
        "rk_raw": float(rk_val),
        # Аннуализированные волатильности
        "rv_vol": to_vol(rv),
        "bv_vol": to_vol(bv),
        "tsrv_vol": to_vol(tsrv_val),
        "msrv_vol": to_vol(msrv_val),
        "rk_vol": to_vol(rk_val),
        # Дополнительно
        "noise_variance": float(noise_var),
        "noise_vol": float(noise_vol),
        "n_observations": int(n),
        "bandwidth_used": int(used_H),
        "bandwidth_auto": int(auto_H),
        "kernel": kernel,
        "ann_factor": float(ann_factor),
        # Тест на скачки
        "jump_test": jump_stats,
        # Данные для графиков
        "signature_plot": sig_plot,
        "optimal_sampling_step": optimal_step,
    }
