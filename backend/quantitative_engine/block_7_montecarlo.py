# -*- coding: utf-8 -*-

import numpy as np
from typing import Tuple, Dict

def simulate_montecarlo(mu: np.ndarray, sigma: np.ndarray, weights: np.ndarray,
                       X_0: float, T: float, n_paths: int = 5000,
                       asset_names: list = None) -> Tuple[np.ndarray, np.ndarray, Dict]:
    
    # 1. Подготовка и проверка входных данных
    mu = np.asarray(mu).flatten()
    sigma = np.asarray(sigma)
    weights = np.asarray(weights).flatten()
    
    n_assets = len(mu)
    
    # Если names не передали, используем индексы
    if asset_names is None:
        asset_names = [f'Asset_{i}' for i in range(n_assets)]
    
    # Параметры времени (дневная частота)
    n_steps = int(T * 252)
    if n_steps < 2: 
        n_steps = 2
    
    t_grid = np.linspace(0, T, n_steps)
    dt = T / (n_steps - 1)
    
    # 2. Агрегация параметров портфеля
    port_mu = np.dot(weights, mu)
    port_var = np.dot(weights, np.dot(sigma, weights))
    port_vol = np.sqrt(port_var)
    
    # 3. Инициализация выходных массивов
    X_paths = np.zeros((n_paths, n_steps))
    X_paths[:, 0] = X_0
    
    # Траектории отдельных активов (начальная стоимость = X_0 / n_assets)
    asset_paths_dict = {}
    for asset_name in asset_names:
        asset_paths_dict[asset_name] = np.zeros((n_paths, n_steps))
        asset_paths_dict[asset_name][:, 0] = X_0 / n_assets  # Равное распределение
    
    # 4. Генерация коррелированных случайных шоков
    np.random.seed(42)
    
    # Матрица Холецкого для корреляции активов
    L = np.linalg.cholesky(sigma)
    
    # Стандартные нормальные случайные величины (n_assets, n_paths, n_steps-1)
    Z = np.random.normal(0, 1, (n_assets, n_paths, n_steps - 1))
    
    # Применяем корреляционную матрицу
    # dW = L @ Z дает коррелированные шоки
    
    # 5. Цикл симуляции
    drift_port = (port_mu - 0.5 * port_var) * dt
    dW_p = np.zeros((n_paths, n_steps - 1))
    
    for step in range(n_steps - 1):
        # Генерируем коррелированные шоки для активов
        # dW_assets имеет shape (n_assets, n_paths)
        dW_assets = np.dot(L, Z[:, :, step]) * np.sqrt(dt)
        
        # Сохраняем шок портфеля (взвешенная комбинация)
        dW_p[:, step] = np.dot(weights, dW_assets)
        
        # Обновляем портфель (Геометрическое Броуновское Движение)
        diffusion_port = port_vol * dW_p[:, step]
        X_paths[:, step + 1] = X_paths[:, step] * np.exp(drift_port + diffusion_port)
        
        # Обновляем отдельные активы
        for i, asset_name in enumerate(asset_names):
            # Параметры актива
            asset_mu = mu[i]
            asset_vol = np.sqrt(sigma[i, i])
            asset_drift = (asset_mu - 0.5 * sigma[i, i]) * dt
            asset_diffusion = asset_vol * dW_assets[i, :]
            
            # Обновляем стоимость актива
            asset_paths_dict[asset_name][:, step + 1] = (
                asset_paths_dict[asset_name][:, step] * 
                np.exp(asset_drift + asset_diffusion)
            )
            
            # Защита от банкротства
            asset_paths_dict[asset_name][asset_paths_dict[asset_name][:, step + 1] < 1e-6, step + 1] = 1e-6
    
    # Защита от банкротства портфеля
    X_paths[X_paths < 1e-6] = 1e-6
    
    return X_paths, t_grid, asset_paths_dict