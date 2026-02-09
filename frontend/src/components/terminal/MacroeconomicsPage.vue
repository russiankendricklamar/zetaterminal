<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box">
          <GlobeIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">МАКРОЭКОНОМИКА</h2>
          <p class="section-subtitle font-mono">ИНДИКАТОРЫ, РЕЛИЗЫ И ЭКОНОМИЧЕСКАЯ ПОЛИТИКА</p>
        </div>
      </div>
      <div class="tab-group">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['tab-btn', { active: section === tab.id }]">
          {{ tab.label }}
        </button>
      </div>
    </div>
    <div class="flex-1 flex flex-col gap-6">
      <EconomicCalendar v-if="section === 'ECO'" />
      <EconomicData v-else-if="section === 'ECST'" />
      <Forecasts v-else-if="section === 'ECFC'" />
      <Workbench v-else-if="section === 'ECWB'" />
      <EconomicCalendar v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineComponent, h } from 'vue';

const GlobeIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('circle', { cx: '12', cy: '12', r: '10' }), h('line', { x1: '2', y1: '12', x2: '22', y2: '12' }), h('path', { d: 'M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z' })]) });

const props = defineProps<{ symbol?: string; activeSection?: string; }>();
const section = ref(props.activeSection || 'ECO');
watch(() => props.activeSection, (v) => { if (v) section.value = v; });

const tabs = [
  { id: 'ECO', label: 'Экономический календарь' },
  { id: 'ECST', label: 'Макроэкономические данные' },
  { id: 'ECFC', label: 'Прогнозы' },
  { id: 'ECWB', label: 'Workbench' },
];

const EconomicCalendar = defineComponent({
  setup() {
    const events = [
      { time: '08:30', country: 'US', impact: 'High', event: 'CPI YoY', period: 'Sep', forecast: '3.6%', actual: '3.7%', prev: '3.7%' },
      { time: '08:30', country: 'US', impact: 'High', event: 'Core CPI YoY', period: 'Sep', forecast: '4.1%', actual: '4.1%', prev: '4.3%' },
      { time: '08:30', country: 'US', impact: 'Med', event: 'Jobless Claims', period: 'Wk', forecast: '210K', actual: '209K', prev: '207K' },
      { time: '14:00', country: 'US', impact: 'High', event: 'FOMC Minutes', period: '-', forecast: '-', actual: '-', prev: '-' },
    ];
    return { events };
  },
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="flex justify-between items-center">
        <div class="flex gap-4">
          <button class="px-3 py-1 rounded-lg bg-white/10 text-xs font-bold text-white">Today</button>
          <button class="px-3 py-1 rounded-lg text-xs font-bold text-gray-500 hover:text-white">Tomorrow</button>
          <button class="px-3 py-1 rounded-lg text-xs font-bold text-gray-500 hover:text-white">This Week</button>
        </div>
      </div>
      <div class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
        <table class="w-full text-left border-collapse">
          <thead><tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0"><th class="p-4 w-20">Time</th><th class="p-4 w-16 text-center">Cty</th><th class="p-4">Event</th><th class="p-4">Period</th><th class="p-4 text-right">Actual</th><th class="p-4 text-right">Forecast</th><th class="p-4 text-right">Previous</th></tr></thead>
          <tbody class="text-sm font-mono text-gray-300">
            <tr v-for="(evt, i) in events" :key="i" class="border-b border-white/5 hover:bg-white/5">
              <td class="p-4 text-xs text-gray-500">{{ evt.time }}</td>
              <td class="p-4 text-center"><span class="text-xs font-bold bg-white/10 px-1.5 py-0.5 rounded text-white">{{ evt.country }}</span></td>
              <td class="p-4"><div class="flex items-center gap-2"><div :class="['w-1.5 h-1.5 rounded-full', evt.impact === 'High' ? 'bg-rose-500' : 'bg-orange-500']"></div><span :class="evt.impact === 'High' ? 'text-white font-bold' : 'text-gray-300'">{{ evt.event }}</span></div></td>
              <td class="p-4 text-xs text-gray-500">{{ evt.period }}</td>
              <td :class="['p-4 text-right font-bold', evt.actual === '-' ? 'text-gray-600' : 'text-white']">{{ evt.actual }}</td>
              <td class="p-4 text-right text-gray-400">{{ evt.forecast }}</td>
              <td class="p-4 text-right text-gray-500">{{ evt.prev }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
});

const EconomicData = defineComponent({ template: `<div class="flex items-center justify-center h-full text-gray-500">[Economic Data Time Series]</div>` });
const Forecasts = defineComponent({
  setup() {
    const forecasts = [
      { country: 'United States', metric: 'Real GDP', y25: '1.5%', y26: '1.8%' },
      { country: 'United States', metric: 'CPI Inflation', y25: '2.5%', y26: '2.1%' },
      { country: 'Euro Area', metric: 'Real GDP', y25: '0.8%', y26: '1.4%' },
      { country: 'China', metric: 'Real GDP', y25: '4.5%', y26: '4.2%' },
    ];
    return { forecasts };
  },
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5"><h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Global Growth (2025E)</h3><div class="text-3xl font-bold text-white">2.9%</div><div class="text-xs text-rose-400 mt-1">Revised Down</div></div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5"><h3 class="text-sm font-bold text-gray-400 uppercase mb-2">US Recession Prob</h3><div class="text-3xl font-bold text-orange-400">45%</div><div class="text-xs text-gray-500 mt-1">Next 12 Months</div></div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5"><h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Peak Rates (Fed)</h3><div class="text-3xl font-bold text-emerald-400">5.50%</div></div>
      </div>
      <div class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
        <table class="w-full text-left"><thead><tr class="text-xs text-gray-400 uppercase bg-white/5"><th class="p-4">Country</th><th class="p-4">Metric</th><th class="p-4 text-right">FY 2025</th><th class="p-4 text-right">FY 2026</th></tr></thead>
        <tbody class="text-sm font-mono text-gray-300">
          <tr v-for="(row, i) in forecasts" :key="i" class="border-b border-white/5 hover:bg-white/5">
            <td class="p-4 font-bold text-white">{{ row.country }}</td>
            <td class="p-4 text-slate-400">{{ row.metric }}</td>
            <td class="p-4 text-right font-bold text-white">{{ row.y25 }}</td>
            <td class="p-4 text-right text-gray-500">{{ row.y26 }}</td>
          </tr>
        </tbody></table>
      </div>
    </div>
  `
});
const Workbench = defineComponent({ template: `<div class="flex items-center justify-center h-full text-gray-500">[Economic Workbench Charts]</div>` });
</script>
