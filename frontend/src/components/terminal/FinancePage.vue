<template>
  <div class="flex-1 flex gap-4 min-h-0 animate-fade-in">
    <div class="flex-1 glass-panel rounded-3xl p-8 flex flex-col">
      <h2 class="text-xl font-bold text-white mb-8">Portfolio Overview</h2>
      <div class="flex items-center gap-8 mb-8 pb-8 border-b border-white/5">
        <div class="flex-1">
          <div class="text-sm text-gray-400 mb-1 uppercase tracking-wider font-bold">Total Balance</div>
          <div class="text-5xl font-bold text-white tracking-tight">$42,301.54 <span class="text-sm text-emerald-400 font-normal ml-2 bg-emerald-500/10 px-2 py-1 rounded">+12.4%</span></div>
        </div>
        <div class="flex gap-3">
          <button class="flex items-center gap-2 px-8 py-4 rounded-2xl bg-white text-black font-bold hover:scale-105 transition-transform shadow-lg shadow-white/10">
            <ArrowDownLeftIcon class="w-4 h-4" /> Deposit
          </button>
          <button class="flex items-center gap-2 px-8 py-4 rounded-2xl bg-white/10 text-white font-bold hover:bg-white/20 transition-all border border-white/10">
            <ArrowUpRightIcon class="w-4 h-4" /> Withdraw
          </button>
        </div>
      </div>

      <div class="flex-1 flex gap-12 items-center">
        <div class="w-1/2 h-[300px] relative flex items-center justify-center text-gray-500">
          [Portfolio Pie Chart]
        </div>
        <div class="w-1/2 space-y-4">
          <div v-for="(item, index) in data" :key="item.name" @click="handleItemClick(item)" class="flex justify-between items-center p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors cursor-pointer group">
            <div class="flex items-center gap-3">
              <div class="w-4 h-4 rounded-full" :style="{ backgroundColor: COLORS[index] }"></div>
              <span class="font-bold text-lg">{{ item.name }}</span>
            </div>
            <div class="text-right">
              <div class="text-white font-mono font-bold">${{ item.value * 10 }}</div>
              <div class="text-xs text-gray-500">{{ ((item.value / 1100) * 100).toFixed(1) }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="w-96 glass-panel rounded-3xl p-6 flex flex-col">
      <h2 class="text-xl font-bold text-white mb-6">Recent Activity</h2>
      <div class="space-y-4 overflow-auto custom-scrollbar flex-1 pr-2">
        <div v-for="i in 6" :key="i" class="flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-colors cursor-pointer group">
          <div class="flex items-center gap-4">
            <div :class="['p-3 rounded-xl', i % 2 === 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400']">
              <component :is="i % 2 === 0 ? ArrowDownLeftIcon : ArrowUpRightIcon" class="w-4 h-4" />
            </div>
            <div>
              <div class="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">{{ i % 2 === 0 ? 'Deposit' : 'Withdrawal' }}</div>
              <div class="text-xs text-gray-500">Oct 24, 2025</div>
            </div>
          </div>
          <div class="text-right">
            <div :class="['text-sm font-mono font-bold', i % 2 === 0 ? 'text-emerald-400' : 'text-white']">
              {{ i % 2 === 0 ? '+' : '-' }}${{ (Math.random() * 1000).toFixed(2) }}
            </div>
            <div class="text-[10px] text-gray-500 bg-white/5 inline-block px-1.5 py-0.5 rounded mt-1">Success</div>
          </div>
        </div>
      </div>
      
      <div class="mt-4 pt-4 border-t border-white/5">
        <div class="p-6 rounded-3xl bg-gradient-to-br from-gray-800 to-black border border-white/10 relative overflow-hidden group cursor-pointer">
          <div class="relative z-10">
            <div class="text-xs text-gray-400 mb-2 uppercase tracking-widest font-bold">Nexus Card</div>
            <div class="text-xl font-mono text-white tracking-widest mb-4">**** **** **** 4921</div>
            <div class="flex justify-between items-end">
              <span class="text-xs text-gray-500">Exp 12/28</span>
              <span class="font-bold italic text-white/50">VISA</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineComponent, h } from 'vue';
import type { AssetInfo } from '@/types/terminal';

const ArrowDownLeftIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('line', { x1: '17', y1: '7', x2: '7', y2: '17' }), h('polyline', { points: '17 17 7 17 7 7' })]) });
const ArrowUpRightIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('line', { x1: '7', y1: '17', x2: '17', y2: '7' }), h('polyline', { points: '7 7 17 7 17 17' })]) });

const props = defineProps<{ onAssetClick?: (asset: AssetInfo) => void; }>();
const emit = defineEmits(['asset-click']);

const data = [
  { name: 'BTC', value: 400, price: '64,230.50', change: '+2.45%' },
  { name: 'ETH', value: 300, price: '3,450.20', change: '-1.12%' },
  { name: 'USDT', value: 300, price: '1.00', change: '+0.01%' },
  { name: 'SOL', value: 100, price: '148.50', change: '+5.67%' },
];
const COLORS = ['#F59E0B', '#6366F1', '#10B981', '#EC4899'];

const handleItemClick = (item: any) => {
  const assetInfo: AssetInfo = {
    name: item.name === 'BTC' ? 'Bitcoin' : item.name === 'ETH' ? 'Ethereum' : item.name === 'SOL' ? 'Solana' : 'Tether',
    symbol: item.name,
    price: item.price,
    change: item.change,
    category: 'Crypto',
    cap: 'N/A',
    vol: 'N/A'
  };
  emit('asset-click', assetInfo);
};
</script>
