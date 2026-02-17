"""
Orthogonal Alpha Stacking (residualization + IC-weighted combination).

Реализует:
- Gram-Schmidt / OLS-residualization: каждый сигнал ортогонализируется
  последовательно или относительно всех остальных
- IC / IR: Information Coefficient (ранговая корреляция сигнал → форв. доходность)
  и Information Ratio (IC / std(IC))
- IC decay: IC на горизонтах 1..H лагов
- Оптимальные веса: IR²-proportional + shrinkage к равным весам
- Стэкинговый сигнал: взвешенная сумма ортогональных сигналов
- Диверсификация: cross-IC матрица до и после ортогонализации
"""
import numpy as np
import scipy.stats
from typing import Dict, List, Optional


# ── IC / IR утилиты ───────────────────────────────────────────────────────────

def _rank_ic(signal: np.ndarray, fwd_returns: np.ndarray) -> float:
    """Ранговая корреляция Спирмена (IC) между сигналом и форвардными доходностями."""
    mask = np.isfinite(signal) & np.isfinite(fwd_returns)
    if mask.sum() < 5:
        return 0.0
    rho, _ = scipy.stats.spearmanr(signal[mask], fwd_returns[mask])
    return float(rho) if np.isfinite(rho) else 0.0


def _ic_series(signals: np.ndarray, fwd_rets: np.ndarray, horizon: int = 1) -> np.ndarray:
    """
    IC во времени для одного сигнала.
    signals: T × N_assets, fwd_rets: T × N_assets (h-period fwd returns)
    Возвращает вектор IC длиной T−h.
    """
    T = signals.shape[0]
    ic_t = []
    for t in range(T - horizon):
        s_t = signals[t]
        r_t = fwd_rets[t + horizon - 1] if horizon > 0 else fwd_rets[t]
        ic_t.append(_rank_ic(s_t, r_t))
    return np.array(ic_t)


# ── Ортогонализация ───────────────────────────────────────────────────────────

def _residualize_signal(target: np.ndarray, controls: np.ndarray) -> np.ndarray:
    """
    OLS-residualization: убираем из target линейную проекцию на controls.
    target: (T,), controls: (T, K)
    Возвращает residuals той же формы.
    """
    T = target.shape[0]
    if controls.shape[1] == 0:
        return target.copy()
    X = np.column_stack([np.ones(T), controls])
    b = np.linalg.lstsq(X, target, rcond=None)[0]
    return target - X @ b


def orthogonalize_signals(signals: np.ndarray, method: str = "sequential") -> np.ndarray:
    """
    Ортогонализация N сигналов.

    methods:
      - 'sequential': Gram-Schmidt последовательная.
        Сигнал k ортогонализируется относительно {1..k-1}.
      - 'pairwise': каждый сигнал ортогонализируется относительно всех остальных.
        Устойчивее, но порядконезависимый.

    signals: T × N или (T_obs × N_assets) × N_signals — здесь T × N
    где T = число наблюдений (дат×активов), N = число сигналов.
    Возвращает матрицу того же размера.
    """
    T, N = signals.shape
    ortho = signals.copy().astype(float)

    if method == "sequential":
        # Gram-Schmidt: signal_k -= projection onto {0..k-1}
        for k in range(1, N):
            controls = ortho[:, :k]
            ortho[:, k] = _residualize_signal(ortho[:, k], controls)
    elif method == "pairwise":
        # Каждый сигнал = остаток регрессии на все остальные (оригинальные)
        original = signals.copy()
        for k in range(N):
            controls = np.delete(original, k, axis=1)
            ortho[:, k] = _residualize_signal(original[:, k], controls)
    else:
        raise ValueError(f"Unknown method: {method}")

    # Стандартизируем каждый ортогональный сигнал
    for k in range(N):
        std = float(np.std(ortho[:, k], ddof=1))
        if std > 1e-15:
            ortho[:, k] /= std

    return ortho


# ── IC decay ──────────────────────────────────────────────────────────────────

def _compute_ic_decay(
    panel_signals: np.ndarray,   # T × N_assets × N_signals or T × N_signals (panel pre-stacked)
    panel_fwd: np.ndarray,       # T × N_assets forward returns
    horizons: List[int],
    signal_names: List[str],
) -> Dict:
    """
    IC на горизонтах 1..H.
    panel_signals: T × N_assets × N_signals
    panel_fwd: T × N_assets
    """
    T, N_a, N_s = panel_signals.shape
    decay = {}
    for h in horizons:
        ic_by_signal = []
        for k in range(N_s):
            ic_t = []
            for t in range(T - h):
                s = panel_signals[t, :, k]
                r = panel_fwd[t + h - 1] if h > 0 else panel_fwd[t]
                ic_t.append(_rank_ic(s, r))
            ic_by_signal.append(float(np.nanmean(ic_t)))
        decay[h] = {signal_names[k]: ic_by_signal[k] for k in range(N_s)}
    return decay


# ── Оптимальные веса стэкинга ──────────────────────────────────────────────────

def _optimal_weights(ir: np.ndarray, shrinkage: float = 0.3) -> np.ndarray:
    """
    Веса пропорциональны IR² (Grinold & Kahn).
    Shrinkage к равным весам: w = (1-α)·w_IR + α·(1/N).
    """
    N = len(ir)
    ir_sq = ir ** 2
    total = ir_sq.sum()
    if total < 1e-15:
        return np.ones(N) / N
    w_ir = ir_sq / total
    w_eq = np.ones(N) / N
    w = (1.0 - shrinkage) * w_ir + shrinkage * w_eq
    return w / w.sum()


# ── Главная функция ───────────────────────────────────────────────────────────

def compute_alpha_stacking(
    panel_signals: List[List[List[float]]],   # T × N_assets × N_signals
    panel_fwd_returns: List[List[float]],     # T × N_assets
    signal_names: Optional[List[str]] = None,
    ortho_method: str = "sequential",
    ic_horizons: List[int] = None,
    shrinkage: float = 0.3,
) -> Dict:
    """
    Полный анализ Orthogonal Alpha Stacking.

    Args:
        panel_signals: T × N_assets × N_signals — сигналы (ранки, z-scores, etc.)
        panel_fwd_returns: T × N_assets — форвардные доходности для оценки IC
        signal_names: имена N_signals сигналов
        ortho_method: 'sequential' (Gram-Schmidt) или 'pairwise'
        ic_horizons: горизонты IC decay (дни/периоды)
        shrinkage: к равным весам (0=pure IR², 1=equal)

    Returns:
        dict с IC/IR, ортогональными сигналами, весами, decay, cross-IC матрицей
    """
    if ic_horizons is None:
        ic_horizons = [1, 5, 10, 21]

    S_raw = np.asarray(panel_signals, dtype=float)   # T × N_a × N_s
    F_raw = np.asarray(panel_fwd_returns, dtype=float)  # T × N_a

    T, N_a, N_s = S_raw.shape
    if T < 10:
        raise ValueError(f"Нужно минимум 10 периодов, получено {T}")
    if N_s < 2:
        raise ValueError("Нужно минимум 2 сигнала")
    if F_raw.shape != (T, N_a):
        raise ValueError(f"panel_fwd_returns должен быть {T}×{N_a}")

    if signal_names is None:
        signal_names = [f"Alpha_{k+1}" for k in range(N_s)]
    elif len(signal_names) != N_s:
        signal_names = [f"Alpha_{k+1}" for k in range(N_s)]

    # ── 1. IC оригинальных сигналов (горизонт 1) ──────────────────────────────
    raw_ic_mean = []
    raw_ic_std = []
    raw_ir = []
    for k in range(N_s):
        ic_list = []
        for t in range(T - 1):
            ic_list.append(_rank_ic(S_raw[t, :, k], F_raw[t]))
        ic_arr = np.array(ic_list)
        m = float(np.nanmean(ic_arr))
        s = float(np.nanstd(ic_arr, ddof=1)) if len(ic_arr) > 1 else 1.0
        raw_ic_mean.append(m)
        raw_ic_std.append(s)
        raw_ir.append(m / (s + 1e-15))

    # ── 2. Cross-IC матрица (до ортогонализации) ───────────────────────────────
    # Аggregation: flatten (T × N_a) × N_s
    flat = S_raw.reshape(T * N_a, N_s)
    cross_ic_raw = np.zeros((N_s, N_s))
    for i in range(N_s):
        for j in range(N_s):
            if i == j:
                cross_ic_raw[i, j] = 1.0
            else:
                r, _ = scipy.stats.spearmanr(flat[:, i], flat[:, j])
                cross_ic_raw[i, j] = float(r) if np.isfinite(r) else 0.0

    # ── 3. Ортогонализация ─────────────────────────────────────────────────────
    # Применяем ортогонализацию отдельно для каждого периода и актива
    S_ortho = np.zeros_like(S_raw)
    for t in range(T):
        S_ortho[t] = orthogonalize_signals(S_raw[t], method=ortho_method)

    # ── 4. IC ортогональных сигналов ──────────────────────────────────────────
    ortho_ic_mean = []
    ortho_ic_std = []
    ortho_ir = []
    for k in range(N_s):
        ic_list = []
        for t in range(T - 1):
            ic_list.append(_rank_ic(S_ortho[t, :, k], F_raw[t]))
        ic_arr = np.array(ic_list)
        m = float(np.nanmean(ic_arr))
        s = float(np.nanstd(ic_arr, ddof=1)) if len(ic_arr) > 1 else 1.0
        ortho_ic_mean.append(m)
        ortho_ic_std.append(s)
        ortho_ir.append(m / (s + 1e-15))

    # ── 5. Cross-IC после ортогонализации ─────────────────────────────────────
    flat_ortho = S_ortho.reshape(T * N_a, N_s)
    cross_ic_ortho = np.zeros((N_s, N_s))
    for i in range(N_s):
        for j in range(N_s):
            if i == j:
                cross_ic_ortho[i, j] = 1.0
            else:
                r, _ = scipy.stats.spearmanr(flat_ortho[:, i], flat_ortho[:, j])
                cross_ic_ortho[i, j] = float(r) if np.isfinite(r) else 0.0

    # ── 6. Оптимальные веса (из IR ортогональных сигналов) ───────────────────
    ir_arr = np.array(ortho_ir)
    weights = _optimal_weights(ir_arr, shrinkage=shrinkage)

    # ── 7. Стэкинговый сигнал ─────────────────────────────────────────────────
    # S_stack[t, a] = sum_k w_k * S_ortho[t, a, k]
    S_stack = (S_ortho * weights[np.newaxis, np.newaxis, :]).sum(axis=-1)

    # Стандартизируем
    std_stack = float(np.std(S_stack, ddof=1))
    if std_stack > 1e-15:
        S_stack = S_stack / std_stack

    # IC стэкингового сигнала
    stack_ic_list = []
    for t in range(T - 1):
        stack_ic_list.append(_rank_ic(S_stack[t], F_raw[t]))
    stack_ic_arr = np.array(stack_ic_list)
    stack_ic_mean = float(np.nanmean(stack_ic_arr))
    stack_ic_std = float(np.nanstd(stack_ic_arr, ddof=1)) if len(stack_ic_arr) > 1 else 1.0
    stack_ir = stack_ic_mean / (stack_ic_std + 1e-15)

    # ── 8. IC decay по горизонтам ─────────────────────────────────────────────
    ic_decay: Dict[str, Dict] = {}
    horizons_clipped = [h for h in ic_horizons if h < T]
    for h in horizons_clipped:
        decay_row: Dict[str, float] = {}
        for k in range(N_s):
            ic_h = []
            for t in range(T - h):
                ic_h.append(_rank_ic(S_ortho[t, :, k], F_raw[min(t + h - 1, T - 1)]))
            decay_row[signal_names[k]] = float(np.nanmean(ic_h))
        # стэк
        ic_h_stack = []
        for t in range(T - h):
            ic_h_stack.append(_rank_ic(S_stack[t], F_raw[min(t + h - 1, T - 1)]))
        decay_row["Stacked"] = float(np.nanmean(ic_h_stack))
        ic_decay[str(h)] = decay_row

    # ── 9. IC over time (h=1) для графика ─────────────────────────────────────
    ic_time_series = {
        "stacked": [float(v) for v in stack_ic_arr],
    }
    for k in range(N_s):
        ic_k = []
        for t in range(T - 1):
            ic_k.append(_rank_ic(S_ortho[t, :, k], F_raw[t]))
        ic_time_series[signal_names[k]] = [float(v) for v in ic_k]

    # ── 10. Диверсификация: avg abs cross-IC до и после ──────────────────────
    triu = np.triu_indices(N_s, k=1)
    avg_cross_ic_raw = float(np.abs(cross_ic_raw[triu]).mean()) if len(triu[0]) > 0 else 0.0
    avg_cross_ic_ortho = float(np.abs(cross_ic_ortho[triu]).mean()) if len(triu[0]) > 0 else 0.0

    # ── Сводка по сигналам ────────────────────────────────────────────────────
    signal_stats = []
    for k in range(N_s):
        signal_stats.append({
            "name": signal_names[k],
            "raw_ic": raw_ic_mean[k],
            "raw_ic_std": raw_ic_std[k],
            "raw_ir": raw_ir[k],
            "ortho_ic": ortho_ic_mean[k],
            "ortho_ic_std": ortho_ic_std[k],
            "ortho_ir": ortho_ir[k],
            "weight": float(weights[k]),
        })

    return {
        # Сводка
        "n_signals": N_s,
        "n_assets": N_a,
        "n_periods": T,
        "ortho_method": ortho_method,
        "shrinkage": shrinkage,
        # Качество стэка
        "stack_ic": stack_ic_mean,
        "stack_ic_std": stack_ic_std,
        "stack_ir": stack_ir,
        # Диверсификация
        "avg_cross_ic_before": avg_cross_ic_raw,
        "avg_cross_ic_after": avg_cross_ic_ortho,
        "diversification_ratio": (
            avg_cross_ic_raw / (avg_cross_ic_ortho + 1e-15)
            if avg_cross_ic_ortho > 1e-10 else float("inf")
        ),
        # Детали по сигналам
        "signal_stats": signal_stats,
        # Матрицы cross-IC
        "cross_ic_before": cross_ic_raw.tolist(),
        "cross_ic_after": cross_ic_ortho.tolist(),
        # IC decay по горизонтам
        "ic_decay": ic_decay,
        "ic_horizons": [str(h) for h in horizons_clipped],
        # IC во времени (h=1)
        "ic_time_series": ic_time_series,
        # Веса стэка
        "weights": {signal_names[k]: float(weights[k]) for k in range(N_s)},
    }
