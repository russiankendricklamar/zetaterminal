<!-- src/pages/VanillaBondReport.vue -->
<template>
  <div class="page-container">
    
    <!-- Header Section -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Vanilla Bond Report</h1>
        <p class="section-subtitle">
          Паспорт выпуска и аналитика по ISIN: <span class="text-accent">{{ isin || '—' }}</span>
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
            <tr><td class="label">Страна</td><td class="value">{{ report.risk_country || '—' }}</td></tr>
            <tr><td class="label">Сектор</td><td class="value">{{ report.sector || '—' }}</td></tr>
            <tr><td class="label">Отрасль</td><td class="value">{{ report.industry || '—' }}</td></tr>
            <tr><td class="label">Объём</td><td class="value mono">{{ formatNumber(report.outstanding_amount) || '—' }}</td></tr>
          </table>
        </div>

        <div class="glass-card">
          <div class="card-header">
            <h3>Параметры выпуска</h3>
          </div>
          <table class="info-table">
            <tr><td class="label">Дата начала</td><td class="value mono">{{ formatDate(report.issue_info?.issue_date) }}</td></tr>
            <tr><td class="label">Дата погашения</td><td class="value mono">{{ formatDate(report.issue_info?.maturity_date) }}</td></tr>
            <tr><td class="label">Ставка купона</td><td class="value"><span v-if="report.issue_info?.coupon_rate !== null" class="accent">{{ (report.issue_info.coupon_rate * 100).toFixed(2) }}%</span><span v-else>—</span></td></tr>
            <tr><td class="label">Купонов в год</td><td class="value mono">{{ report.issue_info?.coupon_per_year ?? '—' }}</td></tr>
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
          </div>
          <div class="metric-list">
            <div class="metric"><span>Кол-во торговых дней</span><span class="val">{{ report.market_activity?.trading_days ?? '—' }}</span></div>
            <div class="metric"><span>Кол-во сделок</span><span class="val">{{ report.market_activity?.trades ?? '—' }}</span></div>
            <div class="metric"><span>Объем торгов/выпуск</span><span class="val">{{ (report.market_activity?.turnover_to_outstanding * 100).toFixed(2) }}%</span></div>
            <div class="metric"><span>Торги 30 дней</span><span class="val">{{ report.market_activity?.traded_last_30d ? 'Да' : 'Нет' }}</span></div>
          </div>
        </div>

        <div class="glass-card">
          <div class="card-header">
            <h3>Котировка и доходность</h3>
          </div>
          <div class="metric-list">
            <div class="metric"><span>Чистая цена</span><span class="val accent">{{ report.pricing?.clean_price_pct?.toFixed(2) }}%</span></div>
            <div class="metric"><span>YTM</span><span class="val accent">{{ (report.pricing?.ytm * 100).toFixed(2) }}%</span></div>
            <div class="metric"><span>G-spread</span><span class="val mono">{{ report.pricing?.g_spread_bps }} bps</span></div>
            <div class="metric"><span>G-curve</span><span class="val mono">{{ (report.pricing?.g_curve_yield * 100).toFixed(2) }}%</span></div>
          </div>
        </div>

        <div class="glass-card">
          <div class="card-header">
            <h3>Риск-метрики</h3>
          </div>
          <div class="metric-list">
            <div class="metric"><span>Дюрация</span><span class="val">{{ report.risk_indicators?.duration?.toFixed(2) }}</span></div>
            <div class="metric"><span>Выпуклость</span><span class="val">{{ report.risk_indicators?.convexity?.toFixed(2) }}</span></div>
            <div class="metric"><span>DV01</span><span class="val">{{ formatNumber(report.risk_indicators?.dv01) }}</span></div>
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

      <!-- BLOCK 3: Yield Chart -->
      <div class="glass-card full-width">
        <div class="chart-header">
          <h3>Динамика доходности</h3>
          <button class="btn-export" @click="exportChart('yield')">💾 PNG</button>
        </div>
        <div class="chart-container tall">
          <canvas ref="yieldDynamicsRef"></canvas>
        </div>
      </div>

    </section>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, onBeforeUnmount } from 'vue'
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
    convexity?: number | null
    dv01?: number | null
  }
  ratings?: {
    issue?: RatingEntry[]
    issuer?: RatingEntry[]
    guarantor?: RatingEntry[]
  }
}

const route = useRoute()
const router = useRouter()

const isin = computed(() => (route.params.isin as string) || '')
const localIsin = ref(isin.value)

const loading = ref(false)
const error = ref<string | null>(null)
const report = ref<BondReport | null>(null)

const priceHistoryRef = ref<HTMLCanvasElement | null>(null)
const yieldDynamicsRef = ref<HTMLCanvasElement | null>(null)

let priceHistoryChart: Chart | null = null
let yieldDynamicsChart: Chart | null = null

const fetchReport = async (targetIsin: string) => {
  if (!targetIsin) return
  loading.value = true
  error.value = null
  report.value = null

  try {
    await new Promise(r => setTimeout(r, 600))
    
    report.value = {
      isin: targetIsin,
      issuer: 'ПАО "Газпром нефть"',
      risk_country: 'Россия',
      sector: 'Корпоративный',
      industry: 'Нефтегаз',
      outstanding_amount: 30000000000,
      issue_info: {
        issue_date: '2023-01-20',
        maturity_date: '2026-01-20',
        coupon_rate: 0.1025,
        coupon_per_year: 2
      },
      market_activity: {
        trading_days: 22,
        trades: 150,
        turnover_to_outstanding: 0.004,
        traded_last_30d: true
      },
      pricing: {
        clean_price_pct: 94.20,
        ytm: 0.185,
        g_spread_bps: 210,
        g_curve_yield: 0.15
      },
      risk_indicators: {
        duration: 1.15,
        convexity: 1.42,
        dv01: 1240
      },
      ratings: {
        issue: [{ agency: 'Expert RA', rating: 'ruAAA', date: '2025-11-15' }],
        issuer: [{ agency: 'AKRA', rating: 'AAA(RU)', outlook: 'Стабильный', date: '2025-09-10' }]
      }
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

  if (priceHistoryRef.value?.getContext('2d')) {
    priceHistoryChart = new Chart(priceHistoryRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Price',
          data: [92, 92.5, 93.1, 93.8, 94.1, 94.2],
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
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } } 
          }
        }
      }
    } as any)
  }

  if (yieldDynamicsRef.value?.getContext('2d')) {
    yieldDynamicsChart = new Chart(yieldDynamicsRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [
          {
            label: 'YTM',
            data: [18.95, 19.1, 19.2, 19.8, 20.2, 21.5],
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.08)',
            fill: true,
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
          legend: { display: false },
          filler: { propagate: true }
        },
        scales: {
          y: { 
            grid: { color: 'rgba(255,255,255,0.05)' }, 
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
}

const onChangeIsin = () => {
  if (localIsin.value?.trim()) {
    router.push({ params: { isin: localIsin.value } })
    fetchReport(localIsin.value)
  }
}

const formatNumber = (v: any) => v ? new Intl.NumberFormat('ru-RU').format(v) : '—'
const formatDate = (v: any) => v || '—'

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
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: linear-gradient(135deg, #02040a 0%, #0f1219 25%, #1a1d26 50%, #0f1219 75%, #02040a 100%);
}

.page-container::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  background: 
    radial-gradient(600px at 20% 50%, rgba(59, 130, 246, 0.15) 0%, transparent 80%),
    radial-gradient(600px at 80% 80%, rgba(139, 92, 246, 0.12) 0%, transparent 80%),
    radial-gradient(600px at 50% 0%, rgba(168, 85, 247, 0.08) 0%, transparent 80%);
  animation: gradientShift 15s ease-in-out infinite;
}

.page-container::after {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}

@keyframes gradientShift {
  0%, 100% {
    background: 
      radial-gradient(600px at 20% 50%, rgba(59, 130, 246, 0.15) 0%, transparent 80%),
      radial-gradient(600px at 80% 80%, rgba(139, 92, 246, 0.12) 0%, transparent 80%),
      radial-gradient(600px at 50% 0%, rgba(168, 85, 247, 0.08) 0%, transparent 80%);
  }
  50% {
    background: 
      radial-gradient(600px at 30% 40%, rgba(56, 189, 248, 0.2) 0%, transparent 80%),
      radial-gradient(600px at 70% 70%, rgba(147, 51, 234, 0.15) 0%, transparent 80%),
      radial-gradient(600px at 50% 20%, rgba(59, 130, 246, 0.1) 0%, transparent 80%);
  }
}

.glass-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px) saturate(160%);
  -webkit-backdrop-filter: blur(30px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.4);
  color: rgba(255, 255, 255, 0.9);
  position: relative;
  z-index: 2;
}

.glass-card:hover {
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
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
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
}

/* ============================================
   HEADER & INPUTS
   ============================================ */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  position: relative;
  z-index: 2;
}

.header-left { flex: 1; }
.section-title { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; }
.section-subtitle { font-size: 13px; color: rgba(255, 255, 255, 0.5); margin: 4px 0 0 0; }
.header-actions { display: flex; gap: 12px; }

.search-input { flex: 1; background: transparent; border: none; color: #fff; font-size: 13px; outline: none; padding: 4px; font-family: 'SF Mono', monospace; }
.search-input::placeholder { color: rgba(255, 255, 255, 0.2); }

.btn-search { background: transparent; border: none; color: #3b82f6; cursor: pointer; font-size: 14px; }
.btn-search:hover:not(:disabled) { color: #60a5fa; }
.btn-search:disabled { opacity: 0.5; cursor: not-allowed; }
.lbl-mini { font-size: 10px; color: rgba(255,255,255,0.5); font-weight: 600; text-transform: uppercase; }

/* ============================================
   GRID & CONTENT
   ============================================ */
.report-content { display: flex; flex-direction: column; gap: 20px; position: relative; z-index: 2; }
.state-section { display: flex; justify-content: center; align-items: center; min-height: 300px; position: relative; z-index: 2; }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.full-width { grid-column: 1 / -1; }

.card-header h3 { font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.6); text-transform: uppercase; margin: 0 0 16px 0; letter-spacing: 0.05em; }

/* ============================================
   TABLES & METRICS
   ============================================ */
.info-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.info-table td { padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); color: rgba(255,255,255,0.9); }
.info-table tr:last-child td { border-bottom: none; }
.info-table td:first-child { color: rgba(255,255,255,0.5); width: 40%; font-weight: 500; }
.info-table td:last-child { text-align: right; font-weight: 500; }

.metric-list { display: flex; flex-direction: column; gap: 8px; }
.metric { display: flex; justify-content: space-between; font-size: 12px; padding-bottom: 6px; border-bottom: 1px dashed rgba(107, 114, 128, 0.1); }
.metric:last-child { border-bottom: none; }
.metric > span:first-child { color: rgba(255, 255, 255, 0.5); font-weight: 500; }
.val { color: #fff; font-weight: 600; }

.ratings-list { display: flex; flex-direction: column; gap: 6px; }
.rating-item { display: flex; justify-content: space-between; font-size: 12px; gap: 8px; padding: 8px; background: rgba(255,255,255,0.02); border-radius: 6px; }
.rating-info { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; }
.agency { color: rgba(255,255,255,0.4); font-size: 10px; font-weight: 500; }
.grade { font-weight: 700; color: #fff; }
.outlook { font-size: 10px; color: rgba(255, 255, 255, 0.4); }
.date { font-size: 10px; color: rgba(255, 255, 255, 0.3); }

/* ============================================
   CHARTS & UTILS
   ============================================ */
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.chart-container { position: relative; width: 100%; height: 360px; background: rgba(15, 23, 42, 0.4); border-radius: 12px; padding: 12px; border: 1px solid rgba(107, 114, 128, 0.08); }
.chart-container.tall { height: 480px; }
.chart-container canvas { width: 100% !important; height: 100% !important; }

.btn-export { background: transparent; border: 1px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.6); padding: 4px 8px; border-radius: 4px; font-size: 11px; cursor: pointer; transition: all 0.2s; }
.btn-export:hover { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.2); color: #fff; }

.mono { font-family: 'SF Mono', monospace; }
.accent { color: #38bdf8; font-weight: 600; }
.text-accent { color: #38bdf8; font-weight: 600; }
.muted { color: rgba(255, 255, 255, 0.4); margin: 0; font-size: 12px; }
.spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(56, 189, 248, 0.3); border-top-color: #38bdf8; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1400px) { .grid-3 { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 1024px) {
  .section-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .header-actions { width: 100%; }
  .glass-pill { width: 100%; }
  .search-input { flex: 1; }
  .grid-2, .grid-3 { grid-template-columns: 1fr; }
}
@media (max-width: 768px) { 
  .page-container { padding: 16px; } 
  .section-title { font-size: 24px; }
  .chart-container { height: 300px; }
  .chart-container.tall { height: 400px; }
  .rating-item, .metric { flex-direction: column; align-items: flex-start; gap: 4px; }
  .val, .metric-value { text-align: left; }
}
</style>