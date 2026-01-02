<template>
  <div class="zcyc-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>КБД (Zero-Coupon Yield Curve)</h1>
        <p class="subtitle">Кривая бескупонных доходностей от MOEX ISS API</p>
      </div>
      <button class="btn btn-primary" @click="loadZCYC" :disabled="loading">
        {{ loading ? 'Загрузка...' : 'Загрузить КБД' }}
      </button>
    </div>

    <!-- Input Parameters Card -->
    <div class="card">
      <div class="card-header">
        <h3>Параметры загрузки</h3>
      </div>
      <div class="card-body">
        <div class="params-grid">
          <div class="form-group">
            <label>Дата расчёта</label>
            <input
              v-model="params.date"
              type="date"
              class="form-control"
              :max="today"
            />
            <small class="form-hint">Если дата недоступна, система найдёт последнюю доступную</small>
          </div>

          <!-- Period Search with Interpolation -->
          <div class="form-group">
            <label>Поиск периода (срок в годах)</label>
            <div class="period-search-wrapper">
              <input
                v-model="periodSearch"
                type="number"
                step="0.01"
                class="form-control period-input"
                placeholder="Введите срок (например 2.23)"
                @input="filterPeriods"
                @change="searchPeriodByInput"
                @keydown.enter="searchPeriodByInput"
              />
              <div v-if="showSuggestions && filteredPeriods.length > 0" class="period-suggestions">
                <div
                  v-for="(period, idx) in filteredPeriods.slice(0, 5)"
                  :key="idx"
                  class="suggestion-item"
                  @click="selectPeriod(period)"
                >
                  <span class="suggestion-term">{{ formatNumber(period.term, 4) }} лет</span>
                  <span class="suggestion-rate">{{ formatNumber(period.value, 3) }}%</span>
                </div>
              </div>
            </div>
            <small class="form-hint">
              {{ selectedPeriod ? `Поиск: ${formatNumber(selectedPeriod.term, 4)} лет → ${formatNumber(selectedPeriod.value, 4)}% (интерполяция)` : 'Введите срок и нажмите Enter или потеряйте фокус' }}
            </small>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="alert alert-danger">
      <span>⚠️</span>
      <span>{{ error }}</span>
    </div>

    <!-- Selected Period Display Card (Interpolated) -->
    <div v-if="selectedPeriod && results" class="card period-result-card">
      <div class="card-header">
        <h3>📊 Результат поиска периода (интерполяция)</h3>
      </div>
      <div class="card-body period-result-body">
        <div class="result-grid">
          <div class="result-item">
            <div class="result-label">Запрошенный период</div>
            <div class="result-value">{{ formatNumber(selectedPeriod.term, 4) }} <span class="unit">лет</span></div>
          </div>
          <div class="result-item">
            <div class="result-label">Интерполированная доходность</div>
            <div class="result-value text-gradient-blue">{{ formatNumber(selectedPeriod.value, 4) }} <span class="unit">%</span></div>
          </div>
          <div class="result-item">
            <div class="result-label">Классификация</div>
            <div class="result-value">
              <span class="badge-type">{{ getTermType(selectedPeriod.term) }}</span>
            </div>
          </div>
          <div class="result-item">
            <div class="result-label">На дату</div>
            <div class="result-value mono">{{ formatDate(results.date) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div v-if="results" class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Дата КБД</div>
        <div class="stat-value">{{ formatDate(results.date) }}</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">Точек на кривой</div>
        <div class="stat-value">{{ results.count }}</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">Минимальная ставка</div>
        <div class="stat-value text-gradient-blue">{{ formatNumber(results.min_rate, 3) }}%</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">Максимальная ставка</div>
        <div class="stat-value text-gradient-green">{{ formatNumber(results.max_rate, 3) }}%</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">Средняя ставка</div>
        <div class="stat-value">{{ formatNumber(results.mean_rate, 3) }}%</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">Диапазон сроков</div>
        <div class="stat-value mono">{{ formatNumber(results.min_term, 4) }} – {{ formatNumber(results.max_term, 2) }} лет</div>
      </div>
    </div>

    <!-- Chart Card (BIG GRAPH) -->
    <div v-if="results" class="card chart-card">
      <div class="card-header">
        <h3>Визуализация КБД</h3>
      </div>
      <div class="card-body chart-body">
        <canvas 
          ref="chartCanvas" 
          class="chart-canvas"
        ></canvas>
      </div>
    </div>

    <!-- Data Table -->
    <div v-if="results && results.data" class="card table-card">
      <div class="card-header">
        <h3>Таблица данных КБД</h3>
        <span class="badge">{{ results.data.length }} точек</span>
      </div>
      <div class="card-body">
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Срок (годы)</th>
                <th>Ставка (%)</th>
                <th>Тип</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(point, idx) in results.data" 
                :key="idx"
                :class="getRowClass(point.term)"
              >
                <td>{{ idx + 1 }}</td>
                <td class="mono">{{ formatNumber(point.term, 4) }}</td>
                <td class="mono text-gradient-blue">{{ formatNumber(point.value, 4) }}</td>
                <td>
                  <span class="badge-type">
                    {{ getTermType(point.term) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Info Section -->
    <div v-if="results" class="card info-card">
      <div class="card-header">
        <h3>ℹ️ Информация</h3>
      </div>
      <div class="card-body">
        <p class="info-text">
          <strong>КБД (Кривая бескупонных доходностей)</strong> — это зависимость доходности до погашения 
          бескупонных облигаций от сроков до их погашения. Используется для оценки облигаций с купонами 
          и как основа для построения других кривых доходности.
        </p>
        <p class="info-text">
          <strong>Источник:</strong> MOEX ISS API (engines/stock/zcyc.json)
        </p>
        <p class="info-text">
          <strong>Автоматический fallback:</strong> Если на выбранную дату нет расчётов (выходной/праздник), 
          система автоматически найдёт последнюю доступную дату в течение 7 дней назад.
        </p>
        <p class="info-text">
          <strong>Интерполяция периода:</strong> Введите любой срок в годах (например 2.23, 5.5, 10.1). 
          Если срок не совпадает ни с одной точкой кривой, система автоматически вычислит доходность 
          методом линейной интерполяции между двумя ближайшими точками.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import Chart from 'chart.js/auto'

// Types
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

// State
const params = ref({
  date: new Date().toISOString().split('T')[0]
})

const results = ref<ZCYCResults | null>(null)
const loading = ref(false)
const error = ref('')
const chartCanvas = ref<HTMLCanvasElement | null>(null)
const chart = ref<Chart | null>(null)

// Period search state
const periodSearch = ref('')
const selectedPeriod = ref<ZCYCPoint | null>(null)
const showSuggestions = ref(false)

// Computed
const today = new Date().toISOString().split('T')[0]

const filteredPeriods = computed((): ZCYCPoint[] => {
  if (!periodSearch.value || !results.value) return []
  
  const searchVal = parseFloat(periodSearch.value)
  if (isNaN(searchVal)) return []

  // Сортируем по близости к введённому значению
  return results.value.data
    .map(p => ({ ...p, diff: Math.abs(p.term - searchVal) }))
    .sort((a, b) => a.diff - b.diff)
    .slice(0, 10)
    .map(({ diff, ...p }) => p)
})

// Methods
const loadZCYC = async () => {
  loading.value = true
  error.value = ''
  results.value = null
  selectedPeriod.value = null

  try {
    const url = new URL('http://127.0.0.1:8000/api/zcyc')
    if (params.value.date) {
      url.searchParams.append('date', params.value.date)
    }

    const response = await fetch(url.toString())

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || `HTTP ${response.status}`)
    }

    const data = await response.json()
    results.value = data

    // Render chart after data is loaded
    await new Promise(resolve => setTimeout(resolve, 0))
    renderChart(data)
  } catch (err: any) {
    error.value = err.message || 'Ошибка при загрузке КБД'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const filterPeriods = () => {
  showSuggestions.value = periodSearch.value.length > 0
}

const interpolateRate = (term: number): number | null => {
  if (!results.value || results.value.data.length < 2) return null

  const data = results.value.data

  // Если точно совпадает с существующей точкой
  const exactMatch = data.find(p => Math.abs(p.term - term) < 0.0001)
  if (exactMatch) return exactMatch.value

  // Ищем две ближайшие точки для интерполяции
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

  // Если за пределами диапазона
  if (!lower) return data[0].value
  if (!upper) return data[data.length - 1].value
  if (!lower || !upper || lower === upper) return lower?.value || null

  // Линейная интерполяция: y = y1 + t * (y2 - y1), где t ∈ [0,1]
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

  // Проверяем диапазон
  if (searchTerm < results.value.min_term || searchTerm > results.value.max_term) {
    error.value = `Период должен быть в диапазоне ${formatNumber(results.value.min_term, 4)} – ${formatNumber(results.value.max_term, 2)} лет`
    selectedPeriod.value = null
    return
  }

  const interpolatedRate = interpolateRate(searchTerm)
  if (interpolatedRate !== null) {
    error.value = ''
    selectedPeriod.value = {
      term: searchTerm,
      value: interpolatedRate
    }
  } else {
    error.value = 'Ошибка при интерполяции'
    selectedPeriod.value = null
  }
}

const renderChart = (data: ZCYCResults) => {
  if (!chartCanvas.value) return

  // Destroy existing chart
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
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2.5,
        fill: true,
        tension: 0.35,
        pointRadius: 4,
        pointBackgroundColor: '#3b82f6',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 1.5,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: '#1e40af',
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            boxWidth: 12,
            padding: 15,
            font: { size: 14, weight: 600 },
            color: '#9ca3af'
          }
        },
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          titleFont: { size: 13, weight: 600 },
          bodyFont: { size: 12 },
          borderColor: '#3b82f6',
          borderWidth: 1,
          titleColor: '#3b82f6',
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
          min: 10,
          max: 16,
          ticks: {
            stepSize: 0.5,
          },
          grid: {
            color: 'rgba(255, 255, 255, 0.08)',
            drawBorder: false,
            lineWidth: 1
          },
          ticks: {
            color: '#9ca3af',
            font: { size: 12 },
            callback: (v) => `${Number(v).toFixed(1)}%`,
            padding: 10
          },
          title: {
            display: true,
            text: 'Ставка, % годовых',
            font: { weight: 'bold', size: 14 },
            color: '#9ca3af',
            padding: 12
          }
        },
        x: {
          grid: {
            display: false,
            drawBorder: false
          },
          ticks: {
            color: '#9ca3af',
            font: { size: 12 },
            padding: 10,
            maxRotation: 0
          },
          title: {
            display: true,
            text: 'Срок до погашения',
            font: { weight: 'bold', size: 14 },
            color: '#9ca3af',
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

// Auto-load on mount
onMounted(() => {
  loadZCYC()
})
</script>

<style scoped>
.zcyc-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-header h1 {
  font-size: 32px;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.8px;
}

.page-header .subtitle {
  margin-top: 6px;
  font-size: 14px;
  color: var(--text-secondary);
}

/* Parameters Grid */
.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-hint {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-top: 4px;
}

/* Period Search Wrapper */
.period-search-wrapper {
  position: relative;
}

.period-input {
  width: 100%;
}

.period-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(30, 41, 59, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-top: none;
  border-radius: 0 0 6px 6px;
  max-height: 220px;
  overflow-y: auto;
  z-index: 100;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(12px);
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  transition: all 0.15s ease;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover {
  background: rgba(59, 130, 246, 0.15);
  border-left: 2px solid #3b82f6;
  padding-left: 10px;
}

.suggestion-term {
  font-size: 12px;
  font-weight: 500;
  color: #fff;
  font-family: var(--font-family-mono);
}

.suggestion-rate {
  font-size: 12px;
  font-weight: 600;
  color: #60a5fa;
  font-family: var(--font-family-mono);
}

/* Period Result Card */
.period-result-card {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(34, 211, 94, 0.04));
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.period-result-body {
  padding: 0 !important;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  padding: 16px;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.result-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.result-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.result-value .unit {
  font-size: 12px;
  font-weight: 500;
  opacity: 0.7;
}

.result-value.mono {
  font-family: var(--font-family-mono);
}

/* Alert */
.alert {
  padding: 14px 18px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  font-size: 13px;
}

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border-soft);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
}

.stat-value.mono {
  font-size: 14px;
}

/* Chart Card */
.chart-card {
  grid-column: 1 / -1;
}

.chart-body {
  padding: 20px !important;
  min-height: 550px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.01);
}

.chart-canvas {
  width: 100% !important;
  height: 500px !important;
}

/* Badge */
.badge {
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  font-size: 11px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-secondary);
}

.badge-type {
  padding: 3px 8px;
  border-radius: var(--radius-pill);
  font-size: 10px;
  font-weight: 600;
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
}

/* Table */
.table-wrapper {
  overflow-x: auto;
  border-radius: var(--radius-sm);
  max-height: 600px;
  overflow-y: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table thead th {
  text-align: left;
  padding: 10px 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--glass-border-soft);
  position: sticky;
  top: 0;
  background: rgba(0, 0, 0, 0.2);
}

.data-table tbody td {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
}

.data-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.data-table tbody tr.short-term {
  background: rgba(59, 130, 246, 0.05);
}

.data-table tbody tr.medium-term {
  background: rgba(34, 197, 94, 0.05);
}

.data-table tbody tr.long-term {
  background: rgba(249, 115, 22, 0.05);
}

.data-table .mono {
  font-family: var(--font-family-mono);
}

/* Info Card */
.info-card {
  /* дополнительные стили */
}

.info-text {
  margin: 12px 0;
  line-height: 1.6;
  color: var(--text-primary);
  font-size: 13px;
}

.info-text:first-child {
  margin-top: 0;
}

.info-text:last-child {
  margin-bottom: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .zcyc-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .page-header .btn {
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .params-grid {
    grid-template-columns: 1fr;
  }

  .result-grid {
    grid-template-columns: 1fr;
  }

  .table-wrapper {
    max-height: 400px;
  }

  .chart-body {
    min-height: 400px !important;
  }

  .chart-canvas {
    height: 350px !important;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .chart-body {
    min-height: 300px !important;
  }

  .chart-canvas {
    height: 250px !important;
  }
}

/* Gradient text */
.text-gradient-blue {
  background: linear-gradient(135deg, #3b82f6, #1e40af);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.text-gradient-green {
  background: linear-gradient(135deg, #10b981, #059669);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Button styles */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #1e40af);
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Card styles */
.card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-md);
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #fff;
}

.card-body {
  padding: 0;
}

.form-control {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #fff;
  font-size: 13px;
  font-family: var(--font-family-mono);
}

.form-control:focus {
  outline: none;
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(255, 255, 255, 0.08);
}
</style>
