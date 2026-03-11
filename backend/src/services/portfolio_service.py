"""
Сервис для расчета метрик портфеля.
"""
from typing import Any

import numpy as np
from scipy import stats
from scipy.stats import norm


class PortfolioService:
    """Сервис для расчета метрик портфеля."""

    @staticmethod
    def calculate_portfolio_metrics(
        positions: list[dict[str, Any]],
        risk_free_rate: float = 0.042,
        market_return: float = 0.10,
        market_volatility: float = 0.15,
        market_correlation: float = 0.7
    ) -> dict[str, Any]:
        """
        Вычисляет все метрики портфеля на основе позиций.

        Args:
            positions: Список позиций портфеля с полями:
                - symbol: символ актива
                - price: цена
                - dayChange: дневное изменение в процентах
                - notional: номинальная стоимость позиции
                - allocation: вес в портфеле (в процентах)
                - targetAllocation: целевой вес (в процентах)
            risk_free_rate: Безрисковая ставка (по умолчанию 4.2%)
            market_return: Ожидаемая доходность рынка (по умолчанию 10%)
            market_volatility: Волатильность рынка (по умолчанию 15%)
            market_correlation: Корреляция портфеля с рынком (по умолчанию 0.7)

        Returns:
            Словарь со всеми метриками портфеля
        """
        if not positions or len(positions) == 0:
            return PortfolioService._get_default_metrics()

        # Преобразуем allocation из процентов в доли
        total_allocation = sum(pos.get('allocation', 0) for pos in positions)
        if total_allocation == 0:
            return PortfolioService._get_default_metrics()

        # Вычисляем общую стоимость портфеля (NAV)
        total_notional = sum(pos.get('notional', 0) for pos in positions)
        nav = total_notional

        # Вычисляем дневные доходности активов
        daily_returns = []
        for pos in positions:
            day_change = pos.get('dayChange', 0) / 100.0  # Преобразуем из процентов
            daily_returns.append(day_change)

        # Взвешенная доходность портфеля
        portfolio_daily_return = sum(
            (pos.get('allocation', 0) / 100.0) * (pos.get('dayChange', 0) / 100.0)
            for pos in positions
        )

        # Годовая доходность (предполагаем 252 торговых дня)
        annual_return = portfolio_daily_return * 252

        # Вычисляем волатильности активов (на основе dayChange)
        # Используем историческую волатильность как приближение
        volatilities = []
        for pos in positions:
            day_change = abs(pos.get('dayChange', 0)) / 100.0
            # Преобразуем дневную волатильность в годовую
            vol = min(day_change * np.sqrt(252), 0.5)  # Ограничиваем максимум 50%
            volatilities.append(vol)

        # Волатильность портфеля: σ²_p = Σ_i Σ_j w_i w_j σ_i σ_j ρ_ij
        # Без корреляционной матрицы используем constant-correlation model
        # ρ_avg ≈ 0.3 (типичная межотраслевая корреляция акций)
        avg_corr = 0.3
        weights = np.array([pos.get('allocation', 0) / 100.0 for pos in positions])
        vols = np.array(volatilities)
        n = len(weights)
        if n > 0 and np.sum(vols) > 0:
            # σ²_p = Σ w²_i σ²_i + avg_corr * Σ_{i≠j} w_i w_j σ_i σ_j
            diag_term = float(np.sum(weights ** 2 * vols ** 2))
            cross_term = float((np.sum(weights * vols)) ** 2 - np.sum(weights ** 2 * vols ** 2))
            portfolio_volatility = float(np.sqrt(max(diag_term + avg_corr * cross_term, 0.0)))
        else:
            portfolio_volatility = 0.0

        if portfolio_volatility < 0.01:
            portfolio_volatility = float(np.sum(weights * vols))

        # Total P&L (прибыль/убыток)
        total_pnl = sum(
            pos.get('notional', 0) * (pos.get('dayChange', 0) / 100.0)
            for pos in positions
        )

        # VaR 95% (Value at Risk)
        # Используем параметрический метод
        var_95 = PortfolioService._calculate_var(
            portfolio_volatility,
            nav,
            confidence_level=0.95
        )
        var_95_daily = PortfolioService._calculate_var(
            portfolio_volatility / np.sqrt(252),
            nav,
            confidence_level=0.95
        )

        # Sharpe Ratio
        sharpe_ratio = PortfolioService._calculate_sharpe_ratio(
            annual_return,
            portfolio_volatility,
            risk_free_rate
        )

        # Sortino Ratio
        sortino_ratio = PortfolioService._calculate_sortino_ratio(
            annual_return,
            daily_returns,
            risk_free_rate
        )

        # Beta: β = Cov(R_p, R_m) / Var(R_m), fallback to proxy
        beta = PortfolioService._calculate_beta(
            positions,
            volatilities,
            market_volatility,
        )

        # Alpha
        alpha = annual_return - (risk_free_rate + beta * (market_return - risk_free_rate))

        # Skewness (асимметрия)
        skew = PortfolioService._calculate_skewness(daily_returns)

        # Max Drawdown (максимальная просадка)
        max_drawdown = PortfolioService._calculate_max_drawdown(daily_returns)

        # Diversification (коэффициент диверсификации)
        diversification = PortfolioService._calculate_diversification(positions)

        # Средняя корреляция (обратная оценка из портфельной волатильности)
        avg_correlation = PortfolioService._calculate_avg_correlation(
            positions, volatilities, portfolio_volatility
        )

        return {
            "total_pnl": float(total_pnl),
            "nav": float(nav),
            "annual_return": float(annual_return),
            "daily_return": float(portfolio_daily_return),
            "volatility": float(portfolio_volatility),
            "var_95": float(var_95),
            "var_95_daily": float(var_95_daily),
            "var_95_percent": float(var_95 / nav * 100) if nav > 0 else 0.0,
            "sharpe_ratio": float(sharpe_ratio),
            "sortino_ratio": float(sortino_ratio),
            "beta": float(beta),
            "alpha": float(alpha),
            "skew": float(skew),
            "max_drawdown": float(max_drawdown),
            "diversification": float(diversification),
            "avg_correlation": float(avg_correlation),
            "risk_free_rate": float(risk_free_rate),
            "num_positions": len(positions)
        }

    @staticmethod
    def _calculate_var(volatility: float, portfolio_value: float, confidence_level: float = 0.95) -> float:
        """Вычисляет Value at Risk."""
        z_score = norm.ppf(1 - confidence_level)
        var = abs(z_score) * volatility * portfolio_value
        return var

    @staticmethod
    def _calculate_sharpe_ratio(return_: float, volatility: float, risk_free_rate: float) -> float:
        """Вычисляет коэффициент Шарпа."""
        if volatility == 0:
            return 0.0
        excess_return = return_ - risk_free_rate
        return excess_return / volatility

    @staticmethod
    def _calculate_sortino_ratio(annual_return: float, daily_returns: list[float], risk_free_rate: float) -> float:
        """Вычисляет коэффициент Сортино."""
        if not daily_returns:
            return 0.0

        # Downside deviation: sqrt(E[min(r - rf_daily, 0)²]) * sqrt(252)
        rf_daily = risk_free_rate / 252
        downside_sq = [(min(r - rf_daily, 0)) ** 2 for r in daily_returns]
        downside_var = sum(downside_sq) / len(daily_returns)
        downside_std = np.sqrt(downside_var) * np.sqrt(252)
        if downside_std < 1e-12:
            return 0.0

        excess_return = annual_return - risk_free_rate
        return excess_return / downside_std

    @staticmethod
    def _calculate_beta(
        positions: list[dict],
        volatilities: list[float],
        market_volatility: float,
        market_returns: list[float] | None = None,
        portfolio_returns: list[float] | None = None,
    ) -> float:
        """β = Cov(R_p, R_m) / Var(R_m).

        If historical returns are available, compute exact beta.
        Otherwise fallback: β = (σ_p / σ_m) × ρ_assumed (ρ=0.7).
        """
        # Exact beta from returns when available
        if (
            market_returns is not None
            and portfolio_returns is not None
            and len(market_returns) >= 20
            and len(portfolio_returns) >= 20
        ):
            m = np.array(market_returns[-min(len(market_returns), len(portfolio_returns)):])
            p = np.array(portfolio_returns[-len(m):])
            var_m = float(np.var(m, ddof=1))
            if var_m > 1e-12:
                cov_pm = float(np.cov(p, m, ddof=1)[0, 1])
                return cov_pm / var_m

        # Fallback: proxy β = (σ_p / σ_m) × ρ_assumed
        if market_volatility <= 0:
            return 1.0
        weighted_vol = sum(
            (pos.get('allocation', 0) / 100.0) * vol
            for pos, vol in zip(positions, volatilities, strict=False)
        )
        return float((weighted_vol / market_volatility) * 0.7)

    @staticmethod
    def _calculate_skewness(returns: list[float]) -> float:
        """Вычисляет асимметрию (skewness)."""
        if len(returns) < 3:
            return 0.0
        return float(stats.skew(returns))

    @staticmethod
    def _calculate_max_drawdown(returns: list[float]) -> float:
        """Вычисляет максимальную просадку."""
        if not returns:
            return 0.0

        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_dd = abs(np.min(drawdown))

        return float(max_dd)

    @staticmethod
    def _calculate_diversification(positions: list[dict]) -> float:
        """Вычисляет коэффициент диверсификации."""
        if len(positions) <= 1:
            return 0.0

        # Используем индекс Херфиндаля-Хиршмана (HHI)
        allocations = [pos.get('allocation', 0) / 100.0 for pos in positions]
        hhi = sum(alloc ** 2 for alloc in allocations)

        # Нормализуем: 1 - HHI (чем ближе к 1, тем лучше диверсификация)
        diversification = 1 - hhi

        return float(diversification)

    @staticmethod
    def _calculate_avg_correlation(positions: list[dict], volatilities: list[float] | None = None,
                                   portfolio_volatility: float | None = None) -> float:
        """
        Оценивает среднюю корреляцию между активами.

        Без исторических рядов используется обратная оценка из соотношения
        портфельной и средневзвешенной волатильностей:
            σ_p² = Σ(w_i² σ_i²) + Σ_{i≠j}(w_i w_j σ_i σ_j ρ̄)
        Решая для ρ̄:
            ρ̄ = (σ_p² - Σ(w_i² σ_i²)) / (Σ(w_i σ_i)² - Σ(w_i² σ_i²))
        """
        n = len(positions)
        if n <= 1:
            return 1.0

        if volatilities is None or portfolio_volatility is None:
            # Без данных возвращаем разумную оценку для диверсифицированного портфеля
            return 1.0 / n + (1.0 - 1.0 / n) * 0.5

        weights = [pos.get('allocation', 0) / 100.0 for pos in positions]

        # Σ(w_i² σ_i²)
        sum_w2_s2 = sum(w ** 2 * s ** 2 for w, s in zip(weights, volatilities, strict=False))

        # (Σ w_i σ_i)²
        sum_ws_sq = sum(w * s for w, s in zip(weights, volatilities, strict=False)) ** 2

        denominator = sum_ws_sq - sum_w2_s2
        if abs(denominator) < 1e-14:
            return 1.0

        numerator = portfolio_volatility ** 2 - sum_w2_s2
        avg_corr = numerator / denominator

        # Ограничиваем результат в допустимом диапазоне [-1, 1]
        return float(np.clip(avg_corr, -1.0, 1.0))

    @staticmethod
    def _get_default_metrics() -> dict[str, Any]:
        """Возвращает метрики по умолчанию."""
        return {
            "total_pnl": 0.0,
            "nav": 0.0,
            "annual_return": 0.0,
            "daily_return": 0.0,
            "volatility": 0.0,
            "var_95": 0.0,
            "var_95_daily": 0.0,
            "var_95_percent": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "beta": 1.0,
            "alpha": 0.0,
            "skew": 0.0,
            "max_drawdown": 0.0,
            "diversification": 0.0,
            "avg_correlation": 0.0,
            "risk_free_rate": 0.042,
            "num_positions": 0
        }
