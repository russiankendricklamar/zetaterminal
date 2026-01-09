<template>
  <div class="flex flex-col h-full bg-transparent w-full">
    <div class="px-3 py-2 border-b border-white/5 flex justify-between items-center">
      <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Стакан</span>
      <div class="flex gap-0.5">
        <div class="w-1 h-1 rounded-full bg-gray-600"></div>
        <div class="w-1 h-1 rounded-full bg-gray-600"></div>
        <div class="w-1 h-1 rounded-full bg-gray-600"></div>
      </div>
    </div>
    
    <div class="flex-1 flex flex-col overflow-hidden relative min-h-0">
      <div class="flex justify-between px-2 py-1 text-[8px] text-gray-500 uppercase font-bold tracking-wider flex-shrink-0">
        <span>Цена</span>
        <span>Объём</span>
      </div>

      <!-- Asks (Sells) -->
      <div class="flex-1 overflow-hidden flex flex-col min-h-0 justify-end">
        <OrderBookRow
          v-for="(ask, i) in reversedAsks"
          :key="i"
          :item="ask"
          type="ask"
        />
      </div>

      <!-- Current Price Banner -->
      <div class="py-2 px-2 border-y border-white/5 bg-white/5 backdrop-blur-sm flex items-center justify-between flex-shrink-0">
        <div class="flex flex-col">
          <span class="text-sm font-bold text-white font-mono tracking-tight">
            {{ currentPrice.toFixed(2) }}
          </span>
          <span class="text-[8px] text-gray-500">≈ ${{ currentPrice.toFixed(2) }}</span>
        </div>
        <div class="text-[8px] font-mono text-emerald-400 flex items-center gap-0.5">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
        </div>
      </div>

      <!-- Bids (Buys) -->
      <div class="flex-1 overflow-hidden flex flex-col min-h-0">
        <OrderBookRow
          v-for="(bid, i) in displayedBids"
          :key="i"
          :item="bid"
          type="bid"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { OrderBookItem } from '@/types/terminal';
import OrderBookRow from './OrderBookRow.vue';

interface Props {
  bids: OrderBookItem[];
  asks: OrderBookItem[];
  currentPrice: number;
}

const props = defineProps<Props>();

// Увеличиваем количество отображаемых ордеров для заполнения высоты
// Количество ордеров для равномерного заполнения (примерно 12-15 на каждую секцию)
const displayedBids = computed(() => props.bids.slice(0, 12));
const reversedAsks = computed(() => [...props.asks.slice(0, 12)].reverse());
</script>
