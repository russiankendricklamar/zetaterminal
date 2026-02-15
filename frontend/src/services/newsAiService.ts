/**
 * News & AI Service — NewsAPI, Currents API, Hugging Face
 *
 * Proxied through backend at /api/news-ai/*
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export interface NewsArticle {
  title: string
  description: string
  url: string
  urlToImage?: string
  image?: string
  publishedAt: string
  source: string
  author?: string
  content?: string
  category?: string[]
}

export interface NewsResponse {
  totalResults?: number
  articles: NewsArticle[]
  provider: string
}

export interface SentimentScore {
  label: string
  score: number
}

export interface SentimentResult {
  text: string
  scores: SentimentScore[]
  provider: string
  model: string
  loading?: boolean
  estimated_time?: number
}

export interface SummarizeResult {
  summary: string
  provider: string
  model: string
  loading?: boolean
  estimated_time?: number
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url)
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || `HTTP error! status: ${response.status}`)
  }
  return response.json()
}

async function postJson<T>(url: string, body: unknown): Promise<T> {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || `HTTP error! status: ${response.status}`)
  }
  return response.json()
}

// ─── NewsAPI ─────────────────────────────────────────────────────────────────

export async function getTopHeadlines(params?: {
  country?: string
  category?: string
  q?: string
  pageSize?: number
}): Promise<NewsResponse> {
  let url = `${API_BASE}/api/news-ai/newsapi/headlines?`
  if (params?.country) url += `country=${params.country}&`
  if (params?.category) url += `category=${params.category}&`
  if (params?.q) url += `q=${encodeURIComponent(params.q)}&`
  if (params?.pageSize) url += `page_size=${params.pageSize}&`
  return fetchJson(url)
}

export async function searchNews(params: {
  q: string
  from?: string
  to?: string
  sortBy?: string
  pageSize?: number
  language?: string
}): Promise<NewsResponse> {
  let url = `${API_BASE}/api/news-ai/newsapi/everything?q=${encodeURIComponent(params.q)}`
  if (params.from) url += `&from=${params.from}`
  if (params.to) url += `&to=${params.to}`
  if (params.sortBy) url += `&sort_by=${params.sortBy}`
  if (params.pageSize) url += `&page_size=${params.pageSize}`
  if (params.language) url += `&language=${params.language}`
  return fetchJson(url)
}

// ─── Currents API ────────────────────────────────────────────────────────────

export async function getLatestNews(params?: {
  language?: string
  keywords?: string
  category?: string
}): Promise<NewsResponse> {
  let url = `${API_BASE}/api/news-ai/currents/latest?`
  if (params?.language) url += `language=${params.language}&`
  if (params?.keywords) url += `keywords=${encodeURIComponent(params.keywords)}&`
  if (params?.category) url += `category=${encodeURIComponent(params.category)}&`
  return fetchJson(url)
}

export async function searchCurrentsNews(keywords: string, language: string = 'en'): Promise<NewsResponse> {
  return fetchJson(`${API_BASE}/api/news-ai/currents/search?keywords=${encodeURIComponent(keywords)}&language=${language}`)
}

// ─── Hugging Face ────────────────────────────────────────────────────────────

export async function runInference(modelId: string, inputs: string): Promise<unknown> {
  return postJson(`${API_BASE}/api/news-ai/huggingface/inference`, { model_id: modelId, inputs })
}

export async function analyzeSentiment(text: string): Promise<SentimentResult> {
  return postJson(`${API_BASE}/api/news-ai/huggingface/sentiment`, { text })
}

export async function summarizeText(text: string, maxLength: number = 150): Promise<SummarizeResult> {
  return postJson(`${API_BASE}/api/news-ai/huggingface/summarize`, { text, max_length: maxLength })
}
