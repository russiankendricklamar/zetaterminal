<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full">
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-600/20 to-orange-600/20 flex items-center justify-center text-lg font-bold text-amber-400 border border-amber-500/30">
          <ActivityIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">Fixed Income Analysis</h2>
          <p class="text-xs text-gray-400">Advanced Yield Analytics & Pricing Models</p>
        </div>
      </div>
      <div class="flex bg-black/40 rounded-xl p-1 border border-white/5 overflow-x-auto max-w-full custom-scrollbar">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap', section === tab.id ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'text-gray-500 hover:text-white hover:bg-white/5']">
          {{ tab.label }}
        </button>
      </div>
    </div>
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <YieldAndSpread v-if="section === 'YAS'" />
      <YieldCurve v-else-if="section === 'YCRV'" />
      <YieldAnalysis v-else-if="section === 'YA'" />
      <OASCalculator v-else-if="section === 'OAS1'" />
      <BondPricing v-else-if="section === 'BB'" />
      <YieldAndSpread v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineComponent, h } from 'vue';

const ActivityIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('polyline', { points: '22 12 18 12 15 21 9 3 6 12 2 12' })]) });

const props = defineProps<{ activeSection?: string; }>();
const section = ref(props.activeSection || 'YAS');
watch(() => props.activeSection, (v) => { if (v) section.value = v; });

const tabs = [
  { id: 'YAS', label: 'Yield & Spread' },
  { id: 'YCRV', label: 'Yield Curve' },
  { id: 'YA', label: 'Yield Analysis' },
  { id: 'OAS1', label: 'OAS Calc' },
  { id: 'BB', label: 'Bond Pricing' },
];

const YieldAndSpread = defineComponent({
  setup() {
    const price = ref(98.50);
    const yieldVal = ref(4.25);
    return { price, yieldVal };
  },
  template: `
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
      <div class="p-6 rounded-2xl bg-white/5 border border-white/5 flex flex-col gap-6">
        <div class="flex justify-between items-center"><h3 class="text-lg font-bold text-white">YAS Calculator</h3><span class="text-xs text-amber-400 font-mono">US Govt 10Y</span></div>
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2"><label class="text-xs text-gray-400 uppercase font-bold">Price ($)</label><input type="number" v-model="price" class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white font-mono focus:border-amber-500/50 outline-none" /></div>
          <div class="space-y-2"><label class="text-xs text-gray-400 uppercase font-bold">Yield (%)</label><input type="number" v-model="yieldVal" class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white font-mono focus:border-amber-500/50 outline-none" /></div>
        </div>
        <div class="p-4 rounded-xl bg-black/20 border border-white/5 space-y-3">
          <div class="flex justify-between text-sm"><span class="text-gray-400">G-Spread</span><span class="font-mono text-white">12.5 bps</span></div>
          <div class="flex justify-between text-sm"><span class="text-gray-400">I-Spread</span><span class="font-mono text-white">15.2 bps</span></div>
          <div class="flex justify-between text-sm"><span class="text-gray-400">Z-Spread</span><span class="font-mono text-white">14.8 bps</span></div>
          <div class="flex justify-between text-sm border-t border-white/5 pt-2"><span class="text-gray-400">Asset Swap Spread</span><span class="font-mono text-amber-400">18.5 bps</span></div>
        </div>
      </div>
      <div class="p-6 rounded-2xl bg-white/5 border border-white/5 flex items-center justify-center text-gray-500">[Scenario Analysis Chart]</div>
    </div>
  `
});

const YieldCurve = defineComponent({ template: `<div class="flex items-center justify-center h-full text-gray-500">[Sovereign Yield Curves Chart]</div>` });
const YieldAnalysis = defineComponent({ template: `<div class="flex items-center justify-center h-full text-gray-500">[Return Decomposition Chart]</div>` });
const OASCalculator = defineComponent({ template: `<div class="flex items-center justify-center h-full text-gray-500">[OAS Calculator]</div>` });
const BondPricing = defineComponent({
  template: `
    <div class="h-full flex flex-col">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5 space-y-4">
          <h3 class="text-sm font-bold text-gray-400 uppercase border-b border-white/10 pb-2">Instrument Specs</h3>
          <div class="space-y-3">
            <div class="flex justify-between text-sm"><span class="text-gray-400">Coupon</span><span class="text-white font-mono">4.50%</span></div>
            <div class="flex justify-between text-sm"><span class="text-gray-400">Frequency</span><span class="text-white font-mono">Semi-Annual</span></div>
            <div class="flex justify-between text-sm"><span class="text-gray-400">Maturity</span><span class="text-white font-mono">15 Nov 2035</span></div>
            <div class="flex justify-between text-sm"><span class="text-gray-400">Day Count</span><span class="text-white font-mono">30/360</span></div>
          </div>
        </div>
        <div class="md:col-span-2 p-6 rounded-2xl bg-black/20 border border-white/5">
          <h3 class="text-sm font-bold text-gray-400 uppercase border-b border-white/10 pb-2 mb-4">Pricing Output</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div><span class="text-xs text-gray-500 block mb-1">Clean Price</span><span class="text-2xl font-bold text-white">98.45</span></div>
            <div><span class="text-xs text-gray-500 block mb-1">Dirty Price</span><span class="text-2xl font-bold text-gray-300">99.12</span></div>
            <div><span class="text-xs text-gray-500 block mb-1">YTM</span><span class="text-2xl font-bold text-amber-400">4.68%</span></div>
            <div><span class="text-xs text-gray-500 block mb-1">Accrued</span><span class="text-2xl font-bold text-gray-300">0.67</span></div>
          </div>
        </div>
      </div>
      <div class="flex-1 bg-white/5 rounded-2xl border border-white/5 p-6">
        <h3 class="text-sm font-bold text-gray-400 uppercase mb-6">Risk Metrics</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="flex flex-col items-center justify-center p-4 bg-black/20 rounded-xl"><div class="text-3xl font-bold text-white mb-2">7.84</div><div class="text-xs text-blue-400 font-bold uppercase">Macaulay Duration</div></div>
          <div class="flex flex-col items-center justify-center p-4 bg-black/20 rounded-xl border border-amber-500/20"><div class="text-3xl font-bold text-amber-400 mb-2">7.52</div><div class="text-xs text-amber-500 font-bold uppercase">Modified Duration</div></div>
          <div class="flex flex-col items-center justify-center p-4 bg-black/20 rounded-xl"><div class="text-3xl font-bold text-white mb-2">0.68</div><div class="text-xs text-emerald-400 font-bold uppercase">Convexity</div></div>
        </div>
      </div>
    </div>
  `
});
</script>
