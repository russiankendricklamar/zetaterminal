<!-- src/pages/ForwardValuation.vue -->
<template>
  <div class="forward-valuation-page">
    
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Оценка форвардов</h1>
        <p class="page-subtitle">Справедливая стоимость и анализ форвардных контрактов</p>
      </div>
      
      <div class="header-right">
        <!-- Forward Type -->
        <div class="control-group">
          <label class="control-label">Тип форварда:</label>
          <select v-model="selectedForwardType" class="forward-type-select" @change="updateValuation">
            <option value="bond">Форвард на облигацию</option>
            <option value="fx">Валютный форвард</option>
            <option value="commodity">Commodity Forward</option>
            <option value="equity">Форвард на акцию</option>
            <option value="rate">Форвард на ставку</option>
          </select>
        </div>

        <!-- Calculation Button -->
        <button 
          @click="calculateValuation" 
          class="btn-primary"
          :disabled="calculating"
        >
          <span v-if="!calculating">Пересчитать</span>
          <span v-else>⟳ Считаю...</span>
        </button>
      </div>
    </div>

    <!-- Input Parameters -->
    <div class="grid-2">
      <!-- Underlying Asset Parameters -->
      <div class="card">
        <div class="card-header">
          <h3>Параметры базового актива</h3>
        </div>
        <div class="parameter-group">
          <div class="param-row">
            <label>Спот цена (S₀)</label>
            <input v-model.number="params.spotPrice" type="number" class="param-input" step="0.01" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Дивиденды / Купоны (%)</label>
            <input v-model.number="params.dividendYield" type="number" class="param-input" step="0.01" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Стоимость хранения (%)</label>
            <input v-model.number="params.carryingCost" type="number" class="param-input" step="0.01" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Удобство владения (Convenience Yield, %)</label>
            <input v-model.number="params.convenienceYield" type="number" class="param-input" step="0.01" @change="updateValuation" />
          </div>
        </div>
      </div>

      <!-- Forward Parameters -->
      <div class="card">
        <div class="card-header">
          <h3>Параметры форварда</h3>
        </div>
        <div class="parameter-group">
          <div class="param-row">
            <label>Время до экспирации (лет)</label>
            <input v-model.number="params.timeToMaturity" type="number" class="param-input" step="0.01" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Безрисковая ставка (%)</label>
            <input v-model.number="params.riskFreeRate" type="number" class="param-input" step="0.01" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Рыночная цена форварда</label>
            <input v-model.number="params.marketForwardPrice" type="number" class="param-input" step="0.01" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Репо ставка (%)</label>
            <input v-model.number="params.repoRate" type="number" class="param-input" step="0.01" @change="updateValuation" />
          </div>
        </div>
      </div>
    </div>

    <!-- Fair Value Results -->
    <div class="grid-3">
      <!-- Forward Price (Theoretical) -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Справедливая стоимость форвардного контракта</h3>
          <span class="metric-unit">Справедливая цена</span>
        </div>
        <div class="metric-value accent">
          {{ formatCurrency(valuationResults.fairForwardPrice) }}
        </div>
        <div class="metric-detail">
          <span class="detail-label">Модель:</span>
          <span class="detail-value">Cost-of-Carry</span>
        </div>
      </div>

      <!-- Market Price -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Рыночная цена форвардного контракта</h3>
          <span class="metric-unit">Рыночная цена</span>
        </div>
        <div class="metric-value blue">
          {{ formatCurrency(params.marketForwardPrice) }}
        </div>
        <div class="metric-detail">
          <span class="detail-label">Источник:</span>
          <span class="detail-value">Рыночные данные</span>
        </div>
      </div>

      <!-- Forward Value (Per Unit) -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Стоимость форвардного контракта</h3>
          <span class="metric-unit">По единице</span>
        </div>
        <div class="metric-value" :class="valuationResults.forwardValue >= 0 ? 'positive' : 'negative'">
          {{ formatCurrency(valuationResults.forwardValue) }}
        </div>
        <div class="metric-detail">
          <span class="detail-label">За контракт:</span>
          <span class="detail-value">{{ formatCompactCurrency(valuationResults.forwardValue * params.contractSize) }}</span>
        </div>
      </div>
    </div>

    <!-- Cost-of-Carry Breakdown -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Cost-of-Carry Модель</h3>
      </div>
      <div class="carry-breakdown">
        <div class="carry-item">
          <span class="carry-label">Спот цена актива (S₀)</span>
          <span class="carry-value accent">{{ formatCurrency(params.spotPrice) }}</span>
        </div>
        <div class="carry-item">
          <span class="carry-label">+ Безрисковая ставка (r)</span>
          <span class="carry-value">{{ (params.riskFreeRate).toFixed(3) }}%</span>
        </div>
        <div class="carry-item">
          <span class="carry-label">+ Стоимость хранения (c)</span>
          <span class="carry-value">{{ (params.carryingCost).toFixed(3) }}%</span>
        </div>
        <div class="carry-item">
          <span class="carry-label">- Дивиденды/Купоны (d)</span>
          <span class="carry-value negative">{{ (params.dividendYield).toFixed(3) }}%</span>
        </div>
        <div class="carry-item">
          <span class="carry-label">- Удобство владения (y)</span>
          <span class="carry-value negative">{{ (params.convenienceYield).toFixed(3) }}%</span>
        </div>
        <div class="carry-item total">
          <span class="carry-label">= Чистый Carry</span>
          <span class="carry-value cyan">
            {{ (params.riskFreeRate + params.carryingCost - params.dividendYield - params.convenienceYield).toFixed(3) }}%
          </span>
        </div>
        <div class="carry-item final">
          <span class="carry-label">= Справедливая стоимость форварда F</span>
          <span class="carry-value" :class="valuationResults.fairForwardPrice >= params.spotPrice ? 'positive' : 'negative'">
            {{ formatCurrency(valuationResults.fairForwardPrice) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Forward Value Components -->
    <div class="grid-3">
      <!-- Intrinsic Value -->
      <div class="card">
        <div class="card-header">
          <h3>Intrinsic Value</h3>
          <span class="card-subtitle">Текущая стоимость позиции</span>
        </div>
        <div class="value-breakdown">
          <div class="item">
            <span class="label">Спот цена</span>
            <span class="value accent">{{ formatCurrency(params.spotPrice) }}</span>
          </div>
          <div class="item">
            <span class="label">Striked цена</span>
            <span class="value blue">{{ formatCurrency(params.marketForwardPrice) }}</span>
          </div>
          <div class="item total">
            <span class="label">Intrinsic Value</span>
            <span class="value" :class="valuationResults.intrinsicValue >= 0 ? 'positive' : 'negative'">
              {{ valuationResults.intrinsicValue >= 0 ? '+' : '' }}{{ formatCurrency(valuationResults.intrinsicValue) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Time Value -->
      <div class="card">
        <div class="card-header">
          <h3>Time Value</h3>
          <span class="card-subtitle">Временная стоимость</span>
        </div>
        <div class="value-breakdown">
          <div class="item">
            <span class="label">Fair Forward Price</span>
            <span class="value accent">{{ formatCurrency(valuationResults.fairForwardPrice) }}</span>
          </div>
          <div class="item">
            <span class="label">Striked цена</span>
            <span class="value blue">{{ formatCurrency(params.marketForwardPrice) }}</span>
          </div>
          <div class="item total">
            <span class="label">Time Value</span>
            <span class="value" :class="valuationResults.timeValue >= 0 ? 'positive' : 'negative'">
              {{ valuationResults.timeValue >= 0 ? '+' : '' }}{{ formatCurrency(valuationResults.timeValue) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Total Value -->
      <div class="card">
        <div class="card-header">
          <h3>Total Forward Value</h3>
          <span class="card-subtitle">Справедливая стоимость позиции</span>
        </div>
        <div class="value-breakdown">
          <div class="item">
            <span class="label">Intrinsic Value</span>
            <span class="value" :class="valuationResults.intrinsicValue >= 0 ? 'positive' : 'negative'">
              {{ valuationResults.intrinsicValue >= 0 ? '+' : '' }}{{ formatCurrency(valuationResults.intrinsicValue) }}
            </span>
          </div>
          <div class="item">
            <span class="label">Time Value</span>
            <span class="value" :class="valuationResults.timeValue >= 0 ? 'positive' : 'negative'">
              {{ valuationResults.timeValue >= 0 ? '+' : '' }}{{ formatCurrency(valuationResults.timeValue) }}
            </span>
          </div>
          <div class="item total">
            <span class="label">Total Value</span>
            <span class="value accent">
              {{ valuationResults.totalValue >= 0 ? '+' : '' }}{{ formatCurrency(valuationResults.totalValue) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Forward Price Profile -->
    <div class="grid-2">
      <!-- Price vs Spot -->
      <div class="card">
        <div class="chart-header">
          <h3>Forward Price Profile</h3>
          <span class="chart-subtitle">F(S) зависимость от спот цены</span>
        </div>
        <div class="chart-container">
          <canvas ref="priceProfileRef"></canvas>
        </div>
      </div>

      <!-- Value vs Time -->
      <div class="card">
        <div class="chart-header">
          <h3>Forward Value vs Time</h3>
          <span class="chart-subtitle">Эволюция стоимости по времени</span>
        </div>
        <div class="chart-container">
          <canvas ref="valueVsTimeRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Scenario Analysis -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Анализ сценариев</h3>
        <span class="card-subtitle">Forward value при различных движениях спота</span>
      </div>
      <div class="scenario-table-container">
        <table class="scenario-table">
          <thead>
            <tr>
              <th>Сценарий</th>
              <th>Spot Price</th>
              <th>% Change</th>
              <th>Forward Value</th>
              <th>P&L (Лонг)</th>
              <th>P&L (Шорт)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="scenario in scenarioAnalysis" :key="scenario.id" :class="scenario.isBase ? 'base' : ''">
              <td class="scenario-name">{{ scenario.name }}</td>
              <td class="spot-price mono">{{ formatCurrency(scenario.spotPrice) }}</td>
              <td class="change mono" :class="scenario.change >= 0 ? 'positive' : 'negative'">
                {{ scenario.change >= 0 ? '+' : '' }}{{ scenario.change.toFixed(1) }}%
              </td>
              <td class="forward-value mono" :class="scenario.forwardValue >= 0 ? 'positive' : 'negative'">
                {{ scenario.forwardValue >= 0 ? '+' : '' }}{{ formatCurrency(scenario.forwardValue) }}
              </td>
              <td class="pnl mono" :class="scenario.pnlLong >= 0 ? 'positive' : 'negative'">
                {{ scenario.pnlLong >= 0 ? '+' : '' }}{{ formatCompactCurrency(scenario.pnlLong) }}
              </td>
              <td class="pnl mono" :class="scenario.pnlShort >= 0 ? 'positive' : 'negative'">
                {{ scenario.pnlShort >= 0 ? '+' : '' }}{{ formatCompactCurrency(scenario.pnlShort) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Sensitivity Analysis -->
    <div class="grid-2">
      <!-- Sensitivity to Spot Price -->
      <div class="card">
        <div class="chart-header">
          <h3>Delta (∂F/∂S)</h3>
          <span class="chart-subtitle">Чувствительность к спот цене</span>
        </div>
        <div class="sensitivity-metrics">
          <div class="sens-item">
            <span class="label">Дельта (Delta)</span>
            <span class="value accent">{{ valuationResults.delta.toFixed(4) }}</span>
          </div>
          <div class="sens-item">
            <span class="label">P&L на 1% спота</span>
            <span class="value blue">{{ formatCompactCurrency(params.spotPrice * params.contractSize * 0.01 * valuationResults.delta) }}</span>
          </div>
          <div class="sens-item">
            <span class="label">Break-even цена</span>
            <span class="value cyan">{{ formatCurrency(params.marketForwardPrice) }}</span>
          </div>
        </div>
      </div>

      <!-- Sensitivity to Interest Rates -->
      <div class="card">
        <div class="chart-header">
          <h3>Rho (∂F/∂r)</h3>
          <span class="chart-subtitle">Чувствительность к ставкам</span>
        </div>
        <div class="sensitivity-metrics">
          <div class="sens-item">
            <span class="label">Rho (Rho)</span>
            <span class="value accent">{{ valuationResults.rho.toFixed(4) }}</span>
          </div>
          <div class="sens-item">
            <span class="label">P&L на 1% ставки</span>
            <span class="value blue">{{ formatCompactCurrency(valuationResults.rho * params.contractSize * 0.01) }}</span>
          </div>
          <div class="sens-item">
            <span class="label">Текущая ставка</span>
            <span class="value cyan">{{ (params.riskFreeRate).toFixed(3) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span>• Модель: Cost-of-Carry (no-arbitrage)</span>
      <span>• Метод: Continuous compounding</span>
      <span>• Обновление: В реальном времени</span>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'

const selectedForwardType = ref('bond')
const calculating = ref(false)

// Parameters
const params = ref({
  spotPrice: 100,
  dividendYield: 2.5,           // % (дивиденды/купоны)
  carryingCost: 0.5,            // % (стоимость хранения)
  convenienceYield: 0,          // % (удобство владения)
  timeToMaturity: 0.25,         // лет
  riskFreeRate: 4.25,           // %
  marketForwardPrice: 101.50,   // рыночная цена форварда
  repoRate: 4.2,                // %
  contractSize: 1_000_000       // условных единиц
})

// Valuation Results
const valuationResults = computed(() => {
  const r = params.value.riskFreeRate / 100
  const d = params.value.dividendYield / 100
  const c = params.value.carryingCost / 100
  const y = params.value.convenienceYield / 100
  const T = params.value.timeToMaturity
  const S0 = params.value.spotPrice

  // Fair Forward Price: F = S0 * e^((r + c - d - y) * T)
  const netCarry = r + c - d - y
  const fairForwardPrice = S0 * Math.exp(netCarry * T)

  // Forward Value = (S - K) / e^(r*T) для лонга
  // Где K - страйк (рыночная цена форварда)
  const K = params.value.marketForwardPrice
  const forwardValue = (S0 - K) / Math.exp(r * T)

  const intrinsicValue = S0 - K
  const timeValue = forwardValue - intrinsicValue
  const totalValue = forwardValue

  // Greeks
  const delta = Math.exp(-r * T)  // всегда близко к 1 для форвардов
  const rho = S0 * T * Math.exp((r + c - d - y) * T)  // чувствительность к ставке

  return {
    fairForwardPrice,
    forwardValue,
    intrinsicValue,
    timeValue,
    totalValue,
    delta,
    rho
  }
})

// Scenario Analysis
const scenarioAnalysis = computed(() => {
  const baseSpot = params.value.spotPrice
  const K = params.value.marketForwardPrice
  const r = params.value.riskFreeRate / 100
  const T = params.value.timeToMaturity

  const scenarios = []
  const spotPrices = [
    baseSpot * 0.8,
    baseSpot * 0.9,
    baseSpot,
    baseSpot * 1.1,
    baseSpot * 1.2
  ]

  spotPrices.forEach((spot, idx) => {
    const change = ((spot - baseSpot) / baseSpot) * 100
    const forwardValue = (spot - K) / Math.exp(r * T)
    const pnlLong = (spot - K)  // при экспирации
    const pnlShort = (K - spot) // при экспирации

    scenarios.push({
      id: idx,
      name: idx === 2 ? 'Base Case' : (idx < 2 ? 'Bear' : 'Bull'),
      spotPrice: spot,
      change: change,
      forwardValue: forwardValue,
      pnlLong: pnlLong * params.value.contractSize,
      pnlShort: pnlShort * params.value.contractSize,
      isBase: idx === 2
    })
  })

  return scenarios
})

// Chart References
const priceProfileRef = ref<HTMLCanvasElement | null>(null)
const valueVsTimeRef = ref<HTMLCanvasElement | null>(null)

let priceProfileChart: Chart | null = null
let valueVsTimeChart: Chart | null = null

// Methods
const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(val)
}

const formatCompactCurrency = (val: number) => {
  if (Math.abs(val) >= 1_000_000) {
    return (val / 1_000_000).toFixed(1) + 'М'
  }
  return '$' + (val / 1000).toFixed(0) + 'K'
}

const updateValuation = () => {
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
  if (priceProfileChart) priceProfileChart.destroy()
  if (valueVsTimeChart) valueVsTimeChart.destroy()

  // Forward Price Profile
  if (priceProfileRef.value?.getContext('2d')) {
    const spotRange = []
    const forwardPrices = []
    
    for (let i = 0.7; i <= 1.3; i += 0.05) {
      const spot = params.value.spotPrice * i
      spotRange.push(spot)
      
      const r = params.value.riskFreeRate / 100
      const d = params.value.dividendYield / 100
      const c = params.value.carryingCost / 100
      const y = params.value.convenienceYield / 100
      const T = params.value.timeToMaturity
      
      const forwardPrice = spot * Math.exp((r + c - d - y) * T)
      forwardPrices.push(forwardPrice)
    }

    priceProfileChart = new Chart(priceProfileRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: spotRange.map(s => s.toFixed(1)),
        datasets: [
          {
            label: 'Fair Forward Price',
            data: forwardPrices,
            borderColor: '#60a5fa',
            backgroundColor: 'rgba(96, 165, 250, 0.08)',
            fill: true,
            tension: 0.4,
            pointRadius: 2,
            borderWidth: 2
          },
          {
            label: 'Market Price',
            data: Array(forwardPrices.length).fill(params.value.marketForwardPrice),
            borderColor: '#f59e0b',
            backgroundColor: 'transparent',
            fill: false,
            tension: 0,
            borderDash: [5, 5],
            pointRadius: 0,
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

  // Forward Value vs Time
  if (valueVsTimeRef.value?.getContext('2d')) {
    const timePoints = []
    const values = []
    
    for (let t = 0; t <= params.value.timeToMaturity; t += params.value.timeToMaturity / 12) {
      const r = params.value.riskFreeRate / 100
      const S0 = params.value.spotPrice
      const K = params.value.marketForwardPrice
      
      const forwardValue = (S0 - K) / Math.exp(r * t)
      timePoints.push((t * 12).toFixed(0))
      values.push(forwardValue)
    }

    valueVsTimeChart = new Chart(valueVsTimeRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: timePoints,
        datasets: [{
          label: 'Forward Value',
          data: values,
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
  initCharts()
})

onBeforeUnmount(() => {
  if (priceProfileChart) priceProfileChart.destroy()
  if (valueVsTimeChart) valueVsTimeChart.destroy()
})
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.forward-valuation-page {
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

.forward-type-select {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  padding: 4px 8px;
  cursor: pointer;
}

.forward-type-select option {
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
  min-width: 180px;
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
   CARRY BREAKDOWN
   ============================================ */
.carry-breakdown {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.carry-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: rgba(255,255,255,0.02);
  border-radius: 6px;
  font-size: 12px;
}

.carry-label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.carry-value {
  font-weight: 700;
  font-family: "SF Mono", monospace;
  color: #fff;
}

.carry-value.negative {
  color: #f87171;
}

.carry-value.cyan {
  color: #06b6d4;
}

.carry-item.total {
  background: rgba(255,255,255,0.04);
  border-top: 1px solid rgba(255,255,255,0.1);
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.carry-item.final {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

/* ============================================
   VALUE BREAKDOWN
   ============================================ */
.value-breakdown {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.item .label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.item .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.item .value.accent {
  color: #f59e0b;
}

.item .value.blue {
  color: #60a5fa;
}

.item .value.positive {
  color: #4ade80;
}

.item .value.negative {
  color: #f87171;
}

.item.total {
  border-top: 1px solid rgba(255,255,255,0.1);
  border-bottom: none;
  padding-top: 10px;
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

.chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

/* ============================================
   SCENARIO TABLE
   ============================================ */
.scenario-table-container {
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

.scenario-name {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
}

.spot-price,
.change,
.forward-value,
.pnl {
  font-family: "SF Mono", monospace;
}

.scenario-table .positive {
  color: #4ade80;
}

.scenario-table .negative {
  color: #f87171;
}

.scenario-table tr.base {
  background: rgba(59, 130, 246, 0.1);
}

/* ============================================
   SENSITIVITY METRICS
   ============================================ */
.sensitivity-metrics {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sens-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.sens-item .label {
  color: rgba(255,255,255,0.6);
}

.sens-item .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.sens-item .value.accent {
  color: #f59e0b;
}

.sens-item .value.blue {
  color: #60a5fa;
}

.sens-item .value.cyan {
  color: #06b6d4;
}

/* ============================================
   ARBITRAGE ANALYSIS
   ============================================ */
.arbitrage-analysis {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.arb-section {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  padding: 16px;
}

.arb-section h4 {
  font-size: 12px;
  color: rgba(255,255,255,0.7);
  margin: 0 0 10px 0;
  font-weight: 600;
}

.arb-strategy {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.strategy-label {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.strategy-steps {
  margin: 6px 0;
  padding-left: 20px;
  font-size: 10px;
  color: rgba(255,255,255,0.5);
}

.strategy-steps li {
  margin: 2px 0;
}

.profit-value {
  font-size: 12px;
  font-weight: 700;
  font-family: "SF Mono", monospace;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.profit-value.positive {
  color: #4ade80;
}

/* ============================================
   FORMULAS GRID
   ============================================ */
.formulas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.formula-card {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.formula-card h4 {
  font-size: 11px;
  color: rgba(255,255,255,0.7);
  margin: 0;
  font-weight: 600;
}

.formula {
  font-size: 10px;
  color: #60a5fa;
  font-family: "SF Mono", monospace;
  background: rgba(96, 165, 250, 0.1);
  padding: 6px;
  border-radius: 4px;
}

.description {
  font-size: 9px;
  color: rgba(255,255,255,0.4);
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

  .arbitrage-analysis {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .forward-valuation-page {
    padding: 16px;
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

  .scenario-table {
    font-size: 10px;
  }

  .scenario-table th,
  .scenario-table td {
    padding: 6px;
  }

  .formulas-grid {
    grid-template-columns: 1fr;
  }
}
</style>
