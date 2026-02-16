"""
Сервис для статистического анализа коэффициента Шарпа.

Реализует:
- SE(SR) по Lo (2002) и Mertens (2002) с поправкой на ненормальность
- t-тест и p-value для H₀: SR = 0
- Доверительные интервалы 95%/99%
- Probabilistic Sharpe Ratio (Bailey & López de Prado 2012)
- Deflated Sharpe Ratio с поправкой на число испытаний
- PSR-кривую как функцию SR*
"""
import numpy as np
import scipy.stats
from typing import Dict, List, Optional


def compute_sharpe_stats(
    returns: List[float],
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
    benchmark_sr: float = 0.0,
    n_trials: int = 1,
) -> Dict:
    """
    Полный статистический анализ коэффициента Шарпа.

    Args:
        returns: ряд периодических доходностей
        risk_free_rate: безрисковая ставка (годовая, в долях)
        periods_per_year: количество периодов в году (252 = дни, 52 = недели, 12 = месяцы)
        benchmark_sr: пороговое SR для PSR (годовое)
        n_trials: число стратегий для DSR (поправка на data mining)

    Returns:
        dict с метриками SR, SE, t-статистикой, p-value, PSR, DSR
    """
    r = np.asarray(returns, dtype=float)
    if len(r) < 10:
        raise ValueError("Нужно минимум 10 наблюдений")

    rf_per_period = risk_free_rate / periods_per_year
    excess_r = r - rf_per_period
    T = len(r)

    mean_e = float(np.mean(excess_r))
    std_e = float(np.std(excess_r, ddof=1))

    if std_e == 0:
        raise ValueError("Стандартное отклонение доходностей равно нулю")

    # Моменты распределения доходностей
    skew = float(scipy.stats.skew(excess_r))
    excess_kurt = float(scipy.stats.kurtosis(excess_r))  # excess kurtosis

    # Коэффициент Шарпа за период
    sr_freq = mean_e / std_e

    # Годовой SR (Lo 2002: умножение на sqrt(T_year), IID assumption)
    sr_annual = sr_freq * np.sqrt(periods_per_year)

    # ── Стандартные ошибки ──────────────────────────────────────────────────

    # SE (IID нормальность, Lo 2002)
    se_iid_freq = np.sqrt((1.0 + sr_freq ** 2 / 2.0) / T)

    # SE с поправкой на ненормальность (Mertens 2002 / Opdyke 2007)
    # Var(SR) ≈ (1 + SR²/2 - skew·SR + excess_kurt/4) / T
    var_nonnormal = (1.0 + 0.5 * sr_freq ** 2 - skew * sr_freq + excess_kurt / 4.0) / T
    var_nonnormal = max(var_nonnormal, 1e-12)  # защита от отрицательных значений при маленьком T
    se_nonnormal_freq = np.sqrt(var_nonnormal)

    # Годовые SE
    se_iid_annual = se_iid_freq * np.sqrt(periods_per_year)
    se_nonnormal_annual = se_nonnormal_freq * np.sqrt(periods_per_year)

    # ── Hypothesis test H₀: SR = 0 ─────────────────────────────────────────
    t_stat = sr_freq / se_nonnormal_freq
    p_value = float(2.0 * (1.0 - scipy.stats.norm.cdf(abs(t_stat))))

    # ── Доверительные интервалы (годовые) ──────────────────────────────────
    ci_95 = [
        float(sr_annual - 1.96 * se_nonnormal_annual),
        float(sr_annual + 1.96 * se_nonnormal_annual),
    ]
    ci_99 = [
        float(sr_annual - 2.576 * se_nonnormal_annual),
        float(sr_annual + 2.576 * se_nonnormal_annual),
    ]

    # ── Probabilistic Sharpe Ratio (Bailey & López de Prado 2012) ──────────
    # PSR(SR*) = Φ( (SR_hat - SR*) · √(T-1) / √(1 - skew·SR_hat + (excess_kurt+1)/4 · SR_hat²) )
    # Все величины в per-period единицах
    sr_star_freq = benchmark_sr / np.sqrt(periods_per_year)

    psr_denom_sq = 1.0 - skew * sr_freq + (excess_kurt + 1.0) / 4.0 * sr_freq ** 2
    if psr_denom_sq <= 0 or T <= 1:
        psr = 0.5
    else:
        psr_z = (sr_freq - sr_star_freq) * np.sqrt(T - 1) / np.sqrt(psr_denom_sq)
        psr = float(scipy.stats.norm.cdf(psr_z))

    # ── Deflated Sharpe Ratio (поправка на число испытаний) ─────────────────
    # DSR = PSR(E[max SR over N trials])
    # E[max SR] ≈ SR_star + SE * ((1-γ_E)·z(1-1/N) + γ_E·z(1-1/(N·e)))
    # γ_E = постоянная Эйлера-Маскерони
    euler_gamma = 0.5772156649015329

    if n_trials > 1:
        z1 = float(scipy.stats.norm.ppf(1.0 - 1.0 / n_trials))
        z2 = float(scipy.stats.norm.ppf(1.0 - 1.0 / (n_trials * np.e)))
        sr_star_dsr = sr_star_freq + se_nonnormal_freq * (
            (1.0 - euler_gamma) * z1 + euler_gamma * z2
        )
    else:
        sr_star_dsr = sr_star_freq

    if psr_denom_sq <= 0 or T <= 1:
        dsr = 0.5
    else:
        dsr_z = (sr_freq - sr_star_dsr) * np.sqrt(T - 1) / np.sqrt(psr_denom_sq)
        dsr = float(scipy.stats.norm.cdf(dsr_z))

    # ── PSR-кривая: PSR как функция SR* (для графика) ──────────────────────
    sr_star_range = np.linspace(
        sr_annual - 3.0 * se_nonnormal_annual,
        sr_annual + 3.0 * se_nonnormal_annual,
        120,
    )
    if psr_denom_sq > 0 and T > 1:
        psr_curve_z = (
            (sr_freq - sr_star_range / np.sqrt(periods_per_year))
            * np.sqrt(T - 1)
            / np.sqrt(psr_denom_sq)
        )
        psr_curve = scipy.stats.norm.cdf(psr_curve_z).tolist()
    else:
        psr_curve = [0.5] * len(sr_star_range)

    # ── Распределение SR под H₀ (для графика) ───────────────────────────────
    # SR_hat ~ N(0, SE²) под H₀
    null_x = np.linspace(-4.0 * se_nonnormal_annual, 4.0 * se_nonnormal_annual, 200)
    null_pdf = scipy.stats.norm.pdf(null_x, loc=0.0, scale=se_nonnormal_annual)

    return {
        "sr_annual": float(sr_annual),
        "sr_freq": float(sr_freq),
        "mean_annual": float(mean_e * periods_per_year),
        "vol_annual": float(std_e * np.sqrt(periods_per_year)),
        "skewness": float(skew),
        "excess_kurtosis": float(excess_kurt),
        "n_observations": int(T),
        "periods_per_year": int(periods_per_year),
        # Стандартные ошибки (годовые)
        "se_iid": float(se_iid_annual),
        "se_nonnormal": float(se_nonnormal_annual),
        # Тест
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "is_significant_5pct": bool(p_value < 0.05),
        "is_significant_1pct": bool(p_value < 0.01),
        # Доверительные интервалы
        "ci_95": ci_95,
        "ci_99": ci_99,
        # PSR / DSR
        "psr": float(psr),
        "dsr": float(dsr),
        "benchmark_sr": float(benchmark_sr),
        "n_trials": int(n_trials),
        # Данные для графиков
        "psr_curve": {
            "sr_star": [float(x) for x in sr_star_range],
            "psr_values": psr_curve,
        },
        "null_distribution": {
            "x": [float(x) for x in null_x],
            "pdf": [float(y) for y in null_pdf],
        },
    }
