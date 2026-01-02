<template>
  <div class="bg-slate-800 rounded-lg p-6 border border-slate-700 h-full min-h-[300px]">
    <h3 class="text-lg font-bold mb-4 text-white">Price History</h3>
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
  if (!chartCanvas.value || !store.priceHistory.length) return

  if (chartInstance) {
    chartInstance.destroy()
  }

  const labels = store.priceHistory.map(p => new Date(p.date).toLocaleDateString())
  const prices = store.priceHistory.map(p => p.close)

  chartInstance = new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Price',
        data: prices,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.2,
        pointRadius: 0,
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { 
          grid: { display: false },
          ticks: { color: '#94a3b8', maxRotation: 0 }
        },
        y: { 
          grid: { color: 'rgba(148, 163, 184, 0.1)' },
          ticks: { color: '#94a3b8' }
        }
      }
    }
  })
}

onMounted(renderChart)

// Следим за обновлением данных в сторе
watch(() => store.priceHistory, renderChart, { deep: true })
</script>
