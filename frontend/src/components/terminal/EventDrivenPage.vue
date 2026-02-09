<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box icon-purple">
          <RadioIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">ИВЕНТ-АНАЛИЗ</h2>
          <p class="section-subtitle font-mono">CATALYSTS, CORPORATE ACTIONS & MARKET MOVING EVENTS</p>
        </div>
      </div>
      <div class="tab-group">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['tab-btn', { active: section === tab.id }]">
          {{ tab.label }}
        </button>
      </div>
    </div>
    <div class="flex-1 flex flex-col gap-6">
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
  { id: 'IPO', label: 'Монитор IPO' },
  { id: 'CACS', label: 'Корпоративные события' },
  { id: 'QUIC', label: 'QuickTakes' },
  { id: 'CM', label: 'Ключевые события' },
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
