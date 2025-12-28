#!/usr/bin/env python
# coding: utf-8

# ---
# # **Стресс-тестирование портфеля**
# 
# **Цель**: Проверить устойчивость портфеля к неблагоприятным сценариям.
# 
# ### Сценарий 1: Базовый
# 
# Исходные параметры:
# $$\boldsymbol{\mu}_{\text{baseline}} = \boldsymbol{\mu}, \quad \Sigma_{\text{baseline}} = \Sigma$$
# 
# ### Сценарий 2: Кризис
# 
# Снижение ожидаемых доходностей на 30%:
# $$\boldsymbol{\mu}_{\text{crisis}} = 0.7 \times \boldsymbol{\mu}, \quad \Sigma_{\text{crisis}} = \Sigma$$
# 
# (волатильность не меняется)
# 
# ### Сценарий 3: Высокая волатильность
# 
# Увеличение ковариации на 50%:
# $$\Sigma_{\text{high vol}} = 1.5 \times \Sigma, \quad \boldsymbol{\mu}_{\text{high vol}} = \boldsymbol{\mu}$$
# 
# (доходность не меняется)
# 
# ### Сценарий 4: Шок корреляций
# 
# Все активы начинают коррелировать сильнее:
# 
# Исходная корреляционная матрица:
# $$C = D^{-1/2} \Sigma D^{-1/2}$$
# 
# $$C_{\text{shock}} = I + 1.5(C - I) = 1.5C - 0.5I$$
# 
# (с ограничением $|C_{\text{shock}}[i,j]| \leq 0.999$)
# 
# Обратная трансформация:
# $$\Sigma_{\text{shock}} = D^{1/2} C_{\text{shock}} D^{1/2}$$
# 
# ### Матрица Холецкого для коррелированных шоков
# 
# $$\Sigma = LL^T$$
# 
# Если $z \sim N(0,I)$, то $\epsilon = Lz$ имеет нужную корреляцию.
# 
# ### Сравнение сценариев
# 
# После симуляции каждого сценария сравниваются:
# - Средний финальный капитал
# - VaR и CVaR
# - Sharpe Ratio
# - Maximum Drawdown
# - Вероятность потерь
# 
# Определяется:
# - Какой сценарий наиболее опасен
# - На сколько процентов портфель теряет стоимость
# - Какие активы страдают больше всего
# - Нужны ли корректировки в стратегии
# 
# ---

# In[ ]:


class StressTestSimulator:

    def __init__(
        self,
        mu,
        cov_matrix,
        X_0,
        strategy,
        asset_names=None,
        rf=results['rf']
    ):

        if rf is None:
            raise ValueError(
            )

        self.mu_base = np.asarray(mu).flatten()
        self.cov_matrix_base = np.asarray(cov_matrix)
        self.X_0 = X_0
        self.strategy = strategy
        self.asset_names = asset_names if asset_names is not None else \
            [f"Asset_{i}" for i in range(len(mu))]
        self.n_assets = len(self.mu_base)
        self.rf = rf

        try:
            eigenvalues = np.linalg.eigvalsh(cov_matrix)
            min_eig = eigenvalues.min()
            max_eig = eigenvalues.max()

            if min_eig > 1e-10:
                self.sigma_base = np.linalg.cholesky(cov_matrix)
                self.cov_matrix_used = cov_matrix
                print(f"Cholesky-разложение успешно")
                print(f"   λ_min = {min_eig:.2e}, λ_max = {max_eig:.2e}")
            else:
                print(f"Матрица близка к вырождению (λ_min = {min_eig:.2e})")
                epsilon = max(1e-6, abs(min_eig) * 10)
                cov_matrix_reg = cov_matrix + epsilon * np.eye(self.n_assets)
                self.sigma_base = np.linalg.cholesky(cov_matrix_reg)
                self.cov_matrix_used = cov_matrix_reg
                print(f"   Применена регуляризация (ε = {epsilon:.2e})")
        except np.linalg.LinAlgError as e:
            raise ValueError(f"Не удалось разложить матрицу: {e}")

        self.results_history = {}

        print(f"   Активов: {self.n_assets}")
        print(f"   Начальный капитал: {self.X_0:,.0f} руб.")
        print(f"   Безрисковая ставка rf: {self.rf:.2%}")

    def simulate_scenario(
            self,
            scenario_name: str,
            mu: np.array,
            sigma: np.array,
            n_paths: int = 1000,
            t_grid: Optional[np.array] = None,
            seed: Optional[int] = None
    ) -> Dict:

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


        if t_grid is None:
            t_grid = np.linspace(0, 1, 252)

        if seed is not None:
            np.random.seed(seed)

        dt = t_grid[1] - t_grid[0]
        num_steps = len(t_grid)
        T_years = t_grid[-1] - t_grid[0]

        X_paths = np.zeros((n_paths, num_steps))
        X_paths[:, 0] = self.X_0
        weights_history = np.zeros((n_paths, num_steps, self.n_assets))

        dW = np.random.normal(0, 1, (n_paths, self.n_assets, num_steps - 1))
        sigma_scaled = sigma * np.sqrt(dt)

        start_time = time.time()

        for step in range(num_steps - 1):
            t = t_grid[step]

            if (step + 1) % max(1, num_steps // 10) == 0:
                elapsed = time.time() - start_time
                progress = (step + 1) / num_steps * 100
                print(f"   Прогресс: {progress:.0f}% ({step + 1}/{num_steps}), {elapsed:.1f}s")

            for path in range(n_paths):
                X_t = X_paths[path, step]

                if X_t < 1e-6:
                    X_paths[path, step + 1:] = 1e-6
                    weights_history[path, step:, :] = 0
                    break

                try:
                    pi_t = self.strategy.update(t, {'capital': X_t})
                except Exception as e:
                    print(f" Ошибка в path={path}, step={step}, t={t:.4f}")
                    print(f"   Тип ошибки: {type(e).__name__}")
                    print(f"   Сообщение: {e}")
                    print(f"   Текущий капитал: X_t = {X_t:.2f}")
                    print(f"   Продолжаем с предыдущими весами...")

                    if step > 0:
                        prev_weights = weights_history[path, step - 1, :]
                        pi_t = prev_weights * X_t
                    else:
                        pi_t = np.ones(self.n_assets) * (X_t / self.n_assets)

                weights = pi_t / X_t if X_t > 1e-6 else np.zeros(self.n_assets)
                weights_history[path, step, :] = weights

                drift = np.dot(pi_t, mu) * dt

                diffusion = np.dot(pi_t, np.dot(sigma_scaled, dW[path, :, step]))

                X_paths[path, step + 1] = max(X_t + drift + diffusion, 1e-6)

        for path in range(n_paths):
            X_final = X_paths[path, -1]
            if X_final > 1e-6:
                try:
                    pi_final = self.strategy.update(t_grid[-1], {'capital': X_final})
                    weights_history[path, -1, :] = pi_final / X_final
                except Exception as e:
                    weights_history[path, -1, :] = weights_history[path, -2, :]
            else:
                weights_history[path, -1, :] = 0

        metrics = self._calculate_metrics(X_paths, weights_history, t_grid, T_years, scenario_name)

        results = {
            'scenario_name': scenario_name,
            'X_paths': X_paths,
            'weights_history': weights_history,
            't_grid': t_grid,
            'T_years': T_years,
            'metrics': metrics
        }

        self.results_history[scenario_name] = results
        return results

    def _calculate_metrics(self, X_paths, weights_history, t_grid, T_years, scenario_name):

        final_capitals = X_paths[:, -1]
        n_paths = X_paths.shape[0]

        mean_final = np.mean(final_capitals)
        median_final = np.median(final_capitals)
        std_final = np.std(final_capitals, ddof=1)

        simple_returns = (final_capitals / self.X_0) - 1

        annualized_returns = (final_capitals / self.X_0) ** (1 / T_years) - 1

        annualized_volatility = np.std(annualized_returns, ddof=1)

        mean_return = np.mean(annualized_returns)
        median_return = np.median(annualized_returns)
        std_return = annualized_volatility

        sharpe = (mean_return - self.rf) / std_return if std_return > 1e-10 else 0

        if n_paths < 5000:
            print(f"     Рекомендуется n_paths ≥ 5000 для надежных VaR/CVaR (текущее: {n_paths})")

        var_95 = np.percentile(final_capitals, 5)
        cvar_indices_95 = final_capitals <= var_95
        cvar_95 = np.mean(final_capitals[cvar_indices_95]) if np.sum(cvar_indices_95) > 0 else var_95

        var_99 = np.percentile(final_capitals, 1)
        cvar_indices_99 = final_capitals <= var_99
        cvar_99 = np.mean(final_capitals[cvar_indices_99]) if np.sum(cvar_indices_99) > 0 else var_99

        def compute_max_drawdown(path):
            running_max = np.maximum.accumulate(path)
            with np.errstate(divide='ignore', invalid='ignore'):
                drawdown = np.where(running_max > 1e-10, (running_max - path) / running_max, 0)
            return np.max(drawdown)

        max_drawdowns = np.array([compute_max_drawdown(path) for path in X_paths])
        mean_max_dd = np.mean(max_drawdowns)
        worst_dd = np.max(max_drawdowns)

        prob_loss = np.mean(final_capitals < self.X_0)
        prob_loss_50 = np.mean(final_capitals < 0.5 * self.X_0)

        mean_weights = np.mean(weights_history[:, -1, :], axis=0)

        return {
            'mean_final': mean_final,
            'median_final': median_final,
            'std_final': std_final,
            'mean_return': mean_return,
            'median_return': median_return,
            'std_return': std_return,=
            'sharpe': sharpe,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'var_99': var_99,
            'cvar_99': cvar_99,
            'mean_max_dd': mean_max_dd,
            'worst_dd': worst_dd,
            'prob_loss': prob_loss,
            'prob_loss_50': prob_loss_50,
            'mean_weights': mean_weights,
            'rf': self.rf
        }

# In[ ]:


def add_comparison_methods_to_simulator():

    def compare_scenarios(self, results: Dict, max_table_width: int = 150):

        if not results:
            raise ValueError(" Словарь results пуст. Запустите simulate_scenario() сначала.")

        scenarios = list(results.keys())
        n_scenarios = len(scenarios)

        estimated_width = 30 + n_scenarios * 16

        if estimated_width > max_table_width:
            print(f"  ВНИМАНИЕ: Таблица очень широкая ({estimated_width} символов)")
            print(f"   Рекомендуется ≤ 8 сценариев для читаемости (текущее: {n_scenarios})\n")

        metrics_keys = [
            ('Средний финальный капитал', 'mean_final', '.0f'),
            ('Медианный финальный капитал', 'median_final', '.0f'),
            ('Средняя доходность', 'mean_return', '.2%'),
            ('Волатильность', 'std_return', '.2%'),
            ('Sharpe Ratio', 'sharpe', '.4f'),
            ('VaR 95%', 'var_95', '.0f'),
            ('CVaR 95%', 'cvar_95', '.0f'),
            ('VaR 99%', 'var_99', '.0f'),
            ('CVaR 99%', 'cvar_99', '.0f'),
            ('Средний Max DD', 'mean_max_dd', '.2%'),
            ('Худший DD', 'worst_dd', '.2%'),
            ('Вероятность потери', 'prob_loss', '.2%'),
            ('Вероятность потери >50%', 'prob_loss_50', '.2%')
        ]

        metric_width = 30
        scenario_width = 16
        total_width = metric_width + (scenario_width * n_scenarios) + n_scenarios

        header = f"{'Метрика':<{metric_width}}"
        for scenario in scenarios:
            scenario_name = results[scenario]['scenario_name'][:15]
            header += f" {scenario_name:>{scenario_width}}"

        for metric_name, metric_key, fmt in metrics_keys:
            row = f"{metric_name:<{metric_width}}"

            for scenario in scenarios:
                if metric_key not in results[scenario]['metrics']:
                    row += f" {'N/A':>{scenario_width}}"
                    continue

                value = results[scenario]['metrics'][metric_key]

                if fmt == '.0f':
                    if abs(value) > 1e9:
                        formatted = f"{value/1e9:.2f}B"
                    elif abs(value) > 1e6:
                        formatted = f"{value/1e6:.2f}M"
                    else:
                        formatted = f"{value:,.0f}"
                elif fmt == '.2%':
                    formatted = f"{value:.2%}"
                elif fmt == '.4f':
                    formatted = f"{value:.4f}"
                else:
                    formatted = str(value)

                row += f" {formatted:>{scenario_width}}"

            print(row)


    def visualize_comparison(self, results: Dict, save_path: Optional[str] = None):

        if not results:
            raise ValueError(" Словарь results пуст. Запустите simulate_scenario() сначала.")

        scenarios = list(results.keys())
        n_scenarios = len(scenarios)

        T_values = [results[s]['T_years'] for s in scenarios]
        if len(set(np.round(T_values, 4))) > 1:
            print(f"  ВНИМАНИЕ: Сценарии имеют разные временные горизонты:")
            for s, T in zip(scenarios, T_values):
                print(f"   {results[s]['scenario_name']}: {T:.4f} лет")
            print(f"   Графики могут быть неправильно сравнены\n")

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        ax = axes[0, 0]

        colors = plt.cm.tab10(np.linspace(0, 1, n_scenarios))

        for idx, scenario in enumerate(scenarios):
            final_caps = results[scenario]['X_paths'][:, -1]

            ax.hist(final_caps, bins=50, alpha=0.3, label=f"Гист. {results[scenario]['scenario_name']}",
                   color=colors[idx], edgecolor='none')

            try:
                kde = stats.gaussian_kde(final_caps)
                x_range = np.linspace(final_caps.min(), final_caps.max(), 200)
                ax.plot(x_range, kde(x_range), linewidth=2.5, label=f"KDE {results[scenario]['scenario_name']}",
                       color=colors[idx])
            except np.linalg.LinAlgError:
                pass

        ax.axvline(self.X_0, color='black', linestyle='--', linewidth=2.5, label='Начальный капитал', zorder=5)
        ax.set_xlabel('Финальный капитал (₽)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Плотность', fontsize=12, fontweight='bold')
        ax.set_title('Распределение финальных капиталов по сценариям', fontsize=14, fontweight='bold')
        ax.legend(fontsize=9, loc='best')
        ax.grid(alpha=0.3, linestyle='--')

        ax = axes[0, 1]
        var_95 = [results[s]['metrics']['var_95'] for s in scenarios]
        cvar_95 = [results[s]['metrics']['cvar_95'] for s in scenarios]
        var_99 = [results[s]['metrics']['var_99'] for s in scenarios]
        cvar_99 = [results[s]['metrics']['cvar_99'] for s in scenarios]

        x = np.arange(len(scenarios))
        width = 0.2

        ax.bar(x - 1.5*width, var_95, width, label='VaR 95%', alpha=0.8)
        ax.bar(x - 0.5*width, cvar_95, width, label='CVaR 95%', alpha=0.8)
        ax.bar(x + 0.5*width, var_99, width, label='VaR 99%', alpha=0.8)
        ax.bar(x + 1.5*width, cvar_99, width, label='CVaR 99%', alpha=0.8)

        ax.axhline(self.X_0, color='black', linestyle='--', linewidth=2, label='Начальный капитал', zorder=5)
        ax.set_ylabel('Капитал (₽)', fontsize=12, fontweight='bold')
        ax.set_title('VaR и CVaR по сценариям (95% и 99%)', fontsize=14, fontweight='bold')
        ax.set_xticks(x)

        if n_scenarios > 8:
            ax.set_xticklabels([results[s]['scenario_name'] for s in scenarios], rotation=90, ha='right', fontsize=9)
        else:
            ax.set_xticklabels([results[s]['scenario_name'] for s in scenarios], rotation=45, ha='right', fontsize=10)

        ax.legend(fontsize=10, loc='best')
        ax.grid(alpha=0.3, linestyle='--', axis='y')

        ax = axes[1, 0]

        for idx, scenario in enumerate(scenarios):
            X_paths = results[scenario]['X_paths']
            t_grid = results[scenario]['t_grid']
            mean_path = np.mean(X_paths, axis=0)
            q25_path = np.quantile(X_paths, 0.25, axis=0)
            q75_path = np.quantile(X_paths, 0.75, axis=0)

            ax.fill_between(t_grid, q25_path, q75_path, alpha=0.2, color=colors[idx])

            ax.plot(t_grid, mean_path, label=results[scenario]['scenario_name'],
                   linewidth=2.5, color=colors[idx], marker='o', markersize=3, alpha=0.8)

        ax.axhline(self.X_0, color='black', linestyle='--', linewidth=2, label='Начальный капитал', zorder=5)
        ax.set_xlabel('Время (годы)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Капитал (₽)', fontsize=12, fontweight='bold')
        ax.set_title('Средние траектории капитала с интервалом 25%-75%', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10, loc='best')
        ax.grid(alpha=0.3, linestyle='--')

        ax = axes[1, 1]
        sharpe = [results[s]['metrics']['sharpe'] for s in scenarios]
        mean_ret = [results[s]['metrics']['mean_return'] * 100 for s in scenarios]

        x = np.arange(len(scenarios))
        width = 0.35

        ax2 = ax.twinx()

        bars1 = ax.bar(x - width/2, sharpe, width, label='Sharpe Ratio', alpha=0.8, color='steelblue')
        bars2 = ax2.bar(x + width/2, mean_ret, width, label='Средняя доходность (%)', alpha=0.8, color='seagreen')

        ax.set_ylabel('Sharpe Ratio', color='steelblue', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Средняя доходность (%)', color='seagreen', fontsize=12, fontweight='bold')
        ax.tick_params(axis='y', labelcolor='steelblue')
        ax2.tick_params(axis='y', labelcolor='seagreen')

        ax.set_title('Sharpe Ratio и среднегодовая доходность', fontsize=14, fontweight='bold')
        ax.set_xticks(x)

        if n_scenarios > 8:
            ax.set_xticklabels([results[s]['scenario_name'] for s in scenarios], rotation=90, ha='right', fontsize=9)
        else:
            ax.set_xticklabels([results[s]['scenario_name'] for s in scenarios], rotation=45, ha='right', fontsize=10)

        ax.legend(handles=[bars1, bars2], loc='upper left', fontsize=10)
        ax.grid(alpha=0.3, linestyle='--', axis='y')


        plt.tight_layout()

        if save_path:
            import os
            os.makedirs(save_path, exist_ok=True)
            filepath = os.path.join(save_path, 'stress_test_comparison.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f" График сохранен: {filepath}")

        plt.show()

    StressTestSimulator.compare_scenarios = compare_scenarios
    StressTestSimulator.visualize_comparison = visualize_comparison

add_comparison_methods_to_simulator()

# In[ ]:


stress_simulator = StressTestSimulator(
    mu=mu_with_dividends,
    cov_matrix=filtered_cov,
    X_0=10_593_820_754_282,
    strategy=strategy,
    asset_names=filtered_names,
    rf=results['rf']
)

# In[ ]:


n_paths = 5000
t_grid = np.linspace(0, 1, 252)
seed = 42

print(f"\n  Параметры симуляции:")
print(f"   Начальный капитал: {stress_simulator.X_0:,.0f} ₽")
print(f"   Количество симуляций: {n_paths:,}")
print(f"   Горизонт: 1 год (252 дня)")
print(f"   Seed: {seed}\n")

basic_stress_results = {}

start_time = time.time()

basic_stress_results['baseline'] = stress_simulator.simulate_scenario(
    scenario_name='Базовый',
    mu=stress_simulator.mu_base,
    sigma=stress_simulator.sigma_base,
    n_paths=n_paths,
    t_grid=t_grid,
    seed=seed
)

start_time = time.time()

mu_crisis = stress_simulator.mu_base * 0.7

basic_stress_results['crisis'] = stress_simulator.simulate_scenario(
    scenario_name='Кризис',
    mu=mu_crisis,
    sigma=stress_simulator.sigma_base,
    n_paths=n_paths,
    t_grid=t_grid,
    seed=seed
)

start_time = time.time()

cov_high_vol = stress_simulator.cov_matrix_base * 1.5
sigma_high_vol = np.linalg.cholesky(cov_high_vol)

basic_stress_results['high_volatility'] = stress_simulator.simulate_scenario(
    scenario_name='Высокая волатильность',
    mu=stress_simulator.mu_base,
    sigma=sigma_high_vol,
    n_paths=n_paths,
    t_grid=t_grid,
    seed=seed
)

start_time = time.time()

try:
    diag_elements = np.diag(stress_simulator.cov_matrix_base)

    if np.any(diag_elements <= 1e-10):
        sigma_corr_shock = stress_simulator.sigma_base
    else:
        D = np.diag(np.sqrt(diag_elements))
        D_inv = np.linalg.inv(D)

        corr_matrix = D_inv @ stress_simulator.cov_matrix_base @ D_inv
        corr_matrix_shocked = np.eye(stress_simulator.n_assets) + 1.5 * (corr_matrix - np.eye(stress_simulator.n_assets))

        for i in range(stress_simulator.n_assets):
            for j in range(stress_simulator.n_assets):
                if i != j:
                    corr_matrix_shocked[i, j] = np.clip(corr_matrix_shocked[i, j], -0.999, 0.999)

        np.fill_diagonal(corr_matrix_shocked, 1.0)

        cov_corr_shock = D @ corr_matrix_shocked @ D
        cov_corr_shock = (cov_corr_shock + cov_corr_shock.T) / 2
        cov_corr_shock += 1e-6 * np.eye(stress_simulator.n_assets)

        try:
            sigma_corr_shock = np.linalg.cholesky(cov_corr_shock)
        except np.linalg.LinAlgError:
            eigenvalues = np.linalg.eigvalsh(cov_corr_shock)
            min_eig = eigenvalues.min()

            if min_eig <= 0:
                epsilon = abs(min_eig) + 1e-3
                cov_corr_shock += epsilon * np.eye(stress_simulator.n_assets)

                try:
                    sigma_corr_shock = np.linalg.cholesky(cov_corr_shock)
                except np.linalg.LinAlgError:
                    sigma_corr_shock = stress_simulator.sigma_base
            else:
                sigma_corr_shock = stress_simulator.sigma_base

        except Exception:
            sigma_corr_shock = stress_simulator.sigma_base

except Exception:
    sigma_corr_shock = stress_simulator.sigma_base

basic_stress_results['correlation_shock'] = stress_simulator.simulate_scenario(
    scenario_name='Корреляционный шок',
    mu=stress_simulator.mu_base,
    sigma=sigma_corr_shock,
    n_paths=n_paths,
    t_grid=t_grid,
    seed=seed
)

start_time = time.time()

gamma = stress_simulator.strategy.gamma
rf = stress_simulator.rf

inv_cov = np.linalg.inv(stress_simulator.cov_matrix_base)
raw_weights = (1 / gamma) * np.dot(inv_cov, stress_simulator.mu_base - rf)
clipped_weights = np.maximum(raw_weights, 0)

total_weight = clipped_weights.sum()
if total_weight > 1e-10:
    normalized_weights = clipped_weights / total_weight
else:
    normalized_weights = clipped_weights

active_indices = np.where(normalized_weights > 1e-6)[0]

if len(active_indices) == 0:
    print(f"    ОШИБКА: Нет активов с положительным весом!")
    raise ValueError("Портфель пуст!")

active_mus = stress_simulator.mu_base[active_indices]
worst_active_idx = active_indices[np.argmin(active_mus)]
worst_asset_name = stress_simulator.asset_names[worst_active_idx]
worst_asset_mu = stress_simulator.mu_base[worst_active_idx]
worst_asset_weight = clipped_weights[worst_active_idx]

print(f"   Актив для шока: {worst_asset_name}")
print(f"   Исходная μ: {worst_asset_mu*100:.2f}%")
print(f"   Вес в портфеле: {worst_asset_weight*100:.2f}%")

mu_individual = stress_simulator.mu_base.copy()
mu_individual[worst_active_idx] *= 0.5
new_mu = mu_individual[worst_active_idx]

print(f"   После шока μ: {new_mu*100:.2f}%")
print(f"   Изменение: {(new_mu - worst_asset_mu)*100:.2f}%\n")

basic_stress_results['individual_shock'] = stress_simulator.simulate_scenario(
    scenario_name='Индивидуальный шок',
    mu=mu_individual,
    sigma=stress_simulator.sigma_base,
    n_paths=n_paths,
    t_grid=t_grid,
    seed=46
)

# In[ ]:


try:
    _ = n_paths
    _ = t_grid
except NameError as e:
    raise NameError(
        f"❌ {e}\n\n"
        f"Блок СТРЕСС-5 требует выполнения Блока СТРЕСС-4 сначала.\n"
        f"Убедитесь, что переменные n_paths и t_grid определены."
    )

extended_stress_results = {}

start_time = time.time()

mu_black_swan = stress_simulator.mu_base * 0.5

extended_stress_results['black_swan'] = stress_simulator.simulate_scenario(
    scenario_name='Чёрный лебедь',
    mu=mu_black_swan,
    sigma=stress_simulator.sigma_base,
    n_paths=n_paths,
    t_grid=t_grid,
    seed=43
)

start_time = time.time()

mu_bull = stress_simulator.mu_base * 1.5

extended_stress_results['bull_market'] = stress_simulator.simulate_scenario(
    scenario_name='Бычий рынок',
    mu=mu_bull,
    sigma=stress_simulator.sigma_base,
    n_paths=n_paths,
    t_grid=t_grid,
    seed=44
)

start_time = time.time()

cov_low_vol = stress_simulator.cov_matrix_base * 0.5

try:
    sigma_low_vol = np.linalg.cholesky(cov_low_vol)
except np.linalg.LinAlgError:
    cov_low_vol += 1e-6 * np.eye(stress_simulator.n_assets)
    try:
        sigma_low_vol = np.linalg.cholesky(cov_low_vol)
    except np.linalg.LinAlgError:
        sigma_low_vol = stress_simulator.sigma_base * np.sqrt(0.5)

extended_stress_results['low_volatility'] = stress_simulator.simulate_scenario(
    scenario_name='Крах волатильности',
    mu=stress_simulator.mu_base,
    sigma=sigma_low_vol,
    n_paths=n_paths,
    t_grid=t_grid,
    seed=45
)

# In[ ]:


horizon_results = {}

horizons = {
    '1_month': (np.linspace(0, 1/12, 21), '1 месяц'),
    '3_months': (np.linspace(0, 1/4, 63), '3 месяца'),
    '1_year': (np.linspace(0, 1, 252), '1 год'),
    '3_years': (np.linspace(0, 3, 756), '3 года')
}

for i, (horizon_key, (t_grid_h, horizon_name)) in enumerate(horizons.items(), 1):
    print(f"⏱️  {i}/4: Горизонт {horizon_name}...")
    start_time = time.time()

    horizon_results[horizon_key] = stress_simulator.simulate_scenario(
        scenario_name=f'Горизонт: {horizon_name}',
        mu=stress_simulator.mu_base,
        sigma=stress_simulator.sigma_base,
        n_paths=n_paths,
        t_grid=t_grid_h,
        seed=seed
    )

# In[ ]:


print(" АНАЛИЗ БАЗОВЫХ СТРЕСС-СЦЕНАРИЕВ:\n")
stress_simulator.compare_scenarios(basic_stress_results)
stress_simulator.visualize_comparison(basic_stress_results)

print("\n АНАЛИЗ РАСШИРЕННЫХ СТРЕСС-СЦЕНАРИЕВ:\n")
stress_simulator.compare_scenarios(extended_stress_results)
stress_simulator.visualize_comparison(extended_stress_results)

print("\n АНАЛИЗ ВРЕМЕННЫХ ГОРИЗОНТОВ:\n")
stress_simulator.compare_scenarios(horizon_results)
stress_simulator.visualize_comparison(horizon_results)

all_stress_results = {
    **basic_stress_results,
    **extended_stress_results,
    **horizon_results
}

print(f"Всего проведено стресс-тестов: {len(all_stress_results)}")
print(f"Результаты доступны в переменной 'all_stress_results'")
