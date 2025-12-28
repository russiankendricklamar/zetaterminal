# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import logging
from typing import Dict, Tuple, List

# --- ИСПРАВЛЕННЫЕ ИМПОРТЫ ---
from quantitative_engine.block_1_loader import load_all_tickers # Исправлено здесь
from quantitative_engine.block_2_returns import calculate_returns
from quantitative_engine.block_3_garch import estimate_garch
from quantitative_engine.block_4_filter import filter_portfolio
from quantitative_engine.block_5_divyields import calculate_dividend_yields
from quantitative_engine.block_6_hjb import optimize_hjb
from quantitative_engine.block_7_montecarlo import simulate_montecarlo
from quantitative_engine.block_8_analysis import analyze_results

logger = logging.getLogger(__name__)

class QuantitativeRiskEngine:
    def __init__(self, gamma: float = 3.0, initial_capital: float = 1_000_000,
                 n_paths: int = 5000, time_horizon: float = 1.0):
        self.gamma = gamma
        self.initial_capital = initial_capital
        self.n_paths = n_paths
        self.time_horizon = time_horizon
        self.rf_rate = 0.1394 # 13.94%

    def run(self) -> Dict:
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
            
            # 6. Оптимизация
            strategy, weights = optimize_hjb(
                mu=mu,
                sigma=cov_f.values,
                gamma=self.gamma,
                rf_rate=self.rf_rate,
                asset_names=assets_f
            )
            
            # 7. Симуляция
            X_paths, t_grid = simulate_montecarlo(
                mu=mu,
                sigma=cov_f.values,
                weights=weights,
                X_0=self.initial_capital,
                T=self.time_horizon,
                n_paths=self.n_paths
            )
            
            # 8. Анализ
            metrics = analyze_results(
                X_paths=X_paths,
                t_grid=t_grid,
                X_0=self.initial_capital,
                rf=self.rf_rate,
                asset_names=assets_f
            )
            
            return {
                'metrics': metrics,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"❌ Ошибка в пайплайне: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e)
            }