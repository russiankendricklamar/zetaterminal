"""
Сервис для выполнения вычислительных задач.
"""
import numpy as np
from typing import Dict, Any


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
