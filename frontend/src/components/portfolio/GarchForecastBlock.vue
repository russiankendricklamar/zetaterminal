<template>
  <div class="glass-panel garch-block">
    <div class="panel-header">
      <div>
        <h3>GARCH Volatility Forecast</h3>
        <span class="panel-subtitle">Прогноз условной волатильности</span>
      </div>
      <div class="garch-controls">
        <select
          v-model="selectedModel"
          class="glass-input compact-select"
        >
          <option value="garch_11">GARCH(1,1)</option>
          <option value="gjr_garch">GJR-GARCH</option>
          <option value="egarch">EGARCH</option>
          <option value="ewma">EWMA</option>
        </select>

        <div class="horizon-control">
          <span class="lbl-mini">Горизонт:</span>
          <input
            v-model.number="forecastHorizon"
            type="range"
            min="1"
            max="252"
            class="range-slider compact"
          >
          <span class="scrub-val">{{ forecastHorizon }}d</span>
        </div>

        <label class="toggle-label">
          <input
            v-model="useManualParams"
            type="checkbox"
          >
          <span>Ручные параметры</span>
        </label>

        <button
          class="btn-glass primary compact"
          :disabled="isLoading || !hasReturns"
          @click="runForecast"
        >
          <span v-if="!isLoading">Forecast →</span>
          <span
            v-else
            class="flex items-center gap-1"
          >
            <span class="spinner-mini" /> ...
          </span>
        </button>
      </div>
    </div>

    <!-- Manual Params -->
    <div
      v-if="useManualParams"
      class="params-row"
    >
      <div
        v-if="selectedModel !== 'ewma'"
        class="param-field"
      >
        <label>omega (ω)</label>
        <input
          v-model.number="manualParams.omega"
          type="number"
          step="0.00001"
          class="glass-input mini"
        >
      </div>
      <div
        v-if="selectedModel !== 'ewma'"
        class="param-field"
      >
        <label>alpha (α)</label>
        <input
          v-model.number="manualParams.alpha"
          type="number"
          step="0.01"
          class="glass-input mini"
        >
      </div>
      <div
        v-if="selectedModel !== 'ewma'"
        class="param-field"
      >
        <label>beta (β)</label>
        <input
          v-model.number="manualParams.beta"
          type="number"
          step="0.01"
          class="glass-input mini"
        >
      </div>
      <div
        v-if="selectedModel === 'gjr_garch' || selectedModel === 'egarch'"
        class="param-field"
      >
        <label>gamma (γ)</label>
        <input
          v-model.number="manualParams.gamma"
          type="number"
          step="0.01"
          class="glass-input mini"
        >
      </div>
      <div
        v-if="selectedModel === 'ewma'"
        class="param-field"
      >
        <label>lambda (λ)</label>
        <input
          v-model.number="manualParams.lambda"
          type="number"
          step="0.01"
          min="0.01"
          max="0.99"
          class="glass-input mini"
        >
      </div>
    </div>

    <!-- Error -->
    <div
      v-if="errorMsg"
      class="error-banner"
    >
      {{ errorMsg }}
    </div>

    <!-- KPI Pills -->
    <div
      v-if="forecastResult"
      class="garch-kpi-row"
    >
      <div class="garch-kpi">
        <span class="garch-kpi-label">Текущая σ</span>
        <span class="garch-kpi-value">{{ formatPct(forecastResult.forecast.current_vol) }}</span>
      </div>
      <div class="garch-kpi">
        <span class="garch-kpi-label">Прогноз σ</span>
        <span class="garch-kpi-value text-accent">{{ formatPct(forecastResult.forecast.forecast_vol) }}</span>
      </div>
      <div
        v-if="forecastResult.forecast.long_run_vol"
        class="garch-kpi"
      >
        <span class="garch-kpi-label">Long-run σ</span>
        <span class="garch-kpi-value">{{ formatPct(forecastResult.forecast.long_run_vol) }}</span>
      </div>
      <div
        v-if="forecastResult.fit.persistence"
        class="garch-kpi"
      >
        <span class="garch-kpi-label">Persistence</span>
        <span class="garch-kpi-value">{{ forecastResult.fit.persistence.toFixed(4) }}</span>
      </div>
      <div class="garch-kpi">
        <span class="garch-kpi-label">Модель</span>
        <span class="garch-kpi-value font-mono text-xs">{{ forecastResult.fit.model }}</span>
      </div>
    </div>

    <!-- Chart -->
    <div
      ref="chartEl"
      class="garch-chart"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { use, init } from 'echarts/core'
import type { ECharts } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { TooltipComponent, GridComponent, LegendComponent, DataZoomComponent } from 'echarts/components'
import { forecastGarch } from '@/services/garchService'
import type { GarchForecastResponse } from '@/services/garchService'

use([CanvasRenderer, LineChart, TooltipComponent, GridComponent, LegendComponent, DataZoomComponent])

const props = defineProps<{
  returns: number[]
}>()

const selectedModel = ref<'garch_11' | 'gjr_garch' | 'egarch' | 'ewma'>('garch_11')
const forecastHorizon = ref(22)
const useManualParams = ref(false)
const manualParams = ref({
  omega: 0.000025,
  alpha: 0.08,
  beta: 0.89,
  gamma: 0.05,
  lambda: 0.94,
})
const isLoading = ref(false)
const errorMsg = ref('')
const forecastResult = ref<GarchForecastResponse | null>(null)
const chartEl = ref<HTMLElement | null>(null)
let chart: ECharts | null = null

const hasReturns = ref(false)
watch(() => props.returns, (r) => { hasReturns.value = r && r.length >= 2 }, { immediate: true })

function formatPct(val: number): string {
  return (val * 100).toFixed(2) + '%'
}

function buildParams(): Record<string, number> | undefined {
  if (!useManualParams.value) return undefined
  const m = selectedModel.value
  if (m === 'ewma') return { lambda: manualParams.value.lambda }
  const p: Record<string, number> = {
    omega: manualParams.value.omega,
    alpha: manualParams.value.alpha,
    beta: manualParams.value.beta,
  }
  if (m === 'gjr_garch' || m === 'egarch') {
    p.gamma = manualParams.value.gamma
  }
  return p
}

async function runForecast() {
  if (!props.returns || props.returns.length < 2) return
  isLoading.value = true
  errorMsg.value = ''
  try {
    forecastResult.value = await forecastGarch({
      returns: props.returns,
      model: selectedModel.value,
      params: buildParams(),
      n_steps: forecastHorizon.value,
      confidence_levels: [0.05, 0.95],
    })
    await nextTick()
    renderChart()
  } catch (e: unknown) {
    errorMsg.value = e instanceof Error ? e.message : 'Forecast failed'
  } finally {
    isLoading.value = false
  }
}

function renderChart() {
  if (!chartEl.value || !forecastResult.value) return

  if (!chart) {
    chart = init(chartEl.value, 'dark')
  }

  const fit = forecastResult.value.fit
  const fc = forecastResult.value.forecast

  const historicalVols = fit.volatilities.map((v: number) => v * 100)
  const forecastVols = fc.forecast_volatilities.map((v: number) => v * 100)

  const ciLower = fc.confidence_intervals['0.05']?.map((v: number) => v * 100) || []
  const ciUpper = fc.confidence_intervals['0.95']?.map((v: number) => v * 100) || []

  const nHist = historicalVols.length
  const totalLen = nHist + forecastVols.length

  // Build x-axis labels
  const labels = Array.from({ length: totalLen }, (_, i) =>
    i < nHist ? `t-${nHist - i}` : `t+${i - nHist + 1}`
  )

  // Historical series
  const histSeries = historicalVols.concat(new Array(forecastVols.length).fill(null))
  // Forecast series
  const fcSeries = new Array(nHist).fill(null).concat(forecastVols)
  // CI band
  const ciBand = new Array(nHist).fill(null).concat(
    ciLower.map((lo: number, i: number) => [lo, ciUpper[i]])
  )

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['Historical Vol', 'Forecast Vol', '90% CI'],
      textStyle: { color: '#a3a3a3', fontFamily: 'Oswald' },
      top: 0,
    },
    grid: { left: 50, right: 20, top: 40, bottom: 40 },
    xAxis: {
      type: 'category',
      data: labels,
      axisLabel: { color: '#737373', fontSize: 10, interval: Math.floor(totalLen / 10) },
      axisLine: { lineStyle: { color: '#262626' } },
    },
    yAxis: {
      type: 'value',
      name: 'Vol %',
      nameTextStyle: { color: '#737373' },
      axisLabel: { color: '#737373', formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#1a1a1a' } },
    },
    series: [
      {
        name: 'Historical Vol',
        type: 'line',
        data: histSeries,
        lineStyle: { color: '#a3a3a3', width: 1 },
        itemStyle: { color: '#a3a3a3' },
        symbol: 'none',
      },
      {
        name: 'Forecast Vol',
        type: 'line',
        data: fcSeries,
        lineStyle: { color: '#DC2626', width: 2 },
        itemStyle: { color: '#DC2626' },
        symbol: 'none',
      },
      {
        name: '90% CI',
        type: 'line',
        data: ciBand.map((v: [number, number] | null) => (v ? v[1] : null)),
        lineStyle: { opacity: 0 },
        areaStyle: { color: 'rgba(220, 38, 38, 0.08)' },
        symbol: 'none',
        stack: 'ci',
      },
      {
        name: 'CI Lower',
        type: 'line',
        data: ciBand.map((v: [number, number] | null) => (v ? v[0] : null)),
        lineStyle: { color: 'rgba(220, 38, 38, 0.3)', type: 'dashed', width: 1 },
        symbol: 'none',
      },
    ],
  }, true)
}

onMounted(() => {
  const ro = new ResizeObserver(() => chart?.resize())
  if (chartEl.value) ro.observe(chartEl.value)
  onUnmounted(() => {
    ro.disconnect()
    chart?.dispose()
    chart = null
  })
})
</script>

<style scoped>
.garch-block { margin-top: 16px; }

.garch-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.compact-select {
  padding: 4px 8px;
  font-size: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-medium);
  color: var(--text-primary);
  border-radius: 4px;
}

.horizon-control {
  display: flex;
  align-items: center;
  gap: 6px;
}

.range-slider.compact { width: 80px; }
.scrub-val { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-secondary); min-width: 32px; }

.toggle-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-secondary);
  cursor: pointer;
}

.params-row {
  display: flex;
  gap: 12px;
  padding: 8px 0;
  flex-wrap: wrap;
}

.param-field {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.param-field label {
  font-size: 10px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  font-family: 'Oswald', sans-serif;
}

.glass-input.mini {
  width: 90px;
  padding: 4px 6px;
  font-size: 12px;
}

.error-banner {
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid var(--accent-red);
  border-radius: 4px;
  padding: 8px 12px;
  color: var(--accent-red);
  font-size: 12px;
  margin-top: 8px;
}

.garch-kpi-row {
  display: flex;
  gap: 16px;
  padding: 12px 0 4px;
  flex-wrap: wrap;
}

.garch-kpi {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.garch-kpi-label {
  font-size: 10px;
  text-transform: uppercase;
  color: var(--text-tertiary);
  font-family: 'Oswald', sans-serif;
  letter-spacing: 0.05em;
}

.garch-kpi-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
}

.text-accent { color: var(--accent-red); }
.text-xs { font-size: 12px; }

.garch-chart {
  width: 100%;
  height: 300px;
  margin-top: 8px;
}

.btn-glass.compact { padding: 4px 12px; font-size: 12px; }
</style>
