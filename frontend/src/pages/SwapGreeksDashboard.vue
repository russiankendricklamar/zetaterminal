<!-- src/pages/SwapGreeksDashboard.vue -->
<template>
  <div class="swap-greeks-page">
    
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Панель греков свопов</h1>
        <p class="page-subtitle">Анализ чувствительности swap-портфеля к рыночным факторам</p>
      </div>
      
      <div class="header-right">
        <!-- Swap Type Filter -->
        <div class="control-group">
          <label class="control-label">Тип свопа:</label>
          <select v-model="selectedSwapType" class="swap-select">
            <option value="all">Все свопы</option>
            <option value="irs">Interest Rate Swaps</option>
            <option value="cds">Credit Default Swaps</option>
            <option value="basis">Basis Swaps</option>
            <option value="cross-currency">Cross-Currency Swaps</option>
          </select>
        </div>

        <!-- Currency/Index -->
        <div class="control-group">
          <label class="control-label">Индекс:</label>
          <select v-model="selectedIndex" class="index-select">
            <option value="usd3m">USD 3M SOFR</option>
            <option value="usd6m">USD 6M LIBOR</option>
            <option value="eur3m">EUR 3M EURIBOR</option>
            <option value="gbp6m">GBP 6M SONIA</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Greeks Overview Cards -->
    <div class="greeks-overview">
      <div class="greek-card dv01">
        <div class="greek-header">
          <span class="greek-symbol">ΔV01</span>
          <span class="greek-name">DV01</span>
        </div>
        <div class="greek-content">
          <div class="greek-value">{{ formatCurrency(swapGreeks.dv01) }}</div>
          <div class="greek-unit">М / 1bp</div>
          <div class="greek-change" :class="swapGreeks.dv01 >= 0 ? 'positive' : 'negative'">
            {{ swapGreeks.dv01 >= 0 ? '+' : '' }}{{ formatCompactCurrency(swapGreeks.dv01) }}
          </div>
        </div>
        <div class="greek-bar">
          <div class="bar-fill" :style="{ width: Math.min(100, Math.abs(swapGreeks.dv01 / 50000)) + '%' }"></div>
        </div>
      </div>

      <div class="greek-card spread-dv01">
        <div class="greek-header">
          <span class="greek-symbol">Δ Spread</span>
          <span class="greek-name">Spread DV01</span>
        </div>
        <div class="greek-content">
          <div class="greek-value">{{ formatCurrency(swapGreeks.spreadDv01) }}</div>
          <div class="greek-unit">М / 1bp</div>
          <div class="greek-change" :class="swapGreeks.spreadDv01 >= 0 ? 'positive' : 'negative'">
            {{ swapGreeks.spreadDv01 >= 0 ? '+' : '' }}{{ formatCompactCurrency(swapGreeks.spreadDv01) }}
          </div>
        </div>
        <div class="greek-bar">
          <div class="bar-fill" :style="{ width: Math.min(100, Math.abs(swapGreeks.spreadDv01 / 30000)) + '%' }"></div>
        </div>
      </div>

      <div class="greek-card basis-risk">
        <div class="greek-header">
          <span class="greek-symbol">Δ Basis</span>
          <span class="greek-name">Basis Risk</span>
        </div>
        <div class="greek-content">
          <div class="greek-value">{{ formatCurrency(swapGreeks.basisRisk) }}</div>
          <div class="greek-unit">М / 1bp</div>
          <div class="greek-change" :class="swapGreeks.basisRisk >= 0 ? 'positive' : 'negative'">
            {{ swapGreeks.basisRisk >= 0 ? '+' : '' }}{{ formatCompactCurrency(swapGreeks.basisRisk) }}
          </div>
        </div>
        <div class="greek-bar">
          <div class="bar-fill" :style="{ width: Math.min(100, Math.abs(swapGreeks.basisRisk / 20000)) + '%' }"></div>
        </div>
      </div>

      <div class="greek-card convexity">
        <div class="greek-header">
          <span class="greek-symbol">Γ</span>
          <span class="greek-name">Convexity</span>
        </div>
        <div class="greek-content">
          <div class="greek-value">{{ swapGreeks.convexity.toFixed(2) }}</div>
          <div class="greek-unit">М / bp²</div>
          <div class="greek-change" :class="swapGreeks.convexity >= 0 ? 'positive' : 'negative'">
            {{ swapGreeks.convexity >= 0 ? '+' : '' }}{{ swapGreeks.convexity.toFixed(2) }}
          </div>
        </div>
        <div class="greek-bar">
          <div class="bar-fill" :style="{ width: Math.min(100, Math.abs(swapGreeks.convexity * 20)) + '%' }"></div>
        </div>
      </div>

      <div class="greek-card vol-exposure">
        <div class="greek-header">
          <span class="greek-symbol">V</span>
          <span class="greek-name">Vol Exposure</span>
        </div>
        <div class="greek-content">
          <div class="greek-value">{{ formatCurrency(swapGreeks.volExposure) }}</div>
          <div class="greek-unit">М / 1% vol</div>
          <div class="greek-change" :class="swapGreeks.volExposure >= 0 ? 'positive' : 'negative'">
            {{ swapGreeks.volExposure >= 0 ? '+' : '' }}{{ formatCompactCurrency(swapGreeks.volExposure) }}
          </div>
        </div>
        <div class="greek-bar">
          <div class="bar-fill" :style="{ width: Math.min(100, Math.abs(swapGreeks.volExposure / 40000)) + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- Key Rate Durations -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Key Rate Durations (КРД)</h3>
        <span class="card-subtitle">Чувствительность по сроках кривой</span>
      </div>
      <div class="krd-container">
        <div v-for="(duration, tenor) in keyRateDurations" :key="tenor" class="krd-item">
          <span class="krd-tenor">{{ tenor }}</span>
          <div class="krd-bar-container">
            <div 
              class="krd-bar"
              :class="duration >= 0 ? 'positive' : 'negative'"
              :style="{ width: Math.min(100, Math.abs(duration * 15)) + '%' }"
            />
          </div>
          <span class="krd-value" :class="duration >= 0 ? 'positive' : 'negative'">
            {{ duration >= 0 ? '+' : '' }}{{ duration.toFixed(2) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Swap Positions Greeks -->
    <div class="grid-2">
      <!-- Long Positions -->
      <div class="card">
        <div class="card-header">
          <h3>Long позиции (Payer)</h3>
        </div>
        <div class="swap-positions">
          <div v-for="position in longPositions" :key="position.id" class="swap-item">
            <div class="swap-header">
              <span class="swap-name">{{ position.name }}</span>
              <span class="swap-tenor">{{ position.tenor }}</span>
              <span class="swap-status" :class="position.direction.toLowerCase()">{{ position.direction }}</span>
            </div>
            <div class="swap-metrics">
              <div class="metric">
                <span class="label">DV01</span>
                <span class="value" :class="position.dv01 >= 0 ? 'positive' : 'negative'">
                  {{ formatCompactCurrency(position.dv01) }}
                </span>
              </div>
              <div class="metric">
                <span class="label">Spread</span>
                <span class="value" :class="position.spread >= 0 ? 'positive' : 'negative'">
                  {{ position.spread >= 0 ? '+' : '' }}{{ position.spread }} bp
                </span>
              </div>
              <div class="metric">
                <span class="label">Notional</span>
                <span class="value mono">{{ formatCurrency(position.notional) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Short Positions -->
      <div class="card">
        <div class="card-header">
          <h3>Short позиции (Receiver)</h3>
        </div>
        <div class="swap-positions">
          <div v-for="position in shortPositions" :key="position.id" class="swap-item">
            <div class="swap-header">
              <span class="swap-name">{{ position.name }}</span>
              <span class="swap-tenor">{{ position.tenor }}</span>
              <span class="swap-status" :class="position.direction.toLowerCase()">{{ position.direction }}</span>
            </div>
            <div class="swap-metrics">
              <div class="metric">
                <span class="label">DV01</span>
                <span class="value" :class="position.dv01 >= 0 ? 'positive' : 'negative'">
                  {{ formatCompactCurrency(position.dv01) }}
                </span>
              </div>
              <div class="metric">
                <span class="label">Spread</span>
                <span class="value" :class="position.spread >= 0 ? 'positive' : 'negative'">
                  {{ position.spread >= 0 ? '+' : '' }}{{ position.spread }} bp
                </span>
              </div>
              <div class="metric">
                <span class="label">Notional</span>
                <span class="value mono">{{ formatCurrency(position.notional) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Par Curve vs Spot Curve -->
    <div class="grid-2">
      <!-- Rate Curve -->
      <div class="card">
        <div class="chart-header">
          <h3>Кривая свопов</h3>
        </div>
        <div class="chart-container">
          <canvas ref="curveChartRef"></canvas>
        </div>
      </div>

      <!-- Spread Curve -->
      <div class="card">
        <div class="chart-header">
          <h3>Кривая спреда (Par - Spot)</h3>
        </div>
        <div class="chart-container">
          <canvas ref="spreadChartRef"></canvas>
        </div>
      </div>
    </div>

    <!-- DV01 Sensitivity Analysis -->
    <div class="grid-2">
      <!-- Rate Sensitivity -->
      <div class="card">
        <div class="chart-header">
          <h3>Чувствительность DV01 (Rate Shock)</h3>
        </div>
        <div class="chart-container">
          <canvas ref="rateSensitivityRef"></canvas>
        </div>
      </div>

      <!-- Spread Sensitivity -->
      <div class="card">
        <div class="chart-header">
          <h3>Чувствительность спреда (Spread Shock)</h3>
        </div>
        <div class="chart-container">
          <canvas ref="spreadSensitivityRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Scenario Analysis -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Матрица сценариев (P&L)</h3>
        <span class="card-subtitle">Чувствительность к комбинированным шокам</span>
      </div>
      <div class="scenario-container">
        <table class="scenario-table">
          <thead>
            <tr>
              <th>Сценарий</th>
              <th>Rate +50bp</th>
              <th>Rate +100bp</th>
              <th>Rate -50bp</th>
              <th>Rate -100bp</th>
              <th>Spread +50bp</th>
              <th>Spread -50bp</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="scenario in scenarioMatrix" :key="scenario.name">
              <td class="scenario-name">{{ scenario.name }}</td>
              <td :class="getPnlClass(scenario.rate50)">{{ formatCurrency(scenario.rate50) }}</td>
              <td :class="getPnlClass(scenario.rate100)">{{ formatCurrency(scenario.rate100) }}</td>
              <td :class="getPnlClass(scenario.rateNeg50)">{{ formatCurrency(scenario.rateNeg50) }}</td>
              <td :class="getPnlClass(scenario.rateNeg100)">{{ formatCurrency(scenario.rateNeg100) }}</td>
              <td :class="getPnlClass(scenario.spread50)">{{ formatCurrency(scenario.spread50) }}</td>
              <td :class="getPnlClass(scenario.spreadNeg50)">{{ formatCurrency(scenario.spreadNeg50) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Basis Risk Analysis -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Риск базиса (3M vs 6M LIBOR)</h3>
        <span class="card-subtitle">Риск от расходимости между индексами</span>
      </div>
      <div class="basis-analysis">
        <div class="basis-item">
          <span class="basis-label">Текущий спред базиса</span>
          <span class="basis-value accent">{{ basisAnalysis.currentSpread }} bp</span>
        </div>
        <div class="basis-item">
          <span class="basis-label">Basis DV01</span>
          <span class="basis-value" :class="basisAnalysis.basisDv01 >= 0 ? 'positive' : 'negative'">
            {{ formatCompactCurrency(basisAnalysis.basisDv01) }}
          </span>
        </div>
        <div class="basis-item">
          <span class="basis-label">Волатильность базиса</span>
          <span class="basis-value">{{ basisAnalysis.basVol }}%</span>
        </div>
        <div class="basis-item">
          <span class="basis-label">P&L (Spread +25bp)</span>
          <span class="basis-value" :class="basisAnalysis.pnlSpread25 >= 0 ? 'positive' : 'negative'">
            {{ formatCurrency(basisAnalysis.pnlSpread25) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span>• DV01 — стоимость 1 базисного пункта в долларах</span>
      <span>• Spread DV01 — чувствительность к спредам</span>
      <span>• Обновление каждые 5 минут</span>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'

const selectedSwapType = ref('all')
const selectedIndex = ref('usd3m')

// Swap Greeks Data
const swapGreeks = ref({
  dv01: 125000,           // Dollar Value of 1bp
  spreadDv01: 85000,      // Spread sensitivity
  basisRisk: 42000,       // Basis swap risk
  convexity: 2.15,        // Convexity (higher order effect)
  volExposure: 55000      // Swaption-like exposure
})

// Key Rate Durations
const keyRateDurations = ref({
  '2Y': -1.25,
  '3Y': -2.15,
  '5Y': -3.85,
  '7Y': -2.95,
  '10Y': -1.85,
  '15Y': -0.95,
  '20Y': -0.35,
  '30Y': 0.05
})

// Long Positions (Payer)
const longPositions = ref([
  {
    id: 1,
    name: 'IRS Payer',
    tenor: '5Y',
    direction: 'Payer',
    dv01: -145000,
    spread: 25,
    notional: 100_000_000
  },
  {
    id: 2,
    name: 'IRS Payer',
    tenor: '10Y',
    direction: 'Payer',
    dv01: -185000,
    spread: 35,
    notional: 150_000_000
  },
  {
    id: 3,
    name: 'CDS Protection Buyer',
    tenor: '5Y',
    direction: 'Payer',
    dv01: -32000,
    spread: 85,
    notional: 50_000_000
  }
])

// Short Positions (Receiver)
const shortPositions = ref([
  {
    id: 4,
    name: 'IRS Receiver',
    tenor: '2Y',
    direction: 'Receiver',
    dv01: 45000,
    spread: 15,
    notional: 75_000_000
  },
  {
    id: 5,
    name: 'IRS Receiver',
    tenor: '7Y',
    direction: 'Receiver',
    dv01: 95000,
    spread: 28,
    notional: 120_000_000
  },
  {
    id: 6,
    name: 'Basis Swap',
    tenor: '5Y',
    direction: 'Receiver',
    dv01: 32000,
    spread: 12,
    notional: 80_000_000
  }
])

// Scenario Matrix
const scenarioMatrix = ref([
  {
    name: 'Bear (Rates Up)',
    rate50: -62500,
    rate100: -125000,
    rateNeg50: 62500,
    rateNeg100: 125000,
    spread50: -42500,
    spreadNeg50: 42500
  },
  {
    name: 'Bull (Rates Down)',
    rate50: 62500,
    rate100: 125000,
    rateNeg50: -62500,
    rateNeg100: -125000,
    spread50: 42500,
    spreadNeg50: -42500
  },
  {
    name: 'Steepening',
    rate50: 35000,
    rate100: 52000,
    rateNeg50: -35000,
    rateNeg100: -52000,
    spread50: 15000,
    spreadNeg50: -15000
  },
  {
    name: 'Flattening',
    rate50: -28000,
    rate100: -45000,
    rateNeg50: 28000,
    rateNeg100: 45000,
    spread50: -12000,
    spreadNeg50: 12000
  }
])

// Basis Risk Analysis
const basisAnalysis = ref({
  currentSpread: 18,      // bp
  basisDv01: 42000,      // М
  basVol: 8.5,            // %
  pnlSpread25: -10500    // М (negative = loss when spread widens)
})

// Chart References
const curveChartRef = ref<HTMLCanvasElement | null>(null)
const spreadChartRef = ref<HTMLCanvasElement | null>(null)
const rateSensitivityRef = ref<HTMLCanvasElement | null>(null)
const spreadSensitivityRef = ref<HTMLCanvasElement | null>(null)

let curveChart: Chart | null = null
let spreadChart: Chart | null = null
let rateSensitivityChart: Chart | null = null
let spreadSensitivityChart: Chart | null = null

// Methods
const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(val)
}

const formatCompactCurrency = (val: number) => {
  if (Math.abs(val) >= 1_000_000) {
    return (val / 1_000_000).toFixed(1) + 'М'
  }
  return '$' + (val / 1000).toFixed(0) + 'K'
}

const getPnlClass = (val: number) => {
  if (val > 0) return 'pnl-positive'
  if (val < 0) return 'pnl-negative'
  return 'pnl-neutral'
}

const initCharts = () => {
  if (curveChart) curveChart.destroy()
  if (spreadChart) spreadChart.destroy()
  if (rateSensitivityChart) rateSensitivityChart.destroy()
  if (spreadSensitivityChart) spreadSensitivityChart.destroy()

  // Swap Curve
  if (curveChartRef.value?.getContext('2d')) {
    curveChart = new Chart(curveChartRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: ['2Y', '3Y', '5Y', '7Y', '10Y', '15Y', '20Y', '30Y'],
        datasets: [
          {
            label: 'Par Curve',
            data: [4.85, 4.75, 4.65, 4.58, 4.42, 4.35, 4.32, 4.28],
            borderColor: '#60a5fa',
            backgroundColor: 'rgba(96, 165, 250, 0.08)',
            fill: false,
            tension: 0.4,
            pointRadius: 4,
            borderWidth: 2
          },
          {
            label: 'Spot Curve',
            data: [4.78, 4.68, 4.55, 4.48, 4.32, 4.25, 4.22, 4.18],
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.08)',
            fill: false,
            tension: 0.4,
            pointRadius: 4,
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

  // Spread Curve
  if (spreadChartRef.value?.getContext('2d')) {
    spreadChart = new Chart(spreadChartRef.value.getContext('2d') as any, {
      type: 'bar',
      data: {
        labels: ['2Y', '3Y', '5Y', '7Y', '10Y', '15Y', '20Y', '30Y'],
        datasets: [{
          label: 'Par - Spot (bp)',
          data: [7, 7, 10, 10, 10, 10, 10, 10],
          backgroundColor: 'rgba(96, 165, 250, 0.6)',
          borderColor: '#60a5fa',
          borderWidth: 1
        }]
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

  // Rate Sensitivity
  if (rateSensitivityRef.value?.getContext('2d')) {
    rateSensitivityChart = new Chart(rateSensitivityRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: ['-100bp', '-50bp', '0bp', '+50bp', '+100bp', '+150bp', '+200bp'],
        datasets: [{
          label: 'Portfolio P&L',
          data: [250000, 125000, 0, -125000, -250000, -375000, -500000],
          borderColor: '#60a5fa',
          backgroundColor: 'rgba(96, 165, 250, 0.08)',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          borderWidth: 2
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

  // Spread Sensitivity
  if (spreadSensitivityRef.value?.getContext('2d')) {
    spreadSensitivityChart = new Chart(spreadSensitivityRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: ['-50bp', '-25bp', '0bp', '+25bp', '+50bp', '+75bp', '+100bp'],
        datasets: [{
          label: 'Portfolio P&L',
          data: [212500, 106250, 0, -106250, -212500, -318750, -425000],
          borderColor: '#38bdf8',
          backgroundColor: 'rgba(56, 189, 248, 0.08)',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          borderWidth: 2
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
}

onMounted(() => {
  setTimeout(() => initCharts(), 100)
})

onBeforeUnmount(() => {
  if (curveChart) curveChart.destroy()
  if (spreadChart) spreadChart.destroy()
  if (rateSensitivityChart) rateSensitivityChart.destroy()
  if (spreadSensitivityChart) spreadSensitivityChart.destroy()
})
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.swap-greeks-page {
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

.swap-select,
.index-select {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  padding: 4px 8px;
  cursor: pointer;
  max-width: 150px;
}

.swap-select option,
.index-select option {
  background: #1e1f28;
  color: #fff;
}

/* ============================================
   GREEKS OVERVIEW GRID
   ============================================ */
.greeks-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.greek-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}

.greek-card:hover {
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.greek-card.dv01 { border-top: 2px solid #60a5fa; }
.greek-card.spread-dv01 { border-top: 2px solid #38bdf8; }
.greek-card.basis-risk { border-top: 2px solid #f59e0b; }
.greek-card.convexity { border-top: 2px solid #4ade80; }
.greek-card.vol-exposure { border-top: 2px solid #c084fc; }

.greek-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.greek-symbol {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.greek-name {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
}

.greek-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

.greek-value {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.greek-unit {
  font-size: 9px;
  color: rgba(255,255,255,0.3);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.greek-change {
  font-size: 10px;
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.greek-change.positive {
  color: #4ade80;
}

.greek-change.negative {
  color: #f87171;
}

.greek-bar {
  height: 4px;
  background: rgba(255,255,255,0.05);
  border-radius: 2px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* ============================================
   CARDS
   ============================================ */
.card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 
    0 20px 40px -10px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
  margin-bottom: 20px;
}

.card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
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

.full-width {
  grid-column: 1 / -1;
}

.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

/* ============================================
   KRD CONTAINER
   ============================================ */
.krd-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(70px, 1fr));
  gap: 12px;
}

.krd-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.krd-tenor {
  font-size: 10px;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
}

.krd-bar-container {
  width: 100%;
  height: 4px;
  background: rgba(255,255,255,0.05);
  border-radius: 2px;
  overflow: hidden;
}

.krd-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s;
}

.krd-bar.positive {
  background: #4ade80;
}

.krd-bar.negative {
  background: #f87171;
}

.krd-value {
  font-size: 10px;
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.krd-value.positive {
  color: #4ade80;
}

.krd-value.negative {
  color: #f87171;
}

/* ============================================
   SWAP POSITIONS
   ============================================ */
.swap-positions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.swap-item {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  padding: 12px;
}

.swap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.swap-name {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.swap-tenor {
  font-size: 10px;
  background: rgba(255,255,255,0.05);
  padding: 2px 8px;
  border-radius: 4px;
  color: rgba(255,255,255,0.6);
}

.swap-status {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.swap-status.payer {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.swap-status.receiver {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

.swap-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric .label {
  font-size: 9px;
  color: rgba(255,255,255,0.4);
  text-transform: uppercase;
  font-weight: 600;
}

.metric .value {
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.metric .value.positive {
  color: #4ade80;
}

.metric .value.negative {
  color: #f87171;
}

.mono {
  font-family: "SF Mono", monospace;
}

/* ============================================
   CHARTS
   ============================================ */
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chart-header h3 {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
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

.chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

/* ============================================
   SCENARIO TABLE
   ============================================ */
.scenario-container {
  overflow-x: auto;
}

.scenario-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.scenario-table th,
.scenario-table td {
  padding: 10px;
  border: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.scenario-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 10px;
}

.scenario-name {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 500;
}

.pnl-positive {
  color: #4ade80;
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.pnl-negative {
  color: #f87171;
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.pnl-neutral {
  color: rgba(255,255,255,0.5);
  font-family: "SF Mono", monospace;
}

/* ============================================
   BASIS ANALYSIS
   ============================================ */
.basis-analysis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.basis-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255,255,255,0.02);
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.05);
}

.basis-label {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
}

.basis-value {
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.basis-value.accent {
  color: #38bdf8;
}

.basis-value.positive {
  color: #4ade80;
}

.basis-value.negative {
  color: #f87171;
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

  .grid-2 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .swap-greeks-page {
    padding: 16px;
  }

  .page-header {
    gap: 16px;
  }

  .greeks-overview {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-container {
    height: 300px;
  }

  .krd-container {
    grid-template-columns: repeat(4, 1fr);
  }

  .swap-metrics {
    grid-template-columns: 1fr;
  }

  .scenario-table th,
  .scenario-table td {
    padding: 6px;
    font-size: 10px;
  }

  .basis-analysis {
    grid-template-columns: 1fr;
  }
}
</style>
