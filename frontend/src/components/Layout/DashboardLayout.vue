<template>
  <div class="flex h-screen bg-gradient-dark text-white">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content -->
    <div class="flex-1 flex flex-col">
      <!-- Header -->
      <header class="bg-dark-secondary border-b border-gray-700 px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <h1 class="text-2xl font-bold">📊 Stochastic Dashboard</h1>
          <span class="text-sm text-gray-400">v2.0.0</span>
        </div>
        <div class="flex items-center gap-4">
          <input
            type="text"
            placeholder="Search..."
            class="bg-dark px-4 py-2 rounded border border-gray-600 focus:border-primary outline-none text-sm"
          />
          <button class="p-2 hover:bg-dark rounded transition">
            <span>🔔</span>
          </button>
        </div>
      </header>

      <!-- Filters -->
      <FilterBar />

      <!-- Content Area -->
      <main class="flex-1 overflow-auto p-6 space-y-6">
        <!-- KPI Cards -->
        <KPICards />

        <!-- Main Grid (Heatmap + Price Chart + Model Output) -->
        <MainGrid />

        <!-- Tabbed Section (Greeks, Stress, Backtest) -->
        <TabbedSection />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'
import Sidebar from '@/components/Layout/Sidebar.vue'
import FilterBar from '@/components/Filters/FilterBar.vue'
import KPICards from '@/components/Dashboard/KPICards.vue'
import MainGrid from '@/components/Dashboard/MainGrid.vue'
import TabbedSection from '@/components/Dashboard/TabbedSection.vue'

const store = usePortfolioStore()

onMounted(() => {
  store.fetchKPIs()
  store.fetchGreeks()
  store.fetchStressScenarios()
  store.fetchModelDiagnostics()
  store.fetchPriceHistory('SPY', 60)
  store.fetchHeatmapData()
})
</script>

<style scoped>
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #0f172a;
}

::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #475569;
}
</style>
