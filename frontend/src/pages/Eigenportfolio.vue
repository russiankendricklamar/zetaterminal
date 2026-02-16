<!-- src/pages/Eigenportfolio.vue -->
<template>
  <div class="ep-page">

    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Eigenportfolios — PCA декомпозиция</h1>
        <p class="page-subtitle">Σ = QΛQᵀ | Marchenko-Pastur сигнал/шум | Ledoit-Wolf shrinkage</p>
      </div>
      <div class="header-right">
        <label class="toggle-label">
          <input type="checkbox" v-model="useShrinkage" />
          Ledoit-Wolf shrinkage
        </label>
        <input v-model.number="nComponents" type="number" min="1" placeholder="K компонент (авто)"
          class="param-input" style="width:160px" />
        <button @click="decompose" class="btn-primary" :disabled="loading">
          <span v-if="!loading">Разложить</span>
          <span v-else>↺ Считаю...</span>
        </button>
      </div>
    </div>

    <!-- Input -->
    <div class="input-grid">
      <div class="panel">
        <div class="panel-header">
          <h3>Матрица доходностей (T × N)</h3>
          <span class="hint">Строки — периоды, столбцы — активы. Разделители: пробел/tab/;. Первая строка — имена.</span>
        </div>
        <textarea v-model="returnsRaw" class="data-textarea" rows="9"
          placeholder="AAPL  MSFT  GOOG  AMZN&#10;0.01  0.02  0.015  0.008&#10;-0.01 0.00  0.005  -0.002&#10;..." />
        <div class="has-header-row">
          <label><input type="checkbox" v-model="hasHeader" /> Первая строка — имена активов</label>
        </div>
      </div>
      <div class="panel">
        <div class="panel-header">
          <h3>Веса портфеля — необязательно</h3>
          <span class="hint">N весов через пробел/запятую для декомпозиции риска по PC</span>
        </div>
        <textarea v-model="weightsRaw" class="data-textarea" rows="4"
          placeholder="0.25 0.25 0.25 0.25" />
        <div class="formula-box">
          <div class="formula">Σ = QΛQᵀ &nbsp;|&nbsp; λ₊ = σ²(1+√q)²</div>
          <div class="formula small">q = N/T &nbsp;|&nbsp; Σ_LW = (1−α)S + α·μI</div>
          <div class="formula small">Reconstruction: Σ_K = Σ_{k≤K} λₖ qₖqₖᵀ</div>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>

    <template v-if="result">

      <!-- KPI -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">Активов N</div>
          <div class="kpi-value">{{ result.n_assets }}</div>
          <div class="kpi-sub">{{ result.n_periods }} периодов</div>
        </div>
        <div class="kpi-card accent-card">
          <div class="kpi-label">Сигнальных PC</div>
          <div class="kpi-value">{{ result.rmt.n_signal }}</div>
          <div class="kpi-sub">из {{ result.n_components_total }} (RMT)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">PC для 80% var</div>
          <div class="kpi-value">{{ result.thresholds.pc_80pct ?? '—' }}</div>
          <div class="kpi-sub">90%: {{ result.thresholds.pc_90pct ?? '—' }}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">PC1 объясняет</div>
          <div class="kpi-value">{{ pct(result.explained_variance[0]) }}</div>
          <div class="kpi-sub">PC2: {{ pct(result.explained_variance[1]) }}</div>
        </div>
        <div class="kpi-card" :class="result.reconstruction_error < 0.1 ? 'kpi-green' : 'kpi-yellow'">
          <div class="kpi-label">Recon. error</div>
          <div class="kpi-value">{{ pct(result.reconstruction_error) }}</div>
          <div class="kpi-sub">K={{ result.n_components_used }}</div>
        </div>
        <div class="kpi-card" v-if="result.shrinkage.applied">
          <div class="kpi-label">Shrinkage α</div>
          <div class="kpi-value mono">{{ fmt3(result.shrinkage.alpha) }}</div>
          <div class="kpi-sub">Ledoit-Wolf</div>
        </div>
      </div>

      <!-- Scree + RMT eigenvalue distribution -->
      <div class="charts-row">
        <div class="panel">
          <div class="panel-header">
            <h3>Scree plot — объяснённая дисперсия</h3>
          </div>
          <div ref="screeEl" class="chart-md" />
        </div>
        <div class="panel">
          <div class="panel-header">
            <h3>Marchenko-Pastur: сигнал vs шум</h3>
            <span class="hint">λ₊={{ fmt3(result.rmt.lambda_plus) }} — граница шума</span>
          </div>
          <div ref="rmtEl" class="chart-md" />
        </div>
      </div>

      <!-- Loadings heatmap + PC contributions -->
      <div class="results-grid">
        <div class="panel">
          <div class="panel-header">
            <h3>Тепловая карта нагрузок (активы × PC)</h3>
            <span class="hint">Вес каждого актива в каждом eigenportfolio</span>
          </div>
          <div ref="heatmapEl" class="chart-heatmap" />
        </div>

        <div class="panel">
          <!-- Eigenvalue table -->
          <div class="panel-header"><h3>Собственные значения</h3></div>
          <table class="ev-table">
            <thead>
              <tr><th>PC</th><th>λ</th><th>Var%</th><th>Cum%</th><th>RMT</th></tr>
            </thead>
            <tbody>
              <tr v-for="(lam, k) in result.eigenvalues.slice(0, 15)" :key="k"
                  :class="lam > result.rmt.lambda_plus ? 'signal-row' : 'noise-row'">
                <td>PC{{ k + 1 }}</td>
                <td class="mono">{{ fmt4(lam) }}</td>
                <td class="mono">{{ pct(result.explained_variance[k]) }}</td>
                <td class="mono">{{ pct(result.cumulative_variance[k]) }}</td>
                <td>
                  <span class="rmt-tag" :class="lam > result.rmt.lambda_plus ? 'signal' : 'noise'">
                    {{ lam > result.rmt.lambda_plus ? 'signal' : 'noise' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Portfolio risk decomposition -->
          <template v-if="result.portfolio_risk">
            <div class="panel-header" style="margin-top:16px">
              <h3>Декомпозиция риска портфеля</h3>
              <span class="hint">vol = {{ pct(result.portfolio_risk.portfolio_vol) }}</span>
            </div>
            <div ref="riskEl" class="chart-sm" />
          </template>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { getApiHeaders } from '@/utils/apiHeaders'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

// ── State ──────────────────────────────────────────────────────────────────────
const returnsRaw = ref('')
const weightsRaw = ref('')
const hasHeader = ref(true)
const useShrinkage = ref(true)
const nComponents = ref<number | null>(null)
const loading = ref(false)
const error = ref('')
const result = ref<Record<string, any> | null>(null)

const screeEl = ref<HTMLElement | null>(null)
const rmtEl = ref<HTMLElement | null>(null)
const heatmapEl = ref<HTMLElement | null>(null)
const riskEl = ref<HTMLElement | null>(null)

let screeChart: echarts.ECharts | null = null
let rmtChart: echarts.ECharts | null = null
let heatmapChart: echarts.ECharts | null = null
let riskChart: echarts.ECharts | null = null

// ── Parsers ────────────────────────────────────────────────────────────────────
function parseMatrix(raw: string, header: boolean): { data: number[][], names: string[] | null } {
  const lines = raw.trim().split('\n').filter(l => l.trim())
  if (!lines.length) return { data: [], names: null }
  const sep = /[\s,;\t]+/
  let names: string[] | null = null
  let dataLines = lines
  if (header && lines.length > 0) {
    names = lines[0].trim().split(sep).filter(Boolean)
    dataLines = lines.slice(1)
  }
  const data = dataLines
    .map(l => l.trim().split(sep).filter(Boolean).map(Number))
    .filter(r => r.length > 0 && r.every(n => !isNaN(n)))
  return { data, names }
}

function parseWeights(raw: string): number[] | null {
  if (!raw.trim()) return null
  const vals = raw.replace(/,/g, ' ').trim().split(/\s+/).map(Number)
  return vals.every(n => !isNaN(n)) ? vals : null
}

// ── Formatters ─────────────────────────────────────────────────────────────────
const pct = (v: number) => v != null ? (v * 100).toFixed(2) + '%' : '—'
const fmt3 = (v: number) => v?.toFixed(3) ?? '—'
const fmt4 = (v: number) => v?.toFixed(4) ?? '—'

// ── API ────────────────────────────────────────────────────────────────────────
async function decompose() {
  error.value = ''
  const { data: rData, names } = parseMatrix(returnsRaw.value, hasHeader.value)
  if (rData.length < 5) { error.value = 'Нужно минимум 5 строк доходностей'; return }

  const weights = parseWeights(weightsRaw.value)
  if (weights !== null && rData.length > 0 && weights.length !== rData[0].length) {
    error.value = `Длина весов ${weights.length} не совпадает с числом активов ${rData[0].length}`
    return
  }

  loading.value = true
  try {
    const resp = await fetch(`${API_BASE}/api/eigenportfolio/decompose`, {
      method: 'POST',
      headers: getApiHeaders(),
      body: JSON.stringify({
        returns: rData,
        asset_names: names,
        use_shrinkage: useShrinkage.value,
        n_components: nComponents.value || null,
        portfolio_weights: weights,
      }),
    })
    if (!resp.ok) {
      const d = await resp.json()
      throw new Error(d.detail || `HTTP ${resp.status}`)
    }
    result.value = (await resp.json()).result
    await nextTick()
    renderAll()
  } catch (e: any) {
    error.value = e.message || 'Неизвестная ошибка'
  } finally {
    loading.value = false
  }
}

// ── Charts ─────────────────────────────────────────────────────────────────────
function renderAll() {
  renderScree()
  renderRMT()
  renderHeatmap()
  if (result.value?.portfolio_risk) renderRisk()
}

function renderScree() {
  if (!screeEl.value || !result.value) return
  if (!screeChart) screeChart = echarts.init(screeEl.value, 'dark')

  const evPct = result.value.explained_variance.map((v: number) => +(v * 100).toFixed(2))
  const cumPct = result.value.cumulative_variance.map((v: number) => +(v * 100).toFixed(2))
  const nSignal = result.value.rmt.n_signal
  const labels = evPct.map((_: number, i: number) => `PC${i + 1}`)
  const barColors = evPct.map((_: number, i: number) =>
    i < nSignal ? '#4e8ef7' : '#2a2a3e'
  )

  screeChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { data: ['Var%', 'Cum%'], top: 4, textStyle: { color: '#aaa' } },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 45, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Var%', axisLabel: { formatter: (v: number) => v + '%' }, max: Math.max(...evPct) * 1.15 },
      { type: 'value', name: 'Cum%', min: 0, max: 100, axisLabel: { formatter: (v: number) => v + '%' } },
    ],
    series: [
      {
        name: 'Var%', type: 'bar', data: evPct.map((v: number, i: number) => ({ value: v, itemStyle: { color: barColors[i] } })),
        yAxisIndex: 0,
      },
      {
        name: 'Cum%', type: 'line', data: cumPct, yAxisIndex: 1,
        lineStyle: { color: '#f5c518', width: 2 }, showSymbol: false,
        markLine: { data: [{ yAxis: 90, lineStyle: { color: '#2ecc71', type: 'dashed' }, label: { formatter: '90%' } }] },
      },
    ],
    grid: { left: 50, right: 55, top: 40, bottom: 55 },
  })
}

function renderRMT() {
  if (!rmtEl.value || !result.value) return
  if (!rmtChart) rmtChart = echarts.init(rmtEl.value, 'dark')

  const { eigenvalues, rmt } = result.value
  const { lambda_plus, lambda_minus, mp_x, mp_pdf } = rmt

  // Нормализуем PDF для отображения вместе с гистограммой
  const maxEv = Math.max(...eigenvalues)
  const pdfMax = Math.max(...mp_pdf)
  const pdfScale = (maxEv * 0.4) / (pdfMax || 1)

  rmtChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { data: ['Eigenvalues', 'MP pdf'], top: 4, textStyle: { color: '#aaa' } },
    xAxis: { type: 'category', data: eigenvalues.map((_: number, i: number) => `PC${i + 1}`), axisLabel: { rotate: 45, fontSize: 10 } },
    yAxis: { type: 'value', name: 'λ' },
    series: [
      {
        name: 'Eigenvalues',
        type: 'bar',
        data: eigenvalues.map((v: number) => ({
          value: v,
          itemStyle: { color: v > lambda_plus ? '#4e8ef7' : '#e74c3c' },
        })),
        markLine: {
          silent: true,
          data: [
            { yAxis: lambda_plus, lineStyle: { color: '#f5c518', type: 'dashed', width: 1.5 }, label: { formatter: `λ₊=${lambda_plus.toFixed(3)}` } },
          ],
        },
      },
    ],
    grid: { left: 55, right: 20, top: 40, bottom: 55 },
  })
}

function renderHeatmap() {
  if (!heatmapEl.value || !result.value) return
  if (!heatmapChart) heatmapChart = echarts.init(heatmapEl.value, 'dark')

  const loadings = result.value.loadings as { asset: string, loadings: number[] }[]
  const K = result.value.n_components_used
  const pcLabels = Array.from({ length: K }, (_, i) => `PC${i + 1}`)
  const assetLabels = loadings.map(l => l.asset)

  const data: [number, number, number][] = []
  let absMax = 0
  loadings.forEach((l, i) => {
    l.loadings.forEach((v, k) => {
      data.push([k, i, parseFloat(v.toFixed(4))])
      if (Math.abs(v) > absMax) absMax = Math.abs(v)
    })
  })

  heatmapChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { formatter: (p: any) => `${assetLabels[p.data[1]]} / ${pcLabels[p.data[0]]}: ${p.data[2]}` },
    xAxis: { type: 'category', data: pcLabels, splitArea: { show: true } },
    yAxis: { type: 'category', data: assetLabels, splitArea: { show: true } },
    visualMap: {
      min: -absMax, max: absMax, calculable: true,
      orient: 'horizontal', left: 'center', bottom: 0,
      inRange: { color: ['#e74c3c', '#1a1a2e', '#2ecc71'] },
      textStyle: { color: '#aaa' },
    },
    series: [{
      type: 'heatmap', data,
      label: { show: loadings.length <= 15 && K <= 8, formatter: (p: any) => p.data[2].toFixed(2), fontSize: 10 },
    }],
    grid: { left: 80, right: 20, top: 10, bottom: 55 },
  })
}

function renderRisk() {
  if (!riskEl.value || !result.value?.portfolio_risk) return
  if (!riskChart) riskChart = echarts.init(riskEl.value, 'dark')

  const contribs = result.value.portfolio_risk.pc_contributions as { pc: number, share: number, var_contribution: number }[]
  const labels = contribs.map(c => `PC${c.pc}`)
  const shares = contribs.map(c => +(c.share * 100).toFixed(2))
  const colors = contribs.map((c, i) => i < result.value!.rmt.n_signal ? '#4e8ef7' : '#666')

  riskChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', formatter: (p: any) => `PC${p[0].axisValue}: ${p[0].value.toFixed(2)}%` },
    xAxis: { type: 'category', data: labels, axisLabel: { fontSize: 10 } },
    yAxis: { type: 'value', axisLabel: { formatter: (v: number) => v + '%' } },
    series: [{
      type: 'bar',
      data: shares.map((v, i) => ({ value: v, itemStyle: { color: colors[i] } })),
    }],
    grid: { left: 45, right: 10, top: 10, bottom: 30 },
  })
}

watch(result, () => nextTick(renderAll))
</script>

<style scoped>
.ep-page { padding: 24px; color: #e0e0e0; }

.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.header-left { flex: 1; }
.page-title { font-size: 22px; font-weight: 600; margin: 0 0 4px; color: #fff; }
.page-subtitle { font-size: 13px; color: #888; margin: 0; }
.header-right { display: flex; gap: 10px; align-items: center; }

.toggle-label { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #aaa; cursor: pointer; }
.param-input { background: #1e1e2e; border: 1px solid #333; color: #e0e0e0; padding: 6px 10px; border-radius: 6px; font-size: 13px; }
.btn-primary { background: #4e8ef7; color: #fff; border: none; padding: 8px 18px; border-radius: 6px; cursor: pointer; font-size: 13px; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary:hover:not(:disabled) { background: #3a7af0; }

.input-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
.panel { background: #13131f; border: 1px solid #252535; border-radius: 10px; padding: 16px; }
.panel-header { display: flex; align-items: baseline; gap: 10px; margin-bottom: 12px; }
.panel-header h3 { font-size: 14px; font-weight: 600; color: #fff; margin: 0; }
.hint { font-size: 11px; color: #666; }
.data-textarea { width: 100%; background: #0d0d1a; border: 1px solid #333; color: #e0e0e0; border-radius: 6px; padding: 8px; font-size: 12px; font-family: monospace; resize: vertical; box-sizing: border-box; }
.has-header-row { margin-top: 8px; font-size: 12px; color: #888; }
.has-header-row label { display: flex; align-items: center; gap: 6px; cursor: pointer; }
.formula-box { margin-top: 12px; background: #0d0d1a; border: 1px solid #252535; border-radius: 6px; padding: 10px; }
.formula { font-family: 'Georgia', serif; font-size: 13px; color: #b0c4de; margin: 3px 0; }
.formula.small { font-size: 11px; color: #777; }

.error-banner { background: rgba(231,76,60,0.15); border: 1px solid #e74c3c; color: #ff6b6b; padding: 10px 14px; border-radius: 6px; margin-bottom: 16px; font-size: 13px; }

.kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 20px; }
.kpi-card { background: #13131f; border: 1px solid #252535; border-radius: 10px; padding: 14px 12px; text-align: center; }
.kpi-card.accent-card { border-color: #4e8ef7; background: rgba(78,142,247,0.08); }
.kpi-card.kpi-green { border-color: #27ae60; background: rgba(39,174,96,0.08); }
.kpi-card.kpi-yellow { border-color: #f39c12; background: rgba(243,156,18,0.08); }
.kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
.kpi-value { font-size: 22px; font-weight: 700; color: #fff; font-family: monospace; }
.kpi-sub { font-size: 11px; color: #777; margin-top: 4px; }

.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
.results-grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 16px; }

.ev-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.ev-table th { text-align: center; padding: 5px 6px; color: #888; font-size: 11px; border-bottom: 1px solid #252535; }
.ev-table td { padding: 4px 6px; border-bottom: 1px solid #1c1c2c; text-align: right; }
.ev-table td:first-child { text-align: left; }
.signal-row { background: rgba(78,142,247,0.04); }
.noise-row { opacity: 0.65; }

.rmt-tag { display: inline-block; padding: 1px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; }
.rmt-tag.signal { background: rgba(78,142,247,0.2); color: #4e8ef7; }
.rmt-tag.noise { background: rgba(231,76,60,0.15); color: #e74c3c; }

.mono { font-family: monospace; }
.chart-md { width: 100%; height: 280px; }
.chart-heatmap { width: 100%; height: 320px; }
.chart-sm { width: 100%; height: 160px; }
</style>
