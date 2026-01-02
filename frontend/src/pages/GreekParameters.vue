<!-- src/views/RiskMetricsView.vue -->
<template>
  <div class="page-container">
    
    <!-- Hero / Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Риск-метрики портфеля</h1>
        <p class="section-subtitle">Продвинутый анализ рисков, факторный анализ</p>
      </div>
      <div class="header-actions">
        <!-- Scrubbable Confidence Level -->
        <div class="glass-panel-mini">
           <span class="lbl-mini">Уровень доверия:</span>
           <ScrubInput 
              v-model="confidenceLevel" 
              :min="90" :max="99.9" :step="0.1" :decimals="1" 
              suffix="%" 
              class="text-accent"
           />
        </div>

        <div class="last-update">Данные на: {{ lastUpdate }}</div>
        <select v-model="selectedTimeframe" class="glass-select">
          <option value="1d">Горизонт: 1 день</option>
          <option value="10d">Горизонт: 10 дней</option>
          <option value="1m">Горизонт: 1 месяц</option>
          <option value="2m">Горизонт: 2 месяца</option>
          <option value="6m">Горизонт: 6 месяцев</option>
          <option value="1y">Горизонт: 1 год</option>
          <option value="2y">Горизонт: 2 года</option>
          <option value="5y">Горизонт: 5 лет</option>
        </select>
        
        <!-- Refresh Button -->
        <button class="btn btn-outline" @click="refreshMetrics" :disabled="isLoading">
          <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-if="!isLoading">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          <span v-else class="spinner-mini"></span>
          {{ isLoading ? 'Расчет...' : 'Обновить' }}
        </button>
      </div>
    </div>

    <!-- Quick Risk Summary (KPIs) -->
    <div class="kpi-cards-grid">
      <div class="kpi-card">
        <div class="kpi-label">VaR {{ confidenceLevel }}% (Value at Risk)</div>
        <div class="kpi-value text-red">{{ formatCurrency(adjustedVaR) }}</div>
        <div class="kpi-sub">
           <span class="text-muted">от капитала:</span> <span class="text-white font-bold">{{ (Math.abs(adjustedVaR)/2400000*100).toFixed(2) }}%</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Expected Shortfall (CVaR)</div>
        <div class="kpi-value text-orange">{{ formatCurrency(adjustedVaR * 1.25) }}</div>
        <div class="kpi-sub">
           <span class="text-muted">средний хвост</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Бэта портфеля (β)</div>
        <div class="kpi-value text-gradient-blue">0.85</div>
        <div class="kpi-sub">
           <span class="text-muted">vs IMOEX</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Коэффициент Шарпа</div>
        <div class="kpi-value text-gradient-green">1.42</div>
        <div class="kpi-sub">
           <span class="text-muted">Коэффициент Сортино:</span> <span class="text-white">2.15</span>
        </div>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="dashboard-grid">
      
      <!-- Left Column -->
      <div class="col-left">
        
        <!-- Detailed Risk Breakdown -->
        <div class="card glass-panel">
          <div class="panel-header">
            <h3>Декомпозиция рисков</h3>
            <div class="badge-info">Marginal VaR</div>
          </div>
          <div class="risk-table-wrapper">
             <table class="simple-table">
                <colgroup>
                    <col style="width: 25%">
                    <col style="width: 20%">
                    <col style="width: 25%">
                    <col style="width: 30%">
                </colgroup>
                <thead>
                   <tr>
                      <th class="text-left pl-0">Актив</th>
                      <th class="text-right">Вес</th>
                      <th class="text-right">Доля риска</th>
                      <th class="text-right pr-0">% от Риска</th>
                   </tr>
                </thead>
                <tbody>
                   <tr v-for="asset in riskContribution" :key="asset.symbol">
                      <td class="pl-0">
                         <div class="asset-row">
                            <span class="dot" :style="{background: asset.color}"></span>
                            <span class="sym">{{ asset.symbol }}</span>
                         </div>
                      </td>
                      <td class="text-right mono">{{ asset.weight }}%</td>
                      <td class="text-right mono text-red">${{ (asset.contribution / 1000).toFixed(1) }}k</td>
                      <td class="text-right pr-0">
                         <div class="bar-cell">
                            <div class="progress-bar">
                               <div class="progress-fill" :style="{width: asset.percentRisk + '%'}"></div>
                            </div>
                            <span class="mono bar-val">{{ asset.percentRisk }}%</span>
                         </div>
                      </td>
                   </tr>
                </tbody>
             </table>
          </div>
        </div>

        <!-- Stress Testing -->
        <div class="card glass-panel">
          <div class="panel-header">
            <h3>Стресс-тестирование</h3>
            <button @click="runStressTest" class="btn-xs" :disabled="isStressTesting">
              {{ isStressTesting ? 'Моделирование...' : 'Запустить Тест' }}
            </button>
          </div>
          <div class="stress-list">
            <div v-for="scenario in stressScenarios" :key="scenario.id" class="stress-item">
              <div class="stress-info">
                <span class="stress-name">{{ scenario.name }}</span>
                <span class="stress-desc">{{ scenario.description }}</span>
              </div>
              <div class="stress-result">
                 <span class="stress-val" :class="scenario.impact > 0 ? 'text-green' : 'text-red'">
                   {{ scenario.impact > 0 ? '+' : '' }}{{ formatCurrency(scenario.impact) }}
                 </span>
                 <span class="stress-pct" :class="scenario.impactPct > 0 ? 'text-green' : 'text-red'">
                   {{ scenario.impactPct > 0 ? '+' : '' }}{{ (scenario.impactPct * 100).toFixed(2) }}%
                 </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Full Correlation Matrix -->
        <div class="card glass-panel">
          <div class="panel-header">
            <h3>Матрица корреляции активов портфеля</h3>
            <div class="legend">
               <span class="dot-legend bg-blue"></span> Положительная
               <span class="dot-legend bg-red"></span> Отрицательная
            </div>
          </div>
          <div class="correlation-matrix-grid">
             <!-- Headers -->
             <div class="matrix-cell empty"></div>
             <div v-for="label in correlationLabels" :key="label" class="matrix-cell header">{{ label }}</div>
             
             <!-- Rows -->
             <template v-for="(row, i) in correlationData" :key="'row-'+i">
                <div class="matrix-cell header">{{ correlationLabels[i] }}</div>
                <div v-for="(cell, j) in row" :key="i+'-'+j" class="matrix-cell value" :style="getHeatmapStyle(cell)">
                  {{ cell.toFixed(2) }}
                </div>
             </template>
          </div>
        </div>

      </div>

      <!-- Right Column -->
      <div class="col-right">
        
        <!-- Factor Exposure -->
        <div class="card glass-panel">
          <div class="panel-header">
            <h3>Факторный Анализ</h3>
          </div>
          <div class="factor-list">
            <div class="list-row" v-for="factor in factors" :key="factor.name">
               <div class="lbl-group">
                  <span class="lbl">{{ factor.name }}</span>
                  <span class="sub-lbl">{{ factor.index }}</span>
               </div>
               <div class="val-group">
                 <span class="val" :class="getBetaClass(factor.beta)">{{ factor.beta > 0 ? '+' : ''}}{{ factor.beta.toFixed(2) }}</span>
                 <span class="diff text-muted">β</span>
               </div>
            </div>
          </div>
        </div>

        <!-- Drawdown Analysis -->
        <div class="card glass-panel">
          <div class="panel-header">
            <h3>Анализ Просадок</h3>
          </div>
          <div class="metrics-kv-list">
             <div class="kv-row">
                <span class="k">Текущая просадка</span>
                <span class="v text-red">-3.45%</span>
             </div>
             <div class="kv-row">
                <span class="k">Макс. просадка</span>
                <span class="v text-red font-bold">-12.40%</span>
             </div>
             <div class="kv-row">
                <span class="k">Дней в просадке</span>
                <span class="v">14 дней</span>
             </div>
             <div class="kv-row">
                <span class="k">Фактор восстановления</span>
                <span class="v text-green">3.2x</span>
             </div>
          </div>
        </div>

        <!-- Liquidity Metrics -->
        <div class="card glass-panel">
          <div class="panel-header">
            <h3>Ликвидность</h3>
          </div>
          <div class="metrics-kv-list">
             <div class="kv-row">
                <span class="k">Ожидаемое время до ликвидации при VaR 95%</span>
                <span class="v">1.2 дня</span>
             </div>
             <div class="kv-row">
                <span class="k">Bid-Ask Spread Cost</span>
                <span class="v text-orange">0.08%</span>
             </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTaskStore } from '@/stores/tasks'
import ScrubInput from '@/components/common/ScrubInput.vue'

const taskStore = useTaskStore()

const selectedTimeframe = ref('1d')
const isLoading = ref(false)
const isStressTesting = ref(false)
const lastUpdate = ref(new Date().toLocaleTimeString())
const confidenceLevel = ref(99.0)

// Base VaR at 99%
const baseVaR = -67500

const adjustedVaR = computed(() => {
    // Approx scaling: Z(99%) ~ 2.33, Z(95%) ~ 1.645
    const zScore = 1.645 + ((confidenceLevel.value - 95) / (99-95)) * (2.33 - 1.645)
    return baseVaR * (zScore / 2.33)
})

const riskContribution = ref([
   { symbol: 'SPY', weight: 40, contribution: 27000, percentRisk: 45, color: '#3b82f6' },
   { symbol: 'QQQ', weight: 30, contribution: 21000, percentRisk: 35, color: '#8b5cf6' },
   { symbol: 'GLD', weight: 15, contribution: 4500, percentRisk: 7.5, color: '#fbbf24' },
   { symbol: 'TLT', weight: 15, contribution: 7500, percentRisk: 12.5, color: '#ef4444' },
])

const stressScenarios = ref([
  { id: 1, name: 'Финансовый Кризис 2008', description: 'Повторение рыночного краха', impact: -452000, impactPct: -0.25 },
  { id: 2, name: 'Скачок Инфляции', description: 'Рост ставок +200 б.п.', impact: -125000, impactPct: -0.07 },
  { id: 3, name: 'Падение Нефти', description: 'Нефть Brent < $40', impact: -35000, impactPct: -0.02 },
  { id: 4, name: 'Рост Волатильности', description: 'VIX > 40', impact: -85000, impactPct: -0.045 }
])

const factors = ref([
   { name: 'Market Risk', index: 'S&P 500', beta: 0.85 },
   { name: 'Interest Rates', index: 'US 10Y Treasury', beta: -0.42 },
   { name: 'Momentum', index: 'MTUM ETF', beta: 0.25 },
   { name: 'Volatility', index: 'VIX Index', beta: -0.65 },
   { name: 'Commodities', index: 'BCOM Index', beta: 0.12 },
])

const correlationLabels = ref(['SPY', 'QQQ', 'TLT', 'GLD', 'BTC'])
const correlationData = ref([
  [1.0, 0.92, -0.35, 0.15, 0.45],
  [0.92, 1.0, -0.42, 0.10, 0.55],
  [-0.35, -0.42, 1.0, 0.25, -0.15],
  [0.15, 0.10, 0.25, 1.0, 0.20],
  [0.45, 0.55, -0.15, 0.20, 1.0]
])

// Helpers
const formatCurrency = (val: number) => '$' + Math.abs(val).toLocaleString('en-US', {maximumFractionDigits: 0})
const getBetaClass = (val: number) => Math.abs(val) > 0.5 ? 'font-bold text-white' : 'text-muted'

const getHeatmapStyle = (val: number) => {
  let bg = 'rgba(255,255,255,0.02)'
  let color = 'rgba(255,255,255,0.6)'
  
  if (val === 1) {
     bg = 'rgba(255,255,255,0.1)'
     color = '#fff'
  } else if (val > 0) {
     const alpha = val * 0.5
     bg = `rgba(59, 130, 246, ${alpha})` 
     color = '#bfdbfe'
  } else if (val < 0) {
     const alpha = Math.abs(val) * 0.5
     bg = `rgba(239, 68, 68, ${alpha})` 
     color = '#fca5a5'
  }
  return { background: bg, color: color }
}

const refreshMetrics = async () => {
  if (isLoading.value) return
  isLoading.value = true
  
  const taskId = taskStore.addTask('Updating Risk Metrics...', 'calculation')
  
  try {
     taskStore.updateProgress(taskId, 20)
     await new Promise(r => setTimeout(r, 600))
     taskStore.updateProgress(taskId, 60)
     await new Promise(r => setTimeout(r, 400))
     taskStore.updateProgress(taskId, 100)
     
     lastUpdate.value = new Date().toLocaleTimeString()
  } catch(e) {
     taskStore.failTask(taskId)
  } finally {
     isLoading.value = false
  }
}

const runStressTest = async () => {
  if (isStressTesting.value) return
  isStressTesting.value = true
  
  const taskId = taskStore.addTask('Running Factor Stress Tests...', 'simulation')
  
  try {
    for(let i=0; i<=100; i+=10) {
        await new Promise(r => setTimeout(r, 150))
        taskStore.updateProgress(taskId, i)
    }
  } catch(e) {
      taskStore.failTask(taskId)
  } finally {
      isStressTesting.value = false
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
  gap: 26px;
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 4px;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  color: #fff;
  letter-spacing: -0.02em;
}

.section-subtitle {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  margin: 4px 0 0 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}
.last-update { font-size: 11px; color: rgba(255,255,255,0.3); }

/* ============================================
   GLASS CARD ENGINE
   ============================================ */
.card, .kpi-card {
  position: relative;
  border-radius: 18px;
  overflow: hidden;
  background: rgba(20, 22, 28, 0.4);
  backdrop-filter: blur(20px) saturate(140%);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

/* ============================================
   KPI GRID
   ============================================ */
.kpi-cards-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.kpi-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 100px;
}

.kpi-label {
  font-size: 11px; text-transform: uppercase;
  color: rgba(255,255,255,0.5); font-weight: 600;
  margin-bottom: 8px; letter-spacing: 0.05em;
}

.kpi-value {
  font-size: 24px; font-weight: 700;
  font-family: var(--font-family-mono); line-height: 1.2;
}

.kpi-sub {
  font-size: 11px; margin-top: 6px; display: flex; gap: 6px;
}

/* ============================================
   DASHBOARD LAYOUT
   ============================================ */
.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  align-items: start;
}

.col-left, .col-right {
  display: flex; flex-direction: column; gap: 20px;
}

.glass-panel { padding: 24px; }
.glass-panel-mini { 
    padding: 6px 12px; background: rgba(255,255,255,0.03); 
    border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); 
    display: flex; align-items: center; gap: 8px;
}
.lbl-mini { font-size: 11px; color: rgba(255,255,255,0.5); }

.panel-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px;
}

.panel-header h3 {
  margin: 0; font-size: 14px; font-weight: 600;
  color: rgba(255,255,255,0.9);
}

/* ============================================
   RISK TABLE
   ============================================ */
.risk-table-wrapper { overflow-x: auto; }
.simple-table { 
    width: 100%; 
    border-collapse: collapse; 
    font-size: 13px; 
    table-layout: fixed; /* Фиксированная ширина колонок */
}
.simple-table th { 
  padding-bottom: 12px; 
  color: rgba(255,255,255,0.4); font-weight: 500; font-size: 11px; text-transform: uppercase;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.simple-table td { padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.simple-table tr:last-child td { border-bottom: none; }

.text-right { text-align: right; }
.text-left { text-align: left; }
.pl-0 { padding-left: 0; }
.pr-0 { padding-right: 0; }

.asset-row { display: flex; align-items: center; gap: 8px; }
.dot { width: 8px; height: 8px; border-radius: 2px; }
.sym { font-weight: 600; color: #fff; }

.bar-cell { display: flex; align-items: center; justify-content: flex-end; gap: 8px; }
.progress-bar { width: 60px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; background: #ef4444; border-radius: 2px; }
.bar-val { min-width: 32px; text-align: right; }

/* ============================================
   STRESS LIST
   ============================================ */
.stress-list { display: flex; flex-direction: column; gap: 12px; }
.stress-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px;
}
.stress-info { display: flex; flex-direction: column; gap: 2px; }
.stress-name { font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.9); }
.stress-desc { font-size: 11px; color: rgba(255,255,255,0.4); }

.stress-result { text-align: right; display: flex; flex-direction: column; }
.stress-val { font-family: var(--font-family-mono); font-weight: 600; font-size: 13px; }
.stress-pct { font-size: 11px; opacity: 0.8; }

/* ============================================
   FACTOR & METRICS LISTS
   ============================================ */
.factor-list, .metrics-kv-list { display: flex; flex-direction: column; gap: 12px; }

/* Factor Row */
.list-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.list-row:last-child { border-bottom: none; }
.lbl-group { display: flex; flex-direction: column; }
.lbl { font-size: 13px; color: #fff; }
.sub-lbl { font-size: 10px; color: rgba(255,255,255,0.4); }
.val-group { display: flex; align-items: baseline; gap: 4px; }
.val { font-family: var(--font-family-mono); font-weight: 500; font-size: 14px; }
.diff { font-size: 10px; }

/* KV Row */
.kv-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
.k { color: rgba(255,255,255,0.6); }
.v { color: #fff; font-family: var(--font-family-mono); }

/* ============================================
   CORRELATION MATRIX GRID
   ============================================ */
.correlation-matrix-grid {
  display: grid; grid-template-columns: 40px repeat(5, 1fr); gap: 2px;
}
.matrix-cell {
  height: 38px; display: flex; align-items: center; justify-content: center;
  font-size: 12px; border-radius: 4px;
}
.matrix-cell.header { color: rgba(255,255,255,0.5); font-weight: 600; font-size: 11px; }
.matrix-cell.value { font-family: var(--font-family-mono); font-size: 12px; }

/* ============================================
   CONTROLS & UTILS
   ============================================ */
.glass-select {
  background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);
  color: #fff; padding: 6px 12px; border-radius: 8px; font-size: 12px; outline: none;
}
.btn {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 14px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer;
  transition: all 0.2s;
}
.btn-outline {
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #fff;
}
.btn-outline:hover { background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.2); }
.btn-xs {
  padding: 4px 10px; font-size: 10px; background: rgba(59, 130, 246, 0.2); border: 1px solid rgba(59, 130, 246, 0.3); color: #93c5fd; border-radius: 4px; cursor: pointer;
}
.btn-xs:hover { background: rgba(59, 130, 246, 0.3); }

/* Colors */
.text-gradient-green { background: linear-gradient(135deg, #4ade80, #22c55e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-gradient-blue { background: linear-gradient(135deg, #60a5fa, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-red { color: #f87171; }
.text-green { color: #4ade80; }
.text-orange { color: #fbbf24; }
.text-white { color: #fff; }
.text-muted { color: rgba(255,255,255,0.4); }
.text-accent { color: #3b82f6; }
.font-bold { font-weight: 700; }
.mono { font-family: var(--font-family-mono); }
.badge-info { font-size: 10px; background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; color: rgba(255,255,255,0.7); }

.legend { display: flex; gap: 12px; align-items: center; font-size: 11px; color: rgba(255,255,255,0.5); }
.dot-legend { width: 6px; height: 6px; border-radius: 50%; display: inline-block; margin-right: 4px; }
.bg-blue { background: #3b82f6; }
.bg-red { background: #ef4444; }

.spinner-mini {
  width: 12px; height: 12px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1200px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .kpi-cards-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>

