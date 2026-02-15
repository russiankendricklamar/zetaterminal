"""
Многомерная скрытая марковская модель (HMM) для анализа рыночных режимов.

Теоретическая основа:
- Многомерный гауссовский HMM для K-мерного временного ряда
- Forward-Backward алгоритм для вычисления апостериорных вероятностей
- EM-алгоритм (Baum-Welch) для обучения модели

Автор: QuantPro Platform
"""

import numpy as np
import pandas as pd
from numpy.linalg import inv, det, LinAlgError
from scipy.cluster.vq import kmeans2
from typing import Dict, List, Optional, Tuple, Any
import logging
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class MultivariateHMMRegimeAnalyzer:
    """
    Анализатор скрытых рыночных режимов через многомерную HMM.
    
    Модель:
    y_t | S_t = k ~ N(μ_k, Σ_k)
    
    где:
    - S_t ∈ {1, 2, ..., M} - скрытое состояние (режим)
    - μ_k ∈ ℝ^K - вектор средних в режиме k
    - Σ_k ∈ ℝ^(K×K) - матрица ковариации в режиме k
    
    Parameters
    ----------
    n_regimes : int, default=2
        Число скрытых режимов M (обычно 2-3)
    random_state : int, default=42
        Seed для воспроизводимости
    """
    
    def __init__(self, n_regimes: int = 2, random_state: int = 42):
        self.n_regimes = n_regimes
        self.random_state = random_state
        self.n_assets = None  # K (будет установлено в fit)
        self.n_samples = None  # T (будет установлено в fit)
        
        # Параметры модели
        self.mu = None  # (M, K) матрица средних
        self.sigma = None  # (M, K, K) тензор ковариаций
        self.transition_matrix = None  # (M, M) матрица переходов
        self.pi = None  # (M,) начальное распределение
        
        # Апостериорные вероятности
        self.gamma = None  # (T, M) вероятности состояний
        self.xi = None  # (T-1, M, M) вероятности переходов
        
        # История обучения
        self.log_likelihood_history = []
        self.asset_names = None
        self.y_normalized = None
        self.y_mean = None
        self.y_std = None
        
        # Установка random seed
        np.random.seed(random_state)
    
    def fit(
        self,
        y: np.ndarray,
        asset_names: Optional[List[str]] = None,
        max_iterations: int = 50,
        tol: float = 1e-6
    ) -> 'MultivariateHMMRegimeAnalyzer':
        """
        Обучение модели на многомерном временном ряде.
        
        Parameters
        ----------
        y : np.ndarray
            (T, K) массив с временным рядом доходностей
        asset_names : list of str, optional
            Список названий активов (K элементов)
        max_iterations : int, default=50
            Максимальное число EM итераций
        tol : float, default=1e-6
            Tolerance для сходимости (изменение log-likelihood)
        
        Returns
        -------
        self
            Возвращает self для chaining
        """
        # 1. Валидация и нормализация
        y = np.asarray(y, dtype=np.float64)
        
        if y.ndim != 2:
            raise ValueError(f"y должен быть 2D массивом (T, K), получен shape: {y.shape}")
        
        T, K = y.shape
        
        if T <= K:
            raise ValueError(f"T ({T}) должно быть больше K ({K})")
        
        self.n_samples = T
        self.n_assets = K
        self.asset_names = asset_names or [f"Asset_{i+1}" for i in range(K)]
        
        if len(self.asset_names) != K:
            raise ValueError(f"asset_names должен содержать {K} элементов")
        
        # Нормализация данных
        self.y_mean = np.mean(y, axis=0, keepdims=True)
        self.y_std = np.std(y, axis=0, keepdims=True)
        self.y_std = np.where(self.y_std < 1e-8, 1.0, self.y_std)  # Избегаем деления на ноль
        
        self.y_normalized = (y - self.y_mean) / self.y_std
        
        # 2. Инициализация параметров
        self._initialize_parameters(self.y_normalized)
        
        # 3. EM итерации
        log_likelihood_old = -np.inf
        
        for iteration in range(max_iterations):
            # E-step: Forward-Backward
            alpha, beta = self.forward_backward(self.y_normalized)
            
            # Вычисление gamma и xi
            gamma, xi = self.forward_backward_posterior(self.y_normalized, alpha, beta)
            
            # M-step: Обновление параметров
            pi_new, P_new, mu_new, sigma_new = self.estimate_parameters(
                self.y_normalized, gamma, xi
            )
            
            # Обновление параметров
            self.pi = pi_new
            self.transition_matrix = P_new
            self.mu = mu_new
            self.sigma = sigma_new
            self.gamma = gamma
            self.xi = xi
            
            # Вычисление log-likelihood
            log_likelihood_new = self.compute_log_likelihood(self.y_normalized, alpha)
            self.log_likelihood_history.append(log_likelihood_new)
            
            # Проверка сходимости
            if abs(log_likelihood_new - log_likelihood_old) < tol:
                logger.info(f"Сходимость достигнута на итерации {iteration + 1}")
                break
            
            log_likelihood_old = log_likelihood_new
            
            if (iteration + 1) % 10 == 0:
                logger.debug(f"Итерация {iteration + 1}/{max_iterations}, log-likelihood: {log_likelihood_new:.4f}")
        
        return self
    
    def _initialize_parameters(self, y: np.ndarray):
        """Инициализация параметров модели."""
        T, K = y.shape
        M = self.n_regimes
        
        # Начальное распределение (равномерное)
        self.pi = np.ones(M) / M
        
        # Инициализация средних через K-means
        try:
            centroids, labels = kmeans2(y, M, minit='points', seed=self.random_state)
            self.mu = centroids  # (M, K)
        except Exception as e:
            logger.warning(f"K-means инициализация не удалась: {e}, используем случайную инициализацию")
            self.mu = np.random.randn(M, K) * 0.1
        
        # Инициализация ковариаций
        self.sigma = np.zeros((M, K, K))
        global_cov = np.cov(y.T)
        
        for k in range(M):
            # Выбираем данные, принадлежащие кластеру k
            cluster_data = y[labels == k] if 'labels' in locals() else y
            
            if len(cluster_data) > K:
                cluster_cov = np.cov(cluster_data.T)
                # Сглаживание: смешиваем с глобальной ковариацией
                alpha = 0.3
                self.sigma[k] = (1 - alpha) * cluster_cov + alpha * global_cov
            else:
                self.sigma[k] = global_cov.copy()
            
            # Регуляризация для положительной определенности
            self.sigma[k] += np.eye(K) * 1e-6
        
        # Инициализация матрицы переходов
        self.transition_matrix = np.zeros((M, M))
        for i in range(M):
            for j in range(M):
                if i == j:
                    self.transition_matrix[i, j] = 0.9
                else:
                    self.transition_matrix[i, j] = 0.1 / (M - 1)
    
    def gaussian_pdf(self, y: np.ndarray, mu: np.ndarray, sigma: np.ndarray) -> np.ndarray:
        """
        Вычислить многомерное гауссово распределение.
        
        Parameters
        ----------
        y : np.ndarray
            (T, K) или (K,) массив данных
        mu : np.ndarray
            (K,) вектор средних
        sigma : np.ndarray
            (K, K) матрица ковариации
        
        Returns
        -------
        np.ndarray
            (T,) массив значений PDF
        """
        if y.ndim == 1:
            y = y.reshape(1, -1)
        
        T, K = y.shape
        
        # Регуляризация для положительной определенности
        sigma_reg = sigma + np.eye(K) * 1e-6
        
        try:
            det_sigma = det(sigma_reg)
            if det_sigma <= 0:
                sigma_reg = sigma + np.eye(K) * 1e-4
                det_sigma = det(sigma_reg)
            
            sigma_inv = inv(sigma_reg)
        except LinAlgError:
            # Если матрица вырождена, используем диагональную
            sigma_reg = np.diag(np.diag(sigma)) + np.eye(K) * 1e-4
            det_sigma = det(sigma_reg)
            sigma_inv = inv(sigma_reg)
        
        # Вычисление PDF для каждого наблюдения
        pdf_values = np.zeros(T)
        const = 1.0 / ((2 * np.pi) ** (K / 2) * np.sqrt(det_sigma))
        
        for t in range(T):
            diff = y[t] - mu
            exponent = -0.5 * diff.T @ sigma_inv @ diff
            pdf_values[t] = const * np.exp(exponent)
        
        return pdf_values
    
    def forward_backward(self, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Вычислить forward и backward вероятности.
        
        Parameters
        ----------
        y : np.ndarray
            (T, K) нормализованный временной ряд
        
        Returns
        -------
        alpha : np.ndarray
            (T, M) forward вероятности
        beta : np.ndarray
            (T, M) backward вероятности
        """
        T, K = y.shape
        M = self.n_regimes
        
        # Forward pass
        alpha = np.zeros((T, M))
        
        # t=1
        for i in range(M):
            pdf_val = self.gaussian_pdf(y[0], self.mu[i], self.sigma[i])
            alpha[0, i] = self.pi[i] * pdf_val[0]
        
        # Нормализация для численной стабильности
        alpha_sum = np.sum(alpha[0])
        if alpha_sum > 0:
            alpha[0] = alpha[0] / alpha_sum
        else:
            alpha[0] = np.ones(M) / M
        
        # t=2..T
        for t in range(1, T):
            for i in range(M):
                pdf_val = self.gaussian_pdf(y[t], self.mu[i], self.sigma[i])
                prob = pdf_val[0]
                
                # Сумма по предыдущим состояниям
                sum_term = np.sum(self.transition_matrix[:, i] * alpha[t-1, :])
                alpha[t, i] = prob * sum_term
            
            # Нормализация
            alpha_sum = np.sum(alpha[t])
            if alpha_sum > 0:
                alpha[t] = alpha[t] / alpha_sum
            else:
                alpha[t] = np.ones(M) / M
        
        # Backward pass
        beta = np.ones((T, M))
        
        for t in range(T-2, -1, -1):
            for i in range(M):
                sum_term = 0.0
                for j in range(M):
                    pdf_val = self.gaussian_pdf(y[t+1], self.mu[j], self.sigma[j])
                    sum_term += self.transition_matrix[i, j] * pdf_val[0] * beta[t+1, j]
                beta[t, i] = sum_term
            
            # Нормализация
            beta_sum = np.sum(beta[t])
            if beta_sum > 0:
                beta[t] = beta[t] / beta_sum
            else:
                beta[t] = np.ones(M) / M
        
        return alpha, beta
    
    def forward_backward_posterior(
        self,
        y: np.ndarray,
        alpha: np.ndarray,
        beta: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Вычислить апостериорные вероятности γ и ξ.
        
        Parameters
        ----------
        y : np.ndarray
            (T, K) нормализованный временной ряд
        alpha : np.ndarray
            (T, M) forward вероятности
        beta : np.ndarray
            (T, M) backward вероятности
        
        Returns
        -------
        gamma : np.ndarray
            (T, M) вероятности состояний
        xi : np.ndarray
            (T-1, M, M) вероятности переходов
        """
        T, M = alpha.shape[0], alpha.shape[1]
        
        # Compute gamma
        gamma = np.zeros((T, M))
        for t in range(T):
            denominator = np.sum(alpha[t, :] * beta[t, :])
            if denominator > 0:
                gamma[t, :] = (alpha[t, :] * beta[t, :]) / denominator
            else:
                gamma[t, :] = 1.0 / M  # Равномерное распределение при underflow
        
        # Compute xi
        xi = np.zeros((T-1, M, M))
        for t in range(T-1):
            denominator = 0.0
            for i in range(M):
                for j in range(M):
                    pdf_val = self.gaussian_pdf(y[t+1], self.mu[j], self.sigma[j])
                    denominator += alpha[t, i] * self.transition_matrix[i, j] * pdf_val[0] * beta[t+1, j]
            
            if denominator > 0:
                for i in range(M):
                    for j in range(M):
                        pdf_val = self.gaussian_pdf(y[t+1], self.mu[j], self.sigma[j])
                        numerator = alpha[t, i] * self.transition_matrix[i, j] * pdf_val[0] * beta[t+1, j]
                        xi[t, i, j] = numerator / denominator
            else:
                # Равномерное распределение при underflow
                xi[t, :, :] = 1.0 / (M * M)
        
        return gamma, xi
    
    def estimate_parameters(
        self,
        y: np.ndarray,
        gamma: np.ndarray,
        xi: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Переоценить параметры в M-step.
        
        Parameters
        ----------
        y : np.ndarray
            (T, K) нормализованный временной ряд
        gamma : np.ndarray
            (T, M) вероятности состояний
        xi : np.ndarray
            (T-1, M, M) вероятности переходов
        
        Returns
        -------
        pi_new : np.ndarray
            (M,) новое начальное распределение
        P_new : np.ndarray
            (M, M) новая матрица переходов
        mu_new : np.ndarray
            (M, K) новые средние
        sigma_new : np.ndarray
            (M, K, K) новые ковариации
        """
        T, K = y.shape
        M = self.n_regimes
        
        # Новое начальное распределение
        pi_new = gamma[0, :].copy()
        pi_sum = np.sum(pi_new)
        pi_new = pi_new / pi_sum if pi_sum > 0 else np.ones(M) / M
        
        # Новая матрица переходов
        P_new = np.zeros((M, M))
        for i in range(M):
            denominator = np.sum(gamma[:-1, i])
            if denominator > 0:
                for j in range(M):
                    numerator = np.sum(xi[:, i, j])
                    P_new[i, j] = numerator / denominator
            else:
                # Если режим не встречается, используем равномерное распределение
                P_new[i, :] = 1.0 / M
        
        # Нормализация строк матрицы переходов
        row_sums = np.sum(P_new, axis=1, keepdims=True)
        row_sums = np.where(row_sums > 0, row_sums, 1.0)
        P_new = P_new / row_sums
        
        # Новые средние
        mu_new = np.zeros((M, K))
        for k in range(M):
            denominator = np.sum(gamma[:, k])
            if denominator > 0:
                numerator = np.sum(gamma[:, k, np.newaxis] * y, axis=0)
                mu_new[k] = numerator / denominator
            else:
                mu_new[k] = self.mu[k].copy()  # Сохраняем старое значение
        
        # Новые ковариации
        sigma_new = np.zeros((M, K, K))
        for k in range(M):
            denominator = np.sum(gamma[:, k])
            if denominator > 0:
                numerator_matrix = np.zeros((K, K))
                for t in range(T):
                    diff = y[t] - mu_new[k]
                    outer_product = np.outer(diff, diff)
                    numerator_matrix += gamma[t, k] * outer_product
                sigma_new[k] = numerator_matrix / denominator
            else:
                sigma_new[k] = self.sigma[k].copy()  # Сохраняем старое значение
            
            # Регуляризация для положительной определенности
            sigma_new[k] += np.eye(K) * 1e-6
        
        return pi_new, P_new, mu_new, sigma_new
    
    def compute_log_likelihood(self, y: np.ndarray, alpha: np.ndarray) -> float:
        """
        Вычислить логарифм правдоподобия.
        
        Parameters
        ----------
        y : np.ndarray
            (T, K) нормализованный временной ряд
        alpha : np.ndarray
            (T, M) forward вероятности
        
        Returns
        -------
        float
            Log-likelihood
        """
        T = alpha.shape[0]
        log_likelihood = 0.0
        
        for t in range(T):
            likelihood_t = np.sum(alpha[t, :])
            if likelihood_t <= 0:
                return -np.inf
            log_likelihood += np.log(max(likelihood_t, 1e-300))
        
        return log_likelihood
    
    def predict_states(self, y: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Определить наиболее вероятные состояния.
        
        Parameters
        ----------
        y : np.ndarray, optional
            (T, K) временной ряд. Если None, используется обученный ряд
        
        Returns
        -------
        np.ndarray
            (T,) массив наиболее вероятных состояний
        """
        if y is not None:
            # Нормализуем новые данные
            y_norm = (y - self.y_mean) / self.y_std
            alpha, beta = self.forward_backward(y_norm)
            gamma, _ = self.forward_backward_posterior(y_norm, alpha, beta)
        else:
            if self.gamma is None:
                raise ValueError("Модель не обучена. Вызовите fit() сначала.")
            gamma = self.gamma
        
        return np.argmax(gamma, axis=1)
    
    def get_regime_statistics(self) -> List[Dict[str, Any]]:
        """
        Получить статистику для каждого режима.
        
        Returns
        -------
        list of dict
            Список словарей со статистикой для каждого режима
        """
        if self.gamma is None:
            raise ValueError("Модель не обучена. Вызовите fit() сначала.")
        
        stats = []
        M = self.n_regimes
        
        for k in range(M):
            # Персистентность (вероятность остаться в режиме)
            persistence = self.transition_matrix[k, k]
            
            # Ожидаемая длительность (в днях)
            if persistence < 1.0:
                duration_days = -1.0 / np.log(max(persistence, 1e-300))
            else:
                duration_days = np.inf
            
            # Частота (доля времени в режиме)
            frequency = np.mean(self.gamma[:, k])
            
            # Количество дней в режиме
            most_likely = self.predict_states()
            days_in_regime = np.sum(most_likely == k)
            
            # Преобразуем средние обратно в исходную шкалу
            mu_original = self.mu[k] * self.y_std.flatten() + self.y_mean.flatten()
            
            # Преобразуем ковариацию обратно в исходную шкалу
            sigma_original = self.sigma[k] * np.outer(self.y_std.flatten(), self.y_std.flatten())
            
            # Матрица корреляции
            vol_per_asset = np.sqrt(np.diag(sigma_original))
            correlation_matrix = sigma_original / np.outer(vol_per_asset, vol_per_asset)
            correlation_matrix = np.where(np.isnan(correlation_matrix), 0.0, correlation_matrix)
            
            stats.append({
                'regime': k,
                'mean': mu_original.tolist(),
                'covariance': sigma_original.tolist(),
                'correlation': correlation_matrix.tolist(),
                'volatility_per_asset': vol_per_asset.tolist(),
                'transition_probs': self.transition_matrix[k, :].tolist(),
                'persistence': float(persistence),
                'duration_days': float(duration_days) if np.isfinite(duration_days) else None,
                'frequency': float(frequency),
                'days_in_regime': int(days_in_regime),
                'asset_names': self.asset_names
            })
        
        return stats
    
    def get_regime_at_time(self, t: int) -> Dict[str, Any]:
        """
        Получить информацию о режиме в момент t.
        
        Parameters
        ----------
        t : int
            Индекс времени
        
        Returns
        -------
        dict
            Информация о режиме в момент t
        """
        if self.gamma is None:
            raise ValueError("Модель не обучена. Вызовите fit() сначала.")
        
        if t < 0 or t >= len(self.gamma):
            raise ValueError(f"Индекс t ({t}) вне диапазона [0, {len(self.gamma)-1}]")
        
        regime_probs = self.gamma[t, :]
        most_likely = int(np.argmax(regime_probs))
        confidence = float(np.max(regime_probs))
        
        # Энтропия (мера неопределенности)
        probs_positive = regime_probs[regime_probs > 1e-10]
        entropy = -np.sum(probs_positive * np.log(probs_positive))
        
        return {
            'time_index': t,
            'regime_probabilities': regime_probs.tolist(),
            'most_likely_regime': most_likely,
            'confidence': confidence,
            'entropy': float(entropy)
        }
    
    def get_dynamic_var(self, returns: np.ndarray, confidence: float = 0.95) -> np.ndarray:
        """
        Вычислить динамический VaR по режимам.
        
        Parameters
        ----------
        returns : np.ndarray
            (T, K) массив доходностей
        confidence : float, default=0.95
            Уровень доверия для VaR
        
        Returns
        -------
        np.ndarray
            (T,) массив динамического VaR
        """
        if self.gamma is None:
            raise ValueError("Модель не обучена. Вызовите fit() сначала.")
        
        T = len(self.gamma)
        M = self.n_regimes
        
        # Вычисляем VaR для каждого режима
        var_per_regime = np.zeros(M)
        for k in range(M):
            regime_mask = self.gamma[:, k] > 0.5
            if np.sum(regime_mask) > 0:
                regime_returns = returns[regime_mask]
                # VaR как перцентиль
                var_per_regime[k] = np.percentile(regime_returns.flatten(), (1 - confidence) * 100)
            else:
                var_per_regime[k] = 0.0
        
        # Динамический VaR
        dynamic_var = np.zeros(T)
        for t in range(T):
            dynamic_var[t] = np.sum(self.gamma[t, :] * var_per_regime)
        
        return dynamic_var
    
    def simulate(self, n_steps: int = 100) -> np.ndarray:
        """
        Симулировать будущие траектории.
        
        Parameters
        ----------
        n_steps : int, default=100
            Количество шагов симуляции
        
        Returns
        -------
        np.ndarray
            (n_steps, K) симулированные траектории
        """
        if self.mu is None:
            raise ValueError("Модель не обучена. Вызовите fit() сначала.")
        
        K = self.n_assets
        M = self.n_regimes
        
        # Стартовый режим
        current_regime = np.random.choice(M, p=self.pi)
        
        # Симуляция
        trajectories = np.zeros((n_steps, K))
        
        for t in range(n_steps):
            # Выбор режима из матрицы переходов
            current_regime = np.random.choice(M, p=self.transition_matrix[current_regime, :])
            
            # Генерация наблюдения из многомерного нормального распределения
            mu_k = self.mu[current_regime]
            sigma_k = self.sigma[current_regime]
            
            # Преобразуем обратно в исходную шкалу
            mu_original = mu_k * self.y_std.flatten() + self.y_mean.flatten()
            sigma_original = sigma_k * np.outer(self.y_std.flatten(), self.y_std.flatten())
            
            # Генерация наблюдения
            observation = np.random.multivariate_normal(mu_original, sigma_original)
            trajectories[t] = observation
        
        return trajectories
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """
        Экспортировать gamma и most_likely_states в pandas DataFrame.
        
        Returns
        -------
        pd.DataFrame
            DataFrame с колонками: time_index, regime_0, ..., regime_M-1, most_likely_regime
        """
        if self.gamma is None:
            raise ValueError("Модель не обучена. Вызовите fit() сначала.")
        
        data = {
            'time_index': np.arange(len(self.gamma))
        }
        
        # Добавляем вероятности режимов
        for k in range(self.n_regimes):
            data[f'regime_{k}'] = self.gamma[:, k]
        
        # Добавляем наиболее вероятный режим
        data['most_likely_regime'] = self.predict_states()
        
        return pd.DataFrame(data)
    
    def find_optimal_n_regimes(
        self,
        y: np.ndarray,
        asset_names: Optional[List[str]] = None,
        min_regimes: int = 2,
        max_regimes: int = 5,
        criterion: str = 'aicc',
        max_iterations: int = 30,
        tol: float = 1e-6
    ) -> Tuple[int, float]:
        """
        Автоматически определить оптимальное количество режимов.
        
        Использует информационные критерии:
        - AIC = -2 * log(L) + 2 * k
        - BIC = -2 * log(L) + k * log(n)
        - AICc = AIC + (2 * k * (k + 1)) / (n - k - 1)
        
        где:
        - L - максимальное правдоподобие
        - k - число параметров модели
        - n - число наблюдений
        
        Parameters
        ----------
        y : np.ndarray
            (T, K) массив с временным рядом доходностей
        asset_names : list of str, optional
            Список названий активов
        min_regimes : int, default=2
            Минимальное число режимов для проверки
        max_regimes : int, default=5
            Максимальное число режимов для проверки
        criterion : str, default='aicc'
            Критерий для выбора: 'aic', 'bic', или 'aicc'
        max_iterations : int, default=30
            Максимальное число EM итераций для каждой модели
        tol : float, default=1e-6
            Tolerance для сходимости
        
        Returns
        -------
        optimal_n_regimes : int
            Оптимальное количество режимов
        best_criterion_value : float
            Значение критерия для оптимальной модели
        """
        y = np.asarray(y, dtype=np.float64)
        T, K = y.shape
        
        if T <= K:
            raise ValueError(f"T ({T}) должно быть больше K ({K})")
        
        criterion_values = []
        models = []
        
        for n_regimes in range(min_regimes, max_regimes + 1):
            try:
                # Создаем модель с n_regimes режимами
                model = MultivariateHMMRegimeAnalyzer(
                    n_regimes=n_regimes,
                    random_state=self.random_state
                )
                
                # Обучаем модель
                model.fit(
                    y=y,
                    asset_names=asset_names,
                    max_iterations=max_iterations,
                    tol=tol
                )
                
                # Вычисляем информационный критерий
                log_likelihood = model.log_likelihood_history[-1] if model.log_likelihood_history else -np.inf
                
                # Число параметров модели:
                # - π: (M-1) параметров (сумма = 1)
                # - P: M * (M-1) параметров (каждая строка суммируется в 1)
                # - μ: M * K параметров
                # - Σ: M * K * (K+1) / 2 параметров (симметричная матрица)
                n_params = (
                    (n_regimes - 1) +  # π
                    n_regimes * (n_regimes - 1) +  # P
                    n_regimes * K +  # μ
                    n_regimes * K * (K + 1) // 2  # Σ
                )
                
                if criterion == 'aic':
                    criterion_value = -2 * log_likelihood + 2 * n_params
                elif criterion == 'bic':
                    criterion_value = -2 * log_likelihood + n_params * np.log(T)
                elif criterion == 'aicc':
                    aic = -2 * log_likelihood + 2 * n_params
                    if T - n_params - 1 > 0:
                        aicc = aic + (2 * n_params * (n_params + 1)) / (T - n_params - 1)
                    else:
                        aicc = aic
                    criterion_value = aicc
                else:
                    raise ValueError(f"Неизвестный критерий: {criterion}")
                
                criterion_values.append(criterion_value)
                models.append(model)
                
                logger.debug(f"n_regimes={n_regimes}, {criterion.upper()}={criterion_value:.4f}, log_likelihood={log_likelihood:.4f}")
                
            except Exception as e:
                logger.warning(f"Ошибка при обучении модели с {n_regimes} режимами: {e}")
                criterion_values.append(np.inf)
                models.append(None)
        
        # Выбираем оптимальное количество режимов (минимальное значение критерия)
        if not criterion_values or all(np.isinf(criterion_values)):
            logger.warning("Не удалось обучить ни одну модель, используем min_regimes")
            optimal_n_regimes = min_regimes
            best_criterion_value = np.inf
        else:
            optimal_idx = np.argmin(criterion_values)
            optimal_n_regimes = min_regimes + optimal_idx
            best_criterion_value = criterion_values[optimal_idx]
            
            # Сохраняем оптимальную модель
            if models[optimal_idx] is not None:
                optimal_model = models[optimal_idx]
                self.n_regimes = optimal_model.n_regimes
                self.n_assets = optimal_model.n_assets
                self.n_samples = optimal_model.n_samples
                self.mu = optimal_model.mu
                self.sigma = optimal_model.sigma
                self.transition_matrix = optimal_model.transition_matrix
                self.pi = optimal_model.pi
                self.gamma = optimal_model.gamma
                self.xi = optimal_model.xi
                self.log_likelihood_history = optimal_model.log_likelihood_history
                self.asset_names = optimal_model.asset_names
                self.y_normalized = optimal_model.y_normalized
                self.y_mean = optimal_model.y_mean
                self.y_std = optimal_model.y_std
        
        return optimal_n_regimes, best_criterion_value
    
    def print_summary(self):
        """Вывести красивое резюме модели."""
        if self.gamma is None:
            print("Модель не обучена.")
            return
        
        print("=" * 80)
        print("МНОГОМЕРНАЯ HMM МОДЕЛЬ - РЕЗЮМЕ")
        print("=" * 80)
        print(f"Число активов (K): {self.n_assets}")
        print(f"Число режимов (M): {self.n_regimes}")
        print(f"Число наблюдений (T): {self.n_samples}")
        print(f"Активы: {', '.join(self.asset_names)}")
        print()
        
        for k in range(self.n_regimes):
            stats = self.get_regime_statistics()[k]
            print(f"--- РЕЖИМ {k} ---")
            print(f"Персистентность: {stats['persistence']:.4f}")
            print(f"Ожидаемая длительность: {stats['duration_days']:.2f} дней" if stats['duration_days'] else "Ожидаемая длительность: ∞")
            print(f"Доля времени: {stats['frequency']:.2%}")
            print(f"Дней в режиме: {stats['days_in_regime']}")
            print(f"Средние доходности:")
            for i, (name, mean_val) in enumerate(zip(self.asset_names, stats['mean'])):
                print(f"  {name}: {mean_val:.6f}")
            print()
        
        print("Матрица переходов:")
        print(self.transition_matrix)
        print()
        
        if self.log_likelihood_history:
            print(f"Log-likelihood (последний): {self.log_likelihood_history[-1]:.4f}")
            print(f"Итераций: {len(self.log_likelihood_history)}")
        print("=" * 80)
