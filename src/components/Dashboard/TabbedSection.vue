<template>
  <div class="tabbed-container">
    <!-- Tab Navigation -->
    <div class="tabs-nav">
      <button
        @click="activeTab = 'greeks'"
        :class="['tab-btn', { active: activeTab === 'greeks' }]"
      >
        <span class="tab-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12h18M3 6h18M3 18h18" />
          </svg>
        </span>
        <span class="tab-label">Греческие параметры</span>
      </button>

      <button
        @click="activeTab = 'stress'"
        :class="['tab-btn', { active: activeTab === 'stress' }]"
      >
        <span class="tab-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2v20M2 12h20" />
            <circle cx="12" cy="12" r="10" />
          </svg>
        </span>
        <span class="tab-label">Стресс-тестирование</span>
      </button>

      <button
        @click="activeTab = 'backtest'"
        :class="['tab-btn', { active: activeTab === 'backtest' }]"
      >
        <span class="tab-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8 10 1 17" />
            <polyline points="17 6 23 6 23 12" />
          </svg>
        </span>
        <span class="tab-label">Результаты бэктестинга</span>
      </button>
    </div>

    <!-- Tab Indicator Line -->
    <div class="tabs-indicator" :style="{ transform: `translateX(${getIndicatorPosition()}%)` }"></div>

    <!-- Tab Content -->
    <div class="tabs-content">
      <!-- Greeks Tab -->
      <transition name="fade" mode="out-in">
        <div v-if="activeTab === 'greeks'" key="greeks" class="tab-pane greeks-tab">
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="col-position">Открытая позиция</th>
                  <th class="col-numeric">Дельта (Δ)</th>
                  <th class="col-numeric">Гамма (Γ)</th>
                  <th class="col-numeric">Вега (ν)</th>
                  <th class="col-numeric">Тета (θ)</th>
                  <th class="col-numeric">Ро (ρ)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="g in store.greeks" :key="g.position" class="data-row">
                  <td class="col-position">
                    <span class="position-name">{{ g.position }}</span>
                  </td>
                  <td class="col-numeric">
                    <span class="value-mono">{{ g.delta.toFixed(4) }}</span>
                  </td>
                  <td class="col-numeric">
                    <span class="value-mono">{{ g.gamma.toFixed(6) }}</span>
                  </td>
                  <td class="col-numeric">
                    <span class="value-mono">{{ g.vega.toFixed(2) }}</span>
                  </td>
                  <td class="col-numeric" :class="getThColor(g.theta)">
                    <span class="value-mono">{{ g.theta.toFixed(2) }}</span>
                  </td>
                  <td class="col-numeric">
                    <span class="value-mono">{{ g.rho.toFixed(2) }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Greeks Summary -->
          <div class="tab-footer">
            <div class="summary-grid">
              <div class="summary-item">
                <span class="summary-label">Портфельная Дельта</span>
                <span class="summary-value">{{ getTotalDelta().toFixed(4) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Портфельная Вега</span>
                <span class="summary-value">{{ getTotalVega().toFixed(2) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Портфельная Тета</span>
                <span class="summary-value" :class="getTotalTheta() < 0 ? 'negative' : 'positive'">
                  {{ getTotalTheta().toFixed(2) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <!-- Stress Testing Tab -->
      <transition name="fade" mode="out-in">
        <div v-if="activeTab === 'stress'" key="stress" class="tab-pane stress-tab">
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="col-scenario">Сценарий</th>
                  <th class="col-description">Описание</th>
                  <th class="col-numeric">Влияние на P&L</th>
                  <th class="col-numeric">Изменение VaR</th>
                  <th class="col-numeric">Вероятность</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="s in store.stressScenarios"
                  :key="s.scenario"
                  class="data-row"
                  :class="{ 'severity-high': Math.abs(s.pnlImpact) > 50000 }"
                >
                  <td class="col-scenario">
                    <div class="scenario-badge">{{ s.scenario }}</div>
                  </td>
                  <td class="col-description">
                    <span class="description-text">{{ s.description }}</span>
                  </td>
                  <td class="col-numeric" :class="getImpactClass(s.pnlImpact)">
                    <span class="value-mono">
                      {{ formatCurrency(s.pnlImpact) }}
                    </span>
                  </td>
                  <td class="col-numeric">
                    <span class="value-mono">{{ formatNumber(s.varChange) }}</span>
                  </td>
                  <td class="col-numeric">
                    <div class="probability-bar">
                      <div class="probability-fill" :style="{ width: (s.probability * 100) + '%' }"></div>
                      <span class="probability-text">{{ (s.probability * 100).toFixed(1) }}%</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Stress Summary -->
          <div class="tab-footer">
            <div class="alert alert-warning">
              <span class="alert-icon">⚠️</span>
              <span class="alert-text">
                В 95% случаев максимальное влияние стресс-сценариев не превышает
                <strong>{{ getMaxStressImpact() }}</strong>
              </span>
            </div>
          </div>
        </div>
      </transition>

      <!-- Backtesting Tab -->
      <transition name="fade" mode="out-in">
        <div v-if="activeTab === 'backtest'" key="backtest" class="tab-pane backtest-tab">
          <!-- Key Metrics Grid -->
          <div class="metrics-grid">
            <div class="metric-card positive">
              <div class="metric-header">
                <span class="metric-icon">📈</span>
                <span class="metric-label">Годовая доходность</span>
              </div>
              <div class="metric-body">
                <span class="metric-value">12.5%</span>
                <span class="metric-change">+2.3% YoY</span>
              </div>
            </div>

            <div class="metric-card negative">
              <div class="metric-header">
                <span class="metric-icon">📉</span>
                <span class="metric-label">Максимальная просадка</span>
              </div>
              <div class="metric-body">
                <span class="metric-value">-18.3%</span>
                <span class="metric-change">During 2024-Q3</span>
              </div>
            </div>

            <div class="metric-card neutral">
              <div class="metric-header">
                <span class="metric-icon">⚖️</span>
                <span class="metric-label">Коэффициент Шарпа</span>
              </div>
              <div class="metric-body">
                <span class="metric-value">1.45</span>
                <span class="metric-change">Risk-adjusted return</span>
              </div>
            </div>

            <div class="metric-card positive">
              <div class="metric-header">
                <span class="metric-icon">✓</span>
                <span class="metric-label">Доля прибыльных сделок</span>
              </div>
              <div class="metric-body">
                <span class="metric-value">58.3%</span>
                <span class="metric-change">{{ store.greeks.length }} позиций</span>
              </div>
            </div>
          </div>

          <!-- Detailed Stats -->
          <div class="backtest-details">
            <div class="details-section">
              <h4 class="section-title">Статистика периода</h4>
              <div class="stats-grid">
                <div class="stat-row">
                  <span class="stat-label">Период тестирования</span>
                  <span class="stat-value">2023-01-01 — 2025-12-31</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">Количество дней</span>
                  <span class="stat-value">1095</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">Волатильность (std)</span>
                  <span class="stat-value">14.2%</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">Risk-Free Rate</span>
                  <span class="stat-value">4.5%</span>
                </div>
              </div>
            </div>

            <div class="details-section">
              <h4 class="section-title">Метрики риска</h4>
              <div class="stats-grid">
                <div class="stat-row">
                  <span class="stat-label">VaR (95%)</span>
                  <span class="stat-value danger">-2.8%</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">CVaR (95%)</span>
                  <span class="stat-value danger">-4.1%</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">Sortino Ratio</span>
                  <span class="stat-value success">2.15</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">Information Ratio</span>
                  <span class="stat-value">0.92</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'

const store = usePortfolioStore()
const activeTab = ref<'greeks' | 'stress' | 'backtest'>('greeks')

// Computed properties
const getTotalDelta = () => {
  return store.greeks.reduce((sum, g) => sum + g.delta, 0)
}

const getTotalVega = () => {
  return store.greeks.reduce((sum, g) => sum + g.vega, 0)
}

const getTotalTheta = () => {
  return store.greeks.reduce((sum, g) => sum + g.theta, 0)
}

const getMaxStressImpact = () => {
  if (!store.stressScenarios.length) return '—'
  const max = Math.max(...store.stressScenarios.map(s => Math.abs(s.pnlImpact)))
  return formatCurrency(max)
}

// Methods
const getThColor = (theta: number) => {
  return theta < 0 ? 'text-danger' : 'text-success'
}

const getImpactClass = (impact: number) => {
  return impact < 0 ? 'text-danger' : 'text-success'
}

const getIndicatorPosition = () => {
  const tabs = { greeks: 0, stress: 33.33, backtest: 66.66 }
  return tabs[activeTab.value]
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0
  }).format(value)
}

const formatNumber = (value: number) => {
  return new Intl.NumberFormat('ru-RU', {
    maximumFractionDigits: 2
  }).format(value)
}
</script>

<style scoped lang="css">
:root {
  --color-bg-primary: #0f0f1e;
  --color-bg-secondary: #1a1a2e;
  --color-bg-tertiary: #16213e;
  --color-bg-glass: rgba(26, 26, 46, 0.4);
  --color-accent-primary: #00d9ff;
  --color-accent-secondary: #ff006e;
  --color-accent-success: #00ff88;
  --color-accent-warning: #ffa500;
  --color-accent-danger: #ff3366;
  --color-text-primary: #e0e0e0;
  --color-text-secondary: #a0a0a0;
  --color-text-tertiary: #707080;
  --color-border: rgba(255, 255, 255, 0.08);
  --color-border-hover: rgba(255, 255, 255, 0.16);
  --spacing-xs: 0.5rem;
  --spacing-sm: 1rem;
  --spacing-md: 1.5rem;
  --spacing-lg: 2rem;
  --duration-normal: 300ms;
  --shadow-md: 0 8px 32px rgba(0, 0, 0, 0.2);
}

[data-theme="light"] {
  --color-bg-secondary: #f8f9fa;
  --color-bg-tertiary: #f0f1f5;
  --color-text-primary: #1a1a2e;
  --color-text-secondary: #6b7280;
  --color-text-tertiary: #9ca3af;
}

.tabbed-container {
  background: var(--color-bg-glass);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Tab Navigation */
.tabs-nav {
  display: flex;
  position: relative;
  border-bottom: 1px solid var(--color-border);
  background: rgba(0, 0, 0, 0.1);
  padding: 0;
  gap: 0;
}

.tab-btn {
  flex: 1;
  padding: var(--spacing-md);
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  transition: all var(--duration-normal);
  position: relative;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tab-btn:hover {
  color: var(--color-text-primary);
  background: rgba(255, 255, 255, 0.02);
}

.tab-btn.active {
  color: var(--color-accent-primary);
}

.tab-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
}

.tab-icon svg {
  width: 100%;
  height: 100%;
}

.tab-label {
  display: none;
}

@media (min-width: 768px) {
  .tab-label {
    display: inline;
  }
}

/* Tab Indicator */
.tabs-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  width: 33.33%;
  background: linear-gradient(90deg, var(--color-accent-primary), #00d9ff);
  transition: transform var(--duration-normal) cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 12px rgba(0, 217, 255, 0.6);
}

/* Tab Content */
.tabs-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

.tab-pane {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

/* Table */
.table-wrapper {
  overflow-x: auto;
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.data-table thead {
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 2px solid var(--color-border);
  position: sticky;
  top: 0;
}

.data-table th {
  padding: var(--spacing-md);
  text-align: left;
  font-weight: 700;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.8rem;
}

.data-table th.col-numeric {
  text-align: right;
}

.data-row {
  border-bottom: 1px solid var(--color-border);
  transition: all var(--duration-normal);
}

.data-row:hover {
  background: rgba(0, 217, 255, 0.05);
}

.data-row.severity-high {
  background: rgba(255, 51, 102, 0.05);
}

.data-table td {
  padding: var(--spacing-md);
  color: var(--color-text-primary);
}

.col-position,
.col-scenario,
.col-description {
  text-align: left;
}

.col-numeric {
  text-align: right;
  font-family: 'Courier New', monospace;
}

.position-name {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(0, 217, 255, 0.1);
  border: 1px solid rgba(0, 217, 255, 0.2);
  border-radius: 0.5rem;
  font-weight: 600;
  color: var(--color-accent-primary);
}

.value-mono {
  font-family: 'Courier New', monospace;
  font-weight: 600;
}

.text-success {
  color: var(--color-accent-success);
}

.text-danger {
  color: var(--color-accent-danger);
}

.scenario-badge {
  display: inline-block;
  padding: 4px 12px;
  background: linear-gradient(135deg, rgba(0, 217, 255, 0.2), rgba(255, 0, 110, 0.2));
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.description-text {
  color: var(--color-text-secondary);
  font-size: 0.85rem;
}

/* Probability Bar */
.probability-bar {
  position: relative;
  display: inline-flex;
  align-items: center;
  width: 100%;
  height: 24px;
  background: var(--color-bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.probability-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: linear-gradient(90deg, var(--color-accent-primary), var(--color-accent-secondary));
  transition: width var(--duration-normal);
}

.probability-text {
  position: relative;
  z-index: 1;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0 8px;
  color: var(--color-text-primary);
}

/* Tab Footer */
.tab-footer {
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
}

.summary-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-accent-primary);
  font-family: 'Courier New', monospace;
}

.summary-value.positive {
  color: var(--color-accent-success);
}

.summary-value.negative {
  color: var(--color-accent-danger);
}

/* Alert */
.alert {
  padding: var(--spacing-md);
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  font-size: 0.9rem;
}

.alert-warning {
  background: rgba(255, 165, 0, 0.1);
  border: 1px solid rgba(255, 165, 0, 0.3);
  color: var(--color-text-primary);
}

.alert-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.alert-text {
  flex: 1;
}

/* Backtest Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--spacing-md);
}

.metric-card {
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  transition: all var(--duration-normal);
}

.metric-card:hover {
  border-color: var(--color-border-hover);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.metric-card.positive {
  border-left: 3px solid var(--color-accent-success);
}

.metric-card.negative {
  border-left: 3px solid var(--color-accent-danger);
}

.metric-card.neutral {
  border-left: 3px solid var(--color-accent-primary);
}

.metric-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.metric-icon {
  font-size: 1.5rem;
}

.metric-label {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-secondary);
}

.metric-body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.metric-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: 'Courier New', monospace;
}

.metric-change {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

/* Backtest Details */
.backtest-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

.details-section {
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
}

.section-title {
  margin: 0 0 var(--spacing-md) 0;
  font-size: 0.95rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-primary);
}

.stats-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-label {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.stat-value {
  font-weight: 700;
  color: var(--color-accent-primary);
  font-family: 'Courier New', monospace;
}

.stat-value.success {
  color: var(--color-accent-success);
}

.stat-value.danger {
  color: var(--color-accent-danger);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--duration-normal) ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Scrollbar */
.tabs-content::-webkit-scrollbar {
  width: 8px;
}

.tabs-content::-webkit-scrollbar-track {
  background: transparent;
}

.tabs-content::-webkit-scrollbar-thumb {
  background: var(--color-border-hover);
  border-radius: 4px;
}

.tabs-content::-webkit-scrollbar-thumb:hover {
  background: var(--color-border);
}

.table-wrapper::-webkit-scrollbar {
  height: 8px;
}

.table-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.table-wrapper::-webkit-scrollbar-thumb {
  background: var(--color-border-hover);
  border-radius: 4px;
}

/* Responsive */
@media (max-width: 1024px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .backtest-details {
    grid-template-columns: 1fr;
  }

  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .tabs-nav {
    padding: 0;
  }

  .tab-btn {
    padding: var(--spacing-sm);
    font-size: 0.8rem;
  }

  .tab-icon {
    width: 18px;
    height: 18px;
  }

  .tabs-content {
    padding: var(--spacing-md);
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .data-table {
    font-size: 0.8rem;
  }

  .data-table th,
  .data-table td {
    padding: var(--spacing-sm);
  }

  .table-wrapper {
    overflow-x: auto;
  }
}
</style>