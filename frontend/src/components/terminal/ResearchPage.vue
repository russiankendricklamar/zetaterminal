<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box icon-indigo">
          <BookOpenIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">ИССЛЕДОВАНИЯ</h2>
          <p class="section-subtitle font-mono">INSTITUTIONAL GRADE ANALYSIS & INSIGHTS</p>
        </div>
      </div>
      <div class="tab-group">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['tab-btn', { active: section === tab.id }]">
          {{ tab.label }}
        </button>
      </div>
    </div>
    <div class="flex-1 flex flex-col gap-6">
      <ResearchHub v-if="section === 'RES'" :symbol="symbol" />
      <CompanyPrimer v-else-if="section === 'BICO'" :symbol="symbol" />
      <IndustryPrimer v-else-if="section === 'BIP'" />
      <Transcripts v-else-if="section === 'ECT'" :symbol="symbol" />
      <ResearchHub v-else :symbol="symbol" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineComponent, h } from 'vue';

const BookOpenIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('path', { d: 'M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z' }), h('path', { d: 'M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z' })]) });

const props = defineProps<{ symbol?: string; activeSection?: string; }>();
const section = ref(props.activeSection || 'RES');
const symbol = ref(props.symbol || 'NVDA');
watch(() => props.activeSection, (v) => { if (v) section.value = v; });

const tabs = [
  { id: 'RES', label: 'Исследовательский хаб' },
  { id: 'BICO', label: 'Company Primer' },
  { id: 'BIP', label: 'Industry Primer' },
  { id: 'ECT', label: 'Transcripts' },
];

const ResearchHub = defineComponent({
  props: ['symbol'],
  setup(props) {
    const reports = [
      { title: `${props.symbol}: The AI Supercycle Thesis`, firm: 'Goldman Sachs', analyst: 'T. Koslowski', date: 'Oct 24, 2025', type: 'Initiation', rating: 'Buy' },
      { title: 'Semiconductors: Supply Chain Resilience', firm: 'Morgan Stanley', analyst: 'J. Moore', date: 'Oct 20, 2025', type: 'Sector Update', rating: 'Overweight' },
      { title: `${props.symbol} Q3 Preview: Expectations High`, firm: 'JP Morgan', analyst: 'H. Yang', date: 'Oct 15, 2025', type: 'Earnings Preview', rating: 'Buy' },
    ];
    return { reports };
  },
  template: `
    <div class="flex flex-col h-full">
      <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div class="relative flex-1 max-w-lg">
          <input type="text" :placeholder="'Search research for ' + symbol + '...'" class="w-full bg-black/40 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white focus:border-indigo-500/50 outline-none" />
        </div>
        <button class="px-3 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-xs font-bold text-white shadow-lg">Latest</button>
      </div>
      <div class="grid grid-cols-1 gap-4">
        <div v-for="(report, i) in reports" :key="i" class="flex flex-col md:flex-row md:items-center justify-between p-5 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 hover:border-indigo-500/30 transition-all cursor-pointer group">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-xs border border-indigo-500/20">{{ report.firm.substring(0, 2) }}</div>
            <div>
              <h4 class="text-base font-bold text-white group-hover:text-indigo-300 transition-colors mb-1">{{ report.title }}</h4>
              <div class="flex flex-wrap items-center gap-3 text-xs text-gray-400">
                <span class="font-bold text-gray-300">{{ report.firm }}</span><span>•</span><span>{{ report.analyst }}</span><span>•</span><span>{{ report.date }}</span>
                <span class="bg-white/10 px-1.5 py-0.5 rounded text-[10px] uppercase">{{ report.type }}</span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-6 mt-4 md:mt-0 pl-14 md:pl-0">
            <div class="text-center">
              <div :class="['text-sm font-bold', report.rating === 'Buy' || report.rating === 'Overweight' ? 'text-emerald-400' : 'text-yellow-400']">{{ report.rating }}</div>
              <div class="text-[10px] text-gray-500 uppercase">Rating</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
});

const CompanyPrimer = defineComponent({ props: ['symbol'], template: `<div class="flex items-center justify-center h-full text-gray-500">[Company Primer Overview]</div>` });
const IndustryPrimer = defineComponent({ template: `<div class="flex items-center justify-center h-full text-gray-500">[Industry Primer & TAM Analysis]</div>` });
const Transcripts = defineComponent({ props: ['symbol'], template: `<div class="flex items-center justify-center h-full text-gray-500">[Earnings Call Transcripts]</div>` });
</script>
