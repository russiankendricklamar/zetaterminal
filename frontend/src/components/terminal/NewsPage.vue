<template>
  <div class="page-container custom-scrollbar">
    <!-- Header & Nav -->
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box icon-indigo">
          <component :is="currentTabData.icon" class="w-5 h-5" />
        </div>
        <div>
          <h2 class="section-title font-anton">НОВОСТИ</h2>
          <p class="section-subtitle font-mono">{{ currentTabData.description }}</p>
        </div>
      </div>

      <div class="tab-group">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="currentTab = tab.id"
          :class="['tab-btn', { active: currentTab === tab.id }]"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 flex flex-col gap-4">
      <!-- Real-time News -->
      <div v-if="currentTab === 'TOP'" class="flex flex-col gap-4">
        <div class="flex items-center justify-between">
          <h3 class="font-oswald text-sm text-text-tertiary uppercase tracking-wider">ГЛАВНЫЕ НОВОСТИ</h3>
          <div class="flex items-center gap-3">
            <button @click="loadHeadlines" class="btn-ghost text-xs font-mono flex items-center gap-1">
              <RefreshIcon class="w-3 h-3" /> ОБНОВИТЬ
            </button>
            <div class="badge badge-red">
              <span class="status-dot"></span> ОНЛАЙН
            </div>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="headlinesLoading" class="flex items-center gap-2 text-gray-400 text-xs">
          <div class="w-3 h-3 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
          Загрузка новостей...
        </div>

        <!-- Error -->
        <div v-if="headlinesError" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-mono">
          {{ headlinesError }}
        </div>

        <div
          v-for="(item, idx) in headlines"
          :key="idx"
          class="news-item"
        >
          <div class="news-meta">
            <span class="news-source">{{ item.source }}</span>
            <span class="news-source flex items-center gap-1">
              <ClockIcon class="w-2.5 h-2.5" /> {{ formatTime(item.publishedAt) }}
            </span>
            <span v-if="item.category && item.category.length" class="news-badge">
              {{ item.category[0].toUpperCase() }}
            </span>
          </div>
          <h3 class="news-title">
            <a :href="item.url" target="_blank" rel="noopener" class="hover:text-[var(--accent-red)] transition-colors">
              {{ item.title }}
            </a>
          </h3>
          <p v-if="item.description" class="text-xs text-[var(--text-muted)] mt-1 line-clamp-2">{{ item.description }}</p>
          <div class="flex items-center gap-4 mt-3">
            <a :href="item.url" target="_blank" rel="noopener" class="btn-ghost text-xs font-mono">ЧИТАТЬ ПОЛНОСТЬЮ</a>
            <button @click="doSummarize(idx)" class="btn-ghost text-xs font-mono" :disabled="item._summarizing">
              {{ item._summarizing ? 'ГЕНЕРАЦИЯ...' : 'РЕЗЮМИРОВАТЬ' }}
            </button>
            <button @click="doSentiment(idx)" class="btn-ghost text-xs font-mono" :disabled="item._sentimentLoading">
              {{ item._sentimentLoading ? 'АНАЛИЗ...' : 'НАСТРОЕНИЕ' }}
            </button>
          </div>
          <!-- Sentiment Result -->
          <div v-if="item._sentiment" class="mt-2 flex items-center gap-2">
            <span :class="['px-2 py-0.5 rounded text-[10px] font-bold uppercase', sentimentClass(item._sentiment.scores)]">
              {{ sentimentLabel(item._sentiment.scores) }}
            </span>
            <span class="text-[10px] text-gray-500 font-mono">{{ sentimentConfidence(item._sentiment.scores) }}</span>
          </div>
          <!-- Summary Result -->
          <div v-if="item._summary" class="mt-2 p-3 rounded-lg bg-white/5 border border-white/5 text-xs text-gray-300 font-mono">
            {{ item._summary }}
          </div>
        </div>

        <!-- Empty -->
        <div v-if="!headlinesLoading && headlines.length === 0 && !headlinesError" class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
          Нет доступных новостей
        </div>
      </div>

      <!-- Company News -->
      <div v-else-if="currentTab === 'CN'" class="flex flex-col gap-6">
        <div class="search-box max-w-md">
          <SearchIcon class="search-icon" />
          <input
            v-model="companyQuery"
            type="text"
            placeholder="ВВЕДИТЕ ТИКЕР ИЛИ НАЗВАНИЕ (НАПРИМЕР, NVDA, TESLA)"
            @keydown.enter="searchCompanyNews"
          />
        </div>

        <!-- Quick tickers -->
        <div class="flex flex-wrap gap-2">
          <button
            v-for="t in quickTickers"
            :key="t"
            @click="companyQuery = t; searchCompanyNews()"
            :class="['px-3 py-1.5 rounded-lg text-xs font-bold transition-all border', companyQuery === t ? 'bg-white/10 text-white border-white/20' : 'text-gray-500 border-white/5 hover:text-white hover:border-white/20']"
          >
            {{ t }}
          </button>
        </div>

        <!-- Loading -->
        <div v-if="companyLoading" class="flex items-center gap-2 text-gray-400 text-xs">
          <div class="w-3 h-3 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
          Поиск новостей по {{ companyQuery }}...
        </div>

        <!-- Company Results -->
        <div v-if="companyResults.length > 0" class="timeline">
          <div v-for="(item, idx) in companyResults" :key="idx" class="timeline-item">
            <div class="timeline-marker">
              <div :class="['timeline-dot', idx < 2 ? 'active' : '']"></div>
              <div v-if="idx < companyResults.length - 1" class="timeline-line"></div>
            </div>
            <div class="timeline-content">
              <span class="timeline-date">{{ formatTime(item.publishedAt) }} — {{ item.source }}</span>
              <h4 class="timeline-title">
                <a :href="item.url" target="_blank" rel="noopener" class="hover:text-[var(--accent-red)] transition-colors">
                  {{ item.title }}
                </a>
              </h4>
              <p v-if="item.description" class="timeline-desc">{{ item.description }}</p>
            </div>
          </div>
        </div>

        <div v-if="!companyLoading && companyResults.length === 0 && companySearched" class="flex items-center justify-center h-32 text-gray-500 font-mono text-sm">
          Нет новостей по запросу "{{ companyQuery }}"
        </div>
      </div>

      <!-- News Search -->
      <div v-else-if="currentTab === 'NSRC'" class="flex flex-col gap-6">
        <div class="data-panel text-center">
          <h3 class="font-anton text-2xl mb-6">ГЛУБОКИЙ ПОИСК ПО РЫНКУ</h3>
          <div class="search-box max-w-2xl mx-auto relative">
            <SearchIcon class="search-icon" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="ПОИСК ПО КОМПАНИИ, ИНВЕСТОРУ, СЕКТОРУ..."
              @keydown.enter="doSearch"
            />
            <button @click="doSearch" class="btn btn-primary absolute right-2 top-1/2 -translate-y-1/2 h-10">
              <ArrowRightIcon class="w-4 h-4" />
            </button>
          </div>
          <div class="flex justify-center gap-3 mt-6">
            <span
              v-for="tag in searchTags"
              :key="tag"
              @click="searchQuery = tag; doSearch()"
              class="badge cursor-pointer hover:border-[var(--accent-red)] hover:color-[var(--accent-red)]"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="searchLoading" class="flex items-center gap-2 text-gray-400 text-xs">
          <div class="w-3 h-3 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
          Поиск "{{ searchQuery }}"...
        </div>

        <!-- Search Results -->
        <div v-if="searchResults.length > 0" class="flex flex-col gap-3">
          <h3 class="font-oswald text-sm text-gray-400 uppercase tracking-wider">
            РЕЗУЛЬТАТЫ: {{ searchResults.length }}
          </h3>
          <div
            v-for="(item, idx) in searchResults"
            :key="idx"
            class="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-white/20 transition-all"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs text-gray-500 font-mono">{{ item.source }} — {{ formatTime(item.publishedAt) }}</span>
              <a :href="item.url" target="_blank" rel="noopener" class="text-xs text-gray-500 hover:text-white font-mono">ОТКРЫТЬ</a>
            </div>
            <h4 class="text-sm text-white font-medium">{{ item.title }}</h4>
            <p v-if="item.description" class="text-xs text-gray-400 mt-1 line-clamp-2">{{ item.description }}</p>
          </div>
        </div>
      </div>

      <!-- News Alerts -->
      <div v-else-if="currentTab === 'SALT'" class="flex flex-col gap-6">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-anton text-xl">УМНЫЕ УВЕДОМЛЕНИЯ</h3>
            <p class="section-subtitle font-mono mt-1">УПРАВЛЯЙТЕ EMAIL-УВЕДОМЛЕНИЯМИ И ТРИГГЕРАМИ</p>
          </div>
          <button class="btn btn-primary">+ СОЗДАТЬ УВЕДОМЛЕНИЕ</button>
        </div>

        <div class="flex flex-col gap-3">
          <div
            v-for="(alert, i) in alerts"
            :key="i"
            class="data-panel flex items-center justify-between"
          >
            <div class="flex items-center gap-4">
              <div :class="['icon-box-sm', alert.active ? 'icon-green' : '']">
                <BellIcon class="w-4 h-4" />
              </div>
              <div>
                <h4 :class="['font-oswald text-sm', alert.active ? 'text-[var(--text-primary)]' : 'text-[var(--text-muted)]']">{{ alert.name }}</h4>
                <p class="font-mono text-xs text-[var(--text-muted)]">{{ alert.condition }}</p>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <span class="font-mono text-xs text-[var(--text-muted)]">{{ alert.active ? 'МГНОВЕННЫЙ EMAIL' : 'ПРИОСТАНОВЛЕНО' }}</span>
              <div :class="['toggle-switch', { active: alert.active }]"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Summaries -->
      <div v-else-if="currentTab === 'FIRS'" class="grid-2">
        <div class="data-panel flex flex-col">
          <div class="data-panel-header">
            <div class="icon-box-sm icon-indigo">
              <BotIcon class="w-4 h-4" />
            </div>
            <h3 class="data-panel-title">ФАКТЫ ПО ЗАПРОСУ</h3>
          </div>
          <p class="section-subtitle font-mono mb-6">ВЫБЕРИТЕ ТРЕНДОВУЮ ТЕМУ ДЛЯ МГНОВЕННОЙ ГЕНЕРАЦИИ AI-РЕЗЮМЕ</p>

          <div class="flex-1 flex flex-col gap-3 overflow-y-auto custom-scrollbar">
            <div
              v-for="(topic, i) in summaryTopics"
              :key="i"
              class="brutalist-card cursor-pointer group"
              @click="generateTopicSummary(i)"
            >
              <h4 class="font-oswald text-sm group-hover:text-[var(--accent-red)] mb-2">{{ topic.title }}</h4>
              <div class="flex items-center justify-between">
                <span class="font-mono text-[10px] text-[var(--text-muted)]">
                  {{ topic.loading ? 'ГЕНЕРАЦИЯ...' : 'ВКЛЮЧАЕТ 12 ИСТОЧНИКОВ' }}
                </span>
                <button class="font-mono text-[10px] text-[var(--accent-red)] opacity-0 group-hover:opacity-100">СГЕНЕРИРОВАТЬ</button>
              </div>
              <p v-if="topic.summary" class="mt-2 text-xs text-gray-300 font-mono leading-relaxed">{{ topic.summary }}</p>
            </div>
          </div>
        </div>

        <div class="data-panel relative overflow-hidden" style="border-color: rgba(220, 38, 38, 0.3)">
          <div class="absolute top-0 right-0 p-8 opacity-10">
            <FileTextIcon class="w-32 h-32" />
          </div>
          <h3 class="font-anton text-lg mb-6">ПОСЛЕДНЕЕ СГЕНЕРИРОВАННОЕ РЕЗЮМЕ</h3>
          <div v-if="lastSummary" class="flex flex-col gap-4">
            <div class="flex items-center gap-2 font-mono text-xs text-[var(--accent-red)]">
              <span>ТЕМА:</span>
              <span class="badge badge-red">{{ lastSummary.topic }}</span>
            </div>
            <p class="font-mono text-sm text-[var(--text-secondary)] leading-relaxed">
              {{ lastSummary.text }}
            </p>
            <div class="pt-4 mt-4 border-t border-[var(--border-dark)] flex gap-3">
              <button class="btn btn-outline flex-1">ПОДЕЛИТЬСЯ</button>
              <button class="btn btn-primary flex-1">ПОЛНЫЙ ОТЧЁТ</button>
            </div>
          </div>
          <div v-else class="text-sm text-gray-500 font-mono">
            Выберите тему для генерации резюме
          </div>
        </div>
      </div>

      <!-- Briefs -->
      <div v-else-if="currentTab === 'BRIE'" class="flex flex-col gap-6">
        <div class="flex items-center justify-between">
          <h3 class="font-anton text-xl">РЫНОЧНЫЕ ОБЗОРЫ</h3>
          <div class="tab-group">
            <button class="tab-btn">ЕЖЕДНЕВНО</button>
            <button class="tab-btn active">ЕЖЕНЕДЕЛЬНО</button>
          </div>
        </div>

        <div class="flex flex-col gap-4">
          <div
            v-for="(brief, i) in briefs"
            :key="i"
            class="data-panel flex items-center justify-between group"
          >
            <div class="flex items-center gap-4">
              <div class="icon-box group-hover:icon-red">
                <BookOpenIcon class="w-5 h-5" />
              </div>
              <div>
                <h4 class="font-oswald text-base mb-1">{{ brief.title }}</h4>
                <div class="flex items-center gap-3 font-mono text-xs text-[var(--text-muted)]">
                  <span>{{ brief.date }}</span>
                  <span>•</span>
                  <span class="uppercase tracking-wider">{{ brief.type }}</span>
                </div>
              </div>
            </div>
            <button class="btn btn-outline">
              <DownloadIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, reactive } from 'vue'
import {
  getTopHeadlines,
  searchNews,
  analyzeSentiment,
  summarizeText,
  type NewsArticle,
  type SentimentScore,
} from '@/services/newsAiService'

interface Props {
  activeSection?: string
}

const props = withDefaults(defineProps<Props>(), {
  activeSection: 'TOP'
})

const currentTab = ref(props.activeSection)

watch(() => props.activeSection, (val) => {
  currentTab.value = val
})

const tabs = [
  { id: 'TOP', label: 'Онлайн', icon: 'ZapIcon', description: 'Актуальные новости рынка в реальном времени' },
  { id: 'CN', label: 'Компании', icon: 'NewspaperIcon', description: 'Новости и события по конкретным компаниям' },
  { id: 'NSRC', label: 'Поиск', icon: 'SearchIcon', description: 'Глубокий поиск по рынку, компаниям и инвесторам' },
  { id: 'SALT', label: 'Уведомления', icon: 'BellIcon', description: 'Управление умными уведомлениями и триггерами' },
  { id: 'FIRS', label: 'Резюме', icon: 'BotIcon', description: 'AI-резюме по трендовым темам и событиям' },
  { id: 'BRIE', label: 'Обзоры', icon: 'BookOpenIcon', description: 'Ежедневные, еженедельные и ежемесячные рыночные обзоры' },
]

const currentTabData = computed(() => tabs.find(t => t.id === currentTab.value) || tabs[0])

// ─── TOP: Headlines ─────────────────────────────────────────────────────────
type EnrichedArticle = NewsArticle & {
  _sentiment?: { scores: SentimentScore[] }
  _sentimentLoading?: boolean
  _summary?: string
  _summarizing?: boolean
}

const headlines = ref<EnrichedArticle[]>([])
const headlinesLoading = ref(false)
const headlinesError = ref<string | null>(null)

const loadHeadlines = async () => {
  headlinesLoading.value = true
  headlinesError.value = null
  try {
    const result = await getTopHeadlines({ pageSize: 30 })
    headlines.value = result.articles.map(a => ({ ...a }))
  } catch (e: unknown) {
    headlinesError.value = e instanceof Error ? e.message : 'Ошибка загрузки новостей'
  } finally {
    headlinesLoading.value = false
  }
}

const doSentiment = async (idx: number) => {
  const item = headlines.value[idx]
  if (!item || item._sentimentLoading) return
  headlines.value = headlines.value.map((h, i) =>
    i === idx ? { ...h, _sentimentLoading: true } : h
  )
  try {
    const text = `${item.title}. ${item.description || ''}`
    const result = await analyzeSentiment(text)
    headlines.value = headlines.value.map((h, i) =>
      i === idx ? { ...h, _sentiment: { scores: result.scores }, _sentimentLoading: false } : h
    )
  } catch {
    headlines.value = headlines.value.map((h, i) =>
      i === idx ? { ...h, _sentimentLoading: false } : h
    )
  }
}

const doSummarize = async (idx: number) => {
  const item = headlines.value[idx]
  if (!item || item._summarizing) return
  headlines.value = headlines.value.map((h, i) =>
    i === idx ? { ...h, _summarizing: true } : h
  )
  try {
    const text = `${item.title}. ${item.description || ''} ${item.content || ''}`
    const result = await summarizeText(text, 120)
    headlines.value = headlines.value.map((h, i) =>
      i === idx ? { ...h, _summary: result.summary, _summarizing: false } : h
    )
  } catch {
    headlines.value = headlines.value.map((h, i) =>
      i === idx ? { ...h, _summarizing: false } : h
    )
  }
}

const sentimentLabel = (scores: SentimentScore[]): string => {
  if (!scores || scores.length === 0) return 'N/A'
  const top = scores.reduce((a, b) => (b.score > a.score ? b : a))
  const labels: Record<string, string> = { POSITIVE: 'ПОЗИТИВ', NEGATIVE: 'НЕГАТИВ', NEUTRAL: 'НЕЙТРАЛ' }
  return labels[top.label] || top.label
}

const sentimentClass = (scores: SentimentScore[]): string => {
  if (!scores || scores.length === 0) return 'bg-gray-500/20 text-gray-400'
  const top = scores.reduce((a, b) => (b.score > a.score ? b : a))
  if (top.label === 'POSITIVE') return 'bg-emerald-500/20 text-emerald-400'
  if (top.label === 'NEGATIVE') return 'bg-rose-500/20 text-rose-400'
  return 'bg-gray-500/20 text-gray-400'
}

const sentimentConfidence = (scores: SentimentScore[]): string => {
  if (!scores || scores.length === 0) return ''
  const top = scores.reduce((a, b) => (b.score > a.score ? b : a))
  return `${(top.score * 100).toFixed(1)}%`
}

// ─── CN: Company News ───────────────────────────────────────────────────────
const companyQuery = ref('')
const companyResults = ref<NewsArticle[]>([])
const companyLoading = ref(false)
const companySearched = ref(false)
const quickTickers = ['NVDA', 'AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'BTC']

const searchCompanyNews = async () => {
  if (!companyQuery.value.trim()) return
  companyLoading.value = true
  companySearched.value = true
  try {
    const result = await searchNews({ q: companyQuery.value, pageSize: 15, sortBy: 'publishedAt' })
    companyResults.value = result.articles
  } catch {
    companyResults.value = []
  } finally {
    companyLoading.value = false
  }
}

// ─── NSRC: General Search ───────────────────────────────────────────────────
const searchQuery = ref('')
const searchResults = ref<NewsArticle[]>([])
const searchLoading = ref(false)
const searchTags = ['Полупроводники', 'Warren Buffet', 'IPO', 'Слияния']

const doSearch = async () => {
  if (!searchQuery.value.trim()) return
  searchLoading.value = true
  try {
    const result = await searchNews({ q: searchQuery.value, pageSize: 20, sortBy: 'relevancy' })
    searchResults.value = result.articles
  } catch {
    searchResults.value = []
  } finally {
    searchLoading.value = false
  }
}

// ─── SALT: Alerts (static for now) ──────────────────────────────────────────
const alerts = [
  { name: 'Предупреждение о падении портфеля', condition: 'Любой актив падает > 5%', active: true },
  { name: 'Новости NVIDIA', condition: 'Ключевые слова: "Прибыль", "Musk"', active: true },
  { name: 'Ставки ФРС', condition: 'Источник: Федеральная резервная система', active: false },
  { name: 'Прорыв Bitcoin', condition: 'BTC > $70k', active: true },
]

// ─── FIRS: AI Summaries ─────────────────────────────────────────────────────
const summaryTopics = reactive([
  { title: 'Обновление о глобальном дефиците чипов', loading: false, summary: '' },
  { title: 'Анализ данных инфляции США', loading: false, summary: '' },
  { title: 'Законопроект о регулировании криптовалют 2025', loading: false, summary: '' },
])

const lastSummary = ref<{ topic: string; text: string } | null>(null)

const generateTopicSummary = async (idx: number) => {
  const topic = summaryTopics[idx]
  if (topic.loading) return
  topic.loading = true
  try {
    const result = await summarizeText(
      `Provide a comprehensive summary about: ${topic.title}. Cover key facts, recent developments, and market implications.`,
      200
    )
    topic.summary = result.summary
    lastSummary.value = { topic: topic.title, text: result.summary }
  } catch {
    topic.summary = 'Не удалось сгенерировать резюме'
  } finally {
    topic.loading = false
  }
}

// ─── BRIE: Briefs (static for now) ──────────────────────────────────────────
const briefs = [
  { title: 'Утренний звонок: Технологический ралли продолжается', date: '24 окт 2025', type: 'Ежедневно' },
  { title: 'Еженедельный обзор криптовалют: Потоки ETF', date: '21 окт 2025', type: 'Еженедельно' },
  { title: 'Макроэкономический прогноз: Проекции Q4', date: '01 окт 2025', type: 'Ежемесячно' },
]

// ─── Helpers ────────────────────────────────────────────────────────────────
const formatTime = (dateStr: string): string => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMin = Math.floor(diffMs / 60000)
    if (diffMin < 1) return 'Только что'
    if (diffMin < 60) return `${diffMin} мин назад`
    const diffHours = Math.floor(diffMin / 60)
    if (diffHours < 24) return `${diffHours} ч назад`
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays < 7) return `${diffDays} д назад`
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
  } catch {
    return dateStr
  }
}

// ─── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(() => {
  loadHeadlines()
})

// Icon components
const ZapIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>' }
const NewspaperIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/></svg>' }
const SearchIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>' }
const BellIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>' }
const BotIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>' }
const BookOpenIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>' }
const ClockIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' }
const ArrowRightIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>' }
const FileTextIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>' }
const DownloadIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>' }
const RefreshIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>' }
</script>
