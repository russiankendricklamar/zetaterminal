"""
Модуль расчёта риск-метрик: VaR, CVaR, исторический анализ потерь
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class VaRCalculator:
    """Расчёт Value at Risk и Conditional VaR"""
    
    @staticmethod
    def calculate_historical_var(
        returns: np.ndarray,
        optimal_weights: np.ndarray,
        initial_capital: float,
        confidence_levels: list = [0.95, 0.99]
    ) -> Dict[str, float]:

        if isinstance(returns, pd.DataFrame):
            returns = returns.values
            
        # Портфельные доходности
        portfolio_returns = (returns * optimal_weights).sum(axis=1)
        portfolio_losses = -portfolio_returns  # Потери (положительные значения)
        portfolio_losses_rub = portfolio_losses * initial_capital

        capital_95 = initial_capital * (1 + np.percentile(returns, (1 - 0.95) * 100))
        capital_99 = initial_capital * (1 + np.percentile(returns, (1 - 0.99) * 100))
        
        result = {
            "capital_95": float(capital_95),
            "capital_99": float(capital_99),
            "loss_pct_95": float(abs(np.percentile(returns, 5)) * 100),
            "loss_pct_99": float(abs(np.percentile(returns, 1)) * 100),
            "cvar_pct_95": float(abs(returns[returns <= np.percentile(returns, 5)].mean()) * 100),
            "cvar_pct_99": float(abs(returns[returns <= np.percentile(returns, 1)].mean()) * 100),
            "avg_loss": float(abs(returns[returns < 0].mean())),
            "max_loss": float(abs(returns.min())),
            "std_loss": float(returns.std())
        }
        
        for level in confidence_levels:
            percentile_idx = int(level * 100)
            loss_value = np.percentile(portfolio_losses_rub, percentile_idx)
            capital_value = initial_capital - loss_value
            loss_pct = (loss_value / initial_capital) * 100
            
            result[f'var_{percentile_idx}'] = float(loss_value)
            result[f'capital_{percentile_idx}'] = float(capital_value)
            result[f'loss_pct_{percentile_idx}'] = float(loss_pct)
            
        return result
    
    @staticmethod
    def calculate_cvar(
        returns: np.ndarray,
        optimal_weights: np.ndarray,
        initial_capital: float,
        confidence_levels: list = [0.95, 0.99]
    ) -> Dict[str, float]:

        if isinstance(returns, pd.DataFrame):
            returns = returns.values
            
        portfolio_returns = (returns * optimal_weights).sum(axis=1)
        portfolio_losses = -portfolio_returns
        portfolio_losses_rub = portfolio_losses * initial_capital
        
        result = {}
        
        for level in confidence_levels:
            percentile_idx = int(level * 100)
            var_threshold = np.percentile(portfolio_losses_rub, percentile_idx)
            
            cvar_value = portfolio_losses_rub[portfolio_losses_rub >= var_threshold].mean()
            cvar_pct = (cvar_value / initial_capital) * 100
            
            result[f'cvar_{percentile_idx}'] = float(cvar_value)
            result[f'cvar_pct_{percentile_idx}'] = float(cvar_pct)
            
        return result
    
    @staticmethod
    def compare_var_methods(
        returns: np.ndarray,
        optimal_weights: np.ndarray,
        initial_capital: float,
        mc_results: Optional[Dict] = None
    ) -> Dict:

        historical_var = VaRCalculator.calculate_historical_var(
            returns, optimal_weights, initial_capital, [0.95, 0.99]
        )
        historical_cvar = VaRCalculator.calculate_cvar(
            returns, optimal_weights, initial_capital, [0.95, 0.99]
        )
        
        result = {
            'historical': {**historical_var, **historical_cvar}
        }
        
        if mc_results:
            result['monte_carlo'] = mc_results
            
            # Расчёт разниц
            for level in [95, 99]:
                hist_var = historical_var.get(f'var_{level}', 0)
                mc_var = mc_results.get(f'var_{level}', 0)
                
                if hist_var > 0:
                    diff = mc_var - hist_var
                    pct_diff = (diff / hist_var) * 100
                    
                    result[f'diff_var_{level}_abs'] = float(diff)
                    result[f'diff_var_{level}_pct'] = float(pct_diff)
                    
                    # Анализ консервативности
                    if diff > 0:
                        result[f'conservatism_{level}'] = "MC консервативнее"
                    else:
                        result[f'conservatism_{level}'] = "MC недооценивает риск"
        
        return result


class RiskProfiler:
    """Комплексный анализ риск-профиля портфеля"""
    
    def __init__(self, returns: pd.DataFrame, optimal_weights: np.ndarray, 
                 initial_capital: float, rf_rate: float = 0.0):
        """
        Args:
            returns: DataFrame с дневными доходностями
            optimal_weights: веса портфеля
            initial_capital: начальный капитал
            rf_rate: безрисковая ставка (для Sharpe)
        """
        self.returns = returns
        self.weights = optimal_weights
        self.initial_capital = initial_capital
        self.rf_rate = rf_rate
        
    def calculate_portfolio_metrics(self) -> Dict[str, float]:
        portfolio_returns = (self.returns.values * self.weights).sum(axis=1)
        
        metrics = {
            'mean_return': float(np.mean(portfolio_returns)),
            'volatility': float(np.std(portfolio_returns)),
            'skewness': float(pd.Series(portfolio_returns).skew()),
            'kurtosis': float(pd.Series(portfolio_returns).kurtosis()),
            'var_95': float(np.percentile(portfolio_returns, 5)),  # 5-й процентиль
            'var_99': float(np.percentile(portfolio_returns, 1)),
            'cvar_95': float(portfolio_returns[portfolio_returns <= np.percentile(portfolio_returns, 5)].mean()),
        }
        
        # Sharpe Ratio
        if metrics['volatility'] > 0:
            metrics['sharpe_ratio'] = (metrics['mean_return'] - self.rf_rate) / metrics['volatility']
        else:
            metrics['sharpe_ratio'] = 0.0
            
        return metrics
    
    def calculate_risk_profile(self) -> Dict:

        var_metrics = VaRCalculator.calculate_historical_var(
            self.returns, self.weights, self.initial_capital, [0.90, 0.95, 0.99]
        )
        cvar_metrics = VaRCalculator.calculate_cvar(
            self.returns, self.weights, self.initial_capital, [0.90, 0.95, 0.99]
        )
        
        portfolio_metrics = self.calculate_portfolio_metrics()
        
        return {
            'var_metrics': var_metrics,
            'cvar_metrics': cvar_metrics,
            'portfolio_metrics': portfolio_metrics,
        }
    
    @staticmethod
    def get_api_metrics(returns, weights, capital, rf_rate=0.0) -> dict:
        profiler = RiskProfiler(returns, weights, capital, rf_rate)
        profile = profiler.calculate_risk_profile()
        
        return {
            "capital_95": float(profile['var_metrics']['capital_95']),
            "loss_pct_95": float(profile['var_metrics']['loss_pct_95']),
            "cvar_pct_95": float(profile['cvar_metrics']['cvar_pct_95']),
            "capital_99": float(profile['var_metrics']['capital_99']),
            "loss_pct_99": float(profile['var_metrics']['loss_pct_99']),
            "cvar_pct_99": float(profile['cvar_metrics']['cvar_pct_99'])
        }