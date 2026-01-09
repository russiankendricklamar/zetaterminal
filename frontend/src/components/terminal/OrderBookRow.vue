<template>
  <div class="relative flex justify-between items-center text-[9px] px-2 hover:bg-white/5 cursor-pointer group transition-colors flex-shrink-0" style="height: calc(100% / 12);">
    <div 
      :class="`absolute top-0 right-0 h-full opacity-10 ${colorClass}`" 
      :style="{ width: barWidth }"
    />
    <span :class="`relative z-10 font-mono ${textClass} font-medium`">
      {{ item.price.toFixed(0) }}
    </span>
    <span class="relative z-10 font-mono text-gray-400 text-right opacity-80 group-hover:opacity-100">
      {{ item.amount.toFixed(3) }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { OrderBookItem } from '@/types/terminal';

interface Props {
  item: OrderBookItem;
  type: 'bid' | 'ask';
}

const props = defineProps<Props>();

const barWidth = computed(() => `${(props.item.amount * 20)}%`);
const colorClass = computed(() => props.type === 'bid' ? 'bg-emerald-500' : 'bg-rose-500');
const textClass = computed(() => props.type === 'bid' ? 'text-emerald-400' : 'text-rose-400');
</script>
