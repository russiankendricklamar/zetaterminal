<template>
  <div class="page-container">
    
    <!-- Hero / Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Риск-метрики</h1>
        <p class="section-subtitle">VaR, Стресс-тесты и Факторный анализ</p>
      </div>
      <div class="header-actions">
        <!-- Selected Bank -->
        <div class="glass-pill control-pill">
           <span class="lbl-mini">Банк:</span>
           <span class="text-white font-bold">{{ selectedBank.name }}</span>
        </div>
        
        <!-- Scrubbable Confidence Level -->
        <div class="glass-pill control-pill">
           <span class="lbl-mini">Доверие:</span>
           <div class="scrub-wrapper">
               <input 
                  type="number" 
                  v-model.number="confidenceLevel" 
                  class="scrub-input text-accent" 
                  step="0.1" min="90" max="99.9"
               />
               <span class="text-accent">%</span>
           </div>
        </div>

        <div class="glass-pill control-pill">
            <span class="lbl-mini">Горизонт:</span>
            <select v-model="selectedTimeframe" class="glass-select-clean">
              <option value="1d">1 день</option>
              <option value="10d">10 дней</option>
              <option value="1m">1 месяц</option>
            </select>
        </div>
        
        <!-- Refresh Button -->
        <button class="btn-glass primary" @click="refreshMetrics" :disabled="isLoading">
          <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-if="!isLoading">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          <span v-else class="spinner-mini"></span>
          <span v-if="!isLoading">Обновить</span>
        </button>
      </div>
    </div>

    <!-- Quick Risk Summary (KPIs) -->
    <div class="kpi-cards-grid">
      <div class="glass-card kpi-card">
        <div class="kpi-label">VaR {{ confidenceLevel }}% (Value at Risk)</div>
        <div class="kpi-value text-red">{{ formatCurrency(adjustedVaR) }}</div>
        <div class="kpi-sub">
           <span class="text-muted">Риск/Капитал:</span> <span class="text-white font-bold">{{ (Math.abs(adjustedVaR)/riskMetricsStore.totalEquity*100).toFixed(2) }}%</span>
        </div>
      </div>
      <div class="glass-card kpi-card">
        <div class="kpi-label">Expected Shortfall (CVaR)</div>
        <div class="kpi-value text-orange">{{ formatCurrency(confidenceLevel >= 99 ? riskMetricsStore.cvar99 : riskMetricsStore.cvar95) }}</div>
        <div class="kpi-sub">
           <span class="text-muted">Средний убыток в хвосте</span>
        </div>
      </div>
      <div class="glass-card kpi-card">
        <div class="kpi-label">Бэта портфеля (β)</div>
        <div class="kpi-value text-gradient-blue">{{ riskMetricsStore.portfolioBeta.toFixed(2) }}</div>
        <div class="kpi-sub">
           <span class="text-muted">vs IMOEX</span>
        </div>
      </div>
      <div class="glass-card kpi-card">
        <div class="kpi-label">Коэффициент Шарпа</div>
        <div class="kpi-value text-gradient-green">{{ riskMetricsStore.sharpeRatio.toFixed(2) }}</div>
        <div class="kpi-sub">
           <span class="text-muted">Sortino:</span> <span class="text-white">{{ riskMetricsStore.calculateSortinoRatio(riskMetricsStore.expectedReturn, riskMetricsStore.volatility).toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="dashboard-grid">
      
      <!-- Left Column -->
      <div class="col-left">
        
        <!-- Detailed Risk Breakdown -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Декомпозиция рисков</h3>
            <div class="badge-glass">Marginal VaR</div>
          </div>
          <div class="risk-table-wrapper">
             <table class="glass-table">
                <colgroup>
                    <col style="width: 30%">
                    <col style="width: 20%">
                    <col style="width: 25%">
                    <col style="width: 25%">
                </colgroup>
                <thead>
                   <tr>
                      <th class="text-left pl-4">Актив</th>
                      <th class="text-right">Вес</th>
                      <th class="text-right">Вклад в риск</th>
                      <th class="text-right pr-4">% Риска</th>
                   </tr>
                </thead>
                <tbody>
                   <tr v-for="asset in riskContribution" :key="asset.symbol">
                      <td class="pl-4">
                         <div class="asset-row">
                            <span class="dot" :style="{background: asset.color}"></span>
                            <span class="sym">{{ asset.symbol }}</span>
                         </div>
                      </td>
                      <td class="text-right mono">{{ asset.weight }}%</td>
                      <td class="text-right mono text-red">${{ (asset.contribution / 1000).toFixed(1) }}k</td>
                      <td class="text-right pr-4">
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
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Стресс-тестирование</h3>
            <button @click="runStressTest" class="btn-xs-glass" :disabled="isStressTesting">
              {{ isStressTesting ? 'Выполняется...' : 'Запустить' }}
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
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Матрица корреляций</h3>
            <div class="legend">
               <span class="dot-legend bg-blue"></span> Поз
               <span class="dot-legend bg-red"></span> Нег
            </div>
          </div>
          <div class="correlation-matrix-wrapper">
            <div class="correlation-matrix-grid">
               <!-- Headers -->
               <div class="matrix-cell empty"></div>
               <div v-for="label in correlationLabels.slice(0, 10)" :key="label" class="matrix-cell header" :title="label">{{ label.length > 6 ? label.substring(0, 6) + '...' : label }}</div>
               
               <!-- Rows -->
               <template v-for="(row, i) in correlationData.slice(0, 10)" :key="'row-'+i">
                  <div class="matrix-cell header" :title="correlationLabels[i]">{{ correlationLabels[i] && correlationLabels[i].length > 6 ? correlationLabels[i].substring(0, 6) + '...' : (correlationLabels[i] || '') }}</div>
                  <div v-for="(cell, j) in row.slice(0, 10)" :key="i+'-'+j" class="matrix-cell value" :style="getHeatmapStyle(cell)" :title="`${correlationLabels[i]} vs ${correlationLabels[j]}: ${cell.toFixed(3)}`">
                    {{ cell.toFixed(2) }}
                  </div>
               </template>
            </div>
          </div>
        </div>

      </div>

      <!-- Right Column -->
      <div class="col-right">
        
        <!-- Factor Exposure -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Факторный Анализ (Beta)</h3>
          </div>
          <div class="factor-list">
            <div class="list-row" v-for="factor in factors" :key="factor.name">
               <div class="lbl-group">
                  <span class="lbl">{{ factor.name }}</span>
                  <span class="sub-lbl">{{ factor.index }}</span>
               </div>
               <div class="val-group">
                 <span class="val" :class="getBetaClass(factor.beta)">{{ factor.beta > 0 ? '+' : ''}}{{ factor.beta.toFixed(2) }}</span>
               </div>
            </div>
          </div>
        </div>

        <!-- Drawdown Analysis -->
        <div class="glass-card panel">
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
                <span class="v text-red font-bold">{{ (riskMetricsStore.maxDrawdown * 100).toFixed(2) }}%</span>
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
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Ликвидность</h3>
          </div>
          <div class="metrics-kv-list">
             <div class="kv-row">
                <span class="k">Дней до ликвидации (95%)</span>
                <span class="v">1.2 дня</span>
             </div>
             <div class="kv-row">
                <span class="k">Стоимость спреда Bid-Ask</span>
                <span class="v text-orange">0.08%</span>
             </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useTaskStore } from '@/stores/tasks'
import { useRiskMetricsStore } from '@/stores/riskMetrics'
import { usePortfolioStore } from '@/stores/portfolio'

const taskStore = useTaskStore()
const riskMetricsStore = useRiskMetricsStore()
const portfolioStore = usePortfolioStore()

const selectedBank = computed(() => portfolioStore.selectedBank)

const selectedTimeframe = ref('1d')
const isLoading = ref(false)
const isStressTesting = ref(false)
const lastUpdate = ref(new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}))
const confidenceLevel = ref(99.0)

// VaR из store, с адаптацией под уровень доверия
const adjustedVaR = computed(() => {
  const var99 = riskMetricsStore.var99
  const var95 = riskMetricsStore.var95
  
  if (var99 === 0 && var95 === 0) {
    // Fallback если метрики еще не вычислены
    const baseVaR = -67500
    const zScore = 1.645 + ((confidenceLevel.value - 95) / (99-95)) * (2.33 - 1.645)
    return baseVaR * (zScore / 2.33)
  }
  
  // Интерполяция между 95% и 99%
  if (confidenceLevel.value <= 95) {
    return var95
  } else if (confidenceLevel.value >= 99) {
    return var99
  } else {
    // Линейная интерполяция
    const ratio = (confidenceLevel.value - 95) / (99 - 95)
    return var95 + (var99 - var95) * ratio
  }
})

// Risk Contribution из store
const riskContribution = computed(() => {
  const contributions = riskMetricsStore.riskContributions
  if (contributions.length > 0) {
    return contributions
  }
  // Fallback данные
  return [
    { symbol: 'SPY', weight: 40, contribution: 27000, percentRisk: 45, color: '#3b82f6' },
    { symbol: 'QQQ', weight: 30, contribution: 21000, percentRisk: 35, color: '#8b5cf6' },
    { symbol: 'GLD', weight: 15, contribution: 4500, percentRisk: 7.5, color: '#fbbf24' },
    { symbol: 'TLT', weight: 15, contribution: 7500, percentRisk: 12.5, color: '#ef4444' },
  ]
})

const stressScenarios = ref([
  { id: 1, name: 'Финансовый Кризис 2008', description: 'Рыночный крах (повтор)', impact: -452000, impactPct: -0.25 },
  { id: 2, name: 'Скачок Инфляции', description: 'Рост ставок +200 б.п.', impact: -125000, impactPct: -0.07 },
  { id: 3, name: 'Падение Нефти', description: 'Нефть Brent < ₽40', impact: -35000, impactPct: -0.02 },
  { id: 4, name: 'Рост Волатильности', description: 'VIX > 40', impact: -85000, impactPct: -0.045 }
])

// Factors из store (пока используем фиксированные, можно расширить позже)
const factors = computed(() => {
  const beta = riskMetricsStore.portfolioBeta
  return [
    { name: 'Рыночный риск', index: 'IMOEX', beta: beta },
    { name: 'Процентные ставки', index: 'RU 10Y', beta: -0.42 },
    { name: 'Momentum', index: 'MTUM ETF', beta: 0.25 },
    { name: 'Волатильность', index: 'RTSVIX', beta: -0.65 },
    { name: 'Сырье', index: 'BCOM Index', beta: 0.12 },
  ]
})

// Функция для генерации fallback матрицы корреляций
const generateCorrelationMatrix = (size: number): number[][] => {
  const matrix: number[][] = []
  for (let i = 0; i < size; i++) {
    const row: number[] = []
    for (let j = 0; j < size; j++) {
      if (i === j) {
        row.push(1.0)
      } else {
        const seed = (i * size + j) % 100
        const baseCorr = (seed / 100) * 2 - 1
        const correlation = Math.max(-0.8, Math.min(0.95, baseCorr))
        row.push(parseFloat(correlation.toFixed(2)))
      }
    }
    matrix.push(row)
  }
  // Делаем матрицу симметричной
  for (let i = 0; i < size; i++) {
    for (let j = i + 1; j < size; j++) {
      matrix[j][i] = matrix[i][j]
    }
  }
  return matrix
}

// Correlation matrix из portfolio store (10x10)
const correlationLabels = computed(() => {
  const positions = portfolioStore.positions.map(p => p.symbol)
  // Берем первые 10 активов, если их меньше - дополняем пустыми строками
  const labels = positions.slice(0, 10)
  while (labels.length < 10) {
    labels.push(`Asset${labels.length + 1}`)
  }
  return labels
})

const correlationData = computed(() => {
  const matrix = portfolioStore.correlationMatrix
  if (!matrix || matrix.length === 0) {
    // Fallback данные для 10x10 матрицы
    return generateCorrelationMatrix(10)
  }
  
  // Берем первые 10 строк и первые 10 значений из каждой строки
  const limitedMatrix = matrix.slice(0, 10).map(row => row.values.slice(0, 10))
  
  // Если данных меньше 10, дополняем fallback
  if (limitedMatrix.length < 10) {
    const fallback = generateCorrelationMatrix(10)
    for (let i = limitedMatrix.length; i < 10; i++) {
      limitedMatrix.push(fallback[i])
    }
  }
  
  // Убеждаемся, что каждая строка имеет 10 элементов
  return limitedMatrix.map(row => {
    const extendedRow = [...row]
    while (extendedRow.length < 10) {
      extendedRow.push(0)
    }
    return extendedRow.slice(0, 10)
  })
})

// Helpers
const formatCurrency = (val: number) => '₽' + Math.abs(val).toLocaleString('ru-RU', {maximumFractionDigits: 0})
const getBetaClass = (val: number) => Math.abs(val) > 0.5 ? 'font-bold text-white' : 'text-muted'

const getHeatmapStyle = (val: number) => {
  let bg = 'rgba(255,255,255,0.02)'
  let color = 'rgba(255,255,255,0.6)'
  
  if (val === 1) {
     bg = 'rgba(255,255,255,0.1)'
     color = '#fff'
  } else if (val > 0) {
     const alpha = val * 0.6 // Более насыщенный цвет
     bg = `rgba(59, 130, 246, ${alpha})` 
     color = '#fff'
  } else if (val < 0) {
     const alpha = Math.abs(val) * 0.6
     bg = `rgba(239, 68, 68, ${alpha})` 
     color = '#fff'
  }
  return { background: bg, color: color }
}

const refreshMetrics = async () => {
  if (isLoading.value) return
  isLoading.value = true
  
  // Эмуляция
  try {
     await new Promise(r => setTimeout(r, 800))
     lastUpdate.value = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
  } finally {
     isLoading.value = false
  }
}

const runStressTest = async () => {
  if (isStressTesting.value) return
  isStressTesting.value = true
  
  // Эмуляция
  try {
     await new Promise(r => setTimeout(r, 1200))
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
  display: flex; flex-direction: column; gap: 24px;
  padding: 24px 32px; max-width: 1600px; margin: 0 auto;
}

.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px; }
.section-title { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }
.header-actions { display: flex; gap: 12px; align-items: center; }

/* ============================================
   GLASS COMPONENTS
   ============================================ */
.glass-card {
  border-radius: 20px; overflow: hidden;
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 20px 40px -10px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
}

.glass-pill {
  display: flex; align-items: center; gap: 8px; padding: 4px 12px;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 99px; height: 36px;
}
.lbl-mini { font-size: 11px; color: rgba(255,255,255,0.5); font-weight: 600; text-transform: uppercase; }

/* Scrub Input */
.scrub-wrapper { display: flex; align-items: center; }
.scrub-input { 
  background: transparent; border: none; color: #3b82f6; width: 40px; text-align: right; 
  font-family: "SF Mono", monospace; font-weight: 600; font-size: 13px; outline: none; padding: 0;
}

/* Select */
.glass-select-clean {
  background: transparent; border: none; color: #fff; font-size: 13px; font-weight: 500; outline: none; cursor: pointer;
}
.glass-select-clean option { background: #1a1c23; color: #fff; }

/* ============================================
   KPI GRID
   ============================================ */
.kpi-cards-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.kpi-card { padding: 20px; display: flex; flex-direction: column; justify-content: space-between; min-height: 110px; }
.kpi-label { font-size: 11px; text-transform: uppercase; color: rgba(255,255,255,0.5); font-weight: 700; letter-spacing: 0.05em; margin-bottom: 8px; }
.kpi-value { font-size: 26px; font-weight: 700; font-family: "SF Mono", monospace; line-height: 1.1; letter-spacing: -0.02em; }
.kpi-sub { font-size: 11px; margin-top: 6px; display: flex; gap: 6px; }

/* ============================================
   DASHBOARD LAYOUT
   ============================================ */
.dashboard-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 24px; align-items: start; }
.col-left, .col-right { display: flex; flex-direction: column; gap: 24px; }
.panel { padding: 24px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.panel-header h3 { margin: 0; font-size: 13px; font-weight: 600; text-transform: uppercase; color: rgba(255,255,255,0.9); letter-spacing: 0.05em; }

/* ============================================
   TABLES
   ============================================ */
.risk-table-wrapper { overflow-x: auto; }
.glass-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.glass-table th { 
  text-align: left; padding: 0 0 12px 0; 
  color: rgba(255,255,255,0.4); font-weight: 600; font-size: 10px; text-transform: uppercase; 
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.glass-table td { padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.03); color: rgba(255,255,255,0.9); }
.glass-table tr:last-child td { border-bottom: none; }

.asset-row { display: flex; align-items: center; gap: 10px; }
.dot { width: 6px; height: 6px; border-radius: 2px; }
.sym { font-weight: 600; color: #fff; }

.bar-cell { display: flex; align-items: center; justify-content: flex-end; gap: 10px; }
.progress-bar { width: 80px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; background: #ef4444; border-radius: 2px; }
.bar-val { min-width: 32px; text-align: right; opacity: 0.7; }

/* ============================================
   STRESS LIST
   ============================================ */
.stress-list { display: flex; flex-direction: column; gap: 8px; }
.stress-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; background: rgba(255,255,255,0.02); border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.03); transition: background 0.2s;
}
.stress-item:hover { background: rgba(255,255,255,0.04); }
.stress-info { display: flex; flex-direction: column; gap: 2px; }
.stress-name { font-size: 13px; font-weight: 600; color: #fff; }
.stress-desc { font-size: 11px; color: rgba(255,255,255,0.4); }
.stress-result { text-align: right; display: flex; flex-direction: column; }
.stress-val { font-family: "SF Mono", monospace; font-weight: 600; font-size: 13px; }
.stress-pct { font-size: 11px; opacity: 0.6; }

/* ============================================
   LISTS & METRICS
   ============================================ */
.factor-list, .metrics-kv-list { display: flex; flex-direction: column; gap: 12px; }
.list-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.list-row:last-child { border-bottom: none; }
.lbl { font-size: 13px; color: #fff; font-weight: 500; }
.sub-lbl { font-size: 10px; color: rgba(255,255,255,0.4); display: block; }
.val { font-family: "SF Mono", monospace; font-weight: 500; font-size: 13px; }

.kv-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
.k { color: rgba(255,255,255,0.6); }
.v { color: #fff; font-family: "SF Mono", monospace; font-weight: 500; }

/* ============================================
   MATRIX
   ============================================ */
.correlation-matrix-grid { display: grid; grid-template-columns: 40px repeat(10, 1fr); gap: 4px; overflow-x: auto; }
.matrix-cell {
  height: 40px; display: flex; align-items: center; justify-content: center;
  font-size: 12px; border-radius: 6px;
}
.matrix-cell.header { color: rgba(255,255,255,0.4); font-weight: 600; font-size: 10px; }
.matrix-cell.value { font-family: "SF Mono", monospace; font-weight: 500; cursor: default; transition: transform 0.1s; font-size: 11px; }
.matrix-cell.value:hover { transform: scale(1.15); z-index: 2; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
.matrix-cell.header { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.correlation-matrix-wrapper { overflow-x: auto; width: 100%; }

/* ============================================
   UTILS
   ============================================ */
.btn-glass {
  height: 36px; padding: 0 16px; border-radius: 10px; font-weight: 600; font-size: 13px;
  display: flex; align-items: center; gap: 8px; cursor: pointer; border: none; transition: all 0.2s;
}
.btn-glass.primary { background: #3b82f6; color: #fff; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }
.btn-glass.primary:hover:not(:disabled) { background: #2563eb; transform: translateY(-1px); }

.btn-xs-glass {
  padding: 4px 10px; font-size: 10px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); 
  color: #fff; border-radius: 6px; cursor: pointer; font-weight: 600; transition: all 0.2s;
}
.btn-xs-glass:hover { background: rgba(255,255,255,0.1); }

.badge-glass { font-size: 10px; background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; color: rgba(255,255,255,0.7); }
.legend { display: flex; gap: 12px; align-items: center; font-size: 10px; color: rgba(255,255,255,0.4); }
.dot-legend { width: 6px; height: 6px; border-radius: 50%; display: inline-block; margin-right: 4px; }

/* Colors & Helpers */
.text-gradient-green { background: linear-gradient(135deg, #4ade80, #22c55e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-gradient-blue { background: linear-gradient(135deg, #60a5fa, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-red { color: #f87171; }
.text-green { color: #4ade80; }
.text-orange { color: #fbbf24; }
.text-white { color: #fff; }
.text-muted { color: rgba(255,255,255,0.4); }
.text-accent { color: #3b82f6; }
.font-bold { font-weight: 700; }
.bg-blue { background: #3b82f6; }
.bg-red { background: #ef4444; }
.pl-4 { padding-left: 16px; }
.pr-4 { padding-right: 16px; }
.mono { font-family: "SF Mono", monospace; }

.spinner-mini { width: 12px; height: 12px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1200px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .kpi-cards-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
    gap: 16px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .glass-pill {
    flex: 1;
    min-width: 120px;
  }
  
  .section-title {
    font-size: 22px;
  }
  
  .section-subtitle {
    font-size: 12px;
  }
  
  .kpi-cards-grid {
    grid-template-columns: 1fr;
  }
  
  .kpi-card {
    min-height: 90px;
    padding: 16px;
  }
  
  .kpi-value {
    font-size: 22px;
  }
  
  .panel {
    padding: 16px;
  }
  
  .risk-table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .correlation-matrix-grid {
    grid-template-columns: 30px repeat(10, 1fr);
    gap: 2px;
  }
  
  .matrix-cell {
    height: 32px;
    font-size: 10px;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 12px;
    gap: 12px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .section-subtitle {
    font-size: 11px;
  }
  
  .glass-pill {
    width: 100%;
    min-width: 100%;
  }
  
  .kpi-value {
    font-size: 20px;
  }
  
  .panel {
    padding: 12px;
  }
  
  .panel-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .glass-table {
    font-size: 11px;
  }
  
  .glass-table th,
  .glass-table td {
    padding: 8px 0;
  }
  
  .correlation-matrix-grid {
    grid-template-columns: 25px repeat(10, 1fr);
    gap: 1px;
    min-width: 100%;
  }
  
  .matrix-cell {
    height: 28px;
    font-size: 9px;
  }
  
  .stress-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .stress-result {
    text-align: left;
  }
}
</style>