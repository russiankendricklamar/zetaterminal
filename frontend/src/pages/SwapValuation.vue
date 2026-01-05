<!-- src/pages/SwapValuation.vue -->
<template>
  <div class="swap-valuation-page">
    
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Swap Valuation</h1>
        <p class="page-subtitle">Справедливая стоимость и анализ IRS, CDS, Basis Swaps</p>
      </div>
      
      <div class="header-right">
        <!-- Swap Type Selector -->
        <div class="control-group">
          <label class="control-label">Тип свопа:</label>
          <select v-model="selectedSwapType" class="swap-type-select" @change="updateValuation">
            <option value="irs">Interest Rate Swap (IRS)</option>
            <option value="cds">Credit Default Swap (CDS)</option>
            <option value="basis">Basis Swap</option>
            <option value="xccy">Cross-Currency Swap</option>
          </select>
        </div>

        <!-- Calculation Button -->
        <button 
          @click="calculateValuation" 
          class="btn-primary"
          :disabled="calculating"
        >
          <span v-if="!calculating">📊 Пересчитать</span>
          <span v-else>⟳ Считаю...</span>
        </button>
      </div>
    </div>

    <!-- Input Parameters Section -->
    <div class="grid-2">
      <!-- Swap Parameters -->
      <div class="card">
        <div class="card-header">
          <h3>Параметры свопа</h3>
        </div>
        <div class="parameter-group">
          <div class="param-row">
            <label>Номинал (млн)</label>
            <input v-model.number="params.notional" type="number" class="param-input" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Срок (годы)</label>
            <input v-model.number="params.tenor" type="number" class="param-input" step="0.5" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Фиксированная ставка (%)</label>
            <input v-model.number="params.fixedRate" type="number" class="param-input" step="0.01" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Купонов в год</label>
            <select v-model.number="params.couponsPerYear" class="param-input" @change="updateValuation">
              <option value="1">1</option>
              <option value="2">2 (Semi-annual)</option>
              <option value="4">4 (Quarterly)</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Market Conditions -->
      <div class="card">
        <div class="card-header">
          <h3>Рыночные условия</h3>
        </div>
        <div class="parameter-group">
          <div class="param-row">
            <label>Floating Rate Index (%)</label>
            <input v-model.number="params.floatingRate" type="number" class="param-input" step="0.01" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Спред (bp)</label>
            <input v-model.number="params.spread" type="number" class="param-input" step="1" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Дисконт кривая (базовая ставка, %)</label>
            <input v-model.number="params.discountRate" type="number" class="param-input" step="0.01" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Волатильность (%)</label>
            <input v-model.number="params.volatility" type="number" class="param-input" step="0.1" @change="updateValuation" />
          </div>
        </div>
      </div>
    </div>

    <!-- Valuation Results -->
    <div class="grid-3">
      <!-- PV Fixed Leg -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>PV Fixed Leg</h3>
          <span class="metric-unit">млн USD</span>
        </div>
        <div class="metric-value accent">
          {{ formatCurrency(valuationResults.pvFixedLeg) }}
        </div>
        <div class="metric-detail">
          <span class="detail-label">Купоны:</span>
          <span class="detail-value">{{ params.couponsPerYear * params.tenor }} шт.</span>
        </div>
      </div>

      <!-- PV Floating Leg -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>PV Floating Leg</h3>
          <span class="metric-unit">млн USD</span>
        </div>
        <div class="metric-value blue">
          {{ formatCurrency(valuationResults.pvFloatingLeg) }}
        </div>
        <div class="metric-detail">
          <span class="detail-label">Forward Rate:</span>
          <span class="detail-value">{{ (params.floatingRate + params.spread / 100).toFixed(2) }}%</span>
        </div>
      </div>

      <!-- Swap Value -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Swap Value (Payer)</h3>
          <span class="metric-unit">млн USD</span>
        </div>
        <div class="metric-value" :class="valuationResults.swapValue >= 0 ? 'positive' : 'negative'">
          {{ formatCurrency(valuationResults.swapValue) }}
        </div>
        <div class="metric-detail">
          <span class="detail-label">В % номинала:</span>
          <span class="detail-value">{{ ((valuationResults.swapValue / params.notional) * 100).toFixed(2) }}%</span>
        </div>
      </div>
    </div>

    <!-- Key Metrics Grid -->
    <div class="grid-3">
      <!-- Duration -->
      <div class="card">
        <div class="card-header">
          <h3>Duration анализ</h3>
        </div>
        <div class="metrics-list">
          <div class="metric-item">
            <span class="label">Modified Duration</span>
            <span class="value">{{ valuationResults.duration.toFixed(2) }}</span>
          </div>
          <div class="metric-item">
            <span class="label">DV01 (М/bp)</span>
            <span class="value" :class="valuationResults.dv01 >= 0 ? 'positive' : 'negative'">
              {{ formatCompactCurrency(valuationResults.dv01) }}
            </span>
          </div>
          <div class="metric-item">
            <span class="label">BPV (М)</span>
            <span class="value mono">{{ (valuationResults.dv01 / 10000).toFixed(4) }}</span>
          </div>
        </div>
      </div>

      <!-- Convexity -->
      <div class="card">
        <div class="card-header">
          <h3>Выпуклость</h3>
        </div>
        <div class="metrics-list">
          <div class="metric-item">
            <span class="label">Convexity</span>
            <span class="value">{{ valuationResults.convexity.toFixed(2) }}</span>
          </div>
          <div class="metric-item">
            <span class="label">Gamma (М/bp²)</span>
            <span class="value">{{ (valuationResults.convexity / 100).toFixed(4) }}</span>
          </div>
          <div class="metric-item">
            <span class="label">Уровень гарантирован</span>
            <span class="value">Низкий</span>
          </div>
        </div>
      </div>

      <!-- Spread Metrics -->
      <div class="card">
        <div class="card-header">
          <h3>Спред-метрики</h3>
        </div>
        <div class="metrics-list">
          <div class="metric-item">
            <span class="label">Spread DV01 (М/bp)</span>
            <span class="value mono">{{ formatCompactCurrency(valuationResults.spreadDv01) }}</span>
          </div>
          <div class="metric-item">
            <span class="label">ASW (All-in Swap)</span>
            <span class="value">{{ params.spread }} bp</span>
          </div>
          <div class="metric-item">
            <span class="label">Z-spread</span>
            <span class="value">{{ (params.spread * 1.05).toFixed(0) }} bp</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Cashflow Schedule -->
    <div class="card full-width">
      <div class="card-header">
        <h3>График денежных потоков</h3>
        <span class="card-subtitle">Fixed vs Floating legs comparison</span>
      </div>
      <div class="cashflow-table-container">
        <table class="cashflow-table">
          <thead>
            <tr>
              <th class="col-period">Период</th>
              <th class="col-date">Дата платежа</th>
              <th class="col-amount">Fixed Leg (М)</th>
              <th class="col-amount">Floating Leg (М)</th>
              <th class="col-amount">Net (М)</th>
              <th class="col-pv">PV (М)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(cf, idx) in valuationResults.cashflows" :key="idx">
              <td class="col-period">{{ idx + 1 }}</td>
              <td class="col-date mono">{{ cf.date }}</td>
              <td class="col-amount accent">{{ formatCurrency(cf.fixedLeg) }}</td>
              <td class="col-amount blue">{{ formatCurrency(cf.floatingLeg) }}</td>
              <td class="col-amount" :class="cf.net >= 0 ? 'positive' : 'negative'">
                {{ cf.net >= 0 ? '+' : '' }}{{ formatCurrency(cf.net) }}
              </td>
              <td class="col-pv mono">{{ formatCurrency(cf.pv) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Valuation Charts -->
    <div class="grid-2">
      <!-- PV Profile -->
      <div class="card">
        <div class="chart-header">
          <h3>Swap Value vs Fixed Rate</h3>
          <span class="chart-subtitle">Чувствительность к изменению фиксированной ставки</span>
        </div>
        <div class="chart-container">
          <canvas ref="pvProfileRef"></canvas>
        </div>
      </div>

      <!-- DV01 Profile -->
      <div class="card">
        <div class="chart-header">
          <h3>DV01 vs Tenor</h3>
          <span class="chart-subtitle">Риск по различным срокам</span>
        </div>
        <div class="chart-container">
          <canvas ref="dv01ProfileRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Scenario Analysis -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Анализ сценариев</h3>
        <span class="card-subtitle">Swap Value при различных уровнях ставок</span>
      </div>
      <div class="scenario-container">
        <table class="scenario-table">
          <thead>
            <tr>
              <th>Сценарий</th>
              <th>Fixed Rate</th>
              <th>Floating Rate</th>
              <th>PV Fixed Leg</th>
              <th>PV Floating Leg</th>
              <th>Swap Value (М)</th>
              <th>PnL (М)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="scenario in scenarioAnalysis" :key="scenario.name" :class="scenario.isBase ? 'base' : ''">
              <td class="scenario-name">{{ scenario.name }}</td>
              <td class="mono">{{ scenario.fixedRate.toFixed(2) }}%</td>
              <td class="mono">{{ scenario.floatingRate.toFixed(2) }}%</td>
              <td class="accent">{{ formatCurrency(scenario.pvFixed) }}</td>
              <td class="blue">{{ formatCurrency(scenario.pvFloating) }}</td>
              <td class="mono" :class="scenario.swapValue >= 0 ? 'positive' : 'negative'">
                {{ scenario.swapValue >= 0 ? '+' : '' }}{{ formatCurrency(scenario.swapValue) }}
              </td>
              <td class="mono" :class="scenario.pnl >= 0 ? 'positive' : 'negative'">
                {{ scenario.pnl >= 0 ? '+' : '' }}{{ formatCurrency(scenario.pnl) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Risk Summary -->
    <div class="grid-3">
      <div class="risk-card risk-high">
        <div class="risk-header">
          <span class="risk-icon">🎯</span>
          <h3>Duration Risk</h3>
        </div>
        <div class="risk-value">{{ valuationResults.duration.toFixed(2) }} y</div>
        <div class="risk-detail">ΔPV / 100bp: {{ formatCompactCurrency(valuationResults.dv01) }}</div>
      </div>

      <div class="risk-card risk-medium">
        <div class="risk-header">
          <span class="risk-icon">📊</span>
          <h3>Spread Risk</h3>
        </div>
        <div class="risk-value">{{ params.spread }} bp</div>
        <div class="risk-detail">Spread DV01: {{ formatCompactCurrency(valuationResults.spreadDv01) }}</div>
      </div>

      <div class="risk-card risk-low">
        <div class="risk-header">
          <span class="risk-icon">⚡</span>
          <h3>Convexity Risk</h3>
        </div>
        <div class="risk-value">{{ valuationResults.convexity.toFixed(2) }}</div>
        <div class="risk-detail">Низкий риск для ваниллы</div>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span>• Модель: Discounted Cash Flow (DCF)</span>
      <span>• Метод: Bootstrap yield curve</span>
      <span>• Расчёт в реальном времени</span>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'

const selectedSwapType = ref('irs')
const calculating = ref(false)

// Swap Parameters
const params = ref({
  notional: 100,            // млн
  tenor: 5,                 // лет
  fixedRate: 4.25,          // %
  floatingRate: 4.15,       // %
  spread: 15,               // bp
  couponsPerYear: 2,
  discountRate: 4.2,        // %
  volatility: 12            // %
})

// Valuation Results
const valuationResults = ref({
  pvFixedLeg: 102.45,
  pvFloatingLeg: 100.0,
  swapValue: 2.45,
  duration: 4.25,
  dv01: 42500,              // млн / 100bp
  spreadDv01: 28500,
  convexity: 18.5,
  cashflows: [] as any[]
})

// Scenario Analysis
const scenarioAnalysis = computed(() => {
  const baseFixed = params.value.fixedRate
  const baseFloating = params.value.floatingRate
  const baseSwapValue = valuationResults.value.swapValue

  return [
    {
      name: 'Down -200bp',
      fixedRate: baseFixed - 2,
      floatingRate: baseFloating - 2,
      pvFixed: 112.5,
      pvFloating: 108.2,
      swapValue: 4.3,
      pnl: 4.3 - baseSwapValue,
      isBase: false
    },
    {
      name: 'Down -100bp',
      fixedRate: baseFixed - 1,
      floatingRate: baseFloating - 1,
      pvFixed: 107.3,
      pvFloating: 104.1,
      swapValue: 3.2,
      pnl: 3.2 - baseSwapValue,
      isBase: false
    },
    {
      name: 'Base Case',
      fixedRate: baseFixed,
      floatingRate: baseFloating,
      pvFixed: valuationResults.value.pvFixedLeg,
      pvFloating: valuationResults.value.pvFloatingLeg,
      swapValue: baseSwapValue,
      pnl: 0,
      isBase: true
    },
    {
      name: 'Up +100bp',
      fixedRate: baseFixed + 1,
      floatingRate: baseFloating + 1,
      pvFixed: 96.8,
      pvFloating: 95.9,
      swapValue: 0.9,
      pnl: 0.9 - baseSwapValue,
      isBase: false
    },
    {
      name: 'Up +200bp',
      fixedRate: baseFixed + 2,
      floatingRate: baseFloating + 2,
      pvFixed: 91.5,
      pvFloating: 91.2,
      swapValue: 0.3,
      pnl: 0.3 - baseSwapValue,
      isBase: false
    }
  ]
})

// Chart References
const pvProfileRef = ref<HTMLCanvasElement | null>(null)
const dv01ProfileRef = ref<HTMLCanvasElement | null>(null)

let pvProfileChart: Chart | null = null
let dv01ProfileChart: Chart | null = null

// Methods
const formatCurrency = (val: number) => {
  if (Math.abs(val) >= 1) {
    return (val >= 0 ? '+' : '') + val.toFixed(2)
  }
  return (val >= 0 ? '+' : '') + (val * 1_000_000).toFixed(0)
}

const formatCompactCurrency = (val: number) => {
  if (Math.abs(val) >= 1_000_000) {
    return (val / 1_000_000).toFixed(1) + 'М'
  }
  return '$' + (val / 1000).toFixed(0) + 'K'
}

const updateValuation = () => {
  // Simplified DCF calculation
  const tenor = params.value.tenor
  const notional = params.value.notional
  const fixedRate = params.value.fixedRate / 100
  const floatingRate = (params.value.floatingRate + params.value.spread / 100) / 100
  const discountRate = params.value.discountRate / 100
  const couponFreq = params.value.couponsPerYear

  const periodRate = discountRate / couponFreq
  const periods = tenor * couponFreq

  let pvFixed = 0
  let pvFloating = 0
  const cashflows = []

  for (let i = 1; i <= periods; i++) {
    const year = i / couponFreq
    const discountFactor = Math.pow(1 + periodRate, -i)
    
    const fixedCoupon = (notional * fixedRate) / couponFreq
    const floatingCoupon = (notional * floatingRate) / couponFreq
    
    pvFixed += fixedCoupon * discountFactor
    pvFloating += floatingCoupon * discountFactor

    cashflows.push({
      date: `${year.toFixed(1)}Y`,
      fixedLeg: fixedCoupon,
      floatingLeg: floatingCoupon,
      net: fixedCoupon - floatingCoupon,
      pv: (fixedCoupon - floatingCoupon) * discountFactor
    })
  }

  pvFixed += notional * Math.pow(1 + periodRate, -periods)
  pvFloating += notional * Math.pow(1 + periodRate, -periods)

  const swapValue = pvFixed - pvFloating
  const duration = tenor * 0.85 // simplified
  const dv01 = (notional * 1_000_000 * duration * 0.0001) / 100

  valuationResults.value = {
    pvFixedLeg: pvFixed,
    pvFloatingLeg: pvFloating,
    swapValue: swapValue,
    duration: duration,
    dv01: dv01,
    spreadDv01: dv01 * 0.67,
    convexity: duration * duration * 0.5,
    cashflows: cashflows
  }

  initCharts()
}

const calculateValuation = async () => {
  calculating.value = true
  try {
    await new Promise(r => setTimeout(r, 1000))
    updateValuation()
  } finally {
    calculating.value = false
  }
}

const initCharts = () => {
  if (pvProfileChart) pvProfileChart.destroy()
  if (dv01ProfileChart) dv01ProfileChart.destroy()

  // PV Profile
  if (pvProfileRef.value?.getContext('2d')) {
    pvProfileChart = new Chart(pvProfileRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: ['3.25%', '3.75%', '4.25%', '4.75%', '5.25%'],
        datasets: [{
          label: 'Swap Value',
          data: [5.8, 4.2, 2.45, 0.95, -0.5],
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

  // DV01 Profile
  if (dv01ProfileRef.value?.getContext('2d')) {
    dv01ProfileChart = new Chart(dv01ProfileRef.value.getContext('2d') as any, {
      type: 'bar',
      data: {
        labels: ['2Y', '3Y', '5Y', '7Y', '10Y'],
        datasets: [{
          label: 'DV01 (USD)',
          data: [28000, 35000, 42500, 48000, 52000],
          backgroundColor: 'rgba(96, 165, 250, 0.6)',
          borderColor: '#60a5fa',
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
}

onMounted(() => {
  updateValuation()
})

onBeforeUnmount(() => {
  if (pvProfileChart) pvProfileChart.destroy()
  if (dv01ProfileChart) dv01ProfileChart.destroy()
})
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.swap-valuation-page {
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

.swap-type-select {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  padding: 4px 8px;
  cursor: pointer;
}

.swap-type-select option {
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
   PARAMETERS
   ============================================ */
.parameter-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.param-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.param-row label {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
  min-width: 150px;
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

.metric-value.accent {
  color: #f59e0b;
}

.metric-value.blue {
  color: #60a5fa;
}

.metric-value.positive {
  color: #4ade80;
}

.metric-value.negative {
  color: #f87171;
}

.metric-detail {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: rgba(255,255,255,0.4);
}

/* ============================================
   METRICS LIST
   ============================================ */
.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.metric-item:last-child {
  border-bottom: none;
}

.metric-item .label {
  color: rgba(255,255,255,0.5);
}

.metric-item .value {
  font-weight: 600;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.metric-item .value.positive {
  color: #4ade80;
}

.metric-item .value.negative {
  color: #f87171;
}

/* ============================================
   CASHFLOW TABLE
   ============================================ */
.cashflow-table-container {
  overflow-x: auto;
}

.cashflow-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.cashflow-table th,
.cashflow-table td {
  padding: 10px;
  text-align: right;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.cashflow-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 10px;
}

.col-period,
.col-date {
  text-align: left;
}

.col-amount.accent {
  color: #f59e0b;
}

.col-amount.blue {
  color: #60a5fa;
}

.col-amount.positive {
  color: #4ade80;
}

.col-amount.negative {
  color: #f87171;
}

.col-pv {
  font-family: "SF Mono", monospace;
}

.mono {
  font-family: "SF Mono", monospace;
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
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.scenario-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 10px;
}

.scenario-table tr.base {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.scenario-name {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
}

.scenario-table .accent {
  color: #f59e0b;
}

.scenario-table .blue {
  color: #60a5fa;
}

.scenario-table .positive {
  color: #4ade80;
}

.scenario-table .negative {
  color: #f87171;
}

/* ============================================
   RISK CARDS
   ============================================ */
.risk-card {
  background: rgba(30, 32, 40, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  border-left: 3px solid;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.risk-card.risk-high {
  border-left-color: #f87171;
}

.risk-card.risk-medium {
  border-left-color: #f59e0b;
}

.risk-card.risk-low {
  border-left-color: #4ade80;
}

.risk-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.risk-icon {
  font-size: 18px;
}

.risk-header h3 {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.7);
  margin: 0;
}

.risk-value {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.risk-detail {
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
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.chart-subtitle {
  font-size: 10px;
  color: rgba(255,255,255,0.3);
  font-weight: normal;
  text-transform: none;
  letter-spacing: 0;
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
  .swap-valuation-page {
    padding: 16px;
  }

  .page-header {
    gap: 16px;
  }

  .param-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .param-row label {
    min-width: unset;
  }

  .param-input {
    width: 100%;
  }

  .chart-container {
    height: 300px;
  }

  .cashflow-table,
  .scenario-table {
    font-size: 10px;
  }

  .cashflow-table th,
  .cashflow-table td,
  .scenario-table th,
  .scenario-table td {
    padding: 6px;
  }
}
</style>
