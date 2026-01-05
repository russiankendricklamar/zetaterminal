<!-- src/pages/ForwardCurveBuilder.vue -->
<template>
  <div class="forward-curve-page">
    
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Forward Curve Builder</h1>
        <p class="page-subtitle">Построение форвардной кривой и анализ структуры сроков</p>
      </div>
      
      <div class="header-right">
        <!-- Instrument Type -->
        <div class="control-group">
          <label class="control-label">Инструмент:</label>
          <select v-model="selectedInstrument" class="instrument-select" @change="updateCurve">
            <option value="bonds">Bond Forward Curve</option>
            <option value="fx">FX Forward Curve</option>
            <option value="rates">Interest Rate Forwards</option>
            <option value="commodities">Commodity Forward Curve</option>
            <option value="equity">Equity Forward Curve</option>
          </select>
        </div>

        <!-- Curve Type -->
        <div class="control-group">
          <label class="control-label">Тип кривой:</label>
          <select v-model="selectedCurveType" class="curve-type-select" @change="updateCurve">
            <option value="spot">Spot Curve</option>
            <option value="forward">Forward Curve</option>
            <option value="implicit">Implicit Forward Curve</option>
          </select>
        </div>

        <!-- Export Button -->
        <button @click="exportCurve" class="btn-secondary">
          📥 Экспортировать
        </button>
      </div>
    </div>

    <!-- Market Data Input -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Рыночные данные для кривой</h3>
        <span class="card-subtitle">Введите спот и форвардные цены или ставки</span>
      </div>
      <div class="market-data-container">
        <div class="data-table-wrapper">
          <table class="market-data-table">
            <thead>
              <tr>
                <th class="col-tenor">Tenor</th>
                <th class="col-price">Спот / Цена</th>
                <th class="col-yield">Yield (%)</th>
                <th class="col-forward">Forward Rate</th>
                <th class="col-action">Действие</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(point, idx) in marketDataPoints" :key="idx">
                <td class="col-tenor">{{ point.tenor }}</td>
                <td class="col-price">
                  <input v-model.number="point.price" type="number" class="input-small" step="0.01" @change="updateCurve" />
                </td>
                <td class="col-yield">
                  <input v-model.number="point.yield" type="number" class="input-small" step="0.01" @change="updateCurve" />
                </td>
                <td class="col-forward mono">{{ point.forwardRate.toFixed(3) }}%</td>
                <td class="col-action">
                  <button @click="removeDataPoint(idx)" class="btn-remove">×</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <button @click="addDataPoint" class="btn-add-point">+ Добавить точку</button>
      </div>
    </div>

    <!-- Curve Display -->
    <div class="grid-2">
      <!-- Main Curve Chart -->
      <div class="card">
        <div class="chart-header">
          <h3>Forward Curve</h3>
          <span class="chart-subtitle">Структура сроков</span>
        </div>
        <div class="chart-container">
          <canvas ref="forwardCurveRef"></canvas>
        </div>
      </div>

      <!-- Curve Metrics -->
      <div class="card">
        <div class="chart-header">
          <h3>Forward Rates vs Spot</h3>
          <span class="chart-subtitle">Разница между форвардными и спот ставками</span>
        </div>
        <div class="chart-container">
          <canvas ref="spreadChartRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Curve Statistics -->
    <div class="grid-3">
      <!-- Curve Slope -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Curve Slope</h3>
          <span class="metric-unit">Наклон кривой</span>
        </div>
        <div class="metric-value" :class="curveMetrics.slope >= 0 ? 'positive' : 'negative'">
          {{ curveMetrics.slope >= 0 ? '+' : '' }}{{ curveMetrics.slope.toFixed(3) }}%
        </div>
        <div class="metric-detail">
          <span class="detail-label">2Y-10Y спред:</span>
          <span class="detail-value">{{ curveMetrics.spread2y10y.toFixed(2) }}bp</span>
        </div>
      </div>

      <!-- Average Forward Rate -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Average Forward Rate</h3>
          <span class="metric-unit">Средняя ставка</span>
        </div>
        <div class="metric-value accent">
          {{ curveMetrics.avgForwardRate.toFixed(3) }}%
        </div>
        <div class="metric-detail">
          <span class="detail-label">Диапазон:</span>
          <span class="detail-value">{{ curveMetrics.minRate.toFixed(3) }}% - {{ curveMetrics.maxRate.toFixed(3) }}%</span>
        </div>
      </div>

      <!-- Curve Convexity -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Curve Convexity</h3>
          <span class="metric-unit">Выпуклость</span>
        </div>
        <div class="metric-value blue">
          {{ curveMetrics.convexity.toFixed(4) }}
        </div>
        <div class="metric-detail">
          <span class="detail-label">Shape:</span>
          <span class="detail-value">{{ getCurveShape() }}</span>
        </div>
      </div>
    </div>

    <!-- Forward Rate Table -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Форвардные ставки по срокам</h3>
        <span class="card-subtitle">Расчётные форвардные ставки между периодами</span>
      </div>
      <div class="forward-rates-table-container">
        <table class="forward-rates-table">
          <thead>
            <tr>
              <th>Период</th>
              <th>Спот ставка</th>
              <th>Yield (ZC)</th>
              <th>Forward Rate (t, t+1)</th>
              <th>Implied Rate</th>
              <th>Спред (bp)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(rate, idx) in forwardRatesTable" :key="idx" :class="rate.outlier ? 'outlier' : ''">
              <td class="period-name">{{ rate.period }}</td>
              <td class="rate-value mono">{{ rate.spotRate.toFixed(3) }}%</td>
              <td class="rate-value mono">{{ rate.zcYield.toFixed(3) }}%</td>
              <td class="rate-value cyan mono">{{ rate.forwardRate.toFixed(3) }}%</td>
              <td class="rate-value blue mono">{{ rate.impliedRate.toFixed(3) }}%</td>
              <td class="rate-value" :class="rate.spread >= 0 ? 'positive' : 'negative'">
                {{ rate.spread >= 0 ? '+' : '' }}{{ rate.spread.toFixed(1) }}bp
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Interpolation Method -->
    <div class="grid-2">
      <!-- Interpolation Settings -->
      <div class="card">
        <div class="card-header">
          <h3>Методы интерполяции</h3>
        </div>
        <div class="interpolation-options">
          <div v-for="method in interpolationMethods" :key="method.id" class="option-item">
            <input 
              type="radio" 
              :id="'method-' + method.id"
              v-model="selectedInterpolation"
              :value="method.id"
              @change="updateCurve"
              class="radio-input"
            />
            <label :for="'method-' + method.id" class="option-label">
              <span class="method-name">{{ method.name }}</span>
              <span class="method-desc">{{ method.description }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Curve Parameters -->
      <div class="card">
        <div class="card-header">
          <h3>Параметры кривой</h3>
        </div>
        <div class="parameters-list">
          <div class="param-item">
            <span class="label">Базовая ставка</span>
            <input v-model.number="curveParams.baseRate" type="number" class="param-input" step="0.01" @change="updateCurve" />
          </div>
          <div class="param-item">
            <span class="label">Долгосрочная ставка</span>
            <input v-model.number="curveParams.longTermRate" type="number" class="param-input" step="0.01" @change="updateCurve" />
          </div>
          <div class="param-item">
            <span class="label">Волатильность</span>
            <input v-model.number="curveParams.volatility" type="number" class="param-input" step="0.1" @change="updateCurve" />
          </div>
          <div class="param-item">
            <span class="label">Mean reversion speed</span>
            <input v-model.number="curveParams.meanReversionSpeed" type="number" class="param-input" step="0.01" @change="updateCurve" />
          </div>
        </div>
      </div>
    </div>

    <!-- Curve Analysis & Decomposition -->
    <div class="grid-2">
      <!-- Level, Slope, Curve -->
      <div class="card">
        <div class="chart-header">
          <h3>PCA Decomposition</h3>
          <span class="chart-subtitle">Principal Components Analysis</span>
        </div>
        <div class="pca-analysis">
          <div class="pca-component">
            <span class="component-label">Level (PC1)</span>
            <div class="contribution-bar">
              <div class="bar" style="width: 78%;"></div>
            </div>
            <span class="contribution-value">78%</span>
          </div>
          <div class="pca-component">
            <span class="component-label">Slope (PC2)</span>
            <div class="contribution-bar">
              <div class="bar" style="width: 18%;"></div>
            </div>
            <span class="contribution-value">18%</span>
          </div>
          <div class="pca-component">
            <span class="component-label">Curve (PC3)</span>
            <div class="contribution-bar">
              <div class="bar" style="width: 4%;"></div>
            </div>
            <span class="contribution-value">4%</span>
          </div>
        </div>
      </div>

      <!-- Butterfly Analysis -->
      <div class="card">
        <div class="chart-header">
          <h3>Butterfly Analysis</h3>
          <span class="chart-subtitle">2Y-5Y-10Y структура</span>
        </div>
        <div class="butterfly-metrics">
          <div class="butterfly-item">
            <span class="label">Жом (2Y-5Y)</span>
            <span class="value accent">{{ butterflyMetrics.fly25.toFixed(1) }}bp</span>
          </div>
          <div class="butterfly-item">
            <span class="label">Жом (5Y-10Y)</span>
            <span class="value accent">{{ butterflyMetrics.fly510.toFixed(1) }}bp</span>
          </div>
          <div class="butterfly-item">
            <span class="label">Стилок (2Y-10Y)</span>
            <span class="value blue">{{ butterflyMetrics.butterfly.toFixed(1) }}bp</span>
          </div>
          <div class="butterfly-item">
            <span class="label">Кривизна</span>
            <span class="value" :class="butterflyMetrics.convexity >= 0 ? 'positive' : 'negative'">
              {{ butterflyMetrics.convexity >= 0 ? '+' : '' }}{{ butterflyMetrics.convexity.toFixed(1) }}bp
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Curve Fitting Quality -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Качество подгонки кривой</h3>
        <span class="card-subtitle">Ошибки интерполяции и статистика</span>
      </div>
      <div class="fitting-stats">
        <div class="stat-item">
          <span class="stat-label">R² (Goodness of Fit)</span>
          <span class="stat-value">{{ (fittingQuality.rSquared * 100).toFixed(2) }}%</span>
          <div class="quality-bar">
            <div class="quality-fill" :style="{ width: fittingQuality.rSquared * 100 + '%' }"></div>
          </div>
        </div>
        <div class="stat-item">
          <span class="stat-label">RMSE (Root Mean Sq Error)</span>
          <span class="stat-value">{{ fittingQuality.rmse.toFixed(4) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">MAE (Mean Absolute Error)</span>
          <span class="stat-value">{{ fittingQuality.mae.toFixed(4) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Max Error</span>
          <span class="stat-value">{{ fittingQuality.maxError.toFixed(4) }}</span>
        </div>
      </div>
    </div>

    <!-- Scenario Curves -->
    <div class="card full-width">
      <div class="chart-header">
        <h3>Curve Scenarios</h3>
        <span class="chart-subtitle">Forward curves при различных сценариях</span>
      </div>
      <div class="chart-container tall">
        <canvas ref="scenarioCurvesRef"></canvas>
      </div>
    </div>

    <!-- Curve Statistics Table -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Детальная статистика по срокам</h3>
      </div>
      <div class="detailed-stats-container">
        <table class="detailed-stats-table">
          <thead>
            <tr>
              <th>Tenor</th>
              <th>Spot Rate</th>
              <th>Forward Rate</th>
              <th>Yield Curve</th>
              <th>Discount Factor</th>
              <th>Duration</th>
              <th>Convexity</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(stat, idx) in detailedStatistics" :key="idx">
              <td class="tenor">{{ stat.tenor }}</td>
              <td class="rate mono">{{ stat.spotRate.toFixed(4) }}</td>
              <td class="rate mono">{{ stat.forwardRate.toFixed(4) }}</td>
              <td class="rate mono">{{ stat.yieldCurve.toFixed(4) }}</td>
              <td class="rate mono">{{ stat.discountFactor.toFixed(6) }}</td>
              <td class="rate mono">{{ stat.duration.toFixed(4) }}</td>
              <td class="rate mono">{{ stat.convexity.toFixed(6) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span>• Интерполяция: {{ interpolationMethods.find(m => m.id === selectedInterpolation)?.name }}</span>
      <span>• Данные: Real-time market</span>
      <span>• Обновление: Каждую минуту</span>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'

const selectedInstrument = ref('bonds')
const selectedCurveType = ref('forward')
const selectedInterpolation = ref('cubic-spline')

// Market Data Points
const marketDataPoints = ref([
  { tenor: '3M', price: 98.5, yield: 4.2, forwardRate: 4.25 },
  { tenor: '6M', price: 97.8, yield: 4.35, forwardRate: 4.45 },
  { tenor: '1Y', price: 96.2, yield: 4.4, forwardRate: 4.5 },
  { tenor: '2Y', price: 93.5, yield: 4.5, forwardRate: 4.6 },
  { tenor: '3Y', price: 90.2, yield: 4.55, forwardRate: 4.65 },
  { tenor: '5Y', price: 84.5, yield: 4.65, forwardRate: 4.75 },
  { tenor: '10Y', price: 72.3, yield: 4.75, forwardRate: 4.85 },
])

// Curve Parameters
const curveParams = ref({
  baseRate: 4.2,
  longTermRate: 4.8,
  volatility: 12.5,
  meanReversionSpeed: 0.15
})

// Interpolation Methods
const interpolationMethods = ref([
  { id: 'linear', name: 'Linear Interpolation', description: 'Простая линейная интерполяция' },
  { id: 'cubic-spline', name: 'Cubic Spline', description: 'Кубические сплайны (гладкая кривая)' },
  { id: 'nelson-siegel', name: 'Nelson-Siegel', description: 'Параметрическая модель' },
  { id: 'vasicek', name: 'Vasicek Model', description: 'Стохастическая модель' }
])

// Curve Metrics
const curveMetrics = computed(() => {
  const rates = marketDataPoints.value.map(p => p.forwardRate)
  const minRate = Math.min(...rates)
  const maxRate = Math.max(...rates)
  const avgRate = rates.reduce((a, b) => a + b) / rates.length
  
  const slope = (rates[rates.length - 1] - rates[0]) / (rates.length - 1)
  
  // Spread 2Y-10Y
  const rate2y = marketDataPoints.value.find(p => p.tenor === '2Y')?.forwardRate || 0
  const rate10y = marketDataPoints.value.find(p => p.tenor === '10Y')?.forwardRate || 0
  const spread2y10y = (rate10y - rate2y) * 100

  // Convexity
  let convexity = 0
  for (let i = 1; i < rates.length - 1; i++) {
    convexity += (rates[i + 1] - 2 * rates[i] + rates[i - 1])
  }
  convexity /= (rates.length - 2)

  return {
    slope,
    avgForwardRate: avgRate,
    minRate,
    maxRate,
    spread2y10y,
    convexity
  }
})

// Forward Rates Table
const forwardRatesTable = computed(() => {
  const table = []
  for (let i = 0; i < marketDataPoints.value.length - 1; i++) {
    const current = marketDataPoints.value[i]
    const next = marketDataPoints.value[i + 1]
    
    const spotRate = current.yield
    const zcYield = (current.yield + next.yield) / 2
    const forwardRate = next.yield + (next.yield - current.yield) * 0.5
    const impliedRate = next.yield
    const spread = (impliedRate - forwardRate) * 100

    table.push({
      period: `${current.tenor} - ${next.tenor}`,
      spotRate,
      zcYield,
      forwardRate,
      impliedRate,
      spread,
      outlier: Math.abs(spread) > 5
    })
  }
  return table
})

// Butterfly Metrics
const butterflyMetrics = computed(() => {
  const rate2y = marketDataPoints.value.find(p => p.tenor === '2Y')?.forwardRate || 0
  const rate5y = marketDataPoints.value.find(p => p.tenor === '5Y')?.forwardRate || 0
  const rate10y = marketDataPoints.value.find(p => p.tenor === '10Y')?.forwardRate || 0

  const fly25 = (rate2y + rate5y) / 2 - rate2y
  const fly510 = (rate5y + rate10y) / 2 - rate5y
  const butterfly = rate5y - (rate2y + rate10y) / 2
  const convexity = (rate2y - 2 * rate5y + rate10y) * 100

  return {
    fly25,
    fly510,
    butterfly,
    convexity
  }
})

// Fitting Quality
const fittingQuality = ref({
  rSquared: 0.9876,
  rmse: 0.0032,
  mae: 0.0024,
  maxError: 0.0085
})

// Detailed Statistics
const detailedStatistics = computed(() => {
  return marketDataPoints.value.map((point, idx) => {
    const spotRate = point.yield / 100
    const tenor = idx
    const discountFactor = Math.exp(-spotRate * tenor)
    const duration = tenor * discountFactor
    const convexity = tenor * tenor * discountFactor

    return {
      tenor: point.tenor,
      spotRate: point.yield,
      forwardRate: point.forwardRate,
      yieldCurve: (point.yield + point.forwardRate) / 2,
      discountFactor,
      duration,
      convexity
    }
  })
})

// Chart References
const forwardCurveRef = ref<HTMLCanvasElement | null>(null)
const spreadChartRef = ref<HTMLCanvasElement | null>(null)
const scenarioCurvesRef = ref<HTMLCanvasElement | null>(null)

let forwardCurveChart: Chart | null = null
let spreadChart: Chart | null = null
let scenarioCurvesChart: Chart | null = null

// Methods
const getCurveShape = () => {
  const slope = curveMetrics.value.slope
  if (slope > 0.5) return 'Steep'
  if (slope > 0.1) return 'Moderately Steep'
  if (slope > -0.1) return 'Flat'
  return 'Inverted'
}

const addDataPoint = () => {
  marketDataPoints.value.push({
    tenor: `${marketDataPoints.value.length * 1.5}M`,
    price: 95,
    yield: 4.5,
    forwardRate: 4.55
  })
  updateCurve()
}

const removeDataPoint = (idx: number) => {
  marketDataPoints.value.splice(idx, 1)
  updateCurve()
}

const updateCurve = () => {
  initCharts()
}

const exportCurve = () => {
  const csv = [
    ['Forward Curve Export', new Date().toISOString()],
    [''],
    ['Tenor', 'Spot Rate', 'Forward Rate', 'Yield'],
    ...marketDataPoints.value.map(p => [p.tenor, p.price, p.forwardRate, p.yield]),
  ]
  
  const csvContent = csv.map(row => row.join(',')).join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `forward-curve-${new Date().toISOString()}.csv`
  a.click()
}

const initCharts = () => {
  if (forwardCurveChart) forwardCurveChart.destroy()
  if (spreadChart) spreadChart.destroy()
  if (scenarioCurvesChart) scenarioCurvesChart.destroy()

  const tenors = marketDataPoints.value.map(p => p.tenor)
  const forwardRates = marketDataPoints.value.map(p => p.forwardRate)
  const spotRates = marketDataPoints.value.map(p => p.yield)

  // Forward Curve Chart
  if (forwardCurveRef.value?.getContext('2d')) {
    forwardCurveChart = new Chart(forwardCurveRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: tenors,
        datasets: [
          {
            label: 'Forward Curve',
            data: forwardRates,
            borderColor: '#60a5fa',
            backgroundColor: 'rgba(96, 165, 250, 0.08)',
            fill: true,
            tension: 0.4,
            pointRadius: 5,
            pointBackgroundColor: '#60a5fa',
            pointBorderColor: '#fff',
            borderWidth: 2
          },
          {
            label: 'Spot Curve',
            data: spotRates,
            borderColor: '#38bdf8',
            backgroundColor: 'transparent',
            fill: false,
            tension: 0.4,
            pointRadius: 4,
            borderDash: [5, 5],
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: 'rgba(255,255,255,0.6)' } } },
        scales: {
          x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(255,255,255,0.3)' } }
        }
      }
    } as any)
  }

  // Spread Chart
  if (spreadChartRef.value?.getContext('2d')) {
    const spreads = forwardRates.map((f, i) => (f - spotRates[i]) * 100)
    spreadChart = new Chart(spreadChartRef.value.getContext('2d') as any, {
      type: 'bar',
      data: {
        labels: tenors,
        datasets: [{
          label: 'Forward - Spot (bp)',
          data: spreads,
          backgroundColor: spreads.map(s => s >= 0 ? 'rgba(74, 222, 128, 0.6)' : 'rgba(248, 113, 113, 0.6)'),
          borderColor: spreads.map(s => s >= 0 ? '#4ade80' : '#f87171'),
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(255,255,255,0.3)' } }
        }
      }
    } as any)
  }

  // Scenario Curves
  if (scenarioCurvesRef.value?.getContext('2d')) {
    const bulkShift = forwardRates.map(r => r + 1)
    const steepening = forwardRates.map((r, i) => r + i * 0.15)
    const flattening = forwardRates.map((r, i) => r - i * 0.08)

    scenarioCurvesChart = new Chart(scenarioCurvesRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: tenors,
        datasets: [
          {
            label: 'Current Curve',
            data: forwardRates,
            borderColor: '#60a5fa',
            backgroundColor: 'transparent',
            tension: 0.4,
            pointRadius: 3,
            borderWidth: 2
          },
          {
            label: 'Bulk +100bp',
            data: bulkShift,
            borderColor: '#4ade80',
            backgroundColor: 'transparent',
            tension: 0.4,
            pointRadius: 0,
            borderDash: [5, 5],
            borderWidth: 1.5
          },
          {
            label: 'Steepening',
            data: steepening,
            borderColor: '#f59e0b',
            backgroundColor: 'transparent',
            tension: 0.4,
            pointRadius: 0,
            borderDash: [5, 5],
            borderWidth: 1.5
          },
          {
            label: 'Flattening',
            data: flattening,
            borderColor: '#f87171',
            backgroundColor: 'transparent',
            tension: 0.4,
            pointRadius: 0,
            borderDash: [5, 5],
            borderWidth: 1.5
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: 'rgba(255,255,255,0.6)' } } },
        scales: {
          x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(255,255,255,0.3)' } }
        }
      }
    } as any)
  }
}

onMounted(() => {
  initCharts()
})

onBeforeUnmount(() => {
  if (forwardCurveChart) forwardCurveChart.destroy()
  if (spreadChart) spreadChart.destroy()
  if (scenarioCurvesChart) scenarioCurvesChart.destroy()
})
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.forward-curve-page {
  width: 100%;
  padding: 24px;
  background: linear-gradient(180deg, rgba(15,20,25,0.5) 0%, rgba(26,31,46,0.3) 100%);
  color: #fff;
  min-height: 100vh;
}

/* ============================================
   HEADER
   ============================================ */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  gap: 24px;
  flex-wrap: wrap;
}

.header-left {
  flex: 1;
  min-width: 300px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  letter-spacing: -0.01em;
}

.page-subtitle {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255,255,255,0.04);
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.08);
}

.control-label {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.instrument-select,
.curve-type-select {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  padding: 4px 8px;
  cursor: pointer;
}

.instrument-select option,
.curve-type-select option {
  background: #1e1f28;
  color: #fff;
}

.btn-secondary {
  padding: 8px 16px;
  background: rgba(255,255,255,0.1);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-secondary:hover {
  background: rgba(255,255,255,0.15);
  border-color: rgba(255,255,255,0.3);
}

/* ============================================
   GRID LAYOUTS
   ============================================ */
.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.full-width {
  grid-column: 1 / -1;
}

/* ============================================
   CARDS
   ============================================ */
.card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s;
  margin-bottom: 20px;
}

.card:hover {
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.card-header {
  margin-bottom: 16px;
}

.card-header h3 {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.card-subtitle {
  font-size: 11px;
  color: rgba(255,255,255,0.4);
  display: block;
  margin-top: 4px;
  font-weight: normal;
  text-transform: none;
  letter-spacing: 0;
}

/* ============================================
   MARKET DATA TABLE
   ============================================ */
.market-data-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.data-table-wrapper {
  overflow-x: auto;
}

.market-data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.market-data-table th,
.market-data-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.market-data-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 10px;
}

.col-tenor {
  text-align: left;
  color: rgba(255,255,255,0.7);
}

.input-small {
  width: 80px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  padding: 4px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-family: "SF Mono", monospace;
}

.input-small:focus {
  outline: none;
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.05);
}

.btn-remove {
  background: rgba(248, 113, 113, 0.2);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #f87171;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-remove:hover {
  background: rgba(248, 113, 113, 0.3);
}

.btn-add-point {
  align-self: flex-start;
  padding: 8px 16px;
  background: rgba(74, 222, 128, 0.2);
  border: 1px solid rgba(74, 222, 128, 0.3);
  color: #4ade80;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add-point:hover {
  background: rgba(74, 222, 128, 0.3);
}

/* ============================================
   METRIC CARDS
   ============================================ */
.metric-card {
  background: rgba(30, 32, 40, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-header {
  margin-bottom: 8px;
}

.metric-header h3 {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  margin: 0;
}

.metric-unit {
  font-size: 10px;
  color: rgba(255,255,255,0.3);
  display: block;
  margin-top: 4px;
}

.metric-value {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.metric-value.positive {
  color: #4ade80;
}

.metric-value.negative {
  color: #f87171;
}

.metric-value.accent {
  color: #f59e0b;
}

.metric-value.blue {
  color: #60a5fa;
}

.metric-detail {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: rgba(255,255,255,0.4);
}

/* ============================================
   CHARTS
   ============================================ */
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  flex-direction: column;
  gap: 4px;
}

.chart-header h3 {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  margin: 0;
}

.chart-subtitle {
  font-size: 10px;
  color: rgba(255,255,255,0.3);
  font-weight: normal;
}

.chart-container {
  position: relative;
  width: 100%;
  height: 360px;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(107, 114, 128, 0.08);
}

.chart-container.tall {
  height: 480px;
}

.chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

/* ============================================
   FORWARD RATES TABLE
   ============================================ */
.forward-rates-table-container {
  overflow-x: auto;
}

.forward-rates-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.forward-rates-table th,
.forward-rates-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.forward-rates-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 10px;
}

.period-name {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
}

.rate-value {
  font-family: "SF Mono", monospace;
  font-weight: 600;
}

.rate-value.cyan {
  color: #06b6d4;
}

.rate-value.blue {
  color: #60a5fa;
}

.rate-value.positive {
  color: #4ade80;
}

.rate-value.negative {
  color: #f87171;
}

.forward-rates-table tr.outlier {
  background: rgba(248, 113, 113, 0.05);
}

/* ============================================
   INTERPOLATION OPTIONS
   ============================================ */
.interpolation-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px;
  background: rgba(255,255,255,0.02);
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.05);
  cursor: pointer;
  transition: all 0.2s;
}

.option-item:hover {
  background: rgba(255,255,255,0.04);
  border-color: rgba(255,255,255,0.1);
}

.radio-input {
  margin-top: 2px;
  cursor: pointer;
}

.option-label {
  display: flex;
  flex-direction: column;
  gap: 3px;
  cursor: pointer;
}

.method-name {
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

.method-desc {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
}

/* ============================================
   PARAMETERS LIST
   ============================================ */
.parameters-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.param-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.param-item .label {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
  min-width: 140px;
}

.param-input {
  flex: 1;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-family: "SF Mono", monospace;
}

.param-input:focus {
  outline: none;
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.05);
}

/* ============================================
   PCA ANALYSIS
   ============================================ */
.pca-analysis {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pca-component {
  display: flex;
  align-items: center;
  gap: 12px;
}

.component-label {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
  min-width: 100px;
}

.contribution-bar {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.05);
  border-radius: 2px;
  overflow: hidden;
}

.bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 2px;
}

.contribution-value {
  font-size: 10px;
  font-weight: 600;
  font-family: "SF Mono", monospace;
  color: rgba(255,255,255,0.6);
  min-width: 35px;
  text-align: right;
}

/* ============================================
   BUTTERFLY METRICS
   ============================================ */
.butterfly-metrics {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.butterfly-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.butterfly-item .label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.butterfly-item .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.butterfly-item .value.accent {
  color: #f59e0b;
}

.butterfly-item .value.blue {
  color: #60a5fa;
}

.butterfly-item .value.positive {
  color: #4ade80;
}

.butterfly-item .value.negative {
  color: #f87171;
}

/* ============================================
   FITTING STATS
   ============================================ */
.fitting-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
  text-transform: uppercase;
}

.stat-value {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.quality-bar {
  height: 6px;
  background: rgba(255,255,255,0.05);
  border-radius: 2px;
  overflow: hidden;
}

.quality-fill {
  height: 100%;
  background: linear-gradient(90deg, #4ade80, #22c55e);
  border-radius: 2px;
  transition: width 0.3s;
}

/* ============================================
   DETAILED STATS TABLE
   ============================================ */
.detailed-stats-container {
  overflow-x: auto;
}

.detailed-stats-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

.detailed-stats-table th,
.detailed-stats-table td {
  padding: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.detailed-stats-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
}

.tenor {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
}

.rate {
  font-family: "SF Mono", monospace;
  color: rgba(255,255,255,0.7);
}

/* ============================================
   FOOTER
   ============================================ */
.page-footer {
  display: flex;
  gap: 16px;
  justify-content: center;
  font-size: 11px;
  color: rgba(255,255,255,0.3);
  margin-top: 24px;
  flex-wrap: wrap;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .page-header {
    flex-direction: column;
  }

  .header-right {
    width: 100%;
    flex-direction: column;
  }

  .control-group {
    width: 100%;
  }

  .grid-2,
  .grid-3 {
    grid-template-columns: 1fr;
  }

  .fitting-stats {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .forward-curve-page {
    padding: 16px;
  }

  .market-data-table,
  .forward-rates-table,
  .detailed-stats-table {
    font-size: 9px;
  }

  .market-data-table th,
  .market-data-table td,
  .forward-rates-table th,
  .forward-rates-table td,
  .detailed-stats-table th,
  .detailed-stats-table td {
    padding: 6px;
  }

  .chart-container {
    height: 300px;
  }

  .chart-container.tall {
    height: 400px;
  }
}
</style>
