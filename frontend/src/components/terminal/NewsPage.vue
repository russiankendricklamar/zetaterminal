<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full">
    <!-- Header & Nav -->
    <div class="flex flex-col md:flex-row items-start md:items-center justify-between p-6 border-b border-white/5 gap-4">
      <div class="flex items-center gap-4">
        <div class="p-3 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 rounded-2xl text-indigo-300">
          <component :is="currentTabData.icon" class="w-4 h-4" />
        </div>
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">
            Новости
          </h2>
          <p class="text-xs text-gray-400">
            {{ currentTabData.description }}
          </p>
        </div>
      </div>
      
      <div class="flex bg-black/20 rounded-xl p-1 border border-white/5 overflow-x-auto max-w-full custom-scrollbar">
        <button 
          v-for="tab in tabs"
          :key="tab.id"
          @click="currentTab = tab.id"
          :class="`px-4 py-2 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${currentTab === tab.id ? 'bg-white/10 text-white shadow-lg' : 'text-gray-500 hover:text-white hover:bg-white/5'}`"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-black/10">
      <!-- Real-time News -->
      <div v-if="currentTab === 'TOP'" class="space-y-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider">Главные новости</h3>
          <div class="flex gap-2">
            <span class="px-2 py-1 bg-rose-500/10 text-rose-400 text-[10px] rounded font-bold border border-rose-500/20 animate-pulse">ОНЛАЙН</span>
          </div>
        </div>
        <div 
          v-for="item in news" 
          :key="item.id"
          class="group relative p-5 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all hover:border-white/20"
        >
          <div :class="`absolute left-0 top-0 bottom-0 w-1 rounded-l-2xl ${getImportanceColor(item.importance)}`"></div>
          <div class="flex justify-between items-start mb-2 pl-2">
            <div class="flex items-center gap-2">
              <span :class="`text-[10px] font-bold px-2 py-0.5 rounded ${item.importance === 'Critical' ? 'bg-rose-500 text-white' : 'bg-gray-700 text-gray-300'}`">
                {{ getImportanceName(item.importance) }}
              </span>
              <span class="text-[10px] text-gray-500 font-mono">{{ item.source }}</span>
            </div>
            <span class="text-[10px] text-gray-500 flex items-center gap-1">
              <ClockIcon class="w-2.5 h-2.5" /> {{ item.time }}
            </span>
          </div>
          <h3 class="text-lg font-bold text-white mb-2 pl-2 leading-snug group-hover:text-indigo-300 transition-colors cursor-pointer">{{ item.title }}</h3>
          <div class="pl-2 flex items-center gap-4 mt-3 opacity-60 group-hover:opacity-100 transition-opacity">
            <button class="text-xs text-gray-400 hover:text-white">
              Читать полностью
            </button>
            <button class="text-xs text-gray-400 hover:text-white">
              Резюмировать
            </button>
          </div>
        </div>
      </div>

      <!-- Company News -->
      <div v-else-if="currentTab === 'CN'" class="flex flex-col h-full">
        <div class="flex items-center gap-4 mb-6">
          <div class="relative flex-1 max-w-md">
            <SearchIcon class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 w-4 h-4" />
            <input 
              type="text" 
              placeholder="Введите тикер (например, NVDA, TSLA)" 
              class="w-full bg-black/20 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-sm text-white focus:outline-none focus:border-indigo-500/50 transition-colors"
              value="NVDA"
            />
          </div>
        </div>

        <div class="flex items-center gap-6 mb-8 p-6 bg-gradient-to-r from-green-900/20 to-transparent rounded-2xl border border-white/5">
          <div class="w-16 h-16 bg-white rounded-xl flex items-center justify-center">
            <span class="text-2xl font-bold text-black">NVDA</span>
          </div>
          <div>
            <h3 class="text-2xl font-bold text-white">NVIDIA Corporation</h3>
            <div class="flex items-center gap-4 mt-1">
              <span class="text-3xl font-mono font-bold text-emerald-400">$892.10</span>
              <span class="text-sm font-bold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded">+4.25%</span>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="flex items-start gap-4">
            <div class="flex flex-col items-center">
              <div class="w-3 h-3 rounded-full bg-indigo-500 shadow-[0_0_10px_#6366f1]"></div>
              <div class="w-0.5 h-full bg-white/10 my-1"></div>
            </div>
            <div class="flex-1 pb-6">
              <span class="text-xs text-indigo-300 font-mono mb-1 block">Сегодня, 10:30</span>
              <h4 class="text-base font-bold text-white mb-2">Подтверждено приобретение Run:ai за $700M</h4>
              <p class="text-sm text-gray-400 leading-relaxed">NVIDIA официально подтвердила приобретение платформы оркестрации Kubernetes Run:ai для усиления возможностей управления инфраструктурой ИИ.</p>
            </div>
          </div>
          <div class="flex items-start gap-4">
            <div class="flex flex-col items-center">
              <div class="w-3 h-3 rounded-full bg-indigo-500 shadow-[0_0_10px_#6366f1]"></div>
              <div class="w-0.5 h-full bg-white/10 my-1"></div>
            </div>
            <div class="flex-1 pb-6">
              <span class="text-xs text-indigo-300 font-mono mb-1 block">Вчера, 14:20</span>
              <h4 class="text-base font-bold text-white mb-2">NVIDIA анонсировала революционный AI-чип 'Rubin'</h4>
              <p class="text-sm text-gray-400 leading-relaxed">Компания представила новый графический процессор следующего поколения с улучшенной производительностью для обучения больших языковых моделей.</p>
            </div>
          </div>
          <div class="flex items-start gap-4">
            <div class="flex flex-col items-center">
              <div class="w-3 h-3 rounded-full bg-gray-600"></div>
              <div class="w-0.5 h-full bg-white/10 my-1"></div>
            </div>
            <div class="flex-1 pb-6">
              <span class="text-xs text-gray-500 font-mono mb-1 block">Вчера, 16:15</span>
              <h4 class="text-base font-bold text-gray-300 mb-2">Директор продал 5,000 акций</h4>
              <p class="text-sm text-gray-500 leading-relaxed">Форма SEC 4 указывает, что директор продал акции по средней цене $850.20.</p>
            </div>
          </div>
          <div class="flex items-start gap-4">
            <div class="flex flex-col items-center">
              <div class="w-3 h-3 rounded-full bg-gray-600"></div>
              <div class="w-0.5 h-full bg-white/10 my-1"></div>
            </div>
            <div class="flex-1 pb-6">
              <span class="text-xs text-gray-500 font-mono mb-1 block">2 дня назад, 11:45</span>
              <h4 class="text-base font-bold text-gray-300 mb-2">Отчёт о прибылях и убытках превзошёл ожидания</h4>
              <p class="text-sm text-gray-500 leading-relaxed">NVIDIA сообщила о выручке $22.1 млрд, что на 15% выше прогнозов аналитиков. Прибыль на акцию составила $4.50.</p>
            </div>
          </div>
          <div class="flex items-start gap-4">
            <div class="flex flex-col items-center">
              <div class="w-3 h-3 rounded-full bg-gray-600"></div>
              <div class="w-0.5 h-full bg-white/10 my-1"></div>
            </div>
            <div class="flex-1 pb-6">
              <span class="text-xs text-gray-500 font-mono mb-1 block">3 дня назад, 09:30</span>
              <h4 class="text-base font-bold text-gray-300 mb-2">Партнёрство с крупными облачными провайдерами</h4>
              <p class="text-sm text-gray-500 leading-relaxed">Компания объявила о расширении сотрудничества с AWS, Microsoft Azure и Google Cloud для развёртывания AI-инфраструктуры.</p>
            </div>
          </div>
          <div class="flex items-start gap-4">
            <div class="flex flex-col items-center">
              <div class="w-3 h-3 rounded-full bg-gray-600"></div>
            </div>
            <div class="flex-1 pb-6">
              <span class="text-xs text-gray-500 font-mono mb-1 block">5 дней назад, 15:00</span>
              <h4 class="text-base font-bold text-gray-300 mb-2">Запуск нового центра разработки в Сингапуре</h4>
              <p class="text-sm text-gray-500 leading-relaxed">NVIDIA инвестирует $500M в создание нового исследовательского центра, специализирующегося на разработке AI-решений для Азиатско-Тихоокеанского региона.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- News Search -->
      <div v-else-if="currentTab === 'NSRC'" class="flex flex-col h-full">
        <div class="p-8 rounded-3xl bg-white/5 border border-white/5 text-center mb-8">
          <h3 class="text-2xl font-bold text-white mb-4">Глубокий поиск по рынку</h3>
          <div class="relative max-w-2xl mx-auto">
            <input 
              type="text" 
              placeholder="Поиск по компании, инвестору, сектору или ключевому слову..." 
              class="w-full bg-black/40 border border-white/10 rounded-2xl py-4 pl-6 pr-12 text-white focus:outline-none focus:border-indigo-500/50 transition-all shadow-inner"
            />
            <button class="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-indigo-500 rounded-xl text-white hover:bg-indigo-600 transition-colors">
              <ArrowRightIcon class="w-4 h-4" />
            </button>
          </div>
          <div class="flex justify-center gap-3 mt-4">
            <span 
              v-for="tag in searchTags" 
              :key="tag"
              class="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-gray-400 hover:text-white cursor-pointer hover:bg-white/10 transition-colors"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>

      <!-- News Alerts -->
      <div v-else-if="currentTab === 'SALT'">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="text-xl font-bold text-white">Умные уведомления</h3>
            <p class="text-sm text-gray-400">Управляйте email-уведомлениями и триггерами.</p>
          </div>
          <button class="px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white text-xs font-bold rounded-xl transition-colors">
            + Создать уведомление
          </button>
        </div>

        <div class="space-y-3">
          <div 
            v-for="(alert, i) in alerts" 
            :key="i"
            class="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5"
          >
            <div class="flex items-center gap-4">
              <div :class="`w-10 h-10 rounded-full flex items-center justify-center ${alert.active ? 'bg-emerald-500/20 text-emerald-400' : 'bg-gray-700/50 text-gray-500'}`">
                <BellIcon class="w-4 h-4" />
              </div>
              <div>
                <h4 :class="`text-sm font-bold ${alert.active ? 'text-white' : 'text-gray-500'}`">{{ alert.name }}</h4>
                <p class="text-xs text-gray-500">{{ alert.condition }}</p>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <span class="text-xs text-gray-500">{{ alert.active ? 'Мгновенный Email' : 'Приостановлено' }}</span>
              <div :class="`w-10 h-5 rounded-full relative cursor-pointer transition-colors ${alert.active ? 'bg-indigo-500' : 'bg-gray-700'}`">
                <div :class="`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${alert.active ? 'left-6' : 'left-1'}`"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Summaries -->
      <div v-else-if="currentTab === 'FIRS'" class="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
        <div class="bg-white/5 border border-white/5 rounded-2xl p-6 flex flex-col">
          <div class="flex items-center gap-2 mb-4">
            <BotIcon class="w-5 h-5 text-indigo-400" />
            <h3 class="text-lg font-bold text-white">Факты по запросу</h3>
          </div>
          <p class="text-sm text-gray-400 mb-6">Выберите трендовую тему для мгновенной генерации AI-резюме.</p>
          
          <div class="flex-1 space-y-3 overflow-y-auto custom-scrollbar">
            <div 
              v-for="(topic, i) in summaryTopics" 
              :key="i"
              class="p-4 rounded-xl bg-black/20 border border-white/5 hover:border-indigo-500/50 cursor-pointer group transition-all"
            >
              <h4 class="text-sm font-bold text-gray-200 group-hover:text-white mb-2">{{ topic }}</h4>
              <div class="flex items-center justify-between">
                <span class="text-[10px] text-gray-500">Включает 12 источников</span>
                <button class="text-[10px] font-bold text-indigo-400 uppercase tracking-wide opacity-0 group-hover:opacity-100 transition-opacity">Сгенерировать</button>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-gradient-to-br from-indigo-900/20 to-black border border-white/10 rounded-2xl p-6 relative overflow-hidden">
          <div class="absolute top-0 right-0 p-8 opacity-10">
            <FileTextIcon class="w-32 h-32" />
          </div>
          <h3 class="text-lg font-bold text-white mb-4">Последнее сгенерированное резюме</h3>
          <div class="space-y-4">
            <div class="flex items-center gap-2 text-xs text-indigo-300 font-mono">
              <span>ТЕМА:</span>
              <span class="bg-indigo-500/20 px-2 py-0.5 rounded">EU AI Act</span>
            </div>
            <p class="text-sm text-gray-300 leading-relaxed">
              Европейский парламент одобрил AI Act, устанавливая первую в мире всеобъемлющую правовую основу для искусственного интеллекта.
            </p>
            <div class="pt-4 mt-4 border-t border-white/5 flex gap-3">
              <button class="flex-1 py-2 bg-white/10 rounded-lg text-xs font-bold hover:bg-white/20 transition-colors">Поделиться</button>
              <button class="flex-1 py-2 bg-indigo-500 rounded-lg text-xs font-bold text-white hover:bg-indigo-600 transition-colors">Полный отчёт</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Briefs -->
      <div v-else-if="currentTab === 'BRIE'">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-bold text-white">Рыночные обзоры</h3>
          <div class="flex gap-2">
            <button class="text-xs font-bold text-gray-400 hover:text-white px-3 py-1">Ежедневно</button>
            <button class="text-xs font-bold text-white bg-white/10 rounded-lg px-3 py-1">Еженедельно</button>
          </div>
        </div>

        <div class="grid gap-4">
          <div 
            v-for="(brief, i) in briefs" 
            :key="i"
            class="flex items-center justify-between p-5 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors group"
          >
            <div class="flex items-center gap-4">
              <div class="p-3 bg-gray-800 rounded-xl text-gray-300 group-hover:bg-white group-hover:text-black transition-colors">
                <BookOpenIcon class="w-5 h-5" />
              </div>
              <div>
                <h4 class="text-base font-bold text-white mb-1">{{ brief.title }}</h4>
                <div class="flex items-center gap-2 text-xs text-gray-500">
                  <span>{{ brief.date }}</span>
                  <span class="w-1 h-1 bg-gray-600 rounded-full"></span>
                  <span class="uppercase tracking-wider">{{ brief.type }}</span>
                </div>
              </div>
            </div>
            <button class="p-2 rounded-lg border border-white/10 text-gray-400 hover:text-white hover:border-white/30 transition-all">
              <DownloadIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';

interface Props {
  activeSection?: string;
}

const props = withDefaults(defineProps<Props>(), {
  activeSection: 'TOP'
});

const currentTab = ref(props.activeSection);

watch(() => props.activeSection, (val) => {
  currentTab.value = val;
});

const tabs = [
  { id: 'TOP', label: 'Онлайн', icon: 'ZapIcon', description: 'Актуальные новости рынка в реальном времени' },
  { id: 'CN', label: 'Компании', icon: 'NewspaperIcon', description: 'Новости и события по конкретным компаниям' },
  { id: 'NSRC', label: 'Поиск', icon: 'SearchIcon', description: 'Глубокий поиск по рынку, компаниям и инвесторам' },
  { id: 'SALT', label: 'Уведомления', icon: 'BellIcon', description: 'Управление умными уведомлениями и триггерами' },
  { id: 'FIRS', label: 'Резюме', icon: 'BotIcon', description: 'AI-резюме по трендовым темам и событиям' },
  { id: 'BRIE', label: 'Обзоры', icon: 'BookOpenIcon', description: 'Ежедневные, еженедельные и ежемесячные рыночные обзоры' },
];

const currentTabData = computed(() => tabs.find(t => t.id === currentTab.value) || tabs[0]);

const news = [
  { id: 1, title: "Bitcoin достиг исторического максимума на фоне институционального ажиотажа", source: "Bloomberg", time: "2 мин назад", importance: "High", sentiment: "Bullish" },
  { id: 2, title: "Федеральная резервная система назначила экстренное заседание на понедельник", source: "Reuters", time: "15 мин назад", importance: "Critical", sentiment: "Bearish" },
  { id: 3, title: "NVIDIA анонсировала революционный AI-чип 'Rubin'", source: "TechCrunch", time: "42 мин назад", importance: "High", sentiment: "Bullish" },
  { id: 4, title: "Цены на нефть снижаются по мере небольшого ослабления напряжённости на Ближнем Востоке", source: "CNBC", time: "1 ч назад", importance: "Medium", sentiment: "Neutral" },
  { id: 5, title: "Apple сообщила о рекордной выручке от услуг в Q3", source: "MarketWatch", time: "2 ч назад", importance: "Medium", sentiment: "Bullish" },
  { id: 6, title: "Microsoft объявляет о крупнейшем инвестиционном раунде в OpenAI на $10 млрд", source: "TechCrunch", time: "3 ч назад", importance: "High", sentiment: "Bullish" },
  { id: 7, title: "Tesla запускает производство новой модели Model Y+ с увеличенным запасом хода", source: "Reuters", time: "4 ч назад", importance: "Medium", sentiment: "Bullish" },
  { id: 8, title: "Amazon Web Services сообщает о росте выручки на 25% в облачном сегменте", source: "Bloomberg", time: "5 ч назад", importance: "High", sentiment: "Bullish" },
  { id: 9, title: "Meta Platforms представляет новую AR-платформу для бизнеса", source: "The Verge", time: "6 ч назад", importance: "Medium", sentiment: "Bullish" },
  { id: 10, title: "JPMorgan Chase увеличивает дивиденды после сильных квартальных результатов", source: "Financial Times", time: "7 ч назад", importance: "High", sentiment: "Bullish" },
  { id: 11, title: "AMD выпускает новые процессоры Ryzen 9000 с улучшенной энергоэффективностью", source: "TechCrunch", time: "8 ч назад", importance: "Medium", sentiment: "Bullish" },
  { id: 12, title: "Exxon Mobil объявляет о новом месторождении в Мексиканском заливе", source: "Reuters", time: "9 ч назад", importance: "Medium", sentiment: "Neutral" },
  { id: 13, title: "Google запускает новую версию поисковой системы с интеграцией AI", source: "The Verge", time: "10 ч назад", importance: "High", sentiment: "Bullish" },
  { id: 14, title: "Pfizer получает одобрение FDA на новое лекарство от диабета", source: "Bloomberg", time: "11 ч назад", importance: "High", sentiment: "Bullish" },
  { id: 15, title: "Intel сообщает о задержке выпуска следующего поколения чипов до 2026 года", source: "Reuters", time: "12 ч назад", importance: "Medium", sentiment: "Bearish" },
  { id: 16, title: "Nike увеличивает прогнозы на год после роста продаж в Азии", source: "MarketWatch", time: "13 ч назад", importance: "Medium", sentiment: "Bullish" },
  { id: 17, title: "Goldman Sachs объявляет о сокращении 3% персонала в инвестиционном банке", source: "Financial Times", time: "14 ч назад", importance: "High", sentiment: "Bearish" },
  { id: 18, title: "Coca-Cola запускает новую линейку энергетических напитков", source: "CNBC", time: "15 ч назад", importance: "Medium", sentiment: "Neutral" },
  { id: 19, title: "Bank of America сообщает о росте кредитных потерь в потребительском сегменте", source: "Reuters", time: "16 ч назад", importance: "High", sentiment: "Bearish" },
  { id: 20, title: "Chevron объявляет о партнёрстве с Tesla для строительства сети зарядных станций", source: "Bloomberg", time: "17 ч назад", importance: "High", sentiment: "Bullish" },
  { id: 21, title: "Apple представляет новый iPhone 16 Pro с улучшенной камерой и AI-функциями", source: "The Verge", time: "18 ч назад", importance: "High", sentiment: "Bullish" },
  { id: 22, title: "Netflix сообщает о рекордном количестве подписчиков после запуска рекламного тарифа", source: "MarketWatch", time: "19 ч назад", importance: "Medium", sentiment: "Bullish" },
];

const alerts = [
  { name: 'Предупреждение о падении портфеля', condition: 'Любой актив падает > 5%', active: true },
  { name: 'Новости NVIDIA', condition: 'Ключевые слова: "Прибыль", "Musk"', active: true },
  { name: 'Ставки ФРС', condition: 'Источник: Федеральная резервная система', active: false },
  { name: 'Прорыв Bitcoin', condition: 'BTC > $70k', active: true },
];

const briefs = [
  { title: "Утренний звонок: Технологический ралли продолжается", date: "24 окт 2025", type: "Ежедневно" },
  { title: "Еженедельный обзор криптовалют: Потоки ETF", date: "21 окт 2025", type: "Еженедельно" },
  { title: "Макроэкономический прогноз: Проекции Q4", date: "01 окт 2025", type: "Ежемесячно" },
];

const searchTags = ['Полупроводники', 'Warren Buffet', 'IPO', 'Слияния'];
const summaryTopics = ['Обновление о глобальном дефиците чипов', 'Анализ данных инфляции США', 'Законопроект о регулировании криптовалют 2025'];

const getImportanceColor = (importance: string) => {
  if (importance === 'Critical') return 'bg-rose-500';
  if (importance === 'High') return 'bg-orange-500';
  return 'bg-blue-500';
};

const getImportanceName = (importance: string) => {
  const names: Record<string, string> = {
    'Critical': 'КРИТИЧНО',
    'High': 'ВЫСОКАЯ',
    'Medium': 'СРЕДНЯЯ',
  };
  return names[importance] || importance.toUpperCase();
};

// Icon components
const ZapIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>' };
const NewspaperIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/></svg>' };
const SearchIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>' };
const BellIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>' };
const BotIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>' };
const BookOpenIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>' };
const ClockIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' };
const ExternalLinkIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>' };
const ArrowRightIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>' };
const FileTextIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>' };
const DownloadIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>' };
</script>
