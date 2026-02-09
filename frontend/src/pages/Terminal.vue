<template>
  <div class="terminal-root">
    <!-- Noise Overlay -->
    <div class="bg-noise"></div>

    <!-- Command Palette -->
    <CommandPalette 
      :isOpen="isSearchOpen" 
      @close="isSearchOpen = false" 
      @select="handleCommandSelect"
      :items="searchItems"
    />

    <!-- Main Content -->
    <div class="terminal-content">
      <!-- Windows Tabs Bar -->
      <div class="tabs-bar">
        <div
          v-for="window in windows"
          :key="window.id"
          @click="setActiveWindow(window.id)"
          :class="['tab-item', { 'tab-active': activeWindowId === window.id }]"
        >
          <component :is="getWindowIcon(window.view)" class="w-3.5 h-3.5" />
          <span class="tab-label font-mono">{{ getWindowTitle(window.view) }}</span>
          <button
            v-if="windows.length > 1"
            @click.stop="closeWindow(window.id)"
            class="tab-close"
          >
            <XIcon class="w-3 h-3" />
          </button>
        </div>
        <button
          @click="() => openNewWindow()"
          class="tab-new"
          title="Открыть новое окно"
        >
          <PlusIcon class="w-3.5 h-3.5" />
          <span class="font-mono">Новое окно</span>
        </button>
      </div>

      <!-- Header -->
      <header class="terminal-header">
        <div class="header-left">
          <div class="logo-area" @click="view = 'Main'">
            <div class="logo-icon">
              <span class="font-oswald">ζ</span>
            </div>
            <span class="logo-text font-oswald hidden lg:block">ДЗЕТА-ТЕРМИНАЛ</span>
          </div>

          <!-- Navigation Dropdown -->
          <div class="nav-dropdown-wrapper">
            <button
              @click="isNavOpen = !isNavOpen"
              :class="['nav-dropdown-trigger', { 'is-open': isNavOpen }]"
            >
              <LayoutTemplateIcon class="w-3.5 h-3.5 text-[#DC2626]" />
              <span class="font-mono">{{ navItems.find(i => i.id === view)?.label || view }}</span>
              <ChevronDownIcon :class="['w-3 h-3 transition-transform', { 'rotate-180': isNavOpen }]" />
            </button>

            <div v-if="isNavOpen" class="nav-overlay" @click="isNavOpen = false"></div>
            <div v-if="isNavOpen" class="nav-dropdown">
              <div class="nav-dropdown-header font-mono">
                <span>НАВИГАЦИЯ</span>
                <span>КОД</span>
              </div>
              <div class="nav-dropdown-list custom-scrollbar">
                <button
                  v-for="item in navItems"
                  :key="item.id"
                  @click="setView(item.id)"
                  :class="['nav-item', { 'nav-item-active': view === item.id }]"
                >
                  <component :is="iconMap[item.icon] || ActivityIcon" class="w-4 h-4" />
                  <span class="nav-item-label font-oswald">{{ item.label }}</span>
                  <span class="nav-item-code font-mono">{{ item.code }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="header-right">
          <div
            @click="isSearchOpen = true"
            class="search-trigger hidden xl:flex"
          >
            <SearchIcon class="w-3.5 h-3.5" />
            <span class="font-mono">Поиск</span>
            <div class="search-hotkey font-mono">⌘K</div>
          </div>

          <div class="header-divider hidden md:block"></div>

          <button
            @click="isAiOpen = !isAiOpen"
            :class="['ai-btn hidden md:flex', { 'ai-btn-active': isAiOpen }]"
          >
            <span class="font-oswald">SPARK AI</span>
            <span v-if="isAiOpen" class="ai-indicator"></span>
          </button>

          <!-- Profile Dropdown -->
          <div class="profile-wrapper">
            <button
              @click="isProfileOpen = !isProfileOpen"
              class="profile-avatar font-oswald"
            >
              AT
            </button>

            <div v-if="isProfileOpen" class="profile-dropdown">
              <!-- User Header -->
              <div class="profile-header">
                <div class="profile-avatar-lg font-oswald">AT</div>
                <div class="profile-info">
                  <div class="profile-name font-oswald">АЛЕКСЕЙ ТРЕЙДЕР</div>
                  <div class="profile-badge font-mono">PRO АККАУНТ</div>
                </div>
              </div>

              <div class="profile-menu">
                <button
                  @click="$router.push('/profile'); isProfileOpen = false"
                  class="profile-menu-item"
                >
                  <UserIcon class="w-4 h-4" />
                  <span class="font-oswald">Профиль</span>
                </button>
                <button
                  @click="setView('Settings'); isProfileOpen = false"
                  class="profile-menu-item"
                >
                  <SettingsIcon class="w-4 h-4" />
                  <span class="font-oswald">Настройки</span>
                </button>
                <button
                  @click="resourcesSection = 'HL'; setView('Resources'); isProfileOpen = false"
                  class="profile-menu-item"
                >
                  <HelpCircleIcon class="w-4 h-4" />
                  <span class="font-oswald">Помощь</span>
                </button>
                <button
                  @click="resourcesSection = 'FLDS'; setView('Resources'); isProfileOpen = false"
                  class="profile-menu-item"
                >
                  <DatabaseIcon class="w-4 h-4" />
                  <span class="font-oswald">Справочник данных</span>
                </button>
              </div>

              <div class="profile-footer">
                <button
                  @click="$router.push('/'); isProfileOpen = false"
                  class="profile-logout"
                >
                  <LogOutIcon class="w-4 h-4" />
                  <span class="font-oswald">Выйти</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Dynamic View Content (Multi-Window Support) -->
      <div class="flex-1 overflow-y-auto min-h-0 custom-scrollbar">
        <div
          v-for="window in windows"
          :key="window.id"
          v-show="activeWindowId === window.id"
          class="w-full min-h-full"
        >
          <DashboardPage 
            v-if="window.view === 'Main'"
            :orderBook="orderBook"
            :currentPrice="currentPrice"
            :chartData="data"
            :symbol="activeSymbol"
          />

          <!-- Markets Page (Stocks) -->
          <MarketsPage 
            v-else-if="window.view === 'Markets'" 
            :category="marketCategory"
            @navigate="(v) => { const w = windows.find(win => win.id === window.id); if (w) { w.view = v; w.title = getWindowTitle(v); } setView(v); }"
            @assetClick="handleAssetClick"
          />

          <!-- Crypto Page -->
          <CryptoPage 
            v-else-if="window.view === 'Crypto'" 
            @navigate="(v) => { const w = windows.find(win => win.id === window.id); if (w) { w.view = v; w.title = getWindowTitle(v); } setView(v); }"
            @assetClick="handleAssetClick"
          />

          <!-- News Page -->
          <NewsPage 
            v-else-if="window.view === 'News'" 
            :activeSection="newsSection"
          />

          <!-- Analytics Page -->
          <AnalyticsPage 
            v-else-if="window.view === 'Analytics'" 
            :activeSection="analyticsSection"
          />

          <!-- Screening Page -->
          <ScreeningPage 
            v-else-if="window.view === 'Screening'" 
            :symbol="activeSymbol"
            :activeSection="screeningSection"
          />

          <!-- Fundamental Analysis Page -->
          <FundamentalAnalysisPage 
            v-else-if="window.view === 'Fundamental'" 
            :symbol="activeSymbol"
            :activeSection="fundamentalSection"
          />

          <!-- Price Analysis Page -->
          <PriceAnalysisPage 
            v-else-if="window.view === 'PriceAnalysis'" 
            :symbol="activeSymbol"
            :activeSection="priceAnalysisSection"
          />

          <!-- FX Page -->
          <FXPage 
            v-else-if="window.view === 'FX'" 
            :symbol="activeSymbol"
            :activeSection="fxSection"
          />

          <!-- Settings Page -->
          <SettingsPage 
            v-else-if="window.view === 'Settings'" 
            :activeSection="settingsSection"
          />

          <!-- Bond Market Page -->
          <BondMarketPage 
            v-else-if="window.view === 'Bonds'" 
            :activeSection="bondsSection"
          />

          <!-- Central Banks Page -->
          <CentralBanksPage 
            v-else-if="window.view === 'CentralBanks'" 
            :activeSection="centralBanksSection"
          />

          <!-- Commodities Page -->
          <CommoditiesPage 
            v-else-if="window.view === 'Commodities'" 
            :symbol="activeSymbol"
            :activeSection="commoditiesSection"
          />

          <!-- Credit Risk Page -->
          <CreditRiskPage 
            v-else-if="window.view === 'CreditRisk'" 
            :symbol="activeSymbol"
            :activeSection="creditRiskSection"
          />

          <!-- Earn Page -->
          <EarnPage 
            v-else-if="window.view === 'Earn'" 
            :activeSection="earnSection"
          />

          <!-- Event Driven Page -->
          <EventDrivenPage 
            v-else-if="window.view === 'EventDriven'" 
            :symbol="activeSymbol"
            :activeSection="eventDrivenSection"
          />

          <!-- Finance Page -->
          <FinancePage 
            v-else-if="window.view === 'Finance'" 
            @asset-click="handleAssetClick"
          />

          <!-- Fixed Income Page -->
          <FixedIncomePage 
            v-else-if="window.view === 'FixedIncome'" 
            :activeSection="fixedIncomeSection"
          />

          <!-- Futures Page -->
          <FuturesPage 
            v-else-if="window.view === 'Futures'" 
            :symbol="activeSymbol"
            :activeSection="futuresSection"
          />

          <!-- Indices Page -->
          <IndicesPage 
            v-else-if="window.view === 'Indices'" 
            :activeSection="indicesSection"
          />

          <!-- Macroeconomics Page -->
          <MacroeconomicsPage 
            v-else-if="window.view === 'Macro'" 
            :activeSection="macroSection"
          />

          <!-- Options Page -->
          <OptionsPage 
            v-else-if="window.view === 'Options'" 
            :symbol="activeSymbol"
            :activeSection="optionsSection"
          />

          <!-- Research Page -->
          <ResearchPage 
            v-else-if="window.view === 'Research'" 
            :symbol="activeSymbol"
            :activeSection="researchSection"
          />

          <!-- Resources Page -->
          <ResourcesPage 
            v-else-if="window.view === 'Resources'" 
            :activeSection="resourcesSection"
          />

          <!-- Swaps Page -->
          <SwapsPage 
            v-else-if="window.view === 'Swaps'" 
            :symbol="activeSymbol"
            :activeSection="swapsSection"
          />
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
// Multi-window system
interface TerminalWindow {
  id: string;
  view: string;
  title?: string;
  symbol?: string;
  activeSection?: string;
}

const windows = ref<TerminalWindow[]>([
  { id: 'main-1', view: 'Main', title: 'Главная' }
]);

const activeWindowId = ref('main-1');
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
  { id: 'Resources', label: 'Ресурсы', icon: 'DatabaseIcon', code: 'FLDS' },
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
  // Quantitative Analysis Tools Commands
  { id: 'VOL', label: 'Поверхность волатильности', code: 'VOL', type: 'command', description: '3D визуализация волатильности по страйкам и экспирациям' },
  { id: 'VOLG', label: 'Поверхность волатильности (по грекам)', code: 'VOLG', type: 'command', description: '3D визуализация волатильности по страйкам и экспирациям на основе греков' },
  { id: 'CZF', label: 'Citadel Zeta Field', code: 'CZF', type: 'command', description: 'Анализ поля дзета-параметров Citadel' },
  { id: 'CVRC', label: 'Convolutional Volatility Resolution Clustering', code: 'CVRC', type: 'command', description: 'Кластеризация волатильности с использованием сверточных нейросетей' },
  { id: 'PSR', label: 'Phase Space Reconstruction', code: 'PSR', type: 'command', description: 'Реконструкция фазового пространства для анализа динамики' },
  { id: 'LVM', label: 'Latent Volatility model', code: 'LVM', type: 'command', description: 'Модель скрытой волатильности' },
  { id: 'MVS', label: 'Momentum-Volatility Surface', code: 'MVS', type: 'command', description: 'Поверхность волатильности с учетом импульса' },
  { id: 'LIQ', label: 'Liquidity Model', code: 'LIQ', type: 'command', description: 'Модель ликвидности рынка' },
  { id: 'HMM', label: 'HMM regime model visualization', code: 'HMM', type: 'command', description: 'Визуализация режимов скрытой марковской модели' },
  { id: 'TSIG', label: 'Time series с сигналами', code: 'TSIG', type: 'command', description: 'Линейный/бар чарт цены + наложение флагов buy/sell' },
  { id: 'CORR', label: 'Correlation heatmap', code: 'CORR', type: 'command', description: 'Цветная матрица корреляций' },
  { id: 'HMMD', label: 'HMM state diagram', code: 'HMMD', type: 'command', description: 'Граф состояний + timeline colors' },
  { id: 'ZSCR', label: 'Z‑score residuals', code: 'ZSCR', type: 'command', description: 'Линейный график отклонений' },
  { id: 'OBHM', label: 'Order book heatmap', code: 'OBHM', type: 'command', description: 'Цветная карта глубины стакана' },
  { id: 'ENSD', label: 'Ensemble signal distribution', code: 'ENSD', type: 'command', description: 'Гистограмма/confidence bands' },
  { id: 'FEAT', label: 'Feature importance bar chart', code: 'FEAT', type: 'command', description: 'Столбцы значимости факторов' },
  { id: 'DDSH', label: 'Drawdown/Sharpe timeline', code: 'DDSH', type: 'command', description: 'Накопленный график + метрики' },
  { id: 'EXEC', label: 'Latency/slippage scatter', code: 'EXEC', type: 'command', description: 'Точечный график execution metrics' },
  { id: 'EXPO', label: 'Turnover/exposure matrix', code: 'EXPO', type: 'command', description: 'Heatmap позиций по активам' },
  { id: 'OB3D', label: 'Объёмная карта ордербука (3D Depth Map)', code: 'OB3D', type: 'command', description: 'Трёхмерная визуализация глубины стакана' },
  { id: 'TVCN', label: 'Динамическая корреляционная сеть (Time‑Varying Correlation Network)', code: 'TVCN', type: 'command', description: 'Сетевая визуализация корреляций во времени' },
  { id: 'CTENSOR', label: 'Ковариационный куб (Covariance Tensor Cube)', code: 'CTENSOR', type: 'command', description: 'Трёхмерное представление ковариационной матрицы' },
  { id: 'HELIX', label: 'Объёмно‑временная спираль ликвидности (Liquidity Helix)', code: 'HELIX', type: 'command', description: 'Спиральная визуализация ликвидности во времени' },
  { id: 'HYPERCUBE', label: 'Пространство корреляций во времени (Correlation Hypercube)', code: 'HYPERCUBE', type: 'command', description: 'Гиперкубическое представление корреляций' },
  { id: 'VORTEX', label: 'Вихрь рыночных настроений (Sentiment Vortex)', code: 'VORTEX', type: 'command', description: 'Вихревая визуализация рыночных настроений' },
  { id: 'PLASMA', label: '«Плазма» потока опционных сделок', code: 'PLASMA', type: 'command', description: 'Визуализация в реальном времени потока опционных сделок как заряженных частиц в магнитном поле' },
  { id: 'LATTICE', label: '«Кристаллическая решетка аукциона» (Auction Lattice)', code: 'LATTICE', type: 'command', description: '3D-структура, показывающая историю и текущее состояние аукциона (открытия/закрытия на бирже, аукциона MOC)' },
  { id: 'TICKCORE', label: '«Тактовый сердечник» процессора исполнения', code: 'TICKCORE', type: 'command', description: 'Метафора процессора, где каждый такт — это пакет рыночных данных (тик). Визуализация нагрузки и задержек в обработке' },
  { id: 'GREEKS3D', label: '3D Greeks Tensor (Delta-Gamma-Vega landscape)', code: 'GREEKS3D', type: 'command', description: 'Для портфеля опционов/структурных продуктов показывай греки как трёхмерный тензор' },
  { id: 'REGNET', label: 'Regime Correlation Network (HMM‑driven)', code: 'REGNET', type: 'command', description: '3D‑граф корреляций, где высота узлов пропорциональна posterior probability текущего режима (из HMM)' },
  { id: 'TAILCUBE', label: 'Tail Risk Cube (EVT Stress Scenarios)', code: 'TAILCUBE', type: 'command', description: 'Куб, где каждый слой — сценарий стресса (GPD fits для tails), вокселы — P&L портфеля при quantile α' },
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
  const activeWindow = windows.value.find(w => w.id === activeWindowId.value);
  if (activeWindow) {
    activeWindow.view = newView;
    activeWindow.title = getWindowTitle(newView);
  }
  view.value = newView;
  isNavOpen.value = false; // Закрываем меню при переключении страницы
};

// Multi-window functions
const setActiveWindow = (windowId: string) => {
  activeWindowId.value = windowId;
  const window = windows.value.find(w => w.id === windowId);
  if (window) {
    view.value = window.view;
  }
};

const openNewWindow = (viewType: string = 'Main') => {
  const newWindow: TerminalWindow = {
    id: `window-${Date.now()}`,
    view: viewType,
    title: getWindowTitle(viewType),
  };
  windows.value.push(newWindow);
  setActiveWindow(newWindow.id);
};

const closeWindow = (windowId: string) => {
  if (windows.value.length <= 1) {
    // Не позволяем закрыть последнее окно
    return;
  }
  const index = windows.value.findIndex(w => w.id === windowId);
  if (index !== -1) {
    windows.value.splice(index, 1);
    // Если закрыли активное окно, переключаемся на другое
    if (activeWindowId.value === windowId) {
      const newActiveIndex = index > 0 ? index - 1 : 0;
      setActiveWindow(windows.value[newActiveIndex].id);
    }
  }
};

const getWindowTitle = (viewType: string): string => {
  const item = navItems.find(i => i.id === viewType);
  return item?.label || viewType;
};

// Icon components - must be defined before iconMap
const ActivityIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>' };
const LayoutTemplateIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>' };
const ChevronDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>' };
const SearchIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>' };
const CommandIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 3a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3H6a3 3 0 0 0-3 3 3 3 0 0 0 3 3 3 3 0 0 0 3-3V6a3 3 0 0 0-3-3 3 3 0 0 0-3 3 3 3 0 0 0 3 3h12a3 3 0 0 0-3-3z"/></svg>' };
const TrendingUpIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
const FilterIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>' };
const PieChartIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>' };
const WifiIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>' };
const PlusIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>' };
const XIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' };
const SettingsIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 6v6m9-9h-6m-6 0H3m15.364 6.364l-4.243-4.243m-4.242 0L5.636 18.364m12.728 0l-4.243-4.243m-4.242 0L5.636 5.636"/></svg>' };
const HelpCircleIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>' };
const DatabaseIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>' };
const LogOutIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>' };
const UserIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' };
const GlobeIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>' };
const DollarSignIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>' };

const iconMap: Record<string, any> = {
  'ActivityIcon': ActivityIcon,
  'GlobeIcon': GlobeIcon,
  'TrendingUpIcon': TrendingUpIcon,
  'FilterIcon': FilterIcon,
  'PieChartIcon': PieChartIcon,
  'WifiIcon': WifiIcon,
  'SearchIcon': SearchIcon,
  'DollarSignIcon': DollarSignIcon,
  'DatabaseIcon': DatabaseIcon,
};

const getWindowIcon = (viewType: string): any => {
  const item = navItems.find(i => i.id === viewType);
  const iconName = item?.icon || 'ActivityIcon';
  return iconMap[iconName] || ActivityIcon;
};

const setActiveSymbol = (symbol: string) => {
  activeSymbol.value = symbol;
  data.value = generateCandles(100);
  orderBook.value = generateOrderBook(currentPrice.value);
};

const handleCommandSelect = (item: SearchResult) => {
  if (item.type === 'command') {
    const code = item.code || '';
    // Определяем view по коду команды
    let targetView = 'Main';
    if (code === 'HOME') targetView = 'Main';
    else if (code === 'TOP') targetView = 'News';
    else if (code === 'GP') targetView = 'PriceAnalysis';
    else if (code === 'EQS') targetView = 'Screening';
    else if (code === 'QUA') targetView = 'Analytics';
    else if (code === 'EE') targetView = 'Fundamental';
    else if (code === 'FX') targetView = 'FX';
    else if (code === 'SET') targetView = 'Settings';
    else if (code === 'MKT') targetView = 'Markets';
    else if (code === 'CRYPTO') targetView = 'Crypto';
    else if (code === 'GOVT') targetView = 'Bonds';
    else if (code === 'FOMC') targetView = 'CentralBanks';
    else if (code === 'CMDX') targetView = 'Commodities';
    else if (code === 'SRSK') targetView = 'CreditRisk';
    else if (code === 'EARN') targetView = 'Earn';
    else if (code === 'IPO') targetView = 'EventDriven';
    else if (code === 'PORT') targetView = 'Finance';
    else if (code === 'YAS') targetView = 'FixedIncome';
    else if (code === 'CTRK') targetView = 'Futures';
    else if (code === 'WEI') targetView = 'Indices';
    else if (code === 'ECOD') targetView = 'Macro';
    else if (code === 'OMON') targetView = 'Options';
    else if (code === 'RES') targetView = 'Research';
    else if (code === 'FLDS') targetView = 'Resources';
    else if (code === 'SWPM') targetView = 'Swaps';
    else if (['VOL', 'VOLG', 'CZF', 'CVRC', 'PSR', 'LVM', 'MVS', 'LIQ', 'HMM', 'TSIG', 'CORR', 'HMMD', 'ZSCR', 'OBHM', 'ENSD', 'FEAT', 'DDSH', 'EXEC', 'EXPO', 'OB3D', 'TVCN', 'CTENSOR', 'HELIX', 'HYPERCUBE', 'VORTEX', 'PLASMA', 'LATTICE', 'TICKCORE', 'GREEKS3D', 'REGNET', 'TAILCUBE'].includes(code)) {
      targetView = 'Analytics';
      analyticsSection.value = 'Quant';
    }
    
    // Открываем новое окно с выбранным view
    openNewWindow(targetView);
    isSearchOpen.value = false;
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


</script>

<style scoped>
/* ============================================
   TERMINAL ROOT - BRUTALIST
   ============================================ */
.terminal-root {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #050505;
  color: #f5f5f5;
  position: relative;
}

.terminal-content {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px;
  gap: 16px;
}

/* ============================================
   TABS BAR - BRUTALIST
   ============================================ */
.tabs-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
  flex-shrink: 0;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #0a0a0a;
  border: 1px solid #1a1a1a;
  color: #737373;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.tab-item:hover {
  border-color: #262626;
  color: #f5f5f5;
}

.tab-active {
  background: #DC2626;
  border-color: #DC2626;
  color: #000;
}

.tab-label {
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  white-space: nowrap;
}

.tab-close {
  margin-left: 4px;
  padding: 2px;
  color: inherit;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.tab-close:hover {
  opacity: 1;
}

.tab-new {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid #262626;
  color: #737373;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  font-size: 11px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.tab-new:hover {
  background: #DC2626;
  border-color: #DC2626;
  color: #000;
}

/* ============================================
   HEADER - BRUTALIST
   ============================================ */
.terminal-header {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: #0a0a0a;
  border: 1px solid #1a1a1a;
  flex-shrink: 0;
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.logo-icon {
  width: 28px;
  height: 28px;
  background: #DC2626;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: #000;
}

.logo-text {
  font-size: 12px;
  font-weight: 500;
  color: #f5f5f5;
  letter-spacing: 0.1em;
}

/* Navigation Dropdown */
.nav-dropdown-wrapper {
  position: relative;
  z-index: 50;
}

.nav-dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid #262626;
  color: #a3a3a3;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 11px;
}

.nav-dropdown-trigger:hover,
.nav-dropdown-trigger.is-open {
  border-color: #DC2626;
  color: #f5f5f5;
}

.nav-overlay {
  position: fixed;
  inset: 0;
  z-index: 40;
  background: rgba(0, 0, 0, 0.5);
}

.nav-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 8px;
  width: 320px;
  background: #0a0a0a;
  border: 1px solid #262626;
  z-index: 50;
  overflow: hidden;
}

.nav-dropdown-header {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  font-size: 10px;
  font-weight: 600;
  color: #525252;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  border-bottom: 1px solid #1a1a1a;
  background: #050505;
}

.nav-dropdown-list {
  max-height: 60vh;
  overflow-y: auto;
  padding: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  color: #737373;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.nav-item:hover {
  background: #DC2626;
  color: #000;
}

.nav-item-active {
  background: rgba(220, 38, 38, 0.15);
  color: #DC2626;
}

.nav-item-label {
  flex: 1;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.nav-item-code {
  font-size: 10px;
  padding: 2px 6px;
  background: #1a1a1a;
  border: 1px solid #262626;
  color: #525252;
}

.nav-item:hover .nav-item-code {
  background: rgba(0, 0, 0, 0.3);
  border-color: transparent;
  color: inherit;
}

/* Header Right */
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #050505;
  border: 1px solid #262626;
  color: #525252;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 11px;
}

.search-trigger:hover {
  border-color: #DC2626;
  color: #f5f5f5;
}

.search-hotkey {
  font-size: 10px;
  padding: 2px 6px;
  background: #1a1a1a;
  border: 1px solid #262626;
  margin-left: 20px;
}

.header-divider {
  width: 1px;
  height: 20px;
  background: #262626;
}

.ai-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #262626;
  color: #737373;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 11px;
  letter-spacing: 0.1em;
  position: relative;
}

.ai-btn:hover {
  border-color: #DC2626;
  color: #f5f5f5;
}

.ai-btn-active {
  background: #DC2626;
  border-color: #DC2626;
  color: #000;
}

.ai-indicator {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 8px;
  height: 8px;
  background: #22c55e;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Profile */
.profile-wrapper {
  position: relative;
}

.profile-avatar {
  width: 32px;
  height: 32px;
  background: #DC2626;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  color: #000;
  cursor: pointer;
  transition: transform 0.2s;
  letter-spacing: 0.05em;
}

.profile-avatar:hover {
  transform: scale(1.05);
}

.profile-dropdown {
  position: absolute;
  top: 48px;
  right: 0;
  width: 280px;
  background: #0a0a0a;
  border: 1px solid #262626;
  z-index: 100;
  overflow: hidden;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #050505;
  border-bottom: 1px solid #1a1a1a;
}

.profile-avatar-lg {
  width: 44px;
  height: 44px;
  background: #DC2626;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #000;
  letter-spacing: 0.05em;
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 13px;
  font-weight: 500;
  color: #f5f5f5;
  letter-spacing: 0.05em;
}

.profile-badge {
  font-size: 10px;
  color: #22c55e;
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.3);
  padding: 2px 6px;
  display: inline-block;
  margin-top: 4px;
}

.profile-menu {
  padding: 8px;
}

.profile-menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  color: #a3a3a3;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  font-size: 12px;
  letter-spacing: 0.05em;
}

.profile-menu-item:hover {
  background: #DC2626;
  color: #000;
}

.profile-footer {
  padding: 8px;
  border-top: 1px solid #1a1a1a;
}

.profile-logout {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  color: #DC2626;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  font-size: 12px;
  letter-spacing: 0.05em;
}

.profile-logout:hover {
  background: #DC2626;
  color: #000;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .terminal-content {
    padding: 12px;
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .terminal-content {
    padding: 8px;
    gap: 8px;
  }

  .terminal-header {
    height: auto;
    min-height: 48px;
    padding: 8px 12px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .nav-dropdown {
    left: -100px;
    width: calc(100vw - 32px);
    max-width: 320px;
  }

  .profile-dropdown {
    right: -16px;
    width: calc(100vw - 32px);
    max-width: 280px;
  }

  .tab-item,
  .tab-new {
    min-height: 44px;
  }
}

@media (max-width: 480px) {
  .terminal-content {
    padding: 6px;
    gap: 6px;
  }

  .terminal-header {
    padding: 6px 10px;
  }

  .logo-text {
    display: none;
  }

  .tab-label {
    font-size: 10px;
  }

  .tab-new span {
    display: none;
  }
}

@media (max-width: 375px) {
  .terminal-content {
    padding: 4px;
    gap: 4px;
  }
}
</style>
