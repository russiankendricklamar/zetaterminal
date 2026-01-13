<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full">
    <!-- Header -->
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4 self-start md:self-auto">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center text-lg font-bold text-emerald-300 border border-emerald-500/30">
          {{ (localSymbol || 'BT').substring(0, 2) }}
        </div>
        
        <div class="relative group" data-dropdown-asset>
          <div 
            @click="isAssetOpen = !isAssetOpen"
            class="cursor-pointer"
          >
            <div class="flex items-center gap-3 mb-1">
              <h2 class="text-2xl font-bold text-white tracking-tight group-hover:text-emerald-300 transition-colors">{{ localSymbol }}</h2>
              <div class="p-1 rounded-lg bg-white/5 group-hover:bg-emerald-500/20 transition-colors">
                <ChevronDownIcon :class="`w-3.5 h-3.5 text-gray-500 group-hover:text-emerald-300 transition-colors ${isAssetOpen ? 'rotate-180' : ''}`" />
              </div>
            </div>
            <div class="flex items-center gap-4 text-xs text-gray-400">
              <span class="font-mono text-white">$145.32</span>
              <span class="text-emerald-400 font-bold">+1.24%</span>
              <span class="px-1.5 py-0.5 rounded bg-white/5 text-[10px] uppercase">Анализ цен</span>
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
                class="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-sm text-white placeholder-gray-500 focus:border-emerald-500/50 outline-none"
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
                    ? 'bg-emerald-500/20 text-emerald-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center text-xs font-bold text-emerald-300">
                  {{ asset.symbol.substring(0, 2) }}
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
          :class="`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${section === tab.id ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-gray-500 hover:text-white hover:bg-white/5'}`"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <!-- Historical Price Table -->
      <div v-if="section === 'HP'" class="space-y-4">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-white">Исторические данные (OHLCV)</h3>
          <div class="flex gap-2">
            <button class="px-3 py-1 bg-white/10 rounded-lg text-xs hover:bg-white/20">День</button>
            <button class="px-3 py-1 text-gray-500 hover:text-white text-xs">Неделя</button>
            <button class="px-3 py-1 text-gray-500 hover:text-white text-xs">Месяц</button>
          </div>
        </div>
        <div class="overflow-x-auto rounded-xl border border-white/5">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-white/5 text-xs text-gray-400 uppercase">
                <th class="p-4 font-bold">Дата</th>
                <th class="p-4 font-bold text-right">Открытие</th>
                <th class="p-4 font-bold text-right">Максимум</th>
                <th class="p-4 font-bold text-right">Минимум</th>
                <th class="p-4 font-bold text-right">Закрытие</th>
                <th class="p-4 font-bold text-right">Объём</th>
                <th class="p-4 font-bold text-right">Изменение %</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="(row, i) in historicalData" :key="i" class="border-t border-white/5 hover:bg-white/5 transition-colors">
                <td class="p-4">{{ row.date }}</td>
                <td class="p-4 text-right">{{ row.open }}</td>
                <td class="p-4 text-right text-emerald-400/80">{{ row.high }}</td>
                <td class="p-4 text-right text-rose-400/80">{{ row.low }}</td>
                <td class="p-4 text-right font-bold text-white">{{ row.close }}</td>
                <td class="p-4 text-right text-gray-500">{{ row.vol }}</td>
                <td :class="`p-4 text-right font-bold ${parseFloat(row.change) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`">
                  {{ parseFloat(row.change) >= 0 ? '+' : '' }}{{ row.change }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Price Chart -->
      <div v-else-if="section === 'GP'" class="h-full flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-white">Технический график цены</h3>
          <div class="flex gap-2">
            <button 
              @click="showMA = !showMA"
              :class="`px-3 py-1 rounded-lg text-xs font-bold border transition-all ${showMA ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-300' : 'border-white/10 text-gray-500'}`"
            >
              MA (20)
            </button>
            <button 
              @click="showBB = !showBB"
              :class="`px-3 py-1 rounded-lg text-xs font-bold border transition-all ${showBB ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-300' : 'border-white/10 text-gray-500'}`"
            >
              Полосы Боллинджера
            </button>
          </div>
        </div>
        <div class="flex-1 bg-black/20 rounded-xl border border-white/5 p-4 min-h-[400px]">
          <v-chart class="w-full h-full" :option="priceChartOption" autoresize />
        </div>
      </div>

      <!-- Intraday Chart -->
      <div v-else-if="section === 'GIP'" class="h-full flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-white">Внутридневной график</h3>
          <div class="flex gap-2">
            <button 
              v-for="interval in intradayIntervals"
              :key="interval.value"
              @click="selectedIntradayInterval = interval.value"
              :class="`px-3 py-1 rounded-lg text-xs font-bold border transition-all ${
                selectedIntradayInterval === interval.value 
                  ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300' 
                  : 'border-white/10 text-gray-500 hover:text-white hover:bg-white/5'
              }`"
            >
              {{ interval.label }}
            </button>
          </div>
        </div>
        <div class="flex-1 bg-black/20 rounded-xl border border-white/5 p-4 min-h-[400px]">
          <v-chart class="w-full h-full" :option="intradayChartOption" autoresize />
        </div>
        <div class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-black/20 rounded-xl border border-white/5 p-4 text-center">
            <div class="text-xs text-gray-400 mb-1">Открытие</div>
            <div class="text-lg font-bold text-white font-mono">{{ intradayStats.open }}</div>
          </div>
          <div class="bg-black/20 rounded-xl border border-white/5 p-4 text-center">
            <div class="text-xs text-gray-400 mb-1">Максимум</div>
            <div class="text-lg font-bold text-emerald-400 font-mono">{{ intradayStats.high }}</div>
          </div>
          <div class="bg-black/20 rounded-xl border border-white/5 p-4 text-center">
            <div class="text-xs text-gray-400 mb-1">Минимум</div>
            <div class="text-lg font-bold text-rose-400 font-mono">{{ intradayStats.low }}</div>
          </div>
          <div class="bg-black/20 rounded-xl border border-white/5 p-4 text-center">
            <div class="text-xs text-gray-400 mb-1">Текущая</div>
            <div class="text-lg font-bold text-white font-mono">{{ intradayStats.current }}</div>
          </div>
        </div>
      </div>

      <!-- Beta Analysis -->
      <div v-else-if="section === 'BETA'" class="h-full grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 bg-black/20 rounded-xl border border-white/5 p-6 flex flex-col min-h-[400px]">
          <h3 class="text-lg font-bold text-white mb-4">Регрессионный анализ (vs SPX)</h3>
          <div class="flex-1">
            <v-chart class="w-full h-full" :option="scatterChartOption" autoresize />
          </div>
        </div>
        <div class="space-y-4">
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5 flex flex-col items-center justify-center text-center">
            <span class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Коэффициент Бета</span>
            <span class="text-5xl font-bold text-emerald-400 mb-2">1.42</span>
            <span class="text-xs text-gray-500">Высокая волатильность к рынку</span>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5 flex flex-col items-center justify-center text-center">
            <span class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Альфа (Дженсен)</span>
            <span class="text-5xl font-bold text-white mb-2">2.1%</span>
            <span class="text-xs text-gray-500">Избыточная доходность</span>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5 flex flex-col items-center justify-center text-center">
            <span class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">R-квадрат</span>
            <span class="text-5xl font-bold text-indigo-400 mb-2">0.65</span>
            <span class="text-xs text-gray-500">Сила корреляции</span>
          </div>
        </div>
      </div>

      <!-- Technical Analysis Hub -->
      <div v-else-if="section === 'TECH'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Oscillators -->
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5 col-span-1 lg:col-span-2">
          <h3 class="text-sm font-bold text-white uppercase mb-6 flex items-center gap-2">
            <ActivityIcon class="w-4 h-4 text-indigo-400" /> Осцилляторы
          </h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div v-for="osc in oscillators" :key="osc.name" class="bg-black/20 p-4 rounded-xl text-center border border-white/5">
              <div class="text-xs text-gray-500 mb-1">{{ osc.name }}</div>
              <div :class="`text-xl font-bold ${osc.color}`">{{ osc.value }}</div>
              <div :class="`text-[10px] mt-1 ${osc.color}`">{{ osc.signal }}</div>
            </div>
          </div>
        </div>

        <!-- Summary Gauge -->
        <div class="p-6 rounded-2xl bg-gradient-to-br from-indigo-900/30 to-black border border-white/5 flex flex-col items-center justify-center text-center">
          <h3 class="text-sm font-bold text-white uppercase mb-4">Общий сигнал</h3>
          <div class="relative w-32 h-32 flex items-center justify-center mb-4">
            <div class="absolute inset-0 rounded-full border-4 border-white/5 border-t-emerald-500 border-r-emerald-500 transform rotate-45"></div>
            <div class="text-2xl font-bold text-emerald-400">СИЛЬНАЯ<br/>ПОКУПКА</div>
          </div>
          <p class="text-xs text-gray-400 px-4">На основе 12 осцилляторов и 8 скользящих средних</p>
        </div>

        <!-- Moving Averages -->
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5 col-span-1 lg:col-span-3">
          <h3 class="text-sm font-bold text-white uppercase mb-4 flex items-center gap-2">
            <TrendingUpIcon class="w-4 h-4 text-indigo-400" /> Скользящие средние
          </h3>
          <div class="overflow-x-auto">
            <table class="w-full text-left">
              <thead>
                <tr class="text-xs text-gray-500 uppercase border-b border-white/10">
                  <th class="py-2">Период</th>
                  <th class="py-2">Простая MA</th>
                  <th class="py-2">Экспоненциальная MA</th>
                  <th class="py-2 text-right">Действие</th>
                </tr>
              </thead>
              <tbody class="text-sm font-mono">
                <tr v-for="ma in movingAverages" :key="ma.period" class="border-b border-white/5">
                  <td class="py-3 font-bold text-white">{{ ma.period }}</td>
                  <td class="py-3 text-gray-300">{{ ma.sma }}</td>
                  <td class="py-3 text-gray-300">{{ ma.ema }}</td>
                  <td class="py-3 text-right text-emerald-400 font-bold">{{ ma.action }}</td>
                </tr>
              </tbody>
            </table>
          </div>
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
import { LineChart, ScatterChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, GridComponent } from 'echarts/components';
import VChart from 'vue-echarts';
import { AssetInfo } from '@/types/terminal';

use([CanvasRenderer, LineChart, ScatterChart, BarChart, TitleComponent, TooltipComponent, GridComponent]);

interface Props {
  symbol: string;
  activeSection: string;
}

const props = defineProps<Props>();

const section = ref(props.activeSection || 'HP');
const localSymbol = ref(props.symbol || 'BTC/USDT');
const showMA = ref(true);
const showBB = ref(false);
const isAssetOpen = ref(false);
const assetSearchQuery = ref('');
const selectedIntradayInterval = ref('1h');

watch(() => props.activeSection, (val) => { section.value = val; });
watch(() => props.symbol, (val) => { localSymbol.value = val; });

const tabs = [
  { id: 'HP', label: 'Историческая цена', icon: 'CalendarIcon' },
  { id: 'GP', label: 'График цены', icon: 'ActivityIcon' },
  { id: 'GIP', label: 'Внутридневной график', icon: 'ClockIcon' },
  { id: 'BETA', label: 'Анализ Бета', icon: 'LayersIcon' },
  { id: 'RG', label: 'Историческая доходность', icon: 'TrendingUpIcon' },
  { id: 'TECH', label: 'Технический анализ', icon: 'BarChart2Icon' },
];

// Список всех активов из терминала (акции + криптовалюты)
const allTerminalAssets: AssetInfo[] = [
  // Криптовалюты
  { name: 'Bitcoin', symbol: 'BTC/USDT', price: '64,230.50', change: '+2.45%', cap: '1.2T', vol: '35B', category: 'Crypto' },
  { name: 'Ethereum', symbol: 'ETH/USDT', price: '3,450.20', change: '-1.12%', cap: '400B', vol: '15B', category: 'Crypto' },
  { name: 'Solana', symbol: 'SOL/USDT', price: '148.50', change: '+5.67%', cap: '65B', vol: '4B', category: 'Crypto' },
  { name: 'Ripple', symbol: 'XRP/USDT', price: '0.62', change: '-0.45%', cap: '34B', vol: '1.2B', category: 'Crypto' },
  { name: 'Cardano', symbol: 'ADA/USDT', price: '0.45', change: '+1.20%', cap: '16B', vol: '400M', category: 'Crypto' },
  { name: 'Polkadot', symbol: 'DOT/USDT', price: '7.25', change: '+3.10%', cap: '9.5B', vol: '250M', category: 'Crypto' },
  { name: 'Chainlink', symbol: 'LINK/USDT', price: '14.80', change: '+1.85%', cap: '8.2B', vol: '180M', category: 'Crypto' },
  { name: 'Polygon', symbol: 'MATIC/USDT', price: '0.85', change: '-0.30%', cap: '7.8B', vol: '150M', category: 'Crypto' },
  { name: 'Avalanche', symbol: 'AVAX/USDT', price: '38.50', change: '+4.20%', cap: '14.5B', vol: '320M', category: 'Crypto' },
  { name: 'Uniswap', symbol: 'UNI/USDT', price: '6.20', change: '+2.50%', cap: '4.6B', vol: '95M', category: 'Crypto' },
  { name: 'Litecoin', symbol: 'LTC/USDT', price: '82.40', change: '+0.95%', cap: '6.1B', vol: '280M', category: 'Crypto' },
  { name: 'Bitcoin Cash', symbol: 'BCH/USDT', price: '245.60', change: '-0.15%', cap: '4.8B', vol: '120M', category: 'Crypto' },
  { name: 'Dogecoin', symbol: 'DOGE/USDT', price: '0.15', change: '+5.25%', cap: '21.5B', vol: '1.2B', category: 'Crypto' },
  { name: 'Shiba Inu', symbol: 'SHIB/USDT', price: '0.000025', change: '+4.50%', cap: '14.8B', vol: '850M', category: 'Crypto' },
  { name: 'Binance Coin', symbol: 'BNB/USDT', price: '585.40', change: '+1.25%', cap: '88B', vol: '1.8B', category: 'Crypto' },
  
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
  
  // Валютные пары
  { name: 'Euro / USD', symbol: 'EUR/USD', price: '1.0850', change: '-0.10%', category: 'FX' },
  { name: 'USD / JPY', symbol: 'USD/JPY', price: '151.20', change: '+0.30%', category: 'FX' },
  { name: 'GBP / USD', symbol: 'GBP/USD', price: '1.2640', change: '+0.05%', category: 'FX' },
  { name: 'AUD / USD', symbol: 'AUD/USD', price: '0.6520', change: '+0.15%', category: 'FX' },
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

const selectAsset = (asset: AssetInfo) => {
  localSymbol.value = asset.symbol;
  isAssetOpen.value = false;
  assetSearchQuery.value = '';
};

const getSectionName = (sectionId: string) => {
  const section = tabs.find(t => t.id === sectionId);
  return section ? section.label : sectionId;
};

// Закрытие выпадающего меню при клике вне его
let clickOutsideHandler: ((e: MouseEvent) => void) | null = null;

onMounted(() => {
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

const historicalData = computed(() => {
  return Array.from({ length: 15 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const open = 140 + Math.random() * 10;
    const close = open + (Math.random() - 0.5) * 5;
    return {
      date: date.toLocaleDateString(),
      open: open.toFixed(2),
      high: (Math.max(open, close) + Math.random()).toFixed(2),
      low: (Math.min(open, close) - Math.random()).toFixed(2),
      close: close.toFixed(2),
      vol: (Math.random() * 10 + 5).toFixed(2) + 'M',
      change: ((close - open) / open * 100).toFixed(2)
    };
  });
});

const priceChartData = computed(() => {
  return Array.from({ length: 50 }, (_, i) => ({
    time: `Day ${i + 1}`,
    close: 140 + Math.sin(i * 0.2) * 10 + Math.random() * 5,
    ma20: 140 + Math.sin(i * 0.2) * 8,
    upperBB: 140 + Math.sin(i * 0.2) * 10 + 8,
    lowerBB: 140 + Math.sin(i * 0.2) * 10 - 8
  }));
});

const priceChartOption = computed(() => ({
  grid: { left: 40, right: 40, top: 20, bottom: 30 },
  xAxis: {
    type: 'category',
    data: priceChartData.value.map(d => d.time),
    axisLabel: { color: 'rgba(255,255,255,0.3)', fontSize: 10 },
    axisLine: { show: false },
    axisTick: { show: false }
  },
  yAxis: {
    type: 'value',
    position: 'right',
    axisLabel: { color: 'rgba(255,255,255,0.3)', fontSize: 10 },
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
  },
  series: [
    {
      type: 'line',
      data: priceChartData.value.map(d => d.close),
      smooth: true,
      symbol: 'none',
      lineStyle: { color: '#10b981', width: 2 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0)' }
          ]
        }
      }
    },
    ...(showMA.value ? [{
      type: 'line',
      data: priceChartData.value.map(d => d.ma20),
      smooth: true,
      symbol: 'none',
      lineStyle: { color: '#fbbf24', width: 2 }
    }] : []),
    ...(showBB.value ? [
      { type: 'line', data: priceChartData.value.map(d => d.upperBB), smooth: true, symbol: 'none', lineStyle: { color: '#60a5fa', width: 1, type: 'dashed' } },
      { type: 'line', data: priceChartData.value.map(d => d.lowerBB), smooth: true, symbol: 'none', lineStyle: { color: '#60a5fa', width: 1, type: 'dashed' } }
    ] : [])
  ],
  tooltip: { backgroundColor: '#18181b', borderColor: '#27272a', textStyle: { color: '#fff' } }
}));

const scatterData = computed(() => {
  return Array.from({ length: 50 }, () => [(Math.random() - 0.5) * 2, (Math.random() - 0.5) * 3]);
});

const scatterChartOption = computed(() => ({
  grid: { left: 40, right: 20, top: 20, bottom: 40 },
  xAxis: {
    type: 'value',
    name: 'Доходность SPX %',
    nameLocation: 'middle',
    nameGap: 25,
    nameTextStyle: { color: '#6b7280', fontSize: 10 },
    axisLabel: { color: '#9ca3af', fontSize: 10 },
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
  },
  yAxis: {
    type: 'value',
    name: 'Доходность актива %',
    nameLocation: 'middle',
    nameGap: 30,
    nameTextStyle: { color: '#6b7280', fontSize: 10 },
    axisLabel: { color: '#9ca3af', fontSize: 10 },
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
  },
  series: [{
    type: 'scatter',
    data: scatterData.value,
    symbolSize: 8,
    itemStyle: { color: '#34d399' }
  }],
  tooltip: { backgroundColor: '#18181b', borderColor: '#27272a', textStyle: { color: '#fff' } }
}));

const oscillators = [
  { name: 'RSI (14)', value: '64.5', signal: 'Нейтрально', color: 'text-emerald-400' },
  { name: 'Stoch (9,6)', value: '82.1', signal: 'Перекупленность', color: 'text-rose-400' },
  { name: 'CCI (20)', value: '110.2', signal: 'Покупка', color: 'text-emerald-400' },
  { name: 'MACD (12,26)', value: '2.45', signal: 'Бычий крест', color: 'text-emerald-400' },
];

const movingAverages = [
  { period: 'MA10', sma: '142.50', ema: '143.10', action: 'ПОКУПКА' },
  { period: 'MA20', sma: '138.20', ema: '139.50', action: 'ПОКУПКА' },
  { period: 'MA50', sma: '125.00', ema: '128.40', action: 'ПОКУПКА' },
  { period: 'MA200', sma: '110.10', ema: '115.20', action: 'ПОКУПКА' },
];

// Intraday intervals
const intradayIntervals = [
  { label: '1 мин', value: '1m' },
  { label: '5 мин', value: '5m' },
  { label: '15 мин', value: '15m' },
  { label: '1 час', value: '1h' },
  { label: '4 часа', value: '4h' },
];

// Intraday data
const intradayData = computed(() => {
  const now = new Date();
  const points = selectedIntradayInterval.value === '1m' ? 390 : 
                 selectedIntradayInterval.value === '5m' ? 78 :
                 selectedIntradayInterval.value === '15m' ? 26 :
                 selectedIntradayInterval.value === '1h' ? 6.5 : 1.5;
  
  const basePrice = 145.32;
  return Array.from({ length: Math.floor(points) }, (_, i) => {
    const time = new Date(now);
    if (selectedIntradayInterval.value === '1m') {
      time.setMinutes(time.getMinutes() - (Math.floor(points) - i));
    } else if (selectedIntradayInterval.value === '5m') {
      time.setMinutes(time.getMinutes() - (Math.floor(points) - i) * 5);
    } else if (selectedIntradayInterval.value === '15m') {
      time.setMinutes(time.getMinutes() - (Math.floor(points) - i) * 15);
    } else if (selectedIntradayInterval.value === '1h') {
      time.setHours(time.getHours() - (Math.floor(points) - i));
    } else {
      time.setHours(time.getHours() - (Math.floor(points) - i) * 4);
    }
    
    const price = basePrice + Math.sin(i * 0.1) * 2 + (Math.random() - 0.5) * 1.5;
    return {
      time: time.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }),
      price: price,
      volume: Math.random() * 1000000
    };
  });
});

const intradayStats = computed(() => {
  const prices = intradayData.value.map(d => d.price);
  if (prices.length === 0) {
    return {
      open: '0.00',
      high: '0.00',
      low: '0.00',
      current: '0.00'
    };
  }
  return {
    open: prices[0]?.toFixed(2) || '0.00',
    high: Math.max(...prices).toFixed(2),
    low: Math.min(...prices).toFixed(2),
    current: prices[prices.length - 1]?.toFixed(2) || '0.00'
  };
});

const intradayChartOption = computed(() => ({
  grid: { left: 50, right: 50, top: 20, bottom: 40 },
  xAxis: {
    type: 'category',
    data: intradayData.value.map(d => d.time),
    axisLabel: { 
      color: 'rgba(255,255,255,0.3)', 
      fontSize: 10,
      rotate: 45,
      interval: selectedIntradayInterval.value === '1m' ? 'auto' : 0
    },
    axisLine: { show: false },
    axisTick: { show: false }
  },
  yAxis: {
    type: 'value',
    position: 'right',
    axisLabel: { color: 'rgba(255,255,255,0.3)', fontSize: 10 },
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
  },
  series: [
    {
      type: 'line',
      data: intradayData.value.map(d => d.price),
      smooth: false,
      symbol: 'none',
      lineStyle: { color: '#10b981', width: 2 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0)' }
          ]
        }
      },
      markLine: {
        silent: true,
        data: [
          { yAxis: parseFloat(intradayStats.value.open), name: 'Открытие', lineStyle: { color: '#60a5fa', type: 'dashed', width: 1 } },
          { yAxis: parseFloat(intradayStats.value.high), name: 'Максимум', lineStyle: { color: '#10b981', type: 'dashed', width: 1 } },
          { yAxis: parseFloat(intradayStats.value.low), name: 'Минимум', lineStyle: { color: '#ef4444', type: 'dashed', width: 1 } }
        ]
      }
    }
  ],
  tooltip: { 
    backgroundColor: '#18181b', 
    borderColor: '#27272a', 
    textStyle: { color: '#fff' },
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    }
  }
}));

// Icon components
const CalendarIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>' };
const ActivityIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>' };
const ClockIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' };
const LayersIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>' };
const TrendingUpIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
const BarChart2Icon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>' };
const ChevronDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>' };
</script>
