<template>
  <div class="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
    <!-- Tabs -->
    <div class="flex border-b border-slate-700">
      <button
        @click="activeTab = 'greeks'"
        :class="[
          'flex-1 px-4 py-3 font-medium text-sm transition',
          activeTab === 'greeks' 
            ? 'bg-slate-900 border-b-2 border-blue-500 text-blue-400' 
            : 'text-slate-400 hover:text-white'
        ]"
      >
        Greeks & Sensitivities
      </button>
      <button
        @click="activeTab = 'stress'"
        :class="[
          'flex-1 px-4 py-3 font-medium text-sm transition',
          activeTab === 'stress' 
            ? 'bg-slate-900 border-b-2 border-blue-500 text-blue-400' 
            : 'text-slate-400 hover:text-white'
        ]"
      >
        Stress Testing
      </button>
      <button
        @click="activeTab = 'backtest'"
        :class="[
          'flex-1 px-4 py-3 font-medium text-sm transition',
          activeTab === 'backtest' 
            ? 'bg-slate-900 border-b-2 border-blue-500 text-blue-400' 
            : 'text-slate-400 hover:text-white'
        ]"
      >
        Backtesting Results
      </button>
    </div>

    <!-- Content -->
    <div class="p-6">
      <!-- Greeks Tab -->
      <div v-if="activeTab === 'greeks'" class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-700">
              <th class="text-left py-2 px-4 text-slate-400">Position</th>
              <th class="text-right py-2 px-4 text-slate-400">Delta</th>
              <th class="text-right py-2 px-4 text-slate-400">Gamma</th>
              <th class="text-right py-2 px-4 text-slate-400">Vega</th>
              <th class="text-right py-2 px-4 text-slate-400">Theta</th>
              <th class="text-right py-2 px-4 text-slate-400">Rho</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="g in store.greeks" :key="g.position" class="border-b border-slate-700 hover:bg-slate-900">
              <td class="py-3 px-4">{{ g.position }}</td>
              <td class="text-right py-3 px-4 font-mono">{{ g.delta.toFixed(4) }}</td>
              <td class="text-right py-3 px-4 font-mono">{{ g.gamma.toFixed(6) }}</td>
              <td class="text-right py-3 px-4 font-mono">{{ g.vega.toFixed(2) }}</td>
              <td class="text-right py-3 px-4 font-mono" :class="g.theta < 0 ? 'text-red-500' : 'text-green-500'">
                {{ g.theta.toFixed(2) }}
              </td>
              <td class="text-right py-3 px-4 font-mono">{{ g.rho.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Stress Testing Tab -->
      <div v-if="activeTab === 'stress'" class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-700">
              <th class="text-left py-2 px-4 text-slate-400">Scenario</th>
              <th class="text-left py-2 px-4 text-slate-400">Description</th>
              <th class="text-right py-2 px-4 text-slate-400">PnL Impact</th>
              <th class="text-right py-2 px-4 text-slate-400">VaR Change</th>
              <th class="text-right py-2 px-4 text-slate-400">Probability</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in store.stressScenarios" :key="s.scenario" class="border-b border-slate-700 hover:bg-slate-900">
              <td class="py-3 px-4 font-medium">{{ s.scenario }}</td>
              <td class="py-3 px-4 text-slate-400 text-xs">{{ s.description }}</td>
              <td class="text-right py-3 px-4 font-mono" :class="s.pnlImpact < 0 ? 'text-red-500' : 'text-green-500'">
                {{ s.pnlImpact.toLocaleString() }}
              </td>
              <td class="text-right py-3 px-4 font-mono">{{ s.varChange.toLocaleString() }}</td>
              <td class="text-right py-3 px-4 font-mono">{{ (s.probability * 100).toFixed(1) }}%</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Backtesting Tab -->
      <div v-if="activeTab === 'backtest'" class="space-y-4">
        <div class="grid grid-cols-4 gap-4">
          <div class="bg-slate-900 rounded p-4">
            <p class="text-xs text-slate-400">Annual Return</p>
            <p class="text-xl font-bold text-blue-500">12.5%</p>
          </div>
          <div class="bg-slate-900 rounded p-4">
            <p class="text-xs text-slate-400">Max Drawdown</p>
            <p class="text-xl font-bold text-red-500">-18.3%</p>
          </div>
          <div class="bg-slate-900 rounded p-4">
            <p class="text-xs text-slate-400">Sharpe Ratio</p>
            <p class="text-xl font-bold text-green-500">1.45</p>
          </div>
          <div class="bg-slate-900 rounded p-4">
            <p class="text-xs text-slate-400">Win Rate</p>
            <p class="text-xl font-bold text-blue-500">58.3%</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'

const store = usePortfolioStore()
const activeTab = ref<'greeks' | 'stress' | 'backtest'>('greeks')
</script>
