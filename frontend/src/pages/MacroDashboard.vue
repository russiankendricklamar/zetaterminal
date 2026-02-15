<!-- src/pages/MacroDashboard.vue — Macro & Economic Data Dashboard -->
<template>
  <div class="page-container">
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Макроэкономика</h1>
        <p class="section-subtitle">FRED, ЦБ РФ, ЕЦБ, SEC EDGAR, OpenFIGI</p>
      </div>
      <div class="header-actions">
        <button class="btn-glass" @click="refreshAll" :disabled="loading">
          {{ loading ? 'Загрузка...' : 'Обновить' }}
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs-navigation">
      <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id" class="tab-item" :class="{ active: activeTab === tab.id }">
        <span class="tab-label">{{ tab.name }}</span>
      </button>
    </div>

    <div class="macro-grid">
      <!-- TAB: CBR -->
      <transition name="fade" mode="out-in">
      <div v-show="activeTab === 'cbr'" class="grid-content">

        <!-- CBR Key Rate -->
        <div class="glass-panel">
          <h3 class="block-title">Ключевая ставка ЦБ РФ</h3>
          <div v-if="cbrKeyRate" class="key-rate-display">
            <span class="rate-value font-mono">{{ cbrKeyRate.current_rate }}%</span>
          </div>
          <div v-if="cbrKeyRate && cbrKeyRate.history.length" class="chart-container">
            <canvas ref="keyRateChartRef"></canvas>
          </div>
          <p v-if="!cbrKeyRate && !loading" class="text-muted">Нажмите «Обновить» для загрузки данных</p>
        </div>

        <!-- CBR FX Rates -->
        <div class="glass-panel">
          <h3 class="block-title">Курсы ЦБ РФ</h3>
          <div v-if="cbrRates && cbrRates.rates.length" class="rates-table-wrap">
            <table class="data-table">
              <thead>
                <tr><th>Код</th><th>Валюта</th><th>Номинал</th><th>Курс (₽)</th></tr>
              </thead>
              <tbody>
                <tr v-for="r in cbrRatesFiltered" :key="r.char_code">
                  <td class="font-mono">{{ r.char_code }}</td>
                  <td>{{ r.name }}</td>
                  <td class="font-mono text-right">{{ r.nominal }}</td>
                  <td class="font-mono text-right">{{ r.value.toFixed(4) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-if="!cbrRates && !loading" class="text-muted">Нет данных</p>
        </div>
      </div>
      </transition>

      <!-- TAB: ECB -->
      <transition name="fade" mode="out-in">
      <div v-show="activeTab === 'ecb'" class="grid-content">
        <div class="glass-panel">
          <h3 class="block-title">Курсы ЕЦБ (Frankfurter)</h3>
          <div class="control-row mb-4">
            <label>Базовая валюта</label>
            <select v-model="ecbBase" class="glass-select" @change="loadEcbRates">
              <option value="EUR">EUR</option>
              <option value="USD">USD</option>
              <option value="GBP">GBP</option>
              <option value="RUB">RUB</option>
            </select>
          </div>
          <div v-if="ecbRates" class="rates-table-wrap">
            <table class="data-table">
              <thead>
                <tr><th>Валюта</th><th>Курс</th></tr>
              </thead>
              <tbody>
                <tr v-for="(rate, code) in ecbRates.rates" :key="code">
                  <td class="font-mono">{{ code }}</td>
                  <td class="font-mono text-right">{{ Number(rate).toFixed(4) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-if="!ecbRates && !loading" class="text-muted">Нажмите «Обновить»</p>
        </div>
      </div>
      </transition>

      <!-- TAB: FRED -->
      <transition name="fade" mode="out-in">
      <div v-show="activeTab === 'fred'" class="grid-content">
        <div class="glass-panel">
          <h3 class="block-title">Индикаторы FRED</h3>
          <div class="fred-controls">
            <div class="control-row mb-4">
              <label>Series ID</label>
              <div class="input-group">
                <input v-model="fredSeriesId" class="glass-input" placeholder="GDP, CPIAUCSL, UNRATE, DFF, M2SL..." />
                <button class="btn-glass xs" @click="loadFredSeries">Загрузить</button>
              </div>
            </div>
            <div class="quick-buttons">
              <button v-for="s in fredQuickSeries" :key="s.id" class="btn-glass xs" @click="fredSeriesId = s.id; loadFredSeries()">{{ s.label }}</button>
            </div>
          </div>
          <div v-if="fredData" class="chart-container">
            <canvas ref="fredChartRef"></canvas>
          </div>
          <div v-if="fredData" class="fred-info font-mono text-muted mt-2">
            {{ fredData.series_id }} — {{ fredData.count }} obs.
          </div>
        </div>

        <!-- FRED Search -->
        <div class="glass-panel">
          <h3 class="block-title">Поиск серий FRED</h3>
          <div class="control-row mb-4">
            <input v-model="fredSearchQuery" class="glass-input full" placeholder="Search: inflation, unemployment, GDP..." @keyup.enter="loadFredSearch" />
            <button class="btn-glass xs" @click="loadFredSearch">Поиск</button>
          </div>
          <div v-if="fredSearchResults && fredSearchResults.series.length" class="rates-table-wrap">
            <table class="data-table">
              <thead>
                <tr><th>ID</th><th>Название</th><th>Частота</th><th>Единицы</th><th></th></tr>
              </thead>
              <tbody>
                <tr v-for="s in fredSearchResults.series" :key="s.id">
                  <td class="font-mono">{{ s.id }}</td>
                  <td>{{ s.title }}</td>
                  <td class="font-mono">{{ s.frequency }}</td>
                  <td class="font-mono">{{ s.units }}</td>
                  <td><button class="btn-glass xs" @click="fredSeriesId = s.id; loadFredSeries()">→</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      </transition>

      <!-- TAB: SEC -->
      <transition name="fade" mode="out-in">
      <div v-show="activeTab === 'sec'" class="grid-content">
        <div class="glass-panel">
          <h3 class="block-title">SEC EDGAR — Поиск компании</h3>
          <div class="control-row mb-4">
            <label>CIK Number</label>
            <div class="input-group">
              <input v-model="secCik" class="glass-input" placeholder="0000320193 (Apple)" />
              <button class="btn-glass xs" @click="loadSecFilings">Загрузить</button>
            </div>
          </div>
          <div v-if="secFilings" class="sec-info mb-4">
            <p class="font-mono"><strong>{{ secFilings.name }}</strong> (CIK: {{ secFilings.cik }})</p>
            <p class="font-mono text-muted">Tickers: {{ secFilings.tickers.join(', ') }} | SIC: {{ secFilings.sic_description }}</p>
          </div>
          <div v-if="secFilings && secFilings.filings.length" class="rates-table-wrap">
            <table class="data-table">
              <thead>
                <tr><th>Form</th><th>Date</th><th>Description</th></tr>
              </thead>
              <tbody>
                <tr v-for="(f, idx) in secFilings.filings.slice(0, 30)" :key="idx">
                  <td class="font-mono">{{ f.form }}</td>
                  <td class="font-mono">{{ f.filing_date }}</td>
                  <td>{{ f.description }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- OpenFIGI -->
        <div class="glass-panel">
          <h3 class="block-title">OpenFIGI — Маппинг идентификаторов</h3>
          <div class="control-row mb-4">
            <label>ISIN</label>
            <div class="input-group">
              <input v-model="figiIsin" class="glass-input" placeholder="US0378331005" />
              <button class="btn-glass xs" @click="loadFigiMap">Map</button>
            </div>
          </div>
          <div v-if="figiResults && figiResults.length" class="rates-table-wrap">
            <div v-for="(r, idx) in figiResults" :key="idx" class="figi-result mb-2">
              <div v-if="r.data" v-for="d in r.data" :key="d.figi" class="font-mono text-sm">
                <strong>{{ d.name }}</strong> — {{ d.ticker }} ({{ d.exchCode }}) — FIGI: {{ d.figi }}
              </div>
              <div v-if="r.error" class="text-red font-mono">{{ r.error }}</div>
            </div>
          </div>
        </div>
      </div>
      </transition>

    </div>

    <!-- Error -->
    <div v-if="error" class="error-banner">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { Chart, registerables } from 'chart.js'
import {
  getCbrRates, getCbrKeyRate, getEcbLatestRates,
  getFredSeries, searchFredSeries,
  getSecFilings, mapOpenFigi,
  type CbrDailyRates, type CbrKeyRate as CbrKeyRateType, type EcbRates as EcbRatesType,
  type FredSeriesData, type FredSearchResult,
  type SecCompanyFilings, type OpenFigiResult
} from '@/services/macroDataService'

Chart.register(...registerables)

const activeTab = ref('cbr')
const loading = ref(false)
const error = ref('')

const tabs = [
  { id: 'cbr', name: 'ЦБ РФ' },
  { id: 'ecb', name: 'ЕЦБ' },
  { id: 'fred', name: 'FRED' },
  { id: 'sec', name: 'SEC / FIGI' },
]

// ─── CBR ─────────────────────────────────────────────────────────────────────
const cbrRates = ref<CbrDailyRates | null>(null)
const cbrKeyRate = ref<CbrKeyRateType | null>(null)
const keyRateChartRef = ref<HTMLCanvasElement | null>(null)
let keyRateChart: Chart | null = null

const cbrRatesFiltered = ref<CbrDailyRates['rates']>([])

const POPULAR_CURRENCIES = ['USD', 'EUR', 'GBP', 'CNY', 'JPY', 'CHF', 'TRY', 'KZT', 'BYN', 'AED']

async function loadCbrData() {
  try {
    const [rates, keyRate] = await Promise.all([getCbrRates(), getCbrKeyRate()])
    cbrRates.value = rates
    cbrKeyRate.value = keyRate
    cbrRatesFiltered.value = rates.rates.filter(r => POPULAR_CURRENCIES.includes(r.char_code))
    await nextTick()
    renderKeyRateChart()
  } catch (e: any) {
    error.value = `CBR: ${e.message}`
  }
}

function renderKeyRateChart() {
  if (!keyRateChartRef.value || !cbrKeyRate.value) return
  if (keyRateChart) keyRateChart.destroy()

  const hist = [...cbrKeyRate.value.history].reverse().slice(-60)
  keyRateChart = new Chart(keyRateChartRef.value, {
    type: 'line',
    data: {
      labels: hist.map(h => h.date.slice(0, 10)),
      datasets: [{
        label: 'Ключевая ставка (%)',
        data: hist.map(h => h.rate),
        borderColor: '#DC2626',
        backgroundColor: 'rgba(220,38,38,0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: 2,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#aaa' } } },
      scales: {
        x: { ticks: { color: '#666', maxTicksLimit: 12 }, grid: { color: '#1a1a1a' } },
        y: { ticks: { color: '#666' }, grid: { color: '#1a1a1a' } },
      },
    },
  })
}

// ─── ECB ─────────────────────────────────────────────────────────────────────
const ecbBase = ref('EUR')
const ecbRates = ref<EcbRatesType | null>(null)

async function loadEcbRates() {
  try {
    ecbRates.value = await getEcbLatestRates(ecbBase.value)
  } catch (e: any) {
    error.value = `ECB: ${e.message}`
  }
}

// ─── FRED ────────────────────────────────────────────────────────────────────
const fredSeriesId = ref('CPIAUCSL')
const fredData = ref<FredSeriesData | null>(null)
const fredChartRef = ref<HTMLCanvasElement | null>(null)
let fredChart: Chart | null = null

const fredSearchQuery = ref('')
const fredSearchResults = ref<FredSearchResult | null>(null)

const fredQuickSeries = [
  { id: 'GDP', label: 'GDP' },
  { id: 'CPIAUCSL', label: 'CPI' },
  { id: 'UNRATE', label: 'Безработица' },
  { id: 'DFF', label: 'Fed Funds Rate' },
  { id: 'M2SL', label: 'M2' },
  { id: 'DGS10', label: 'US 10Y' },
]

async function loadFredSeries() {
  if (!fredSeriesId.value) return
  try {
    fredData.value = await getFredSeries(fredSeriesId.value, 200, 'asc')
    await nextTick()
    renderFredChart()
  } catch (e: any) {
    error.value = `FRED: ${e.message}`
  }
}

function renderFredChart() {
  if (!fredChartRef.value || !fredData.value) return
  if (fredChart) fredChart.destroy()

  const obs = fredData.value.observations.filter(o => o.value !== null)
  fredChart = new Chart(fredChartRef.value, {
    type: 'line',
    data: {
      labels: obs.map(o => o.date),
      datasets: [{
        label: fredData.value.series_id,
        data: obs.map(o => o.value as number),
        borderColor: '#3B82F6',
        backgroundColor: 'rgba(59,130,246,0.1)',
        fill: true,
        tension: 0.2,
        pointRadius: 0,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#aaa' } } },
      scales: {
        x: { ticks: { color: '#666', maxTicksLimit: 12 }, grid: { color: '#1a1a1a' } },
        y: { ticks: { color: '#666' }, grid: { color: '#1a1a1a' } },
      },
    },
  })
}

async function loadFredSearch() {
  if (!fredSearchQuery.value) return
  try {
    fredSearchResults.value = await searchFredSeries(fredSearchQuery.value)
  } catch (e: any) {
    error.value = `FRED search: ${e.message}`
  }
}

// ─── SEC EDGAR ───────────────────────────────────────────────────────────────
const secCik = ref('')
const secFilings = ref<SecCompanyFilings | null>(null)

async function loadSecFilings() {
  if (!secCik.value) return
  try {
    secFilings.value = await getSecFilings(secCik.value)
  } catch (e: any) {
    error.value = `SEC: ${e.message}`
  }
}

// ─── OpenFIGI ────────────────────────────────────────────────────────────────
const figiIsin = ref('')
const figiResults = ref<OpenFigiResult[]>([])

async function loadFigiMap() {
  if (!figiIsin.value) return
  try {
    figiResults.value = await mapOpenFigi([{ idType: 'ID_ISIN', idValue: figiIsin.value }])
  } catch (e: any) {
    error.value = `FIGI: ${e.message}`
  }
}

// ─── Global ──────────────────────────────────────────────────────────────────
async function refreshAll() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([loadCbrData(), loadEcbRates()])
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshAll()
})
</script>

<style scoped>
.page-container { padding: 24px 32px; max-width: 1400px; }
.section-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.section-title { font-family: 'Oswald', sans-serif; font-size: 28px; font-weight: 700; text-transform: uppercase; color: #f5f5f5; letter-spacing: 2px; }
.section-subtitle { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #666; margin-top: 4px; text-transform: uppercase; }

.tabs-navigation { display: flex; gap: 2px; margin-bottom: 24px; border-bottom: 1px solid #1a1a1a; }
.tab-item { padding: 10px 20px; background: transparent; border: none; color: #666; font-family: 'JetBrains Mono', monospace; font-size: 12px; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.2s; text-transform: uppercase; }
.tab-item.active { color: #DC2626; border-bottom-color: #DC2626; }
.tab-item:hover { color: #f5f5f5; }

.macro-grid { display: flex; flex-direction: column; gap: 20px; }
.grid-content { display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; }
.glass-panel { background: rgba(255,255,255,0.02); border: 1px solid #1a1a1a; padding: 20px; }
.block-title { font-family: 'Oswald', sans-serif; font-size: 14px; font-weight: 600; text-transform: uppercase; color: #f5f5f5; letter-spacing: 1px; margin-bottom: 16px; }

.key-rate-display { text-align: center; margin-bottom: 16px; }
.rate-value { font-size: 48px; font-weight: 700; color: #DC2626; }

.chart-container { height: 250px; position: relative; }
.chart-container canvas { width: 100% !important; height: 100% !important; }

.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { text-align: left; padding: 8px; color: #666; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; border-bottom: 1px solid #1a1a1a; }
.data-table td { padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.03); color: #ccc; }
.data-table tr:hover td { background: rgba(255,255,255,0.02); }
.text-right { text-align: right; }
.text-muted { color: #555; font-size: 12px; }
.text-red { color: #DC2626; }

.control-row { display: flex; align-items: center; gap: 12px; }
.control-row label { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #888; white-space: nowrap; }
.glass-input { background: rgba(255,255,255,0.03); border: 1px solid #333; padding: 8px 12px; color: #f5f5f5; font-family: 'JetBrains Mono', monospace; font-size: 13px; outline: none; }
.glass-input.full { width: 100%; }
.glass-input:focus { border-color: #DC2626; }
.glass-select { background: rgba(255,255,255,0.03); border: 1px solid #333; padding: 8px 12px; color: #f5f5f5; font-family: 'JetBrains Mono', monospace; font-size: 13px; }
.input-group { display: flex; gap: 8px; flex: 1; }
.input-group .glass-input { flex: 1; }
.quick-buttons { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }

.btn-glass { padding: 8px 16px; background: rgba(255,255,255,0.03); border: 1px solid #333; color: #f5f5f5; font-family: 'JetBrains Mono', monospace; font-size: 12px; cursor: pointer; transition: all 0.2s; text-transform: uppercase; }
.btn-glass:hover { border-color: #DC2626; color: #DC2626; }
.btn-glass:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-glass.xs { padding: 4px 10px; font-size: 11px; }

.error-banner { background: rgba(220,38,38,0.1); border: 1px solid #DC2626; padding: 12px; margin-top: 16px; color: #DC2626; font-family: 'JetBrains Mono', monospace; font-size: 12px; }

.rates-table-wrap { max-height: 400px; overflow-y: auto; }
.mb-2 { margin-bottom: 8px; }
.mb-4 { margin-bottom: 16px; }
.mt-2 { margin-top: 8px; }
.font-mono { font-family: 'JetBrains Mono', monospace; }
.text-sm { font-size: 12px; }

.sec-info { padding: 12px; background: rgba(255,255,255,0.02); border: 1px solid #1a1a1a; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
