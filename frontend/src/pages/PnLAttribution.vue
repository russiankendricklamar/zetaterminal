<!-- src/pages/PnLAttribution.vue -->
<template>
  <div class="pnl-attribution-page">
    
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">P&L Attribution</h1>
        <p class="page-subtitle">Разложение прибыли по источникам и факторам риска</p>
      </div>
      
      <div class="header-right">
        <!-- Time Period Selector -->
        <div class="control-group">
          <label class="control-label">Период:</label>
          <select v-model="selectedPeriod" class="period-select" @change="updateAttribution">
            <option value="day">Сегодня</option>
            <option value="week">Неделя</option>
            <option value="month">Месяц</option>
            <option value="ytd">YTD</option>
            <option value="year">Год</option>
          </select>
        </div>

        <!-- Attribution Method -->
        <div class="control-group">
          <label class="control-label">Метод:</label>
          <select v-model="selectedMethod" class="method-select" @change="updateAttribution">
            <option value="greeks">Greeks Decomposition</option>
            <option value="riskfactors">Risk Factors</option>
            <option value="positions">By Position</option>
          </select>
        </div>

        <!-- Export Button -->
        <button @click="exportData" class="btn-secondary">
          📥 Экспортировать
        </button>
      </div>
    </div>

    <!-- Total P&L Summary -->
    <div class="pnl-summary">
      <div class="summary-card total">
        <div class="summary-label">Total P&L</div>
        <div class="summary-value" :class="totalPnL >= 0 ? 'positive' : 'negative'">
          {{ formatCurrency(totalPnL) }}
        </div>
        <div class="summary-change">
          {{ ((totalPnL / Math.abs(totalPnL || 1)) > 0 ? '↑' : '↓') }} 
          {{ Math.abs(percentageChange).toFixed(2) }}%
        </div>
      </div>

      <div class="summary-card">
        <div class="summary-label">Market P&L</div>
        <div class="summary-value accent">
          {{ formatCurrency(pnlComponents.market) }}
        </div>
        <div class="summary-change">
          {{ (pnlComponents.market / totalPnL * 100).toFixed(1) }}% of total
        </div>
      </div>

      <div class="summary-card">
        <div class="summary-label">Theta (Time Decay)</div>
        <div class="summary-value" :class="pnlComponents.theta >= 0 ? 'positive' : 'negative'">
          {{ formatCurrency(pnlComponents.theta) }}
        </div>
        <div class="summary-change">
          {{ (pnlComponents.theta / totalPnL * 100).toFixed(1) }}% of total
        </div>
      </div>

      <div class="summary-card">
        <div class="summary-label">Gamma P&L</div>
        <div class="summary-value" :class="pnlComponents.gamma >= 0 ? 'positive' : 'negative'">
          {{ formatCurrency(pnlComponents.gamma) }}
        </div>
        <div class="summary-change">
          {{ (pnlComponents.gamma / totalPnL * 100).toFixed(1) }}% of total
        </div>
      </div>

      <div class="summary-card">
        <div class="summary-label">Vega P&L</div>
        <div class="summary-value" :class="pnlComponents.vega >= 0 ? 'positive' : 'negative'">
          {{ formatCurrency(pnlComponents.vega) }}
        </div>
        <div class="summary-change">
          {{ (pnlComponents.vega / totalPnL * 100).toFixed(1) }}% of total
        </div>
      </div>
    </div>

    <!-- P&L Breakdown Charts -->
    <div class="grid-2">
      <!-- Pie Chart: Composition -->
      <div class="card">
        <div class="chart-header">
          <h3>P&L Composition</h3>
          <span class="chart-subtitle">Доля каждого компонента</span>
        </div>
        <div class="chart-container">
          <canvas ref="compositionChartRef"></canvas>
        </div>
      </div>

      <!-- Bar Chart: Components Over Time -->
      <div class="card">
        <div class="chart-header">
          <h3>Daily P&L Attribution</h3>
          <span class="chart-subtitle">Разложение по дням</span>
        </div>
        <div class="chart-container">
          <canvas ref="dailyAttributionRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Detailed Attribution Table -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Детальное разложение P&L</h3>
        <span class="card-subtitle">Greeks & Risk Factor Attribution</span>
      </div>
      <div class="table-container">
        <table class="attribution-table">
          <thead>
            <tr>
              <th class="col-component">Компонент</th>
              <th class="col-amount">Amount (М USD)</th>
              <th class="col-percent">% of Total</th>
              <th class="col-description">Описание</th>
              <th class="col-bucket">Категория</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in attributionDetails" :key="item.id" :class="item.type">
              <td class="col-component">{{ item.component }}</td>
              <td class="col-amount" :class="item.amount >= 0 ? 'positive' : 'negative'">
                {{ item.amount >= 0 ? '+' : '' }}{{ formatCompactCurrency(item.amount) }}
              </td>
              <td class="col-percent mono">{{ (item.percentage).toFixed(1) }}%</td>
              <td class="col-description">{{ item.description }}</td>
              <td class="col-bucket">{{ item.category }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="total-row">
              <td class="col-component"><strong>TOTAL</strong></td>
              <td class="col-amount" :class="totalPnL >= 0 ? 'positive' : 'negative'">
                <strong>{{ totalPnL >= 0 ? '+' : '' }}{{ formatCompactCurrency(totalPnL) }}</strong>
              </td>
              <td class="col-percent mono"><strong>100.0%</strong></td>
              <td colspan="2"></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Greeks Attribution -->
    <div class="grid-3">
      <!-- Delta P&L -->
      <div class="card">
        <div class="card-header">
          <h3>Δ (Delta) P&L</h3>
          <span class="card-subtitle">Directional risk exposure</span>
        </div>
        <div class="greek-breakdown">
          <div class="breakdown-item">
            <span class="label">Rate moves</span>
            <span class="value" :class="greeksPnL.delta.rates >= 0 ? 'positive' : 'negative'">
              {{ greeksPnL.delta.rates >= 0 ? '+' : '' }}{{ formatCompactCurrency(greeksPnL.delta.rates) }}
            </span>
          </div>
          <div class="breakdown-item">
            <span class="label">Curve shift</span>
            <span class="value" :class="greeksPnL.delta.curve >= 0 ? 'positive' : 'negative'">
              {{ greeksPnL.delta.curve >= 0 ? '+' : '' }}{{ formatCompactCurrency(greeksPnL.delta.curve) }}
            </span>
          </div>
          <div class="breakdown-item">
            <span class="label">Curve twist</span>
            <span class="value" :class="greeksPnL.delta.twist >= 0 ? 'positive' : 'negative'">
              {{ greeksPnL.delta.twist >= 0 ? '+' : '' }}{{ formatCompactCurrency(greeksPnL.delta.twist) }}
            </span>
          </div>
          <div class="breakdown-item total">
            <span class="label">Δ Total</span>
            <span class="value accent">
              {{ greeksPnL.delta.rates + greeksPnL.delta.curve + greeksPnL.delta.twist >= 0 ? '+' : '' }}
              {{ formatCompactCurrency(greeksPnL.delta.rates + greeksPnL.delta.curve + greeksPnL.delta.twist) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Gamma P&L -->
      <div class="card">
        <div class="card-header">
          <h3>Γ (Gamma) P&L</h3>
          <span class="card-subtitle">Convexity gains/losses</span>
        </div>
        <div class="greek-breakdown">
          <div class="breakdown-item">
            <span class="label">Price gamma</span>
            <span class="value" :class="greeksPnL.gamma.price >= 0 ? 'positive' : 'negative'">
              {{ greeksPnL.gamma.price >= 0 ? '+' : '' }}{{ formatCompactCurrency(greeksPnL.gamma.price) }}
            </span>
          </div>
          <div class="breakdown-item">
            <span class="label">Vol gamma</span>
            <span class="value" :class="greeksPnL.gamma.vol >= 0 ? 'positive' : 'negative'">
              {{ greeksPnL.gamma.vol >= 0 ? '+' : '' }}{{ formatCompactCurrency(greeksPnL.gamma.vol) }}
            </span>
          </div>
          <div class="breakdown-item">
            <span class="label">Cross gamma</span>
            <span class="value" :class="greeksPnL.gamma.cross >= 0 ? 'positive' : 'negative'">
              {{ greeksPnL.gamma.cross >= 0 ? '+' : '' }}{{ formatCompactCurrency(greeksPnL.gamma.cross) }}
            </span>
          </div>
          <div class="breakdown-item total">
            <span class="label">Γ Total</span>
            <span class="value blue">
              {{ greeksPnL.gamma.price + greeksPnL.gamma.vol + greeksPnL.gamma.cross >= 0 ? '+' : '' }}
              {{ formatCompactCurrency(greeksPnL.gamma.price + greeksPnL.gamma.vol + greeksPnL.gamma.cross) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Vega & Other -->
      <div class="card">
        <div class="card-header">
          <h3>V (Vega) & Other</h3>
          <span class="card-subtitle">Vol and residual</span>
        </div>
        <div class="greek-breakdown">
          <div class="breakdown-item">
            <span class="label">Vega (vol moves)</span>
            <span class="value" :class="greeksPnL.vega >= 0 ? 'positive' : 'negative'">
              {{ greeksPnL.vega >= 0 ? '+' : '' }}{{ formatCompactCurrency(greeksPnL.vega) }}
            </span>
          </div>
          <div class="breakdown-item">
            <span class="label">Rho (rate/credit)</span>
            <span class="value" :class="greeksPnL.rho >= 0 ? 'positive' : 'negative'">
              {{ greeksPnL.rho >= 0 ? '+' : '' }}{{ formatCompactCurrency(greeksPnL.rho) }}
            </span>
          </div>
          <div class="breakdown-item">
            <span class="label">Other/FX</span>
            <span class="value" :class="greeksPnL.other >= 0 ? 'positive' : 'negative'">
              {{ greeksPnL.other >= 0 ? '+' : '' }}{{ formatCompactCurrency(greeksPnL.other) }}
            </span>
          </div>
          <div class="breakdown-item total">
            <span class="label">V Total</span>
            <span class="value cyan">
              {{ greeksPnL.vega + greeksPnL.rho + greeksPnL.other >= 0 ? '+' : '' }}
              {{ formatCompactCurrency(greeksPnL.vega + greeksPnL.rho + greeksPnL.other) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- P&L Waterfall Chart -->
    <div class="card full-width">
      <div class="chart-header">
        <h3>P&L Waterfall</h3>
        <span class="chart-subtitle">Траектория накопления P&L с начала периода</span>
      </div>
      <div class="chart-container tall">
        <canvas ref="waterfallChartRef"></canvas>
      </div>
    </div>

    <!-- Risk Factor Attribution -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Risk Factor Attribution</h3>
        <span class="card-subtitle">P&L по экономическим факторам</span>
      </div>
      <div class="table-container">
        <table class="risk-factor-table">
          <thead>
            <tr>
              <th>Risk Factor</th>
              <th>Market Move</th>
              <th>Position Exposure</th>
              <th>Implied P&L</th>
              <th>Actual P&L</th>
              <th>Explained %</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="factor in riskFactorAttribution" :key="factor.id">
              <td class="factor-name">{{ factor.name }}</td>
              <td class="move" :class="factor.move >= 0 ? 'positive' : 'negative'">
                {{ factor.move >= 0 ? '+' : '' }}{{ factor.move.toFixed(2) }}
              </td>
              <td class="exposure mono">{{ factor.exposure.toFixed(1) }}</td>
              <td class="pnl" :class="factor.impliedPnL >= 0 ? 'positive' : 'negative'">
                {{ factor.impliedPnL >= 0 ? '+' : '' }}{{ formatCompactCurrency(factor.impliedPnL) }}
              </td>
              <td class="pnl" :class="factor.actualPnL >= 0 ? 'positive' : 'negative'">
                {{ factor.actualPnL >= 0 ? '+' : '' }}{{ formatCompactCurrency(factor.actualPnL) }}
              </td>
              <td class="explained mono">{{ factor.explained.toFixed(1) }}%</td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="total-row">
              <td><strong>TOTAL</strong></td>
              <td colspan="5"></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Unexplained P&L -->
    <div class="grid-2">
      <!-- Unexplained Analysis -->
      <div class="card">
        <div class="card-header">
          <h3>Unexplained P&L</h3>
          <span class="card-subtitle">P&L не объяснённый факторами</span>
        </div>
        <div class="unexplained-metrics">
          <div class="metric-item">
            <span class="label">Total Unexplained</span>
            <span class="value" :class="unexplainedPnL >= 0 ? 'positive' : 'negative'">
              {{ unexplainedPnL >= 0 ? '+' : '' }}{{ formatCompactCurrency(unexplainedPnL) }}
            </span>
          </div>
          <div class="metric-item">
            <span class="label">% of Total P&L</span>
            <span class="value mono">{{ ((Math.abs(unexplainedPnL) / Math.abs(totalPnL)) * 100).toFixed(1) }}%</span>
          </div>
          <div class="metric-item">
            <span class="label">Likely causes</span>
            <ul class="causes-list">
              <li>• Bid-ask spread slippage</li>
              <li>• Execution timing</li>
              <li>• Correlation changes</li>
              <li>• Dividend/coupon accrual</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Top Positions -->
      <div class="card">
        <div class="card-header">
          <h3>Top P&L Contributors</h3>
          <span class="card-subtitle">5 позиций с максимальным вкладом</span>
        </div>
        <div class="top-positions">
          <div v-for="(pos, idx) in topPositions" :key="idx" class="position-item">
            <div class="position-rank">{{ idx + 1 }}</div>
            <div class="position-info">
              <span class="position-name">{{ pos.name }}</span>
              <span class="position-detail">{{ pos.asset }}</span>
            </div>
            <div class="position-pnl" :class="pos.pnl >= 0 ? 'positive' : 'negative'">
              {{ pos.pnl >= 0 ? '+' : '' }}{{ formatCompactCurrency(pos.pnl) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span>• Метод: Greeks Decomposition (DCF-based)</span>
      <span>• Обновление: В реальном времени</span>
      <span>• Базовая валюта: USD</span>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'

const selectedPeriod = ref('day')
const selectedMethod = ref('greeks')

// Main P&L Components
const pnlComponents = ref({
  market: 125400,     // Market moves
  gamma: 28500,       // Convexity
  theta: -12300,      // Time decay
  vega: 18200,        // Vol moves
  other: -5200        // Residual
})

const totalPnL = computed(() => {
  return Object.values(pnlComponents.value).reduce((a, b) => a + b, 0)
})

const percentageChange = computed(() => {
  return (totalPnL.value / 1000000) * 100 // Assuming 1M base
})

// Greeks P&L Breakdown
const greeksPnL = ref({
  delta: {
    rates: 85000,
    curve: 32000,
    twist: 8400
  },
  gamma: {
    price: 22000,
    vol: 5500,
    cross: 1000
  },
  vega: 18200,
  rho: 8500,
  other: -5200
})

// Attribution Details
const attributionDetails = ref([
  {
    id: 1,
    component: 'Δ - Rate Moves (parallel shift)',
    amount: 85000,
    percentage: 32.5,
    description: 'Sensitivity to parallel shift in yield curve',
    category: 'Directional',
    type: 'delta'
  },
  {
    id: 2,
    component: 'Δ - Curve Shift',
    amount: 32000,
    percentage: 12.2,
    description: 'Steepening/Flattening contribution',
    category: 'Directional',
    type: 'delta'
  },
  {
    id: 3,
    component: 'Δ - Curve Twist',
    amount: 8400,
    percentage: 3.2,
    description: 'Butterfly and higher order effects',
    category: 'Directional',
    type: 'delta'
  },
  {
    id: 4,
    component: 'Γ - Price Gamma',
    amount: 22000,
    percentage: 8.4,
    description: 'Rebalancing/convexity gains from rate moves',
    category: 'Convexity',
    type: 'gamma'
  },
  {
    id: 5,
    component: 'Γ - Vol Gamma',
    amount: 5500,
    percentage: 2.1,
    description: 'Vol-related second order effects',
    category: 'Convexity',
    type: 'gamma'
  },
  {
    id: 6,
    component: 'Θ - Theta Decay',
    amount: -12300,
    percentage: -4.7,
    description: 'Time value decay (daily)',
    category: 'Time Value',
    type: 'theta'
  },
  {
    id: 7,
    component: 'V - Vega',
    amount: 18200,
    percentage: 6.9,
    description: 'Volatility level changes',
    category: 'Vol',
    type: 'vega'
  },
  {
    id: 8,
    component: 'ρ - Rho',
    amount: 8500,
    percentage: 3.2,
    description: 'Credit spread and rate correlation moves',
    category: 'Spread',
    type: 'rho'
  },
  {
    id: 9,
    component: 'Other/FX',
    amount: -5200,
    percentage: -2.0,
    description: 'FX moves, dividends, other factors',
    category: 'Other',
    type: 'other'
  }
])

// Risk Factor Attribution
const riskFactorAttribution = ref([
  {
    id: 1,
    name: 'Yield Curve (2Y-10Y)',
    move: 15,
    exposure: 4.25,
    impliedPnL: 63750,
    actualPnL: 68200,
    explained: 96.3
  },
  {
    id: 2,
    name: 'Volatility (Swaption)',
    move: 2.5,
    exposure: 7200,
    impliedPnL: 18000,
    actualPnL: 16800,
    explained: 93.3
  },
  {
    id: 3,
    name: 'Credit Spread (IG)',
    move: -8,
    exposure: -2150,
    impliedPnL: -17200,
    actualPnL: -15600,
    explained: 90.7
  },
  {
    id: 4,
    name: 'EUR/USD FX',
    move: 0.5,
    exposure: 12000,
    impliedPnL: 6000,
    actualPnL: 5800,
    explained: 96.7
  },
  {
    id: 5,
    name: 'Equity Index',
    move: 1.2,
    exposure: 800,
    impliedPnL: 960,
    actualPnL: 850,
    explained: 88.5
  }
])

const unexplainedPnL = computed(() => {
  const explained = riskFactorAttribution.value.reduce((sum, f) => sum + f.actualPnL, 0)
  return totalPnL.value - explained
})

// Top Positions
const topPositions = ref([
  {
    name: 'Long IRS 5Y',
    asset: 'USD SOFR',
    pnl: 85400
  },
  {
    name: 'Short Bonds',
    asset: 'US Treasuries',
    pnl: 42300
  },
  {
    name: 'Long Swaptions',
    asset: 'Payer Swaption 2Yx5Y',
    pnl: 28500
  },
  {
    name: 'CDS Protection',
    asset: 'IG Index',
    pnl: 18200
  },
  {
    name: 'Basis Swap',
    asset: '3M vs 6M',
    pnl: 12000
  }
])

// Chart References
const compositionChartRef = ref<HTMLCanvasElement | null>(null)
const dailyAttributionRef = ref<HTMLCanvasElement | null>(null)
const waterfallChartRef = ref<HTMLCanvasElement | null>(null)

let compositionChart: Chart | null = null
let dailyAttributionChart: Chart | null = null
let waterfallChart: Chart | null = null

// Methods
const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('en-US', {
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

const updateAttribution = () => {
  initCharts()
}

const exportData = () => {
  const csv = [
    ['P&L Attribution Report', selectedPeriod.value],
    [''],
    ['Component', 'Amount', '% of Total'],
    ...attributionDetails.value.map(item => [
      item.component,
      item.amount,
      item.percentage
    ]),
    ['TOTAL', totalPnL.value, '100.0']
  ]
  
  const csvContent = csv.map(row => row.join(',')).join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `pnl-attribution-${new Date().toISOString()}.csv`
  a.click()
}

const initCharts = () => {
  if (compositionChart) compositionChart.destroy()
  if (dailyAttributionChart) dailyAttributionChart.destroy()
  if (waterfallChart) waterfallChart.destroy()

  // Composition Pie Chart
  if (compositionChartRef.value?.getContext('2d')) {
    compositionChart = new Chart(compositionChartRef.value.getContext('2d') as any, {
      type: 'doughnut',
      data: {
        labels: ['Market P&L', 'Gamma', 'Vega', 'Theta', 'Other'],
        datasets: [{
          data: [
            pnlComponents.value.market,
            pnlComponents.value.gamma,
            pnlComponents.value.vega,
            Math.abs(pnlComponents.value.theta),
            Math.abs(pnlComponents.value.other)
          ],
          backgroundColor: [
            'rgba(59, 130, 246, 0.8)',
            'rgba(34, 197, 94, 0.8)',
            'rgba(56, 189, 248, 0.8)',
            'rgba(168, 85, 247, 0.8)',
            'rgba(248, 113, 113, 0.8)'
          ],
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: 'rgba(255,255,255,0.6)' }, position: 'right' }
        }
      }
    } as any)
  }

  // Daily Attribution Bar Chart
  if (dailyAttributionRef.value?.getContext('2d')) {
    dailyAttributionChart = new Chart(dailyAttributionRef.value.getContext('2d') as any, {
      type: 'bar',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        datasets: [
          {
            label: 'Delta',
            data: [85, 92, 78, 101, 95],
            backgroundColor: 'rgba(59, 130, 246, 0.6)'
          },
          {
            label: 'Gamma',
            data: [22, 18, 24, 32, 28],
            backgroundColor: 'rgba(34, 197, 94, 0.6)'
          },
          {
            label: 'Vega',
            data: [15, 12, 18, 16, 20],
            backgroundColor: 'rgba(56, 189, 248, 0.6)'
          },
          {
            label: 'Theta',
            data: [-12, -12, -12, -12, -12],
            backgroundColor: 'rgba(168, 85, 247, 0.6)'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: undefined,
        scales: {
          x: { stacked: false, grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
          y: { stacked: false, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(255,255,255,0.3)' } }
        },
        plugins: { legend: { labels: { color: 'rgba(255,255,255,0.6)' } } }
      }
    } as any)
  }

  // Waterfall Chart
  if (waterfallChartRef.value?.getContext('2d')) {
    waterfallChart = new Chart(waterfallChartRef.value.getContext('2d') as any, {
      type: 'bar',
      data: {
        labels: ['Start', 'Delta', 'Gamma', 'Vega', 'Theta', 'Other', 'End'],
        datasets: [{
          label: 'Cumulative P&L',
          data: [0, 85000, 28500, 18200, -12300, -5200, 114200],
          backgroundColor: [
            'rgba(255,255,255,0.1)',
            'rgba(34, 197, 94, 0.6)',
            'rgba(34, 197, 94, 0.6)',
            'rgba(34, 197, 94, 0.6)',
            'rgba(248, 113, 113, 0.6)',
            'rgba(248, 113, 113, 0.6)',
            'rgba(59, 130, 246, 0.8)'
          ],
          borderColor: 'rgba(255, 255, 255, 0.2)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(255,255,255,0.3)' } }
        },
        plugins: { legend: { display: false } }
      }
    } as any)
  }
}

const btn_secondary = () => {}

onMounted(() => {
  initCharts()
})

onBeforeUnmount(() => {
  if (compositionChart) compositionChart.destroy()
  if (dailyAttributionChart) dailyAttributionChart.destroy()
  if (waterfallChart) waterfallChart.destroy()
})
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.pnl-attribution-page {
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

.period-select,
.method-select {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  padding: 4px 8px;
  cursor: pointer;
}

.period-select option,
.method-select option {
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
   P&L SUMMARY
   ============================================ */
.pnl-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.summary-card {
  background: rgba(30, 32, 40, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-card.total {
  border: 2px solid rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.05);
}

.summary-label {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
}

.summary-value {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.summary-value.positive {
  color: #4ade80;
}

.summary-value.negative {
  color: #f87171;
}

.summary-value.accent {
  color: #f59e0b;
}

.summary-change {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
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

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
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
   TABLES
   ============================================ */
.table-container {
  overflow-x: auto;
}

.attribution-table,
.risk-factor-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.attribution-table th,
.attribution-table td,
.risk-factor-table th,
.risk-factor-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.attribution-table th,
.risk-factor-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 10px;
}

.col-component,
.col-description,
.factor-name {
  text-align: left;
}

.col-percent,
.explained {
  font-family: "SF Mono", monospace;
}

.col-amount.positive,
.pnl.positive,
.move.positive {
  color: #4ade80;
}

.col-amount.negative,
.pnl.negative,
.move.negative {
  color: #f87171;
}

.col-amount.positive,
.pnl.positive {
  font-weight: 600;
}

.attribution-table tr.delta:hover,
.attribution-table tr.gamma:hover,
.attribution-table tr.vega:hover {
  background: rgba(255,255,255,0.02);
}

.total-row {
  background: rgba(59, 130, 246, 0.1);
  border-top: 2px solid rgba(59, 130, 246, 0.3);
  font-weight: 600;
}

.col-bucket {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
}

/* ============================================
   GREEKS BREAKDOWN
   ============================================ */
.greek-breakdown {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.breakdown-item.total {
  border-bottom: none;
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 10px;
  font-weight: 600;
}

.breakdown-item .label {
  color: rgba(255,255,255,0.6);
}

.breakdown-item .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.breakdown-item .value.positive {
  color: #4ade80;
}

.breakdown-item .value.negative {
  color: #f87171;
}

.breakdown-item .value.accent {
  color: #f59e0b;
}

.breakdown-item .value.blue {
  color: #60a5fa;
}

.breakdown-item .value.cyan {
  color: #06b6d4;
}

/* ============================================
   UNEXPLAINED & TOP POSITIONS
   ============================================ */
.unexplained-metrics {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.metric-item .label {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.metric-item .value {
  font-size: 13px;
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.metric-item .value.positive {
  color: #4ade80;
}

.metric-item .value.negative {
  color: #f87171;
}

.causes-list {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 10px;
  color: rgba(255,255,255,0.5);
}

.causes-list li {
  padding: 2px 0;
}

/* ============================================
   TOP POSITIONS
   ============================================ */
.top-positions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.position-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: rgba(255,255,255,0.02);
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.05);
}

.position-rank {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: rgba(59, 130, 246, 0.2);
  border-radius: 6px;
  font-weight: 700;
  color: #60a5fa;
  font-size: 12px;
}

.position-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.position-name {
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

.position-detail {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
}

.position-pnl {
  font-size: 12px;
  font-weight: 700;
  font-family: "SF Mono", monospace;
}

.position-pnl.positive {
  color: #4ade80;
}

.position-pnl.negative {
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

  .grid-2,
  .grid-3 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .pnl-attribution-page {
    padding: 16px;
  }

  .pnl-summary {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-container {
    height: 300px;
  }

  .chart-container.tall {
    height: 400px;
  }

  .attribution-table,
  .risk-factor-table {
    font-size: 10px;
  }

  .attribution-table th,
  .attribution-table td,
  .risk-factor-table th,
  .risk-factor-table td {
    padding: 6px;
  }
}
</style>
