"""
Сервис для HAR модели прогнозирования волатильности.

Реализует:
- HAR-RV (Corsi 2009): RV_t = β₀ + β_d·RV_{t-1} + β_w·RV̄_{t-5} + β_m·RV̄_{t-22}
- HAR-RV-J: расширение с компонентом скачков (J_t = max(RV_t − BV_t, 0))
- HAR-RV-CJ: раздельно непрерывный (C) и скачковый (J) компоненты
- Log-HAR: регрессия log(RV) для улучшенных дистрибуционных свойств
- OLS с поправкой Ньюи-Уэста (HAC SE) на гетероскедастичность и автокорреляцию
- h-шаговые прогнозы: h = 1, 5, 22
- Оценка качества: RMSE, MAE, QLIKE
"""
import numpy as np
import scipy.stats
from typing import Dict, List, Optional, Tuple


# ── Построение регрессоров HAR ────────────────────────────────────────────────

def _build_har_features(rv: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    Строит матрицу регрессоров [1, RV_{t-1}, RV̄_{t-5}, RV̄_{t-22}].
    Первые 22 наблюдения теряются для формирования лагов.

    Returns:
        X: матрица регрессоров (T-22) × 4
        start: индекс первого используемого таргета
    """
    T = len(rv)
    start = 22
    n = T - start

    X = np.ones((n, 4))
    for i in range(n):
        t = i + start
        X[i, 1] = rv[t - 1]                          # дневной лаг
        X[i, 2] = np.mean(rv[t - 5: t])              # недельный (5 дней)
        X[i, 3] = np.mean(rv[t - 22: t])             # месячный (22 дня)
    return X, start


def _build_har_cj_features(rv: np.ndarray, bv: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    Строит регрессоры HAR-RV-CJ:
    [1, C_{t-1}, J_{t-1}, C̄_{t-5}, C̄_{t-22}]
    где C_t = BV_t (continuous), J_t = max(RV_t − BV_t, 0) (jump)
    """
    C = bv.copy()
    J = np.maximum(rv - bv, 0.0)

    T = len(rv)
    start = 22
    n = T - start

    X = np.ones((n, 5))
    for i in range(n):
        t = i + start
        X[i, 1] = C[t - 1]
        X[i, 2] = J[t - 1]
        X[i, 3] = np.mean(C[t - 5: t])
        X[i, 4] = np.mean(C[t - 22: t])
    return X, start


# ── OLS с Newey-West HAC SE ───────────────────────────────────────────────────

def _ols_newey_west(X: np.ndarray, y: np.ndarray, lags: int = 5) -> Dict:
    """
    OLS оценка с HAC стандартными ошибками (Newey-West 1987).

    Var_NW = (XᵀX)⁻¹ · S_NW · (XᵀX)⁻¹
    S_NW = Γ₀ + Σ_{h=1}^{L} w_h · (Γ_h + Γ_hᵀ)
    w_h = 1 − h/(L+1)  (веса Бартлетта)
    """
    n, k = X.shape
    # OLS β = (XᵀX)⁻¹ Xᵀy
    XtX = X.T @ X
    try:
        XtX_inv = np.linalg.inv(XtX)
    except np.linalg.LinAlgError:
        XtX_inv = np.linalg.pinv(XtX)

    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta
    fitted = X @ beta

    # R²
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    r2_adj = 1.0 - (1.0 - r2) * (n - 1) / (n - k - 1) if n > k + 1 else r2

    # Newey-West HAC
    scores = resid[:, None] * X  # n × k
    S = scores.T @ scores  # Γ₀
    for h in range(1, lags + 1):
        w = 1.0 - h / (lags + 1.0)
        gamma_h = scores[h:].T @ scores[:-h]
        S += w * (gamma_h + gamma_h.T)

    vcov = XtX_inv @ S @ XtX_inv
    se = np.sqrt(np.maximum(np.diag(vcov), 0.0))
    t_stats = beta / (se + 1e-15)
    p_values = 2.0 * (1.0 - scipy.stats.t.cdf(np.abs(t_stats), df=n - k))

    return {
        "beta": beta.tolist(),
        "se": se.tolist(),
        "t_stat": t_stats.tolist(),
        "p_value": p_values.tolist(),
        "r2": float(r2),
        "r2_adj": float(r2_adj),
        "n_obs": int(n),
        "fitted": fitted.tolist(),
        "residuals": resid.tolist(),
    }


# ── Метрики прогноза ──────────────────────────────────────────────────────────

def _forecast_metrics(actual: np.ndarray, predicted: np.ndarray) -> Dict:
    """RMSE, MAE, QLIKE (стандартная функция потерь для волатильности)."""
    err = actual - predicted
    rmse = float(np.sqrt(np.mean(err ** 2)))
    mae = float(np.mean(np.abs(err)))
    # QLIKE: E[RV/RV_hat − log(RV/RV_hat) − 1]
    ratio = actual / np.maximum(predicted, 1e-15)
    qlike = float(np.mean(ratio - np.log(ratio) - 1.0))
    return {"rmse": rmse, "mae": mae, "qlike": qlike}


# ── h-шаговые прогнозы ────────────────────────────────────────────────────────

def _multi_step_forecast(rv: np.ndarray, beta: np.ndarray, h: int = 1) -> float:
    """
    Прогноз HAR-RV на h шагов вперёд.
    Для h > 1 итеративно подставляет прогнозы.
    """
    rv_ext = list(rv.copy())
    for _ in range(h):
        t = len(rv_ext)
        x = np.array([
            1.0,
            rv_ext[t - 1],
            np.mean(rv_ext[max(t - 5, 0): t]),
            np.mean(rv_ext[max(t - 22, 0): t]),
        ])
        rv_next = float(max(np.dot(beta, x), 0.0))
        rv_ext.append(rv_next)
    return rv_ext[-1]


# ── Главная функция ───────────────────────────────────────────────────────────

def fit_har_model(
    rv: List[float],
    bv: Optional[List[float]] = None,
    log_transform: bool = False,
    forecast_horizons: List[int] = None,
    train_ratio: float = 0.8,
) -> Dict:
    """
    Оценивает HAR-RV, HAR-RV-CJ (если передан BV) и Log-HAR модели.

    Args:
        rv: ряд реализованных дисперсий (ежедневные)
        bv: ряд bipower variation (для выделения скачков, опционально)
        log_transform: применять log(RV) в качестве зависимой переменной
        forecast_horizons: горизонты прогноза в днях (по умолчанию [1, 5, 22])
        train_ratio: доля обучающей выборки

    Returns:
        dict с коэффициентами, метриками, прогнозами и данными для графиков
    """
    if forecast_horizons is None:
        forecast_horizons = [1, 5, 22]

    rv_arr = np.asarray(rv, dtype=float)
    if len(rv_arr) < 50:
        raise ValueError("Нужно минимум 50 наблюдений для HAR модели")
    if np.any(rv_arr <= 0):
        raise ValueError("Все значения RV должны быть положительными")

    # ── Разбивка train/test ────────────────────────────────────────────────
    split = int(len(rv_arr) * train_ratio)
    split = max(split, 44)  # минимум 22 для лагов + 22 для оценки

    rv_train = rv_arr[:split]
    rv_test = rv_arr[split:]

    # ── HAR-RV ────────────────────────────────────────────────────────────────
    X_train, start = _build_har_features(rv_train)
    y_train = rv_train[start:]

    X_all, _ = _build_har_features(rv_arr)
    y_all = rv_arr[22:]

    if log_transform:
        y_fit = np.log(y_train)
        y_all_fit = np.log(y_all)
        X_train_log = X_train.copy()
        X_train_log[:, 1:] = np.log(np.maximum(X_train[:, 1:], 1e-15))
        X_all_log = X_all.copy()
        X_all_log[:, 1:] = np.log(np.maximum(X_all[:, 1:], 1e-15))
        ols_train = _ols_newey_west(X_train_log, y_fit)
        ols_all = _ols_newey_west(X_all_log, y_all_fit)
    else:
        ols_train = _ols_newey_west(X_train, y_train)
        ols_all = _ols_newey_west(X_all, y_all)

    beta_har = np.array(ols_train["beta"])
    coef_names = ["β₀ (intercept)", "β_d (daily)", "β_w (weekly)", "β_m (monthly)"]

    # OOS прогноз (итеративный)
    if len(rv_test) > 0:
        X_test, _ = _build_har_features(rv_arr)
        n_train_X = len(rv_train) - 22
        n_all_X = len(rv_arr) - 22
        X_test_part = X_test[n_train_X:]
        y_test = rv_arr[22 + n_train_X:]

        if log_transform:
            X_test_log = X_test_part.copy()
            X_test_log[:, 1:] = np.log(np.maximum(X_test_part[:, 1:], 1e-15))
            y_hat_test = np.exp(X_test_log @ beta_har)
        else:
            y_hat_test = np.maximum(X_test_part @ beta_har, 0.0)

        oos_metrics = _forecast_metrics(y_test, y_hat_test) if len(y_test) > 0 else {}
    else:
        y_hat_test = np.array([])
        y_test = np.array([])
        oos_metrics = {}

    # IS метрики
    fitted_arr = np.array(ols_train["fitted"])
    if log_transform:
        fitted_arr = np.exp(fitted_arr)
    is_metrics = _forecast_metrics(y_train, fitted_arr)

    # ── Multi-step forecasts ──────────────────────────────────────────────────
    forecasts = {}
    for h in forecast_horizons:
        val = _multi_step_forecast(rv_arr, beta_har, h)
        if log_transform:
            val = float(np.exp(val))
        # Аннуализированная волатильность: sqrt(RV_daily * 252)
        forecasts[f"h{h}"] = {
            "rv": float(val),
            "vol_annual": float(np.sqrt(max(val * 252, 0.0))),
            "horizon_days": h,
        }

    # ── HAR-RV-CJ (если есть BV) ──────────────────────────────────────────────
    cj_result = None
    if bv is not None and len(bv) == len(rv):
        bv_arr = np.asarray(bv, dtype=float)
        bv_train = bv_arr[:split]
        X_cj, start_cj = _build_har_cj_features(rv_train, bv_train)
        y_cj = rv_train[start_cj:]
        if log_transform:
            ols_cj = _ols_newey_west(X_cj, np.log(y_cj))
        else:
            ols_cj = _ols_newey_west(X_cj, y_cj)

        cj_coef_names = ["β₀", "β_C (continuous)", "β_J (jump)", "β_w (weekly C)", "β_m (monthly C)"]
        cj_result = {
            "coefficients": [
                {"name": cj_coef_names[i], "beta": ols_cj["beta"][i],
                 "se": ols_cj["se"][i], "t_stat": ols_cj["t_stat"][i],
                 "p_value": ols_cj["p_value"][i]}
                for i in range(len(ols_cj["beta"]))
            ],
            "r2": ols_cj["r2"],
            "r2_adj": ols_cj["r2_adj"],
        }

    # ── Данные для графиков ───────────────────────────────────────────────────
    # Fitted (полная выборка)
    if log_transform:
        X_all_log = X_all.copy()
        X_all_log[:, 1:] = np.log(np.maximum(X_all[:, 1:], 1e-15))
        fitted_full = np.exp(X_all_log @ beta_har).tolist()
    else:
        fitted_full = np.maximum(X_all @ beta_har, 0.0).tolist()

    # Аннуализированная vol для графика: sqrt(RV * 252)
    actual_vol = (np.sqrt(y_all * 252) * 100).tolist()
    fitted_vol = (np.sqrt(np.maximum(np.array(fitted_full), 0) * 252) * 100).tolist()
    n_plot = len(actual_vol)

    return {
        # HAR-RV коэффициенты (на обучающей выборке)
        "coefficients": [
            {
                "name": coef_names[i],
                "beta": ols_train["beta"][i],
                "se": ols_train["se"][i],
                "t_stat": ols_train["t_stat"][i],
                "p_value": ols_train["p_value"][i],
                "significant": bool(ols_train["p_value"][i] < 0.05),
            }
            for i in range(len(ols_train["beta"]))
        ],
        "r2": ols_train["r2"],
        "r2_adj": ols_train["r2_adj"],
        "r2_full": ols_all["r2"],
        # Метрики
        "is_metrics": is_metrics,
        "oos_metrics": oos_metrics,
        # Прогнозы
        "forecasts": forecasts,
        # HAR-RV-CJ
        "cj_model": cj_result,
        # Log-transform flag
        "log_transform": log_transform,
        # Данные для графика
        "plot_data": {
            "actual_vol": actual_vol,
            "fitted_vol": fitted_vol,
            "n": n_plot,
            "train_end": split - 22,
        },
        "n_observations": len(rv_arr),
        "n_train": split,
        "n_test": len(rv_test),
    }
