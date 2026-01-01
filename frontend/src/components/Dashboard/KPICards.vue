<template>
  <div class="grid grid-cols-5 gap-4">
    <!-- KPI Card: Total PnL -->
    <div class="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <p class="text-sm text-slate-400 mb-2">Total P&L</p>
      <p class="text-2xl font-bold text-green-500">{{ formatNumber(store.kpis.totalPnL) }}</p>
      <p class="text-xs text-slate-500 mt-2">USD</p>
    </div>

    <!-- KPI Card: VaR 95 -->
    <div class="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <p class="text-sm text-slate-400 mb-2">VaR (95%)</p>
      <p class="text-2xl font-bold text-red-500">{{ formatNumber(store.kpis.var95) }}</p>
      <p class="text-xs text-slate-500 mt-2">Confidence Level</p>
    </div>

    <!-- KPI Card: Expected Shortfall -->
    <div class="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <p class="text-sm text-slate-400 mb-2">CVaR (ES)</p>
      <p class="text-2xl font-bold text-red-500">{{ formatNumber(store.kpis.expectedShortfall) }}</p>
      <p class="text-xs text-slate-500 mt-2">Expected Shortfall</p>
    </div>

    <!-- KPI Card: Sharpe Ratio -->
    <div class="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <p class="text-sm text-slate-400 mb-2">Sharpe Ratio</p>
      <p class="text-2xl font-bold text-blue-500">{{ store.kpis.sharpeRatio.toFixed(2) }}</p>
      <p class="text-xs text-slate-500 mt-2">Risk-Adjusted Return</p>
    </div>

    <!-- KPI Card: Max Drawdown -->
    <div class="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <p class="text-sm text-slate-400 mb-2">Max Drawdown</p>
      <p class="text-2xl font-bold" :class="store.kpis.maxDrawdown < 0 ? 'text-red-500' : 'text-green-500'">
        {{ (store.kpis.maxDrawdown * 100).toFixed(2) }}%
      </p>
      <p class="text-xs text-slate-500 mt-2">Peak-to-Trough</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePortfolioStore } from '@/stores/portfolio'

const store = usePortfolioStore()

const formatNumber = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0
  }).format(value)
}
</script>
