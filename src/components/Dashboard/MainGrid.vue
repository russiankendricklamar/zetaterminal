<template>
  <div class="main-grid-container">
    <!-- Heatmap Chart -->
    <div class="chart-card heatmap-card">
      <div class="card-header">
        <div class="header-content">
          <h3 class="card-title">Тепловая карта портфеля</h3>
          <p class="card-description">Корреляция vs волатильность по активам</p>
        </div>
        <button class="btn-refresh" @click="refreshHeatmap" title="Обновить">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10" />
            <polyline points="1 20 1 14 7 14" />
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36M20.49 15a9 9 0 0 1-14.85 3.36" />
          </svg>
        </button>
      </div>
      <div class="chart-wrapper">
        <canvas id="heatmapChart" class="chart-canvas"></canvas>
      </div>
      <div class="card-footer">
        <span class="footer-text">{{ store.heatmapData.length }} активов в портфеле</span>
      </div>
    </div>

    <!-- Price Chart -->
    <div class="chart-card price-card">
      <div class="card-header">
        <div class="header-content">
          <h3 class="card-title">Динамика цены</h3>
          <p class="card-description">{{ store.selectedModel }}</p>
        </div>
        <div class="header-actions">
          <select v-model="store.selectedModel" class="model-select">
            <option value="SPY">SPY</option>
            <option value="QQQ">QQQ</option>
            <option value="IVV">IVV</option>
          </select>
        </div>
      </div>
      <div class="chart-wrapper">
        <canvas id="priceChart" class="chart-canvas"></canvas>
      </div>
      <div class="card-footer">
        <div class="footer-stats">
          <span class="stat-item">
            <span class="stat-label">Точек:</span>
            <span class="stat-value">{{ store.priceHistory.length }}</span>
          </span>
          <span class="stat-divider">•</span>
          <span class="stat-item">
            <span class="stat-label">Период:</span>
            <span class="stat-value">{{ chartPeriod }}</span>
          </span>
        </div>
      </div>
    </div>

    <!-- Model Diagnostics & Monte Carlo -->
    <div class="diagnostics-card">
      <div class="card-header">
        <div class="header-content">
          <h3 class="card-title">Диагностика модели</h3>
          <p class="card-description">Параметры и статистика</p>
        </div>
        <div class="header-badge" :class="{ 'status-good': isModelGood }">
          {{ isModelGood ? '✓ OK' : '⚠ Warning' }}
        </div>
      </div>

      <div class="diagnostics-content">
        <!-- Model Metrics Grid -->
        <div class="metrics-grid">
          <div class="metric-item">
            <span class="metric-label">Модель</span>
            <span class="metric-value">
              {{ store.modelDiagnostics.modelName || '—' }}
            </span>
          </div>

          <div class="metric-item">
            <span class="metric-label">KS-тест</span>
            <span class="metric-value" :class="getKsTestClass()">
              {{ store.modelDiagnostics.ksTestPValue != null
                  ? store.modelDiagnostics.ksTestPValue.toFixed(4)
                  : 'N/A' }}
            </span>
            <span class="metric-hint">p-value</span>
          </div>

          <div class="metric-item">
            <span class="metric-label">Accuracy</span>
            <span class="metric-value success">
              {{ (store.modelDiagnostics.backtestingAccuracy * 100).toFixed(1) }}%
            </span>
            <span class="metric-hint">Backtesting</span>
          </div>
        </div>

        <!-- Monte Carlo Configuration -->
        <div class="monte-carlo-section">
          <div class="section-divider"></div>

          <h4 class="section-title">Монте-Карло симуляция</h4>

          <div class="controls-grid">
            <div class="control-group">
              <label class="control-label">Количество путей</label>
              <div class="input-wrapper">
                <input
                  v-model.number="nPaths"
                  type="number"
                  min="1000"
                  step="1000"
                  max="1000000"
                  class="control-input"
                  :disabled="isRunning"
                />
                <span class="input-unit">paths</span>
              </div>
            </div>

            <div class="control-group">
              <label class="control-label">Шагов</label>
              <div class="input-wrapper">
                <input
                  v-model.number="nSteps"
                  type="number"
                  min="10"
                  step="10"
                  max="1000"
                  class="control-input"
                  :disabled="isRunning"
                />
                <span class="input-unit">steps</span>
              </div>
            </div>
          </div>

          <button
            @click="runMonteCarlo"
            :disabled="isRunning"
            class="btn-run-mc"
            :class="{ running: isRunning }"
          >
            <span v-if="!isRunning" class="btn-text">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
              Запустить симуляцию
            </span>
            <span v-else class="btn-text loading">
              <span class="spinner"></span>
              Выполняется на {{ nPaths.toLocaleString('ru-RU') }} путей...
            </span>
          </button>

          <!-- Results Section -->
          <transition name="fade">
            <div v-if="mcResults" class="results-section">
              <div class="results-header">
                <h5 class="results-title">Результаты последней симуляции</h5>
              </div>
              <div class="results-grid">
                <div class="result-item">
                  <span class="result-label">VaR 95%</span>
                  <span class="result-value danger">
                    {{ mcResults.var95.toFixed(4) }}
                  </span>
                </div>
                <div class="result-item">
                  <span class="result-label">CVaR 95%</span>
                  <span class="result-value danger">
                    {{ mcResults.cvar95.toFixed(4) }}
                  </span>
                </div>
                <div class="result-item">
                  <span class="result-label">Mean Return</span>
                  <span class="result-value success">
                    {{ mcResults.meanReturn.toFixed(4) }}
                  </span>
                </div>
              </div>
              <div class="result-meta">
                <span class="meta-time">{{ mcResultsTime }}</span>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'
import Chart from 'chart.js/auto'

const store = usePortfolioStore()

// State
const nPaths = ref(10000)
const nSteps = ref(252)
const isRunning = ref(false)
const mcResults = ref<any>(null)
const mcResultsTime = ref<string>('')

let heatmapChart: Chart | null = null
let priceChart: Chart | null = null

const isModelGood = computed(
  () => store.modelDiagnostics.ksTestPValue > 0.05
)

const chartPeriod = computed(() => {
  if (store.priceHistory.length < 2) return '—'
  const first = new Date(store.priceHistory[0].date)
  const last = new Date(store.priceHistory[store.priceHistory.length - 1].date)
  const days = Math.floor((last.getTime() - first.getTime()) / (1000 * 60 * 60 * 24))
  return `${days} дней`
})

// Methods
const getKsTestClass = () => {
  const p = store.modelDiagnostics.ksTestPValue
  if (p > 0.1) return 'success'
  if (p > 0.05) return 'warning'
  return 'danger'
}

const renderHeatmapChart = () => {
  if (!store.heatmapData.length) return

  const canvas = document.getElementById('heatmapChart') as HTMLCanvasElement
  if (!canvas) return

  // Destroy existing chart
  if (heatmapChart) {
    heatmapChart.destroy()
  }

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  heatmapChart = new Chart(ctx, {
    type: 'bubble',
    data: {
      datasets: store.heatmapData.map((item, idx) => ({
        label: item.asset,
        data: [
          {
            x: item.correlation,
            y: item.volatility,
            r: Math.sqrt(Math.abs(item.notional)) / 50
          }
        ],
        backgroundColor: item.pnl > 0
          ? 'rgba(0, 255, 136, 0.5)'
          : 'rgba(255, 51, 102, 0.5)',
        borderColor: item.pnl > 0 ? '#00ff88' : '#ff3366',
        borderWidth: 2,
        hoverBackgroundColor: item.pnl > 0
          ? 'rgba(0, 255, 136, 0.8)'
          : 'rgba(255, 51, 102, 0.8)'
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(26, 26, 46, 0.9)',
          borderColor: 'rgba(0, 217, 255, 0.3)',
          borderWidth: 1,
          padding: 12,
          titleColor: '#e0e0e0',
          bodyColor: '#a0a0a0',
          cornerRadius: 8
        }
      },
      scales: {
        x: {
          min: -1,
          max: 1,
          grid: {
            color: 'rgba(255, 255, 255, 0.05)',
            drawBorder: false
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.5)'
          },
          title: {
            display: true,
            text: 'Корреляция',
            color: '#e0e0e0',
            font: { weight: 'bold' as const }
          }
        },
        y: {
          min: 0,
          max: 0.5,
          grid: {
            color: 'rgba(255, 255, 255, 0.05)',
            drawBorder: false
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.5)'
          },
          title: {
            display: true,
            text: 'Волатильность',
            color: '#e0e0e0',
            font: { weight: 'bold' as const }
          }
        }
      }
    }
  })
}

const renderPriceChart = () => {
  if (!store.priceHistory.length) return

  const canvas = document.getElementById('priceChart') as HTMLCanvasElement
  if (!canvas) return

  // Destroy existing chart
  if (priceChart) {
    priceChart.destroy()
  }

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const dates = store.priceHistory.map((p) =>
    new Date(p.date).toLocaleDateString('ru-RU', {
      month: 'short',
      day: 'numeric'
    })
  )
  const closes = store.priceHistory.map((p) => p.close)

  priceChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: dates,
      datasets: [
        {
          label: 'Цена закрытия',
          data: closes,
          borderColor: '#00d9ff',
          backgroundColor: 'rgba(0, 217, 255, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 6,
          pointBackgroundColor: '#00d9ff',
          pointBorderColor: '#0f0f1e',
          pointBorderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      interaction: {
        mode: 'index' as const,
        intersect: false
      },
      plugins: {
        legend: {
          display: true,
          labels: {
            color: '#e0e0e0',
            usePointStyle: true,
            padding: 15
          }
        },
        tooltip: {
          backgroundColor: 'rgba(26, 26, 46, 0.9)',
          borderColor: 'rgba(0, 217, 255, 0.3)',
          borderWidth: 1,
          padding: 12,
          titleColor: '#e0e0e0',
          bodyColor: '#00d9ff',
          cornerRadius: 8
        }
      },
      scales: {
        x: {
          grid: {
            display: false,
            drawBorder: false
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.5)',
            maxRotation: 0
          }
        },
        y: {
          beginAtZero: false,
          grid: {
            color: 'rgba(255, 255, 255, 0.05)',
            drawBorder: false
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.5)'
          }
        }
      }
    }
  })
}

const refreshHeatmap = () => {
  store.fetchHeatmapData()
  setTimeout(renderHeatmapChart, 100)
}

const runMonteCarlo = async () => {
  try {
    isRunning.value = true

    const result = await store.runMonteCarlo(nPaths.value, nSteps.value, 'levy')

    mcResults.value = result.results
    const now = new Date()
    mcResultsTime.value = now.toLocaleTimeString('ru-RU')

    // Show success notification
    console.log('Monte Carlo completed:', result)
  } catch (error) {
    console.error('Monte Carlo error:', error)
    mcResults.value = null
  } finally {
    isRunning.value = false
  }
}

onMounted(() => {
  store.fetchHeatmapData()
  store.fetchPriceHistory('SPY', 60)
  store.fetchModelDiagnostics()

  setTimeout(() => {
    renderHeatmapChart()
    renderPriceChart()
  }, 100)
})
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

.main-grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: var(--spacing-lg);
  width: 100%;
}

/* Chart Cards */
.chart-card {
  display: flex;
  flex-direction: column;
  background: var(--color-bg-glass);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: all var(--duration-normal);
}

.chart-card:hover {
  border-color: var(--color-border-hover);
  box-shadow: 0 12px 40px rgba(0, 217, 255, 0.1);
}

.heatmap-card {
  grid-column: 1;
  grid-row: 1 / 3;
}

.price-card {
  grid-column: 2;
  grid-row: 1;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
  background: rgba(0, 0, 0, 0.1);
}

.header-content {
  flex: 1;
  min-width: 0;
}

.card-title {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.5px;
}

.card-description {
  margin: 0;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.btn-refresh {
  width: 36px;
  height: 36px;
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-normal);
}

.btn-refresh:hover {
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
  background: rgba(0, 217, 255, 0.1);
}

.btn-refresh svg {
  width: 18px;
  height: 18px;
}

.model-select {
  padding: 6px 12px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  color: var(--color-text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all var(--duration-normal);
}

.model-select:hover,
.model-select:focus {
  border-color: var(--color-accent-primary);
  outline: none;
}

.header-badge {
  padding: 4px 12px;
  background: rgba(255, 165, 0, 0.15);
  border: 1px solid rgba(255, 165, 0, 0.3);
  color: var(--color-accent-warning);
  border-radius: 0.5rem;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}

.header-badge.status-good {
  background: rgba(0, 255, 136, 0.15);
  border-color: rgba(0, 255, 136, 0.3);
  color: var(--color-accent-success);
}

/* Chart Wrapper */
.chart-wrapper {
  flex: 1;
  position: relative;
  padding: var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.chart-canvas {
  width: 100% !important;
  height: 100% !important;
}

/* Card Footer */
.card-footer {
  border-top: 1px solid var(--color-border);
  padding: var(--spacing-sm) var(--spacing-lg);
  background: rgba(0, 0, 0, 0.05);
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.footer-text {
  display: block;
}

.footer-stats {
  display: flex;
  gap: var(--spacing-md);
}

.stat-item {
  display: flex;
  gap: var(--spacing-xs);
}

.stat-label {
  color: var(--color-text-secondary);
}

.stat-value {
  color: var(--color-accent-primary);
  font-weight: 600;
}

.stat-divider {
  opacity: 0.3;
}

/* Diagnostics Card */
.diagnostics-card {
  grid-column: 2;
  grid-row: 2;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-glass);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: all var(--duration-normal);
}

.diagnostics-card:hover {
  border-color: var(--color-border-hover);
}

.diagnostics-content {
  flex: 1;
  padding: var(--spacing-lg);
  overflow-y: auto;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.metric-item {
  display: flex;
  flex-direction: column;
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  gap: var(--spacing-xs);
}

.metric-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.metric-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.metric-value.success {
  color: var(--color-accent-success);
}

.metric-value.warning {
  color: var(--color-accent-warning);
}

.metric-value.danger {
  color: var(--color-accent-danger);
}

.metric-hint {
  font-size: 0.7rem;
  color: var(--color-text-tertiary);
}

/* Monte Carlo Section */
.section-divider {
  height: 1px;
  background: var(--color-border);
  margin: var(--spacing-lg) 0;
}

.section-title {
  margin: 0 0 var(--spacing-md) 0;
  font-size: 0.95rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-primary);
}

.controls-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.control-label {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-secondary);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.control-input {
  flex: 1;
  padding: 10px 12px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  color: var(--color-text-primary);
  font-size: 0.9rem;
  font-weight: 600;
  outline: none;
  transition: all var(--duration-normal);
}

.control-input:focus {
  border-color: var(--color-accent-primary);
  box-shadow: 0 0 12px rgba(0, 217, 255, 0.2);
}

.control-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-unit {
  position: absolute;
  right: 12px;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  pointer-events: none;
}

/* Monte Carlo Button */
.btn-run-mc {
  width: 100%;
  padding: 12px 16px;
  background: linear-gradient(135deg, var(--color-accent-primary), #00d9ff);
  border: none;
  border-radius: 0.75rem;
  color: var(--color-bg-primary);
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all var(--duration-normal);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-run-mc:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 217, 255, 0.4);
}

.btn-run-mc:disabled {
  opacity: 0.8;
  cursor: wait;
}

.btn-run-mc svg {
  width: 16px;
  height: 16px;
}

.btn-text {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.btn-text.loading {
  gap: var(--spacing-md);
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(15, 15, 30, 0.3);
  border-top: 2px solid var(--color-bg-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Results Section */
.results-section {
  margin-top: var(--spacing-lg);
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
}

.results-header {
  margin-bottom: var(--spacing-md);
}

.results-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--color-text-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-sm);
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm);
  background: var(--color-bg-tertiary);
  border-radius: 0.5rem;
}

.result-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.result-value {
  font-size: 1rem;
  font-weight: 700;
  font-family: 'Courier New', monospace;
}

.result-value.success {
  color: var(--color-accent-success);
}

.result-value.danger {
  color: var(--color-accent-danger);
}

.result-meta {
  margin-top: var(--spacing-sm);
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  text-align: right;
}

.meta-time {
  display: block;
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

/* Responsive */
@media (max-width: 1400px) {
  .main-grid-container {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
  }

  .heatmap-card {
    grid-column: 1;
    grid-row: 1;
  }

  .price-card {
    grid-column: 1;
    grid-row: 2;
  }

  .diagnostics-card {
    grid-column: 1;
    grid-row: 3;
  }

  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .main-grid-container {
    gap: var(--spacing-md);
  }

  .chart-wrapper {
    min-height: 250px;
    padding: var(--spacing-md);
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .controls-grid {
    grid-template-columns: 1fr;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }
}

/* Scrollbar */
.diagnostics-content::-webkit-scrollbar {
  width: 6px;
}

.diagnostics-content::-webkit-scrollbar-track {
  background: transparent;
}

.diagnostics-content::-webkit-scrollbar-thumb {
  background: var(--color-border-hover);
  border-radius: 3px;
}
</style>