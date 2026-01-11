"""
Сервис для HJB (Hamilton-Jacobi-Bellman) оптимизации портфеля.
Основан на задаче Мертона с CRRA utility.
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings

warnings.filterwarnings('ignore')


class HJBStrategy:
    """
    Стратегия оптимального управления портфелем на основе HJB-уравнения.
    
    Математическая модель: Задача Мертона с бесконечным горизонтом
    Решение: π* = (1/γ) Σ^(-1) (μ - r_f·1)
    """
    
    def __init__(
        self,
        mu: np.ndarray,
        cov_matrix: np.ndarray,
        risk_free_rate: float,
        gamma: float,
        asset_names: Optional[List[str]] = None,
        short_sales_allowed: bool = False,
        max_leverage: float = 1.0,
        min_weight: float = 0.0,
        normalize_weights: bool = True
    ):
        """
        Инициализация HJB стратегии.
        
        Args:
            mu: Вектор ожидаемых годовых доходностей (с дивидендами)
            cov_matrix: Ковариационная матрица доходностей
            risk_free_rate: Безрисковая ставка (в долях)
            gamma: Коэффициент относительного неприятия риска (γ > 0)
            asset_names: Названия активов
            short_sales_allowed: Разрешены ли короткие продажи
            max_leverage: Максимальное плечо
            min_weight: Минимальный вес актива
            normalize_weights: Нормировать ли веса до 1
        """
        # Валидация входных данных
        self.mu = np.asarray(mu).flatten()
        self.cov_matrix = np.asarray(cov_matrix)
        self.risk_free_rate = float(risk_free_rate)
        self.gamma = float(gamma)
        self.n_assets = len(self.mu)
        self.asset_names = asset_names if asset_names is not None else \
                          [f"Asset_{i+1}" for i in range(self.n_assets)]
        
        # Ограничения
        self.short_sales_allowed = short_sales_allowed
        self.max_leverage = max_leverage
        self.min_weight = min_weight
        self.normalize_weights = normalize_weights
        
        # Проверки
        if self.gamma <= 0:
            raise ValueError(f"γ должен быть > 0, получено {self.gamma}")
        
        if self.cov_matrix.shape != (self.n_assets, self.n_assets):
            raise ValueError(
                f"Размерность ковариационной матрицы {self.cov_matrix.shape} "
                f"не соответствует количеству активов {self.n_assets}"
            )
        
        if self.max_leverage <= 0:
            raise ValueError(f"max_leverage должен быть > 0, получено {self.max_leverage}")
        
        # Вычисляем избыточные доходности (критично для формулы Мертона)
        self.excess_mu = self.mu - self.risk_free_rate
        
        # Обратная матрица ковариации
        try:
            self.inv_cov_matrix = np.linalg.inv(self.cov_matrix)
        except np.linalg.LinAlgError:
            self.inv_cov_matrix = np.linalg.pinv(self.cov_matrix)
        
        # Формула Мертона: w_base = Σ^(-1) (μ - r_f·1)
        self._weights_base = np.dot(self.inv_cov_matrix, self.excess_mu)
    
    def get_optimal_weights(self) -> np.ndarray:
        """
        Вычисляет оптимальные веса портфеля.
        
        Returns:
            Оптимальные веса активов
        """
        # Базовые веса с учетом γ
        weights_raw = (1.0 / self.gamma) * self._weights_base
        
        # Запрет коротких продаж
        if not self.short_sales_allowed:
            weights_raw = np.maximum(weights_raw, 0.0)
        
        # Фильтрация малых весов
        weights_raw[weights_raw < self.min_weight] = 0.0
        
        # Нормировка
        total_weight = np.sum(weights_raw)
        
        if total_weight == 0:
            # Если все веса нулевые, возвращаем равномерное распределение
            weights = np.ones(self.n_assets) / self.n_assets
        elif self.normalize_weights:
            # Нормируем до 1
            weights = weights_raw / total_weight
        else:
            # Масштабируем до max_leverage
            if total_weight > self.max_leverage:
                weights = (self.max_leverage / total_weight) * weights_raw
            else:
                weights = weights_raw
        
        return weights
    
    def get_portfolio_stats(self) -> Dict:
        """
        Вычисляет статистику портфеля.
        
        Returns:
            Словарь со статистикой портфеля
        """
        weights = self.get_optimal_weights()
        
        # Ожидаемая доходность портфеля
        expected_return = np.dot(weights, self.mu)
        
        # Волатильность портфеля
        portfolio_variance = np.dot(weights, np.dot(self.cov_matrix, weights))
        volatility = np.sqrt(portfolio_variance)
        
        # Sharpe ratio
        sharpe_ratio = (expected_return - self.risk_free_rate) / volatility if volatility > 1e-10 else 0.0
        
        return {
            'optimal_weights': weights.tolist(),
            'expected_return': float(expected_return),
            'volatility': float(volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'risk_free_rate': self.risk_free_rate,
            'gamma': self.gamma
        }


def simulate_monte_carlo(
    mu: np.ndarray,
    cov_matrix: np.ndarray,
    weights: np.ndarray,
    initial_capital: float,
    horizon_years: float,
    n_paths: int,
    n_steps: int = 252,
    random_seed: Optional[int] = None
) -> Dict:
    """
    Монте-Карло симуляция портфеля.
    
    Args:
        mu: Ожидаемые доходности активов
        cov_matrix: Ковариационная матрица
        weights: Веса активов
        initial_capital: Начальный капитал
        horizon_years: Горизонт инвестирования (годы)
        n_paths: Количество траекторий
        n_steps: Количество временных шагов (торговых дней)
        random_seed: Seed для воспроизводимости
    
    Returns:
        Результаты симуляции
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Параметры симуляции
    dt = horizon_years / n_steps  # Временной шаг в годах
    
    # Cholesky разложение для коррелированных шоков
    try:
        L = np.linalg.cholesky(cov_matrix)
    except np.linalg.LinAlgError:
        # Если матрица не положительно определенная, используем приближение
        L = np.linalg.cholesky(cov_matrix + np.eye(len(cov_matrix)) * 1e-6)
    
    # Симуляция траекторий
    X_paths = np.zeros((n_paths, n_steps + 1))
    X_paths[:, 0] = initial_capital
    
    # Портфельная волатильность
    portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
    # Портфельная доходность
    portfolio_mu = np.dot(weights, mu)
    
    for i in range(n_paths):
        X = initial_capital
        for t in range(1, n_steps + 1):
            # Геометрическое броуновское движение
            Z = np.random.normal(0, 1)
            drift = (portfolio_mu - 0.5 * portfolio_vol ** 2) * dt
            diffusion = portfolio_vol * np.sqrt(dt) * Z
            X = X * np.exp(drift + diffusion)
            X_paths[i, t] = X
    
    # Вычисление статистик
    final_capitals = X_paths[:, -1]
    
    mean_final = float(np.mean(final_capitals))
    median_final = float(np.median(final_capitals))
    std_final = float(np.std(final_capitals))
    min_final = float(np.min(final_capitals))
    max_final = float(np.max(final_capitals))
    
    # VaR и CVaR (95%)
    var_95 = float(np.quantile(final_capitals, 0.05))
    cvar_95 = float(np.mean(final_capitals[final_capitals <= var_95]))
    
    # VaR и CVaR (99%)
    var_99 = float(np.quantile(final_capitals, 0.01))
    cvar_99 = float(np.mean(final_capitals[final_capitals <= var_99]))
    
    # Maximum Drawdown
    max_drawdowns = []
    for path in X_paths:
        peak = path[0]
        max_dd = 0
        for value in path:
            if value > peak:
                peak = value
            dd = (peak - value) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd
        max_drawdowns.append(max_dd)
    mean_max_drawdown = float(np.mean(max_drawdowns))
    
    # Годовая доходность
    returns = (final_capitals / initial_capital) ** (1 / horizon_years) - 1
    mean_return = float(np.mean(returns))
    median_return = float(np.median(returns))
    std_return = float(np.std(returns))
    
    # Sharpe ratio
    sharpe = mean_return / std_return if std_return > 1e-10 else 0.0
    
    # Квантили траекторий
    t_grid = np.linspace(0, horizon_years, n_steps + 1)
    median_path = np.median(X_paths, axis=0).tolist()
    q05_path = np.quantile(X_paths, 0.05, axis=0).tolist()
    q95_path = np.quantile(X_paths, 0.95, axis=0).tolist()
    
    # Выбираем подмножество траекторий для отображения (до 50)
    display_paths = X_paths[:min(50, n_paths)].tolist()
    
    return {
        'paths': display_paths,
        'median_path': median_path,
        'q05_path': q05_path,
        'q95_path': q95_path,
        't_grid': t_grid.tolist(),
        'stats': {
            'mean_final': mean_final,
            'median_final': median_final,
            'std_final': std_final,
            'min_final': min_final,
            'max_final': max_final,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'var_99': var_99,
            'cvar_99': cvar_99,
            'mean_max_drawdown': mean_max_drawdown,
            'mean_return': mean_return,
            'median_return': median_return,
            'std_return': std_return,
            'sharpe_ratio': float(sharpe)
        }
    }


def optimize_hjb(
    mu: List[float],
    cov_matrix: List[List[float]],
    risk_free_rate: float,
    gamma: float,
    asset_names: Optional[List[str]] = None,
    monte_carlo_params: Optional[Dict] = None
) -> Dict:
    """
    Полная HJB оптимизация с Монте-Карло симуляцией.
    
    Args:
        mu: Ожидаемые доходности активов
        cov_matrix: Ковариационная матрица
        risk_free_rate: Безрисковая ставка
        gamma: Коэффициент риск-аверсии
        asset_names: Названия активов
        monte_carlo_params: Параметры Монте-Карло симуляции
    
    Returns:
        Результаты оптимизации
    """
    # Создаем стратегию
    strategy = HJBStrategy(
        mu=np.array(mu),
        cov_matrix=np.array(cov_matrix),
        risk_free_rate=risk_free_rate,
        gamma=gamma,
        asset_names=asset_names
    )
    
    # Получаем оптимальные веса и статистику
    portfolio_stats = strategy.get_portfolio_stats()
    
    # Монте-Карло симуляция (если параметры указаны)
    monte_carlo_results = None
    if monte_carlo_params:
        monte_carlo_results = simulate_monte_carlo(
            mu=np.array(mu),
            cov_matrix=np.array(cov_matrix),
            weights=np.array(portfolio_stats['optimal_weights']),
            initial_capital=monte_carlo_params.get('initial_capital', 1000000),
            horizon_years=monte_carlo_params.get('horizon_years', 1.0),
            n_paths=monte_carlo_params.get('n_paths', 5000),
            n_steps=monte_carlo_params.get('n_steps', 252),
            random_seed=monte_carlo_params.get('random_seed', 42)
        )
    
    result = {
        'portfolio_stats': portfolio_stats,
        'monte_carlo': monte_carlo_results
    }
    
    return result
