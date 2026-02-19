<template>
  <div class="adv-page">
    <!-- Header -->
    <div class="page-header">
      <h1>Adversarial Stress Testing</h1>
      <p class="subtitle">
        Distributionally Robust worst-case сценарии · EVT tail analysis · Mahalanobis plausibility
      </p>
    </div>

    <!-- Parameters Panel -->
    <div class="card params-card">
      <h2>Параметры</h2>
      <div class="form-grid">
        <div class="form-group">
          <label>κ — интенсивность (mean shift)</label>
          <input type="range" v-model.number="params.kappa" min="0.1" max="3.0" step="0.1" class="range-input" />
          <span class="range-val">{{ params.kappa.toFixed(1) }}</span>
          <span class="hint">Радиус эллипсоидальной неопределённости для μ</span>
        </div>
        <div class="form-group">
          <label>ε — пертурбация ковариации</label>
          <input type="range" v-model.number="params.epsilon" min="0.01" max="0.5" step="0.01" class="range-input" />
          <span class="range-val">{{ params.epsilon.toFixed(2) }}</span>
          <span class="hint">Радиус Фробениуса для Σ*</span>
        </div>
        <div class="form-group">
          <label>MC траектории</label>
          <input type="number" v-model.number="params.nPaths" min="500" max="5000" step="500" />
        </div>
        <div class="form-group">
          <label>Начальный капитал</label>
          <input type="number" v-model.number="params.initialCapital" min="100000" step="100000" />
        </div>
        <div class="form-group">
          <label>Безрисковая ставка</label>
          <input type="number" v-model.number="params.riskFreeRate" min="0" max="0.5" step="0.01" />
        </div>
        <div class="form-group">
          <label>γ (risk aversion)</label>
          <input type="number" v-model.number="params.gamma" min="0.5" max="10" step="0.5" />
        </div>
      </div>

      <div class="actions">
        <button class="btn-primary" @click="runStress" :disabled="loading || positions.length === 0">
          {{ loading ? 'Генерация...' : 'Запустить Adversarial Stress' }}
        </button>
        <span class="asset-count" v-if="positions.length > 0">
          {{ positions.length }} активов в портфеле
        </span>
        <span class="asset-count warn" v-else>Портфель пуст — добавьте активы</span>
      </div>

      <div class="error-msg" v-if="error">{{ error }}</div>
    </div>

    <!-- Results -->
    <template v-if="result">
      <!-- KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi-card danger">
          <div class="kpi-label">Worst-Case VaR 95%</div>
          <div class="kpi-value">{{ formatCurrency(result.adversarial_scenario.var_95) }}</div>
          <div class="kpi-sub">потеря: {{ formatCurrency(params.initialCapital - result.adversarial_scenario.var_95) }}</div>
        </div>
        <div class="kpi-card danger">
          <div class="kpi-label">Worst-Case CVaR 95%</div>
          <div class="kpi-value">{{ formatCurrency(result.adversarial_scenario.cvar_95) }}</div>
          <div class="kpi-sub">expected shortfall</div>
        </div>
        <div class="kpi-card danger">
          <div class="kpi-label">Worst-Case VaR 99%</div>
          <div class="kpi-value">{{ formatCurrency(result.adversarial_scenario.var_99) }}</div>
          <div class="kpi-sub">потеря: {{ formatCurrency(params.initialCapital - result.adversarial_scenario.var_99) }}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Max Drawdown</div>
          <div class="kpi-value">{{ (result.adversarial_scenario.max_drawdown * 100).toFixed(1) }}%</div>
          <div class="kpi-sub">adversarial сценарий</div>
        </div>
        <div class="kpi-card" :class="getPlausClass(result.plausibility.combined_score)">
          <div class="kpi-label">Plausibility</div>
          <div class="kpi-value">{{ (result.plausibility.combined_score * 100).toFixed(0) }}%</div>
          <div class="kpi-sub">Mahalanobis: {{ result.plausibility.mahalanobis_distance.toFixed(2) }}</div>
        </div>
        <div class="kpi-card" v-if="result.evt_tail.fit_success">
          <div class="kpi-label">EVT VaR 99.9%</div>
          <div class="kpi-value">{{ formatCurrency(params.initialCapital - result.evt_tail.var_999) }}</div>
          <div class="kpi-sub">ξ = {{ result.evt_tail.xi.toFixed(3) }} (GPD shape)</div>
        </div>
      </div>

      <!-- Base vs Adversarial Comparison -->
      <div class="card">
        <h3>Base vs Adversarial</h3>
        <table class="comparison-table">
          <thead>
            <tr>
              <th>Метрика</th>
              <th>Base</th>
              <th>Adversarial</th>
              <th>Δ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in comparisonRows" :key="row.label">
              <td>{{ row.label }}</td>
              <td>{{ row.base }}</td>
              <td>{{ row.adv }}</td>
              <td :class="row.deltaClass">{{ row.delta }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Charts Row 1: Distribution + MC Paths -->
      <div class="charts-row">
        <div class="card chart-card">
          <h3>Распределение доходностей: Base vs Adversarial</h3>
          <div ref="distChart" class="chart" />
        </div>
        <div class="card chart-card">
          <h3>MC Trajectories (Adversarial)</h3>
          <div ref="pathsChart" class="chart" />
        </div>
      </div>

      <!-- Charts Row 2: Per-asset shift + Tail -->
      <div class="charts-row">
        <div class="card chart-card">
          <h3>Per-Asset μ Shift (Adversarial − Base)</h3>
          <div ref="shiftChart" class="chart" />
        </div>
        <div class="card chart-card" v-if="result.evt_tail.fit_success">
          <h3>EVT Tail: GPD Fit</h3>
          <div ref="tailChart" class="chart" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { usePortfolioStore } from '@/stores/portfolio'
import { getApiHeaders } from '@/utils/apiHeaders'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
const portfolioStore = usePortfolioStore()

const positions = computed(() => portfolioStore.positions)
const correlationMatrix = computed(() => portfolioStore.correlationMatrix)

// --- State ---
const loading = ref(false)
const error = ref('')
const result = ref<any>(null)

const params = ref({
  kappa: 1.0,
  epsilon: 0.1,
  nPaths: 2000,
  initialCapital: 1000000,
  riskFreeRate: 0.045,
  gamma: 3.0,
})

// Chart refs
const distChart = ref<HTMLElement | null>(null)
const pathsChart = ref<HTMLElement | null>(null)
const shiftChart = ref<HTMLElement | null>(null)
const tailChart = ref<HTMLElement | null>(null)
let distInstance: echarts.ECharts | null = null
let pathsInstance: echarts.ECharts | null = null
let shiftInstance: echarts.ECharts | null = null
let tailInstance: echarts.ECharts | null = null

// --- Helpers ---
const formatCurrency = (v: number) => {
  if (Math.abs(v) >= 1e6) return (v / 1e6).toFixed(2) + 'M'
  if (Math.abs(v) >= 1e3) return (v / 1e3).toFixed(0) + 'K'
  return v.toFixed(0)
}

const getPlausClass = (score: number) => {
  if (score < 0.3) return 'ok'
  if (score < 0.6) return 'warning'
  return 'danger'
}

// --- Comparison Table ---
const comparisonRows = computed(() => {
  if (!result.value) return []
  const b = result.value.base_scenario
  const a = result.value.adversarial_scenario
  const ic = params.value.initialCapital

  const fmt = (v: number) => (v * 100).toFixed(2) + '%'
  const fmtC = (v: number) => formatCurrency(v)
  const delta = (bv: number, av: number, pct: boolean) => {
    const d = av - bv
    return pct ? (d > 0 ? '+' : '') + (d * 100).toFixed(2) + '%' : (d > 0 ? '+' : '') + formatCurrency(d)
  }
  const cls = (bv: number, av: number, lower: boolean) => {
    const d = av - bv
    if (Math.abs(d) < 1e-6) return ''
    return (lower ? d < 0 : d > 0) ? 'text-red' : 'text-green'
  }

  return [
    { label: 'Expected Return', base: fmt(b.expected_return), adv: fmt(a.expected_return), delta: delta(b.expected_return, a.expected_return, true), deltaClass: cls(b.expected_return, a.expected_return, true) },
    { label: 'Volatility', base: fmt(b.volatility), adv: fmt(a.volatility), delta: delta(b.volatility, a.volatility, true), deltaClass: cls(b.volatility, a.volatility, false) },
    { label: 'Sharpe Ratio', base: b.sharpe.toFixed(3), adv: a.sharpe.toFixed(3), delta: (a.sharpe - b.sharpe > 0 ? '+' : '') + (a.sharpe - b.sharpe).toFixed(3), deltaClass: cls(b.sharpe, a.sharpe, true) },
    { label: 'VaR 95%', base: fmtC(b.var_95), adv: fmtC(a.var_95), delta: delta(b.var_95, a.var_95, false), deltaClass: cls(b.var_95, a.var_95, true) },
    { label: 'CVaR 95%', base: fmtC(b.cvar_95), adv: fmtC(a.cvar_95), delta: delta(b.cvar_95, a.cvar_95, false), deltaClass: cls(b.cvar_95, a.cvar_95, true) },
    { label: 'VaR 99%', base: fmtC(b.var_99), adv: fmtC(a.var_99), delta: delta(b.var_99, a.var_99, false), deltaClass: cls(b.var_99, a.var_99, true) },
    { label: 'Max Drawdown', base: fmt(b.max_drawdown), adv: fmt(a.max_drawdown), delta: delta(b.max_drawdown, a.max_drawdown, true), deltaClass: cls(b.max_drawdown, a.max_drawdown, false) },
    { label: 'Mean Final Capital', base: fmtC(b.mean_final), adv: fmtC(a.mean_final), delta: delta(b.mean_final, a.mean_final, false), deltaClass: cls(b.mean_final, a.mean_final, true) },
  ]
})

// --- Build portfolio data for API ---
const buildPayload = () => {
  const pos = positions.value
  const n = pos.length
  const totalAlloc = pos.reduce((s, p) => s + p.allocation, 0)
  const weights = totalAlloc > 0 ? pos.map(p => p.allocation / totalAlloc) : pos.map(() => 1 / n)

  // Build covariance from correlation matrix
  const vols = pos.map(() => 0.20)
  const corrMatrix = correlationMatrix.value
  const covMatrix: number[][] = []
  for (let i = 0; i < n; i++) {
    const row: number[] = []
    for (let j = 0; j < n; j++) {
      const corr = corrMatrix[i]?.values[j] ?? (i === j ? 1 : 0)
      row.push(corr * vols[i] * vols[j])
    }
    covMatrix.push(row)
  }

  const mu = pos.map(p => {
    const dailyRet = p.dayChange / 100
    return 0.05 + dailyRet * 252
  })

  return {
    cov_matrix: covMatrix,
    mu,
    weights,
    kappa: params.value.kappa,
    epsilon: params.value.epsilon,
    n_paths: params.value.nPaths,
    risk_free_rate: params.value.riskFreeRate,
    initial_capital: params.value.initialCapital,
    gamma: params.value.gamma,
    asset_names: pos.map(p => p.symbol),
    seed: 42,
  }
}

// --- Run ---
const runStress = async () => {
  if (positions.value.length === 0) return
  loading.value = true
  error.value = ''
  result.value = null

  try {
    const resp = await fetch(`${API_BASE}/api/adversarial-stress/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getApiHeaders() },
      body: JSON.stringify(buildPayload()),
    })
    if (!resp.ok) {
      const d = await resp.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(d.detail || `HTTP ${resp.status}`)
    }
    result.value = await resp.json()
    await nextTick()
    renderCharts()
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// --- Charts ---
const renderCharts = () => {
  renderDistChart()
  renderPathsChart()
  renderShiftChart()
  renderTailChart()
}

const chartTheme = {
  backgroundColor: 'transparent',
  textStyle: { color: '#d1d5db' },
}

const renderDistChart = () => {
  if (!distChart.value || !result.value) return
  distInstance?.dispose()
  distInstance = echarts.init(distChart.value)

  const baseDist = result.value.return_distributions.base
  const advDist = result.value.return_distributions.adversarial

  const bins = 40
  const allVals = [...baseDist, ...advDist]
  const min = Math.min(...allVals)
  const max = Math.max(...allVals)
  const step = (max - min) / bins

  const histogram = (data: number[]) => {
    const counts = new Array(bins).fill(0)
    for (const v of data) {
      const idx = Math.min(Math.floor((v - min) / step), bins - 1)
      if (idx >= 0) counts[idx]++
    }
    return counts.map((c, i) => [min + (i + 0.5) * step, c / data.length])
  }

  const baseHist = histogram(baseDist)
  const advHist = histogram(advDist)

  distInstance.setOption({
    ...chartTheme,
    tooltip: { trigger: 'axis' },
    legend: { data: ['Base', 'Adversarial'], textStyle: { color: '#d1d5db' } },
    xAxis: { type: 'value', name: 'Return', axisLabel: { formatter: (v: number) => (v * 100).toFixed(0) + '%' } },
    yAxis: { type: 'value', name: 'Density' },
    series: [
      { name: 'Base', type: 'bar', data: baseHist, barWidth: '90%', itemStyle: { color: 'rgba(96,165,250,0.6)' } },
      { name: 'Adversarial', type: 'bar', data: advHist, barWidth: '90%', itemStyle: { color: 'rgba(248,113,113,0.6)' } },
    ],
  })
}

const renderPathsChart = () => {
  if (!pathsChart.value || !result.value) return
  pathsInstance?.dispose()
  pathsInstance = echarts.init(pathsChart.value)

  const mc = result.value.mc_adversarial
  const tGrid = mc.t_grid

  const series: any[] = []

  // Individual paths (faded)
  for (let i = 0; i < Math.min(mc.paths.length, 20); i++) {
    series.push({
      type: 'line',
      data: mc.paths[i].map((v: number, idx: number) => [tGrid[idx], v]),
      lineStyle: { width: 0.5, color: 'rgba(248,113,113,0.15)' },
      symbol: 'none',
      silent: true,
    })
  }

  // Median
  series.push({
    name: 'Median',
    type: 'line',
    data: mc.median_path.map((v: number, idx: number) => [tGrid[idx], v]),
    lineStyle: { width: 2, color: '#f87171' },
    symbol: 'none',
  })

  // Q5-Q95 band
  series.push({
    name: '5%-95% Band',
    type: 'line',
    data: mc.q95_path.map((v: number, idx: number) => [tGrid[idx], v]),
    lineStyle: { width: 1, type: 'dashed', color: '#fca5a5' },
    symbol: 'none',
    areaStyle: { color: 'transparent' },
  })
  series.push({
    type: 'line',
    data: mc.q05_path.map((v: number, idx: number) => [tGrid[idx], v]),
    lineStyle: { width: 1, type: 'dashed', color: '#fca5a5' },
    symbol: 'none',
    areaStyle: { color: 'rgba(248,113,113,0.08)', origin: 'auto' },
  })

  // Base median for comparison
  const baseMc = result.value.mc_base
  series.push({
    name: 'Base Median',
    type: 'line',
    data: baseMc.median_path.map((v: number, idx: number) => [baseMc.t_grid[idx], v]),
    lineStyle: { width: 2, color: '#60a5fa', type: 'dashed' },
    symbol: 'none',
  })

  pathsInstance.setOption({
    ...chartTheme,
    tooltip: { trigger: 'axis' },
    legend: { data: ['Median', 'Base Median'], textStyle: { color: '#d1d5db' } },
    xAxis: { type: 'value', name: 'Years' },
    yAxis: { type: 'value', name: 'Capital', axisLabel: { formatter: (v: number) => formatCurrency(v) } },
    series,
  })
}

const renderShiftChart = () => {
  if (!shiftChart.value || !result.value) return
  shiftInstance?.dispose()
  shiftInstance = echarts.init(shiftChart.value)

  const names = result.value.asset_names
  const shifts = result.value.mu_shift

  shiftInstance.setOption({
    ...chartTheme,
    tooltip: { trigger: 'axis', formatter: (p: any) => {
      const item = Array.isArray(p) ? p[0] : p
      return `${item.name}: ${(item.value * 100).toFixed(2)}%`
    }},
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 45, color: '#9ca3af' } },
    yAxis: { type: 'value', name: 'Δμ', axisLabel: { formatter: (v: number) => (v * 100).toFixed(1) + '%' } },
    series: [{
      type: 'bar',
      data: shifts.map((s: number) => ({
        value: s,
        itemStyle: { color: s < 0 ? '#f87171' : '#34d399' },
      })),
    }],
  })
}

const renderTailChart = () => {
  if (!tailChart.value || !result.value || !result.value.evt_tail.fit_success) return
  tailInstance?.dispose()
  tailInstance = echarts.init(tailChart.value)

  const losses = result.value.return_distributions.adversarial
    .map((r: number) => -r)
    .filter((l: number) => l > 0)
    .sort((a: number, b: number) => a - b)

  const n = losses.length
  const empiricalCdf = losses.map((_: number, i: number) => [losses[i], (i + 1) / n])

  const evt = result.value.evt_tail
  const threshold = evt.threshold / params.value.initialCapital
  const xi = evt.xi
  const beta = evt.beta / params.value.initialCapital

  // GPD survival function
  const gpdPoints: [number, number][] = []
  const tailLosses = losses.filter((l: number) => l >= threshold * 0.5)
  for (const l of tailLosses) {
    const x = l - threshold
    if (x < 0) {
      gpdPoints.push([l, 1.0])
      continue
    }
    let surv: number
    if (Math.abs(xi) < 1e-8) {
      surv = Math.exp(-x / beta)
    } else {
      const arg = 1 + xi * x / beta
      surv = arg > 0 ? Math.pow(arg, -1 / xi) : 0
    }
    gpdPoints.push([l, 1 - surv * (1 - 0.9)])
  }

  tailInstance.setOption({
    ...chartTheme,
    tooltip: { trigger: 'axis' },
    legend: { data: ['Empirical CDF', 'GPD Fit'], textStyle: { color: '#d1d5db' } },
    xAxis: { type: 'value', name: 'Loss', axisLabel: { formatter: (v: number) => (v * 100).toFixed(0) + '%' } },
    yAxis: { type: 'value', name: 'CDF', min: 0, max: 1 },
    series: [
      { name: 'Empirical CDF', type: 'scatter', data: empiricalCdf.filter((_: any, i: number) => i % 3 === 0), symbolSize: 3, itemStyle: { color: '#9ca3af' } },
      { name: 'GPD Fit', type: 'line', data: gpdPoints, lineStyle: { color: '#f87171', width: 2 }, symbol: 'none' },
    ],
  })
}

// Resize
const handleResize = () => {
  distInstance?.resize()
  pathsInstance?.resize()
  shiftInstance?.resize()
  tailInstance?.resize()
}

watch(() => result.value, async (v) => {
  if (v) {
    await nextTick()
    renderCharts()
  }
})

if (typeof window !== 'undefined') {
  window.addEventListener('resize', handleResize)
}
</script>

<style scoped>
.adv-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  color: #e5e7eb;
}

.page-header {
  margin-bottom: 24px;
}
.page-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  background: linear-gradient(135deg, #f87171, #fca5a5);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.subtitle {
  color: #9ca3af;
  font-size: 0.875rem;
  margin-top: 4px;
}

/* Card */
.card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  backdrop-filter: blur(12px);
}
.card h2 { font-size: 1.125rem; font-weight: 600; margin-bottom: 16px; color: #f3f4f6; }
.card h3 { font-size: 1rem; font-weight: 600; margin-bottom: 12px; color: #f3f4f6; }

/* Form */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.form-group label {
  font-size: 0.8rem;
  color: #9ca3af;
  font-weight: 500;
}
.form-group input[type="number"] {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 8px;
  padding: 8px 12px;
  color: #e5e7eb;
  font-size: 0.9rem;
}
.range-input {
  accent-color: #f87171;
  width: 100%;
}
.range-val {
  font-size: 0.85rem;
  font-weight: 600;
  color: #f87171;
}
.hint {
  font-size: 0.7rem;
  color: #6b7280;
}

/* Actions */
.actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}
.btn-primary {
  background: linear-gradient(135deg, #f87171, #dc2626);
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}
.btn-primary:hover:not(:disabled) { opacity: 0.9; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.asset-count { font-size: 0.8rem; color: #9ca3af; }
.asset-count.warn { color: #fbbf24; }

.error-msg {
  margin-top: 12px;
  padding: 8px 12px;
  background: rgba(248,113,113,0.15);
  border: 1px solid rgba(248,113,113,0.3);
  border-radius: 8px;
  color: #fca5a5;
  font-size: 0.85rem;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}
.kpi-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px;
  padding: 16px;
  text-align: center;
}
.kpi-card.danger { border-color: rgba(248,113,113,0.4); background: rgba(248,113,113,0.08); }
.kpi-card.warning { border-color: rgba(251,191,36,0.4); background: rgba(251,191,36,0.06); }
.kpi-card.ok { border-color: rgba(52,211,153,0.4); background: rgba(52,211,153,0.06); }
.kpi-label { font-size: 0.75rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-value { font-size: 1.5rem; font-weight: 700; color: #f3f4f6; margin: 4px 0; }
.kpi-sub { font-size: 0.7rem; color: #6b7280; }

/* Comparison Table */
.comparison-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
.comparison-table th {
  text-align: left;
  padding: 8px 12px;
  color: #9ca3af;
  font-weight: 500;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.comparison-table td {
  padding: 8px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  color: #d1d5db;
}
.comparison-table tr:hover { background: rgba(255,255,255,0.02); }
.text-red { color: #f87171; }
.text-green { color: #34d399; }

/* Charts */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}
.chart-card { min-height: 350px; }
.chart { width: 100%; height: 300px; }

@media (max-width: 900px) {
  .charts-row { grid-template-columns: 1fr; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
