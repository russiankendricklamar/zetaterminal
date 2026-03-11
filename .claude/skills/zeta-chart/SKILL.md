---
name: zeta-chart
description: Create charts and visualizations in zetaterminal using Chart.js, ECharts, or Three.js with brutalist design. Use when adding graphs, plots, 3D visualizations, or data displays.
---

# Zeta Terminal — Charts & Visualizations

## Library Selection

| Library | Use For | Example |
|---------|---------|---------|
| **Chart.js** | Simple 2D charts (line, bar, pie, scatter) | Portfolio returns, VaR histogram |
| **ECharts** | Complex 2D charts (heatmaps, candlestick, multi-axis) | Correlation matrix, yield curves |
| **Three.js** | 3D visualizations | Volatility surface, regime space 3D |

## Brutalist Chart Theme (MANDATORY)

```typescript
const ZETA_COLORS = {
  bg: '#050505',
  grid: '#1a1a1a',
  text: '#888888',
  textBright: '#f5f5f5',
  accent: '#DC2626',
  success: '#22C55E',
  warning: '#F59E0B',
  // Series palette (no bright/neon colors)
  series: ['#DC2626', '#F59E0B', '#22C55E', '#3B82F6', '#8B5CF6', '#888888'],
}
```

## Chart.js Template

```vue
<template>
  <div class="bg-[var(--bg-secondary)] border border-[var(--border)] rounded p-4">
    <h3 class="font-oswald text-[var(--text-primary)] mb-3">CHART TITLE</h3>
    <canvas ref="chartRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps<{
  data: number[]
  labels: string[]
}>()

const chartRef = ref<HTMLCanvasElement>()
let chart: Chart | null = null

function createChart() {
  if (!chartRef.value) return
  chart = new Chart(chartRef.value, {
    type: 'line',
    data: {
      labels: props.labels,
      datasets: [{
        data: props.data,
        borderColor: '#DC2626',
        backgroundColor: 'rgba(220, 38, 38, 0.1)',
        borderWidth: 1.5,
        pointRadius: 0,
        tension: 0,  // No curve smoothing — brutalist
      }],
    },
    options: {
      responsive: true,
      animation: false,  // No animations — brutalist
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0a0a0a',
          borderColor: '#1a1a1a',
          borderWidth: 1,
          titleFont: { family: 'Oswald' },
          bodyFont: { family: 'Space Mono' },
        },
      },
      scales: {
        x: {
          grid: { color: '#1a1a1a' },
          ticks: { color: '#888888', font: { family: 'Space Mono', size: 10 } },
        },
        y: {
          grid: { color: '#1a1a1a' },
          ticks: { color: '#888888', font: { family: 'Space Mono', size: 10 } },
        },
      },
    },
  })
}

// Update data without recreating chart
watch(() => props.data, (newData) => {
  if (chart) {
    chart.data.datasets[0].data = newData
    chart.data.labels = props.labels
    chart.update('none')
  }
})

onMounted(createChart)
onUnmounted(() => chart?.destroy())
</script>
```

## ECharts Template

```typescript
import * as echarts from 'echarts'

const option: echarts.EChartsOption = {
  backgroundColor: 'transparent',
  textStyle: { fontFamily: 'Space Mono', color: '#888888' },
  grid: { top: 40, right: 20, bottom: 40, left: 60 },
  xAxis: {
    axisLine: { lineStyle: { color: '#1a1a1a' } },
    splitLine: { lineStyle: { color: '#1a1a1a' } },
    axisLabel: { color: '#888888', fontFamily: 'Space Mono', fontSize: 10 },
  },
  yAxis: {
    axisLine: { lineStyle: { color: '#1a1a1a' } },
    splitLine: { lineStyle: { color: '#1a1a1a' } },
    axisLabel: { color: '#888888', fontFamily: 'Space Mono', fontSize: 10 },
  },
  tooltip: {
    backgroundColor: '#0a0a0a',
    borderColor: '#1a1a1a',
    textStyle: { fontFamily: 'Space Mono', color: '#f5f5f5' },
  },
}
```

## Three.js — Reference

Existing 3D patterns in project:
- `frontend/src/utils/RegimeSpaceRenderer.ts` — 3D regime space
- `frontend/src/composables/useRegimeSpace3D.ts` — composable wrapper

## Rules

- [ ] `animation: false` on Chart.js (brutalist = no animations)
- [ ] `tension: 0` on line charts (no curve smoothing)
- [ ] Colors from ZETA_COLORS palette only
- [ ] Font: Space Mono for data, Oswald for labels
- [ ] Grid: `#1a1a1a`, background: transparent (inherits from container)
- [ ] No rounded corners on chart containers beyond 6px
- [ ] `chart.update('none')` for data updates (skip animations)
- [ ] `onUnmounted(() => chart?.destroy())` — always cleanup
