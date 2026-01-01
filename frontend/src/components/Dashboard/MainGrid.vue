<template>
  <div class="grid grid-cols-3 gap-6">
    <!-- Heatmap Chart -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-lg font-bold mb-4">Portfolio Heatmap</h3>
      <canvas id="heatmapChart"></canvas>
    </div>

    <!-- Price Chart -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-lg font-bold mb-4">Price Action ({{ store.selectedModel }})</h3>
      <canvas id="priceChart"></canvas>
    </div>

    <!-- Model Output -->
    <div class="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 class="text-lg font-bold mb-4">Model Diagnostics</h3>
      <div class="space-y-3 text-sm">
        <div class="flex justify-between">
          <span class="text-slate-400">Model:</span>
          <span class="font-semibold">{{ store.modelDiagnostics.modelName }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-400">KS Test:</span>
          <span class="font-semibold">{{ store.modelDiagnostics.ksTestPValue?.toFixed(4) ?? 'N/A' }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-400">Accuracy:</span>
          <span class="font-semibold text-green-500">{{ (store.modelDiagnostics.backtestingAccuracy * 100).toFixed(1) }}%</span>
        </div>
        <button
          @click="runMonteCarlo"
          class="w-full mt-4 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium transition"
        >
          🎲 Run MC (10k paths)
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'
import Chart from 'chart.js/auto'

const store = usePortfolioStore()

onMounted(() => {
  renderHeatmapChart()
  renderPriceChart()
  store.fetchModelDiagnostics()
})

const renderHeatmapChart = () => {
  if (!store.heatmapData.length) return
  const ctx = document.getElementById('heatmapChart') as HTMLCanvasElement
  if (!ctx) return

  new Chart(ctx, {
    type: 'bubble',
    data: {
      datasets: store.heatmapData.map((item) => ({
        label: item.asset,
        data: [{
          x: item.correlation,
          y: item.volatility,
          r: Math.sqrt(Math.abs(item.notional)) / 50
        }],
        backgroundColor: item.pnl > 0 ? 'rgba(34, 197, 94, 0.6)' : 'rgba(239, 68, 68, 0.6)',
        borderColor: item.pnl > 0 ? '#22c55e' : '#ef4444',
        borderWidth: 2
      }))
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { min: -1, max: 1, title: { display: true, text: 'Correlation' } },
        y: { min: 0, max: 0.5, title: { display: true, text: 'Volatility' } }
      }
    }
  })
}

const renderPriceChart = () => {
  if (!store.priceHistory.length) return
  const ctx = document.getElementById('priceChart') as HTMLCanvasElement
  if (!ctx) return

  const dates = store.priceHistory.map(p => new Date(p.date).toLocaleDateString())
  const closes = store.priceHistory.map(p => p.close)

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: dates,
      datasets: [{
        label: 'Close',
        data: closes,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.1,
        fill: true
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true } },
      scales: {
        y: { beginAtZero: false }
      }
    }
  })
}

const runMonteCarlo = async () => {
  const result = await store.runMonteCarlo(10000, 252, 'levy')
  console.log('Monte Carlo result:', result)
  alert(`MC completed: VaR95=${result.results.var95.toFixed(3)}`)
}
</script>
