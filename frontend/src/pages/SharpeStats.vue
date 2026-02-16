<!-- src/pages/SharpeStats.vue -->
<template>
  <div class="sharpe-stats-page">

    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Статистика коэффициента Шарпа</h1>
        <p class="page-subtitle">SE, t-тест, PSR, DSR — проверка значимости и поправки на ненормальность</p>
      </div>
      <div class="header-right">
        <select v-model="periodsPerYear" class="control-select">
          <option :value="252">Дневные (252/год)</option>
          <option :value="52">Недельные (52/год)</option>
          <option :value="12">Месячные (12/год)</option>
        </select>
        <button @click="analyze" class="btn-primary" :disabled="loading">
          <span v-if="!loading">Рассчитать</span>
          <span v-else>↺ Считаю...</span>
        </button>
      </div>
    </div>

    <!-- Input + params -->
    <div class="input-grid">
      <div class="panel">
        <div class="panel-header">
          <h3>Ряд доходностей</h3>
          <span class="hint">Вставьте числа через запятую, пробел или перенос строки (в долях: 0.01 = 1%)</span>
        </div>
        <textarea
          v-model="returnsRaw"
          class="returns-textarea"
          placeholder="0.001&#10;-0.002&#10;0.003&#10;..."
          rows="8"
        />
        <div class="input-row">
          <label>Безрисковая ставка (годовая):</label>
          <input v-model.number="riskFreeRate" type="number" step="0.001" min="0" max="1" class="param-input" />
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <h3>Параметры тестирования</h3>
        </div>
        <div class="params-grid">
          <div class="param-row">
            <label>Пороговое SR (для PSR):</label>
            <input v-model.number="benchmarkSr" type="number" step="0.1" class="param-input" />
          </div>
          <div class="param-row">
            <label>Кол-во стратегий N (для DSR):</label>
            <input v-model.number="nTrials" type="number" min="1" step="1" class="param-input" />
          </div>
        </div>
        <div class="formula-box">
          <div class="formula-title">Ключевые формулы</div>
          <div class="formula">SR = μ<sub>e</sub> / σ · √T</div>
          <div class="formula">SE<sub>adj</sub> = √[(1 + SR²/2 − γ₁·SR + γ₂/4) / n]</div>
          <div class="formula">PSR(SR*) = Φ[(SR̂ − SR*)·√(n−1) / √D]</div>
          <div class="formula small">D = 1 − γ₁·SR̂ + (γ₂+1)/4·SR̂²</div>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="error-banner">{{ error }}</div>

    <!-- Results -->
    <template v-if="result">

      <!-- KPI cards -->
      <div class="kpi-grid">
        <div class="kpi-card" :class="srClass">
          <div class="kpi-label">Годовой SR</div>
          <div class="kpi-value">{{ fmt2(result.sr_annual) }}</div>
          <div class="kpi-sub">{{ result.is_significant_5pct ? 'значим на 5%' : 'не значим на 5%' }}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">t-статистика</div>
          <div class="kpi-value">{{ fmt2(result.t_stat) }}</div>
          <div class="kpi-sub">p = {{ fmtP(result.p_value) }}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">SE (ненорм.)</div>
          <div class="kpi-value">{{ fmt3(result.se_nonnormal) }}</div>
          <div class="kpi-sub">IID: {{ fmt3(result.se_iid) }}</div>
        </div>
        <div class="kpi-card" :class="psrClass">
          <div class="kpi-label">PSR</div>
          <div class="kpi-value">{{ pct(result.psr) }}</div>
          <div class="kpi-sub">vs SR* = {{ fmt2(result.benchmark_sr) }}</div>
        </div>
        <div class="kpi-card" :class="dsrClass">
          <div class="kpi-label">DSR</div>
          <div class="kpi-value">{{ pct(result.dsr) }}</div>
          <div class="kpi-sub">N = {{ result.n_trials }} стратегий</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Наблюдений</div>
          <div class="kpi-value">{{ result.n_observations }}</div>
          <div class="kpi-sub">vol = {{ pct(result.vol_annual) }}</div>
        </div>
      </div>

      <!-- Stats table + CI -->
      <div class="results-grid">
        <div class="panel">
          <div class="panel-header"><h3>Распределение доходностей</h3></div>
          <table class="stats-table">
            <tbody>
              <tr><td>Среднегодовая доходность</td><td class="mono">{{ pct(result.mean_annual) }}</td></tr>
              <tr><td>Годовая волатильность</td><td class="mono">{{ pct(result.vol_annual) }}</td></tr>
              <tr><td>Асимметрия (skewness)</td><td class="mono" :class="result.skewness < 0 ? 'neg' : 'pos'">{{ fmt3(result.skewness) }}</td></tr>
              <tr><td>Избыточный эксцесс</td><td class="mono" :class="result.excess_kurtosis > 0 ? 'neg' : 'pos'">{{ fmt3(result.excess_kurtosis) }}</td></tr>
              <tr class="sep"><td>SR (за период)</td><td class="mono">{{ fmt4(result.sr_freq) }}</td></tr>
              <tr><td>SR годовой</td><td class="mono accent">{{ fmt2(result.sr_annual) }}</td></tr>
              <tr><td>SE (IID нормальность)</td><td class="mono">{{ fmt3(result.se_iid) }}</td></tr>
              <tr><td>SE (с поправкой)</td><td class="mono accent">{{ fmt3(result.se_nonnormal) }}</td></tr>
              <tr class="sep"><td>t-статистика</td><td class="mono">{{ fmt2(result.t_stat) }}</td></tr>
              <tr><td>p-value (двустор.)</td><td class="mono" :class="result.p_value < 0.05 ? 'pos' : 'neg'">{{ fmtP(result.p_value) }}</td></tr>
              <tr><td>95% ДИ</td><td class="mono">[{{ fmt2(result.ci_95[0]) }}, {{ fmt2(result.ci_95[1]) }}]</td></tr>
              <tr><td>99% ДИ</td><td class="mono">[{{ fmt2(result.ci_99[0]) }}, {{ fmt2(result.ci_99[1]) }}]</td></tr>
            </tbody>
          </table>
        </div>

        <!-- Null distribution chart -->
        <div class="panel">
          <div class="panel-header"><h3>Распределение SR под H₀</h3></div>
          <div ref="nullChartEl" class="chart-container" />
        </div>
      </div>

      <!-- PSR curve chart -->
      <div class="panel">
        <div class="panel-header">
          <h3>PSR-кривая — вероятность превышения SR*</h3>
          <span class="hint">Вертикальная линия — текущий SR*={{ fmt2(result.benchmark_sr) }}, PSR={{ pct(result.psr) }}</span>
        </div>
        <div ref="psrChartEl" class="chart-container chart-tall" />
      </div>

    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { getApiHeaders } from '@/utils/apiHeaders'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

// ── State ─────────────────────────────────────────────────────────────────────
const returnsRaw = ref('')
const riskFreeRate = ref(0.05)
const periodsPerYear = ref(252)
const benchmarkSr = ref(1.0)
const nTrials = ref(1)
const loading = ref(false)
const error = ref('')
const result = ref<Record<string, any> | null>(null)

const nullChartEl = ref<HTMLElement | null>(null)
const psrChartEl = ref<HTMLElement | null>(null)
let nullChart: echarts.ECharts | null = null
let psrChart: echarts.ECharts | null = null

// ── Helpers ───────────────────────────────────────────────────────────────────
function parseReturns(): number[] {
  return returnsRaw.value
    .replace(/,/g, ' ')
    .split(/\s+/)
    .map(s => s.trim())
    .filter(s => s.length > 0)
    .map(s => parseFloat(s))
    .filter(n => !isNaN(n))
}

const fmt2 = (v: number) => v?.toFixed(2) ?? '—'
const fmt3 = (v: number) => v?.toFixed(3) ?? '—'
const fmt4 = (v: number) => v?.toFixed(4) ?? '—'
const pct = (v: number) => v != null ? (v * 100).toFixed(2) + '%' : '—'
const fmtP = (v: number) => {
  if (v == null) return '—'
  if (v < 0.001) return '<0.001'
  return v.toFixed(3)
}

const srClass = computed(() => {
  if (!result.value) return ''
  const sr = result.value.sr_annual
  if (sr >= 2) return 'kpi-green'
  if (sr >= 1) return 'kpi-yellow'
  return 'kpi-red'
})
const psrClass = computed(() => {
  if (!result.value) return ''
  return result.value.psr >= 0.95 ? 'kpi-green' : result.value.psr >= 0.8 ? 'kpi-yellow' : 'kpi-red'
})
const dsrClass = computed(() => {
  if (!result.value) return ''
  return result.value.dsr >= 0.95 ? 'kpi-green' : result.value.dsr >= 0.8 ? 'kpi-yellow' : 'kpi-red'
})

// ── API call ──────────────────────────────────────────────────────────────────
async function analyze() {
  error.value = ''
  const returns = parseReturns()
  if (returns.length < 10) {
    error.value = 'Нужно минимум 10 наблюдений'
    return
  }
  loading.value = true
  try {
    const resp = await fetch(`${API_BASE}/api/sharpe-stats/analyze`, {
      method: 'POST',
      headers: getApiHeaders(),
      body: JSON.stringify({
        returns,
        risk_free_rate: riskFreeRate.value,
        periods_per_year: periodsPerYear.value,
        benchmark_sr: benchmarkSr.value,
        n_trials: nTrials.value,
      }),
    })
    if (!resp.ok) {
      const data = await resp.json()
      throw new Error(data.detail || `HTTP ${resp.status}`)
    }
    const data = await resp.json()
    result.value = data.result
    await nextTick()
    renderCharts()
  } catch (e: any) {
    error.value = e.message || 'Неизвестная ошибка'
  } finally {
    loading.value = false
  }
}

// ── Charts ────────────────────────────────────────────────────────────────────
function renderCharts() {
  if (!result.value) return
  renderNullChart()
  renderPsrChart()
}

function renderNullChart() {
  if (!nullChartEl.value || !result.value) return
  if (!nullChart) nullChart = echarts.init(nullChartEl.value, 'dark')

  const { x, pdf } = result.value.null_distribution
  const sr = result.value.sr_annual
  const se = result.value.se_nonnormal
  const ci95l = result.value.ci_95[0]
  const ci95r = result.value.ci_95[1]

  nullChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', formatter: (p: any) => `SR = ${parseFloat(p[0].axisValue).toFixed(3)}<br/>pdf = ${p[0].value[1].toFixed(4)}` },
    xAxis: { type: 'value', name: 'SR (годовой)', nameLocation: 'middle', nameGap: 25, axisLine: { lineStyle: { color: '#666' } } },
    yAxis: { type: 'value', name: 'Плотность', axisLine: { lineStyle: { color: '#666' } } },
    series: [
      {
        type: 'line',
        data: x.map((xi: number, i: number) => [xi, pdf[i]]),
        smooth: true,
        lineStyle: { color: '#4e8ef7', width: 2 },
        areaStyle: { color: 'rgba(78,142,247,0.15)' },
        showSymbol: false,
        name: 'H₀: SR=0',
      },
    ],
    markLine: {
      data: [
        { xAxis: sr, lineStyle: { color: '#f5c518', type: 'solid', width: 2 }, label: { formatter: `SR=${sr.toFixed(2)}` } },
        { xAxis: ci95l, lineStyle: { color: '#ff6b6b', type: 'dashed' }, label: { formatter: '95% ДИ' } },
        { xAxis: ci95r, lineStyle: { color: '#ff6b6b', type: 'dashed' }, label: { formatter: '' } },
      ],
    },
    grid: { left: 60, right: 20, top: 20, bottom: 40 },
  })
}

function renderPsrChart() {
  if (!psrChartEl.value || !result.value) return
  if (!psrChart) psrChart = echarts.init(psrChartEl.value, 'dark')

  const { sr_star, psr_values } = result.value.psr_curve
  const benchSr = result.value.benchmark_sr
  const psr = result.value.psr

  psrChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', formatter: (p: any) => `SR* = ${parseFloat(p[0].axisValue).toFixed(2)}<br/>PSR = ${(p[0].value[1] * 100).toFixed(1)}%` },
    xAxis: { type: 'value', name: 'SR* (пороговое значение)', nameLocation: 'middle', nameGap: 25, axisLine: { lineStyle: { color: '#666' } } },
    yAxis: { type: 'value', name: 'PSR(SR*)', min: 0, max: 1, axisLabel: { formatter: (v: number) => (v * 100).toFixed(0) + '%' }, axisLine: { lineStyle: { color: '#666' } } },
    series: [
      {
        type: 'line',
        data: sr_star.map((x: number, i: number) => [x, psr_values[i]]),
        smooth: true,
        lineStyle: { color: '#2ecc71', width: 2 },
        areaStyle: { color: 'rgba(46,204,113,0.12)' },
        showSymbol: false,
        name: 'PSR',
        markLine: {
          data: [
            {
              xAxis: benchSr,
              lineStyle: { color: '#f5c518', type: 'solid', width: 2 },
              label: { formatter: `SR*=${benchSr.toFixed(2)}\nPSR=${(psr * 100).toFixed(1)}%` },
            },
          ],
        },
      },
    ],
    grid: { left: 65, right: 20, top: 20, bottom: 40 },
  })
}

watch(result, () => { nextTick(renderCharts) })
</script>

<style scoped>
.sharpe-stats-page { padding: 24px; color: #e0e0e0; }

.page-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 24px;
}
.header-left { flex: 1; }
.page-title { font-size: 22px; font-weight: 600; margin: 0 0 4px; color: #fff; }
.page-subtitle { font-size: 13px; color: #888; margin: 0; }
.header-right { display: flex; gap: 10px; align-items: center; }

.control-select, .param-input {
  background: #1e1e2e; border: 1px solid #333; color: #e0e0e0;
  padding: 6px 10px; border-radius: 6px; font-size: 13px;
}
.btn-primary {
  background: #4e8ef7; color: #fff; border: none; padding: 8px 18px;
  border-radius: 6px; cursor: pointer; font-size: 13px; white-space: nowrap;
}
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary:hover:not(:disabled) { background: #3a7af0; }

.input-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }

.panel {
  background: #13131f; border: 1px solid #252535; border-radius: 10px; padding: 16px;
}
.panel-header {
  display: flex; align-items: baseline; gap: 10px; margin-bottom: 12px;
}
.panel-header h3 { font-size: 14px; font-weight: 600; color: #fff; margin: 0; }
.hint { font-size: 11px; color: #666; }

.returns-textarea {
  width: 100%; background: #0d0d1a; border: 1px solid #333; color: #e0e0e0;
  border-radius: 6px; padding: 8px; font-size: 12px; font-family: monospace;
  resize: vertical; box-sizing: border-box;
}
.input-row { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 13px; }
.params-grid { display: flex; flex-direction: column; gap: 10px; }
.param-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; }

.formula-box {
  margin-top: 16px; background: #0d0d1a; border: 1px solid #252535;
  border-radius: 6px; padding: 12px;
}
.formula-title { font-size: 11px; color: #666; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em; }
.formula { font-family: 'Georgia', serif; font-size: 13px; color: #b0c4de; margin: 4px 0; }
.formula.small { font-size: 11px; color: #777; }

.error-banner {
  background: rgba(231,76,60,0.15); border: 1px solid #e74c3c;
  color: #ff6b6b; padding: 10px 14px; border-radius: 6px; margin-bottom: 16px; font-size: 13px;
}

.kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 20px; }
.kpi-card {
  background: #13131f; border: 1px solid #252535; border-radius: 10px;
  padding: 14px 12px; text-align: center;
}
.kpi-card.kpi-green { border-color: #27ae60; background: rgba(39,174,96,0.08); }
.kpi-card.kpi-yellow { border-color: #f39c12; background: rgba(243,156,18,0.08); }
.kpi-card.kpi-red { border-color: #e74c3c; background: rgba(231,76,60,0.08); }
.kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
.kpi-value { font-size: 22px; font-weight: 700; color: #fff; font-family: monospace; }
.kpi-sub { font-size: 11px; color: #777; margin-top: 4px; }

.results-grid { display: grid; grid-template-columns: 1fr 1.5fr; gap: 16px; margin-bottom: 20px; }

.stats-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.stats-table td { padding: 5px 8px; border-bottom: 1px solid #1c1c2c; }
.stats-table td:last-child { text-align: right; }
.stats-table tr.sep td { border-top: 1px solid #252535; padding-top: 8px; }
.mono { font-family: monospace; }
.accent { color: #4e8ef7; }
.pos { color: #2ecc71; }
.neg { color: #e74c3c; }

.chart-container { width: 100%; height: 280px; }
.chart-tall { height: 320px; }
</style>
