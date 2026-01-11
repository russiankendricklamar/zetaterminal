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
        
        Args:
            returns: Список доходностей (returns)
            omega: Параметр ω (константа)
            alpha: Параметр α (ARCH)
            beta: Параметр β (GARCH)
            initial_variance: Начальная дисперсия (опционально)
            
        Returns:
            Словарь с результатами GARCH моделирования
        """
        returns_array = np.array(returns)
        n = len(returns_array)
        
        # Инициализация дисперсии
        if initial_variance is None:
            initial_variance = float(np.var(returns_array))
        
        # Массивы для хранения результатов
        variances = np.zeros(n)
        volatilities = np.zeros(n)
        residuals = np.zeros(n)
        
        # Начальное значение
        variances[0] = initial_variance
        volatilities[0] = np.sqrt(initial_variance)
        residuals[0] = returns_array[0] / volatilities[0] if volatilities[0] > 0 else 0
        
        # GARCH(1,1) рекурсия
        for t in range(1, n):
            # Обновление дисперсии: σ²_t = ω + α*ε²_{t-1} + β*σ²_{t-1}
            variances[t] = omega + alpha * (residuals[t-1] ** 2) + beta * variances[t-1]
            volatilities[t] = np.sqrt(variances[t])
            
            # Вычисление остатков
            if volatilities[t] > 0:
                residuals[t] = returns_array[t] / volatilities[t]
            else:
                residuals[t] = 0
        
        # Долгосрочная волатильность
        long_term_variance = omega / (1 - alpha - beta) if (1 - alpha - beta) > 0 else initial_variance
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
