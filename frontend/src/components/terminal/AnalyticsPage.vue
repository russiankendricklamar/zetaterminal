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


    <!-- Assets and Instruments Dropdowns for Quantitative Analytics -->
    <div v-if="activeTab === 'Quant'" class="mb-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Assets Dropdown -->
      <div class="relative" data-dropdown-assets>
        <button
          @click="isAssetsOpen = !isAssetsOpen"
          class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl hover:border-blue-500/50 transition-all flex items-center justify-between text-left group"
        >
          <div class="flex items-center gap-3">
            <div class="p-2 rounded-lg bg-blue-500/20 text-blue-400">
              <ActivityIcon class="w-4 h-4" />
            </div>
            <div>
              <div class="text-sm font-bold text-white">Активы</div>
              <div class="text-xs text-gray-400">{{ selectedAsset || 'Выберите актив' }}</div>
            </div>
          </div>
          <ChevronDownIcon :class="`w-4 h-4 text-gray-400 transition-transform ${isAssetsOpen ? 'rotate-180' : ''}`" />
        </button>
        <div
          v-if="isAssetsOpen"
          @click.stop
          class="absolute top-full left-0 mt-2 w-full bg-black/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl z-50 max-h-[500px] overflow-hidden flex flex-col"
        >
          <!-- Search Input -->
          <div class="p-3 border-b border-white/10 bg-white/5">
            <div class="relative">
              <SearchIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                v-model="assetSearchQuery"
                @click.stop
                type="text"
                placeholder="Поиск актива..."
                class="w-full pl-10 pr-3 py-2 bg-black/40 border border-white/10 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/50 transition-colors"
              />
            </div>
          </div>
          
          <!-- Assets List -->
          <div class="overflow-y-auto custom-scrollbar flex-1">
            <div class="p-2">
              <template v-for="(assets, type) in filteredAssetsByType" :key="type">
                <div v-if="assets.length > 0" class="mb-4">
                  <!-- Category Header -->
                  <div class="px-3 py-2 text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">
                    {{ assetTypeLabels[type as keyof typeof assetTypeLabels] }}
                  </div>
                  
                  <!-- Assets in Category -->
                  <div
                    v-for="asset in assets"
                    :key="asset.symbol"
                    @click="selectAsset(asset.symbol)"
                    :class="`flex items-center justify-between gap-3 px-4 py-2.5 rounded-lg text-sm transition-colors cursor-pointer ${
                      selectedAsset === asset.symbol
                        ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                        : 'text-gray-300 hover:bg-white/5 hover:text-white border border-transparent'
                    }`"
                  >
                    <div class="flex-1 min-w-0">
                      <div class="font-medium truncate">{{ asset.name }}</div>
                    </div>
                    <span :class="`text-xs font-mono px-2 py-0.5 rounded ${
                      selectedAsset === asset.symbol
                        ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                        : 'bg-white/5 text-gray-500 border border-white/5'
                    }`">
                      {{ asset.symbol }}
                    </span>
                  </div>
                </div>
              </template>
              
              <!-- No Results -->
              <div v-if="Object.values(filteredAssetsByType).every(arr => arr.length === 0)" class="py-8 text-center text-gray-500 text-sm">
                Активы не найдены
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Instruments Dropdown -->
      <div class="relative" data-dropdown-instruments>
        <button
          @click="isInstrumentsOpen = !isInstrumentsOpen"
          class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl hover:border-emerald-500/50 transition-all flex items-center justify-between text-left group"
        >
          <div class="flex items-center gap-3">
            <div class="p-2 rounded-lg bg-emerald-500/20 text-emerald-400">
              <LayoutTemplateIcon class="w-4 h-4" />
            </div>
            <div>
              <div class="text-sm font-bold text-white">Инструменты</div>
              <div class="text-xs text-gray-400">{{ selectedInstrument?.label || 'Выберите инструмент' }}</div>
            </div>
          </div>
          <ChevronDownIcon :class="`w-4 h-4 text-gray-400 transition-transform ${isInstrumentsOpen ? 'rotate-180' : ''}`" />
        </button>
        <div
          v-if="isInstrumentsOpen"
          @click.stop
          class="absolute top-full left-0 mt-2 w-full bg-black/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl z-50 max-h-96 overflow-y-auto custom-scrollbar"
        >
          <div class="p-2">
            <div
              v-for="tool in quantitativeTools"
              :key="tool.id"
              @click="selectInstrument(tool)"
              :class="`flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-colors cursor-pointer ${
                selectedInstrument?.id === tool.id
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : 'text-gray-300 hover:bg-white/5 hover:text-white border border-transparent'
              }`"
            >
              <div :class="`p-1.5 rounded-lg ${selectedInstrument?.id === tool.id ? 'bg-emerald-500/30' : 'bg-white/5'}`">
                <component :is="tool.icon" :class="`w-4 h-4 ${selectedInstrument?.id === tool.id ? 'text-emerald-300' : 'text-gray-400'}`" />
              </div>
              <div class="flex-1">
                <div class="font-medium">{{ tool.label }}</div>
                <div class="text-xs text-gray-500">{{ tool.description }}</div>
              </div>
              <span :class="`text-xs font-mono px-2 py-0.5 rounded ${
                selectedInstrument?.id === tool.id
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : 'bg-white/5 text-gray-500 border border-white/5'
              }`">
                {{ tool.code }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Chart Area -->
    <div class="flex-1 min-h-[400px] p-6 rounded-2xl bg-black/20 border border-white/5 relative flex flex-col lg:flex-row gap-6">
      
      <!-- Quantitative Analysis Tool Content -->
      <div v-if="activeTab === 'Quant' && selectedInstrument" class="w-full flex flex-col">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-bold text-white flex items-center gap-2">
            <component :is="selectedInstrument.icon" class="w-5 h-5 text-emerald-400" />
            <span>{{ selectedInstrument.label }}</span>
          </h3>
          <span class="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">
            {{ selectedInstrument.code }}
          </span>
        </div>
        
        <!-- Volatility Surface -->
        <div v-if="selectedInstrument.id === 'volatility-surface'" class="flex-1 flex flex-col gap-4">
          <div v-if="!selectedAsset" class="flex-1 flex items-center justify-center">
            <div class="text-center">
              <ActivityIcon class="w-16 h-16 text-gray-500 mx-auto mb-4 opacity-50" />
              <p class="text-gray-400">Выберите актив для анализа</p>
            </div>
          </div>
          <div v-else class="flex-1 flex flex-col gap-4">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
              <div class="p-4 rounded-xl bg-white/5 border border-white/10">
                <div class="text-xs text-gray-400 mb-2">Актив</div>
                <div class="text-lg font-bold text-white">{{ selectedAsset }}</div>
              </div>
              <div class="p-4 rounded-xl bg-white/5 border border-white/10">
                <div class="text-xs text-gray-400 mb-2">Текущая волатильность</div>
                <div class="text-2xl font-bold text-emerald-400">14.2%</div>
              </div>
            </div>
            <div class="flex-1 min-h-[300px] bg-black/20 rounded-xl p-4">
              <v-chart class="w-full h-full" :option="volatilitySurfaceOption" autoresize />
            </div>
          </div>
        </div>

        <!-- Volatility Surface (by Greeks) -->
        <div v-else-if="selectedInstrument.id === 'volatility-surface-greeks'" class="flex-1 flex flex-col gap-4">
          <div v-if="!selectedAsset" class="flex-1 flex items-center justify-center">
            <div class="text-center">
              <ActivityIcon class="w-16 h-16 text-gray-500 mx-auto mb-4 opacity-50" />
              <p class="text-gray-400">Выберите актив для анализа</p>
            </div>
          </div>
          <div v-else class="flex-1 flex flex-col gap-4">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
              <div class="p-4 rounded-xl bg-white/5 border border-white/10">
                <div class="text-xs text-gray-400 mb-2">Актив</div>
                <div class="text-lg font-bold text-white">{{ selectedAsset }}</div>
              </div>
              <div class="p-4 rounded-xl bg-white/5 border border-white/10">
                <div class="text-xs text-gray-400 mb-2">Текущая волатильность</div>
                <div class="text-2xl font-bold text-emerald-400">14.2%</div>
              </div>
            </div>
            <div class="flex-1 min-h-[300px] bg-black/20 rounded-xl p-4">
              <v-chart class="w-full h-full" :option="volatilitySurfaceOption" autoresize />
            </div>
          </div>
        </div>

        <!-- Other Tools Placeholder -->
        <div v-else class="flex-1 flex items-center justify-center">
          <div class="text-center">
            <component :is="selectedInstrument.icon" class="w-16 h-16 text-emerald-400 mx-auto mb-4 opacity-50" />
            <h4 class="text-xl font-bold text-white mb-2">{{ selectedInstrument.label }}</h4>
            <p class="text-gray-400">{{ selectedInstrument.description }}</p>
            <p v-if="!selectedAsset" class="text-xs text-gray-500 mt-4">Выберите актив для анализа</p>
            <div v-else class="mt-4 p-4 rounded-xl bg-white/5 border border-white/10 inline-block">
              <div class="text-xs text-gray-400 mb-1">Актив</div>
              <div class="text-lg font-bold text-white">{{ selectedAsset }}</div>
            </div>
          </div>
        </div>

      </div>

      <!-- Default Chart Container (for AI and Finance tabs) -->
      <div v-else :class="`flex-1 flex flex-col ${activeTab === 'Finance' ? 'lg:w-2/3' : 'w-full'}`">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-bold text-white flex items-center gap-2">
            <BarChart2Icon class="w-4 h-4 text-gray-400" />
            <span v-if="activeTab === 'AI'">Модель прогнозирования тренда (Gemini-3 Pro)</span>
            <span v-else-if="activeTab === 'Quant'">Выберите инструмент количественного анализа</span>
            <span v-else>История производительности портфеля</span>
          </h3>
          <div v-if="activeTab === 'Quant' && !selectedInstrument" class="flex gap-2">
            <span class="text-xs text-gray-500">Выберите инструмент из меню выше</span>
          </div>
          <span v-if="activeTab === 'Finance'" class="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">+15.4% За всё время</span>
        </div>
        
        <div v-if="activeTab !== 'Quant' || !selectedInstrument" class="flex-1 min-h-[300px]">
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
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, PieChart, HeatmapChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent, VisualMapComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, LineChart, PieChart, HeatmapChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, VisualMapComponent]);

interface Props {
  activeSection?: 'AI' | 'Quant' | 'Finance';
}

const props = withDefaults(defineProps<Props>(), {
  activeSection: 'AI'
});

const activeTab = ref<'AI' | 'Quant' | 'Finance'>(props.activeSection);
const isAssetsOpen = ref(false);
const isInstrumentsOpen = ref(false);
const selectedAsset = ref<string>('');
const selectedInstrument = ref<any>(null);
const assetSearchQuery = ref('');

// Available assets grouped by type
const assetsByType = {
  crypto: [
    { symbol: 'BTC/USDT', name: 'Bitcoin' },
    { symbol: 'ETH/USDT', name: 'Ethereum' },
    { symbol: 'SOL/USDT', name: 'Solana' },
    { symbol: 'XRP/USDT', name: 'Ripple' },
    { symbol: 'BNB/USDT', name: 'Binance Coin' },
    { symbol: 'ADA/USDT', name: 'Cardano' },
  ],
  stocks: [
    { symbol: 'AAPL', name: 'Apple Inc.' },
    { symbol: 'TSLA', name: 'Tesla Inc.' },
    { symbol: 'NVDA', name: 'NVIDIA Corporation' },
    { symbol: 'AMD', name: 'Advanced Micro Devices' },
    { symbol: 'MSFT', name: 'Microsoft Corporation' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.' },
    { symbol: 'AMZN', name: 'Amazon.com Inc.' },
    { symbol: 'META', name: 'Meta Platforms Inc.' },
  ],
  forex: [
    { symbol: 'EUR/USD', name: 'Euro / US Dollar' },
    { symbol: 'GBP/USD', name: 'British Pound / US Dollar' },
    { symbol: 'USD/JPY', name: 'US Dollar / Japanese Yen' },
    { symbol: 'AUD/USD', name: 'Australian Dollar / US Dollar' },
    { symbol: 'USD/CHF', name: 'US Dollar / Swiss Franc' },
    { symbol: 'USD/CAD', name: 'US Dollar / Canadian Dollar' },
  ],
  commodities: [
    { symbol: 'GOLD', name: 'Gold' },
    { symbol: 'SILVER', name: 'Silver' },
    { symbol: 'OIL', name: 'Crude Oil' },
    { symbol: 'COPPER', name: 'Copper' },
  ],
  indices: [
    { symbol: 'SPX', name: 'S&P 500' },
    { symbol: 'DJI', name: 'Dow Jones Industrial Average' },
    { symbol: 'IXIC', name: 'NASDAQ Composite' },
    { symbol: 'RUT', name: 'Russell 2000' },
  ],
};

const assetTypeLabels = {
  crypto: 'Криптовалюты',
  stocks: 'Акции',
  forex: 'Валютные пары',
  commodities: 'Сырьё',
  indices: 'Индексы',
};

// Computed filtered assets
const filteredAssetsByType = computed(() => {
  const query = assetSearchQuery.value.toLowerCase().trim();
  if (!query) {
    return assetsByType;
  }
  
  const filtered: typeof assetsByType = {
    crypto: [],
    stocks: [],
    forex: [],
    commodities: [],
    indices: [],
  };
  
  Object.keys(assetsByType).forEach((type) => {
    filtered[type as keyof typeof assetsByType] = assetsByType[type as keyof typeof assetsByType].filter(
      (asset) => 
        asset.symbol.toLowerCase().includes(query) || 
        asset.name.toLowerCase().includes(query)
    );
  });
  
  return filtered;
});

// All available assets for simple list (legacy)
const availableAssets = computed(() => {
  return Object.values(assetsByType).flat().map(a => a.symbol);
});

watch(() => props.activeSection, (val) => {
  activeTab.value = val;
});

// Quantitative analysis tools list
const quantitativeTools = [
  { 
    id: 'volatility-surface', 
    label: 'Поверхность волатильности', 
    code: 'VOL', 
    description: '3D визуализация волатильности по страйкам и экспирациям', 
    icon: 'LayersIcon'
  },
  { 
    id: 'volatility-surface-greeks', 
    label: 'Поверхность волатильности (по грекам)', 
    code: 'VOLG', 
    description: '3D визуализация волатильности по страйкам и экспирациям на основе греков', 
    icon: 'LayersIcon'
  },
  { 
    id: 'citadel-zeta-field', 
    label: 'Citadel Zeta Field', 
    code: 'CZF', 
    description: 'Анализ поля дзета-параметров Citadel', 
    icon: 'TargetIcon'
  },
  { 
    id: 'cvrc', 
    label: 'Convolutional Volatility Resolution Clustering', 
    code: 'CVRC', 
    description: 'Кластеризация волатильности с использованием сверточных нейросетей', 
    icon: 'ActivityIcon'
  },
  { 
    id: 'phase-space', 
    label: 'Phase Space Reconstruction', 
    code: 'PSR', 
    description: 'Реконструкция фазового пространства для анализа динамики', 
    icon: 'BarChart2Icon'
  },
  { 
    id: 'latent-volatility', 
    label: 'Latent Volatility model', 
    code: 'LVM', 
    description: 'Модель скрытой волатильности', 
    icon: 'LayersIcon'
  },
  { 
    id: 'momentum-volatility', 
    label: 'Momentum-Volatility Surface', 
    code: 'MVS', 
    description: 'Поверхность волатильности с учетом импульса', 
    icon: 'TrendingUpIcon'
  },
  { 
    id: 'liquidity-model', 
    label: 'Liquidity Model', 
    code: 'LIQ', 
    description: 'Модель ликвидности рынка', 
    icon: 'ActivityIcon'
  },
  { 
    id: 'hmm-regime', 
    label: 'HMM regime model visualization', 
    code: 'HMM', 
    description: 'Визуализация режимов скрытой марковской модели', 
    icon: 'PieChartIcon'
  },
  { 
    id: 'time-series-signals', 
    label: 'Time series с сигналами', 
    code: 'TSIG', 
    description: 'Линейный/бар чарт цены + наложение флагов buy/sell', 
    icon: 'ChartBarIcon'
  },
  { 
    id: 'correlation-heatmap', 
    label: 'Correlation heatmap', 
    code: 'CORR', 
    description: 'Цветная матрица корреляций', 
    icon: 'TableCellsIcon'
  },
  { 
    id: 'hmm-state-diagram', 
    label: 'HMM state diagram', 
    code: 'HMMD', 
    description: 'Граф состояний + timeline colors', 
    icon: 'ShareIcon'
  },
  { 
    id: 'zscore-residuals', 
    label: 'Z‑score residuals', 
    code: 'ZSCR', 
    description: 'Линейный график отклонений', 
    icon: 'TrendingDownIcon'
  },
  { 
    id: 'orderbook-heatmap', 
    label: 'Order book heatmap', 
    code: 'OBHM', 
    description: 'Цветная карта глубины стакана', 
    icon: 'Squares2X2Icon'
  },
  { 
    id: 'ensemble-signal', 
    label: 'Ensemble signal distribution', 
    code: 'ENSD', 
    description: 'Гистограмма/confidence bands', 
    icon: 'Bars3Icon'
  },
  { 
    id: 'feature-importance', 
    label: 'Feature importance bar chart', 
    code: 'FEAT', 
    description: 'Столбцы значимости факторов', 
    icon: 'BarChart3Icon'
  },
  { 
    id: 'drawdown-sharpe', 
    label: 'Drawdown/Sharpe timeline', 
    code: 'DDSH', 
    description: 'Накопленный график + метрики', 
    icon: 'LineChartIcon'
  },
  { 
    id: 'latency-slippage', 
    label: 'Latency/slippage scatter', 
    code: 'EXEC', 
    description: 'Точечный график execution metrics', 
    icon: 'ScatterIcon'
  },
  { 
    id: 'turnover-exposure', 
    label: 'Turnover/exposure matrix', 
    code: 'EXPO', 
    description: 'Heatmap позиций по активам', 
    icon: 'TableCellsIcon'
  },
  { 
    id: 'orderbook-3d', 
    label: 'Объёмная карта ордербука (3D Depth Map)', 
    code: 'OB3D', 
    description: 'Трёхмерная визуализация глубины стакана', 
    icon: 'LayersIcon'
  },
  { 
    id: 'time-varying-correlation', 
    label: 'Динамическая корреляционная сеть (Time‑Varying Correlation Network)', 
    code: 'TVCN', 
    description: 'Сетевая визуализация корреляций во времени', 
    icon: 'ShareIcon'
  },
  { 
    id: 'covariance-tensor', 
    label: 'Ковариационный куб (Covariance Tensor Cube)', 
    code: 'CTENSOR', 
    description: 'Трёхмерное представление ковариационной матрицы', 
    icon: 'Squares2X2Icon'
  },
  { 
    id: 'liquidity-helix', 
    label: 'Объёмно‑временная спираль ликвидности (Liquidity Helix)', 
    code: 'HELIX', 
    description: 'Спиральная визуализация ликвидности во времени', 
    icon: 'ActivityIcon'
  },
  { 
    id: 'correlation-hypercube', 
    label: 'Пространство корреляций во времени (Correlation Hypercube)', 
    code: 'HYPERCUBE', 
    description: 'Гиперкубическое представление корреляций', 
    icon: 'Squares2X2Icon'
  },
  { 
    id: 'sentiment-vortex', 
    label: 'Вихрь рыночных настроений (Sentiment Vortex)', 
    code: 'VORTEX', 
    description: 'Вихревая визуализация рыночных настроений', 
    icon: 'ActivityIcon'
  },
  { 
    id: 'options-plasma', 
    label: '«Плазма» потока опционных сделок', 
    code: 'PLASMA', 
    description: 'Визуализация в реальном времени потока опционных сделок как заряженных частиц в магнитном поле', 
    icon: 'ActivityIcon'
  },
  { 
    id: 'auction-lattice', 
    label: '«Кристаллическая решетка аукциона» (Auction Lattice)', 
    code: 'LATTICE', 
    description: '3D-структура, показывающая историю и текущее состояние аукциона (открытия/закрытия на бирже, аукциона MOC)', 
    icon: 'Squares2X2Icon'
  },
  { 
    id: 'tick-core', 
    label: '«Тактовый сердечник» процессора исполнения', 
    code: 'TICKCORE', 
    description: 'Метафора процессора, где каждый такт — это пакет рыночных данных (тик). Визуализация нагрузки и задержек в обработке', 
    icon: 'ActivityIcon'
  },
  { 
    id: 'greeks-3d-tensor', 
    label: '3D Greeks Tensor (Delta-Gamma-Vega landscape)', 
    code: 'GREEKS3D', 
    description: 'Для портфеля опционов/структурных продуктов показывай греки как трёхмерный тензор', 
    icon: 'LayersIcon'
  },
  { 
    id: 'regime-correlation-network', 
    label: 'Regime Correlation Network (HMM‑driven)', 
    code: 'REGNET', 
    description: '3D‑граф корреляций, где высота узлов пропорциональна posterior probability текущего режима (из HMM)', 
    icon: 'ShareIcon'
  },
  { 
    id: 'tail-risk-cube', 
    label: 'Tail Risk Cube (EVT Stress Scenarios)', 
    code: 'TAILCUBE', 
    description: 'Куб, где каждый слой — сценарий стресса (GPD fits для tails), вокселы — P&L портфеля при quantile α', 
    icon: 'Squares2X2Icon'
  },
];

const selectAsset = (asset: string) => {
  selectedAsset.value = asset;
  isAssetsOpen.value = false;
};

const selectInstrument = (tool: any) => {
  selectedInstrument.value = tool;
  isInstrumentsOpen.value = false;
};

// Close dropdowns when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  if (!target.closest('[data-dropdown-assets]')) {
    isAssetsOpen.value = false;
  }
  if (!target.closest('[data-dropdown-instruments]')) {
    isInstrumentsOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
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

// Volatility Surface Chart Option (Heatmap)
const volatilitySurfaceOption = computed(() => {
  const strikes = [80, 85, 90, 95, 100, 105, 110, 115, 120];
  const tenors = ['1M', '3M', '6M', '1Y', '2Y', '3Y'];
  const data: number[][] = [];
  
  strikes.forEach((strike, i) => {
    tenors.forEach((tenor, j) => {
      const vol = 0.15 + (Math.random() - 0.5) * 0.1 + Math.abs(strike - 100) / 1000;
      data.push([i, j, Math.max(0.05, Math.min(0.5, vol))]);
    });
  });

  return {
    tooltip: {
      backgroundColor: 'rgba(20,20,30,0.9)',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#fff' },
      formatter: (params: any) => {
        const strike = strikes[params.data[0]];
        const tenor = tenors[params.data[1]];
        const vol = (params.data[2] * 100).toFixed(2);
        return `Страйк: ${strike}<br/>Экспирация: ${tenor}<br/>Волатильность: ${vol}%`;
      }
    },
    grid: {
      height: '60%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: strikes,
      splitArea: {
        show: true
      },
      axisLabel: { color: 'rgba(255,255,255,0.7)' },
      name: 'Страйк',
      nameTextStyle: { color: '#fff' }
    },
    yAxis: {
      type: 'category',
      data: tenors,
      splitArea: {
        show: true
      },
      axisLabel: { color: 'rgba(255,255,255,0.7)' },
      name: 'Экспирация',
      nameTextStyle: { color: '#fff' }
    },
    visualMap: {
      min: 0.05,
      max: 0.5,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '5%',
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffcc', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
      },
      textStyle: { color: '#fff' }
    },
    series: [{
      name: 'Волатильность',
      type: 'heatmap',
      data: data,
      label: {
        show: true,
        formatter: (params: any) => {
          return (params.data[2] * 100).toFixed(1) + '%';
        },
        color: '#fff',
        fontSize: 10
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  };
});


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
const ChartBarIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>' };
const TableCellsIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h18v18H3z"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/></svg>' };
const ShareIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>' };
const Squares2X2Icon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>' };
const Bars3Icon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>' };
const BarChart3Icon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/><line x1="3" y1="20" x2="21" y2="20"/></svg>' };
const LineChartIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 3 7 9 12 5 15 9 21 3"/><polyline points="3 21 7 15 12 19 15 15 21 21"/></svg>' };
const ScatterIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="7" cy="7" r="2"/><circle cx="17" cy="7" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/></svg>' };
const TrendingDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>' };
const LayoutTemplateIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>' };
const ChevronDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>' };
const GlobeIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>' };
const FilterIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>' };
const WifiIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>' };
const SearchIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>' };
const DatabaseIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>' };
</script>
