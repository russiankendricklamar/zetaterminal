<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 p-8 flex flex-col animate-fade-in custom-scrollbar overflow-y-auto">
    
    <!-- Header & Tabs -->
    <div class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-6">
      <div class="flex items-center gap-4">
        <div :class="`p-3 rounded-2xl transition-colors ${getAccentColor()}`">
          <component :is="getTabIcon()" class="w-8 h-8" />
        </div>
        <div>
          <h1 class="text-3xl font-bold text-white tracking-tight">Аналитический хаб</h1>
          <p class="text-gray-400">
            <span v-if="activeTab === 'AI'">Продвинутая аналитика рынка на основе ИИ</span>
            <span v-else-if="activeTab === 'Quant'">Количественные метрики и моделирование рисков</span>
            <span v-else>Производительность портфеля и распределение активов</span>
          </p>
        </div>
      </div>

      <div class="flex bg-white/5 rounded-xl p-1.5 border border-white/5 self-start md:self-center">
        <button 
          @click="activeTab = 'AI'" 
          :class="`px-6 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${getTabColor(activeTab === 'AI')}`"
        >
          <BrainIcon class="w-3.5 h-3.5" /> AI Анализ
        </button>
        <button 
          @click="activeTab = 'Quant'" 
          :class="`px-6 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${getTabColor(activeTab === 'Quant')}`"
        >
          <CalculatorIcon class="w-3.5 h-3.5" /> Количественная аналитика
        </button>
        <button 
          @click="activeTab = 'Finance'" 
          :class="`px-6 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${getTabColor(activeTab === 'Finance')}`"
        >
          <PieChartIcon class="w-3.5 h-3.5" /> Финансовый анализ
        </button>
      </div>
    </div>

    <!-- Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <!-- Metric Card 1 -->
      <div class="p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
        <div class="flex justify-between items-start mb-4">
          <div class="p-2 rounded-lg bg-blue-500/20 text-blue-400">
            <component :is="activeTab === 'Finance' ? 'DollarSignIcon' : 'ActivityIcon'" class="w-5 h-5" />
          </div>
          <span class="text-xs text-gray-500 font-bold uppercase">
            {{ activeTab === 'AI' ? 'Настроение' : activeTab === 'Quant' ? 'Бета' : 'Чистая стоимость' }}
          </span>
        </div>
        <div class="text-3xl font-bold text-white mb-1">
          {{ activeTab === 'AI' ? 'Бычье' : activeTab === 'Quant' ? '1.45' : '$42,301.54' }}
        </div>
        <div class="text-sm text-gray-400">
          {{ activeTab === 'AI' ? 'Настроение рынка' : activeTab === 'Quant' ? 'Корреляция с SPX' : 'Общая стоимость портфеля' }}
        </div>
      </div>

      <!-- Metric Card 2 -->
      <div class="p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
        <div class="flex justify-between items-start mb-4">
          <div class="p-2 rounded-lg bg-purple-500/20 text-purple-400"><ZapIcon class="w-5 h-5" /></div>
          <span class="text-xs text-gray-500 font-bold uppercase">
            {{ activeTab === 'AI' ? 'Уверенность' : activeTab === 'Quant' ? 'Шарп' : 'PnL за 24ч' }}
          </span>
        </div>
        <div class="text-3xl font-bold text-white mb-1">
          {{ activeTab === 'AI' ? '87%' : activeTab === 'Quant' ? '2.1' : '+$1,240.50' }}
        </div>
        <div class="text-sm text-gray-400">
          {{ activeTab === 'AI' ? 'Уверенность прогноза' : activeTab === 'Quant' ? 'Доходность с учётом риска' : 'Прибыль/Убыток за день' }}
        </div>
      </div>

      <!-- Metric Card 3 -->
      <div class="p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
        <div class="flex justify-between items-start mb-4">
          <div class="p-2 rounded-lg bg-pink-500/20 text-pink-400">
            <component :is="activeTab === 'Finance' ? 'PercentIcon' : 'LayersIcon'" class="w-5 h-5" />
          </div>
          <span class="text-xs text-gray-500 font-bold uppercase">
            {{ activeTab === 'AI' ? 'Волатильность' : activeTab === 'Quant' ? 'Подразумеваемая волатильность' : 'Уровень маржи' }}
          </span>
        </div>
        <div class="text-3xl font-bold text-white mb-1">
          {{ activeTab === 'AI' ? 'Высокая' : activeTab === 'Quant' ? '14.2%' : '420%' }}
        </div>
        <div class="text-sm text-gray-400">
          {{ activeTab === 'AI' ? 'Прогноз волатильности' : activeTab === 'Quant' ? '30-дневная ПВ' : 'Здоровый статус' }}
        </div>
      </div>
    </div>

    <!-- Main Chart Area -->
    <div class="flex-1 min-h-[400px] p-6 rounded-2xl bg-black/20 border border-white/5 relative flex flex-col lg:flex-row gap-6">
      
      <!-- Chart Container -->
      <div :class="`flex-1 flex flex-col ${activeTab === 'Finance' ? 'lg:w-2/3' : 'w-full'}`">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-bold text-white flex items-center gap-2">
            <BarChart2Icon class="w-4 h-4 text-gray-400" />
            <span v-if="activeTab === 'AI'">Модель прогнозирования тренда (Gemini-3 Pro)</span>
            <span v-else-if="activeTab === 'Quant'">Генерация альфы и просадка</span>
            <span v-else>История производительности портфеля</span>
          </h3>
          <div v-if="activeTab === 'Quant'" class="flex gap-2">
            <span class="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">Процент побед: 65%</span>
            <span class="text-xs font-mono text-rose-400 bg-rose-500/10 px-2 py-1 rounded border border-rose-500/20">Макс. просадка: -12%</span>
          </div>
          <span v-if="activeTab === 'Finance'" class="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">+15.4% За всё время</span>
        </div>
        
        <div class="flex-1 min-h-[300px]">
          <v-chart class="w-full h-full" :option="chartOption" autoresize />
        </div>
      </div>

      <!-- Finance Side Panel (Pie Chart) -->
      <div v-if="activeTab === 'Finance'" class="lg:w-1/3 bg-white/5 rounded-xl p-4 border border-white/5 flex flex-col">
        <h3 class="text-sm font-bold text-white mb-4 flex items-center gap-2">
          <PieChartIcon class="w-3.5 h-3.5 text-gray-400" /> Распределение активов
        </h3>
        <div class="flex-1 min-h-[200px] relative">
          <v-chart class="w-full h-full" :option="pieOption" autoresize />
        </div>
        <div class="mt-4 space-y-2">
          <div v-for="(item, index) in financeData" :key="item.name" class="flex justify-between items-center text-xs">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full" :style="{ backgroundColor: COLORS[index] }"></div>
              <span class="text-gray-300">{{ item.name }}</span>
            </div>
            <span class="text-white font-mono">{{ ((item.value / 1100) * 100).toFixed(0) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Opportunity Banner -->
    <div v-if="activeTab === 'AI'" class="mt-6 p-6 rounded-2xl bg-gradient-to-r from-indigo-900/40 to-purple-900/40 border border-white/10 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="p-3 bg-white/10 rounded-xl backdrop-blur-md">
          <TrendingUpIcon class="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 class="font-bold text-white text-lg">Обнаружена следующая возможность</h3>
          <p class="text-sm text-gray-400">Gemini выявил дивергенцию на часовом таймфрейме BTC/USDT.</p>
        </div>
      </div>
      <button class="px-6 py-2 bg-white text-black font-bold rounded-xl hover:scale-105 transition-transform shadow-lg shadow-white/10 text-sm">Подробнее</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, PieChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, LineChart, PieChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent]);

interface Props {
  activeSection?: 'AI' | 'Quant' | 'Finance';
}

const props = withDefaults(defineProps<Props>(), {
  activeSection: 'AI'
});

const activeTab = ref<'AI' | 'Quant' | 'Finance'>(props.activeSection);

watch(() => props.activeSection, (val) => {
  activeTab.value = val;
});

const COLORS = ['#F59E0B', '#6366F1', '#10B981', '#EC4899'];

const financeData = [
  { name: 'BTC', value: 400 },
  { name: 'ETH', value: 300 },
  { name: 'USDT', value: 300 },
  { name: 'SOL', value: 100 },
];

const chartData = computed(() => {
  return Array.from({ length: 20 }, (_, i) => ({
    name: i,
    val1: Math.random() * 100 + (activeTab.value === 'Finance' ? 40000 : 0),
    val2: Math.random() * 100 + 50 + (activeTab.value === 'Finance' ? 40000 : 0),
  }));
});

const chartOption = computed(() => {
  const color = activeTab.value === 'Finance' ? '#F59E0B' : activeTab.value === 'AI' ? '#6366f1' : '#10b981';
  
  return {
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: chartData.value.map(d => d.name),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: 'rgba(255,255,255,0.3)' }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: 'rgba(255,255,255,0.3)' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
    },
    series: [
      {
        type: 'line',
        data: chartData.value.map(d => d.val1),
        smooth: true,
        symbol: 'none',
        lineStyle: { color, width: 3 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: color.replace(')', ', 0.3)').replace('rgb', 'rgba') },
              { offset: 1, color: 'rgba(0,0,0,0)' }
            ]
          }
        }
      }
    ],
    tooltip: {
      backgroundColor: 'rgba(20,20,30,0.9)',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#fff' }
    }
  };
});

const pieOption = computed(() => ({
  series: [{
    type: 'pie',
    radius: ['50%', '70%'],
    center: ['50%', '50%'],
    data: financeData.map((item, index) => ({
      value: item.value,
      name: item.name,
      itemStyle: { color: COLORS[index] }
    })),
    label: { show: false },
    emphasis: { scale: true, scaleSize: 5 }
  }],
  tooltip: {
    backgroundColor: 'rgba(20,20,30,0.9)',
    borderColor: 'rgba(255,255,255,0.1)',
    textStyle: { color: '#fff' }
  }
}));

const getAccentColor = () => {
  if (activeTab.value === 'AI') return 'bg-indigo-500/20 text-indigo-400';
  if (activeTab.value === 'Quant') return 'bg-emerald-500/20 text-emerald-400';
  return 'bg-orange-500/20 text-orange-400';
};

const getTabColor = (isActive: boolean) => {
  if (!isActive) return 'text-gray-400 hover:text-white hover:bg-white/5';
  return 'bg-white/10 text-white shadow-lg';
};

const getTabIcon = () => {
  if (activeTab.value === 'AI') return 'BrainIcon';
  if (activeTab.value === 'Quant') return 'TargetIcon';
  return 'WalletIcon';
};

// Icon components
const BrainIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.54ZM14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.54Z"/></svg>' };
const CalculatorIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="16" y1="14" x2="16" y2="18"/><line x1="16" y1="10" x2="16" y2="10"/><line x1="12" y1="10" x2="12" y2="10"/><line x1="8" y1="10" x2="8" y2="10"/><line x1="12" y1="14" x2="12" y2="14"/><line x1="8" y1="14" x2="8" y2="14"/><line x1="12" y1="18" x2="12" y2="18"/><line x1="8" y1="18" x2="8" y2="18"/></svg>' };
const PieChartIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>' };
const TargetIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>' };
const WalletIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0 0 4h4v-4h-4Z"/></svg>' };
const ActivityIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>' };
const DollarSignIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>' };
const ZapIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>' };
const LayersIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>' };
const PercentIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>' };
const BarChart2Icon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>' };
const TrendingUpIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
</script>
