<template>
  <div class="ai-panel">
    <!-- Header -->
    <div class="ai-header">
      <div class="ai-header-left">
        <div class="ai-icon">
          <BotIcon class="w-4 h-4" />
        </div>
        <span class="ai-title font-oswald">ИИ АНАЛИТИК</span>
      </div>
      <div class="ai-status font-mono">
        <span class="status-dot"></span>
        <span>LIVE</span>
      </div>
    </div>

    <div class="ai-content custom-scrollbar">
      <!-- Idle State -->
      <div v-if="!analysis && !loading" class="ai-idle">
        <div class="idle-icon">
          <SparklesIcon class="w-6 h-6" />
        </div>
        <div class="idle-text">
          <h3 class="font-oswald">ОЖИДАНИЕ КОМАНДЫ</h3>
          <p class="font-mono">Анализ рыночных данных для определения трендов и ключевых уровней.</p>
        </div>
        <button @click="handleAnalyze" class="ai-btn font-oswald">
          <ZapIcon class="w-3.5 h-3.5" /> ЗАПУСТИТЬ АНАЛИЗ
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="ai-loading">
        <div class="loading-spinner"></div>
        <span class="font-mono">ОБРАБОТКА РЫНОЧНЫХ ДАННЫХ...</span>
      </div>

      <!-- Results -->
      <div v-if="analysis" class="ai-results">
        <!-- Trend Card -->
        <div class="trend-card">
          <span class="trend-label font-mono">СИГНАЛ</span>
          <div class="trend-value">
            <h2
              :class="['trend-text font-anton', {
                'trend-bullish': analysis.trend === 'BULLISH',
                'trend-bearish': analysis.trend === 'BEARISH'
              }]"
            >
              {{ analysis.trend }}
            </h2>
          </div>

          <div class="confidence-section">
            <div class="confidence-header font-mono">
              <span>УВЕРЕННОСТЬ</span>
              <span>{{ analysis.confidence }}%</span>
            </div>
            <div class="confidence-bar">
              <div
                :class="['confidence-fill', { 'high': analysis.confidence > 70 }]"
                :style="{ width: `${analysis.confidence}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Reasoning -->
        <div class="reasoning-card">
          <div class="reasoning-header">
            <div class="reasoning-indicator"></div>
            <span class="font-mono">АНАЛИЗ</span>
          </div>
          <p class="reasoning-text font-mono">{{ analysis.reasoning }}</p>
        </div>

        <!-- Levels -->
        <div class="levels-grid">
          <div class="level-card level-support">
            <span class="level-label font-mono">ПОДДЕРЖКА</span>
            <span class="level-value font-mono">{{ analysis.keyLevels.support.toFixed(2) }}</span>
          </div>
          <div class="level-card level-resistance">
            <span class="level-label font-mono">СОПРОТИВЛЕНИЕ</span>
            <span class="level-value font-mono">{{ analysis.keyLevels.resistance.toFixed(2) }}</span>
          </div>
        </div>

        <button @click="handleAnalyze" class="refresh-btn font-mono">
          <RefreshCwIcon class="w-3 h-3" /> ОБНОВИТЬ АНАЛИЗ
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
const RefreshCwIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>' };
</script>

<style scoped>
/* ============================================
   AI PANEL - BRUTALIST
   ============================================ */
.ai-panel {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: transparent;
}

.ai-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #1a1a1a;
}

.ai-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-icon {
  width: 28px;
  height: 28px;
  background: rgba(168, 85, 247, 0.15);
  border: 1px solid rgba(168, 85, 247, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a855f7;
}

.ai-title {
  font-size: 12px;
  font-weight: 500;
  color: #f5f5f5;
  letter-spacing: 0.1em;
}

.ai-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  color: #DC2626;
  letter-spacing: 0.1em;
}

.status-dot {
  width: 6px;
  height: 6px;
  background: #DC2626;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.ai-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

/* Idle State */
.ai-idle {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  text-align: center;
  gap: 16px;
}

.idle-icon {
  width: 64px;
  height: 64px;
  background: #0a0a0a;
  border: 1px solid #262626;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #525252;
}

.idle-text h3 {
  font-size: 14px;
  color: #f5f5f5;
  letter-spacing: 0.1em;
  margin-bottom: 6px;
}

.idle-text p {
  font-size: 11px;
  color: #525252;
  max-width: 200px;
}

.ai-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #DC2626;
  border: none;
  color: #000;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.1em;
  cursor: pointer;
  transition: all 0.2s;
}

.ai-btn:hover {
  background: #f5f5f5;
}

/* Loading State */
.ai-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  gap: 16px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 2px solid #1a1a1a;
  border-top-color: #DC2626;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.ai-loading span {
  font-size: 11px;
  color: #DC2626;
  letter-spacing: 0.1em;
}

/* Results */
.ai-results {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.trend-card {
  padding: 16px;
  background: #050505;
  border: 1px solid #1a1a1a;
}

.trend-label {
  font-size: 10px;
  color: #525252;
  letter-spacing: 0.15em;
}

.trend-value {
  margin-top: 8px;
}

.trend-text {
  font-size: 28px;
  font-weight: 400;
  letter-spacing: 0.05em;
}

.trend-bullish {
  color: #22c55e;
}

.trend-bearish {
  color: #DC2626;
}

.confidence-section {
  margin-top: 16px;
}

.confidence-header {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: #525252;
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}

.confidence-header span:last-child {
  color: #f5f5f5;
}

.confidence-bar {
  height: 4px;
  background: #1a1a1a;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: #f59e0b;
  transition: width 0.3s ease;
}

.confidence-fill.high {
  background: #22c55e;
}

/* Reasoning */
.reasoning-card {
  padding: 16px;
  background: #050505;
  border: 1px solid #1a1a1a;
}

.reasoning-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.reasoning-indicator {
  width: 3px;
  height: 12px;
  background: #DC2626;
}

.reasoning-header span {
  font-size: 10px;
  color: #DC2626;
  letter-spacing: 0.15em;
}

.reasoning-text {
  font-size: 12px;
  color: #a3a3a3;
  line-height: 1.6;
}

/* Levels */
.levels-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.level-card {
  padding: 12px;
  text-align: center;
}

.level-support {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.level-resistance {
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.3);
}

.level-label {
  font-size: 9px;
  letter-spacing: 0.1em;
  display: block;
  margin-bottom: 4px;
}

.level-support .level-label {
  color: rgba(34, 197, 94, 0.7);
}

.level-resistance .level-label {
  color: rgba(220, 38, 38, 0.7);
}

.level-value {
  font-size: 14px;
  font-weight: 600;
}

.level-support .level-value {
  color: #22c55e;
}

.level-resistance .level-value {
  color: #DC2626;
}

.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px;
  background: transparent;
  border: 1px solid #262626;
  color: #525252;
  font-size: 10px;
  letter-spacing: 0.1em;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover {
  border-color: #DC2626;
  color: #DC2626;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 768px) {
  .ai-content {
    padding: 12px;
  }

  .ai-header {
    padding: 10px 12px;
  }
}

@media (max-width: 480px) {
  .ai-content {
    padding: 8px;
  }

  .trend-text {
    font-size: 24px;
  }

  .level-value {
    font-size: 12px;
  }
}
</style>
