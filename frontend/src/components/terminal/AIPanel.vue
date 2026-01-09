<template>
  <div class="w-full h-full bg-transparent flex flex-col flex-shrink-0 relative">
    <!-- Header -->
    <div class="px-5 py-4 border-b border-white/5 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="p-1.5 bg-indigo-500/20 rounded-lg border border-indigo-500/30">
          <BotIcon class="w-4 h-4 text-indigo-300" />
        </div>
        <span class="font-bold text-sm text-white">ИИ Аналитик</span>
      </div>
      <div class="flex items-center gap-1.5 px-2 py-1 bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 rounded-full">
        <span class="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse"></span>
        <span class="text-[10px] font-bold text-indigo-300">LIVE</span>
      </div>
    </div>

    <div class="p-5 flex-1 overflow-y-auto space-y-6 custom-scrollbar">
      <div v-if="!analysis && !loading" class="flex flex-col items-center justify-center h-48 text-center space-y-4">
        <div class="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center border border-white/10 shadow-[0_0_30px_rgba(255,255,255,0.05)]">
          <SparklesIcon class="w-6 h-6 text-gray-400" />
        </div>
        <div>
          <h3 class="text-sm font-bold text-white mb-1">Ожидание команды</h3>
          <p class="text-xs text-gray-500 max-w-[200px] mx-auto">
            Анализ рыночных данных для определения трендов и ключевых уровней.
          </p>
        </div>
        <button 
          @click="handleAnalyze"
          class="mt-2 px-6 py-2.5 bg-white text-black rounded-full text-xs font-bold hover:scale-105 transition-transform shadow-[0_0_20px_rgba(255,255,255,0.3)] flex items-center gap-2"
        >
          <ZapIcon class="w-3.5 h-3.5 fill-current" /> Запустить анализ
        </button>
      </div>

      <div v-if="loading" class="flex flex-col items-center justify-center h-48 space-y-4">
        <div class="relative w-12 h-12">
          <div class="absolute inset-0 border-2 border-indigo-500/30 rounded-full"></div>
          <div class="absolute inset-0 border-t-2 border-indigo-400 rounded-full animate-spin"></div>
        </div>
        <span class="text-xs font-mono text-indigo-300 animate-pulse">Обработка рыночных данных...</span>
      </div>

      <!-- Results -->
      <div v-if="analysis" class="space-y-5 animate-fade-in">
        <!-- Trend Card -->
        <div class="relative overflow-hidden p-4 rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-transparent">
          <div class="absolute top-0 right-0 p-3 opacity-10">
            <component :is="analysis.trend === 'BULLISH' ? 'TrendingUpIcon' : 'TrendingDownIcon'" class="w-15 h-15" />
          </div>
          
          <span class="text-[10px] text-gray-400 uppercase font-bold tracking-widest">Сигнал</span>
          <div class="flex items-center gap-3 mt-1">
            <h2 :class="`text-2xl font-bold tracking-tight ${
              analysis.trend === 'BULLISH' ? 'text-emerald-400 drop-shadow-[0_0_10px_rgba(52,211,153,0.5)]' : 
              analysis.trend === 'BEARISH' ? 'text-rose-400 drop-shadow-[0_0_10px_rgba(248,113,113,0.5)]' : 'text-gray-200'
            }`">
              {{ analysis.trend }}
            </h2>
          </div>
          
          <div class="mt-4">
            <div class="flex justify-between text-[10px] mb-1.5">
              <span class="text-gray-400">Уверенность</span>
              <span class="text-white font-mono">{{ analysis.confidence }}%</span>
            </div>
            <div class="h-1.5 w-full bg-black/40 rounded-full overflow-hidden border border-white/5">
              <div 
                :class="`h-full rounded-full shadow-[0_0_10px_currentColor] ${analysis.confidence > 70 ? 'bg-emerald-500 text-emerald-500' : 'bg-amber-500 text-amber-500'}`" 
                :style="{ width: `${analysis.confidence}%` }"
              />
            </div>
          </div>
        </div>

        <!-- Reasoning -->
        <div class="p-4 rounded-2xl bg-black/20 border border-white/5 backdrop-blur-sm">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-1 h-3 bg-indigo-500 rounded-full"></div>
            <span class="text-[10px] text-indigo-300 font-bold uppercase">Анализ</span>
          </div>
          <p class="text-xs text-gray-300 leading-relaxed font-light">
            {{ analysis.reasoning }}
          </p>
        </div>

        <!-- Levels -->
        <div class="grid grid-cols-2 gap-3">
          <div class="p-3 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 text-center">
            <span class="text-[10px] text-emerald-300/70 block uppercase font-bold mb-1">Поддержка</span>
            <span class="text-sm font-mono text-emerald-400 font-bold">{{ analysis.keyLevels.support.toFixed(2) }}</span>
          </div>
          <div class="p-3 rounded-2xl bg-rose-500/5 border border-rose-500/20 text-center">
            <span class="text-[10px] text-rose-300/70 block uppercase font-bold mb-1">Сопротивление</span>
            <span class="text-sm font-mono text-rose-400 font-bold">{{ analysis.keyLevels.resistance.toFixed(2) }}</span>
          </div>
        </div>
        
        <button 
          @click="handleAnalyze" 
          class="w-full py-2 mt-2 text-xs text-gray-500 hover:text-white transition-colors flex items-center justify-center gap-2"
        >
          <RefreshCwIcon class="w-3 h-3" /> Обновить анализ
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Candle, AIAnalysisResult } from '@/types/terminal';
import { analyzeMarketData } from '@/services/geminiService';

interface Props {
  data: Candle[];
}

const props = defineProps<Props>();

const analysis = ref<AIAnalysisResult | null>(null);
const loading = ref(false);

const handleAnalyze = async () => {
  if (loading.value) return;
  loading.value = true;
  const result = await analyzeMarketData(props.data);
  analysis.value = result;
  loading.value = false;
};

// Icon components
const BotIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>' };
const SparklesIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>' };
const ZapIcon = { template: '<svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>' };
const TrendingUpIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
const TrendingDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>' };
const RefreshCwIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>' };
</script>
