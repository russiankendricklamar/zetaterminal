<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full">
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-rose-600/20 to-red-600/20 flex items-center justify-center text-lg font-bold text-rose-400 border border-rose-500/30">
          <ShieldAlertIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">Credit Risk Analysis</h2>
          <p class="text-xs text-gray-400">Ratings, Default Risk & Debt Structure</p>
        </div>
      </div>
      <div class="flex bg-black/40 rounded-xl p-1 border border-white/5 overflow-x-auto max-w-full custom-scrollbar">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap', section === tab.id ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'text-gray-500 hover:text-white hover:bg-white/5']">
          {{ tab.label }}
        </button>
      </div>
    </div>
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <CreditRatings v-if="section === 'RATC'" :symbol="symbol" />
      <CDSSpreads v-else-if="section === 'GCDS'" :symbol="symbol" />
      <ProbDefault v-else-if="section === 'SRSK'" :symbol="symbol" />
      <DebtDist v-else-if="section === 'DDIS'" :symbol="symbol" />
      <CreditRatings v-else :symbol="symbol" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineComponent, h } from 'vue';

const ShieldAlertIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('path', { d: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z' }), h('line', { x1: '12', y1: '8', x2: '12', y2: '12' }), h('line', { x1: '12', y1: '16', x2: '12.01', y2: '16' })]) });

const props = defineProps<{ symbol?: string; activeSection?: string; }>();
const section = ref(props.activeSection || 'RATC');
const symbol = ref(props.symbol || 'AAPL');
watch(() => props.activeSection, (v) => { if (v) section.value = v; });

const tabs = [
  { id: 'RATC', label: 'Credit Ratings' },
  { id: 'GCDS', label: 'CDS Spreads' },
  { id: 'SRSK', label: 'Prob. of Default' },
  { id: 'DDIS', label: 'Debt Dist.' },
];

const CreditRatings = defineComponent({
  props: ['symbol'],
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">S&P Global</h3>
          <div class="flex items-baseline gap-2"><div class="text-4xl font-bold text-white">AA+</div><span class="text-xs font-bold text-gray-500 bg-black/30 px-2 py-1 rounded">Stable</span></div>
          <div class="mt-4 text-xs text-gray-400">Last Action: Affirmed (Oct 2024)</div>
        </div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Moody's</h3>
          <div class="flex items-baseline gap-2"><div class="text-4xl font-bold text-white">Aa1</div><span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">Positive</span></div>
          <div class="mt-4 text-xs text-gray-400">Last Action: Outlook Rev (Sep 2024)</div>
        </div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Fitch</h3>
          <div class="flex items-baseline gap-2"><div class="text-4xl font-bold text-white">AA</div><span class="text-xs font-bold text-gray-500 bg-black/30 px-2 py-1 rounded">Stable</span></div>
          <div class="mt-4 text-xs text-gray-400">Last Action: Affirmed (Nov 2024)</div>
        </div>
      </div>
      <div class="flex-1 bg-black/20 rounded-2xl border border-white/5 p-6 flex items-center justify-center text-gray-500">
        [Rating History Timeline]
      </div>
    </div>
  `
});

const CDSSpreads = defineComponent({
  props: ['symbol'],
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="flex justify-between items-end">
        <div><h3 class="text-lg font-bold text-white mb-1">5Y Senior CDS Spread</h3><div class="flex items-center gap-3"><span class="text-3xl font-bold text-emerald-400">42.5 bps</span><span class="text-xs font-bold text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded">-2.1 bps (Today)</span></div></div>
      </div>
      <div class="flex-1 bg-black/20 rounded-2xl border border-white/5 p-4 flex items-center justify-center text-gray-500">[CDS Spread Chart]</div>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="p-4 rounded-xl bg-white/5 border border-white/5"><div class="text-xs text-gray-500 uppercase font-bold mb-1">Implied Rating</div><div class="text-lg font-bold text-white">AA-</div></div>
        <div class="p-4 rounded-xl bg-white/5 border border-white/5"><div class="text-xs text-gray-500 uppercase font-bold mb-1">Recovery Rate</div><div class="text-lg font-bold text-white">40%</div></div>
        <div class="p-4 rounded-xl bg-white/5 border border-white/5"><div class="text-xs text-gray-500 uppercase font-bold mb-1">Z-Score (1Y)</div><div class="text-lg font-bold text-emerald-400">-1.2</div></div>
        <div class="p-4 rounded-xl bg-white/5 border border-white/5"><div class="text-xs text-gray-500 uppercase font-bold mb-1">Liquidity</div><div class="text-lg font-bold text-white">High</div></div>
      </div>
    </div>
  `
});

const ProbDefault = defineComponent({ props: ['symbol'], template: `<div class="flex items-center justify-center h-full text-gray-500">[Probability of Default Analysis]</div>` });
const DebtDist = defineComponent({ props: ['symbol'], template: `<div class="flex items-center justify-center h-full text-gray-500">[Debt Distribution Charts]</div>` });
</script>
