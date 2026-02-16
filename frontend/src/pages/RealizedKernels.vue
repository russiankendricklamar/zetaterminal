<!-- src/pages/RealizedKernels.vue -->
<template>
  <div class="rk-page">

    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Realized Kernels — Измерение волатильности</h1>
        <p class="page-subtitle">Оценщики RV, BV, TSRV, MSRV, RK с поправкой на рыночный микроструктурный шум</p>
      </div>
      <div class="header-right">
        <select v-model="kernel" class="control-select">
          <option value="parzen">Parzen kernel</option>
          <option value="tukey-hanning">Tukey-Hanning kernel</option>
          <option value="bartlett">Bartlett kernel</option>
        </select>
        <select v-model="periodsPerDay" class="control-select">
          <option :value="390">Минуты (390/день)</option>
          <option :value="78">5-мин (78/день)</option>
          <option :value="26">15-мин (26/день)</option>
          <option :value="1">Дневные</option>
        </select>
        <button @click="estimate" class="btn-primary" :disabled="loading">
          <span v-if="!loading">Рассчитать</span>
          <span v-else>↺ Считаю...</span>
        </button>
      </div>
    </div>

    <!-- Input -->
    <div class="input-grid">
      <div class="panel">
        <div class="panel-header">
          <h3>Ряд цен</h3>
          <span class="hint">Цены через запятую, пробел или перенос строки (обязательно > 0)</span>
        </div>
        <textarea
          v-model="pricesRaw"
          class="data-textarea"
          placeholder="100.00&#10;100.02&#10;99.98&#10;100.05&#10;..."
          rows="8"
        />
        <div class="input-row">
          <label>Bandwidth H (RK):</label>
          <input v-model.number="bandwidth" type="number" min="1" placeholder="авто (n^3/5)" class="param-input" />
        </div>
        <div class="input-row">
          <label>Масштабы K (TSRV):</label>
          <input v-model.number="tsrvScales" type="number" min="2" max="50" class="param-input" />
        </div>
      </div>

      <div class="panel">
        <div class="panel-header"><h3>О методах</h3></div>
        <div class="methods-desc">
          <div class="method-item">
            <span class="method-tag rv">RV</span>
            <span>Σ rᵢ² — наивный, смещён вверх при наличии шума</span>
          </div>
          <div class="method-item">
            <span class="method-tag bv">BV</span>
            <span>(π/2)·Σ|rᵢ||rᵢ₊₁| — устойчив к скачкам (BN-Shephard 2004)</span>
          </div>
          <div class="method-item">
            <span class="method-tag tsrv">TSRV</span>
            <span>Двухмасштабный RV — поправка на шум (Zhang et al. 2005)</span>
          </div>
          <div class="method-item">
            <span class="method-tag msrv">MSRV</span>
            <span>Многомасштабный RV — оптимальные веса (Zhang 2006)</span>
          </div>
          <div class="method-item">
            <span class="method-tag rk">RK</span>
            <span>γ₀ + 2Σ k(h/H)·γₕ — ядерный оценщик (BN et al. 2008)</span>
          </div>
          <div class="formula-box">
            <div class="formula">RK = γ₀ + 2 Σ<sub>h=1</sub><sup>H</sup> k(h/(H+1)) · γₕ</div>
            <div class="formula small">γₕ = Σᵢ rᵢ · rᵢ₊ₕ &nbsp;|&nbsp; H ≈ n<sup>3/5</sup></div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>

    <template v-if="result">

      <!-- KPI cards -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label kpi-tag rv-tag">RV Vol</div>
          <div class="kpi-value">{{ pct(result.rv_vol) }}</div>
          <div class="kpi-sub">Наивный (смещён)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label kpi-tag bv-tag">BV Vol</div>
          <div class="kpi-value">{{ pct(result.bv_vol) }}</div>
          <div class="kpi-sub">Jump-robust</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label kpi-tag tsrv-tag">TSRV Vol</div>
          <div class="kpi-value">{{ pct(result.tsrv_vol) }}</div>
          <div class="kpi-sub">K={{ result.tsrv_scales ?? tsrvScales }}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label kpi-tag msrv-tag">MSRV Vol</div>
          <div class="kpi-value">{{ pct(result.msrv_vol) }}</div>
          <div class="kpi-sub">Multi-scale</div>
        </div>
        <div class="kpi-card accent-card">
          <div class="kpi-label kpi-tag rk-tag">RK Vol</div>
          <div class="kpi-value">{{ pct(result.rk_vol) }}</div>
          <div class="kpi-sub">{{ result.kernel }} H={{ result.bandwidth_used }}</div>
        </div>
        <div class="kpi-card" :class="result.jump_test.has_jumps ? 'kpi-red' : 'kpi-green'">
          <div class="kpi-label">Скачки</div>
          <div class="kpi-value">{{ result.jump_test.has_jumps ? 'Есть' : 'Нет' }}</div>
          <div class="kpi-sub">p = {{ fmtP(result.jump_test.p_value) }}</div>
        </div>
      </div>

      <!-- Estimator comparison + Jump test details -->
      <div class="results-grid">
        <div class="panel">
          <div class="panel-header"><h3>Сравнение оценщиков</h3></div>
          <table class="stats-table">
            <thead>
              <tr>
                <th>Оценщик</th>
                <th>Σrᵢ² (raw)</th>
                <th>Годовая vol</th>
                <th>Отклонение от RK</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><span class="method-tag rv">RV</span></td>
                <td class="mono">{{ sci(result.rv_raw) }}</td>
                <td class="mono">{{ pct(result.rv_vol) }}</td>
                <td class="mono" :class="biasClass(result.rv_vol, result.rk_vol)">{{ biasPct(result.rv_vol, result.rk_vol) }}</td>
              </tr>
              <tr>
                <td><span class="method-tag bv">BV</span></td>
                <td class="mono">{{ sci(result.bv_raw) }}</td>
                <td class="mono">{{ pct(result.bv_vol) }}</td>
                <td class="mono" :class="biasClass(result.bv_vol, result.rk_vol)">{{ biasPct(result.bv_vol, result.rk_vol) }}</td>
              </tr>
              <tr>
                <td><span class="method-tag tsrv">TSRV</span></td>
                <td class="mono">{{ sci(result.tsrv_raw) }}</td>
                <td class="mono">{{ pct(result.tsrv_vol) }}</td>
                <td class="mono" :class="biasClass(result.tsrv_vol, result.rk_vol)">{{ biasPct(result.tsrv_vol, result.rk_vol) }}</td>
              </tr>
              <tr>
                <td><span class="method-tag msrv">MSRV</span></td>
                <td class="mono">{{ sci(result.msrv_raw) }}</td>
                <td class="mono">{{ pct(result.msrv_vol) }}</td>
                <td class="mono" :class="biasClass(result.msrv_vol, result.rk_vol)">{{ biasPct(result.msrv_vol, result.rk_vol) }}</td>
              </tr>
              <tr class="highlight-row">
                <td><span class="method-tag rk">RK</span></td>
                <td class="mono">{{ sci(result.rk_raw) }}</td>
                <td class="mono accent">{{ pct(result.rk_vol) }}</td>
                <td class="mono">—</td>
              </tr>
            </tbody>
          </table>

          <div class="panel-header" style="margin-top:16px"><h3>Тест на скачки (BN-Shephard)</h3></div>
          <table class="stats-table">
            <tbody>
              <tr><td>Компонент скачков</td><td class="mono">{{ sci(result.jump_test.jump_component) }}</td></tr>
              <tr><td>Непрерывный компонент (BV)</td><td class="mono">{{ sci(result.jump_test.continuous_component) }}</td></tr>
              <tr><td>Доля скачков (J/RV)</td><td class="mono" :class="result.jump_test.ratio > 0.1 ? 'neg' : 'pos'">{{ pct(result.jump_test.ratio) }}</td></tr>
              <tr><td>z-статистика</td><td class="mono">{{ fmt2(result.jump_test.z_stat) }}</td></tr>
              <tr><td>p-value</td><td class="mono" :class="result.jump_test.has_jumps ? 'neg' : 'pos'">{{ fmtP(result.jump_test.p_value) }}</td></tr>
              <tr><td>Вывод</td><td :class="result.jump_test.has_jumps ? 'neg' : 'pos'">{{ result.jump_test.has_jumps ? 'Значимые скачки обнаружены' : 'Скачков не обнаружено' }}</td></tr>
            </tbody>
          </table>

          <div class="noise-info">
            <span class="noise-label">Дисперсия шума ω²:</span>
            <span class="mono">{{ sci(result.noise_variance) }}</span>
            <span class="noise-label" style="margin-left:16px">Оптимальный шаг дискретизации Δ*:</span>
            <span class="mono accent">{{ result.optimal_sampling_step }}</span>
          </div>
        </div>

        <!-- Signature plot -->
        <div class="panel">
          <div class="panel-header">
            <h3>Сигнатурный график</h3>
            <span class="hint">RV(Δ) vs шаг дискретизации — рост при малых Δ свидетельствует о микроструктурном шуме</span>
          </div>
          <div ref="sigChartEl" class="chart-container" />
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
const pricesRaw = ref('')
const kernel = ref('parzen')
const periodsPerDay = ref(390)
const bandwidth = ref<number | null>(null)
const tsrvScales = ref(5)
const loading = ref(false)
const error = ref('')
const result = ref<Record<string, any> | null>(null)
const sigChartEl = ref<HTMLElement | null>(null)
let sigChart: echarts.ECharts | null = null

// ── Formatters ─────────────────────────────────────────────────────────────────
function parsePrices(): number[] {
  return pricesRaw.value
    .replace(/,/g, ' ')
    .split(/\s+/)
    .map(s => s.trim())
    .filter(s => s.length > 0)
    .map(s => parseFloat(s))
    .filter(n => !isNaN(n) && n > 0)
}

const pct = (v: number) => v != null ? (v * 100).toFixed(2) + '%' : '—'
const fmt2 = (v: number) => v?.toFixed(2) ?? '—'
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
const biasPct = (vol: number, rk: number) => {
  if (!vol || !rk) return '—'
  return ((vol - rk) / rk * 100).toFixed(1) + '%'
}
const biasClass = (vol: number, rk: number) => {
  if (!vol || !rk) return ''
  const diff = (vol - rk) / rk
  return diff > 0.02 ? 'neg' : diff < -0.02 ? 'pos' : ''
}

// ── API ────────────────────────────────────────────────────────────────────────
async function estimate() {
  error.value = ''
  const prices = parsePrices()
  if (prices.length < 10) {
    error.value = 'Нужно минимум 10 положительных значений цен'
    return
  }
  loading.value = true
  try {
    const resp = await fetch(`${API_BASE}/api/realized-kernels/estimate`, {
      method: 'POST',
      headers: getApiHeaders(),
      body: JSON.stringify({
        prices,
        kernel: kernel.value,
        bandwidth: bandwidth.value || null,
        tsrv_scales: tsrvScales.value,
        annualize: true,
        periods_per_day: periodsPerDay.value,
      }),
    })
    if (!resp.ok) {
      const data = await resp.json()
      throw new Error(data.detail || `HTTP ${resp.status}`)
    }
    const data = await resp.json()
    result.value = data.result
    await nextTick()
    renderSignaturePlot()
  } catch (e: any) {
    error.value = e.message || 'Неизвестная ошибка'
  } finally {
    loading.value = false
  }
}

// ── Chart ──────────────────────────────────────────────────────────────────────
function renderSignaturePlot() {
  if (!sigChartEl.value || !result.value) return
  if (!sigChart) sigChart = echarts.init(sigChartEl.value, 'dark')

  const { steps, rv } = result.value.signature_plot
  const optStep = result.value.optimal_sampling_step
  const rvVol = result.value.rv_vol
  const rkVol = result.value.rk_vol

  // Конвертируем raw RV в приблизительную волатильность для оси Y
  // rv[i] уже нормирован на шаг, делим на ту же ann_factor и берём sqrt
  const annFactor = result.value.ann_factor
  const volData = rv.map((v: number) => Math.sqrt(Math.max(v / steps[rv.indexOf(v)], 0) * annFactor))

  sigChart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      formatter: (p: any) => `Шаг Δ = ${p[0].axisValue}<br/>RK Vol ≈ ${(p[0].value[1] * 100).toFixed(2)}%`,
    },
    xAxis: {
      type: 'value',
      name: 'Шаг дискретизации Δ',
      nameLocation: 'middle',
      nameGap: 28,
      axisLine: { lineStyle: { color: '#555' } },
    },
    yAxis: {
      type: 'value',
      name: 'Годовая vol',
      axisLabel: { formatter: (v: number) => (v * 100).toFixed(1) + '%' },
      axisLine: { lineStyle: { color: '#555' } },
    },
    series: [
      {
        type: 'line',
        data: steps.map((s: number, i: number) => [s, volData[i]]),
        lineStyle: { color: '#4e8ef7', width: 2 },
        showSymbol: false,
        name: 'RV(Δ)',
        markLine: {
          silent: true,
          data: [
            {
              xAxis: optStep,
              lineStyle: { color: '#f5c518', type: 'dashed', width: 1.5 },
              label: { formatter: `Δ*=${optStep}`, position: 'insideEndTop' },
            },
            {
              yAxis: rkVol,
              lineStyle: { color: '#2ecc71', type: 'dashed', width: 1.5 },
              label: { formatter: `RK=${(rkVol * 100).toFixed(1)}%`, position: 'insideEndBottom' },
            },
          ],
        },
      },
    ],
    grid: { left: 65, right: 20, top: 20, bottom: 45 },
  })
}

watch(result, () => nextTick(renderSignaturePlot))
</script>

<style scoped>
.rk-page { padding: 24px; color: #e0e0e0; }

.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
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
.panel { background: #13131f; border: 1px solid #252535; border-radius: 10px; padding: 16px; }
.panel-header { display: flex; align-items: baseline; gap: 10px; margin-bottom: 12px; }
.panel-header h3 { font-size: 14px; font-weight: 600; color: #fff; margin: 0; }
.hint { font-size: 11px; color: #666; }

.data-textarea {
  width: 100%; background: #0d0d1a; border: 1px solid #333; color: #e0e0e0;
  border-radius: 6px; padding: 8px; font-size: 12px; font-family: monospace;
  resize: vertical; box-sizing: border-box;
}
.input-row { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 13px; }

.methods-desc { display: flex; flex-direction: column; gap: 8px; }
.method-item { display: flex; align-items: center; gap: 10px; font-size: 13px; color: #aaa; }

.method-tag {
  display: inline-block; padding: 2px 7px; border-radius: 4px;
  font-size: 11px; font-weight: 700; white-space: nowrap;
}
.rv { background: rgba(231,76,60,0.2); color: #e74c3c; border: 1px solid #e74c3c55; }
.bv { background: rgba(243,156,18,0.2); color: #f39c12; border: 1px solid #f39c1255; }
.tsrv { background: rgba(78,142,247,0.2); color: #4e8ef7; border: 1px solid #4e8ef755; }
.msrv { background: rgba(155,89,182,0.2); color: #9b59b6; border: 1px solid #9b59b655; }
.rk { background: rgba(46,204,113,0.2); color: #2ecc71; border: 1px solid #2ecc7155; }

.formula-box { margin-top: 12px; background: #0d0d1a; border: 1px solid #252535; border-radius: 6px; padding: 10px; }
.formula { font-family: 'Georgia', serif; font-size: 13px; color: #b0c4de; margin: 3px 0; }
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
.kpi-card.accent-card { border-color: #2ecc71; background: rgba(46,204,113,0.07); }
.kpi-card.kpi-green { border-color: #27ae60; background: rgba(39,174,96,0.08); }
.kpi-card.kpi-red { border-color: #e74c3c; background: rgba(231,76,60,0.08); }
.kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
.kpi-tag { display: inline-block; border-radius: 4px; padding: 2px 7px; margin-bottom: 6px; font-size: 11px; font-weight: 700; }
.rv-tag { background: rgba(231,76,60,0.2); color: #e74c3c; }
.bv-tag { background: rgba(243,156,18,0.2); color: #f39c12; }
.tsrv-tag { background: rgba(78,142,247,0.2); color: #4e8ef7; }
.msrv-tag { background: rgba(155,89,182,0.2); color: #9b59b6; }
.rk-tag { background: rgba(46,204,113,0.2); color: #2ecc71; }
.kpi-value { font-size: 22px; font-weight: 700; color: #fff; font-family: monospace; }
.kpi-sub { font-size: 11px; color: #777; margin-top: 4px; }

.results-grid { display: grid; grid-template-columns: 1fr 1.4fr; gap: 16px; }
.stats-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.stats-table th { text-align: left; padding: 6px 8px; color: #888; font-size: 11px; border-bottom: 1px solid #252535; }
.stats-table td { padding: 5px 8px; border-bottom: 1px solid #1c1c2c; }
.stats-table td:not(:first-child) { text-align: right; }
.highlight-row td { background: rgba(46,204,113,0.06); }

.mono { font-family: monospace; }
.accent { color: #4e8ef7; }
.pos { color: #2ecc71; }
.neg { color: #e74c3c; }

.noise-info {
  margin-top: 14px; padding: 10px; background: #0d0d1a; border-radius: 6px;
  display: flex; align-items: center; flex-wrap: wrap; gap: 6px; font-size: 13px;
}
.noise-label { color: #888; }

.chart-container { width: 100%; height: 320px; }
</style>
