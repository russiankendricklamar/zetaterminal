<template>
  <div class="relative h-screen w-screen overflow-hidden bg-black text-white font-sans selection:bg-blue-500/30 selection:text-blue-200">
    <!-- Mesh Gradient Background -->
    <div class="fixed inset-0 z-0 pointer-events-none">
      <div class="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] bg-blue-950/40 blur-[120px] rounded-full mix-blend-screen animate-blob"></div>
      <div class="absolute top-[20%] right-[-10%] w-[40vw] h-[40vw] bg-orange-600/15 blur-[120px] rounded-full mix-blend-screen animate-blob animation-delay-2000"></div>
      <div class="absolute bottom-[-20%] left-[20%] w-[60vw] h-[60vw] bg-slate-900/20 blur-[100px] rounded-full mix-blend-screen animate-blob animation-delay-4000"></div>
      <div class="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150"></div>
    </div>

    <!-- Command Palette -->
    <CommandPalette 
      :isOpen="isSearchOpen" 
      @close="isSearchOpen = false" 
      @select="handleCommandSelect"
      :items="searchItems"
    />

    <!-- Main Content -->
    <div class="relative z-10 flex flex-col h-full p-4 gap-4">
      <!-- Header -->
      <header class="h-10 glass-panel rounded-xl flex items-center justify-between px-4 flex-shrink-0 transition-all duration-300 z-50">
        <div class="flex items-center gap-4 overflow-visible relative">
          <div class="flex items-center gap-2 text-white cursor-pointer flex-shrink-0" @click="view = 'Main'">
            <div class="p-1 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-md shadow-lg shadow-blue-500/20 flex items-center justify-center w-6 h-6">
              <span class="text-white font-bold text-sm">ζ</span>
            </div>
            <span class="font-bold tracking-tight text-sm bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400 hidden lg:block">Дзета-Терминал</span>
          </div>
          
          <!-- Navigation Dropdown -->
          <div class="relative z-50">
            <button 
              @click="isNavOpen = !isNavOpen"
              :class="`w-full flex items-center justify-center gap-2 px-2 py-1 rounded-lg border transition-all group ${isNavOpen ? 'bg-white/10 border-white/20 text-white' : 'bg-white/5 border-white/5 text-gray-300 hover:text-white hover:bg-white/10'}`"
            >
              <LayoutTemplateIcon class="w-3.5 h-3.5 text-indigo-400 flex-shrink-0"/>
              <span class="font-medium text-xs text-center flex-1">
                {{ navItems.find(i => i.id === view)?.label || view }}
              </span>
              <ChevronDownIcon :class="`w-3 h-3 text-gray-500 transition-transform duration-300 flex-shrink-0 ${isNavOpen ? 'rotate-180' : ''}`" />
            </button>

            <div v-if="isNavOpen" class="fixed inset-0 z-40 bg-black/20 backdrop-blur-[1px]" @click="isNavOpen = false"></div>
            <div v-if="isNavOpen" class="absolute top-full left-0 mt-3 w-72 bg-[#141419] border border-white/10 rounded-2xl shadow-2xl shadow-black/80 overflow-hidden z-50 animate-fade-in flex flex-col p-2 max-h-[80vh] overflow-y-auto">
              <div class="px-3 py-2 text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1 flex justify-between">
                <span>Навигация</span>
                <span>КОД</span>
              </div>
              <div class="grid grid-cols-1 gap-1">
                <button 
                  v-for="item in navItems"
                  :key="item.id"
                  @click="setView(item.id)"
                  :class="`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold transition-all text-left group ${view === item.id ? 'bg-indigo-500/10 text-indigo-300 border border-indigo-500/20' : 'text-gray-400 hover:text-white hover:bg-white/5 border border-transparent'}`"
                >
                  <component :is="item.icon" :class="view === item.id ? 'text-indigo-400' : 'text-gray-500 group-hover:text-white'" />
                  <span class="flex-1">{{ item.label }}</span>
                  <span :class="`font-mono text-[10px] px-1.5 py-0.5 rounded border ${view === item.id ? 'bg-indigo-500/20 border-indigo-500/30 text-indigo-300' : 'bg-white/5 border-white/5 text-gray-500 group-hover:text-gray-300'}`">
                    {{ item.code }}
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="flex items-center gap-4 flex-shrink-0">
          <div 
            @click="isSearchOpen = true"
            class="hidden xl:flex items-center gap-3 px-3 py-1 bg-black/30 rounded-lg border border-white/10 text-xs text-gray-500 cursor-pointer hover:bg-white/10 hover:text-white transition-colors group"
          >
            <SearchIcon class="w-3.5 h-3.5" />
            <span>Поиск</span>
            <div class="flex items-center gap-1 ml-6 text-[11px] text-gray-500 group-hover:text-gray-300 transition-colors">
              <span>⌘</span><span>K</span>
            </div>
          </div>

          <div class="h-4 w-[1px] bg-white/10 mx-1 hidden md:block"></div>

          <button 
            @click="isAiOpen = !isAiOpen"
            :class="`hidden md:block relative group px-3 py-1 rounded-lg text-xs font-medium transition-all duration-300 border ${isAiOpen ? 'bg-blue-500/20 border-blue-400/30 text-blue-300 shadow-[0_0_20px_rgba(59,130,246,0.3)]' : 'bg-white/5 border-white/10 text-gray-400 hover:text-white'}`"
          >
            <span class="relative z-10 flex items-center gap-2">
              Spark AI
              <span v-if="isAiOpen" class="absolute top-0 right-0 -mt-1 -mr-1 flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
              </span>
            </span>
          </button>
          
          <!-- Profile Dropdown -->
          <div class="relative">
            <button 
              @click="isProfileOpen = !isProfileOpen"
              class="w-6 h-6 rounded-full bg-gradient-to-br from-gray-100 to-gray-300 shadow-inner border border-white/20 hover:scale-105 transition-transform flex items-center justify-center"
            >
            </button>

            <div v-if="isProfileOpen" class="absolute top-12 right-0 w-72 bg-[#141419] rounded-2xl shadow-2xl shadow-black/80 overflow-hidden flex flex-col animate-fade-in z-[100] border border-white/10 max-h-[80vh]">
              <!-- User Header -->
              <div class="p-4 border-b border-white/5 bg-white/5 relative overflow-hidden flex-shrink-0">
                <div class="absolute top-0 right-0 -mt-4 -mr-4 w-16 h-16 bg-blue-500/20 blur-xl rounded-full"></div>
                <div class="relative z-10 flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-gray-100 to-gray-400 shadow-inner flex items-center justify-center text-black font-bold text-xs">AT</div>
                  <div>
                    <div class="font-bold text-white text-sm">Алексей Трейдер</div>
                    <div class="text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20 inline-block mt-0.5">Pro Аккаунт</div>
                  </div>
                </div>
              </div>
              
              <div class="p-2 space-y-1">
                <button 
                  @click="$router.push('/profile'); isProfileOpen = false"
                  class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium text-gray-300 hover:bg-white/5 hover:text-white transition-colors text-left group"
                >
                  <div class="p-1.5 rounded-lg bg-purple-500/20 text-purple-400 group-hover:bg-purple-500/30 transition-colors">
                    <UserIcon class="w-3.5 h-3.5" />
                  </div>
                  Профиль
                </button>
                <button 
                  @click="setView('Settings'); isProfileOpen = false"
                  class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium text-gray-300 hover:bg-white/5 hover:text-white transition-colors text-left group"
                >
                  <div class="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400 group-hover:bg-indigo-500/30 transition-colors">
                    <SettingsIcon class="w-3.5 h-3.5" />
                  </div>
                  Настройки
                </button>
                <button 
                  @click="resourcesSection = 'HL'; setView('Resources'); isProfileOpen = false"
                  class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium text-gray-300 hover:bg-white/5 hover:text-white transition-colors text-left group"
                >
                  <div class="p-1.5 rounded-lg bg-teal-500/20 text-teal-400 group-hover:bg-teal-500/30 transition-colors">
                    <HelpCircleIcon class="w-3.5 h-3.5" />
                  </div>
                  Помощь
                </button>
                <button 
                  @click="resourcesSection = 'FLDS'; setView('Resources'); isProfileOpen = false"
                  class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium text-gray-300 hover:bg-white/5 hover:text-white transition-colors text-left group"
                >
                  <div class="p-1.5 rounded-lg bg-blue-500/20 text-blue-400 group-hover:bg-blue-500/30 transition-colors">
                    <DatabaseIcon class="w-3.5 h-3.5" />
                  </div>
                  Справочник данных
                </button>
              </div>

              <div class="p-2 border-t border-white/5">
                <button 
                  @click="$router.push('/'); isProfileOpen = false"
                  class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium text-rose-400 hover:bg-rose-500/10 transition-colors text-left group"
                >
                  <div class="p-1.5 rounded-lg bg-rose-500/10 text-rose-400 group-hover:bg-rose-500/20 transition-colors">
                    <LogOutIcon class="w-3.5 h-3.5" />
                  </div>
                  Выйти
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Dynamic View Content -->
      <DashboardPage 
        v-if="view === 'Main'"
        :orderBook="orderBook"
        :currentPrice="currentPrice"
        :chartData="data"
        :symbol="activeSymbol"
      />

      <!-- Markets Page (Stocks) -->
      <MarketsPage 
        v-else-if="view === 'Markets'" 
        :category="marketCategory"
        @navigate="setView"
        @assetClick="handleAssetClick"
      />

      <!-- Crypto Page -->
      <CryptoPage 
        v-else-if="view === 'Crypto'" 
        @navigate="setView"
        @assetClick="handleAssetClick"
      />

      <!-- News Page -->
      <NewsPage 
        v-else-if="view === 'News'" 
        :activeSection="newsSection"
      />

      <!-- Analytics Page -->
      <AnalyticsPage 
        v-else-if="view === 'Analytics'" 
        :activeSection="analyticsSection"
      />

      <!-- Screening Page -->
      <ScreeningPage 
        v-else-if="view === 'Screening'" 
        :symbol="activeSymbol"
        :activeSection="screeningSection"
      />

      <!-- Fundamental Analysis Page -->
      <FundamentalAnalysisPage 
        v-else-if="view === 'Fundamental'" 
        :symbol="activeSymbol"
        :activeSection="fundamentalSection"
      />

      <!-- Price Analysis Page -->
      <PriceAnalysisPage 
        v-else-if="view === 'PriceAnalysis'" 
        :symbol="activeSymbol"
        :activeSection="priceAnalysisSection"
      />

      <!-- FX Page -->
      <FXPage 
        v-else-if="view === 'FX'" 
        :symbol="activeSymbol"
        :activeSection="fxSection"
      />

      <!-- Settings Page -->
      <SettingsPage 
        v-else-if="view === 'Settings'" 
        :activeSection="settingsSection"
      />

      <!-- Bond Market Page -->
      <BondMarketPage 
        v-else-if="view === 'Bonds'" 
        :activeSection="bondsSection"
      />

      <!-- Central Banks Page -->
      <CentralBanksPage 
        v-else-if="view === 'CentralBanks'" 
        :activeSection="centralBanksSection"
      />

      <!-- Commodities Page -->
      <CommoditiesPage 
        v-else-if="view === 'Commodities'" 
        :symbol="activeSymbol"
        :activeSection="commoditiesSection"
      />

      <!-- Credit Risk Page -->
      <CreditRiskPage 
        v-else-if="view === 'CreditRisk'" 
        :symbol="activeSymbol"
        :activeSection="creditRiskSection"
      />

      <!-- Earn Page -->
      <EarnPage 
        v-else-if="view === 'Earn'" 
        :activeSection="earnSection"
      />

      <!-- Event Driven Page -->
      <EventDrivenPage 
        v-else-if="view === 'EventDriven'" 
        :symbol="activeSymbol"
        :activeSection="eventDrivenSection"
      />

      <!-- Finance Page -->
      <FinancePage 
        v-else-if="view === 'Finance'" 
        @asset-click="handleAssetClick"
      />

      <!-- Fixed Income Page -->
      <FixedIncomePage 
        v-else-if="view === 'FixedIncome'" 
        :activeSection="fixedIncomeSection"
      />

      <!-- Futures Page -->
      <FuturesPage 
        v-else-if="view === 'Futures'" 
        :symbol="activeSymbol"
        :activeSection="futuresSection"
      />

      <!-- Indices Page -->
      <IndicesPage 
        v-else-if="view === 'Indices'" 
        :activeSection="indicesSection"
      />

      <!-- Macroeconomics Page -->
      <MacroeconomicsPage 
        v-else-if="view === 'Macro'" 
        :activeSection="macroSection"
      />

      <!-- Options Page -->
      <OptionsPage 
        v-else-if="view === 'Options'" 
        :symbol="activeSymbol"
        :activeSection="optionsSection"
      />

      <!-- Research Page -->
      <ResearchPage 
        v-else-if="view === 'Research'" 
        :symbol="activeSymbol"
        :activeSection="researchSection"
      />

      <!-- Resources Page -->
      <ResourcesPage 
        v-else-if="view === 'Resources'" 
        :activeSection="resourcesSection"
      />

      <!-- Swaps Page -->
      <SwapsPage 
        v-else-if="view === 'Swaps'" 
        :symbol="activeSymbol"
        :activeSection="swapsSection"
      />

      <!-- Default placeholder -->
      <div v-else class="flex-1 flex items-center justify-center glass-panel rounded-3xl">
        <div class="text-center">
          <h2 class="text-2xl font-bold text-white mb-2">{{ view }} View</h2>
          <p class="text-gray-400">Этот раздел будет реализован в ближайшее время</p>
        </div>
      </div>
    </div>

    <!-- Asset Detail Modal -->
    <AssetDetailModal 
      v-if="selectedAsset"
      :asset="selectedAsset"
      @close="selectedAsset = null"
      @trade="handleTradeFromModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { Candle, OrderBookItem, SearchResult, AssetInfo } from '@/types/terminal';
import { generateCandles, generateOrderBook, INITIAL_PRICE } from '@/utils/terminalConstants';
import ChartWidget from '@/components/terminal/ChartWidget.vue';
import OrderBook from '@/components/terminal/OrderBook.vue';
import TradeForm from '@/components/terminal/TradeForm.vue';
import AIPanel from '@/components/terminal/AIPanel.vue';
import FooterPanel from '@/components/terminal/FooterPanel.vue';
import CommandPalette from '@/components/terminal/CommandPalette.vue';
import MarketsPage from '@/components/terminal/MarketsPage.vue';
import CryptoPage from '@/components/terminal/CryptoPage.vue';
import NewsPage from '@/components/terminal/NewsPage.vue';
import AnalyticsPage from '@/components/terminal/AnalyticsPage.vue';
import ScreeningPage from '@/components/terminal/ScreeningPage.vue';
import FundamentalAnalysisPage from '@/components/terminal/FundamentalAnalysisPage.vue';
import PriceAnalysisPage from '@/components/terminal/PriceAnalysisPage.vue';
import FXPage from '@/components/terminal/FXPage.vue';
import SettingsPage from '@/components/terminal/SettingsPage.vue';
import AssetDetailModal from '@/components/terminal/AssetDetailModal.vue';
import BondMarketPage from '@/components/terminal/BondMarketPage.vue';
import CentralBanksPage from '@/components/terminal/CentralBanksPage.vue';
import CommoditiesPage from '@/components/terminal/CommoditiesPage.vue';
import CreditRiskPage from '@/components/terminal/CreditRiskPage.vue';
import EarnPage from '@/components/terminal/EarnPage.vue';
import EventDrivenPage from '@/components/terminal/EventDrivenPage.vue';
import FinancePage from '@/components/terminal/FinancePage.vue';
import FixedIncomePage from '@/components/terminal/FixedIncomePage.vue';
import FuturesPage from '@/components/terminal/FuturesPage.vue';
import IndicesPage from '@/components/terminal/IndicesPage.vue';
import MacroeconomicsPage from '@/components/terminal/MacroeconomicsPage.vue';
import OptionsPage from '@/components/terminal/OptionsPage.vue';
import ResearchPage from '@/components/terminal/ResearchPage.vue';
import ResourcesPage from '@/components/terminal/ResourcesPage.vue';
import SwapsPage from '@/components/terminal/SwapsPage.vue';
import DashboardPage from '@/components/terminal/DashboardPage.vue';

// State
const data = ref<Candle[]>([]);
const currentPrice = ref(INITIAL_PRICE);
const orderBook = ref<{ bids: OrderBookItem[], asks: OrderBookItem[] }>({ bids: [], asks: [] });
const isAiOpen = ref(true);
const view = ref('Main');
const history = ref<string[]>(['Main']);
const isNavOpen = ref(false);
const isSearchOpen = ref(false);
const isChartExpanded = ref(false);
const isProfileOpen = ref(false);
const activeSymbol = ref('BTC/USDT');
const selectedAsset = ref<AssetInfo | null>(null);

const layout = ref({
  showOrderBook: true,
  showTradeForm: true,
  showFooter: true
});

// Page sections
const marketCategory = ref('All');
const newsSection = ref('TOP');
const analyticsSection = ref<'AI' | 'Quant' | 'Finance'>('AI');
const screeningSection = ref('EQS');
const fundamentalSection = ref('EE');
const priceAnalysisSection = ref('HP');
const fxSection = ref('FXC');
const settingsSection = ref('BLP');
const bondsSection = ref('GOVT');
const centralBanksSection = ref('FOMC');
const commoditiesSection = ref('CMDX');
const creditRiskSection = ref('SRSK');
const earnSection = ref('EARN');
const eventDrivenSection = ref('IPO');
const fixedIncomeSection = ref('YAS');
const futuresSection = ref('CTRK');
const indicesSection = ref('WEI');
const macroSection = ref('ECOD');
const optionsSection = ref('OMON');
const researchSection = ref('RES');
const resourcesSection = ref('FLDS');
const swapsSection = ref('SWPM');

// Navigation items
const navItems = [
  { id: 'Main', label: 'Главная', icon: 'ActivityIcon', code: 'HOME' },
  { id: 'Markets', label: 'Акции', icon: 'GlobeIcon', code: 'MKT' },
  { id: 'Crypto', label: 'Криптовалюты', icon: 'ActivityIcon', code: 'CRYPTO' },
  { id: 'PriceAnalysis', label: 'Анализ цен', icon: 'TrendingUpIcon', code: 'GP' },
  { id: 'Screening', label: 'Скрининг', icon: 'FilterIcon', code: 'EQS' },
  { id: 'Analytics', label: 'Аналитика', icon: 'PieChartIcon', code: 'QUA' },
  { id: 'News', label: 'Новости', icon: 'WifiIcon', code: 'TOP' },
  { id: 'Fundamental', label: 'Фундаментальный анализ', icon: 'SearchIcon', code: 'EE' },
  { id: 'FX', label: 'Валютный рынок', icon: 'DollarSignIcon', code: 'FX' },
  { id: 'Bonds', label: 'Облигации', icon: 'ActivityIcon', code: 'GOVT' },
  { id: 'CentralBanks', label: 'Центробанки', icon: 'DatabaseIcon', code: 'FOMC' },
  { id: 'Commodities', label: 'Сырьё', icon: 'TrendingUpIcon', code: 'CMDX' },
  { id: 'CreditRisk', label: 'Кредитный риск', icon: 'FilterIcon', code: 'SRSK' },
  { id: 'Earn', label: 'Доходность', icon: 'PieChartIcon', code: 'EARN' },
  { id: 'EventDriven', label: 'События', icon: 'WifiIcon', code: 'IPO' },
  { id: 'Finance', label: 'Финансы', icon: 'DatabaseIcon', code: 'PORT' },
  { id: 'FixedIncome', label: 'Фикс. доход', icon: 'ActivityIcon', code: 'YAS' },
  { id: 'Futures', label: 'Фьючерсы', icon: 'TrendingUpIcon', code: 'CTRK' },
  { id: 'Indices', label: 'Индексы', icon: 'PieChartIcon', code: 'WEI' },
  { id: 'Macro', label: 'Макроэкономика', icon: 'DatabaseIcon', code: 'ECOD' },
  { id: 'Options', label: 'Опционы', icon: 'FilterIcon', code: 'OMON' },
  { id: 'Research', label: 'Исследования', icon: 'SearchIcon', code: 'RES' },
  { id: 'Swaps', label: 'Свопы', icon: 'ActivityIcon', code: 'SWPM' },
];

// System Commands
const systemCommands: SearchResult[] = [
  { id: 'HOME', label: 'Главная', code: 'HOME', type: 'command', description: 'Вернуться на главный экран' },
  { id: 'MKT', label: 'Акции', code: 'MKT', type: 'command', description: 'Акции и индексы' },
  { id: 'CRYPTO', label: 'Криптовалюты', code: 'CRYPTO', type: 'command', description: 'Криптовалютные активы' },
  { id: 'TOP', label: 'Новости', code: 'TOP', type: 'command', description: 'Главные новости по важности' },
  { id: 'GP', label: 'График цен', code: 'GP', type: 'command', description: 'Технический анализ с индикаторами' },
  { id: 'EQS', label: 'Скрининг акций', code: 'EQS', type: 'command', description: 'Фильтрация компаний по параметрам' },
  { id: 'QUA', label: 'Квант-анализ', code: 'QUA', type: 'command', description: 'Количественные метрики и риски' },
  { id: 'EE', label: 'Прогноз прибыли', code: 'EE', type: 'command', description: 'Прогнозы на 1-2 года' },
  { id: 'FX', label: 'Валютный рынок', code: 'FX', type: 'command', description: 'Валютные курсы и анализ' },
  { id: 'GOVT', label: 'Облигации', code: 'GOVT', type: 'command', description: 'Гос. и корпоративные облигации' },
  { id: 'FOMC', label: 'Центробанки', code: 'FOMC', type: 'command', description: 'Монетарная политика и ставки' },
  { id: 'CMDX', label: 'Сырьё', code: 'CMDX', type: 'command', description: 'Энергия, металлы, агрокультуры' },
  { id: 'SRSK', label: 'Кредитный риск', code: 'SRSK', type: 'command', description: 'Рейтинги и CDS анализ' },
  { id: 'EARN', label: 'Доходность', code: 'EARN', type: 'command', description: 'Стейкинг и фарминг' },
  { id: 'IPO', label: 'События', code: 'IPO', type: 'command', description: 'IPO и корпоративные действия' },
  { id: 'PORT', label: 'Финансы', code: 'PORT', type: 'command', description: 'Обзор портфеля' },
  { id: 'YAS', label: 'Фикс. доход', code: 'YAS', type: 'command', description: 'Анализ доходности и спредов' },
  { id: 'CTRK', label: 'Фьючерсы', code: 'CTRK', type: 'command', description: 'Фьючерсные контракты и роллы' },
  { id: 'WEI', label: 'Индексы', code: 'WEI', type: 'command', description: 'Мировые индексы' },
  { id: 'ECOD', label: 'Макроэкономика', code: 'ECOD', type: 'command', description: 'Экономические данные и прогнозы' },
  { id: 'OMON', label: 'Опционы', code: 'OMON', type: 'command', description: 'Опционные цепочки и греки' },
  { id: 'RES', label: 'Исследования', code: 'RES', type: 'command', description: 'Инвестиционные исследования' },
  { id: 'FLDS', label: 'Ресурсы', code: 'FLDS', type: 'command', description: 'Справочник данных и помощь' },
  { id: 'SWPM', label: 'Свопы', code: 'SWPM', type: 'command', description: 'Ценообразование IRS и CDS' },
  { id: 'SET', label: 'Настройки', code: 'SET', type: 'command', description: 'Настройка терминала' },
];

// Assets
const allAssets = [
  'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT',
  'AAPL', 'TSLA', 'NVDA', 'AMD', 'MSFT', 'GOOGL', 'AMZN',
  'EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD',
  'GOLD', 'SILVER', 'OIL'
];

const searchItems = computed(() => [
  ...systemCommands
]);

const setView = (newView: string) => {
  history.value = [newView, ...history.value].slice(0, 9);
  view.value = newView;
  isNavOpen.value = false; // Закрываем меню при переключении страницы
};

const setActiveSymbol = (symbol: string) => {
  activeSymbol.value = symbol;
  data.value = generateCandles(100);
  orderBook.value = generateOrderBook(currentPrice.value);
};

const handleCommandSelect = (item: SearchResult) => {
  if (item.type === 'command') {
    const code = item.code || '';
    if (code === 'HOME') { setView('Main'); isSearchOpen.value = false; return; }
    if (code === 'TOP') { setView('News'); isSearchOpen.value = false; return; }
    if (code === 'GP') { setView('PriceAnalysis'); isSearchOpen.value = false; return; }
    if (code === 'EQS') { setView('Screening'); isSearchOpen.value = false; return; }
    if (code === 'QUA') { setView('Analytics'); isSearchOpen.value = false; return; }
    if (code === 'EE') { setView('Fundamental'); isSearchOpen.value = false; return; }
    if (code === 'FX') { setView('FX'); isSearchOpen.value = false; return; }
    if (code === 'SET') { setView('Settings'); isSearchOpen.value = false; return; }
    if (code === 'MKT') { setView('Markets'); isSearchOpen.value = false; return; }
    if (code === 'CRYPTO') { setView('Crypto'); isSearchOpen.value = false; return; }
    if (code === 'GOVT') { setView('Bonds'); isSearchOpen.value = false; return; }
    if (code === 'FOMC') { setView('CentralBanks'); isSearchOpen.value = false; return; }
    if (code === 'CMDX') { setView('Commodities'); isSearchOpen.value = false; return; }
    if (code === 'SRSK') { setView('CreditRisk'); isSearchOpen.value = false; return; }
    if (code === 'EARN') { setView('Earn'); isSearchOpen.value = false; return; }
    if (code === 'IPO') { setView('EventDriven'); isSearchOpen.value = false; return; }
    if (code === 'PORT') { setView('Finance'); isSearchOpen.value = false; return; }
    if (code === 'YAS') { setView('FixedIncome'); isSearchOpen.value = false; return; }
    if (code === 'CTRK') { setView('Futures'); isSearchOpen.value = false; return; }
    if (code === 'WEI') { setView('Indices'); isSearchOpen.value = false; return; }
    if (code === 'ECOD') { setView('Macro'); isSearchOpen.value = false; return; }
    if (code === 'OMON') { setView('Options'); isSearchOpen.value = false; return; }
    if (code === 'RES') { setView('Research'); isSearchOpen.value = false; return; }
    if (code === 'FLDS') { setView('Resources'); isSearchOpen.value = false; return; }
    if (code === 'SWPM') { setView('Swaps'); isSearchOpen.value = false; return; }
  }
};

const handleAssetClick = (asset: AssetInfo) => {
  selectedAsset.value = asset;
};

const handleTradeFromModal = (symbol: string) => {
  setActiveSymbol(symbol);
  setView('Main');
};

// Command Palette Keyboard Listener
onMounted(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      isSearchOpen.value = !isSearchOpen.value;
    }
  };
  document.addEventListener('keydown', handleKeyDown);
  
  // Initialize data
  data.value = generateCandles(100);
  orderBook.value = generateOrderBook(INITIAL_PRICE);
  
  let tickCount = 0;
  
  // Price update interval - быстрое обновление цены
  const interval = setInterval(() => {
    const change = (Math.random() - 0.5) * 30;
    currentPrice.value = currentPrice.value + change;
    orderBook.value = generateOrderBook(currentPrice.value);
    
    tickCount++;
    
    // Каждые 3 секунды добавляем новую свечу и сдвигаем график
    if (tickCount >= 3) {
      tickCount = 0;
      
      // Создаём новую свечу
      const lastCandle = data.value[data.value.length - 1];
      const now = new Date();
      const newCandle = {
        time: `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`,
        open: lastCandle.close,
        high: currentPrice.value + Math.random() * 20,
        low: currentPrice.value - Math.random() * 20,
        close: currentPrice.value,
        volume: 0.5 + Math.random() * 2
      };
      
      // Удаляем первую свечу и добавляем новую в конец
      data.value = [...data.value.slice(1), newCandle];
    } else {
      // Обновляем только последнюю свечу
      data.value = data.value.map((candle, i, arr) => {
        if (i === arr.length - 1) {
          return {
            ...candle,
            close: currentPrice.value,
            high: Math.max(candle.high, currentPrice.value),
            low: Math.min(candle.low, currentPrice.value),
            volume: candle.volume + Math.random() * 0.1
          };
        }
        return candle;
      });
    }
  }, 1000);
  
  onBeforeUnmount(() => {
    document.removeEventListener('keydown', handleKeyDown);
    clearInterval(interval);
  });
});

watch(() => activeSymbol.value, () => {
  data.value = generateCandles(100);
  orderBook.value = generateOrderBook(currentPrice.value);
});

// Icon components
const ActivityIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>' };
const LayoutTemplateIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>' };
const ChevronDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>' };
const SearchIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>' };
const CommandIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 3a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3H6a3 3 0 0 0-3 3 3 3 0 0 0 3 3 3 3 0 0 0 3-3V6a3 3 0 0 0-3-3 3 3 0 0 0-3 3 3 3 0 0 0 3 3h12a3 3 0 0 0-3-3z"/></svg>' };
const TrendingUpIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
const FilterIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>' };
const PieChartIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>' };
const WifiIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>' };
const SettingsIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 6v6m9-9h-6m-6 0H3m15.364 6.364l-4.243-4.243m-4.242 0L5.636 18.364m12.728 0l-4.243-4.243m-4.242 0L5.636 5.636"/></svg>' };
const HelpCircleIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>' };
const DatabaseIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>' };
const LogOutIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>' };
const UserIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' };
</script>

<style scoped>
/* Glass Panel - matching original design */
.glass-panel {
  background: rgba(30, 30, 40, 0.4);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}

@keyframes blob {
  0%, 100% { 
    transform: translate(0px, 0px) scale(1); 
  }
  33% { 
    transform: translate(30px, -50px) scale(1.1); 
  }
  66% { 
    transform: translate(-20px, 20px) scale(0.9); 
  }
}

.animate-blob {
  animation: blob 7s infinite ease-in-out;
  will-change: transform;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

.animate-fade-in {
  animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity, transform;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Custom scrollbar - переопределение для терминала */
:deep(.custom-scrollbar) {
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

:deep(.custom-scrollbar)::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

:deep(.custom-scrollbar)::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 10px;
}

:deep(.custom-scrollbar)::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  transition: background 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
  background-clip: padding-box;
}

:deep(.custom-scrollbar)::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.custom-scrollbar)::-webkit-scrollbar-thumb:active {
  background: rgba(255, 255, 255, 0.35);
}
</style>
