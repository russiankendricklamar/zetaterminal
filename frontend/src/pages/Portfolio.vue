<!-- src/views/PortfolioView.vue -->
<template>
  <div class="portfolio-page">
    
    <!-- Hero Section: Заголовок и основные действия -->
    <div class="hero-section">
      <div class="hero-left">
        <h1>Управление портфелем</h1>
        <div class="hero-meta">
          <span class="glass-pill">Стратегия: <strong>Multi-Asset</strong></span>
          <span class="glass-pill">Ребалансировка: <strong>Monthly</strong></span>
          <span class="glass-pill risk-aggressive">
            <span class="status-dot"></span>
            Риск: Агрессивный
          </span>
        </div>
      </div>
      <div class="hero-actions">
        <div class="last-update">Обновлено: <span class="mono">{{ lastUpdate }}</span></div>
        <button class="btn-glass primary" @click="recalcPortfolio" :disabled="isRecalcing">
          <svg v-if="!isRecalcing" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          <span v-else class="spinner"></span>
          {{ isRecalcing ? 'Пересчет...' : 'Пересчитать' }}
        </button>
        <button class="btn-glass outline" @click="exportPdf">
          <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
          Экспорт PDF
        </button>
      </div>
    </div>

    <!-- KPI Grid: Ключевые показатели (Стеклянные карточки) -->
    <div class="kpi-grid">
      <div class="glass-card kpi-card glow-green">
        <div class="kpi-header">
          <span class="kpi-label">Total P&L</span>
          <div class="trend-badge positive">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4"><path d="M18 15l-6-6-6 6"/></svg>
            12.4%
          </div>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-gradient-green">452,109 <small>RUB</small></div>
          <div class="kpi-sub">NAV: 3.64M</div>
        </div>
      </div>

      <div class="glass-card kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">VaR 95%</span>
          <div class="trend-badge negative">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4"><path d="M6 9l6 6 6-6"/></svg>
            1.2%
          </div>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-white">2.45%</div>
          <div class="kpi-sub">Daily Risk</div>
        </div>
      </div>

      <div class="glass-card kpi-card glow-blue">
        <div class="kpi-header">
          <span class="kpi-label">Sharpe Ratio</span>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-gradient-blue">1.85</div>
          <div class="kpi-sub">Risk-Free Rate: 4.2%</div>
        </div>
      </div>

      <div class="glass-card kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">Diversification</span>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-white">0.34</div>
          <div class="kpi-sub">Correlation Coeff</div>
        </div>
      </div>
    </div>

    <!-- Main Dashboard Grid -->
    <div class="dashboard-grid">
      
      <!-- LEFT COLUMN -->
      <div class="col-main">
        
        <!-- Positions Table -->
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Открытые позиции</h3>
            <div class="search-sm">
               <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
               <input type="text" placeholder="Фильтр..." class="input-reset" @input="filterPositions">
            </div>
          </div>
          <div class="panel-body p-0">
             <div class="table-container">
               <table class="glass-table">
                 <thead>
                   <tr>
                     <th>Инструмент</th>
                     <th class="text-right">Цена</th>
                     <th class="text-right">День %</th>
                     <th class="text-right">Позиция</th>
                     <th class="text-right">Вес</th>
                     <th class="text-right">Таргет</th>
                     <th class="text-right">Дрифт</th>
                   </tr>
                 </thead>
                 <tbody>
                   <tr 
                      v-for="pos in filteredPositions" 
                      :key="pos.symbol"
                      @click="selectAsset(pos)"
                      :class="{ active: selectedAsset?.symbol === pos.symbol }"
                   >
                     <td>
                       <div class="asset-cell">
                         <div class="asset-icon" :style="{ background: pos.color }">{{ pos.symbol[0] }}</div>
                         <div class="asset-info">
                           <span class="symbol">{{ pos.symbol }}</span>
                           <span class="name">{{ pos.name }}</span>
                         </div>
                       </div>
                     </td>
                     <td class="text-right mono">${{ pos.price }}</td>
                     <td class="text-right mono">
                       <span :class="['change-pill', pos.dayChange > 0 ? 'text-green' : 'text-red']">{{ pos.dayChange > 0 ? '+' : '' }}{{ pos.dayChange }}%</span>
                     </td>
                     <td class="text-right mono opacity-80">${{ (pos.notional / 1000).toFixed(1) }}k</td>
                     <td class="text-right mono font-bold">{{ pos.allocation }}%</td>
                     <td class="text-right mono opacity-50">{{ pos.targetAllocation }}%</td>
                     <td class="text-right">
                        <div :class="['drift-val', getDriftClass(pos)]">{{ (pos.allocation - pos.targetAllocation).toFixed(1) }}%</div>
                     </td>
                   </tr>
                 </tbody>
               </table>
             </div>
          </div>
        </div>

        <!-- Charts Row: Матрица и Карта -->
        <div class="charts-row-vertical">
            <!-- Correlation Matrix -->
            <div class="glass-panel">
               <div class="panel-header">
                  <h3>Матрица Корреляций</h3>
               </div>
               <div class="panel-body heatmap-body">
                  <div class="heatmap-wrapper">
                     <div class="heatmap-header-row">
                        <div class="heatmap-empty"></div>
                        <div v-for="col in correlationMatrix" :key="col.label" class="heatmap-th">{{ col.label }}</div>
                     </div>
                     <div class="heatmap-row" v-for="(row, r) in correlationMatrix" :key="r">
                        <div class="heatmap-rh">{{ row.label }}</div>
                        <div 
                          class="heatmap-cell" 
                          v-for="(val, c) in row.values" 
                          :key="c"
                          :style="{ backgroundColor: getHeatmapColor(val) }"
                        >
                          {{ val === 1 ? '1.0' : val.toFixed(2) }}
                        </div>
                     </div>
                  </div>
               </div>
            </div>
            
            <!-- Market Map -->
            <div class="glass-panel">
               <div class="panel-header">
                  <h3>Тепловая карта</h3>
               </div>
               <div class="panel-body" style="min-height: 280px; padding: 0;">
                  <div class="treemap-tall">
                     <div 
                        v-for="pos in positions" 
                        :key="pos.symbol"
                        class="treemap-item"
                        :style="{ 
                           flexGrow: pos.allocation, 
                           backgroundColor: pos.dayChange > 0 ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)'
                        }"
                     >
                        <span class="tm-symbol">{{ pos.symbol }}</span>
                        <span class="tm-val">{{ pos.dayChange > 0 ? '+' : '' }}{{ pos.dayChange }}%</span>
                     </div>
                  </div>
               </div>
            </div>
        </div>

      </div>

      <!-- RIGHT COLUMN: ALL FULL WIDTH -->
      <aside class="col-side-flex">
        
        <!-- Asset Details -->
        <transition name="fade">
        <div class="glass-panel inspector-card" v-if="selectedAsset">
          <div class="panel-header">
             <div class="inspector-header-top">
                 <div class="asset-lg-icon" :style="{ background: selectedAsset.color }">{{ selectedAsset.symbol[0] }}</div>
                 <div class="inspector-title">
                     <h2>{{ selectedAsset.symbol }}</h2>
                     <span>{{ selectedAsset.name }}</span>
                 </div>
             </div>
             <div class="badge-glass">Equity</div>
          </div>
          <div class="panel-body">
             <div class="mini-chart-container">
                 <div class="chart-bars">
                    <div 
                       v-for="(h, i) in getMockHistogram(selectedAsset.symbol)" 
                       :key="i"
                       class="chart-bar"
                       :style="{ height: h + '%', backgroundColor: i > 15 ? '#4ade80' : 'rgba(255,255,255,0.2)' }"
                    ></div>
                 </div>
                 <div class="chart-meta">
                    <span class="active">1D</span><span>1W</span><span>1M</span><span>3M</span><span>1Y</span>
                 </div>
             </div>

             <div class="inspector-grid">
                <div class="metric-cell">
                   <label>Return</label>
                   <span class="text-green">+14.2%</span>
                </div>
                <div class="metric-cell">
                   <label>Volatility</label>
                   <span>18.5%</span>
                </div>
                <div class="metric-cell">
                   <label>Beta</label>
                   <span>1.12</span>
                </div>
                <div class="metric-cell">
                   <label>Max DD</label>
                   <span class="text-red">-12.4%</span>
                </div>
             </div>
             
             <div class="micro-metrics">
                <div class="micro-metric">
                   <span class="label">Sharpe</span>
                   <span class="value">0.92</span>
                </div>
                <div class="micro-metric">
                   <span class="label">Sortino</span>
                   <span class="value">1.38</span>
                </div>
                <div class="micro-metric">
                   <span class="label">Skew</span>
                   <span class="value">-0.24</span>
                </div>
             </div>
             
             <button class="btn-glass primary w-full mt-3" @click="openAnalysis">Открыть анализ</button>
          </div>
        </div>
        </transition>

        <!-- Optimizer Widget -->
        <div class="glass-panel optimizer-card">
           <div class="panel-header">
              <h3>Оптимизатор</h3>
              <button class="btn-icon-xs" @click="resetOptimizer" title="Сброс">↺</button>
           </div>
           <div class="panel-body-optimizer">
              
              <div class="control-group compact">
                 <label>Модель</label>
                 <div class="custom-select">
                    <select v-model="optimizer.model">
                       <option>Mean-Variance</option>
                       <option>Black-Litterman</option>
                       <option>Risk Parity</option>
                    </select>
                    <svg class="chevron" width="10" height="6" viewBox="0 0 10 6" fill="none" stroke="currentColor"><path d="M1 1L5 5L9 1" stroke-width="1.5"/></svg>
                 </div>
              </div>
              
              <div class="control-group compact">
                 <div class="flex justify-between mb-1">
                    <label>Веса (%)</label>
                 </div>
                 <div class="range-inputs-row">
                    <div class="glass-input-wrapper">
                       <input type="number" v-model.number="optimizer.minWeight" @change="validateWeights">
                       <span>%</span>
                    </div>
                    <div class="dash">-</div>
                    <div class="glass-input-wrapper">
                       <input type="number" v-model.number="optimizer.maxWeight" @change="validateWeights">
                       <span>%</span>
                    </div>
                 </div>
              </div>

              <div class="control-group compact">
                 <div class="flex justify-between mb-1">
                    <label>Target Vol</label>
                    <span class="val-highlight">{{ optimizer.targetVol }}%</span>
                 </div>
                 <input type="range" class="ios-slider-sm" min="5" max="30" v-model.number="optimizer.targetVol">
              </div>
              
              <div class="control-group toggle-row compact">
                 <label>Ребалансировка</label>
                 <label class="ios-toggle-sm">
                    <input type="checkbox" v-model="optimizer.rebalance">
                    <span class="slider"></span>
                 </label>
              </div>

              <div class="flex-spacer"></div>

              <button class="btn-glass primary w-full compact" @click="calculateOptimization" :disabled="isOptimizing">
                <span v-if="!isOptimizing">Рассчитать</span>
                <span v-else class="flex-center"><span class="spinner-sm"></span> Расчет...</span>
              </button>
           </div>
        </div>

        <!-- Combined Metrics: Risk + Stats with Tabs -->
        <div class="glass-panel combined-metrics">
           <div class="combined-tabs">
              <button 
                 :class="['tab-button', { active: activeMetricsTab === 'risk' }]"
                 @click="activeMetricsTab = 'risk'"
              >
                 Риск-метрики
              </button>
              <button 
                 :class="['tab-button', { active: activeMetricsTab === 'stats' }]"
                 @click="activeMetricsTab = 'stats'"
              >
                 Статистика
              </button>
           </div>

           <!-- Risk Metrics Tab -->
           <div class="tab-content" v-show="activeMetricsTab === 'risk'">
              <div class="metric-row">
                 <div class="metric-label">
                    <span>Expected Shortfall</span>
                    <span class="meta-hint">CVaR 95%</span>
                 </div>
                 <div class="metric-value text-red">-3.78%</div>
              </div>
              <div class="metric-row">
                 <div class="metric-label">
                    <span>Max Drawdown</span>
                    <span class="meta-hint">Peak-to-Trough</span>
                 </div>
                 <div class="metric-value text-red">-18.24%</div>
              </div>
              <div class="metric-row">
                 <div class="metric-label">
                    <span>Calmar Ratio</span>
                    <span class="meta-hint">Return / Max DD</span>
                 </div>
                 <div class="metric-value text-white">1.41</div>
              </div>
              <div class="metric-row">
                 <div class="metric-label">
                    <span>Rolling Vol (30D)</span>
                    <span class="meta-hint">Annualized</span>
                 </div>
                 <div class="metric-value text-white">12.8%</div>
              </div>
           </div>

           <!-- Performance Stats Tab -->
           <div class="tab-content" v-show="activeMetricsTab === 'stats'">
              <div class="stats-grid">
                 <div class="stat-item">
                    <span class="stat-label">YTD Return</span>
                    <span class="stat-value text-green">+8.42%</span>
                 </div>
                 <div class="stat-item">
                    <span class="stat-label">Win Rate</span>
                    <span class="stat-value text-green">58.3%</span>
                 </div>
                 <div class="stat-item">
                    <span class="stat-label">Profit Factor</span>
                    <span class="stat-value text-white">1.87x</span>
                 </div>
                 <div class="stat-item">
                    <span class="stat-label">Avg Trade</span>
                    <span class="stat-value text-white">+0.34%</span>
                 </div>
              </div>
           </div>
        </div>

      </aside>
    </div>

    <!-- Toast Notifications -->
    <transition name="slide-up">
      <div v-if="toast.show" class="toast-notification" :class="'toast-' + toast.type">
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Mock Positions Data
const positions = ref([
  { symbol: 'SPY', name: 'S&P 500 ETF', price: '142.50', dayChange: 1.24, notional: 850000, allocation: 35, targetAllocation: 30, color: '#3b82f6' },
  { symbol: 'TLT', name: 'US Bonds 20Y', price: '87.30', dayChange: -0.48, notional: 620000, allocation: 25, targetAllocation: 28, color: '#10b981' },
  { symbol: 'GLD', name: 'Gold ETF', price: '198.75', dayChange: 0.92, notional: 450000, allocation: 18, targetAllocation: 15, color: '#fbbf24' },
  { symbol: 'DXY', name: 'US Dollar Idx', price: '104.20', dayChange: -0.15, notional: 380000, allocation: 15, targetAllocation: 17, color: '#8b5cf6' },
  { symbol: 'QQQ', name: 'Nasdaq 100', price: '325.48', dayChange: 2.15, notional: 310000, allocation: 12, targetAllocation: 10, color: '#ec4899' }
])

const selectedAsset = ref(positions.value[0])
const lastUpdate = ref(new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}))
const isRecalcing = ref(false)
const isOptimizing = ref(false)
const searchFilter = ref('')
const activeMetricsTab = ref('risk')

const toast = ref({ show: false, message: '', type: 'success' })

const optimizer = ref({
  model: 'Mean-Variance',
  minWeight: 0,
  maxWeight: 25,
  targetVol: 15,
  rebalance: true
})

const filteredPositions = computed(() => {
  if (!searchFilter.value) return positions.value
  const query = searchFilter.value.toLowerCase()
  return positions.value.filter(p => 
    p.symbol.toLowerCase().includes(query) || p.name.toLowerCase().includes(query)
  )
})

const correlationMatrix = [
   { label: 'SPY', values: [1.0, 0.6, 0.3, -0.2, 0.8] },
   { label: 'TLT', values: [0.6, 1.0, 0.1, 0.4, 0.5] },
   { label: 'GLD', values: [0.3, 0.1, 1.0, 0.2, 0.3] },
   { label: 'DXY', values: [-0.2, 0.4, 0.2, 1.0, -0.1] },
   { label: 'QQQ', values: [0.8, 0.5, 0.3, -0.1, 1.0] },
]

onMounted(() => {
  if (positions.value?.length > 0) selectedAsset.value = positions.value[0]
})

const selectAsset = (pos: any) => selectedAsset.value = pos

const recalcPortfolio = async () => {
  isRecalcing.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  lastUpdate.value = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
  isRecalcing.value = false
  showToast('Портфель пересчитан', 'success')
}

const exportPdf = () => {
  showToast('PDF экспорт инициирован...', 'info')
  setTimeout(() => {
    showToast('Файл portfolio_2026-01-03.pdf загружен', 'success')
  }, 1200)
}

const filterPositions = (e: any) => {
  searchFilter.value = e.target.value
}

const openAnalysis = () => {
  if (selectedAsset.value) {
    showToast(`Открыт анализ ${selectedAsset.value.symbol}`, 'info')
  }
}

const calculateOptimization = async () => {
  isOptimizing.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))
  isOptimizing.value = false
  showToast(`Оптимизация завершена (модель: ${optimizer.value.model})`, 'success')
}

const resetOptimizer = () => {
  optimizer.value = {
    model: 'Mean-Variance',
    minWeight: 0,
    maxWeight: 25,
    targetVol: 15,
    rebalance: true
  }
  showToast('Оптимизатор сброшен', 'info')
}

const validateWeights = () => {
  if (optimizer.value.minWeight > optimizer.value.maxWeight) {
    optimizer.value.maxWeight = optimizer.value.minWeight + 5
  }
}

const showToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

const getHeatmapColor = (val: number) => {
   const alpha = Math.abs(val)
   if (val === 1) return 'rgba(255,255,255,0.05)'
   return val > 0 ? `rgba(59, 130, 246, ${alpha})` : `rgba(239, 68, 68, ${alpha})`
}

const getDriftClass = (pos: any) => {
   const drift = Math.abs(pos.allocation - pos.targetAllocation)
   if (drift < 0.5) return 'text-muted'
   return (pos.allocation - pos.targetAllocation) > 0 ? 'text-green' : 'text-red'
}

const getMockHistogram = (symbol: string) => {
   return Array.from({length: 20}, () => Math.random() * 80 + 20)
}
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.portfolio-page {
  padding: 24px 32px; 
  max-width: 1800px; 
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 28px;
  min-height: 100vh;
}

/* ============================================
   HERO & ACTIONS
   ============================================ */
.hero-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding-bottom: 8px;
}

.hero-left h1 {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 16px 0;
  letter-spacing: -0.01em;
}

.hero-meta {
  display: flex;
  gap: 10px;
}

.glass-pill {
  font-size: 12px;
  padding: 6px 12px; 
  background: rgba(255,255,255,0.06); 
  border: 1px solid rgba(255,255,255,0.1); 
  border-radius: 99px; 
  color: rgba(255,255,255,0.8);
  display: flex;
  align-items: center;
  gap: 6px;
  backdrop-filter: blur(4px);
}

.glass-pill strong {
  color: #fff;
  font-weight: 600;
}

.risk-aggressive {
  background: rgba(251, 191, 36, 0.1);
  border-color: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
}

.status-dot {
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
  box-shadow: 0 0 6px currentColor;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.last-update {
  font-size: 12px;
  color: rgba(255,255,255,0.4);
  margin-right: 8px;
}

/* GLASS BUTTONS */
.btn-glass {
  height: 36px;
  padding: 0 16px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  border: 1px solid transparent;
}

.btn-glass.primary {
  background: rgba(255, 255, 255, 0.9);
  color: #000;
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2);
}

.btn-glass.primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(255, 255, 255, 0.3);
}

.btn-glass.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-glass.outline {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.1);
}

.btn-glass.outline:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.btn-glass.compact {
  height: 32px;
  font-size: 11px;
  padding: 0 12px;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #000;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ============================================
   KPI GRID
   ============================================ */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.glass-card {
  position: relative;
  overflow: hidden;
  background: rgba(30, 32, 40, 0.4); 
  backdrop-filter: blur(20px) saturate(140%);
  border: 1px solid rgba(255,255,255,0.08); 
  border-radius: 20px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 10px 30px -10px rgba(0,0,0,0.3);
  transition: transform 0.2s, background 0.2s;
}

.glass-card:hover {
  background: rgba(40, 42, 50, 0.5);
  transform: translateY(-2px);
}

.glass-card.glow-green::before {
  content: "";
  position: absolute;
  top: -50px;
  right: -50px;
  width: 100px;
  height: 100px;
  background: #4ade80;
  filter: blur(60px);
  opacity: 0.15;
  pointer-events: none;
}

.glass-card.glow-blue::before {
  content: "";
  position: absolute;
  top: -50px;
  right: -50px;
  width: 100px;
  height: 100px;
  background: #3b82f6;
  filter: blur(60px);
  opacity: 0.15;
  pointer-events: none;
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.kpi-label {
  font-size: 11px;
  text-transform: uppercase;
  color: rgba(255,255,255,0.5);
  font-weight: 700;
  letter-spacing: 0.05em;
}

.trend-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 99px; 
  display: flex;
  align-items: center;
  gap: 4px;
}

.trend-badge.positive {
  color: #4ade80;
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.1);
}

.trend-badge.negative {
  color: #f87171;
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.1);
}

.kpi-value {
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.1;
}

.kpi-value small {
  font-size: 14px;
  color: rgba(255,255,255,0.4);
  font-weight: 500;
  margin-left: 4px;
}

.kpi-sub {
  font-size: 11px;
  color: rgba(255,255,255,0.4);
}

/* ============================================
   MAIN CONTENT GRID
   ============================================ */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
  flex: 1;
}

.col-main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ============================================
   RIGHT COLUMN - FLEX COLUMN (FULL WIDTH BLOCKS)
   ============================================ */
.col-side-flex {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

/* GLASS PANEL */
.glass-panel {
  background: rgba(20, 22, 28, 0.5); 
  backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.06); 
  border-radius: 20px; 
  box-shadow: 0 20px 40px -10px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255,255,255,0.02);
  flex-shrink: 0;
}

.panel-header h3 {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255,255,255,0.9);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.panel-body {
  padding: 16px 20px;
  overflow: hidden;
}

.panel-body.p-0 {
  padding: 0;
}

.heatmap-body {
  min-height: 380px !important;
  padding: 24px 20px !important;
}

.panel-body-optimizer {
  padding: 16px 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow: hidden;
}

/* SEARCH */
.search-sm {
  position: relative;
  width: 140px;
}

.search-sm svg {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255,255,255,0.3);
}

.input-reset {
  width: 100%;
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.1); 
  border-radius: 6px;
  padding: 4px 8px 4px 24px;
  color: #fff;
  font-size: 11px;
  outline: none;
  transition: all 0.2s;
}

.input-reset:focus {
  background: rgba(0,0,0,0.4);
  border-color: rgba(255,255,255,0.3);
}

/* ============================================
   TABLE STYLES
   ============================================ */
.table-container {
  overflow-x: auto;
}

.glass-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.glass-table th {
  text-align: left;
  padding: 12px 20px;
  color: rgba(255,255,255,0.4);
  font-weight: 600;
  font-size: 10px;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.glass-table tr {
  transition: background 0.15s;
  cursor: pointer;
  border-bottom: 1px solid rgba(255,255,255,0.02);
}

.glass-table tr:last-child {
  border-bottom: none;
}

.glass-table tr:hover {
  background: rgba(255,255,255,0.04);
}

.glass-table tr.active {
  background: rgba(59, 130, 246, 0.15);
  box-shadow: inset 3px 0 0 #3b82f6;
}

.glass-table td {
  padding: 12px 20px;
  color: rgba(255,255,255,0.9);
}

.asset-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.asset-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.asset-info {
  display: flex;
  flex-direction: column;
}

.asset-info .symbol {
  font-weight: 600;
  font-size: 13px;
  color: #fff;
}

.asset-info .name {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
}

.change-pill {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.text-green {
  color: #4ade80;
}

.text-red {
  color: #f87171;
}

.text-muted {
  color: rgba(255,255,255,0.3);
}

.drift-val {
  font-size: 11px;
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

/* ============================================
   CHARTS ROW
   ============================================ */
.charts-row-vertical {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.heatmap-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: rgba(0,0,0,0.15);
  border-radius: 12px;
}

.heatmap-header-row {
  display: flex;
  margin-bottom: 12px;
  gap: 2px;
}

.heatmap-empty {
  width: 50px;
}

.heatmap-th {
  flex: 1;
  text-align: center;
  font-size: 11px;
  color: rgba(255,255,255,0.5);
  font-weight: 700;
  padding: 8px 4px;
}

.heatmap-row {
  display: flex;
  align-items: stretch;
  gap: 2px;
  min-height: 48px;
}

.heatmap-rh {
  width: 50px;
  font-size: 11px;
  font-weight: 700;
  color: rgba(255,255,255,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.heatmap-cell {
  flex: 1;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.95);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.heatmap-cell:hover {
  transform: scale(1.15);
  z-index: 10;
  box-shadow: 0 6px 16px rgba(0,0,0,0.6), inset 0 0 8px rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.3);
}

.treemap-tall {
  display: flex;
  flex-wrap: wrap;
  height: 280px;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
}

.treemap-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  border: 1px solid rgba(0,0,0,0.2);
  color: #fff;
  transition: filter 0.2s;
  min-width: 60px;
}

.treemap-item:hover {
  filter: brightness(1.15);
  z-index: 2;
}

.tm-symbol {
  font-size: 12px;
  font-weight: 700;
}

.tm-val {
  font-size: 10px;
  opacity: 0.8;
  margin-top: 2px;
}

/* ============================================
   SIDEBAR - INSPECTOR
   ============================================ */
.inspector-card {
  flex-shrink: 0;
}

.inspector-header-top {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.asset-lg-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
  flex-shrink: 0;
}

.inspector-title h2 {
  margin: 0;
  font-size: 16px;
  color: #fff;
  line-height: 1.2;
}

.inspector-title span {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
  display: block;
}

.badge-glass {
  font-size: 9px;
  padding: 3px 6px;
  background: rgba(255,255,255,0.1);
  border-radius: 4px;
  color: rgba(255,255,255,0.8);
  flex-shrink: 0;
  margin-left: auto;
}

.inspector-card .panel-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mini-chart-container {
  background: rgba(0,0,0,0.2);
  border-radius: 8px;
  padding: 8px;
  border: 1px solid rgba(255,255,255,0.05);
  min-height: 50px;
}

.chart-bars {
  height: 40px;
  display: flex;
  align-items: flex-end;
  gap: 1px;
  margin-bottom: 4px;
}

.chart-bar {
  flex: 1;
  border-radius: 1px 1px 0 0;
  min-width: 2px;
}

.chart-meta {
  display: flex;
  justify-content: space-between;
  font-size: 8px;
  color: rgba(255,255,255,0.2);
}

.chart-meta span.active {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.inspector-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.metric-cell {
  background: rgba(255,255,255,0.03);
  padding: 6px 8px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.metric-cell label {
  font-size: 8px;
  text-transform: uppercase;
  color: rgba(255,255,255,0.3);
  margin-bottom: 2px;
  font-weight: 600;
  line-height: 1;
}

.metric-cell span {
  font-size: 11px;
  font-weight: 700;
  font-family: monospace;
  color: #fff;
  line-height: 1;
}

.micro-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 6px;
  padding: 8px;
  background: rgba(0,0,0,0.15);
  border-radius: 6px;
}

.micro-metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  min-height: 50px;
  justify-content: center;
}

.micro-metric .label {
  font-size: 8px;
  color: rgba(255,255,255,0.3);
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 3px;
  line-height: 1;
}

.micro-metric .value {
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}

/* ============================================
   OPTIMIZER
   ============================================ */
.optimizer-card {
  flex-shrink: 0;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.control-group.compact {
  gap: 3px;
}

.control-group.compact label {
  font-size: 9px !important;
  margin-bottom: 1px !important;
  font-weight: 600;
  color: rgba(255,255,255,0.7);
}

.custom-select {
  position: relative;
}

.custom-select select {
  width: 100%;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  padding: 6px 10px;
  color: #fff;
  font-size: 11px;
  appearance: none;
  outline: none;
}

.custom-select .chevron {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  opacity: 0.5;
}

.range-inputs-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.glass-input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  padding: 0 6px;
  height: 28px;
  transition: all 0.2s;
}

.glass-input-wrapper:focus-within {
  background: rgba(0,0,0,0.35);
  border-color: rgba(255,255,255,0.3);
  box-shadow: 0 0 0 2px rgba(255,255,255,0.05);
}

.glass-input-wrapper input {
  width: 100%;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: #fff;
  text-align: right;
  padding: 0;
  margin-right: 3px;
  font-family: "SF Mono", monospace;
  outline: none;
  font-size: 11px;
  height: 100%;
}

.glass-input-wrapper span {
  font-size: 11px;
  color: rgba(255,255,255,0.3);
  font-weight: 500;
}

.dash {
  color: rgba(255,255,255,0.15);
  font-weight: 600;
  font-size: 11px;
}

.flex-spacer {
  flex: 1;
  min-height: 4px;
}

.ios-slider-sm {
  -webkit-appearance: none;
  width: 100%;
  height: 2px;
  background: rgba(255,255,255,0.15);
  border-radius: 2px;
  outline: none;
}

.ios-slider-sm::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
  cursor: grab;
  margin-top: -6px;
  border: 0.5px solid rgba(0,0,0,0.1);
}

.toggle-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 28px;
}

.ios-toggle-sm {
  position: relative;
  display: inline-block;
  width: 28px;
  height: 16px;
}

.ios-toggle-sm input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255,255,255,0.1);
  border-radius: 20px;
  transition: .3s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 12px;
  width: 12px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  border-radius: 50%;
  transition: .3s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

input:checked + .slider {
  background-color: #34c759;
}

input:checked + .slider:before {
  transform: translateX(12px);
}

/* ============================================
   COMBINED METRICS - RISK + STATS WITH TABS
   ============================================ */
.combined-metrics {
  flex-shrink: 0;
}

.combined-tabs {
  display: flex;
  gap: 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  padding: 0 20px;
}

.tab-button {
  flex: 1;
  padding: 12px 16px;
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.4);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  position: relative;
  transition: color 0.2s;
}

.tab-button:hover {
  color: rgba(255,255,255,0.6);
}

.tab-button.active {
  color: rgba(255,255,255,0.9);
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #3b82f6;
}

.tab-content {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Risk Metrics Rows */
.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: rgba(0,0,0,0.15);
  border-radius: 6px;
  border-left: 2px solid rgba(255,255,255,0.1);
}

.metric-label {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.metric-label span:first-child {
  font-size: 10px;
  font-weight: 600;
  color: rgba(255,255,255,0.85);
  line-height: 1.2;
}

.meta-hint {
  font-size: 8px !important;
  color: rgba(255,255,255,0.25) !important;
  font-weight: 400 !important;
}

.metric-value {
  font-size: 11px;
  font-weight: 700;
  font-family: monospace;
  white-space: nowrap;
}

/* Performance Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  background: rgba(0,0,0,0.15);
  border-radius: 6px;
  text-align: center;
  min-height: 50px;
  justify-content: center;
}

.stat-label {
  font-size: 9px;
  color: rgba(255,255,255,0.3);
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 4px;
  line-height: 1.2;
}

.stat-value {
  font-size: 13px;
  font-weight: 700;
  font-family: monospace;
  color: #fff;
  line-height: 1;
}

/* ============================================
   BUTTONS & UTILS
   ============================================ */
.btn-icon-xs {
  width: 22px;
  height: 22px;
  padding: 0;
  border: none;
  background: rgba(255,255,255,0.05);
  color: #fff;
  cursor: pointer;
  border-radius: 4px;
  font-size: 11px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon-xs:hover {
  background: rgba(255,255,255,0.1);
}

.spinner-sm {
  width: 10px;
  height: 10px;
  border: 1.5px solid #fff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* TOAST */
.toast-notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 14px 20px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  max-width: 320px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  z-index: 1000;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.1);
}

.toast-success {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
  border-color: rgba(74, 222, 128, 0.3);
}

.toast-error {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.3);
}

.toast-info {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
  border-color: rgba(96, 165, 250, 0.3);
}

/* ============================================
   UTILS
   ============================================ */
.text-right {
  text-align: right;
}

.text-gradient-green {
  background: linear-gradient(to right, #4ade80, #22c55e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.text-gradient-blue {
  background: linear-gradient(to right, #60a5fa, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.text-white {
  color: #fff;
}

.mono {
  font-family: "SF Mono", monospace;
}

.opacity-50 {
  opacity: 0.5;
}

.opacity-80 {
  opacity: 0.8;
}

.font-bold {
  font-weight: 700;
}

.w-full {
  width: 100%;
}

.mt-3 {
  margin-top: 12px;
}

.mb-1 {
  margin-bottom: 4px;
}

.flex {
  display: flex;
}

.flex-center {
  display: flex;
  align-items: center;
  gap: 4px;
}

.justify-between {
  justify-content: space-between;
}

.val-highlight {
  color: #3b82f6;
  font-weight: 600;
  font-size: 9px;
}

/* ============================================
   TRANSITIONS
   ============================================ */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.slide-up-enter-from {
  transform: translateY(20px);
  opacity: 0;
}

.slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1400px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .portfolio-page {
    padding: 16px;
  }

  .hero-section {
    flex-direction: column;
    gap: 16px;
  }

  .hero-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-grid {
    grid-template-columns: 1fr 280px;
    gap: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>