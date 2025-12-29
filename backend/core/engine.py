# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import logging
from typing import Dict, Tuple, List

# --- ИСПРАВЛЕННЫЕ ИМПОРТЫ ---
from quantitative_engine.block_1_loader import load_all_tickers
from quantitative_engine.block_2_returns import calculate_returns
from quantitative_engine.block_3_garch import estimate_garch
from quantitative_engine.block_4_filter import filter_portfolio
from quantitative_engine.block_5_divyields import calculate_dividend_yields
from quantitative_engine.block_6_hjb import optimize_hjb
from quantitative_engine.block_7_montecarlo import simulate_montecarlo
from quantitative_engine.block_8_analysis import analyze_results
from quantitative_engine.risk_metrics import RiskProfiler, VaRCalculator
from quantitative_engine.stress_test import StressTestSimulator as StressSimulator
from quantitative_engine.backtest import Backtester

logger = logging.getLogger(__name__)

class QuantitativeRiskEngine:
    def __init__(self, gamma: float = 3.0, initial_capital: float = 1_000_000,
                 n_paths: int = 5000, time_horizon: float = 1.0):
        self.gamma = gamma
        self.initial_capital = initial_capital
        self.n_paths = n_paths
        self.time_horizon = time_horizon
        self.rf_rate = 0.1394 # 13.94%

    def run(self, run_stress: bool = False) -> Dict:
        try: # Добавлена обработка ошибок
            logger.info("="*80)
            logger.info("QUANTITATIVE RISK ENGINE - STARTING")
            
            # 1. Загрузка
            priced_df, tickers = load_all_tickers()
            
            # 2. Доходности
            returns, cov_matrix, corr_matrix = calculate_returns(priced_df)
            
            # 3. GARCH
            vols, garch_results = estimate_garch(returns)
            
            # 4. Фильтрация
            returns_f, cov_f, assets_f = filter_portfolio(returns, cov_matrix, vols)
            
            # 5. Дивиденды
            mu = calculate_dividend_yields(returns_f, priced_df)

            logger.info(f"🔍 Перед optimizehjb: gamma={self.gamma}")
            
            # 6. Оптимизация
            strategy, weights = optimize_hjb(
                mu=mu,
                sigma=cov_f.values,
                gamma=self.gamma,
                rf_rate=self.rf_rate,
                asset_names=assets_f
            )

            logger.info(f"✅ После optimizehjb: weights={weights}")
            
            # 7. Симуляция
            X_paths, t_grid, asset_paths_dict = simulate_montecarlo(
                mu=mu,
                sigma=cov_f.values,
                weights=weights,
                X_0=self.initial_capital,
                T=self.time_horizon,
                n_paths=self.n_paths,
                asset_names=assets_f
            )
            
            # 8. Анализ
            metrics = analyze_results(
                X_paths=X_paths,
                t_grid=t_grid,
                X_0=self.initial_capital,
                rf=self.rf_rate,
                asset_names=assets_f,
                asset_paths=asset_paths_dict
            )

            metrics['chart_data'] = {
                'timestamps': t_grid.tolist(),  # временная сетка
                'capital_mean': np.mean(X_paths, axis=0).tolist(),      # средний путь
                'capital_q25': np.percentile(X_paths, 25, axis=0).tolist(),   # Q1
                'capital_q75': np.percentile(X_paths, 75, axis=0).tolist(),   # Q3
            }

            mean_final = metrics.get('mean_final_capital', self.initial_capital)
            total_return = (mean_final / self.initial_capital - 1)

            if self.time_horizon > 0:
                annualized_return = ((1 + total_return) ** (1 / self.time_horizon) - 1)
                metrics['mean_return'] = float(annualized_return) * 100
            else:
                metrics['mean_return'] = float(total_return) * 100

            volatility_annual = metrics.get('volatility', 0) * 100
            metrics['volatility'] = float(volatility_annual)

            mdd = metrics.get('max_drawdown', 0)
            mdd_pct = mdd * 100
            metrics['max_drawdown'] = max(min(mdd_pct, 0.0), -100.0)

            profiler = RiskProfiler(
                returns=returns_f, 
                optimal_weights=weights, 
                initial_capital=self.initial_capital,
                rf_rate=self.rf_rate
            )

            risk_profile = profiler.calculate_risk_profile()

            v_m = risk_profile['var_metrics']
            cv_m = risk_profile['cvar_metrics']

            hist_risk = {
                'capital_95': float(v_m.get('capital_95', self.initial_capital - v_m.get('var_95', 0))),
                'loss_pct_95': float(v_m.get('loss_pct_95', 0)),
                'cvar_pct_95': float(cv_m.get('cvar_pct_95', 0)),
                'capital_99': float(v_m.get('capital_99', self.initial_capital - v_m.get('var_99', 0))),
                'loss_pct_99': float(v_m.get('loss_pct_99', 0)),
                'cvar_pct_99': float(cv_m.get('cvar_pct_99', 0)),
            }

            avg_loss_val = v_m.get('mean_loss', 0)
            max_loss_val = v_m.get('max_loss', 0)
            std_loss_val = v_m.get('std_loss', 0)

            metrics['var_metrics'] = RiskProfiler.get_api_metrics(
                returns=returns_f, 
                weights=weights, 
                capital=self.initial_capital,
                rf_rate=self.rf_rate
            )

            profiler = RiskProfiler(returns_f, weights, self.initial_capital, self.rf_rate)

            stress_results = {}
            if run_stress:
                simulator = StressSimulator(mu, cov_f.values, self.initial_capital, assets_f)
                
                res_crisis = simulator.run_scenario("crisis")
                res_swan = simulator.run_scenario("black_swan")
                
                stress_results = {
                    "crisis": {
                        "scenario_name": "Кризис (-30% доходности)",
                        "expected_capital": float(res_crisis.expected_capital),
                        "max_drawdown": float(res_crisis.max_drawdown),
                        "prob_of_loss": float(getattr(res_crisis, 'prob_of_loss', 0.65))
                    },
                    "black_swan": {
                        "scenario_name": "Черный лебедь (-50% доходности)",
                        "expected_capital": float(res_swan.expected_capital),
                        "max_drawdown": float(res_swan.max_drawdown),
                        "prob_of_loss": float(getattr(res_swan, 'prob_of_loss', 0.85))
                    }
                }

            portfolio_returns = returns_f.values @ weights
            all_losses = portfolio_returns[portfolio_returns < 0]

            avg_loss_val = float(abs(all_losses.mean()) ) if all_losses.size > 0 else 0.0
            max_loss_val = float(abs(all_losses.min())) if all_losses.size > 0 else 0.0
            std_loss_val = float(portfolio_returns.std()) if portfolio_returns.size > 0 else 0.0

            def to_float(val):
                if isinstance(val, (pd.Series, np.ndarray)):
                    return float(val.mean()) if val.size > 0 else 0.0
                return float(val) if val is not None else 0.0

            var_metrics_final = {
                'capital_95': float(hist_risk.get('capital_95', 0)),
                'loss_pct_95': float(hist_risk.get('loss_pct_95', 0)),
                'cvar_pct_95': float(hist_risk.get('cvar_pct_95', 0)),
                'capital_99': float(hist_risk.get('capital_99', 0)),
                'loss_pct_99': float(hist_risk.get('loss_pct_99', 0)),
                'cvar_pct_99': float(hist_risk.get('cvar_pct_99', 0)),
                'avg_loss': float(avg_loss_val), 
                'max_loss': float(max_loss_val),
                'std_loss': float(std_loss_val)
            }

            c_95 = hist_risk['capital_95']

            return {
                'status': 'success',
                'metrics': {
                    **metrics,
                    'var_metrics': var_metrics_final
                },
                'stress_tests': stress_results,
                'raw_data': {
                    'weights': weights.tolist(),
                    'asset_names': assets_f,
                    'mu': mu.tolist(),
                    'cov': cov_f.values.tolist()
                }
            }

        except Exception as e:
            logger.error(f"❌ Ошибка в пайплайне: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e)
            }