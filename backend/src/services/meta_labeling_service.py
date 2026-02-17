"""
Meta-Labeling (López de Prado, AFML 2018).

Pipeline:
1. Triple-Barrier Labeling: profit-take / stop-loss / time barriers → {+1, 0, -1}
2. Primary model: side prediction (rule-based или логистическая регрессия на raw features)
3. Meta-model: логистическая регрессия, предсказывает P(primary correct)
4. Bet sizing: position = primary_side × meta_probability
5. Evaluation: precision/recall/F1 + финансовые метрики (SR, hit-rate, avg bet)
"""
import numpy as np
import scipy.stats
import scipy.optimize
from typing import Dict, List, Optional, Tuple


# ── Утилиты ──────────────────────────────────────────────────────────────────

def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))


def _logistic_loss_grad(w: np.ndarray, X: np.ndarray, y: np.ndarray, lam: float):
    """BCE loss + L2 regularization, с градиентом."""
    p = _sigmoid(X @ w)
    p = np.clip(p, 1e-9, 1 - 1e-9)
    loss = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)) + lam * np.dot(w, w)
    grad = (X.T @ (p - y)) / len(y) + 2 * lam * w
    return float(loss), grad


def _fit_logistic(X: np.ndarray, y: np.ndarray, lam: float = 0.01) -> np.ndarray:
    """
    L2-регуляризованная логистическая регрессия через L-BFGS-B.
    X: (N, K+1) — с константой, y: (N,) — бинарная
    """
    w0 = np.zeros(X.shape[1])
    res = scipy.optimize.minimize(
        _logistic_loss_grad,
        w0,
        jac=True,
        args=(X, y, lam),
        method="L-BFGS-B",
        options={"maxiter": 300},
    )
    return res.x


def _add_intercept(X: np.ndarray) -> np.ndarray:
    return np.column_stack([np.ones(len(X)), X])


def _standardize(X_train: np.ndarray, X_test: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    mu = X_train.mean(axis=0)
    sd = X_train.std(axis=0) + 1e-15
    return (X_train - mu) / sd, (X_test - mu) / sd


# ── Шаг 1: Признаки ─────────────────────────────────────────────────────────

def _build_features(prices: np.ndarray, window: int = 20) -> np.ndarray:
    """
    Признаки для primary + meta моделей:
    - momentum (1-, 5-, 20-период доходность)
    - rolling vol (std returns за window)
    - z-score доходности
    - RSI-approx (avg up / avg total)
    - Возвращает матрицу (T, K) — NaN в начале обрезаются снаружи.
    """
    T = len(prices)
    rets = np.diff(np.log(prices), prepend=np.nan)  # log returns, len=T

    feats = np.full((T, 5), np.nan)
    for t in range(window, T):
        r_w = rets[t - window + 1: t + 1]
        r_w = r_w[~np.isnan(r_w)]
        if len(r_w) < 3:
            continue
        vol = float(np.std(r_w, ddof=1)) if len(r_w) > 1 else 1e-9
        # momentum at lag 1, 5, 20
        mom1 = rets[t] if not np.isnan(rets[t]) else 0.0
        mom5 = float(np.sum(rets[max(0, t - 4): t + 1])) if t >= 4 else 0.0
        mom20 = float(np.sum(rets[max(0, t - 19): t + 1])) if t >= 19 else 0.0
        z = mom1 / (vol + 1e-15)
        # RSI proxy
        up = r_w[r_w > 0].sum()
        total = np.abs(r_w).sum()
        rsi = up / (total + 1e-15)
        feats[t] = [mom1, mom5, mom20, z, rsi]

    return feats  # (T, 5)


# ── Шаг 2: Triple-Barrier Labeling ───────────────────────────────────────────

def _triple_barrier(
    prices: np.ndarray,
    t0: int,
    pt: float,    # profit-take multiplier (× daily_vol)
    sl: float,    # stop-loss multiplier  (× daily_vol)
    tmax: int,    # max holding (bars)
    daily_vol: float,
    side: int,    # primary side: +1 (long) or -1 (short)
) -> Tuple[int, float]:
    """
    Возвращает (label, return) где label ∈ {+1, -1, 0}.
    - +1: profit-take barrier hit first → profit
    - -1: stop-loss barrier hit first  → loss
    -  0: time barrier                  → neutral
    """
    pt_threshold = prices[t0] * (1.0 + side * pt * daily_vol)
    sl_threshold = prices[t0] * (1.0 - side * sl * daily_vol)

    T = len(prices)
    for dt in range(1, tmax + 1):
        t = t0 + dt
        if t >= T:
            break
        p = prices[t]
        if side == 1:
            if p >= pt_threshold:
                return +1, float(np.log(p / prices[t0]))
            if p <= sl_threshold:
                return -1, float(np.log(p / prices[t0]))
        else:
            if p <= pt_threshold:
                return +1, float(np.log(p / prices[t0]))
            if p >= sl_threshold:
                return -1, float(np.log(p / prices[t0]))

    t_end = min(t0 + tmax, T - 1)
    r = float(np.log(prices[t_end] / prices[t0]))
    return 0, side * r  # neutral


# ── Шаг 3: Primary side rule ─────────────────────────────────────────────────

def _primary_side(feats: np.ndarray) -> int:
    """
    Простое правило: side = sign(mom20 + mom5).
    +1 → long, -1 → short.
    """
    mom5 = feats[1]
    mom20 = feats[2]
    s = mom5 + mom20
    return 1 if s >= 0 else -1


# ── Шаг 4: Полный пайплайн ───────────────────────────────────────────────────

def compute_meta_labeling(
    prices: List[float],
    pt_multiplier: float = 1.5,
    sl_multiplier: float = 1.0,
    max_holding: int = 5,
    vol_window: int = 20,
    train_ratio: float = 0.7,
    regularization: float = 0.01,
    meta_threshold: float = 0.5,
) -> Dict:
    """
    Полный Meta-Labeling анализ.

    Args:
        prices: ценовой ряд (T,)
        pt_multiplier: profit-take барьер = pt × daily_vol
        sl_multiplier: stop-loss барьер  = sl × daily_vol
        max_holding: максимальный горизонт (баров)
        vol_window: окно для rolling vol
        train_ratio: доля обучающей выборки
        regularization: L2 λ для логистической регрессии
        meta_threshold: порог для бинарной мета-метки

    Returns:
        dict с метками, прогнозами, метриками, кривой equity
    """
    P = np.asarray(prices, dtype=float)
    T = len(P)
    if T < 50:
        raise ValueError(f"Нужно минимум 50 наблюдений, получено {T}")

    # 1. Признаки
    feats = _build_features(P, window=vol_window)

    # 2. Triple-barrier labeling
    records = []
    for t in range(vol_window, T - max_holding - 1):
        f = feats[t]
        if np.any(np.isnan(f)):
            continue
        # rolling daily vol
        rets_w = np.diff(np.log(P[max(0, t - vol_window): t + 1]))
        daily_vol = float(np.std(rets_w, ddof=1)) if len(rets_w) > 1 else 1e-4
        if daily_vol < 1e-8:
            continue

        primary_side = _primary_side(f)
        label, ret = _triple_barrier(P, t, pt_multiplier, sl_multiplier, max_holding, daily_vol, primary_side)
        records.append((t, primary_side, label, ret, f.copy(), daily_vol))

    if len(records) < 20:
        raise ValueError("Недостаточно меток после triple-barrier (нужно ≥ 20)")

    records_arr = records  # list of tuples

    # 3. Разбиваем на train/test
    n = len(records_arr)
    n_train = max(10, int(n * train_ratio))
    train = records_arr[:n_train]
    test = records_arr[n_train:]

    if len(test) < 5:
        raise ValueError("Слишком мало тестовых точек (< 5)")

    # 4. Primary model: оцениваем первичное качество
    # Используем логистическую регрессию для предсказания sign(ret) > 0
    def make_Xy(recs):
        X = np.array([r[4] for r in recs])    # (N, 5) features
        # primary label: было ли выгодным?
        y = np.array([1.0 if r[3] > 0 else 0.0 for r in recs])
        sides = np.array([r[1] for r in recs])
        labels = np.array([r[2] for r in recs])
        rets = np.array([r[3] for r in recs])
        t_idx = np.array([r[0] for r in recs])
        return X, y, sides, labels, rets, t_idx

    X_tr, y_tr, sides_tr, labels_tr, rets_tr, t_tr = make_Xy(train)
    X_te, y_te, sides_te, labels_te, rets_te, t_te = make_Xy(test)

    # Стандартизация
    X_tr_s, X_te_s = _standardize(X_tr, X_te)

    # 4a. Логистическая регрессия (первичная модель — предсказывает side direction)
    # Для простоты используем те же признаки, side = sign(mom20+mom5) → уже в records
    # Оцениваем first-pass accuracy на train
    primary_hits_tr = float(np.mean((sides_tr > 0) == (rets_tr > 0)))
    primary_hits_te = float(np.mean((sides_te > 0) == (rets_te > 0)))

    # 4b. Meta-model: предсказываем является ли ставка primary_side profitable
    # Meta-label: 1 если primary_side привёл к прибыли (ret > 0), иначе 0
    # Используем РАСШИРЕННЫЕ признаки: [feats, |side|, label != 0]
    X_meta_tr = X_tr_s
    X_meta_te = X_te_s

    w_meta = _fit_logistic(_add_intercept(X_meta_tr), y_tr, lam=regularization)

    # Predict probability
    prob_tr = _sigmoid(_add_intercept(X_meta_tr) @ w_meta)
    prob_te = _sigmoid(_add_intercept(X_meta_te) @ w_meta)

    # 5. Evaluation metrics
    def _metrics(y_true: np.ndarray, prob: np.ndarray, threshold: float, rets: np.ndarray) -> Dict:
        pred = (prob >= threshold).astype(float)
        tp = float(np.sum((pred == 1) & (y_true == 1)))
        fp = float(np.sum((pred == 1) & (y_true == 0)))
        fn = float(np.sum((pred == 0) & (y_true == 1)))
        tn = float(np.sum((pred == 0) & (y_true == 0)))

        precision = tp / (tp + fp + 1e-15)
        recall = tp / (tp + fn + 1e-15)
        f1 = 2 * precision * recall / (precision + recall + 1e-15)
        accuracy = (tp + tn) / (tp + fp + fn + tn + 1e-15)

        # Financial: bet only when pred=1, size = probability
        bet_mask = pred == 1
        if bet_mask.sum() > 0:
            bet_rets = rets[bet_mask] * prob[bet_mask]  # scaled by confidence
            sr = float(np.mean(bet_rets) / (np.std(bet_rets, ddof=1) + 1e-15))
            avg_bet = float(prob[bet_mask].mean())
            bet_count = int(bet_mask.sum())
        else:
            sr, avg_bet, bet_count = 0.0, 0.0, 0

        # vs no-filter baseline
        raw_sr = float(np.mean(rets) / (np.std(rets, ddof=1) + 1e-15))

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "accuracy": accuracy,
            "sr": sr,
            "raw_sr": raw_sr,
            "avg_bet_size": avg_bet,
            "n_bets": bet_count,
            "n_total": int(len(y_true)),
        }

    train_metrics = _metrics(y_tr, prob_tr, meta_threshold, rets_tr)
    test_metrics = _metrics(y_te, prob_te, meta_threshold, rets_te)

    # 6. Equity curves
    # Baseline: every signal, size=1
    # Meta: only when prob >= threshold, size=prob
    def _equity_curve(rets: np.ndarray, sides: np.ndarray, probs: np.ndarray, threshold: float):
        baseline = np.cumsum(sides * rets * 0)  # placeholder
        baseline = np.cumsum(rets)
        bet_mask = probs >= threshold
        meta_rets = np.where(bet_mask, rets * probs, 0.0)
        meta_eq = np.cumsum(meta_rets)
        return baseline.tolist(), meta_eq.tolist()

    baseline_eq, meta_eq = _equity_curve(rets_te, sides_te, prob_te, meta_threshold)

    # 7. Prob distribution
    hist_counts, hist_edges = np.histogram(prob_te, bins=20, range=(0, 1))

    # 8. Feature importances (коэф. логистической регрессии)
    feat_names = ["mom1", "mom5", "mom20", "z_score", "rsi"]
    importances = {feat_names[k]: float(w_meta[k + 1]) for k in range(len(feat_names))}

    # 9. Threshold sweep (precision-recall curve)
    thresholds = np.linspace(0.3, 0.9, 25)
    pr_curve = []
    for thr in thresholds:
        pred = (prob_te >= thr).astype(float)
        tp = float(np.sum((pred == 1) & (y_te == 1)))
        fp = float(np.sum((pred == 1) & (y_te == 0)))
        fn = float(np.sum((pred == 0) & (y_te == 1)))
        prec = tp / (tp + fp + 1e-15)
        rec = tp / (tp + fn + 1e-15)
        n_bets = int(pred.sum())
        pr_curve.append({
            "threshold": round(float(thr), 2),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "n_bets": n_bets,
        })

    # 10. Label distribution
    unique, counts = np.unique(labels_te, return_counts=True)
    label_dist = {int(u): int(c) for u, c in zip(unique, counts)}

    return {
        # Config
        "n_samples": int(n),
        "n_train": n_train,
        "n_test": int(len(test)),
        "pt_multiplier": pt_multiplier,
        "sl_multiplier": sl_multiplier,
        "max_holding": max_holding,
        "meta_threshold": meta_threshold,
        # Primary model
        "primary_accuracy_train": primary_hits_tr,
        "primary_accuracy_test": primary_hits_te,
        # Meta metrics
        "train_metrics": train_metrics,
        "test_metrics": test_metrics,
        # Equity curves (test set)
        "equity_baseline": baseline_eq,
        "equity_meta": meta_eq,
        # Probability histogram
        "prob_hist": {
            "counts": hist_counts.tolist(),
            "bin_edges": hist_edges.tolist(),
        },
        # PR curve
        "pr_curve": pr_curve,
        # Feature importances (logistic weights)
        "feature_importances": importances,
        "feature_names": feat_names,
        # Label distribution
        "label_distribution": label_dist,
        # Probabilities (test, for scatter)
        "test_probs": prob_te.tolist(),
        "test_returns": rets_te.tolist(),
        "test_labels": y_te.tolist(),
    }
