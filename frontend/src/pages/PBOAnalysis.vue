<template>
  <div class="pbo-page">
    <div class="page-header">
      <h1>PBO / DSR — Анализ переобучения бэктеста</h1>
      <p class="subtitle">
        Probability of Backtest Overfitting (CSCV) · Deflated Sharpe Ratio · Minimum Backtest Length
      </p>
    </div>

    <!-- Input Panel -->
    <div class="card input-card">
      <h2>Параметры</h2>

      <div class="form-grid">
        <div class="form-group">
          <label>Число подмножеств (S)</label>
          <input v-model.number="params.n_splits" type="number" min="4" max="64" step="2" />
          <span class="hint">Чётное, ≥ 4. C(S, S/2) комбинаций для CSCV.</span>
        </div>
        <div class="form-group">
          <label>Периодов в году</label>
          <input v-model.number="params.annualize" type="number" min="1" />
          <span class="hint">252 для дневных, 52 для недельных данных.</span>
        </div>
        <div class="form-group">
          <label>SR бенчмарк (годовой)</label>
          <input v-model.number="params.sr_benchmark" type="number" step="0.1" />
          <span class="hint">Пороговый SR для PSR. Обычно 0.</span>
        </div>
      </div>

      <div class="matrix-input">
        <label>Матрица доходностей (T × N)</label>
        <p class="hint">Каждая строка — период, столбцы — стратегии. CSV-формат, разделитель ",".</p>
        <textarea
          v-model="returnsText"
          rows="10"
          placeholder="0.001,0.002,-0.001&#10;-0.001,0.000,0.002&#10;0.002,0.001,0.000"
        />
        <div class="matrix-info" v-if="parsedShape">
          Матрица: {{ parsedShape.T }} × {{ parsedShape.N }} (T × N стратегий)
        </div>
        <div class="matrix-error" v-if="parseError">{{ parseError }}</div>
      </div>

      <div class="actions">
        <button class="btn-primary" @click="compute" :disabled="loading || !!parseError">
          {{ loading ? 'Вычисление...' : 'Запустить анализ' }}
        </button>
        <button class="btn-secondary" @click="loadDemo">Демо-данные</button>
      </div>

      <div class="error-msg" v-if="error">{{ error }}</div>
    </div>

    <!-- Results -->
    <template v-if="result">
      <!-- Verdict Banner -->
      <div class="verdict-banner" :class="result.verdict_level">
        <div class="verdict-icon">
          {{ result.verdict_level === 'danger' ? '⚠️' : result.verdict_level === 'warning' ? '⚡' : '✅' }}
        </div>
        <div class="verdict-text">
          <strong>{{ result.verdict }}</strong>
          <span>PBO = {{ (result.pbo * 100).toFixed(1) }}% · {{ result.n_combinations }} комбинаций CSCV</span>
        </div>
      </div>

      <!-- KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi-card" :class="getPBOClass(result.pbo)">
          <div class="kpi-label">PBO</div>
          <div class="kpi-value">{{ (result.pbo * 100).toFixed(1) }}%</div>
          <div class="kpi-sub">вероятность переобучения</div>
        </div>
        <div class="kpi-card" :class="getDSRClass(result.dsr)">
          <div class="kpi-label">DSR</div>
          <div class="kpi-value">{{ (result.dsr * 100).toFixed(1) }}%</div>
          <div class="kpi-sub">Deflated Sharpe Ratio</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">SR̂ (лучший)</div>
          <div class="kpi-value">{{ result.sr_hat_annual.toFixed(2) }}</div>
          <div class="kpi-sub">годовой, аннуализированный</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">SR* (порог)</div>
          <div class="kpi-value">{{ result.sr_star_annual.toFixed(2) }}</div>
          <div class="kpi-sub">E[max SR] с поправкой</div>
        </div>
        <div class="kpi-card" :class="result.btl_sufficient ? 'ok' : 'danger'">
          <div class="kpi-label">MinBTL</div>
          <div class="kpi-value">{{ result.min_btl.toLocaleString() }}</div>
          <div class="kpi-sub">
            мин. длина бэктеста (текущий: {{ result.current_t }})
            {{ result.btl_sufficient ? '✅' : '❌' }}
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Стратегий</div>
          <div class="kpi-value">{{ result.n_strategies }}</div>
          <div class="kpi-sub">лучшая: #{{ result.best_strategy }}</div>
        </div>
      </div>

      <!-- Charts Row 1 -->
      <div class="charts-row">
        <div class="card chart-card">
          <h3>IS vs OOS Scatter</h3>
          <div ref="scatterChart" class="chart" />
        </div>
        <div class="card chart-card">
          <h3>Логит-распределение OOS ранга</h3>
          <div ref="logitChart" class="chart" />
        </div>
      </div>

      <!-- Strategy Stats Table -->
      <div class="card">
        <h3>Статистика стратегий</h3>
        <table class="stats-table">
          <thead>
            <tr>
              <th>Стратегия</th>
              <th>SR (период)</th>
              <th>SR (годовой)</th>
              <th>Асимметрия</th>
              <th>Эксц. куртозис</th>
              <th>PSR</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="s in result.strategy_stats"
              :key="s.strategy"
              :class="{ 'best-row': s.strategy === result.best_strategy }"
            >
              <td>
                {{ s.strategy }}
                <span v-if="s.strategy === result.best_strategy" class="best-tag">★ лучшая</span>
              </td>
              <td>{{ s.sr_freq.toFixed(4) }}</td>
              <td>{{ s.sr_annual.toFixed(3) }}</td>
              <td>{{ s.skewness.toFixed(3) }}</td>
              <td>{{ s.excess_kurtosis.toFixed(3) }}</td>
              <td :class="getPSRClass(s.psr)">{{ (s.psr * 100).toFixed(1) }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getApiHeaders } from '@/utils/apiHeaders'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

// --- State ---
const params = ref({ n_splits: 16, annualize: 252, sr_benchmark: 0.0 })
const returnsText = ref('')
const loading = ref(false)
const error = ref('')
const result = ref<any>(null)

const scatterChart = ref<HTMLElement | null>(null)
const logitChart = ref<HTMLElement | null>(null)
let scatterInstance: echarts.ECharts | null = null
let logitInstance: echarts.ECharts | null = null

// --- Parse matrix ---
const parseResult = computed(() => {
  if (!returnsText.value.trim()) return { matrix: null, error: '' }
  const rows = returnsText.value.trim().split('\n').filter(r => r.trim())
  const matrix: number[][] = []
  for (const row of rows) {
    const vals = row.split(',').map(v => parseFloat(v.trim()))
    if (vals.some(isNaN)) return { matrix: null, error: `Не удалось разобрать строку: "${row}"` }
    matrix.push(vals)
  }
  const N = matrix[0].length
  if (matrix.some(r => r.length !== N)) return { matrix: null, error: 'Все строки должны иметь одинаковое число столбцов' }
  if (matrix.length < 20) return { matrix: null, error: `Нужно минимум 20 строк, получено ${matrix.length}` }
  if (N < 2) return { matrix: null, error: 'Нужно минимум 2 стратегии (столбца)' }
  return { matrix, error: '' }
})

const parsedShape = computed(() => {
  if (!parseResult.value.matrix) return null
  return { T: parseResult.value.matrix.length, N: parseResult.value.matrix[0].length }
})

const parseError = computed(() => parseResult.value.error)

// --- Demo data ---
function loadDemo() {
  const T = 100
  const N = 8
  const rows: string[] = []
  const rng = (seed: number) => {
    let s = seed
    return () => { s = (s * 1664525 + 1013904223) & 0xffffffff; return (s >>> 0) / 0xffffffff - 0.5 }
  }
  const rand = rng(42)
  for (let t = 0; t < T; t++) {
    const vals = Array.from({ length: N }, (_, n) => {
      const drift = n === 0 ? 0.001 : 0
      return (rand() * 0.02 + drift).toFixed(5)
    })
    rows.push(vals.join(','))
  }
  returnsText.value = rows.join('\n')
}

// --- Compute ---
async function compute() {
  if (!parseResult.value.matrix) return
  loading.value = true
  error.value = ''
  result.value = null

  try {
    const resp = await fetch(`${API_BASE}/api/pbo/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getApiHeaders() },
      body: JSON.stringify({
        strategy_returns: parseResult.value.matrix,
        n_splits: params.value.n_splits,
        annualize: params.value.annualize,
        sr_benchmark: params.value.sr_benchmark,
      }),
    })
    if (!resp.ok) {
      const d = await resp.json()
      throw new Error(d.detail || `HTTP ${resp.status}`)
    }
    const data = await resp.json()
    result.value = data.result
    await nextTick()
    renderCharts()
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// --- Charts ---
function renderCharts() {
  renderScatter()
  renderLogit()
}

function renderScatter() {
  if (!scatterChart.value || !result.value) return
  scatterInstance?.dispose()
  scatterInstance = echarts.init(scatterChart.value, 'dark')

  const isSR: number[] = result.value.scatter.is_sr
  const oosSR: number[] = result.value.scatter.oos_sr
  const data = isSR.map((v, i) => [v, oosSR[i]])

  const allVals = [...isSR, ...oosSR]
  const minV = Math.min(...allVals)
  const maxV = Math.max(...allVals)

  scatterInstance.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (p: any) => `IS SR: ${p.data[0].toFixed(4)}<br/>OOS SR: ${p.data[1].toFixed(4)}`,
    },
    xAxis: {
      name: 'IS Sharpe Ratio',
      nameLocation: 'middle',
      nameGap: 30,
      splitLine: { lineStyle: { color: '#333' } },
    },
    yAxis: {
      name: 'OOS Sharpe Ratio',
      nameLocation: 'middle',
      nameGap: 40,
      splitLine: { lineStyle: { color: '#333' } },
    },
    series: [
      {
        type: 'scatter',
        data,
        symbolSize: 7,
        itemStyle: { color: '#5b8af5', opacity: 0.75 },
      },
      {
        // 45° diagonal (ideal: IS=OOS)
        type: 'line',
        data: [[minV, minV], [maxV, maxV]],
        lineStyle: { color: '#888', type: 'dashed', width: 1 },
        symbol: 'none',
        tooltip: { show: false },
      },
    ],
    grid: { left: 60, right: 20, top: 20, bottom: 50 },
  })
}

function renderLogit() {
  if (!logitChart.value || !result.value) return
  logitInstance?.dispose()
  logitInstance = echarts.init(logitChart.value, 'dark')

  const { counts, bin_edges, mean } = result.value.logit_hist
  const barData = counts.map((c: number, i: number) => ({
    value: c,
    name: `[${bin_edges[i].toFixed(2)}, ${bin_edges[i + 1].toFixed(2)})`,
  }))

  logitInstance.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', formatter: (p: any) => `${p[0].name}<br/>Частота: ${p[0].value}` },
    xAxis: {
      type: 'category',
      data: bin_edges.slice(0, -1).map((v: number) => v.toFixed(1)),
      name: 'Логит OOS ранга',
      nameLocation: 'middle',
      nameGap: 30,
      axisLabel: { interval: 4 },
    },
    yAxis: { name: 'Частота', splitLine: { lineStyle: { color: '#333' } } },
    series: [
      {
        type: 'bar',
        data: barData,
        itemStyle: {
          color: (p: any) => (bin_edges[p.dataIndex] < 0 ? '#e05c5c' : '#5b8af5'),
        },
      },
    ],
    markLine: {
      data: [{ xAxis: mean.toFixed(1), label: { formatter: `mean=${mean.toFixed(2)}` } }],
    },
    grid: { left: 50, right: 20, top: 20, bottom: 50 },
  })
}

// --- CSS helpers ---
function getPBOClass(pbo: number) {
  if (pbo > 0.75) return 'danger'
  if (pbo > 0.5) return 'warning'
  return 'ok'
}

function getDSRClass(dsr: number) {
  if (dsr > 0.95) return 'ok'
  if (dsr > 0.5) return 'warning'
  return 'danger'
}

function getPSRClass(psr: number) {
  if (psr > 0.95) return 'ok-text'
  if (psr > 0.5) return 'warn-text'
  return 'danger-text'
}

watch(result, async (val) => {
  if (!val) return
  await nextTick()
  renderCharts()
})
</script>

<style scoped>
.pbo-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  color: #e0e0e0;
}

.page-header h1 {
  font-size: 1.6rem;
  font-weight: 600;
  margin: 0 0 4px;
}
.subtitle { color: #888; font-size: 0.85rem; margin: 0; }

.card {
  background: #1a1a2e;
  border: 1px solid #2a2a4a;
  border-radius: 8px;
  padding: 20px;
}

.input-card h2 { font-size: 1.1rem; margin: 0 0 16px; }

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.form-group label { font-size: 0.85rem; color: #aaa; }
.form-group input {
  background: #111;
  border: 1px solid #333;
  border-radius: 4px;
  padding: 8px;
  color: #e0e0e0;
  font-size: 0.9rem;
}

.matrix-input { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.matrix-input label { font-size: 0.85rem; color: #aaa; }
.matrix-input textarea {
  background: #111;
  border: 1px solid #333;
  border-radius: 4px;
  padding: 10px;
  color: #e0e0e0;
  font-size: 0.8rem;
  font-family: monospace;
  resize: vertical;
}
.matrix-info { font-size: 0.8rem; color: #5b8af5; }
.matrix-error { font-size: 0.8rem; color: #e05c5c; }

.hint { font-size: 0.75rem; color: #666; }

.actions { display: flex; gap: 12px; align-items: center; }
.btn-primary {
  background: #5b8af5;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 10px 24px;
  cursor: pointer;
  font-size: 0.9rem;
}
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary {
  background: #2a2a4a;
  color: #aaa;
  border: 1px solid #333;
  border-radius: 6px;
  padding: 10px 18px;
  cursor: pointer;
  font-size: 0.9rem;
}

.error-msg { color: #e05c5c; font-size: 0.9rem; margin-top: 8px; }

/* Verdict Banner */
.verdict-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  border-radius: 8px;
  padding: 16px 20px;
  border-left: 4px solid;
}
.verdict-banner.ok { background: #0d2b1a; border-color: #4caf72; }
.verdict-banner.warning { background: #2b2200; border-color: #f5a623; }
.verdict-banner.danger { background: #2b0d0d; border-color: #e05c5c; }
.verdict-icon { font-size: 1.8rem; }
.verdict-text { display: flex; flex-direction: column; gap: 2px; }
.verdict-text strong { font-size: 1rem; }
.verdict-text span { font-size: 0.85rem; color: #aaa; }

/* KPI */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
}
.kpi-card {
  background: #1a1a2e;
  border: 1px solid #2a2a4a;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}
.kpi-card.ok { border-color: #4caf72; }
.kpi-card.warning { border-color: #f5a623; }
.kpi-card.danger { border-color: #e05c5c; }
.kpi-label { font-size: 0.75rem; color: #888; margin-bottom: 6px; }
.kpi-value { font-size: 1.4rem; font-weight: 600; color: #e0e0e0; }
.kpi-sub { font-size: 0.7rem; color: #666; margin-top: 4px; }

/* Charts */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.chart-card h3 { font-size: 0.9rem; color: #aaa; margin: 0 0 12px; }
.chart { height: 300px; }

/* Table */
.stats-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
.stats-table th {
  text-align: left;
  padding: 8px 12px;
  border-bottom: 1px solid #333;
  color: #888;
  font-weight: 500;
}
.stats-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #222;
}
.best-row { background: #1a2a3a; }
.best-tag {
  font-size: 0.7rem;
  color: #f5a623;
  margin-left: 6px;
}
.ok-text { color: #4caf72; }
.warn-text { color: #f5a623; }
.danger-text { color: #e05c5c; }

h3 { font-size: 1rem; margin: 0 0 12px; }
</style>
