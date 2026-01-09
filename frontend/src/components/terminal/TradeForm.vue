<template>
  <div class="w-full h-full flex flex-col p-4 relative overflow-hidden">
    <!-- Progress Bar Top -->
    <div class="absolute top-0 left-0 w-full h-[3px] bg-white/5 overflow-hidden z-10">
      <div 
        :key="newsIndex" 
        class="progress-bar h-full bg-gradient-to-l from-blue-500 via-blue-400 to-cyan-400 shadow-[0_0_15px_rgba(59,130,246,0.8)]"
      ></div>
    </div>

    <!-- Header -->
    <div class="flex items-center justify-between mb-4 flex-shrink-0">
      <span class="text-xs uppercase font-bold text-gray-400 tracking-wider flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-blue-500 animate-pulse shadow-[0_0_10px_rgba(59,130,246,0.5)]"></div> 
        ЛЕНТА НОВОСТЕЙ
      </span>
      <span class="text-[10px] text-emerald-400 font-mono flex items-center gap-1 bg-emerald-500/10 px-2 py-1 rounded-full border border-emerald-500/20">
        <ClockIcon class="w-2.5 h-2.5" /> Онлайн
      </span>
    </div>

    <!-- Sentiment & Time -->
    <div class="flex justify-between items-start animate-fade-in mb-3">
      <span :class="`px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wide border flex items-center gap-1.5 ${getSentimentColor(currentNews.sentiment)}`">
        <component :is="getSentimentIcon(currentNews.sentiment)" class="w-3.5 h-3.5" />
        {{ currentNews.sentiment }}
      </span>
      <span class="text-[10px] text-gray-500 font-mono flex items-center gap-1">
        <ClockIcon class="w-2.5 h-2.5" /> {{ currentNews.time }}
      </span>
    </div>

    <!-- News Title -->
    <div class="flex-1 flex flex-col justify-center">
      <h3 class="text-sm font-semibold text-white leading-relaxed animate-fade-in">
        {{ currentNews.title }}
      </h3>
    </div>

    <!-- Source -->
    <div class="flex items-center justify-between pt-3 mt-auto border-t border-white/5">
      <div class="flex items-center gap-2">
        <div class="w-6 h-6 rounded-lg bg-white/10 flex items-center justify-center text-[10px] font-bold text-gray-300 border border-white/10">
          {{ currentNews.source.substring(0,1) }}
        </div>
        <span class="text-xs text-gray-400">{{ currentNews.source }}</span>
      </div>
      <button class="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-500 hover:text-white transition-colors">
        <ArrowUpRightIcon class="w-3.5 h-3.5" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';

interface NewsItem {
  title: string;
  source: string;
  time: string;
  sentiment: 'positive' | 'negative' | 'neutral';
}

const newsItems: NewsItem[] = [
  { title: "Крупный перевод: 5,000 ETH отправлено на биржевой кошелёк", source: "WhaleWatch", time: "2 мин", sentiment: "negative" },
  { title: "BTC ETF: рекордный приток средств от институционалов", source: "Bloomberg", time: "15 мин", sentiment: "positive" },
  { title: "ФРС сигнализирует о возможном снижении ставок в Q4", source: "Reuters", time: "32 мин", sentiment: "positive" },
  { title: "Сеть Solana восстановлена после развёртывания патча", source: "Coindesk", time: "1 час", sentiment: "positive" },
  { title: "Ожидается волатильность перед публикацией данных CPI", source: "CNBC", time: "2 часа", sentiment: "neutral" }
];

const newsIndex = ref(0);
let interval: number | null = null;

const currentNews = computed(() => newsItems[newsIndex.value]);

const getSentimentIcon = (sentiment: string) => {
  if (sentiment === 'positive') return 'TrendingUpIcon';
  if (sentiment === 'negative') return 'TrendingDownIcon';
  return 'MinusIcon';
};

const getSentimentColor = (sentiment: string) => {
  if (sentiment === 'positive') return 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400';
  if (sentiment === 'negative') return 'bg-rose-500/10 border-rose-500/20 text-rose-400';
  return 'bg-blue-500/10 border-blue-500/20 text-blue-400';
};

onMounted(() => {
  interval = window.setInterval(() => {
    newsIndex.value = (newsIndex.value + 1) % newsItems.length;
  }, 6000);
});

onBeforeUnmount(() => {
  if (interval) clearInterval(interval);
});

// Simple icon components
const ClockIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' };
const TrendingUpIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
const TrendingDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>' };
const MinusIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/></svg>' };
const GlobeIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>' };
const ZapIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>' };
const ArrowUpRightIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>' };
</script>

<style scoped>
.progress-bar {
  width: 100%;
  transform-origin: left;
  animation: countdown 6s linear forwards;
}

@keyframes countdown {
  from { 
    transform: scaleX(1);
  }
  to { 
    transform: scaleX(0);
  }
}
</style>
