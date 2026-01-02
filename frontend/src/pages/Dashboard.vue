<!-- src/views/SummaryView.vue -->
<template>
  <div class="page-container">
    
    <!-- Header и KPI - без изменений -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Обзор Портфеля</h1>
        <p class="section-subtitle">Сводная аналитика, P&L и анализ распределения доходности</p>
      </div>
      <div class="header-actions">
         <span class="last-update">Обновлено: {{ lastUpdate }}</span>
         <button class="btn btn-outline" @click="refreshData">
            <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
            Обновить
         </button>
      </div>
    </div>

    <!-- 1. Top KPIs -->
    <div class="kpi-cards-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total Net Asset Value</div>
        <div class="kpi-value text-gradient-green">$1,245,230</div>
        <div class="kpi-change positive">↗ +$45,230 (YTD)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Risk (VaR 99%)</div>
        <div class="kpi-value text-red">-$67,500</div>
        <div class="kpi-change">2.8% от капитала</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Sharpe Ratio</div>
        <div class="kpi-value text-gradient-blue">1.85</div>
        <div class="kpi-change">Top 15% percentile</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Stress Test Impact</div>
        <div class="kpi-value text-orange">-18.5%</div>
        <div class="kpi-change">Сценарий: Black Swan</div>
      </div>
    </div>

    <!-- 2. Charts Row -->
    <div class="charts-grid">
        <div class="card glass-panel col-span-2">
            <div class="panel-header">
                <h3>Динамика Портфеля (Total Return)</h3>
                <div class="chart-legend">
                    <span class="legend-item"><span class="dot bg-green"></span> Портфель</span>
                    <span class="legend-item"><span class="dot bg-muted"></span> Benchmark (SPY)</span>
                </div>
            </div>
            <div class="chart-container">
                <svg viewBox="0 0 800 200" class="line-chart" preserveAspectRatio="none">
                    <line x1="0" y1="150" x2="800" y2="150" stroke="rgba(255,255,255,0.05)" />
                    <line x1="0" y1="100" x2="800" y2="100" stroke="rgba(255,255,255,0.05)" />
                    <line x1="0" y1="50" x2="800" y2="50" stroke="rgba(255,255,255,0.05)" />
                    <path d="M0,150 C100,140 200,120 300,130 S500,100 800,80" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="2" stroke-dasharray="4" />
                    <defs>
                        <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
                            <stop offset="0%" stop-color="#4ade80" />
                            <stop offset="100%" stop-color="#3b82f6" />
                        </linearGradient>
                        <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="rgba(74, 222, 128, 0.2)" />
                            <stop offset="100%" stop-color="rgba(74, 222, 128, 0)" />
                        </linearGradient>
                    </defs>
                    <path d="M0,150 C100,130 200,140 300,100 S500,80 600,60 S700,40 800,20" fill="none" stroke="url(#lineGrad)" stroke-width="3" />
                    <path d="M0,150 C100,130 200,140 300,100 S500,80 600,60 S700,40 800,20 V200 H0 Z" fill="url(#areaGrad)" stroke="none" />
                </svg>
                <div class="chart-labels">
                    <span>Jan</span><span>Mar</span><span>May</span><span>Jul</span><span>Sep</span><span>Nov</span><span>Now</span>
                </div>
            </div>
        </div>

        <div class="card glass-panel">
            <div class="panel-header">
                <h3>Распределение Доходности</h3>
                <div class="chart-legend">
                   <span class="legend-item"><span class="dot bg-blue"></span> Факт</span>
                   <span class="legend-item"><span class="line-sample bg-orange"></span> Норм.</span>
                </div>
            </div>
            <div class="histogram-container">
                <div class="hist-chart-wrapper">
                    <div class="hist-bars">
                        <div v-for="(bar, i) in histogramData" :key="i" class="h-bar-col">
                            <div class="h-bar" :style="{ height: bar.height + '%' }"></div>
                        </div>
                    </div>
                    <svg class="normal-curve" viewBox="0 0 200 100" preserveAspectRatio="none">
                         <path d="M0,95 Q50,95 80,40 Q100,5 120,40 Q150,95 200,95" fill="none" stroke="#fbbf24" stroke-width="2" />
                         <line x1="100" y1="5" x2="100" y2="100" stroke="rgba(255,255,255,0.2)" stroke-dasharray="2" />
                    </svg>
                </div>
                <div class="hist-axis">
                    <span>-3σ</span><span>-2σ</span><span>-1σ</span><span class="text-white">μ</span><span>+1σ</span><span>+2σ</span><span>+3σ</span>
                </div>
                <div class="hist-stats">
                    <div class="h-stat"><span class="lbl">Kurtosis</span><span class="val">3.42 (Fat Tails)</span></div>
                    <div class="h-stat"><span class="lbl">Skewness</span><span class="val text-red">-0.85 (Neg)</span></div>
                </div>
            </div>
        </div>
    </div>

    <!-- 3. Detailed Metrics Integration Grid -->
    <div class="details-grid">
        
        <!-- Asset Allocation Summary -->
        <div class="card glass-panel">
            <div class="panel-header-simple">
                 <h3>Аллокация Активов</h3>
            </div>
            <div class="allocation-content">
                <div class="allocation-list">
                    <div class="alloc-row">
                        <div class="alloc-info">
                            <span class="dot bg-blue"></span> <span>Акции (Equities)</span>
                        </div>
                        <span class="mono">45%</span>
                    </div>
                    <div class="alloc-row">
                        <div class="alloc-info">
                            <span class="dot bg-red"></span> <span>Облигации (Fixed)</span>
                        </div>
                        <span class="mono">30%</span>
                    </div>
                    <div class="alloc-row">
                        <div class="alloc-info">
                            <span class="dot bg-orange"></span> <span>Commodities</span>
                        </div>
                        <span class="mono">15%</span>
                    </div>
                    <div class="alloc-row">
                        <div class="alloc-info">
                            <span class="dot bg-green"></span> <span>Crypto / Alt</span>
                        </div>
                        <span class="mono">10%</span>
                    </div>
                </div>
                <!-- Simple Progress Stack -->
                <div class="progress-stack-wrapper">
                    <div class="progress-stack">
                        <div style="width: 45%; background: #3b82f6"></div>
                        <div style="width: 30%; background: #ef4444"></div>
                        <div style="width: 15%; background: #fbbf24"></div>
                        <div style="width: 10%; background: #4ade80"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Top Risks -->
        <div class="card glass-panel">
            <div class="panel-header-simple">
                <h3>Риск-концентрация (Top VaR)</h3>
            </div>
            <div class="table-container">
                <table class="mini-table">
                    <thead>
                        <tr><th>Актив</th><th>Exp.</th><th>VaR Contrib.</th></tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><span class="font-bold">SPY</span></td>
                            <td>40%</td>
                            <td class="text-red">-$27,000</td>
                        </tr>
                        <tr>
                            <td><span class="font-bold">QQQ</span></td>
                            <td>30%</td>
                            <td class="text-red">-$21,000</td>
                        </tr>
                        <tr>
                            <td><span class="font-bold">TLT</span></td>
                            <td>15%</td>
                            <td class="text-orange">-$7,500</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Stress Tests -->
        <div class="card glass-panel">
             <div class="panel-header-simple">
                <h3>Результаты Стресс-тестов</h3>
            </div>
            <div class="stress-mini-list">
                <div class="stress-row">
                    <span>📉 Кризис 2008</span>
                    <span class="text-red font-bold">-25.0%</span>
                </div>
                <div class="stress-row">
                    <span>🔥 Рост ставок</span>
                    <span class="text-orange font-bold">-12.5%</span>
                </div>
                <div class="stress-row">
                    <span>📊 VIX Spike</span>
                    <span class="text-orange font-bold">-8.2%</span>
                </div>
            </div>
        </div>
        
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const lastUpdate = ref(new Date().toLocaleTimeString())

const histogramData = ref([
    { height: 5 }, { height: 8 }, { height: 12 }, { height: 25 }, 
    { height: 45 }, { height: 70 }, { height: 90 }, { height: 100 }, 
    { height: 85 }, { height: 60 }, { height: 30 }, { height: 15 }, 
    { height: 10 }, { height: 8 }, { height: 6 }
])

const refreshData = () => {
    lastUpdate.value = new Date().toLocaleTimeString()
}
</script>

<style scoped>
/* ============================================
   LAYOUT
   ============================================ */
.page-container {
  display: flex; flex-direction: column; gap: 24px; padding: 28px;
  max-width: 1400px; margin: 0 auto;
}

.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px; }
.section-title { font-size: 28px; font-weight: 700; margin: 0; color: #fff; letter-spacing: -0.02em; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }

.header-actions { display: flex; align-items: center; gap: 12px; }
.last-update { font-size: 11px; color: rgba(255,255,255,0.3); }

/* ============================================
   GLASS CARD ENGINE
   ============================================ */
.card, .kpi-card {
  position: relative; border-radius: 18px; overflow: hidden;
  background: rgba(20, 22, 28, 0.25);
  backdrop-filter: blur(34px) saturate(185%);
  -webkit-backdrop-filter: blur(34px) saturate(185%);
  box-shadow: 0 18px 40px -18px rgba(0,0,0,0.55), inset 0 0 0 1px rgba(255, 255, 255, 0.1);
}
.glass-panel { padding: 20px; display: flex; flex-direction: column; }

/* Panel Headers */
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.panel-header-simple { margin-bottom: 20px; } /* Increased margin for better spacing */
.panel-header h3, .panel-header-simple h3 { margin: 0; font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.04em; }

/* ============================================
   KPI GRID
   ============================================ */
.kpi-cards-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.kpi-card { padding: 18px; display: flex; flex-direction: column; justify-content: space-between; min-height: 90px; }
.kpi-label { font-size: 10px; text-transform: uppercase; color: rgba(255,255,255,0.5); font-weight: 600; margin-bottom: 8px; }
.kpi-value { font-size: 24px; font-weight: 700; font-family: var(--font-family-mono); line-height: 1; color: #fff; }
.kpi-change { font-size: 11px; margin-top: 6px; color: rgba(255,255,255,0.4); }
.kpi-change.positive { color: #4ade80; }

/* ============================================
   CHARTS GRID
   ============================================ */
.charts-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 18px; }
.col-span-2 { grid-column: span 1; } 

.chart-container { height: 220px; width: 100%; position: relative; display: flex; flex-direction: column; justify-content: flex-end; }
.line-chart { width: 100%; height: 100%; overflow: visible; }
.chart-labels { display: flex; justify-content: space-between; margin-top: 8px; font-size: 10px; color: rgba(255,255,255,0.3); padding: 0 10px; }

.chart-legend { display: flex; gap: 12px; font-size: 11px; color: rgba(255,255,255,0.6); }
.legend-item { display: flex; align-items: center; gap: 6px; }
.dot { width: 6px; height: 6px; border-radius: 50%; }
.line-sample { width: 12px; height: 2px; }

/* Histogram Styles */
.histogram-container { height: 220px; display: flex; flex-direction: column; }
.hist-chart-wrapper { position: relative; flex-grow: 1; display: flex; align-items: flex-end; padding-bottom: 4px; border-bottom: 1px solid rgba(255,255,255,0.1); }
.hist-bars { display: flex; width: 100%; height: 100%; align-items: flex-end; justify-content: space-between; gap: 2px; padding: 0 10px; }
.h-bar-col { flex: 1; display: flex; align-items: flex-end; justify-content: center; height: 100%; }
.h-bar { width: 80%; background: rgba(59, 130, 246, 0.4); border-top-left-radius: 2px; border-top-right-radius: 2px; transition: height 0.5s ease; }
.h-bar:hover { background: rgba(59, 130, 246, 0.8); }

.normal-curve { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2; }
.hist-axis { display: flex; justify-content: space-between; font-size: 10px; color: rgba(255,255,255,0.3); margin-top: 6px; padding: 0 10px; }
.hist-stats { display: flex; justify-content: space-between; margin-top: 12px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px; }
.h-stat { display: flex; flex-direction: column; gap: 2px; }
.h-stat .lbl { font-size: 10px; color: rgba(255,255,255,0.5); }
.h-stat .val { font-size: 12px; font-family: var(--font-family-mono); }

/* ============================================
   DETAILS GRID
   ============================================ */
.details-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }

/* Allocations */
.allocation-content { display: flex; flex-direction: column; height: 100%; justify-content: space-between; }
.allocation-list { display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px; } /* Corrected Spacing */
.alloc-row { display: flex; justify-content: space-between; font-size: 12px; color: rgba(255,255,255,0.8); }
.alloc-info { display: flex; align-items: center; gap: 8px; }
.progress-stack-wrapper { margin-top: auto; }
.progress-stack { display: flex; height: 6px; width: 100%; border-radius: 3px; overflow: hidden; gap: 1px; }

/* Mini Tables & Lists */
.table-container { flex-grow: 1; }
.mini-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.mini-table th { text-align: left; color: rgba(255,255,255,0.4); font-weight: 500; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); }
.mini-table td { padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); color: #fff; } /* Increased Padding */
.mini-table td:last-child { text-align: right; font-family: var(--font-family-mono); }

.stress-mini-list { display: flex; flex-direction: column; gap: 12px; } /* Increased Gap */
.stress-row { display: flex; justify-content: space-between; font-size: 12px; color: rgba(255,255,255,0.8); border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 10px; }
.stress-row:last-child { border-bottom: none; }

/* ============================================
   UTILITIES
   ============================================ */
.btn { display: flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; border: none; color: white; transition: all 0.2s; }
.btn-outline { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); }
.btn-outline:hover { background: rgba(255,255,255,0.1); }

.text-gradient-green { background: linear-gradient(135deg, #4ade80, #22c55e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-gradient-blue { background: linear-gradient(135deg, #60a5fa, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-red { color: #f87171; }
.text-orange { color: #fbbf24; }
.text-white { color: #fff; }
.bg-green { background: #4ade80; }
.bg-blue { background: #3b82f6; }
.bg-red { background: #ef4444; }
.bg-orange { background: #fbbf24; }
.bg-muted { background: rgba(255,255,255,0.3); }
.font-bold { font-weight: 700; }
.mono { font-family: var(--font-family-mono); }

@media (max-width: 1200px) {
  .charts-grid, .details-grid { grid-template-columns: 1fr; }
  .kpi-cards-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>