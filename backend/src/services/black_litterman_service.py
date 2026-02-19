"""
Сервис для Black-Litterman оптимизации портфеля.

Реализует байесовскую модель Black-Litterman (1992):
  E[R] = [(tau*Sigma)^{-1} + P'*Omega^{-1}*P]^{-1} * [(tau*Sigma)^{-1}*pi + P'*Omega^{-1}*Q]

где:
  pi = delta * Sigma * w_mkt  — равновесные (implied) доходности
  P  — матрица выбора взглядов (K x N)
  Q  — вектор ожидаемых доходностей по взглядам (K)
  Omega — матрица неопределённости взглядов (K x K)
  tau — скаляр масштаба неопределённости рынка
"""
import numpy as np
from typing import Dict, List, Optional
import warnings

warnings.filterwarnings('ignore')


def compute_equilibrium_returns(
    cov_matrix: np.ndarray,
    market_weights: np.ndarray,
    delta: float = 2.5,
) -> np.ndarray:
    """
    Вычисляет равновесные (implied) доходности из рыночных весов.

    pi = delta * Sigma * w_mkt
    """
    return delta * cov_matrix @ market_weights


def build_omega(
    P: np.ndarray,
    cov_matrix: np.ndarray,
    tau: float,
    confidence: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Строит матрицу неопределённости взглядов Omega.

    По умолчанию: Omega = diag(P * tau * Sigma * P')  (формула He & Litterman 1999)
    Если передан вектор confidence (0..1), Omega масштабируется обратно пропорционально уверенности.
    """
    base = P @ (tau * cov_matrix) @ P.T

    if confidence is not None:
        conf = np.clip(confidence, 0.01, 1.0)
        scale = (1.0 - conf) / conf
        omega = np.diag(np.diag(base) * scale)
    else:
        omega = np.diag(np.diag(base))

    return omega


def black_litterman_posterior(
    cov_matrix: np.ndarray,
    pi: np.ndarray,
    P: np.ndarray,
    Q: np.ndarray,
    omega: np.ndarray,
    tau: float = 0.05,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Вычисляет апостериорные доходности и ковариацию Black-Litterman.

    E[R]      = M^{-1} * [(tau*Sigma)^{-1}*pi + P'*Omega^{-1}*Q]
    Sigma_post = M^{-1}   где M = (tau*Sigma)^{-1} + P'*Omega^{-1}*P
    """
    tau_sigma = tau * cov_matrix
    tau_sigma_inv = np.linalg.inv(tau_sigma)
    omega_inv = np.linalg.inv(omega)

    M = tau_sigma_inv + P.T @ omega_inv @ P
    M_inv = np.linalg.inv(M)

    posterior_mu = M_inv @ (tau_sigma_inv @ pi + P.T @ omega_inv @ Q)
    posterior_cov = M_inv

    return posterior_mu, posterior_cov


def optimal_weights_from_posterior(
    posterior_mu: np.ndarray,
    cov_matrix: np.ndarray,
    posterior_cov: np.ndarray,
    delta: float = 2.5,
    tau: float = 0.05,
) -> np.ndarray:
    """
    Вычисляет оптимальные веса из апостериорных параметров.

    w* = (delta * (Sigma + Sigma_post))^{-1} * E[R]
    """
    combined_cov = cov_matrix + posterior_cov
    w_star = np.linalg.inv(delta * combined_cov) @ posterior_mu

    # Нормализуем: sum(w) = 1, long-only
    w_star = np.maximum(w_star, 0)
    total = np.sum(w_star)
    if total > 1e-10:
        w_star = w_star / total

    return w_star


def optimize_black_litterman(
    cov_matrix: np.ndarray,
    market_weights: np.ndarray,
    views_P: np.ndarray,
    views_Q: np.ndarray,
    tau: float = 0.05,
    delta: float = 2.5,
    risk_free_rate: float = 0.0,
    confidence: Optional[np.ndarray] = None,
    asset_names: Optional[List[str]] = None,
    max_weight: float = 1.0,
) -> Dict:
    """
    Полная Black-Litterman оптимизация.

    Parameters
    ----------
    cov_matrix : (N, N) ковариационная матрица
    market_weights : (N,) рыночные (капитализационные) веса
    views_P : (K, N) матрица выбора взглядов
    views_Q : (K,) ожидаемые доходности по взглядам
    tau : скаляр масштаба
    delta : коэффициент неприятия риска
    risk_free_rate : безрисковая ставка
    confidence : (K,) уверенность во взглядах (0..1)
    asset_names : имена активов
    max_weight : ограничение максимального веса

    Returns
    -------
    Dict с ключами: optimal_weights, equilibrium_returns, posterior_returns,
                     posterior_cov, portfolio_stats, views_impact, ...
    """
    N = cov_matrix.shape[0]
    K = views_P.shape[0]

    # Валидация
    eigenvalues = np.linalg.eigvalsh(cov_matrix)
    if np.any(eigenvalues < -1e-10):
        cov_matrix = cov_matrix + (abs(np.min(eigenvalues)) + 1e-8) * np.eye(N)

    # 1. Равновесные доходности
    pi = compute_equilibrium_returns(cov_matrix, market_weights, delta)

    # 2. Omega
    omega = build_omega(views_P, cov_matrix, tau, confidence)

    # 3. Апостериорные параметры
    posterior_mu, posterior_cov = black_litterman_posterior(
        cov_matrix, pi, views_P, views_Q, omega, tau
    )

    # 4. Оптимальные веса
    w_star = optimal_weights_from_posterior(
        posterior_mu, cov_matrix, posterior_cov, delta, tau
    )

    # Ограничение максимального веса
    if max_weight < 1.0:
        w_star = np.minimum(w_star, max_weight)
        total = np.sum(w_star)
        if total > 1e-10:
            w_star = w_star / total

    # 5. Статистика портфеля
    portfolio_return = float(np.dot(w_star, posterior_mu))
    portfolio_variance = float(w_star @ cov_matrix @ w_star)
    portfolio_volatility = float(np.sqrt(portfolio_variance))
    sharpe = (
        (portfolio_return - risk_free_rate) / portfolio_volatility
        if portfolio_volatility > 1e-10
        else 0.0
    )

    # 6. Равновесные веса (без views)
    w_eq = np.linalg.inv(delta * cov_matrix) @ pi
    w_eq = np.maximum(w_eq, 0)
    total_eq = np.sum(w_eq)
    if total_eq > 1e-10:
        w_eq = w_eq / total_eq

    eq_return = float(np.dot(w_eq, pi))
    eq_variance = float(w_eq @ cov_matrix @ w_eq)
    eq_volatility = float(np.sqrt(eq_variance))
    eq_sharpe = (
        (eq_return - risk_free_rate) / eq_volatility if eq_volatility > 1e-10 else 0.0
    )

    # 7. Влияние взглядов
    views_impact = []
    for k in range(K):
        # Какие активы затрагивает этот view
        active_indices = np.nonzero(views_P[k])[0].tolist()
        active_assets = (
            [asset_names[i] for i in active_indices]
            if asset_names
            else [f"Asset_{i}" for i in active_indices]
        )

        # Отклонение апостериорной от равновесной доходности
        weight_shift = float(np.sum(w_star[active_indices] - w_eq[active_indices]))

        views_impact.append(
            {
                "view_index": k,
                "view_return": float(views_Q[k]),
                "confidence": float(confidence[k]) if confidence is not None else 0.5,
                "affected_assets": active_assets,
                "weight_shift": weight_shift,
            }
        )

    # 8. Marginal risk contributions
    marginal_risk = cov_matrix @ w_star
    total_risk = portfolio_volatility
    risk_contributions = (
        (w_star * marginal_risk / total_risk).tolist()
        if total_risk > 1e-10
        else [0.0] * N
    )

    names = asset_names or [f"Asset_{i}" for i in range(N)]

    return {
        "optimal_weights": w_star.tolist(),
        "equilibrium_weights": w_eq.tolist(),
        "equilibrium_returns": pi.tolist(),
        "posterior_returns": posterior_mu.tolist(),
        "posterior_cov": posterior_cov.tolist(),
        "risk_contributions": risk_contributions,
        "views_impact": views_impact,
        "portfolio_stats": {
            "expected_return": portfolio_return,
            "volatility": portfolio_volatility,
            "sharpe_ratio": float(sharpe),
            "num_positions": int(np.sum(w_star > 0.001)),
        },
        "equilibrium_stats": {
            "expected_return": eq_return,
            "volatility": eq_volatility,
            "sharpe_ratio": float(eq_sharpe),
        },
        "parameters": {
            "tau": tau,
            "delta": delta,
            "risk_free_rate": risk_free_rate,
            "max_weight": max_weight,
            "num_views": K,
        },
        "asset_names": names,
    }
