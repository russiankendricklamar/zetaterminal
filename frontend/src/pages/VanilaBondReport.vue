<!-- src/pages/VanillaBondReport.vue -->
<template>
  <div class="page-container">
    
    <!-- HEADER -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Vanilla Bond Report</h1>
        <p class="section-subtitle">
          Паспорт выпуска и аналитика по ISIN: <span class="text-accent">{{ isin || '—' }}</span>
        </p>
      </div>
      <div class="header-actions">
        <div class="glass-pill">
          <span class="lbl-mini">Поиск</span>
          <input 
            v-model="localIsin"
            type="text"
            class="search-input"
            placeholder="RU000A103943"
            @keyup.enter="onChangeIsin"
          />
          <button class="btn-search" @click="onChangeIsin" :disabled="!localIsin">🔍</button>
        </div>
      </div>
    </div>

    <!-- STATES -->
    <section v-if="loading" class="state-section">
      <div class="glass-card">
        <span class="spinner"></span> Загрузка данных...
      </div>
    </section>

    <section v-else-if="error" class="state-section">
      <div class="glass-card error">⚠ {{ error }}</div>
    </section>

    <section v-else-if="!report" class="state-section">
      <div class="glass-card">Введите ISIN для генерации отчёта</div>
    </section>

    <!-- REPORT -->
    <section v-else class="report-content">
      
      <!-- BLOCK 1: General Info (2 cols) -->
      <div class="grid-2">
        <div class="glass-card">
          <h3>Общие сведения</h3>
          <table class="info-table">
            <tr><td>Эмитент</td><td>{{ report.issuer }}</td></tr>
            <tr><td>ISIN</td><td class="mono">{{ report.isin }}</td></tr>
            <tr><td>Страна</td><td>{{ report.risk_country || '—' }}</td></tr>
            <tr><td>Сектор</td><td>{{ report.sector || '—' }}</td></tr>
            <tr><td>Отрасль</td><td>{{ report.industry || '—' }}</td></tr>
            <tr><td>Объём</td><td class="mono">{{ formatNumber(report.outstanding_amount) || '—' }}</td></tr>
          </table>
        </div>

        <div class="glass-card">
          <h3>Параметры выпуска</h3>
          <table class="info-table">
            <tr><td>Дата начала</td><td class="mono">{{ formatDate(report.issue_info?.issue_date) }}</td></tr>
            <tr><td>Дата погашения</td><td class="mono">{{ formatDate(report.issue_info?.maturity_date) }}</td></tr>
            <tr><td>Ставка купона</td><td><span v-if="report.issue_info?.coupon_rate !== null" class="accent">{{ (report.issue_info.coupon_rate * 100).toFixed(2) }}%</span><span v-else>—</span></td></tr>
            <tr><td>Купонов в год</td><td class="mono">{{ report.issue_info?.coupon_per_year ?? '—' }}</td></tr>
          </table>
        </div>
      </div>

      <div class="grid-3">
        <div class="glass-card">
          <h3>Рейтинг эмиссии</h3>
          <div v-if="report.ratings?.issue?.length" class="ratings-list">
            <div v-for="(r, idx) in report.ratings.issue" :key="idx" class="rating-item">
              <span class="agency">{{ r.agency }}</span>
              <span class="grade">{{ r.rating }}</span>
              <span class="date mono">{{ formatDate(r.date) }}</span>
            </div>
          </div>
          <p v-else class="muted">Нет данных</p>
        </div>

        <div class="glass-card">
          <h3>Рейтинг эмитента</h3>
          <div v-if="report.ratings?.issuer?.length" class="ratings-list">
            <div v-for="(r, idx) in report.ratings.issuer" :key="idx" class="rating-item">
              <span class="agency">{{ r.agency }}</span>
              <div>
                <span class="grade">{{ r.rating }}</span>
                <span class="outlook" v-if="r.outlook">{{ r.outlook }}</span>
              </div>
              <span class="date mono">{{ formatDate(r.date) }}</span>
            </div>
          </div>
          <p v-else class="muted">Нет данных</p>
        </div>

        <div class="glass-card">
          <h3>Рейтинг гаранта</h3>
          <div v-if="report.ratings?.guarantor?.length" class="ratings-list">
            <div v-for="(r, idx) in report.ratings.guarantor" :key="idx" class="rating-item">
              <span class="agency">{{ r.agency }}</span>
              <span class="grade">{{ r.rating }}</span>
              <span class="date mono">{{ formatDate(r.date) }}</span>
            </div>
          </div>
          <p v-else class="muted">Нет данных</p>
        </div>
      </div>

      <div class="grid-3">
        <div class="glass-card">
          <div class="metric-header">
            <h3>Активность рынка</h3>
            <span class="activity-indicator" :class="isMarketActive ? 'active' : 'inactive'">
              <span class="indicator-dot"></span>
              {{ isMarketActive ? 'Активный рынок' : 'Неактивный рынок' }}
            </span>
          </div>
          <div class="metric-list">
            <div class="metric"><span>Кол-во торговых дней</span><span class="val badge badge-value">{{ report.market_activity?.trading_days ?? '—' }}</span></div>
            <div class="metric"><span>Кол-во сделок</span><span class="val badge badge-value">{{ report.market_activity?.trades ?? '—' }}</span></div>
            <div class="metric"><span>Объем торгов/объем выпуска в обращении</span><span class="val badge badge-value" v-if="report.market_activity?.turnover_to_outstanding !== null">{{ (report.market_activity.turnover_to_outstanding * 100).toFixed(2) }}%</span><span class="val badge badge-value" v-else>—</span></div>
            <div class="metric"><span>Наличие торгов в течение последних 30 календарных дней</span><span class="val badge" :class="report.market_activity?.traded_last_30d ? 'ok' : 'bad'">{{ report.market_activity?.traded_last_30d ? 'Да' : 'Нет' }}</span></div>
            <div class="metric"><span>Источник</span><span class="val badge badge-source">{{ report.market_activity?.source || 'MOEX' }}</span></div>
          </div>
        </div>

        <div class="glass-card">
          <h3>Котировка и доходность</h3>
          <div class="metric-list">
            <div class="metric"><span>Чистая цена</span><span class="val accent" v-if="report.pricing?.clean_price_pct !== null">{{ report.pricing.clean_price_pct.toFixed(2) }}%</span><span class="val" v-else>—</span></div>
            <div class="metric"><span>YTP (доходность)</span><span class="val accent" v-if="report.pricing?.ytm !== null">{{ (report.pricing.ytm * 100).toFixed(2) }}%</span><span class="val" v-else>—</span></div>
            <div class="metric"><span>G-spread</span><span class="val mono" v-if="report.pricing?.g_spread_bps !== null">{{ report.pricing.g_spread_bps.toFixed(0) }} б.п.</span><span class="val" v-else>—</span></div>
            <div class="metric"><span>G-curve (КБД)</span><span class="val mono" v-if="report.pricing?.g_curve_yield !== null">{{ (report.pricing.g_curve_yield * 100).toFixed(2) }}%</span><span class="val" v-else>—</span></div>
          </div>
        </div>

        <div class="glass-card">
          <h3>Индикаторы рыночного риска</h3>
          <div class="metric-list">
            <div class="metric">
              <span>Модифицированная дюрация (к погашению)</span>
              <span class="val badge badge-value" v-if="report.risk_indicators?.duration !== null">
                {{ report.risk_indicators.duration.toFixed(2) }}
              </span>
              <span class="val badge badge-value" v-else>—</span>
            </div>
            <div class="metric">
              <span>Выпуклость (к погашению)</span>
              <span class="val badge badge-value" v-if="report.risk_indicators?.convexity !== null">
                {{ report.risk_indicators.convexity.toFixed(2) }}
              </span>
              <span class="val badge badge-value" v-else>—</span>
            </div>
            <div class="metric">
              <span>DV01</span>
              <span class="val badge badge-value" v-if="report.risk_indicators?.dv01 !== null">
                {{ formatNumber(report.risk_indicators.dv01) }}
              </span>
              <span class="val badge badge-value" v-else>—</span>
            </div>
          </div>
          <div v-if="report.warnings?.length" class="warnings">
            <div v-for="(w, idx) in report.warnings" :key="idx" class="warning">⚠ {{ w }}</div>
          </div>
          <div v-else class="success">✓ Ошибок в данных нет</div>
        </div>

      </div>

      <!-- BLOCK 2: Price Chart (full width, tall) -->
      <div class="glass-card chart-card full-width">
        <div class="chart-top">
          <h3>Динамика цены</h3>
          <button class="btn-export" @click="exportChart('price')">💾 PNG</button>
        </div>
        <div class="chart-container tall">
          <canvas ref="priceHistoryRef"></canvas>
        </div>
      </div>

      <!-- BLOCK 3: Yield Chart (full width, tall) -->
      <div class="glass-card chart-card full-width">
        <div class="chart-top">
          <h3>Динамика доходности (YTM, G-curve, G-spread)</h3>
          <button class="btn-export" @click="exportChart('yield')">💾 PNG</button>
        </div>
        <div class="chart-container tall">
          <canvas ref="yieldDynamicsRef"></canvas>
        </div>
      </div>

      <!-- BLOCK 4: Index Comparison (full width) - NEW -->
      <div class="glass-card full-width">
        <div class="index-comparison-header">
          <div>
            <h3>Сравнение с индексами корпоративных облигаций Московской биржи</h3>
            <p class="index-subtitle">Позиционирование выпуска относительно бенчмарков по доходности</p>
          </div>
          <button class="btn-export" @click="exportChart('indices')">💾 PNG</button>
        </div>
        <div class="index-comparison-content">
          <div class="index-stats">
            <div class="stat-item">
              <span class="stat-label">Доходность индекса государственных облигаций (менее года)</span>
              <span class="stat-value">{{ indexYields.gov }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Доходность индекса корпоративных облигаций с рейтингом AAA</span>
              <span class="stat-value">{{ indexYields.aaa }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Доходность индекса корпоративных облигаций с рейтингом AA</span>
              <span class="stat-value">{{ indexYields.aa }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Доходность индекса корпоративных облигаций с рейтингом A</span>
              <span class="stat-value">{{ indexYields.a }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Доходность индекса корпоративных облигаций с рейтингом BBB</span>
              <span class="stat-value">{{ indexYields.bbb }}%</span>
            </div>
          </div>
          <div class="index-visualization">
            <div class="yield-scale">
              <span>12%</span>
              <span>14%</span>
              <span>16%</span>
              <span>18%</span>
              <span>20%</span>
              <span>22%</span>
              <span>24%</span>
            </div>
            <div class="yield-bar">
              <!-- Гос облигации -->
              <div class="benchmark" :style="{ left: getBenchmarkPosition(indexYields.gov) }">
                <div 
                  class="benchmark-dot"
                  @mouseenter="hoveredBenchmark = 'gov'"
                  @mouseleave="hoveredBenchmark = null"
                >
                  <div class="tooltip" v-if="hoveredBenchmark === 'gov'">
                    <div class="tooltip-title">Индекс государственных облигаций (менее года)</div>
                    <div class="tooltip-value">{{ indexYields.gov.toFixed(2) }}%</div>
                  </div>
                </div>
              </div>

              <!-- AAA корп облигации -->
              <div class="benchmark" :style="{ left: getBenchmarkPosition(indexYields.aaa) }">
                <div 
                  class="benchmark-dot"
                  @mouseenter="hoveredBenchmark = 'aaa'"
                  @mouseleave="hoveredBenchmark = null"
                >
                  <div class="tooltip" v-if="hoveredBenchmark === 'aaa'">
                    <div class="tooltip-title">Индекс корп. облигаций AAA</div>
                    <div class="tooltip-value">{{ indexYields.aaa.toFixed(2) }}%</div>
                  </div>
                </div>
              </div>

              <!-- AA корп облигации -->
              <div class="benchmark" :style="{ left: getBenchmarkPosition(16.89) }">
                <div 
                  class="benchmark-dot"
                  @mouseenter="hoveredBenchmark = 'aa'"
                  @mouseleave="hoveredBenchmark = null"
                >
                  <div class="tooltip" v-if="hoveredBenchmark === 'aa'">
                    <div class="tooltip-title">Индекс корп. облигаций AA</div>
                    <div class="tooltip-value">16.89%</div>
                  </div>
                </div>
              </div>

              <!-- A корп облигации -->
              <div class="benchmark" :style="{ left: getBenchmarkPosition(indexYields.a) }">
                <div 
                  class="benchmark-dot"
                  @mouseenter="hoveredBenchmark = 'a'"
                  @mouseleave="hoveredBenchmark = null"
                >
                  <div class="tooltip" v-if="hoveredBenchmark === 'a'">
                    <div class="tooltip-title">Индекс корп. облигаций A</div>
                    <div class="tooltip-value">{{ indexYields.a.toFixed(2) }}%</div>
                  </div>
                </div>
              </div>

              <!-- BBB корп облигации -->
              <div class="benchmark" :style="{ left: getBenchmarkPosition(22.68) }">
                <div 
                  class="benchmark-dot"
                  @mouseenter="hoveredBenchmark = 'bbb'"
                  @mouseleave="hoveredBenchmark = null"
                >
                  <div class="tooltip" v-if="hoveredBenchmark === 'bbb'">
                    <div class="tooltip-title">Индекс корп. облигаций BBB</div>
                    <div class="tooltip-value">22.68%</div>
                  </div>
                </div>
              </div>

              <!-- Оцениваемая облигация -->
              <div class="our-bond" :style="{ left: getBenchmarkPosition(indexYields.our) }">
                <div 
                  class="our-bond-dot"
                  @mouseenter="hoveredBenchmark = 'our'"
                  @mouseleave="hoveredBenchmark = null"
                >
                  <div class="tooltip our-tooltip" v-if="hoveredBenchmark === 'our'">
                    <div class="tooltip-title">Оцениваемая облигация</div>
                    <div class="tooltip-value">{{ indexYields.our.toFixed(2) }}%</div>
                  </div>
                </div>
              </div>

              <div class="yield-grid"></div>
            </div>
          </div>
          <div class="index-legend">
            <div class="legend-item">
              <div class="legend-circle gray"></div>
              <span>Индексные бенчмарки MOEX</span>
            </div>
            <div class="legend-item">
              <div class="legend-circle red"></div>
              <span>Оцениваемая облигация</span>
            </div>
          </div>
        </div>
      </div>

      <!-- BLOCK 6: Analogs & Indices (2 cols) -->
      <div class="grid-2">
        <!-- Analogs -->
        <div class="glass-card full-width">
          <h3>Сравнение с аналогами</h3>
          <div class="analog-inputs">
            <div v-for="(isin, idx) in analogsIsins" :key="idx" class="analog-item">
              <label>Аналог {{ idx + 1 }}</label>
              <div class="input-group">
                <input v-model="analogsIsins[idx]" type="text" placeholder="RU000B100001" @keyup.enter="loadAnalogs" />
                <button v-if="analogsIsins[idx]" @click="removeAnalog(idx)" class="remove-btn">×</button>
              </div>
            </div>
          </div>
          <div class="actions">
            <button class="btn-secondary" @click="addAnalogInput" v-if="analogsIsins.length < 5">+ Добавить</button>
            <button class="btn-primary" @click="loadAnalogs" :disabled="!hasFilledAnalogs">Загрузить</button>
          </div>
          <div v-if="analogsData.length" class="analogs-visualization">
            <div class="axes-labels">
              <div class="y-axis-label">Доходность, %</div>
            </div>
            <div class="chart-grid">
              <!-- Y-axis -->
              <div class="y-axis">
                <span v-for="(tick, i) in yAxisTicks" :key="'y-' + i" class="tick">{{ tick }}%</span>
              </div>
              <!-- Chart area -->
              <div class="chart-area">
                <!-- Grid lines -->
                <div class="grid-lines">
                  <div v-for="(_, i) in yAxisTicks" :key="'grid-' + i" class="grid-line"></div>
                </div>
                <!-- Our bond point -->
                <div 
                  class="analog-point our-bond-analog"
                  :style="{ 
                    left: getAnalogXPosition(ourBondDuration),
                    bottom: getAnalogYPosition(ourBondYTM),
                    zIndex: hoveredAnalog === 'our' ? 20 : 10
                  }"
                  @mouseenter="hoveredAnalog = 'our'"
                  @mouseleave="hoveredAnalog = null"
                >
                  <div class="point-dot">
                    <div class="tooltip analog-tooltip" v-if="hoveredAnalog === 'our'">
                      <div class="tooltip-title">Оцениваемая облигация</div>
                      <div class="tooltip-detail">Дюрация: {{ ourBondDuration.toFixed(2) }} лет</div>
                      <div class="tooltip-detail">Доходность: {{ ourBondYTM.toFixed(2) }}%</div>
                    </div>
                  </div>
                </div>
                <!-- Analog points -->
                <div 
                  v-for="(analog, idx) in analogsData"
                  :key="idx"
                  class="analog-point"
                  :style="{ 
                    left: getAnalogXPosition(analog.duration),
                    bottom: getAnalogYPosition(analog.ytm),
                    zIndex: hoveredAnalog === idx ? 20 : 5
                  }"
                  @mouseenter="hoveredAnalog = idx"
                  @mouseleave="hoveredAnalog = null"
                >
                  <div class="point-dot" :class="{ highlight: hoveredAnalog === idx }">
                    <div class="tooltip analog-tooltip" v-if="hoveredAnalog === idx">
                      <div class="tooltip-title">{{ analog.issuer }}</div>
                      <div class="tooltip-detail">Рейтинг: {{ analog.rating }}</div>
                      <div class="tooltip-detail">Дюрация: {{ analog.duration.toFixed(2) }} лет</div>
                      <div class="tooltip-detail">YTM: {{ analog.ytm.toFixed(2) }}%</div>
                      <div class="tooltip-detail">G-spread: {{ analog.gspread }} б.п.</div>
                    </div>
                  </div>
                </div>
              </div>
              <!-- X-axis -->
              <div class="x-axis">
                <span v-for="(tick, i) in xAxisTicks" :key="'x-' + i" class="tick">{{ tick.toFixed(2) }}</span>
              </div>
            </div>
            <div class="x-axis-label">Дюрация, лет</div>
            <div class="chart-legend">
              <div class="legend-item">
                <div class="legend-dot analog"></div>
                <span>Аналоги</span>
              </div>
              <div class="legend-item">
                <div class="legend-dot our"></div>
                <span>Оцениваемая облигация</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            Загрузите аналоги для сравнения
          </div>
        </div>
      </div>

    </section>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Chart from 'chart.js/auto'

// TYPES
interface RatingEntry {
  agency: string
  rating: string
  outlook?: string | null
  date?: string | null
}

interface BondReport {
  isin: string
  issuer: string
  risk_country?: string | null
  sector?: string | null
  industry?: string | null
  outstanding_amount?: number | null
  issue_info?: {
    issue_date?: string | null
    maturity_date?: string | null
    coupon_rate?: number | null
    coupon_per_year?: number | null
  }
  analysis_period?: {
    from?: string | null
    to?: string | null
  }
  market_activity?: {
    trading_days?: number | null
    trades?: number | null
    turnover_to_outstanding?: number | null
    traded_last_30d?: boolean
    source?: string | null
  }
  pricing?: {
    clean_price_pct?: number | null
    ytm?: number | null
    g_spread_bps?: number | null
    g_curve_yield?: number | null
  }
  risk_indicators?: {
    duration?: number | null
    convexity?: number | null
    dv01?: number | null
    other?: string | null
  }
  ratings?: {
    issue?: RatingEntry[]
    issuer?: RatingEntry[]
    guarantor?: RatingEntry[]
  }
  warnings?: string[]
}

interface AnalogData {
  issuer: string
  isin: string
  rating: string
  coupon: number
  ytm: number
  gspread: number
  duration: number
  dv01: number
}

// STATE
const route = useRoute()
const router = useRouter()

const isin = computed(() => (route.params.isin as string) || '')
const localIsin = ref(isin.value)

const loading = ref(false)
const error = ref<string | null>(null)
const report = ref<BondReport | null>(null)

const analogsIsins = ref<string[]>(['', '', ''])
const analogsData = ref<AnalogData[]>([])

// Index yields data
const indexYields = ref({
  gov: 13.89,
  aaa: 15.69,
  aa: 16.89,
  a: 20.54,
  bbb: 22.68,
  our: 19.91  // Оцениваемая облигация
})

const priceHistoryRef = ref<HTMLCanvasElement | null>(null)
const yieldDynamicsRef = ref<HTMLCanvasElement | null>(null)
const analogsScatterRef = ref<HTMLCanvasElement | null>(null)
const indicesPositionRef = ref<HTMLCanvasElement | null>(null)
const indexComparisonRef = ref<HTMLCanvasElement | null>(null)

let priceHistoryChart: Chart | null = null
let yieldDynamicsChart: Chart | null = null
let analogsScatterChart: Chart | null = null
let indicesPositionChart: Chart | null = null
let indexComparisonChart: Chart | null = null

const hasFilledAnalogs = computed(() => analogsIsins.value.some(i => i.trim().length > 0))

// CHART CONFIG
const tooltipConfig = {
  backgroundColor: 'rgba(15, 23, 42, 0.95)',
  titleColor: '#f1f5f9',
  bodyColor: '#cbd5e1',
  borderColor: '#f1f5f9',
  borderWidth: 1.5,
  cornerRadius: 6,
  titleFont: { weight: 'bold', size: 12 },
  bodyFont: { size: 11, weight: '500' },
  padding: 10,
  displayColors: false
}

const createPriceChartConfig = () => ({
  type: 'line' as const,
  data: {
    labels: ['01.12.2024', '01.01.2025', '01.02.2025', '01.03.2025', '01.04.2025', '01.05.2025', '01.06.2025', '01.07.2025', '01.08.2025', '01.09.2025', '01.10.2025', '01.11.2025', '01.12.2025'],
    datasets: [{
      label: 'Чистая цена',
      data: [74.2, 79.5, 81.3, 82.8, 84.0, 85.2, 86.8, 88.5, 89.2, 91.5, 93.2, 93.8, 93.95],
      borderColor: '#f1f5f9',
      backgroundColor: 'transparent',
      tension: 0.5,
      fill: false,
      pointRadius: 0,
      pointHoverRadius: 0,
      borderWidth: 2.5,
      hitRadius: 30,
      clip: false
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    devicePixelRatio: window.devicePixelRatio || 1,
    interaction: { mode: 'index' as const, intersect: false },
    elements: { line: { borderCapStyle: 'round', borderJoinStyle: 'round' } },
    plugins: {
      legend: { display: false },
      tooltip: tooltipConfig
    },
    scales: {
      y: {
        min: 70, max: 100,
        ticks: { color: '#6b7280', font: { size: 10 }, callback: (v: any) => v.toFixed(0) },
        grid: { color: 'rgba(107, 114, 128, 0.1)', drawBorder: false }
      },
      x: {
        ticks: { color: '#6b7280', font: { size: 10 } },
        grid: { color: 'rgba(107, 114, 128, 0.08)', drawBorder: false }
      }
    }
  }
})

const createYieldChartConfig = () => ({
  type: 'line' as const,
  data: {
    labels: ['01.12.2024', '01.01.2025', '01.02.2025', '01.03.2025', '01.04.2025', '01.05.2025', '01.06.2025', '01.07.2025', '01.08.2025', '01.09.2025', '01.10.2025', '01.11.2025', '01.12.2025'],
    datasets: [
      {
        label: 'YTM (%)',
        data: [30.2, 28.8, 27.5, 26.8, 25.5, 24.2, 22.8, 21.5, 20.2, 19.8, 19.2, 19.1, 18.95],
        borderColor: '#38bdf8',
        backgroundColor: 'transparent',
        tension: 0.5,
        fill: false,
        pointRadius: 4,
        pointBackgroundColor: '#38bdf8',
        pointBorderColor: '#0f172a',
        pointBorderWidth: 2,
        borderWidth: 2.5,
        yAxisID: 'y',
        hitRadius: 12
      },
      {
        label: 'G-curve (%)',
        data: [22.0, 20.8, 19.5, 18.8, 17.5, 16.2, 14.8, 13.5, 12.2, 11.8, 11.2, 11.1, 10.95],
        borderColor: '#f97316',
        backgroundColor: 'transparent',
        tension: 0.5,
        fill: false,
        pointRadius: 4,
        pointBackgroundColor: '#f97316',
        pointBorderColor: '#0f172a',
        pointBorderWidth: 2,
        borderWidth: 2.5,
        yAxisID: 'y',
        hitRadius: 12
      },
      {
        label: 'G-spread (б.п.)',
        data: [800, 750, 700, 650, 600, 550, 500, 450, 400, 380, 360, 340, 320],
        borderColor: '#9ca3af',
        backgroundColor: 'transparent',
        tension: 0.5,
        fill: false,
        pointRadius: 4,
        pointBackgroundColor: '#9ca3af',
        pointBorderColor: '#0f172a',
        pointBorderWidth: 2,
        borderWidth: 2.5,
        yAxisID: 'y1',
        hitRadius: 12
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    devicePixelRatio: window.devicePixelRatio || 1,
    interaction: { mode: 'index' as const, intersect: false },
    elements: { line: { borderCapStyle: 'round', borderJoinStyle: 'round' } },
    plugins: {
      legend: { display: false },
      tooltip: {
        ...tooltipConfig,
        callbacks: {
          title: (c: any) => c[0].label,
          label: (c: any) => {
            const val = c.dataset.yAxisID === 'y1' ? c.parsed.y.toFixed(0) : c.parsed.y.toFixed(2)
            return `${c.dataset.label}: ${val}`
          }
        }
      }
    },
    scales: {
      y: {
        display: true,
        position: 'left' as const,
        min: 10, max: 35,
        ticks: { color: '#6b7280', font: { size: 10 }, callback: (v: any) => v.toFixed(0) + '%' },
        grid: { color: 'rgba(107, 114, 128, 0.1)', drawBorder: false },
        title: { display: true, text: 'Доходность (%)', color: '#6b7280', font: { size: 10, weight: 'bold' } }
      },
      y1: {
        display: true,
        position: 'right' as const,
        min: 200, max: 1000,
        ticks: { color: '#6b7280', font: { size: 10 }, callback: (v: any) => v.toFixed(0) + ' б.п.' },
        grid: { display: false },
        title: { display: true, text: 'G-spread (б.п.)', color: '#6b7280', font: { size: 10, weight: 'bold' } }
      },
      x: {
        ticks: { color: '#6b7280', font: { size: 10 } },
        grid: { color: 'rgba(107, 114, 128, 0.08)', drawBorder: false }
      }
    }
  }
})

const createScatterChartConfig = () => ({
  type: 'scatter' as const,
  data: {
    datasets: [{
      label: 'Выпуски',
      data: [
        { x: 0.52, y: 18.5, label: 'Аналог А' },
        { x: 0.75, y: 20.5, label: 'Аналог Б' },
        { x: 1.10, y: 21.2, label: 'Аналог В' },
        ...analogsData.value.map(a => ({ x: a.duration, y: a.ytm, label: a.issuer }))
      ],
      backgroundColor: '#38bdf8',
      pointRadius: 7,
      pointHoverRadius: 9,
      borderWidth: 0
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    devicePixelRatio: window.devicePixelRatio || 1,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: (c: any) => `${c.raw.label}: ${c.raw.y.toFixed(2)}% / ${c.raw.x.toFixed(2)}г` } }
    },
    scales: {
      x: {
        title: { display: true, text: 'Дюрация, лет', color: '#64748b', font: { size: 11 } },
        grid: { color: 'rgba(51, 65, 85, 0.2)' },
        ticks: { color: '#94a3b8', font: { size: 10 } }
      },
      y: {
        title: { display: true, text: 'YTM, %', color: '#64748b', font: { size: 11 } },
        grid: { color: 'rgba(51, 65, 85, 0.2)' },
        ticks: { color: '#94a3b8', font: { size: 10 } }
      }
    }
  }
})

const createIndicesChartConfig = () => ({
  type: 'scatter' as const,
  data: {
    datasets: [{
      data: [
        { x: 13.89, y: 0, label: 'Гос' },
        { x: 15.69, y: 0, label: 'AAA' },
        { x: 16.89, y: 0, label: 'AA' },
        { x: 20.54, y: 0, label: 'A' },
        { x: 22.68, y: 0, label: 'BBB' },
        { x: 19.91, y: 0, label: 'Наша бумага', isTarget: true }
      ],
      backgroundColor: (c: any) => c.raw?.isTarget ? '#ef4444' : '#64748b',
      pointRadius: 12,
      pointHoverRadius: 14,
      borderWidth: 0
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    devicePixelRatio: window.devicePixelRatio || 1,
    layout: { padding: { top: 35, bottom: 10, left: 20, right: 20 } },
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: (c: any) => `${c.raw.label}: ${c.raw.x.toFixed(2)}%` } }
    },
    scales: {
      x: {
        min: 12, max: 24,
        grid: { display: false },
        ticks: { color: '#cbd5e1', font: { size: 11, weight: 'bold' }, callback: (v: any) => v + '%', stepSize: 2 }
      },
      y: { display: false, min: -1, max: 1 }
    }
  }
})

// NEW: Index comparison chart config (horizontal scatter with background beam)
const createIndexComparisonChartConfig = () => ({
  type: 'scatter' as const,
  data: {
    datasets: [{
      label: 'Индексы и выпуск',
      data: [
        { x: indexYields.value.gov, y: 0, label: 'Гос облигации' },
        { x: 15.0, y: 0, label: 'Индекс корп. обл. AAA' },
        { x: 16.0, y: 0, label: 'Индекс корп. обл. AA' },
        { x: indexYields.value.a, y: 0, label: 'Индекс корп. обл. A' },
        { x: 22.68, y: 0, label: 'Индекс корп. обл. BBB' },
        { x: indexYields.value.our, y: 0, label: 'Оцениваемая облигация', isTarget: true }
      ],
      backgroundColor: (c: any) => c.raw?.isTarget ? '#ef4444' : '#78716c',
      pointRadius: 13,
      pointHoverRadius: 15,
      borderWidth: 0
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    devicePixelRatio: window.devicePixelRatio || 1,
    layout: { padding: { top: 40, bottom: 20, left: 30, right: 30 } },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        titleColor: '#f1f5f9',
        bodyColor: '#cbd5e1',
        borderColor: '#f1f5f9',
        borderWidth: 1.5,
        cornerRadius: 6,
        callbacks: {
          title: () => '',
          label: (c: any) => `${c.raw.label}: ${c.raw.x.toFixed(2)}%`
        }
      }
    },
    scales: {
      x: {
        min: 12, max: 25,
        ticks: {
          color: '#94a3b8',
          font: { size: 11, weight: '500' },
          callback: (v: any) => v.toFixed(1) + '%',
          stepSize: 1
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.15)',
          drawBorder: false
        }
      },
      y: {
        display: false,
        min: -1,
        max: 1
      }
    }
  }
})

// Функция для расчёта позиции на шкале
const getBenchmarkPosition = (yield_value: number) => {
  const min = 12
  const max = 24
  const percent = ((yield_value - min) / (max - min)) * 100
  return Math.max(0, Math.min(100, percent)) + '%'
}

// Проверка, совпадает ли позиция с нашей облигацией
const isOurBondAtYield = (yield_value: number) => {
  return Math.abs(yield_value - indexYields.value.our) < 0.5
}

const hoveredBenchmark = ref<string | null>(null)

// CHART INIT
const initCharts = () => {
  destroyCharts()

  if (priceHistoryRef.value?.getContext('2d')) {
    priceHistoryChart = new Chart(priceHistoryRef.value.getContext('2d') as any, createPriceChartConfig() as any)
  }
  if (yieldDynamicsRef.value?.getContext('2d')) {
    yieldDynamicsChart = new Chart(yieldDynamicsRef.value.getContext('2d') as any, createYieldChartConfig() as any)
  }
  if (analogsScatterRef.value?.getContext('2d') && analogsData.value.length > 0) {
    analogsScatterChart = new Chart(analogsScatterRef.value.getContext('2d') as any, createScatterChartConfig() as any)
  }
  if (indicesPositionRef.value?.getContext('2d')) {
    indicesPositionChart = new Chart(indicesPositionRef.value.getContext('2d') as any, createIndicesChartConfig() as any)
  }
  if (indexComparisonRef.value?.getContext('2d')) {
    indexComparisonChart = new Chart(indexComparisonRef.value.getContext('2d') as any, createIndexComparisonChartConfig() as any)
  }
}

const destroyCharts = () => {
  [priceHistoryChart, yieldDynamicsChart, analogsScatterChart, indicesPositionChart, indexComparisonChart].forEach(c => c?.destroy())
  priceHistoryChart = yieldDynamicsChart = analogsScatterChart = indicesPositionChart = indexComparisonChart = null
}

const exportChart = (name: 'price' | 'yield' | 'indices') => {
  let canvas: HTMLCanvasElement | null = null
  if (name === 'price') canvas = priceHistoryRef.value
  else if (name === 'yield') canvas = yieldDynamicsRef.value
  else if (name === 'indices') canvas = indexComparisonRef.value
  
  if (!canvas) return
  const link = document.createElement('a')
  link.href = canvas.toDataURL('image/png', 1.0)
  link.download = `bond-${name}-${new Date().toISOString().split('T')[0]}.png`
  link.click()
}

// METHODS
const fetchReport = async (targetIsin: string) => {
  if (!targetIsin) return
  loading.value = true
  error.value = null
  report.value = null

  try {
    await new Promise(r => setTimeout(r, 600))
    
    report.value = {
      isin: targetIsin,
      issuer: 'ПАО "Аэрофлот - российские авиалинии"',
      risk_country: 'Россия',
      sector: 'Корпоративный',
      industry: 'Авиаперевозки',
      outstanding_amount: 24500000000,
      issue_info: {
        issue_date: '2023-05-15',
        maturity_date: '2026-05-15',
        coupon_rate: 0.095,
        coupon_per_year: 4
      },
      market_activity: {
        trading_days: 5,
        trades: 12,
        turnover_to_outstanding: 0.0015,
        traded_last_30d: true,
        source: 'Московская Биржа'
      },
      pricing: {
        clean_price_pct: 93.95,
        ytm: 0.19,
        g_spread_bps: 145,
        g_curve_yield: 0.138
      },
      risk_indicators: {
        duration: 0.52,           // Модифицированная дюрация (лет)
        convexity: 0.71,          // Выпуклость
        dv01: 52,             // DV01
      },
      ratings: {
        issue: [{ agency: 'Expert RA', rating: 'ruAA', date: '2025-10-31' }],
        issuer: [
          { agency: 'Expert RA', rating: 'ruAA', outlook: 'Стабильный', date: '2025-10-27' },
          { agency: 'AKRA', rating: 'AA(RU)', outlook: 'Стабильный', date: '2025-06-23' }
        ],
        guarantor: []
      },
      warnings: []
    }
    setTimeout(() => initCharts(), 100)
  } catch (e: any) {
    error.value = 'Ошибка загрузки данных'
  } finally {
    loading.value = false
  }
}

const loadAnalogs = async () => {
  // Mock данные — заглушка для демонстрации
  const mockAnalogs: AnalogData[] = [
    { 
      issuer: 'Компания А (Авиа)', 
      isin: 'RU000B100001', 
      rating: 'ruAA', 
      coupon: 9.75, 
      ytm: 18.55, 
      gspread: 135, 
      duration: 0.65, 
      dv01: 148000 
    },
    { 
      issuer: 'Компания B (Авиа)', 
      isin: 'RU000C200002', 
      rating: 'ruA', 
      coupon: 10.50, 
      ytm: 19.80, 
      gspread: 185, 
      duration: 1.15, 
      dv01: 162000 
    },
    { 
      issuer: 'Компания C (Финансы)', 
      isin: 'RU000D300003', 
      rating: 'ruAAA', 
      coupon: 8.50, 
      ytm: 17.20, 
      gspread: 125, 
      duration: 0.55, 
      dv01: 140000 
    }
  ]
  
  // Фильтруем по заполненным полям ввода
  analogsData.value = mockAnalogs.filter(
    (_, idx) => analogsIsins.value[idx]?.trim().length > 0
  )
}

// ============================================
// COMPUTED & REF для интерактивного графика
// ============================================

const hoveredAnalog = ref<number | string | null>(null)

// Наша облигация (данные)
const ourBondDuration = computed(() => {
  if (!report.value?.issue_info?.maturity_date || !report.value?.issue_info?.issue_date) {
    return 1.0
  }
  const issueDate = new Date(report.value.issue_info.issue_date)
  const maturityDate = new Date(report.value.issue_info.maturity_date)
  const daysToMaturity = (maturityDate.getTime() - issueDate.getTime()) / (1000 * 60 * 60 * 24)
  return daysToMaturity / 365
})

const ourBondYTM = computed(() => {
  return (report.value?.pricing?.ytm ?? 0.19) * 100
})

// Оси графика
const yAxisTicks = [14, 16, 18, 20, 22]

const xAxisTicks = computed(() => {
  const min = 0
  const max = 1.8
  return [min, 0.45, 0.9, 1.35, max]
})

// ============================================
// ФУНКЦИИ для расчёта позиций на графике
// ============================================

const getAnalogXPosition = (duration: number): string => {
  const min = 0
  const max = 1.8
  const percent = ((duration - min) / (max - min)) * 100
  return Math.max(0, Math.min(100, percent)) + '%'
}

const getAnalogYPosition = (ytm: number): string => {
  const min = yAxisTicks[0]
  const max = yAxisTicks[yAxisTicks.length - 1]
  const percent = ((ytm - min) / (max - min)) * 100
  return Math.max(0, Math.min(100, percent)) + '%'
}

// ============================================
// СУЩЕСТВУЮЩИЕ ФУНКЦИИ (без изменений)
// ============================================

const onChangeIsin = () => {
  const val = localIsin.value?.trim()
  if (!val) return
  destroyCharts()
  router.push({ name: 'BondReport', params: { isin: val } })
  fetchReport(val)
}

const addAnalogInput = () => {
  if (analogsIsins.value.length < 5) analogsIsins.value.push('')
}

const removeAnalog = (idx: number) => {
  analogsIsins.value.splice(idx, 1)
}

const formatDate = (val?: string | null): string => {
  if (!val) return '—'
  const d = new Date(val)
  return isNaN(d.getTime()) ? val : d.toLocaleDateString('ru-RU')
}

const formatNumber = (val?: number | null): string => {
  if (val === null || val === undefined) return '—'
  return new Intl.NumberFormat('ru-RU').format(val)
}

const isMarketActive = computed(() => {
  if (!report.value?.market_activity) return false
  const td = report.value.market_activity.trading_days ?? 0
  const tr = report.value.market_activity.trades ?? 0
  const lq = report.value.market_activity.traded_last_30d ?? false
  return td > 0 && tr > 5 && lq
})

onMounted(() => {
  if (isin.value) {
    fetchReport(isin.value)
  } else {
    localIsin.value = 'RU000A103943'
    fetchReport('RU000A103943')
  }
})

onBeforeUnmount(() => {
  destroyCharts()
})
</script>

<style scoped>
* { box-sizing: border-box; }

.page-container {
  padding: 24px 32px;
  max-width: 1600px;
  margin: 0 auto;
  background: linear-gradient(135deg, #0f172a 0%, #1a2332 100%);
  min-height: 100vh;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  gap: 20px;
}

.header-left {
  flex: 1;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  background: linear-gradient(90deg, #fff, #cbd5e1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.section-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin: 4px 0 0 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.glass-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  min-width: 300px;
}

.lbl-mini {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 600;
  text-transform: uppercase;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 13px;
  outline: none;
  padding: 4px;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

.btn-search {
  background: transparent;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: 14px;
  transition: color 0.2s;
}

.btn-search:hover:not(:disabled) {
  color: #60a5fa;
}

.btn-search:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* STATES */
.state-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.glass-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.4);
  color: rgba(255, 255, 255, 0.9);
}

.glass-card.error {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
  border-color: rgba(239, 68, 68, 0.2);
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(56, 189, 248, 0.3);
  border-top-color: #38bdf8;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* REPORT CONTENT */
.report-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.full-width {
  grid-column: 1 / -1;
}

.chart-card h3 {
  margin: 0 0 12px 0;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.9);
}

.chart-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.btn-export {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.2s;
}

.btn-export:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
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
  image-rendering: crisp-edges;
}

/* INDEX COMPARISON BLOCK */
.index-comparison-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.index-comparison-header h3 {
  margin: 0 0 4px 0;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.9);
}

.index-subtitle {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0;
}

.index-comparison-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.index-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 12px;
  background: rgba(15, 23, 42, 0.3);
  border-radius: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 600;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #38bdf8;
  font-family: 'SF Mono', monospace;
}

.index-chart-container {
  position: relative;
  width: 100%;
  height: 180px;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(107, 114, 128, 0.08);
}

.index-chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

.index-legend {
  display: flex;
  gap: 24px;
  justify-content: center;
  padding: 8px 0;
  font-size: 11px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.6);
}

.legend-circle {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-circle.gray {
  background-color: #78716c;
}

.legend-circle.red {
  background-color: #ef4444;
}

/* GRIDS */
.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.glass-card h3 {
  margin: 0 0 16px 0;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 0.05em;
}

/* INFO TABLES */
.info-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.info-table tr {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.info-table tr:last-child {
  border-bottom: none;
}

.info-table td {
  padding: 8px 0;
  color: rgba(255, 255, 255, 0.9);
}

.info-table td:first-child {
  color: rgba(255, 255, 255, 0.5);
  width: 40%;
}

.info-table td:last-child {
  text-align: right;
  font-weight: 500;
}

/* METRIC LISTS */
.metric-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  padding-bottom: 6px;
  border-bottom: 1px dashed rgba(107, 114, 128, 0.1);
}

.metric:last-child {
  border-bottom: none;
}

.metric > span:first-child {
  color: rgba(255, 255, 255, 0.5);
}

.metric .val {
  color: #fff;
  font-weight: 500;
  text-align: right;
}

.accent {
  color: #38bdf8;
  font-weight: 600;
}

.mono {
  font-family: 'SF Mono', monospace;
  letter-spacing: -0.01em;
}

.badge {
  display: inline-block;
  font-size: 10px;
  padding: 3px 7px;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
  background: rgba(107, 114, 128, 0.15);
  color: rgba(255, 255, 255, 0.7);
}

.badge.ok {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
}

.badge.bad {
  background: rgba(244, 63, 94, 0.15);
  color: #fb7185;
}

/* WARNINGS */
.warnings {
  margin-top: 12px;
  background: rgba(234, 179, 8, 0.08);
  border: 1px solid rgba(234, 179, 8, 0.15);
  border-radius: 8px;
  padding: 8px;
}

.warning {
  font-size: 11px;
  color: #fbbf24;
  margin-bottom: 4px;
}

.success {
  margin-top: 12px;
  font-size: 11px;
  color: #34d399;
}

/* ANALOGS */
.analogs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.analog-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.analog-item label {
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
}

.input-group {
  display: flex;
  gap: 4px;
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid rgba(107, 114, 128, 0.2);
  border-radius: 6px;
  overflow: hidden;
}

.input-group input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 6px 8px;
  color: #f1f5f9;
  font-family: 'SF Mono', monospace;
  font-size: 11px;
  outline: none;
}

.input-group input::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

.remove-btn {
  background: transparent;
  border: none;
  color: #ef4444;
  cursor: pointer;
  font-size: 14px;
  padding: 0 4px;
  transition: color 0.2s;
}

.remove-btn:hover {
  color: #fb7185;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-primary, .btn-secondary {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid;
}

.btn-secondary {
  background: rgba(107, 114, 128, 0.1);
  border-color: rgba(107, 114, 128, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

.btn-secondary:hover {
  background: rgba(107, 114, 128, 0.15);
  border-color: rgba(107, 114, 128, 0.3);
}

.btn-primary {
  background: rgba(56, 189, 248, 0.15);
  border-color: rgba(56, 189, 248, 0.3);
  color: #38bdf8;
}

.btn-primary:hover:not(:disabled) {
  background: rgba(56, 189, 248, 0.25);
  border-color: rgba(56, 189, 248, 0.5);
}

.btn-primary:disabled {
  background: rgba(107, 114, 128, 0.1);
  border-color: rgba(107, 114, 128, 0.15);
  color: rgba(107, 114, 128, 0.6);
  cursor: not-allowed;
}

/* RATINGS */
.ratings-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.rating-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  background: rgba(107, 114, 128, 0.05);
  padding: 8px;
  border-radius: 6px;
  gap: 8px;
}

.rating-item .agency {
  color: rgba(255, 255, 255, 0.5);
  font-size: 10px;
  font-weight: 600;
  min-width: 60px;
}

.tooltip {
  position: absolute;
  bottom: calc(100% + 16px);           /* Выплывает ВЫШЕ кружка */
  padding: 8px 12px;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 6px;
  animation: slideUp 0.2s;  /* Плавная анимация */
  z-index: 30;
}

.tooltip-title {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);  /* Серый текст */
}

.tooltip-value {
  font-size: 12px;
  color: #38bdf8;        /* Синий процент */
}

.rating-item .grade {
  font-weight: 700;
  color: #f1f5f9;
}

.rating-item .outlook {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.4);
}

.rating-item .date {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  white-space: nowrap;
}

.muted {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0;
}

.text-accent {
  color: #3b82f6;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.metric-header h3 {
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.9);
}

.activity-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  border: 1px solid;
}

.activity-indicator.active {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
  border-color: rgba(16, 185, 129, 0.3);
}

.activity-indicator.inactive {
  background: rgba(244, 63, 94, 0.12);
  color: #f43f5e;
  border-color: rgba(244, 63, 94, 0.3);
}

.indicator-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.activity-indicator.active .indicator-dot {
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
  animation: pulse-active 2s ease-in-out infinite;
}

.activity-indicator.inactive .indicator-dot {
  background: #f43f5e;
}

@keyframes pulse-active {
  0%, 100% { box-shadow: 0 0 8px rgba(16, 185, 129, 0.6); }
  50% { box-shadow: 0 0 12px rgba(16, 185, 129, 0.8); }
}

.badge-value {
  display: inline-block;
  min-width: 40px;
  text-align: right;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(56, 189, 248, 0.12);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.2);
  font-family: 'SF Mono', monospace;
}

.index-visualization {
  margin: 24px 0;
  padding: 20px;
  padding-top: 40px;
  background: rgba(15, 23, 42, 0.3);
  border-radius: 12px;
  border: 1px solid rgba(107, 114, 128, 0.08);
  overflow: visible;
}

.yield-scale {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: 10px;
  color: rgba(107, 114, 128, 0.8);
  font-weight: 600;
  padding: 0 10px;
}

.yield-bar {
  position: relative;
  height: 80px;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(107, 114, 128, 0.15);
  overflow: visible;
  padding-top: 80px;
}

.yield-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    linear-gradient(
      90deg,
      rgba(107, 114, 128, 0.1) 1px,
      transparent 1px
    );
  background-size: 14.28% 100%;
  pointer-events: none;
}

.benchmark {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.benchmark-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #78716c;
  box-shadow: 0 0 8px rgba(120, 113, 108, 0.4);
  transition: all 0.3s ease;
}

.benchmark-dot.highlight {
  background: #78716c;
  box-shadow: 0 0 0 4px rgba(120, 113, 108, 0.2);
}

.our-bond {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.our-bond-dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #ef4444;
  box-shadow: 
    0 0 12px rgba(239, 68, 68, 0.8),
    0 0 0 3px rgba(239, 68, 68, 0.2);
  animation: pulse-bond 2s ease-in-out infinite;
}

@keyframes pulse-bond {
  0%, 100% {
    box-shadow: 
      0 0 12px rgba(239, 68, 68, 0.8),
      0 0 0 3px rgba(239, 68, 68, 0.2);
  }
  50% {
    box-shadow: 
      0 0 16px rgba(239, 68, 68, 1),
      0 0 0 6px rgba(239, 68, 68, 0.3);
  }
}

.analog-inputs {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.analogs-visualization {
  margin-top: 20px;
  padding: 20px;
  background: rgba(15, 23, 42, 0.3);
  border-radius: 12px;
  border: 1px solid rgba(107, 114, 128, 0.08);
}

.axes-labels {
  position: relative;
  margin-bottom: 12px;
  margin-left: 0px;  /* ← Место для Y-axis лейбла */
}

.y-axis-label {
  position: absolute;
  left: 0px;
  top: 50%;
  transform: translateY(-50%) rotate(-90deg);
  transform-origin: center;
  font-size: 10px;
  color: rgba(107, 114, 128, 0.6);
  font-weight: 600;
  line-height: 20px;
  white-space: nowrap;
}

.chart-grid {
  display: grid;
  grid-template-columns: 50px 1fr;
  gap: 8px;
  height: 360px;  /* ← Увеличена высота */
  margin-bottom: 0px;
}

.y-axis {
  display: flex;
  min-width: 50px;
  flex-direction: column-reverse;
  justify-content: space-between;
  font-size: 10px;
  flex-shrink: 0;
  text-align: right;
  color: rgba(107, 114, 128, 0.6);
  font-weight: 600;
  padding: 0 8px;
}

.chart-area {
  position: relative;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(107, 114, 128, 0.15);
  border-radius: 8px;
  overflow: visible;
  padding: 0px;
  margin: 0;
}

.grid-lines {
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column-reverse;
  pointer-events: none;
}

.grid-line {
  flex: 1;
  border-bottom: 1px solid rgba(107, 114, 128, 0.1);
}

.analog-point {
  position: absolute;
  width: 20px;
  height: 20px;
  transform: translate(-50%, 50%);
  cursor: pointer;
  z-index: 10;
}

.point-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #64748b;
  box-shadow: 0 0 8px rgba(100, 116, 139, 0.4);
  transition: all 0.3s ease;
  position: relative;
}

.analog-point:hover .point-dot {
  width: 20px;
  height: 20px;
  box-shadow: 0 0 12px rgba(100, 116, 139, 0.6);
}

.point-dot.highlight {
  width: 20px;
  height: 20px;
  box-shadow: 0 0 12px rgba(100, 116, 139, 0.8);
}

.our-bond-analog .point-dot {
  background: #ef4444;
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.8), 0 0 0 3px rgba(239, 68, 68, 0.2);
  animation: pulse-analog 2s ease-in-out infinite;
}

.our-bond-analog:hover .point-dot {
  width: 24px;
  height: 24px;
  box-shadow: 0 0 16px rgba(239, 68, 68, 1), 0 0 0 5px rgba(239, 68, 68, 0.3);
}

@keyframes pulse-analog {
  0%, 100% {
    box-shadow: 0 0 12px rgba(239, 68, 68, 0.8), 0 0 0 3px rgba(239, 68, 68, 0.2);
  }
  50% {
    box-shadow: 0 0 16px rgba(239, 68, 68, 1), 0 0 0 5px rgba(239, 68, 68, 0.3);
  }
}

.x-axis {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: rgba(107, 114, 128, 0.6);
  font-weight: 600;
  padding: 4px 58px 0 58px;
  height: 20px;
  min-height: 20px;
  margin-bottom: 4px;
}

.x-axis-label {
  text-align: center;
  font-size: 10px;
  color: rgba(107, 114, 128, 0.6);
  font-weight: 600;
  margin-bottom: 12px;
}

.chart-legend {
  display: flex;
  gap: 24px;
  justify-content: center;
  font-size: 11px;
  margin-top: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.6);
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.analog {
  background: #64748b;
}

.legend-dot.our {
  background: #ef4444;
}

.analog-tooltip {
  position: absolute;
  bottom: 120%;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 12px;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 6px;
  white-space: nowrap;
  z-index: 30;
  pointer-events: none;
  animation: slideUp 0.2s ease-out;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
}

.our-bond-analog .analog-tooltip {
  border-color: rgba(239, 68, 68, 0.3);
}

.analog-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid rgba(56, 189, 248, 0.3);
}

.our-bond-analog .analog-tooltip::after {
  border-top-color: rgba(239, 68, 68, 0.3);
}

.tooltip-title {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 600;
  margin-bottom: 4px;
}

.tooltip-detail {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.6);
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 11px;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.index-legend {
  display: flex;
  gap: 24px;
  justify-content: center;
  padding: 12px 0;
  font-size: 11px;
  margin-top: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.6);
}

.legend-circle {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-circle.gray {
  background-color: #78716c;
}

.legend-circle.red {
  background-color: #ef4444;
}

.badge-source {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  background: rgba(148, 163, 184, 0.12);
  color: rgba(226, 232, 240, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.badge {
  display: inline-block;
  font-size: 10px;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 600;
  text-transform: uppercase;
  border: 1px solid rgba(107, 114, 128, 0.2);
}

.badge.ok {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge.bad {
  background: rgba(244, 63, 94, 0.15);
  color: #fb7185;
  border: 1px solid rgba(244, 63, 94, 0.2);
}

/* RESPONSIVE */
@media (max-width: 1200px) {
  .grid-3 { grid-template-columns: repeat(2, 1fr); }
  .index-stats { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .page-container { padding: 16px; }
  .section-header { flex-direction: column; }
  .glass-pill { min-width: auto; width: 100%; }
  .grid-2, .grid-3 { grid-template-columns: 1fr; }
  .chart-container { height: 280px; }
  .chart-container.tall { height: 360px; }
  .index-stats { grid-template-columns: 1fr; }
  .index-legend { flex-wrap: wrap; }
}
</style>