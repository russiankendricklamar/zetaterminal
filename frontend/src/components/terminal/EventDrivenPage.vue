<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box icon-purple">
          <RadioIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">ИВЕНТ-АНАЛИЗ</h2>
          <p class="section-subtitle font-mono">НОВОСТИ, IPO И КОРПОРАТИВНЫЕ СОБЫТИЯ</p>
        </div>
      </div>
      <div class="tab-group">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['tab-btn', { active: section === tab.id }]">
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex items-center gap-2 text-gray-400 text-xs p-4">
      <div class="w-3 h-3 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
      Загрузка...
    </div>

    <div class="flex-1 flex flex-col gap-6 p-6">
      <!-- ═══ IPO / Market Events ═══ -->
      <div v-if="section === 'IPO'" class="flex flex-col h-full gap-6">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-white">Новости IPO и листингов</h3>
          <button @click="loadIpoNews" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-xs font-bold text-white rounded-lg transition-colors">
            Обновить
          </button>
        </div>

        <div v-if="ipoNews.length > 0" class="flex-1 space-y-4 overflow-auto">
          <div v-for="(article, i) in ipoNews" :key="i" class="p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors cursor-pointer">
            <div class="flex justify-between items-start gap-4">
              <div class="flex-1">
                <h4 class="text-sm font-bold text-white mb-1">{{ article.title }}</h4>
                <p class="text-xs text-gray-400 line-clamp-2">{{ article.description }}</p>
                <div class="flex items-center gap-3 mt-2">
                  <span class="text-[10px] text-gray-500 font-mono">{{ article.source }}</span>
                  <span class="text-[10px] text-gray-600">{{ formatDate(article.publishedAt) }}</span>
                </div>
              </div>
              <a v-if="article.url" :href="article.url" target="_blank" class="text-xs text-purple-400 hover:text-purple-300 whitespace-nowrap">Читать</a>
            </div>
          </div>
        </div>
        <div v-else-if="!loading" class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
          Нет новостей
        </div>
      </div>

      <!-- ═══ Corporate Events (News Search) ═══ -->
      <div v-else-if="section === 'CACS'" class="flex flex-col h-full gap-6">
        <h3 class="text-lg font-bold text-white">Корпоративные события</h3>
        <div class="flex gap-4 items-end">
          <div class="flex-1">
            <input
              v-model="corpEventQuery"
              type="text"
              placeholder="Поиск: дивиденды, buyback, M&A..."
              class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white font-mono focus:border-purple-500/50 outline-none text-sm"
              @keydown.enter="searchCorpEvents"
            />
          </div>
          <button @click="searchCorpEvents" class="px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white rounded-xl font-bold text-sm transition-colors">
            Поиск
          </button>
        </div>

        <div class="flex flex-wrap gap-2">
          <button
            v-for="preset in eventPresets"
            :key="preset"
            @click="corpEventQuery = preset; searchCorpEvents()"
            class="px-3 py-1.5 bg-white/5 hover:bg-white/10 text-xs font-bold text-gray-300 rounded-lg border border-white/5 transition-colors"
          >
            {{ preset }}
          </button>
        </div>

        <div v-if="corpEvents.length > 0" class="flex-1 space-y-4 overflow-auto">
          <div v-for="(article, i) in corpEvents" :key="i" class="p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
            <h4 class="text-sm font-bold text-white mb-1">{{ article.title }}</h4>
            <p class="text-xs text-gray-400 line-clamp-2">{{ article.description }}</p>
            <div class="flex items-center gap-3 mt-2">
              <span class="text-[10px] text-gray-500 font-mono">{{ article.source }}</span>
              <span class="text-[10px] text-gray-600">{{ formatDate(article.publishedAt) }}</span>
              <a v-if="article.url" :href="article.url" target="_blank" class="text-[10px] text-purple-400 hover:text-purple-300">Открыть</a>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ Quick Takes (Sentiment) ═══ -->
      <div v-else-if="section === 'QUIC'" class="flex flex-col h-full gap-6">
        <h3 class="text-lg font-bold text-white">Quick Takes — Анализ настроений</h3>
        <div class="flex gap-4 items-end">
          <div class="flex-1">
            <input
              v-model="sentimentText"
              type="text"
              placeholder="Введите текст для анализа настроений..."
              class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white font-mono focus:border-purple-500/50 outline-none text-sm"
              @keydown.enter="analyzeSentimentText"
            />
          </div>
          <button @click="analyzeSentimentText" class="px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white rounded-xl font-bold text-sm transition-colors">
            Анализ
          </button>
        </div>

        <div v-if="sentimentResult" class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h4 class="text-sm font-bold text-gray-400 uppercase mb-4">Результат</h4>
          <div class="grid grid-cols-3 gap-4">
            <div v-for="score in sentimentResult.scores" :key="score.label" class="text-center p-4 rounded-xl bg-black/20">
              <div class="text-xs text-gray-500 uppercase mb-1">{{ score.label }}</div>
              <div :class="['text-2xl font-bold font-mono', score.label === 'POSITIVE' ? 'text-emerald-400' : score.label === 'NEGATIVE' ? 'text-rose-400' : 'text-gray-300']">
                {{ (score.score * 100).toFixed(1) }}%
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ Key Events ═══ -->
      <div v-else-if="section === 'CM'" class="flex flex-col h-full gap-6">
        <h3 class="text-lg font-bold text-white">Ключевые события рынка</h3>
        <div v-if="keyEventNews.length > 0" class="flex-1 space-y-4 overflow-auto">
          <div v-for="(article, i) in keyEventNews" :key="i" class="p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
            <h4 class="text-sm font-bold text-white mb-1">{{ article.title }}</h4>
            <p class="text-xs text-gray-400 line-clamp-2">{{ article.description }}</p>
            <div class="flex items-center gap-3 mt-2">
              <span class="text-[10px] text-gray-500 font-mono">{{ article.source }}</span>
              <span class="text-[10px] text-gray-600">{{ formatDate(article.publishedAt) }}</span>
            </div>
          </div>
        </div>
        <div v-else-if="!loading" class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
          Нет данных
        </div>
      </div>

      <div v-else class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
        Выберите раздел
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, defineComponent, h } from 'vue'
import { searchNews, analyzeSentiment, type NewsArticle, type SentimentResult } from '@/services/newsAiService'

const RadioIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('circle', { cx: '12', cy: '12', r: '2' }), h('path', { d: 'M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14' })]) })

const props = defineProps<{ symbol?: string; activeSection?: string }>()
const section = ref(props.activeSection || 'IPO')
watch(() => props.activeSection, (v) => { if (v) section.value = v })

const tabs = [
  { id: 'IPO', label: 'IPO / Листинги' },
  { id: 'CACS', label: 'Корпоративные события' },
  { id: 'QUIC', label: 'Sentiment анализ' },
  { id: 'CM', label: 'Ключевые события' },
]

const loading = ref(false)

// IPO News
const ipoNews = ref<NewsArticle[]>([])

const loadIpoNews = async () => {
  loading.value = true
  try {
    const res = await searchNews({ q: 'IPO listing stock market', pageSize: 20 })
    ipoNews.value = res.articles
  } catch {
    ipoNews.value = []
  } finally {
    loading.value = false
  }
}

// Corporate Events
const corpEventQuery = ref('dividends buyback')
const corpEvents = ref<NewsArticle[]>([])
const eventPresets = ['dividends', 'M&A merger acquisition', 'stock buyback', 'earnings report', 'stock split', 'bankruptcy']

const searchCorpEvents = async () => {
  if (!corpEventQuery.value.trim()) return
  loading.value = true
  try {
    const res = await searchNews({ q: corpEventQuery.value.trim(), pageSize: 20 })
    corpEvents.value = res.articles
  } catch {
    corpEvents.value = []
  } finally {
    loading.value = false
  }
}

// Sentiment Analysis
const sentimentText = ref('')
const sentimentResult = ref<SentimentResult | null>(null)

const analyzeSentimentText = async () => {
  if (!sentimentText.value.trim()) return
  loading.value = true
  try {
    sentimentResult.value = await analyzeSentiment(sentimentText.value.trim())
  } catch {
    sentimentResult.value = null
  } finally {
    loading.value = false
  }
}

// Key Events
const keyEventNews = ref<NewsArticle[]>([])

const loadKeyEvents = async () => {
  loading.value = true
  try {
    const res = await searchNews({ q: 'Federal Reserve ECB central bank rate decision market crash rally', pageSize: 20 })
    keyEventNews.value = res.articles
  } catch {
    keyEventNews.value = []
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr: string): string => {
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
  } catch {
    return dateStr
  }
}

watch(section, (s) => {
  if (s === 'CM' && keyEventNews.value.length === 0) loadKeyEvents()
})

onMounted(() => {
  loadIpoNews()
})
</script>
