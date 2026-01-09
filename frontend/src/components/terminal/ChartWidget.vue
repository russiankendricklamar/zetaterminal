<template>
  <div class="h-full w-full flex flex-col bg-transparent relative">
    <!-- Glass Header -->
    <div class="absolute top-0 left-0 right-0 z-10 px-4 py-3 flex justify-between items-start bg-gradient-to-b from-black/40 to-transparent">
      <div class="flex flex-col gap-1">
        <div class="flex items-baseline gap-3">
          <h2 class="text-lg font-bold text-white tracking-tight font-mono">{{ symbol }}</h2>
          <span class="text-xl font-bold font-mono" :class="priceChange >= 0 ? 'text-emerald-400' : 'text-rose-400'">
            {{ currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
          </span>
          <span class="text-xs font-mono px-2 py-0.5 rounded" :class="priceChange >= 0 ? 'text-emerald-400 bg-emerald-500/10' : 'text-rose-400 bg-rose-500/10'">
            {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
          </span>
        </div>
        <div class="flex gap-2 text-[10px] font-medium">
          <span class="bg-white/5 px-2 py-0.5 rounded text-white/60 border border-white/5">{{ assetName }}</span>
          <span class="bg-white/5 px-2 py-0.5 rounded text-white/60 border border-white/5">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block mr-1 animate-pulse"></span>
            Онлайн
          </span>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <div class="flex bg-black/30 rounded-lg p-0.5 backdrop-blur-md border border-white/5">
          <button
            v-for="(t, i) in timeframes"
            :key="t"
            :class="`px-3 py-1 text-xs rounded-md transition-all ${i === 1 ? 'bg-white/10 text-white shadow-sm' : 'text-gray-500 hover:text-gray-300'}`"
          >
            {{ t }}
          </button>
        </div>
        <button 
          v-if="onToggleExpand"
          @click="onToggleExpand"
          class="p-1.5 text-gray-400 hover:text-white transition-colors hover:bg-white/10 rounded-lg"
        >
          <component :is="isExpanded ? 'MinimizeIcon' : 'MaximizeIcon'" class="w-4 h-4" />
        </button>
      </div>
    </div>
    
    <!-- Chart Area -->
    <div class="flex-1 w-full pt-16">
      <v-chart 
        ref="chartRef"
        class="chart" 
        :option="chartOption"
        :style="{ height: '100%', width: '100%' }"
      />
    </div>
    
    <!-- Volume Chart at bottom -->
    <div class="h-[60px] w-full border-t border-white/5 bg-black/10">
      <v-chart 
        ref="volumeChartRef"
        class="volume-chart" 
        :option="volumeOption"
        :style="{ height: '100%', width: '100%' }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, BarChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  MarkLineComponent
} from 'echarts/components';
import VChart from 'vue-echarts';
import { Candle } from '@/types/terminal';

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  MarkLineComponent
]);

interface Props {
  data: Candle[];
  isExpanded?: boolean;
  symbol: string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  toggleExpand: [];
}>();

const chartRef = ref<InstanceType<typeof VChart> | null>(null);
const volumeChartRef = ref<InstanceType<typeof VChart> | null>(null);

const timeframes = ['15m', '1H', '4H', '1D'];

const assetName = computed(() => {
  const map: Record<string, string> = {
    'BTC/USDT': 'Bitcoin',
    'ETH/USDT': 'Ethereum',
    'SOL/USDT': 'Solana',
    'AAPL': 'Apple Inc.'
  };
  return map[props.symbol] || 'Asset';
});

// Текущая цена (последняя свеча)
const currentPrice = computed(() => {
  if (props.data.length === 0) return 0;
  return props.data[props.data.length - 1].close;
});

// Изменение цены
const priceChange = computed(() => {
  if (props.data.length < 2) return 0;
  const first = props.data[0].close;
  const last = props.data[props.data.length - 1].close;
  return ((last - first) / first) * 100;
});

const onToggleExpand = () => emit('toggleExpand');

const chartOption = computed(() => {
  const prices = props.data.map(d => d.close);
  const minPrice = Math.min(...prices) * 0.999;
  const maxPrice = Math.max(...prices) * 1.001;
  
  return {
    animation: true,
    animationDuration: 300,
    animationEasing: 'cubicOut',
    grid: {
      left: 10,
      right: 70,
      top: 10,
      bottom: 30,
      containLabel: false
    },
    xAxis: {
      type: 'category',
      data: props.data.map(d => d.time),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: 'rgba(255,255,255,0.3)',
        fontSize: 9,
        interval: Math.floor(props.data.length / 6),
        formatter: (val: string) => val
      },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      position: 'right',
      min: minPrice,
      max: maxPrice,
      splitNumber: 6,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: 'rgba(255,255,255,0.5)',
        fontSize: 10,
        fontFamily: 'JetBrains Mono, monospace',
        formatter: (val: number) => val.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: 'rgba(255,255,255,0.05)',
          type: 'dashed'
        }
      }
    },
    series: [{
      type: 'line',
      data: prices,
      smooth: 0.3,
      symbol: 'none',
      lineStyle: {
        color: priceChange.value >= 0 ? '#10B981' : '#EF4444',
        width: 2,
        shadowColor: priceChange.value >= 0 ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)',
        shadowBlur: 10
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: priceChange.value >= 0 ? [
            { offset: 0, color: 'rgba(16, 185, 129, 0.25)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0)' }
          ] : [
            { offset: 0, color: 'rgba(239, 68, 68, 0.25)' },
            { offset: 1, color: 'rgba(239, 68, 68, 0)' }
          ]
        }
      },
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: {
          color: priceChange.value >= 0 ? '#10B981' : '#EF4444',
          type: 'dashed',
          width: 1
        },
        label: {
          show: true,
          position: 'end',
          formatter: currentPrice.value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
          backgroundColor: priceChange.value >= 0 ? '#10B981' : '#EF4444',
          color: '#fff',
          padding: [4, 8],
          borderRadius: 4,
          fontSize: 11,
          fontFamily: 'JetBrains Mono, monospace',
          fontWeight: 'bold'
        },
        data: [{ yAxis: currentPrice.value }]
      },
      animationDuration: 300,
      animationEasing: 'cubicOut'
    }],
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 15, 20, 0.95)',
      borderColor: 'rgba(255,255,255,0.1)',
      borderRadius: 8,
      padding: [10, 14],
      textStyle: {
        color: '#fff',
        fontSize: 12,
        fontFamily: 'JetBrains Mono, monospace'
      },
      formatter: (params: any) => {
        const data = params[0];
        return `<div style="font-size:10px;color:#888;margin-bottom:4px">${data.name}</div>
                <div style="font-size:14px;font-weight:bold;color:#fff">${Number(data.value).toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>`;
      }
    }
  };
});

const volumeOption = computed(() => ({
  animation: true,
  animationDuration: 300,
  grid: {
    left: 10,
    right: 70,
    top: 5,
    bottom: 5
  },
  xAxis: {
    type: 'category',
    data: props.data.map(d => d.time),
    show: false
  },
  yAxis: {
    type: 'value',
    show: false
  },
  series: [{
    type: 'bar',
    data: props.data.map((d, i) => ({
      value: d.volume,
      itemStyle: {
        color: i > 0 && props.data[i].close >= props.data[i-1].close 
          ? 'rgba(16, 185, 129, 0.3)' 
          : 'rgba(239, 68, 68, 0.3)',
        borderRadius: [2, 2, 0, 0]
      }
    })),
    barWidth: '80%'
  }],
  tooltip: { show: false }
}));

// Watch for data changes to update charts smoothly
watch(() => props.data, () => {
  // Charts will auto-update via computed options
}, { deep: true });

// Icon components
const MaximizeIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>' };
const MinimizeIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3"/></svg>' };
</script>

<style scoped>
.chart,
.volume-chart {
  height: 100%;
  width: 100%;
}
</style>
