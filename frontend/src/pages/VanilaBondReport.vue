<!-- src/pages/VanillaBondReport.vue -->
<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Vanilla Bond Report</h1>
        <p class="section-subtitle">Паспорт выпуска и аналитика по ISIN</p>
      </div>
      
      <div class="header-actions">
        <div class="glass-pill search-pill">
          <span class="lbl-mini">Поиск ISIN</span>
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
        <div class="spinner-large"></div>
        <span>Загрузка данных...</span>
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
      
      <!-- Block 1: Main Info -->
      <div class="grid-2">
        <div class="glass-card panel">
          <div class="panel-header"><h3>Общие сведения</h3></div>
          <table class="info-table">
            <tr><td>Эмитент</td><td>{{ report.issuer }}</td></tr>
            <tr><td>ISIN</td><td class="mono">{{ report.isin }}</td></tr>
            <tr><td>Страна</td><td>{{ report.risk_country || '—' }}</td></tr>
            <tr><td>Сектор</td><td>{{ report.sector || '—' }}</td></tr>
            <tr><td>Отрасль</td><td>{{ report.industry || '—' }}</td></tr>
            <tr><td>Объём выпуска</td><td class="mono">{{ formatNumber(report.outstanding_amount) }}</td></tr>
          </table>
        </div>

        <div class="glass-card panel">
          <div class="panel-header"><h3>Параметры выпуска</h3></div>
          <table class="info-table">
            <tr><td>Дата начала</td><td class="mono">{{ formatDate(report.issue_info?.issue_date) }}</td></tr>
            <tr><td>Дата погашения</td><td class="mono">{{ formatDate(report.issue_info?.maturity_date) }}</td></tr>
            <tr><td>Ставка купона</td><td><span v-if="report.issue_info?.coupon_rate" class="text-green">{{ (report.issue_info.coupon_rate * 100).toFixed(2) }}%</span><span v-else>—</span></td></tr>
            <tr><td>Купонов в год</td><td class="mono">{{ report.issue_info?.coupon_per_year ?? '—' }}</td></tr>
          </table>
        </div>
      </div>

      <!-- Block 2: Ratings -->
      <div class="grid-3">
        <div class="glass-card panel">
          <div class="panel-header"><h3>Рейтинг эмиссии</h3></div>
          <div v-if="report.ratings?.issue?.length" class="rating-list">
            <div v-for="(r, idx) in report.ratings.issue" :key="idx" class="rating-item">
              <span class="agency">{{ r.agency }}</span>
              <span class="grade">{{ r.rating }}</span>
              <span class="date mono">{{ formatDate(r.date) }}</span>
            </div>
          </div>
          <p v-else class="muted">Нет данных</p>
        </div>

        <div class="glass-card panel">
          <div class="panel-header"><h3>Рейтинг эмитента</h3></div>
          <div v-if="report.ratings?.issuer?.length" class="rating-list">
            <div v-for="(r, idx) in report.ratings.issuer" :key="idx" class="rating-item">
              <span class="agency">{{ r.agency }}</span>
              <div>
                <span class="grade">{{ r.rating }}</span>
                <span class="outlook" v-if="r.outlook"> ({{ r.outlook }})</span>
              </div>
              <span class="date mono">{{ formatDate(r.date) }}</span>
            </div>
          </div>
          <p v-else class="muted">Нет данных</p>
        </div>

        <div class="glass-card panel">
          <div class="panel-header"><h3>Рейтинг гаранта</h3></div>
          <div v-if="report.ratings?.guarantor?.length" class="rating-list">
            <div v-for="(r, idx) in report.ratings.guarantor" :key="idx" class="rating-item">
              <span class="agency">{{ r.agency }}</span>
              <span class="grade">{{ r.rating }}</span>
              <span class="date mono">{{ formatDate(r.date) }}</span>
            </div>
          </div>
          <p v-else class="muted">Нет данных</p>
        </div>
      </div>

      <!-- Block 3: Market & Pricing -->
      <div class="grid-3">
        <div class="glass-card panel">
          <div class="metric-header-wrap">
            <div class="panel-header"><h3>Активность рынка</h3></div>
            <span class="badge-status" :class="isMarketActive ? 'active' : 'inactive'">
              <span class="indicator-dot"></span>
              {{ isMarketActive ? 'Активный' : 'Неактивный' }}
            </span>
          </div>
          <div class="metric-stack">
            <div class="metric"><span>Торговых дней</span><span class="val badge-sm">{{ report.market_activity?.trading_days ?? 0 }}</span></div>
            <div class="metric"><span>Сделок</span><span class="val badge-sm">{{ report.market_activity?.trades ?? 0 }}</span></div>
            <div class="metric"><span>Оборот/Выпуск</span><span class="val badge-sm">{{ (report.market_activity?.turnover_to_outstanding * 100).toFixed(2) }}%</span></div>
            <div class="metric"><span>Торги (30д)</span><span class="val badge-xs" :class="report.market_activity?.traded_last_30d ? 'ok' : 'bad'">{{ report.market_activity?.traded_last_30d ? 'ДА' : 'НЕТ' }}</span></div>
          </div>
        </div>

        <div class="glass-card panel">
          <div class="panel-header"><h3>Котировка и доходность</h3></div>
          <div class="metric-stack">
            <div class="metric"><span>Чистая цена</span><span class="val text-accent">{{ report.pricing?.clean_price_pct?.toFixed(2) }}%</span></div>
            <div class="metric"><span>YTM (доходность)</span><span class="val text-accent">{{ (report.pricing?.ytm * 100).toFixed(2) }}%</span></div>
            <div class="metric"><span>G-spread</span><span class="val mono">{{ report.pricing?.g_spread_bps }} bps</span></div>
            <div class="metric"><span>G-curve</span><span class="val mono">{{ (report.pricing?.g_curve_yield * 100).toFixed(2) }}%</span></div>
          </div>
        </div>

        <div class="glass-card panel">
          <div class="panel-header"><h3>Риск-метрики</h3></div>
          <div class="metric-stack">
            <div class="metric"><span>Мод. дюрация</span><span class="val badge-sm">{{ report.risk_indicators?.duration?.toFixed(2) }}</span></div>
            <div class="metric"><span>Выпуклость</span><span class="val badge-sm">{{ report.risk_indicators?.convexity?.toFixed(2) }}</span></div>
            <div class="metric"><span>DV01</span><span class="val badge-sm">{{ formatNumber(report.risk_indicators?.dv01) }}</span></div>
          </div>
          <div v-if="report.warnings?.length" class="warnings-box mt-3">
            <div v-for="(w, idx) in report.warnings" :key="idx" class="warn-item">⚠ {{ w }}</div>
          </div>
          <div v-else class="success-box mt-3">✓ Ошибок нет</div>
        </div>
      </div>

      <!-- Block 4: Charts -->
      <div class="glass-card chart-card full-width mt-4">
        <div class="chart-header">
          <h3>Динамика цены</h3>
          <button class="btn-export" @click="exportChart('price')">💾 PNG</button>
        </div>
        <div class="chart-box tall">
          <canvas ref="priceHistoryRef"></canvas>
        </div>
      </div>

      <div class="glass-card chart-card full-width mt-4">
        <div class="chart-header">
          <h3>Динамика доходности (YTM, G-curve, G-spread)</h3>
          <button class="btn-export" @click="exportChart('yield')">💾 PNG</button>
        </div>
        <div class="chart-box tall">
          <canvas ref="yieldDynamicsRef"></canvas>
        </div>
      </div>

      <!-- Block 5: Benchmark Comparison -->
      <div class="glass-card panel full-width mt-4">
        <div class="panel-header"><h3>Сравнение с индексами MOEX</h3></div>
        <p class="subtitle">Позиционирование доходности относительно бенчмарков</p>
        
        <div class="benchmark-container">
          <div class="yield-scale">
            <span>12%</span><span>16%</span><span>20%</span><span>24%</span>
          </div>
          <div class="yield-track">
            <!-- Benchmarks -->
            <div v-for="(val, key) in indexYields" :key="key" v-show="key !== 'our'"
                 class="b-point" :style="{ left: getBenchmarkPosition(val) }"
                 @mouseenter="hoveredBench = key" @mouseleave="hoveredBench = null">
              <div class="b-dot"></div>
              <div class="b-tooltip" v-if="hoveredBench === key">{{ key.toUpperCase() }}: {{ val }}%</div>
            </div>
            <!-- Main Bond -->
            <div class="b-point our" :style="{ left: getBenchmarkPosition(indexYields.our) }"
                 @mouseenter="hoveredBench = 'our'" @mouseleave="hoveredBench = null">
              <div class="b-dot-main pulse"></div>
              <div class="b-tooltip" v-if="hoveredBench === 'our'">Облигация: {{ indexYields.our }}%</div>
            </div>
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

interface BondReport {
  isin: string
  issuer: string
  risk_country?: string
  sector?: string
  industry?: string
  outstanding_amount?: number
  issue_info?: {
    issue_date?: string
    maturity_date?: string
    coupon_rate?: number
    coupon_per_year?: number
  }
  market_activity?: {
    trading_days?: number
    trades?: number
    turnover_to_outstanding?: number
    traded_last_30d?: boolean
  }
  pricing?: {
    clean_price_pct?: number
    ytm?: number
    g_spread_bps?: number
    g_curve_yield?: number
  }
  risk_indicators?: {
    duration?: number
    convexity?: number
    dv01?: number
  }
  ratings?: {
    issue?: Array<{ agency: string; rating: string; date?: string }>
    issuer?: Array<{ agency: string; rating: string; outlook?: string; date?: string }>
    guarantor?: Array<{ agency: string; rating: string; date?: string }>
  }
  warnings?: string[]
}

const route = useRoute()
const router = useRouter()
const isin = computed(() => (route.params.isin as string) || '')
const localIsin = ref(isin.value)
const loading = ref(false)
const error = ref<string | null>(null)
const report = ref<BondReport | null>(null)
const indexYields = ref({
  gov: 13.89,
  aaa: 15.69,
  aa: 16.89,
  a: 20.54,
  bbb: 22.68,
  our: 19.91
})
const hoveredBench = ref<string | null>(null)

const priceHistoryRef = ref<HTMLCanvasElement | null>(null)
const yieldDynamicsRef = ref<HTMLCanvasElement | null>(null)
let priceChart: Chart | null = null
let yieldChart: Chart | null = null

const fetchReport = async (targetIsin: string) => {
  if (!targetIsin) return
  loading.value = true
  error.value = null
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
      },
      warnings: []
    }
    setTimeout(() => initCharts(), 100)
  } catch (e) {
    error.value = 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

const initCharts = () => {
  if (priceChart) priceChart.destroy()
  if (yieldChart) yieldChart.destroy()

  if (priceHistoryRef.value) {
    priceChart = new Chart(priceHistoryRef.value, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Price',
          data: [92, 92.5, 93.1, 93.8, 94.1, 94.2],
          borderColor: '#fff',
          backgroundColor: 'rgba(255,255,255,0.05)',
          fill: true,
          tension: 0.4,
          pointRadius: 0
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

  if (yieldDynamicsRef.value) {
    yieldChart = new Chart(yieldDynamicsRef.value, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [
          {
            label: 'YTM',
            data: [18.95, 19.1, 19.2, 19.8, 20.2, 21.5],
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.05)',
            fill: true,
            tension: 0.4,
            pointRadius: 0
          },
          {
            label: 'G-spread',
            data: [320, 340, 360, 380, 400, 450],
            borderColor: '#f97316',
            backgroundColor: 'transparent',
            tension: 0.4,
            pointRadius: 0,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { display: false } },
        scales: {
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(255,255,255,0.3)' } },
          y1: { position: 'right', grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
          x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } }
        }
      }
    } as any)
  }
}

const getBenchmarkPosition = (val: number) => {
  const min = 12, max = 24
  const pos = ((val - min) / (max - min)) * 100
  return `${Math.max(0, Math.min(100, pos))}%`
}

const onChangeIsin = () => {
  if (localIsin.value?.trim()) {
    router.push({ params: { isin: localIsin.value } })
    fetchReport(localIsin.value)
  }
}

const formatNumber = (v: any) => v ? new Intl.NumberFormat('ru-RU').format(v) : '—'
const formatDate = (v: any) => v || '—'
const isMarketActive = computed(() => (report.value?.market_activity?.trades || 0) > 5)

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
  if (priceChart) priceChart.destroy()
  if (yieldChart) yieldChart.destroy()
})
</script>

<style scoped>
/* ============================================
   ROOT & BACKGROUND PHYSICS (MainLayout style)
   ============================================ */
.page-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 24px;
  
  /* ===== ЖИВОЙ ФОНОВЫЙ ГРАДИЕНТ ===== */
  background-color: #02040a;
  background-image: 
    radial-gradient(800px at 20% 50%, rgba(59, 130, 246, 0.15) 0%, transparent 80%),
    radial-gradient(700px at 80% 80%, rgba(139, 92, 246, 0.12) 0%, transparent 80%),
    radial-gradient(600px at 50% 0%, rgba(168, 85, 247, 0.08) 0%, transparent 80%);
  animation: bgShift 15s ease-in-out infinite;
}

/* ===== ШУМНАЯ ТЕКСТУРА СВЕРХУ ===== */
.page-container::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  opacity: 0.035;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}

@keyframes bgShift {
  0%, 100% {
    background-image: 
      radial-gradient(800px at 20% 50%, rgba(59, 130, 246, 0.15) 0%, transparent 80%),
      radial-gradient(700px at 80% 80%, rgba(139, 92, 246, 0.12) 0%, transparent 80%),
      radial-gradient(600px at 50% 0%, rgba(168, 85, 247, 0.08) 0%, transparent 80%);
  }
  50% {
    background-image: 
      radial-gradient(800px at 30% 40%, rgba(56, 189, 248, 0.2) 0%, transparent 80%),
      radial-gradient(700px at 70% 70%, rgba(147, 51, 234, 0.15) 0%, transparent 80%),
      radial-gradient(600px at 50% 20%, rgba(59, 130, 246, 0.1) 0%, transparent 80%);
  }
}

/* ============================================
   SCROLL
   ============================================ */
.custom-scroll {
  position: relative;
  z-index: 2;
  overflow-y: auto;
  padding: 24px 32px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

.custom-scroll::-webkit-scrollbar {
  width: 6px;
}

.custom-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 99px;
}

.custom-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* ============================================
   💎 GLASS CARD STYLES
   ============================================ */
.glass-card {
  background: rgba(30, 35, 45, 0.40);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  box-shadow: 
    0 20px 50px -10px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.25),
    inset 0 0 0 1px rgba(255, 255, 255, 0.05);
  transition: all 0.3s cubic-bezier(0.3, 0.7, 0.4, 1);
}

.glass-card:hover {
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 
    0 25px 60px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.3),
    inset 0 0 0 1px rgba(255, 255, 255, 0.1);
}

.glass-card.error {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
}

/* ============================================
   GLASS PILL (Search)
   ============================================ */
.glass-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  position: relative;
  z-index: 1;
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

.lbl-mini {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 600;
  text-transform: uppercase;
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

/* ============================================
   HEADER & TEXT
   ============================================ */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 4px;
  flex-shrink: 0;
  padding: 0 32px;
  position: relative;
  z-index: 2;
}

.header-left {
  flex: 1;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  letter-spacing: -0.01em;
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

.panel-header h3 {
  margin: 0 0 16px 0;
  font-size: 11px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 700;
  letter-spacing: 0.05em;
}

/* ============================================
   STATES
   ============================================ */
.state-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  position: relative;
  z-index: 2;
  padding: 0 32px;
}

.loading-state,
.error,
.empty-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.error {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
}

/* ============================================
   LAYOUTS & GRIDS
   ============================================ */
.report-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
  z-index: 2;
}

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.full-width {
  grid-column: 1 / -1;
}

.panel {
  padding: 24px;
}

/* ============================================
   PANEL & CARDS
   ============================================ */
.info-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.info-table td {
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.info-table td:first-child {
  color: rgba(255, 255, 255, 0.4);
}

.info-table td:last-child {
  text-align: right;
  font-weight: 600;
}

/* ============================================
   METRICS & VALUES
   ============================================ */
.metric-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric span:first-child {
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
}

.val {
  font-weight: 700;
  font-family: "SF Mono", monospace;
}

.badge-mini {
  background: rgba(59, 130, 246, 0.1);
  color: #60a5fa;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 700;
}

.badge-sm {
  background: rgba(59, 130, 246, 0.1);
  color: #60a5fa;
  padding: 4px 8px;
  border-radius: 6px;
}

.badge-xs {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.badge-xs.ok {
  background: rgba(74, 222, 128, 0.1);
  color: #4ade80;
}

.badge-xs.bad {
  background: rgba(248, 113, 113, 0.1);
  color: #f87171;
}

.text-accent {
  color: #38bdf8;
  font-weight: 700;
}

.text-green {
  color: #4ade80;
  font-weight: 700;
}

.mono {
  font-family: "SF Mono", monospace;
}

/* ============================================
   RATINGS & LISTS
   ============================================ */
.rating-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rating-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  align-items: center;
}

.agency {
  color: rgba(255, 255, 255, 0.4);
}

.grade {
  font-weight: 600;
  color: #fff;
}

.outlook {
  color: rgba(255, 255, 255, 0.4);
  font-size: 11px;
}

.date {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
}

.muted {
  color: rgba(255, 255, 255, 0.3);
  font-size: 12px;
  margin: 0;
}

/* ============================================
   STATUS INDICATORS
   ============================================ */
.badge-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 99px;
}

.badge-status.active {
  background: rgba(74, 222, 128, 0.1);
  color: #4ade80;
}

.badge-status.inactive {
  background: rgba(248, 113, 113, 0.1);
  color: #f87171;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 8px currentColor;
}

.indicator-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 8px currentColor;
}

.metric-header-wrap {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

/* ============================================
   CHARTS
   ============================================ */
.chart-card {
  padding: 24px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  margin: 0;
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.9);
}

.chart-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.btn-export {
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.2s;
}

.btn-export:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.chart-box {
  position: relative;
  height: 350px;
  width: 100%;
  margin-top: 10px;
}

.chart-box.tall {
  height: 450px;
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

/* ============================================
   BENCHMARK SECTION
   ============================================ */
.benchmark-container {
  margin-top: 20px;
}

.yield-scale {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 12px;
}

.yield-track {
  height: 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
  position: relative;
  margin-top: 12px;
}

.b-point {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  cursor: pointer;
}

.b-dot {
  width: 10px;
  height: 10px;
  background: #475569;
  border-radius: 50%;
}

.b-dot-main {
  width: 16px;
  height: 16px;
  background: #ef4444;
  border-radius: 50%;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.6);
}

.pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  50% {
    transform: scale(1.3);
    opacity: 0.7;
  }
}

.b-tooltip {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: #1e293b;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 10px;
  white-space: nowrap;
  border: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 10;
  pointer-events: none;
}

/* ============================================
   UTILITY CLASSES
   ============================================ */
.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subtitle {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  margin: 6px 0 0 0;
}

.mt-2 {
  margin-top: 8px;
}

.mt-3 {
  margin-top: 12px;
}

.mt-4 {
  margin-top: 20px;
}

.warnings {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.warn {
  font-size: 11px;
  color: #f97316;
}

.warn-item {
  font-size: 11px;
  color: #f97316;
}

.success {
  font-size: 11px;
  color: #4ade80;
}

.success-box {
  font-size: 11px;
  color: #4ade80;
}

.warnings-box {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* ============================================
   SPINNER & LOADING
   ============================================ */
.spinner-large {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
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

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .grid-2,
  .grid-3 {
    grid-template-columns: 1fr;
  }
  
  .page-container {
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .section-title {
    font-size: 24px;
  }
  
  .custom-scroll {
    padding: 16px;
  }
}
</style>
