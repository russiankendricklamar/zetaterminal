<!-- src/pages/HARModel.vue -->
<template>
  <div class="har-page">

    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">HAR Model — Прогнозирование волатильности</h1>
        <p class="page-subtitle">Heterogeneous AutoRegressive модель: β₀ + β_d·RV_t + β_w·RV̄_{t-5} + β_m·RV̄_{t-22}</p>
      </div>
      <div class="header-right">
        <label class="toggle-label">
          <input type="checkbox" v-model="logTransform" />
          log(RV)
        </label>
        <select v-model="trainRatio" class="control-select">
          <option :value="0.7">70/30 split</option>
          <option :value="0.8">80/20 split</option>
          <option :value="0.9">90/10 split</option>
        </select>
        <button @click="fitModel" class="btn-primary" :disabled="loading">
          <span v-if="!loading">Оценить</span>
          <span v-else>↺ Считаю...</span>
        </button>
      </div>
    </div>

    <!-- Input -->
    <div class="input-grid">
      <div class="panel">
        <div class="panel-header">
          <h3>Ряд RV (Realized Variance)</h3>
          <span class="hint">Ежедневные значения через запятую/пробел/перенос строки (> 0)</span>
        </div>
        <textarea v-model="rvRaw" class="data-textarea" placeholder="0.0001&#10;0.00015&#10;0.00012&#10;..." rows="7" />
      </div>
      <div class="panel">
        <div class="panel-header">
          <h3>BV (Bipower Variation) — необязательно</h3>
          <span class="hint">Для HAR-RV-CJ модели с компонентом скачков</span>
        </div>
        <textarea v-model="bvRaw" class="data-textarea" placeholder="0.00009&#10;0.00013&#10;0.00011&#10;..." rows="7" />
      </div>
    </div>

    <!-- Model description -->
    <div class="model-desc-row">
      <div class="formula-card" :class="{ active: !logTransform }">
        <div class="fc-title">HAR-RV</div>
        <div class="fc-formula">RV_t = β₀ + β_d·RV_{t-1} + β_w·RV̄_{t-5} + β_m·RV̄_{t-22} + ε_t</div>
      </div>
      <div class="formula-card" :class="{ active: logTransform }">
        <div class="fc-title">Log-HAR</div>
        <div class="fc-formula">log(RV_t) = β₀ + β_d·log(RV_{t-1}) + β_w·log(RV̄_{t-5}) + β_m·log(RV̄_{t-22})</div>
      </div>
      <div class="formula-card" :class="{ active: bvParsed.length > 0 }">
        <div class="fc-title">HAR-RV-CJ</div>
        <div class="fc-formula">RV_t = β₀ + β_C·C_{t-1} + β_J·J_{t-1} + β_w·C̄_{t-5} + β_m·C̄_{t-22}</div>
      </div>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>

    <template v-if="result">

      <!-- KPI -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">R² (train)</div>
          <div class="kpi-value" :class="result.r2 > 0.7 ? 'val-green' : result.r2 > 0.4 ? 'val-yellow' : 'val-red'">{{ pct(result.r2) }}</div>
          <div class="kpi-sub">скорр.: {{ pct(result.r2_adj) }}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">R² (full)</div>
          <div class="kpi-value">{{ pct(result.r2_full) }}</div>
          <div class="kpi-sub">вся выборка</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">IS RMSE</div>
          <div class="kpi-value mono">{{ sci(result.is_metrics?.rmse) }}</div>
          <div class="kpi-sub">QLIKE: {{ fmt4(result.is_metrics?.qlike) }}</div>
        </div>
        <div class="kpi-card" v-if="result.oos_metrics?.rmse != null">
          <div class="kpi-label">OOS RMSE</div>
          <div class="kpi-value mono">{{ sci(result.oos_metrics.rmse) }}</div>
          <div class="kpi-sub">QLIKE: {{ fmt4(result.oos_metrics.qlike) }}</div>
        </div>
        <div class="kpi-card accent-card">
          <div class="kpi-label">Прогноз h=1</div>
          <div class="kpi-value">{{ pct(result.forecasts?.h1?.vol_annual) }}</div>
          <div class="kpi-sub">годовая vol</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Прогноз h=22</div>
          <div class="kpi-value">{{ pct(result.forecasts?.h22?.vol_annual) }}</div>
          <div class="kpi-sub">месячный горизонт</div>
        </div>
      </div>

      <!-- Coefficients + Forecasts -->
      <div class="results-grid">
        <div class="panel">
          <div class="panel-header"><h3>Коэффициенты HAR-RV (Newey-West SE)</h3></div>
          <table class="coef-table">
            <thead>
              <tr>
                <th>Параметр</th>
                <th>β</th>
                <th>SE</th>
                <th>t-стат</th>
                <th>p-value</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in result.coefficients" :key="c.name">
                <td>{{ c.name }}</td>
                <td class="mono">{{ fmt4(c.beta) }}</td>
                <td class="mono">{{ fmt4(c.se) }}</td>
                <td class="mono" :class="Math.abs(c.t_stat) > 1.96 ? 'pos' : 'muted'">{{ fmt2(c.t_stat) }}</td>
                <td class="mono" :class="c.p_value < 0.05 ? 'pos' : 'muted'">{{ fmtP(c.p_value) }}</td>
                <td>{{ c.significant ? '***' : '' }}</td>
              </tr>
            </tbody>
          </table>

          <!-- CJ coefficients if available -->
          <template v-if="result.cj_model">
            <div class="panel-header" style="margin-top:16px"><h3>HAR-RV-CJ коэффициенты</h3></div>
            <table class="coef-table">
              <thead>
                <tr><th>Параметр</th><th>β</th><th>SE</th><th>t-стат</th><th>p-value</th></tr>
              </thead>
              <tbody>
                <tr v-for="c in result.cj_model.coefficients" :key="c.name">
                  <td>{{ c.name }}</td>
                  <td class="mono">{{ fmt4(c.beta) }}</td>
                  <td class="mono">{{ fmt4(c.se) }}</td>
                  <td class="mono" :class="Math.abs(c.t_stat) > 1.96 ? 'pos' : 'muted'">{{ fmt2(c.t_stat) }}</td>
                  <td class="mono" :class="c.p_value < 0.05 ? 'pos' : 'muted'">{{ fmtP(c.p_value) }}</td>
                </tr>
              </tbody>
            </table>
            <div class="r2-row">R² = {{ pct(result.cj_model.r2) }} &nbsp;|&nbsp; R²_adj = {{ pct(result.cj_model.r2_adj) }}</div>
          </template>
        </div>

        <!-- Forecast panel -->
        <div class="panel">
          <div class="panel-header"><h3>Прогнозы волатильности</h3></div>
          <div class="forecast-cards">
            <div v-for="(fcast, key) in result.forecasts" :key="key" class="fcast-card">
              <div class="fcast-h">h = {{ fcast.horizon_days }} {{ fcast.horizon_days === 1 ? 'день' : fcast.horizon_days < 5 ? 'дня' : 'дней' }}</div>
              <div class="fcast-vol">{{ pct(fcast.vol_annual) }}</div>
              <div class="fcast-rv">RV = {{ sci(fcast.rv) }}</div>
            </div>
          </div>

          <div class="metrics-comparison" v-if="result.oos_metrics?.rmse != null">
            <div class="panel-header" style="margin-top:16px"><h3>IS vs OOS сравнение</h3></div>
            <table class="stats-table">
              <thead><tr><th>Метрика</th><th>IS (train)</th><th>OOS (test)</th></tr></thead>
              <tbody>
                <tr>
                  <td>RMSE</td>
                  <td class="mono">{{ sci(result.is_metrics.rmse) }}</td>
                  <td class="mono" :class="result.oos_metrics.rmse > result.is_metrics.rmse * 1.5 ? 'neg' : 'pos'">{{ sci(result.oos_metrics.rmse) }}</td>
                </tr>
                <tr>
                  <td>MAE</td>
                  <td class="mono">{{ sci(result.is_metrics.mae) }}</td>
                  <td class="mono">{{ sci(result.oos_metrics.mae) }}</td>
                </tr>
                <tr>
                  <td>QLIKE</td>
                  <td class="mono">{{ fmt4(result.is_metrics.qlike) }}</td>
                  <td class="mono" :class="result.oos_metrics.qlike > result.is_metrics.qlike * 1.5 ? 'neg' : 'pos'">{{ fmt4(result.oos_metrics.qlike) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Fitted vs Actual chart -->
      <div class="panel">
        <div class="panel-header">
          <h3>Фактическая vs подогнанная волатильность</h3>
          <span class="hint">Серая вертикаль — граница обучающей/тестовой выборки</span>
        </div>
        <div ref="chartEl" class="chart-container" />
      </div>

    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { getApiHeaders } from '@/utils/apiHeaders'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

// ── State ──────────────────────────────────────────────────────────────────────
const rvRaw = ref('')
const bvRaw = ref('')
const logTransform = ref(false)
const trainRatio = ref(0.8)
const loading = ref(false)
const error = ref('')
const result = ref<Record<string, any> | null>(null)
const chartEl = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

// ── Parsers ────────────────────────────────────────────────────────────────────
function parseFloats(raw: string): number[] {
  return raw.replace(/,/g, ' ').split(/\s+/).map(s => s.trim())
    .filter(s => s.length > 0).map(s => parseFloat(s)).filter(n => !isNaN(n))
}

const bvParsed = computed(() => parseFloats(bvRaw.value))

// ── Formatters ─────────────────────────────────────────────────────────────────
const pct = (v: number) => v != null ? (v * 100).toFixed(2) + '%' : '—'
const fmt2 = (v: number) => v?.toFixed(2) ?? '—'
const fmt4 = (v: number) => v?.toFixed(4) ?? '—'
const fmtP = (v: number) => {
  if (v == null) return '—'
  if (v < 0.001) return '<0.001'
  return v.toFixed(3)
}
const sci = (v: number) => {
  if (v == null) return '—'
  if (v === 0) return '0'
  return v.toExponential(3)
}

// ── API ────────────────────────────────────────────────────────────────────────
async function fitModel() {
  error.value = ''
  const rv = parseFloats(rvRaw.value)
  if (rv.length < 50) { error.value = 'Нужно минимум 50 наблюдений RV'; return }

  const bv = bvParsed.value
  if (bv.length > 0 && bv.length !== rv.length) {
    error.value = 'BV должен совпадать по длине с RV'
    return
  }

  loading.value = true
  try {
    const resp = await fetch(`${API_BASE}/api/har/fit`, {
      method: 'POST',
      headers: getApiHeaders(),
      body: JSON.stringify({
        rv,
        bv: bv.length > 0 ? bv : null,
        log_transform: logTransform.value,
        forecast_horizons: [1, 5, 22],
        train_ratio: trainRatio.value,
      }),
    })
    if (!resp.ok) {
      const data = await resp.json()
      throw new Error(data.detail || `HTTP ${resp.status}`)
    }
    const data = await resp.json()
    result.value = data.result
    await nextTick()
    renderChart()
  } catch (e: any) {
    error.value = e.message || 'Неизвестная ошибка'
  } finally {
    loading.value = false
  }
}

// ── Chart ──────────────────────────────────────────────────────────────────────
function renderChart() {
  if (!chartEl.value || !result.value) return
  if (!chart) chart = echarts.init(chartEl.value, 'dark')

  const { actual_vol, fitted_vol, n, train_end } = result.value.plot_data
  const indices = Array.from({ length: n }, (_, i) => i + 1)

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      formatter: (p: any) => {
        const t = p[0]?.axisValue
        const lines = p.map((s: any) => `${s.seriesName}: ${parseFloat(s.value).toFixed(2)}%`).join('<br/>')
        return `t = ${t}<br/>${lines}`
      },
    },
    legend: { data: ['Факт. vol', 'HAR fitted'], top: 4, textStyle: { color: '#aaa' } },
    xAxis: {
      type: 'category',
      data: indices,
      axisLabel: { show: false },
      axisLine: { lineStyle: { color: '#444' } },
    },
    yAxis: {
      type: 'value',
      name: 'Vol % (годовая)',
      axisLabel: { formatter: (v: number) => v.toFixed(1) + '%' },
      axisLine: { lineStyle: { color: '#444' } },
    },
    series: [
      {
        name: 'Факт. vol',
        type: 'line',
        data: actual_vol,
        lineStyle: { color: '#4e8ef7', width: 1.5 },
        showSymbol: false,
        areaStyle: { color: 'rgba(78,142,247,0.07)' },
      },
      {
        name: 'HAR fitted',
        type: 'line',
        data: fitted_vol,
        lineStyle: { color: '#f5c518', width: 1.5, type: 'dashed' },
        showSymbol: false,
      },
    ],
    markLine: {
      data: [{
        xAxis: train_end,
        lineStyle: { color: '#555', type: 'solid', width: 1 },
        label: { formatter: 'train|test', color: '#666' },
      }],
    },
    grid: { left: 60, right: 20, top: 40, bottom: 20 },
    dataZoom: [{ type: 'inside' }, { type: 'slider', height: 20, bottom: 0 }],
  })
}

watch(result, () => nextTick(renderChart))
</script>

<style scoped>
.har-page { padding: 24px; color: #e0e0e0; }

.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.header-left { flex: 1; }
.page-title { font-size: 22px; font-weight: 600; margin: 0 0 4px; color: #fff; }
.page-subtitle { font-size: 13px; color: #888; margin: 0; }
.header-right { display: flex; gap: 10px; align-items: center; }

.toggle-label { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #aaa; cursor: pointer; }
.control-select, .param-input {
  background: #1e1e2e; border: 1px solid #333; color: #e0e0e0;
  padding: 6px 10px; border-radius: 6px; font-size: 13px;
}
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

.model-desc-row { display: flex; gap: 12px; margin-bottom: 16px; }
.formula-card {
  flex: 1; background: #13131f; border: 1px solid #252535; border-radius: 8px;
  padding: 12px; opacity: 0.55; transition: opacity 0.2s, border-color 0.2s;
}
.formula-card.active { opacity: 1; border-color: #4e8ef7; }
.fc-title { font-size: 12px; font-weight: 700; color: #4e8ef7; margin-bottom: 6px; }
.fc-formula { font-family: 'Georgia', serif; font-size: 12px; color: #b0c4de; line-height: 1.5; }

.error-banner {
  background: rgba(231,76,60,0.15); border: 1px solid #e74c3c;
  color: #ff6b6b; padding: 10px 14px; border-radius: 6px; margin-bottom: 16px; font-size: 13px;
}

.kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 20px; }
.kpi-card {
  background: #13131f; border: 1px solid #252535; border-radius: 10px;
  padding: 14px 12px; text-align: center;
}
.kpi-card.accent-card { border-color: #4e8ef7; background: rgba(78,142,247,0.08); }
.kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
.kpi-value { font-size: 22px; font-weight: 700; color: #fff; font-family: monospace; }
.kpi-value.val-green { color: #2ecc71; }
.kpi-value.val-yellow { color: #f39c12; }
.kpi-value.val-red { color: #e74c3c; }
.kpi-sub { font-size: 11px; color: #777; margin-top: 4px; }

.results-grid { display: grid; grid-template-columns: 1.3fr 1fr; gap: 16px; margin-bottom: 20px; }

.coef-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.coef-table th { text-align: left; padding: 6px 8px; color: #888; font-size: 11px; border-bottom: 1px solid #252535; }
.coef-table td { padding: 5px 8px; border-bottom: 1px solid #1c1c2c; }
.coef-table td:not(:first-child) { text-align: right; }

.r2-row { font-size: 12px; color: #888; margin-top: 8px; }

.forecast-cards { display: flex; gap: 10px; flex-wrap: wrap; }
.fcast-card {
  flex: 1; min-width: 80px; background: #0d0d1a; border: 1px solid #252535;
  border-radius: 8px; padding: 12px; text-align: center;
}
.fcast-h { font-size: 11px; color: #888; margin-bottom: 4px; }
.fcast-vol { font-size: 20px; font-weight: 700; color: #4e8ef7; font-family: monospace; }
.fcast-rv { font-size: 11px; color: #555; margin-top: 4px; font-family: monospace; }

.stats-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.stats-table th { text-align: left; padding: 6px 8px; color: #888; font-size: 11px; border-bottom: 1px solid #252535; }
.stats-table td { padding: 5px 8px; border-bottom: 1px solid #1c1c2c; }
.stats-table td:not(:first-child) { text-align: right; }

.mono { font-family: monospace; }
.pos { color: #2ecc71; }
.neg { color: #e74c3c; }
.muted { color: #666; }

.chart-container { width: 100%; height: 320px; }
</style>
