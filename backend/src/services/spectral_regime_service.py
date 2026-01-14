"""
Комплексный анализ скрытых рыночных режимов через спектральную плотность.

Теоретическая основа:
Для стационарного временного ряда {y_t} спектральная плотность определяется как:
f(ω) = (1/2π) * Σ(h=-∞ до ∞) γ(h) * exp(-i*ω*h),  где ω ∈ [-π, π]

Мероморфное расширение на комплексную плоскость:
Γ(z) = Σ(h=-∞ до ∞) γ(h) * z^h,  где z ∈ ℂ

Полюсы спектра λ_k определяют рыночные режимы:
- |λ_k| < 0.5: шум
- 0.5 < |λ_k| < 0.8: переходный режим
- 0.8 < |λ_k| < 0.95: нормальный режим
- 0.95 < |λ_k| < 0.999: стрессовый режим
- |λ_k| ≥ 0.999: кризис

Автор: QuantPro Platform
"""

import numpy as np
from numpy.linalg import eig, lstsq, LinAlgError
from scipy.linalg import hankel
from scipy.signal import hilbert
from scipy.cluster.hierarchy import fclusterdata
from typing import Dict, List, Optional, Tuple, Any
import warnings

warnings.filterwarnings('ignore')


class SpectralRegimeAnalyzer:
    """
    Анализатор скрытых рыночных режимов через комплексный анализ спектральной плотности.
    
    Использует метод Prony для идентификации полюсов спектра,
    иерархическую кластеризацию для группировки полюсов в режимы,
    и анализ минимальной фазы через преобразование Гильберта.
    
    Parameters
    ----------
    max_lag : int, optional
        Максимальный лаг для автокорреляционной функции.
        Если None, устанавливается T//4
    n_poles : int, default=5
        Количество полюсов M для идентификации (5-10 рекомендуется)
    window_size : int, default=20
        Размер скользящего окна W для динамического анализа (10-30 дней)
    
    Attributes
    ----------
    poles : ndarray
        Идентифицированные полюсы (комплексные)
    residues : ndarray
        Остатки полюсов (амплитуды режимов)
    regime_poles : ndarray
        Средние полюсы для каждого режима
    K : int
        Количество идентифицированных режимов
    regime_params : dict
        Параметры каждого режима (радиус, длительность, тип)
    is_minimum_phase : bool
        Признак минимально-фазовой системы
    regime_signal : ndarray
        Временной ряд доминирующих режимов
    entropy : ndarray
        Временной ряд энтропии режимности
    """
    
    def __init__(
        self,
        max_lag: Optional[int] = None,
        n_poles: Optional[int] = 5,
        window_size: Optional[int] = 20
    ):
        """
        Инициализация анализатора.
        
        Parameters
        ----------
        max_lag : int, optional
            Максимальный лаг для ACF. Если None, установить T//4
        n_poles : int
            Количество полюсов M для идентификации (5-10)
        window_size : int
            Размер скользящего окна W для динамического анализа (10-30 дней)
        """
        self.max_lag = max_lag
        self.n_poles = n_poles
        self.window_size = window_size
        
        # Результаты анализа
        self.poles: Optional[np.ndarray] = None
        self.residues: Optional[np.ndarray] = None
        self.regime_poles: Optional[np.ndarray] = None
        self.pole_clusters: Dict = {}
        self.K: int = 0
        
        # Данные
        self.y: Optional[np.ndarray] = None
        self.T: int = 0
        self.acf: Optional[np.ndarray] = None
        
        # Спектральный анализ
        self.omega: Optional[np.ndarray] = None
        self.H_spectrum: Optional[np.ndarray] = None
        self.amplitude_spectrum: Optional[np.ndarray] = None
        self.log_amplitude_spectrum: Optional[np.ndarray] = None
        self.phase_spectrum: Optional[np.ndarray] = None
        self.is_minimum_phase: bool = False
        
        # Динамический анализ
        self.regime_signal: Optional[np.ndarray] = None
        self.regime_energies: Optional[np.ndarray] = None
        self.entropy: Optional[np.ndarray] = None
        self.regime_params: Dict = {}
    
    def compute_acf(self, y: np.ndarray) -> np.ndarray:
        """
        Вычислить автокорреляционную функцию из данных.
        
        Формула:
        γ(h) = (1/T) * Σ(t=0 до T-h-1) (y_t - ȳ)(y_{t+h} - ȳ)
        
        Parameters
        ----------
        y : ndarray
            Временной ряд размерности (T,)
        
        Returns
        -------
        acf : ndarray
            Автоковариация для лагов 0...max_lag, размерность (max_lag+1,)
        
        Raises
        ------
        ValueError
            Если y не 1D array или max_lag >= T
        """
        y = np.asarray(y).flatten()
        T = len(y)
        
        if y.ndim != 1 or len(y.shape) > 1:
            raise ValueError("y должен быть одномерным массивом")
        
        if self.max_lag is None:
            self.max_lag = T // 4
        
        if self.max_lag >= T:
            raise ValueError(f"max_lag ({self.max_lag}) должен быть меньше T ({T})")
        
        # Центрирование данных
        y_centered = y - np.mean(y)
        
        # Вычисление автоковариации для каждого лага
        acf = np.zeros(self.max_lag + 1)
        for h in range(self.max_lag + 1):
            acf[h] = np.mean(y_centered[:T-h] * y_centered[h:]) if T-h > 0 else 0.0
        
        # Нормализация (делим на дисперсию для получения автокорреляции)
        if acf[0] > 0:
            acf = acf / acf[0]
        
        self.acf = acf
        return acf
    
    def prony_method(self, acf: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Идентифицировать полюсы методом Prony через eigendecomposition матрицы Hankel.
        
        Алгоритм:
        1. Построить матрицу Hankel из ACF
        2. Решить обобщённую проблему собственных значений
        3. Извлечь полюсы и вычислить остатки
        
        Parameters
        ----------
        acf : ndarray
            Автоковариация размерности (H+1,)
        
        Returns
        -------
        poles : ndarray
            Комплексные полюсы размерности (M,)
        residues : ndarray
            Остатки (амплитуды) размерности (M,)
        """
        H = len(acf) - 1
        M = min(self.n_poles, H // 2 - 1)
        
        if M < 2:
            M = 2
        
        try:
            # Шаг 1: Построение матрицы Hankel
            # Используем scipy.linalg.hankel
            c = acf[:H-M+1]
            r = acf[H-M:H+1]
            hankel_matrix = hankel(c, r)
            
            # Шаг 2: Обобщённая проблема собственных значений
            # Γ_upper = Hankel[:-1, :-1]
            # Γ_lower = Hankel[1:, :-1]
            n = hankel_matrix.shape[0]
            if n < 2:
                raise ValueError("Матрица Hankel слишком мала")
            
            Gamma_upper = hankel_matrix[:-1, :-1]
            Gamma_lower = hankel_matrix[1:, :-1]
            
            # Регуляризация для численной стабильности
            reg = 1e-8 * np.eye(Gamma_lower.shape[0])
            Gamma_lower_reg = Gamma_lower + reg
            
            # Решение обобщённой проблемы собственных значений
            eigenvalues, _ = eig(Gamma_upper, Gamma_lower_reg)
            
            # Фильтрация: оставляем только конечные и стабильные
            valid_mask = np.isfinite(eigenvalues) & (np.abs(eigenvalues) < 10)
            eigenvalues = eigenvalues[valid_mask]
            
            if len(eigenvalues) == 0:
                eigenvalues = np.array([0.5 + 0.1j, 0.5 - 0.1j, 0.3])
            
            # Сортировка по модулю (убывание)
            sorted_idx = np.argsort(-np.abs(eigenvalues))
            poles = eigenvalues[sorted_idx][:M]
            
            # Шаг 3: Расчёт остатков через решение линейной системы
            # A * R = γ̂_vector
            # A[h, k] = λ_k^h
            n_residues = len(poles)
            A = np.zeros((n_residues, n_residues), dtype=complex)
            for h in range(n_residues):
                for k in range(n_residues):
                    A[h, k] = poles[k] ** h
            
            gamma_vector = acf[:n_residues].astype(complex)
            
            try:
                residues, _, _, _ = lstsq(A, gamma_vector, rcond=None)
            except LinAlgError:
                residues = np.ones(n_residues, dtype=complex) / n_residues
            
        except Exception as e:
            # Fallback: равномерно распределённые полюсы
            print(f"Prony method warning: {e}, используем fallback")
            poles = np.array([
                0.85 * np.exp(1j * 0.1),
                0.85 * np.exp(-1j * 0.1),
                0.6 + 0j,
                0.4 + 0j,
                0.2 + 0j
            ])[:M]
            residues = np.ones(M, dtype=complex) / M
        
        self.poles = poles
        self.residues = residues
        return poles, residues
    
    def cluster_poles(
        self,
        poles: np.ndarray,
        threshold: float = 0.15
    ) -> Tuple[np.ndarray, Dict, int]:
        """
        Кластеризовать полюсы в режимы через иерархическую кластеризацию.
        
        Parameters
        ----------
        poles : ndarray
            Комплексные полюсы размерности (M,)
        threshold : float
            Порог δ для объединения полюсов (по умолчанию 0.15)
        
        Returns
        -------
        regime_poles : ndarray
            Средние полюсы для каждого режима (K,)
        pole_clusters : dict
            Словарь {cluster_id: [indices полюсов]}
        K : int
            Количество режимов
        """
        # Преобразуем комплексные полюсы в 2D координаты для кластеризации
        poles_2d = np.column_stack([poles.real, poles.imag])
        
        # Иерархическая кластеризация
        if len(poles) > 1:
            # fclusterdata автоматически выбирает количество кластеров
            clusters = fclusterdata(
                poles_2d,
                t=threshold,
                criterion='distance',
                method='average'
            )
        else:
            clusters = np.array([1])
        
        # Группировка полюсов по кластерам
        unique_clusters = np.unique(clusters)
        K = len(unique_clusters)
        
        regime_poles = np.zeros(K, dtype=complex)
        pole_clusters = {}
        
        for i, cluster_id in enumerate(unique_clusters):
            mask = clusters == cluster_id
            indices = np.where(mask)[0]
            pole_clusters[i] = indices.tolist()
            
            # Средний полюс для кластера
            regime_poles[i] = np.mean(poles[mask])
        
        # Сортировка режимов по радиусу (убывание)
        sorted_idx = np.argsort(-np.abs(regime_poles))
        regime_poles = regime_poles[sorted_idx]
        
        # Переназначение кластеров
        new_clusters = {}
        for new_i, old_i in enumerate(sorted_idx):
            new_clusters[new_i] = pole_clusters[old_i]
        
        self.regime_poles = regime_poles
        self.pole_clusters = new_clusters
        self.K = K
        
        return regime_poles, new_clusters, K
    
    @staticmethod
    def classify_regime_type(radius: float) -> str:
        """
        Классифицировать тип режима по радиусу полюса.
        
        Parameters
        ----------
        radius : float
            Модуль полюса |λ_k|
        
        Returns
        -------
        str
            Тип режима: "Noise", "Transient", "Normal", "Stress", "Crisis"
        """
        if radius < 0.5:
            return "Noise"
        elif radius < 0.8:
            return "Transient"
        elif radius < 0.95:
            return "Normal"
        elif radius < 0.999:
            return "Stress"
        else:
            return "Crisis"
    
    def regime_parameters(self) -> Dict:
        """
        Вычислить параметры каждого режима.
        
        Для каждого режима k с полюсом λ_k = r_k * exp(i*θ_k):
        - radius = |λ_k|
        - angle = arg(λ_k)
        - duration = -1 / ln(radius) дней
        - intensity = |R_k|
        - type = classify_regime_type(radius)
        
        Returns
        -------
        regime_params : dict
            Параметры для каждого режима
        """
        if self.regime_poles is None:
            raise ValueError("Сначала необходимо выполнить cluster_poles()")
        
        self.regime_params = {}
        
        for k in range(self.K):
            pole = self.regime_poles[k]
            radius = np.abs(pole)
            angle = np.angle(pole)
            
            # Длительность (персистентность) в днях
            # τ = -1 / ln(|λ|)
            duration = -1.0 / (np.log(radius + 1e-10) + 1e-10)
            
            # Периодичность
            if np.abs(angle) > 1e-6:
                periodicity = 2 * np.pi / np.abs(angle)
            else:
                periodicity = float('inf')  # Тренд
            
            # Интенсивность - средняя амплитуда остатков полюсов в кластере
            cluster_indices = self.pole_clusters.get(k, [])
            if len(cluster_indices) > 0 and self.residues is not None:
                intensity = np.mean(np.abs(self.residues[cluster_indices]))
            else:
                intensity = 0.1
            
            regime_type = self.classify_regime_type(radius)
            
            self.regime_params[k] = {
                'pole': complex(pole),
                'radius': float(radius),
                'angle': float(angle),
                'duration': float(duration),
                'periodicity': float(periodicity),
                'intensity': float(intensity),
                'type': regime_type
            }
        
        return self.regime_params
    
    def spectral_factorization(self) -> None:
        """
        Вычислить спектральную плотность и её амплитуду на частотах.
        
        Формула:
        H(e^{iω}) = Σ(k=1 до M) R_k / (1 - λ_k * exp(-i*ω))
        
        Результаты сохраняются в атрибуты:
        - self.omega: частоты
        - self.H_spectrum: комплексный спектр
        - self.amplitude_spectrum: |H|
        - self.log_amplitude_spectrum: log|H|
        """
        if self.poles is None or self.residues is None:
            raise ValueError("Сначала необходимо выполнить prony_method()")
        
        # Частотный массив
        N = 512
        self.omega = np.linspace(-np.pi, np.pi, N)
        
        # Вычисление спектра для каждой частоты
        H = np.zeros(N, dtype=complex)
        
        for i, omega in enumerate(self.omega):
            z = np.exp(1j * omega)
            for k in range(len(self.poles)):
                denominator = 1 - self.poles[k] * np.exp(-1j * omega)
                if np.abs(denominator) > 1e-10:
                    H[i] += self.residues[k] / denominator
        
        self.H_spectrum = H
        self.amplitude_spectrum = np.abs(H)
        self.log_amplitude_spectrum = np.log(self.amplitude_spectrum + 1e-10)
    
    def minimum_phase_recovery(self) -> None:
        """
        Восстановить фазу через преобразование Гильберта (Kramers-Kronig).
        
        Для минимально-фазовой системы:
        φ(ω) = -H{log|H(e^{iω})|}
        
        Результаты:
        - self.phase_spectrum: восстановленная фаза
        - self.is_minimum_phase: признак минимальной фазы
        """
        if self.log_amplitude_spectrum is None:
            raise ValueError("Сначала необходимо выполнить spectral_factorization()")
        
        log_amp = self.log_amplitude_spectrum
        
        # Периодическое расширение для FFT
        log_amp_ext = np.concatenate([log_amp[::-1], log_amp])
        
        # Преобразование Гильберта
        analytic = hilbert(log_amp_ext)
        phase_ext = np.unwrap(np.angle(analytic))
        
        # Извлечение фазы на исходных частотах
        N = len(log_amp)
        self.phase_spectrum = phase_ext[N:]
        
        # Проверка минимально-фазового условия
        # Все полюсы должны быть внутри единичного круга
        if self.poles is not None:
            all_inside = np.all(np.abs(self.poles) < 1.0)
            self.is_minimum_phase = all_inside
        else:
            self.is_minimum_phase = False
    
    def dynamic_regime_analysis(self, y: np.ndarray) -> None:
        """
        Анализ режимов в скользящем окне.
        
        Для каждого момента t вычисляется:
        - Энергия каждого режима E_k(t)
        - Нормализованные вероятности P̃_k(t)
        - Доминирующий режим S_t
        - Энтропия режимности H(t)
        
        Parameters
        ----------
        y : ndarray
            Временной ряд размерности (T,)
        """
        if self.regime_poles is None or self.K == 0:
            raise ValueError("Сначала необходимо выполнить cluster_poles()")
        
        T = len(y)
        W = self.window_size
        
        if T <= W:
            raise ValueError(f"Длина ряда ({T}) должна быть больше window_size ({W})")
        
        n_points = T - W
        
        # Инициализация массивов
        self.regime_energies = np.zeros((n_points, self.K))
        self.regime_signal = np.zeros(n_points, dtype=int)
        self.entropy = np.zeros(n_points)
        
        # Используем остатки режимов (агрегированные для каждого режима)
        regime_residues = np.zeros(self.K, dtype=complex)
        for k in range(self.K):
            cluster_indices = self.pole_clusters.get(k, [])
            if len(cluster_indices) > 0 and self.residues is not None:
                regime_residues[k] = np.mean(self.residues[cluster_indices])
            else:
                regime_residues[k] = 1.0 / self.K
        
        # Для каждого момента времени
        for t_idx in range(n_points):
            t = t_idx + W
            
            # Вычисление энергии каждого режима
            for k in range(self.K):
                lambda_k = self.regime_poles[k]
                R_k = regime_residues[k]
                
                # E_k(t) = Σ(s=0 до W-1) |R_k * λ_k^{t-s}|²
                # Используем формулу геометрического ряда
                r_squared = np.abs(lambda_k) ** 2
                if np.abs(1 - r_squared) > 1e-10:
                    # Геометрический ряд: |R_k|² * |λ_k|^{2t} * (1 - |λ_k|^{2W}) / (1 - |λ_k|²)
                    energy = (np.abs(R_k) ** 2) * (r_squared ** t) * \
                             (1 - r_squared ** W) / (1 - r_squared + 1e-10)
                else:
                    energy = (np.abs(R_k) ** 2) * W
                
                self.regime_energies[t_idx, k] = max(energy, 1e-10)
            
            # Нормализация энергий (мягкие вероятности)
            total_energy = np.sum(self.regime_energies[t_idx, :])
            if total_energy > 0:
                probs = self.regime_energies[t_idx, :] / total_energy
            else:
                probs = np.ones(self.K) / self.K
            
            # Доминирующий режим
            self.regime_signal[t_idx] = np.argmax(probs)
            
            # Энтропия режимности
            # H(t) = -Σ P̃_k * log(P̃_k + ε)
            eps = 1e-10
            self.entropy[t_idx] = -np.sum(probs * np.log(probs + eps))
    
    def fit(self, y: np.ndarray) -> 'SpectralRegimeAnalyzer':
        """
        Полный pipeline оценки.
        
        Выполняет последовательно:
        1. compute_acf
        2. prony_method
        3. cluster_poles
        4. regime_parameters
        5. spectral_factorization
        6. minimum_phase_recovery
        7. dynamic_regime_analysis
        
        Parameters
        ----------
        y : ndarray
            Временной ряд размерности (T,)
        
        Returns
        -------
        self : SpectralRegimeAnalyzer
            Для chaining
        """
        y = np.asarray(y).flatten()
        self.y = y
        self.T = len(y)
        
        if self.max_lag is None:
            self.max_lag = self.T // 4
        
        # 1. Вычисление ACF
        self.compute_acf(y)
        
        # 2. Если n_poles не задан, используем значение по умолчанию
        if self.n_poles is None or self.n_poles <= 0:
            self.n_poles = 5
        
        # 3. Метод Prony
        self.prony_method(self.acf)
        
        # 4. Если window_size не задан, используем значение по умолчанию
        if self.window_size is None or self.window_size <= 0:
            self.window_size = 20
        
        # 5. Кластеризация полюсов
        self.cluster_poles(self.poles)
        
        # 6. Параметры режимов
        self.regime_parameters()
        
        # 7. Спектральная факторизация
        self.spectral_factorization()
        
        # 8. Восстановление фазы
        self.minimum_phase_recovery()
        
        # 9. Динамический анализ
        if self.T > self.window_size:
            self.dynamic_regime_analysis(y)
        
        return self
    
    def fit_auto(self, y: np.ndarray, criterion: str = 'bic') -> 'SpectralRegimeAnalyzer':
        """
        Полный pipeline оценки с автоматическим определением оптимальных параметров.
        
        Автоматически определяет:
        - Оптимальное количество полюсов через информационные критерии
        - Оптимальный размер окна на основе длины ряда
        
        Parameters
        ----------
        y : ndarray
            Временной ряд размерности (T,)
        criterion : str
            Критерий для выбора количества полюсов: 'aic', 'bic', или 'aicc'
        
        Returns
        -------
        self : SpectralRegimeAnalyzer
            Для chaining
        """
        y = np.asarray(y).flatten()
        self.y = y
        self.T = len(y)
        
        if self.max_lag is None:
            self.max_lag = self.T // 4
        
        # 1. Вычисление ACF
        self.compute_acf(y)
        
        # 2. Автоматическое определение оптимального количества полюсов
        if self.n_poles is None or self.n_poles <= 0:
            self.n_poles = self.find_optimal_n_poles(self.acf, criterion=criterion)
        
        # 3. Автоматическое определение оптимального размера окна
        if self.window_size is None or self.window_size <= 0:
            self.window_size = self.find_optimal_window_size(self.T)
        
        # 4. Метод Prony
        self.prony_method(self.acf)
        
        # 5. Кластеризация полюсов
        self.cluster_poles(self.poles)
        
        # 6. Параметры режимов
        self.regime_parameters()
        
        # 7. Спектральная факторизация
        self.spectral_factorization()
        
        # 8. Восстановление фазы
        self.minimum_phase_recovery()
        
        # 9. Динамический анализ
        if self.T > self.window_size:
            self.dynamic_regime_analysis(y)
        
        return self
    
    def stability_check(self) -> Tuple[bool, List[int]]:
        """
        Проверить стабильность (все ли |λ| < 1).
        
        Returns
        -------
        is_stable : bool
            True если все полюсы стабильны
        violations : list
            Индексы нестабильных полюсов
        """
        if self.poles is None:
            return True, []
        
        violations = []
        for i, pole in enumerate(self.poles):
            if np.abs(pole) >= 1.0:
                violations.append(i)
        
        is_stable = len(violations) == 0
        return is_stable, violations
    
    def minimum_phase_check(self) -> Tuple[bool, Dict]:
        """
        Проверить минимально-фазовое условие.
        
        Returns
        -------
        is_minimum_phase : bool
            True если система минимально-фазовая
        info : dict
            Информация о нарушениях
        """
        if self.poles is None:
            return False, {'error': 'Poles not computed'}
        
        # Все полюсы должны быть внутри единичного круга
        outside_poles = []
        for i, pole in enumerate(self.poles):
            if np.abs(pole) >= 1.0:
                outside_poles.append({
                    'index': i,
                    'pole': complex(pole),
                    'radius': float(np.abs(pole))
                })
        
        is_min_phase = len(outside_poles) == 0
        
        info = {
            'is_minimum_phase': is_min_phase,
            'n_violations': len(outside_poles),
            'violations': outside_poles
        }
        
        return is_min_phase, info
    
    def reconstruction_error(self) -> Tuple[float, float]:
        """
        Вычислить ошибку восстановления ACF.
        
        Восстанавливает ACF из полюсов и остатков:
        γ_recon(h) = Σ(k) R_k * λ_k^h
        
        Returns
        -------
        rmse : float
            RMSE между истинной и восстановленной ACF
        pct_explained : float
            Процент объяснённой дисперсии
        """
        if self.acf is None or self.poles is None or self.residues is None:
            return 0.0, 0.0
        
        H = len(self.acf)
        acf_recon = np.zeros(H, dtype=complex)
        
        for h in range(H):
            for k in range(len(self.poles)):
                acf_recon[h] += self.residues[k] * (self.poles[k] ** h)
        
        acf_recon = np.real(acf_recon)
        
        # RMSE
        rmse = np.sqrt(np.mean((self.acf - acf_recon) ** 2))
        
        # Процент объяснённой дисперсии
        var_true = np.var(self.acf)
        if var_true > 0:
            pct_explained = (1 - rmse**2 / var_true) * 100
        else:
            pct_explained = 100.0
        
        return float(rmse), float(max(0, pct_explained))
    
    def get_regime_at_time(self, t: int) -> Dict:
        """
        Получить информацию о режиме в момент t.
        
        Parameters
        ----------
        t : int
            Индекс временной точки
        
        Returns
        -------
        dict
            Информация о режиме
        """
        if self.regime_signal is None or self.regime_energies is None:
            return {
                'regime_index': -1,
                'regime_energies': [],
                'entropy': 0.0,
                'timestamp': t
            }
        
        # Индекс в массивах (учитываем offset от window_size)
        idx = t - self.window_size
        if idx < 0 or idx >= len(self.regime_signal):
            return {
                'regime_index': -1,
                'regime_energies': [],
                'entropy': 0.0,
                'timestamp': t
            }
        
        # Нормализованные энергии
        energies = self.regime_energies[idx, :]
        total = np.sum(energies)
        probs = (energies / total).tolist() if total > 0 else [1.0/self.K] * self.K
        
        return {
            'regime_index': int(self.regime_signal[idx]),
            'regime_energies': probs,
            'entropy': float(self.entropy[idx]),
            'timestamp': t
        }
    
    def get_current_regime_metrics(self) -> Dict:
        """
        Получить метрики текущего момента (конец временного ряда).
        
        Returns
        -------
        dict
            Текущие метрики режима
        """
        if self.regime_signal is None or len(self.regime_signal) == 0:
            return {
                'regime_index': -1,
                'regime_type': 'Unknown',
                'regime_energies': [],
                'entropy': 0.0,
                'is_stable': True,
                'is_minimum_phase': True,
                'expected_duration_days': 0.0
            }
        
        # Последняя точка
        idx = len(self.regime_signal) - 1
        regime_idx = int(self.regime_signal[idx])
        
        # Нормализованные энергии
        energies = self.regime_energies[idx, :]
        total = np.sum(energies)
        probs = (energies / total).tolist() if total > 0 else [1.0/self.K] * self.K
        
        # Параметры режима
        regime_type = self.regime_params.get(regime_idx, {}).get('type', 'Unknown')
        duration = self.regime_params.get(regime_idx, {}).get('duration', 0.0)
        
        is_stable, _ = self.stability_check()
        
        return {
            'regime_index': regime_idx,
            'regime_type': regime_type,
            'regime_energies': probs,
            'entropy': float(self.entropy[idx]),
            'is_stable': is_stable,
            'is_minimum_phase': self.is_minimum_phase,
            'expected_duration_days': duration
        }
    
    @staticmethod
    def find_optimal_n_poles(
        acf: np.ndarray,
        min_poles: int = 3,
        max_poles: int = 12,
        criterion: str = 'bic'
    ) -> int:
        """
        Найти оптимальное количество полюсов через информационные критерии.
        
        Использует AIC (Akaike Information Criterion) или BIC (Bayesian Information Criterion)
        для выбора оптимального количества полюсов, балансируя между точностью
        восстановления и сложностью модели.
        
        Формулы:
        AIC = 2k - 2*ln(L)  где k - число параметров, L - likelihood
        BIC = k*ln(n) - 2*ln(L)  где n - размер выборки
        
        Parameters
        ----------
        acf : ndarray
            Автоковариация размерности (H+1,)
        min_poles : int
            Минимальное количество полюсов (по умолчанию 3)
        max_poles : int
            Максимальное количество полюсов (по умолчанию 12)
        criterion : str
            Критерий выбора: 'aic', 'bic', или 'aicc' (скорректированный AIC)
        
        Returns
        -------
        optimal_n_poles : int
            Оптимальное количество полюсов
        """
        H = len(acf) - 1
        max_poles = min(max_poles, H // 2 - 1)
        min_poles = max(min_poles, 2)
        
        if max_poles < min_poles:
            return min_poles
        
        criteria_values = []
        n_poles_range = range(min_poles, max_poles + 1)
        
        for M in n_poles_range:
            try:
                # Создаём временный анализатор для тестирования
                temp_analyzer = SpectralRegimeAnalyzer(
                    max_lag=H,
                    n_poles=M,
                    window_size=20  # Не важно для этого теста
                )
                
                # Вычисляем полюсы
                poles, residues = temp_analyzer.prony_method(acf)
                
                # Восстанавливаем ACF
                acf_recon = np.zeros(len(acf), dtype=complex)
                for h in range(len(acf)):
                    for k in range(len(poles)):
                        acf_recon[h] += residues[k] * (poles[k] ** h)
                acf_recon = np.real(acf_recon)
                
                # Вычисляем ошибку восстановления
                rmse = np.sqrt(np.mean((acf - acf_recon) ** 2))
                
                # Количество параметров: 2*M (комплексные полюсы) + 2*M (комплексные остатки) = 4*M
                k = 4 * M
                n = len(acf)
                
                # Log-likelihood (приблизительно через RMSE)
                # L ∝ exp(-n*RMSE^2 / (2*σ^2)), где σ^2 - дисперсия ACF
                var_acf = np.var(acf)
                if var_acf > 0 and rmse > 0:
                    # Приближение: ln(L) ≈ -n*RMSE^2 / (2*var_acf)
                    log_likelihood = -n * (rmse ** 2) / (2 * var_acf + 1e-10)
                else:
                    log_likelihood = -1e10
                
                # Вычисляем критерий
                if criterion.lower() == 'aic':
                    criterion_value = 2 * k - 2 * log_likelihood
                elif criterion.lower() == 'aicc':
                    # Скорректированный AIC: AICc = AIC + 2k(k+1)/(n-k-1)
                    aic = 2 * k - 2 * log_likelihood
                    if n > k + 1:
                        correction = 2 * k * (k + 1) / (n - k - 1)
                    else:
                        correction = 0
                    criterion_value = aic + correction
                else:  # BIC (по умолчанию)
                    criterion_value = k * np.log(n) - 2 * log_likelihood
                
                criteria_values.append((M, criterion_value, rmse))
                
            except Exception:
                # Если не удалось вычислить для данного M, пропускаем
                continue
        
        if not criteria_values:
            # Fallback: возвращаем среднее значение
            return (min_poles + max_poles) // 2
        
        # Находим минимум критерия
        criteria_values = np.array(criteria_values)
        best_idx = np.argmin(criteria_values[:, 1])  # Индекс минимального критерия
        optimal_n_poles = int(criteria_values[best_idx, 0])
        
        return optimal_n_poles
    
    @staticmethod
    def find_optimal_window_size(
        T: int,
        min_window: int = 10,
        max_window: int = 50
    ) -> int:
        """
        Найти оптимальный размер скользящего окна.
        
        Использует эвристические правила на основе длины временного ряда:
        - window_size = sqrt(T) для коротких рядов
        - window_size = T/10 для длинных рядов
        - Ограничивается min_window и max_window
        
        Parameters
        ----------
        T : int
            Длина временного ряда
        min_window : int
            Минимальный размер окна (по умолчанию 10)
        max_window : int
            Максимальный размер окна (по умолчанию 50)
        
        Returns
        -------
        optimal_window_size : int
            Оптимальный размер окна
        """
        if T < min_window:
            return min_window
        
        # Правило 1: sqrt(T) для коротких рядов
        sqrt_rule = int(np.sqrt(T))
        
        # Правило 2: T/10 для длинных рядов
        fraction_rule = int(T / 10)
        
        # Правило 3: log(T) * 5 для средних рядов
        log_rule = int(np.log(T + 1) * 5)
        
        # Выбираем среднее значение правил
        candidates = [sqrt_rule, fraction_rule, log_rule]
        candidates = [c for c in candidates if min_window <= c <= max_window]
        
        if not candidates:
            # Если все выходят за границы, используем граничные значения
            if sqrt_rule < min_window:
                return min_window
            elif sqrt_rule > max_window:
                return max_window
            else:
                return sqrt_rule
        
        # Возвращаем медиану кандидатов
        optimal = int(np.median(candidates))
        
        # Ограничиваем границами
        optimal = max(min_window, min(optimal, max_window))
        
        return optimal
    
    def get_summary(self) -> Dict:
        """
        Получить сводную информацию об анализе.
        
        Returns
        -------
        dict
            Полная сводка результатов анализа
        """
        is_stable, violations = self.stability_check()
        is_min_phase, min_phase_info = self.minimum_phase_check()
        rmse, pct_explained = self.reconstruction_error()
        current_metrics = self.get_current_regime_metrics()
        
        # Статистика времени в каждом режиме
        regime_time_stats = {}
        if self.regime_signal is not None:
            for k in range(self.K):
                time_in_regime = np.sum(self.regime_signal == k)
                regime_time_stats[k] = {
                    'count': int(time_in_regime),
                    'percentage': float(time_in_regime / len(self.regime_signal) * 100)
                }
        
        # Статистика энтропии
        entropy_stats = {}
        if self.entropy is not None and len(self.entropy) > 0:
            entropy_stats = {
                'mean': float(np.mean(self.entropy)),
                'max': float(np.max(self.entropy)),
                'min': float(np.min(self.entropy)),
                'std': float(np.std(self.entropy))
            }
        
        return {
            'n_regimes': self.K,
            'n_poles': len(self.poles) if self.poles is not None else 0,
            'regime_params': {str(k): v for k, v in self.regime_params.items()},
            'stability': {
                'is_stable': is_stable,
                'n_violations': len(violations),
                'violation_indices': violations
            },
            'minimum_phase': min_phase_info,
            'reconstruction': {
                'rmse': rmse,
                'pct_explained': pct_explained
            },
            'regime_time_stats': {str(k): v for k, v in regime_time_stats.items()},
            'entropy_stats': entropy_stats,
            'current_metrics': current_metrics
        }
    
    def get_visualization_data(self) -> Dict:
        """
        Получить данные для визуализации на фронтенде.
        
        Returns
        -------
        dict
            Данные для построения графиков
        """
        # Полюсы для диаграммы
        poles_data = []
        if self.poles is not None:
            for i, pole in enumerate(self.poles):
                poles_data.append({
                    'index': i,
                    'real': float(pole.real),
                    'imag': float(pole.imag),
                    'radius': float(np.abs(pole)),
                    'angle': float(np.angle(pole))
                })
        
        # Режимные полюсы
        regime_poles_data = []
        if self.regime_poles is not None:
            for k, pole in enumerate(self.regime_poles):
                regime_poles_data.append({
                    'regime': k,
                    'real': float(pole.real),
                    'imag': float(pole.imag),
                    'radius': float(np.abs(pole)),
                    'type': self.regime_params.get(k, {}).get('type', 'Unknown')
                })
        
        # Спектр
        spectrum_data = {}
        if self.omega is not None and self.amplitude_spectrum is not None:
            # Берём положительные частоты
            pos_idx = self.omega >= 0
            spectrum_data = {
                'frequencies': self.omega[pos_idx].tolist(),
                'amplitude': self.amplitude_spectrum[pos_idx].tolist(),
                'log_amplitude': self.log_amplitude_spectrum[pos_idx].tolist() if self.log_amplitude_spectrum is not None else [],
                'phase': self.phase_spectrum[pos_idx].tolist() if self.phase_spectrum is not None else []
            }
        
        # Динамика режимов
        dynamics_data = {}
        if self.regime_signal is not None and self.y is not None:
            # Временной ряд (начиная с window_size)
            start_idx = self.window_size
            time_series = self.y[start_idx:].tolist()
            
            # Нормализованные энергии режимов
            energies_normalized = []
            if self.regime_energies is not None:
                for t in range(len(self.regime_energies)):
                    row = self.regime_energies[t, :]
                    total = np.sum(row)
                    energies_normalized.append((row / total).tolist() if total > 0 else [1.0/self.K] * self.K)
            
            dynamics_data = {
                'time_series': time_series,
                'regime_signal': self.regime_signal.tolist() if self.regime_signal is not None else [],
                'regime_energies': energies_normalized,
                'entropy': self.entropy.tolist() if self.entropy is not None else []
            }
        
        # ACF для визуализации
        acf_data = []
        if self.acf is not None:
            acf_data = self.acf.tolist()
        
        return {
            'poles': poles_data,
            'regime_poles': regime_poles_data,
            'spectrum': spectrum_data,
            'dynamics': dynamics_data,
            'acf': acf_data
        }


def run_spectral_regime_analysis(
    returns: List[float],
    n_poles: Optional[int] = None,
    window_size: Optional[int] = None,
    max_lag: Optional[int] = None,
    auto_optimize: bool = False,
    criterion: str = 'bic'
) -> Dict[str, Any]:
    """
    Запустить комплексный анализ скрытых рыночных режимов.
    
    Parameters
    ----------
    returns : list
        Временной ряд доходностей
    n_poles : int, optional
        Количество полюсов для идентификации. Если None и auto_optimize=True,
        определяется автоматически через информационные критерии.
    window_size : int, optional
        Размер скользящего окна. Если None и auto_optimize=True,
        определяется автоматически на основе длины ряда.
    max_lag : int, optional
        Максимальный лаг для ACF (по умолчанию T/4)
    auto_optimize : bool
        Если True, автоматически определяет оптимальные n_poles и window_size
    criterion : str
        Критерий для выбора количества полюсов: 'aic', 'bic', или 'aicc'
        (используется только если auto_optimize=True)
    
    Returns
    -------
    dict
        Полные результаты анализа с информацией об использованных параметрах
    """
    returns_arr = np.array(returns)
    
    # Если auto_optimize=True, устанавливаем None для автоматического определения
    if auto_optimize:
        n_poles = None
        window_size = None
    
    analyzer = SpectralRegimeAnalyzer(
        max_lag=max_lag,
        n_poles=n_poles,
        window_size=window_size
    )
    
    # Используем fit_auto если auto_optimize=True или параметры не заданы
    if auto_optimize or (n_poles is None and window_size is None):
        analyzer.fit_auto(returns_arr, criterion=criterion)
    else:
        analyzer.fit(returns_arr)
    
    summary = analyzer.get_summary()
    
    # Добавляем информацию об использованных параметрах
    summary['optimization'] = {
        'auto_optimized': auto_optimize or (n_poles is None or window_size is None),
        'n_poles_used': analyzer.n_poles,
        'window_size_used': analyzer.window_size,
        'criterion_used': criterion if auto_optimize else None
    }
    
    return {
        'summary': summary,
        'visualization': analyzer.get_visualization_data()
    }
