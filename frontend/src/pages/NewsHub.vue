<!-- src/pages/NewsHub.vue — News Hub with AI Analysis -->
<template>
  <div class="page-container">
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Новостной хаб</h1>
        <p class="section-subtitle">NewsAPI + Currents + HuggingFace AI</p>
      </div>
      <div class="header-actions">
        <button class="btn-glass" @click="refreshAll" :disabled="loading">
          {{ loading ? 'Загрузка...' : 'Обновить' }}
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs-navigation">
      <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id" class="tab-item" :class="{ active: activeTab === tab.id }">
        {{ tab.name }}
      </button>
    </div>

    <!-- Search bar -->
    <div class="search-bar">
      <input v-model="searchQuery" class="glass-input full" placeholder="Поиск новостей..." @keyup.enter="doSearch" />
      <select v-model="newsCategory" class="glass-select">
        <option value="">Все</option>
        <option value="business">Business</option>
        <option value="technology">Technology</option>
        <option value="science">Science</option>
        <option value="health">Health</option>
      </select>
      <button class="btn-glass xs" @click="doSearch">Найти</button>
    </div>

    <!-- NewsAPI Headlines -->
    <transition name="fade" mode="out-in">
    <div v-show="activeTab === 'headlines'" class="news-grid">
      <div v-for="(article, idx) in headlines" :key="idx" class="news-card">
        <div class="news-img-wrap" v-if="article.urlToImage">
          <img :src="article.urlToImage" :alt="article.title" class="news-img" />
        </div>
        <div class="news-body">
          <div class="news-meta font-mono">
            <span class="news-source">{{ article.source }}</span>
            <span class="news-date">{{ formatDate(article.publishedAt) }}</span>
          </div>
          <a :href="article.url" target="_blank" rel="noopener" class="news-title">{{ article.title }}</a>
          <p class="news-desc">{{ article.description }}</p>
          <div class="news-actions">
            <button class="btn-glass xs" @click="doSentiment(article.title + '. ' + (article.description || ''), idx)" :disabled="sentimentLoading[idx]">
              {{ sentimentLoading[idx] ? '...' : 'AI Sentiment' }}
            </button>
            <span v-if="sentimentResults[idx]" class="sentiment-badge font-mono" :class="'sentiment-' + sentimentResults[idx].label">
              {{ sentimentResults[idx].label }} ({{ (sentimentResults[idx].score * 100).toFixed(0) }}%)
            </span>
          </div>
        </div>
      </div>
      <p v-if="!headlines.length && !loading" class="text-muted">Нажмите «Обновить» для загрузки новостей</p>
    </div>
    </transition>

    <!-- Currents Latest -->
    <transition name="fade" mode="out-in">
    <div v-show="activeTab === 'currents'" class="news-grid">
      <div v-for="(article, idx) in currentsArticles" :key="idx" class="news-card">
        <div class="news-img-wrap" v-if="article.image">
          <img :src="article.image" :alt="article.title" class="news-img" />
        </div>
        <div class="news-body">
          <div class="news-meta font-mono">
            <span class="news-source">{{ article.source }}</span>
            <span class="news-date">{{ formatDate(article.publishedAt) }}</span>
          </div>
          <a :href="article.url" target="_blank" rel="noopener" class="news-title">{{ article.title }}</a>
          <p class="news-desc">{{ article.description }}</p>
        </div>
      </div>
      <p v-if="!currentsArticles.length && !loading" class="text-muted">Нет данных</p>
    </div>
    </transition>

    <!-- Search Results -->
    <transition name="fade" mode="out-in">
    <div v-show="activeTab === 'search'" class="news-grid">
      <div v-for="(article, idx) in searchResults" :key="idx" class="news-card">
        <div class="news-body">
          <div class="news-meta font-mono">
            <span class="news-source">{{ article.source }}</span>
            <span class="news-date">{{ formatDate(article.publishedAt) }}</span>
          </div>
          <a :href="article.url" target="_blank" rel="noopener" class="news-title">{{ article.title }}</a>
          <p class="news-desc">{{ article.description }}</p>
        </div>
      </div>
      <p v-if="!searchResults.length && !loading" class="text-muted">Введите запрос и нажмите «Найти»</p>
    </div>
    </transition>

    <div v-if="error" class="error-banner">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import {
  getTopHeadlines, getLatestNews, searchNews, analyzeSentiment,
  type NewsArticle, type SentimentScore
} from '@/services/newsAiService'

const loading = ref(false)
const error = ref('')
const activeTab = ref('headlines')
const searchQuery = ref('')
const newsCategory = ref('')

const tabs = [
  { id: 'headlines', name: 'Заголовки' },
  { id: 'currents', name: 'Currents' },
  { id: 'search', name: 'Поиск' },
]

const headlines = ref<NewsArticle[]>([])
const currentsArticles = ref<NewsArticle[]>([])
const searchResults = ref<NewsArticle[]>([])
const sentimentResults = reactive<Record<number, { label: string; score: number }>>({})
const sentimentLoading = reactive<Record<number, boolean>>({})

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function loadHeadlines() {
  try {
    const data = await getTopHeadlines({
      country: 'us',
      category: newsCategory.value || undefined,
      pageSize: 20,
    })
    headlines.value = data.articles
  } catch (e: any) {
    error.value = e.message
  }
}

async function loadCurrents() {
  try {
    const data = await getLatestNews({ language: 'en', keywords: newsCategory.value || undefined })
    currentsArticles.value = data.articles
  } catch (e: any) {
    error.value = e.message
  }
}

async function doSearch() {
  if (!searchQuery.value) return
  activeTab.value = 'search'
  try {
    const data = await searchNews({ q: searchQuery.value, pageSize: 20 })
    searchResults.value = data.articles
  } catch (e: any) {
    error.value = e.message
  }
}

async function doSentiment(text: string, idx: number) {
  if (!text) return
  sentimentLoading[idx] = true
  try {
    const result = await analyzeSentiment(text)
    if (result.scores && result.scores.length) {
      const best = result.scores.reduce((a: SentimentScore, b: SentimentScore) => a.score > b.score ? a : b)
      sentimentResults[idx] = { label: best.label, score: best.score }
    }
  } catch (e: any) {
    error.value = e.message
  } finally {
    sentimentLoading[idx] = false
  }
}

async function refreshAll() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([loadHeadlines(), loadCurrents()])
  } finally {
    loading.value = false
  }
}

onMounted(() => refreshAll())
</script>

<style scoped>
.page-container { padding: 24px 32px; max-width: 1400px; }
.section-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.section-title { font-family: 'Oswald', sans-serif; font-size: 28px; font-weight: 700; text-transform: uppercase; color: #f5f5f5; letter-spacing: 2px; }
.section-subtitle { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #666; margin-top: 4px; }
.header-actions { display: flex; gap: 8px; }

.tabs-navigation { display: flex; gap: 2px; margin-bottom: 16px; border-bottom: 1px solid #1a1a1a; }
.tab-item { padding: 10px 20px; background: transparent; border: none; color: #666; font-family: 'JetBrains Mono', monospace; font-size: 12px; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.2s; text-transform: uppercase; }
.tab-item.active { color: #DC2626; border-bottom-color: #DC2626; }

.search-bar { display: flex; gap: 8px; margin-bottom: 20px; }
.glass-input { background: rgba(255,255,255,0.03); border: 1px solid #333; padding: 8px 12px; color: #f5f5f5; font-family: 'JetBrains Mono', monospace; font-size: 13px; outline: none; }
.glass-input.full { flex: 1; }
.glass-input:focus { border-color: #DC2626; }
.glass-select { background: rgba(255,255,255,0.03); border: 1px solid #333; padding: 8px 12px; color: #f5f5f5; font-family: 'JetBrains Mono', monospace; font-size: 13px; }

.news-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 16px; }
.news-card { background: rgba(255,255,255,0.02); border: 1px solid #1a1a1a; overflow: hidden; transition: border-color 0.2s; }
.news-card:hover { border-color: #333; }
.news-img-wrap { height: 180px; overflow: hidden; }
.news-img { width: 100%; height: 100%; object-fit: cover; }
.news-body { padding: 16px; }
.news-meta { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 11px; }
.news-source { color: #DC2626; }
.news-date { color: #555; }
.news-title { display: block; color: #f5f5f5; font-size: 15px; font-weight: 600; line-height: 1.4; margin-bottom: 8px; text-decoration: none; }
.news-title:hover { color: #DC2626; }
.news-desc { color: #888; font-size: 13px; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.news-actions { display: flex; align-items: center; gap: 10px; margin-top: 12px; }

.sentiment-badge { padding: 2px 8px; font-size: 11px; border: 1px solid; }
.sentiment-positive { color: #22c55e; border-color: #22c55e; }
.sentiment-negative { color: #DC2626; border-color: #DC2626; }
.sentiment-neutral { color: #888; border-color: #555; }

.btn-glass { padding: 8px 16px; background: rgba(255,255,255,0.03); border: 1px solid #333; color: #f5f5f5; font-family: 'JetBrains Mono', monospace; font-size: 12px; cursor: pointer; text-transform: uppercase; }
.btn-glass:hover { border-color: #DC2626; color: #DC2626; }
.btn-glass:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-glass.xs { padding: 4px 10px; font-size: 11px; }
.text-muted { color: #555; font-size: 12px; font-family: 'JetBrains Mono', monospace; }
.error-banner { background: rgba(220,38,38,0.1); border: 1px solid #DC2626; padding: 12px; margin-top: 16px; color: #DC2626; font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.font-mono { font-family: 'JetBrains Mono', monospace; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
