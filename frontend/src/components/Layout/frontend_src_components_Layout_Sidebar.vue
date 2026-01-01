<template>
  <aside class="w-64 bg-slate-800 border-r border-slate-700 p-6 h-screen">
    <!-- Logo -->
    <div class="mb-8">
      <h2 class="text-xl font-bold text-blue-500">📈 QA Suite</h2>
      <p class="text-xs text-slate-400 mt-1">v2.0.0</p>
    </div>

    <!-- Navigation Menu -->
    <nav class="space-y-2">
      <!-- Analytics -->
      <div>
        <h3 class="text-xs uppercase font-semibold text-slate-500 px-3 py-2">Analytics</h3>
        <button class="w-full text-left px-3 py-2 rounded hover:bg-slate-700 transition text-sm">
          📊 Dashboard
        </button>
        <button class="w-full text-left px-3 py-2 rounded hover:bg-slate-700 transition text-sm">
          📈 Risk Metrics
        </button>
        <button class="w-full text-left px-3 py-2 rounded hover:bg-slate-700 transition text-sm">
          🎯 Portfolio Optimization
        </button>
      </div>

      <!-- Tools -->
      <div class="mt-6">
        <h3 class="text-xs uppercase font-semibold text-slate-500 px-3 py-2">Tools</h3>
        <button class="w-full text-left px-3 py-2 rounded hover:bg-slate-700 transition text-sm">
          🎲 Monte Carlo
        </button>
        <button class="w-full text-left px-3 py-2 rounded hover:bg-slate-700 transition text-sm">
          🧪 Backtesting
        </button>
        <button class="w-full text-left px-3 py-2 rounded hover:bg-slate-700 transition text-sm">
          ⚠️ Stress Testing
        </button>
      </div>

      <!-- Data -->
      <div class="mt-6">
        <h3 class="text-xs uppercase font-semibold text-slate-500 px-3 py-2">Data</h3>
        <button class="w-full text-left px-3 py-2 rounded hover:bg-slate-700 transition text-sm">
          📊 Market Data
        </button>
        <button class="w-full text-left px-3 py-2 rounded hover:bg-slate-700 transition text-sm">
          💾 Historical
        </button>
        <button class="w-full text-left px-3 py-2 rounded hover:bg-slate-700 transition text-sm">
          ⚙️ Configuration
        </button>
      </div>
    </nav>

    <!-- Footer -->
    <div class="absolute bottom-6 left-6 right-6 pt-4 border-t border-slate-700">
      <p class="text-xs text-slate-500">© 2026 Stochastic Analytics</p>
    </div>
  </aside>
</template>

<script setup lang="ts">
// Navigation functionality
</script>

<style scoped>
button:hover {
  background-color: rgb(51, 65, 85);
}

button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: -2px;
}
</style>
