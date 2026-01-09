<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full">
    <!-- Header -->
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-teal-600/20 to-cyan-600/20 flex items-center justify-center text-lg font-bold text-teal-400 border border-teal-500/30">
          <LayersIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">Bond Market Data</h2>
          <p class="text-xs text-gray-400">Global Government & Corporate Debt Markets</p>
        </div>
      </div>

      <div class="flex bg-black/40 rounded-xl p-1 border border-white/5 overflow-x-auto max-w-full custom-scrollbar">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="section = tab.id"
          :class="[
            'px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 whitespace-nowrap',
            section === tab.id || (section === 'PX1' && tab.id === 'BBT') 
              ? 'bg-teal-500/20 text-teal-300 border border-teal-500/30' 
              : 'text-gray-500 hover:text-white hover:bg-white/5'
          ]"
        >
          <component :is="tab.icon" class="w-3.5 h-3.5" /> {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <FederalLoanBonds v-if="section === 'BBT' || section === 'PX1'" />
      <AllQuotes v-else-if="section === 'ALLQ'" />
      <BondPicks v-else-if="section === 'PICK'" />
      <SovereignBonds v-else-if="section === 'WB'" />
      <NewIssueMonitor v-else-if="section === 'NIM'" />
      <FederalLoanBonds v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineComponent, h } from 'vue';

// Icons
const LayersIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('polygon', { points: '12 2 2 7 12 12 22 7 12 2' }), h('polyline', { points: '2 17 12 22 22 17' }), h('polyline', { points: '2 12 12 17 22 12' })]) });
const ShieldCheckIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('path', { d: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z' }), h('path', { d: 'm9 12 2 2 4-4' })]) });
const ListIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('line', { x1: '8', y1: '6', x2: '21', y2: '6' }), h('line', { x1: '8', y1: '12', x2: '21', y2: '12' }), h('line', { x1: '8', y1: '18', x2: '21', y2: '18' }), h('line', { x1: '3', y1: '6', x2: '3.01', y2: '6' }), h('line', { x1: '3', y1: '12', x2: '3.01', y2: '12' }), h('line', { x1: '3', y1: '18', x2: '3.01', y2: '18' })]) });
const AwardIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('circle', { cx: '12', cy: '8', r: '7' }), h('polyline', { points: '8.21 13.89 7 23 12 20 17 23 15.79 13.88' })]) });
const GlobeIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('circle', { cx: '12', cy: '12', r: '10' }), h('line', { x1: '2', y1: '12', x2: '22', y2: '12' }), h('path', { d: 'M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z' })]) });
const CalendarIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('rect', { x: '3', y: '4', width: '18', height: '18', rx: '2', ry: '2' }), h('line', { x1: '16', y1: '2', x2: '16', y2: '6' }), h('line', { x1: '8', y1: '2', x2: '8', y2: '6' }), h('line', { x1: '3', y1: '10', x2: '21', y2: '10' })]) });

const props = defineProps<{
  activeSection?: string;
}>();

const section = ref(props.activeSection || 'BBT');

watch(() => props.activeSection, (newVal) => {
  if (newVal) section.value = newVal;
});

const tabs = [
  { id: 'BBT', label: 'Federal Bonds', icon: ShieldCheckIcon },
  { id: 'ALLQ', label: 'All Quotes', icon: ListIcon },
  { id: 'PICK', label: 'Bond Picks', icon: AwardIcon },
  { id: 'WB', label: 'Sovereign Monitor', icon: GlobeIcon },
  { id: 'NIM', label: 'New Issues', icon: CalendarIcon },
];

// Sub-components
const FederalLoanBonds = defineComponent({
  setup() {
    const bonds = [
      { id: '26238', mat: '15/05/2041', cpn: '7.10%', price: '68.450', yld: '12.45%', spread: '2bp', vol: '1.2B' },
      { id: '26243', mat: '19/05/2038', cpn: '9.80%', price: '82.150', yld: '12.20%', spread: '3bp', vol: '850M' },
      { id: '26244', mat: '15/03/2034', cpn: '11.25%', price: '94.200', yld: '11.95%', spread: '2bp', vol: '2.1B' },
      { id: '26242', mat: '29/08/2029', cpn: '9.00%', price: '88.500', yld: '11.50%', spread: '1bp', vol: '540M' },
      { id: '26241', mat: '17/11/2032', cpn: '9.50%', price: '85.600', yld: '11.85%', spread: '4bp', vol: '320M' },
    ];
    return { bonds };
  },
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">RGBI Index</h3>
          <div class="text-3xl font-bold text-rose-400">112.45</div>
          <div class="text-xs text-rose-500 mt-1">-0.45% (Intraday)</div>
        </div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Avg Yield (10Y)</h3>
          <div class="text-3xl font-bold text-white">12.15%</div>
          <div class="text-xs text-emerald-400 mt-1">+5bps vs Prev Close</div>
        </div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Total Turnover</h3>
          <div class="text-3xl font-bold text-white">14.2B</div>
          <div class="text-xs text-gray-500 mt-1">RUB</div>
        </div>
      </div>

      <div class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0 backdrop-blur-md z-10">
              <th class="p-4 font-bold">Issue / Ticker</th>
              <th class="p-4 font-bold">Maturity</th>
              <th class="p-4 font-bold text-right">Coupon</th>
              <th class="p-4 font-bold text-right">Price</th>
              <th class="p-4 font-bold text-right">Yield</th>
              <th class="p-4 font-bold text-right">B/A Spread</th>
              <th class="p-4 font-bold text-right">Volume</th>
            </tr>
          </thead>
          <tbody class="text-sm font-mono text-gray-300">
            <tr v-for="(bond, i) in bonds" :key="i" class="border-b border-white/5 hover:bg-white/5 transition-colors group cursor-pointer">
              <td class="p-4 font-bold text-white group-hover:text-teal-400">{{ bond.id }}</td>
              <td class="p-4">{{ bond.mat }}</td>
              <td class="p-4 text-right text-gray-400">{{ bond.cpn }}</td>
              <td class="p-4 text-right font-bold text-white">{{ bond.price }}</td>
              <td class="p-4 text-right text-teal-400">{{ bond.yld }}</td>
              <td class="p-4 text-right text-gray-500">{{ bond.spread }}</td>
              <td class="p-4 text-right">{{ bond.vol }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
});

const AllQuotes = defineComponent({
  setup() {
    const quotes = [
      { ticker: 'GAZP 34', dealer: 'JPM', bidSize: '5M', bid: '92.45', ask: '92.65', askSize: '2M', time: '14:20:05' },
      { ticker: 'LUK 30', dealer: 'GSI', bidSize: '1M', bid: '88.10', ask: '88.40', askSize: '5M', time: '14:20:02' },
      { ticker: 'SBER 28', dealer: 'MS', bidSize: '10M', bid: '95.00', ask: '95.15', askSize: '10M', time: '14:19:55' },
      { ticker: 'RUAL 27', dealer: 'CITI', bidSize: '500k', bid: '84.20', ask: '84.80', askSize: '1M', time: '14:19:40' },
      { ticker: 'NOV 29', dealer: 'VTB', bidSize: '2M', bid: '90.50', ask: '90.75', askSize: '3M', time: '14:19:12' },
    ];
    return { quotes };
  },
  template: `
    <div class="flex flex-col h-full">
      <div class="flex justify-between items-center mb-6">
        <div class="flex items-center gap-3">
          <h3 class="text-lg font-bold text-white">Corporate Quotes Monitor</h3>
          <span class="text-[10px] bg-green-500/20 text-green-400 px-2 py-0.5 rounded border border-green-500/20 flex items-center gap-1">
            <span class="animate-pulse">●</span> Stream Active
          </span>
        </div>
        <div class="flex gap-2">
          <input type="text" placeholder="Filter by Ticker..." class="bg-black/30 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white outline-none focus:border-teal-500/50" />
        </div>
      </div>

      <div class="flex-1 bg-black/20 rounded-2xl border border-white/5 overflow-hidden">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="text-xs text-gray-500 uppercase bg-white/5 border-b border-white/10">
              <th class="p-4">Time</th>
              <th class="p-4">Ticker</th>
              <th class="p-4">Dealer</th>
              <th class="p-4 text-right">Bid Size</th>
              <th class="p-4 text-right text-emerald-400">Bid</th>
              <th class="p-4 text-right text-rose-400">Ask</th>
              <th class="p-4 text-right">Ask Size</th>
              <th class="p-4 text-right">Spread</th>
            </tr>
          </thead>
          <tbody class="text-sm font-mono text-gray-300">
            <tr v-for="(q, i) in quotes" :key="i" class="border-b border-white/5 hover:bg-white/5 transition-colors">
              <td class="p-4 text-gray-500 text-xs">{{ q.time }}</td>
              <td class="p-4 font-bold text-white">{{ q.ticker }}</td>
              <td class="p-4 text-teal-300">{{ q.dealer }}</td>
              <td class="p-4 text-right">{{ q.bidSize }}</td>
              <td class="p-4 text-right font-bold text-emerald-400 bg-emerald-500/5">{{ q.bid }}</td>
              <td class="p-4 text-right font-bold text-rose-400 bg-rose-500/5">{{ q.ask }}</td>
              <td class="p-4 text-right">{{ q.askSize }}</td>
              <td class="p-4 text-right text-xs text-gray-500">{{ (parseFloat(q.ask) - parseFloat(q.bid)).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
});

const BondPicks = defineComponent({
  setup() {
    const picks = [
      { issuer: 'Apple Inc', tenor: '5Y', rating: 'AA+', yield: '4.25%', spread: '+45bp', rationale: 'Strong cash flow, defensive play in tech.' },
      { issuer: 'JPMorgan Chase', tenor: '10Y', rating: 'A-', yield: '5.10%', spread: '+95bp', rationale: 'Attractive spread vs historicals.' },
      { issuer: 'Verizon Comm', tenor: '30Y', rating: 'BBB+', yield: '5.85%', spread: '+140bp', rationale: 'Yield pickup for long duration exposure.' },
      { issuer: 'Ford Motor', tenor: '3Y', rating: 'BB+', yield: '6.50%', spread: '+210bp', rationale: 'Improving credit metrics, upgrade candidate.' },
    ];
    return { picks };
  },
  template: `
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="(pick, i) in picks" :key="i" class="p-6 rounded-2xl bg-white/5 border border-white/5 hover:border-teal-500/30 transition-colors group cursor-pointer relative overflow-hidden">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h4 class="text-lg font-bold text-white">{{ pick.issuer }}</h4>
            <div class="flex gap-2 mt-1">
              <span class="text-xs bg-white/10 px-2 py-0.5 rounded text-gray-300">{{ pick.tenor }}</span>
              <span :class="['text-xs px-2 py-0.5 rounded font-bold', pick.rating.startsWith('A') ? 'bg-emerald-500/20 text-emerald-400' : 'bg-yellow-500/20 text-yellow-400']">
                {{ pick.rating }}
              </span>
            </div>
          </div>
          <div class="text-right">
            <div class="text-2xl font-bold text-teal-400">{{ pick.yield }}</div>
            <div class="text-xs text-gray-500 uppercase">Yield</div>
          </div>
        </div>
        
        <div class="mb-4">
          <span class="text-xs text-gray-500 uppercase font-bold">OAS Spread</span>
          <div class="text-sm font-mono text-white">{{ pick.spread }}</div>
        </div>

        <div class="pt-4 border-t border-white/10">
          <p class="text-xs text-gray-400 italic">"{{ pick.rationale }}"</p>
        </div>
      </div>
    </div>
  `
});

const SovereignBonds = defineComponent({
  setup() {
    const data = [
      { country: 'US', yield: 4.25, spread: 185 },
      { country: 'UK', yield: 4.10, spread: 170 },
      { country: 'France', yield: 2.90, spread: 50 },
      { country: 'Italy', yield: 3.85, spread: 145 },
      { country: 'Spain', yield: 3.25, spread: 85 },
      { country: 'Japan', yield: 0.85, spread: -155 },
      { country: 'Brazil', yield: 10.50, spread: 810 },
    ];
    return { data };
  },
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-black/20 rounded-2xl border border-white/5 p-6 flex flex-col">
          <h3 class="text-lg font-bold text-white mb-6">10Y Yield Comparison</h3>
          <div class="flex-1 min-h-[250px] flex items-center justify-center text-gray-500">
            [Chart: Yield Comparison]
          </div>
        </div>

        <div class="bg-white/5 rounded-2xl border border-white/5 p-6">
          <h3 class="text-lg font-bold text-white mb-6">Spread vs Bunds (DE)</h3>
          <div class="overflow-auto custom-scrollbar max-h-[300px]">
            <table class="w-full text-left">
              <thead>
                <tr class="text-xs text-gray-500 uppercase border-b border-white/10">
                  <th class="pb-3">Country</th>
                  <th class="pb-3 text-right">Yield</th>
                  <th class="pb-3 text-right">Spread (bps)</th>
                  <th class="pb-3 text-right">1D Chg</th>
                </tr>
              </thead>
              <tbody class="text-sm font-mono">
                <tr v-for="(row, i) in data" :key="i" class="border-b border-white/5 hover:bg-white/5">
                  <td class="py-3 font-bold text-white">{{ row.country }}</td>
                  <td class="py-3 text-right text-gray-300">{{ row.yield.toFixed(2) }}%</td>
                  <td :class="['py-3 text-right font-bold', row.spread > 100 ? 'text-rose-400' : 'text-teal-400']">
                    {{ row.spread > 0 ? '+' : '' }}{{ row.spread }}
                  </td>
                  <td class="py-3 text-right text-gray-500">
                    {{ (Math.random() * 5 - 2.5).toFixed(1) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  `
});

const NewIssueMonitor = defineComponent({
  setup() {
    const deals = [
      { date: '26 Oct', issuer: 'Coca-Cola Co', rating: 'A+', tenor: '10Y', size: '$1.5B', ipt: 'T+85bp', status: 'Announced' },
      { date: '26 Oct', issuer: 'Pfizer Inc', rating: 'A', tenor: '30Y', size: '$2.0B', ipt: 'T+110bp', status: 'Book Building' },
      { date: '27 Oct', issuer: 'Oracle Corp', rating: 'BBB+', tenor: '5Y', size: '$1.0B', ipt: 'T+95bp', status: 'Rumored' },
      { date: '28 Oct', issuer: 'Kingdom of Saudi Arabia', rating: 'A', tenor: '12Y', size: '$5.0B', ipt: 'T+145bp', status: 'Roadshow' },
    ];
    return { deals };
  },
  template: `
    <div class="flex flex-col h-full">
      <div class="flex gap-4 mb-6">
        <div class="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex-1">
          <div class="text-xs text-indigo-400 uppercase font-bold mb-1">Expected Weekly Volume</div>
          <div class="text-2xl font-bold text-white">$24.5B</div>
        </div>
        <div class="p-4 rounded-xl bg-teal-500/10 border border-teal-500/20 flex-1">
          <div class="text-xs text-teal-400 uppercase font-bold mb-1">Active Deals</div>
          <div class="text-2xl font-bold text-white">12</div>
        </div>
        <div class="p-4 rounded-xl bg-orange-500/10 border border-orange-500/20 flex-1">
          <div class="text-xs text-orange-400 uppercase font-bold mb-1">Avg Oversubscription</div>
          <div class="text-2xl font-bold text-white">3.2x</div>
        </div>
      </div>

      <div class="flex-1 bg-white/5 rounded-2xl border border-white/5 overflow-hidden">
        <div class="p-4 border-b border-white/10 bg-black/20">
          <h3 class="font-bold text-white">Deal Calendar</h3>
        </div>
        <div class="overflow-auto">
          <table class="w-full text-left">
            <thead>
              <tr class="text-xs text-gray-500 uppercase bg-black/10">
                <th class="p-4">Date</th>
                <th class="p-4">Issuer</th>
                <th class="p-4">Rating</th>
                <th class="p-4">Tenor</th>
                <th class="p-4">Size</th>
                <th class="p-4">IPT (Price Talk)</th>
                <th class="p-4 text-right">Status</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="(deal, i) in deals" :key="i" class="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td class="p-4 text-gray-500">{{ deal.date }}</td>
                <td class="p-4 font-bold text-white">{{ deal.issuer }}</td>
                <td class="p-4">
                  <span :class="['px-2 py-0.5 rounded text-xs border', deal.rating.startsWith('A') ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400']">
                    {{ deal.rating }}
                  </span>
                </td>
                <td class="p-4">{{ deal.tenor }}</td>
                <td class="p-4">{{ deal.size }}</td>
                <td class="p-4 text-teal-300">{{ deal.ipt }}</td>
                <td class="p-4 text-right">
                  <span class="text-xs font-bold text-gray-400 uppercase">{{ deal.status }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `
});
</script>
