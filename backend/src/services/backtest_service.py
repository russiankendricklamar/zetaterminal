"""
Сервис для бэктестинга портфеля.
Основан на блоках бэктестинга из notebook.

Модули:
- Monte Carlo (run_backtest) — MC симуляция через HJB
- Historical replay (run_historical_backtest) — реплей на реальных ценах
- Walk-forward optimization (walk_forward_optimization) — IS/OOS rolling
- Transaction costs (apply_transaction_costs) — turnover-based costs
"""
import warnings
from datetime import datetime, timedelta

import numpy as np

from src.services.hjb_service import HJBStrategy, simulate_monte_carlo

warnings.filterwarnings('ignore', category=DeprecationWarning)


# ── Rebalance frequency helpers ──────────────────────────────────────────────

_REBALANCE_PERIOD: dict[str, int] = {
    "daily": 1,
    "weekly": 5,
    "monthly": 21,
    "quarterly": 63,
}


def _rebalance_indices(n_periods: int, frequency: str) -> list[int]:
    """Return indices at which rebalancing occurs (0-based)."""
    step = _REBALANCE_PERIOD.get(frequency, 21)
    return list(range(0, n_periods, step))


# ── Strategy weight computation ──────────────────────────────────────────────

def _compute_strategy_weights(
    returns_window: np.ndarray,
    strategy_type: str,
    n_assets: int,
    current_weights: np.ndarray | None = None,
) -> np.ndarray:
    """Compute target weights for a given strategy on a lookback window.

    Supported strategies: equal_weight, min_variance, risk_parity, max_sharpe, custom.
    For optimization-based strategies, delegates to convex_portfolio_service.
    """
    if strategy_type == "equal_weight" or returns_window.shape[0] < 30:
        return np.ones(n_assets) / n_assets

    if strategy_type == "custom" and current_weights is not None:
        return current_weights

    # Import here to avoid circular imports at module level
    from src.services.convex_portfolio_service import compute_convex_portfolio

    objectives_map: dict[str, str] = {
        "min_variance": "min_variance",
        "risk_parity": "risk_parity",
        "max_sharpe": "max_sharpe",
    }

    obj_key = objectives_map.get(strategy_type)
    if obj_key is None:
        return np.ones(n_assets) / n_assets

    try:
        result = compute_convex_portfolio(
            returns=returns_window.tolist(),
            objectives=[obj_key],
            long_only=True,
        )
        weights_list = result["results"][obj_key]["weights_list"]
        return np.array(weights_list, dtype=float)
    except Exception:
        return np.ones(n_assets) / n_assets


# ── Transaction cost engine ──────────────────────────────────────────────────

def apply_transaction_costs(
    weights_history: list[np.ndarray],
    portfolio_values: np.ndarray,
    cost_bps: float,
) -> dict:
    """Deduct proportional transaction costs at each rebalance.

    Args:
        weights_history: list of weight vectors at each rebalance point.
        portfolio_values: portfolio value at each rebalance point (before cost).
        cost_bps: cost in basis points (e.g. 10 = 10 bps = 0.10%).

    Returns:
        dict with adjusted_values, total_cost, cost_pct.
    """
    cost_rate = cost_bps / 10_000.0
    adjusted = np.array(portfolio_values, dtype=float)
    total_cost = 0.0

    for i in range(1, len(weights_history)):
        turnover = float(np.sum(np.abs(weights_history[i] - weights_history[i - 1])))
        cost = turnover * adjusted[i] * cost_rate
        adjusted[i] -= cost
        total_cost += cost
        # propagate cost reduction to subsequent values
        if i < len(adjusted) - 1:
            ratio = adjusted[i] / (portfolio_values[i] if portfolio_values[i] > 0 else 1.0)
            for j in range(i + 1, len(adjusted)):
                adjusted[j] *= ratio
            break  # only adjust once; we recompute each step

    # Re-run properly: iterate through all rebalance points
    adjusted = np.array(portfolio_values, dtype=float)
    total_cost = 0.0
    cumulative_factor = 1.0

    for i in range(1, len(weights_history)):
        adjusted[i] = portfolio_values[i] * cumulative_factor
        turnover = float(np.sum(np.abs(weights_history[i] - weights_history[i - 1])))
        cost = turnover * adjusted[i] * cost_rate
        adjusted[i] -= cost
        total_cost += cost
        cumulative_factor = adjusted[i] / (portfolio_values[i] if portfolio_values[i] > 0 else 1.0)

    initial_val = portfolio_values[0] if len(portfolio_values) > 0 else 1.0
    cost_pct = total_cost / initial_val if initial_val > 0 else 0.0

    return {
        "adjusted_values": adjusted.tolist(),
        "total_cost": float(total_cost),
        "cost_pct": float(cost_pct),
    }


# ── Extended metrics (Calmar, Sortino, Information Ratio) ────────────────────

def _compute_extended_metrics(
    equity_curve: np.ndarray,
    risk_free_rate: float,
    benchmark_returns: np.ndarray | None = None,
) -> dict:
    """Compute Calmar, Sortino, and Information Ratio."""
    returns = np.diff(equity_curve) / equity_curve[:-1]
    n_years = len(equity_curve) / 252.0

    # CAGR
    cagr = (equity_curve[-1] / equity_curve[0]) ** (1.0 / max(n_years, 1e-6)) - 1.0

    # Max drawdown
    running_max = np.maximum.accumulate(equity_curve)
    drawdowns = (equity_curve - running_max) / running_max
    max_dd = float(np.min(drawdowns))

    # Calmar = CAGR / |max drawdown|
    calmar = float(cagr / abs(max_dd)) if abs(max_dd) > 1e-10 else 0.0

    # Sortino = (mean return - rf) / downside_deviation
    daily_rf = risk_free_rate / 252.0
    excess = returns - daily_rf
    downside = excess[excess < 0]
    downside_dev = float(np.std(downside) * np.sqrt(252)) if len(downside) > 0 else 1e-10
    sortino = float((cagr - risk_free_rate) / downside_dev) if downside_dev > 1e-10 else 0.0

    # Information Ratio
    info_ratio = 0.0
    if benchmark_returns is not None and len(benchmark_returns) == len(returns):
        active = returns - benchmark_returns
        te = float(np.std(active) * np.sqrt(252))
        info_ratio = float(np.mean(active) * 252 / te) if te > 1e-10 else 0.0

    return {
        "calmar_ratio": calmar,
        "sortino_ratio": sortino,
        "information_ratio": info_ratio,
    }


# ── Historical Backtest ──────────────────────────────────────────────────────

def run_historical_backtest(
    historical_prices: list[list[float]],
    asset_names: list[str] | None = None,
    rebalance_frequency: str = "monthly",
    strategy_type: str = "equal_weight",
    initial_weights: list[float] | None = None,
    lookback_window: int = 60,
    transaction_cost_bps: float = 10.0,
    risk_free_rate: float = 0.05,
    initial_capital: float = 1_000_000.0,
) -> dict:
    """Replay a portfolio strategy on actual historical price series.

    Args:
        historical_prices: T x N matrix of daily prices.
        asset_names: names of N assets.
        rebalance_frequency: daily / weekly / monthly / quarterly.
        strategy_type: equal_weight / min_variance / risk_parity / max_sharpe / custom.
        initial_weights: custom starting weights (required if strategy_type='custom').
        lookback_window: rolling window size (trading days) for optimization strategies.
        transaction_cost_bps: proportional transaction cost in basis points.
        risk_free_rate: annualized risk-free rate.
        initial_capital: starting portfolio value.

    Returns:
        dict with equity_curve, dates, metrics, weights_history, etc.
    """
    prices = np.asarray(historical_prices, dtype=float)
    if prices.ndim != 2:
        raise ValueError("historical_prices must be a T x N matrix")

    t_total, n_assets = prices.shape
    if t_total < 2:
        raise ValueError("Need at least 2 price observations")

    if asset_names is None or len(asset_names) != n_assets:
        asset_names = [f"Asset_{i + 1}" for i in range(n_assets)]

    # Compute daily returns from prices
    daily_returns = np.diff(prices, axis=0) / prices[:-1]
    n_returns = daily_returns.shape[0]

    # Determine rebalance schedule
    rebal_indices = _rebalance_indices(n_returns, rebalance_frequency)

    # Initialize
    if initial_weights is not None and len(initial_weights) == n_assets:
        weights = np.array(initial_weights, dtype=float)
        weights = weights / weights.sum()
    else:
        weights = np.ones(n_assets) / n_assets

    portfolio_value = initial_capital
    equity_curve = [portfolio_value]
    weights_history: list[np.ndarray] = [weights.copy()]
    rebalance_values: list[float] = [portfolio_value]
    rebalance_weights: list[np.ndarray] = [weights.copy()]

    for t in range(n_returns):
        # Daily portfolio return (weighted sum of asset returns)
        daily_ret = float(np.dot(weights, daily_returns[t]))
        portfolio_value *= (1.0 + daily_ret)

        # Update weights for drift
        if np.sum(weights) > 1e-10:
            asset_growth = 1.0 + daily_returns[t]
            drifted = weights * asset_growth
            weights = drifted / np.sum(drifted)

        # Rebalance check
        if t in rebal_indices and t > 0:
            lookback_start = max(0, t - lookback_window)
            window = daily_returns[lookback_start:t]

            new_weights = _compute_strategy_weights(
                window, strategy_type, n_assets, weights
            )

            # Transaction cost
            turnover = float(np.sum(np.abs(new_weights - weights)))
            cost = turnover * portfolio_value * (transaction_cost_bps / 10_000.0)
            portfolio_value -= cost

            weights = new_weights
            rebalance_values.append(portfolio_value)
            rebalance_weights.append(weights.copy())

        equity_curve.append(portfolio_value)
        weights_history.append(weights.copy())

    equity_arr = np.array(equity_curve)

    # Generate date strings
    start_date = datetime.now() - timedelta(days=n_returns)
    dates = [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(len(equity_curve))
    ]

    # Compute base metrics
    metrics = calculate_backtest_metrics(
        equity_curve=equity_arr,
        dates=dates,
        initial_capital=initial_capital,
        risk_free_rate=risk_free_rate,
    )

    # Extended metrics
    ext = _compute_extended_metrics(equity_arr, risk_free_rate)
    metrics["calmar_ratio"] = ext["calmar_ratio"]
    metrics["sortino_ratio"] = ext["sortino_ratio"]
    metrics["information_ratio"] = ext["information_ratio"]

    # Transaction cost summary
    tc_result = apply_transaction_costs(
        rebalance_weights, np.array(rebalance_values), transaction_cost_bps
    )

    # Benchmark: equal weight buy-and-hold
    ew = np.ones(n_assets) / n_assets
    bh_returns = daily_returns @ ew
    bh_curve = initial_capital * np.cumprod(np.concatenate([[1.0], 1.0 + bh_returns]))

    return {
        "equity_curve": equity_arr.tolist(),
        "benchmark_curve": bh_curve.tolist(),
        "dates": dates,
        "metrics": metrics,
        "weights_history": [w.tolist() for w in weights_history[::max(1, n_returns // 50)]],
        "asset_names": asset_names,
        "n_rebalances": len(rebalance_values) - 1,
        "total_transaction_cost": tc_result["total_cost"],
        "transaction_cost_pct": tc_result["cost_pct"],
        "strategy_type": strategy_type,
        "rebalance_frequency": rebalance_frequency,
    }


# ── Walk-Forward Optimization ────────────────────────────────────────────────

def walk_forward_optimization(
    historical_prices: list[list[float]],
    asset_names: list[str] | None = None,
    in_sample_window: int = 252,
    out_of_sample_window: int = 63,
    optimization_method: str = "max_sharpe",
    step_size: int | None = None,
    transaction_cost_bps: float = 10.0,
    risk_free_rate: float = 0.05,
    initial_capital: float = 1_000_000.0,
) -> dict:
    """Rolling walk-forward: optimize on IS window, test on OOS window, step forward.

    Args:
        historical_prices: T x N price matrix.
        asset_names: N asset names.
        in_sample_window: IS window size (trading days).
        out_of_sample_window: OOS window size (trading days).
        optimization_method: min_variance / risk_parity / max_sharpe.
        step_size: step forward size (defaults to out_of_sample_window).
        transaction_cost_bps: cost in bps.
        risk_free_rate: annualized risk-free rate.
        initial_capital: starting capital.

    Returns:
        dict with oos_equity_curve, per_window_metrics, aggregated_stats.
    """
    prices = np.asarray(historical_prices, dtype=float)
    if prices.ndim != 2:
        raise ValueError("historical_prices must be a T x N matrix")

    t_total, n_assets = prices.shape
    min_required = in_sample_window + out_of_sample_window + 1
    if t_total < min_required:
        raise ValueError(
            f"Need at least {min_required} price observations, got {t_total}"
        )

    if asset_names is None or len(asset_names) != n_assets:
        asset_names = [f"Asset_{i + 1}" for i in range(n_assets)]

    if step_size is None:
        step_size = out_of_sample_window

    daily_returns = np.diff(prices, axis=0) / prices[:-1]
    n_returns = daily_returns.shape[0]

    per_window_metrics: list[dict] = []
    oos_returns_all: list[float] = []
    portfolio_value = initial_capital
    oos_equity = [portfolio_value]
    prev_weights: np.ndarray | None = None

    window_start = 0
    while window_start + in_sample_window + out_of_sample_window <= n_returns:
        is_start = window_start
        is_end = window_start + in_sample_window
        oos_start = is_end
        oos_end = min(is_end + out_of_sample_window, n_returns)

        is_returns = daily_returns[is_start:is_end]
        oos_returns = daily_returns[oos_start:oos_end]

        # Optimize on IS
        weights = _compute_strategy_weights(
            is_returns, optimization_method, n_assets
        )

        # Transaction cost at start of OOS
        if prev_weights is not None:
            turnover = float(np.sum(np.abs(weights - prev_weights)))
            cost = turnover * portfolio_value * (transaction_cost_bps / 10_000.0)
            portfolio_value -= cost

        # IS metrics
        is_port_returns = is_returns @ weights
        is_vol = float(np.std(is_port_returns) * np.sqrt(252))
        is_mean = float(np.mean(is_port_returns) * 252)
        is_sharpe = is_mean / is_vol if is_vol > 1e-10 else 0.0

        # OOS replay
        oos_port_returns = oos_returns @ weights
        oos_vol = float(np.std(oos_port_returns) * np.sqrt(252))
        oos_mean = float(np.mean(oos_port_returns) * 252)
        oos_sharpe = oos_mean / oos_vol if oos_vol > 1e-10 else 0.0
        oos_total = float(np.prod(1.0 + oos_port_returns) - 1.0)

        for ret in oos_port_returns:
            portfolio_value *= (1.0 + float(ret))
            oos_equity.append(portfolio_value)
            oos_returns_all.append(float(ret))

        per_window_metrics.append({
            "window": len(per_window_metrics) + 1,
            "is_start": int(is_start),
            "is_end": int(is_end),
            "oos_start": int(oos_start),
            "oos_end": int(oos_end),
            "is_sharpe": round(is_sharpe, 4),
            "oos_sharpe": round(oos_sharpe, 4),
            "oos_return": round(oos_total, 6),
            "oos_vol": round(oos_vol, 6),
            "weights": weights.tolist(),
        })

        prev_weights = weights.copy()
        window_start += step_size

    oos_equity_arr = np.array(oos_equity)

    # Generate dates
    start_date = datetime.now() - timedelta(days=len(oos_equity))
    dates = [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(len(oos_equity))
    ]

    # Aggregated stats
    if len(per_window_metrics) > 0:
        avg_is_sharpe = float(np.mean([w["is_sharpe"] for w in per_window_metrics]))
        avg_oos_sharpe = float(np.mean([w["oos_sharpe"] for w in per_window_metrics]))
        degradation_ratio = avg_oos_sharpe / avg_is_sharpe if abs(avg_is_sharpe) > 1e-10 else 0.0
    else:
        avg_is_sharpe = 0.0
        avg_oos_sharpe = 0.0
        degradation_ratio = 0.0

    # OOS metrics
    oos_metrics = calculate_backtest_metrics(
        equity_curve=oos_equity_arr,
        dates=dates,
        initial_capital=initial_capital,
        risk_free_rate=risk_free_rate,
    )

    ext = _compute_extended_metrics(oos_equity_arr, risk_free_rate)
    oos_metrics["calmar_ratio"] = ext["calmar_ratio"]
    oos_metrics["sortino_ratio"] = ext["sortino_ratio"]

    return {
        "oos_equity_curve": oos_equity_arr.tolist(),
        "dates": dates,
        "metrics": oos_metrics,
        "per_window_metrics": per_window_metrics,
        "aggregated_stats": {
            "n_windows": len(per_window_metrics),
            "avg_is_sharpe": round(avg_is_sharpe, 4),
            "avg_oos_sharpe": round(avg_oos_sharpe, 4),
            "degradation_ratio": round(degradation_ratio, 4),
            "total_oos_return": round(
                float((oos_equity_arr[-1] / initial_capital) - 1.0), 6
            ) if len(oos_equity_arr) > 0 else 0.0,
        },
        "asset_names": asset_names,
        "optimization_method": optimization_method,
        "in_sample_window": in_sample_window,
        "out_of_sample_window": out_of_sample_window,
    }


def calculate_backtest_metrics(
    equity_curve: np.ndarray,
    dates: list[str],
    initial_capital: float,
    risk_free_rate: float,
    benchmark_returns: np.ndarray | None = None
) -> dict:
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
    cagr = (equity_curve[-1] / initial_capital) ** (1 / n_years) - 1 if n_years > 0 else 0.0

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


def calculate_monthly_returns(equity_curve: np.ndarray, dates: list[str]) -> dict:
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
    mu: list[float],
    cov_matrix: list[list[float]],
    initial_capital: float,
    risk_free_rate: float,
    gamma: float,
    horizon_years: float = 1.0,
    n_steps: int = 252,
    asset_names: list[str] | None = None,
    n_paths: int = 1000,
    seed: int | None = None
) -> dict:
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
