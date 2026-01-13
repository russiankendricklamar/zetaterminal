<!-- src/pages/VanillaBondReport.vue -->
<template>
  <div class="page-container">
    
    <!-- Header Section -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title" v-if="report">
          {{ report.issuer }}, {{ report.isin }}
        </h1>
        <h1 class="section-title" v-else>Vanilla Bond Report</h1>
        <p class="section-subtitle" v-if="report">
          Паспорт выпуска и аналитика по ISIN: <span class="text-accent">{{ report.isin }}</span>
        </p>
        <p class="section-subtitle" v-else>
          Паспорт выпуска и аналитика по ISIN: <span class="text-accent">{{ isin || '—' }}</span>
        </p>
      </div>
      
      <div class="header-actions">
        <!-- Valuation Date -->
        <div class="glass-pill">
          <label class="lbl-mini">Дата оценки:</label>
          <input 
            v-model="valuationDate"
            type="date"
            class="date-input-small"
            @change="onValuationDateChange"
          />
        </div>

        <!-- Edit Mode Toggle -->
        <button 
          @click="toggleEditMode" 
          class="btn-toggle-edit"
          :class="{ 'active': editMode }"
        >
          {{ editMode ? '✓ Режим редактирования' : '✎ Редактировать' }}
        </button>

        <!-- Export to Excel -->
        <button 
          @click="exportToExcel" 
          class="btn-export-excel"
          :disabled="!report"
        >
          📊 Excel
        </button>

        <!-- Search Control -->
        <div class="glass-pill">
          <label class="lbl-mini">ISIN:</label>
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

    <!-- States -->
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

    <!-- Report Content -->
    <section v-else class="report-content">
      
      <!-- General Info Section -->
      <div class="grid-2">
        <div class="glass-card">
          <div class="card-header">
            <h3>Общие сведения</h3>
          </div>
          <table class="info-table">
            <tr>
              <td class="label">Эмитент</td>
              <td class="value">
                <input v-if="editMode && editableReport" v-model="editableReport.issuer" type="text" class="edit-input" />
                <span v-else>{{ report.issuer }}</span>
              </td>
            </tr>
            <tr><td class="label">ISIN</td><td class="value mono">{{ report.isin }}</td></tr>
            <tr>
              <td class="label">Страна</td>
              <td class="value">
                <input v-if="editMode && editableReport" v-model="editableReport.risk_country" type="text" class="edit-input" />
                <span v-else>{{ report.risk_country || '—' }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Сектор</td>
              <td class="value">
                <input v-if="editMode && editableReport" v-model="editableReport.sector" type="text" class="edit-input" />
                <span v-else>{{ report.sector || '—' }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Отрасль</td>
              <td class="value">
                <input v-if="editMode && editableReport" v-model="editableReport.industry" type="text" class="edit-input" />
                <span v-else>{{ report.industry || '—' }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Объём</td>
              <td class="value mono">
                <input v-if="editMode && editableReport" v-model.number="editableReport.outstanding_amount" type="number" class="edit-input" />
                <span v-else>{{ formatNumber(report.outstanding_amount) || '—' }}</span>
              </td>
            </tr>
          </table>
        </div>

        <div class="glass-card">
          <div class="card-header">
            <h3>Параметры выпуска</h3>
          </div>
          <table class="info-table">
            <tr>
              <td class="label">Дата начала</td>
              <td class="value mono">
                <input v-if="editMode && editableReport?.issue_info" v-model="editableReport.issue_info.issue_date" type="date" class="edit-input" />
                <span v-else>{{ formatDate(report.issue_info?.issue_date) }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Дата погашения</td>
              <td class="value mono">
                <input v-if="editMode && editableReport?.issue_info" v-model="editableReport.issue_info.maturity_date" type="date" class="edit-input" />
                <span v-else>{{ formatDate(report.issue_info?.maturity_date) }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Ставка купона</td>
              <td class="value">
                <input v-if="editMode && editableReport?.issue_info" v-model.number="editableReport.issue_info.coupon_rate" type="number" step="0.01" class="edit-input" placeholder="0.00" />
                <span v-else>
                  <span v-if="report.issue_info?.coupon_rate !== null && report.issue_info?.coupon_rate !== undefined" class="accent">{{ ((report.issue_info?.coupon_rate || 0) * 100).toFixed(2) }}%</span>
                  <span v-else>—</span>
                </span>
              </td>
            </tr>
            <tr>
              <td class="label">Купонов в год</td>
              <td class="value mono">
                <input v-if="editMode && editableReport?.issue_info" v-model.number="editableReport.issue_info.coupon_per_year" type="number" class="edit-input" />
                <span v-else>{{ report.issue_info?.coupon_per_year ?? '—' }}</span>
              </td>
            </tr>
          </table>
        </div>
      </div>

      <!-- Ratings Section -->
      <div class="grid-3">
        <div class="glass-card">
          <div class="card-header">
            <h3>Рейтинг эмиссии</h3>
          </div>
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
          <div class="card-header">
            <h3>Рейтинг эмитента</h3>
          </div>
          <div v-if="report.ratings?.issuer?.length" class="ratings-list">
            <div v-for="(r, idx) in report.ratings.issuer" :key="idx" class="rating-item">
              <span class="agency">{{ r.agency }}</span>
              <div class="rating-info">
                <span class="grade">{{ r.rating }}</span>
                <span class="outlook" v-if="r.outlook">{{ r.outlook }}</span>
              </div>
              <span class="date mono">{{ formatDate(r.date) }}</span>
            </div>
          </div>
          <p v-else class="muted">Нет данных</p>
        </div>

        <div class="glass-card">
          <div class="card-header">
            <h3>Рейтинг гаранта</h3>
          </div>
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

      <!-- Market & Pricing Metrics -->
      <div class="grid-3">
        <div class="glass-card">
          <div class="card-header">
            <h3>Активность рынка</h3>
            <span class="status-badge fulfilled">АКТИВНЫЙ</span>
          </div>
          <div class="metric-list">
            <div class="metric"><span>Кол-во торговых дней</span><span class="val">{{ report.market_activity?.trading_days ?? '—' }}</span></div>
            <div class="metric"><span>Кол-во сделок</span><span class="val">{{ report.market_activity?.trades ?? '—' }}</span></div>
            <div class="metric"><span>Объем торгов/выпуск</span><span class="val">{{ report.market_activity?.turnover_to_outstanding ? ((report.market_activity.turnover_to_outstanding * 100).toFixed(2) + '%') : '—' }}</span></div>
            <div class="metric"><span>Торги 30 дней</span><span class="val"><span v-if="report.market_activity?.traded_last_30d" class="status-badge fulfilled">Да</span><span v-else>Нет</span></span></div>
          </div>
        </div>

        <div class="glass-card">
          <div class="card-header">
            <h3>Котировка и доходность</h3>
          </div>
          <div class="metric-list">
            <div class="metric">
              <span>Чистая цена</span>
              <span class="val accent">
                <input v-if="editMode && editableReport?.pricing" v-model.number="editableReport.pricing.clean_price_pct" type="number" step="0.01" class="edit-input-inline" />
                <span v-else>{{ report.pricing?.clean_price_pct?.toFixed(2) }}%</span>
              </span>
            </div>
            <div class="metric">
              <span>YTM</span>
              <span class="val accent">
                <input v-if="editMode && editableReport?.pricing" v-model.number="editableReport.pricing.ytm" type="number" step="0.0001" class="edit-input-inline" />
                <span v-else>{{ report.pricing?.ytm ? ((report.pricing.ytm * 100).toFixed(2) + '%') : '—' }}</span>
              </span>
            </div>
            <div class="metric">
              <span>G-spread</span>
              <span class="val mono">
                <input v-if="editMode && editableReport?.pricing" v-model.number="editableReport.pricing.g_spread_bps" type="number" class="edit-input-inline" />
                <span v-else>{{ report.pricing?.g_spread_bps ?? '—' }}<span v-if="report.pricing?.g_spread_bps"> bps</span></span>
              </span>
            </div>
            <div class="metric">
              <span>G-curve</span>
              <span class="val mono">
                <input v-if="editMode && editableReport?.pricing" v-model.number="editableReport.pricing.g_curve_yield" type="number" step="0.0001" class="edit-input-inline" />
                <span v-else>{{ report.pricing?.g_curve_yield ? ((report.pricing.g_curve_yield * 100).toFixed(2) + '%') : '—' }}</span>
              </span>
            </div>
          </div>
        </div>

        <div class="glass-card">
          <div class="card-header">
            <h3>Риск-метрики</h3>
          </div>
          <div class="metric-list">
            <div class="metric">
              <span>Мод. дюрация</span>
              <span class="val">
                <input v-if="editMode && editableReport?.risk_indicators" v-model.number="editableReport.risk_indicators.mod_duration" type="number" step="0.0001" class="edit-input-inline" />
                <span v-else>{{ report.risk_indicators?.mod_duration?.toFixed(4) || report.risk_indicators?.duration?.toFixed(4) || '—' }}</span>
              </span>
            </div>
            <div class="metric">
              <span>Дюрация</span>
              <span class="val">
                <input v-if="editMode && editableReport?.risk_indicators" v-model.number="editableReport.risk_indicators.duration" type="number" step="0.0001" class="edit-input-inline" />
                <span v-else>{{ report.risk_indicators?.duration?.toFixed(4) }}</span>
              </span>
            </div>
            <div class="metric">
              <span>Выпуклость</span>
              <span class="val">
                <input v-if="editMode && editableReport?.risk_indicators" v-model.number="editableReport.risk_indicators.convexity" type="number" step="0.01" class="edit-input-inline" />
                <span v-else>{{ report.risk_indicators?.convexity?.toFixed(2) }}</span>
              </span>
            </div>
            <div class="metric">
              <span>DV01</span>
              <span class="val">
                <input v-if="editMode && editableReport?.risk_indicators" v-model.number="editableReport.risk_indicators.dv01" type="number" step="0.01" class="edit-input-inline" />
                <span v-else>{{ formatNumber(report.risk_indicators?.dv01) }}</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- BLOCK 2: Price Chart -->
      <div class="glass-card full-width">
        <div class="chart-header">
          <h3>Динамика цены</h3>
          <button class="btn-export" @click="exportChart('price')">💾 PNG</button>
        </div>
        <div class="chart-container tall">
          <canvas ref="priceHistoryRef"></canvas>
        </div>
      </div>

      <!-- BLOCK 3: Yield Chart with G-curve and G-spread -->
      <div class="glass-card full-width">
        <div class="chart-header">
          <h3>Динамика доходности облигации в RUB, g-curve, g-spread</h3>
          <button class="btn-export" @click="exportChart('yield')">💾 PNG</button>
        </div>
        <div class="chart-container tall">
          <canvas ref="yieldDynamicsRef"></canvas>
        </div>
      </div>

      <!-- BLOCK 4: Comparison with Indices -->
      <div class="glass-card full-width">
        <div class="card-header">
          <h3>Сравнение с индексами корпоративных облигаций Московской биржи</h3>
        </div>
        <div class="comparison-section">
          <table class="comparison-table">
            <thead>
              <tr>
                <th>Индекс</th>
                <th>Доходность, %</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Доходность индекса государственных облигаций (менее года)</td>
                <td class="mono">{{ report.indices?.gov_less_1y?.toFixed(2) || '—' }}%</td>
              </tr>
              <tr>
                <td>Доходность индекса корпоративных облигаций с рейтингом ААА</td>
                <td class="mono">{{ report.indices?.corp_aaa?.toFixed(2) || '—' }}%</td>
              </tr>
              <tr>
                <td>Доходность индекса корпоративных облигаций с рейтингом АА</td>
                <td class="mono">{{ report.indices?.corp_aa?.toFixed(2) || '—' }}%</td>
              </tr>
              <tr class="highlight-row">
                <td><strong>Оцениваемая облигация</strong></td>
                <td class="mono accent"><strong>{{ report.pricing?.ytm ? ((report.pricing.ytm * 100).toFixed(2) + '%') : '—' }}</strong></td>
              </tr>
              <tr>
                <td>Доходность индекса корпоративных облигаций с рейтингом А</td>
                <td class="mono">{{ report.indices?.corp_a?.toFixed(2) || '—' }}%</td>
              </tr>
              <tr>
                <td>Доходность индекса корпоративных облигаций с рейтингом ВВВ</td>
                <td class="mono">{{ report.indices?.corp_bbb?.toFixed(2) || '—' }}%</td>
              </tr>
            </tbody>
          </table>
          <div class="chart-container indices-chart">
            <canvas ref="indicesComparisonRef"></canvas>
          </div>
        </div>
      </div>

      <!-- BLOCK 5: Comparison with Analogous Bonds -->
      <div class="glass-card full-width">
        <div class="card-header">
          <h3>Сравнение с облигациями-аналогами</h3>
        </div>
        
        <!-- Input Section for Analogous Bonds -->
        <div class="analogous-input-section">
          <div class="glass-pill">
            <label class="lbl-mini">ISIN аналога:</label>
            <input 
              v-model="newAnalogIsin"
              type="text"
              class="search-input"
              placeholder="RU000A10XXXX"
              @keyup.enter="addAnalogBond"
            />
            <button class="btn-search" @click="addAnalogBond" :disabled="!newAnalogIsin || loadingAnalogs">➕</button>
          </div>
          
          <!-- List of added analogs -->
          <div v-if="analogBondsList.length > 0" class="analogs-list">
            <div v-for="(bond, idx) in analogBondsList" :key="idx" class="analog-item">
              <span class="analog-isin mono">{{ bond.isin }}</span>
              <span class="analog-name">{{ bond.name || 'Загрузка...' }}</span>
              <button class="btn-remove" @click="removeAnalogBond(idx)" title="Удалить">×</button>
            </div>
          </div>
        </div>
        
        <div class="chart-container tall">
          <canvas ref="analogousBondsRef"></canvas>
        </div>
      </div>

      <!-- BLOCK 6: Corporate Events -->
      <div class="glass-card full-width">
        <div class="card-header">
          <h3>Корпоративные события</h3>
        </div>
        <div v-if="report.corporate_events?.length" class="events-list">
          <div v-for="(event, idx) in report.corporate_events" :key="idx" class="event-item">
            <span class="event-date mono">{{ formatDate(event.date) }}</span>
            <span class="event-description">{{ event.description }}</span>
          </div>
        </div>
        <p v-else class="muted">Нет данных о корпоративных событиях</p>
      </div>

    </section>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Chart from 'chart.js/auto'
import * as XLSX from 'xlsx'

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
  market_activity?: {
    trading_days?: number | null
    trades?: number | null
    turnover_to_outstanding?: number | null
    traded_last_30d?: boolean
  }
  pricing?: {
    clean_price_pct?: number | null
    ytm?: number | null
    g_spread_bps?: number | null
    g_curve_yield?: number | null
  }
  risk_indicators?: {
    duration?: number | null
    mod_duration?: number | null
    convexity?: number | null
    dv01?: number | null
  }
  ratings?: {
    issue?: RatingEntry[]
    issuer?: RatingEntry[]
    guarantor?: RatingEntry[]
  }
  indices?: {
    gov_less_1y?: number
    corp_aaa?: number
    corp_aa?: number
    corp_a?: number
    corp_bbb?: number
  }
  corporate_events?: {
    date?: string | null
    description: string
  }[]
  analogous_bonds?: {
    name: string
    duration: number
    yield: number
  }[]
}

const route = useRoute()
const router = useRouter()

const isin = computed(() => (route.params.isin as string) || '')
const localIsin = ref(isin.value)

const loading = ref(false)
const error = ref<string | null>(null)
const report = ref<BondReport | null>(null)
const valuationDate = ref(new Date().toISOString().split('T')[0])
const editMode = ref(false)
const editableReport = ref<BondReport | null>(null)

// Analogous bonds management
const newAnalogIsin = ref('')
const loadingAnalogs = ref(false)
const analogBondsList = ref<Array<{
  isin: string
  name?: string
  duration?: number
  yield?: number
}>>([])

const priceHistoryRef = ref<HTMLCanvasElement | null>(null)
const yieldDynamicsRef = ref<HTMLCanvasElement | null>(null)
const indicesComparisonRef = ref<HTMLCanvasElement | null>(null)
const analogousBondsRef = ref<HTMLCanvasElement | null>(null)

let priceHistoryChart: Chart | null = null
let yieldDynamicsChart: Chart | null = null
let indicesComparisonChart: Chart | null = null
let analogousBondsChart: Chart | null = null

const fetchReport = async (targetIsin: string) => {
  if (!targetIsin) return
  loading.value = true
  error.value = null
  report.value = null

  try {
    await new Promise(r => setTimeout(r, 600))
    
    report.value = {
      isin: targetIsin,
      issuer: 'Синара - Транспортные Машины, АО',
      risk_country: 'Россия',
      sector: 'Корпоративный',
      industry: 'Прочее машиностроение и приборостроение',
      outstanding_amount: 10000000000,
      issue_info: {
        issue_date: '2021-07-28',
        maturity_date: '2026-07-22',
        coupon_rate: 0.087,
        coupon_per_year: 2
      },
      market_activity: {
        trading_days: 20,
        trades: 3447,
        turnover_to_outstanding: 0.0092,
        traded_last_30d: true
      },
      pricing: {
        clean_price_pct: 93.95,
        ytm: 0.1991,
        g_spread_bps: 622.94,
        g_curve_yield: 0.1369
      },
      risk_indicators: {
        duration: 0.62,
        convexity: 0.71,
        dv01: 52
      },
      ratings: {
        issue: [{ agency: 'AKPA', rating: 'A(RU)', date: '2025-02-07' }],
        issuer: [
          { agency: 'AKPA', rating: 'a(ru)', outlook: 'Стабильный', date: '2025-02-07' },
          { agency: 'HKP', rating: 'a+.ru', outlook: 'Негативный', date: '2025-06-11' }
        ]
      },
      indices: {
        gov_less_1y: 0.1389,
        corp_aaa: 0.1569,
        corp_aa: 0.1689,
        corp_a: 0.2054,
        corp_bbb: 0.2268
      },
      corporate_events: [
        { date: '2025-08-21', description: 'НОВИКОМ и «Синара - Транспортные машины» подписали кредитное соглашение на 10 млрд рублей' },
        { date: '2025-07-11', description: '«Синара - Транспортные Машины» получает финансирование на создание производства трамваев' }
      ],
      analogous_bonds: []
    }
    setTimeout(() => initCharts(), 100)
  } catch (e) {
    error.value = 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

const initCharts = () => {
  if (priceHistoryChart) priceHistoryChart.destroy()
  if (yieldDynamicsChart) yieldDynamicsChart.destroy()
  if (indicesComparisonChart) indicesComparisonChart.destroy()
  if (analogousBondsChart) analogousBondsChart.destroy()

  if (priceHistoryRef.value?.getContext('2d')) {
    const months = ['Dec 2024', 'Jan 2025', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec 2025']
    const prices = [74, 75, 78, 82, 85, 87, 88, 89, 90, 91, 92, 93, 94]
    
    priceHistoryChart = new Chart(priceHistoryRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: months,
        datasets: [{
          label: 'Цена, %',
          data: prices,
          borderColor: '#60a5fa',
          backgroundColor: 'rgba(96, 165, 250, 0.08)',
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { 
          legend: { display: false },
          filler: { propagate: true }
        },
        scales: {
          x: { 
            grid: { display: false }, 
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } } 
          },
          y: { 
            grid: { color: 'rgba(255,255,255,0.05)' }, 
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } },
            title: {
              display: true,
              text: 'Цена, %',
              color: 'rgba(255,255,255,0.5)',
              font: { size: 11 }
            }
          }
        }
      }
    } as any)
  }

  if (yieldDynamicsRef.value?.getContext('2d')) {
    const months = ['Dec 2024', 'Jan 2025', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec 2025']
    const ytm = [28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18.5, 19, 19.91]
    const gcurve = [20, 19.5, 19, 18, 17, 16, 15.5, 15, 14.5, 14, 13.8, 13.7, 13.69]
    const gspread = [800, 750, 700, 650, 600, 550, 500, 450, 400, 420, 600, 620, 622.94]
    
    yieldDynamicsChart = new Chart(yieldDynamicsRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: months,
        datasets: [
          {
            label: 'YTM',
            data: ytm,
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.08)',
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            borderWidth: 2,
            yAxisID: 'y'
          },
          {
            label: 'g-curve',
            data: gcurve,
            borderColor: '#f59e0b',
            backgroundColor: 'transparent',
            fill: false,
            tension: 0.4,
            pointRadius: 0,
            borderWidth: 2,
            borderDash: [5, 5],
            yAxisID: 'y'
          },
          {
            label: 'g-spread',
            data: gspread,
            borderColor: '#9ca3af',
            backgroundColor: 'transparent',
            fill: false,
            tension: 0.4,
            pointRadius: 0,
            borderWidth: 2,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: { 
          legend: { 
            display: true,
            labels: {
              color: 'rgba(255,255,255,0.6)',
              font: { size: 11 },
              usePointStyle: true
            },
            position: 'top'
          }
        },
        scales: {
          y: { 
            type: 'linear',
            position: 'left',
            grid: { color: 'rgba(255,255,255,0.05)' }, 
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } },
            title: {
              display: true,
              text: 'Доходность, %',
              color: 'rgba(255,255,255,0.5)',
              font: { size: 11 }
            }
          },
          y1: {
            type: 'linear',
            position: 'right',
            grid: { display: false },
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } } 
          },
          x: { 
            grid: { display: false }, 
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } } 
          }
        }
      }
    } as any)
  }

  // Indices Comparison Chart - Timeline style with points
  if (indicesComparisonRef.value?.getContext('2d') && report.value?.indices && report.value?.pricing) {
    const indices = report.value.indices
    const bondYtm = (report.value.pricing.ytm || 0) * 100
    
    const dataPoints = [
      { label: 'Индекс гос. облигаций', value: (indices.gov_less_1y || 0) * 100, color: '#9ca3af' },
      { label: 'Индекс корп. облигаций (ААА)', value: (indices.corp_aaa || 0) * 100, color: '#9ca3af' },
      { label: 'Индекс корп. облигаций (АА)', value: (indices.corp_aa || 0) * 100, color: '#9ca3af' },
      { label: 'Оцениваемая облигация', value: bondYtm, color: '#ef4444' },
      { label: 'Индекс корп. облигаций (А)', value: (indices.corp_a || 0) * 100, color: '#9ca3af' },
      { label: 'Индекс корп. облигаций (ВВВ)', value: (indices.corp_bbb || 0) * 100, color: '#9ca3af' }
    ]
    
    indicesComparisonChart = new Chart(indicesComparisonRef.value.getContext('2d') as any, {
      type: 'scatter',
      data: {
        datasets: dataPoints.map((point, index) => ({
          label: point.label,
          data: [{ x: point.value, y: 0 }],
          backgroundColor: index === 3 ? 'rgba(239, 68, 68, 0)' : point.color, // Transparent for red point, will be drawn by plugin
          borderColor: index === 3 ? 'rgba(239, 68, 68, 0)' : point.color,
          pointRadius: index === 3 ? 1 : 10, // Small invisible radius for hover detection
          pointHoverRadius: index === 3 ? 14 : 12, // Keep hover area for tooltip
          showLine: false
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 0 // Disable default animation for custom blinking
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            displayColors: false,
            backgroundColor: 'rgba(0, 0, 0, 0.9)',
            titleColor: 'rgba(255, 255, 255, 1)',
            bodyColor: 'rgba(255, 255, 255, 0.9)',
            borderColor: 'rgba(255, 255, 255, 0.3)',
            borderWidth: 1,
            padding: 14,
            titleFont: {
              size: 13,
              weight: 'bold'
            },
            bodyFont: {
              size: 12
            },
            cornerRadius: 8,
            callbacks: {
              title: (context: any) => {
                const point = dataPoints[context[0].datasetIndex]
                return point.label
              },
              label: (context: any) => {
                const point = dataPoints[context.datasetIndex]
                return `Доходность: ${point.value.toFixed(2)}%`
              }
            }
          }
        },
        scales: {
          x: {
            type: 'linear',
            position: 'bottom',
            min: 12,
            max: 25,
            grid: { 
              color: 'rgba(255,255,255,0.05)',
              display: true
            },
            ticks: { 
              color: 'rgba(255,255,255,0.3)', 
              font: { size: 11 },
              stepSize: 1
            },
            title: {
              display: true,
              text: 'Доходность, %',
              color: 'rgba(255,255,255,0.5)',
              font: { size: 11 }
            }
          },
          y: {
            type: 'linear',
            min: -0.5,
            max: 0.5,
            display: false,
            grid: { display: false },
            ticks: { display: false }
          }
        }
      },
      plugins: [{
        id: 'indicesTimeline',
        afterDraw: (chart: any) => {
          const ctx = chart.ctx
          const chartArea = chart.chartArea
          const yCenter = (chartArea.top + chartArea.bottom) / 2
          const barHeight = 40
          
          // Draw horizontal beige bar
          ctx.save()
          ctx.fillStyle = 'rgba(245, 245, 220, 0.3)' // Beige color
          ctx.fillRect(chartArea.left, yCenter - barHeight / 2, chartArea.right - chartArea.left, barHeight)
          ctx.restore()
        }
      }, {
        id: 'blinkingRedPoint',
        afterDraw: (chart: any) => {
          const ctx = chart.ctx
          const redPointIndex = 3 // Index of "Оцениваемая облигация"
          const meta = chart.getDatasetMeta(redPointIndex)
          if (!meta || !meta.data || meta.data.length === 0) return
          
          const dataPoint = meta.data[0]
          const view = dataPoint.getProps(['x', 'y'], true)
          
          // Blinking animation
          const time = Date.now() / 1000
          const blink = Math.sin(time * 3) * 0.5 + 0.5 // 0 to 1
          const alpha = 0.5 + blink * 0.5 // 0.5 to 1.0
          const radius = 10 + blink * 4 // 10 to 14
          
          // Draw outer glow
          const gradient = ctx.createRadialGradient(view.x, view.y, 0, view.x, view.y, radius * 2)
          gradient.addColorStop(0, `rgba(239, 68, 68, ${alpha * 0.4})`)
          gradient.addColorStop(0.5, `rgba(239, 68, 68, ${alpha * 0.2})`)
          gradient.addColorStop(1, 'rgba(239, 68, 68, 0)')
          
          ctx.save()
          ctx.fillStyle = gradient
          ctx.beginPath()
          ctx.arc(view.x, view.y, radius * 2, 0, Math.PI * 2)
          ctx.fill()
          
          // Draw blinking circular point
          ctx.fillStyle = `rgba(239, 68, 68, ${alpha})`
          ctx.strokeStyle = `rgba(255, 255, 255, ${alpha * 0.9})`
          ctx.lineWidth = 2
          ctx.beginPath()
          ctx.arc(view.x, view.y, radius, 0, Math.PI * 2)
          ctx.fill()
          ctx.stroke()
          ctx.restore()
        }
      }]
    } as any)
    
    // Start animation loop for blinking red point
    let indicesAnimationFrameId: number | null = null
    let isIndicesAnimating = true
    const animateIndices = () => {
      if (indicesComparisonChart && isIndicesAnimating) {
        try {
          indicesComparisonChart.draw()
          if (isIndicesAnimating) {
            indicesAnimationFrameId = requestAnimationFrame(animateIndices)
          }
        } catch (e) {
          isIndicesAnimating = false
        }
      }
    }
    animateIndices()
    
    // Store animation frame ID for cleanup
    if (indicesComparisonChart) {
      const chartRef = indicesComparisonChart as any
      chartRef.__animationFrameId = indicesAnimationFrameId
      chartRef.__stopAnimation = () => {
        isIndicesAnimating = false
        const frameId = chartRef.__animationFrameId
        if (frameId !== null && frameId !== undefined && typeof frameId === 'number') {
          cancelAnimationFrame(frameId)
        }
      }
    }
  }

  // Analogous Bonds Scatter Chart
  if (analogousBondsRef.value?.getContext('2d') && report.value?.risk_indicators && report.value?.pricing) {
    const analogous = analogBondsList.value.filter(b => b.duration !== undefined && b.yield !== undefined)
    const bondDuration = report.value.risk_indicators.duration || 0
    const bondYield = (report.value.pricing.ytm || 0) * 100
    const bondName = report.value.issuer || 'Оцениваемая облигация'
    
    const datasets: any[] = []
    
    // Add analogous bonds if any
    if (analogous.length > 0) {
      datasets.push({
        label: 'Облигации-аналоги',
        data: analogous.map(b => ({ x: b.duration!, y: b.yield! })),
        backgroundColor: 'rgba(96, 165, 250, 0.6)',
        borderColor: '#60a5fa',
        pointRadius: 8,
        pointStyle: 'diamond',
        borderWidth: 2
      })
    }
    
    // Add current bond with animation
    const currentBondDataset = {
      label: bondName,
      data: [{ x: bondDuration, y: bondYield }],
      backgroundColor: '#ef4444',
      borderColor: '#ef4444',
      pointRadius: 10,
      pointStyle: 'diamond',
      borderWidth: 2,
      pointHoverRadius: 12
    }
    datasets.push(currentBondDataset)
    
    analogousBondsChart = new Chart(analogousBondsRef.value.getContext('2d') as any, {
      type: 'scatter',
      data: {
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 0 // Disable default animation for custom blinking
        },
        plugins: {
          legend: {
            display: true,
            labels: {
              color: 'rgba(255,255,255,0.6)',
              font: { size: 11 },
              usePointStyle: true
            },
            position: 'top'
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } },
            title: {
              display: true,
              text: 'Дюрация, лет',
              color: 'rgba(255,255,255,0.5)',
              font: { size: 11 }
            }
          },
          y: {
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } },
            title: {
              display: true,
              text: 'Доходность к оферте/погашению, %',
              color: 'rgba(255,255,255,0.5)',
              font: { size: 11 }
            }
          }
        }
      },
      plugins: [{
        id: 'blinkingPoint',
        afterDraw: (chart: any) => {
          const ctx = chart.ctx
          const currentBondDatasetIndex = chart.data.datasets.length - 1
          const meta = chart.getDatasetMeta(currentBondDatasetIndex)
          if (!meta || !meta.data || meta.data.length === 0) return
          
          const point = meta.data[0]
          const view = point.getProps(['x', 'y'], true)
          
          // Blinking animation using sine wave
          const time = Date.now() / 1000
          const blink = Math.sin(time * 3) * 0.5 + 0.5 // 0 to 1
          const alpha = 0.4 + blink * 0.6 // 0.4 to 1.0
          const radius = 10 + blink * 5 // 10 to 15
          
          // Draw outer glow
          const gradient = ctx.createRadialGradient(view.x, view.y, 0, view.x, view.y, radius * 2.5)
          gradient.addColorStop(0, `rgba(239, 68, 68, ${alpha * 0.5})`)
          gradient.addColorStop(0.4, `rgba(239, 68, 68, ${alpha * 0.2})`)
          gradient.addColorStop(1, 'rgba(239, 68, 68, 0)')
          
          ctx.save()
          ctx.fillStyle = gradient
          ctx.beginPath()
          ctx.arc(view.x, view.y, radius * 2.5, 0, Math.PI * 2)
          ctx.fill()
          
          // Draw blinking circular point
          ctx.fillStyle = `rgba(239, 68, 68, ${alpha})`
          ctx.strokeStyle = `rgba(255, 255, 255, ${alpha * 0.8})`
          ctx.lineWidth = 2
          ctx.beginPath()
          ctx.arc(view.x, view.y, radius, 0, Math.PI * 2)
          ctx.fill()
          ctx.stroke()
          ctx.restore()
        }
      }]
    } as any)
    
    // Start continuous animation loop
    let animationFrameId: number | null = null
    let isAnimating = true
    const animate = () => {
      if (analogousBondsChart && isAnimating) {
        try {
          analogousBondsChart.draw()
          if (isAnimating) {
            animationFrameId = requestAnimationFrame(animate)
          }
        } catch (e) {
          // Chart was destroyed
          isAnimating = false
        }
      }
    }
    animate()
    
    // Store animation frame ID and stop function for cleanup
    if (analogousBondsChart) {
      const chartRef = analogousBondsChart as any
      chartRef.__animationFrameId = animationFrameId
      chartRef.__stopAnimation = () => {
        isAnimating = false
        const frameId = chartRef.__animationFrameId
        if (frameId !== null && frameId !== undefined && typeof frameId === 'number') {
          cancelAnimationFrame(frameId)
        }
      }
    }
  }
}

// Toggle edit mode
const toggleEditMode = () => {
  editMode.value = !editMode.value
  if (editMode.value && report.value) {
    // Создаем глубокую копию отчета для редактирования
    editableReport.value = JSON.parse(JSON.stringify(report.value))
    // Инициализируем вложенные объекты, если их нет
    if (editableReport.value && !editableReport.value.issue_info) {
      editableReport.value.issue_info = {
        issue_date: null,
        maturity_date: null,
        coupon_rate: null,
        coupon_per_year: null
      }
    }
    if (editableReport.value && !editableReport.value.pricing) {
      editableReport.value.pricing = {
        clean_price_pct: null,
        ytm: null,
        g_spread_bps: null,
        g_curve_yield: null
      }
    }
    if (editableReport.value && !editableReport.value.risk_indicators) {
      editableReport.value.risk_indicators = {
        duration: null,
        mod_duration: null,
        convexity: null,
        dv01: null
      }
    }
  } else if (!editMode.value && editableReport.value) {
    // При выходе из режима редактирования обновляем основной отчет
    report.value = JSON.parse(JSON.stringify(editableReport.value))
  }
}


// Valuation date change handler
const onValuationDateChange = () => {
  // Здесь можно добавить логику пересчета отчета на новую дату
  console.log('Valuation date changed to:', valuationDate.value)
}

// Export to Excel
const exportToExcel = () => {
  const dataToExport = editMode.value && editableReport.value ? editableReport.value : report.value
  if (!dataToExport) return

  try {
    const data: any[][] = []
    
    // Заголовок
    data.push(['Отчет по облигации'])
    data.push(['Дата оценки:', valuationDate.value])
    data.push(['ISIN:', dataToExport.isin])
    data.push([])

    // Общие сведения
    data.push(['ОБЩИЕ СВЕДЕНИЯ'])
    data.push(['Эмитент', dataToExport.issuer || ''])
    data.push(['ISIN', dataToExport.isin])
    data.push(['Страна', dataToExport.risk_country || ''])
    data.push(['Сектор', dataToExport.sector || ''])
    data.push(['Отрасль', dataToExport.industry || ''])
    data.push(['Объём', dataToExport.outstanding_amount || ''])
    data.push([])

    // Параметры выпуска
    data.push(['ПАРАМЕТРЫ ВЫПУСКА'])
    data.push(['Дата начала', dataToExport.issue_info?.issue_date || ''])
    data.push(['Дата погашения', dataToExport.issue_info?.maturity_date || ''])
    data.push(['Ставка купона', dataToExport.issue_info?.coupon_rate ? (dataToExport.issue_info.coupon_rate * 100).toFixed(2) + '%' : ''])
    data.push(['Купонов в год', dataToExport.issue_info?.coupon_per_year || ''])
    data.push([])

    // Котировка и доходность
    data.push(['КОТИРОВКА И ДОХОДНОСТЬ'])
    data.push(['Чистая цена', dataToExport.pricing?.clean_price_pct ? dataToExport.pricing.clean_price_pct.toFixed(2) + '%' : ''])
    data.push(['YTM', dataToExport.pricing?.ytm ? (dataToExport.pricing.ytm * 100).toFixed(2) + '%' : ''])
    data.push(['G-spread', dataToExport.pricing?.g_spread_bps ? dataToExport.pricing.g_spread_bps + ' bps' : ''])
    data.push(['G-curve', dataToExport.pricing?.g_curve_yield ? (dataToExport.pricing.g_curve_yield * 100).toFixed(2) + '%' : ''])
    data.push([])

    // Риск-метрики
    data.push(['РИСК-МЕТРИКИ'])
    data.push(['Мод. дюрация', dataToExport.risk_indicators?.mod_duration?.toFixed(4) || ''])
    data.push(['Дюрация', dataToExport.risk_indicators?.duration?.toFixed(4) || ''])
    data.push(['Выпуклость', dataToExport.risk_indicators?.convexity?.toFixed(2) || ''])
    data.push(['DV01', dataToExport.risk_indicators?.dv01 || ''])
    data.push([])

    // Индексы
    if (dataToExport.indices) {
      data.push(['СРАВНЕНИЕ С ИНДЕКСАМИ'])
      data.push(['Индекс гос. облигаций (менее года)', dataToExport.indices.gov_less_1y ? (dataToExport.indices.gov_less_1y * 100).toFixed(2) + '%' : ''])
      data.push(['Индекс корп. облигаций (ААА)', dataToExport.indices.corp_aaa ? (dataToExport.indices.corp_aaa * 100).toFixed(2) + '%' : ''])
      data.push(['Индекс корп. облигаций (АА)', dataToExport.indices.corp_aa ? (dataToExport.indices.corp_aa * 100).toFixed(2) + '%' : ''])
      data.push(['Оцениваемая облигация', dataToExport.pricing?.ytm ? (dataToExport.pricing.ytm * 100).toFixed(2) + '%' : ''])
      data.push(['Индекс корп. облигаций (А)', dataToExport.indices.corp_a ? (dataToExport.indices.corp_a * 100).toFixed(2) + '%' : ''])
      data.push(['Индекс корп. облигаций (ВВВ)', dataToExport.indices.corp_bbb ? (dataToExport.indices.corp_bbb * 100).toFixed(2) + '%' : ''])
      data.push([])
    }

    // Рейтинги
    if (dataToExport.ratings?.issue?.length) {
      data.push(['РЕЙТИНГ ЭМИССИИ'])
      data.push(['Агентство', 'Рейтинг', 'Дата'])
      dataToExport.ratings.issue.forEach(r => {
        data.push([r.agency, r.rating, r.date || ''])
      })
      data.push([])
    }

    if (dataToExport.ratings?.issuer?.length) {
      data.push(['РЕЙТИНГ ЭМИТЕНТА'])
      data.push(['Агентство', 'Рейтинг', 'Прогноз', 'Дата'])
      dataToExport.ratings.issuer.forEach(r => {
        data.push([r.agency, r.rating, r.outlook || '', r.date || ''])
      })
      data.push([])
    }

    // Корпоративные события
    if (dataToExport.corporate_events?.length) {
      data.push(['КОРПОРАТИВНЫЕ СОБЫТИЯ'])
      data.push(['Дата', 'Описание'])
      dataToExport.corporate_events.forEach(ev => {
        data.push([ev.date || '', ev.description])
      })
    }

    // Создаем книгу Excel
    const ws = XLSX.utils.aoa_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Отчет')

    // Настройка ширины колонок
    ws['!cols'] = [
      { wch: 40 },
      { wch: 30 }
    ]

    // Сохраняем файл
    const fileName = `Bond_Report_${dataToExport.isin}_${valuationDate.value}.xlsx`
    XLSX.writeFile(wb, fileName)
  } catch (err: any) {
    console.error('Export error:', err)
    alert(`Ошибка при экспорте: ${err.message}`)
  }
}

const onChangeIsin = () => {
  if (localIsin.value?.trim()) {
    router.push({ params: { isin: localIsin.value } })
    fetchReport(localIsin.value)
  }
}

const formatNumber = (v: any) => v ? new Intl.NumberFormat('ru-RU').format(v) : '—'
const formatDate = (v: any) => v || '—'

// Analogous bonds functions
const addAnalogBond = async () => {
  if (!newAnalogIsin.value?.trim()) return
  
  const isin = newAnalogIsin.value.trim().toUpperCase()
  
  // Check if already exists
  if (analogBondsList.value.some(b => b.isin === isin)) {
    error.value = 'Облигация с таким ISIN уже добавлена'
    setTimeout(() => { error.value = null }, 3000)
    return
  }
  
  loadingAnalogs.value = true
  
  // Add to list immediately
  analogBondsList.value.push({
    isin: isin,
    name: undefined,
    duration: undefined,
    yield: undefined
  })
  
  newAnalogIsin.value = ''
  
  try {
    // Simulate API call - in real app, fetch bond data by ISIN
    await new Promise(r => setTimeout(r, 500))
    
    // Mock data - replace with actual API call
    const mockBondData: Record<string, { name: string; duration: number; yield: number }> = {
      'RU000A10XXXX': { name: 'ИЭК Холдинг, 001P-01', duration: 0.15, yield: 21.5 },
      'RU000A10YYYY': { name: 'ИЭК Холдинг, 001P-03', duration: 0.75, yield: 18.0 },
      'RU000A10ZZZZ': { name: 'ГИДРОМАШСЕРВИС, 001P-01', duration: 0.05, yield: 15.0 },
      'RU000A10AAAA': { name: 'ГИДРОМАШСЕРВИС, 001P-02', duration: 1.15, yield: 17.5 },
      'RU000A10BBBB': { name: 'ГИДРОМАШСЕРВИС, 001P-04', duration: 1.45, yield: 16.5 }
    }
    
    const bondData = mockBondData[isin] || {
      name: `Облигация ${isin}`,
      duration: Math.random() * 1.5,
      yield: 15 + Math.random() * 7
    }
    
    // Update the bond in list
    const index = analogBondsList.value.findIndex(b => b.isin === isin)
    if (index !== -1) {
      analogBondsList.value[index] = {
        isin: isin,
        name: bondData.name,
        duration: bondData.duration,
        yield: bondData.yield
      }
    }
    
    // Update report with new analogs
    if (report.value) {
      report.value.analogous_bonds = analogBondsList.value
        .filter(b => b.duration !== undefined && b.yield !== undefined)
        .map(b => ({
          name: b.name || b.isin,
          duration: b.duration!,
          yield: b.yield!
        }))
      
      // Rebuild chart
      setTimeout(() => {
        if (analogousBondsChart) analogousBondsChart.destroy()
        initCharts()
      }, 100)
    }
  } catch (e) {
    // Remove on error
    const index = analogBondsList.value.findIndex(b => b.isin === isin)
    if (index !== -1) {
      analogBondsList.value.splice(index, 1)
    }
    error.value = `Ошибка загрузки данных по ISIN ${isin}`
    setTimeout(() => { error.value = null }, 3000)
  } finally {
    loadingAnalogs.value = false
  }
}

const removeAnalogBond = (index: number) => {
  analogBondsList.value.splice(index, 1)
  
  // Update report
  if (report.value) {
    report.value.analogous_bonds = analogBondsList.value
      .filter(b => b.duration !== undefined && b.yield !== undefined)
      .map(b => ({
        name: b.name || b.isin,
        duration: b.duration!,
        yield: b.yield!
      }))
    
    // Rebuild chart
    setTimeout(() => {
      if (analogousBondsChart) analogousBondsChart.destroy()
      initCharts()
    }, 100)
  }
}

const exportChart = (name: 'price' | 'yield') => {
  const canvas = name === 'price' ? priceHistoryRef.value : yieldDynamicsRef.value
  if (!canvas) return
  const link = document.createElement('a')
  link.href = canvas.toDataURL('image/png')
  link.download = `bond-${name}-${new Date().toISOString().split('T')[0]}.png`
  link.click()
}

onMounted(() => fetchReport(isin.value || 'RU000A103943'))
onBeforeUnmount(() => {
  if (priceHistoryChart) priceHistoryChart.destroy()
  if (yieldDynamicsChart) yieldDynamicsChart.destroy()
  if (indicesComparisonChart) indicesComparisonChart.destroy()
  if (analogousBondsChart) {
    // Stop animation
    const stopAnimation = (analogousBondsChart as any).__stopAnimation
    if (stopAnimation && typeof stopAnimation === 'function') {
      stopAnimation()
    }
    
    // Cancel animation frame if exists
    const frameId = (analogousBondsChart as any).__animationFrameId
    if (frameId !== null && frameId !== undefined && typeof frameId === 'number') {
      cancelAnimationFrame(frameId)
    }
    analogousBondsChart.destroy()
  }
})
</script>

<style scoped>
* { box-sizing: border-box; }

/* ============================================
   PAGE CONTAINER & BACKGROUND
   ============================================ */
.page-container {
  padding: 24px 32px;
  max-width: 1600px;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.glass-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 
    0 20px 40px -10px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 
    0 25px 50px -10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.glass-card.error {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
  border-color: rgba(239, 68, 68, 0.2);
}

.glass-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-pill:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

/* ============================================
   HEADER & INPUTS
   ============================================ */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 4px;
  flex-shrink: 0;
}

.header-left { flex: 1; }
.section-title { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; }
.section-subtitle { font-size: 13px; color: rgba(255, 255, 255, 0.5); margin: 4px 0 0 0; }
.header-actions { display: flex; gap: 12px; }

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 13px;
  outline: none;
  padding: 4px;
  font-family: 'SF Mono', monospace;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.search-input:focus {
  color: rgba(255, 255, 255, 0.95);
}

.btn-search {
  background: transparent;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: 14px;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-search:hover:not(:disabled) {
  color: #60a5fa;
  background: rgba(59, 130, 246, 0.1);
  transform: scale(1.05);
}

.btn-search:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.lbl-mini { font-size: 10px; color: rgba(255,255,255,0.5); font-weight: 600; text-transform: uppercase; }

.date-input-small {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  padding: 4px 8px;
  cursor: pointer;
  font-family: inherit;
  min-width: 140px;
}

.date-input-small::-webkit-calendar-picker-indicator {
  filter: invert(1);
  cursor: pointer;
}

.date-input-small::-webkit-datetime-edit-text {
  color: #fff;
}

.date-input-small::-webkit-datetime-edit-month-field,
.date-input-small::-webkit-datetime-edit-day-field,
.date-input-small::-webkit-datetime-edit-year-field {
  color: #fff;
}

.btn-toggle-edit {
  padding: 8px 16px;
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 8px;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-toggle-edit:hover {
  background: rgba(34, 197, 94, 0.25);
  border-color: rgba(34, 197, 94, 0.5);
  transform: translateY(-1px);
}

.btn-toggle-edit.active {
  background: rgba(34, 197, 94, 0.3);
  border-color: rgba(34, 197, 94, 0.5);
  color: #4ade80;
}

.btn-export-excel {
  padding: 8px 16px;
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 8px;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-export-excel:hover:not(:disabled) {
  background: rgba(245, 158, 11, 0.25);
  border-color: rgba(245, 158, 11, 0.5);
  transform: translateY(-1px);
}

.btn-export-excel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.edit-input {
  width: 100%;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 6px;
  color: #fff;
  padding: 4px 8px;
  font-size: 12px;
  outline: none;
  transition: all 0.2s;
}

.edit-input:focus {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.5);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.edit-input-inline {
  width: 120px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 6px;
  color: #fff;
  padding: 4px 8px;
  font-size: 12px;
  outline: none;
  transition: all 0.2s;
  text-align: right;
}

.edit-input-inline:focus {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.5);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

/* ============================================
   GRID & CONTENT
   ============================================ */
.report-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.state-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.full-width { grid-column: 1 / -1; }

.card-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 16px; 
}
.card-header h3 { font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.6); text-transform: uppercase; margin: 0; letter-spacing: 0.05em; }

/* ============================================
   TABLES & METRICS
   ============================================ */
.info-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.info-table td {
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.9);
  transition: color 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.info-table tr:hover td {
  color: rgba(255, 255, 255, 0.95);
}

.info-table tr:last-child td {
  border-bottom: none;
}

.info-table td:first-child {
  color: rgba(255, 255, 255, 0.5);
  width: 40%;
  font-weight: 500;
}

.info-table td:last-child {
  text-align: right;
  font-weight: 500;
}

.metric-list { display: flex; flex-direction: column; gap: 8px; }
.metric {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  padding-bottom: 6px;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.08);
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.metric:last-child {
  border-bottom: none;
}

.metric > span:first-child {
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.val {
  color: #fff;
  font-weight: 600;
}

.ratings-list { display: flex; flex-direction: column; gap: 6px; }
.rating-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  gap: 8px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.rating-item:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.08);
}
.rating-info { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; }
.agency { color: rgba(255,255,255,0.4); font-size: 10px; font-weight: 500; }
.grade { font-weight: 700; color: #fff; }
.outlook { font-size: 10px; color: rgba(255, 255, 255, 0.4); }
.date { font-size: 10px; color: rgba(255, 255, 255, 0.3); }

/* ============================================
   CHARTS & UTILS
   ============================================ */
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.chart-container {
  position: relative;
  width: 100%;
  height: 360px;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.chart-container.tall {
  height: 480px;
}

.chart-container.indices-chart {
  height: 200px;
}

.chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

.btn-export {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  font-weight: 500;
}

.btn-export:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.mono { font-family: 'SF Mono', monospace; }
.accent { color: #38bdf8; font-weight: 600; }
.text-accent { color: #38bdf8; font-weight: 600; }
.muted { color: rgba(255, 255, 255, 0.4); margin: 0; font-size: 12px; }
.status-text-active {
  color: #4ade80;
  font-weight: 600;
}
.spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(56, 189, 248, 0.3); border-top-color: #38bdf8; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ============================================
   COMPARISON SECTION
   ============================================ */
.comparison-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.comparison-table thead th {
  text-align: left;
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 10px;
  letter-spacing: 0.05em;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.comparison-table tbody td {
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.comparison-table tbody tr:last-child td {
  border-bottom: none;
}

.comparison-table tbody tr.highlight-row {
  background: rgba(239, 68, 68, 0.1);
}

.comparison-table tbody tr.highlight-row td {
  color: #fff;
  font-weight: 600;
}

/* ============================================
   EVENTS LIST
   ============================================ */
.events-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.event-item {
  display: flex;
  gap: 16px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.event-item:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.08);
}

.event-date {
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
  font-weight: 600;
  min-width: 100px;
  flex-shrink: 0;
}

.event-description {
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
  line-height: 1.5;
  flex: 1;
}

/* ============================================
   STATUS BADGES
   ============================================ */
.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.fulfilled {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

/* ============================================
   ANALOGOUS BONDS INPUT
   ============================================ */
.analogous-input-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.analogs-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.analog-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.analog-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.12);
}

.analog-isin {
  color: rgba(255, 255, 255, 0.7);
  font-size: 11px;
  font-weight: 600;
  min-width: 120px;
  flex-shrink: 0;
}

.analog-name {
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
  flex: 1;
}

.btn-remove {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f87171;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  flex-shrink: 0;
  padding: 0;
}

.btn-remove:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.5);
  color: #ef4444;
  transform: scale(1.1);
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1200px) { 
  .grid-3 { grid-template-columns: repeat(2, 1fr); } 
}

@media (max-width: 1024px) {
  .section-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .header-actions { width: 100%; }
  .glass-pill { width: 100%; }
  .search-input { flex: 1; }
  .grid-2, .grid-3 { grid-template-columns: 1fr; }
  .comparison-section {
    gap: 16px;
}
}

@media (max-width: 768px) { 
  .page-container { padding: 16px; } 
  .section-title { font-size: 20px; }
  .chart-container { height: 300px; }
  .chart-container.tall { height: 400px; }
  .chart-container.indices-chart { height: 180px; }
  .rating-item, .metric { flex-direction: column; align-items: flex-start; gap: 4px; }
  .val, .metric-value { text-align: left; }
  .comparison-table {
    font-size: 11px;
  }
  .comparison-table thead th,
  .comparison-table tbody td {
    padding: 8px 12px;
  }
  .analogous-input-section {
    padding: 12px;
  }
  .analog-item {
    flex-wrap: wrap;
    padding: 8px;
  }
  .analog-isin {
    min-width: 100px;
    font-size: 10px;
  }
  .analog-name {
    font-size: 11px;
  }
  .events-list {
    gap: 8px;
  }
  .event-item {
    flex-direction: column;
    gap: 8px;
    padding: 10px;
  }
  .event-date {
    min-width: auto;
  }
}

@media (max-width: 480px) {
  .page-container { padding: 12px; }
  .section-title { font-size: 18px; }
  .chart-container { height: 250px; }
  .chart-container.tall { height: 300px; }
  .chart-container.indices-chart { height: 150px; }
  .info-table {
    font-size: 10px;
  }
  .comparison-table {
    font-size: 10px;
  }
  .comparison-table thead th,
  .comparison-table tbody td {
    padding: 6px 8px;
  }
  .status-badge {
    font-size: 9px;
    padding: 3px 6px;
  }
  .note-text {
    font-size: 9px;
  }
}
</style>