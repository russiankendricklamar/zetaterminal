# -*- coding: utf-8 -*-
import numpy as np
from typing import Tuple

def simulate_montecarlo(mu: np.ndarray, sigma: np.ndarray, weights: np.ndarray, 
                        X_0: float, T: float, n_paths: int = 5000) -> Tuple[np.ndarray, np.ndarray]:
    """
    БЛОК 7: Монте-Карло симуляция портфеля (Исправленная версия).
    Реализует динамику капитала с непрерывной ребалансировкой согласно весам HJB.
    
    Входные mu и sigma должны быть в ДОЛЯХ (напр. 0.15, а не 15.0).
    """
    
    # 1. Подготовка и проверка входных данных
    mu = np.asarray(mu).flatten()
    sigma = np.asarray(sigma)
    weights = np.asarray(weights).flatten()
    
    # Параметры времени (дневная частота)
    n_steps = int(T * 252)
    if n_steps < 2: n_steps = 2
    t_grid = np.linspace(0, T, n_steps)
    dt = T / (n_steps - 1)
    
    # 2. Агрегация параметров портфеля (Portfolio mu и Portfolio variance)
    # Вместо симуляции каждого актива отдельно, мы симулируем процесс всего капитала.
    # Это соответствует стратегии с мгновенной ребалансировкой (HJB/Merton).
    
    # Ожидаемая доходность портфеля: w' * mu
    port_mu = np.dot(weights, mu)
    
    # Дисперсия портфеля: w' * Sigma * w
    port_var = np.dot(weights, np.dot(sigma, weights))
    port_vol = np.sqrt(port_var)

    # 3. Инициализация выходного массива
    X_paths = np.zeros((n_paths, n_steps))
    X_paths[:, 0] = X_0
    
    # 4. Генерация случайных шоков для портфеля
    # Нам нужен только один вектор шоков на каждый шаг, так как мы смотрим на портфель в целом
    np.random.seed(42) 
    dW_p = np.random.normal(0, np.sqrt(dt), (n_paths, n_steps - 1))
    
    # 5. Цикл симуляции капитала (Геометрическое Броуновское Движение)
    # Формула: dX_t = X_t * (port_mu * dt + port_vol * dW_t)
    # Решение через Ито: X_{t+1} = X_t * exp((port_mu - 0.5 * port_var) * dt + port_vol * dW_p)
    
    drift = (port_mu - 0.5 * port_var) * dt
    
    for step in range(n_steps - 1):
        diffusion = port_vol * dW_p[:, step]
        
        # Обновляем капитал для всех путей одновременно
        X_paths[:, step + 1] = X_paths[:, step] * np.exp(drift + diffusion)
        
        # Защита от банкротства (капитал не может быть меньше 0)
        # Если путь упал ниже порога, фиксируем минимальное значение
        X_paths[X_paths[:, step + 1] < 1e-6, step + 1] = 1e-6

    return X_paths, t_grid