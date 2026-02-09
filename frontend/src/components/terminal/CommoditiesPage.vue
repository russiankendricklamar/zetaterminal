<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box icon-orange">
          <BoxIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">СЫРЬЁ</h2>
          <p class="section-subtitle font-mono">ЭНЕРГОРЕСУРСЫ, МЕТАЛЛЫ, АГРОКОМПЛЕКС И ПОГОДА</p>
        </div>
      </div>
      <div class="tab-group">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['tab-btn', { active: section === tab.id }]">
          {{ tab.label }}
        </button>
      </div>
    </div>
    <div class="flex-1 flex flex-col gap-6">
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
  { id: 'GLCO', label: 'Международное сырьё' },
  { id: 'NRG', label: 'Рынок энергоресурсов' },
  { id: 'NGAS', label: 'Газ' },
  { id: 'FDM', label: 'Fundamentals' },
  { id: 'CPF', label: 'Прогнозы' },
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
