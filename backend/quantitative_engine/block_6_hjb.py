# -*- coding: utf-8 -*-
import numpy as np
from typing import Dict, List, Tuple

class HJBStrategy:
    """
    Класс реализации оптимальной динамической стратегии на основе 
    уравнения Гамильтона — Якоби — Беллмана.
    """
    def __init__(self, mu, cov_matrix, risk_free_rate, gamma, asset_names=None,
                 short_sales_allowed=False, max_leverage=1.0, min_weight=0.0,
                 normalize_weights=True):

        self.mu = np.asarray(mu).flatten()
        self.cov_matrix = np.asarray(cov_matrix)
        self.risk_free_rate = float(risk_free_rate)
        self.gamma = float(gamma)
        self.n_assets = len(self.mu)
        self.asset_names = asset_names if asset_names is not None else \
                          [f"Asset_{i+1}" for i in range(self.n_assets)]

        self.short_sales_allowed = short_sales_allowed
        self.max_leverage = max_leverage
        self.min_weight = min_weight
        self.normalize_weights = normalize_weights

        self.excess_mu = self.mu - self.risk_free_rate

        # Инверсия матрицы ковариации с проверкой на вырожденность
        try:
            self.inv_cov_matrix = np.linalg.inv(self.cov_matrix)
        except np.linalg.LinAlgError:
            self.inv_cov_matrix = np.linalg.pinv(self.cov_matrix)

        self._weights_base = np.dot(self.inv_cov_matrix, self.excess_mu)

    def get_optimal_weights(self) -> np.ndarray:
        """Расчет весов w* = (1/gamma) * inv(Sigma) * (mu - rf)"""
        weights_raw = (1.0 / self.gamma) * self._weights_base

        # Ограничение на короткие продажи
        if not self.short_sales_allowed:
            weights_clipped = np.clip(weights_raw, 0, None)
        else:
            weights_clipped = weights_raw.copy()

        sum_weights = np.sum(np.abs(weights_clipped))

        # Защита от нулевых весов (если все mu < rf)
        if sum_weights < 1e-10:
            return np.ones(self.n_assets) / self.n_assets

        # Нормировка
        if self.normalize_weights:
            weights_final = weights_clipped / np.sum(weights_clipped)
        else:
            current_leverage = np.sum(weights_clipped)
            if current_leverage > self.max_leverage:
                weights_final = weights_clipped * (self.max_leverage / current_leverage)
            else:
                weights_final = weights_clipped

        # Применение минимального порога веса
        if self.min_weight > 0:
            weights_final[weights_final < self.min_weight] = 0.0
            if self.normalize_weights:
                sum_w = np.sum(weights_final)
                if sum_w > 1e-10:
                    weights_final = weights_final / sum_w

        return weights_final

def optimize_hjb(mu: np.ndarray, sigma: np.ndarray, gamma: float, 
                 rf_rate: float, asset_names: List[str]) -> Tuple[HJBStrategy, np.ndarray]:
    """
    Интерфейсная функция для вызова из engine.py.
    """
    # Инициализируем стратегию
    strategy = HJBStrategy(
        mu=mu, 
        cov_matrix=sigma, 
        risk_free_rate=rf_rate, 
        gamma=gamma, 
        asset_names=asset_names,
        normalize_weights=True # Для MVP используем классическую нормировку (сумма весов = 1)
    )
    
    # Получаем веса
    weights = strategy.get_optimal_weights()
    
    return strategy, weights