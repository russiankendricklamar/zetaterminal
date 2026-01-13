<!-- src/pages/MarginFinancing.vue -->
<template>
  <div class="margin-financing-page">
    
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Маржа и финансирование</h1>
        <p class="page-subtitle">Управление маржой, финансированием и стоимостью позиций</p>
      </div>
      
      <div class="header-right">
        <!-- Position Type -->
        <div class="control-group">
          <label class="control-label">Позиция:</label>
          <select v-model="selectedPosition" class="position-select" @change="updateMargin">
            <option value="bond-long">Long фьючерс на облигацию</option>
            <option value="bond-short">Short фьючерс на облигацию</option>
            <option value="equity-long">Long позиция в акциях</option>
            <option value="fx-spot">Валютный спот</option>
            <option value="commodity">Позиция в товарах</option>
          </select>
        </div>

        <!-- Time Horizon -->
        <div class="control-group">
          <label class="control-label">Горизонт:</label>
          <select v-model="selectedHorizon" class="horizon-select" @change="updateMargin">
            <option value="1d">1 день</option>
            <option value="1w">1 неделя</option>
            <option value="1m">1 месяц</option>
            <option value="3m">3 месяца</option>
          </select>
        </div>

        <!-- Update Button -->
        <button @click="updateMargin" class="btn-primary" :disabled="calculating">
          <span v-if="!calculating">Пересчитать</span>
          <span v-else>↺ Считаю...</span>
        </button>
      </div>
    </div>

    <!-- Margin Overview -->
    <div class="grid-3">
      <!-- Initial Margin -->
      <div class="margin-card">
        <div class="margin-header">
          <h3>Начальная маржа</h3>
          <span class="margin-unit">Начальная маржа</span>
        </div>
        <div class="margin-value accent">
          {{ formatCompactCurrency(marginData.initialMargin) }}
        </div>
        <div class="margin-details">
          <div class="detail">
            <span class="label">% позиции</span>
            <span class="value">{{ marginData.initialMarginPct.toFixed(2) }}%</span>
          </div>
          <div class="detail">
            <span class="label">За контракт</span>
            <span class="value">{{ formatCurrency(marginData.initialMarginPerContract) }}</span>
          </div>
        </div>
      </div>

      <!-- Maintenance Margin -->
      <div class="margin-card">
        <div class="margin-header">
          <h3>Поддерживающая маржа</h3>
          <span class="margin-unit">Поддерживающая маржа</span>
        </div>
        <div class="margin-value blue">
          {{ formatCompactCurrency(marginData.maintenanceMargin) }}
        </div>
        <div class="margin-details">
          <div class="detail">
            <span class="label">% позиции</span>
            <span class="value">{{ marginData.maintenanceMarginPct.toFixed(2) }}%</span>
          </div>
          <div class="detail">
            <span class="label">Запас</span>
            <span class="value" :class="marginData.marginCushion >= 0 ? 'positive' : 'negative'">
              {{ formatCompactCurrency(marginData.marginCushion) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Financing Cost -->
      <div class="margin-card">
        <div class="margin-header">
          <h3>Стоимость финансирования</h3>
          <span class="margin-unit">Стоимость финансирования</span>
        </div>
        <div class="margin-value" :class="marginData.financingCost >= 0 ? 'positive' : 'negative'">
          {{ marginData.financingCost >= 0 ? '+' : '' }}{{ formatCompactCurrency(marginData.financingCost) }}
        </div>
        <div class="margin-details">
          <div class="detail">
            <span class="label">Годовая ставка</span>
            <span class="value">{{ marginData.financingRate.toFixed(2) }}%</span>
          </div>
          <div class="detail">
            <span class="label">Период</span>
            <span class="value">{{ selectedHorizon }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Financing Sources -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Источники и стоимость финансирования</h3>
        <span class="card-subtitle">Сравнение различных источников финансирования</span>
      </div>
      <div class="financing-sources-container">
        <table class="financing-sources-table">
          <thead>
            <tr>
              <th class="col-source">Источник</th>
              <th class="col-type">Тип</th>
              <th class="col-rate">Ставка (%)</th>
              <th class="col-spread">Спред (bp)</th>
              <th class="col-amount">Доступно</th>
              <th class="col-cost">Стоимость {{ selectedHorizon }}</th>
              <th class="col-rating">Рейтинг</th>
              <th class="col-action">Действие</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="source in financingSources" :key="source.id" :class="source.selected ? 'selected' : ''">
              <td class="col-source">{{ source.name }}</td>
              <td class="col-type">
                <span class="type-badge" :class="source.type.toLowerCase()">{{ source.type }}</span>
              </td>
              <td class="col-rate mono">{{ source.rate.toFixed(3) }}%</td>
              <td class="col-spread mono">{{ source.spread.toFixed(0) }}bp</td>
              <td class="col-amount">{{ formatCompactCurrency(source.available) }}</td>
              <td class="col-cost accent mono">{{ formatCompactCurrency(source.cost) }}</td>
              <td class="col-rating">
                <span class="rating-badge" :class="source.rating.toLowerCase()">{{ source.rating }}</span>
              </td>
              <td class="col-action">
                <button 
                  @click="toggleFinancingSource(source.id)"
                  :class="source.selected ? 'btn-selected' : 'btn-unselected'"
                >
                  {{ source.selected ? '✓' : '○' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Margin & Financing Analysis -->
    <div class="grid-2">
      <!-- Margin Requirement Breakdown -->
      <div class="card">
        <div class="card-header">
          <h3>Разложение требования маржи</h3>
          <span class="card-subtitle">Разложение требования маржи</span>
        </div>
        <div class="margin-breakdown">
          <div class="breakdown-item">
            <span class="label">Position Size</span>
            <span class="value accent">{{ formatCompactCurrency(marginData.positionSize) }}</span>
          </div>
          <div class="breakdown-item">
            <span class="label">Регуляторное требование</span>
            <span class="value blue">{{ marginData.regulatoryMarginPct.toFixed(2) }}%</span>
          </div>
          <div class="breakdown-item">
            <span class="label">Требование брокера</span>
            <span class="value blue">{{ marginData.brokerMarginPct.toFixed(2) }}%</span>
          </div>
          <div class="breakdown-item">
            <span class="label">Корректировка риска</span>
            <span class="value" :class="marginData.riskAdjustment >= 0 ? 'positive' : 'negative'">
              {{ marginData.riskAdjustment >= 0 ? '+' : '' }}{{ marginData.riskAdjustment.toFixed(2) }}%
            </span>
          </div>
          <div class="breakdown-item total">
            <span class="label">Общая требуемая маржа</span>
            <span class="value accent">{{ marginData.totalRequiredMargin.toFixed(2) }}%</span>
          </div>
        </div>
      </div>

      <!-- Financing Cost Breakdown -->
      <div class="card">
        <div class="chart-header">
          <h3>Разложение стоимости финансирования</h3>
          <span class="chart-subtitle">Компоненты стоимости финансирования</span>
        </div>
        <div class="chart-container">
          <canvas ref="financingCostChartRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Margin Utilization -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Использование маржи</h3>
        <span class="card-subtitle">Использование доступной маржи</span>
      </div>
      <div class="margin-utilization">
        <div class="utilization-item">
          <span class="label">Cash Balance</span>
          <span class="value accent">{{ formatCompactCurrency(marginData.cashBalance) }}</span>
        </div>
        <div class="utilization-bar-container">
          <div class="utilization-section">
            <div class="section-name">Используемая маржа</div>
            <div class="section-bar">
              <div class="bar-fill used" :style="{ width: marginData.usedMarginPct + '%' }"></div>
            </div>
            <span class="section-value">{{ marginData.usedMarginPct.toFixed(1) }}%</span>
          </div>
          <div class="utilization-section">
            <div class="section-name">Доступная маржа</div>
            <div class="section-bar">
              <div class="bar-fill available" :style="{ width: marginData.availableMarginPct + '%' }"></div>
            </div>
            <span class="section-value">{{ marginData.availableMarginPct.toFixed(1) }}%</span>
          </div>
        </div>
        <div class="utilization-metrics">
          <div class="metric">
            <span class="label">Используемая маржа</span>
            <span class="value used">{{ formatCompactCurrency(marginData.usedMargin) }}</span>
          </div>
          <div class="metric">
            <span class="label">Доступная маржа</span>
            <span class="value available">{{ formatCompactCurrency(marginData.availableMargin) }}</span>
          </div>
          <div class="metric">
            <span class="label">Избыточная маржа</span>
            <span class="value" :class="marginData.excessMargin >= 0 ? 'positive' : 'negative'">
              {{ marginData.excessMargin >= 0 ? '+' : '' }}{{ formatCompactCurrency(marginData.excessMargin) }}
            </span>
          </div>
          <div class="metric">
            <span class="label">Коэффициент маржи</span>
            <span class="value accent">{{ marginData.marginRatio.toFixed(2) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Repo vs Direct Financing -->
    <div class="grid-2">
      <!-- Repo Market -->
      <div class="card">
        <div class="card-header">
          <h3>Репо финансирование</h3>
          <span class="card-subtitle">Репо ставки по срокам</span>
        </div>
        <div class="chart-container">
          <canvas ref="repoRatesRef"></canvas>
        </div>
      </div>

      <!-- Direct Loan Financing -->
      <div class="card">
        <div class="card-header">
          <h3>Прямое кредитное финансирование</h3>
          <span class="card-subtitle">Кредитные ставки по срокам</span>
        </div>
        <div class="chart-container">
          <canvas ref="loanRatesRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Collateral & Haircut -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Анализ залога и скидок</h3>
        <span class="card-subtitle">Стоимость залога и применяемые скидки</span>
      </div>
      <div class="collateral-table-container">
        <table class="collateral-table">
          <thead>
            <tr>
              <th>Тип залога</th>
              <th>Рыночная стоимость</th>
              <th>Скидка (%)</th>
              <th>Сумма скидки</th>
              <th>Стоимость залога</th>
              <th>Рейтинг</th>
              <th>Duration</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="collateral in collateralData" :key="collateral.id">
              <td class="collateral-name">{{ collateral.name }}</td>
              <td class="value mono">{{ formatCompactCurrency(collateral.marketValue) }}</td>
              <td class="value mono">{{ collateral.haircut.toFixed(2) }}%</td>
              <td class="value mono negative">{{ formatCompactCurrency(collateral.haircutAmount) }}</td>
              <td class="value accent mono">{{ formatCompactCurrency(collateral.collateralValue) }}</td>
              <td class="rating">
                <span class="rating-badge" :class="collateral.rating.toLowerCase()">{{ collateral.rating }}</span>
              </td>
              <td class="value mono">{{ collateral.duration.toFixed(2) }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="total-row">
              <td colspan="2"><strong>ИТОГО</strong></td>
              <td class="avg mono"><strong>{{ collateralData.reduce((sum, c) => sum + c.haircut, 0) / collateralData.length | 0 }}%</strong></td>
              <td class="value mono"><strong>{{ formatCompactCurrency(collateralData.reduce((sum, c) => sum + c.haircutAmount, 0)) }}</strong></td>
              <td class="accent mono"><strong>{{ formatCompactCurrency(collateralData.reduce((sum, c) => sum + c.collateralValue, 0)) }}</strong></td>
              <td colspan="2"></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Financing Scenarios -->
    <div class="card full-width">
      <div class="chart-header">
        <h3>Сценарии стоимости финансирования</h3>
        <span class="chart-subtitle">Стоимость финансирования при различных ставках</span>
      </div>
      <div class="chart-container tall">
        <canvas ref="financingScenariosRef"></canvas>
      </div>
    </div>

    <!-- Margin Call Risk -->
    <div class="grid-2">
      <!-- Margin Call Analysis -->
      <div class="card">
        <div class="card-header">
          <h3>Margin Call Risk</h3>
          <span class="card-subtitle">Вероятность margin call при движениях рынка</span>
        </div>
        <div class="margin-call-analysis">
          <div class="risk-item">
            <span class="label">Текущий коэффициент маржи</span>
            <span class="value accent">{{ marginData.marginRatio.toFixed(2) }}</span>
          </div>
          <div class="risk-item">
            <span class="label">Минимально требуемый коэффициент</span>
            <span class="value blue">{{ marginData.minMarginRatio.toFixed(2) }}</span>
          </div>
          <div class="risk-item">
            <span class="label">Расстояние до margin call</span>
            <span class="value" :class="marginData.distanceToCall >= 0 ? 'positive' : 'negative'">
              {{ marginData.distanceToCall >= 0 ? '+' : '' }}{{ marginData.distanceToCall.toFixed(2) }}%
            </span>
          </div>
          <div class="risk-item">
            <span class="label">Убыток до margin call</span>
            <span class="value negative">{{ formatCompactCurrency(marginData.lossPct) }}</span>
          </div>
          <div class="risk-item total">
            <span class="label">Вероятность (1Н)</span>
            <span class="value" :class="marginData.marginCallProb >= 0.3 ? 'negative' : 'positive'">
              {{ (marginData.marginCallProb * 100).toFixed(1) }}%
            </span>
          </div>
        </div>
      </div>

      <!-- Stress Testing -->
      <div class="card">
        <div class="chart-header">
          <h3>Маржа при стрессе</h3>
          <span class="chart-subtitle">Маржа при экстремальных сценариях</span>
        </div>
        <div class="chart-container">
          <canvas ref="stressTestRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Financing Optimization -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Financing Optimization</h3>
        <span class="card-subtitle">Оптимальная структура финансирования</span>
      </div>
      <div class="optimization-table">
        <table class="optimization-data-table">
          <thead>
            <tr>
              <th>Стратегия</th>
              <th>Репо %</th>
              <th>Кредит %</th>
              <th>Средняя ставка</th>
              <th>Месячная стоимость</th>
              <th>Годовая стоимость</th>
              <th>Уровень риска</th>
              <th>Рекомендация</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="strategy in optimizationStrategies" :key="strategy.id" :class="strategy.recommended ? 'recommended' : ''">
              <td class="strategy-name">{{ strategy.name }}</td>
              <td class="value mono">{{ strategy.repoPercentage.toFixed(0) }}%</td>
              <td class="value mono">{{ strategy.loanPercentage.toFixed(0) }}%</td>
              <td class="value mono">{{ strategy.avgRate.toFixed(3) }}%</td>
              <td class="value accent mono">{{ formatCompactCurrency(strategy.monthlyCost) }}</td>
              <td class="value accent mono">{{ formatCompactCurrency(strategy.annualCost) }}</td>
              <td class="risk-level">
                <span class="badge" :class="strategy.riskLevel.toLowerCase()">{{ strategy.riskLevel }}</span>
              </td>
              <td class="recommend">
                <span v-if="strategy.recommended" class="badge recommended">✓ Лучшая</span>
                <span v-else class="badge">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Real-time Financing Dashboard -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Панель финансирования в реальном времени</h3>
        <span class="card-subtitle">Текущие параметры финансирования</span>
      </div>
      <div class="rt-dashboard">
        <div class="rt-item">
          <span class="label">Position Size</span>
          <span class="value">{{ formatCompactCurrency(marginData.positionSize) }}</span>
        </div>
        <div class="rt-item">
          <span class="label">Financing Rate</span>
          <span class="value accent">{{ marginData.financingRate.toFixed(3) }}%</span>
        </div>
        <div class="rt-item">
          <span class="label">Ежедневная стоимость финансирования</span>
          <span class="value" :class="marginData.dailyFinancingCost >= 0 ? 'positive' : 'negative'">
            {{ marginData.dailyFinancingCost >= 0 ? '+' : '' }}{{ formatCompactCurrency(marginData.dailyFinancingCost) }}
          </span>
        </div>
        <div class="rt-item">
          <span class="label">Использование маржи</span>
          <span class="value">{{ marginData.usedMarginPct.toFixed(1) }}%</span>
        </div>
        <div class="rt-item">
          <span class="label">Available Margin</span>
          <span class="value available">{{ formatCompactCurrency(marginData.availableMargin) }}</span>
        </div>
        <div class="rt-item">
          <span class="label">Margin Ratio</span>
          <span class="value accent">{{ marginData.marginRatio.toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span>• Модель: Regulatory + Broker Requirements</span>
      <span>• Частота: В реальном времени</span>
      <span>• Обновление: Непрерывно</span>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'

const selectedPosition = ref('bond-long')
const selectedHorizon = ref('1m')
const calculating = ref(false)

// Margin Data
const marginData = ref({
  positionSize: 10_000_000,
  initialMargin: 500_000,
  initialMarginPct: 5.0,
  initialMarginPerContract: 5000,
  maintenanceMargin: 400_000,
  maintenanceMarginPct: 4.0,
  marginCushion: 100_000,
  financingCost: 8_500,
  financingRate: 4.25,
  regulatoryMarginPct: 3.5,
  brokerMarginPct: 5.0,
  riskAdjustment: 0.5,
  totalRequiredMargin: 5.5,
  cashBalance: 2_000_000,
  usedMargin: 1_200_000,
  usedMarginPct: 60,
  availableMargin: 800_000,
  availableMarginPct: 40,
  excessMargin: 500_000,
  marginRatio: 2.5,
  minMarginRatio: 1.25,
  distanceToCall: 100,
  lossPct: -1_250_000,
  marginCallProb: 0.15,
  dailyFinancingCost: 1_160
})

// Financing Sources
const financingSources = ref([
  {
    id: 1,
    name: 'Overnight Repo',
    type: 'Repo',
    rate: 4.15,
    spread: 5,
    available: 5_000_000,
    cost: 4_792,
    rating: 'AAA',
    selected: true
  },
  {
    id: 2,
    name: 'Term Repo (1M)',
    type: 'Repo',
    rate: 4.22,
    spread: 12,
    available: 3_000_000,
    cost: 3_550,
    rating: 'AAA',
    selected: true
  },
  {
    id: 3,
    name: 'Bank Credit Line',
    type: 'Loan',
    rate: 4.35,
    spread: 25,
    available: 5_000_000,
    cost: 4_583,
    rating: 'A+',
    selected: false
  },
  {
    id: 4,
    name: 'Prime Brokerage Loan',
    type: 'Loan',
    rate: 4.5,
    spread: 40,
    available: 2_000_000,
    cost: 1_875,
    rating: 'AA',
    selected: false
  },
  {
    id: 5,
    name: 'Tri-party Repo',
    type: 'Repo',
    rate: 4.18,
    spread: 8,
    available: 4_000_000,
    cost: 3_483,
    rating: 'AAA',
    selected: true
  }
])

// Collateral Data
const collateralData = ref([
  {
    id: 1,
    name: 'US Treasury 10Y',
    marketValue: 2_000_000,
    haircut: 0.5,
    haircutAmount: 10_000,
    collateralValue: 1_990_000,
    rating: 'AAA',
    duration: 8.5
  },
  {
    id: 2,
    name: 'Corporate Bonds (A)',
    marketValue: 1_500_000,
    haircut: 2.0,
    haircutAmount: 30_000,
    collateralValue: 1_470_000,
    rating: 'A',
    duration: 5.2
  },
  {
    id: 3,
    name: 'Equity Index ETF',
    marketValue: 3_000_000,
    haircut: 8.0,
    haircutAmount: 240_000,
    collateralValue: 2_760_000,
    rating: 'BBB',
    duration: 1.0
  },
  {
    id: 4,
    name: 'Commodity Futures',
    marketValue: 1_500_000,
    haircut: 12.0,
    haircutAmount: 180_000,
    collateralValue: 1_320_000,
    rating: 'Not Rated',
    duration: 0.25
  }
])

// Optimization Strategies
const optimizationStrategies = ref([
  {
    id: 1,
    name: 'Max Repo (Low Cost)',
    repoPercentage: 80,
    loanPercentage: 20,
    avgRate: 4.19,
    monthlyCost: 3_495,
    annualCost: 41_940,
    riskLevel: 'Low',
    recommended: false
  },
  {
    id: 2,
    name: 'Balanced (Recommended)',
    repoPercentage: 60,
    loanPercentage: 40,
    avgRate: 4.27,
    monthlyCost: 3_558,
    annualCost: 42_700,
    riskLevel: 'Medium',
    recommended: true
  },
  {
    id: 3,
    name: 'Diversified (Low Rollover)',
    repoPercentage: 40,
    loanPercentage: 60,
    avgRate: 4.35,
    monthlyCost: 3_625,
    annualCost: 43_500,
    riskLevel: 'Medium',
    recommended: false
  },
  {
    id: 4,
    name: 'Max Loan (Stable)',
    repoPercentage: 20,
    loanPercentage: 80,
    avgRate: 4.42,
    monthlyCost: 3_683,
    annualCost: 44_200,
    riskLevel: 'High',
    recommended: false
  }
])

// Chart References
const financingCostChartRef = ref<HTMLCanvasElement | null>(null)
const repoRatesRef = ref<HTMLCanvasElement | null>(null)
const loanRatesRef = ref<HTMLCanvasElement | null>(null)
const financingScenariosRef = ref<HTMLCanvasElement | null>(null)
const stressTestRef = ref<HTMLCanvasElement | null>(null)

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
  return '₽' + (val / 1000).toFixed(0) + 'K'
}

const toggleFinancingSource = (id: number) => {
  const source = financingSources.value.find(s => s.id === id)
  if (source) {
    source.selected = !source.selected
    updateMargin()
  }
}

const updateMargin = () => {
  initCharts()
}

const initCharts = () => {
  Object.values(charts).forEach(chart => {
    if (chart) chart.destroy()
  })
  charts = {}

  // Financing Cost Breakdown
  if (financingCostChartRef.value?.getContext('2d')) {
    charts.financing = new Chart(financingCostChartRef.value.getContext('2d') as any, {
      type: 'doughnut',
      data: {
        labels: ['Repo Cost', 'Loan Cost', 'Operational Fee', 'Other'],
        datasets: [{
          data: [4792, 3550, 1000, 150],
          backgroundColor: [
            'rgba(96, 165, 250, 0.8)',
            'rgba(74, 222, 128, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(168, 85, 247, 0.8)'
          ],
          borderColor: ['#60a5fa', '#4ade80', '#f59e0b', '#a855f7'],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: 'rgba(255,255,255,0.6)' } }
        }
      }
    } as any)
  }

  // Repo Rates by Tenor
  if (repoRatesRef.value?.getContext('2d')) {
    charts.repo = new Chart(repoRatesRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: ['O/N', '1W', '2W', '1M', '3M', '6M'],
        datasets: [{
          label: 'Repo Rate (%)',
          data: [4.15, 4.16, 4.18, 4.22, 4.28, 4.32],
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
        plugins: { legend: { labels: { color: 'rgba(255,255,255,0.6)' } } },
        scales: {
          x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(255,255,255,0.3)' } }
        }
      }
    } as any)
  }

  // Loan Rates by Tenor
  if (loanRatesRef.value?.getContext('2d')) {
    charts.loan = new Chart(loanRatesRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: ['O/N', '1W', '2W', '1M', '3M', '6M'],
        datasets: [{
          label: 'Loan Rate (%)',
          data: [4.35, 4.37, 4.40, 4.45, 4.52, 4.58],
          borderColor: '#4ade80',
          backgroundColor: 'rgba(74, 222, 128, 0.08)',
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

  // Financing Scenarios
  if (financingScenariosRef.value?.getContext('2d')) {
    const rates = ['3.5%', '3.75%', '4.0%', '4.25%', '4.5%', '4.75%', '5.0%']
    const monthlyCosts = [3200, 3350, 3500, 3558, 3700, 3850, 4000]

    charts.scenarios = new Chart(financingScenariosRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: rates,
        datasets: [
          {
            label: 'Monthly Cost (Repo 60%)',
            data: monthlyCosts,
            borderColor: '#60a5fa',
            backgroundColor: 'rgba(96, 165, 250, 0.08)',
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            borderWidth: 2
          },
          {
            label: 'Current Rate',
            data: [3558, 3558, 3558, 3558, 3558, 3558, 3558],
            borderColor: '#f59e0b',
            backgroundColor: 'transparent',
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

  // Stress Test
  if (stressTestRef.value?.getContext('2d')) {
    charts.stress = new Chart(stressTestRef.value.getContext('2d') as any, {
      type: 'bar',
      data: {
        labels: ['-10%', '-5%', 'Base', '+5%', '+10%'],
        datasets: [{
          label: 'Margin Ratio',
          data: [3.8, 3.1, 2.5, 1.9, 1.2],
          backgroundColor: [
            'rgba(74, 222, 128, 0.6)',
            'rgba(245, 158, 11, 0.6)',
            'rgba(96, 165, 250, 0.6)',
            'rgba(245, 158, 11, 0.6)',
            'rgba(248, 113, 113, 0.6)'
          ],
          borderColor: ['#4ade80', '#f59e0b', '#60a5fa', '#f59e0b', '#f87171'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
          y: {
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: 'rgba(255,255,255,0.3)' },
            title: { display: true, text: 'Margin Ratio' }
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
.margin-financing-page {
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
.horizon-select {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  padding: 4px 8px;
  cursor: pointer;
}

.position-select option,
.horizon-select option {
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
   MARGIN CARDS
   ============================================ */
.margin-card {
  background: rgba(30, 32, 40, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.margin-header {
  margin-bottom: 4px;
}

.margin-header h3 {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  margin: 0;
  text-transform: uppercase;
}

.margin-unit {
  font-size: 9px;
  color: rgba(255,255,255,0.3);
  display: block;
  margin-top: 2px;
}

.margin-value {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.margin-value.accent {
  color: #f59e0b;
}

.margin-value.blue {
  color: #60a5fa;
}

.margin-value.positive {
  color: #4ade80;
}

.margin-value.negative {
  color: #f87171;
}

.margin-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-top: 1px solid rgba(255,255,255,0.05);
  padding-top: 6px;
}

.detail {
  display: flex;
  justify-content: space-between;
  font-size: 9px;
}

.detail .label {
  color: rgba(255,255,255,0.4);
}

.detail .value {
  font-weight: 600;
  color: rgba(255,255,255,0.6);
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

/* ============================================
   FINANCING SOURCES TABLE
   ============================================ */
.financing-sources-container {
  overflow-x: auto;
}

.financing-sources-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

.financing-sources-table th,
.financing-sources-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.financing-sources-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 9px;
}

.col-source {
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

.type-badge.repo {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
}

.type-badge.loan {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

.rating-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 9px;
  font-weight: 600;
}

.rating-badge.aaa {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

.rating-badge.aa {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
}

.rating-badge.a {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.financing-sources-table tr.selected {
  background: rgba(59, 130, 246, 0.1);
}

.btn-unselected,
.btn-selected {
  padding: 4px 8px;
  border: 1px solid;
  border-radius: 4px;
  background: transparent;
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-unselected {
  border-color: rgba(255,255,255,0.2);
  color: rgba(255,255,255,0.3);
}

.btn-unselected:hover {
  border-color: rgba(74, 222, 128, 0.5);
  color: #4ade80;
}

.btn-selected {
  border-color: rgba(74, 222, 128, 0.5);
  color: #4ade80;
  background: rgba(74, 222, 128, 0.1);
}

/* ============================================
   MARGIN BREAKDOWN
   ============================================ */
.margin-breakdown {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.breakdown-item .label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.breakdown-item .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.breakdown-item .value.accent {
  color: #f59e0b;
}

.breakdown-item .value.blue {
  color: #60a5fa;
}

.breakdown-item .value.positive {
  color: #4ade80;
}

.breakdown-item .value.negative {
  color: #f87171;
}

.breakdown-item.total {
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
   MARGIN UTILIZATION
   ============================================ */
.margin-utilization {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.utilization-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.utilization-item .label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.utilization-item .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.utilization-item .value.accent {
  color: #f59e0b;
}

.utilization-bar-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.utilization-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-name {
  font-size: 10px;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
  min-width: 120px;
}

.section-bar {
  flex: 1;
  height: 8px;
  background: rgba(255,255,255,0.05);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
}

.bar-fill.used {
  background: linear-gradient(90deg, #60a5fa, #3b82f6);
}

.bar-fill.available {
  background: linear-gradient(90deg, #4ade80, #22c55e);
}

.section-value {
  font-size: 10px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  min-width: 40px;
  text-align: right;
}

.utilization-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: rgba(255,255,255,0.02);
  border-radius: 6px;
  font-size: 11px;
}

.metric .label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.metric .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.metric .value.used {
  color: #60a5fa;
}

.metric .value.available {
  color: #4ade80;
}

.metric .value.positive {
  color: #4ade80;
}

.metric .value.negative {
  color: #f87171;
}

.metric .value.accent {
  color: #f59e0b;
}

/* ============================================
   COLLATERAL TABLE
   ============================================ */
.collateral-table-container {
  overflow-x: auto;
}

.collateral-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

.collateral-table th,
.collateral-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.collateral-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 9px;
}

.collateral-name {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
}

.collateral-table .value {
  font-family: "SF Mono", monospace;
  color: rgba(255,255,255,0.7);
}

.collateral-table .value.accent {
  color: #f59e0b;
}

.collateral-table .value.negative {
  color: #f87171;
}

.collateral-table .total-row {
  background: rgba(59, 130, 246, 0.1);
  border-top: 2px solid rgba(59, 130, 246, 0.3);
}

/* ============================================
   MARGIN CALL ANALYSIS
   ============================================ */
.margin-call-analysis {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.risk-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.risk-item .label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.risk-item .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.risk-item .value.accent {
  color: #f59e0b;
}

.risk-item .value.blue {
  color: #60a5fa;
}

.risk-item .value.positive {
  color: #4ade80;
}

.risk-item .value.negative {
  color: #f87171;
}

.risk-item.total {
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 8px;
}

/* ============================================
   OPTIMIZATION TABLE
   ============================================ */
.optimization-table {
  overflow-x: auto;
}

.optimization-data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

.optimization-data-table th,
.optimization-data-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.optimization-data-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 9px;
}

.strategy-name {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
}

.optimization-data-table .value {
  font-family: "SF Mono", monospace;
  color: rgba(255,255,255,0.7);
}

.optimization-data-table .value.mono {
  font-family: "SF Mono", monospace;
}

.optimization-data-table .value.accent {
  color: #f59e0b;
}

.risk-level .badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 9px;
  font-weight: 600;
}

.badge.low {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

.badge.medium {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.badge.high {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.badge.recommended {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.optimize-data-table tr.recommended {
  background: rgba(59, 130, 246, 0.1);
}

/* ============================================
   REAL-TIME DASHBOARD
   ============================================ */
.rt-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.rt-item {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 10px;
}

.rt-item .label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.rt-item .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
  color: #fff;
}

.rt-item .value.accent {
  color: #f59e0b;
}

.rt-item .value.available {
  color: #4ade80;
}

.rt-item .value.positive {
  color: #4ade80;
}

.rt-item .value.negative {
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

  .grid-3 {
    grid-template-columns: 1fr;
  }

  .grid-2 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .margin-financing-page {
    padding: 16px;
  }

  .financing-sources-table,
  .collateral-table,
  .optimization-data-table {
    font-size: 9px;
  }

  .financing-sources-table th,
  .financing-sources-table td,
  .collateral-table th,
  .collateral-table td,
  .optimization-data-table th,
  .optimization-data-table td {
    padding: 6px;
  }

  .chart-container {
    height: 300px;
  }

  .chart-container.tall {
    height: 400px;
  }

  .rt-dashboard {
    grid-template-columns: 1fr;
  }
}
</style>
