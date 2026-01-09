<template>
  <BaseWidget
    title="Рынки"
    icon="TrendingUpIcon"
    icon-bg="bg-green-500/20"
    icon-color="text-green-400"
    :width="width"
    :height="height"
    :resizable="resizable"
    @settings="$emit('settings')"
    @remove="$emit('remove')"
    @resize="handleResize"
  >
    <div class="p-4 space-y-2">
      <div 
        v-for="asset in topAssets.slice(0, 8)" 
        :key="asset.symbol"
        class="flex items-center justify-between p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors cursor-pointer"
        @click="$emit('assetClick', asset)"
      >
        <div class="flex items-center gap-3">
          <div :class="`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${getCategoryStyle(asset.category)}`">
            {{ asset.symbol.substring(0, 2) }}
          </div>
          <div>
            <div class="text-sm font-bold text-white">{{ asset.symbol }}</div>
            <div class="text-xs text-gray-500">{{ asset.name }}</div>
          </div>
        </div>
        <div class="text-right">
          <div class="text-sm font-mono text-white">{{ asset.price }}</div>
          <div :class="`text-xs font-bold ${asset.change.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'}`">
            {{ asset.change }}
          </div>
        </div>
      </div>
    </div>
  </BaseWidget>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import BaseWidget from './BaseWidget.vue';
import { AssetInfo } from '@/types/terminal';

interface Props {
  width?: number;
  height?: number;
  resizable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  width: 2,
  height: 3,
  resizable: true,
});

const emit = defineEmits<{
  settings: [];
  remove: [];
  resize: [width: number, height: number];
  assetClick: [asset: AssetInfo];
}>();

const width = ref(props.width);
const height = ref(props.height);

const handleResize = (w: number, h: number) => {
  width.value = w;
  height.value = h;
  emit('resize', w, h);
};

const topAssets: AssetInfo[] = [
  { name: 'Apple Inc.', symbol: 'AAPL', price: '173.50', change: '+1.20%', category: 'Equities' },
  { name: 'NVIDIA Corp', symbol: 'NVDA', price: '892.10', change: '+4.25%', category: 'Equities' },
  { name: 'Microsoft', symbol: 'MSFT', price: '420.55', change: '-0.45%', category: 'Equities' },
  { name: 'Tesla Inc', symbol: 'TSLA', price: '175.30', change: '+2.10%', category: 'Equities' },
  { name: 'Bitcoin', symbol: 'BTC/USDT', price: '64,230.50', change: '+2.45%', category: 'Crypto' },
  { name: 'Ethereum', symbol: 'ETH/USDT', price: '3,450.20', change: '-1.12%', category: 'Crypto' },
  { name: 'Amazon', symbol: 'AMZN', price: '180.25', change: '+0.95%', category: 'Equities' },
  { name: 'Meta Platforms', symbol: 'META', price: '495.10', change: '+1.85%', category: 'Equities' },
];

const getCategoryStyle = (category?: string) => {
  if (category === 'Crypto') return 'bg-gradient-to-br from-yellow-500/20 to-orange-500/20 text-yellow-300';
  return 'bg-gradient-to-br from-indigo-500/20 to-purple-500/20 text-indigo-300';
};

const TrendingUpIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
</script>
