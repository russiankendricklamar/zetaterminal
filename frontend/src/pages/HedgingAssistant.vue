<!-- src/pages/HedgingAssistant.vue -->
<template>
  <div class="hedging-assistant-page">
    
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Помощник по хеджированию</h1>
        <p class="page-subtitle">Репликация и хеджирование портфеля инструментами</p>
      </div>
      
      <div class="header-right">
        <!-- Position Type -->
        <div class="control-group">
          <label class="control-label">Позиция:</label>
          <select v-model="selectedPosition" class="position-select" @change="updateHedge">
            <option value="long-bond">Long позиция в облигациях</option>
            <option value="long-stock">Long позиция в акциях</option>
            <option value="long-swap">Long Interest Rate Swap</option>
            <option value="long-credit">Long кредитная экспозиция</option>
          </select>
        </div>

        <!-- Hedging Strategy -->
        <div class="control-group">
          <label class="control-label">Стратегия:</label>
          <select v-model="selectedStrategy" class="strategy-select" @change="updateHedge">
            <option value="delta">Delta хедж</option>
            <option value="duration">Совпадение Duration</option>
            <option value="regression">Регрессионный хедж</option>
            <option value="optimal">Оптимальная репликация</option>
          </select>
        </div>

        <!-- Calculate Button -->
        <button @click="calculateHedge" class="btn-primary" :disabled="calculating">
          <span v-if="!calculating">Пересчитать хедж</span>
          <span v-else>↺ Считаю...</span>
        </button>
      </div>
    </div>

    <!-- Position Overview -->
    <div class="grid-3">
      <div class="overview-card">
        <div class="card-header">
          <h3>Исходная позиция</h3>
        </div>
        <div class="overview-metrics">
          <div class="metric">
            <span class="label">Инструмент</span>
            <span class="value">{{ positionInfo.name }}</span>
          </div>
          <div class="metric">
            <span class="label">Размер</span>
            <span class="value mono">{{ formatCurrency(positionInfo.size) }}</span>
          </div>
          <div class="metric">
            <span class="label">Duration</span>
            <span class="value mono">{{ positionInfo.duration.toFixed(2) }}</span>
          </div>
          <div class="metric">
            <span class="label">Экспозиция</span>
            <span class="value accent mono">{{ formatCompactCurrency(positionInfo.exposure) }}</span>
          </div>
        </div>
      </div>

      <div class="overview-card">
        <div class="card-header">
          <h3>Риск позиции</h3>
        </div>
        <div class="overview-metrics">
          <div class="metric">
            <span class="label">DV01</span>
            <span class="value" :class="positionInfo.dv01 >= 0 ? 'positive' : 'negative'">
              {{ formatCompactCurrency(positionInfo.dv01) }}
            </span>
          </div>
          <div class="metric">
            <span class="label">Vega (Vol)</span>
            <span class="value" :class="positionInfo.vega >= 0 ? 'positive' : 'negative'">
              {{ formatCompactCurrency(positionInfo.vega) }}
            </span>
          </div>
          <div class="metric">
            <span class="label">Gamma</span>
            <span class="value mono">{{ positionInfo.gamma.toFixed(4) }}</span>
          </div>
          <div class="metric">
            <span class="label">Max Loss (1σ)</span>
            <span class="value negative">{{ formatCompactCurrency(positionInfo.maxLoss) }}</span>
          </div>
        </div>
      </div>

      <div class="overview-card">
        <div class="card-header">
          <h3>Хедж требования</h3>
        </div>
        <div class="overview-metrics">
          <div class="metric">
            <span class="label">Целевой DV01</span>
            <span class="value cyan mono">{{ formatCompactCurrency(hedgeRequirements.targetDv01) }}</span>
          </div>
          <div class="metric">
            <span class="label">Целевая Vega</span>
            <span class="value blue mono">{{ formatCompactCurrency(hedgeRequirements.targetVega) }}</span>
          </div>
          <div class="metric">
            <span class="label">Корреляция цели</span>
            <span class="value mono">{{ (hedgeRequirements.correlation * 100).toFixed(1) }}%</span>
          </div>
          <div class="metric">
            <span class="label">Эффективность</span>
            <span class="value green mono">{{ (hedgeRequirements.efficiency * 100).toFixed(1) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Hedging Instruments Selection -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Доступные инструменты для хеджирования</h3>
        <span class="card-subtitle">Выберите инструменты для репликации позиции</span>
      </div>
      <div class="instruments-grid">
        <div 
          v-for="instrument in availableInstruments" 
          :key="instrument.id"
          class="instrument-card"
          :class="{ selected: selectedInstruments.includes(instrument.id) }"
          @click="toggleInstrument(instrument.id)"
        >
          <div class="instrument-header">
            <span class="instrument-name">{{ instrument.name }}</span>
            <span class="instrument-type">{{ instrument.type }}</span>
          </div>
          <div class="instrument-metrics">
            <div class="metric-row">
              <span class="label">DV01</span>
              <span class="value">{{ instrument.dv01.toFixed(0) }}</span>
            </div>
            <div class="metric-row">
              <span class="label">Vega</span>
              <span class="value">{{ instrument.vega.toFixed(0) }}</span>
            </div>
            <div class="metric-row">
              <span class="label">Корр</span>
              <span class="value">{{ (instrument.correlation * 100).toFixed(0) }}%</span>
            </div>
            <div class="metric-row">
              <span class="label">Стоимость</span>
              <span class="value">{{ instrument.cost }}bp</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Hedge Portfolio -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Портфель хеджирования</h3>
        <span class="card-subtitle">Рекомендуемые размеры позиций</span>
      </div>
      <div class="hedge-table-container">
        <table class="hedge-table">
          <thead>
            <tr>
              <th class="col-instrument">Инструмент</th>
              <th class="col-quantity">Количество</th>
              <th class="col-size">Размер (М)</th>
              <th class="col-dv01">DV01 вклад</th>
              <th class="col-vega">Vega вклад</th>
              <th class="col-cost">Стоимость (bp)</th>
              <th class="col-action">Действие</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="hedge in hedgePortfolio" :key="hedge.id" :class="hedge.direction.toLowerCase()">
              <td class="col-instrument">
                <span class="instrument-badge" :class="hedge.type">{{ hedge.instrument }}</span>
              </td>
              <td class="col-quantity mono">{{ hedge.quantity.toFixed(2) }}</td>
              <td class="col-size accent">{{ formatCompactCurrency(hedge.size) }}</td>
              <td class="col-dv01" :class="hedge.dv01Contribution >= 0 ? 'positive' : 'negative'">
                {{ hedge.dv01Contribution >= 0 ? '+' : '' }}{{ formatCompactCurrency(hedge.dv01Contribution) }}
              </td>
              <td class="col-vega" :class="hedge.vegaContribution >= 0 ? 'positive' : 'negative'">
                {{ hedge.vegaContribution >= 0 ? '+' : '' }}{{ formatCompactCurrency(hedge.vegaContribution) }}
              </td>
              <td class="col-cost mono">{{ hedge.cost }}</td>
              <td class="col-action">
                <button @click="executeHedge(hedge.id)" class="btn-action">
                  {{ hedge.executed ? '✓' : '↓' }}
                </button>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="total-row">
              <td colspan="2"><strong>ИТОГО ХЕДЖ</strong></td>
              <td class="accent"><strong>{{ formatCompactCurrency(totalHedgeSize) }}</strong></td>
              <td class="positive"><strong>{{ formatCompactCurrency(totalDv01) }}</strong></td>
              <td class="blue"><strong>{{ formatCompactCurrency(totalVega) }}</strong></td>
              <td class="mono"><strong>{{ totalCost.toFixed(1) }}bp</strong></td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Hedge Effectiveness -->
    <div class="grid-2">
      <!-- Before/After Comparison -->
      <div class="card">
        <div class="card-header">
          <h3>Сравнение: До/После хеджирования</h3>
        </div>
        <div class="comparison-table-container">
          <table class="comparison-table">
            <thead>
              <tr>
                <th>Метрика</th>
                <th>До хеджа</th>
                <th>После хеджа</th>
                <th>Снижение</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="metric-name">DV01 (М/bp)</td>
                <td class="value accent">{{ formatCompactCurrency(positionInfo.dv01) }}</td>
                <td class="value cyan">{{ formatCompactCurrency(positionInfo.dv01 - totalDv01) }}</td>
                <td class="value green">{{ ((totalDv01 / positionInfo.dv01) * 100).toFixed(1) }}%</td>
              </tr>
              <tr>
                <td class="metric-name">Vega (М/1%)</td>
                <td class="value accent">{{ formatCompactCurrency(positionInfo.vega) }}</td>
                <td class="value cyan">{{ formatCompactCurrency(positionInfo.vega - totalVega) }}</td>
                <td class="value green">{{ ((totalVega / positionInfo.vega) * 100).toFixed(1) }}%</td>
              </tr>
              <tr>
                <td class="metric-name">Max Loss (1σ)</td>
                <td class="value negative">{{ formatCompactCurrency(positionInfo.maxLoss) }}</td>
                <td class="value cyan">{{ formatCompactCurrency(positionInfo.maxLoss * 0.15) }}</td>
                <td class="value green">{{ 85 }}%</td>
              </tr>
              <tr>
                <td class="metric-name">Correlation</td>
                <td class="value">-</td>
                <td class="value blue mono">{{ (hedgeCorrelation * 100).toFixed(1) }}%</td>
                <td class="value green">{{ (hedgeCorrelation * 100).toFixed(1) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Risk Reduction -->
      <div class="card">
        <div class="card-header">
          <h3>Снижение риска</h3>
        </div>
        <div class="risk-reduction">
          <div class="reduction-item">
            <span class="risk-type">Направленный риск</span>
            <div class="bar-container">
              <div class="bar-before" style="width: 100%; height: 8px; background: rgba(248, 113, 113, 0.4);"></div>
              <div class="bar-after" style="width: 5%; height: 8px; background: rgba(74, 222, 128, 0.6); position: relative; top: -8px;"></div>
            </div>
            <span class="reduction-text">95% снижено</span>
          </div>
          <div class="reduction-item">
            <span class="risk-type">Риск Duration</span>
            <div class="bar-container">
              <div class="bar-before" style="width: 100%; height: 8px; background: rgba(248, 113, 113, 0.4);"></div>
              <div class="bar-after" style="width: 8%; height: 8px; background: rgba(74, 222, 128, 0.6); position: relative; top: -8px;"></div>
            </div>
            <span class="reduction-text">92% снижено</span>
          </div>
          <div class="reduction-item">
            <span class="risk-type">Риск Vol</span>
            <div class="bar-container">
              <div class="bar-before" style="width: 100%; height: 8px; background: rgba(248, 113, 113, 0.4);"></div>
              <div class="bar-after" style="width: 15%; height: 8px; background: rgba(74, 222, 128, 0.6); position: relative; top: -8px;"></div>
            </div>
            <span class="reduction-text">85% снижено</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Hedge Cost Analysis -->
    <div class="grid-2">
      <!-- Cost Breakdown -->
      <div class="card">
        <div class="chart-header">
          <h3>Стоимость хеджирования</h3>
          <span class="chart-subtitle">Разложение по инструментам</span>
        </div>
        <div class="cost-breakdown">
          <div v-for="hedge in hedgePortfolio" :key="hedge.id" class="cost-item">
            <span class="instrument-name">{{ hedge.instrument }}</span>
            <div class="cost-bar-container">
              <div 
                class="cost-bar"
                :style="{ width: Math.min(100, Math.max(2, (Math.abs(hedge.cost) / Math.max(totalCost, 1)) * 100)) + '%' }"
              ></div>
            </div>
            <span class="cost-value mono">{{ hedge.cost.toFixed(1) }}bp</span>
          </div>
          <div class="cost-item total">
            <span class="instrument-name"><strong>ОБЩАЯ СТОИМОСТЬ</strong></span>
            <div class="cost-bar-container total-bar-container">
              <div 
                class="cost-bar total-bar"
                :style="{ width: '100%' }"
              ></div>
            </div>
            <span class="cost-value total-value mono"><strong>{{ totalCost.toFixed(1) }}bp</strong></span>
          </div>
        </div>
      </div>

      <!-- Optimal Replication -->
      <div class="card">
        <div class="chart-header">
          <h3>Оптимальная репликация</h3>
          <span class="chart-subtitle">Коэффициенты регрессии</span>
        </div>
        <div class="regression-info">
          <div class="regression-item">
            <span class="variable">β (Beta)</span>
            <span class="value mono">{{ regressionCoefficients.beta.toFixed(3) }}</span>
          </div>
          <div class="regression-item">
            <span class="variable">α (Alpha)</span>
            <span class="value mono">{{ regressionCoefficients.alpha.toFixed(4) }}</span>
          </div>
          <div class="regression-item">
            <span class="variable">R² (Adjusted)</span>
            <span class="value mono">{{ (regressionCoefficients.rSquared * 100).toFixed(2) }}%</span>
          </div>
          <div class="regression-item">
            <span class="variable">Станд. ошибка</span>
            <span class="value mono">{{ regressionCoefficients.stdError.toFixed(4) }}</span>
          </div>
          <div class="regression-item">
            <span class="variable">RMSE</span>
            <span class="value mono">{{ regressionCoefficients.rmse.toFixed(2) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Scenario Analysis -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Анализ сценариев: Эффективность хеджа</h3>
        <span class="card-subtitle">P&L позиции с хеджем в различных сценариях</span>
      </div>
      <div class="scenario-table-container">
        <table class="scenario-table">
          <thead>
            <tr>
              <th>Сценарий</th>
              <th>Движение рынка</th>
              <th>Исходный P&L</th>
              <th>P&L хеджа</th>
              <th>Чистый P&L</th>
              <th>Эффективность хеджа</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="scenario in scenarioAnalysis" :key="scenario.id" :class="scenario.id === 3 ? 'base' : ''">
              <td class="scenario-name">{{ scenario.name }}</td>
              <td class="market-move" :class="scenario.move >= 0 ? 'positive' : 'negative'">
                {{ scenario.move >= 0 ? '+' : '' }}{{ scenario.move.toFixed(0) }}bp
              </td>
              <td class="pnl" :class="scenario.originalPnL >= 0 ? 'positive' : 'negative'">
                {{ scenario.originalPnL >= 0 ? '+' : '' }}{{ formatCompactCurrency(scenario.originalPnL) }}
              </td>
              <td class="pnl" :class="scenario.hedgePnL >= 0 ? 'positive' : 'negative'">
                {{ scenario.hedgePnL >= 0 ? '+' : '' }}{{ formatCompactCurrency(scenario.hedgePnL) }}
              </td>
              <td class="pnl" :class="scenario.netPnL >= 0 ? 'positive' : 'negative'">
                {{ scenario.netPnL >= 0 ? '+' : '' }}{{ formatCompactCurrency(scenario.netPnL) }}
              </td>
              <td class="effectiveness mono">{{ (scenario.effectiveness * 100).toFixed(1) }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Execution Status -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Статус выполнения</h3>
        <span class="card-subtitle">Ордера и исполнение</span>
      </div>
      <div class="execution-status">
        <div v-for="hedge in hedgePortfolio" :key="hedge.id" class="execution-item">
          <div class="execution-header">
            <span class="instrument-badge" :class="hedge.type">{{ hedge.instrument }}</span>
            <span class="quantity">{{ hedge.quantity.toFixed(2) }} контрактов</span>
            <span class="status" :class="hedge.executed ? 'executed' : 'pending'">
              {{ hedge.executed ? '✓ Исполнено' : 'Ожидание' }}
            </span>
          </div>
          <div class="execution-detail">
            <span>Размер: {{ formatCompactCurrency(hedge.size) }}</span>
            <span>Направление: {{ hedge.direction }}</span>
            <span>Цена: {{ hedge.price }}</span>
            <span v-if="hedge.executed">Время: {{ hedge.executionTime }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span>• Метод: Регрессионное оптимальное хеджирование</span>
      <span>• Обновление: В реальном времени</span>
      <span>• Запас прочности: 10% (buffer)</span>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const selectedPosition = ref('long-bond')
const selectedStrategy = ref('optimal')
const calculating = ref(false)
const selectedInstruments = ref<number[]>([1, 2, 3])

// Position Information
const positionInfo = ref({
  name: 'US Treasury 10Y Bond',
  size: 100,
  duration: 8.5,
  exposure: 850000,
  dv01: 85000,
  vega: 18200,
  gamma: 0.0025,
  maxLoss: -425000
})

// Hedge Requirements
const hedgeRequirements = ref({
  targetDv01: 0,
  targetVega: 0,
  correlation: 0.95,
  efficiency: 0.92
})

// Available Instruments
const availableInstruments = ref([
  {
    id: 1,
    name: 'US Treasury 2Y',
    type: 'Bond',
    dv01: 19500,
    vega: 3200,
    correlation: 0.98,
    cost: 2
  },
  {
    id: 2,
    name: 'US Treasury 5Y',
    type: 'Bond',
    dv01: 48000,
    vega: 8500,
    correlation: 0.97,
    cost: 2
  },
  {
    id: 3,
    name: 'IRS Receiver 10Y',
    type: 'Swap',
    dv01: 82000,
    vega: 17800,
    correlation: 0.99,
    cost: 3
  },
  {
    id: 4,
    name: 'Treasury Futures',
    type: 'Futures',
    dv01: 28500,
    vega: 4200,
    correlation: 0.96,
    cost: 1
  },
  {
    id: 5,
    name: 'Payer Swaption 5Y2Y',
    type: 'Option',
    dv01: 12000,
    vega: 45000,
    correlation: 0.85,
    cost: 25
  }
])

// Hedge Portfolio
const hedgePortfolio = ref([
  {
    id: 1,
    instrument: 'US Treasury 5Y',
    type: 'bond',
    quantity: 1.75,
    size: 84000,
    direction: 'Short',
    dv01Contribution: -84000,
    vegaContribution: -14875,
    cost: 3.5,
    executed: true,
    price: '98.45',
    executionTime: '10:15 AM'
  },
  {
    id: 2,
    instrument: 'IRS Receiver 10Y',
    type: 'swap',
    quantity: 1.04,
    size: 104000,
    direction: 'Receiver',
    dv01Contribution: -85280,
    vegaContribution: -18512,
    cost: 3.12,
    executed: true,
    price: 'Par',
    executionTime: '10:22 AM'
  }
])

const totalHedgeSize = computed(() => {
  return hedgePortfolio.value.reduce((sum, h) => sum + h.size, 0)
})

const totalDv01 = computed(() => {
  return hedgePortfolio.value.reduce((sum, h) => sum + h.dv01Contribution, 0)
})

const totalVega = computed(() => {
  return hedgePortfolio.value.reduce((sum, h) => sum + h.vegaContribution, 0)
})

const totalCost = computed(() => {
  return hedgePortfolio.value.reduce((sum, h) => sum + h.cost, 0)
})

const hedgeCorrelation = computed(() => {
  return 0.94
})

// Regression Coefficients
const regressionCoefficients = ref({
  beta: 1.002,
  alpha: 0.0015,
  rSquared: 0.9487,
  stdError: 0.0025,
  rmse: 42.35
})

// Scenario Analysis
const scenarioAnalysis = ref([
  {
    id: 1,
    name: 'Bear (-200bp)',
    move: -200,
    originalPnL: -1700000,
    hedgePnL: 1680000,
    netPnL: -20000,
    effectiveness: 0.988
  },
  {
    id: 2,
    name: 'Bear (-100bp)',
    move: -100,
    originalPnL: -850000,
    hedgePnL: 840000,
    netPnL: -10000,
    effectiveness: 0.988
  },
  {
    id: 3,
    name: 'Base Case',
    move: 0,
    originalPnL: 0,
    hedgePnL: 0,
    netPnL: 0,
    effectiveness: 1.0
  },
  {
    id: 4,
    name: 'Bull (+100bp)',
    move: 100,
    originalPnL: 850000,
    hedgePnL: -840000,
    netPnL: 10000,
    effectiveness: 0.988
  },
  {
    id: 5,
    name: 'Bull (+200bp)',
    move: 200,
    originalPnL: 1700000,
    hedgePnL: -1680000,
    netPnL: 20000,
    effectiveness: 0.988
  }
])

// Methods
const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
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

const toggleInstrument = (id: number) => {
  const index = selectedInstruments.value.indexOf(id)
  if (index > -1) {
    selectedInstruments.value.splice(index, 1)
  } else {
    selectedInstruments.value.push(id)
  }
}

const updateHedge = () => {
  // Update hedge calculation
}

const calculateHedge = async () => {
  calculating.value = true
  try {
    await new Promise(r => setTimeout(r, 1500))
    // Recalculate hedge
  } finally {
    calculating.value = false
  }
}

const executeHedge = (id: number) => {
  const hedge = hedgePortfolio.value.find(h => h.id === id)
  if (hedge) {
    hedge.executed = true
    hedge.executionTime = new Date().toLocaleTimeString()
  }
}

onMounted(() => {
  // Initialize
})
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.hedging-assistant-page {
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
.strategy-select {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  padding: 4px 8px;
  cursor: pointer;
}

.position-select option,
.strategy-select option {
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
   OVERVIEW CARDS
   ============================================ */
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.overview-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 16px;
  box-shadow: 
    0 20px 40px -10px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.overview-card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 
    0 25px 50px -10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.overview-metrics {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.metric .label {
  color: rgba(255,255,255,0.5);
  font-weight: 600;
}

.metric .value {
  color: #fff;
  font-weight: 600;
}

.metric .value.accent {
  color: #f59e0b;
}

.metric .value.positive {
  color: #4ade80;
}

.metric .value.negative {
  color: #f87171;
}

.metric .value.cyan {
  color: #06b6d4;
}

.metric .value.blue {
  color: #60a5fa;
}

.metric .value.green {
  color: #4ade80;
}

.mono {
  font-family: "SF Mono", monospace;
}

/* ============================================
   INSTRUMENTS GRID
   ============================================ */
.instruments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.instrument-card {
  background: rgba(255,255,255,0.02);
  border: 2px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.instrument-card:hover {
  border-color: rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.04);
}

.instrument-card.selected {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.2);
}

.instrument-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 10px;
}

.instrument-name {
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

.instrument-type {
  font-size: 9px;
  background: rgba(255,255,255,0.1);
  padding: 2px 6px;
  border-radius: 4px;
  color: rgba(255,255,255,0.5);
}

.instrument-metrics {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: rgba(255,255,255,0.6);
}

.metric-row .label {
  font-weight: 600;
}

.metric-row .value {
  font-weight: 600;
  color: #fff;
  font-family: "SF Mono", monospace;
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
   HEDGE TABLE
   ============================================ */
.hedge-table-container {
  overflow-x: auto;
}

.hedge-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.hedge-table th,
.hedge-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.hedge-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 10px;
}

.col-instrument {
  text-align: left;
}

.instrument-badge {
  display: inline-block;
  padding: 4px 8px;
  background: rgba(255,255,255,0.05);
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
}

.instrument-badge.bond {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.instrument-badge.swap {
  background: rgba(168, 85, 247, 0.2);
  color: #c084fc;
}

.instrument-badge.futures {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}

.instrument-badge.option {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.hedge-table tr.short {
  background: rgba(248, 113, 113, 0.05);
}

.hedge-table .positive {
  color: #4ade80;
}

.hedge-table .negative {
  color: #f87171;
}

.hedge-table .accent {
  color: #f59e0b;
}

.hedge-table .cyan {
  color: #06b6d4;
}

.hedge-table .blue {
  color: #60a5fa;
}

.hedge-table .col-cost {
  font-family: "SF Mono", monospace;
}

.hedge-table .total-row {
  background: rgba(59, 130, 246, 0.1);
  border-top: 2px solid rgba(59, 130, 246, 0.3);
}

.btn-action {
  padding: 4px 8px;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: #60a5fa;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-action:hover {
  background: rgba(59, 130, 246, 0.4);
}

/* ============================================
   COMPARISON TABLE
   ============================================ */
.comparison-table-container {
  overflow-x: auto;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.comparison-table th,
.comparison-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.comparison-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 10px;
}

.metric-name {
  text-align: left;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.comparison-table .value {
  font-family: "SF Mono", monospace;
  font-weight: 600;
}

.comparison-table .accent {
  color: #f59e0b;
}

.comparison-table .cyan {
  color: #06b6d4;
}

.comparison-table .green {
  color: #4ade80;
}

.comparison-table .blue {
  color: #60a5fa;
}

/* ============================================
   RISK REDUCTION
   ============================================ */
.risk-reduction {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reduction-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.risk-type {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
}

.bar-container {
  background: rgba(255,255,255,0.02);
  border-radius: 4px;
  overflow: hidden;
  height: 16px;
  position: relative;
}

.reduction-text {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
}

/* ============================================
   COST BREAKDOWN
   ============================================ */
.cost-breakdown {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 4px 0;
}

.cost-item {
  display: grid;
  grid-template-columns: minmax(140px, 1fr) minmax(120px, 2fr) minmax(60px, auto);
  align-items: center;
  gap: 16px;
  padding: 8px 0;
}

.cost-item.total {
  border-top: 2px solid rgba(255,255,255,0.15);
  padding-top: 16px;
  margin-top: 4px;
}

.instrument-name {
  font-size: 11px;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cost-item.total .instrument-name {
  color: rgba(255,255,255,0.9);
  font-size: 12px;
}

.cost-bar-container {
  flex: 1;
  height: 8px;
  background: rgba(255,255,255,0.06);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  min-width: 0;
}

.cost-item.total .cost-bar-container {
  height: 10px;
  background: rgba(255,255,255,0.08);
}

.cost-bar {
  height: 100%;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.8), rgba(96, 165, 250, 0.9));
  border-radius: 4px;
  transition: width 0.3s ease;
  min-width: 2px;
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.3);
}

.cost-item.total .cost-bar {
  background: linear-gradient(90deg, rgba(59, 130, 246, 1), rgba(96, 165, 250, 1));
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.5);
}

.cost-value {
  font-size: 11px;
  font-family: "SF Mono", monospace;
  color: rgba(255,255,255,0.7);
  min-width: 55px;
  text-align: right;
  font-weight: 600;
}

.cost-item.total .cost-value {
  color: rgba(255,255,255,0.95);
  font-size: 12px;
}

/* ============================================
   REGRESSION INFO
   ============================================ */
.regression-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.regression-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.variable {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.regression-item .value {
  font-weight: 600;
  color: #fff;
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
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.scenario-table .positive {
  color: #4ade80;
}

.scenario-table .negative {
  color: #f87171;
}

.scenario-table .pnl {
  font-family: "SF Mono", monospace;
}

.scenario-table tr.base {
  background: rgba(59, 130, 246, 0.1);
}

.effectiveness {
  font-family: "SF Mono", monospace;
  color: #4ade80;
}

/* ============================================
   EXECUTION STATUS
   ============================================ */
.execution-status {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.execution-item {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  padding: 12px;
}

.execution-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.quantity {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
}

.status {
  font-size: 10px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
}

.status.executed {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

.status.pending {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.execution-detail {
  display: flex;
  gap: 16px;
  font-size: 10px;
  color: rgba(255,255,255,0.4);
  flex-wrap: wrap;
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

  .grid-3 {
    grid-template-columns: 1fr;
  }

  .grid-2 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hedging-assistant-page {
    padding: 16px;
  }

  .instruments-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .hedge-table,
  .comparison-table,
  .scenario-table {
    font-size: 10px;
  }

  .hedge-table th,
  .hedge-table td,
  .comparison-table th,
  .comparison-table td,
  .scenario-table th,
  .scenario-table td {
    padding: 6px;
  }
}
</style>
