<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 p-8 flex flex-col animate-fade-in overflow-y-auto custom-scrollbar">
    <div class="text-center mb-10">
      <h1 class="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-500 mb-2">Grow Your Assets</h1>
      <p class="text-gray-400">Simple. Secure. High Yields.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="p in products" 
        :key="p.asset" 
        class="bg-white/5 border border-white/5 rounded-2xl p-6 hover:bg-white/10 transition-all hover:-translate-y-1 cursor-pointer group hover:border-white/20"
      >
        <div class="flex justify-between items-start mb-6">
          <div class="w-12 h-12 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-white text-lg shadow-lg">
            {{ p.asset.substring(0, 2) }}
          </div>
          <span class="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-[10px] font-bold uppercase tracking-wide border border-emerald-500/20">{{ p.type }}</span>
        </div>
        <div class="mb-6">
          <div class="text-4xl font-bold text-white mb-2 group-hover:text-emerald-400 transition-colors tracking-tight">{{ p.apy }}</div>
          <div class="text-xs text-gray-500 uppercase font-bold tracking-wider">APY</div>
        </div>
        <div class="flex justify-between items-center text-xs text-gray-400 border-t border-white/5 pt-4">
          <span>Duration: <span class="text-white font-medium">{{ p.duration }}</span></span>
          <ShieldCheckIcon class="w-4 h-4 text-indigo-400" />
        </div>
      </div>
    </div>

    <div class="mt-8 p-6 rounded-2xl bg-gradient-to-r from-indigo-900/40 to-purple-900/40 border border-white/10 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="p-4 bg-white/10 rounded-xl backdrop-blur-md">
          <TrendingUpIcon class="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 class="font-bold text-white text-lg">Auto-Invest</h3>
          <p class="text-sm text-gray-400">Accumulate crypto on autopilot with dollar-cost averaging.</p>
        </div>
      </div>
      <button class="px-8 py-3 bg-white text-black font-bold rounded-xl hover:scale-105 transition-transform shadow-lg shadow-white/10">Start Now</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineComponent, h } from 'vue';

const ShieldCheckIcon = defineComponent({
  render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
    h('path', { d: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z' }),
    h('path', { d: 'm9 12 2 2 4-4' })
  ])
});

const TrendingUpIcon = defineComponent({
  render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
    h('polyline', { points: '23 6 13.5 15.5 8.5 10.5 1 18' }),
    h('polyline', { points: '17 6 23 6 23 12' })
  ])
});

const products = [
  { asset: 'USDT', apy: '12.5%', duration: 'Flexible', type: 'Savings' },
  { asset: 'BTC', apy: '4.2%', duration: '30 Days', type: 'Staking' },
  { asset: 'ETH', apy: '5.8%', duration: 'Locked', type: 'Staking' },
  { asset: 'DOT', apy: '14.2%', duration: '90 Days', type: 'Staking' },
  { asset: 'SOL', apy: '7.5%', duration: 'Flexible', type: 'Staking' },
  { asset: 'USDC', apy: '10.0%', duration: 'Flexible', type: 'Savings' },
];
</script>
