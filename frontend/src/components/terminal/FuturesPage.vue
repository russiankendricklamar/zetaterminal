<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full">
    <!-- Header -->
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-600/20 to-blue-600/20 flex items-center justify-center text-lg font-bold text-cyan-400 border border-cyan-500/30">
          <GitCommitIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">Futures Market</h2>
          <p class="text-xs text-gray-400">Contracts, Spreads & Forward Curves</p>
        </div>
      </div>

      <div class="flex bg-black/40 rounded-xl p-1 border border-white/5 overflow-x-auto max-w-full custom-scrollbar">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="section = tab.id"
          :class="[
            'px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 whitespace-nowrap',
            section === tab.id || (section === 'CURV' && tab.id === 'FWCV')
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' 
              : 'text-gray-500 hover:text-white hover:bg-white/5'
          ]"
        >
          <component :is="tab.icon" class="w-3.5 h-3.5" /> {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <FuturesContracts v-if="section === 'FUT'" :symbol="symbol" />
      <ForwardCurves v-else-if="section === 'FWCV' || section === 'CURV'" :symbol="symbol" />
      <FuturesContracts v-else :symbol="symbol" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineComponent, h } from 'vue';

const GitCommitIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('circle', { cx: '12', cy: '12', r: '4' }), h('line', { x1: '1.05', y1: '12', x2: '7', y2: '12' }), h('line', { x1: '17.01', y1: '12', x2: '22.96', y2: '12' })]) });
const LayersIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('polygon', { points: '12 2 2 7 12 12 22 7 12 2' }), h('polyline', { points: '2 17 12 22 22 17' }), h('polyline', { points: '2 12 12 17 22 12' })]) });
const TrendingUpIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('polyline', { points: '23 6 13.5 15.5 8.5 10.5 1 18' }), h('polyline', { points: '17 6 23 6 23 12' })]) });

const props = defineProps<{
  symbol?: string;
  activeSection?: string;
}>();

const section = ref(props.activeSection || 'FUT');
const symbol = ref(props.symbol || 'ES');

watch(() => props.activeSection, (newVal) => {
  if (newVal) section.value = newVal;
});

const tabs = [
  { id: 'FUT', label: 'Futures Contracts', icon: LayersIcon },
  { id: 'FWCV', label: 'Forward Curves', icon: TrendingUpIcon },
];

const FuturesContracts = defineComponent({
  props: ['symbol'],
  setup() {
    const contracts = [
      { code: 'ESZ5', name: 'E-mini S&P 500 Dec 25', last: 5845.50, change: '+1.25%', vol: '1.2M', oi: '2.4M', roll: '12 Days' },
      { code: 'NQZ5', name: 'E-mini Nasdaq Dec 25', last: 20150.25, change: '+1.80%', vol: '850K', oi: '950K', roll: '12 Days' },
      { code: 'CLX5', name: 'Crude Oil Nov 25', last: 74.25, change: '-0.45%', vol: '450K', oi: '620K', roll: '4 Days' },
      { code: 'GCZ5', name: 'Gold Dec 25', last: 2685.10, change: '+0.15%', vol: '220K', oi: '410K', roll: '25 Days' },
      { code: 'BTCX5', name: 'Bitcoin Nov 25', last: 64550.00, change: '+2.10%', vol: '15K', oi: '45K', roll: '18 Days' },
      { code: 'ZB Z5', name: 'US Treasury Bond Dec 25', last: 118.15, change: '-0.10%', vol: '380K', oi: '750K', roll: '20 Days' },
    ];
    return { contracts };
  },
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Total Open Interest</h3>
          <div class="text-3xl font-bold text-cyan-400">$2.4T</div>
          <div class="text-xs text-cyan-500 mt-1">+1.5% (DoD)</div>
        </div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Roll Activity</h3>
          <div class="text-3xl font-bold text-white">High</div>
          <div class="text-xs text-gray-500 mt-1">Approaching Expiry (Equity)</div>
        </div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Basis (Spot-Fut)</h3>
          <div class="text-3xl font-bold text-white">+12.5</div>
          <div class="text-xs text-gray-500 mt-1">Contango</div>
        </div>
      </div>

      <div class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0 backdrop-blur-md z-10">
              <th class="p-4 font-bold">Code</th>
              <th class="p-4 font-bold">Contract Name</th>
              <th class="p-4 font-bold text-right">Last Price</th>
              <th class="p-4 font-bold text-right">Change</th>
              <th class="p-4 font-bold text-right">Volume</th>
              <th class="p-4 font-bold text-right">Open Int.</th>
              <th class="p-4 font-bold text-right">Days to Roll</th>
            </tr>
          </thead>
          <tbody class="text-sm font-mono text-gray-300">
            <tr v-for="(cont, i) in contracts" :key="i" class="border-b border-white/5 hover:bg-white/5 transition-colors group cursor-pointer">
              <td class="p-4 font-bold text-white group-hover:text-cyan-400">{{ cont.code }}</td>
              <td class="p-4 text-xs font-sans text-gray-400">{{ cont.name }}</td>
              <td class="p-4 text-right font-bold text-white">{{ cont.last.toLocaleString() }}</td>
              <td :class="['p-4 text-right font-bold', cont.change.startsWith('+') ? 'text-emerald-400' : 'text-rose-400']">
                {{ cont.change }}
              </td>
              <td class="p-4 text-right">{{ cont.vol }}</td>
              <td class="p-4 text-right">{{ cont.oi }}</td>
              <td class="p-4 text-right">
                <span :class="['px-2 py-1 rounded text-xs border', parseInt(cont.roll) < 5 ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' : 'bg-gray-700/30 border-gray-600/30 text-gray-400']">
                  {{ cont.roll }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
});

const ForwardCurves = defineComponent({
  props: ['symbol'],
  setup() {
    const asset = ref('Crude Oil (WTI)');
    const assets = ['Crude Oil (WTI)', 'Natural Gas', 'Corn', 'Gold', 'VIX'];
    const data = [
      { term: 'M1', current: 74.25, prev: 73.10 },
      { term: 'M2', current: 73.80, prev: 72.90 },
      { term: 'M3', current: 73.45, prev: 72.80 },
      { term: 'M6', current: 72.50, prev: 72.20 },
      { term: 'M12', current: 70.10, prev: 70.50 },
      { term: 'M18', current: 68.50, prev: 69.20 },
      { term: 'M24', current: 66.80, prev: 68.10 },
    ];
    return { asset, assets, data };
  },
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-4">
          <h3 class="text-lg font-bold text-white">Term Structure</h3>
          <div class="flex bg-black/30 rounded-lg p-1 border border-white/10">
            <button 
              v-for="a in assets" 
              :key="a"
              @click="asset = a"
              :class="['px-3 py-1 rounded-md text-xs font-bold transition-all', asset === a ? 'bg-cyan-600 text-white shadow-lg' : 'text-gray-400 hover:text-white']"
            >
              {{ a }}
            </button>
          </div>
        </div>
        <div class="flex gap-4 text-xs font-bold">
          <span class="flex items-center gap-2"><div class="w-3 h-1 bg-cyan-400"></div> Current Curve</span>
          <span class="flex items-center gap-2"><div class="w-3 h-1 bg-gray-500"></div> 1 Month Ago</span>
        </div>
      </div>

      <div class="flex-1 bg-black/20 rounded-2xl border border-white/5 p-6 flex flex-col items-center justify-center text-gray-500">
        [Forward Curve Chart]
      </div>

      <div class="grid grid-cols-3 gap-6">
        <div class="p-4 rounded-xl bg-white/5 border border-white/5 text-center">
          <div class="text-xs text-gray-500 uppercase font-bold mb-1">Structure</div>
          <div class="text-xl font-bold text-white">Backwardation</div>
          <div class="text-[10px] text-gray-400">Bullish Indicator</div>
        </div>
        <div class="p-4 rounded-xl bg-white/5 border border-white/5 text-center">
          <div class="text-xs text-gray-500 uppercase font-bold mb-1">M1-M12 Spread</div>
          <div class="text-xl font-bold text-cyan-400">+$4.15</div>
          <div class="text-[10px] text-gray-400">Roll Yield Positive</div>
        </div>
        <div class="p-4 rounded-xl bg-white/5 border border-white/5 text-center">
          <div class="text-xs text-gray-500 uppercase font-bold mb-1">Inventory Levels</div>
          <div class="text-xl font-bold text-white">-2.5M Bbls</div>
          <div class="text-[10px] text-gray-400">Below Avg</div>
        </div>
      </div>
    </div>
  `
});
</script>
