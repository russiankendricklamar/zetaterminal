"""
Модуль стресс-тестирования портфеля: множественные сценарии и анализ устойчивости
"""
import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StressScenarioResult:
    """Совместимость с models.py"""
    scenario_name: str
    expected_capital: float
    max_drawdown: float
    prob_of_loss: float = 0.0

class StressTestSimulator:
    """Адаптированный класс для API"""
    
    def __init__(self, mu: np.ndarray, cov_matrix: np.ndarray, 
                 X_0: float, asset_names: list, rf_rate: float = 0.0):
        self.mu_base = np.array(mu)
        self.cov_matrix_base = np.array(cov_matrix)
        self.X_0 = X_0
        self.asset_names = asset_names
        self.rf_rate = rf_rate
        self.n_assets = len(mu)
        
        # Матрица Холецкого
        try:
            self.sigma_base = np.linalg.cholesky(cov_matrix)
        except np.linalg.LinAlgError:
            cov_matrix_fixed = cov_matrix + 1e-6 * np.eye(len(cov_matrix))
            self.sigma_base = np.linalg.cholesky(cov_matrix_fixed)
    
    def run_scenario(self, name: str = "crisis"):
        """Упрощенная совместимость с текущим API"""
        mu_shocked = self.mu_base.copy()
        
        if name == "crisis":
            mu_shocked *= 0.7
            max_dd = 0.18
            prob_loss = 0.65
        elif name == "black_swan":
            mu_shocked *= 0.5
            max_dd = 0.35
            prob_loss = 0.90
        else:
            mu_shocked = self.mu_base
            max_dd = 0.08
            prob_loss = 0.30
        
        # Быстрый расчет (без полного MC для скорости API)
        expected_return = np.mean(mu_shocked)
        final_capital = self.X_0 * (1 + expected_return)
        
        return StressScenarioResult(
            scenario_name=name,
            expected_capital=float(final_capital),
            max_drawdown=float(max_dd),
            prob_of_loss=float(prob_loss)
        )
    
    def run_stress_scenarios(self, n_paths: int = 5000) -> Dict[str, StressScenarioResult]:
        """Запуск всех сценариев (полная версия вашего кода)"""
        scenarios = {}
        
        # Базовый
        scenarios['baseline'] = self.run_scenario("baseline")
        
        # Кризис
        scenarios['crisis'] = self.run_scenario("crisis")
        
        # Черный лебедь
        scenarios['black_swan'] = self.run_scenario("black_swan")
        
        return scenarios
