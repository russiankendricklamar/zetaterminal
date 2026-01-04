<template>
  <div class="page-container">
    
    <!-- Hero / Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">КБД (Zero-Coupon Yield Curve)</h1>
        <p class="section-subtitle">Кривая бескупонных доходностей от MOEX ISS API</p>
      </div>
      <div class="header-actions">
        <!-- Date Picker -->
        <div class="glass-pill control-pill">
          <span class="lbl-mini">Дата:</span>
          <input
            v-model="params.date"
            type="date"
            class="date-input"
            :max="today"
          />
        </div>

        <!-- Refresh Button -->
        <button class="btn-glass primary" @click="loadZCYC" :disabled="loading">
          <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-if="!loading">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          <span v-else class="spinner-mini"></span>
          <span>{{ loading ? 'Загрузка...' : 'Загрузить' }}</span>
        </button>
      </div>
    </div>

    <!-- Quick ZCYC Summary (KPIs) -->
    <div class="kpi-cards-grid">
      <div class="glass-card kpi-card">
        <div class="kpi-label">Дата КБД</div>
        <div class="kpi-value">{{ formatDate(results.date) }}</div>
        <div class="kpi-sub">
          <span class="text-muted">Last update</span>
        </div>
      </div>
      <div class="glass-card kpi-card">
        <div class="kpi-label">Точек на кривой</div>
        <div class="kpi-value text-gradient-blue">{{ results.count }}</div>
        <div class="kpi-sub">
          <span class="text-muted">Data points</span>
        </div>
      </div>
      <div class="glass-card kpi-card">
        <div class="kpi-label">Минимальная ставка</div>
        <div class="kpi-value">{{ formatNumber(results.min_rate, 3) }}%</div>
        <div class="kpi-sub">
          <span class="text-muted">Min rate</span>
        </div>
      </div>
      <div class="glass-card kpi-card">
        <div class="kpi-label">Максимальная ставка</div>
        <div class="kpi-value text-gradient-green">{{ formatNumber(results.max_rate, 3) }}%</div>
        <div class="kpi-sub">
          <span class="text-muted">Max rate</span>
        </div>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="dashboard-grid">
      
      <!-- Left Column -->
      <div class="col-left">
        
        <!-- Period Search & Interpolation -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Поиск периода (интерполяция)</h3>
          </div>
          <div class="search-container">
            <div class="search-input-wrapper">
              <input
                v-model="periodSearch"
                type="number"
                step="0.01"
                class="search-input"
                placeholder="Введите срок (например 2.23)"
                @input="filterPeriods"
                @change="searchPeriodByInput"
                @keydown.enter="searchPeriodByInput"
              />
              <span class="search-unit">лет</span>
            </div>
            <div v-if="showSuggestions && filteredPeriods.length > 0" class="period-suggestions">
              <div
                v-for="(period, idx) in filteredPeriods.slice(0, 5)"
                :key="idx"
                class="suggestion-item"
                @click="selectPeriod(period)"
              >
                <span class="suggestion-term">{{ formatNumber(period.term, 4) }}</span>
                <span class="suggestion-rate">{{ formatNumber(period.value, 3) }}%</span>
              </div>
            </div>
          </div>
          <small class="form-hint">
            {{ selectedPeriod 
              ? `Найдено: ${formatNumber(selectedPeriod.term, 4)} лет → ${formatNumber(selectedPeriod.value, 4)}%` 
              : 'Введите срок и нажмите Enter' }}
          </small>
        </div>

        <!-- Interpolated Result Card -->
        <div v-if="selectedPeriod" class="glass-card panel highlight-panel">
          <div class="panel-header">
            <h3>📊 Результат интерполяции</h3>
            <div class="badge-glass">{{ getTermType(selectedPeriod.term) }}</div>
          </div>
          <div class="result-metrics">
            <div class="metric-item">
              <span class="metric-label">Период</span>
              <span class="metric-value">{{ formatNumber(selectedPeriod.term, 4) }} лет</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">Доходность</span>
              <span class="metric-value text-gradient-blue">{{ formatNumber(selectedPeriod.value, 4) }}%</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">На дату</span>
              <span class="metric-value">{{ formatDate(results.date) }}</span>
            </div>
          </div>
        </div>

        <!-- Yield Curve Visualization -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Кривая доходности</h3>
            <div class="legend">
              <span class="dot-legend bg-blue"></span> Ставка КБД
            </div>
          </div>
          <div class="chart-container">
            <canvas ref="chartCanvas" class="chart-canvas"></canvas>
          </div>
        </div>

        <!-- Data Table -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Таблица данных</h3>
            <div class="badge-glass">{{ results.data.length }} точек</div>
          </div>
          <div class="table-wrapper">
            <table class="glass-table">
              <thead>
                <tr>
                  <th class="text-left">#</th>
                  <th class="text-right">Срок (годы)</th>
                  <th class="text-right">Ставка (%)</th>
                  <th class="text-right">Класс</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(point, idx) in results.data" :key="idx" :class="getRowClass(point.term)">
                  <td class="text-left">{{ idx + 1 }}</td>
                  <td class="text-right mono">{{ formatNumber(point.term, 4) }}</td>
                  <td class="text-right mono text-gradient-blue">{{ formatNumber(point.value, 4) }}</td>
                  <td class="text-right">
                    <span class="badge-type">{{ getTermType(point.term) }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <!-- Right Column -->
      <div class="col-right">
        
        <!-- Statistics -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Статистика кривой</h3>
          </div>
          <div class="metrics-kv-list">
            <div class="kv-row">
              <span class="k">Диапазон сроков</span>
              <span class="v mono">{{ formatNumber(results.min_term, 4) }} – {{ formatNumber(results.max_term, 2) }}</span>
            </div>
            <div class="kv-row">
              <span class="k">Средняя ставка</span>
              <span class="v mono">{{ formatNumber(results.mean_rate, 3) }}%</span>
            </div>
            <div class="kv-row">
              <span class="k">Разброс (max-min)</span>
              <span class="v mono">{{ formatNumber(results.max_rate - results.min_rate, 3) }}%</span>
            </div>
            <div class="kv-row">
              <span class="k">Slope (5y - 0.5y)</span>
              <span class="v mono" :class="getSlope() > 0 ? 'text-green' : 'text-red'">{{ formatNumber(getSlope(), 3) }}%</span>
            </div>
          </div>
        </div>

        <!-- Term Classification -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Классификация сроков</h3>
          </div>
          <div class="factor-list">
            <div class="list-row">
              <div class="lbl-group">
                <span class="lbl">Ночной</span>
                <span class="sub-lbl">≤ 0.5 лет</span>
              </div>
            </div>
            <div class="list-row">
              <div class="lbl-group">
                <span class="lbl">Краткосрочный</span>
                <span class="sub-lbl">0.5 – 1 год</span>
              </div>
            </div>
            <div class="list-row">
              <div class="lbl-group">
                <span class="lbl">Среднесрочный</span>
                <span class="sub-lbl">1 – 3 года</span>
              </div>
            </div>
            <div class="list-row">
              <div class="lbl-group">
                <span class="lbl">Долгосрочный</span>
                <span class="sub-lbl">3 – 5 лет</span>
              </div>
            </div>
            <div class="list-row">
              <div class="lbl-group">
                <span class="lbl">Очень долгосрочный</span>
                <span class="sub-lbl">> 5 лет</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Information -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>ℹ️ О КБД</h3>
          </div>
          <div class="info-text">
            <p>
              <strong>КБД</strong> — кривая бескупонных доходностей показывает зависимость доходности до погашения 
              бескупонных облигаций от сроков до погашения.
            </p>
            <p>
              <strong>Источник:</strong> MOEX ISS API
            </p>
            <p>
              <strong>Интерполяция:</strong> Если срок не совпадает ни с одной точкой кривой, система вычисляет 
              доходность методом линейной интерполяции между двумя ближайшими точками.
            </p>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import Chart from 'chart.js/auto'

// ============= TYPES =============
interface ZCYCPoint {
  term: number
  value: number
}

interface ZCYCResults {
  status: string
  date: string
  data: ZCYCPoint[]
  count: number
  min_term: number
  max_term: number
  min_rate: number
  max_rate: number
  mean_rate: number
}

interface ZCYCParams {
  date: string
}

// ============= STATE =============
const params = ref<ZCYCParams>({
  date: '2026-01-03'
})

// Mock data
const mockData: ZCYCResults = {
  status: 'ok',
  date: '2026-01-03',
  count: 12,
  min_term: 0.083,
  max_term: 10.0,
  min_rate: 13.45,
  max_rate: 14.82,
  mean_rate: 14.12,
  data: [
    { term: 0.083, value: 13.45 },
    { term: 0.25, value: 13.52 },
    { term: 0.5, value: 13.68 },
    { term: 1.0, value: 13.95 },
    { term: 2.0, value: 14.28 },
    { term: 3.0, value: 14.42 },
    { term: 5.0, value: 14.65 },
    { term: 7.0, value: 14.75 },
    { term: 10.0, value: 14.82 },
    { term: 15.0, value: 14.80 },
    { term: 20.0, value: 14.75 },
    { term: 30.0, value: 14.70 }
  ]
}

const results = ref<ZCYCResults>(mockData)
const loading = ref(false)
const chartCanvas = ref<HTMLCanvasElement | null>(null)
const chart = ref<Chart | null>(null)

// Period search
const periodSearch = ref('')
const selectedPeriod = ref<ZCYCPoint | null>(null)
const showSuggestions = ref(false)

// ============= COMPUTED =============
const today = new Date().toISOString().split('T')[0]

const filteredPeriods = computed((): ZCYCPoint[] => {
  if (!periodSearch.value || !results.value) return []
  
  const searchVal = parseFloat(periodSearch.value)
  if (isNaN(searchVal)) return []

  return results.value.data
    .map(p => ({ ...p, diff: Math.abs(p.term - searchVal) }))
    .sort((a, b) => a.diff - b.diff)
    .slice(0, 10)
    .map(({ diff, ...p }) => p)
})

// ============= METHODS =============
const loadZCYC = async () => {
  loading.value = true
  
  setTimeout(() => {
    // Simulate API call - in real app this would fetch from API
    loading.value = false
    renderChart(results.value)
  }, 800)
}

const filterPeriods = () => {
  showSuggestions.value = periodSearch.value.length > 0
}

const interpolateRate = (term: number): number | null => {
  if (!results.value || results.value.data.length < 2) return null

  const data = results.value.data

  const exactMatch = data.find(p => Math.abs(p.term - term) < 0.0001)
  if (exactMatch) return exactMatch.value

  let lower: ZCYCPoint | null = null
  let upper: ZCYCPoint | null = null

  for (let i = 0; i < data.length; i++) {
    if (data[i].term <= term && (!lower || data[i].term > lower.term)) {
      lower = data[i]
    }
    if (data[i].term >= term && (!upper || data[i].term < upper.term)) {
      upper = data[i]
    }
  }

  if (!lower) return data[0].value
  if (!upper) return data[data.length - 1].value
  if (!lower || !upper || lower === upper) return lower?.value || null

  const t = (term - lower.term) / (upper.term - lower.term)
  return lower.value + t * (upper.value - lower.value)
}

const selectPeriod = (period: ZCYCPoint | undefined) => {
  if (!period) return
  selectedPeriod.value = period
  periodSearch.value = formatNumber(period.term, 4)
  showSuggestions.value = false
}

const searchPeriodByInput = () => {
  if (!periodSearch.value || !results.value) {
    selectedPeriod.value = null
    return
  }

  const searchTerm = parseFloat(periodSearch.value)
  if (isNaN(searchTerm)) {
    selectedPeriod.value = null
    return
  }

  if (searchTerm < results.value.min_term || searchTerm > results.value.max_term) {
    selectedPeriod.value = null
    return
  }

  const interpolatedRate = interpolateRate(searchTerm)
  if (interpolatedRate !== null) {
    selectedPeriod.value = {
      term: searchTerm,
      value: interpolatedRate
    }
  } else {
    selectedPeriod.value = null
  }
}

const renderChart = (data: ZCYCResults) => {
  if (!chartCanvas.value) return

  if (chart.value) {
    chart.value.destroy()
  }

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  chart.value = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.data.map(d => `${d.term.toFixed(2)}y`),
      datasets: [{
        label: 'Ставка КБД (%)',
        data: data.data.map(d => d.value),
        borderColor: '#60a5fa',
        backgroundColor: 'rgba(96, 165, 250, 0.1)',
        borderWidth: 2.5,
        fill: true,
        tension: 0.35,
        pointRadius: 4,
        pointBackgroundColor: '#60a5fa',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 1.5,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: '#3b82f6',
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top' as const,
          labels: {
            boxWidth: 12,
            padding: 15,
            font: { size: 14, weight: 'bold' as const },
            color: 'rgba(255,255,255,0.6)'
          }
        },
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          titleFont: { size: 13, weight: 'bold' as const },
          bodyFont: { size: 12 },
          borderColor: '#60a5fa',
          borderWidth: 1,
          titleColor: '#60a5fa',
          bodyColor: '#e5e7eb',
          displayColors: false,
          callbacks: {
            label: (context) => `Ставка: ${Number(context.parsed.y).toFixed(3)}%`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          grid: {
            color: 'rgba(255, 255, 255, 0.08)',
            drawBorder: false,
            lineWidth: 1
          },
          ticks: {
            color: 'rgba(255,255,255,0.6)',
            font: { size: 12 },
            callback: (v) => `${Number(v).toFixed(1)}%`,
            padding: 10
          },
          title: {
            display: true,
            text: 'Ставка, % годовых',
            font: { weight: 'bold', size: 13 },
            color: 'rgba(255,255,255,0.6)',
            padding: 12
          }
        },
        x: {
          grid: {
            display: false,
            drawBorder: false
          },
          ticks: {
            color: 'rgba(255,255,255,0.6)',
            font: { size: 12 },
            padding: 10,
            maxRotation: 0
          },
          title: {
            display: true,
            text: 'Срок до погашения',
            font: { weight: 'bold', size: 13 },
            color: 'rgba(255,255,255,0.6)',
            padding: 12
          }
        }
      }
    }
  })
}

const getTermType = (term: number): string => {
  if (term <= 0.5) return 'Ночной'
  if (term <= 1) return 'Краткосрочный'
  if (term <= 3) return 'Среднесрочный'
  if (term <= 5) return 'Долгосрочный'
  return 'Очень долгосрочный'
}

const getRowClass = (term: number): Record<string, boolean> => {
  return {
    'short-term': term <= 1,
    'medium-term': term > 1 && term <= 3,
    'long-term': term > 3
  }
}

const getSlope = (): number => {
  if (!results.value || results.value.data.length === 0) return 0
  
  const data = results.value.data
  let rate5y = data[data.length - 1].value
  let rate05y = data[0].value
  
  for (const point of data) {
    if (Math.abs(point.term - 5) < Math.abs(rate5y - 5)) {
      rate5y = point.value
    }
    if (Math.abs(point.term - 0.5) < Math.abs(rate05y - 0.5)) {
      rate05y = point.value
    }
  }
  
  return rate5y - rate05y
}

// Formatters
const formatNumber = (val: number, decimals = 2): string => {
  return val.toLocaleString('ru-RU', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

const formatDate = (dateStr: string): string => {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

// Auto-render chart on mount
onMounted(() => {
  renderChart(results.value)
})
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.page-container {
  display: flex; flex-direction: column; gap: 24px;
  padding: 24px 32px; max-width: 1600px; margin: 0 auto;
}

.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px; }
.section-title { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }
.header-actions { display: flex; gap: 12px; align-items: center; }
.header-left { display: flex; flex-direction: column; }

/* ============================================
   GLASS COMPONENTS
   ============================================ */
.glass-card {
  border-radius: 20px; overflow: hidden;
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 20px 40px -10px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
}

.glass-pill {
  display: flex; align-items: center; gap: 8px; padding: 4px 12px;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 99px; height: 36px;
}
.lbl-mini { font-size: 11px; color: rgba(255,255,255,0.5); font-weight: 600; text-transform: uppercase; }

.date-input {
  background: transparent; border: none; color: #60a5fa; width: 120px;
  font-family: "SF Mono", monospace; font-weight: 500; font-size: 13px; outline: none; padding: 0;
  cursor: pointer;
}
.date-input::-webkit-calendar-picker-indicator {
  filter: invert(1) brightness(0.8);
  cursor: pointer;
}

/* ============================================
   KPI GRID
   ============================================ */
.kpi-cards-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.kpi-card { padding: 20px; display: flex; flex-direction: column; justify-content: space-between; min-height: 110px; }
.kpi-label { font-size: 11px; text-transform: uppercase; color: rgba(255,255,255,0.5); font-weight: 700; letter-spacing: 0.05em; margin-bottom: 8px; }
.kpi-value { font-size: 26px; font-weight: 700; font-family: "SF Mono", monospace; line-height: 1.1; letter-spacing: -0.02em; }
.kpi-sub { font-size: 11px; margin-top: 6px; display: flex; gap: 6px; }

/* ============================================
   DASHBOARD LAYOUT
   ============================================ */
.dashboard-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 24px; align-items: start; }
.col-left, .col-right { display: flex; flex-direction: column; gap: 24px; }
.panel { padding: 24px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.panel-header h3 { margin: 0; font-size: 13px; font-weight: 600; text-transform: uppercase; color: rgba(255,255,255,0.9); letter-spacing: 0.05em; }

.highlight-panel {
  border: 1px solid rgba(96, 165, 250, 0.3);
  background: rgba(96, 165, 250, 0.05);
}

/* ============================================
   SEARCH
   ============================================ */
.search-container { display: flex; flex-direction: column; gap: 12px; }
.search-input-wrapper {
  position: relative;
  display: flex; align-items: center;
}
.search-input {
  width: 100%; padding: 10px 12px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px; color: #60a5fa; font-size: 13px; font-family: "SF Mono", monospace; outline: none;
  transition: border-color 0.2s;
}
.search-input:focus {
  border-color: rgba(96, 165, 250, 0.5); background: rgba(255,255,255,0.08);
}
.search-unit { position: absolute; right: 12px; color: rgba(255,255,255,0.5); font-size: 12px; }

.period-suggestions {
  background: rgba(30, 32, 40, 0.95); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px; max-height: 200px; overflow-y: auto;
  box-shadow: 0 8px 20px rgba(0,0,0,0.4);
}
.suggestion-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 12px; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.04);
  transition: background 0.15s ease;
}
.suggestion-item:last-child { border-bottom: none; }
.suggestion-item:hover { background: rgba(96, 165, 250, 0.15); }
.suggestion-term { font-size: 12px; font-weight: 500; color: #fff; font-family: "SF Mono", monospace; }
.suggestion-rate { font-size: 12px; font-weight: 600; color: #60a5fa; font-family: "SF Mono", monospace; }

.form-hint { font-size: 11px; color: rgba(255,255,255,0.4); margin-top: 4px; display: block; }

/* ============================================
   RESULT METRICS
   ============================================ */
.result-metrics {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
}
.metric-item { display: flex; flex-direction: column; gap: 6px; padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; }
.metric-label { font-size: 10px; text-transform: uppercase; color: rgba(255,255,255,0.4); font-weight: 600; }
.metric-value { font-size: 14px; font-weight: 700; font-family: "SF Mono", monospace; color: #fff; }

/* ============================================
   CHART
   ============================================ */
.chart-container { position: relative; height: 350px; }
.chart-canvas { width: 100% !important; height: 100% !important; }

/* ============================================
   TABLES
   ============================================ */
.table-wrapper { overflow-x: auto; max-height: 500px; overflow-y: auto; }
.glass-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.glass-table th {
  text-align: left; padding: 12px 0; color: rgba(255,255,255,0.4); font-weight: 600; font-size: 10px;
  text-transform: uppercase; border-bottom: 1px solid rgba(255,255,255,0.08);
}
.glass-table td { padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.03); color: rgba(255,255,255,0.9); }
.glass-table tr:last-child td { border-bottom: none; }
.glass-table tr.short-term { background: rgba(96, 165, 250, 0.05); }
.glass-table tr.medium-term { background: rgba(34, 197, 94, 0.05); }
.glass-table tr.long-term { background: rgba(249, 115, 22, 0.05); }

/* ============================================
   LISTS & METRICS
   ============================================ */
.factor-list, .metrics-kv-list { display: flex; flex-direction: column; gap: 8px; }
.list-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.list-row:last-child { border-bottom: none; }
.lbl-group { display: flex; flex-direction: column; gap: 2px; }
.lbl { font-size: 13px; color: #fff; font-weight: 500; }
.sub-lbl { font-size: 10px; color: rgba(255,255,255,0.4); }

.kv-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.03); }
.kv-row:last-child { border-bottom: none; }
.k { color: rgba(255,255,255,0.6); }
.v { color: #fff; font-family: "SF Mono", monospace; font-weight: 500; }

.info-text { font-size: 12px; line-height: 1.6; }
.info-text p { margin: 12px 0; color: rgba(255,255,255,0.8); }
.info-text p:first-child { margin-top: 0; }
.info-text p:last-child { margin-bottom: 0; }
.info-text strong { color: #fff; }

/* ============================================
   UTILS
   ============================================ */
.btn-glass {
  height: 36px; padding: 0 16px; border-radius: 10px; font-weight: 600; font-size: 13px;
  display: flex; align-items: center; gap: 8px; cursor: pointer; border: none; transition: all 0.2s;
}
.btn-glass.primary { background: #60a5fa; color: #fff; box-shadow: 0 4px 12px rgba(96, 165, 250, 0.3); }
.btn-glass.primary:hover:not(:disabled) { background: #3b82f6; transform: translateY(-1px); }
.btn-glass:disabled { opacity: 0.5; cursor: not-allowed; }

.badge-glass { font-size: 10px; background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; color: rgba(255,255,255,0.7); }
.badge-type { font-size: 10px; background: rgba(96, 165, 250, 0.15); padding: 2px 6px; border-radius: 4px; color: #60a5fa; }
.legend { display: flex; gap: 12px; align-items: center; font-size: 10px; color: rgba(255,255,255,0.4); }
.dot-legend { width: 6px; height: 6px; border-radius: 50%; display: inline-block; margin-right: 4px; }

/* Colors & Helpers */
.text-gradient-green { background: linear-gradient(135deg, #4ade80, #22c55e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-gradient-blue { background: linear-gradient(135deg, #60a5fa, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-red { color: #f87171; }
.text-green { color: #4ade80; }
.text-muted { color: rgba(255,255,255,0.4); }
.text-white { color: #fff; }
.font-bold { font-weight: 700; }
.bg-blue { background: #60a5fa; }
.bg-red { background: #ef4444; }
.mono { font-family: "SF Mono", monospace; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.spinner-mini { width: 12px; height: 12px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1200px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .kpi-cards-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .page-container { padding: 16px; }
  .section-header { flex-direction: column; gap: 16px; }
  .header-actions { width: 100%; flex-wrap: wrap; }
  .btn-glass { width: 100%; justify-content: center; }
  .kpi-cards-grid { grid-template-columns: 1fr; }
  .result-metrics { grid-template-columns: 1fr; }
}
</style>