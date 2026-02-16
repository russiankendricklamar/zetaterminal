<!-- src/pages/FactorAnalysis.vue -->
<template>
  <div class="fa-page">

    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">TS vs CS Factor Analysis</h1>
        <p class="page-subtitle">Fama-MacBeth двухшаговый метод: нагрузки β (TS) → риск-премии λ (CS)</p>
      </div>
      <div class="header-right">
        <button @click="analyze" class="btn-primary" :disabled="loading">
          <span v-if="!loading">Анализировать</span>
          <span v-else>↺ Считаю...</span>
        </button>
      </div>
    </div>

    <!-- Input -->
    <div class="input-grid">
      <div class="panel">
        <div class="panel-header">
          <h3>Матрица доходностей (T × N)</h3>
          <span class="hint">Строки — периоды, столбцы — активы. Разделители: пробел/tab/точка с запятой. Первая строка — опционально имена активов.</span>
        </div>
        <textarea v-model="returnsRaw" class="data-textarea" rows="8"
          placeholder="AAPL  MSFT  GOOG&#10;0.01  0.02  0.015&#10;-0.01 0.00  0.005&#10;0.02  0.01  0.018" />
        <div class="has-header-row">
          <label><input type="checkbox" v-model="returnsHasHeader" /> Первая строка — имена активов</label>
        </div>
      </div>
      <div class="panel">
        <div class="panel-header">
          <h3>Матрица факторов (T × K)</h3>
          <span class="hint">Те же T строк, столбцы — факторы (MKT, HML, SMB и др.).</span>
        </div>
        <textarea v-model="factorsRaw" class="data-textarea" rows="8"
          placeholder="MKT   HML&#10;0.005 0.002&#10;-0.003 0.001&#10;0.008 -0.001" />
        <div class="has-header-row">
          <label><input type="checkbox" v-model="factorsHasHeader" /> Первая строка — имена факторов</label>
        </div>
      </div>
    </div>

    <!-- Method explanation -->
    <div class="method-row">
      <div class="method-card ts-card">
        <div class="mc-step">Шаг 1 — Time-Series</div>
        <div class="mc-formula">R_{i,t} = αᵢ + Σ βᵢₖ·Fₖ,ₜ + εᵢ,ₜ</div>
        <div class="mc-desc">Оценка факторных нагрузок β для каждого актива. Даёт attribution риска.</div>
      </div>
      <div class="method-arrow">→</div>
      <div class="method-card cs-card">
        <div class="mc-step">Шаг 2 — Cross-Sectional</div>
        <div class="mc-formula">R̄ᵢ = λ₀ + Σ λₖ·βᵢₖ + αᵢ</div>
        <div class="mc-desc">Оценка факторных премий λ — цена единицы β-риска в CS.</div>
      </div>
      <div class="method-arrow">+</div>
      <div class="method-card grs-card">
        <div class="mc-step">GRS тест</div>
        <div class="mc-formula">F = [(T-N-K)/N] · (1+SR_F²)⁻¹ · α'Σ⁻¹α</div>
        <div class="mc-desc">H₀: все αᵢ = 0 — модель объясняет все доходности.</div>
      </div>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>

    <template v-if="result">

      <!-- KPI row -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">Активов N</div>
          <div class="kpi-value">{{ result.n_assets }}</div>
          <div class="kpi-sub">{{ result.n_periods }} периодов</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Факторов K</div>
          <div class="kpi-value">{{ result.n_factors }}</div>
          <div class="kpi-sub">{{ result.factor_names?.join(', ') }}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">R² TS (avg)</div>
          <div class="kpi-value" :class="result.ts.mean_r2 > 0.5 ? 'val-green' : 'val-yellow'">{{ pct(result.ts.mean_r2) }}</div>
          <div class="kpi-sub">средний по активам</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">R² CS</div>
          <div class="kpi-value">{{ pct(result.cs.r2_cs) }}</div>
          <div class="kpi-sub">cross-sectional</div>
        </div>
        <div class="kpi-card" :class="result.ts.grs.rejects_H0 ? 'kpi-red' : 'kpi-green'">
          <div class="kpi-label">GRS тест</div>
          <div class="kpi-value">{{ result.ts.grs.rejects_H0 ? 'Отклоняет' : 'Не откл.' }}</div>
          <div class="kpi-sub">p = {{ fmtP(result.ts.grs.p_value) }}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Shanken c</div>
          <div class="kpi-value mono">{{ fmt2(result.cs.shanken_c) }}</div>
          <div class="kpi-sub">коррекция SE</div>
        </div>
      </div>

      <!-- TS results + CS results -->
      <div class="results-grid">

        <!-- TS: бета-матрица + alpha -->
        <div class="panel">
          <div class="panel-header">
            <h3>TS: Факторные нагрузки β и альфа</h3>
            <span class="hint">* p&lt;0.05, ** p&lt;0.01</span>
          </div>
          <table class="coef-table">
            <thead>
              <tr>
                <th>Актив</th>
                <th>α</th>
                <th v-for="f in result.factor_names" :key="f">β<sub>{{ f }}</sub></th>
                <th>R²</th>
                <th>Sys%</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in result.ts.assets" :key="a.asset">
                <td>{{ a.asset }}</td>
                <td class="mono" :class="Math.abs(a.t_alpha) > 1.96 ? (a.alpha > 0 ? 'pos' : 'neg') : ''">
                  {{ fmt4(a.alpha) }}{{ Math.abs(a.t_alpha) > 2.58 ? '**' : Math.abs(a.t_alpha) > 1.96 ? '*' : '' }}
                </td>
                <td v-for="(b, k) in a.betas" :key="k" class="mono"
                    :class="Math.abs(a.t_betas[k]) > 1.96 ? 'accent' : ''">
                  {{ fmt3(b) }}{{ Math.abs(a.t_betas[k]) > 2.58 ? '**' : Math.abs(a.t_betas[k]) > 1.96 ? '*' : '' }}
                </td>
                <td class="mono">{{ pct(a.r2) }}</td>
                <td class="mono">{{ pct(result.ts.systematic_share[result.ts.assets.indexOf(a)]) }}</td>
              </tr>
            </tbody>
          </table>

          <!-- GRS details -->
          <div class="grs-box">
            <span class="grs-label">GRS F({{ result.ts.grs.df1 }}, {{ result.ts.grs.df2 }})</span>
            <span class="mono">= {{ fmt2(result.ts.grs.stat) }}</span>
            <span class="grs-label" style="margin-left:12px">p-value</span>
            <span class="mono" :class="result.ts.grs.rejects_H0 ? 'neg' : 'pos'">= {{ fmtP(result.ts.grs.p_value) }}</span>
            <span class="grs-verdict" :class="result.ts.grs.rejects_H0 ? 'neg' : 'pos'">
              {{ result.ts.grs.rejects_H0 ? '→ H₀ отклоняется: значимые альфа' : '→ H₀ не отклоняется: модель адекватна' }}
            </span>
          </div>
        </div>

        <!-- CS: риск-премии λ -->
        <div class="panel">
          <div class="panel-header">
            <h3>CS: Риск-премии λ (Fama-MacBeth)</h3>
          </div>
          <table class="coef-table">
            <thead>
              <tr>
                <th>Параметр</th>
                <th>λ̄</th>
                <th>SE (FM)</th>
                <th>SE (Shanken)</th>
                <th>t-стат</th>
                <th>p-value</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rp in result.cs.risk_premia" :key="rp.name">
                <td>{{ rp.name }}</td>
                <td class="mono accent">{{ fmt4(rp.lambda_mean) }}</td>
                <td class="mono muted">{{ fmt4(rp.se_fm) }}</td>
                <td class="mono">{{ fmt4(rp.se_shanken) }}</td>
                <td class="mono" :class="Math.abs(rp.t_stat) > 1.96 ? 'pos' : 'muted'">{{ fmt2(rp.t_stat) }}</td>
                <td class="mono" :class="rp.p_value < 0.05 ? 'pos' : 'muted'">{{ fmtP(rp.p_value) }}</td>
              </tr>
            </tbody>
          </table>

          <!-- Pricing errors chart -->
          <div class="panel-header" style="margin-top:16px">
            <h3>Ценовые ошибки per asset</h3>
            <span class="hint">αᵢ = E[Rᵢ] − λ'βᵢ</span>
          </div>
          <div ref="peChartEl" class="chart-sm" />

          <!-- Factor stats -->
          <div class="panel-header" style="margin-top:16px"><h3>Статистика факторов</h3></div>
          <table class="stats-table">
            <thead><tr><th>Фактор</th><th>E[F]</th><th>Vol</th><th>Sharpe</th></tr></thead>
            <tbody>
              <tr v-for="fs in result.factor_stats" :key="fs.name">
                <td>{{ fs.name }}</td>
                <td class="mono" :class="fs.mean > 0 ? 'pos' : 'neg'">{{ fmt4(fs.mean) }}</td>
                <td class="mono">{{ fmt4(fs.vol) }}</td>
                <td class="mono" :class="fs.sharpe > 0 ? 'pos' : 'neg'">{{ fmt2(fs.sharpe) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Beta heatmap -->
      <div class="panel">
        <div class="panel-header">
          <h3>Тепловая карта β (активы × факторы)</h3>
        </div>
        <div ref="heatmapEl" class="chart-container" />
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
const factorsRaw = ref('')
const returnsHasHeader = ref(true)
const factorsHasHeader = ref(true)
const loading = ref(false)
const error = ref('')
const result = ref<Record<string, any> | null>(null)

const peChartEl = ref<HTMLElement | null>(null)
const heatmapEl = ref<HTMLElement | null>(null)
let peChart: echarts.ECharts | null = null
let heatmapChart: echarts.ECharts | null = null

// ── Parsers ────────────────────────────────────────────────────────────────────
function parseMatrix(raw: string, hasHeader: boolean): { data: number[][], names: string[] | null } {
  const lines = raw.trim().split('\n').filter(l => l.trim().length > 0)
  if (lines.length === 0) return { data: [], names: null }

  let names: string[] | null = null
  let dataLines = lines

  if (hasHeader && lines.length > 0) {
    names = lines[0].trim().split(/[\s,;\t]+/).filter(s => s.length > 0)
    dataLines = lines.slice(1)
  }

  const data = dataLines.map(line =>
    line.trim().split(/[\s,;\t]+/).filter(s => s.length > 0).map(s => parseFloat(s))
  ).filter(row => row.length > 0 && row.every(n => !isNaN(n)))

  return { data, names }
}

// ── Formatters ─────────────────────────────────────────────────────────────────
const pct = (v: number) => v != null ? (v * 100).toFixed(2) + '%' : '—'
const fmt2 = (v: number) => v?.toFixed(2) ?? '—'
const fmt3 = (v: number) => v?.toFixed(3) ?? '—'
const fmt4 = (v: number) => v?.toFixed(4) ?? '—'
const fmtP = (v: number) => {
  if (v == null) return '—'
  if (v < 0.001) return '<0.001'
  return v.toFixed(3)
}

// ── API ────────────────────────────────────────────────────────────────────────
async function analyze() {
  error.value = ''
  const { data: rData, names: assetNames } = parseMatrix(returnsRaw.value, returnsHasHeader.value)
  const { data: fData, names: factorNames } = parseMatrix(factorsRaw.value, factorsHasHeader.value)

  if (rData.length < 10) { error.value = 'Нужно минимум 10 строк доходностей'; return }
  if (fData.length === 0) { error.value = 'Введите матрицу факторов'; return }
  if (rData.length !== fData.length) { error.value = `Разное число периодов: returns=${rData.length}, factors=${fData.length}`; return }

  loading.value = true
  try {
    const resp = await fetch(`${API_BASE}/api/factor-analysis/analyze`, {
      method: 'POST',
      headers: getApiHeaders(),
      body: JSON.stringify({
        returns: rData,
        factors: fData,
        asset_names: assetNames,
        factor_names: factorNames,
      }),
    })
    if (!resp.ok) {
      const d = await resp.json()
      throw new Error(d.detail || `HTTP ${resp.status}`)
    }
    const d = await resp.json()
    result.value = d.result
    await nextTick()
    renderCharts()
  } catch (e: any) {
    error.value = e.message || 'Неизвестная ошибка'
  } finally {
    loading.value = false
  }
}

// ── Charts ─────────────────────────────────────────────────────────────────────
function renderCharts() {
  renderPricingErrors()
  renderHeatmap()
}

function renderPricingErrors() {
  if (!peChartEl.value || !result.value) return
  if (!peChart) peChart = echarts.init(peChartEl.value, 'dark')

  const errors = result.value.cs.pricing_errors as number[]
  const names = result.value.cs.pricing_errors_assets as string[]
  const colors = errors.map(e => e >= 0 ? '#2ecc71' : '#e74c3c')

  peChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', formatter: (p: any) => `${p[0].name}: ${parseFloat(p[0].value).toFixed(4)}` },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', axisLabel: { formatter: (v: number) => v.toFixed(3) } },
    series: [{
      type: 'bar',
      data: errors.map((v, i) => ({ value: v, itemStyle: { color: colors[i] } })),
      name: 'Pricing error',
    }],
    grid: { left: 50, right: 10, top: 10, bottom: 60 },
  })
}

function renderHeatmap() {
  if (!heatmapEl.value || !result.value) return
  if (!heatmapChart) heatmapChart = echarts.init(heatmapEl.value, 'dark')

  const betas = result.value.ts.beta_matrix as number[][]
  const assetNames = result.value.asset_names as string[]
  const factorNames = result.value.factor_names as string[]
  const N = assetNames.length
  const K = factorNames.length

  // echarts heatmap: data = [[colIdx, rowIdx, value]]
  const data: [number, number, number][] = []
  let minV = Infinity, maxV = -Infinity
  for (let i = 0; i < N; i++) {
    for (let k = 0; k < K; k++) {
      const v = betas[i][k]
      data.push([k, i, parseFloat(v.toFixed(4))])
      if (v < minV) minV = v
      if (v > maxV) maxV = v
    }
  }

  const absMax = Math.max(Math.abs(minV), Math.abs(maxV))

  heatmapChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { formatter: (p: any) => `${assetNames[p.data[1]]} / ${factorNames[p.data[0]]}: β = ${p.data[2]}` },
    xAxis: { type: 'category', data: factorNames, splitArea: { show: true } },
    yAxis: { type: 'category', data: assetNames, splitArea: { show: true } },
    visualMap: {
      min: -absMax, max: absMax, calculable: true,
      orient: 'horizontal', left: 'center', bottom: 0,
      inRange: { color: ['#e74c3c', '#1a1a2e', '#2ecc71'] },
      textStyle: { color: '#aaa' },
    },
    series: [{
      type: 'heatmap',
      data,
      label: { show: N <= 12, formatter: (p: any) => p.data[2].toFixed(2), fontSize: 11 },
    }],
    grid: { left: 80, right: 20, top: 10, bottom: 60 },
  })
}

watch(result, () => nextTick(renderCharts))
</script>

<style scoped>
.fa-page { padding: 24px; color: #e0e0e0; }

.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.header-left { flex: 1; }
.page-title { font-size: 22px; font-weight: 600; margin: 0 0 4px; color: #fff; }
.page-subtitle { font-size: 13px; color: #888; margin: 0; }
.header-right { display: flex; gap: 10px; align-items: center; }

.btn-primary {
  background: #4e8ef7; color: #fff; border: none; padding: 8px 18px;
  border-radius: 6px; cursor: pointer; font-size: 13px;
}
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary:hover:not(:disabled) { background: #3a7af0; }

.input-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.panel { background: #13131f; border: 1px solid #252535; border-radius: 10px; padding: 16px; }
.panel-header { display: flex; align-items: baseline; gap: 10px; margin-bottom: 12px; }
.panel-header h3 { font-size: 14px; font-weight: 600; color: #fff; margin: 0; }
.hint { font-size: 11px; color: #666; }

.data-textarea {
  width: 100%; background: #0d0d1a; border: 1px solid #333; color: #e0e0e0;
  border-radius: 6px; padding: 8px; font-size: 12px; font-family: monospace;
  resize: vertical; box-sizing: border-box;
}
.has-header-row { margin-top: 8px; font-size: 12px; color: #888; }
.has-header-row label { display: flex; align-items: center; gap: 6px; cursor: pointer; }

.method-row { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.method-card {
  flex: 1; background: #13131f; border: 1px solid #252535;
  border-radius: 8px; padding: 12px;
}
.ts-card { border-left: 3px solid #4e8ef7; }
.cs-card { border-left: 3px solid #2ecc71; }
.grs-card { border-left: 3px solid #f39c12; }
.mc-step { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; color: #aaa; }
.ts-card .mc-step { color: #4e8ef7; }
.cs-card .mc-step { color: #2ecc71; }
.grs-card .mc-step { color: #f39c12; }
.mc-formula { font-family: 'Georgia', serif; font-size: 12px; color: #c8d8f0; margin-bottom: 6px; }
.mc-desc { font-size: 11px; color: #666; }
.method-arrow { font-size: 22px; color: #444; flex-shrink: 0; }

.error-banner {
  background: rgba(231,76,60,0.15); border: 1px solid #e74c3c;
  color: #ff6b6b; padding: 10px 14px; border-radius: 6px; margin-bottom: 16px; font-size: 13px;
}

.kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 20px; }
.kpi-card { background: #13131f; border: 1px solid #252535; border-radius: 10px; padding: 14px 12px; text-align: center; }
.kpi-card.kpi-green { border-color: #27ae60; background: rgba(39,174,96,0.08); }
.kpi-card.kpi-red { border-color: #e74c3c; background: rgba(231,76,60,0.08); }
.kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
.kpi-value { font-size: 22px; font-weight: 700; color: #fff; font-family: monospace; }
.kpi-value.val-green { color: #2ecc71; }
.kpi-value.val-yellow { color: #f39c12; }
.kpi-sub { font-size: 11px; color: #777; margin-top: 4px; }

.results-grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 16px; margin-bottom: 20px; }

.coef-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.coef-table th { text-align: center; padding: 5px 6px; color: #888; font-size: 11px; border-bottom: 1px solid #252535; }
.coef-table td { padding: 4px 6px; border-bottom: 1px solid #1c1c2c; text-align: right; }
.coef-table td:first-child { text-align: left; }

.stats-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.stats-table th { text-align: left; padding: 5px 8px; color: #888; font-size: 11px; border-bottom: 1px solid #252535; }
.stats-table td { padding: 4px 8px; border-bottom: 1px solid #1c1c2c; text-align: right; }
.stats-table td:first-child { text-align: left; }

.grs-box {
  margin-top: 12px; padding: 10px 12px; background: #0d0d1a;
  border-radius: 6px; border-left: 3px solid #f39c12; font-size: 13px;
  display: flex; align-items: center; flex-wrap: wrap; gap: 6px;
}
.grs-label { color: #888; }
.grs-verdict { margin-left: auto; font-size: 12px; }

.mono { font-family: monospace; }
.accent { color: #4e8ef7; }
.pos { color: #2ecc71; }
.neg { color: #e74c3c; }
.muted { color: #666; }

.chart-sm { width: 100%; height: 180px; }
.chart-container { width: 100%; height: 300px; }
</style>
