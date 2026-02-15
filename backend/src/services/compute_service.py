"""
Сервис для выполнения вычислительных задач.
"""
import numpy as np
from typing import Dict, Any, List, Optional


class ComputeService:
    """Сервис для вычислительных операций."""
    
    @staticmethod
    def calculate_statistics(data: List[float]) -> Dict[str, Any]:
        """
        Вычисляет статистику для массива данных.
        
        Args:
            data: Список числовых значений
            
        Returns:
            Словарь со статистическими показателями
        """
        arr = np.array(data)
        
        return {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "median": float(np.median(arr)),
            "count": len(data)
        }
    
    @staticmethod
    def calculate_garch(
        returns: List[float],
        omega: float = 0.000025,
        alpha: float = 0.082,
        beta: float = 0.893,
        initial_variance: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Вычисляет GARCH(1,1) модель волатильности.

        Stationarity constraint: α + β < 1
        Positivity constraints: ω > 0, α ≥ 0, β ≥ 0

        Args:
            returns: Список доходностей (returns)
            omega: Параметр ω (константа), должен быть > 0
            alpha: Параметр α (ARCH), должен быть ≥ 0
            beta: Параметр β (GARCH), должен быть ≥ 0
            initial_variance: Начальная дисперсия (опционально)

        Returns:
            Словарь с результатами GARCH моделирования

        Raises:
            ValueError: Если параметры нарушают constraints
        """
        returns_array = np.array(returns)
        n = len(returns_array)

        if n < 2:
            raise ValueError(f"Требуется минимум 2 наблюдения, получено: {n}")

        # Валидация параметров
        if omega <= 0:
            raise ValueError(f"omega должна быть > 0, получено: {omega}")
        if alpha < 0:
            raise ValueError(f"alpha должна быть >= 0, получено: {alpha}")
        if beta < 0:
            raise ValueError(f"beta должна быть >= 0, получено: {beta}")

        persistence = alpha + beta
        is_stationary = persistence < 1.0

        if not is_stationary:
            raise ValueError(
                f"Нарушено условие стационарности: α + β = {persistence:.6f} >= 1. "
                f"Дисперсия не сходится. Уменьшите alpha ({alpha}) или beta ({beta})."
            )

        # Минимальный порог дисперсии для численной стабильности
        variance_floor = 1e-12

        # Инициализация дисперсии: используем long-run variance если стационарна
        if initial_variance is None:
            long_run_var = omega / (1.0 - persistence)
            initial_variance = float(long_run_var)

        initial_variance = max(initial_variance, variance_floor)

        # Массивы для хранения результатов
        variances = np.zeros(n)
        volatilities = np.zeros(n)
        residuals = np.zeros(n)

        # Начальное значение
        variances[0] = initial_variance
        volatilities[0] = np.sqrt(initial_variance)
        residuals[0] = returns_array[0] / volatilities[0] if volatilities[0] > 0 else 0.0

        # GARCH(1,1) рекурсия: σ²_t = ω + α*r²_{t-1} + β*σ²_{t-1}
        for t in range(1, n):
            variances[t] = omega + alpha * (returns_array[t-1] ** 2) + beta * variances[t-1]

            # Enforce variance floor для численной стабильности
            variances[t] = max(variances[t], variance_floor)

            volatilities[t] = np.sqrt(variances[t])

            # Стандартизированные остатки: z_t = r_t / σ_t
            residuals[t] = returns_array[t] / volatilities[t]

        # Долгосрочная волатильность (гарантированно корректна т.к. is_stationary = True)
        long_term_variance = omega / (1.0 - persistence)
        long_term_volatility = np.sqrt(long_term_variance)
        
        return {
            "variances": variances.tolist(),
            "volatilities": volatilities.tolist(),
            "residuals": residuals.tolist(),
            "parameters": {
                "omega": omega,
                "alpha": alpha,
                "beta": beta
            },
            "long_term_volatility": float(long_term_volatility),
            "mean_variance": float(np.mean(variances)),
            "mean_volatility": float(np.mean(volatilities))
        }
    
    @staticmethod
    def matrix_operations(matrix_a: List[List[float]], 
                         matrix_b: List[List[float]]) -> Dict[str, Any]:
        """
        Выполняет операции с матрицами.
        
        Args:
            matrix_a: Первая матрица
            matrix_b: Вторая матрица
            
        Returns:
            Результаты операций с матрицами
        """
        a = np.array(matrix_a)
        b = np.array(matrix_b)
        
        result = {
            "addition": (a + b).tolist() if a.shape == b.shape else None,
            "multiplication": (a @ b).tolist() if a.shape[1] == b.shape[0] else None,
        }
        
        return result
