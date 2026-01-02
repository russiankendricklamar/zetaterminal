<!-- src/views/PortfolioView.vue -->
<template>
  <div class="portfolio-page">
    
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-left">
        <h1>Управление портфелем ценных бумаг</h1>
        <div class="hero-meta">
          <span class="meta-tag">Стратегия: Глобальная мультиактивная</span>
          <span class="meta-tag">Ребалансировка: каждый месяц</span>
          <span class="meta-tag risk-tag">Риск-профиль: Агрессивный</span>
        </div>
      </div>
      <div class="hero-actions">
        <div class="last-update">Обновлено: {{ lastUpdate }}</div>
        <button class="btn btn-primary" @click="recalcPortfolio">
          <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          Пересчитать
        </button>
        <button class="btn btn-outline">
          <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
          Отчет PDF
        </button>
      </div>
    </div>

    <!-- KPI Grid -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">Общий P&L</span>
          <span class="kpi-trend positive">+12.4%</span>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-gradient-green">452,109 руб.</div>
          <div class="kpi-sub">Общая стоимость: {{ (store.totalNotional / 1000000).toFixed(2) }} млн. руб.</div>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">VaR 95%</span>
          <span class="kpi-trend negative">+1.2%</span>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-white">{{ (store.kpis.var95 / 1000).toFixed(2) }}%</div>
          <div class="kpi-sub">Оценка дневной волатильности</div>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">Эффективность</span>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-gradient-blue">{{ store.kpis.sharpeRatio.toFixed(2) }}</div>
          <div class="kpi-sub">Коэффициент Шарпа (Rf=4.2%)</div>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">Диверсификация</span>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-white">0.34</div>
          <div class="kpi-sub">Коэффициент корреляции</div>
        </div>
      </div>
    </div>

    <!-- Main Dashboard Grid -->
    <div class="dashboard-grid">
      
      <!-- LEFT COLUMN (Main Content) -->
      <div class="col-main">
        
        <!-- Positions Table -->
        <div class="card">
          <div class="card-header">
            <h3>Открытые позиции</h3>
            <div class="header-controls">
               <input type="text" placeholder="Выбрать..." class="mini-search">
            </div>
          </div>
          <div class="card-body p-0">
             <div class="table-container">
               <table class="asset-table">
                 <thead>
                   <tr>
                     <th>Тикет (ISIN)</th>
                     <th class="text-right">Цена</th>
                     <th class="text-right">Изменение</th>
                     <th class="text-right">Позиция по активу</th>
                     <th class="text-right">Вес в портфеле</th>
                     <th class="text-right">Целевое значение веса</th>
                     <th>Разница</th>
                   </tr>
                 </thead>
                 <tbody>
                   <tr 
                      v-for="pos in store.positions" 
                      :key="pos.symbol"
                      @click="selectAsset(pos)"
                      :class="{ active: selectedAsset?.symbol === pos.symbol }"
                   >
                     <td>
                       <div class="asset-name-cell">
                         <span class="color-dot" :style="{ background: pos.color }"></span>
                         <div class="name-wrapper">
                           <span class="symbol">{{ pos.symbol }}</span>
                           <span class="name">{{ pos.name }}</span>
                         </div>
                       </div>
                     </td>
                     <td class="text-right mono">${{ pos.price || '142.50' }}</td>
                     <td class="text-right mono" :class="getRandomChangeClass()">
                       {{ getRandomChange() }}%
                     </td>
                     <td class="text-right mono">${{ (pos.notional / 1000).toFixed(1) }}k</td>
                     <td class="text-right mono font-bold">{{ pos.allocation }}%</td>
                     <td class="text-right mono text-muted">{{ pos.targetAllocation }}%</td>
                     <td class="gap-cell">
                        <div class="gap-bar-wrapper">
                           <div class="gap-val" :class="getGapClass(pos)">{{ (pos.allocation - pos.targetAllocation).toFixed(1) }}%</div>
                        </div>
                     </td>
                   </tr>
                 </tbody>
               </table>
             </div>
          </div>
        </div>

        <!-- Correlation Matrix -->
        <div class="card">
           <div class="card-header">
              <h3>Матрица Корреляций</h3>
           </div>
           <div class="card-body">
              <div class="heatmap-container">
                 <div class="heatmap-header-row">
                    <div class="heatmap-empty-cell"></div>
                    <div v-for="col in correlationMatrix" :key="col.label" class="heatmap-col-header">{{ col.label }}</div>
                 </div>
                 <div class="heatmap-row" v-for="(row, r) in correlationMatrix" :key="r">
                    <div class="heatmap-row-header">{{ row.label }}</div>
                    <div 
                      class="heatmap-cell" 
                      v-for="(val, c) in row.values" 
                      :key="c"
                      :style="{ backgroundColor: getHeatmapColor(val) }"
                    >
                      {{ val.toFixed(2) }}
                    </div>
                 </div>
              </div>
           </div>
        </div>
        
        <!-- Market Map (Tree Map) -->
        <div class="card">
           <div class="card-header">
              <h3>Тепловая карта портфеля</h3>
           </div>
           <div class="card-body">
              <div class="market-map">
                 <div 
                    v-for="pos in store.positions" 
                    :key="pos.symbol"
                    class="map-tile"
                    :style="{ 
                       flexGrow: pos.allocation, 
                       backgroundColor: getMarketMapColor()
                    }"
                 >
                    <span class="tile-symbol">{{ pos.symbol }}</span>
                    <span class="tile-change">{{ getRandomChange() }}%</span>
                 </div>
              </div>
           </div>
        </div>

      </div>

      <!-- RIGHT COLUMN (Detail View - STATIC) -->
      <aside class="col-side">
        
        <!-- Asset Analysis Card -->
        <div class="card" v-if="selectedAsset">
          <div class="card-header">
             <div class="asset-title">
               <span class="asset-lg-symbol">{{ selectedAsset.symbol }}</span>
               <span class="asset-lg-name">{{ selectedAsset.name }}</span>
             </div>
             <div class="badge-pill">Акции</div>
          </div>
          
          <div class="card-body">
             <!-- Chart Controls -->
             <div class="chart-controls">
                <button class="pill-btn active">Доходности</button>
                <button class="pill-btn">Просадка</button>
                <div class="spacer"></div>
                <select class="mini-select">
                   <option>1W</option>
                   <option>2W</option>
                   <option>1M</option>
                   <option selected>3M</option>
                   <option>6M</option>
                   <option>1Y</option>
                   <option>2Y</option>
                   <option>5Y</option>
                </select>
             </div>

             <!-- Histogram -->
             <div class="histogram-wrapper">
                <div class="histogram-bars">
                   <div 
                      v-for="(h, i) in getMockHistogram(selectedAsset.symbol)" 
                      :key="i"
                      class="hist-bar"
                      :style="{ height: h + '%', background: selectedAsset.color }"
                   ></div>
                </div>
             </div>

             <!-- Risk Metrics Grid -->
             <div class="metrics-grid-sm">
                <div class="metric-box">
                   <label>Годовая доходность</label>
                   <span class="text-green">+14.2%</span>
                </div>
                <div class="metric-box">
                   <label>Волатильность</label>
                   <span>18.5%</span>
                </div>
                <div class="metric-box">
                   <label>Бэта (β)</label>
                   <span>1.12</span>
                </div>
                <div class="metric-box">
                   <label>Максимальная просадка</label>
                   <span class="text-red">-12.4%</span>
                </div>
                <div class="metric-box">
                   <label>VaR (99%)</label>
                   <span>-2.8%</span>
                </div>
                <div class="metric-box">
                   <label>Эксцесс</label>
                   <span>3.4</span>
                </div>
                <div class="metric-box">
                   <label>Асимметрия</label>
                   <span>5.2</span>
                </div>
             </div>

             <div class="divider"></div>

             <!-- Action Buttons -->
             <div class="asset-actions">
                <button class="btn btn-outline w-full">Симуляция</button>
             </div>
          </div>
        </div>

        <!-- Portfolio Optimizer Settings (FIXED WIDTH) -->
        <div class="card">
           <div class="card-header">
              <h3>Оптимизация портфеля</h3>
              <button class="icon-btn-sm" title="Reset">↺</button>
           </div>
           <div class="card-body">
              <div class="settings-form">
                 
                 <!-- Optimization Model -->
                 <div class="form-group">
                    <label class="form-label">Модель Оптимизации</label>
                    <div class="select-wrapper">
                       <select class="form-control">
                          <option>Mean-Variance (Markowitz)</option>
                          <option>Black-Litterman Model</option>
                          <option>Risk Parity (ERC)</option>
                          <option>Hierarchical Risk Parity</option>
                       </select>
                       <span class="select-arrow">▼</span>
                    </div>
                 </div>
                 
                 <!-- Weight Constraints -->
                 <div class="form-group">
                    <div class="label-row">
                       <label class="form-label">Весовые Ограничения</label>
                       <span class="label-hint">Min - Max %</span>
                    </div>
                    <div class="range-inputs">
                       <div class="input-suffix">
                          <input type="number" value="0" class="input-box">
                          <span class="suffix">%</span>
                       </div>
                       <span class="separator">to</span>
                       <div class="input-suffix">
                          <input type="number" value="25" class="input-box">
                          <span class="suffix">%</span>
                       </div>
                    </div>
                 </div>

                 <!-- Target Volatility -->
                 <div class="form-group">
                    <div class="label-row">
                       <label class="form-label">Целевая волатильность</label>
                       <span class="val-display">15%</span>
                    </div>
                    <div class="slider-container">
                       <input type="range" class="range-slider" min="5" max="30" value="15">
                       <div class="range-scale">
                          <span>5%</span>
                          <span class="center-tick">15%</span>
                          <span>30%</span>
                       </div>
                    </div>
                 </div>
                 
                 <!-- Checkbox -->
                 <div class="form-group checkbox-group">
                    <label class="checkbox-container">
                       <input type="checkbox" checked>
                       <div class="checkmark"></div>
                       <span class="checkbox-label">Ребалансировать веса текущего портфеля</span>
                    </label>
                 </div>

                 <button class="btn btn-primary w-full mt-2">Запустить оптимизацию</button>
              </div>
           </div>
        </div>

      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'

const store = usePortfolioStore()
const selectedAsset = ref(null)
const lastUpdate = ref(new Date().toLocaleTimeString())

onMounted(() => {
  if (store.positions?.length > 0) selectedAsset.value = store.positions[0]
})

const selectAsset = (pos: any) => selectedAsset.value = pos
const recalcPortfolio = () => { lastUpdate.value = new Date().toLocaleTimeString() }

// Mock Correlation Matrix
const correlationMatrix = [
   { label: 'SPY', values: [1.0, 0.6, 0.3, -0.2, 0.8] },
   { label: 'TLT', values: [0.6, 1.0, 0.1, 0.4, 0.5] },
   { label: 'GLD', values: [0.3, 0.1, 1.0, 0.2, 0.3] },
   { label: 'DXY', values: [-0.2, 0.4, 0.2, 1.0, -0.1] },
   { label: 'QQQ', values: [0.8, 0.5, 0.3, -0.1, 1.0] },
]

// Visual Helpers
const getHeatmapColor = (val: number) => {
   const alpha = Math.abs(val)
   if (val === 1) return 'rgba(255,255,255,0.1)' // Diagonal
   return val > 0 ? `rgba(59, 130, 246, ${alpha})` : `rgba(239, 68, 68, ${alpha})`
}

const getRandomChange = () => (Math.random() * 3 - 1.5).toFixed(2)
const getRandomChangeClass = () => Math.random() > 0.5 ? 'text-green' : 'text-red'
const getGapClass = (pos: any) => (pos.allocation - pos.targetAllocation) > 0 ? 'text-green' : 'text-red'

const getMarketMapColor = () => {
   const val = Math.random() - 0.5;
   const alpha = Math.min(1, Math.abs(val) + 0.2);
   return val > 0 ? `rgba(16, 185, 129, ${alpha})` : `rgba(239, 68, 68, ${alpha})`
}

const getMockHistogram = (symbol: string) => {
   const bars = []
   const seed = symbol ? symbol.charCodeAt(0) : 50
   for (let i = 0; i < 20; i++) {
      let h = 50 * Math.exp(-Math.pow(i - 10, 2) / 10) 
      h += (Math.random() * 20 - 10)
      bars.push(Math.max(5, h))
   }
   return bars
}
</script>

<style scoped>
/* ============================================
   PAGE STRUCTURE
   ============================================ */
.portfolio-page {
  padding: 32px; max-width: 1600px; margin: 0 auto;
  display: flex; flex-direction: column; gap: 24px;
}

/* ============================================
   HERO & KPI
   ============================================ */
.hero-section { display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }
.hero-left h1 { font-size: 32px; font-weight: 700; color: #fff; margin: 0 0 12px 0; letter-spacing: -0.02em; }
.hero-meta { display: flex; gap: 8px; }
.meta-tag { font-size: 11px; padding: 4px 10px; background: rgba(255,255,255,0.05); border-radius: 6px; color: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.1); }
.risk-tag { color: #fbbf24; border-color: rgba(251, 191, 36, 0.3); background: rgba(251, 191, 36, 0.1); }
.hero-actions { display: flex; align-items: center; gap: 12px; }
.last-update { font-size: 11px; color: rgba(255,255,255,0.3); margin-right: 8px; }

.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.kpi-card {
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px;
  display: flex; flex-direction: column; gap: 12px; backdrop-filter: blur(10px);
}
.kpi-header { display: flex; justify-content: space-between; align-items: center; }
.kpi-label { font-size: 11px; text-transform: uppercase; color: rgba(255,255,255,0.4); font-weight: 600; letter-spacing: 0.05em; }
.kpi-trend { font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
.kpi-trend.positive { color: #4ade80; background: rgba(74, 222, 128, 0.1); }
.kpi-trend.negative { color: #f87171; background: rgba(248, 113, 113, 0.1); }
.kpi-value { font-size: 28px; font-weight: 700; font-family: var(--font-family-mono); letter-spacing: -0.03em; }
.kpi-sub { font-size: 11px; color: rgba(255,255,255,0.3); }

/* ============================================
   MAIN GRID
   ============================================ */
.dashboard-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 24px; align-items: start; }
.col-main { display: flex; flex-direction: column; gap: 24px; }

/* STATIC Side Column (Removed sticky) */
.col-side { 
  display: flex; flex-direction: column; gap: 24px; 
}

.card {
  background: rgba(30, 32, 40, 0.6); backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; overflow: hidden;
}
.card-header { padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { font-size: 14px; font-weight: 600; color: rgba(255,255,255,0.9); margin: 0; }
.card-body { padding: 20px; }
.card-body.p-0 { padding: 0; }
.icon-btn-sm { background: none; border: none; color: rgba(255,255,255,0.4); cursor: pointer; font-size: 16px; }
.icon-btn-sm:hover { color: #fff; }

/* ============================================
   TABLE
   ============================================ */
.table-container { overflow-x: auto; }
.asset-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.asset-table th { 
  text-align: left; padding: 12px 20px; color: rgba(255,255,255,0.4); font-weight: 500; font-size: 11px; text-transform: uppercase; border-bottom: 1px solid rgba(255,255,255,0.05);
}
.asset-table td { padding: 14px 20px; border-bottom: 1px solid rgba(255,255,255,0.03); color: rgba(255,255,255,0.9); transition: background 0.2s; cursor: pointer; }
.asset-table tr:hover td { background: rgba(255,255,255,0.03); }
.asset-table tr.active td { background: rgba(59, 130, 246, 0.1); border-bottom-color: rgba(59, 130, 246, 0.2); }
.asset-name-cell { display: flex; align-items: center; gap: 12px; }
.name-wrapper { display: flex; flex-direction: column; }
.symbol { font-weight: 700; font-size: 13px; color: #fff; }
.name { font-size: 11px; color: rgba(255,255,255,0.4); }
.color-dot { width: 8px; height: 8px; border-radius: 2px; }
.text-right { text-align: right; }
.mono { font-family: monospace; }
.font-bold { font-weight: 700; }
.text-muted { color: rgba(255,255,255,0.3); }

/* ============================================
   CORRELATION & MAP
   ============================================ */
.heatmap-container { display: flex; flex-direction: column; gap: 4px; overflow-x: auto; }
.heatmap-header-row { display: flex; gap: 4px; margin-bottom: 4px; }
.heatmap-empty-cell { width: 60px; }
.heatmap-col-header { width: 50px; text-align: center; font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.5); }
.heatmap-row { display: flex; gap: 4px; align-items: center; }
.heatmap-row-header { width: 60px; font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.5); }
.heatmap-cell { width: 50px; height: 40px; display: flex; align-items: center; justify-content: center; font-size: 11px; color: #fff; border-radius: 6px; transition: transform 0.2s; }
.heatmap-cell:hover { transform: scale(1.1); z-index: 2; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }

.market-map { display: flex; flex-wrap: wrap; gap: 2px; height: 180px; width: 100%; }
.map-tile { display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 4px; color: #fff; overflow: hidden; position: relative; transition: filter 0.2s; min-width: 60px; min-height: 60px; }
.map-tile:hover { filter: brightness(1.2); }
.tile-symbol { font-weight: 700; font-size: 12px; text-shadow: 0 1px 2px rgba(0,0,0,0.3); }
.tile-change { font-size: 10px; font-weight: 500; text-shadow: 0 1px 2px rgba(0,0,0,0.3); }

/* ============================================
   ASSET DETAIL & OPTIMIZER
   ============================================ */
.asset-title { display: flex; flex-direction: column; }
.asset-lg-symbol { font-size: 20px; font-weight: 700; color: #fff; }
.asset-lg-name { font-size: 12px; color: rgba(255,255,255,0.4); }
.badge-pill { font-size: 10px; background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px; }
.chart-controls { display: flex; gap: 8px; margin-bottom: 16px; }
.pill-btn { background: transparent; border: 1px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.5); padding: 4px 12px; border-radius: 20px; font-size: 11px; cursor: pointer; }
.pill-btn.active { background: #3b82f6; color: #fff; border-color: #3b82f6; }
.spacer { flex: 1; }
.mini-select { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: #fff; font-size: 11px; padding: 2px 8px; border-radius: 4px; }
.histogram-bars { height: 100px; display: flex; align-items: flex-end; gap: 4px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); }
.hist-bar { flex: 1; min-height: 2px; border-radius: 2px 2px 0 0; opacity: 0.8; }
.metrics-grid-sm { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px; }
.metric-box { background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; display: flex; flex-direction: column; gap: 2px; }
.metric-box label { font-size: 10px; color: rgba(255,255,255,0.4); text-transform: uppercase; }
.metric-box span { font-size: 13px; font-weight: 600; font-family: monospace; color: #fff; }
.divider { height: 1px; background: rgba(255,255,255,0.05); margin: 20px 0; }
.asset-actions { display: flex; gap: 10px; }

/* OPTIMIZER STYLES (FIXED: Flex & Sizes) */
.settings-form { display: flex; flex-direction: column; gap: 20px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.label-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; }
.form-label { font-size: 11px; font-weight: 700; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 0.05em; }
.label-hint, .val-display { font-size: 11px; color: rgba(255,255,255,0.4); font-family: monospace; }

.select-wrapper { position: relative; }
.form-control { width: 100%; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 10px 12px; color: #fff; border-radius: 8px; appearance: none; font-size: 13px; transition: all 0.2s; cursor: pointer; }
.form-control:hover { border-color: rgba(255,255,255,0.2); background: rgba(255,255,255,0.08); }
.form-control:focus { border-color: #3b82f6; outline: none; background: rgba(59, 130, 246, 0.1); }
.select-arrow { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); font-size: 10px; color: rgba(255,255,255,0.4); pointer-events: none; }

/* Fixed Range Inputs Sizing */
.range-inputs { display: flex; align-items: center; gap: 8px; width: 100%; }
.input-suffix { position: relative; flex: 1; display: flex; }
.input-box { 
  width: 100%; 
  min-width: 0; /* Важно: позволяет сжиматься */
  background: rgba(255,255,255,0.05); 
  border: 1px solid rgba(255,255,255,0.1); 
  color: #fff; 
  padding: 10px 24px 10px 10px; /* Справа место под % */
  border-radius: 8px; 
  text-align: right; 
  font-family: monospace; 
  font-size: 13px; 
  transition: all 0.2s; 
}
.input-box:focus { border-color: #3b82f6; outline: none; }
.suffix { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); font-size: 12px; color: rgba(255,255,255,0.4); pointer-events: none; }
.separator { font-size: 11px; color: rgba(255,255,255,0.3); flex-shrink: 0; }

/* Slider Fixes */
.slider-container { padding: 0 4px; }
.range-slider { width: 100%; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; -webkit-appearance: none; margin: 10px 0; cursor: pointer; }
.range-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 18px; height: 18px; background: #3b82f6; border-radius: 50%; border: 2px solid #1e2028; box-shadow: 0 0 0 1px rgba(59,130,246,0.5); cursor: grab; transition: transform 0.1s; }
.range-slider::-webkit-slider-thumb:active { transform: scale(1.1); cursor: grabbing; }
.range-scale { display: flex; justify-content: space-between; font-size: 10px; color: rgba(255,255,255,0.3); margin-top: -2px; padding: 0 2px; }
.center-tick { text-align: center; }

/* Checkbox */
.checkbox-container { display: flex; align-items: center; cursor: pointer; gap: 10px; font-size: 12px; color: rgba(255,255,255,0.8); user-select: none; }
.checkbox-container input { display: none; }
.checkmark { width: 18px; height: 18px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; transition: all 0.2s; flex-shrink: 0; }
.checkbox-container input:checked ~ .checkmark { background: #3b82f6; border-color: #3b82f6; }
.checkbox-container input:checked ~ .checkmark::after { content: "✓"; color: #fff; font-size: 12px; font-weight: bold; }
.checkbox-container:hover .checkmark { border-color: rgba(255,255,255,0.4); }

.mt-2 { margin-top: 8px; }

/* UTILITIES */
.text-green { color: #4ade80; }
.text-red { color: #f87171; }
.text-gradient-green { background: linear-gradient(135deg, #4ade80, #22c55e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-gradient-blue { background: linear-gradient(135deg, #60a5fa, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.w-full { width: 100%; }
.btn { padding: 8px 16px; border-radius: 8px; font-weight: 600; font-size: 13px; cursor: pointer; border: none; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s; }
.btn-primary { background: #3b82f6; color: #fff; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }
.btn-primary:hover { background: #2563eb; transform: translateY(-1px); }
.btn-outline { background: transparent; border: 1px solid rgba(255,255,255,0.2); color: #fff; }
.btn-outline:hover { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.4); }
.mini-search { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 6px; color: #fff; font-size: 12px; outline: none; }

@media (max-width: 1200px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .kpi-grid { grid-template-columns: 1fr 1fr; }
  .col-side { position: static; max-height: none; overflow: visible; }
}
</style>