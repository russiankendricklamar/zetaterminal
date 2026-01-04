<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Стресс-тестирование</h1>
        <p class="section-subtitle">Симуляция экстремальных рыночных шоков</p>
      </div>
      
      <div class="header-right">
        <!-- Severity Multiplier -->
        <div class="glass-pill control-pill">
            <span class="lbl-mini">Множитель шока:</span>
            <div class="scrub-wrapper">
                <input 
                    type="range"
                    v-model.number="shockMultiplier"
                    :step="0.1"
                    :min="0.5"
                    :max="3.0"
                    class="range-slider"
                />
                <span class="scrub-val text-accent">{{ shockMultiplier.toFixed(1) }}x</span>
            </div>
        </div>

        <button @click="runAllStressTests" class="btn-glass primary" :disabled="isRunning">
          <span v-if="!isRunning" class="flex items-center gap-2">
             <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
             <span>Запустить все</span>
          </span>
          <span v-else class="flex items-center gap-2">
             <span class="spinner-mini"></span> Тестирую...
          </span>
        </button>
      </div>
    </div>

    <!-- Scenarios Grid -->
    <div class="scenarios-grid">
      <div 
        v-for="scenario in scenarios" 
        :key="scenario.id"
        @click="selectScenario(scenario)"
        class="glass-card scenario-card"
        :class="{ active: selectedScenario?.id === scenario.id }"
      >
        <div class="sc-header">
          <span class="sc-name">{{ scenario.name }}</span>
          <span class="badge" :class="scenario.severity">{{ scenario.severity }}</span>
        </div>
        <p class="sc-desc">{{ scenario.description }}</p>
        <div class="sc-footer">
            <span class="sc-impact" :class="getImpact(scenario.pnlImpact) < 0 ? 'text-red' : 'text-green'">
                {{ formatCurrencyCompact(getImpact(scenario.pnlImpact)) }}
            </span>
            <span class="sc-prob">Вероятность: {{ (scenario.probability * 100).toFixed(0) }}%</span>
        </div>
      </div>
    </div>

    <!-- Selected Scenario Detail (Split View) -->
    <transition name="fade" mode="out-in">
    <div v-if="selectedScenario" class="dashboard-grid">
        
        <!-- Left: Impact Analysis & Stats -->
        <div class="col-left">
            <div class="glass-card panel">
                <div class="panel-header">
                    <h3>Влияние сценария: <span class="text-white">{{ selectedScenario.name }}</span></h3>
                </div>
                
                <!-- 4 Key Metrics -->
                <div class="impact-metrics-grid">
                    <div class="metric-box">
                        <span class="lbl">P&L Impact</span>
                        <span class="val text-red">{{ formatCurrency(getImpact(selectedScenario.pnlImpact)) }}</span>
                    </div>
                    <div class="metric-box">
                        <span class="lbl">VaR Change</span>
                        <span class="val" :class="selectedScenario.varChange < 0 ? 'text-red' : 'text-green'">
                            {{ (selectedScenario.varChange * shockMultiplier).toFixed(1) }}%
                        </span>
                    </div>
                    <div class="metric-box">
                        <span class="lbl">Duration</span>
                        <span class="val text-white">{{ selectedScenario.duration }}</span>
                    </div>
                     <div class="metric-box">
                        <span class="lbl">Probability</span>
                        <span class="val text-orange">{{ (selectedScenario.probability * 100).toFixed(1) }}%</span>
                    </div>
                </div>

                <div class="divider"></div>

                <!-- Asset Impact Bars -->
                <div class="panel-header">
                    <h3>Влияние на классы активов</h3>
                </div>
                <div class="impact-bars-list">
                    <div v-for="(baseImpact, asset) in selectedScenario.assetImpact" :key="asset" class="bar-row">
                        <span class="bar-label">{{ asset }}</span>
                        <div class="bar-track">
                             <div class="bar-fill" 
                                  :class="baseImpact < 0 ? 'bg-red' : 'bg-green'"
                                  :style="{ width: Math.min(100, Math.abs(baseImpact * shockMultiplier * 1.5)) + '%' }">
                             </div>
                        </div>
                        <span class="bar-val" :class="baseImpact < 0 ? 'text-red' : 'text-green'">
                            {{ baseImpact > 0 ? '+' : '' }}{{ (baseImpact * shockMultiplier).toFixed(1) }}%
                        </span>
                    </div>
                </div>

                <div class="divider"></div>

                <!-- Stats Mini Panel -->
                <div class="panel-header">
                    <h3>Статистика риска (Risk Stats)</h3>
                </div>
                <div class="stats-grid-row">
                     <div class="stat-box">
                         <span class="lbl-sm">Avg Loss</span>
                         <span class="val-sm text-red">{{ formatCurrencyCompact(avgLoss * shockMultiplier) }}</span>
                     </div>
                     <div class="stat-box">
                         <span class="lbl-sm">Max Drawdown</span>
                         <span class="val-sm text-red">{{ formatCurrencyCompact(maxLoss * shockMultiplier) }}</span>
                     </div>
                     <div class="stat-box">
                         <span class="lbl-sm">Expected Shortfall</span>
                         <span class="val-sm text-orange">{{ formatCurrencyCompact(expectedLoss * shockMultiplier) }}</span>
                     </div>
                </div>
            </div>
        </div>

        <!-- Right: Market Conditions -->
        <aside class="col-right">
            <div class="glass-card panel sticky-panel">
                <div class="panel-header">
                    <h3>Рыночные условия</h3>
                </div>
                <div class="market-changes-list">
                    <div v-for="(change, key) in selectedScenario.marketChanges" :key="key" class="market-row">
                        <span class="m-key">{{ formatLabel(key) }}</span>
                        <span class="m-val" :class="change.includes('-') ? 'text-red' : 'text-green'">{{ change }}</span>
                    </div>
                </div>
                <div class="divider"></div>
                <div class="info-block">
                    <p class="text-xs text-muted">
                        Метрики пересчитаны с учетом коэффициента шока: <b class="text-white">{{ shockMultiplier.toFixed(1) }}x</b>.
                    </p>
                </div>
            </div>
        </aside>
    </div>
    </transition>

    <!-- Comparison Table -->
    <div class="glass-card panel">
      <div class="panel-header">
        <h3>Сравнение сценариев</h3>
      </div>
      <div class="table-wrapper">
        <table class="glass-table">
          <thead>
            <tr>
              <th class="col-left pl-4">Сценарий</th>
              <th>P&L Impact</th>
              <th>VaR Change</th>
              <th>Duration</th>
              <th>Prob.</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="scenario in scenarios" :key="scenario.id" 
                class="hover-row"
                :class="{ 'row-active': selectedScenario?.id === scenario.id }"
                @click="selectScenario(scenario)">
              <td class="col-left pl-4">
                <span class="sc-name-sm">{{ scenario.name }}</span>
              </td>
              <td :class="scenario.pnlImpact < 0 ? 'text-red' : 'text-green'">
                {{ formatCurrency(getImpact(scenario.pnlImpact)) }}
              </td>
              <td :class="scenario.varChange < 0 ? 'text-red' : 'text-green'">
                {{ (scenario.varChange * shockMultiplier).toFixed(1) }}%
              </td>
              <td class="text-muted">{{ scenario.duration }}</td>
              <td class="text-orange">{{ (scenario.probability * 100).toFixed(1) }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Footer Notes -->
    <div class="footer-notes">
        <span class="note-item">Данные основаны на исторических корреляциях</span>
        <span class="note-item">•</span>
        <span class="note-item">Рекомендуется ежеквартальный пересмотр</span>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const isRunning = ref(false)
const shockMultiplier = ref(1.0)

const scenarios = ref([
  {
    id: 1,
    name: '«Чёрный лебедь»',
    description: 'Глобальный рыночный крах (как COVID-19)',
    pnlImpact: -185000,
    varChange: -45.5,
    duration: '1–3 дня',
    probability: 0.01,
    severity: 'critical',
    marketChanges: { 'Волатильность': '+25%', 'Bonds Yield': '+150 bps', 'Correlation': '+0.50', 'Spreads': '+100 bps' },
    assetImpact: { 'Акции': -35, 'Облигации': -12, 'Товары': -25, 'Валюта': -8 }
  },
  {
    id: 2,
    name: 'Скачок волатильности',
    description: 'Резкий рост индекса VIX > 40',
    pnlImpact: -67500,
    varChange: -18.2,
    duration: '1–5 дней',
    probability: 0.05,
    severity: 'high',
    marketChanges: { 'VIX': '+20 pts', 'Range': '+15%', 'Liquidity': '-10%' },
    assetImpact: { 'Акции': -18, 'Облигации': -5, 'Опционы': -40, 'Валюта': -3 }
  },
  {
    id: 3,
    name: 'Рост ставок ЦБ',
    description: 'Неожиданное повышение ставки на 100 б.п.',
    pnlImpact: -45200,
    varChange: -12.5,
    duration: '1–10 дней',
    probability: 0.15,
    severity: 'high',
    marketChanges: { 'Key Rate': '+100 bps', 'Spreads': '+50 bps', 'FX Rate': '-5%' },
    assetImpact: { 'Акции': -12, 'Облигации': -22, 'Недвижимость': -15, 'Валюта': -6 }
  },
  {
    id: 4,
    name: 'Техническая коррекция',
    description: 'Умеренное снижение S&P 500 на 10%',
    pnlImpact: -12400,
    varChange: -5.2,
    duration: '5–20 дней',
    probability: 0.35,
    severity: 'medium',
    marketChanges: { 'Index': '-8%', 'Volatility': '+10%', 'Spreads': '+20 bps' },
    assetImpact: { 'Акции': -8, 'Облигации': 2, 'Товары': -5, 'Валюта': -2 }
  }
])

const selectedScenario = ref(scenarios.value[0])
const selectScenario = (scenario: any) => selectedScenario.value = scenario

// Helpers
const getImpact = (val: number) => val * shockMultiplier.value
const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val)
const formatCurrencyCompact = (val: number) => '$' + (val / 1000).toFixed(0) + 'k'
const formatLabel = (key: string) => key.charAt(0).toUpperCase() + key.slice(1)

const avgLoss = computed(() => scenarios.value.reduce((sum, s) => sum + s.pnlImpact, 0) / scenarios.value.length)
const maxLoss = computed(() => Math.min(...scenarios.value.map(s => s.pnlImpact)))
const expectedLoss = computed(() => scenarios.value.reduce((sum, s) => sum + s.pnlImpact * s.probability, 0))

const runAllStressTests = async () => {
  if (isRunning.value) return
  isRunning.value = true
  
  try {
    for (let i = 0; i <= 100; i += 20) {
      await new Promise(r => setTimeout(r, 250))
    }
  } catch (e) {
    console.error(e)
  } finally {
    isRunning.value = false
  }
}
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.page-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px 32px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 4px;
  flex-shrink: 0;
  gap: 20px;
}

.header-left {
  display: flex;
  flex-direction: column;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #fff;
  letter-spacing: -0.01em;
}

.section-subtitle {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  margin: 0;
}

/* ============================================
   GLASS COMPONENTS
   ============================================ */
.glass-card {
  border-radius: 20px;
  overflow: hidden;
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 20px 40px -10px rgba(0,0,0,0.4);
}

.glass-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 16px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 99px;
  height: 40px;
  flex-shrink: 0;
}

.lbl-mini {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.scrub-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 80px;
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  outline: none;
  cursor: pointer;
}

.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 14px;
  height: 14px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: grab;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.range-slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: grab;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
  border: none;
}

.scrub-val {
  font-family: "SF Mono", monospace;
  font-weight: 700;
  font-size: 13px;
  width: 35px;
  text-align: right;
  white-space: nowrap;
}

.panel {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-header h3 {
  margin: 0;
  font-size: 11px;
  font-weight: 600;
  color: rgba(255,255,255,0.5);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.divider {
  height: 1px;
  background: rgba(255,255,255,0.08);
  margin: 4px 0;
}

/* ============================================
   SCENARIOS GRID
   ============================================ */
.scenarios-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.scenario-card {
  padding: 20px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 160px;
  position: relative;
  transition: all 0.2s;
}

.scenario-card:hover {
  transform: translateY(-3px);
  background: rgba(255,255,255,0.05);
}

.scenario-card.active {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.4);
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.15);
}

.sc-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  gap: 8px;
}

.sc-name {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
  flex: 1;
}

.sc-desc {
  font-size: 12px;
  color: rgba(255,255,255,0.5);
  line-height: 1.4;
  flex-grow: 1;
  margin: 0;
}

.sc-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-top: 12px;
  gap: 8px;
}

.sc-impact {
  font-family: "SF Mono", monospace;
  font-weight: 700;
  font-size: 16px;
  letter-spacing: -0.02em;
}

.sc-prob {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
  font-weight: 500;
}

.badge {
  font-size: 9px;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 700;
  letter-spacing: 0.05em;
  white-space: nowrap;
  flex-shrink: 0;
}

.badge.critical {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.badge.high {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
}

.badge.medium {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

/* ============================================
   DASHBOARD SPLIT VIEW
   ============================================ */
.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  align-items: start;
}

.col-left,
.col-right {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sticky-panel {
  position: sticky;
  top: 20px;
}

/* Impact Metrics */
.impact-metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.metric-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: rgba(255,255,255,0.03);
  padding: 12px;
  border-radius: 10px;
}

.metric-box .lbl {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.metric-box .val {
  font-family: "SF Mono", monospace;
  font-weight: 600;
  font-size: 16px;
  line-height: 1;
}

/* Asset Bars */
.impact-bars-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bar-row {
  display: grid;
  grid-template-columns: 100px 1fr 60px;
  align-items: center;
  gap: 12px;
}

.bar-label {
  font-size: 12px;
  color: rgba(255,255,255,0.7);
  font-weight: 500;
}

.bar-track {
  height: 6px;
  background: rgba(255,255,255,0.05);
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.bar-val {
  font-family: "SF Mono", monospace;
  font-size: 12px;
  text-align: right;
  font-weight: 600;
}

/* Stats Grid Row */
.stats-grid-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: rgba(255,255,255,0.03);
  padding: 10px;
  border-radius: 8px;
}

.lbl-sm {
  font-size: 9px;
  color: rgba(255,255,255,0.4);
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.val-sm {
  font-family: "SF Mono", monospace;
  font-weight: 600;
  font-size: 13px;
}

/* Market Changes */
.market-changes-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.market-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  padding-bottom: 8px;
  font-size: 13px;
}

.market-row:last-child {
  border-bottom: none;
}

.m-key {
  color: rgba(255,255,255,0.6);
  font-weight: 500;
}

.m-val {
  font-family: "SF Mono", monospace;
  font-weight: 600;
}

.info-block {
  background: rgba(255,255,255,0.02);
  padding: 12px;
  border-radius: 8px;
  border-left: 2px solid rgba(59, 130, 246, 0.3);
}

.text-xs {
  font-size: 11px;
  line-height: 1.5;
}

/* ============================================
   TABLE
   ============================================ */
.table-wrapper {
  overflow-x: auto;
  border-radius: 0 0 20px 20px;
}

.glass-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.glass-table th {
  text-align: right;
  padding: 12px 12px;
  color: rgba(255,255,255,0.4);
  font-weight: 600;
  font-size: 10px;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.02);
}

.glass-table th.col-left {
  text-align: left;
  padding-left: 20px;
}

.glass-table td {
  text-align: right;
  padding: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  font-family: "SF Mono", monospace;
  color: #fff;
  font-weight: 500;
}

.glass-table td.col-left {
  text-align: left;
  font-family: inherit;
  font-weight: 500;
  padding-left: 20px;
}

.hover-row {
  cursor: pointer;
  transition: background 0.1s;
}

.hover-row:hover {
  background: rgba(255,255,255,0.05);
}

.row-active {
  background: rgba(59, 130, 246, 0.1) !important;
}

.sc-name-sm {
  font-weight: 600;
  font-size: 13px;
}

.pl-4 {
  padding-left: 20px !important;
}

/* ============================================
   BUTTONS & UTILS
   ============================================ */
.btn-glass {
  height: 40px;
  padding: 0 16px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-glass.primary {
  background: #3b82f6;
  color: #fff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-glass.primary:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-glass:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.footer-notes {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  font-size: 11px;
  justify-content: center;
  color: rgba(255,255,255,0.3);
  flex-wrap: wrap;
}

.note-item {
  white-space: nowrap;
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.gap-2 {
  gap: 8px;
}

.text-red { color: #f87171; }
.text-green { color: #4ade80; }
.text-orange { color: #fbbf24; }
.text-white { color: #fff; }
.text-accent { color: #3b82f6; }
.text-muted { color: rgba(255,255,255,0.4); }

.bg-red { background: #f87171; }
.bg-green { background: #4ade80; }

.spinner-mini {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1200px) {
  .scenarios-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .impact-metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-grid-row {
    grid-template-columns: 1fr;
  }

  .sticky-panel {
    position: relative;
    top: 0;
  }
}

@media (max-width: 768px) {
  .page-container {
    gap: 16px;
    padding: 16px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-right {
    width: 100%;
    flex-direction: column;
  }

  .glass-pill {
    width: 100%;
    justify-content: space-between;
  }

  .btn-glass {
    flex: 1;
  }

  .scenarios-grid {
    grid-template-columns: 1fr;
  }

  .section-title {
    font-size: 24px;
  }

  .table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
}
</style>