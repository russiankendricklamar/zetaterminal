<template>
  <div class="bg-slate-800 rounded-lg p-6 border border-slate-700 h-full min-h-[300px]">
    <h3 class="text-lg font-bold mb-4 text-white">Risk Heatmap (Vol vs Corr)</h3>
    <div class="relative h-[250px]">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'
import Chart from 'chart.js/auto'

const store = usePortfolioStore()
const chartCanvas = ref<HTMLCanvasElement | null>(null)
let chartInstance: Chart | null = null

const renderChart = () => {
  if (!chartCanvas.value || !store.heatmapData.length) return

  if (chartInstance) {
    chartInstance.destroy()
  }

  chartInstance = new Chart(chartCanvas.value, {
    type: 'bubble',
    data: {
      datasets: store.heatmapData.map((asset) => ({
        label: asset.asset,
        data: [{
          x: asset.correlation,
          y: asset.volatility,
          r: Math.sqrt(asset.notional) / 50 // Масштабируем размер
        }],
        backgroundColor: asset.pnlPct >= 0 ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)',
        borderColor: asset.pnlPct >= 0 ? '#10b981' : '#ef4444',
        borderWidth: 1
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: { display: true, text: 'Correlation', color: '#94a3b8' },
          min: -1,
          max: 1,
          grid: { color: 'rgba(148, 163, 184, 0.1)' },
          ticks: { color: '#94a3b8' }
        },
        y: {
          title: { display: true, text: 'Volatility', color: '#94a3b8' },
          min: 0,
          grid: { color: 'rgba(148, 163, 184, 0.1)' },
          ticks: { color: '#94a3b8' }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: Vol=${ctx.raw.y.toFixed(2)}, Corr=${ctx.raw.x.toFixed(2)}`
          }
        }
      }
    }
  })
}

onMounted(renderChart)
watch(() => store.heatmapData, renderChart, { deep: true })
</script>
