<!-- src/pages/BasisAnalysis.vue -->
<template>
  <div class="basis-analysis-page">
    
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Анализ базиса</h1>
        <p class="page-subtitle">Анализ спот-форвард базиса и стоимости переноса позиций</p>
      </div>
      
      <div class="header-right">
        <!-- Instrument -->
        <div class="control-group">
          <label class="control-label">Инструмент:</label>
          <select v-model="selectedInstrument" class="instrument-select" @change="updateAnalysis">
            <option value="bonds">Базис облигаций</option>
            <option value="fx">Валютный базис</option>
            <option value="equity">Базис акций</option>
            <option value="commodities">Базис товаров</option>
          </select>
        </div>

        <!-- Time Period -->
        <div class="control-group">
          <label class="control-label">Период:</label>
          <select v-model="selectedPeriod" class="period-select" @change="updateAnalysis">
            <option value="1m">1 месяц</option>
            <option value="3m">3 месяца</option>
            <option value="6m">6 месяцев</option>
            <option value="1y">1 год</option>
            <option value="2y">2 года</option>
          </select>
        </div>

        <!-- Update Button -->
        <button @click="updateAnalysis" class="btn-primary" :disabled="calculating">
          <span v-if="!calculating">Обновить</span>
          <span v-else>↺ Считаю...</span>
        </button>
      </div>
    </div>

    <!-- Current Basis Overview -->
    <div class="grid-4">
      <!-- Spot Price -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Спот цена</h3>
          <span class="metric-unit">Текущая цена</span>
        </div>
        <div class="metric-value accent">
          {{ formatCurrency(basisData.spotPrice) }}
        </div>
        <div class="metric-detail">
          <span class="label">Изменение (1Д)</span>
          <span class="value" :class="basisData.spotChange >= 0 ? 'positive' : 'negative'">
            {{ basisData.spotChange >= 0 ? '+' : '' }}{{ basisData.spotChange.toFixed(3) }}%
          </span>
        </div>
      </div>

      <!-- Forward Price -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Форвардная цена</h3>
          <span class="metric-unit">Форвардная цена</span>
        </div>
        <div class="metric-value blue">
          {{ formatCurrency(basisData.forwardPrice) }}
        </div>
        <div class="metric-detail">
          <span class="label">Tenor</span>
          <span class="value">{{ selectedPeriod }}</span>
        </div>
      </div>

      <!-- Basis -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Базис (пункты)</h3>
          <span class="metric-unit">F - S</span>
        </div>
        <div class="metric-value cyan">
          {{ basisData.basis.toFixed(4) }}
        </div>
        <div class="metric-detail">
          <span class="label">% от спота</span>
          <span class="value">{{ ((basisData.basis / basisData.spotPrice) * 100).toFixed(3) }}%</span>
        </div>
      </div>

      <!-- Annualized Carry -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Годовая стоимость переноса</h3>
          <span class="metric-unit">Годовая стоимость</span>
        </div>
        <div class="metric-value" :class="basisData.annualizedCarry >= 0 ? 'positive' : 'negative'">
          {{ basisData.annualizedCarry >= 0 ? '+' : '' }}{{ basisData.annualizedCarry.toFixed(2) }}%
        </div>
        <div class="metric-detail">
          <span class="label">Срок</span>
          <span class="value">{{ basisData.termLength.toFixed(2) }}M</span>
        </div>
      </div>
    </div>

    <!-- Basis Decomposition -->
    <div class="grid-2">
      <!-- Cost of Carry Breakdown -->
      <div class="card">
        <div class="card-header">
          <h3>Разложение стоимости переноса</h3>
          <span class="card-subtitle">Что составляет базис</span>
        </div>
        <div class="carry-breakdown">
          <div class="carry-item">
            <span class="label">Безрисковая ставка (r)</span>
            <span class="value positive">{{ basisData.carryComponents.riskFreeRate.toFixed(3) }}%</span>
          </div>
          <div class="carry-item">
            <span class="label">Стоимость хранения (u)</span>
            <span class="value positive">{{ basisData.carryComponents.storageCost.toFixed(3) }}%</span>
          </div>
          <div class="carry-item">
            <span class="label">Стоимость финансирования (f)</span>
            <span class="value positive">{{ basisData.carryComponents.financingCost.toFixed(3) }}%</span>
          </div>
          <div class="carry-item">
            <span class="label">- Дивидендная доходность (d)</span>
            <span class="value negative">{{ basisData.carryComponents.dividendYield.toFixed(3) }}%</span>
          </div>
          <div class="carry-item">
            <span class="label">- Удобство владения (y)</span>
            <span class="value negative">{{ basisData.carryComponents.convenienceYield.toFixed(3) }}%</span>
          </div>
          <div class="carry-item total">
            <span class="label">= Чистый Carry (Базис)</span>
            <span class="value cyan">{{ basisData.annualizedCarry.toFixed(3) }}%</span>
          </div>
        </div>
      </div>

      <!-- Basis vs Carry Chart -->
      <div class="card">
        <div class="chart-header">
          <h3>Теоретический vs фактический базис</h3>
          <span class="chart-subtitle">F_fair vs F_market</span>
        </div>
        <div class="chart-container">
          <canvas ref="basisChartRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Basis Term Structure -->
    <div class="card full-width">
      <div class="chart-header">
        <h3>Структура базиса по срокам</h3>
        <span class="chart-subtitle">Как базис меняется по срокам</span>
      </div>
      <div class="chart-container tall">
        <canvas ref="termStructureRef"></canvas>
      </div>
    </div>

    <!-- Basis Table by Tenor -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Basis по срокам</h3>
        <span class="card-subtitle">Детальный анализ базиса для каждого tenor</span>
      </div>
      <div class="basis-table-container">
        <table class="basis-table">
          <thead>
            <tr>
              <th>Tenor</th>
              <th>Спот цена</th>
              <th>Форвардная цена</th>
              <th>Базис (пт)</th>
              <th>Базис (%)</th>
              <th>Справедливый базис</th>
              <th>Отклонение базиса</th>
              <th>Carry (год.)</th>
              <th>Возможность</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tenor in basisByTenor" :key="tenor.tenor" :class="tenor.opportunity !== 'Neutral' ? tenor.opportunity.toLowerCase() : ''">
              <td class="tenor-name">{{ tenor.tenor }}</td>
              <td class="price mono">{{ formatCurrency(tenor.spotPrice) }}</td>
              <td class="price mono">{{ formatCurrency(tenor.forwardPrice) }}</td>
              <td class="basis mono">{{ tenor.basis.toFixed(4) }}</td>
              <td class="basis-pct mono">{{ tenor.basisPct.toFixed(3) }}%</td>
              <td class="fair mono">{{ tenor.fairBasis.toFixed(4) }}</td>
              <td class="variance mono" :class="Math.abs(tenor.variance) > 0.01 ? 'outlier' : ''">
                {{ tenor.variance >= 0 ? '+' : '' }}{{ tenor.variance.toFixed(4) }}
              </td>
              <td class="carry mono">{{ tenor.carryAnn.toFixed(2) }}%</td>
              <td class="opportunity" :class="tenor.opportunity.toLowerCase()">
                {{ tenor.opportunity }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Rolling Analysis -->
    <div class="grid-2">
      <!-- Roll Yield -->
      <div class="card">
        <div class="chart-header">
          <h3>Roll Yield Analysis</h3>
          <span class="chart-subtitle">Доход от переноса позиции на следующий контракт</span>
        </div>
        <div class="roll-analysis">
          <div class="roll-item">
            <span class="label">Текущий контракт</span>
            <span class="value">{{ basisData.currentTenor }}</span>
          </div>
          <div class="roll-item">
            <span class="label">Следующий контракт</span>
            <span class="value">{{ basisData.nextTenor }}</span>
          </div>
          <div class="roll-item">
            <span class="label">Изменение базиса</span>
            <span class="value cyan mono">
              {{ basisData.rollYield >= 0 ? '+' : '' }}{{ basisData.rollYield.toFixed(4) }}
            </span>
          </div>
          <div class="roll-item">
            <span class="label">Roll Yield (год.)</span>
            <span class="value" :class="basisData.rollYieldAnnual >= 0 ? 'positive' : 'negative'">
              {{ basisData.rollYieldAnnual >= 0 ? '+' : '' }}{{ basisData.rollYieldAnnual.toFixed(2) }}%
            </span>
          </div>
          <div class="roll-item total">
            <span class="label">Общая доходность</span>
            <span class="value accent">
              {{ basisData.totalReturn >= 0 ? '+' : '' }}{{ basisData.totalReturn.toFixed(2) }}%
            </span>
          </div>
        </div>
      </div>

      <!-- Carry Roll Strategy -->
      <div class="card">
        <div class="chart-header">
          <h3>Стратегия Carry Roll</h3>
          <span class="chart-subtitle">Стратегия "buy and carry"</span>
        </div>
        <div class="strategy-analysis">
          <div class="strategy-item">
            <span class="label">Buy Spot @ </span>
            <span class="value">{{ formatCurrency(basisData.spotPrice) }}</span>
          </div>
          <div class="strategy-item">
            <span class="label">Финансировать @ </span>
            <span class="value">{{ basisData.carryComponents.riskFreeRate.toFixed(2) }}%</span>
          </div>
          <div class="strategy-item">
            <span class="label">Стоимость удержания @ </span>
            <span class="value">{{ (basisData.carryComponents.storageCost + basisData.carryComponents.financingCost).toFixed(2) }}%</span>
          </div>
          <div class="strategy-item">
            <span class="label">Продать форвард @ </span>
            <span class="value">{{ formatCurrency(basisData.forwardPrice) }}</span>
          </div>
          <div class="strategy-item total">
            <span class="label">Арбитражная прибыль</span>
            <span class="value positive">
              {{ formatCompactCurrency(basisData.arbitrageProfit) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Basis Spread Analysis -->
    <div class="grid-2">
      <!-- Calendar Spread -->
      <div class="card">
        <div class="chart-header">
          <h3>Calendar Spread (Roll Spread)</h3>
          <span class="chart-subtitle">Разница в базисе между контрактами</span>
        </div>
        <div class="chart-container">
          <canvas ref="spreadChartRef"></canvas>
        </div>
      </div>

      <!-- Basis Volatility -->
      <div class="card">
        <div class="chart-header">
          <h3>Волатильность базиса</h3>
          <span class="chart-subtitle">Историческая волатильность базиса</span>
        </div>
        <div class="volatility-metrics">
          <div class="vol-item">
            <span class="label">Текущая волатильность базиса</span>
            <span class="value accent">{{ basisData.basisVolatility.current.toFixed(2) }}%</span>
          </div>
          <div class="vol-item">
            <span class="label">20Д историческая</span>
            <span class="value blue">{{ basisData.basisVolatility.vol20d.toFixed(2) }}%</span>
          </div>
          <div class="vol-item">
            <span class="label">60Д историческая</span>
            <span class="value">{{ basisData.basisVolatility.vol60d.toFixed(2) }}%</span>
          </div>
          <div class="vol-item">
            <span class="label">1Г историческая</span>
            <span class="value">{{ basisData.basisVolatility.vol1y.toFixed(2) }}%</span>
          </div>
          <div class="vol-item total">
            <span class="label">Диапазон базиса (1Г)</span>
            <span class="value cyan">
              {{ basisData.basisVolatility.minBasis.toFixed(4) }} - {{ basisData.basisVolatility.maxBasis.toFixed(4) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Historical Basis Trend -->
    <div class="card full-width">
      <div class="chart-header">
        <h3>Историческая динамика базиса</h3>
        <span class="chart-subtitle">Изменение базиса и carry за последний год</span>
      </div>
      <div class="chart-container tall">
        <canvas ref="historicalBasisRef"></canvas>
      </div>
    </div>

    <!-- Factors Affecting Basis -->
    <div class="grid-2">
      <!-- Key Drivers -->
      <div class="card">
        <div class="card-header">
          <h3>Ключевые драйверы базиса</h3>
        </div>
        <div class="drivers-list">
          <div v-for="driver in basisDrivers" :key="driver.name" class="driver-item">
            <span class="driver-name">{{ driver.name }}</span>
            <div class="driver-impact" :class="driver.impact.toLowerCase()">
              {{ driver.impact }}
            </div>
            <span class="driver-value">{{ driver.value }}</span>
          </div>
        </div>
      </div>

      <!-- Basis Forecast -->
      <div class="card">
        <div class="card-header">
          <h3>Прогноз базиса (90Д)</h3>
        </div>
        <div class="forecast-metrics">
          <div class="forecast-item">
            <span class="label">Текущий базис</span>
            <span class="value">{{ basisData.basis.toFixed(4) }}</span>
          </div>
          <div class="forecast-item">
            <span class="label">Прогноз базиса (30Д)</span>
            <span class="value cyan">{{ (basisData.basis * 0.85).toFixed(4) }}</span>
          </div>
          <div class="forecast-item">
            <span class="label">Прогноз базиса (60Д)</span>
            <span class="value cyan">{{ (basisData.basis * 0.65).toFixed(4) }}</span>
          </div>
          <div class="forecast-item">
            <span class="label">Прогноз базиса (90Д)</span>
            <span class="value cyan">{{ (basisData.basis * 0.4).toFixed(4) }}</span>
          </div>
          <div class="forecast-item total">
            <span class="label">Ожидаемый Carry</span>
            <span class="value positive">
              {{ (basisData.annualizedCarry * 0.75).toFixed(2) }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Cash-and-Carry Arbitrage Opportunities -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Арбитражные возможности Cash-and-Carry</h3>
        <span class="card-subtitle">Прибыльные позиции при отклонении от справедливого базиса</span>
      </div>
      <div class="opportunities-table-container">
        <table class="opportunities-table">
          <thead>
            <tr>
              <th>Tenor</th>
              <th>Спот цена</th>
              <th>Форвардная цена</th>
              <th>Справедливый базис</th>
              <th>Рыночный базис</th>
              <th>Неправильная оценка</th>
              <th>Стратегия</th>
              <th>Потенциальная прибыль</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="opp in arbitrageOpportunities" :key="opp.tenor" :class="opp.strategy.toLowerCase()">
              <td class="tenor">{{ opp.tenor }}</td>
              <td class="price mono">{{ formatCurrency(opp.spotPrice) }}</td>
              <td class="price mono">{{ formatCurrency(opp.forwardPrice) }}</td>
              <td class="basis mono">{{ opp.fairBasis.toFixed(4) }}</td>
              <td class="basis mono">{{ opp.marketBasis.toFixed(4) }}</td>
              <td class="mispricing mono" :class="Math.abs(opp.mispricing) > 0.001 ? 'significant' : ''">
                {{ opp.mispricing >= 0 ? '+' : '' }}{{ opp.mispricing.toFixed(4) }}
              </td>
              <td class="strategy" :class="opp.strategy.toLowerCase()">
                {{ opp.strategy }}
              </td>
              <td class="profit mono positive">
                {{ formatCompactCurrency(opp.profitPotential) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Basis Risk Summary -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Резюме рисков базиса</h3>
        <span class="card-subtitle">Риски, связанные с движением базиса</span>
      </div>
      <div class="risk-summary">
        <div class="risk-item">
          <div class="risk-header">
            <span class="risk-type">Convergence Risk</span>
            <span class="risk-level high">HIGH</span>
          </div>
          <div class="risk-description">
            Базис конвергирует к нулю при экспирации форварда. Если вы позиционированы против конвергенции, вы потеряете на сходимости.
          </div>
          <div class="risk-metric">
            <span>Convergence P&L @ Expiry:</span>
            <span class="value negative">{{ formatCompactCurrency(-basisData.basis * basisData.contractSize / 100) }}</span>
          </div>
        </div>

        <div class="risk-item">
          <div class="risk-header">
            <span class="risk-type">Риск Carry Roll</span>
            <span class="risk-level medium">СРЕДНИЙ</span>
          </div>
          <div class="risk-description">
            Базис следующего контракта может отличаться. Roll yield может быть хуже ожиданий.
          </div>
          <div class="risk-metric">
            <span>1M Roll Impact:</span>
            <span class="value" :class="basisData.rollYield >= 0 ? 'positive' : 'negative'">
              {{ basisData.rollYield >= 0 ? '+' : '' }}{{ formatCompactCurrency(basisData.rollYield * basisData.contractSize / 100) }}
            </span>
          </div>
        </div>

        <div class="risk-item">
          <div class="risk-header">
            <span class="risk-type">Риск стоимости финансирования</span>
            <span class="risk-level medium">СРЕДНИЙ</span>
          </div>
          <div class="risk-description">
            Стоимость финансирования может вырасти, уменьшив доходность carry стратегии.
          </div>
          <div class="risk-metric">
            <span>Влияние ставки +50bp:</span>
            <span class="value negative">{{ formatCompactCurrency(-basisData.contractSize * basisData.termLength * 50 / 365 / 10000) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span>• Модель: Cost-of-Carry with convenience yield</span>
      <span>• Частота: Ежедневно</span>
      <span>• Обновление: Конец дня</span>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'

const selectedInstrument = ref('bonds')
const selectedPeriod = ref('3m')
const calculating = ref(false)

// Basis Data
const basisData = ref({
  spotPrice: 100,
  forwardPrice: 101.25,
  basis: 1.25,
  annualizedCarry: 5.2,
  termLength: 3,
  spotChange: 0.45,
  currentTenor: '3M',
  nextTenor: '6M',
  rollYield: -0.15,
  rollYieldAnnual: -2.0,
  totalReturn: 3.2,
  arbitrageProfit: 12500,
  contractSize: 100000,
  carryComponents: {
    riskFreeRate: 4.25,
    storageCost: 0.25,
    financingCost: 0.75,
    dividendYield: 2.5,
    convenienceYield: 0.5
  },
  basisVolatility: {
    current: 8.5,
    vol20d: 7.2,
    vol60d: 8.1,
    vol1y: 9.3,
    minBasis: 0.8,
    maxBasis: 2.1
  }
})

// Basis by Tenor
const basisByTenor = ref([
  {
    tenor: '1M',
    spotPrice: 100,
    forwardPrice: 100.35,
    basis: 0.35,
    basisPct: 0.35,
    fairBasis: 0.42,
    variance: -0.07,
    carryAnn: 4.2,
    opportunity: 'Underpriced'
  },
  {
    tenor: '3M',
    spotPrice: 100,
    forwardPrice: 101.25,
    basis: 1.25,
    basisPct: 1.25,
    fairBasis: 1.32,
    variance: -0.07,
    carryAnn: 5.2,
    opportunity: 'Underpriced'
  },
  {
    tenor: '6M',
    spotPrice: 100,
    forwardPrice: 102.65,
    basis: 2.65,
    basisPct: 2.65,
    fairBasis: 2.58,
    variance: 0.07,
    carryAnn: 5.3,
    opportunity: 'Overpriced'
  },
  {
    tenor: '1Y',
    spotPrice: 100,
    forwardPrice: 105.4,
    basis: 5.4,
    basisPct: 5.4,
    fairBasis: 5.25,
    variance: 0.15,
    carryAnn: 5.4,
    opportunity: 'Overpriced'
  },
  {
    tenor: '2Y',
    spotPrice: 100,
    forwardPrice: 110.8,
    basis: 10.8,
    basisPct: 10.8,
    fairBasis: 10.95,
    variance: -0.15,
    carryAnn: 5.4,
    opportunity: 'Neutral'
  }
])

// Basis Drivers
const basisDrivers = ref([
  { name: 'Risk-free Rate', impact: 'Positive', value: '+4.25%' },
  { name: 'Dividend Yield', impact: 'Negative', value: '-2.50%' },
  { name: 'Storage Cost', impact: 'Positive', value: '+0.25%' },
  { name: 'Convenience Yield', impact: 'Negative', value: '-0.50%' },
  { name: 'Financing Cost', impact: 'Positive', value: '+0.75%' },
])

// Arbitrage Opportunities
const arbitrageOpportunities = computed(() => {
  return basisByTenor.value.map(tenor => ({
    tenor: tenor.tenor,
    spotPrice: tenor.spotPrice,
    forwardPrice: tenor.forwardPrice,
    fairBasis: tenor.fairBasis,
    marketBasis: tenor.basis,
    mispricing: tenor.variance,
    strategy: tenor.opportunity === 'Underpriced' ? 'Buy Spot + Sell Forward' : 
              tenor.opportunity === 'Overpriced' ? 'Short Spot + Buy Forward' : 'Neutral',
    profitPotential: Math.abs(tenor.variance) * basisData.value.contractSize / 100
  }))
})

// Chart References
const basisChartRef = ref<HTMLCanvasElement | null>(null)
const termStructureRef = ref<HTMLCanvasElement | null>(null)
const spreadChartRef = ref<HTMLCanvasElement | null>(null)
const historicalBasisRef = ref<HTMLCanvasElement | null>(null)

let charts: { [key: string]: Chart | null } = {}

// Methods
const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
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

const updateAnalysis = () => {
  initCharts()
}

const initCharts = () => {
  // Destroy existing charts
  Object.values(charts).forEach(chart => {
    if (chart) chart.destroy()
  })
  charts = {}

  const tenors = basisByTenor.value.map(t => t.tenor)
  const actualBasis = basisByTenor.value.map(t => t.basis)
  const fairBasis = basisByTenor.value.map(t => t.fairBasis)

  // Basis Chart
  if (basisChartRef.value?.getContext('2d')) {
    charts.basis = new Chart(basisChartRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: tenors,
        datasets: [
          {
            label: 'Actual Basis',
            data: actualBasis,
            borderColor: '#60a5fa',
            backgroundColor: 'rgba(96, 165, 250, 0.08)',
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            borderWidth: 2
          },
          {
            label: 'Fair Basis (Cost-of-Carry)',
            data: fairBasis,
            borderColor: '#4ade80',
            backgroundColor: 'transparent',
            fill: false,
            tension: 0.4,
            pointRadius: 3,
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

  // Term Structure Chart
  if (termStructureRef.value?.getContext('2d')) {
    const carries = basisByTenor.value.map(t => t.carryAnn)
    charts.termStruct = new Chart(termStructureRef.value.getContext('2d') as any, {
      type: 'bar',
      data: {
        labels: tenors,
        datasets: [
          {
            label: 'Basis (Points)',
            data: actualBasis,
            backgroundColor: 'rgba(96, 165, 250, 0.6)',
            borderColor: '#60a5fa',
            yAxisID: 'y'
          },
          {
            label: 'Annualized Carry (%)',
            data: carries,
            backgroundColor: 'rgba(74, 222, 128, 0.6)',
            borderColor: '#4ade80',
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { labels: { color: 'rgba(255,255,255,0.6)' } } },
        scales: {
          x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
          y: { 
            type: 'linear' as const,
            display: true,
            position: 'left' as const,
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: 'rgba(255,255,255,0.3)' },
            title: { display: true, text: 'Basis (Pts)' }
          },
          y1: {
            type: 'linear' as const,
            display: true,
            position: 'right' as const,
            grid: { drawOnChartArea: false },
            ticks: { color: 'rgba(255,255,255,0.3)' },
            title: { display: true, text: 'Carry (%)' }
          }
        }
      }
    } as any)
  }

  // Spread Chart
  if (spreadChartRef.value?.getContext('2d')) {
    const spreads = [0.9, 1.4, 1.75, 2.55, 3.2]
    charts.spread = new Chart(spreadChartRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: ['1M-3M', '3M-6M', '6M-1Y', '1Y-2Y', 'Avg'],
        datasets: [{
          label: 'Roll Spread',
          data: spreads,
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.08)',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
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

  // Historical Basis Chart
  if (historicalBasisRef.value?.getContext('2d')) {
    const dates = ['1M ago', '3W ago', '2W ago', '1W ago', '3D ago', 'Today']
    const basisHistory = [1.5, 1.45, 1.35, 1.28, 1.26, 1.25]
    const carryHistory = [5.8, 5.7, 5.5, 5.4, 5.3, 5.2]

    charts.historical = new Chart(historicalBasisRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [
          {
            label: 'Basis',
            data: basisHistory,
            borderColor: '#60a5fa',
            backgroundColor: 'rgba(96, 165, 250, 0.08)',
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            borderWidth: 2,
            yAxisID: 'y'
          },
          {
            label: 'Annualized Carry (%)',
            data: carryHistory,
            borderColor: '#4ade80',
            backgroundColor: 'transparent',
            fill: false,
            tension: 0.4,
            pointRadius: 3,
            borderWidth: 2,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { labels: { color: 'rgba(255,255,255,0.6)' } } },
        scales: {
          x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
          y: { 
            type: 'linear' as const,
            display: true,
            position: 'left' as const,
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: 'rgba(255,255,255,0.3)' }
          },
          y1: {
            type: 'linear' as const,
            display: true,
            position: 'right' as const,
            grid: { drawOnChartArea: false },
            ticks: { color: 'rgba(255,255,255,0.3)' }
          }
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
.basis-analysis-page {
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
.period-select {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  padding: 4px 8px;
  cursor: pointer;
}

.instrument-select option,
.period-select option {
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
.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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
   METRIC CARDS
   ============================================ */
.metric-card {
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

.metric-card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
}

.metric-header {
  margin-bottom: 4px;
}

.metric-header h3 {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  margin: 0;
  text-transform: uppercase;
}

.metric-unit {
  font-size: 9px;
  color: rgba(255,255,255,0.3);
  display: block;
  margin-top: 2px;
}

.metric-value {
  font-size: 16px;
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

.metric-value.cyan {
  color: #06b6d4;
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
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.carry-item .label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.carry-item .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.carry-item .value.positive {
  color: #4ade80;
}

.carry-item .value.negative {
  color: #f87171;
}

.carry-item .value.cyan {
  color: #06b6d4;
}

.carry-item.total {
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 8px;
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
   BASIS TABLE
   ============================================ */
.basis-table-container {
  overflow-x: auto;
}

.basis-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

.basis-table th,
.basis-table td {
  padding: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.basis-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 9px;
}

.tenor-name {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
}

.price,
.basis,
.basis-pct,
.fair,
.variance,
.carry {
  font-family: "SF Mono", monospace;
  color: rgba(255,255,255,0.7);
}

.variance.outlier {
  background: rgba(248, 113, 113, 0.1);
  color: #f87171;
}

.opportunity {
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 9px;
}

.opportunity.underpriced {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

.opportunity.overpriced {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.opportunity.neutral {
  background: rgba(107, 114, 128, 0.2);
  color: rgba(255,255,255,0.6);
}

/* ============================================
   ROLL & STRATEGY ANALYSIS
   ============================================ */
.roll-analysis,
.strategy-analysis {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.roll-item,
.strategy-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.roll-item .label,
.strategy-item .label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.roll-item .value,
.strategy-item .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.roll-item .value.cyan,
.roll-item .value.positive,
.roll-item .value.negative {
  font-family: "SF Mono", monospace;
}

.roll-item .value.positive,
.strategy-item .value.positive {
  color: #4ade80;
}

.roll-item .value.negative {
  color: #f87171;
}

.roll-item.total,
.strategy-item.total {
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 8px;
}

.strategy-item .value.accent {
  color: #f59e0b;
}

/* ============================================
   VOLATILITY METRICS
   ============================================ */
.volatility-metrics {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.vol-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.vol-item .label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.vol-item .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
  color: rgba(255,255,255,0.7);
}

.vol-item .value.accent {
  color: #f59e0b;
}

.vol-item .value.blue {
  color: #60a5fa;
}

.vol-item .value.cyan {
  color: #06b6d4;
}

.vol-item.total {
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 8px;
}

/* ============================================
   DRIVERS LIST
   ============================================ */
.drivers-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.driver-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: rgba(255,255,255,0.02);
  border-radius: 6px;
  font-size: 11px;
}

.driver-name {
  flex: 1;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.driver-impact {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
}

.driver-impact.positive {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

.driver-impact.negative {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.driver-value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
  min-width: 50px;
  text-align: right;
}

/* ============================================
   FORECAST METRICS
   ============================================ */
.forecast-metrics {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.forecast-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.forecast-item .label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.forecast-item .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.forecast-item .value.cyan {
  color: #06b6d4;
}

.forecast-item .value.positive {
  color: #4ade80;
}

.forecast-item .value.accent {
  color: #f59e0b;
}

.forecast-item.total {
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 8px;
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
  padding: 8px;
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

.opportunities-table .tenor {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
}

.opportunities-table .price,
.opportunities-table .basis,
.opportunities-table .mispricing,
.opportunities-table .profit {
  font-family: "SF Mono", monospace;
}

.opportunities-table .mispricing.significant {
  background: rgba(248, 113, 113, 0.1);
  color: #f87171;
}

.opportunities-table .strategy {
  font-weight: 600;
  font-size: 9px;
}

.opportunities-table .strategy.buy {
  color: #4ade80;
}

.opportunities-table .strategy.short {
  color: #f87171;
}

.opportunities-table .strategy.neutral {
  color: rgba(255,255,255,0.4);
}

.opportunities-table .profit.positive {
  color: #4ade80;
}

/* ============================================
   RISK SUMMARY
   ============================================ */
.risk-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.risk-item {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.risk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.risk-type {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.7);
}

.risk-level {
  font-size: 9px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 3px;
  text-transform: uppercase;
}

.risk-level.high {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.risk-level.medium {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.risk-description {
  font-size: 10px;
  color: rgba(255,255,255,0.5);
  line-height: 1.4;
}

.risk-metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 10px;
  padding: 8px;
  background: rgba(255,255,255,0.01);
  border-radius: 4px;
  border-top: 1px solid rgba(255,255,255,0.05);
}

.risk-metric .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.risk-metric .value.positive {
  color: #4ade80;
}

.risk-metric .value.negative {
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
@media (max-width: 1200px) {
  .grid-4 {
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

  .risk-summary {
    grid-template-columns: 1fr;
  }
  .basis-analysis-page {
    padding: 16px 20px;
  }
}

@media (max-width: 768px) {
  .basis-analysis-page {
    padding: 16px;
  }

  .grid-4 {
    grid-template-columns: 1fr;
  }

  .basis-table,
  .opportunities-table {
    font-size: 9px;
  }

  .basis-table th,
  .basis-table td,
  .opportunities-table th,
  .opportunities-table td {
    padding: 6px;
  }

  .chart-container {
    height: 300px;
  }

  .chart-container.tall {
    height: 400px;
  }
}

@media (max-width: 480px) {
  .basis-analysis-page {
    padding: 12px;
  }
  .chart-container {
    height: 250px;
  }
  .chart-container.tall {
    height: 300px;
  }
  .basis-table,
  .opportunities-table {
    font-size: 8px;
  }
  .basis-table th,
  .basis-table td,
  .opportunities-table th,
  .opportunities-table td {
    padding: 4px;
  }
}
</style>
