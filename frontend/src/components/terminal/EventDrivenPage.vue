<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full">
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-600/20 to-pink-600/20 flex items-center justify-center text-lg font-bold text-purple-300 border border-purple-500/30">
          <RadioIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">Event-Driven Analysis</h2>
          <p class="text-xs text-gray-400">Catalysts, Corporate Actions & Market Moving Events</p>
        </div>
      </div>
      <div class="flex bg-black/40 rounded-xl p-1 border border-white/5 overflow-x-auto max-w-full custom-scrollbar">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap', section === tab.id ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' : 'text-gray-500 hover:text-white hover:bg-white/5']">
          {{ tab.label }}
        </button>
      </div>
    </div>
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <IPOMonitor v-if="section === 'IPO'" />
      <CorporateEvents v-else-if="section === 'CACS'" :symbol="symbol" />
      <QuickTakes v-else-if="section === 'QUIC'" :symbol="symbol" />
      <KeyEvents v-else-if="section === 'CM'" :symbol="symbol" />
      <IPOMonitor v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineComponent, h } from 'vue';

const RadioIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('circle', { cx: '12', cy: '12', r: '2' }), h('path', { d: 'M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14' })]) });

const props = defineProps<{ symbol?: string; activeSection?: string; }>();
const section = ref(props.activeSection || 'IPO');
const symbol = ref(props.symbol || 'NVDA');
watch(() => props.activeSection, (v) => { if (v) section.value = v; });

const tabs = [
  { id: 'IPO', label: 'IPO Monitor' },
  { id: 'CACS', label: 'Corporate Events' },
  { id: 'QUIC', label: 'QuickTakes' },
  { id: 'CM', label: 'Key Events' },
];

const IPOMonitor = defineComponent({
  setup() {
    const ipos = [
      { name: 'Stripe Inc.', symbol: 'STRIP', date: 'Q4 2025', range: '$45 - $55', shares: '25M', exchange: 'NYSE', status: 'Filing' },
      { name: 'Discord', symbol: 'DSCD', date: 'Q1 2026', range: '$30 - $35', shares: '18M', exchange: 'NASDAQ', status: 'Rumored' },
      { name: 'SpaceX (Starlink)', symbol: 'LINK', date: 'TBD', range: 'N/A', shares: 'N/A', exchange: 'NASDAQ', status: 'Rumored' },
      { name: 'Databricks', symbol: 'DATA', date: 'Oct 28', range: '$60 - $70', shares: '15M', exchange: 'NYSE', status: 'Pricing' },
    ];
    return { ipos };
  },
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5"><h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Upcoming Volume</h3><div class="text-3xl font-bold text-white">$12.5B</div><div class="text-xs text-emerald-400 mt-1">High Activity Expected Q4</div></div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5"><h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Avg First Day Pop</h3><div class="text-3xl font-bold text-white">+18.2%</div><div class="text-xs text-gray-500 mt-1">Tech Sector (YTD)</div></div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5"><h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Market Sentiment</h3><div class="text-3xl font-bold text-emerald-400">Warm</div></div>
      </div>
      <div class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
        <table class="w-full text-left border-collapse"><thead><tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0"><th class="p-4">Company</th><th class="p-4">Symbol</th><th class="p-4">Expected Date</th><th class="p-4">Price Range</th><th class="p-4">Shares</th><th class="p-4">Exchange</th><th class="p-4 text-right">Status</th></tr></thead>
        <tbody class="text-sm font-mono text-gray-300">
          <tr v-for="(ipo, i) in ipos" :key="i" class="border-b border-white/5 hover:bg-white/5 group">
            <td class="p-4 font-bold text-white">{{ ipo.name }}</td>
            <td class="p-4 text-purple-300">{{ ipo.symbol }}</td>
            <td class="p-4">{{ ipo.date }}</td>
            <td class="p-4">{{ ipo.range }}</td>
            <td class="p-4 text-gray-500">{{ ipo.shares }}</td>
            <td class="p-4">{{ ipo.exchange }}</td>
            <td class="p-4 text-right"><span :class="['px-2 py-1 rounded text-xs font-bold border', ipo.status === 'Pricing' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : ipo.status === 'Filing' ? 'bg-blue-500/10 border-blue-500/20 text-blue-400' : 'bg-gray-700/30 border-gray-600/30 text-gray-400']">{{ ipo.status }}</span></td>
          </tr>
        </tbody></table>
      </div>
    </div>
  `
});

const CorporateEvents = defineComponent({ props: ['symbol'], template: `<div class="flex items-center justify-center h-full text-gray-500">[Corporate Events Timeline]</div>` });
const QuickTakes = defineComponent({ props: ['symbol'], template: `<div class="flex items-center justify-center h-full text-gray-500">[QuickTakes Analysis Cards]</div>` });
const KeyEvents = defineComponent({ props: ['symbol'], template: `<div class="flex items-center justify-center h-full text-gray-500">[Key Events Price Impact Chart]</div>` });
</script>
