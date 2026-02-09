<template>
  <div class="page-container custom-scrollbar">
    <!-- Header -->
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4 self-start md:self-auto">
        <div :class="`w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold shadow-lg overflow-hidden ${getCategoryStyle(selectedAssetInfo?.category || 'Equities')}`">
          <img v-if="selectedAssetInfo?.logoUrl" :src="selectedAssetInfo.logoUrl" alt="Logo" class="w-full h-full object-cover" @error="handleLogoError(selectedAssetInfo.symbol)" />
          <span v-else>{{ localSymbol.substring(0, 2) }}</span>
        </div>
        
        <div class="relative group" data-dropdown-asset>
          <div 
            @click="isAssetOpen = !isAssetOpen"
            class="cursor-pointer"
          >
            <div class="flex items-center gap-3 mb-1">
              <h2 class="text-2xl font-bold text-white tracking-tight group-hover:text-indigo-300 transition-colors">{{ localSymbol }}</h2>
              <div class="p-1 rounded-lg bg-white/5 group-hover:bg-indigo-500/20 transition-colors">
                <ChevronDownIcon :class="`w-3.5 h-3.5 text-gray-500 group-hover:text-indigo-300 transition-colors ${isAssetOpen ? 'rotate-180' : ''}`" />
              </div>
            </div>
            <div class="flex items-center gap-4 text-xs text-gray-400">
              <span class="font-mono text-white">{{ currentPrice }}</span>
              <span :class="`font-bold ${currentChange.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'}`">{{ currentChange }}</span>
              <span class="px-1.5 py-0.5 rounded bg-white/5 text-[10px] uppercase">Фундаментальный анализ</span>
            </div>
          </div>
          
          <!-- Выпадающее меню с поиском -->
          <div
            v-if="isAssetOpen"
            @click.stop
            class="absolute top-full left-0 mt-2 w-80 bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl z-50 max-h-96 flex flex-col"
          >
            <!-- Поиск -->
            <div class="p-3 border-b border-white/5">
              <input
                v-model="assetSearchQuery"
                type="text"
                placeholder="Поиск актива..."
                class="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-sm text-white placeholder-gray-500 focus:border-indigo-500/50 outline-none"
                @input="assetSearchQuery = ($event.target as HTMLInputElement).value"
              />
            </div>
            
            <!-- Список активов -->
            <div class="overflow-y-auto custom-scrollbar max-h-64">
              <button
                v-for="asset in filteredAssets"
                :key="asset.symbol"
                @click="selectAsset(asset)"
                :class="`w-full px-4 py-3 text-left text-sm transition-colors flex items-center gap-3 ${
                  localSymbol === asset.symbol 
                    ? 'bg-indigo-500/20 text-indigo-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                <div :class="`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold shadow-lg overflow-hidden ${getCategoryStyle(asset.category)}`">
                  <img v-if="asset.logoUrl" :src="asset.logoUrl" alt="Logo" class="w-full h-full object-cover" @error="handleLogoError(asset.symbol)" />
                  <span v-else>{{ asset.symbol.substring(0, 2) }}</span>
                </div>
                <div class="flex-1">
                  <div class="font-bold">{{ asset.symbol }}</div>
                  <div class="text-xs text-gray-500">{{ asset.name }}</div>
                </div>
              </button>
              <div v-if="filteredAssets.length === 0" class="px-4 py-3 text-sm text-gray-500 text-center">
                Активы не найдены
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="flex bg-black/40 rounded-xl p-1 border border-white/5 overflow-x-auto max-w-full custom-scrollbar self-stretch md:self-auto">
        <button 
          v-for="tab in tabs"
          :key="tab.id"
          @click="section = tab.id"
          :class="`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${section === tab.id ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' : 'text-gray-500 hover:text-white hover:bg-white/5'}`"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <!-- Earnings Estimates -->
      <div v-if="section === 'EE'" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-4">Консенсус-прогнозы EPS</h3>
            <div class="h-64">
              <v-chart class="w-full h-full" :option="epsChartOption" autoresize />
            </div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-4">Прогноз выручки (млрд)</h3>
            <div class="h-64">
              <v-chart class="w-full h-full" :option="revenueChartOption" autoresize />
            </div>
          </div>
        </div>
      </div>

      <!-- Earnings Summary -->
      <div v-else-if="section === 'ERN'" class="p-6 rounded-2xl bg-white/5 border border-white/5">
        <h3 class="text-lg font-bold text-white mb-6">История прибылей: Факт vs Консенсус</h3>
        <table class="w-full text-left">
          <thead>
            <tr class="text-xs text-gray-500 uppercase border-b border-white/10">
              <th class="py-3 px-4">Период</th>
              <th class="py-3 px-4">Прогноз</th>
              <th class="py-3 px-4">Факт</th>
              <th class="py-3 px-4">Сюрприз</th>
              <th class="py-3 px-4 text-right">Реакция цены</th>
            </tr>
          </thead>
          <tbody class="text-sm">
            <tr v-for="(h, i) in earningsHistory" :key="i" class="border-b border-white/5 hover:bg-white/5">
              <td class="py-4 px-4 font-bold text-white">{{ h.q }}</td>
              <td class="py-4 px-4 text-gray-400">${{ h.est }}</td>
              <td class="py-4 px-4 text-white">${{ h.act }}</td>
              <td :class="`py-4 px-4 font-bold ${h.surprise.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'}`">{{ h.surprise }}</td>
              <td class="py-4 px-4 text-right">
                <span :class="`px-2 py-1 rounded text-xs ${h.surprise.startsWith('+') ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`">
                  {{ h.surprise.startsWith('+') ? '+2.4%' : '-1.1%' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Analyst Recommendations -->
      <div v-else-if="section === 'ANR'" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5 flex flex-col items-center justify-center">
          <h3 class="text-lg font-bold text-white mb-2">Консенсус-рейтинг</h3>
          <div class="text-5xl font-bold text-emerald-400 mb-2">4.8</div>
          <div class="flex gap-1 mb-6">
            <span v-for="s in 5" :key="s" :class="`w-5 h-5 ${s <= 4 ? 'text-yellow-400' : 'text-gray-600'}`">★</span>
          </div>
          <div class="h-64 w-full">
            <v-chart class="w-full h-full" :option="analystPieOption" autoresize />
          </div>
        </div>

        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-lg font-bold text-white mb-6">Целевые цены аналитиков</h3>
          <div class="space-y-6">
            <div v-for="(analyst, i) in analystTargets" :key="i" class="flex justify-between items-center p-4 bg-white/5 rounded-xl border border-white/5">
              <span class="text-gray-400 font-medium">{{ analyst.name }}</span>
              <div class="flex gap-4 items-center">
                <span :class="`font-bold px-2 py-0.5 rounded text-xs ${analyst.rating === 'BUY' || analyst.rating === 'OW' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-yellow-500/10 text-yellow-400'}`">{{ getRatingName(analyst.rating) }}</span>
                <span class="text-white font-mono font-bold">${{ analyst.target }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Valuation Ratios -->
      <div v-else-if="section === 'RV'" class="p-6 rounded-2xl bg-white/5 border border-white/5">
        <h3 class="text-lg font-bold text-white mb-6">Относительная оценка</h3>
        <table class="w-full text-left">
          <thead>
            <tr class="text-xs text-gray-500 uppercase border-b border-white/10">
              <th class="py-3 px-4">Тикер</th>
              <th class="py-3 px-4">P/E (TTM)</th>
              <th class="py-3 px-4">P/B</th>
              <th class="py-3 px-4">EV/EBITDA</th>
              <th class="py-3 px-4">ROE</th>
            </tr>
          </thead>
          <tbody class="text-sm font-mono">
            <tr v-for="(p, i) in valuationPeers" :key="i" :class="`border-b border-white/5 ${p.t === localSymbol ? 'bg-indigo-500/10' : ''}`">
              <td :class="`py-4 px-4 font-bold ${p.t === localSymbol ? 'text-indigo-300' : 'text-white'}`">{{ p.t }}</td>
              <td class="py-4 px-4 text-gray-300">{{ p.pe }}x</td>
              <td class="py-4 px-4 text-gray-300">{{ p.pb }}x</td>
              <td class="py-4 px-4 text-gray-300">{{ p.ev }}x</td>
              <td class="py-4 px-4 text-emerald-400 font-bold">{{ p.roe }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Dividends -->
      <div v-else-if="section === 'DVD'" class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5 text-center">
          <div class="text-sm text-gray-400 uppercase font-bold mb-2">Дивидендная доходность</div>
          <div class="text-3xl font-bold text-white">0.04%</div>
          <div class="text-xs text-gray-500 mt-1">Годовая</div>
        </div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5 text-center">
          <div class="text-sm text-gray-400 uppercase font-bold mb-2">Дата выплаты</div>
          <div class="text-3xl font-bold text-white">28 дек</div>
          <div class="text-xs text-gray-500 mt-1">2025</div>
        </div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5 text-center">
          <div class="text-sm text-gray-400 uppercase font-bold mb-2">Ex-Dividend</div>
          <div class="text-3xl font-bold text-white">04 дек</div>
          <div class="text-xs text-gray-500 mt-1">Подтверждено</div>
        </div>
      </div>

      <!-- Default placeholder -->
      <div v-else class="flex items-center justify-center h-full">
        <div class="text-center">
          <h3 class="text-xl font-bold text-white mb-2">{{ getSectionName(section) }}</h3>
          <p class="text-gray-400">Содержимое появится в ближайшее время</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, PieChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components';
import VChart from 'vue-echarts';
import { AssetInfo } from '@/types/terminal';

use([CanvasRenderer, BarChart, PieChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent]);

interface Props {
  symbol: string;
  activeSection: string;
}

const props = defineProps<Props>();

const section = ref(props.activeSection);
const localSymbol = ref(props.symbol);
const isAssetOpen = ref(false);
const assetSearchQuery = ref('');
const selectedAssetInfo = ref<AssetInfo | null>(null);

watch(() => props.activeSection, (val) => {
  section.value = val;
});

watch(() => props.symbol, (val) => {
  localSymbol.value = val;
  updateSelectedAsset();
});

const tabs = [
  { id: 'EE', label: 'Прогнозы', icon: 'TrendingUpIcon' },
  { id: 'ERN', label: 'Прибыли', icon: 'DollarSignIcon' },
  { id: 'ANR', label: 'Рекомендации', icon: 'UsersIcon' },
  { id: 'INT', label: 'Аналитика', icon: 'FileTextIcon' },
  { id: 'RV', label: 'Оценка', icon: 'ScaleIcon' },
  { id: 'DVD', label: 'Дивиденды', icon: 'CalendarIcon' },
  { id: 'CAST', label: 'Структура капитала', icon: 'LayersIcon' },
];

// Список всех активов из терминала
const allTerminalAssets: AssetInfo[] = [
  // Криптовалюты
  { name: 'Bitcoin', symbol: 'BTC/USDT', price: '64,230.50', change: '+2.45%', cap: '1.2T', vol: '35B', category: 'Crypto' },
  { name: 'Ethereum', symbol: 'ETH/USDT', price: '3,450.20', change: '-1.12%', cap: '400B', vol: '15B', category: 'Crypto' },
  { name: 'Solana', symbol: 'SOL/USDT', price: '148.50', change: '+5.67%', cap: '65B', vol: '4B', category: 'Crypto' },
  
  // Акции - топ
  { name: 'Apple Inc.', symbol: 'AAPL', price: '173.50', change: '+1.20%', category: 'Equities', vol: '55M', cap: '2.7T' },
  { name: 'NVIDIA Corp', symbol: 'NVDA', price: '892.10', change: '+4.25%', category: 'Equities', vol: '42M', cap: '2.2T' },
  { name: 'Microsoft', symbol: 'MSFT', price: '420.55', change: '-0.45%', category: 'Equities', vol: '22M', cap: '3.1T' },
  { name: 'Tesla Inc', symbol: 'TSLA', price: '175.30', change: '+2.10%', category: 'Equities', vol: '95M', cap: '550B' },
  { name: 'Amazon', symbol: 'AMZN', price: '180.25', change: '+0.95%', category: 'Equities', vol: '38M', cap: '1.8T' },
  { name: 'Meta Platforms', symbol: 'META', price: '495.10', change: '+1.85%', category: 'Equities', vol: '18M', cap: '1.2T' },
  { name: 'Google', symbol: 'GOOGL', price: '156.40', change: '-0.20%', category: 'Equities', vol: '24M', cap: '1.9T' },
  { name: 'AMD', symbol: 'AMD', price: '142.50', change: '+3.15%', category: 'Equities', vol: '65M', cap: '230B' },
  { name: 'Netflix', symbol: 'NFLX', price: '485.20', change: '+2.30%', category: 'Equities', vol: '8M', cap: '215B' },
  { name: 'JPMorgan Chase', symbol: 'JPM', price: '185.40', change: '+0.55%', category: 'Equities', vol: '15M', cap: '540B' },
  { name: 'Bank of America', symbol: 'BAC', price: '38.50', change: '+0.40%', category: 'Equities', vol: '45M', cap: '305B' },
  { name: 'Walmart', symbol: 'WMT', price: '165.30', change: '+0.45%', category: 'Equities', vol: '8M', cap: '445B' },
  { name: 'Johnson & Johnson', symbol: 'JNJ', price: '158.40', change: '+0.30%', category: 'Equities', vol: '9M', cap: '420B' },
  { name: 'Exxon Mobil', symbol: 'XOM', price: '118.50', change: '+0.85%', category: 'Equities', vol: '22M', cap: '495B' },
  { name: 'Boeing', symbol: 'BA', price: '185.40', change: '+1.85%', category: 'Equities', vol: '8M', cap: '115B' },
  
  // Российские акции
  { name: 'Сбербанк', symbol: 'SBER', price: '285.40', change: '+1.85%', category: 'Equities', vol: '125M', cap: '6.5T' },
  { name: 'Газпром', symbol: 'GAZP', price: '168.50', change: '+0.95%', category: 'Equities', vol: '85M', cap: '4.2T' },
  { name: 'Лукойл', symbol: 'LKOH', price: '7850.60', change: '+1.25%', category: 'Equities', vol: '1.2M', cap: '8.1T' },
  { name: 'Яндекс', symbol: 'YNDX', price: '2840.50', change: '+1.45%', category: 'Equities', vol: '2.5M', cap: '1.1T' },
];

const filteredAssets = computed(() => {
  if (!assetSearchQuery.value) {
    return allTerminalAssets;
  }
  const query = assetSearchQuery.value.toLowerCase();
  return allTerminalAssets.filter(asset => 
    asset.symbol.toLowerCase().includes(query) || 
    asset.name.toLowerCase().includes(query)
  );
});

const currentPrice = computed(() => {
  return selectedAssetInfo.value?.price || '0.00';
});

const currentChange = computed(() => {
  return selectedAssetInfo.value?.change || '+0.00%';
});

const selectAsset = (asset: AssetInfo) => {
  localSymbol.value = asset.symbol;
  selectedAssetInfo.value = asset;
  isAssetOpen.value = false;
  assetSearchQuery.value = '';
};

const updateSelectedAsset = () => {
  selectedAssetInfo.value = allTerminalAssets.find(a => a.symbol === localSymbol.value) || null;
};

const getCategoryStyle = (category?: string) => {
  const styles: Record<string, string> = {
    'Crypto': 'bg-gradient-to-br from-yellow-500/20 to-orange-500/20 text-yellow-300 border border-yellow-500/30',
    'Equities': 'bg-gradient-to-br from-indigo-500/20 to-purple-500/20 text-indigo-300 border border-indigo-500/30',
    'FX': 'bg-gradient-to-br from-blue-500/20 to-cyan-500/20 text-blue-300 border border-blue-500/30',
  };
  return styles[category || 'Equities'] || styles['Equities'];
};

const getRatingName = (rating: string) => {
  const names: Record<string, string> = {
    'BUY': 'ПОКУПАТЬ',
    'OW': 'ПРЕВЫШЕНИЕ',
    'HOLD': 'ДЕРЖАТЬ',
    'UW': 'НЕДООЦЕНКА',
    'SELL': 'ПРОДАВАТЬ',
  };
  return names[rating] || rating;
};

const getSectionName = (sectionId: string) => {
  const section = tabs.find(t => t.id === sectionId);
  return section ? section.label : sectionId;
};

const logoErrors = ref(new Set<string>());

const handleLogoError = (symbol: string) => {
  logoErrors.value.add(symbol);
};

// Загрузка логотипов
const loadLogos = () => {
  allTerminalAssets.forEach(asset => {
    if (asset.category === 'Equities' && !logoErrors.value.has(asset.symbol)) {
      const domainMap: Record<string, string> = {
        'AAPL': 'apple.com', 'MSFT': 'microsoft.com', 'GOOGL': 'google.com', 'AMZN': 'amazon.com', 'META': 'meta.com',
        'NVDA': 'nvidia.com', 'TSLA': 'tesla.com', 'NFLX': 'netflix.com', 'AMD': 'amd.com', 'JPM': 'jpmorganchase.com',
        'BAC': 'bankofamerica.com', 'WMT': 'walmart.com', 'JNJ': 'jnj.com', 'XOM': 'exxonmobil.com', 'BA': 'boeing.com',
        'SBER': 'sber.ru', 'GAZP': 'gazprom.ru', 'LKOH': 'lukoil.ru', 'YNDX': 'yandex.ru',
      };
      const domain = domainMap[asset.symbol] || `${asset.name.toLowerCase().replace(/[^a-z0-9]/g, '')}.com`;
      asset.logoUrl = `https://logo.clearbit.com/${domain}?size=40&format=png`;
    }
  });
};

// Закрытие выпадающего меню при клике вне его
let clickOutsideHandler: ((e: MouseEvent) => void) | null = null;

onMounted(() => {
  updateSelectedAsset();
  loadLogos();
  clickOutsideHandler = (e: MouseEvent) => {
    const target = e.target as HTMLElement;
    if (!target.closest('[data-dropdown-asset]')) {
      isAssetOpen.value = false;
    }
  };
  document.addEventListener('click', clickOutsideHandler);
});

onBeforeUnmount(() => {
  if (clickOutsideHandler) {
    document.removeEventListener('click', clickOutsideHandler);
  }
});

const estimatesData = [
  { period: 'Q3 2025', eps: 2.45, rev: 45.2 },
  { period: 'Q4 2025', eps: 2.80, rev: 48.5 },
  { period: 'Q1 2026', eps: 3.10, rev: 52.1 },
  { period: 'Q2 2026', eps: 3.35, rev: 55.8 },
];

const earningsHistory = [
  { q: 'Q2 25', est: 2.10, act: 2.25, surprise: '+7.1%' },
  { q: 'Q1 25', est: 1.95, act: 2.05, surprise: '+5.1%' },
  { q: 'Q4 24', est: 1.80, act: 1.88, surprise: '+4.4%' },
  { q: 'Q3 24', est: 1.65, act: 1.60, surprise: '-3.0%' },
];

const analystTargets = [
  { name: 'Goldman Sachs', rating: 'BUY', target: '1,200' },
  { name: 'Morgan Stanley', rating: 'OW', target: '1,150' },
  { name: 'JP Morgan', rating: 'HOLD', target: '980' },
];

const valuationPeers = computed(() => [
  { t: localSymbol.value, pe: 35.2, pb: 12.4, ev: 28.5, roe: '45%' },
  { t: 'AMD', pe: 42.1, pb: 8.2, ev: 30.1, roe: '12%' },
  { t: 'INTC', pe: 85.4, pb: 1.1, ev: 12.5, roe: '5%' },
  { t: 'TSM', pe: 22.8, pb: 5.6, ev: 18.2, roe: '28%' },
]);

const epsChartOption = computed(() => ({
  grid: { left: 40, right: 20, top: 20, bottom: 30 },
  xAxis: {
    type: 'category',
    data: estimatesData.map(d => d.period),
    axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 10 },
    axisLine: { show: false },
    axisTick: { show: false }
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 10 },
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
  },
  series: [{
    type: 'bar',
    data: estimatesData.map(d => d.eps),
    itemStyle: { color: '#6366f1', borderRadius: [4, 4, 0, 0] },
    barWidth: 40
  }],
  tooltip: { backgroundColor: '#18181b', borderColor: '#27272a', textStyle: { color: '#fff' } }
}));

const revenueChartOption = computed(() => ({
  grid: { left: 40, right: 20, top: 20, bottom: 30 },
  xAxis: {
    type: 'category',
    data: estimatesData.map(d => d.period),
    axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 10 },
    axisLine: { show: false },
    axisTick: { show: false }
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 10 },
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
  },
  series: [{
    type: 'bar',
    data: estimatesData.map(d => d.rev),
    itemStyle: { color: '#10b981', borderRadius: [4, 4, 0, 0] },
    barWidth: 40
  }],
  tooltip: { backgroundColor: '#18181b', borderColor: '#27272a', textStyle: { color: '#fff' } }
}));

const analystPieOption = computed(() => ({
  series: [{
    type: 'pie',
    radius: ['50%', '70%'],
    center: ['50%', '50%'],
    data: [
      { value: 35, name: 'Покупать', itemStyle: { color: '#10b981' } },
      { value: 10, name: 'Держать', itemStyle: { color: '#fbbf24' } },
      { value: 2, name: 'Продавать', itemStyle: { color: '#f43f5e' } }
    ],
    label: { show: false },
    emphasis: { scale: true, scaleSize: 5 }
  }],
  tooltip: { backgroundColor: '#18181b', borderColor: '#27272a', textStyle: { color: '#fff' } },
  legend: { bottom: 0, textStyle: { color: '#9ca3af' } }
}));

// Icon components
const ChevronDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>' };
</script>
