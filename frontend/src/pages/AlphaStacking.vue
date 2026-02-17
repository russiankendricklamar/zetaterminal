<template>
  <div class="alpha-page">
    <div class="page-header">
      <h1>Orthogonal Alpha Stacking</h1>
      <p class="subtitle">
        Residualization · IC / IR Analysis · Cross-Signal Diversification · Optimal Combination
      </p>
    </div>

    <!-- Input -->
    <div class="card input-card">
      <h2>Параметры</h2>
      <div class="form-grid">
        <div class="form-group">
          <label>Метод ортогонализации</label>
          <select v-model="params.ortho_method">
            <option value="sequential">Sequential (Gram-Schmidt)</option>
            <option value="pairwise">Pairwise (каждый vs все)</option>
          </select>
          <span class="hint">Sequential — порядок важен (сигнал 1 — базовый).</span>
        </div>
        <div class="form-group">
          <label>Shrinkage к равным весам</label>
          <input v-model.number="params.shrinkage" type="number" min="0" max="1" step="0.05" />
          <span class="hint">0 = чисто IR², 1 = равные веса.</span>
        </div>
        <div class="form-group">
          <label>IC горизонты (через запятую)</label>
          <input v-model="horizonsText" type="text" placeholder="1,5,10,21" />
          <span class="hint">Периоды для decay анализа.</span>
        </div>
      </div>

      <!-- Signal Names -->
      <div class="form-group" style="margin-bottom:16px">
        <label>Названия сигналов (через запятую)</label>
        <input v-model="signalNamesText" type="text" placeholder="Momentum,Reversal,Quality,Value" />
      </div>

      <!-- Panel Data Format Help -->
      <div class="format-help">
        <h4>Формат данных</h4>
        <p>
          Введите данные в виде CSV: каждая строка = один период + один актив,
          столбцы: <code>period, asset, signal_1, signal_2, ..., fwd_return</code>.
          Последний столбец — форвардная доходность, остальные после первых двух — сигналы.
        </p>
        <p class="hint">Пример (2 периода, 3 актива, 2 сигнала):</p>
        <pre class="code-example">0,0,0.5,0.2,0.01
0,1,-0.3,0.4,-0.005
0,2,0.1,-0.1,0.003
1,0,-0.1,0.4,-0.002
1,1,0.3,-0.2,0.008
1,2,0.2,0.3,0.001</pre>
      </div>

      <div class="form-group" style="margin-bottom:16px">
        <label>Данные (period, asset, sig_1, ..., sig_N, fwd_return)</label>
        <textarea v-model="dataText" rows="10" :placeholder="demoPlaceholder" />
        <div class="parse-info" v-if="parsedInfo">{{ parsedInfo }}</div>
        <div class="parse-error" v-if="parseError">{{ parseError }}</div>
      </div>

      <div class="actions">
        <button class="btn-primary" @click="compute" :disabled="loading || !!parseError || !dataText.trim()">
          {{ loading ? 'Вычисление...' : 'Запустить анализ' }}
        </button>
        <button class="btn-secondary" @click="loadDemo">Демо-данные</button>
      </div>
      <div class="error-msg" v-if="error">{{ error }}</div>
    </div>

    <!-- Results -->
    <template v-if="result">
      <!-- KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi-card highlight">
          <div class="kpi-label">IC стэка</div>
          <div class="kpi-value" :class="icClass(result.stack_ic)">
            {{ (result.stack_ic * 100).toFixed(2) }}%
          </div>
          <div class="kpi-sub">mean Spearman rank IC</div>
        </div>
        <div class="kpi-card highlight">
          <div class="kpi-label">IR стэка</div>
          <div class="kpi-value" :class="irClass(result.stack_ir)">
            {{ result.stack_ir.toFixed(3) }}
          </div>
          <div class="kpi-sub">IC / std(IC)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Avg Cross-IC до</div>
          <div class="kpi-value danger-val">{{ (result.avg_cross_ic_before * 100).toFixed(1) }}%</div>
          <div class="kpi-sub">средняя корреляция сигналов</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Avg Cross-IC после</div>
          <div class="kpi-value ok-val">{{ (result.avg_cross_ic_after * 100).toFixed(1) }}%</div>
          <div class="kpi-sub">после ортогонализации</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Diversification Ratio</div>
          <div class="kpi-value">
            {{ result.diversification_ratio > 100 ? '>100×' : result.diversification_ratio.toFixed(1) + '×' }}
          </div>
          <div class="kpi-sub">Cross-IC снижение</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Сигналов / Активов</div>
          <div class="kpi-value">{{ result.n_signals }} / {{ result.n_assets }}</div>
          <div class="kpi-sub">{{ result.n_periods }} периодов</div>
        </div>
      </div>

      <!-- Charts Row 1 -->
      <div class="charts-row">
        <div class="card chart-card">
          <h3>IC / IR: до и после ортогонализации</h3>
          <div ref="irBarChart" class="chart" />
        </div>
        <div class="card chart-card">
          <h3>Веса стэкингового портфеля</h3>
          <div ref="weightsChart" class="chart" />
        </div>
      </div>

      <!-- Cross-IC Heatmaps -->
      <div class="charts-row">
        <div class="card chart-card">
          <h3>Cross-IC до ортогонализации</h3>
          <div ref="crossIcBefore" class="chart" />
        </div>
        <div class="card chart-card">
          <h3>Cross-IC после ортогонализации</h3>
          <div ref="crossIcAfter" class="chart" />
        </div>
      </div>

      <!-- IC Decay -->
      <div class="card">
        <h3>IC Decay по горизонтам</h3>
        <div ref="decayChart" class="chart tall-chart" />
      </div>

      <!-- IC Time Series -->
      <div class="card">
        <h3>IC во времени (горизонт 1 период)</h3>
        <div ref="icTimeChart" class="chart tall-chart" />
      </div>

      <!-- Signal Stats Table -->
      <div class="card">
        <h3>Детали по сигналам</h3>
        <table class="stats-table">
          <thead>
            <tr>
              <th>Сигнал</th>
              <th>IC (raw)</th>
              <th>IC std (raw)</th>
              <th>IR (raw)</th>
              <th>IC (ortho)</th>
              <th>IC std (ortho)</th>
              <th>IR (ortho)</th>
              <th>Вес в стэке</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in result.signal_stats" :key="s.name">
              <td><strong>{{ s.name }}</strong></td>
              <td :class="icClass(s.raw_ic)">{{ (s.raw_ic * 100).toFixed(2) }}%</td>
              <td>{{ (s.raw_ic_std * 100).toFixed(2) }}%</td>
              <td :class="irClass(s.raw_ir)">{{ s.raw_ir.toFixed(3) }}</td>
              <td :class="icClass(s.ortho_ic)">{{ (s.ortho_ic * 100).toFixed(2) }}%</td>
              <td>{{ (s.ortho_ic_std * 100).toFixed(2) }}%</td>
              <td :class="irClass(s.ortho_ir)">{{ s.ortho_ir.toFixed(3) }}</td>
              <td class="weight-col">{{ (s.weight * 100).toFixed(1) }}%</td>
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
const params = ref({ ortho_method: 'sequential', shrinkage: 0.3 })
const horizonsText = ref('1,5,10,21')
const signalNamesText = ref('')
const dataText = ref('')
const loading = ref(false)
const error = ref('')
const result = ref<any>(null)

// chart refs
const irBarChart = ref<HTMLElement | null>(null)
const weightsChart = ref<HTMLElement | null>(null)
const crossIcBefore = ref<HTMLElement | null>(null)
const crossIcAfter = ref<HTMLElement | null>(null)
const decayChart = ref<HTMLElement | null>(null)
const icTimeChart = ref<HTMLElement | null>(null)

let chartInstances: echarts.ECharts[] = []

const demoPlaceholder = `0,0,0.5,0.2,0.01
0,1,-0.3,0.4,-0.005
0,2,0.1,-0.1,0.003
1,0,-0.1,0.4,-0.002
...`

// --- Parse ---
interface ParsedData {
  panel_signals: number[][][]
  panel_fwd_returns: number[][]
  T: number
  N_a: number
  N_s: number
}

const parsed = computed<{ data: ParsedData | null; error: string }>(() => {
  if (!dataText.value.trim()) return { data: null, error: '' }
  const rows = dataText.value.trim().split('\n').filter(r => r.trim())
  if (rows.length === 0) return { data: null, error: '' }

  // parse rows: period, asset, s1, ..., sN, fwd_return
  const parsed_rows: { t: number; a: number; signals: number[]; fwd: number }[] = []
  for (const row of rows) {
    const vals = row.split(',').map(v => parseFloat(v.trim()))
    if (vals.some(isNaN)) return { data: null, error: `Не удалось разобрать: "${row}"` }
    if (vals.length < 4) return { data: null, error: 'Нужно минимум 4 столбца: period, asset, signal, fwd_return' }
    parsed_rows.push({
      t: vals[0],
      a: vals[1],
      signals: vals.slice(2, -1),
      fwd: vals[vals.length - 1],
    })
  }

  const T = Math.max(...parsed_rows.map(r => r.t)) + 1
  const N_a = Math.max(...parsed_rows.map(r => r.a)) + 1
  const N_s = parsed_rows[0].signals.length

  if (N_s < 2) return { data: null, error: 'Нужно минимум 2 сигнала' }
  if (T < 10) return { data: null, error: `Нужно минимум 10 периодов, получено ${T}` }

  // Build T × N_a × N_s and T × N_a
  const panel_signals = Array.from({ length: T }, () =>
    Array.from({ length: N_a }, () => Array(N_s).fill(0))
  )
  const panel_fwd = Array.from({ length: T }, () => Array(N_a).fill(0))

  for (const r of parsed_rows) {
    if (r.t < T && r.a < N_a) {
      panel_signals[r.t][r.a] = r.signals
      panel_fwd[r.t][r.a] = r.fwd
    }
  }

  return { data: { panel_signals, panel_fwd_returns: panel_fwd, T, N_a, N_s }, error: '' }
})

const parsedInfo = computed(() => {
  if (!parsed.value.data) return ''
  const { T, N_a, N_s } = parsed.value.data
  return `Распознано: ${T} периодов × ${N_a} активов × ${N_s} сигналов`
})

const parseError = computed(() => parsed.value.error)

// --- Demo ---
function loadDemo() {
  const T = 40
  const N_a = 8
  const N_s = 4
  const rows: string[] = []
  let seed = 1234
  const rnd = () => {
    seed = (seed * 1664525 + 1013904223) & 0x7fffffff
    return (seed / 0x7fffffff) * 2 - 1
  }

  // true signal
  for (let t = 0; t < T; t++) {
    for (let a = 0; a < N_a; a++) {
      const true_v = rnd() * 0.02
      const signals = Array.from({ length: N_s }, (_, k) =>
        (true_v * (0.6 + k * 0.1) + rnd() * 0.1).toFixed(4)
      )
      const fwd = (true_v * 0.5 + rnd() * 0.01).toFixed(5)
      rows.push([t, a, ...signals, fwd].join(','))
    }
  }
  dataText.value = rows.join('\n')
  signalNamesText.value = 'Momentum,Reversal,Quality,Value'
}

// --- Compute ---
async function compute() {
  if (!parsed.value.data) return
  loading.value = true
  error.value = ''
  result.value = null

  const horizons = horizonsText.value
    .split(',')
    .map(v => parseInt(v.trim()))
    .filter(v => !isNaN(v) && v > 0)

  const names = signalNamesText.value.trim()
    ? signalNamesText.value.split(',').map(v => v.trim())
    : undefined

  try {
    const resp = await fetch(`${API_BASE}/api/alpha-stacking/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getApiHeaders() },
      body: JSON.stringify({
        panel_signals: parsed.value.data!.panel_signals,
        panel_fwd_returns: parsed.value.data!.panel_fwd_returns,
        signal_names: names,
        ortho_method: params.value.ortho_method,
        ic_horizons: horizons,
        shrinkage: params.value.shrinkage,
      }),
    })
    if (!resp.ok) {
      const d = await resp.json()
      throw new Error(d.detail || `HTTP ${resp.status}`)
    }
    const data = await resp.json()
    result.value = data.result
    await nextTick()
    renderAllCharts()
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// --- Charts ---
function disposeAll() {
  chartInstances.forEach(c => c.dispose())
  chartInstances = []
}

function initChart(el: HTMLElement | null): echarts.ECharts | null {
  if (!el) return null
  const inst = echarts.init(el, 'dark')
  chartInstances.push(inst)
  return inst
}

function renderAllCharts() {
  disposeAll()
  renderIRBar()
  renderWeights()
  renderCrossIC(crossIcBefore.value, result.value.cross_ic_before, 'До ортогонализации')
  renderCrossIC(crossIcAfter.value, result.value.cross_ic_after, 'После ортогонализации')
  renderDecay()
  renderICTime()
}

function renderIRBar() {
  const inst = initChart(irBarChart.value)
  if (!inst) return
  const names = result.value.signal_stats.map((s: any) => s.name)
  const rawIC = result.value.signal_stats.map((s: any) => +(s.raw_ic * 100).toFixed(3))
  const orthoIC = result.value.signal_stats.map((s: any) => +(s.ortho_ic * 100).toFixed(3))
  const rawIR = result.value.signal_stats.map((s: any) => +s.raw_ir.toFixed(3))
  const orthoIR = result.value.signal_stats.map((s: any) => +s.ortho_ir.toFixed(3))

  inst.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { top: 5, textStyle: { color: '#aaa' } },
    xAxis: { type: 'category', data: names, axisLabel: { color: '#aaa' } },
    yAxis: [
      { name: 'IC (%)', splitLine: { lineStyle: { color: '#333' } } },
      { name: 'IR', splitLine: { show: false } },
    ],
    series: [
      { name: 'IC raw', type: 'bar', data: rawIC, itemStyle: { color: '#5b8af5', opacity: 0.6 } },
      { name: 'IC ortho', type: 'bar', data: orthoIC, itemStyle: { color: '#5b8af5' } },
      { name: 'IR raw', type: 'line', yAxisIndex: 1, data: rawIR, lineStyle: { type: 'dashed' }, itemStyle: { color: '#f5a623' } },
      { name: 'IR ortho', type: 'line', yAxisIndex: 1, data: orthoIR, itemStyle: { color: '#4caf72' } },
    ],
    grid: { left: 55, right: 55, top: 40, bottom: 40 },
  })
}

function renderWeights() {
  const inst = initChart(weightsChart.value)
  if (!inst) return
  const stats = result.value.signal_stats
  inst.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: (p: any) => `${p.name}: ${(p.value * 100).toFixed(1)}%` },
    series: [{
      type: 'pie',
      radius: ['35%', '70%'],
      data: stats.map((s: any) => ({ name: s.name, value: +(s.weight).toFixed(4) })),
      label: { formatter: (p: any) => `${p.name}\n${(p.value * 100).toFixed(1)}%`, color: '#e0e0e0' },
    }],
  })
}

function renderCrossIC(el: HTMLElement | null, matrix: number[][], _title: string) {
  const inst = initChart(el)
  if (!inst || !result.value) return
  const names = result.value.signal_stats.map((s: any) => s.name)
  const N = names.length
  const data: [number, number, number][] = []
  for (let i = 0; i < N; i++) {
    for (let j = 0; j < N; j++) {
      data.push([j, i, +matrix[i][j].toFixed(3)])
    }
  }

  inst.setOption({
    backgroundColor: 'transparent',
    tooltip: { formatter: (p: any) => `${names[p.data[1]]} vs ${names[p.data[0]]}: ${p.data[2]}` },
    xAxis: { type: 'category', data: names, axisLabel: { color: '#aaa', rotate: 30 } },
    yAxis: { type: 'category', data: names, axisLabel: { color: '#aaa' } },
    visualMap: {
      min: -1, max: 1, calculable: true,
      inRange: { color: ['#e05c5c', '#1a1a2e', '#4caf72'] },
      textStyle: { color: '#aaa' },
      right: 5, top: 'middle',
    },
    series: [{
      type: 'heatmap',
      data,
      label: { show: true, formatter: (p: any) => p.data[2].toFixed(2), color: '#fff', fontSize: 11 },
    }],
    grid: { left: 80, right: 80, top: 10, bottom: 50 },
  })
}

function renderDecay() {
  const inst = initChart(decayChart.value)
  if (!inst || !result.value) return
  const decay = result.value.ic_decay
  const horizons = result.value.ic_horizons
  const signalNames = [...result.value.signal_stats.map((s: any) => s.name), 'Stacked']
  const colors = ['#5b8af5', '#4caf72', '#f5a623', '#e05c5c', '#b39ddb', '#80deea']

  const series = signalNames.map((name, idx) => ({
    name,
    type: 'line',
    data: horizons.map((h: string) => decay[h]?.[name] ?? null),
    lineStyle: name === 'Stacked' ? { width: 2.5 } : { type: 'dashed', width: 1.5 },
    itemStyle: { color: colors[idx % colors.length] },
    symbol: 'circle',
    symbolSize: 6,
  }))

  inst.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { top: 5, textStyle: { color: '#aaa' } },
    xAxis: { type: 'category', data: horizons, name: 'Горизонт (периодов)', nameLocation: 'middle', nameGap: 30, axisLabel: { color: '#aaa' } },
    yAxis: { name: 'Mean IC', splitLine: { lineStyle: { color: '#333' } } },
    series,
    grid: { left: 60, right: 20, top: 40, bottom: 50 },
  })
}

function renderICTime() {
  const inst = initChart(icTimeChart.value)
  if (!inst || !result.value) return
  const ts = result.value.ic_time_series
  const keys = Object.keys(ts)
  const T = ts[keys[0]]?.length ?? 0
  const xData = Array.from({ length: T }, (_, i) => i + 1)
  const colors = ['#4caf72', '#5b8af5', '#f5a623', '#e05c5c', '#b39ddb', '#80deea']

  const series = keys.map((name, idx) => ({
    name,
    type: 'line',
    data: ts[name],
    lineStyle: name === 'stacked' ? { width: 2 } : { type: 'dashed', width: 1, opacity: 0.7 },
    itemStyle: { color: colors[idx % colors.length] },
    symbol: 'none',
    smooth: false,
  }))

  inst.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { top: 5, textStyle: { color: '#aaa' } },
    xAxis: { type: 'category', data: xData, name: 'Период', nameLocation: 'middle', nameGap: 25, axisLabel: { color: '#aaa' } },
    yAxis: { name: 'IC', splitLine: { lineStyle: { color: '#333' } } },
    series,
    grid: { left: 55, right: 20, top: 40, bottom: 50 },
  })
}

// --- CSS helpers ---
function icClass(ic: number) {
  if (ic > 0.05) return 'ok-val'
  if (ic > 0) return 'warn-val'
  return 'danger-val'
}
function irClass(ir: number) {
  if (ir > 0.5) return 'ok-val'
  if (ir > 0) return 'warn-val'
  return 'danger-val'
}

watch(result, async (val) => {
  if (!val) return
  await nextTick()
  renderAllCharts()
})
</script>

<style scoped>
.alpha-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  color: #e0e0e0;
}

.page-header h1 { font-size: 1.6rem; font-weight: 600; margin: 0 0 4px; }
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
.form-group { display: flex; flex-direction: column; gap: 4px; }
.form-group label { font-size: 0.85rem; color: #aaa; }
.form-group input, .form-group select, .form-group textarea {
  background: #111;
  border: 1px solid #333;
  border-radius: 4px;
  padding: 8px;
  color: #e0e0e0;
  font-size: 0.9rem;
}
.form-group textarea { font-family: monospace; font-size: 0.8rem; resize: vertical; }
.hint { font-size: 0.75rem; color: #666; }

.format-help {
  background: #0f0f22;
  border: 1px solid #2a2a4a;
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 16px;
}
.format-help h4 { margin: 0 0 8px; font-size: 0.9rem; color: #aaa; }
.format-help p { margin: 4px 0; font-size: 0.8rem; color: #999; }
.code-example {
  background: #111;
  padding: 8px;
  border-radius: 4px;
  font-size: 0.78rem;
  color: #7ecfff;
  margin: 6px 0 0;
}

.parse-info { font-size: 0.8rem; color: #5b8af5; margin-top: 4px; }
.parse-error { font-size: 0.8rem; color: #e05c5c; margin-top: 4px; }

.actions { display: flex; gap: 12px; align-items: center; }
.btn-primary {
  background: #5b8af5; color: #fff; border: none;
  border-radius: 6px; padding: 10px 24px; cursor: pointer; font-size: 0.9rem;
}
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary {
  background: #2a2a4a; color: #aaa; border: 1px solid #333;
  border-radius: 6px; padding: 10px 18px; cursor: pointer; font-size: 0.9rem;
}
.error-msg { color: #e05c5c; font-size: 0.9rem; margin-top: 8px; }

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
.kpi-card.highlight { border-color: #5b8af5; }
.kpi-label { font-size: 0.75rem; color: #888; margin-bottom: 6px; }
.kpi-value { font-size: 1.4rem; font-weight: 600; }
.kpi-sub { font-size: 0.7rem; color: #666; margin-top: 4px; }

/* Charts */
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.chart-card h3, .card > h3 { font-size: 0.9rem; color: #aaa; margin: 0 0 12px; }
.chart { height: 280px; }
.tall-chart { height: 240px; }

/* Colors */
.ok-val { color: #4caf72; }
.warn-val { color: #f5a623; }
.danger-val { color: #e05c5c; }

/* Table */
.stats-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.stats-table th {
  text-align: left; padding: 8px 12px;
  border-bottom: 1px solid #333; color: #888; font-weight: 500;
}
.stats-table td { padding: 8px 12px; border-bottom: 1px solid #222; }
.weight-col { color: #5b8af5; font-weight: 600; }
</style>
