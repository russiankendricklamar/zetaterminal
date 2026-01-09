<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full">
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-gray-700/20 to-zinc-700/20 flex items-center justify-center text-lg font-bold text-gray-300 border border-gray-500/30">
          <component :is="section === 'FLDS' ? DatabaseIcon : HelpCircleIcon" class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">{{ section === 'FLDS' ? 'Data Field Dictionary' : 'Help Center' }}</h2>
          <p class="text-xs text-gray-400">{{ section === 'FLDS' ? 'Catalog of Terminal Data Points' : 'Documentation, FAQ & Support' }}</p>
        </div>
      </div>
      <div class="flex bg-black/40 rounded-xl p-1 border border-white/5 overflow-x-auto">
        <button @click="section = 'FLDS'" :class="['px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap', section === 'FLDS' ? 'bg-gray-600/20 text-gray-200 border border-gray-500/30' : 'text-gray-500 hover:text-white hover:bg-white/5']">
          Data Fields
        </button>
        <button @click="section = 'HL'" :class="['px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap', section === 'HL' ? 'bg-gray-600/20 text-gray-200 border border-gray-500/30' : 'text-gray-500 hover:text-white hover:bg-white/5']">
          Help & Support
        </button>
      </div>
    </div>
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <DataFieldsCatalog v-if="section === 'FLDS'" />
      <HelpCenter v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineComponent, h } from 'vue';

const DatabaseIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('ellipse', { cx: '12', cy: '5', rx: '9', ry: '3' }), h('path', { d: 'M21 12c0 1.66-4 3-9 3s-9-1.34-9-3' }), h('path', { d: 'M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5' })]) });
const HelpCircleIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('circle', { cx: '12', cy: '12', r: '10' }), h('path', { d: 'M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3' }), h('line', { x1: '12', y1: '17', x2: '12.01', y2: '17' })]) });

const props = defineProps<{ activeSection?: string; }>();
const section = ref(props.activeSection || 'FLDS');
watch(() => props.activeSection, (v) => { if (v) section.value = v; });

const DataFieldsCatalog = defineComponent({
  setup() {
    const fields = [
      { mnemonic: 'LAST_PRICE', name: 'Last Price', category: 'Market Data', desc: 'The most recent trade price for the asset.' },
      { mnemonic: 'PX_OPEN', name: 'Open Price', category: 'Market Data', desc: 'Price at market open.' },
      { mnemonic: 'PE_RATIO', name: 'P/E Ratio', category: 'Fundamental', desc: 'Price-to-Earnings ratio based on TTM earnings.' },
      { mnemonic: 'EPS_FWD', name: 'Forward EPS', category: 'Fundamental', desc: 'Consensus EPS forecast for next 12m.' },
      { mnemonic: 'RSI_14D', name: 'RSI (14)', category: 'Technical', desc: 'Relative Strength Index (14 period).' },
      { mnemonic: 'BETA_RAW', name: 'Raw Beta', category: 'Risk', desc: 'Slope of regression line vs benchmark.' },
    ];
    return { fields };
  },
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="flex gap-4">
        <div class="relative flex-1"><input type="text" placeholder="Search by Mnemonic or Name..." class="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white focus:border-gray-500/50 outline-none" /></div>
        <div class="flex gap-2">
          <button v-for="cat in ['All', 'Market Data', 'Fundamental', 'Technical', 'Risk']" :key="cat" class="px-3 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-xs font-bold text-gray-400 hover:text-white border border-white/5">{{ cat }}</button>
        </div>
      </div>
      <div class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
        <table class="w-full text-left border-collapse"><thead><tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0 z-10"><th class="p-4">Mnemonic</th><th class="p-4">Name</th><th class="p-4">Category</th><th class="p-4">Description</th></tr></thead>
        <tbody class="text-sm font-mono text-gray-300">
          <tr v-for="(f, i) in fields" :key="i" class="border-b border-white/5 hover:bg-white/5">
            <td class="p-4 font-bold text-indigo-300">{{ f.mnemonic }}</td>
            <td class="p-4 text-white font-sans font-bold">{{ f.name }}</td>
            <td class="p-4"><span class="px-2 py-1 rounded bg-white/5 text-[10px] text-gray-400 uppercase border border-white/5">{{ f.category }}</span></td>
            <td class="p-4 text-gray-400 font-sans text-xs">{{ f.desc }}</td>
          </tr>
        </tbody></table>
      </div>
    </div>
  `
});

const HelpCenter = defineComponent({
  template: `
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 h-full">
      <div class="p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors cursor-pointer group">
        <div class="p-3 bg-blue-500/20 rounded-xl text-blue-400 w-fit mb-4">📘</div>
        <h3 class="text-lg font-bold text-white mb-2">Documentation</h3>
        <p class="text-sm text-gray-400 mb-4">Comprehensive guides on terminal features, syntax, and APIs.</p>
        <span class="text-xs text-blue-400 font-bold group-hover:underline">Read Docs →</span>
      </div>
      <div class="p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors cursor-pointer group">
        <div class="p-3 bg-emerald-500/20 rounded-xl text-emerald-400 w-fit mb-4">💬</div>
        <h3 class="text-lg font-bold text-white mb-2">Live Support</h3>
        <p class="text-sm text-gray-400 mb-4">Chat with our 24/7 support desk for technical issues.</p>
        <span class="text-xs text-emerald-400 font-bold group-hover:underline">Start Chat →</span>
      </div>
      <div class="p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors cursor-pointer group">
        <div class="p-3 bg-purple-500/20 rounded-xl text-purple-400 w-fit mb-4">🔌</div>
        <h3 class="text-lg font-bold text-white mb-2">API Reference</h3>
        <p class="text-sm text-gray-400 mb-4">Integrate Terminal data into your own applications.</p>
        <span class="text-xs text-purple-400 font-bold group-hover:underline">View Spec →</span>
      </div>
      <div class="col-span-1 md:col-span-2 lg:col-span-3 p-6 rounded-2xl bg-black/20 border border-white/5 mt-4">
        <h3 class="text-lg font-bold text-white mb-4">FAQ</h3>
        <div class="space-y-2">
          <div v-for="q in ['How do I create a custom formula?', 'Where can I find historical spread data?', 'How to export data to Excel?', 'What is the latency of the Live feed?']" :key="q" class="p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 flex justify-between items-center cursor-pointer">
            <span class="text-sm text-gray-300">{{ q }}</span><span class="text-gray-600">→</span>
          </div>
        </div>
      </div>
    </div>
  `
});
</script>
