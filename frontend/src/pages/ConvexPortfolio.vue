<template>
  <div class="cp-page">
    <div class="page-header">
      <h1>Convex Portfolio Construction</h1>
      <p class="subtitle">
        Min-Variance · Max-Sharpe · CVaR · Risk Parity (ERC) · Fractional Kelly · Efficient Frontier
      </p>
    </div>

    <!-- Input -->
    <div class="card input-card">
      <h2>Параметры</h2>

      <div class="section-label">Задачи оптимизации</div>
      <div class="objectives-row">
        <label v-for="obj in ALL_OBJECTIVES" :key="obj.key" class="obj-check">
          <input type="checkbox" v-model="selectedObjectives" :value="obj.key" />
          {{ obj.label }}
        </label>
      </div>

      <div class="form-grid">
        <div class="form-group">
          <label>Long-Only</label>
          <select v-model="params.long_only">
            <option :value="true">Да (w ≥ 0)</option>
            <option :value="false">Long-Short</option>
          </select>
        </div>
        <div class="form-group">
          <label>Макс. вес актива</label>
          <input v-model.number="params.max_weight" type="number" min="0.01" max="1" step="0.05" />
          <span class="hint">Ограничение концентрации.</span>
        </div>
        <div class="form-group">
          <label>CVaR уровень (α)</label>
          <input v-model.number="params.cvar_alpha" type="number" min="0.5" max="0.999" step="0.01" />
          <span class="hint">0.95 = 95% CVaR (Expected Shortfall).</span>
        </div>
        <div class="form-group">
          <label>Kelly дробь</label>
          <input v-model.number="params.kelly_fraction" type="number" min="0.1" max="1" step="0.1" />
          <span class="hint">0.5 = half-Kelly, 1 = full Kelly.</span>
        </div>
        <div class="form-group">
          <label>Безрисковая ставка (дн.)</label>
          <input v-model.number="params.risk_free" type="number" step="0.00001" />
        </div>
        <div class="form-group">
          <label>Периодов в году</label>
          <input v-model.number="params.annualize" type="number" min="1" />
          <span class="hint">252 (дн.), 52 (нед.), 12 (мес.).</span>
        </div>
      </div>

      <div class="form-group names-group">
        <label>Названия активов (через запятую)</label>
        <input v-model="assetNamesText" type="text" placeholder="SPY,QQQ,IEF,GLD,BTC" />
      </div>

      <div class="form-group" style="margin-bottom:16px">
        <label>Матрица доходностей (T × N, CSV, строка = период)</label>
        <textarea v-model="returnsText" rows="10"
          placeholder="0.001,0.002,-0.001&#10;-0.001,0.000,0.002&#10;0.002,0.001,0.000" />
        <div class="parse-info" v-if="parsedShape">{{ parsedShape.T }} × {{ parsedShape.N }} (T × N)</div>
        <div class="parse-error" v-if="parseError">{{ parseError }}</div>
      </div>

      <div class="actions">
        <button class="btn-primary" @click="compute" :disabled="loading || !!parseError || !returnsText.trim()">
          {{ loading ? 'Оптимизация...' : 'Оптимизировать' }}
        </button>
        <button class="btn-secondary" @click="loadDemo">Демо (5 активов, 200 дней)</button>
      </div>
      <div class="error-msg" v-if="error">{{ error }}</div>
    </div>

    <!-- Results -->
    <template v-if="result">
      <!-- Summary Table -->
      <div class="card">
        <h3>Сравнение стратегий</h3>
        <table class="summary-table">
          <thead>
            <tr>
              <th>Стратегия</th>
              <th>Sharpe</th>
              <th>Доходность (г.)</th>
              <th>Волатильность (г.)</th>
              <th>CVaR</th>
              <th>Eff. N</th>
              <th>Div. Ratio</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in result.summary" :key="s.objective"
                :class="{ 'best-row': isBestSharpe(s) }">
              <td>
                <span class="obj-badge" :style="{ background: objColor(s.objective) }">
                  {{ objLabel(s.objective) }}
                </span>
              </td>
              <td :class="s.sharpe > 0 ? 'ok-val' : 'danger-val'">{{ s.sharpe.toFixed(3) }}</td>
              <td :class="s.return_annual > 0 ? 'ok-val' : 'danger-val'">{{ pct(s.return_annual) }}</td>
              <td>{{ pct(s.vol_annual) }}</td>
              <td>{{ s.cvar.toFixed(4) }}</td>
              <td>{{ s.effective_n.toFixed(1) }}</td>
              <td>{{ s.diversification_ratio.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Weights Charts Row -->
      <div class="charts-row">
        <div class="card chart-card">
          <h3>Веса портфелей (stacked bar)</h3>
          <div ref="weightsChart" class="chart tall-chart" />
        </div>
        <div class="card chart-card">
          <h3>Вклад риска (Risk Parity)</h3>
          <div ref="rcChart" class="chart tall-chart" />
        </div>
      </div>

      <!-- Efficient Frontier -->
      <div class="card">
        <h3>Эффективная граница (Mean-Variance)</h3>
        <div ref="frontierChart" class="chart" />
      </div>

      <!-- Per-objective detail -->
      <div class="obj-details">
        <div
          v-for="obj in result.objectives_computed"
          :key="obj"
          class="card obj-detail-card"
          v-if="result.results[obj]"
        >
          <h3>
            <span class="obj-badge-sm" :style="{ background: objColor(obj) }">{{ objLabel(obj) }}</span>
          </h3>
          <div class="detail-kpi-row">
            <div class="detail-kpi">
              <div class="kpi-label">Sharpe</div>
              <div class="kpi-val" :class="result.results[obj].sharpe > 0 ? 'ok-val' : 'danger-val'">
                {{ result.results[obj].sharpe.toFixed(3) }}
              </div>
            </div>
            <div class="detail-kpi">
              <div class="kpi-label">CVaR</div>
              <div class="kpi-val">{{ result.results[obj].cvar.toFixed(4) }}</div>
            </div>
            <div class="detail-kpi">
              <div class="kpi-label">Max DD</div>
              <div class="kpi-val danger-val">{{ pct(result.results[obj].max_drawdown) }}</div>
            </div>
            <div class="detail-kpi">
              <div class="kpi-label">Eff. N</div>
              <div class="kpi-val">{{ result.results[obj].effective_n.toFixed(2) }}</div>
            </div>
          </div>
          <div class="weight-bars">
            <div
              v-for="(name, i) in result.asset_names"
              :key="name"
              class="weight-bar-row"
            >
              <span class="asset-name">{{ name }}</span>
              <div class="bar-track">
                <div class="bar-fill"
                  :style="{
                    width: pct(Math.abs(result.results[obj].weights_list[i])),
                    background: result.results[obj].weights_list[i] >= 0 ? '#5b8af5' : '#e05c5c'
                  }" />
              </div>
              <span class="weight-label">{{ pct(result.results[obj].weights_list[i]) }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getApiHeaders } from '@/utils/apiHeaders'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const ALL_OBJECTIVES = [
  { key: 'min_variance', label: 'Min Variance' },
  { key: 'max_sharpe', label: 'Max Sharpe' },
  { key: 'cvar', label: 'Min CVaR' },
  { key: 'risk_parity', label: 'Risk Parity' },
  { key: 'kelly', label: 'Kelly' },
  { key: 'mean_variance', label: 'Mean-Variance' },
]

const OBJ_COLORS: Record<string, string> = {
  min_variance: '#5b8af5',
  max_sharpe: '#4caf72',
  cvar: '#f5a623',
  risk_parity: '#b39ddb',
  kelly: '#80deea',
  mean_variance: '#e05c5c',
  equal_weight: '#888',
}

const selectedObjectives = ref(['min_variance', 'max_sharpe', 'cvar', 'risk_parity', 'kelly'])
const params = ref({
  long_only: true,
  max_weight: 0.4,
  cvar_alpha: 0.95,
  kelly_fraction: 0.5,
  risk_free: 0.0,
  annualize: 252,
})
const assetNamesText = ref('')
const returnsText = ref('')
const loading = ref(false)
const error = ref('')
const result = ref<any>(null)

// chart refs
const weightsChart = ref<HTMLElement | null>(null)
const rcChart = ref<HTMLElement | null>(null)
const frontierChart = ref<HTMLElement | null>(null)
let chartInstances: echarts.ECharts[] = []

// --- Parse ---
const parseResult = computed(() => {
  if (!returnsText.value.trim()) return { matrix: null, error: '' }
  const rows = returnsText.value.trim().split('\n').filter(r => r.trim())
  const matrix: number[][] = []
  for (const row of rows) {
    const vals = row.split(',').map(v => parseFloat(v.trim()))
    if (vals.some(isNaN)) return { matrix: null, error: `Не удалось разобрать: "${row}"` }
    matrix.push(vals)
  }
  const N = matrix[0]?.length ?? 0
  if (matrix.some(r => r.length !== N)) return { matrix: null, error: 'Все строки должны иметь одинаковое число столбцов' }
  if (matrix.length < 30) return { matrix: null, error: `Нужно минимум 30 строк, получено ${matrix.length}` }
  if (N < 2) return { matrix: null, error: 'Нужно минимум 2 актива' }
  return { matrix, error: '' }
})
const parsedShape = computed(() => {
  if (!parseResult.value.matrix) return null
  return { T: parseResult.value.matrix.length, N: parseResult.value.matrix[0].length }
})
const parseError = computed(() => parseResult.value.error)

// --- Demo ---
function loadDemo() {
  const T = 200
  const N = 5
  let seed = 314
  const rnd = () => {
    seed = (seed * 1664525 + 1013904223) & 0x7fffffff
    return (seed / 0x7fffffff) * 2 - 1
  }
  const drifts = [0.0005, 0.0008, 0.0002, 0.0004, 0.0001]
  const vols = [0.012, 0.018, 0.005, 0.008, 0.025]
  const rows: string[] = []
  for (let t = 0; t < T; t++) {
    const vals = drifts.map((d, i) => (d + rnd() * vols[i]).toFixed(5))
    rows.push(vals.join(','))
  }
  returnsText.value = rows.join('\n')
  assetNamesText.value = 'SPY,QQQ,IEF,GLD,BTC'
}

// --- Compute ---
async function compute() {
  if (!parseResult.value.matrix) return
  loading.value = true
  error.value = ''
  result.value = null

  const names = assetNamesText.value.trim()
    ? assetNamesText.value.split(',').map(v => v.trim())
    : undefined

  try {
    const resp = await fetch(`${API_BASE}/api/convex-portfolio/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getApiHeaders() },
      body: JSON.stringify({
        returns: parseResult.value.matrix,
        asset_names: names,
        objectives: selectedObjectives.value,
        ...params.value,
        n_frontier: 30,
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
function disposeAll() { chartInstances.forEach(c => c.dispose()); chartInstances = [] }
function mk(el: HTMLElement | null) {
  if (!el) return null
  const inst = echarts.init(el, 'dark')
  chartInstances.push(inst)
  return inst
}

function renderAllCharts() {
  disposeAll()
  renderWeights()
  renderRC()
  renderFrontier()
}

function renderWeights() {
  const inst = mk(weightsChart.value)
  if (!inst || !result.value) return
  const names = result.value.asset_names
  const objs = result.value.objectives_computed
  const series = names.map((asset: string, i: number) => ({
    name: asset,
    type: 'bar',
    stack: 'weights',
    data: objs.map((obj: string) =>
      +(result.value.results[obj]?.weights_list?.[i] ?? 0).toFixed(4)
    ),
  }))
  inst.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { bottom: 5, textStyle: { color: '#aaa' } },
    xAxis: {
      type: 'category',
      data: objs.map((o: string) => objLabel(o)),
      axisLabel: { color: '#aaa', rotate: 20 },
    },
    yAxis: { name: 'Вес', min: 0, max: 1, splitLine: { lineStyle: { color: '#333' } } },
    series,
    grid: { left: 50, right: 20, top: 10, bottom: 70 },
  })
}

function renderRC() {
  const inst = mk(rcChart.value)
  if (!inst || !result.value) return
  const rpRes = result.value.results['risk_parity'] || result.value.results['min_variance']
  if (!rpRes) return
  const names = result.value.asset_names
  const rc: number[] = rpRes.risk_contributions
  inst.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: (p: any) => `${p.name}: ${(p.value * 100).toFixed(2)}%` },
    series: [{
      type: 'pie',
      radius: ['30%', '65%'],
      data: names.map((n: string, i: number) => ({
        name: n,
        value: +Math.abs(rc[i] ?? 0).toFixed(6),
      })),
      label: { formatter: (p: any) => `${p.name}\n${(p.value * 100).toFixed(1)}%`, color: '#e0e0e0' },
    }],
  })
}

function renderFrontier() {
  const inst = mk(frontierChart.value)
  if (!inst || !result.value) return
  const frontier = result.value.frontier as { vol: number; return: number; sharpe: number }[]

  // overlay individual portfolio points
  const overlayObjs = result.value.objectives_computed.filter(
    (o: string) => result.value.results[o]
  )
  const overlayPoints = overlayObjs.map((obj: string) => {
    const r = result.value.results[obj]
    return { value: [r.vol_annual, r.return_annual], name: objLabel(obj), color: objColor(obj) }
  })

  inst.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (p: any) => {
        if (p.seriesName === 'Frontier') {
          return `Vol: ${(p.data[0] * 100).toFixed(2)}%<br/>Ret: ${(p.data[1] * 100).toFixed(2)}%`
        }
        return `${p.seriesName}<br/>Vol: ${(p.data[0] * 100).toFixed(2)}%<br/>Ret: ${(p.data[1] * 100).toFixed(2)}%`
      },
    },
    legend: { right: 10, top: 10, textStyle: { color: '#aaa' } },
    xAxis: { name: 'Волатильность (г.)', nameLocation: 'middle', nameGap: 30, splitLine: { lineStyle: { color: '#333' } }, axisLabel: { formatter: (v: number) => `${(v * 100).toFixed(0)}%` } },
    yAxis: { name: 'Доходность (г.)', nameLocation: 'middle', nameGap: 45, splitLine: { lineStyle: { color: '#333' } }, axisLabel: { formatter: (v: number) => `${(v * 100).toFixed(1)}%` } },
    series: [
      {
        name: 'Frontier',
        type: 'line',
        data: frontier.map(p => [p.vol, p.return]),
        lineStyle: { color: '#5b8af5', width: 2 },
        itemStyle: { color: '#5b8af5' },
        symbol: 'none',
      },
      ...overlayPoints.map((p: any) => ({
        name: p.name,
        type: 'scatter',
        data: [p.value],
        symbolSize: 12,
        itemStyle: { color: p.color },
      })),
    ],
    grid: { left: 65, right: 20, top: 40, bottom: 50 },
  })
}

// --- Helpers ---
const pct = (v: number) => `${(v * 100).toFixed(2)}%`
const objLabel = (k: string) => ({
  min_variance: 'Min Var', max_sharpe: 'Max SR', cvar: 'CVaR',
  risk_parity: 'Risk Parity', kelly: 'Kelly', mean_variance: 'MV',
  equal_weight: 'Equal Wt',
}[k] ?? k)
const objColor = (k: string) => OBJ_COLORS[k] ?? '#888'
const isBestSharpe = (s: any) => {
  const best = Math.max(...(result.value?.summary ?? []).map((x: any) => x.sharpe))
  return s.sharpe === best && best > 0
}

watch(result, async (val) => {
  if (!val) return
  await nextTick()
  renderAllCharts()
})
</script>

<style scoped>
.cp-page {
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

.card { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 8px; padding: 20px; }
.input-card h2 { font-size: 1.1rem; margin: 0 0 16px; }

.section-label { font-size: 0.8rem; color: #888; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em; }
.objectives-row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }
.obj-check { display: flex; align-items: center; gap: 6px; font-size: 0.85rem; cursor: pointer; }
.obj-check input { accent-color: #5b8af5; }

.form-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px; }
.form-group { display: flex; flex-direction: column; gap: 4px; }
.names-group { margin-bottom: 16px; }
.form-group label { font-size: 0.85rem; color: #aaa; }
.form-group input, .form-group select, .form-group textarea {
  background: #111; border: 1px solid #333; border-radius: 4px;
  padding: 8px; color: #e0e0e0; font-size: 0.9rem;
}
.form-group textarea { font-family: monospace; font-size: 0.8rem; resize: vertical; }
.hint { font-size: 0.75rem; color: #666; }

.parse-info { font-size: 0.8rem; color: #5b8af5; margin-top: 4px; }
.parse-error { font-size: 0.8rem; color: #e05c5c; margin-top: 4px; }

.actions { display: flex; gap: 12px; }
.btn-primary { background: #5b8af5; color: #fff; border: none; border-radius: 6px; padding: 10px 24px; cursor: pointer; font-size: 0.9rem; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary { background: #2a2a4a; color: #aaa; border: 1px solid #333; border-radius: 6px; padding: 10px 18px; cursor: pointer; font-size: 0.9rem; }
.error-msg { color: #e05c5c; font-size: 0.9rem; margin-top: 8px; }

/* Summary table */
.summary-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.summary-table th { text-align: left; padding: 8px 12px; border-bottom: 1px solid #333; color: #888; font-weight: 500; }
.summary-table td { padding: 8px 12px; border-bottom: 1px solid #222; }
.best-row { background: #1a2a3a; }
.obj-badge { font-size: 0.72rem; padding: 2px 8px; border-radius: 10px; color: #fff; font-weight: 600; white-space: nowrap; }
.obj-badge-sm { font-size: 0.78rem; padding: 2px 8px; border-radius: 10px; color: #fff; font-weight: 600; }

/* Charts */
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.chart-card h3, .card > h3 { font-size: 0.9rem; color: #aaa; margin: 0 0 12px; }
.chart { height: 320px; }
.tall-chart { height: 280px; }

/* Colors */
.ok-val { color: #4caf72; }
.danger-val { color: #e05c5c; }

/* Obj detail grid */
.obj-details { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.obj-detail-card h3 { font-size: 0.85rem; margin: 0 0 12px; }
.detail-kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 16px; }
.detail-kpi { text-align: center; }
.kpi-label { font-size: 0.7rem; color: #888; }
.kpi-val { font-size: 1rem; font-weight: 600; margin-top: 2px; }

/* Weight bars */
.weight-bars { display: flex; flex-direction: column; gap: 6px; }
.weight-bar-row { display: grid; grid-template-columns: 48px 1fr 48px; gap: 8px; align-items: center; }
.asset-name { font-size: 0.75rem; color: #aaa; text-align: right; }
.bar-track { height: 10px; background: #111; border-radius: 5px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 5px; transition: width 0.3s; }
.weight-label { font-size: 0.75rem; color: #e0e0e0; }
</style>
