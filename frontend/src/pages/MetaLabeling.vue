<template>
  <div class="ml-page">
    <div class="page-header">
      <h1>Meta-Labeling</h1>
      <p class="subtitle">
        Triple-Barrier Labeling · Primary Side Rule · Logistic Meta-Model · Bet Sizing
      </p>
    </div>

    <!-- Input Panel -->
    <div class="card input-card">
      <h2>Параметры</h2>
      <div class="form-grid">
        <div class="form-group">
          <label>Profit-Take множитель</label>
          <input v-model.number="params.pt_multiplier" type="number" min="0.1" step="0.1" />
          <span class="hint">PT барьер = pt × daily_vol. Рекомендовано 1.5–3.</span>
        </div>
        <div class="form-group">
          <label>Stop-Loss множитель</label>
          <input v-model.number="params.sl_multiplier" type="number" min="0.1" step="0.1" />
          <span class="hint">SL барьер = sl × daily_vol. Рекомендовано 0.5–1.5.</span>
        </div>
        <div class="form-group">
          <label>Макс. горизонт (баров)</label>
          <input v-model.number="params.max_holding" type="number" min="1" max="100" />
          <span class="hint">Временной барьер. 5 = 1 неделя для дневных.</span>
        </div>
        <div class="form-group">
          <label>Окно rolling vol</label>
          <input v-model.number="params.vol_window" type="number" min="5" max="252" />
          <span class="hint">Используется для нормировки барьеров.</span>
        </div>
        <div class="form-group">
          <label>Обучающая выборка</label>
          <input v-model.number="params.train_ratio" type="number" min="0.1" max="0.9" step="0.05" />
          <span class="hint">0.7 = первые 70% для обучения.</span>
        </div>
        <div class="form-group">
          <label>Порог вероятности</label>
          <input v-model.number="params.meta_threshold" type="number" min="0.1" max="0.9" step="0.05" />
          <span class="hint">Открывать позицию только при P(profit) ≥ порог.</span>
        </div>
      </div>

      <div class="form-group" style="margin-bottom:16px">
        <label>Ценовой ряд (одно значение на строку или через запятую)</label>
        <textarea v-model="pricesText" rows="6" placeholder="100.0&#10;100.5&#10;101.2&#10;..." />
        <div class="parse-info" v-if="parsedPrices">{{ parsedPrices.length }} цен загружено</div>
        <div class="parse-error" v-if="priceError">{{ priceError }}</div>
      </div>

      <div class="actions">
        <button class="btn-primary" @click="compute" :disabled="loading || !!priceError || !pricesText.trim()">
          {{ loading ? 'Вычисление...' : 'Запустить анализ' }}
        </button>
        <button class="btn-secondary" @click="loadDemo">Демо-данные (300 баров)</button>
      </div>
      <div class="error-msg" v-if="error">{{ error }}</div>
    </div>

    <!-- Results -->
    <template v-if="result">
      <!-- KPI Row -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">Precision (тест)</div>
          <div class="kpi-value" :class="colorPct(result.test_metrics.precision)">
            {{ pct(result.test_metrics.precision) }}
          </div>
          <div class="kpi-sub">точность мета-сигнала</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Recall (тест)</div>
          <div class="kpi-value" :class="colorPct(result.test_metrics.recall)">
            {{ pct(result.test_metrics.recall) }}
          </div>
          <div class="kpi-sub">полнота</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">F1 (тест)</div>
          <div class="kpi-value" :class="colorPct(result.test_metrics.f1)">
            {{ pct(result.test_metrics.f1) }}
          </div>
          <div class="kpi-sub">гармоническое среднее</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">SR (мета)</div>
          <div class="kpi-value" :class="result.test_metrics.sr > result.test_metrics.raw_sr ? 'ok-val' : 'danger-val'">
            {{ result.test_metrics.sr.toFixed(3) }}
          </div>
          <div class="kpi-sub">фильтрованный Sharpe</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">SR (baseline)</div>
          <div class="kpi-value">{{ result.test_metrics.raw_sr.toFixed(3) }}</div>
          <div class="kpi-sub">без фильтра</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Ставок / Всего</div>
          <div class="kpi-value">{{ result.test_metrics.n_bets }} / {{ result.test_metrics.n_total }}</div>
          <div class="kpi-sub">avg bet={{ pct(result.test_metrics.avg_bet_size) }}</div>
        </div>
      </div>

      <!-- Triple-Barrier info -->
      <div class="info-row">
        <div class="info-card">
          <span class="info-label">Выборок</span>
          <span class="info-val">{{ result.n_samples }}</span>
        </div>
        <div class="info-card">
          <span class="info-label">Обучение</span>
          <span class="info-val">{{ result.n_train }}</span>
        </div>
        <div class="info-card">
          <span class="info-label">Тест</span>
          <span class="info-val">{{ result.n_test }}</span>
        </div>
        <div class="info-card">
          <span class="info-label">Primary acc (тест)</span>
          <span class="info-val" :class="colorPct(result.primary_accuracy_test)">
            {{ pct(result.primary_accuracy_test) }}
          </span>
        </div>
        <div class="info-card" v-for="(cnt, lbl) in result.label_distribution" :key="lbl">
          <span class="info-label">Label {{ lbl }}</span>
          <span class="info-val"
            :class="lbl == 1 ? 'ok-val' : lbl == -1 ? 'danger-val' : 'neutral-val'">
            {{ cnt }}
          </span>
        </div>
      </div>

      <!-- Charts Row 1: Equity + PR Curve -->
      <div class="charts-row">
        <div class="card chart-card">
          <h3>Equity кривые (тест)</h3>
          <div ref="equityChart" class="chart" />
        </div>
        <div class="card chart-card">
          <h3>Precision-Recall кривая (threshold sweep)</h3>
          <div ref="prChart" class="chart" />
        </div>
      </div>

      <!-- Charts Row 2: Prob hist + Feature importance -->
      <div class="charts-row">
        <div class="card chart-card">
          <h3>Распределение мета-вероятностей (тест)</h3>
          <div ref="probHistChart" class="chart" />
        </div>
        <div class="card chart-card">
          <h3>Feature Importances (мета-модель)</h3>
          <div ref="featChart" class="chart" />
        </div>
      </div>

      <!-- Bet Scatter -->
      <div class="card">
        <h3>Ставки: вероятность vs реализованная доходность (тест)</h3>
        <div ref="betScatter" class="chart tall-chart" />
      </div>

      <!-- Metrics Table -->
      <div class="card">
        <h3>Метрики: обучение vs тест</h3>
        <table class="stats-table">
          <thead>
            <tr>
              <th>Метрика</th>
              <th>Обучение</th>
              <th>Тест</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="key in metricKeys" :key="key">
              <td>{{ metricLabel(key) }}</td>
              <td :class="metricClass(key, result.train_metrics[key])">
                {{ formatMetric(key, result.train_metrics[key]) }}
              </td>
              <td :class="metricClass(key, result.test_metrics[key])">
                {{ formatMetric(key, result.test_metrics[key]) }}
              </td>
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

const params = ref({
  pt_multiplier: 1.5,
  sl_multiplier: 1.0,
  max_holding: 5,
  vol_window: 20,
  train_ratio: 0.7,
  meta_threshold: 0.5,
})
const pricesText = ref('')
const loading = ref(false)
const error = ref('')
const result = ref<any>(null)

// chart refs
const equityChart = ref<HTMLElement | null>(null)
const prChart = ref<HTMLElement | null>(null)
const probHistChart = ref<HTMLElement | null>(null)
const featChart = ref<HTMLElement | null>(null)
const betScatter = ref<HTMLElement | null>(null)
let chartInstances: echarts.ECharts[] = []

// --- Prices parsing ---
const parsedPrices = computed<number[] | null>(() => {
  if (!pricesText.value.trim()) return null
  const raw = pricesText.value.trim().replace(/\n/g, ',')
  const vals = raw.split(',').map(v => parseFloat(v.trim())).filter(v => !isNaN(v))
  return vals.length >= 50 ? vals : null
})

const priceError = computed(() => {
  if (!pricesText.value.trim()) return ''
  const raw = pricesText.value.trim().replace(/\n/g, ',')
  const vals = raw.split(',').map(v => parseFloat(v.trim()))
  const valid = vals.filter(v => !isNaN(v))
  if (valid.length < 50) return `Нужно минимум 50 значений, получено ${valid.length}`
  return ''
})

// --- Demo ---
function loadDemo() {
  let seed = 7654
  const rnd = () => {
    seed = (seed * 1664525 + 1013904223) & 0x7fffffff
    return (seed / 0x7fffffff) * 2 - 1
  }
  const T = 300
  const prices = [100.0]
  for (let i = 1; i < T; i++) {
    prices.push(prices[i - 1] * (1 + rnd() * 0.01 + 0.0002))
  }
  pricesText.value = prices.map(p => p.toFixed(4)).join('\n')
}

// --- Compute ---
async function compute() {
  if (!parsedPrices.value) return
  loading.value = true
  error.value = ''
  result.value = null

  try {
    const resp = await fetch(`${API_BASE}/api/meta-labeling/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getApiHeaders() },
      body: JSON.stringify({ prices: parsedPrices.value, ...params.value }),
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
function mkChart(el: HTMLElement | null) {
  if (!el) return null
  const inst = echarts.init(el, 'dark')
  chartInstances.push(inst)
  return inst
}

function renderAllCharts() {
  disposeAll()
  renderEquity()
  renderPR()
  renderProbHist()
  renderFeatures()
  renderBetScatter()
}

function renderEquity() {
  const inst = mkChart(equityChart.value)
  if (!inst || !result.value) return
  const base: number[] = result.value.equity_baseline
  const meta: number[] = result.value.equity_meta
  const xData = base.map((_: number, i: number) => i + 1)
  inst.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { top: 5, textStyle: { color: '#aaa' } },
    xAxis: { type: 'category', data: xData, axisLabel: { color: '#aaa' } },
    yAxis: { name: 'Cumulative Log Return', splitLine: { lineStyle: { color: '#333' } } },
    series: [
      { name: 'Baseline (все сигналы)', type: 'line', data: base, lineStyle: { color: '#888', type: 'dashed' }, symbol: 'none' },
      { name: 'Meta (фильтровано)', type: 'line', data: meta, lineStyle: { color: '#4caf72', width: 2 }, symbol: 'none' },
    ],
    grid: { left: 65, right: 20, top: 35, bottom: 30 },
  })
}

function renderPR() {
  const inst = mkChart(prChart.value)
  if (!inst || !result.value) return
  const curve = result.value.pr_curve
  const data = curve.map((p: any) => [p.recall, p.precision])
  const labels = curve.map((p: any) => `thr=${p.threshold} n=${p.n_bets}`)
  inst.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (p: any) => `${labels[p.dataIndex]}<br/>P=${p.data[1].toFixed(3)} R=${p.data[0].toFixed(3)}`,
    },
    xAxis: { name: 'Recall', nameLocation: 'middle', nameGap: 28, min: 0, max: 1, splitLine: { lineStyle: { color: '#333' } } },
    yAxis: { name: 'Precision', nameLocation: 'middle', nameGap: 40, min: 0, max: 1, splitLine: { lineStyle: { color: '#333' } } },
    series: [
      {
        type: 'line',
        data,
        lineStyle: { color: '#5b8af5' },
        itemStyle: { color: '#5b8af5' },
        symbol: 'circle',
        symbolSize: 5,
      },
    ],
    grid: { left: 60, right: 20, top: 20, bottom: 45 },
  })
}

function renderProbHist() {
  const inst = mkChart(probHistChart.value)
  if (!inst || !result.value) return
  const { counts, bin_edges } = result.value.prob_hist
  const threshold = result.value.meta_threshold
  inst.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: bin_edges.slice(0, -1).map((v: number) => v.toFixed(2)),
      name: 'P(profitable)',
      nameLocation: 'middle',
      nameGap: 28,
      axisLabel: { interval: 4, color: '#aaa' },
    },
    yAxis: { name: 'Частота', splitLine: { lineStyle: { color: '#333' } } },
    series: [{
      type: 'bar',
      data: counts,
      itemStyle: {
        color: (p: any) => bin_edges[p.dataIndex] >= threshold ? '#4caf72' : '#5b8af5',
        opacity: 0.85,
      },
    }],
    grid: { left: 50, right: 20, top: 20, bottom: 45 },
  })
}

function renderFeatures() {
  const inst = mkChart(featChart.value)
  if (!inst || !result.value) return
  const imp = result.value.feature_importances
  const names = result.value.feature_names
  const vals = names.map((n: string) => imp[n] ?? 0)
  const sorted = names.map((n: string, i: number) => ({ n, v: vals[i] }))
    .sort((a: { n: string; v: number }, b: { n: string; v: number }) => Math.abs(b.v) - Math.abs(a.v))

  inst.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: '#333' } } },
    yAxis: { type: 'category', data: sorted.map((s: any) => s.n), axisLabel: { color: '#aaa' } },
    series: [{
      type: 'bar',
      data: sorted.map((s: any) => ({
        value: +s.v.toFixed(4),
        itemStyle: { color: s.v >= 0 ? '#4caf72' : '#e05c5c' },
      })),
    }],
    grid: { left: 75, right: 20, top: 10, bottom: 30 },
  })
}

function renderBetScatter() {
  const inst = mkChart(betScatter.value)
  if (!inst || !result.value) return
  const probs: number[] = result.value.test_probs
  const rets: number[] = result.value.test_returns
  const labels: number[] = result.value.test_labels
  const threshold = result.value.meta_threshold

  const data = probs.map((p, i) => ({
    value: [p, rets[i]],
    label: labels[i],
    bet: p >= threshold,
  }))

  const colors: Record<number, string> = { 1: '#4caf72', 0: '#f5a623' }

  inst.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (p: any) => {
        const d = data[p.dataIndex]
        return `P(profit)=${d.value[0].toFixed(3)}<br/>Return=${d.value[1].toFixed(4)}<br/>Bet: ${d.bet ? 'Да' : 'Нет'}`
      },
    },
    xAxis: { name: 'P(profitable)', nameLocation: 'middle', nameGap: 28, min: 0, max: 1, splitLine: { lineStyle: { color: '#333' } } },
    yAxis: { name: 'Realized Return', nameLocation: 'middle', nameGap: 45, splitLine: { lineStyle: { color: '#333' } } },
    series: [
      {
        type: 'scatter',
        data: data.map(d => d.value),
        symbolSize: 8,
        itemStyle: {
          color: (p: any) => data[p.dataIndex].label === 1 ? colors[1] : '#e05c5c',
          opacity: (p: any) => (data[p.dataIndex].bet ? 1.0 : 0.35),
          borderColor: (p: any) => data[p.dataIndex].bet ? '#fff' : 'transparent',
          borderWidth: 1,
        },
      },
    ],
    grid: { left: 65, right: 20, top: 20, bottom: 45 },
  })
}

// --- Helpers ---
const pct = (v: number) => `${(v * 100).toFixed(1)}%`
const colorPct = (v: number) => v >= 0.55 ? 'ok-val' : v >= 0.45 ? 'warn-val' : 'danger-val'

const metricKeys = ['precision', 'recall', 'f1', 'accuracy', 'sr', 'raw_sr', 'n_bets', 'avg_bet_size']
const metricLabel = (k: string) => ({
  precision: 'Precision', recall: 'Recall', f1: 'F1', accuracy: 'Accuracy',
  sr: 'Sharpe (meta)', raw_sr: 'Sharpe (raw)', n_bets: 'Кол-во ставок', avg_bet_size: 'Avg bet size',
}[k] ?? k)
const formatMetric = (k: string, v: number) => ['precision', 'recall', 'f1', 'accuracy', 'avg_bet_size'].includes(k)
  ? pct(v) : ['sr', 'raw_sr'].includes(k) ? v.toFixed(3) : String(Math.round(v))
const metricClass = (k: string, v: number) => {
  if (['sr', 'raw_sr'].includes(k)) return v > 0 ? 'ok-val' : 'danger-val'
  if (['precision', 'recall', 'f1', 'accuracy'].includes(k)) return colorPct(v)
  return ''
}

watch(result, async (val) => {
  if (!val) return
  await nextTick()
  renderAllCharts()
})
</script>

<style scoped>
.ml-page {
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

.form-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px; }
.form-group { display: flex; flex-direction: column; gap: 4px; }
.form-group label { font-size: 0.85rem; color: #aaa; }
.form-group input, .form-group textarea {
  background: #111; border: 1px solid #333; border-radius: 4px;
  padding: 8px; color: #e0e0e0; font-size: 0.9rem;
}
.form-group textarea { font-family: monospace; font-size: 0.8rem; resize: vertical; }
.hint { font-size: 0.75rem; color: #666; }

.parse-info { font-size: 0.8rem; color: #5b8af5; margin-top: 4px; }
.parse-error { font-size: 0.8rem; color: #e05c5c; margin-top: 4px; }

.actions { display: flex; gap: 12px; }
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
.kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; }
.kpi-card {
  background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 8px;
  padding: 16px; text-align: center;
}
.kpi-label { font-size: 0.75rem; color: #888; margin-bottom: 6px; }
.kpi-value { font-size: 1.35rem; font-weight: 600; }
.kpi-sub { font-size: 0.7rem; color: #666; margin-top: 4px; }

/* Info row */
.info-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.info-card {
  background: #1a1a2e;
  border: 1px solid #2a2a4a;
  border-radius: 6px;
  padding: 8px 14px;
  display: flex;
  gap: 8px;
  align-items: center;
}
.info-label { font-size: 0.78rem; color: #888; }
.info-val { font-size: 0.9rem; font-weight: 600; }

/* Charts */
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.chart-card h3, .card > h3 { font-size: 0.9rem; color: #aaa; margin: 0 0 12px; }
.chart { height: 280px; }
.tall-chart { height: 260px; }

/* Colors */
.ok-val { color: #4caf72; }
.warn-val { color: #f5a623; }
.danger-val { color: #e05c5c; }
.neutral-val { color: #888; }

/* Table */
.stats-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.stats-table th { text-align: left; padding: 8px 12px; border-bottom: 1px solid #333; color: #888; font-weight: 500; }
.stats-table td { padding: 8px 12px; border-bottom: 1px solid #222; }
</style>
