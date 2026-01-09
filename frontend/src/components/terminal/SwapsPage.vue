<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full">
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-600/20 to-cyan-600/20 flex items-center justify-center text-lg font-bold text-indigo-400 border border-indigo-500/30">
          <ArrowLeftRightIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">Swaps Analysis</h2>
          <p class="text-xs text-gray-400">Pricing, Valuation & Curve Monitoring</p>
        </div>
      </div>
      <div class="flex bg-black/40 rounded-xl p-1 border border-white/5 overflow-x-auto max-w-full custom-scrollbar">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="section = tab.id"
          :class="['px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 whitespace-nowrap', section === tab.id ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' : 'text-gray-500 hover:text-white hover:bg-white/5']"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <SwapPricingModel v-if="section === 'SWPM'" />
      <InterestRateBasics v-else-if="section === 'IRSB'" />
      <SwapMonitor v-else-if="section === 'IRSM'" />
      <AssetSwap v-else-if="section === 'ASW'" />
      <SwapPricingModel v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineComponent, h } from 'vue';

const ArrowLeftRightIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('polyline', { points: '18 8 22 12 18 16' }), h('polyline', { points: '6 8 2 12 6 16' }), h('line', { x1: '2', y1: '12', x2: '22', y2: '12' })]) });

const props = defineProps<{ symbol?: string; activeSection?: string; }>();
const section = ref(props.activeSection || 'SWPM');
watch(() => props.activeSection, (v) => { if (v) section.value = v; });

const tabs = [
  { id: 'SWPM', label: 'Pricing Model' },
  { id: 'IRSB', label: 'Rate Basics' },
  { id: 'IRSM', label: 'Swap Monitor' },
  { id: 'ASW', label: 'Asset Swap' },
];

const SwapPricingModel = defineComponent({
  setup() {
    const notional = ref(10);
    const fixedRate = ref(4.25);
    const tenor = ref(5);
    return { notional, fixedRate, tenor };
  },
  template: `
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 h-full">
      <div class="space-y-6">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-4">Deal Parameters</h3>
          <div class="space-y-4">
            <div><label class="text-xs text-gray-500 block mb-1">Notional ($M)</label><input type="number" v-model="notional" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
            <div><label class="text-xs text-gray-500 block mb-1">Fixed Rate (%)</label><input type="number" v-model="fixedRate" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
            <div><label class="text-xs text-gray-500 block mb-1">Tenor (Years)</label><input type="range" min="1" max="30" v-model="tenor" class="w-full" /><div class="text-right text-xs text-indigo-400">{{ tenor }} Years</div></div>
          </div>
          <button class="w-full mt-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold">Calculate NPV</button>
        </div>
        <div class="p-6 rounded-2xl bg-black/20 border border-white/5 text-center">
          <h3 class="text-xs font-bold text-gray-500 uppercase mb-2">Net Present Value</h3>
          <div class="text-3xl font-bold font-mono text-emerald-400">+$145,230</div>
        </div>
      </div>
      <div class="lg:col-span-2 p-6 rounded-2xl bg-white/5 border border-white/5 flex items-center justify-center text-gray-500">
        [Cash Flow Chart]
      </div>
    </div>
  `
});

const InterestRateBasics = defineComponent({
  setup() {
    const rates = [
      { ccy: 'USD', t2y: '4.15%', t5y: '3.95%', t10y: '3.85%', t30y: '4.05%', trend: 'down' },
      { ccy: 'EUR', t2y: '2.85%', t5y: '2.60%', t10y: '2.65%', t30y: '2.75%', trend: 'flat' },
      { ccy: 'GBP', t2y: '4.45%', t5y: '4.10%', t10y: '4.00%', t30y: '4.15%', trend: 'down' },
      { ccy: 'JPY', t2y: '0.45%', t5y: '0.65%', t10y: '0.95%', t30y: '1.85%', trend: 'up' },
    ];
    return { rates };
  },
  template: `
    <div class="flex flex-col h-full">
      <h3 class="text-lg font-bold text-white mb-6">Major Currency Swap Rates</h3>
      <div class="flex-1 bg-black/20 rounded-2xl border border-white/5 overflow-hidden">
        <table class="w-full text-left border-collapse">
          <thead><tr class="text-xs text-gray-500 uppercase bg-white/5"><th class="p-4">Currency</th><th class="p-4 text-center">Trend</th><th class="p-4 text-right">2Y</th><th class="p-4 text-right">5Y</th><th class="p-4 text-right">10Y</th><th class="p-4 text-right">30Y</th></tr></thead>
          <tbody class="text-sm font-mono text-gray-300">
            <tr v-for="r in rates" :key="r.ccy" class="border-b border-white/5 hover:bg-white/5">
              <td class="p-4 font-bold text-white">{{ r.ccy }}</td>
              <td class="p-4 text-center">{{ r.trend === 'down' ? '▼' : r.trend === 'up' ? '▲' : '−' }}</td>
              <td class="p-4 text-right">{{ r.t2y }}</td>
              <td class="p-4 text-right">{{ r.t5y }}</td>
              <td class="p-4 text-right font-bold text-white">{{ r.t10y }}</td>
              <td class="p-4 text-right">{{ r.t30y }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
});

const SwapMonitor = defineComponent({
  template: `
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
      <div class="bg-black/20 rounded-2xl border border-white/5 p-6 flex items-center justify-center text-gray-500">
        [USD Swap Curve Chart]
      </div>
      <div class="flex flex-col gap-6">
        <div class="bg-white/5 rounded-2xl border border-white/5 p-6">
          <h3 class="text-lg font-bold text-white mb-4">Key Forward Rates</h3>
          <table class="w-full text-left"><tbody class="text-sm font-mono text-gray-300">
            <tr class="border-b border-white/5"><td class="py-2 font-bold text-white">1Y1Y</td><td class="text-right">3.85%</td><td class="text-right text-emerald-400">-10bp</td></tr>
            <tr class="border-b border-white/5"><td class="py-2 font-bold text-white">5Y5Y</td><td class="text-right">4.10%</td><td class="text-right text-rose-400">+5bp</td></tr>
          </tbody></table>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="p-4 rounded-xl bg-white/5 border border-white/5 text-center"><div class="text-xs text-gray-500 uppercase mb-1">Swap Spread (10Y)</div><div class="text-2xl font-bold text-white">-15.5</div></div>
          <div class="p-4 rounded-xl bg-white/5 border border-white/5 text-center"><div class="text-xs text-gray-500 uppercase mb-1">Fly (2s5s10s)</div><div class="text-2xl font-bold text-indigo-400">-22.0</div></div>
        </div>
      </div>
    </div>
  `
});

const AssetSwap = defineComponent({
  template: `
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 h-full items-center">
      <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
        <h3 class="text-lg font-bold text-white mb-6">Asset Details</h3>
        <div class="space-y-4">
          <div><label class="text-xs text-gray-500 block mb-1">Bond Price</label><input type="text" value="98.50" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="text-xs text-gray-500 block mb-1">Coupon</label><input type="text" value="4.00%" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
            <div><label class="text-xs text-gray-500 block mb-1">Maturity</label><input type="text" value="15 Nov 2030" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
          </div>
        </div>
        <button class="w-full mt-6 py-3 bg-teal-600 hover:bg-teal-500 text-white rounded-xl font-bold">Calculate Spread</button>
      </div>
      <div class="p-8 rounded-2xl bg-gradient-to-br from-teal-900/20 to-black border border-teal-500/30 text-center">
        <h3 class="text-sm font-bold text-teal-500 uppercase mb-2">Asset Swap Spread</h3>
        <div class="text-6xl font-bold text-white mb-2">32.5 <span class="text-2xl text-gray-500">bps</span></div>
        <p class="text-xs text-gray-400">Spread over SOFR flat</p>
      </div>
    </div>
  `
});
</script>
