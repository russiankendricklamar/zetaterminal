<!-- src/pages/ArbitrageScanner.vue -->
<template>
  <div class="arbitrage-scanner-page">
    
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Сканер арбитража</h1>
        <p class="page-subtitle">Поиск и анализ возможностей арбитража на рынке форвардов</p>
      </div>
      
      <div class="header-right">
        <!-- Instrument Type -->
        <div class="control-group">
          <label class="control-label">Инструмент:</label>
          <select v-model="selectedInstrument" class="instrument-select" @change="scanArbitrage">
            <option value="bonds">Арбитраж форварда на облигацию</option>
            <option value="fx">Арбитраж валютного форварда</option>
            <option value="equity">Арбитраж форварда на акцию</option>
            <option value="commodities">Арбитраж форварда на товар</option>
          </select>
        </div>

        <!-- Min Profit Threshold -->
        <div class="control-group">
          <label class="control-label">Мин. прибыль (bp):</label>
          <input v-model.number="minProfitThreshold" type="number" class="threshold-input" step="1" @change="scanArbitrage" />
        </div>

        <!-- Scan Button -->
        <button @click="scanArbitrage" class="btn-primary" :disabled="scanning">
          <span v-if="!scanning">Сканировать</span>
          <span v-else>↺ Сканирую...</span>
        </button>
      </div>
    </div>

    <!-- Scanner Status & Summary -->
    <div class="grid-4">
      <!-- Total Opportunities -->
      <div class="status-card">
        <div class="status-header">
          <h3>Всего возможностей</h3>
          <span class="status-unit">Всего арбитражей</span>
        </div>
        <div class="status-value accent">{{ arbitrageOpportunities.length }}</div>
        <div class="status-detail">
          <span class="label">Последнее сканирование</span>
          <span class="value">{{ lastScanTime }}</span>
        </div>
      </div>

      <!-- Profitable Arbitrages -->
      <div class="status-card">
        <div class="status-header">
          <h3>Прибыльные</h3>
          <span class="status-unit">С положительным P&L</span>
        </div>
        <div class="status-value positive">
          {{ profitableCount }}
        </div>
        <div class="status-detail">
          <span class="label">Средняя прибыль</span>
          <span class="value">{{ avgProfit.toFixed(1) }}bp</span>
        </div>
      </div>

      <!-- Total Potential P&L -->
      <div class="status-card">
        <div class="status-header">
          <h3>Общий потенциал</h3>
          <span class="status-unit">Суммарный P&L</span>
        </div>
        <div class="status-value green">
          {{ formatCompactCurrency(totalPotentialPnL) }}
        </div>
        <div class="status-detail">
          <span class="label">Размер позиции</span>
          <span class="value">{{ formatCompactCurrency(defaultPositionSize) }}</span>
        </div>
      </div>

      <!-- Execution Feasibility -->
      <div class="status-card">
        <div class="status-header">
          <h3>Исполнимые</h3>
          <span class="status-unit">Технически исполнимые</span>
        </div>
        <div class="status-value cyan">
          {{ feasibleCount }}
        </div>
        <div class="status-detail">
          <span class="label">Ликвидность OK</span>
          <span class="value">{{ (feasibilityRate * 100).toFixed(0) }}%</span>
        </div>
      </div>
    </div>

    <!-- Active Arbitrage Opportunities -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Активные возможности арбитража</h3>
        <span class="card-subtitle">Сортировка по потенциальному профиту</span>
      </div>
      <div class="opportunities-controls">
        <div class="filter-group">
          <label>Фильтр по типу:</label>
          <div class="filter-buttons">
            <button 
              v-for="type in arbitrageTypes"
              :key="type"
              @click="selectedArbitrageType = selectedArbitrageType === type ? null : type"
              :class="selectedArbitrageType === type ? 'active' : ''"
              class="filter-btn"
            >
              {{ type }}
            </button>
          </div>
        </div>
      </div>
      <div class="opportunities-table-container">
        <table class="opportunities-table">
          <thead>
            <tr>
              <th class="col-rank">#</th>
              <th class="col-type">Тип</th>
              <th class="col-instrument">Инструмент</th>
              <th class="col-spot">Спот</th>
              <th class="col-forward">Форвард</th>
              <th class="col-fair">Fair Forward</th>
              <th class="col-mispricing">Неправильная оценка (б.п.)</th>
              <th class="col-profit">Profit Potential</th>
              <th class="col-liquidity">Liquidity</th>
              <th class="col-execution">Execution</th>
              <th class="col-action">Действие</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(opp, idx) in filteredOpportunities" :key="opp.id" :class="opp.type.toLowerCase()">
              <td class="col-rank">{{ idx + 1 }}</td>
              <td class="col-type">
                <span class="type-badge" :class="opp.type.toLowerCase()">{{ opp.type }}</span>
              </td>
              <td class="col-instrument">{{ opp.instrument }}</td>
              <td class="col-spot mono">{{ formatCurrency(opp.spotPrice) }}</td>
              <td class="col-forward mono">{{ formatCurrency(opp.marketForwardPrice) }}</td>
              <td class="col-fair mono">{{ formatCurrency(opp.fairForwardPrice) }}</td>
              <td class="col-mispricing mono" :class="opp.mispricing >= minProfitThreshold ? 'opportunity' : ''">
                {{ opp.mispricing >= 0 ? '+' : '' }}{{ opp.mispricing.toFixed(1) }}bp
              </td>
              <td class="col-profit accent mono">
                {{ formatCompactCurrency(opp.profitPotential) }}
              </td>
              <td class="col-liquidity">
                <span class="liquidity-badge" :class="opp.liquidity.toLowerCase()">{{ opp.liquidity }}</span>
              </td>
              <td class="col-execution">
                <div class="execution-score">
                  <div class="score-bar" :style="{ width: (opp.executionScore * 100) + '%' }"></div>
                </div>
                <span class="score-text">{{ (opp.executionScore * 100).toFixed(0) }}%</span>
              </td>
              <td class="col-action">
                <button @click="executeArbitrage(opp.id)" class="btn-execute">
                  {{ opp.executed ? '✓' : '→' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Arbitrage Strategy Details -->
    <div class="grid-2">
      <!-- Cash-and-Carry Strategy -->
      <div class="card">
        <div class="card-header">
          <h3>Стратегия Cash-and-Carry</h3>
          <span class="card-subtitle">Купить Spot + Продать Forward</span>
        </div>
        <div class="strategy-details">
          <div v-for="strategy in cashAndCarryStrategies" :key="strategy.id" class="strategy-item">
            <span class="strategy-title">{{ strategy.name }}</span>
            <div class="strategy-breakdown">
              <div class="breakdown-row">
                <span class="label">Купить Spot @</span>
                <span class="value">{{ formatCurrency(strategy.spotPrice) }}</span>
              </div>
              <div class="breakdown-row">
                <span class="label">Продать Forward @</span>
                <span class="value">{{ formatCurrency(strategy.forwardPrice) }}</span>
              </div>
              <div class="breakdown-row">
                <span class="label">Стоимость финансирования</span>
                <span class="value negative">{{ formatCompactCurrency(strategy.financingCost) }}</span>
              </div>
              <div class="breakdown-row">
                <span class="label">Стоимость хранения</span>
                <span class="value negative">{{ formatCompactCurrency(strategy.storageCost) }}</span>
              </div>
              <div class="breakdown-row total">
                <span class="label">Чистая прибыль арбитража</span>
                <span class="value positive">{{ formatCompactCurrency(strategy.netProfit) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Reverse Cash-and-Carry Strategy -->
      <div class="card">
        <div class="card-header">
          <h3>Обратный Cash-and-Carry</h3>
          <span class="card-subtitle">Продать Spot + Купить Forward</span>
        </div>
        <div class="strategy-details">
          <div v-for="strategy in reverseCashAndCarryStrategies" :key="strategy.id" class="strategy-item">
            <span class="strategy-title">{{ strategy.name }}</span>
            <div class="strategy-breakdown">
              <div class="breakdown-row">
                <span class="label">Продать Spot @</span>
                <span class="value">{{ formatCurrency(strategy.spotPrice) }}</span>
              </div>
              <div class="breakdown-row">
                <span class="label">Купить Forward @</span>
                <span class="value">{{ formatCurrency(strategy.forwardPrice) }}</span>
              </div>
              <div class="breakdown-row">
                <span class="label">Стоимость займа</span>
                <span class="value negative">{{ formatCompactCurrency(strategy.borrowCost) }}</span>
              </div>
              <div class="breakdown-row">
                <span class="label">Удобство владения</span>
                <span class="value positive">{{ formatCompactCurrency(strategy.convenienceYield) }}</span>
              </div>
              <div class="breakdown-row total">
                <span class="label">Чистая прибыль арбитража</span>
                <span class="value positive">{{ formatCompactCurrency(strategy.netProfit) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Arbitrage Calendar -->
    <div class="card full-width">
      <div class="chart-header">
        <h3>Возможности арбитража по сроку и времени</h3>
        <span class="chart-subtitle">Тепловая карта возможностей</span>
      </div>
      <div class="chart-container tall">
        <canvas ref="arbitrageHeatmapRef"></canvas>
      </div>
    </div>

    <!-- Risk & Feasibility Analysis -->
    <div class="grid-2">
      <!-- Execution Risk -->
      <div class="card">
        <div class="card-header">
          <h3>Оценка риска исполнения</h3>
          <span class="card-subtitle">Риски при исполнении стратегии</span>
        </div>
        <div class="risk-assessment">
          <div class="risk-factor">
            <span class="factor-name">Влияние спреда Bid-Ask</span>
            <div class="factor-bar">
              <div class="bar-fill" style="width: 35%;"></div>
            </div>
            <span class="factor-value">35bp</span>
          </div>
          <div class="risk-factor">
            <span class="factor-name">Влияние на рынок</span>
            <div class="factor-bar">
              <div class="bar-fill" style="width: 22%;"></div>
            </div>
            <span class="factor-value">22bp</span>
          </div>
          <div class="risk-factor">
            <span class="factor-name">Время исполнения</span>
            <div class="factor-bar">
              <div class="bar-fill" style="width: 18%;"></div>
            </div>
            <span class="factor-value">18bp</span>
          </div>
          <div class="risk-factor">
            <span class="factor-name">Риск ликвидности</span>
            <div class="factor-bar">
              <div class="bar-fill" style="width: 12%;"></div>
            </div>
            <span class="factor-value">12bp</span>
          </div>
          <div class="risk-factor">
            <span class="factor-name">Риск финансирования</span>
            <div class="factor-bar">
              <div class="bar-fill" style="width: 8%;"></div>
            </div>
            <span class="factor-value">8bp</span>
          </div>
        </div>
      </div>

      <!-- Profitability Distribution -->
      <div class="card">
        <div class="chart-header">
          <h3>Распределение прибыли</h3>
          <span class="chart-subtitle">Распределение потенциального профита</span>
        </div>
        <div class="chart-container">
          <canvas ref="profitDistributionRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Market Statistics -->
    <div class="grid-3">
      <!-- Avg Mispricing -->
      <div class="stat-card">
        <div class="stat-header">
          <h3>Средняя неправильная оценка</h3>
          <span class="stat-unit">Средний размер</span>
        </div>
        <div class="stat-value accent">{{ avgMispricing.toFixed(1) }}bp</div>
        <div class="stat-detail">
          <span class="label">Диапазон</span>
          <span class="value">{{ minMispricing.toFixed(1) }} - {{ maxMispricing.toFixed(1) }}bp</span>
        </div>
      </div>

      <!-- Success Rate -->
      <div class="stat-card">
        <div class="stat-header">
          <h3>Историческая частота успеха</h3>
          <span class="stat-unit">Реализация возможностей</span>
        </div>
        <div class="stat-value green">{{ (successRate * 100).toFixed(1) }}%</div>
        <div class="stat-detail">
          <span class="label">Из последних 100 сканирований</span>
          <span class="value">{{ Math.round(successRate * 100) }} арбитражей</span>
        </div>
      </div>

      <!-- Avg Execution Time -->
      <div class="stat-card">
        <div class="stat-header">
          <h3>Среднее время исполнения</h3>
          <span class="stat-unit">Среднее время</span>
        </div>
        <div class="stat-value cyan">{{ avgExecutionTime.toFixed(1) }}ms</div>
        <div class="stat-detail">
          <span class="label">От сканирования до исполнения</span>
          <span class="value">{{ minExecutionTime }} - {{ maxExecutionTime }}ms</span>
        </div>
      </div>
    </div>

    <!-- Arbitrage Watchlist -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Список наблюдения</h3>
        <span class="card-subtitle">Отслеживаемые возможности</span>
      </div>
      <div class="watchlist-container">
        <table class="watchlist-table">
          <thead>
            <tr>
              <th>Инструмент</th>
              <th>Текущая неправильная оценка</th>
              <th>Тренд</th>
              <th>Уровень оповещения</th>
              <th>Добавлено</th>
              <th>Действие</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in watchlist" :key="item.id">
              <td class="instrument">{{ item.instrument }}</td>
              <td class="mispricing mono" :class="item.mispricing >= 0 ? 'positive' : 'negative'">
                {{ item.mispricing >= 0 ? '+' : '' }}{{ item.mispricing.toFixed(1) }}bp
              </td>
              <td class="trend">
                <span class="trend-badge" :class="item.trend">{{ item.trendDisplay }}</span>
              </td>
              <td class="alert">
                <span class="alert-badge" :class="item.alertLevel.toLowerCase()">{{ item.alertLevelDisplay }}</span>
              </td>
              <td class="time">{{ item.addedTime }}</td>
              <td class="action">
                <button @click="removeFromWatchlist(item.id)" class="btn-remove">×</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Alerts & Notifications -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Последние оповещения</h3>
        <span class="card-subtitle">Последние обнаруженные возможности</span>
      </div>
      <div class="alerts-container">
        <div v-for="alert in recentAlerts" :key="alert.id" class="alert-item" :class="alert.type.toLowerCase()">
          <div class="alert-icon">{{ alert.icon }}</div>
          <div class="alert-content">
            <span class="alert-title">{{ alert.title }}</span>
            <span class="alert-message">{{ alert.message }}</span>
          </div>
          <span class="alert-time">{{ alert.time }}</span>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span>• Алгоритм: Cost-of-Carry + Convenience Yield</span>
      <span>• Частота: Обновления в реальном времени</span>
      <span>• Обновление: Каждую сек</span>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'

const selectedInstrument = ref('bonds')
const selectedArbitrageType = ref<string | null>(null)
const minProfitThreshold = ref(5)
const scanning = ref(false)
const lastScanTime = ref('Только что')
const defaultPositionSize = 1_000_000

// Arbitrage Opportunities
const arbitrageOpportunities = ref([
  {
    id: 1,
    type: 'Cash-and-Carry',
    instrument: 'US Treasury 10Y',
    spotPrice: 100.5,
    marketForwardPrice: 101.75,
    fairForwardPrice: 101.35,
    mispricing: 40,
    profitPotential: 4000,
    liquidity: 'High',
    executionScore: 0.95,
    executed: false
  },
  {
    id: 2,
    type: 'Reverse Carry',
    instrument: 'Corporate Bond (A)',
    spotPrice: 98.2,
    marketForwardPrice: 99.1,
    fairForwardPrice: 99.45,
    mispricing: -35,
    profitPotential: 3500,
    liquidity: 'Medium',
    executionScore: 0.88,
    executed: false
  },
  {
    id: 3,
    type: 'Cash-and-Carry',
    instrument: 'S&P 500 Index',
    spotPrice: 4850.3,
    marketForwardPrice: 4895.2,
    fairForwardPrice: 4862.1,
    mispricing: 33,
    profitPotential: 3300,
    liquidity: 'High',
    executionScore: 0.92,
    executed: false
  },
  {
    id: 4,
    type: 'Cash-and-Carry',
    instrument: 'EUR/USD Spot',
    spotPrice: 1.0825,
    marketForwardPrice: 1.0848,
    fairForwardPrice: 1.0842,
    mispricing: 60,
    profitPotential: 6000,
    liquidity: 'Very High',
    executionScore: 0.98,
    executed: false
  },
  {
    id: 5,
    type: 'Reverse Carry',
    instrument: 'Commodity (Oil)',
    spotPrice: 78.5,
    marketForwardPrice: 79.8,
    fairForwardPrice: 80.2,
    mispricing: -40,
    profitPotential: 4000,
    liquidity: 'High',
    executionScore: 0.85,
    executed: true
  }
])

const arbitrageTypes = ['Cash-and-Carry', 'Reverse Carry', 'Calendar Spread']

// Cash-and-Carry Strategies
const cashAndCarryStrategies = ref([
  {
    id: 1,
    name: 'US Treasury 10Y',
    spotPrice: 100.5,
    forwardPrice: 101.75,
    financingCost: -425,
    storageCost: -50,
    netProfit: 775
  },
  {
    id: 2,
    name: 'EUR/USD',
    spotPrice: 1.0825,
    forwardPrice: 1.0848,
    financingCost: -120,
    storageCost: 0,
    netProfit: 203
  }
])

// Reverse Cash-and-Carry Strategies
const reverseCashAndCarryStrategies = ref([
  {
    id: 1,
    name: 'Corporate Bond (A)',
    spotPrice: 98.2,
    forwardPrice: 99.1,
    borrowCost: -280,
    convenienceYield: 315,
    netProfit: 615
  },
  {
    id: 2,
    name: 'Oil Futures',
    spotPrice: 78.5,
    forwardPrice: 79.8,
    borrowCost: -150,
    convenienceYield: 370,
    netProfit: 870
  }
])

// Watchlist
const watchlist = ref([
  {
    id: 1,
    instrument: 'US Treasury 10Y',
    mispricing: 40,
    trend: 'Increasing',
    trendDisplay: '↑ Растет',
    alertLevel: 'High',
    alertLevelDisplay: 'Высокий',
    addedTime: '2 часа назад'
  },
  {
    id: 2,
    instrument: 'EUR/USD Spot',
    mispricing: 60,
    trend: 'Stable',
    trendDisplay: '→ Стабильно',
    alertLevel: 'Critical',
    alertLevelDisplay: 'Критический',
    addedTime: '15 мин назад'
  },
  {
    id: 3,
    instrument: 'S&P 500 Index',
    mispricing: 33,
    trend: 'Decreasing',
    trendDisplay: '↓ Снижается',
    alertLevel: 'Medium',
    alertLevelDisplay: 'Средний',
    addedTime: '1 час назад'
  }
])

// Recent Alerts
const recentAlerts = ref([
  {
    id: 1,
    type: 'Opportunity',
    icon: '',
    title: 'Обнаружена возможность высокой прибыли',
    message: 'EUR/USD Forward: неправильная оценка 60б.п., Потенциальная прибыль: $6,000',
    time: '2 сек назад'
  },
  {
    id: 2,
    type: 'Warning',
    icon: '',
    title: 'Проблема ликвидности',
    message: 'Corporate Bond Forward: спред Bid-Ask расширился до 25б.п.',
    time: '45 сек назад'
  },
  {
    id: 3,
    type: 'Opportunity',
    icon: '',
    title: 'Неправильная оценка изменилась',
    message: 'US Treasury 10Y: неправильная оценка увеличилась с 32б.п. до 40б.п.',
    time: '1 мин назад'
  },
  {
    id: 4,
    type: 'Execution',
    icon: '✓',
    title: 'Арбитраж исполнен',
    message: 'Oil Futures: Reverse Carry исполнен, Прибыль: $870',
    time: '3 мин назад'
  }
])

// Chart References
const arbitrageHeatmapRef = ref<HTMLCanvasElement | null>(null)
const profitDistributionRef = ref<HTMLCanvasElement | null>(null)

let charts: { [key: string]: Chart | null } = {}

// Computed Properties
const filteredOpportunities = computed(() => {
  return arbitrageOpportunities.value.filter(opp => {
    if (selectedArbitrageType.value && opp.type !== selectedArbitrageType.value) {
      return false
    }
    return Math.abs(opp.mispricing) >= minProfitThreshold.value
  }).sort((a, b) => Math.abs(b.mispricing) - Math.abs(a.mispricing))
})

const profitableCount = computed(() => {
  return arbitrageOpportunities.value.filter(o => Math.abs(o.mispricing) >= minProfitThreshold.value).length
})

const feasibleCount = computed(() => {
  return arbitrageOpportunities.value.filter(o => o.executionScore >= 0.8).length
})

const totalPotentialPnL = computed(() => {
  return arbitrageOpportunities.value.reduce((sum, o) => sum + o.profitPotential, 0)
})

const avgProfit = computed(() => {
  const profitable = filteredOpportunities.value
  return profitable.length ? profitable.reduce((sum, o) => sum + o.mispricing, 0) / profitable.length : 0
})

const feasibilityRate = computed(() => {
  return arbitrageOpportunities.value.length ? 
    arbitrageOpportunities.value.filter(o => o.executionScore >= 0.8).length / arbitrageOpportunities.value.length 
    : 0
})

const avgMispricing = computed(() => {
  const opps = filteredOpportunities.value
  return opps.length ? opps.reduce((sum, o) => sum + Math.abs(o.mispricing), 0) / opps.length : 0
})

const minMispricing = computed(() => {
  const opps = filteredOpportunities.value
  return opps.length ? Math.min(...opps.map(o => Math.abs(o.mispricing))) : 0
})

const maxMispricing = computed(() => {
  const opps = filteredOpportunities.value
  return opps.length ? Math.max(...opps.map(o => Math.abs(o.mispricing))) : 0
})

const successRate = 0.87
const avgExecutionTime = 245.5
const minExecutionTime = 120
const maxExecutionTime = 450

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

const scanArbitrage = async () => {
  scanning.value = true
  try {
    await new Promise(r => setTimeout(r, 800))
    lastScanTime.value = 'Только что'
    initCharts()
  } finally {
    scanning.value = false
  }
}

const executeArbitrage = (id: number) => {
  const opp = arbitrageOpportunities.value.find(o => o.id === id)
  if (opp) {
    opp.executed = true
  }
}

const removeFromWatchlist = (id: number) => {
  watchlist.value = watchlist.value.filter(w => w.id !== id)
}

const initCharts = () => {
  Object.values(charts).forEach(chart => {
    if (chart) chart.destroy()
  })
  charts = {}

  // Arbitrage Heatmap
  if (arbitrageHeatmapRef.value?.getContext('2d')) {
    const tenors = ['1M', '3M', '6M', '1Y', '2Y']
    const instruments = ['US Treasury', 'Corporate Bond', 'Stock Index', 'FX Pair', 'Commodity']

    charts.heatmap = new Chart(arbitrageHeatmapRef.value.getContext('2d') as any, {
      type: 'bubble',
      data: {
        datasets: [
          {
            label: 'Cash-and-Carry',
            data: [
              { x: 0, y: 0, r: 25 },
              { x: 1, y: 1, r: 20 },
              { x: 2, y: 2, r: 18 },
              { x: 3, y: 3, r: 22 },
              { x: 4, y: 4, r: 19 }
            ],
            backgroundColor: 'rgba(74, 222, 128, 0.6)',
            borderColor: '#4ade80'
          },
          {
            label: 'Reverse Carry',
            data: [
              { x: 1, y: 0, r: 15 },
              { x: 2, y: 1, r: 18 },
              { x: 3, y: 2, r: 12 },
              { x: 4, y: 3, r: 16 }
            ],
            backgroundColor: 'rgba(248, 113, 113, 0.6)',
            borderColor: '#f87171'
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

  // Profit Distribution
  if (profitDistributionRef.value?.getContext('2d')) {
    charts.distribution = new Chart(profitDistributionRef.value.getContext('2d') as any, {
      type: 'bar',
      data: {
        labels: ['0-10bp', '10-25bp', '25-50bp', '50-100bp', '100+bp'],
        datasets: [{
          label: 'Количество',
          data: [2, 5, 8, 6, 3],
          backgroundColor: [
            'rgba(168, 85, 247, 0.6)',
            'rgba(96, 165, 250, 0.6)',
            'rgba(74, 222, 128, 0.6)',
            'rgba(245, 158, 11, 0.6)',
            'rgba(248, 113, 113, 0.6)'
          ],
          borderColor: ['#a855f7', '#60a5fa', '#4ade80', '#f59e0b', '#f87171'],
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
.arbitrage-scanner-page {
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
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.control-group:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.control-label {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.instrument-select,
.threshold-input {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  padding: 4px 8px;
  cursor: pointer;
}

.instrument-select option {
  background: #1e1f28;
  color: #fff;
}

.threshold-input {
  width: 60px;
  text-align: center;
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
.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

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
   STATUS CARDS
   ============================================ */
.status-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 
    0 20px 40px -10px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.status-card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
}

.status-header {
  margin-bottom: 4px;
}

.status-header h3 {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  margin: 0;
  text-transform: uppercase;
}

.status-unit {
  font-size: 9px;
  color: rgba(255,255,255,0.3);
  display: block;
  margin-top: 2px;
}

.status-value {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.status-value.accent {
  color: #f59e0b;
}

.status-value.positive {
  color: #4ade80;
}

.status-value.green {
  color: #4ade80;
}

.status-value.cyan {
  color: #06b6d4;
}

.status-detail {
  display: flex;
  justify-content: space-between;
  font-size: 9px;
  color: rgba(255,255,255,0.4);
  border-top: 1px solid rgba(255,255,255,0.05);
  padding-top: 6px;
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
   OPPORTUNITIES CONTROLS
   ============================================ */
.opportunities-controls {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-group > label {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
  text-transform: uppercase;
}

.filter-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 4px 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.6);
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.4);
  color: #60a5fa;
}

.filter-btn.active {
  background: rgba(59, 130, 246, 0.25);
  border-color: rgba(59, 130, 246, 0.6);
  color: #60a5fa;
}

/* ============================================
   OPPORTUNITIES TABLE
   ============================================ */
.opportunities-table-container {
  overflow-x: auto;
}

.opportunities-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

.opportunities-table th,
.opportunities-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.opportunities-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 9px;
}

.col-rank {
  text-align: center;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
}

.col-type {
  text-align: center;
}

.col-instrument {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
}

.type-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 9px;
  font-weight: 600;
}

.type-badge.cash-and-carry {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

.type-badge.reverse {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.type-badge.calendar {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
}

.col-mispricing.opportunity {
  background: rgba(74, 222, 128, 0.1);
  color: #4ade80;
}

.liquidity-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 9px;
  font-weight: 600;
}

.liquidity-badge.high {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

.liquidity-badge.medium {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.liquidity-badge.low {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.execution-score {
  position: relative;
  width: 100%;
  height: 4px;
  background: rgba(255,255,255,0.05);
  border-radius: 2px;
  overflow: hidden;
  margin: 2px 0;
}

.score-bar {
  height: 100%;
  background: linear-gradient(90deg, #4ade80, #22c55e);
  border-radius: 2px;
}

.score-text {
  font-size: 9px;
  color: rgba(255,255,255,0.5);
}

.btn-execute {
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

.btn-execute:hover {
  background: rgba(59, 130, 246, 0.4);
}

/* ============================================
   STRATEGY DETAILS
   ============================================ */
.strategy-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.strategy-item {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  padding: 12px;
}

.strategy-title {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255,255,255,0.7);
  display: block;
  margin-bottom: 8px;
}

.strategy-breakdown {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.breakdown-row {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  padding: 4px 0;
  border-bottom: 1px solid rgba(255,255,255,0.02);
}

.breakdown-row .label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.breakdown-row .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
  color: rgba(255,255,255,0.7);
}

.breakdown-row .value.positive {
  color: #4ade80;
}

.breakdown-row .value.negative {
  color: #f87171;
}

.breakdown-row.total {
  border-top: 1px solid rgba(255,255,255,0.1);
  border-bottom: none;
  padding-top: 6px;
  font-weight: 600;
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
   RISK ASSESSMENT
   ============================================ */
.risk-assessment {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.risk-factor {
  display: flex;
  align-items: center;
  gap: 12px;
}

.factor-name {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
  min-width: 140px;
}

.factor-bar {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.05);
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #f87171);
  border-radius: 3px;
}

.factor-value {
  font-size: 10px;
  font-family: "SF Mono", monospace;
  color: rgba(255,255,255,0.6);
  min-width: 40px;
  text-align: right;
}

/* ============================================
   STAT CARDS
   ============================================ */
.stat-card {
  background: rgba(30, 32, 40, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-header {
  margin-bottom: 4px;
}

.stat-header h3 {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  margin: 0;
  text-transform: uppercase;
}

.stat-unit {
  font-size: 9px;
  color: rgba(255,255,255,0.3);
  display: block;
  margin-top: 2px;
}

.stat-value {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.stat-value.accent {
  color: #f59e0b;
}

.stat-value.green {
  color: #4ade80;
}

.stat-value.cyan {
  color: #06b6d4;
}

.stat-detail {
  display: flex;
  justify-content: space-between;
  font-size: 9px;
  color: rgba(255,255,255,0.4);
  border-top: 1px solid rgba(255,255,255,0.05);
  padding-top: 6px;
}

/* ============================================
   WATCHLIST TABLE
   ============================================ */
.watchlist-container {
  overflow-x: auto;
}

.watchlist-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

.watchlist-table th,
.watchlist-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.watchlist-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 9px;
}

.instrument {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
}

.mispricing {
  font-family: "SF Mono", monospace;
}

.mispricing.positive {
  color: #4ade80;
}

.mispricing.negative {
  color: #f87171;
}

.trend {
  font-size: 9px;
}

.trend-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.trend-badge.Increasing {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

.trend-badge.Stable {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
}

.trend-badge.Decreasing {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.alert {
  font-size: 9px;
}

.alert-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.alert-badge.critical {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.alert-badge.high {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.alert-badge.medium {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
}

.time {
  color: rgba(255,255,255,0.4);
  font-size: 9px;
}

.btn-remove {
  background: rgba(248, 113, 113, 0.2);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #f87171;
  padding: 2px 6px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-remove:hover {
  background: rgba(248, 113, 113, 0.3);
}

/* ============================================
   ALERTS CONTAINER
   ============================================ */
.alerts-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255,255,255,0.02);
  border-left: 4px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  font-size: 11px;
}

.alert-item.opportunity {
  border-left-color: rgba(74, 222, 128, 0.6);
  background: rgba(74, 222, 128, 0.05);
}

.alert-item.warning {
  border-left-color: rgba(245, 158, 11, 0.6);
  background: rgba(245, 158, 11, 0.05);
}

.alert-item.execution {
  border-left-color: rgba(96, 165, 250, 0.6);
  background: rgba(96, 165, 250, 0.05);
}

.alert-icon {
  font-size: 16px;
  min-width: 24px;
}

.alert-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.alert-title {
  font-weight: 600;
  color: rgba(255,255,255,0.7);
}

.alert-message {
  color: rgba(255,255,255,0.4);
  font-size: 10px;
}

.alert-time {
  color: rgba(255,255,255,0.3);
  font-size: 9px;
  text-align: right;
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
@media (max-width: 1200px) {
  .grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }

  .grid-3 {
    grid-template-columns: repeat(2, 1fr);
  }
}

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
  .arbitrage-scanner-page {
    padding: 16px;
  }

  .grid-4 {
    grid-template-columns: 1fr;
  }

  .grid-3 {
    grid-template-columns: 1fr;
  }

  .opportunities-table,
  .watchlist-table {
    font-size: 9px;
  }

  .opportunities-table th,
  .opportunities-table td,
  .watchlist-table th,
  .watchlist-table td {
    padding: 6px;
  }

  .chart-container {
    height: 300px;
  }

  .chart-container.tall {
    height: 400px;
  }

  .filter-buttons {
    width: 100%;
  }

  .filter-btn {
    flex: 1;
    min-width: 80px;
  }
}

@media (max-width: 480px) {
  .arbitrage-scanner-page {
    padding: 12px;
  }
  .chart-container {
    height: 250px;
  }
  .chart-container.tall {
    height: 300px;
  }
  .opportunities-table,
  .watchlist-table {
    font-size: 8px;
  }
  .opportunities-table th,
  .opportunities-table td,
  .watchlist-table th,
  .watchlist-table td {
    padding: 4px;
  }
  .filter-btn {
    font-size: 11px;
    padding: 6px 10px;
  }
}
</style>
