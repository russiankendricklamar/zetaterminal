<template>
  <div class="bg-slate-800 border-b border-slate-700 px-6 py-4">
    <div class="flex gap-4 flex-wrap items-center">
      <!-- Date Range -->
      <div>
        <label class="text-xs text-slate-400 block mb-1">Date Range</label>
        <input
          type="date"
          class="bg-slate-900 px-3 py-2 rounded border border-slate-600 focus:border-blue-500 outline-none text-sm"
        />
      </div>

      <!-- Portfolio Selector -->
      <div>
        <label class="text-xs text-slate-400 block mb-1">Portfolio</label>
        <select class="bg-slate-900 px-3 py-2 rounded border border-slate-600 focus:border-blue-500 outline-none text-sm">
          <option>All Portfolios</option>
          <option>Portfolio A</option>
          <option>Portfolio B</option>
        </select>
      </div>

      <!-- Model Selector -->
      <div>
        <label class="text-xs text-slate-400 block mb-1">Model</label>
        <select
          v-model="store.selectedModel"
          class="bg-slate-900 px-3 py-2 rounded border border-slate-600 focus:border-blue-500 outline-none text-sm"
        >
          <option>Lévy Process</option>
          <option>HMM</option>
          <option>Gaussian</option>
        </select>
      </div>

      <!-- Action Buttons -->
      <div class="ml-auto flex gap-2">
        <button
          @click="applyFilters"
          class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium transition"
        >
          Apply
        </button>
        <button
          @click="resetFilters"
          class="bg-slate-600 hover:bg-slate-700 px-4 py-2 rounded text-sm font-medium transition"
        >
          Reset
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePortfolioStore } from '@/stores/portfolio'

const store = usePortfolioStore()

const applyFilters = () => {
  console.log('Filters applied')
  store.fetchPriceHistory('SPY', 60)
  store.fetchHeatmapData()
}

const resetFilters = () => {
  console.log('Filters reset')
}
</script>
