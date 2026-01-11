<!-- src/pages/ForwardsGreeksDashboard.vue -->
<template>
  <div class="greeks-dashboard-page">
    
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Панель греков</h1>
        <p class="page-subtitle">Анализ чувствительности форвардных позиций</p>
      </div>
      
      <div class="header-right">
        <!-- Position Type -->
        <div class="control-group">
          <label class="control-label">Позиция:</label>
          <select v-model="selectedPosition" class="position-select" @change="updateGreeks">
            <option value="long-bond">Long форвард на облигацию</option>
            <option value="short-bond">Short форвард на облигацию</option>
            <option value="long-fx">Long валютный форвард</option>
            <option value="short-fx">Short валютный форвард</option>
            <option value="long-commodity">Long форвард на товар</option>
          </select>
        </div>

        <!-- View Type -->
        <div class="control-group">
          <label class="control-label">Вид:</label>
          <select v-model="selectedViewType" class="view-select" @change="updateGreeks">
            <option value="summary">Резюме</option>
            <option value="detailed">Детальные греки</option>
            <option value="sensitivity">Графики чувствительности</option>
          </select>
        </div>

        <!-- Update Button -->
        <button @click="updateGreeks" class="btn-primary" :disabled="calculating">
          <span v-if="!calculating">Обновить</span>
          <span v-else>↺ Считаю...</span>
        </button>
      </div>
    </div>

    <!-- Greeks Summary Cards -->
    <div class="greeks-summary">
      <!-- Delta -->
      <div class="greek-card delta-card">
        <div class="greek-header">
          <span class="greek-symbol">Δ (Delta)</span>
          <span class="greek-name">Чувствительность к спот цене</span>
        </div>
        <div class="greek-value positive">{{ greeksValues.delta.toFixed(4) }}</div>
        <div class="greek-details">
          <div class="detail">
            <span class="label">P&L / 1% спота</span>
            <span class="value">{{ formatCompactCurrency(pnlMetrics.deltaP1pct) }}</span>
          </div>
          <div class="detail">
            <span class="label">Gamma (рост дельты)</span>
            <span class="value" :class="greeksValues.gamma >= 0 ? 'positive' : 'negative'">
              {{ greeksValues.gamma >= 0 ? '+' : '' }}{{ greeksValues.gamma.toFixed(6) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Vega -->
      <div class="greek-card vega-card">
        <div class="greek-header">
          <span class="greek-symbol">ν (Vega)</span>
          <span class="greek-name">Чувствительность к волатильности</span>
        </div>
        <div class="greek-value blue">{{ greeksValues.vega.toFixed(4) }}</div>
        <div class="greek-details">
          <div class="detail">
            <span class="label">P&L / 1% vol</span>
            <span class="value">{{ formatCompactCurrency(pnlMetrics.vegaP1pct) }}</span>
          </div>
          <div class="detail">
            <span class="label">Volga (кривизна)</span>
            <span class="value" :class="greeksValues.volga >= 0 ? 'positive' : 'negative'">
              {{ greeksValues.volga >= 0 ? '+' : '' }}{{ greeksValues.volga.toFixed(6) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Theta -->
      <div class="greek-card theta-card">
        <div class="greek-header">
          <span class="greek-symbol">Θ (Theta)</span>
          <span class="greek-name">Временное затухание (P&L от времени)</span>
        </div>
        <div class="greek-value" :class="greeksValues.theta >= 0 ? 'positive' : 'negative'">
          {{ greeksValues.theta >= 0 ? '+' : '' }}{{ greeksValues.theta.toFixed(4) }}
        </div>
        <div class="greek-details">
          <div class="detail">
            <span class="label">P&L / день</span>
            <span class="value">{{ formatCompactCurrency(pnlMetrics.thetaPerDay) }}</span>
          </div>
          <div class="detail">
            <span class="label">Годовая</span>
            <span class="value">{{ (greeksValues.theta * 252).toFixed(2) }}/год</span>
          </div>
        </div>
      </div>

      <!-- Rho -->
      <div class="greek-card rho-card">
        <div class="greek-header">
          <span class="greek-symbol">ρ (Rho)</span>
          <span class="greek-name">Чувствительность к ставкам</span>
        </div>
        <div class="greek-value cyan">{{ greeksValues.rho.toFixed(4) }}</div>
        <div class="greek-details">
          <div class="detail">
            <span class="label">P&L / 1% ставки</span>
            <span class="value">{{ formatCompactCurrency(pnlMetrics.rhoP1pct) }}</span>
          </div>
          <div class="detail">
            <span class="label">Rogas (кривизна)</span>
            <span class="value" :class="greeksValues.rogas >= 0 ? 'positive' : 'negative'">
              {{ greeksValues.rogas >= 0 ? '+' : '' }}{{ greeksValues.rogas.toFixed(6) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Greeks Sensitivity Charts -->
    <div class="grid-2">
      <!-- Delta vs Spot -->
      <div class="card">
        <div class="chart-header">
          <h3>Delta: Чувствительность к спот цене</h3>
          <span class="chart-subtitle">∂F/∂S — как меняется стоимость форварда</span>
        </div>
        <div class="chart-container">
          <canvas ref="deltaChartRef"></canvas>
        </div>
      </div>

      <!-- Gamma vs Spot -->
      <div class="card">
        <div class="chart-header">
          <h3>Gamma: Выпуклость Delta</h3>
          <span class="chart-subtitle">∂²F/∂S² — как меняется дельта</span>
        </div>
        <div class="chart-container">
          <canvas ref="gammaChartRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Vega & Vol Surface -->
    <div class="grid-2">
      <!-- Vega vs Vol -->
      <div class="card">
        <div class="chart-header">
          <h3>Vega: Чувствительность к волатильности</h3>
          <span class="chart-subtitle">∂F/∂σ — как меняется стоимость с волатильностью</span>
        </div>
        <div class="chart-container">
          <canvas ref="vegaChartRef"></canvas>
        </div>
      </div>

      <!-- Vega vs Tenor -->
      <div class="card">
        <div class="chart-header">
          <h3>Разложение Vega по срокам</h3>
          <span class="chart-subtitle">Вклад каждого срока в итоговый vega</span>
        </div>
        <div class="chart-container">
          <canvas ref="vegaDecompRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Theta & Time Decay -->
    <div class="grid-2">
      <!-- Theta vs Time -->
      <div class="card">
        <div class="chart-header">
          <h3>Theta: Временное затухание</h3>
          <span class="chart-subtitle">∂F/∂t — P&L от изменения времени</span>
        </div>
        <div class="chart-container">
          <canvas ref="thetaChartRef"></canvas>
        </div>
      </div>

      <!-- Cross Gamma (Spot vs Vol) -->
      <div class="card">
        <div class="chart-header">
          <h3>Cross Gamma: Спот × Vol</h3>
          <span class="chart-subtitle">∂²F/∂S∂σ — взаимодействие факторов</span>
        </div>
        <div class="chart-container">
          <canvas ref="crossGammaChartRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Detailed Greeks Table -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Детальная таблица греков</h3>
        <span class="card-subtitle">Первые, вторые и смешанные производные</span>
      </div>
      <div class="greeks-table-container">
        <table class="greeks-table">
          <thead>
            <tr>
              <th class="col-name">Greeks</th>
              <th class="col-symbol">Символ</th>
              <th class="col-value">Значение</th>
              <th class="col-meaning">Интерпретация</th>
              <th class="col-impact">Влияние @ 1%</th>
              <th class="col-order">Порядок</th>
            </tr>
          </thead>
          <tbody>
            <!-- First-order Greeks -->
            <tr class="section-header">
              <td colspan="6">ГРЕКИ ПЕРВОГО ПОРЯДКА</td>
            </tr>
            <tr>
              <td class="greek-name">Delta</td>
              <td class="symbol">Δ = ∂F/∂S</td>
              <td class="value mono positive">{{ greeksValues.delta.toFixed(4) }}</td>
              <td class="meaning">Forward при изменении спота</td>
              <td class="impact mono">{{ formatCompactCurrency(pnlMetrics.deltaP1pct) }}</td>
              <td class="order">1st</td>
            </tr>
            <tr>
              <td class="greek-name">Vega</td>
              <td class="symbol">ν = ∂F/∂σ</td>
              <td class="value mono blue">{{ greeksValues.vega.toFixed(4) }}</td>
              <td class="meaning">Forward при изменении волатильности</td>
              <td class="impact mono">{{ formatCompactCurrency(pnlMetrics.vegaP1pct) }}</td>
              <td class="order">1st</td>
            </tr>
            <tr>
              <td class="greek-name">Theta</td>
              <td class="symbol">Θ = ∂F/∂t</td>
              <td class="value mono" :class="greeksValues.theta >= 0 ? 'positive' : 'negative'">
                {{ greeksValues.theta >= 0 ? '+' : '' }}{{ greeksValues.theta.toFixed(4) }}
              </td>
              <td class="meaning">Forward при изменении времени</td>
              <td class="impact mono">{{ formatCompactCurrency(pnlMetrics.thetaPerDay) }}/day</td>
              <td class="order">1st</td>
            </tr>
            <tr>
              <td class="greek-name">Rho</td>
              <td class="symbol">ρ = ∂F/∂r</td>
              <td class="value mono cyan">{{ greeksValues.rho.toFixed(4) }}</td>
              <td class="meaning">Forward при изменении ставки</td>
              <td class="impact mono">{{ formatCompactCurrency(pnlMetrics.rhoP1pct) }}</td>
              <td class="order">1st</td>
            </tr>

            <!-- Second-order Greeks -->
            <tr class="section-header">
              <td colspan="6">ГРЕКИ ВТОРОГО ПОРЯДКА</td>
            </tr>
            <tr>
              <td class="greek-name">Gamma</td>
              <td class="symbol">Γ = ∂²F/∂S²</td>
              <td class="value mono" :class="greeksValues.gamma >= 0 ? 'positive' : 'negative'">
                {{ greeksValues.gamma >= 0 ? '+' : '' }}{{ greeksValues.gamma.toFixed(6) }}
              </td>
              <td class="meaning">Как меняется дельта при изменении спота</td>
              <td class="impact mono">{{ greeksValues.gamma.toFixed(6) }}</td>
              <td class="order">2nd</td>
            </tr>
            <tr>
              <td class="greek-name">Volga</td>
              <td class="symbol">ϝ = ∂²F/∂σ²</td>
              <td class="value mono" :class="greeksValues.volga >= 0 ? 'positive' : 'negative'">
                {{ greeksValues.volga >= 0 ? '+' : '' }}{{ greeksValues.volga.toFixed(6) }}
              </td>
              <td class="meaning">Как меняется vega при изменении волатильности</td>
              <td class="impact mono">{{ greeksValues.volga.toFixed(6) }}</td>
              <td class="order">2nd</td>
            </tr>
            <tr>
              <td class="greek-name">Vanna</td>
              <td class="symbol">χ = ∂²F/∂S∂σ</td>
              <td class="value mono" :class="greeksValues.vanna >= 0 ? 'positive' : 'negative'">
                {{ greeksValues.vanna >= 0 ? '+' : '' }}{{ greeksValues.vanna.toFixed(6) }}
              </td>
              <td class="meaning">Взаимодействие спота и волатильности</td>
              <td class="impact mono">{{ greeksValues.vanna.toFixed(6) }}</td>
              <td class="order">2nd</td>
            </tr>
            <tr>
              <td class="greek-name">Charm</td>
              <td class="symbol">χ = ∂²F/∂t∂S</td>
              <td class="value mono" :class="greeksValues.charm >= 0 ? 'positive' : 'negative'">
                {{ greeksValues.charm >= 0 ? '+' : '' }}{{ greeksValues.charm.toFixed(6) }}
              </td>
              <td class="meaning">Как меняется дельта при изменении времени</td>
              <td class="impact mono">{{ greeksValues.charm.toFixed(6) }}</td>
              <td class="order">2nd</td>
            </tr>
            <tr>
              <td class="greek-name">Rogas</td>
              <td class="symbol">ρρ = ∂²F/∂r²</td>
              <td class="value mono" :class="greeksValues.rogas >= 0 ? 'positive' : 'negative'">
                {{ greeksValues.rogas >= 0 ? '+' : '' }}{{ greeksValues.rogas.toFixed(6) }}
              </td>
              <td class="meaning">Как меняется rho при изменении ставки</td>
              <td class="impact mono">{{ greeksValues.rogas.toFixed(6) }}</td>
              <td class="order">2nd</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Greeks Risk Heatmap -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Тепловая карта риска греков</h3>
        <span class="card-subtitle">Тепловая карта по движениям рынка</span>
      </div>
      <div class="heatmap-container">
        <canvas ref="heatmapRef"></canvas>
      </div>
    </div>

    <!-- P&L Attribution by Greeks -->
    <div class="grid-2">
      <!-- Greeks P&L Contribution -->
      <div class="card">
        <div class="chart-header">
          <h3>Атрибуция P&L по грекам</h3>
          <span class="chart-subtitle">Вклад каждого грека в общий P&L</span>
        </div>
        <div class="chart-container">
          <canvas ref="pnlAttributionRef"></canvas>
        </div>
      </div>

      <!-- Greeks Contribution Table -->
      <div class="card">
        <div class="chart-header">
          <h3>Резюме P&L греков</h3>
          <span class="chart-subtitle">Эффект каждого фактора</span>
        </div>
        <div class="greeks-pnl-summary">
          <div class="pnl-item">
            <span class="factor-label">Delta P&L (Движение спота)</span>
            <span class="factor-value" :class="greeksValues.delta >= 0 ? 'positive' : 'negative'">
              {{ greeksValues.delta >= 0 ? '+' : '' }}{{ formatCompactCurrency(pnlMetrics.deltaPnL) }}
            </span>
          </div>
          <div class="pnl-item">
            <span class="factor-label">Gamma P&L (Выпуклость)</span>
            <span class="factor-value" :class="greeksValues.gamma >= 0 ? 'positive' : 'negative'">
              {{ greeksValues.gamma >= 0 ? '+' : '' }}{{ formatCompactCurrency(pnlMetrics.gammaPnL) }}
            </span>
          </div>
          <div class="pnl-item">
            <span class="factor-label">Vega P&L (Движение Vol)</span>
            <span class="factor-value" :class="greeksValues.vega >= 0 ? 'positive' : 'negative'">
              {{ greeksValues.vega >= 0 ? '+' : '' }}{{ formatCompactCurrency(pnlMetrics.vegaPnL) }}
            </span>
          </div>
          <div class="pnl-item">
            <span class="factor-label">Theta P&L (Временное затухание)</span>
            <span class="factor-value" :class="greeksValues.theta >= 0 ? 'positive' : 'negative'">
              {{ greeksValues.theta >= 0 ? '+' : '' }}{{ formatCompactCurrency(pnlMetrics.thetaPnL) }}
            </span>
          </div>
          <div class="pnl-item">
            <span class="factor-label">Rho P&L (Движение ставки)</span>
            <span class="factor-value" :class="greeksValues.rho >= 0 ? 'positive' : 'negative'">
              {{ greeksValues.rho >= 0 ? '+' : '' }}{{ formatCompactCurrency(pnlMetrics.rhoPnL) }}
            </span>
          </div>
          <div class="pnl-item total">
            <span class="factor-label"><strong>Общий P&L</strong></span>
            <span class="factor-value accent">
              <strong>{{ formatCompactCurrency(pnlMetrics.totalPnL) }}</strong>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Risk Limits & Monitoring -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Risk Limits & Monitoring</h3>
        <span class="card-subtitle">Проверка лимитов греков и alerts</span>
      </div>
      <div class="risk-limits-table-container">
        <table class="risk-limits-table">
          <thead>
            <tr>
              <th>Greeks</th>
              <th>Текущее</th>
              <th>Лимит</th>
              <th>Использование</th>
              <th>Статус</th>
              <th>Действие</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="limit in riskLimits" :key="limit.greeks" :class="limit.status.toLowerCase()">
              <td class="greeks-name">{{ limit.greeks }}</td>
              <td class="current mono">{{ limit.current.toFixed(4) }}</td>
              <td class="limit mono">{{ limit.limit }}</td>
              <td class="utilization">
                <div class="util-bar">
                  <div class="util-fill" :style="{ width: (limit.utilization * 100) + '%' }"></div>
                </div>
                <span class="util-text">{{ (limit.utilization * 100).toFixed(0) }}%</span>
              </td>
              <td class="status" :class="limit.status.toLowerCase()">
                {{ limit.status }}
              </td>
              <td class="action">
                <button v-if="limit.status === 'Warning'" class="btn-action warning">Уменьшить</button>
                <button v-else-if="limit.status === 'Critical'" class="btn-action critical">Хеджировать!</button>
                <span v-else class="btn-action ok">OK</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Greeks Scenarios -->
    <div class="card full-width">
      <div class="chart-header">
        <h3>P&L в рыночных сценариях</h3>
        <span class="chart-subtitle">Как меняется P&L при различных комбинациях движений</span>
      </div>
      <div class="chart-container tall">
        <canvas ref="scenariosRef"></canvas>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span>• Модель: Black-Scholes (для форвардов)</span>
      <span>• Частота: Непрерывная</span>
      <span>• Обновление: В реальном времени</span>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'

const selectedPosition = ref('long-bond')
const selectedViewType = ref('summary')
const calculating = ref(false)

// Position Parameters
const positionParams = ref({
  spotPrice: 100,
  strikePrice: 100,
  timeToMaturity: 0.25,
  volatility: 12.5,
  riskFreeRate: 4.25,
  dividendYield: 2.5,
  contractSize: 1_000_000
})

// Greeks Values
const greeksValues = computed(() => {
  const S = positionParams.value.spotPrice
  const K = positionParams.value.strikePrice
  const T = positionParams.value.timeToMaturity
  const r = positionParams.value.riskFreeRate / 100
  const q = positionParams.value.dividendYield / 100
  const sigma = positionParams.value.volatility / 100

  // Black-Scholes Greeks for forwards
  const delta = Math.exp((r - q) * T) // always close to 1 for ATM forwards
  const gamma = Math.exp((r - q) * T) / (S * sigma * Math.sqrt(T))
  const vega = S * Math.exp((r - q) * T) * Math.sqrt(T) / 100
  const theta = -(S * sigma * Math.exp((r - q) * T)) / (2 * Math.sqrt(T)) / 365
  const rho = K * T * Math.exp(-r * T) / 100

  const volga = vega * (Math.log(S / K) / (sigma * sigma * T) - 1) / sigma
  const vanna = -Math.exp((r - q) * T) * Math.log(S / K) / (sigma * sigma * T)
  const charm = (r - q) * delta - gamma * S * sigma
  const rogas = rho * T / 100

  return {
    delta,
    gamma,
    vega,
    theta,
    rho,
    volga,
    vanna,
    charm,
    rogas
  }
})

// P&L Metrics
const pnlMetrics = computed(() => {
  const g = greeksValues.value
  const cs = positionParams.value.contractSize

  const deltaP1pct = g.delta * positionParams.value.spotPrice * 0.01 * cs
  const vegaP1pct = g.vega * cs
  const rhoP1pct = g.rho * cs
  const thetaPerDay = g.theta * cs

  // Simulated P&L (based on market moves)
  const spotMove = 0.02 // 2% spot move
  const volMove = 0.02 // 2% vol move
  const timePass = 1 / 365 // 1 day

  const deltaPnL = g.delta * spotMove * positionParams.value.spotPrice * cs
  const gammaPnL = 0.5 * g.gamma * Math.pow(spotMove * positionParams.value.spotPrice, 2) * cs
  const vegaPnL = g.vega * volMove * cs
  const thetaPnL = g.theta * timePass * cs
  const rhoPnL = g.rho * 0.01 * cs

  const totalPnL = deltaPnL + gammaPnL + vegaPnL + thetaPnL + rhoPnL

  return {
    deltaP1pct,
    vegaP1pct,
    rhoP1pct,
    thetaPerDay,
    deltaPnL,
    gammaPnL,
    vegaPnL,
    thetaPnL,
    rhoPnL,
    totalPnL
  }
})

// Risk Limits
const riskLimits = ref([
  { greeks: 'Delta', current: 0.98, limit: 2.0, utilization: 0.49, status: 'OK' },
  { greeks: 'Gamma', current: 0.0015, limit: 0.005, utilization: 0.30, status: 'OK' },
  { greeks: 'Vega', current: 850, limit: 1500, utilization: 0.57, status: 'OK' },
  { greeks: 'Theta', current: -45.2, limit: -100, utilization: 0.45, status: 'OK' },
  { greeks: 'Rho', current: 125.3, limit: 200, utilization: 0.63, status: 'Warning' },
])

// Chart References
const deltaChartRef = ref<HTMLCanvasElement | null>(null)
const gammaChartRef = ref<HTMLCanvasElement | null>(null)
const vegaChartRef = ref<HTMLCanvasElement | null>(null)
const vegaDecompRef = ref<HTMLCanvasElement | null>(null)
const thetaChartRef = ref<HTMLCanvasElement | null>(null)
const crossGammaChartRef = ref<HTMLCanvasElement | null>(null)
const heatmapRef = ref<HTMLCanvasElement | null>(null)
const pnlAttributionRef = ref<HTMLCanvasElement | null>(null)
const scenariosRef = ref<HTMLCanvasElement | null>(null)

let charts: { [key: string]: Chart | null } = {}

// Methods
const formatCompactCurrency = (val: number) => {
  if (Math.abs(val) >= 1_000_000) {
    return (val / 1_000_000).toFixed(1) + 'М'
  }
  return '$' + (val / 1000).toFixed(0) + 'K'
}

const updateGreeks = () => {
  // Update computed properties
  initCharts()
}

const initCharts = () => {
  // Destroy existing charts
  Object.values(charts).forEach(chart => {
    if (chart) chart.destroy()
  })
  charts = {}

  const S = positionParams.value.spotPrice
  const sigma = positionParams.value.volatility / 100

  // Delta Chart
  if (deltaChartRef.value?.getContext('2d')) {
    const spotPrices = []
    const deltaValues = []
    for (let i = 0.7; i <= 1.3; i += 0.05) {
      spotPrices.push((i * 100).toFixed(0))
      deltaValues.push(greeksValues.value.delta)
    }

    charts.delta = new Chart(deltaChartRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: spotPrices,
        datasets: [{
          label: 'Delta (∂F/∂S)',
          data: deltaValues,
          borderColor: '#4ade80',
          backgroundColor: 'rgba(74, 222, 128, 0.08)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          borderWidth: 2
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

  // Gamma Chart
  if (gammaChartRef.value?.getContext('2d')) {
    const spotPrices = []
    const gammaValues = []
    for (let i = 0.7; i <= 1.3; i += 0.05) {
      spotPrices.push((i * 100).toFixed(0))
      gammaValues.push(greeksValues.value.gamma)
    }

    charts.gamma = new Chart(gammaChartRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: spotPrices,
        datasets: [{
          label: 'Gamma (∂²F/∂S²)',
          data: gammaValues,
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.08)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          borderWidth: 2
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

  // Vega Chart
  if (vegaChartRef.value?.getContext('2d')) {
    const vols = []
    const vegaValues = []
    for (let v = 5; v <= 25; v += 2) {
      vols.push(v.toString())
      vegaValues.push(greeksValues.value.vega)
    }

    charts.vega = new Chart(vegaChartRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: vols,
        datasets: [{
          label: 'Vega (∂F/∂σ)',
          data: vegaValues,
          borderColor: '#60a5fa',
          backgroundColor: 'rgba(96, 165, 250, 0.08)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          borderWidth: 2
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

  // Vega Decomposition
  if (vegaDecompRef.value?.getContext('2d')) {
    charts.vegaDecomp = new Chart(vegaDecompRef.value.getContext('2d') as any, {
      type: 'bar',
      data: {
        labels: ['1M', '3M', '6M', '1Y', '2Y', '5Y', '10Y'],
        datasets: [{
          label: 'Vega by Tenor',
          data: [120, 180, 240, 290, 350, 280, 150],
          backgroundColor: ['#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8', '#1e40af', '#1e3a8a', '#172554'],
          borderColor: '#0f172a',
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

  // Theta Chart
  if (thetaChartRef.value?.getContext('2d')) {
    const daysToExp = []
    const thetaVals = []
    for (let days = 90; days >= 1; days -= 10) {
      daysToExp.push(days.toString())
      thetaVals.push(-(days / 10) * 2)
    }

    charts.theta = new Chart(thetaChartRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: daysToExp,
        datasets: [{
          label: 'Theta (∂F/∂t)',
          data: thetaVals,
          borderColor: '#f87171',
          backgroundColor: 'rgba(248, 113, 113, 0.08)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          borderWidth: 2
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

  // Cross Gamma
  if (crossGammaChartRef.value?.getContext('2d')) {
    charts.crossGamma = new Chart(crossGammaChartRef.value.getContext('2d') as any, {
      type: 'bubble',
      data: {
        datasets: [{
          label: 'Vanna (∂²F/∂S∂σ)',
          data: [
            { x: 95, y: 8, r: 10 },
            { x: 98, y: 12, r: 15 },
            { x: 100, y: 15, r: 20 },
            { x: 102, y: 12, r: 15 },
            { x: 105, y: 8, r: 10 }
          ],
          backgroundColor: 'rgba(96, 165, 250, 0.6)',
          borderColor: '#60a5fa'
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

  // P&L Attribution
  if (pnlAttributionRef.value?.getContext('2d')) {
    const pm = pnlMetrics.value
    charts.pnlAttr = new Chart(pnlAttributionRef.value.getContext('2d') as any, {
      type: 'bar',
      data: {
        labels: ['Delta', 'Gamma', 'Vega', 'Theta', 'Rho'],
        datasets: [{
          label: 'P&L Contribution',
          data: [pm.deltaPnL, pm.gammaPnL, pm.vegaPnL, pm.thetaPnL, pm.rhoPnL],
          backgroundColor: [
            pm.deltaPnL >= 0 ? 'rgba(74, 222, 128, 0.6)' : 'rgba(248, 113, 113, 0.6)',
            pm.gammaPnL >= 0 ? 'rgba(74, 222, 128, 0.6)' : 'rgba(248, 113, 113, 0.6)',
            pm.vegaPnL >= 0 ? 'rgba(74, 222, 128, 0.6)' : 'rgba(248, 113, 113, 0.6)',
            pm.thetaPnL >= 0 ? 'rgba(74, 222, 128, 0.6)' : 'rgba(248, 113, 113, 0.6)',
            pm.rhoPnL >= 0 ? 'rgba(74, 222, 128, 0.6)' : 'rgba(248, 113, 113, 0.6)'
          ],
          borderColor: ['#4ade80', '#4ade80', '#4ade80', '#4ade80', '#4ade80'],
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

  // Scenarios
  if (scenariosRef.value?.getContext('2d')) {
    charts.scenarios = new Chart(scenariosRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: ['-2% Spot', '-1.5% Spot', '-1% Spot', 'Base', '+1% Spot', '+1.5% Spot', '+2% Spot'],
        datasets: [
          {
            label: 'No Vol Change',
            data: [-25000, -18000, -12000, 0, 12000, 18000, 25000],
            borderColor: '#60a5fa',
            tension: 0.4
          },
          {
            label: 'Vol +5%',
            data: [-20000, -13000, -7000, 5000, 17000, 23000, 30000],
            borderColor: '#4ade80',
            tension: 0.4
          },
          {
            label: 'Vol -5%',
            data: [-30000, -23000, -17000, -5000, 7000, 13000, 20000],
            borderColor: '#f87171',
            tension: 0.4
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
  Object.values(charts).forEach(chart => {
    if (chart) chart.destroy()
  })
})
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.greeks-dashboard-page {
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

.position-select,
.view-select {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  padding: 4px 8px;
  cursor: pointer;
}

.position-select option,
.view-select option {
  background: #1e1f28;
  color: #fff;
}

.btn-primary {
  padding: 8px 16px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  white-space: nowrap;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* ============================================
   GREEKS SUMMARY
   ============================================ */
.greeks-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.greek-card {
  background: rgba(30, 32, 40, 0.4);
  border: 2px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.2s;
}

.greek-card:hover {
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.greek-card.delta-card {
  border-color: rgba(74, 222, 128, 0.2);
}

.greek-card.vega-card {
  border-color: rgba(96, 165, 250, 0.2);
}

.greek-card.theta-card {
  border-color: rgba(248, 113, 113, 0.2);
}

.greek-card.rho-card {
  border-color: rgba(6, 182, 212, 0.2);
}

.greek-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  flex-direction: column;
}

.greek-symbol {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.greek-name {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
  font-weight: 500;
}

.greek-value {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.greek-value.positive {
  color: #4ade80;
}

.greek-value.negative {
  color: #f87171;
}

.greek-value.blue {
  color: #60a5fa;
}

.greek-value.cyan {
  color: #06b6d4;
}

.greek-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  border-top: 1px solid rgba(255,255,255,0.05);
  padding-top: 8px;
}

.detail {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
}

.detail .label {
  color: rgba(255,255,255,0.4);
}

.detail .value {
  font-weight: 600;
  color: rgba(255,255,255,0.7);
  font-family: "SF Mono", monospace;
}

.detail .value.positive {
  color: #4ade80;
}

.detail .value.negative {
  color: #f87171;
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

.full-width {
  grid-column: 1 / -1;
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
   GREEKS TABLE
   ============================================ */
.greeks-table-container {
  overflow-x: auto;
}

.greeks-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

.greeks-table th,
.greeks-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.greeks-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 9px;
}

.col-name {
  text-align: left;
}

.greek-name {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
}

.symbol {
  font-family: "SF Mono", monospace;
  color: rgba(255,255,255,0.5);
}

.value {
  font-family: "SF Mono", monospace;
  font-weight: 600;
}

.value.positive {
  color: #4ade80;
}

.value.negative {
  color: #f87171;
}

.meaning {
  color: rgba(255,255,255,0.5);
  font-size: 9px;
}

.impact {
  font-family: "SF Mono", monospace;
}

.order {
  color: rgba(255,255,255,0.4);
  font-weight: 600;
}

.greeks-table .section-header {
  background: rgba(59, 130, 246, 0.1);
  font-weight: 600;
  color: rgba(96, 165, 250, 0.8);
}

/* ============================================
   PNL SUMMARY
   ============================================ */
.greeks-pnl-summary {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pnl-item {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background: rgba(255,255,255,0.02);
  border-radius: 6px;
  font-size: 11px;
}

.factor-label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.factor-value {
  font-family: "SF Mono", monospace;
  font-weight: 600;
  color: #fff;
}

.factor-value.positive {
  color: #4ade80;
}

.factor-value.negative {
  color: #f87171;
}

.pnl-item.total {
  background: rgba(59, 130, 246, 0.1);
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 10px;
}

.factor-value.accent {
  color: #f59e0b;
}

/* ============================================
   RISK LIMITS TABLE
   ============================================ */
.risk-limits-table-container {
  overflow-x: auto;
}

.risk-limits-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.risk-limits-table th,
.risk-limits-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.risk-limits-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 10px;
}

.greeks-name {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
}

.current,
.limit {
  font-family: "SF Mono", monospace;
}

.utilization {
  display: flex;
  align-items: center;
  gap: 8px;
}

.util-bar {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.05);
  border-radius: 2px;
  overflow: hidden;
  min-width: 60px;
}

.util-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 2px;
}

.util-text {
  font-size: 10px;
  color: rgba(255,255,255,0.5);
  min-width: 35px;
  text-align: right;
}

.status {
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
}

.status.ok {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

.status.warning {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.status.critical {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.action {
  text-align: right;
}

.btn-action {
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid;
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-action.ok {
  background: rgba(74, 222, 128, 0.2);
  border-color: rgba(74, 222, 128, 0.4);
  color: #4ade80;
}

.btn-action.warning {
  background: rgba(245, 158, 11, 0.2);
  border-color: rgba(245, 158, 11, 0.4);
  color: #f59e0b;
  cursor: pointer;
}

.btn-action.warning:hover {
  background: rgba(245, 158, 11, 0.3);
}

.btn-action.critical {
  background: rgba(248, 113, 113, 0.2);
  border-color: rgba(248, 113, 113, 0.4);
  color: #f87171;
  cursor: pointer;
}

.btn-action.critical:hover {
  background: rgba(248, 113, 113, 0.3);
}

/* ============================================
   HEATMAP
   ============================================ */
.heatmap-container {
  position: relative;
  width: 100%;
  height: 400px;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(107, 114, 128, 0.08);
}

.heatmap-container canvas {
  width: 100% !important;
  height: 100% !important;
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

  .greeks-summary {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .greeks-dashboard-page {
    padding: 16px;
  }

  .greeks-summary {
    grid-template-columns: 1fr;
  }

  .greeks-table,
  .risk-limits-table {
    font-size: 9px;
  }

  .greeks-table th,
  .greeks-table td,
  .risk-limits-table th,
  .risk-limits-table td {
    padding: 6px;
  }

  .chart-container {
    height: 300px;
  }

  .chart-container.tall {
    height: 400px;
  }

  .heatmap-container {
    height: 300px;
  }
}
</style>
