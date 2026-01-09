<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full">
    <!-- Header -->
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-fuchsia-600/20 to-purple-600/20 flex items-center justify-center text-lg font-bold text-fuchsia-400 border border-fuchsia-500/30">
          <SigmaIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">Options Analytics</h2>
          <p class="text-xs text-gray-400">Derivatives Pricing & Volatility Analysis</p>
        </div>
      </div>

      <div class="flex bg-black/40 rounded-xl p-1 border border-white/5 overflow-x-auto max-w-full custom-scrollbar">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="section = tab.id"
          :class="[
            'px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 whitespace-nowrap',
            section === tab.id 
              ? 'bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-500/30' 
              : 'text-gray-500 hover:text-white hover:bg-white/5'
          ]"
        >
          <component :is="tab.icon" class="w-3.5 h-3.5" /> {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <OptionAnalytics v-if="section === 'OVML'" :symbol="symbol" />
      <VolatilitySurface v-else-if="section === 'VOL'" :symbol="symbol" />
      <OptionScreening v-else-if="section === 'OCRN'" :symbol="symbol" />
      <ImpliedVsRealized v-else-if="section === 'VARL'" :symbol="symbol" />
      <OptionAnalytics v-else :symbol="symbol" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineComponent, h } from 'vue';

const SigmaIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('path', { d: 'M18 7V4H6l6 8-6 8h12v-3' })]) });
const CalculatorIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('rect', { x: '4', y: '2', width: '16', height: '20', rx: '2' }), h('line', { x1: '8', y1: '6', x2: '16', y2: '6' }), h('line', { x1: '8', y1: '10', x2: '8', y2: '10' }), h('line', { x1: '12', y1: '10', x2: '12', y2: '10' }), h('line', { x1: '16', y1: '10', x2: '16', y2: '10' }), h('line', { x1: '8', y1: '14', x2: '8', y2: '14' }), h('line', { x1: '12', y1: '14', x2: '12', y2: '14' }), h('line', { x1: '16', y1: '14', x2: '16', y2: '14' }), h('line', { x1: '8', y1: '18', x2: '8', y2: '18' }), h('line', { x1: '12', y1: '18', x2: '16', y2: '18' })]) });
const ActivityIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('polyline', { points: '22 12 18 12 15 21 9 3 6 12 2 12' })]) });
const FilterIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('polygon', { points: '22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3' })]) });
const TrendingUpIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('polyline', { points: '23 6 13.5 15.5 8.5 10.5 1 18' }), h('polyline', { points: '17 6 23 6 23 12' })]) });

const props = defineProps<{
  symbol?: string;
  activeSection?: string;
}>();

const section = ref(props.activeSection || 'OVML');
const symbol = ref(props.symbol || 'NVDA');

watch(() => props.activeSection, (newVal) => {
  if (newVal) section.value = newVal;
});

const tabs = [
  { id: 'OVML', label: 'Option Analytics', icon: CalculatorIcon },
  { id: 'VOL', label: 'Volatility Surface', icon: ActivityIcon },
  { id: 'OCRN', label: 'Option Screening', icon: FilterIcon },
  { id: 'VARL', label: 'Imp. vs Realized', icon: TrendingUpIcon },
];

const OptionAnalytics = defineComponent({
  props: ['symbol'],
  setup() {
    const strike = ref(150);
    const vol = ref(35);
    const days = ref(30);
    const greeks = [
      { name: 'Delta', val: '0.45', desc: 'Price Sensitivity', color: 'text-blue-400' },
      { name: 'Gamma', val: '0.04', desc: 'Rate of Change', color: 'text-purple-400' },
      { name: 'Vega', val: '0.12', desc: 'Vol Sensitivity', color: 'text-orange-400' },
      { name: 'Theta', val: '-0.08', desc: 'Time Decay', color: 'text-rose-400' },
      { name: 'Rho', val: '0.02', desc: 'Rate Sensitivity', color: 'text-gray-300' },
    ];
    return { strike, vol, days, greeks };
  },
  template: `
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 h-full">
      <div class="lg:col-span-1 space-y-6">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-lg font-bold text-white mb-6">Pricing Inputs</h3>
          <div class="space-y-4">
            <div>
              <div class="flex justify-between mb-2">
                <label class="text-xs text-gray-400 font-bold uppercase">Underlying Price</label>
                <span class="text-xs font-mono text-white">$145.32</span>
              </div>
              <div class="h-10 bg-black/40 rounded-lg border border-white/10 flex items-center px-3 text-gray-500 text-sm cursor-not-allowed">
                145.32
              </div>
            </div>
            <div>
              <div class="flex justify-between mb-2">
                <label class="text-xs text-gray-400 font-bold uppercase">Strike Price</label>
                <span class="text-xs font-mono text-fuchsia-400">\${{ strike }}</span>
              </div>
              <input type="range" min="100" max="200" step="5" v-model="strike" class="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-fuchsia-500" />
            </div>
            <div>
              <div class="flex justify-between mb-2">
                <label class="text-xs text-gray-400 font-bold uppercase">Implied Volatility</label>
                <span class="text-xs font-mono text-fuchsia-400">{{ vol }}%</span>
              </div>
              <input type="range" min="10" max="150" step="1" v-model="vol" class="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-fuchsia-500" />
            </div>
            <div>
              <div class="flex justify-between mb-2">
                <label class="text-xs text-gray-400 font-bold uppercase">Days to Expiry</label>
                <span class="text-xs font-mono text-fuchsia-400">{{ days }} Days</span>
              </div>
              <input type="range" min="1" max="365" step="1" v-model="days" class="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-fuchsia-500" />
            </div>
          </div>
        </div>

        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <div class="grid grid-cols-2 gap-4">
            <div class="text-center p-3 rounded-xl bg-black/20">
              <div class="text-xs text-gray-500 uppercase mb-1">Call Price</div>
              <div class="text-xl font-bold text-emerald-400 font-mono">$4.25</div>
            </div>
            <div class="text-center p-3 rounded-xl bg-black/20">
              <div class="text-xs text-gray-500 uppercase mb-1">Put Price</div>
              <div class="text-xl font-bold text-rose-400 font-mono">$8.40</div>
            </div>
          </div>
        </div>
      </div>

      <div class="lg:col-span-2 flex flex-col gap-6">
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div v-for="greek in greeks" :key="greek.name" class="p-4 rounded-xl bg-white/5 border border-white/5 flex flex-col items-center justify-center text-center hover:bg-white/10 transition-colors">
            <span class="text-xs text-gray-500 font-bold uppercase mb-2">{{ greek.name }}</span>
            <span :class="['text-2xl font-mono font-bold mb-1', greek.color]">{{ greek.val }}</span>
            <span class="text-[10px] text-gray-600">{{ greek.desc }}</span>
          </div>
        </div>

        <div class="flex-1 p-6 rounded-2xl bg-black/20 border border-white/5 flex items-center justify-center text-gray-500">
          [P/L Chart]
        </div>
      </div>
    </div>
  `
});

const VolatilitySurface = defineComponent({
  props: ['symbol'],
  template: `
    <div class="flex flex-col h-full">
      <div class="flex justify-between items-center mb-6">
        <h3 class="text-lg font-bold text-white">Volatility Skew (Smile)</h3>
        <div class="flex gap-4 text-xs font-bold">
          <span class="flex items-center gap-2"><div class="w-3 h-1 bg-fuchsia-500"></div> 30 Days</span>
          <span class="flex items-center gap-2"><div class="w-3 h-1 bg-blue-500"></div> 90 Days</span>
          <span class="flex items-center gap-2"><div class="w-3 h-1 bg-emerald-500"></div> 180 Days</span>
        </div>
      </div>

      <div class="flex-1 bg-black/20 rounded-2xl border border-white/5 p-6 flex items-center justify-center text-gray-500">
        [Volatility Surface Chart]
      </div>

      <div class="grid grid-cols-3 gap-6 mt-6">
        <div class="p-4 rounded-xl bg-white/5 border border-white/5 text-center">
          <div class="text-xs text-gray-500 uppercase font-bold mb-1">Put-Call Skew</div>
          <div class="text-xl font-bold text-rose-400">4.5%</div>
          <div class="text-[10px] text-gray-400">Puts Expensive</div>
        </div>
        <div class="p-4 rounded-xl bg-white/5 border border-white/5 text-center">
          <div class="text-xs text-gray-500 uppercase font-bold mb-1">Term Structure</div>
          <div class="text-xl font-bold text-white">Contango</div>
          <div class="text-[10px] text-gray-400">Normal</div>
        </div>
        <div class="p-4 rounded-xl bg-white/5 border border-white/5 text-center">
          <div class="text-xs text-gray-500 uppercase font-bold mb-1">ATM Vol</div>
          <div class="text-xl font-bold text-fuchsia-400">32.5%</div>
          <div class="text-[10px] text-gray-400">Elevated</div>
        </div>
      </div>
    </div>
  `
});

const OptionScreening = defineComponent({
  props: ['symbol'],
  setup(props) {
    const rows = [
      { s: props.symbol, exp: '24 Oct', str: 150, t: 'CALL', b: 2.10, a: 2.15, iv: '32%', d: 0.45, v: 1.2 },
      { s: props.symbol, exp: '24 Oct', str: 140, t: 'PUT', b: 1.85, a: 1.90, iv: '34%', d: -0.30, v: 0.8 },
      { s: props.symbol, exp: '21 Nov', str: 160, t: 'CALL', b: 3.40, a: 3.50, iv: '31%', d: 0.35, v: 2.1 },
      { s: props.symbol, exp: '21 Nov', str: 130, t: 'PUT', b: 2.20, a: 2.30, iv: '36%', d: -0.25, v: 0.5 },
      { s: props.symbol, exp: '19 Dec', str: 150, t: 'CALL', b: 5.60, a: 5.80, iv: '30%', d: 0.52, v: 1.5 },
    ];
    return { rows };
  },
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="p-4 rounded-2xl bg-white/5 border border-white/5 flex flex-wrap gap-4 items-center">
        <select class="bg-black/20 text-xs text-white border border-white/10 rounded-lg px-3 py-2 outline-none">
          <option>High IV Percentile (>90)</option>
          <option>Cheap Delta (<20)</option>
          <option>Earnings Plays</option>
        </select>
        <select class="bg-black/20 text-xs text-white border border-white/10 rounded-lg px-3 py-2 outline-none">
          <option>Exp: Next Week</option>
          <option>Exp: Next Month</option>
          <option>Exp: LEAPS</option>
        </select>
        <div class="ml-auto">
          <button class="px-4 py-2 bg-fuchsia-600 hover:bg-fuchsia-500 text-white text-xs font-bold rounded-lg transition-colors shadow-lg shadow-fuchsia-500/20">
            Scan Market
          </button>
        </div>
      </div>

      <div class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0 backdrop-blur-md z-10">
              <th class="p-4 font-bold">Symbol</th>
              <th class="p-4 font-bold">Expiry</th>
              <th class="p-4 font-bold">Strike</th>
              <th class="p-4 font-bold">Type</th>
              <th class="p-4 font-bold text-right">Bid</th>
              <th class="p-4 font-bold text-right">Ask</th>
              <th class="p-4 font-bold text-right">IV</th>
              <th class="p-4 font-bold text-right">Delta</th>
              <th class="p-4 font-bold text-right">Vol/OI</th>
            </tr>
          </thead>
          <tbody class="text-sm font-mono text-gray-300">
            <tr v-for="(row, i) in rows" :key="i" class="border-b border-white/5 hover:bg-white/5 transition-colors group cursor-pointer">
              <td class="p-4 font-bold text-white">{{ row.s }}</td>
              <td class="p-4 text-gray-400">{{ row.exp }}</td>
              <td class="p-4 text-white">{{ row.str }}</td>
              <td :class="['p-4 font-bold', row.t === 'CALL' ? 'text-emerald-400' : 'text-rose-400']">{{ row.t }}</td>
              <td class="p-4 text-right text-emerald-400/80">{{ row.b.toFixed(2) }}</td>
              <td class="p-4 text-right text-rose-400/80">{{ row.a.toFixed(2) }}</td>
              <td class="p-4 text-right text-fuchsia-400">{{ row.iv }}</td>
              <td class="p-4 text-right">{{ row.d }}</td>
              <td class="p-4 text-right">{{ row.v }}x</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
});

const ImpliedVsRealized = defineComponent({
  props: ['symbol'],
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">IV Rank (1Y)</h3>
          <div class="text-3xl font-bold text-fuchsia-400">72%</div>
          <div class="text-xs text-gray-500 mt-1">High Volatility Regime</div>
        </div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Volatility Risk Premium</h3>
          <div class="text-3xl font-bold text-emerald-400">+4.2%</div>
          <div class="text-xs text-gray-500 mt-1">IV Overpricing RV</div>
        </div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Parkinson Volatility</h3>
          <div class="text-3xl font-bold text-white">28.5%</div>
          <div class="text-xs text-gray-500 mt-1">High-Low Range Based</div>
        </div>
      </div>

      <div class="flex-1 bg-black/20 rounded-2xl border border-white/5 p-6 flex items-center justify-center text-gray-500">
        [IV vs RV Chart]
      </div>
    </div>
  `
});
</script>
