"""
Сервис для бэктестинга портфеля.
Основан на блоках бэктестинга из notebook.
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
from datetime import datetime, timedelta
from src.services.hjb_service import HJBStrategy, simulate_monte_carlo

warnings.filterwarnings('ignore')


def calculate_backtest_metrics(
    equity_curve: np.ndarray,
    dates: List[str],
    initial_capital: float,
    risk_free_rate: float,
    benchmark_returns: Optional[np.ndarray] = None
) -> Dict:
    """
    Вычисляет метрики бэктеста на основе equity curve.
    
    Args:
        equity_curve: Массив значений капитала во времени
        dates: Список дат (строки)
        initial_capital: Начальный капитал
        risk_free_rate: Безрисковая ставка (годовая)
        benchmark_returns: Доходности бенчмарка (опционально)
    
    Returns:
        Словарь с метриками бэктеста
    """
    # Вычисляем доходности
    returns = np.diff(equity_curve) / equity_curve[:-1]
    
    # Total Return
    total_return = (equity_curve[-1] - initial_capital) / initial_capital
    
    # CAGR (Compound Annual Growth Rate)
    n_years = len(equity_curve) / 252  # Предполагаем 252 торговых дня в году
    if n_years > 0:
        cagr = (equity_curve[-1] / initial_capital) ** (1 / n_years) - 1
    else:
        cagr = 0.0
    
    # Волатильность (годовая)
    volatility = np.std(returns) * np.sqrt(252)
    
    # Sharpe Ratio
    sharpe_ratio = (cagr - risk_free_rate) / volatility if volatility > 1e-10 else 0.0
    
    # Maximum Drawdown
    peak = initial_capital
    max_drawdown = 0.0
    drawdown_periods = []
    current_dd_start = None
    
    for i, value in enumerate(equity_curve):
        if value > peak:
            peak = value
            if current_dd_start is not None:
                # Завершилась просадка
                drawdown_periods.append({
                    'start_idx': current_dd_start[0],
                    'end_idx': i - 1,
                    'peak': current_dd_start[1],
                    'trough': min(equity_curve[current_dd_start[0]:i]),
                    'recovery_idx': i - 1
                })
                current_dd_start = None
        else:
            dd = (value - peak) / peak
            if dd < max_drawdown:
                max_drawdown = dd
                if current_dd_start is None:
                    current_dd_start = (i, peak)
    
    # Завершаем последнюю просадку если она не закончилась
    if current_dd_start is not None:
        drawdown_periods.append({
            'start_idx': current_dd_start[0],
            'end_idx': len(equity_curve) - 1,
            'peak': current_dd_start[1],
            'trough': min(equity_curve[current_dd_start[0]:]),
            'recovery_idx': None
        })
    
    # Сортируем просадки по величине
    drawdown_periods.sort(key=lambda x: (x['trough'] - x['peak']) / x['peak'])
    
    # Топ-3 просадки
    top_drawdowns = drawdown_periods[:3]
    
    # Месячная доходность
    monthly_returns = calculate_monthly_returns(equity_curve, dates)
    
    # Статистика сделок (упрощенная версия)
    positive_returns = returns[returns > 0]
    negative_returns = returns[returns < 0]
    
    win_rate = len(positive_returns) / len(returns) if len(returns) > 0 else 0.0
    avg_profit = np.mean(positive_returns) * initial_capital if len(positive_returns) > 0 else 0.0
    avg_loss = abs(np.mean(negative_returns)) * initial_capital if len(negative_returns) > 0 else 1.0
    profit_factor = (np.sum(positive_returns) / abs(np.sum(negative_returns))) if len(negative_returns) > 0 and np.sum(negative_returns) < 0 else 0.0
    
    # Среднее время удержания (упрощенно - средняя длительность положительных периодов)
    hold_time = calculate_average_hold_time(returns)
    
    return {
        'total_return': float(total_return),
        'cagr': float(cagr),
        'volatility': float(volatility),
        'sharpe_ratio': float(sharpe_ratio),
        'max_drawdown': float(max_drawdown),
        'drawdowns': [
            {
                'period': f"{dates[dd['start_idx']][:7]} — {dates[dd['end_idx']][:7] if dd['end_idx'] < len(dates) else dates[-1][:7]}",
                'amount': float((dd['trough'] - dd['peak']) / dd['peak'] * 100),
                'recovery': 'N/A' if dd['recovery_idx'] is None else f"{(dd['recovery_idx'] - dd['end_idx']) / 252 * 12:.0f} mo"
            }
            for dd in top_drawdowns
        ],
        'monthly_returns': monthly_returns,
        'total_trades': len(returns),
        'win_rate': float(win_rate),
        'profit_factor': float(profit_factor),
        'avg_profit': float(avg_profit),
        'avg_loss': float(avg_loss),
        'hold_time': float(hold_time),
        'equity_curve': equity_curve.tolist(),
        'dates': dates
    }


def calculate_monthly_returns(equity_curve: np.ndarray, dates: List[str]) -> Dict:
    """
    Вычисляет месячную доходность.
    
    Args:
        equity_curve: Массив значений капитала
        dates: Список дат
    
    Returns:
        Словарь с месячной доходностью {year: {month: return}}
    """
    monthly_returns = {}
    
    # Группируем по годам и месяцам
    for i in range(1, len(equity_curve)):
        if i < len(dates):
            date_str = dates[i]
            try:
                # Парсим дату (предполагаем формат YYYY-MM-DD)
                year = date_str[:4]
                month = int(date_str[5:7])
                
                if year not in monthly_returns:
                    monthly_returns[year] = {}
                
                # Вычисляем доходность за месяц
                if i > 0:
                    monthly_return = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] * 100
                    monthly_returns[year][month] = monthly_return
            except (ValueError, IndexError):
                continue
    
    return monthly_returns


def calculate_average_hold_time(returns: np.ndarray) -> float:
    """
    Вычисляет среднее время удержания позиции (в днях).
    
    Args:
        returns: Массив доходностей
    
    Returns:
        Среднее время удержания в днях
    """
    if len(returns) == 0:
        return 0.0
    
    # Упрощенный подход: считаем среднюю длительность положительных периодов
    positive_periods = []
    current_period_length = 0
    
    for ret in returns:
        if ret > 0:
            current_period_length += 1
        else:
            if current_period_length > 0:
                positive_periods.append(current_period_length)
            current_period_length = 0
    
    if current_period_length > 0:
        positive_periods.append(current_period_length)
    
    return np.mean(positive_periods) if len(positive_periods) > 0 else 0.0


def run_backtest(
    mu: List[float],
    cov_matrix: List[List[float]],
    initial_capital: float,
    risk_free_rate: float,
    gamma: float,
    horizon_years: float = 1.0,
    n_steps: int = 252,
    asset_names: Optional[List[str]] = None,
    n_paths: int = 1000,
    seed: Optional[int] = None
) -> Dict:
    """
    Запускает бэктест портфеля используя Монте-Карло симуляцию.
    
    Args:
        mu: Ожидаемые доходности активов
        cov_matrix: Ковариационная матрица
        initial_capital: Начальный капитал
        risk_free_rate: Безрисковая ставка
        gamma: Коэффициент риск-аверсии
        horizon_years: Горизонт инвестирования (годы)
        n_steps: Количество временных шагов
        asset_names: Названия активов
        n_paths: Количество Монте-Карло траекторий
        seed: Seed для воспроизводимости
    
    Returns:
        Результаты бэктеста
    """
    # Создаем стратегию
    strategy = HJBStrategy(
        mu=np.array(mu),
        cov_matrix=np.array(cov_matrix),
        risk_free_rate=risk_free_rate,
        gamma=gamma,
        asset_names=asset_names
    )
    
    # Получаем оптимальные веса
    optimal_weights = strategy.get_optimal_weights()
    portfolio_stats = strategy.get_portfolio_stats()
    
    # Монте-Карло симуляция
    monte_carlo_result = simulate_monte_carlo(
        mu=np.array(mu),
        cov_matrix=np.array(cov_matrix),
        weights=optimal_weights,
        initial_capital=initial_capital,
        horizon_years=horizon_years,
        n_paths=n_paths,
        n_steps=n_steps,
        random_seed=seed,
        risk_free_rate=risk_free_rate
    )
    
    # Используем медианную траекторию как equity curve
    equity_curve = np.array(monte_carlo_result['median_path'])
    
    # Генерируем даты
    start_date = datetime.now() - timedelta(days=int(horizon_years * 365))
    dates = [
        (start_date + timedelta(days=int(i * horizon_years * 365 / n_steps))).strftime('%Y-%m-%d')
        for i in range(len(equity_curve))
    ]
    
    # Вычисляем метрики
    metrics = calculate_backtest_metrics(
        equity_curve=equity_curve,
        dates=dates,
        initial_capital=initial_capital,
        risk_free_rate=risk_free_rate
    )
    
    # Добавляем данные для графика
    benchmark_returns = np.array([0.05 / 252] * len(equity_curve))  # Упрощенный бенчмарк
    benchmark_curve = initial_capital * (1 + benchmark_returns).cumprod()
    
    return {
        'metrics': metrics,
        'equity_curve': equity_curve.tolist(),
        'benchmark_curve': benchmark_curve.tolist(),
        'dates': dates,
        'optimal_weights': optimal_weights.tolist(),
        'portfolio_stats': portfolio_stats,
        'monte_carlo_stats': monte_carlo_result.get('stats', {})
    }
