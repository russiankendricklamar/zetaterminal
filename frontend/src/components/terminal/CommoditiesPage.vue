<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full">
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-600/20 to-amber-600/20 flex items-center justify-center text-lg font-bold text-orange-400 border border-orange-500/30">
          <BoxIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">Commodities</h2>
          <p class="text-xs text-gray-400">Energy, Metals, Agriculture & Weather</p>
        </div>
      </div>
      <div class="flex bg-black/40 rounded-xl p-1 border border-white/5 overflow-x-auto max-w-full custom-scrollbar">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap', section === tab.id ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30' : 'text-gray-500 hover:text-white hover:bg-white/5']">
          {{ tab.label }}
        </button>
      </div>
    </div>
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <GlobalCommodities v-if="section === 'GLCO'" />
      <EnergyMarkets v-else-if="section === 'NRG'" />
      <NaturalGas v-else-if="section === 'NGAS'" />
      <Fundamentals v-else-if="section === 'FDM'" />
      <Forecasts v-else-if="section === 'CPF'" />
      <GlobalCommodities v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineComponent, h } from 'vue';

const BoxIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('path', { d: 'M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z' }), h('polyline', { points: '3.27 6.96 12 12.01 20.73 6.96' }), h('line', { x1: '12', y1: '22.08', x2: '12', y2: '12' })]) });

const props = defineProps<{ symbol?: string; activeSection?: string; }>();
const section = ref(props.activeSection || 'GLCO');
watch(() => props.activeSection, (v) => { if (v) section.value = v; });

const tabs = [
  { id: 'GLCO', label: 'Global Commodities' },
  { id: 'NRG', label: 'Energy Markets' },
  { id: 'NGAS', label: 'Natural Gas' },
  { id: 'FDM', label: 'Fundamentals' },
  { id: 'CPF', label: 'Price Forecasts' },
];

const GlobalCommodities = defineComponent({
  setup() {
    const data = [
      { name: 'Crude Oil (WTI)', price: 74.25, change: -0.45, unit: 'USD/bbl' },
      { name: 'Brent Crude', price: 78.10, change: -0.30, unit: 'USD/bbl' },
      { name: 'Gold', price: 2685.50, change: 1.25, unit: 'USD/t.oz' },
      { name: 'Silver', price: 32.15, change: 2.10, unit: 'USD/t.oz' },
      { name: 'Copper', price: 4.35, change: 0.85, unit: 'USD/lb' },
      { name: 'Natural Gas', price: 2.85, change: -1.20, unit: 'USD/MMBtu' },
      { name: 'Corn', price: 425.00, change: 0.50, unit: 'USD/bu' },
      { name: 'Soybeans', price: 1150.25, change: -0.15, unit: 'USD/bu' },
    ];
    return { data };
  },
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-bold text-white">Global Benchmark Prices</h3>
        <div class="flex gap-2">
          <span class="px-2 py-1 bg-emerald-500/10 text-emerald-400 text-xs rounded border border-emerald-500/20">Metals Bullish</span>
          <span class="px-2 py-1 bg-rose-500/10 text-rose-400 text-xs rounded border border-rose-500/20">Energy Bearish</span>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="(item, i) in data" :key="i" class="p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all cursor-pointer group">
          <div class="flex justify-between items-start mb-2">
            <h4 class="text-sm font-bold text-gray-300 group-hover:text-white">{{ item.name }}</h4>
          </div>
          <div class="flex items-baseline gap-2 mb-1">
            <span class="text-2xl font-bold text-white">{{ item.price.toLocaleString() }}</span>
            <span class="text-xs text-gray-500">{{ item.unit }}</span>
          </div>
          <div :class="['text-xs font-bold', item.change >= 0 ? 'text-emerald-400' : 'text-rose-400']">
            {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
          </div>
        </div>
      </div>
      <div class="flex-1 bg-black/20 rounded-2xl border border-white/5 p-6 flex items-center justify-center text-gray-500">
        [YTD Performance Chart]
      </div>
    </div>
  `
});

const EnergyMarkets = defineComponent({ template: `<div class="flex items-center justify-center h-full text-gray-500">[Energy Markets Charts]</div>` });
const NaturalGas = defineComponent({ template: `<div class="flex items-center justify-center h-full text-gray-500">[Natural Gas Storage Charts]</div>` });
const Fundamentals = defineComponent({ template: `<div class="flex items-center justify-center h-full text-gray-500">[Oil Market Balance & Inventory]</div>` });
const Forecasts = defineComponent({ template: `<div class="flex items-center justify-center h-full text-gray-500">[Analyst Price Forecasts Table]</div>` });
</script>
