"""
Сервис для стресс-тестирования портфеля.
Основан на StressTestSimulator из notebook.
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
from src.services.hjb_service import HJBStrategy, simulate_monte_carlo

warnings.filterwarnings('ignore')


class StressTestSimulator:
    """
    Симулятор для стресс-тестирования портфеля.
    
    Поддерживает:
    - Базовые и экстремальные стресс-сценарии
    - Шоковые изменения параметров (доходность, волатильность, корреляции)
    - Различные временные горизонты
    - Детальную аналитику риск-метрик
    """
    
    def __init__(
        self,
        mu: np.ndarray,
        cov_matrix: np.ndarray,
        initial_capital: float,
        risk_free_rate: float,
        gamma: float,
        asset_names: Optional[List[str]] = None
    ):
        """
        Инициализация симулятора.
        
        Args:
            mu: Вектор ожидаемых доходностей (с дивидендами)
            cov_matrix: Ковариационная матрица доходностей
            initial_capital: Начальный капитал (в рублях)
            risk_free_rate: Безрисковая ставка
            gamma: Коэффициент риск-аверсии
            asset_names: Названия активов (для визуализации)
        """
        self.mu_base = np.asarray(mu).flatten()
        self.cov_matrix_base = np.asarray(cov_matrix)
        self.X_0 = float(initial_capital)
        self.rf = float(risk_free_rate)
        self.gamma = float(gamma)
        self.n_assets = len(self.mu_base)
        self.asset_names = asset_names if asset_names is not None else \
                          [f"Asset_{i+1}" for i in range(self.n_assets)]
        
        # Создаем базовую стратегию
        self.strategy = HJBStrategy(
            mu=self.mu_base,
            cov_matrix=self.cov_matrix_base,
            risk_free_rate=self.rf,
            gamma=self.gamma,
            asset_names=self.asset_names
        )
        
        # Базовое Cholesky разложение
        try:
            self.sigma_base = np.linalg.cholesky(self.cov_matrix_base)
        except np.linalg.LinAlgError:
            # Если матрица не положительно определенная
            self.sigma_base = np.linalg.cholesky(
                self.cov_matrix_base + np.eye(self.n_assets) * 1e-6
            )
    
    @property
    def risk_free_rate(self):
        """Alias для совместимости."""
        return self.rf
    
    def simulate_scenario(
        self,
        scenario_name: str,
        mu: np.ndarray,
        sigma: np.ndarray,
        n_paths: int = 1000,
        t_grid: Optional[np.ndarray] = None,
        seed: Optional[int] = None
    ) -> Dict:
        """
        Симулирует портфель для заданного сценария.
        
        Args:
            scenario_name: Название сценария
            mu: Вектор ожидаемых доходностей для сценария
            sigma: Матрица Холецкого для сценария
            n_paths: Количество симуляций
            t_grid: Временная сетка (по умолчанию 252 дня)
            seed: Seed для воспроизводимости
        
        Returns:
            Словарь с результатами симуляции
        """
        # Валидация входных параметров
        mu = np.asarray(mu).flatten()
        sigma = np.asarray(sigma)
        
        if len(mu) != self.n_assets:
            raise ValueError(
                f"Размерность μ не совпадает: {len(mu)} элементов, "
                f"ожидается {self.n_assets}"
            )
        
        if sigma.shape[0] != self.n_assets or sigma.shape[1] != self.n_assets:
            raise ValueError(
                f"Размерность σ не совпадает: {sigma.shape}, "
                f"ожидается ({self.n_assets}, {self.n_assets})"
            )
        
        # Обновляем стратегию для нового сценария
        scenario_strategy = HJBStrategy(
            mu=mu,
            cov_matrix=np.dot(sigma, sigma.T),
            risk_free_rate=self.rf,
            gamma=self.gamma,
            asset_names=self.asset_names
        )
        
        # Получаем оптимальные веса
        optimal_weights = scenario_strategy.get_optimal_weights()
        
        # Определяем временную сетку
        if t_grid is None:
            horizon_years = 1.0
            n_steps = 252
            t_grid = np.linspace(0, horizon_years, n_steps)
        else:
            t_grid = np.asarray(t_grid)
            horizon_years = t_grid[-1] - t_grid[0]
            n_steps = len(t_grid) - 1
        
        # Монте-Карло симуляция
        monte_carlo_result = simulate_monte_carlo(
            mu=mu,
            cov_matrix=np.dot(sigma, sigma.T),
            weights=optimal_weights,
            initial_capital=self.X_0,
            horizon_years=horizon_years,
            n_paths=n_paths,
            n_steps=n_steps,
            random_seed=seed
        )
        
        # Статистика портфеля
        portfolio_stats = scenario_strategy.get_portfolio_stats()
        
        # Вычисляем дополнительные метрики
        # Извлекаем финальные капиталы из траекторий
        paths = monte_carlo_result.get('paths', [])
        if len(paths) > 0:
            final_capitals = np.array([path[-1] if len(path) > 0 else self.X_0 for path in paths])
        else:
            final_capitals = np.array([self.X_0])
        
        # VaR и CVaR в абсолютных значениях
        var_95 = float(np.quantile(final_capitals, 0.05)) if len(final_capitals) > 0 else 0.0
        var_99 = float(np.quantile(final_capitals, 0.01)) if len(final_capitals) > 0 else 0.0
        
        cvar_95 = float(np.mean(final_capitals[final_capitals <= var_95])) if len(final_capitals[final_capitals <= var_95]) > 0 else var_95
        cvar_99 = float(np.mean(final_capitals[final_capitals <= var_99])) if len(final_capitals[final_capitals <= var_99]) > 0 else var_99
        
        # Потери (относительно начального капитала)
        loss_var_95 = self.X_0 - var_95
        loss_var_99 = self.X_0 - var_99
        loss_cvar_95 = self.X_0 - cvar_95
        loss_cvar_99 = self.X_0 - cvar_99
        
        # Вероятности потерь
        losses = self.X_0 - final_capitals
        prob_loss_10 = float(np.mean(losses > 0.1 * self.X_0)) if len(losses) > 0 else 0.0
        prob_loss_50 = float(np.mean(losses > 0.5 * self.X_0)) if len(losses) > 0 else 0.0
        
        stats = monte_carlo_result.get('stats', {})
        
        return {
            'scenario_name': scenario_name,
            'metrics': {
                'mean_final': stats.get('mean_final', float(np.mean(final_capitals)) if len(final_capitals) > 0 else self.X_0),
                'median_final': stats.get('median_final', float(np.median(final_capitals)) if len(final_capitals) > 0 else self.X_0),
                'mean_return': stats.get('mean_return', 0.0),
                'median_return': stats.get('median_return', 0.0),
                'std_return': stats.get('std_return', portfolio_stats.get('volatility', 0.0)),
                'sharpe': stats.get('sharpe_ratio', portfolio_stats.get('sharpe_ratio', 0.0)),
                'var_95': var_95,
                'var_99': var_99,
                'cvar_95': cvar_95,
                'cvar_99': cvar_99,
                'loss_var_95': loss_var_95,
                'loss_var_99': loss_var_99,
                'loss_cvar_95': loss_cvar_95,
                'loss_cvar_99': loss_cvar_99,
                'mean_max_dd': stats.get('mean_max_drawdown', 0.0),
                'worst_dd': stats.get('mean_max_drawdown', 0.0),  # Упрощение
                'prob_loss': prob_loss_10,
                'prob_loss_50': prob_loss_50
            },
            'optimal_weights': optimal_weights.tolist(),
            'portfolio_stats': portfolio_stats,
            'monte_carlo': monte_carlo_result,
            'T_years': horizon_years,
            'n_paths': n_paths
        }


def run_stress_test(
    mu: List[float],
    cov_matrix: List[List[float]],
    initial_capital: float,
    risk_free_rate: float,
    gamma: float,
    scenarios: List[Dict],
    asset_names: Optional[List[str]] = None,
    n_paths: int = 1000,
    seed: Optional[int] = None
) -> Dict:
    """
    Запускает стресс-тестирование для списка сценариев.
    
    Args:
        mu: Ожидаемые доходности активов
        cov_matrix: Ковариационная матрица
        initial_capital: Начальный капитал
        risk_free_rate: Безрисковая ставка
        gamma: Коэффициент риск-аверсии
        scenarios: Список сценариев для тестирования
        asset_names: Названия активов
        n_paths: Количество Монте-Карло траекторий
        seed: Seed для воспроизводимости
    
    Returns:
        Результаты стресс-тестирования
    """
    # Инициализация симулятора
    simulator = StressTestSimulator(
        mu=np.array(mu),
        cov_matrix=np.array(cov_matrix),
        initial_capital=initial_capital,
        risk_free_rate=risk_free_rate,
        gamma=gamma,
        asset_names=asset_names
    )
    
    # Выполняем симуляции для каждого сценария
    results = {}
    
    for scenario in scenarios:
        scenario_name = scenario['name']
        scenario_type = scenario.get('type', 'return_shock')
        
        # Применяем шок в зависимости от типа сценария
        if scenario_type == 'return_shock':
            # Шок доходности
            mu_shock = simulator.mu_base * scenario.get('return_multiplier', 1.0)
            sigma_shock = simulator.sigma_base
        elif scenario_type == 'volatility_shock':
            # Шок волатильности
            mu_shock = simulator.mu_base
            vol_multiplier = scenario.get('volatility_multiplier', 1.0)
            cov_shock = simulator.cov_matrix_base * vol_multiplier
            try:
                sigma_shock = np.linalg.cholesky(cov_shock)
            except np.linalg.LinAlgError:
                sigma_shock = np.linalg.cholesky(
                    cov_shock + np.eye(simulator.n_assets) * 1e-6
                )
        elif scenario_type == 'correlation_shock':
            # Шок корреляций
            mu_shock = simulator.mu_base
            corr_multiplier = scenario.get('correlation_multiplier', 1.5)
            # Увеличиваем корреляции
            diag_elements = np.diag(simulator.cov_matrix_base)
            D = np.diag(np.sqrt(diag_elements))
            D_inv = np.linalg.inv(D)
            corr_matrix = D_inv @ simulator.cov_matrix_base @ D_inv
            corr_matrix_shocked = np.eye(simulator.n_assets) + corr_multiplier * (corr_matrix - np.eye(simulator.n_assets))
            corr_matrix_shocked = np.clip(corr_matrix_shocked, -0.999, 0.999)
            np.fill_diagonal(corr_matrix_shocked, 1.0)
            cov_shock = D @ corr_matrix_shocked @ D
            cov_shock = (cov_shock + cov_shock.T) / 2
            cov_shock += 1e-6 * np.eye(simulator.n_assets)
            try:
                sigma_shock = np.linalg.cholesky(cov_shock)
            except np.linalg.LinAlgError:
                sigma_shock = simulator.sigma_base
        else:
            # По умолчанию - базовый сценарий
            mu_shock = simulator.mu_base
            sigma_shock = simulator.sigma_base
        
        # Симулируем сценарий
        scenario_result = simulator.simulate_scenario(
            scenario_name=scenario_name,
            mu=mu_shock,
            sigma=sigma_shock,
            n_paths=n_paths,
            seed=seed if seed is not None else scenario.get('seed', None)
        )
        
        results[scenario.get('key', scenario_name.lower().replace(' ', '_'))] = scenario_result
    
    return {
        'results': results,
        'baseline': {
            'initial_capital': initial_capital,
            'risk_free_rate': risk_free_rate,
            'gamma': gamma,
            'n_assets': simulator.n_assets,
            'asset_names': simulator.asset_names
        }
    }
