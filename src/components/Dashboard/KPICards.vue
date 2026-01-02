<template>
  <div class="kpi-grid">
    <!-- KPI Card: Total PnL -->
    <div class="kpi-card" :class="{ positive: store.kpis.totalPnL >= 0 }">
      <div class="card-header">
        <h3 class="card-label">Итоговый P&L</h3>
        <div class="card-icon pnl-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8 10 1 17" />
            <polyline points="17 6 23 6 23 12" />
          </svg>
        </div>
      </div>
      <div class="card-value">
        <p class="value-primary" :class="store.kpis.totalPnL >= 0 ? 'positive' : 'negative'">
          {{ formatNumber(store.kpis.totalPnL) }}
        </p>
      </div>
      <div class="card-meta">
        <span class="meta-label">RUB</span>
        <span class="meta-change" :class="store.kpis.totalPnL >= 0 ? 'positive' : 'negative'">
          {{ store.kpis.totalPnL >= 0 ? '↗' : '↘' }}
        </span>
      </div>
      <div class="card-progress">
        <div class="progress-bar" :style="{ width: getProgressWidth(store.kpis.totalPnL) }"></div>
      </div>
    </div>

    <!-- KPI Card: VaR 95 -->
    <div class="kpi-card warning">
      <div class="card-header">
        <h3 class="card-label">VaR (95%)</h3>
        <div class="card-icon var-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 6v6l4 2" />
          </svg>
        </div>
      </div>
      <div class="card-value">
        <p class="value-primary danger">{{ formatNumber(Math.abs(store.kpis.var95)) }}</p>
      </div>
      <div class="card-meta">
        <span class="meta-label">Уровень доверия 95%</span>
        <span class="meta-indicator">⚠️</span>
      </div>
      <div class="card-progress">
        <div class="progress-bar danger" style="width: 95%"></div>
      </div>
    </div>

    <!-- KPI Card: CVaR -->
    <div class="kpi-card critical">
      <div class="card-header">
        <h3 class="card-label">CVaR (Expected Shortfall)</h3>
        <div class="card-icon cvar-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2v20M2 12h20" />
            <circle cx="12" cy="12" r="10" />
          </svg>
        </div>
      </div>
      <div class="card-value">
        <p class="value-primary danger">{{ formatNumber(Math.abs(store.kpis.expectedShortfall)) }}</p>
      </div>
      <div class="card-meta">
        <span class="meta-label">Хвостовой риск</span>
        <span class="meta-indicator">🔴</span>
      </div>
      <div class="card-progress">
        <div class="progress-bar danger" style="width: 100%"></div>
      </div>
    </div>

    <!-- KPI Card: Sharpe Ratio -->
    <div class="kpi-card" :class="{ positive: store.kpis.sharpeRatio > 1 }">
      <div class="card-header">
        <h3 class="card-label">Коэффициент Шарпа</h3>
        <div class="card-icon sharpe-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12h2m16 0h2M12 3v2m0 16v2M5.64 5.64l1.41 1.41m9.9 9.9l1.41 1.41M5.64 18.36l1.41-1.41m9.9-9.9l1.41-1.41" />
            <circle cx="12" cy="12" r="8" />
          </svg>
        </div>
      </div>
      <div class="card-value">
        <p class="value-primary accent">{{ store.kpis.sharpeRatio.toFixed(3) }}</p>
      </div>
      <div class="card-meta">
        <span class="meta-label">Доходность / риск</span>
        <span class="meta-benchmark">Benchmark: 1.0</span>
      </div>
      <div class="card-progress">
        <div class="progress-bar accent" :style="{ width: Math.min(store.kpis.sharpeRatio * 20, 100) + '%' }"></div>
      </div>
    </div>

    <!-- KPI Card: Max Drawdown -->
    <div class="kpi-card" :class="{ negative: store.kpis.maxDrawdown < -0.1 }">
      <div class="card-header">
        <h3 class="card-label">Макс. просадка</h3>
        <div class="card-icon drawdown-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 18 13.5 8.5 8 14 1 7" />
            <polyline points="17 18 23 18 23 12" />
          </svg>
        </div>
      </div>
      <div class="card-value">
        <p class="value-primary" :class="store.kpis.maxDrawdown < 0 ? 'negative' : 'positive'">
          {{ (store.kpis.maxDrawdown * 100).toFixed(2) }}%
        </p>
      </div>
      <div class="card-meta">
        <span class="meta-label">От пика до дна</span>
        <span class="meta-change" :class="store.kpis.maxDrawdown < 0 ? 'negative' : 'positive'">
          {{ store.kpis.maxDrawdown < 0 ? '↓' : '↑' }}
        </span>
      </div>
      <div class="card-progress">
        <div class="progress-bar" :class="store.kpis.maxDrawdown < 0 ? 'danger' : 'success'" :style="{ width: Math.min(Math.abs(store.kpis.maxDrawdown * 100), 100) + '%' }"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePortfolioStore } from '@/stores/portfolio'

const store = usePortfolioStore()

const formatNumber = (value: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0,
    minimumFractionDigits: 0
  }).format(value)
}

const getProgressWidth = (value: number) => {
  // Нормализуем значение в диапазон 0-100%
  const maxValue = 1000000 // Предположим максимум 1M
  return Math.min(Math.abs(value) / maxValue * 100, 100) + '%'
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
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.12);
  --shadow-md: 0 8px 32px rgba(0, 0, 0, 0.2);
}

[data-theme="light"] {
  --color-bg-secondary: #f8f9fa;
  --color-bg-tertiary: #f0f1f5;
  --color-text-primary: #1a1a2e;
  --color-text-secondary: #6b7280;
  --color-text-tertiary: #9ca3af;
  --color-border: rgba(0, 0, 0, 0.08);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--spacing-md);
  width: 100%;
}

/* KPI Card Base */
.kpi-card {
  position: relative;
  padding: var(--spacing-md);
  background: var(--color-bg-glass);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition: all var(--duration-normal) cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  cursor: pointer;
  box-shadow: var(--shadow-md);
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--color-accent-primary), transparent);
  opacity: 0;
  transition: opacity var(--duration-normal);
}

.kpi-card:hover {
  border-color: var(--color-border-hover);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 217, 255, 0.15);
}

.kpi-card:hover::before {
  opacity: 1;
}

.kpi-card.positive::before {
  background: linear-gradient(90deg, transparent, var(--color-accent-success), transparent);
}

.kpi-card.warning::before {
  background: linear-gradient(90deg, transparent, var(--color-accent-warning), transparent);
}

.kpi-card.critical::before {
  background: linear-gradient(90deg, transparent, var(--color-accent-danger), transparent);
}

.kpi-card.negative::before {
  background: linear-gradient(90deg, transparent, var(--color-accent-danger), transparent);
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-sm);
}

.card-label {
  margin: 0;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-secondary);
  line-height: 1.2;
}

.card-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(0, 217, 255, 0.1);
  border: 1px solid rgba(0, 217, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-icon svg {
  width: 16px;
  height: 16px;
  color: var(--color-accent-primary);
}

.pnl-icon svg {
  color: var(--color-accent-success);
}

.pnl-icon {
  background: rgba(0, 255, 136, 0.1);
  border-color: rgba(0, 255, 136, 0.2);
}

.var-icon svg {
  color: var(--color-accent-warning);
}

.var-icon {
  background: rgba(255, 165, 0, 0.1);
  border-color: rgba(255, 165, 0, 0.2);
}

.cvar-icon svg {
  color: var(--color-accent-danger);
}

.cvar-icon {
  background: rgba(255, 51, 102, 0.1);
  border-color: rgba(255, 51, 102, 0.2);
}

.sharpe-icon svg {
  color: var(--color-accent-primary);
}

.sharpe-icon {
  background: rgba(0, 217, 255, 0.1);
  border-color: rgba(0, 217, 255, 0.2);
}

.drawdown-icon svg {
  color: var(--color-accent-secondary);
}

.drawdown-icon {
  background: rgba(255, 0, 110, 0.1);
  border-color: rgba(255, 0, 110, 0.2);
}

/* Card Value */
.card-value {
  margin-bottom: var(--spacing-sm);
}

.value-primary {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.5px;
  line-height: 1.2;
}

.value-primary.positive {
  color: var(--color-accent-success);
  text-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
}

.value-primary.negative {
  color: var(--color-accent-danger);
  text-shadow: 0 0 20px rgba(255, 51, 102, 0.3);
}

.value-primary.danger {
  color: var(--color-accent-danger);
  text-shadow: 0 0 20px rgba(255, 51, 102, 0.3);
}

.value-primary.accent {
  color: var(--color-accent-primary);
  text-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
}

/* Card Meta */
.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
  font-size: 0.75rem;
}

.meta-label {
  color: var(--color-text-secondary);
  font-weight: 500;
}

.meta-change {
  font-size: 1rem;
  font-weight: 700;
  transition: transform var(--duration-normal);
}

.meta-change.positive {
  color: var(--color-accent-success);
}

.meta-change.negative {
  color: var(--color-accent-danger);
}

.meta-indicator {
  font-size: 0.9rem;
  animation: pulse-indicator 2s ease-in-out infinite;
}

@keyframes pulse-indicator {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.meta-benchmark {
  color: var(--color-text-tertiary);
  font-size: 0.7rem;
}

/* Progress Bar */
.card-progress {
  width: 100%;
  height: 3px;
  background: var(--color-border);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--color-accent-primary), var(--color-accent-secondary));
  border-radius: 2px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 12px rgba(0, 217, 255, 0.5);
}

.progress-bar.success {
  background: linear-gradient(90deg, var(--color-accent-success), #00ff88);
  box-shadow: 0 0 12px rgba(0, 255, 136, 0.5);
}

.progress-bar.danger {
  background: linear-gradient(90deg, var(--color-accent-danger), #ff3366);
  box-shadow: 0 0 12px rgba(255, 51, 102, 0.5);
}

.progress-bar.accent {
  background: linear-gradient(90deg, var(--color-accent-primary), #00d9ff);
  box-shadow: 0 0 12px rgba(0, 217, 255, 0.5);
}

/* Responsive */
@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: var(--spacing-sm);
  }

  .value-primary {
    font-size: 1.5rem;
  }

  .card-label {
    font-size: 0.75rem;
  }
}

@media (max-width: 768px) {
  .kpi-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: var(--spacing-sm);
  }

  .kpi-card {
    padding: var(--spacing-sm);
  }

  .value-primary {
    font-size: 1.25rem;
  }

  .card-header {
    margin-bottom: var(--spacing-xs);
  }

  .card-icon {
    width: 28px;
    height: 28px;
  }

  .card-icon svg {
    width: 14px;
    height: 14px;
  }
}
</style>
