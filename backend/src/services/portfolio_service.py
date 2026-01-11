"""
Сервис для расчета метрик портфеля.
"""
import numpy as np
from typing import List, Dict, Any
from scipy import stats
from scipy.stats import norm


class PortfolioService:
    """Сервис для расчета метрик портфеля."""
    
    @staticmethod
    def calculate_portfolio_metrics(
        positions: List[Dict[str, Any]],
        risk_free_rate: float = 0.042,
        market_return: float = 0.10,
        market_volatility: float = 0.15
    ) -> Dict[str, Any]:
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
        
        # Волатильность портфеля (упрощенный расчет)
        # Для более точного расчета нужна корреляционная матрица
        portfolio_volatility = np.sqrt(
            sum(
                (pos.get('allocation', 0) / 100.0) ** 2 * vol ** 2
                for pos, vol in zip(positions, volatilities)
            )
        )
        
        # Если волатильность слишком мала, используем средневзвешенную
        if portfolio_volatility < 0.01:
            portfolio_volatility = sum(
                (pos.get('allocation', 0) / 100.0) * vol
                for pos, vol in zip(positions, volatilities)
            )
        
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
        
        # Beta (упрощенный расчет)
        beta = PortfolioService._calculate_beta(
            positions,
            volatilities,
            market_volatility
        )
        
        # Alpha
        alpha = annual_return - (risk_free_rate + beta * (market_return - risk_free_rate))
        
        # Skewness (асимметрия)
        skew = PortfolioService._calculate_skewness(daily_returns)
        
        # Max Drawdown (максимальная просадка)
        max_drawdown = PortfolioService._calculate_max_drawdown(daily_returns)
        
        # Diversification (коэффициент диверсификации)
        diversification = PortfolioService._calculate_diversification(positions)
        
        # Средняя корреляция
        avg_correlation = PortfolioService._calculate_avg_correlation(positions)
        
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
    def _calculate_sortino_ratio(annual_return: float, daily_returns: List[float], risk_free_rate: float) -> float:
        """Вычисляет коэффициент Сортино."""
        if not daily_returns:
            return 0.0
        
        # Вычисляем downside deviation (только отрицательные доходности)
        downside_returns = [r for r in daily_returns if r < 0]
        if not downside_returns:
            return 0.0
        
        downside_std = np.std(downside_returns) * np.sqrt(252)
        if downside_std == 0:
            return 0.0
        
        excess_return = annual_return - risk_free_rate
        return excess_return / downside_std
    
    @staticmethod
    def _calculate_beta(positions: List[Dict], volatilities: List[float], market_volatility: float) -> float:
        """Вычисляет бета портфеля."""
        if market_volatility == 0:
            return 1.0
        
        # Упрощенный расчет: средневзвешенная волатильность / волатильность рынка
        weighted_vol = sum(
            (pos.get('allocation', 0) / 100.0) * vol
            for pos, vol in zip(positions, volatilities)
        )
        
        # Предполагаем корреляцию с рынком 0.7
        correlation = 0.7
        beta = (weighted_vol / market_volatility) * correlation
        
        return max(0.5, min(beta, 2.0))  # Ограничиваем между 0.5 и 2.0
    
    @staticmethod
    def _calculate_skewness(returns: List[float]) -> float:
        """Вычисляет асимметрию (skewness)."""
        if len(returns) < 3:
            return 0.0
        return float(stats.skew(returns))
    
    @staticmethod
    def _calculate_max_drawdown(returns: List[float]) -> float:
        """Вычисляет максимальную просадку."""
        if not returns:
            return 0.0
        
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_dd = abs(np.min(drawdown))
        
        return float(max_dd)
    
    @staticmethod
    def _calculate_diversification(positions: List[Dict]) -> float:
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
    def _calculate_avg_correlation(positions: List[Dict]) -> float:
        """Вычисляет среднюю корреляцию между активами."""
        if len(positions) <= 1:
            return 1.0
        
        # Упрощенный расчет: для облигаций корреляция выше, для акций ниже
        bonds = sum(1 for pos in positions if 'SU' in pos.get('symbol', '') or 'RU000' in pos.get('symbol', ''))
        stocks = len(positions) - bonds
        
        # Средняя корреляция зависит от состава портфеля
        if bonds > stocks:
            avg_corr = 0.6 + 0.2 * (bonds / len(positions))
        else:
            avg_corr = 0.3 + 0.3 * (stocks / len(positions))
        
        return float(avg_corr)
    
    @staticmethod
    def _get_default_metrics() -> Dict[str, Any]:
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
