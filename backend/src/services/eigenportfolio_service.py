"""
Сервис для анализа Eigenportfolios (PCA декомпозиция ковариационной матрицы).

Реализует:
- Спектральное разложение Σ = QΛQᵀ
- Eigenportfolios: столбцы Q — ортогональные, некоррелированные портфели
- Explained variance и кумулятивный scree plot
- Shrinkage: Ledoit-Wolf (sklearn) для улучшенной оценки Σ
- Random Matrix Theory (Marchenko-Pastur): отделение сигнала от шума
- Реконструкция Σ с K < N главными компонентами
- Декомпозиция риска портфеля на вклады PC
"""
import numpy as np
import scipy.stats
from typing import Dict, List, Optional, Tuple


# ── Marchenko-Pastur распределение ────────────────────────────────────────────

def _marchenko_pastur_bounds(sigma2: float, q: float) -> Tuple[float, float]:
    """
    Границы Маршенко-Пастура для собственных значений матрицы шума.
    q = N/T (отношение числа переменных к числу наблюдений).
    λ₋ = σ²(1 − √q)², λ₊ = σ²(1 + √q)²
    Собственные значения выше λ₊ считаются сигналом.
    """
    lam_minus = sigma2 * (1.0 - np.sqrt(q)) ** 2
    lam_plus = sigma2 * (1.0 + np.sqrt(q)) ** 2
    return float(lam_minus), float(lam_plus)


def _marchenko_pastur_pdf(x: np.ndarray, sigma2: float, q: float) -> np.ndarray:
    """Плотность Маршенко-Пастура для overlay на гистограмму собственных значений."""
    lam_minus, lam_plus = _marchenko_pastur_bounds(sigma2, q)
    pdf = np.zeros_like(x)
    mask = (x >= lam_minus) & (x <= lam_plus)
    xm = x[mask]
    pdf[mask] = (
        np.sqrt((lam_plus - xm) * (xm - lam_minus))
        / (2.0 * np.pi * sigma2 * q * xm)
    )
    return pdf


# ── Ledoit-Wolf shrinkage ─────────────────────────────────────────────────────

def _ledoit_wolf_shrinkage(X: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Ledoit-Wolf аналитический shrinkage для ковариационной матрицы.
    Σ_LW = (1 − α) · S + α · μ · I
    где μ = trace(S)/N — shrinkage target (scaled identity).
    Возвращает (Σ_LW, α).
    """
    T, N = X.shape
    S = np.cov(X.T, ddof=1)  # выборочная ковариационная матрица N×N

    # Аналитические формулы Ledoit-Wolf (2004, Analytical Shrinkage)
    # Оптимальный α минимизирует E[||Σ_LW − Σ||²_F]
    mu = float(np.trace(S) / N)

    # delta²: squared Frobenius norm of S - mu*I (numerator of shrinkage)
    delta2 = float(np.sum((S - mu * np.eye(N)) ** 2))

    # beta_bar²: mean of squared sum of outer products (variance of sample cov)
    X_c = X - X.mean(axis=0)
    beta2_sum = 0.0
    for t in range(T):
        xi = X_c[t]
        outer = np.outer(xi, xi)
        beta2_sum += float(np.sum((outer - S) ** 2))
    beta2 = beta2_sum / (T ** 2)

    alpha = min(beta2 / delta2, 1.0) if delta2 > 0 else 0.0
    Sigma_lw = (1.0 - alpha) * S + alpha * mu * np.eye(N)

    return Sigma_lw, float(alpha)


# ── Главная функция ───────────────────────────────────────────────────────────

def compute_eigenportfolios(
    returns: List[List[float]],
    asset_names: Optional[List[str]] = None,
    use_shrinkage: bool = True,
    n_components: Optional[int] = None,
    portfolio_weights: Optional[List[float]] = None,
) -> Dict:
    """
    PCA декомпозиция ковариационной матрицы доходностей.

    Args:
        returns: матрица T × N доходностей
        asset_names: названия N активов
        use_shrinkage: применять Ledoit-Wolf shrinkage
        n_components: число PC для реконструкции (None = все)
        portfolio_weights: веса текущего портфеля для декомпозиции риска

    Returns:
        dict с eigenvalues, eigenvectors, explained variance, RMT bounds,
        PC scores, risk decomposition, reconstruction error
    """
    R = np.asarray(returns, dtype=float)
    if R.ndim == 1:
        R = R[:, None]

    T, N = R.shape
    if T < N + 5:
        raise ValueError(f"Недостаточно наблюдений: T={T}, N={N}. Нужно T > N+5.")
    if N < 2:
        raise ValueError("Нужно минимум 2 актива.")

    if asset_names is None:
        asset_names = [f"Asset_{i+1}" for i in range(N)]
    if len(asset_names) != N:
        raise ValueError(f"Ожидается {N} названий активов, получено {len(asset_names)}")

    # ── Ковариационная матрица ───────────────────────────────────────────────
    if use_shrinkage:
        Sigma, shrink_alpha = _ledoit_wolf_shrinkage(R)
    else:
        Sigma = np.cov(R.T, ddof=1)
        shrink_alpha = 0.0

    # ── Спектральное разложение Σ = QΛQᵀ ────────────────────────────────────
    # Сортируем по убыванию собственных значений
    eigenvalues, eigenvectors = np.linalg.eigh(Sigma)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]   # N × N, столбцы = PC

    # Нормализуем знак: первый ненулевой элемент каждого PC положителен
    for k in range(N):
        if eigenvectors[:, k][np.abs(eigenvectors[:, k]).argmax()] < 0:
            eigenvectors[:, k] *= -1

    # ── Explained variance ───────────────────────────────────────────────────
    total_var = float(eigenvalues.sum())
    explained_var = (eigenvalues / total_var).tolist()
    cumulative_var = np.cumsum(eigenvalues / total_var).tolist()

    # Число PC для 80%, 90%, 95% объяснённой дисперсии
    thresholds = {}
    for thr in [0.80, 0.90, 0.95]:
        for k, cv in enumerate(cumulative_var):
            if cv >= thr:
                thresholds[f"pc_{int(thr*100)}pct"] = k + 1
                break

    # ── Marchenko-Pastur (RMT) ───────────────────────────────────────────────
    q = N / T  # ratio
    sigma2_noise = float(np.median(eigenvalues))  # оценка дисперсии шума через медиану
    lam_minus, lam_plus = _marchenko_pastur_bounds(sigma2_noise, q)

    # Число "сигнальных" PC (собственные значения выше λ₊)
    n_signal = int(np.sum(eigenvalues > lam_plus))
    n_noise = N - n_signal

    # PDF Маршенко-Пастура для оверлея
    ev_range = np.linspace(max(0.0, lam_minus * 0.5), lam_plus * 1.5, 200)
    mp_pdf = _marchenko_pastur_pdf(ev_range, sigma2_noise, q)

    # ── PC scores (проекция доходностей на PC) ────────────────────────────────
    R_centered = R - R.mean(axis=0)
    K = n_components if n_components is not None else min(N, 10)
    K = min(K, N)
    scores = (R_centered @ eigenvectors[:, :K]).tolist()  # T × K

    # ── Реконструкция Σ с K компонентами ─────────────────────────────────────
    lam_k = eigenvalues[:K]
    Q_k = eigenvectors[:, :K]
    Sigma_recon = Q_k @ np.diag(lam_k) @ Q_k.T

    # Ошибка реконструкции: ||Σ − Σ_K||_F / ||Σ||_F
    recon_error = float(np.linalg.norm(Sigma - Sigma_recon, 'fro') / (np.linalg.norm(Sigma, 'fro') + 1e-15))

    # ── Декомпозиция риска портфеля ──────────────────────────────────────────
    port_risk_decomp = None
    if portfolio_weights is not None and len(portfolio_weights) == N:
        w = np.asarray(portfolio_weights, dtype=float)
        w = w / (w.sum() + 1e-15)
        port_var = float(w @ Sigma @ w)
        port_vol = float(np.sqrt(max(port_var, 0.0)))

        # Вклад каждого PC: var_k = (wᵀqₖ)² · λₖ
        pc_contributions = []
        for k in range(N):
            exposure = float(w @ eigenvectors[:, k])
            contrib_var = float(exposure ** 2 * eigenvalues[k])
            pc_contributions.append({
                "pc": k + 1,
                "exposure": float(exposure),
                "var_contribution": contrib_var,
                "share": float(contrib_var / port_var) if port_var > 0 else 0.0,
            })

        port_risk_decomp = {
            "portfolio_variance": port_var,
            "portfolio_vol": port_vol,
            "pc_contributions": pc_contributions[:min(K, 10)],
        }

    # ── Данные для scree plot ─────────────────────────────────────────────────
    n_show = min(N, 30)

    return {
        # Eigenvalues / vectors
        "eigenvalues": eigenvalues[:n_show].tolist(),
        "eigenvectors": eigenvectors[:, :min(K, N)].tolist(),  # N × K
        "explained_variance": explained_var[:n_show],
        "cumulative_variance": cumulative_var[:n_show],
        "total_variance": float(total_var),
        # PC structure
        "n_components_used": int(K),
        "n_components_total": int(N),
        "thresholds": thresholds,
        # Marchenko-Pastur
        "rmt": {
            "lambda_minus": float(lam_minus),
            "lambda_plus": float(lam_plus),
            "sigma2_noise": float(sigma2_noise),
            "q": float(q),
            "n_signal": int(n_signal),
            "n_noise": int(n_noise),
            "mp_x": ev_range.tolist(),
            "mp_pdf": mp_pdf.tolist(),
        },
        # Shrinkage
        "shrinkage": {
            "applied": bool(use_shrinkage),
            "alpha": float(shrink_alpha),
        },
        # PC scores (для графика)
        "pc_scores": scores,
        # Reconstruction
        "reconstruction_error": float(recon_error),
        # Heatmap: загрузки активов на PC (N × K)
        "loadings": [
            {
                "asset": asset_names[i],
                "loadings": eigenvectors[i, :K].tolist(),
            }
            for i in range(N)
        ],
        # Risk decomposition
        "portfolio_risk": port_risk_decomp,
        "asset_names": asset_names,
        "n_assets": int(N),
        "n_periods": int(T),
    }
