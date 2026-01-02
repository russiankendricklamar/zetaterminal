<!-- src/pages/StressTest.vue -->
<template>
  <div class="page-container">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Стресс-тестирование</h1>
        <p class="section-subtitle">Сценарии экстремальных рыночных условий</p>
      </div>
      
      <div class="header-right">
        <!-- New Feature: Scrubbable Severity Multiplier -->
        <div class="sensitivity-control glass-panel-mini">
            <span class="lbl">Множитель шока:</span>
            <ScrubInput 
                v-model="shockMultiplier" 
                :step="0.1" 
                :min="0.5" 
                :max="3.0" 
                :decimals="1" 
                suffix="x"
                class="text-accent"
            />
        </div>

        <button @click="runAllStressTests" class="btn btn-primary-gradient" :disabled="isRunning">
          <svg v-if="!isRunning" width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <span v-else class="spinner-mini"></span>
          {{ isRunning ? 'Тестирую...' : 'Запустить все' }}
        </button>
      </div>
    </div>

    <!-- Scenarios Grid -->
    <div class="scenarios-grid">
      <div 
        v-for="scenario in scenarios" 
        :key="scenario.id"
        @click="selectScenario(scenario)"
        class="card scenario-card"
        :class="{ active: selectedScenario?.id === scenario.id }"
      >
        <div class="card-glow"></div>
        <div class="sc-header">
          <span class="sc-name">{{ scenario.name }}</span>
          <span class="badge" :class="scenario.severity">{{ scenario.severity }}</span>
        </div>
        <p class="sc-desc">{{ scenario.description }}</p>
        <div class="sc-footer">
            <!-- Reactive P&L based on Multiplier -->
            <span class="sc-impact" :class="getImpact(scenario.pnlImpact) < 0 ? 'text-red' : 'text-green'">
                {{ formatCurrencyCompact(getImpact(scenario.pnlImpact)) }}
            </span>
            <span class="sc-prob">Вероятность: {{ (scenario.probability * 100).toFixed(0) }}%</span>
        </div>
      </div>
    </div>

    <!-- Selected Scenario Detail (Split View) -->
    <div v-if="selectedScenario" class="dashboard-grid">
        
        <!-- Left: Impact Analysis & Stats -->
        <div class="col-left">
            <div class="card glass-panel">
                <div class="panel-header">
                    <h3>Влияние сценария: {{ selectedScenario.name }}</h3>
                </div>
                
                <!-- 4 Key Metrics -->
                <div class="impact-metrics-grid">
                    <div class="metric-box">
                        <span class="lbl">P&L Impact</span>
                        <span class="val text-red">{{ formatCurrency(getImpact(selectedScenario.pnlImpact)) }}</span>
                    </div>
                    <div class="metric-box">
                        <span class="lbl">Изменение VaR</span>
                        <span class="val" :class="selectedScenario.varChange < 0 ? 'text-red' : 'text-green'">
                            {{ (selectedScenario.varChange * shockMultiplier).toFixed(1) }}%
                        </span>
                    </div>
                    <div class="metric-box">
                        <span class="lbl">Длительность</span>
                        <span class="val text-white">{{ selectedScenario.duration }}</span>
                    </div>
                     <div class="metric-box">
                        <span class="lbl">Вероятность</span>
                        <span class="val text-orange">{{ (selectedScenario.probability * 100).toFixed(1) }}%</span>
                    </div>
                </div>

                <div class="divider"></div>

                <!-- Asset Impact Bars -->
                <div class="panel-header">
                    <h3>Влияние на активы</h3>
                </div>
                <div class="impact-bars-list">
                    <div v-for="(baseImpact, asset) in selectedScenario.assetImpact" :key="asset" class="bar-row">
                        <span class="bar-label">{{ asset }}</span>
                        <!-- Calculate adjusted impact -->
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
                    <h3>Статистика риска</h3>
                </div>
                <div class="stats-grid-row">
                     <div class="stat-box">
                         <span class="lbl-sm">Средний убыток</span>
                         <span class="val-sm text-red">{{ formatCurrencyCompact(avgLoss * shockMultiplier) }}</span>
                     </div>
                     <div class="stat-box">
                         <span class="lbl-sm">Макс. просадка</span>
                         <span class="val-sm text-red">{{ formatCurrencyCompact(maxLoss * shockMultiplier) }}</span>
                     </div>
                     <div class="stat-box">
                         <span class="lbl-sm">Ожидаемый убыток</span>
                         <span class="val-sm text-orange">{{ formatCurrencyCompact(expectedLoss * shockMultiplier) }}</span>
                     </div>
                </div>
            </div>
        </div>

        <!-- Right: Market Conditions (Sticky) -->
        <aside class="col-right">
            <div class="card glass-panel sticky-panel">
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
                        Данные пересчитаны с учетом коэффициента шока: <b class="text-white">{{ shockMultiplier.toFixed(1) }}x</b>.
                    </p>
                </div>
            </div>
        </aside>
    </div>

    <!-- Comparison Table -->
    <div class="card glass-panel">
      <div class="panel-header">
        <h3>Сравнение сценариев</h3>
      </div>
      <div class="table-wrapper">
        <table class="metrics-table">
          <thead>
            <tr>
              <th class="col-left">Сценарий</th>
              <th>P&L</th>
              <th>Изменение VaR</th>
              <th>Длительность</th>
              <th>Вероятность</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="scenario in scenarios" :key="scenario.id" 
                class="hover-row"
                :class="{ 'row-active': selectedScenario?.id === scenario.id }"
                @click="selectScenario(scenario)">
              <td class="col-left">
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
        <div class="note-item">Сценарии основаны на исторических данных</div>
        <div class="note-item">Корреляции могут меняться в кризис</div>
        <div class="note-item">Рекомендуется ежеквартальный пересмотр</div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTaskStore } from '@/stores/tasks' // <-- Task Store
import ScrubInput from '@/components/common/ScrubInput.vue' // <-- Scrubbable Input

const taskStore = useTaskStore()
const isRunning = ref(false)
const shockMultiplier = ref(1.0) // <-- New Reactive State

const scenarios = ref([
  {
    id: 1,
    name: '«Чёрный лебедь»',
    description: 'Рыночный крах, подобный COVID-19',
    pnlImpact: -185000,
    varChange: -45.5,
    duration: '1–3 дня',
    probability: 0.01,
    severity: 'critical',
    marketChanges: { 'Волатильность': '+25%', 'Доходность облигаций': '+150 б.п.', 'Корреляция': '+0.50', 'Спред': '+100 б.п.' },
    assetImpact: { 'Акции': -35, 'Облигации': -12, 'Товары': -25, 'Валюта': -8 }
  },
  {
    id: 2,
    name: 'Скачок волатильности',
    description: 'Резкий рост ожидаемой волатильности (VIX)',
    pnlImpact: -67500,
    varChange: -18.2,
    duration: '1–5 дней',
    probability: 0.05,
    severity: 'high',
    marketChanges: { 'VIX': '+20 пп', 'Размах торгов': '+15%', 'Ликвидность': '-10%' },
    assetImpact: { 'Акции': -18, 'Облигации': -5, 'Опционы': -40, 'Валюта': -3 }
  },
  {
    id: 3,
    name: 'Рост ставок',
    description: 'ЦБ неожиданно поднял ставку на 100 б.п.',
    pnlImpact: -45200,
    varChange: -12.5,
    duration: '1–10 дней',
    probability: 0.15,
    severity: 'high',
    marketChanges: { 'Ставка ЦБ': '+100 б.п.', 'Спреды': '+50 б.п.', 'Курс': '-5%' },
    assetImpact: { 'Акции': -12, 'Облигации': -22, 'Недвижимость': -15, 'Валюта': -6 }
  },
  {
    id: 4,
    name: 'Коррекция рынка',
    description: 'Умеренное снижение, обычная корректировка',
    pnlImpact: -12400,
    varChange: -5.2,
    duration: '5–20 дней',
    probability: 0.35,
    severity: 'medium',
    marketChanges: { 'Индекс': '-8%', 'Волатильность': '+10%', 'Спреды': '+20 б.п.' },
    assetImpact: { 'Акции': -8, 'Облигации': 2, 'Товары': -5, 'Валюта': -2 }
  }
])

const selectedScenario = ref(scenarios.value[0])
const selectScenario = (scenario: any) => selectedScenario.value = scenario

// Reactive Helpers
const getImpact = (val: number) => val * shockMultiplier.value
const formatCurrency = (val: number) => new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(val)
const formatCurrencyCompact = (val: number) => (val / 1000).toFixed(0) + 'k'
const formatLabel = (key: string) => key.charAt(0).toUpperCase() + key.slice(1)

const avgLoss = computed(() => scenarios.value.reduce((sum, s) => sum + s.pnlImpact, 0) / scenarios.value.length)
const maxLoss = computed(() => Math.min(...scenarios.value.map(s => s.pnlImpact)))
const expectedLoss = computed(() => scenarios.value.reduce((sum, s) => sum + s.pnlImpact * s.probability, 0))

// --- DYNAMIC ISLAND INTEGRATION ---
const runAllStressTests = async () => {
  if (isRunning.value) return
  isRunning.value = true
  
  // 1. Start Task
  const taskId = taskStore.addTask('Simulating Stress Scenarios...', 'simulation')
  
  try {
    // 2. Mock 4 scenarios calculation (25% each)
    for (let i = 0; i <= 100; i += 25) {
      await new Promise(r => setTimeout(r, 300))
      taskStore.updateProgress(taskId, i)
    }
    
    // 3. (Optional) Could reset multiplier here, or allow persistent shock
    
  } catch (e) {
    taskStore.failTask(taskId)
  } finally {
    isRunning.value = false
  }
}
</script>

<style scoped>
/* ============================================
   LAYOUT
   ============================================ */
.page-container {
  display: flex; flex-direction: column; gap: 26px; padding: 28px;
  max-width: 1280px; margin: 0 auto;
}

.section-header {
  display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px;
}
.header-right { display: flex; align-items: center; gap: 16px; }

.section-title { font-size: 28px; font-weight: 700; margin: 0; color: #fff; letter-spacing: -0.02em; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }

/* ============================================
   GLASS CARD ENGINE
   ============================================ */
.card {
  position: relative; border-radius: 18px; overflow: hidden;
  background: rgba(20, 22, 28, 0.18);
  backdrop-filter: blur(34px) saturate(185%);
  -webkit-backdrop-filter: blur(34px) saturate(185%);
  box-shadow: 0 18px 40px -18px rgba(0,0,0,0.55), inset 0 0 0 1px rgba(255, 255, 255, 0.14), inset 0 1px 0 0 rgba(255, 255, 255, 0.10);
  transform: translateZ(0); transition: all 220ms ease;
}

/* Glare & Texture */
.card::before {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.0) 40%); opacity: 0.8; z-index: 0;
}
.card::after {
  content: ""; position: absolute; inset: -1px; pointer-events: none;
  background: radial-gradient(800px circle at 50% 0%, rgba(255,255,255,0.06), transparent 40%); opacity: 0.6; z-index: 0;
}

/* ============================================
   SCENARIOS GRID
   ============================================ */
.scenarios-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }

.scenario-card {
  padding: 18px; cursor: pointer; display: flex; flex-direction: column; justify-content: space-between; min-height: 140px;
  border: 1px solid transparent;
}
.scenario-card:hover { transform: translateY(-2px); background: rgba(255,255,255,0.05); }
.scenario-card.active {
  background: rgba(255, 51, 102, 0.15); border-color: rgba(255, 51, 102, 0.4);
}

.sc-header { position: relative; z-index: 1; display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
.sc-name { font-size: 13px; font-weight: 700; color: #fff; line-height: 1.2; max-width: 70%; }
.sc-desc { position: relative; z-index: 1; font-size: 11px; color: rgba(255,255,255,0.5); line-height: 1.4; flex-grow: 1; }
.sc-footer { position: relative; z-index: 1; display: flex; justify-content: space-between; align-items: flex-end; margin-top: 12px; }
.sc-impact { font-family: var(--font-family-mono); font-weight: 700; font-size: 16px; }
.sc-prob { font-size: 10px; color: rgba(255,255,255,0.4); }

.badge { font-size: 9px; text-transform: uppercase; padding: 2px 6px; border-radius: 4px; font-weight: 700; }
.badge.critical { background: rgba(248, 113, 113, 0.2); color: #f87171; }
.badge.high { background: rgba(251, 191, 36, 0.2); color: #fbbf24; }
.badge.medium { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }

/* ============================================
   DASHBOARD SPLIT VIEW
   ============================================ */
.dashboard-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 18px; align-items: start; }
.col-left, .col-right { display: flex; flex-direction: column; gap: 18px; }

.glass-panel { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.glass-panel-mini { padding: 8px 16px; background: rgba(255,255,255,0.03); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); display: flex; align-items: center; gap: 10px; }
.sticky-panel { position: sticky; top: 20px; }
.panel-header h3 { margin: 0; font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.04em; }
.divider { height: 1px; background: rgba(255,255,255,0.1); margin: 8px 0; }

/* Impact Metrics */
.impact-metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.metric-box { display: flex; flex-direction: column; gap: 4px; }
.metric-box .lbl { font-size: 11px; color: rgba(255,255,255,0.5); }
.metric-box .val { font-family: var(--font-family-mono); font-weight: 600; font-size: 18px; }

/* Asset Bars */
.impact-bars-list { display: flex; flex-direction: column; gap: 12px; }
.bar-row { display: grid; grid-template-columns: 100px 1fr 50px; align-items: center; gap: 12px; }
.bar-label { font-size: 12px; color: rgba(255,255,255,0.7); }
.bar-track { height: 6px; background: rgba(255,255,255,0.05); border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
.bar-val { font-family: var(--font-family-mono); font-size: 12px; text-align: right; font-weight: 600; }

/* Stats Grid Row */
.stats-grid-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.stat-box { display: flex; flex-direction: column; gap: 4px; }
.lbl-sm { font-size: 10px; color: rgba(255,255,255,0.5); text-transform: uppercase; }
.val-sm { font-family: var(--font-family-mono); font-weight: 600; font-size: 14px; }

/* Market Changes */
.market-changes-list { display: flex; flex-direction: column; gap: 10px; }
.market-row { display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px; font-size: 13px; }
.market-row:last-child { border-bottom: none; }
.m-key { color: rgba(255,255,255,0.6); }
.m-val { font-family: var(--font-family-mono); font-weight: 600; }

.text-xs { font-size: 10px; line-height: 1.4; }
.text-accent { color: #3b82f6; }

/* ============================================
   TABLE
   ============================================ */
.table-wrapper { overflow-x: auto; margin-top: -10px; }
.metrics-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.metrics-table th { text-align: right; padding: 10px; color: rgba(255,255,255,0.4); font-weight: 500; border-bottom: 1px solid rgba(255,255,255,0.1); }
.metrics-table th.col-left { text-align: left; }
.metrics-table td { text-align: right; padding: 12px 10px; border-bottom: 1px solid rgba(255,255,255,0.05); font-family: var(--font-family-mono); color: #fff; }
.metrics-table td.col-left { text-align: left; font-family: inherit; }
.hover-row { cursor: pointer; transition: background 0.1s; }
.hover-row:hover { background: rgba(255,255,255,0.05); }
.row-active { background: rgba(255, 51, 102, 0.1) !important; }
.sc-name-sm { font-weight: 600; font-size: 13px; }

/* ============================================
   FOOTER & UTILITY
   ============================================ */
.footer-notes { display: flex; gap: 24px; margin-top: 10px; opacity: 0.5; font-size: 11px; justify-content: center; }

.btn { display: flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; border: none; color: white; }
.btn-primary-gradient { background: linear-gradient(135deg, #0ea5e9, #2563eb); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); }
.btn-primary-gradient:hover { filter: brightness(1.1); transform: translateY(-1px); }
.btn:disabled { opacity: 0.6; cursor: default; }

.text-red { color: #f87171; }
.text-green { color: #4ade80; }
.text-orange { color: #fbbf24; }
.text-white { color: #fff; }
.text-muted { color: rgba(255,255,255,0.4); }
.bg-red { background: #f87171; }
.bg-green { background: #4ade80; }

.spinner-mini { width: 12px; height: 12px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .scenarios-grid, .dashboard-grid, .impact-metrics-grid, .stats-grid-row { grid-template-columns: 1fr; }
}
</style>