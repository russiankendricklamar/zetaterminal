<template>
  <div class="glass-panel rounded-3xl shadow-2xl shadow-black/20 p-6 flex flex-col animate-fade-in relative">
    <!-- Decorative background element -->
    <div class="absolute top-0 right-0 w-96 h-96 bg-gradient-to-b from-indigo-500/5 to-transparent rounded-full blur-3xl -z-10 pointer-events-none"></div>

    <div class="flex flex-col gap-4 mb-8 flex-shrink-0">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-3xl font-bold text-white tracking-tight mb-1">
            {{ category === 'All' ? 'Акции' : category }}
          </h2>
          <p class="text-sm text-gray-400">Цены и аналитика в реальном времени</p>
        </div>
        <div class="flex gap-2">
          <button
            v-for="(filter, i) in filters"
            :key="filter"
            @click="activeFilter = filter"
            :class="`px-4 py-2 rounded-xl text-xs font-bold transition-all border border-white/5 hover:border-white/20 ${activeFilter === filter ? 'bg-white/10 text-white' : 'bg-transparent text-gray-400 hover:text-white'}`"
          >
            {{ filter }}
          </button>
        </div>
      </div>
      
      <!-- Фильтры по регионам и странам -->
      <div class="flex flex-wrap items-center gap-3">
        <!-- Регион Dropdown -->
        <div class="relative" data-dropdown-region>
          <span class="text-xs font-bold text-gray-500 uppercase mb-2 block">Регион</span>
          <div class="relative">
            <button
              @click="isRegionOpen = !isRegionOpen"
              class="px-4 py-2.5 bg-black/20 border border-white/10 rounded-xl text-sm text-white hover:border-indigo-500/50 transition-all flex items-center justify-between gap-3 min-w-[200px]"
            >
              <span>{{ selectedRegion === 'All' ? 'Все регионы' : getRegionName(selectedRegion) }}</span>
              <ChevronDownIcon :class="`w-4 h-4 transition-transform ${isRegionOpen ? 'rotate-180' : ''}`" />
            </button>
            <div
              v-if="isRegionOpen"
              @click.stop
              class="absolute top-full left-0 mt-2 w-full bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl z-50 max-h-64 overflow-y-auto custom-scrollbar"
            >
              <button
                @click="selectRegion('All')"
                :class="`w-full px-4 py-3 text-left text-sm transition-colors ${
                  selectedRegion === 'All' 
                    ? 'bg-indigo-500/20 text-indigo-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                Все регионы
              </button>
              <button
                v-for="region in availableRegions"
                :key="region"
                @click="selectRegion(region)"
                :class="`w-full px-4 py-3 text-left text-sm transition-colors ${
                  selectedRegion === region 
                    ? 'bg-indigo-500/20 text-indigo-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                {{ getRegionName(region) }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- Страна Dropdown -->
        <div class="relative" data-dropdown-country>
          <span class="text-xs font-bold text-gray-500 uppercase mb-2 block">Страна</span>
          <div class="relative">
            <button
              @click="selectedRegion !== 'All' && (isCountryOpen = !isCountryOpen)"
              :class="`px-4 py-2.5 bg-black/20 border border-white/10 rounded-xl text-sm transition-all flex items-center justify-between gap-3 min-w-[200px] ${
                selectedRegion === 'All' 
                  ? 'opacity-50 cursor-not-allowed text-gray-500' 
                  : 'text-white hover:border-indigo-500/50 cursor-pointer'
              }`"
            >
              <span>{{ selectedCountry === 'All' ? 'Все страны' : getCountryName(selectedCountry) }}</span>
              <ChevronDownIcon :class="`w-4 h-4 transition-transform ${isCountryOpen && selectedRegion !== 'All' ? 'rotate-180' : ''}`" />
            </button>
            <div
              v-if="isCountryOpen && selectedRegion !== 'All' && availableCountries.length > 0"
              @click.stop
              class="absolute top-full left-0 mt-2 w-full bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl z-50 max-h-64 overflow-y-auto custom-scrollbar"
            >
              <button
                @click="selectCountry('All')"
                :class="`w-full px-4 py-3 text-left text-sm transition-colors ${
                  selectedCountry === 'All' 
                    ? 'bg-indigo-500/20 text-indigo-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                Все страны
              </button>
              <button
                v-for="country in availableCountries"
                :key="country"
                @click="selectCountry(country)"
                :class="`w-full px-4 py-3 text-left text-sm transition-colors ${
                  selectedCountry === country 
                    ? 'bg-indigo-500/20 text-indigo-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                {{ getCountryName(country) }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- Сектор Dropdown -->
        <div class="relative" data-dropdown-sector>
          <span class="text-xs font-bold text-gray-500 uppercase mb-2 block">Сектор</span>
          <div class="relative">
            <button
              @click="isSectorOpen = !isSectorOpen"
              class="px-4 py-2.5 bg-black/20 border border-white/10 rounded-xl text-sm text-white hover:border-indigo-500/50 transition-all flex items-center justify-between gap-3 min-w-[200px]"
            >
              <span>{{ selectedSector === 'All' ? 'Все сектора' : getSectorName(selectedSector) }}</span>
              <ChevronDownIcon :class="`w-4 h-4 transition-transform ${isSectorOpen ? 'rotate-180' : ''}`" />
            </button>
            <div
              v-if="isSectorOpen"
              @click.stop
              class="absolute top-full left-0 mt-2 w-full bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl z-50 max-h-64 overflow-y-auto custom-scrollbar"
            >
              <button
                @click="selectSector('All')"
                :class="`w-full px-4 py-3 text-left text-sm transition-colors ${
                  selectedSector === 'All' 
                    ? 'bg-indigo-500/20 text-indigo-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                Все сектора
              </button>
              <button
                v-for="sector in availableSectors"
                :key="sector"
                @click="selectSector(sector)"
                :class="`w-full px-4 py-3 text-left text-sm transition-colors ${
                  selectedSector === sector 
                    ? 'bg-indigo-500/20 text-indigo-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                {{ getSectorName(sector) }}
              </button>
            </div>
          </div>
        </div>
        
        <div class="flex items-end">
          <button 
            v-if="selectedRegion !== 'All' || selectedCountry !== 'All' || selectedSector !== 'All'"
            @click="clearFilters"
            class="px-4 py-2.5 text-xs font-bold text-gray-400 hover:text-white hover:bg-white/5 rounded-xl border border-white/5 hover:border-white/20 transition-all"
          >
            Сбросить
          </button>
        </div>
      </div>
    </div>

    <!-- Индикатор загрузки -->
    <div v-if="loading" class="flex items-center justify-center py-8 text-gray-400 flex-shrink-0">
      <div class="flex items-center gap-2">
        <div class="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        <span class="text-xs font-bold">Загрузка реальных данных...</span>
      </div>
    </div>

    <div :class="{ 'opacity-50': loading }" class="bg-black/20 rounded-2xl border border-white/5 relative">
      <table class="w-full text-left border-collapse">
        <thead class="sticky top-0 z-20">
          <tr class="bg-black/95 backdrop-blur-md border-b border-white/10">
            <th class="font-bold py-3.5 px-6 text-xs text-gray-400 uppercase tracking-wider" style="border-radius: 0.75rem 0 0 0;">Инструмент</th>
            <th class="font-bold py-3.5 px-6 text-xs text-gray-400 uppercase tracking-wider text-right">Цена</th>
            <th class="font-bold py-3.5 px-6 text-xs text-gray-400 uppercase tracking-wider text-right">Изменение 24ч</th>
            <th class="font-bold py-3.5 px-6 text-xs text-gray-400 uppercase tracking-wider text-right hidden md:table-cell" style="border-radius: 0 0.75rem 0 0;">Детали</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="asset in filteredAssets" 
            :key="asset.symbol"
            @click="$emit('assetClick', asset)"
            class="border-b border-white/5 hover:bg-white/5 transition-all duration-150 group cursor-pointer"
          >
            <td class="py-4 px-6">
              <div class="flex items-center gap-3">
                <button 
                  class="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-yellow-400 transition-all duration-150 flex-shrink-0"
                  @click.stop
                  title="Добавить в избранное"
                >
                  <StarIcon class="w-4 h-4" />
                </button>
                <div :class="`w-12 h-12 rounded-xl flex items-center justify-center text-xs font-bold shadow-md overflow-hidden flex-shrink-0 ${getCategoryStyle(asset.category)}`">
                  <img 
                    v-if="!logoErrors.has(asset.symbol) && getLogoUrl(asset.symbol)"
                    :src="getLogoUrl(asset.symbol)" 
                    :alt="asset.symbol"
                    @error="handleLogoError"
                    class="w-full h-full object-cover"
                    loading="lazy"
                  />
                  <span v-else class="text-white text-xs font-bold">
                    {{ asset.symbol.substring(0, 2) }}
                  </span>
                </div>
                <div class="min-w-0 flex-1">
                  <div class="text-white font-bold text-sm mb-0.5 truncate">{{ asset.symbol }}</div>
                  <div class="text-xs text-gray-400 flex items-center gap-2 truncate">
                    <span class="truncate">{{ asset.name }}</span>
                    <span class="px-2 py-0.5 rounded-md bg-white/5 text-[10px] font-medium uppercase text-gray-400 flex-shrink-0">{{ asset.category }}</span>
                  </div>
                </div>
              </div>
            </td>
            <td class="py-4 px-6 text-right">
              <div class="font-mono text-white text-sm font-semibold">{{ asset.price }}</div>
            </td>
            <td class="py-4 px-6 text-right">
              <div :class="`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold ${
                asset.change.startsWith('+') 
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20' 
                  : 'bg-rose-500/15 text-rose-400 border border-rose-500/20'
              }`">
                <component :is="asset.change.startsWith('+') ? 'TrendingUpIcon' : 'TrendingDownIcon'" class="w-3.5 h-3.5 flex-shrink-0" />
                <span class="font-mono">{{ asset.change }}</span>
              </div>
            </td>
            <td class="py-4 px-6 text-right hidden md:table-cell">
              <div class="text-xs text-gray-400 font-mono">
                <span v-if="asset.cap" class="text-gray-300">{{ asset.cap }}</span>
                <span v-else class="text-gray-600">-</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount, reactive } from 'vue';
import { AssetInfo } from '@/types/terminal';
import { getMultipleStocks, getPopularTickers, getMOEXStocks, getSPBStocks, type StockInfo, type MOEXStockInfo } from '@/services/marketDataService';

interface Props {
  category: string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  navigate: [page: string];
  assetClick: [asset: AssetInfo];
}>();

const filters = ['Топ роста', 'Топ падения', 'Высокий объём'];
const activeFilter = ref('Топ роста');
const selectedRegion = ref('All');
const selectedCountry = ref('All');
const selectedSector = ref('All');
const isRegionOpen = ref(false);
const isCountryOpen = ref(false);
const isSectorOpen = ref(false);
const logoErrors = ref(new Set<string>());
const loading = ref(false);
const useRealData = ref(true); // Флаг для переключения между реальными и статическими данными

const selectRegion = (region: string) => {
  selectedRegion.value = region;
  selectedCountry.value = 'All';
  isRegionOpen.value = false;
  isCountryOpen.value = false;
  // Если регион выбран, автоматически открываем меню стран для удобства
  if (region !== 'All') {
    setTimeout(() => {
      isCountryOpen.value = true;
    }, 100);
  }
};

const selectCountry = (country: string) => {
  selectedCountry.value = country;
  isCountryOpen.value = false;
};

const selectSector = (sector: string) => {
  selectedSector.value = sector;
  isSectorOpen.value = false;
};

// Закрытие выпадающих меню при клике вне их
let clickOutsideHandler: ((e: MouseEvent) => void) | null = null;

onMounted(() => {
  clickOutsideHandler = (e: MouseEvent) => {
    const target = e.target as HTMLElement;
    if (!target.closest('[data-dropdown-region]') && !target.closest('[data-dropdown-country]') && !target.closest('[data-dropdown-sector]')) {
      isRegionOpen.value = false;
      isCountryOpen.value = false;
      isSectorOpen.value = false;
    }
  };
  document.addEventListener('click', clickOutsideHandler);
});

// Переменная для интервала обновления
let updateInterval: ReturnType<typeof setInterval> | null = null;

onMounted(async () => {
  clickOutsideHandler = (e: MouseEvent) => {
    const target = e.target as HTMLElement;
    if (!target.closest('[data-dropdown-region]') && !target.closest('[data-dropdown-country]') && !target.closest('[data-dropdown-sector]')) {
      isRegionOpen.value = false;
      isCountryOpen.value = false;
      isSectorOpen.value = false;
    }
  };
  document.addEventListener('click', clickOutsideHandler);
  
  // Загружаем данные сразу при монтировании
  await loadRealData();
  // Обновляем данные каждые 60 секунд
  updateInterval = setInterval(loadRealData, 60000);
});

onBeforeUnmount(() => {
  if (updateInterval) {
    clearInterval(updateInterval);
  }
  if (clickOutsideHandler) {
    document.removeEventListener('click', clickOutsideHandler);
  }
});

// Функция для загрузки всех тикеров с MOEX
const loadMOEXStocks = async () => {
  try {
    console.log('🔄 Loading MOEX stocks...');
    const moexStocks = await getMOEXStocks();
    console.log(`✅ Loaded ${moexStocks.length} stocks from MOEX`);

    const existingSymbols = new Set(allAssets.value.map(a => a.symbol));
    let addedCount = 0;

    moexStocks.forEach((stock: MOEXStockInfo) => {
      if (!existingSymbols.has(stock.ticker)) {
        // Определяем сектор на основе тикера
        let sector = 'Technology';
        const ticker = stock.ticker.toUpperCase();

        if (['SBER', 'VTBR', 'MOEX', 'TCSG', 'BSPB', 'CBOM'].some(t => ticker.includes(t))) {
          sector = 'Banking';
        } else if (['GAZP', 'LKOH', 'ROSN', 'TATN', 'NVTK', 'SNGS', 'SIBN', 'TRNFP', 'BANEP'].some(t => ticker.includes(t))) {
          sector = 'Oil & Gas';
        } else if (['GMKN', 'ALRS', 'PLZL', 'POLY', 'CHMF', 'NLMK', 'MAGN', 'RUAL', 'VSMO'].some(t => ticker.includes(t))) {
          sector = 'Materials';
        } else if (['YNDX', 'VKCO', 'OZON', 'HHRU', 'CIAN', 'POSI'].some(t => ticker.includes(t))) {
          sector = 'Technology';
        } else if (['MGNT', 'FIVE', 'LENT', 'FIXP', 'DSKY'].some(t => ticker.includes(t))) {
          sector = 'Retail';
        } else if (['MTSS', 'RTKM', 'RTKMP'].some(t => ticker.includes(t))) {
          sector = 'Telecommunications';
        } else if (['AFLT', 'FLOT', 'NMTP', 'FESH'].some(t => ticker.includes(t))) {
          sector = 'Industrial';
        } else if (['HYDR', 'IRAO', 'FEES', 'OGKB', 'TGKA', 'MSNG', 'UPRO'].some(t => ticker.includes(t))) {
          sector = 'Utilities';
        } else if (['PIKK', 'LSRG', 'ETLN', 'SMLT'].some(t => ticker.includes(t))) {
          sector = 'Real Estate';
        } else if (['PHOR', 'AKRN', 'KZOS'].some(t => ticker.includes(t))) {
          sector = 'Materials';
        }

        // Форматируем капитализацию
        const capB = stock.marketCap / 1e9;
        const capStr = capB >= 1000 ? `${(capB / 1000).toFixed(1)}T` : capB >= 1 ? `${capB.toFixed(0)}B` : `${(stock.marketCap / 1e6).toFixed(0)}M`;

        // Форматируем объем
        const volM = stock.volume / 1e6;
        const volStr = volM >= 1 ? `${volM.toFixed(1)}M` : `${(stock.volume / 1e3).toFixed(0)}K`;

        allAssets.value.push({
          name: stock.name,
          symbol: stock.ticker,
          price: stock.price.toFixed(2),
          change: `${stock.changePercent >= 0 ? '+' : ''}${stock.changePercent.toFixed(2)}%`,
          category: 'Equities',
          region: 'EMEA',
          country: 'Russia',
          sector: sector,
          vol: volStr,
          cap: capStr
        });
        existingSymbols.add(stock.ticker);
        addedCount++;
      }
    });

    console.log(`✅ Added ${addedCount} MOEX stocks to the list`);
  } catch (error: any) {
    console.error('❌ Error loading MOEX stocks:', error);
  }
};

// Функция для загрузки популярных тикеров и расширения списка акций
const loadPopularTickers = async () => {
  try {
    console.log('🔄 Loading popular tickers from API...');
    const tickers = await getPopularTickers();
    const spbTickers = await getSPBStocks();
    const allTickers = [...new Set([...tickers, ...spbTickers])];
    console.log(`✅ Loaded ${allTickers.length} popular tickers from API`);

    // Создаем мапу существующих символов для быстрой проверки
    const existingSymbols = new Set(allAssets.value.map(a => a.symbol));

    // Добавляем новые тикеры, которых еще нет в списке
    let addedCount = 0;
    allTickers.forEach(ticker => {
      if (!existingSymbols.has(ticker)) {
        // Определяем регион и страну на основе тикера
        let region = 'Americas';
        let country = 'USA';
        let sector = 'Technology';

        if (ticker.includes('.ME')) {
          region = 'EMEA';
          country = 'Russia';
          sector = 'Banking';
        } else if (ticker.includes('.L') || ['AZN', 'SHEL', 'BP', 'GSK', 'VOD', 'DEO', 'UL'].some(t => ticker.includes(t))) {
          region = 'EMEA';
          country = 'UK';
          sector = 'Consumer';
        } else if (['SAP', 'SIEGY', 'MBGYY', 'BMWYY', 'VWAGY', 'ALIZY'].some(t => ticker.includes(t))) {
          region = 'EMEA';
          country = 'Germany';
          sector = 'Technology';
        } else if (['TTE', 'LVMUY', 'LRLCY', 'SNY', 'EADSY'].some(t => ticker.includes(t))) {
          region = 'EMEA';
          country = 'France';
          sector = 'Consumer';
        } else if (['NSRGY', 'NVS', 'RHHBY', 'UBS'].some(t => ticker.includes(t))) {
          region = 'EMEA';
          country = 'Switzerland';
          sector = 'Healthcare';
        } else if (['ASML', 'UNLY', 'ING'].some(t => ticker.includes(t))) {
          region = 'EMEA';
          country = 'Netherlands';
          sector = 'Technology';
        } else if (['TM', 'SONY', 'SFTBY', 'NTDOY', 'HMC', 'NSANY'].some(t => ticker.includes(t))) {
          region = 'APAC';
          country = 'Japan';
          sector = 'Technology';
        } else if (['SSNLF', 'HXSCL', 'LGEAF'].some(t => ticker.includes(t))) {
          region = 'APAC';
          country = 'South Korea';
          sector = 'Technology';
        } else if (ticker.includes('TSM')) {
          region = 'APAC';
          country = 'Taiwan';
          sector = 'Technology';
        } else if (ticker.includes('.BSE') || ['RELIANCE', 'TCS', 'INFY'].some(t => ticker.includes(t))) {
          region = 'APAC';
          country = 'India';
          sector = 'Technology';
        } else if (['BABA', 'TCEHY', 'JD', 'BIDU', 'PNGAY', 'IDCBY', 'CICHY', 'BYDDY', 'NIO', 'XPEV', 'LI'].some(t => ticker.includes(t))) {
          region = 'APAC';
          country = 'China';
          sector = 'Technology';
        } else if (['SHOP', 'RY', 'CNI'].some(t => ticker.includes(t))) {
          region = 'Americas';
          country = 'Canada';
          sector = 'Technology';
        } else if (['BHP', 'RIO', 'CMWAY'].some(t => ticker.includes(t))) {
          region = 'APAC';
          country = 'Australia';
          sector = 'Materials';
        }

        allAssets.value.push({
          name: ticker,
          symbol: ticker,
          price: '0.00',
          change: '+0.00%',
          category: 'Equities',
          region: region,
          country: country,
          sector: sector,
          vol: '-',
          cap: '-'
        });
        existingSymbols.add(ticker);
        addedCount++;
      }
    });

    console.log(`✅ Added ${addedCount} new tickers to the list`);
  } catch (error: any) {
    console.error('❌ Error loading popular tickers:', error);
    console.warn('⚠️ Using static tickers only');
  }
};

// Функция для загрузки реальных данных с yfinance
const loadRealData = async () => {
  if (!useRealData.value) {
    console.log('Real data loading is disabled');
    return;
  }

  loading.value = true;
  try {
    // Сначала загружаем все акции с Московской биржи (MOEX ISS API)
    await loadMOEXStocks();

    // Затем загружаем популярные тикеры и тикеры СПБ Биржи
    await loadPopularTickers();
    
    // Получаем список всех тикеров из статических данных
    const allTickers = allAssets.value.map(asset => asset.symbol);
    
    console.log('🔄 Loading market data for', allTickers.length, 'tickers...');
    
    // Загружаем данные батчами по 50 тикеров для оптимизации
    const batchSize = 50;
    let updatedCount = 0;
    
    for (let i = 0; i < allTickers.length; i += batchSize) {
      const batch = allTickers.slice(i, i + batchSize);
      console.log(`📦 Loading batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(allTickers.length / batchSize)} (${batch.length} tickers)...`);
      
      try {
        const stocksData = await getMultipleStocks(batch);
        
        // Обновляем данные в allAssets
        stocksData.forEach((stock: StockInfo) => {
          const assetIndex = allAssets.value.findIndex(a => a.symbol === stock.ticker);
          if (assetIndex !== -1) {
            allAssets.value[assetIndex].price = stock.price.toFixed(2);
            allAssets.value[assetIndex].change = `${stock.changePercent >= 0 ? '+' : ''}${stock.changePercent.toFixed(2)}%`;
            allAssets.value[assetIndex].name = stock.name;
            if (stock.marketCap) {
              const capB = stock.marketCap / 1e9;
              allAssets.value[assetIndex].cap = capB >= 1000 ? `${(capB / 1000).toFixed(1)}T` : `${capB.toFixed(0)}B`;
            }
            if (stock.volume) {
              const volM = stock.volume / 1e6;
              allAssets.value[assetIndex].vol = `${volM.toFixed(0)}M`;
            }
            updatedCount++;
          }
        });
        
        // Небольшая задержка между батчами, чтобы не перегружать API
        if (i + batchSize < allTickers.length) {
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } catch (batchError: any) {
        console.warn(`⚠️ Error loading batch ${Math.floor(i / batchSize) + 1}:`, batchError.message);
        // Продолжаем загрузку следующих батчей
      }
    }
    
    console.log(`✅ Updated ${updatedCount} assets with real data`);
  } catch (error: any) {
    console.error('❌ Error loading real market data:', error);
    console.error('Error message:', error.message);
    if (error.stack) {
      console.error('Error stack:', error.stack);
    }
    
    // В случае ошибки используем статические данные
    useRealData.value = false;
    console.warn('⚠️ Falling back to static data');
  } finally {
    loading.value = false;
    console.log('🏁 Data loading finished');
  }
};

// Инициализируем allAssets как реактивный массив
const allAssets = ref<AssetInfo[]>([
  // США - Технологии
  { name: 'Apple Inc.', symbol: 'AAPL', price: '173.50', change: '+1.20%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '55M', cap: '2.7T' },
  { name: 'NVIDIA Corp', symbol: 'NVDA', price: '892.10', change: '+4.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '42M', cap: '2.2T' },
  { name: 'Microsoft', symbol: 'MSFT', price: '420.55', change: '-0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '22M', cap: '3.1T' },
  { name: 'Tesla Inc', symbol: 'TSLA', price: '175.30', change: '+2.10%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Automotive', vol: '95M', cap: '550B' },
  { name: 'Amazon', symbol: 'AMZN', price: '180.25', change: '+0.95%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Retail', vol: '38M', cap: '1.8T' },
  { name: 'Meta Platforms', symbol: 'META', price: '495.10', change: '+1.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '18M', cap: '1.2T' },
  { name: 'Google', symbol: 'GOOGL', price: '156.40', change: '-0.20%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '24M', cap: '1.9T' },
  { name: 'Alphabet Inc', symbol: 'GOOG', price: '156.80', change: '-0.18%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '12M', cap: '1.9T' },
  { name: 'Netflix', symbol: 'NFLX', price: '485.20', change: '+2.30%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '8M', cap: '215B' },
  { name: 'AMD', symbol: 'AMD', price: '142.50', change: '+3.15%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '65M', cap: '230B' },
  { name: 'Intel', symbol: 'INTC', price: '44.80', change: '+0.90%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '35M', cap: '185B' },
  { name: 'Qualcomm', symbol: 'QCOM', price: '145.60', change: '+1.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '12M', cap: '162B' },
  { name: 'Broadcom', symbol: 'AVGO', price: '1280.40', change: '+2.60%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '3M', cap: '590B' },
  { name: 'Oracle', symbol: 'ORCL', price: '118.25', change: '+0.75%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '18M', cap: '320B' },
  { name: 'Adobe', symbol: 'ADBE', price: '545.80', change: '+1.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '5M', cap: '248B' },
  
  // США - Финансы
  { name: 'JPMorgan Chase', symbol: 'JPM', price: '185.40', change: '+0.55%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Banking', vol: '15M', cap: '540B' },
  { name: 'Bank of America', symbol: 'BAC', price: '38.50', change: '+0.40%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Banking', vol: '45M', cap: '305B' },
  { name: 'Wells Fargo', symbol: 'WFC', price: '58.20', change: '+0.30%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Banking', vol: '25M', cap: '215B' },
  { name: 'Goldman Sachs', symbol: 'GS', price: '425.80', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '3M', cap: '145B' },
  { name: 'Morgan Stanley', symbol: 'MS', price: '95.60', change: '+0.65%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '8M', cap: '175B' },
  { name: 'Citigroup', symbol: 'C', price: '62.40', change: '+0.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Banking', vol: '28M', cap: '120B' },
  
  // США - Потребительские товары
  { name: 'Walmart', symbol: 'WMT', price: '165.30', change: '+0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Retail', vol: '8M', cap: '445B' },
  { name: 'Procter & Gamble', symbol: 'PG', price: '168.90', change: '+0.35%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '7M', cap: '400B' },
  { name: 'Coca-Cola', symbol: 'KO', price: '62.80', change: '+0.20%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '18M', cap: '270B' },
  { name: 'PepsiCo', symbol: 'PEP', price: '172.50', change: '+0.40%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '6M', cap: '238B' },
  { name: 'Nike', symbol: 'NKE', price: '98.40', change: '+1.15%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '8M', cap: '151B' },
  { name: 'McDonald\'s', symbol: 'MCD', price: '295.60', change: '+0.50%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '4M', cap: '215B' },
  { name: 'Starbucks', symbol: 'SBUX', price: '95.80', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '9M', cap: '110B' },
  
  // США - Здравоохранение
  { name: 'Johnson & Johnson', symbol: 'JNJ', price: '158.40', change: '+0.30%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Healthcare', vol: '9M', cap: '420B' },
  { name: 'Pfizer', symbol: 'PFE', price: '27.80', change: '-0.50%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Healthcare', vol: '45M', cap: '158B' },
  { name: 'Merck', symbol: 'MRK', price: '128.60', change: '+0.55%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Healthcare', vol: '12M', cap: '326B' },
  { name: 'AbbVie', symbol: 'ABBV', price: '168.90', change: '+0.40%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Healthcare', vol: '8M', cap: '298B' },
  { name: 'UnitedHealth', symbol: 'UNH', price: '525.40', change: '+1.20%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Healthcare', vol: '4M', cap: '495B' },
  { name: 'Eli Lilly', symbol: 'LLY', price: '765.20', change: '+2.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Healthcare', vol: '3M', cap: '728B' },
  
  // США - Энергетика
  { name: 'Exxon Mobil', symbol: 'XOM', price: '118.50', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Oil & Gas', vol: '22M', cap: '495B' },
  { name: 'Chevron', symbol: 'CVX', price: '162.40', change: '+0.75%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Oil & Gas', vol: '12M', cap: '305B' },
  { name: 'ConocoPhillips', symbol: 'COP', price: '115.80', change: '+1.05%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Oil & Gas', vol: '8M', cap: '138B' },
  
  // США - Промышленность
  { name: 'Boeing', symbol: 'BA', price: '185.40', change: '+1.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '8M', cap: '115B' },
  { name: 'Caterpillar', symbol: 'CAT', price: '348.60', change: '+1.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '4M', cap: '175B' },
  { name: '3M', symbol: 'MMM', price: '98.50', change: '+0.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '5M', cap: '55B' },
  { name: 'General Electric', symbol: 'GE', price: '148.20', change: '+1.15%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '12M', cap: '162B' },
  
  // США - Телекоммуникации
  { name: 'AT&T', symbol: 'T', price: '17.40', change: '+0.15%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Telecommunications', vol: '45M', cap: '124B' },
  { name: 'Verizon', symbol: 'VZ', price: '40.80', change: '+0.10%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Telecommunications', vol: '25M', cap: '172B' },
  { name: 'T-Mobile', symbol: 'TMUS', price: '165.40', change: '+0.65%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Telecommunications', vol: '5M', cap: '195B' },
  
  // Европа - Великобритания
  { name: 'BP', symbol: 'BP', price: '38.50', change: '+0.85%', category: 'Equities', region: 'EMEA', country: 'UK', sector: 'Oil & Gas', vol: '18M', cap: '82B' },
  { name: 'Shell', symbol: 'SHEL', price: '32.80', change: '+0.75%', category: 'Equities', region: 'EMEA', country: 'UK', sector: 'Oil & Gas', vol: '15M', cap: '210B' },
  { name: 'AstraZeneca', symbol: 'AZN', price: '68.40', change: '+0.45%', category: 'Equities', region: 'EMEA', country: 'UK', sector: 'Healthcare', vol: '5M', cap: '215B' },
  { name: 'Unilever', symbol: 'UL', price: '52.60', change: '+0.30%', category: 'Equities', region: 'EMEA', country: 'UK', sector: 'Consumer', vol: '8M', cap: '125B' },
  { name: 'Diageo', symbol: 'DEO', price: '145.20', change: '+0.50%', category: 'Equities', region: 'EMEA', country: 'UK', sector: 'Consumer', vol: '2M', cap: '82B' },
  { name: 'GlaxoSmithKline', symbol: 'GSK', price: '42.80', change: '+0.35%', category: 'Equities', region: 'EMEA', country: 'UK', sector: 'Healthcare', vol: '12M', cap: '88B' },
  { name: 'Vodafone', symbol: 'VOD', price: '8.45', change: '+0.15%', category: 'Equities', region: 'EMEA', country: 'UK', sector: 'Telecommunications', vol: '28M', cap: '24B' },
  
  // Европа - Германия
  { name: 'SAP', symbol: 'SAP', price: '185.40', change: '+1.25%', category: 'Equities', region: 'EMEA', country: 'Germany', sector: 'Technology', vol: '2M', cap: '228B' },
  { name: 'Siemens', symbol: 'SIEGY', price: '95.80', change: '+0.85%', category: 'Equities', region: 'EMEA', country: 'Germany', sector: 'Industrial', vol: '1.5M', cap: '145B' },
  { name: 'Mercedes-Benz', symbol: 'MBGYY', price: '18.50', change: '+0.60%', category: 'Equities', region: 'EMEA', country: 'Germany', sector: 'Automotive', vol: '0.5M', cap: '68B' },
  { name: 'BMW', symbol: 'BMWYY', price: '36.40', change: '+0.45%', category: 'Equities', region: 'EMEA', country: 'Germany', sector: 'Automotive', vol: '0.8M', cap: '62B' },
  { name: 'Volkswagen', symbol: 'VWAGY', price: '15.20', change: '+0.35%', category: 'Equities', region: 'EMEA', country: 'Germany', sector: 'Technology', vol: '1.2M', cap: '75B' },
  { name: 'Allianz', symbol: 'ALIZY', price: '28.60', change: '+0.40%', category: 'Equities', region: 'EMEA', country: 'Germany', sector: 'Technology', vol: '0.6M', cap: '112B' },
  
  // Европа - Франция
  { name: 'TotalEnergies', symbol: 'TTE', price: '68.40', change: '+0.95%', category: 'Equities', region: 'EMEA', country: 'France', sector: 'Oil & Gas', vol: '5M', cap: '165B' },
  { name: 'LVMH', symbol: 'LVMUY', price: '182.50', change: '+1.15%', category: 'Equities', region: 'EMEA', country: 'France', sector: 'Consumer', vol: '0.3M', cap: '385B' },
  { name: 'L\'Oreal', symbol: 'LRLCY', price: '28.40', change: '+0.55%', category: 'Equities', region: 'EMEA', country: 'France', sector: 'Consumer', vol: '0.5M', cap: '245B' },
  { name: 'Sanofi', symbol: 'SNY', price: '48.20', change: '+0.35%', category: 'Equities', region: 'EMEA', country: 'France', sector: 'Healthcare', vol: '3M', cap: '120B' },
  { name: 'Airbus', symbol: 'EADSY', price: '42.80', change: '+0.85%', category: 'Equities', region: 'EMEA', country: 'France', sector: 'Industrial', vol: '1.8M', cap: '125B' },
  
  // Европа - Швейцария
  { name: 'Nestle', symbol: 'NSRGY', price: '108.40', change: '+0.25%', category: 'Equities', region: 'EMEA', country: 'Switzerland', sector: 'Consumer', vol: '1.2M', cap: '295B' },
  { name: 'Novartis', symbol: 'NVS', price: '98.60', change: '+0.40%', category: 'Equities', region: 'EMEA', country: 'Switzerland', sector: 'Healthcare', vol: '3M', cap: '215B' },
  { name: 'Roche', symbol: 'RHHBY', price: '45.20', change: '+0.30%', category: 'Equities', region: 'EMEA', country: 'Switzerland', sector: 'Healthcare', vol: '1.5M', cap: '265B' },
  { name: 'UBS', symbol: 'UBS', price: '28.40', change: '+0.55%', category: 'Equities', region: 'EMEA', country: 'Switzerland', sector: 'Finance', vol: '8M', cap: '95B' },
  
  // Европа - Нидерланды
  { name: 'ASML', symbol: 'ASML', price: '945.60', change: '+2.85%', category: 'Equities', region: 'EMEA', country: 'Netherlands', sector: 'Technology', vol: '1.2M', cap: '375B' },
  { name: 'Unilever', symbol: 'UNLY', price: '52.80', change: '+0.30%', category: 'Equities', region: 'EMEA', country: 'Netherlands', sector: 'Consumer', vol: '2M', cap: '125B' },
  { name: 'ING Group', symbol: 'ING', price: '16.80', change: '+0.45%', category: 'Equities', region: 'EMEA', country: 'Netherlands', sector: 'Banking', vol: '15M', cap: '62B' },
  
  // Россия
  { name: 'Сбербанк', symbol: 'SBER', price: '285.40', change: '+1.85%', category: 'Equities', region: 'EMEA', country: 'Russia', sector: 'Banking', vol: '125M', cap: '6.5T' },
  { name: 'Газпром', symbol: 'GAZP', price: '168.50', change: '+0.95%', category: 'Equities', region: 'EMEA', country: 'Russia', sector: 'Oil & Gas', vol: '85M', cap: '4.2T' },
  { name: 'Лукойл', symbol: 'LKOH', price: '7850.60', change: '+1.25%', category: 'Equities', region: 'EMEA', country: 'Russia', sector: 'Oil & Gas', vol: '1.2M', cap: '8.1T' },
  { name: 'Роснефть', symbol: 'ROSN', price: '585.40', change: '+0.75%', category: 'Equities', region: 'EMEA', country: 'Russia', sector: 'Oil & Gas', vol: '15M', cap: '6.2T' },
  { name: 'Норникель', symbol: 'GMKN', price: '16250.80', change: '+2.15%', category: 'Equities', region: 'EMEA', country: 'Russia', sector: 'Materials', vol: '0.8M', cap: '2.8T' },
  { name: 'Яндекс', symbol: 'YNDX', price: '2840.50', change: '+1.45%', category: 'Equities', region: 'EMEA', country: 'Russia', sector: 'Technology', vol: '2.5M', cap: '1.1T' },
  { name: 'Магнит', symbol: 'MGNT', price: '7850.20', change: '+0.55%', category: 'Equities', region: 'EMEA', country: 'Russia', sector: 'Retail', vol: '0.3M', cap: '1.8T' },
  { name: 'ВТБ', symbol: 'VTBR', price: '0.0285', change: '+1.20%', category: 'Equities', region: 'EMEA', country: 'Russia', sector: 'Banking', vol: '2.5B', cap: '850B' },
  { name: 'Татнефть', symbol: 'TATN', price: '625.80', change: '+0.85%', category: 'Equities', region: 'EMEA', country: 'Russia', sector: 'Oil & Gas', vol: '8M', cap: '1.4T' },
  { name: 'Новатэк', symbol: 'NVTK', price: '1650.40', change: '+1.55%', category: 'Equities', region: 'EMEA', country: 'Russia', sector: 'Oil & Gas', vol: '1.8M', cap: '5.5T' },
  { name: 'Сургутнефтегаз', symbol: 'SNGS', price: '42.60', change: '+0.65%', category: 'Equities', region: 'EMEA', country: 'Russia', sector: 'Oil & Gas', vol: '12M', cap: '1.2T' },
  { name: 'Алроса', symbol: 'ALRS', price: '82.40', change: '+1.95%', category: 'Equities', region: 'EMEA', country: 'Russia', sector: 'Materials', vol: '5M', cap: '625B' },
  { name: 'МТС', symbol: 'MTSS', price: '285.60', change: '+0.45%', category: 'Equities', region: 'EMEA', country: 'Russia', sector: 'Telecommunications', vol: '3M', cap: '585B' },
  { name: 'Транснефть', symbol: 'TRNFP', price: '185000', change: '+0.35%', category: 'Equities', region: 'EMEA', country: 'Russia', sector: 'Oil & Gas', vol: '0.01M', cap: '4.2T' },
  
  // Азия - Китай
  { name: 'Alibaba', symbol: 'BABA', price: '85.40', change: '+2.15%', category: 'Equities', region: 'APAC', country: 'China', sector: 'Technology', vol: '25M', cap: '215B' },
  { name: 'Tencent', symbol: 'TCEHY', price: '48.60', change: '+1.85%', category: 'Equities', region: 'APAC', country: 'China', sector: 'Technology', vol: '18M', cap: '465B' },
  { name: 'JD.com', symbol: 'JD', price: '28.80', change: '+1.45%', category: 'Equities', region: 'APAC', country: 'China', sector: 'Retail', vol: '12M', cap: '45B' },
  { name: 'Baidu', symbol: 'BIDU', price: '115.40', change: '+0.95%', category: 'Equities', region: 'APAC', country: 'China', sector: 'Technology', vol: '8M', cap: '42B' },
  { name: 'Ping An', symbol: 'PNGAY', price: '12.80', change: '+0.65%', category: 'Equities', region: 'APAC', country: 'China', sector: 'Finance', vol: '5M', cap: '95B' },
  { name: 'ICBC', symbol: 'IDCBY', price: '18.40', change: '+0.35%', category: 'Equities', region: 'APAC', country: 'China', sector: 'Banking', vol: '3M', cap: '285B' },
  { name: 'China Construction Bank', symbol: 'CICHY', price: '15.60', change: '+0.25%', category: 'Equities', region: 'APAC', country: 'China', sector: 'Banking', vol: '2M', cap: '198B' },
  { name: 'BYD', symbol: 'BYDDY', price: '62.40', change: '+3.25%', category: 'Equities', region: 'APAC', country: 'China', sector: 'Automotive', vol: '8M', cap: '95B' },
  
  // Азия - Япония
  { name: 'Toyota', symbol: 'TM', price: '245.80', change: '+0.85%', category: 'Equities', region: 'APAC', country: 'Japan', sector: 'Automotive', vol: '1.2M', cap: '285B' },
  { name: 'Sony', symbol: 'SONY', price: '98.40', change: '+1.45%', category: 'Equities', region: 'APAC', country: 'Japan', sector: 'Technology', vol: '3M', cap: '125B' },
  { name: 'SoftBank', symbol: 'SFTBY', price: '28.60', change: '+0.65%', category: 'Equities', region: 'APAC', country: 'Japan', sector: 'Finance', vol: '2M', cap: '85B' },
  { name: 'Nintendo', symbol: 'NTDOY', price: '15.80', change: '+0.35%', category: 'Equities', region: 'APAC', country: 'Japan', sector: 'Technology', vol: '0.8M', cap: '68B' },
  { name: 'Honda', symbol: 'HMC', price: '38.40', change: '+0.55%', category: 'Equities', region: 'APAC', country: 'Japan', sector: 'Automotive', vol: '1.5M', cap: '72B' },
  { name: 'Nissan', symbol: 'NSANY', price: '8.50', change: '+0.25%', category: 'Equities', region: 'APAC', country: 'Japan', sector: 'Automotive', vol: '1.2M', cap: '18B' },
  
  // Азия - Южная Корея
  { name: 'Samsung', symbol: 'SSNLF', price: '45.80', change: '+1.15%', category: 'Equities', region: 'APAC', country: 'South Korea', sector: 'Technology', vol: '0.5M', cap: '385B' },
  { name: 'SK Hynix', symbol: 'HXSCL', price: '128.40', change: '+2.45%', category: 'Equities', region: 'APAC', country: 'South Korea', sector: 'Technology', vol: '1.2M', cap: '95B' },
  { name: 'LG', symbol: 'LGEAF', price: '18.60', change: '+0.65%', category: 'Equities', region: 'APAC', country: 'South Korea', sector: 'Technology', vol: '0.8M', cap: '12B' },
  
  // Азия - Тайвань
  { name: 'Taiwan Semiconductor', symbol: 'TSM', price: '142.50', change: '+3.15%', category: 'Equities', region: 'APAC', country: 'Taiwan', sector: 'Technology', vol: '15M', cap: '725B' },
  
  // Азия - Индия
  { name: 'Reliance Industries', symbol: 'RELIANCE.BSE', price: '2845.60', change: '+1.85%', category: 'Equities', region: 'APAC', country: 'India', sector: 'Oil & Gas', vol: '2M', cap: '245B' },
  { name: 'TCS', symbol: 'TCS.BSE', price: '3850.40', change: '+0.95%', category: 'Equities', region: 'APAC', country: 'India', sector: 'Technology', vol: '1.2M', cap: '145B' },
  { name: 'Infosys', symbol: 'INFY', price: '18.50', change: '+0.75%', category: 'Equities', region: 'APAC', country: 'India', sector: 'Technology', vol: '8M', cap: '82B' },
  
  // Канада
  { name: 'Shopify', symbol: 'SHOP', price: '78.40', change: '+2.15%', category: 'Equities', region: 'Americas', country: 'Canada', sector: 'Technology', vol: '8M', cap: '98B' },
  { name: 'Royal Bank of Canada', symbol: 'RY', price: '128.60', change: '+0.45%', category: 'Equities', region: 'Americas', country: 'Canada', sector: 'Banking', vol: '3M', cap: '185B' },
  { name: 'Canadian National Railway', symbol: 'CNI', price: '132.80', change: '+0.65%', category: 'Equities', region: 'Americas', country: 'Canada', sector: 'Industrial', vol: '1.5M', cap: '95B' },
  
  // Австралия
  { name: 'BHP Group', symbol: 'BHP', price: '62.40', change: '+1.25%', category: 'Equities', region: 'APAC', country: 'Australia', sector: 'Materials', vol: '5M', cap: '158B' },
  { name: 'Rio Tinto', symbol: 'RIO', price: '68.80', change: '+1.05%', category: 'Equities', region: 'APAC', country: 'Australia', sector: 'Materials', vol: '3M', cap: '125B' },
  { name: 'Commonwealth Bank', symbol: 'CMWAY', price: '85.20', change: '+0.55%', category: 'Equities', region: 'APAC', country: 'Australia', sector: 'Banking', vol: '1.2M', cap: '165B' },

  // Дополнительные популярные акции США - S&P 500
  { name: 'Costco', symbol: 'COST', price: '850.20', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Retail', vol: '2M', cap: '375B' },
  { name: 'Home Depot', symbol: 'HD', price: '385.60', change: '+0.65%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Retail', vol: '4M', cap: '385B' },
  { name: 'Visa', symbol: 'V', price: '285.40', change: '+0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '8M', cap: '585B' },
  { name: 'Mastercard', symbol: 'MA', price: '485.80', change: '+0.55%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '3M', cap: '425B' },
  { name: 'PayPal', symbol: 'PYPL', price: '68.50', change: '+1.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '12M', cap: '72B' },
  { name: 'Salesforce', symbol: 'CRM', price: '285.40', change: '+1.15%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '8M', cap: '285B' },
  { name: 'Cisco', symbol: 'CSCO', price: '52.80', change: '+0.35%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '18M', cap: '215B' },
  { name: 'IBM', symbol: 'IBM', price: '185.60', change: '+0.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '5M', cap: '168B' },
  { name: 'Disney', symbol: 'DIS', price: '112.40', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '15M', cap: '205B' },
  { name: 'Comcast', symbol: 'CMCSA', price: '42.80', change: '+0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Telecommunications', vol: '18M', cap: '175B' },
  { name: 'AT&T', symbol: 'T', price: '17.40', change: '+0.15%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Telecommunications', vol: '45M', cap: '124B' },
  { name: 'Boeing', symbol: 'BA', price: '185.40', change: '+1.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '8M', cap: '115B' },
  { name: 'Lockheed Martin', symbol: 'LMT', price: '485.20', change: '+0.95%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '1M', cap: '125B' },
  { name: 'Raytheon', symbol: 'RTX', price: '95.80', change: '+0.65%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '5M', cap: '145B' },
  { name: 'General Motors', symbol: 'GM', price: '42.60', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Automotive', vol: '18M', cap: '48B' },
  { name: 'Ford', symbol: 'F', price: '12.80', change: '+0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Automotive', vol: '45M', cap: '52B' },
  { name: 'Starbucks', symbol: 'SBUX', price: '95.80', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '9M', cap: '110B' },
  { name: 'Chipotle', symbol: 'CMG', price: '2850.40', change: '+1.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '0.3M', cap: '78B' },
  { name: 'Target', symbol: 'TGT', price: '165.20', change: '+0.55%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Retail', vol: '5M', cap: '75B' },
  { name: 'Lowe\'s', symbol: 'LOW', price: '225.60', change: '+0.75%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Retail', vol: '4M', cap: '135B' },
  { name: 'Nike', symbol: 'NKE', price: '98.40', change: '+1.15%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '8M', cap: '151B' },
  { name: 'Coca-Cola', symbol: 'KO', price: '62.80', change: '+0.20%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '18M', cap: '270B' },
  { name: 'PepsiCo', symbol: 'PEP', price: '172.50', change: '+0.40%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '6M', cap: '238B' },
  { name: 'Procter & Gamble', symbol: 'PG', price: '168.90', change: '+0.35%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '7M', cap: '400B' },
  { name: 'Johnson & Johnson', symbol: 'JNJ', price: '158.40', change: '+0.30%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Healthcare', vol: '9M', cap: '420B' },
  { name: 'Pfizer', symbol: 'PFE', price: '27.80', change: '-0.50%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Healthcare', vol: '45M', cap: '158B' },
  { name: 'Merck', symbol: 'MRK', price: '128.60', change: '+0.55%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Healthcare', vol: '12M', cap: '326B' },
  { name: 'AbbVie', symbol: 'ABBV', price: '168.90', change: '+0.40%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Healthcare', vol: '8M', cap: '298B' },
  { name: 'UnitedHealth', symbol: 'UNH', price: '525.40', change: '+1.20%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Healthcare', vol: '4M', cap: '495B' },
  { name: 'Eli Lilly', symbol: 'LLY', price: '765.20', change: '+2.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Healthcare', vol: '3M', cap: '728B' },
  { name: 'Exxon Mobil', symbol: 'XOM', price: '118.50', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Oil & Gas', vol: '22M', cap: '495B' },
  { name: 'Chevron', symbol: 'CVX', price: '162.40', change: '+0.75%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Oil & Gas', vol: '12M', cap: '305B' },
  { name: 'ConocoPhillips', symbol: 'COP', price: '115.80', change: '+1.05%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Oil & Gas', vol: '8M', cap: '138B' },
  { name: 'Schlumberger', symbol: 'SLB', price: '52.40', change: '+0.95%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Oil & Gas', vol: '12M', cap: '75B' },
  { name: 'Halliburton', symbol: 'HAL', price: '38.60', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Oil & Gas', vol: '8M', cap: '35B' },
  { name: 'Caterpillar', symbol: 'CAT', price: '348.60', change: '+1.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '4M', cap: '175B' },
  { name: '3M', symbol: 'MMM', price: '98.50', change: '+0.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '5M', cap: '55B' },
  { name: 'General Electric', symbol: 'GE', price: '148.20', change: '+1.15%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '12M', cap: '162B' },
  { name: 'Honeywell', symbol: 'HON', price: '215.80', change: '+0.65%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '3M', cap: '145B' },
  { name: 'Deere', symbol: 'DE', price: '385.40', change: '+1.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '2M', cap: '108B' },
  { name: 'Union Pacific', symbol: 'UNP', price: '245.60', change: '+0.55%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '3M', cap: '145B' },
  { name: 'FedEx', symbol: 'FDX', price: '285.40', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '2M', cap: '72B' },
  { name: 'UPS', symbol: 'UPS', price: '165.80', change: '+0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '4M', cap: '145B' },
  { name: 'JPMorgan Chase', symbol: 'JPM', price: '185.40', change: '+0.55%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Banking', vol: '15M', cap: '540B' },
  { name: 'Bank of America', symbol: 'BAC', price: '38.50', change: '+0.40%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Banking', vol: '45M', cap: '305B' },
  { name: 'Wells Fargo', symbol: 'WFC', price: '58.20', change: '+0.30%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Banking', vol: '25M', cap: '215B' },
  { name: 'Goldman Sachs', symbol: 'GS', price: '425.80', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '3M', cap: '145B' },
  { name: 'Morgan Stanley', symbol: 'MS', price: '95.60', change: '+0.65%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '8M', cap: '175B' },
  { name: 'Citigroup', symbol: 'C', price: '62.40', change: '+0.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Banking', vol: '28M', cap: '120B' },
  { name: 'Charles Schwab', symbol: 'SCHW', price: '68.50', change: '+0.35%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '8M', cap: '125B' },
  { name: 'BlackRock', symbol: 'BLK', price: '825.40', change: '+0.55%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '0.5M', cap: '125B' },
  { name: 'Berkshire Hathaway', symbol: 'BRK.B', price: '385.60', change: '+0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '4M', cap: '875B' },
  { name: 'American Express', symbol: 'AXP', price: '225.80', change: '+0.65%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '3M', cap: '165B' },
  { name: 'Walmart', symbol: 'WMT', price: '165.30', change: '+0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Retail', vol: '8M', cap: '445B' },
  { name: 'Amazon', symbol: 'AMZN', price: '180.25', change: '+0.95%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Retail', vol: '38M', cap: '1.8T' },
  { name: 'Apple Inc.', symbol: 'AAPL', price: '173.50', change: '+1.20%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '55M', cap: '2.7T' },
  { name: 'Microsoft', symbol: 'MSFT', price: '420.55', change: '-0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '22M', cap: '3.1T' },
  { name: 'NVIDIA Corp', symbol: 'NVDA', price: '892.10', change: '+4.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '42M', cap: '2.2T' },
  { name: 'Google', symbol: 'GOOGL', price: '156.40', change: '-0.20%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '24M', cap: '1.9T' },
  { name: 'Meta Platforms', symbol: 'META', price: '495.10', change: '+1.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '18M', cap: '1.2T' },
  { name: 'Tesla Inc', symbol: 'TSLA', price: '175.30', change: '+2.10%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Automotive', vol: '95M', cap: '550B' },
  { name: 'Netflix', symbol: 'NFLX', price: '485.20', change: '+2.30%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '8M', cap: '215B' },
  { name: 'AMD', symbol: 'AMD', price: '142.50', change: '+3.15%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '65M', cap: '230B' },
  { name: 'Intel', symbol: 'INTC', price: '44.80', change: '+0.90%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '35M', cap: '185B' },
  { name: 'Qualcomm', symbol: 'QCOM', price: '145.60', change: '+1.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '12M', cap: '162B' },
  { name: 'Broadcom', symbol: 'AVGO', price: '1280.40', change: '+2.60%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '3M', cap: '590B' },
  { name: 'Oracle', symbol: 'ORCL', price: '118.25', change: '+0.75%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '18M', cap: '320B' },
  { name: 'Adobe', symbol: 'ADBE', price: '545.80', change: '+1.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '5M', cap: '248B' },
  { name: 'Snowflake', symbol: 'SNOW', price: '185.40', change: '+2.15%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '5M', cap: '58B' },
  { name: 'Palantir', symbol: 'PLTR', price: '25.60', change: '+3.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '45M', cap: '52B' },
  { name: 'Zoom', symbol: 'ZM', price: '68.50', change: '+1.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '5M', cap: '22B' },
  { name: 'Datadog', symbol: 'DDOG', price: '145.80', change: '+2.35%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '3M', cap: '48B' },
  { name: 'CrowdStrike', symbol: 'CRWD', price: '325.40', change: '+2.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '4M', cap: '78B' },
  { name: 'Zscaler', symbol: 'ZS', price: '185.60', change: '+1.95%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '2M', cap: '28B' },
  { name: 'Okta', symbol: 'OKTA', price: '95.40', change: '+1.65%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '3M', cap: '15B' },
  { name: 'Twilio', symbol: 'TWLO', price: '68.20', change: '+1.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '5M', cap: '12B' },
  { name: 'Shopify', symbol: 'SHOP', price: '78.40', change: '+2.15%', category: 'Equities', region: 'Americas', country: 'Canada', sector: 'Technology', vol: '8M', cap: '98B' },
  { name: 'Square', symbol: 'SQ', price: '68.50', change: '+1.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '12M', cap: '42B' },
  { name: 'Coinbase', symbol: 'COIN', price: '185.40', change: '+4.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '8M', cap: '45B' },
  { name: 'Robinhood', symbol: 'HOOD', price: '18.50', change: '+2.15%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '15M', cap: '16B' },
  { name: 'SoFi', symbol: 'SOFI', price: '8.50', change: '+1.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '45M', cap: '8B' },
  { name: 'Rivian', symbol: 'RIVN', price: '15.80', change: '+3.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Automotive', vol: '25M', cap: '15B' },
  { name: 'Lucid', symbol: 'LCID', price: '3.25', change: '+2.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Automotive', vol: '45M', cap: '7B' },
  { name: 'NIO', symbol: 'NIO', price: '5.80', change: '+1.95%', category: 'Equities', region: 'APAC', country: 'China', sector: 'Automotive', vol: '55M', cap: '12B' },
  { name: 'XPeng', symbol: 'XPEV', price: '8.50', change: '+2.15%', category: 'Equities', region: 'APAC', country: 'China', sector: 'Automotive', vol: '25M', cap: '8B' },
  { name: 'Li Auto', symbol: 'LI', price: '28.40', change: '+1.65%', category: 'Equities', region: 'APAC', country: 'China', sector: 'Automotive', vol: '12M', cap: '28B' },
  { name: 'Rivian', symbol: 'RIVN', price: '15.80', change: '+3.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Automotive', vol: '25M', cap: '15B' },
  { name: 'Lucid', symbol: 'LCID', price: '3.25', change: '+2.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Automotive', vol: '45M', cap: '7B' },
  
  // Дополнительные популярные акции - S&P 500 расширенный список
  { name: 'Costco', symbol: 'COST', price: '850.20', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Retail', vol: '2M', cap: '375B' },
  { name: 'Home Depot', symbol: 'HD', price: '385.60', change: '+0.65%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Retail', vol: '4M', cap: '385B' },
  { name: 'Visa', symbol: 'V', price: '285.40', change: '+0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '8M', cap: '585B' },
  { name: 'Mastercard', symbol: 'MA', price: '485.80', change: '+0.55%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '3M', cap: '425B' },
  { name: 'Salesforce', symbol: 'CRM', price: '285.40', change: '+1.15%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '8M', cap: '285B' },
  { name: 'Cisco', symbol: 'CSCO', price: '52.80', change: '+0.35%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '18M', cap: '215B' },
  { name: 'IBM', symbol: 'IBM', price: '185.60', change: '+0.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Technology', vol: '5M', cap: '168B' },
  { name: 'Disney', symbol: 'DIS', price: '112.40', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '15M', cap: '205B' },
  { name: 'Lockheed Martin', symbol: 'LMT', price: '485.20', change: '+0.95%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '1M', cap: '125B' },
  { name: 'Raytheon', symbol: 'RTX', price: '95.80', change: '+0.65%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '5M', cap: '145B' },
  { name: 'General Motors', symbol: 'GM', price: '42.60', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Automotive', vol: '18M', cap: '48B' },
  { name: 'Ford', symbol: 'F', price: '12.80', change: '+0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Automotive', vol: '45M', cap: '52B' },
  { name: 'Chipotle', symbol: 'CMG', price: '2850.40', change: '+1.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '0.3M', cap: '78B' },
  { name: 'Target', symbol: 'TGT', price: '165.20', change: '+0.55%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Retail', vol: '5M', cap: '75B' },
  { name: 'Lowe\'s', symbol: 'LOW', price: '225.60', change: '+0.75%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Retail', vol: '4M', cap: '135B' },
  { name: 'Charles Schwab', symbol: 'SCHW', price: '68.50', change: '+0.35%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '8M', cap: '125B' },
  { name: 'BlackRock', symbol: 'BLK', price: '825.40', change: '+0.55%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '0.5M', cap: '125B' },
  { name: 'Berkshire Hathaway', symbol: 'BRK.B', price: '385.60', change: '+0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '4M', cap: '875B' },
  { name: 'American Express', symbol: 'AXP', price: '225.80', change: '+0.65%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Finance', vol: '3M', cap: '165B' },
  { name: 'Honeywell', symbol: 'HON', price: '215.80', change: '+0.65%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '3M', cap: '145B' },
  { name: 'Deere', symbol: 'DE', price: '385.40', change: '+1.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '2M', cap: '108B' },
  { name: 'Union Pacific', symbol: 'UNP', price: '245.60', change: '+0.55%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '3M', cap: '145B' },
  { name: 'FedEx', symbol: 'FDX', price: '285.40', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '2M', cap: '72B' },
  { name: 'UPS', symbol: 'UPS', price: '165.80', change: '+0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '4M', cap: '145B' },
  { name: 'Schlumberger', symbol: 'SLB', price: '52.40', change: '+0.95%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Oil & Gas', vol: '12M', cap: '75B' },
  { name: 'Halliburton', symbol: 'HAL', price: '38.60', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Oil & Gas', vol: '8M', cap: '35B' },
  { name: 'NextEra Energy', symbol: 'NEE', price: '68.50', change: '+0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Utilities', vol: '8M', cap: '145B' },
  { name: 'Duke Energy', symbol: 'DUK', price: '102.40', change: '+0.35%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Utilities', vol: '5M', cap: '78B' },
  { name: 'Prologis', symbol: 'PLD', price: '125.60', change: '+0.55%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Real Estate', vol: '4M', cap: '125B' },
  { name: 'Freeport-McMoRan', symbol: 'FCX', price: '42.60', change: '+1.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Materials', vol: '18M', cap: '62B' },
  { name: 'Newmont', symbol: 'NEM', price: '42.80', change: '+0.85%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Materials', vol: '12M', cap: '52B' },
  { name: 'Northrop Grumman', symbol: 'NOC', price: '485.60', change: '+0.75%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '0.8M', cap: '75B' },
  { name: 'General Dynamics', symbol: 'GD', price: '285.40', change: '+0.55%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Industrial', vol: '1.2M', cap: '78B' },
  { name: 'Domino\'s', symbol: 'DPZ', price: '425.60', change: '+0.95%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '0.5M', cap: '15B' },
  { name: 'Yum Brands', symbol: 'YUM', price: '142.80', change: '+0.65%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Consumer', vol: '2M', cap: '38B' },
  { name: 'Marathon Petroleum', symbol: 'MPC', price: '185.40', change: '+1.15%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Oil & Gas', vol: '5M', cap: '68B' },
  { name: 'Valero Energy', symbol: 'VLO', price: '145.60', change: '+0.95%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Oil & Gas', vol: '6M', cap: '52B' },
  { name: 'Southern Company', symbol: 'SO', price: '72.80', change: '+0.25%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Utilities', vol: '6M', cap: '82B' },
  { name: 'Equity Residential', symbol: 'EQR', price: '62.40', change: '+0.45%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Real Estate', vol: '3M', cap: '25B' },
  { name: 'Simon Property', symbol: 'SPG', price: '145.80', change: '+0.65%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Real Estate', vol: '2M', cap: '48B' },
  { name: 'Southern Copper', symbol: 'SCCO', price: '85.40', change: '+1.15%', category: 'Equities', region: 'Americas', country: 'USA', sector: 'Materials', vol: '2M', cap: '68B' },

]);

// Получаем доступные регионы и страны
const availableRegions = computed(() => {
  const equities = allAssets.value.filter(a => a.category === 'Equities');
  const regions = new Set(equities.map(a => a.region).filter(Boolean));
  return Array.from(regions).sort();
});

const availableCountries = computed(() => {
  const equities = allAssets.value.filter(a => a.category === 'Equities');
  let filtered = equities;
  
  if (selectedRegion.value !== 'All') {
    filtered = filtered.filter(a => a.region === selectedRegion.value);
  }
  
  const countries = new Set(filtered.map(a => a.country).filter(Boolean));
  return Array.from(countries).sort();
});

const availableSectors = computed(() => {
  const equities = allAssets.value.filter(a => a.category === 'Equities');
  let filtered = equities;
  
  if (selectedRegion.value !== 'All') {
    filtered = filtered.filter(a => a.region === selectedRegion.value);
  }
  
  if (selectedCountry.value !== 'All') {
    filtered = filtered.filter(a => a.country === selectedCountry.value);
  }
  
  const sectors = new Set(filtered.map(a => a.sector).filter(Boolean));
  return Array.from(sectors).sort();
});


const filteredAssets = computed(() => {
  // Показываем только акции (Equities), исключаем индексы и криптовалюты
  let equities = allAssets.value.filter(a => a.category === 'Equities');
  
  // Фильтр по категории
  if (props.category !== 'All') {
    equities = equities.filter(a => a.category === props.category);
  }
  
  // Фильтр по региону
  if (selectedRegion.value !== 'All') {
    equities = equities.filter(a => a.region === selectedRegion.value);
  }
  
  // Фильтр по стране
  if (selectedCountry.value !== 'All') {
    equities = equities.filter(a => a.country === selectedCountry.value);
  }
  
  // Фильтр по сектору
  if (selectedSector.value !== 'All') {
    equities = equities.filter(a => a.sector === selectedSector.value);
  }
  
  // Применяем сортировку в зависимости от активного фильтра
  if (activeFilter.value === 'Топ роста') {
    equities = [...equities].sort((a, b) => {
      const aChange = parseFloat(a.change.replace('%', ''));
      const bChange = parseFloat(b.change.replace('%', ''));
      return bChange - aChange;
    });
  } else if (activeFilter.value === 'Топ падения') {
    equities = [...equities].sort((a, b) => {
      const aChange = parseFloat(a.change.replace('%', ''));
      const bChange = parseFloat(b.change.replace('%', ''));
      return aChange - bChange;
    });
  } else if (activeFilter.value === 'Высокий объём') {
    equities = [...equities].sort((a, b) => {
      const aVol = parseFloat(a.vol?.replace(/[MB]/g, '') || '0');
      const bVol = parseFloat(b.vol?.replace(/[MB]/g, '') || '0');
      return bVol - aVol;
    });
  }
  
  return equities;
});

const getRegionName = (region: string) => {
  const names: Record<string, string> = {
    'Americas': 'Америка',
    'EMEA': 'Европа, Ближний Восток, Африка',
    'APAC': 'Азия и Тихоокеанский регион',
  };
  return names[region] || region;
};

const getCountryName = (country: string) => {
  const names: Record<string, string> = {
    'USA': 'США',
    'UK': 'Великобритания',
    'Germany': 'Германия',
    'France': 'Франция',
    'Switzerland': 'Швейцария',
    'Netherlands': 'Нидерланды',
    'China': 'Китай',
    'Japan': 'Япония',
    'South Korea': 'Южная Корея',
    'Taiwan': 'Тайвань',
    'India': 'Индия',
    'Canada': 'Канада',
    'Australia': 'Австралия',
    'Russia': 'Россия',
  };
  return names[country] || country;
};

const clearFilters = () => {
  selectedRegion.value = 'All';
  selectedCountry.value = 'All';
  selectedSector.value = 'All';
};

const getSectorName = (sector: string) => {
  const names: Record<string, string> = {
    'Technology': 'Технологии',
    'Finance': 'Финансы',
    'Healthcare': 'Здравоохранение',
    'Energy': 'Энергетика',
    'Consumer': 'Потребительские товары',
    'Industrial': 'Промышленность',
    'Telecommunications': 'Телекоммуникации',
    'Materials': 'Материалы',
    'Real Estate': 'Недвижимость',
    'Utilities': 'Коммунальные услуги',
    'Oil & Gas': 'Нефть и газ',
    'Banking': 'Банковский сектор',
    'Retail': 'Розничная торговля',
    'Automotive': 'Автомобильная промышленность',
  };
  return names[sector] || sector;
};

const getLogoUrl = (symbol: string) => {
  // Если логотип уже не загрузился, не пытаемся загрузить снова
  if (logoErrors.value.has(symbol)) {
    return ''; // Пустая строка, чтобы не делать лишние запросы
  }
  
  // Убираем суффиксы типа .BSE, .NSE и т.д.
  const cleanSymbol = symbol.split('.')[0].toUpperCase();
  
  // Используем несколько источников логотипов
  // Источник 1: Публичный сервис для логотипов по тикеру (не требует API ключа)
  // Если этот источник не работает, будет использован fallback на инициалы
  const domain = getCompanyDomain(cleanSymbol);
  
  // Используем Clearbit для известных компаний, для остальных - альтернативный источник
  // ВАЖНО: Эти внешние сервисы могут быть недоступны, поэтому мы обрабатываем ошибки
  if (domain && (domain.includes('.com') || domain.includes('.ru') || domain.includes('.cn'))) {
    return `https://logo.clearbit.com/${domain}`;
  }
  
  // Альтернативный источник для тикеров напрямую
  // Если и этот не работает, вернется пустая строка и будет показан fallback
  return `https://assets.cdn.money.net/udata/images/logos/${cleanSymbol}.png`;
};

const getCompanyDomain = (symbol: string) => {
  // Маппинг тикеров на домены компаний для Clearbit
  const domainMap: Record<string, string> = {
    'AAPL': 'apple.com',
    'MSFT': 'microsoft.com',
    'GOOGL': 'google.com',
    'GOOG': 'google.com',
    'AMZN': 'amazon.com',
    'META': 'meta.com',
    'TSLA': 'tesla.com',
    'NVDA': 'nvidia.com',
    'NFLX': 'netflix.com',
    'AMD': 'amd.com',
    'INTC': 'intel.com',
    'QCOM': 'qualcomm.com',
    'AVGO': 'broadcom.com',
    'ORCL': 'oracle.com',
    'ADBE': 'adobe.com',
    'JPM': 'jpmorganchase.com',
    'BAC': 'bankofamerica.com',
    'WFC': 'wellsfargo.com',
    'GS': 'goldmansachs.com',
    'MS': 'morganstanley.com',
    'C': 'citi.com',
    'WMT': 'walmart.com',
    'PG': 'pg.com',
    'KO': 'coca-cola.com',
    'PEP': 'pepsico.com',
    'NKE': 'nike.com',
    'MCD': 'mcdonalds.com',
    'SBUX': 'starbucks.com',
    'JNJ': 'jnj.com',
    'PFE': 'pfizer.com',
    'MRK': 'merck.com',
    'ABBV': 'abbvie.com',
    'UNH': 'unitedhealthgroup.com',
    'LLY': 'lilly.com',
    'XOM': 'exxonmobil.com',
    'CVX': 'chevron.com',
    'COP': 'conocophillips.com',
    'BA': 'boeing.com',
    'CAT': 'caterpillar.com',
    'MMM': '3m.com',
    'GE': 'ge.com',
    'T': 'att.com',
    'VZ': 'verizon.com',
    'TMUS': 't-mobile.com',
    'BP': 'bp.com',
    'SHEL': 'shell.com',
    'AZN': 'astrazeneca.com',
    'UL': 'unilever.com',
    'DEO': 'diageo.com',
    'GSK': 'gsk.com',
    'VOD': 'vodafone.com',
    'SAP': 'sap.com',
    'SIEGY': 'siemens.com',
    'MBGYY': 'mercedes-benz.com',
    'BMWYY': 'bmw.com',
    'VWAGY': 'volkswagen.com',
    'ALIZY': 'allianz.com',
    'TTE': 'totalenergies.com',
    'LVMUY': 'lvmh.com',
    'LRLCY': 'loreal.com',
    'SNY': 'sanofi.com',
    'EADSY': 'airbus.com',
    'NSRGY': 'nestle.com',
    'NVS': 'novartis.com',
    'RHHBY': 'roche.com',
    'UBS': 'ubs.com',
    'ASML': 'asml.com',
    'UNLY': 'unilever.com',
    'ING': 'ing.com',
    'BABA': 'alibaba.com',
    'TCEHY': 'tencent.com',
    'JD': 'jd.com',
    'BIDU': 'baidu.com',
    'PNGAY': 'pingan.com',
    'IDCBY': 'icbc.com.cn',
    'CICHY': 'ccb.com',
    'BYDDY': 'byd.com',
    'TM': 'toyota.com',
    'SONY': 'sony.com',
    'SFTBY': 'softbank.com',
    'NTDOY': 'nintendo.com',
    'HMC': 'honda.com',
    'NSANY': 'nissan.com',
    'SSNLF': 'samsung.com',
    'HXSCL': 'skhynix.com',
    'LGEAF': 'lg.com',
    'TSM': 'tsmc.com',
    'SHOP': 'shopify.com',
    'RY': 'rbc.com',
    'CNI': 'cn.ca',
    'BHP': 'bhp.com',
    'RIO': 'riotinto.com',
    'CMWAY': 'commbank.com.au',
    // Российские компании
    'SBER': 'sberbank.ru',
    'GAZP': 'gazprom.ru',
    'LKOH': 'lukoil.ru',
    'ROSN': 'rosneft.ru',
    'GMKN': 'nornickel.com',
    'YNDX': 'yandex.ru',
    'MGNT': 'magnit.ru',
    'VTBR': 'vtb.ru',
    'TATN': 'tatneft.ru',
    'NVTK': 'novatek.ru',
    'SNGS': 'surgutneftegas.ru',
    'ALRS': 'alrosa.ru',
    'MTSS': 'mts.ru',
    'TRNFP': 'transneft.ru',
  };
  
  // Если тикер не найден в маппинге, возвращаем дефолтный домен
  // Это вызовет ошибку загрузки, и будет использован fallback на инициалы
  return domainMap[symbol] || `unknown-${symbol.toLowerCase()}.com`;
};

const handleLogoError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  const symbol = img.alt;
  // Добавляем символ в список ошибок, чтобы не пытаться загрузить снова
  logoErrors.value.add(symbol);
  // Скрываем изображение, чтобы не было видно битого изображения
  if (img) {
    img.style.display = 'none';
  }
};

const getCategoryStyle = (category: string) => {
  const styles: Record<string, string> = {
    'Crypto': 'bg-gradient-to-br from-orange-500/20 to-yellow-500/20 text-orange-400',
    'Indices': 'bg-gradient-to-br from-blue-500/20 to-cyan-500/20 text-blue-400',
    'FX': 'bg-gradient-to-br from-emerald-500/20 to-teal-500/20 text-emerald-400',
    'Equities': 'bg-gradient-to-br from-indigo-500/20 to-purple-500/20 text-indigo-400',
  };
  return styles[category] || 'bg-gradient-to-br from-purple-500/20 to-pink-500/20 text-purple-400';
};

const handleTrade = (asset: AssetInfo) => {
  emit('navigate', 'Main');
  emit('assetClick', asset);
};

// Icon components
const StarIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>' };
const TrendingUpIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
const TrendingDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>' };
const ArrowRightIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>' };
const ChevronDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>' };
</script>
