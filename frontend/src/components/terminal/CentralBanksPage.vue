<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box">
          <BuildingIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">ЦЕНТРАЛЬНЫЕ БАНКИ</h2>
          <p class="section-subtitle font-mono">ДЕНЕЖНО-КРЕДИТНАЯ ПОЛИТИКА, СТАВКИ, ЛИКВИДНОСТЬ</p>
        </div>
      </div>
      <div class="tab-group">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['tab-btn', { active: section === tab.id }]">
          {{ tab.label }}
        </button>
      </div>
    </div>
    <div class="flex-1 flex flex-col gap-6">
      <BankOfRussia v-if="section === 'CBR'" />
      <FederalReserve v-else-if="section === 'FED'" />
      <GlobalCBs v-else-if="section === 'CENB'" />
      <FOMCCenter v-else-if="section === 'FOMC'" />
      <BankOfRussia v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineComponent, h } from 'vue';

const BuildingIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('rect', { x: '3', y: '4', width: '18', height: '16', rx: '2' }), h('path', { d: 'M16 2v2' }), h('path', { d: 'M8 2v2' }), h('path', { d: 'M3 10h18' })]) });

const props = defineProps<{ symbol?: string; activeSection?: string; }>();
const section = ref(props.activeSection || 'CBR');
watch(() => props.activeSection, (v) => { if (v) section.value = v; });

const tabs = [
  { id: 'CBR', label: 'Банк России' },
  { id: 'FED', label: 'ФРС' },
  { id: 'CENB', label: 'Международные ЦБ' },
  { id: 'FOMC', label: 'Расшифровки совещаний' },
];

const BankOfRussia = defineComponent({
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Key Rate</h3>
          <div class="text-3xl font-bold text-rose-400">21.00%</div>
          <div class="text-xs text-rose-500 mt-1">Hawkish Stance</div>
        </div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Inflation (YoY)</h3>
          <div class="text-3xl font-bold text-white">8.5%</div>
          <div class="text-xs text-gray-500 mt-1">Target: 4.0%</div>
        </div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Next Decision</h3>
          <div class="text-3xl font-bold text-white">Dec 20</div>
          <div class="text-xs text-gray-500 mt-1">13:30 MSK</div>
        </div>
      </div>
      <div class="flex-1 bg-black/20 rounded-2xl border border-white/5 p-6 flex items-center justify-center text-gray-500">
        [Rate vs Inflation Chart]
      </div>
    </div>
  `
});

const FederalReserve = defineComponent({
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="flex justify-between items-center">
        <div><h3 class="text-lg font-bold text-white">Federal Funds Rate</h3><div class="flex items-center gap-3"><span class="text-3xl font-bold text-emerald-400">4.75 - 5.00%</span><span class="text-xs font-bold text-gray-500 bg-white/10 px-2 py-1 rounded">Target Range</span></div></div>
        <div class="flex gap-4"><div class="text-right"><div class="text-xs text-gray-500 uppercase font-bold">Balance Sheet</div><div class="text-lg font-bold text-white">$7.1 Trillion</div></div><div class="text-right"><div class="text-xs text-gray-500 uppercase font-bold">Next Meeting</div><div class="text-lg font-bold text-white">Nov 07</div></div></div>
      </div>
      <div class="flex-1 bg-black/20 rounded-2xl border border-white/5 p-6 flex items-center justify-center text-gray-500">[Dot Plot Chart]</div>
    </div>
  `
});

const GlobalCBs = defineComponent({
  setup() {
    const cbs = [
      { country: 'USA', bank: 'Fed', rate: '5.00%', change: '-25bp', sentiment: 'Neutral', next: 'Nov 07' },
      { country: 'Eurozone', bank: 'ECB', rate: '3.25%', change: '-25bp', sentiment: 'Dovish', next: 'Dec 12' },
      { country: 'UK', bank: 'BoE', rate: '5.00%', change: '0bp', sentiment: 'Neutral', next: 'Nov 07' },
      { country: 'Japan', bank: 'BoJ', rate: '0.25%', change: '+15bp', sentiment: 'Hawkish', next: 'Oct 31' },
      { country: 'Russia', bank: 'CBR', rate: '21.00%', change: '+100bp', sentiment: 'Hawkish', next: 'Dec 20' },
    ];
    return { cbs };
  },
  template: `
    <div class="flex flex-col h-full gap-6">
      <h3 class="text-lg font-bold text-white">Global Policy Rates</h3>
      <div class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
        <table class="w-full text-left border-collapse"><thead><tr class="text-xs text-gray-400 uppercase bg-white/5"><th class="p-4">Country</th><th class="p-4">Central Bank</th><th class="p-4 text-right">Current Rate</th><th class="p-4 text-right">Last Change</th><th class="p-4">Bias</th><th class="p-4 text-right">Next Meeting</th></tr></thead>
        <tbody class="text-sm font-mono text-gray-300">
          <tr v-for="cb in cbs" :key="cb.country" class="border-b border-white/5 hover:bg-white/5">
            <td class="p-4 font-bold text-white">{{ cb.country }}</td>
            <td class="p-4">{{ cb.bank }}</td>
            <td class="p-4 text-right font-bold text-white">{{ cb.rate }}</td>
            <td :class="['p-4 text-right', cb.change.includes('-') ? 'text-emerald-400' : cb.change === '0bp' ? 'text-gray-500' : 'text-rose-400']">{{ cb.change }}</td>
            <td class="p-4"><span :class="['px-2 py-1 rounded text-xs font-bold border', cb.sentiment === 'Hawkish' ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' : cb.sentiment === 'Dovish' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-gray-700/30 border-gray-600/30 text-gray-400']">{{ cb.sentiment }}</span></td>
            <td class="p-4 text-right text-gray-400">{{ cb.next }}</td>
          </tr>
        </tbody></table>
      </div>
    </div>
  `
});

const FOMCCenter = defineComponent({ template: `<div class="flex items-center justify-center h-full text-gray-500">[FOMC Meeting Analysis]</div>` });
</script>
