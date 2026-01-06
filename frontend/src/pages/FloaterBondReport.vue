<!-- src/pages/FloaterBondReport.vue -->
<template>
  <div class="page-container">
    
    <!-- Header Section -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title" v-if="report">
          {{ report.issuer }}, {{ report.isin }}
        </h1>
        <h1 class="section-title" v-else>Floater Bond Report</h1>
        <p class="section-subtitle" v-if="report">
          Отчет по облигации с плавающим купоном ISIN: <span class="text-accent">{{ report.isin }}</span>
        </p>
        <p class="section-subtitle" v-else>
          Отчет по облигации с плавающим купоном ISIN: <span class="text-accent">{{ isin || '—' }}</span>
        </p>
      </div>
      
      <div class="header-actions">
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
            <tr><td class="label">Эмитент</td><td class="value">{{ report.issuer }}</td></tr>
            <tr><td class="label">ISIN</td><td class="value mono">{{ report.isin }}</td></tr>
            <tr><td class="label">Страна риска</td><td class="value">{{ report.risk_country || '—' }}</td></tr>
            <tr><td class="label">Сектор</td><td class="value">{{ report.sector || '—' }}</td></tr>
            <tr><td class="label">Отрасль</td><td class="value">{{ report.industry || '—' }}</td></tr>
            <tr><td class="label">Кол-во выпусков в обращении</td><td class="value mono">{{ report.issues_count || '—' }}</td></tr>
          </table>
        </div>

        <div class="glass-card">
          <div class="card-header">
            <h3>Информация по выпуску</h3>
          </div>
          <table class="info-table">
            <tr><td class="label">Дата выпуска</td><td class="value mono">{{ formatDate(report.issue_info?.issue_date) }}</td></tr>
            <tr><td class="label">Объем в обращении, RUB</td><td class="value mono">{{ formatNumber(report.outstanding_amount) || '—' }}</td></tr>
            <tr><td class="label">Дата погашения</td><td class="value mono">{{ formatDate(report.issue_info?.maturity_date) }}</td></tr>
            <tr><td class="label">Купон, %</td><td class="value accent">{{ report.issue_info?.coupon_formula || '—' }}</td></tr>
            <tr><td class="label">Следующий купон</td><td class="value accent">{{ report.issue_info?.next_coupon ? ((report.issue_info.next_coupon * 100).toFixed(2) + '%') : '—' }}</td></tr>
            <tr><td class="label">Номинал, RUB</td><td class="value mono">{{ report.issue_info?.nominal ? formatNumber(report.issue_info.nominal) : '—' }}</td></tr>
            <tr><td class="label">Кол-во купонных платежей в год</td><td class="value mono">{{ report.issue_info?.coupon_per_year ?? '—' }}</td></tr>
            <tr><td class="label">Анализируемый период</td><td class="value mono">{{ report.analysis_period || '—' }}</td></tr>
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
            <div class="metric"><span>Чистая цена</span><span class="val accent">{{ report.pricing?.clean_price_pct?.toFixed(2) }}%</span></div>
            <div class="metric"><span>YTM</span><span class="val accent">{{ report.pricing?.ytm ? ((report.pricing.ytm * 100).toFixed(2) + '%') : '—' }}</span></div>
            <div class="metric"><span>G-spread</span><span class="val mono">{{ report.pricing?.g_spread_bps ?? '—' }}<span v-if="report.pricing?.g_spread_bps"> bps</span></span></div>
            <div class="metric"><span>G-curve</span><span class="val mono">{{ report.pricing?.g_curve_yield ? ((report.pricing.g_curve_yield * 100).toFixed(2) + '%') : '—' }}</span></div>
          </div>
          <p class="note-text">* Доходность, дюрация и следующий купон рассчитаны на основе рыночных значений форвардной кривой к ключевой ставке ЦБ РФ</p>
        </div>

        <div class="glass-card">
          <div class="card-header">
            <h3>Риск-метрики</h3>
          </div>
          <div class="metric-list">
            <div class="metric"><span>Мод. дюрация</span><span class="val">{{ report.risk_indicators?.mod_duration?.toFixed(2) || report.risk_indicators?.duration?.toFixed(2) || '—' }}</span></div>
            <div class="metric"><span>Дюрация</span><span class="val">{{ report.risk_indicators?.duration?.toFixed(2) }}</span></div>
            <div class="metric"><span>Выпуклость</span><span class="val">{{ report.risk_indicators?.convexity?.toFixed(2) }}</span></div>
            <div class="metric"><span>DV01</span><span class="val">{{ formatNumber(report.risk_indicators?.dv01) }}</span></div>
          </div>
        </div>
      </div>

      <!-- BLOCK 2: Price Chart -->
      <div class="glass-card full-width">
        <div class="chart-header">
          <h3>Динамика цен</h3>
          <button class="btn-export" @click="exportChart('price')">💾 PNG</button>
        </div>
        <div class="chart-container tall">
          <canvas ref="priceHistoryRef"></canvas>
        </div>
      </div>

      <!-- BLOCK 3: DM and QM Dynamics Chart -->
      <div class="glass-card full-width">
        <div class="chart-header">
          <h3>Динамика дисконтной маржи (DM) и фиксированной маржи (QM)</h3>
          <button class="btn-export" @click="exportChart('margin')">💾 PNG</button>
        </div>
        <div class="chart-container tall">
          <canvas ref="marginDynamicsRef"></canvas>
        </div>
      </div>

      <!-- Comparison with Indices -->
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
                <td>Доходность индекса государственных облигаций (1-3 года)</td>
                <td class="mono">{{ report.indices?.gov_1_3y ? ((report.indices.gov_1_3y * 100).toFixed(2)) : '—' }}%</td>
              </tr>
              <tr>
                <td>Доходность индекса корпоративных облигаций с рейтингом ААА (1-3 года)</td>
                <td class="mono">{{ report.indices?.corp_aaa_1_3y ? ((report.indices.corp_aaa_1_3y * 100).toFixed(2)) : '—' }}%</td>
              </tr>
              <tr>
                <td>Доходность индекса корпоративных облигаций с рейтингом АА (1-3 года)</td>
                <td class="mono">{{ report.indices?.corp_aa_1_3y ? ((report.indices.corp_aa_1_3y * 100).toFixed(2)) : '—' }}%</td>
              </tr>
              <tr>
                <td>Доходность индекса корпоративных облигаций с рейтингом А (1-3 года)</td>
                <td class="mono">{{ report.indices?.corp_a_1_3y ? ((report.indices.corp_a_1_3y * 100).toFixed(2)) : '—' }}%</td>
              </tr>
              <tr>
                <td>Доходность индекса корпоративных облигаций с рейтингом ВВВ</td>
                <td class="mono">{{ report.indices?.corp_bbb ? ((report.indices.corp_bbb * 100).toFixed(2)) : '—' }}%</td>
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
        <p v-if="report.analogous_bonds_note" class="note-text">{{ report.analogous_bonds_note }}</p>
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
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Chart from 'chart.js/auto'

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
  issues_count?: number | null
  analysis_period?: string | null
  issue_info?: {
    issue_date?: string | null
    maturity_date?: string | null
    coupon_formula?: string | null
    next_coupon?: number | null
    nominal?: number | null
    coupon_per_year?: number | null
  }
  ratings?: {
    issue?: RatingEntry[]
    issuer?: RatingEntry[]
    guarantor?: RatingEntry[]
  }
  activity_criteria?: {
    trading_days?: { value?: number; threshold?: number }
    trades?: { value?: number; threshold?: number }
    turnover?: { value?: number; threshold?: number }
    traded_30d?: boolean
    source?: string
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
  indices?: {
    gov_1_3y?: number
    corp_aaa_1_3y?: number
    corp_aa_1_3y?: number
    corp_a_1_3y?: number
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
  analogous_bonds_note?: string
}

const route = useRoute()
const router = useRouter()

const isin = computed(() => (route.params.isin as string) || '')
const localIsin = ref(isin.value)

const loading = ref(false)
const error = ref<string | null>(null)
const report = ref<BondReport | null>(null)

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
const marginDynamicsRef = ref<HTMLCanvasElement | null>(null)
const indicesComparisonRef = ref<HTMLCanvasElement | null>(null)
const analogousBondsRef = ref<HTMLCanvasElement | null>(null)

let priceHistoryChart: Chart | null = null
let marginDynamicsChart: Chart | null = null
let indicesComparisonChart: Chart | null = null
let analogousBondsChart: Chart | null = null

const fetchReport = async (targetIsin: string) => {
  if (!targetIsin) return
  loading.value = true
  error.value = null
  report.value = null

  try {
    await new Promise(r => setTimeout(r, 600))
    
    // Data from template (РУСАЛ, БО-001Р-09)
    report.value = {
      isin: targetIsin || 'RU000A108VW7',
      issuer: '"Объединённая Компания "РУСАЛ", МКПАО',
      risk_country: 'Россия',
      sector: 'Корпоративный',
      industry: 'Цветная металлургия',
      outstanding_amount: 30000000000,
      issues_count: 15,
      analysis_period: 'с 01.10.2025 по 01.11.2025',
      issue_info: {
        issue_date: '2024-07-02',
        maturity_date: '2027-06-17',
        coupon_formula: 'Ключевая ставка ЦБ РФ + 2,2%',
        next_coupon: 0.187,
        nominal: 1000,
        coupon_per_year: 12
      },
      ratings: {
        issue: [
          { agency: 'AKPA', rating: 'A+(RU)', date: '2025-03-27' }
        ],
        issuer: [
          { agency: 'Эксперт РА', rating: 'ruA+', outlook: 'Стабильный', date: '2025-08-29' },
          { agency: 'AKPA', rating: 'a+(ru)', outlook: 'Стабильный', date: '2025-03-27' }
        ]
      },
      activity_criteria: {
        trading_days: { value: 22, threshold: 5 },
        trades: { value: 3312, threshold: 10 },
        turnover: { value: 0.0093, threshold: 0.001 },
        traded_30d: true,
        source: 'Московская биржа'
      },
      market_activity: {
        trading_days: 22,
        trades: 3312,
        turnover_to_outstanding: 0.0093,
        traded_last_30d: true
      },
      pricing: {
        clean_price_pct: 100.29,
        ytm: 0.1721,
        g_spread_bps: 326.47,
        g_curve_yield: 0.1394
      },
      risk_indicators: {
        duration: 1.43,
        convexity: 0.04,
        dv01: 6
      },
      indices: {
        gov_1_3y: 0.1398,
        corp_aaa_1_3y: 0.1576,
        corp_aa_1_3y: 0.1711,
        corp_a_1_3y: 0.2028,
        corp_bbb: 0.3072
      },
      corporate_events: [
        { date: '2025-10-30', description: '"Русал" созовет акционеров 3 декабря для рассмотрения вопроса о выплате дивидендов' },
        { date: '2025-10-17', description: 'Русал объявил о выкупе 3 миллионов своих облигаций на сумму 3 миллиарда китайских юаней с обязательным досрочным выкупом за месяц до погашения' },
        { date: '2025-10-13', description: 'Русал приостановил работу крупнейшего кремниевого завода в Иркутской области с 1 января 2026 года из-за мирового перепроизводства кремния и демпингового импорта из Китая' }
      ],
      analogous_bonds: [
        { name: 'ХК Новотранс, 001P-05', duration: 1.1, yield: 17.7 },
        { name: 'Новабев Групп, БО-П05', duration: 1.0, yield: 16.8 },
        { name: 'КАМАЗ, БО-П15', duration: 1.4, yield: 16.0 },
        { name: 'Автодор (Государственная компания), БО-003Р-02', duration: 1.6, yield: 16.7 },
        { name: 'ЕвразХолдинг Финанс, 003Р-04', duration: 1.95, yield: 16.5 }
      ],
      analogous_bonds_note: 'В связи недостаточным количеством аналогов по отрасли, также приведены аналоги из других отраслей'
    }
    setTimeout(() => initCharts(), 100)
  } catch (err: any) {
    error.value = err.message || 'Ошибка загрузки данных'
  } finally {
    loading.value = false
  }
}

const onChangeIsin = () => {
  if (!localIsin.value) return
  router.push(`/floater-bond-report/${localIsin.value}`)
}

const formatDate = (dateStr?: string | null): string => {
  if (!dateStr) return '—'
  try {
    const date = new Date(dateStr)
    const day = String(date.getDate()).padStart(2, '0')
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const year = date.getFullYear()
    return `${day}.${month}.${year}`
  } catch {
    return dateStr
  }
}

const formatNumber = (num?: number | null): string => {
  if (num === undefined || num === null) return '—'
  return new Intl.NumberFormat('ru-RU').format(num)
}

const initCharts = () => {
  if (priceHistoryChart) priceHistoryChart.destroy()
  if (marginDynamicsChart) marginDynamicsChart.destroy()
  if (indicesComparisonChart) indicesComparisonChart.destroy()
  if (analogousBondsChart) analogousBondsChart.destroy()

  // Price History Chart
  if (priceHistoryRef.value?.getContext('2d')) {
    const months = ['01.11.2024', '01.12.2024', '01.01.2025', '01.02.2025', '01.03.2025', '01.04.2025', '01.05.2025', '01.06.2025', '01.07.2025', '01.08.2025', '01.09.2025', '01.10.2025', '01.11.2025']
    const prices = [98, 92, 88, 90, 92, 94, 93, 95, 96, 97, 98, 99, 100]
    
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
          legend: { display: false }
        },
        scales: {
          x: { 
            grid: { display: false }, 
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } } 
          },
          y: { 
            grid: { color: 'rgba(255,255,255,0.05)' }, 
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } },
            min: 88,
            max: 102,
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

  // Margin Dynamics Chart (DM and QM)
  if (marginDynamicsRef.value?.getContext('2d')) {
    const months = ['01.11.2024', '01.12.2024', '01.01.2025', '01.02.2025', '01.03.2025', '01.04.2025', '01.05.2025', '01.06.2025', '01.07.2025', '01.08.2025', '01.09.2025', '01.10.2025', '01.11.2025']
    const dm = [250, 280, 320, 380, 450, 520, 570, 580, 400, 250, 220, 200, 200]
    const qm = [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200]
    
    marginDynamicsChart = new Chart(marginDynamicsRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: months,
        datasets: [
          {
            label: 'DM',
            data: dm,
            borderColor: '#60a5fa',
            backgroundColor: 'rgba(96, 165, 250, 0.08)',
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            borderWidth: 2
          },
          {
            label: 'QM',
            data: qm,
            borderColor: '#f59e0b',
            backgroundColor: 'transparent',
            fill: false,
            tension: 0.4,
            pointRadius: 0,
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
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
            grid: { display: false }, 
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } } 
          },
          y: { 
            grid: { color: 'rgba(255,255,255,0.05)' }, 
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } },
            min: 170,
            max: 620,
            title: {
              display: true,
              text: 'б.п.',
              color: 'rgba(255,255,255,0.5)',
              font: { size: 11 }
            }
          }
        }
      }
    } as any)
  }

  // Indices Comparison Chart
  if (indicesComparisonRef.value?.getContext('2d') && report.value?.indices && report.value?.pricing) {
    const indices = report.value.indices
    const bondYtm = (report.value.pricing.ytm || 0) * 100
    
    const dataPoints = [
      { label: 'Индекс гос. облигаций', value: (indices.gov_1_3y || 0) * 100, color: '#9ca3af' },
      { label: 'Индекс корп. облигаций (ААА)', value: (indices.corp_aaa_1_3y || 0) * 100, color: '#9ca3af' },
      { label: 'Индекс корп. облигаций (АА)', value: (indices.corp_aa_1_3y || 0) * 100, color: '#9ca3af' },
      { label: 'Оцениваемая облигация', value: bondYtm, color: '#ef4444' },
      { label: 'Индекс корп. облигаций (А)', value: (indices.corp_a_1_3y || 0) * 100, color: '#9ca3af' },
      { label: 'Индекс корп. облигаций (ВВВ)', value: (indices.corp_bbb || 0) * 100, color: '#9ca3af' }
    ]
    
    indicesComparisonChart = new Chart(indicesComparisonRef.value.getContext('2d') as any, {
      type: 'scatter',
      data: {
        datasets: dataPoints.map((point, index) => ({
          label: point.label,
          data: [{ x: point.value, y: 0 }],
          backgroundColor: index === 3 ? 'rgba(239, 68, 68, 0)' : point.color,
          borderColor: index === 3 ? 'rgba(239, 68, 68, 0)' : point.color,
          pointRadius: index === 3 ? 1 : 10,
          pointHoverRadius: index === 3 ? 14 : 12,
          showLine: false
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 0 },
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
            titleFont: { size: 13, weight: 'bold' },
            bodyFont: { size: 12 },
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
            min: 13,
            max: 31,
            grid: { color: 'rgba(255,255,255,0.05)', display: true },
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 }, stepSize: 2 },
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
          ctx.save()
          ctx.fillStyle = 'rgba(245, 245, 220, 0.3)'
          ctx.fillRect(chartArea.left, yCenter - barHeight / 2, chartArea.right - chartArea.left, barHeight)
          ctx.restore()
        }
      }, {
        id: 'blinkingRedPoint',
        afterDraw: (chart: any) => {
          const ctx = chart.ctx
          const redPointIndex = 3
          const meta = chart.getDatasetMeta(redPointIndex)
          if (!meta || !meta.data || meta.data.length === 0) return
          const dataPoint = meta.data[0]
          const view = dataPoint.getProps(['x', 'y'], true)
          const time = Date.now() / 1000
          const blink = Math.sin(time * 3) * 0.5 + 0.5
          const alpha = 0.5 + blink * 0.5
          const radius = 10 + blink * 4
          const gradient = ctx.createRadialGradient(view.x, view.y, 0, view.x, view.y, radius * 2)
          gradient.addColorStop(0, `rgba(239, 68, 68, ${alpha * 0.4})`)
          gradient.addColorStop(0.5, `rgba(239, 68, 68, ${alpha * 0.2})`)
          gradient.addColorStop(1, 'rgba(239, 68, 68, 0)')
          ctx.save()
          ctx.fillStyle = gradient
          ctx.beginPath()
          ctx.arc(view.x, view.y, radius * 2, 0, Math.PI * 2)
          ctx.fill()
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
      data: { datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 0 },
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
          const time = Date.now() / 1000
          const blink = Math.sin(time * 3) * 0.5 + 0.5
          const alpha = 0.4 + blink * 0.6
          const radius = 10 + blink * 5
          const gradient = ctx.createRadialGradient(view.x, view.y, 0, view.x, view.y, radius * 2.5)
          gradient.addColorStop(0, `rgba(239, 68, 68, ${alpha * 0.5})`)
          gradient.addColorStop(0.4, `rgba(239, 68, 68, ${alpha * 0.2})`)
          gradient.addColorStop(1, 'rgba(239, 68, 68, 0)')
          ctx.save()
          ctx.fillStyle = gradient
          ctx.beginPath()
          ctx.arc(view.x, view.y, radius * 2.5, 0, Math.PI * 2)
          ctx.fill()
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
          isAnimating = false
        }
      }
    }
    animate()
    
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

const exportChart = (name: 'price' | 'margin') => {
  const canvas = name === 'price' ? priceHistoryRef.value : marginDynamicsRef.value
  if (!canvas) return
  const link = document.createElement('a')
  link.href = canvas.toDataURL('image/png')
  link.download = `floater-bond-${name}-${new Date().toISOString().split('T')[0]}.png`
  link.click()
}

watch(() => route.params.isin, (newIsin) => {
  if (newIsin) {
    localIsin.value = newIsin as string
    fetchReport(newIsin as string)
  }
}, { immediate: true })

onMounted(() => {
  if (isin.value) {
    fetchReport(isin.value)
  } else {
    // Load default ISIN
    fetchReport('RU000A108VW7')
  }
})

onBeforeUnmount(() => {
  if (priceHistoryChart) priceHistoryChart.destroy()
  if (marginDynamicsChart) marginDynamicsChart.destroy()
  if (indicesComparisonChart) {
    // Stop animation
    const stopAnimation = (indicesComparisonChart as any).__stopAnimation
    if (stopAnimation && typeof stopAnimation === 'function') {
      stopAnimation()
    }
    
    // Cancel animation frame if exists
    const frameId = (indicesComparisonChart as any).__animationFrameId
    if (frameId !== null && frameId !== undefined && typeof frameId === 'number') {
      cancelAnimationFrame(frameId)
    }
    indicesComparisonChart.destroy()
  }
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

.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }

.info-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.info-table td {
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.9);
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

.ratings-list { display: flex; flex-direction: column; gap: 6px; }
.rating-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  gap: 8px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.rating-info { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; }
.agency { color: rgba(255,255,255,0.4); font-size: 10px; font-weight: 500; }
.grade { font-weight: 700; color: #fff; }
.outlook { font-size: 10px; color: rgba(255, 255, 255, 0.4); }
.date { font-size: 10px; color: rgba(255, 255, 255, 0.3); }

.activity-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.activity-table thead th {
  text-align: left;
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 600;
  text-transform: uppercase; 
  font-size: 10px;
  letter-spacing: 0.05em; 
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.activity-table tbody td {
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.activity-table tbody tr:last-child td {
  border-bottom: none;
}

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

.status-text-active {
  color: #4ade80;
  font-weight: 600;
}

.status-text-active {
  color: #4ade80;
  font-weight: 600;
}

.note-text {
  margin-top: 16px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  font-style: italic;
}

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
   ACTIVITY TABLE
   ============================================ */
.activity-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.activity-table thead th {
  text-align: left;
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 10px;
  letter-spacing: 0.05em;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.activity-table tbody td {
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.activity-table tbody tr:last-child td {
  border-bottom: none;
}

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

.status-text-active {
  color: #4ade80;
  font-weight: 600;
}

.status-text-active {
  color: #4ade80;
  font-weight: 600;
}

.note-text {
  margin-top: 16px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  font-style: italic;
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
  .activity-table {
    font-size: 11px;
  }
  .activity-table thead th,
  .activity-table tbody td {
    padding: 8px 12px;
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
  .activity-table {
    font-size: 10px;
  }
  .activity-table thead th,
  .activity-table tbody td {
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
