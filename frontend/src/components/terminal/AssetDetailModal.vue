<template>
  <div class="fixed inset-0 z-[100] flex items-center justify-center p-4">
    <div 
      class="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" 
      @click="$emit('close')"
    ></div>
    
    <div class="relative w-full max-w-lg data-panel overflow-hidden transition-all transform scale-100 flex flex-col max-h-[90vh]">
      
      <!-- Header -->
      <div class="p-6 border-b border-white/5 flex items-start justify-between bg-white/5">
        <div class="flex items-center gap-4">
          <div :class="`w-14 h-14 rounded-2xl flex items-center justify-center text-xl font-bold shadow-lg ${
            asset.category === 'Crypto' ? 'bg-gradient-to-br from-orange-500/20 to-yellow-500/20 text-orange-400' :
            'bg-gradient-to-br from-blue-500/20 to-cyan-500/20 text-blue-400'
          }`">
            {{ asset.symbol.substring(0, 2) }}
          </div>
          <div>
            <h2 class="text-2xl font-bold text-white tracking-tight">{{ asset.name }}</h2>
            <div class="flex items-center gap-2 text-sm text-gray-400">
              <span class="font-mono">{{ asset.symbol }}</span>
              <span class="w-1 h-1 rounded-full bg-gray-600"></span>
              <span class="bg-white/10 px-1.5 py-0.5 rounded text-[10px] uppercase">{{ asset.category || 'Asset' }}</span>
            </div>
          </div>
        </div>
        <button 
          @click="$emit('close')"
          class="p-2 rounded-full hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
        >
          <XIcon class="w-5 h-5" />
        </button>
      </div>

      <div class="overflow-y-auto custom-scrollbar">
        <!-- Price & Chart -->
        <div class="p-6">
          <div class="flex items-baseline gap-4 mb-6">
            <span class="text-4xl font-mono font-bold text-white">{{ asset.price }}</span>
            <div :class="`flex items-center gap-1 px-2 py-1 rounded-lg text-sm font-bold ${isPositive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`">
              <component :is="isPositive ? 'TrendingUpIcon' : 'TrendingDownIcon'" class="w-4 h-4" />
              {{ asset.change }}
            </div>
          </div>

          <div class="h-48 w-full bg-black/20 rounded-xl border border-white/5 overflow-hidden relative mb-6">
            <div class="absolute top-3 left-3 z-10 text-[10px] font-bold text-gray-500 uppercase tracking-wider">1H Performance</div>
            <v-chart class="w-full h-full" :option="chartOption" autoresize />
          </div>

          <!-- Statistics Grid -->
          <div class="grid grid-cols-2 gap-3 mb-6">
            <div class="p-3 rounded-xl bg-white/5 border border-white/5">
              <div class="flex items-center gap-2 text-gray-500 text-xs mb-1">
                <ActivityIcon class="w-3 h-3" /> Vol (24h)
              </div>
              <div class="font-mono text-white font-medium">{{ asset.vol || '1.2B' }}</div>
            </div>
            <div class="p-3 rounded-xl bg-white/5 border border-white/5">
              <div class="flex items-center gap-2 text-gray-500 text-xs mb-1">
                <BarChart3Icon class="w-3 h-3" /> Mkt Cap
              </div>
              <div class="font-mono text-white font-medium">{{ asset.cap || '850M' }}</div>
            </div>
            <div class="p-3 rounded-xl bg-white/5 border border-white/5">
              <div class="flex items-center gap-2 text-gray-500 text-xs mb-1">
                <DollarSignIcon class="w-3 h-3" /> High (24h)
              </div>
              <div class="font-mono text-white font-medium">{{ high24h }}</div>
            </div>
            <div class="p-3 rounded-xl bg-white/5 border border-white/5">
              <div class="flex items-center gap-2 text-gray-500 text-xs mb-1">
                <DollarSignIcon class="w-3 h-3" /> Low (24h)
              </div>
              <div class="font-mono text-white font-medium">{{ low24h }}</div>
            </div>
          </div>

          <!-- About Section -->
          <div class="mb-6">
            <h3 class="text-sm font-bold text-white mb-2 flex items-center gap-2">
              <GlobeIcon class="w-3.5 h-3.5 text-indigo-400" /> About {{ asset.name }}
            </h3>
            <p class="text-xs text-gray-400 leading-relaxed">
              {{ asset.name }} is a leading digital asset in the {{ asset.category || 'Global' }} market. 
              It has shown significant volatility in the last 24 hours. Smart contract capability 
              and decentralized nature make it a key player in the ecosystem.
            </p>
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="p-4 border-t border-white/5 bg-black/20 backdrop-blur-md flex gap-3">
        <button class="flex-1 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm transition-colors flex items-center justify-center gap-2 border border-white/5">
          <StarIcon class="w-4 h-4" /> Favorite
        </button>
        <button 
          @click="handleTrade"
          class="flex-[2] py-3 rounded-xl bg-white text-black font-bold text-sm hover:scale-[1.02] transition-transform shadow-lg shadow-white/10 flex items-center justify-center gap-2"
        >
          Go to Analysis <ArrowRightIcon class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, useMemo } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import { TooltipComponent, GridComponent } from 'echarts/components';
import VChart from 'vue-echarts';
import { AssetInfo } from '@/types/terminal';
import { generateCandles } from '@/utils/terminalConstants';

use([CanvasRenderer, LineChart, TooltipComponent, GridComponent]);

interface Props {
  asset: AssetInfo;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  close: [];
  trade: [symbol: string];
}>();

const isPositive = computed(() => props.asset.change.startsWith('+'));

const chartData = computed(() => generateCandles(30));

const priceNum = computed(() => parseFloat(props.asset.price.replace(/[^0-9.]/g, '')));
const high24h = computed(() => (priceNum.value * 1.05).toFixed(2));
const low24h = computed(() => (priceNum.value * 0.95).toFixed(2));

const chartOption = computed(() => ({
  grid: { left: 0, right: 0, top: 20, bottom: 0 },
  xAxis: { type: 'category', show: false, data: chartData.value.map((_, i) => i) },
  yAxis: { type: 'value', show: false },
  series: [{
    type: 'line',
    data: chartData.value.map(d => d.close),
    smooth: true,
    symbol: 'none',
    lineStyle: { color: isPositive.value ? '#10B981' : '#F43F5E', width: 2 },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: isPositive.value ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)' },
          { offset: 1, color: isPositive.value ? 'rgba(16, 185, 129, 0)' : 'rgba(244, 63, 94, 0)' }
        ]
      }
    }
  }],
  tooltip: {
    backgroundColor: 'rgba(0,0,0,0.8)',
    borderColor: 'transparent',
    textStyle: { color: '#fff', fontSize: 12 }
  }
}));

const handleTrade = () => {
  emit('trade', props.asset.symbol);
  emit('close');
};

// Icon components
const XIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' };
const TrendingUpIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
const TrendingDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>' };
const ActivityIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>' };
const BarChart3Icon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>' };
const DollarSignIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>' };
const GlobeIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>' };
const StarIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>' };
const ArrowRightIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>' };
</script>
