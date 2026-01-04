<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Детальный анализ режимов</h1>
        <p class="section-subtitle">Метрики устойчивости, матрицы переходов и сценарное прогнозирование</p>
      </div>
      <div class="header-actions">
         <div class="glass-pill status-pill">
            <span class="status-label text-muted">Data: <b class="text-white">01.11.2025</b></span>
         </div>
      </div>
    </div>

    <!-- 1. KEY METRICS CARDS -->
    <div class="grid-3 mb-6">
        <!-- Stability -->
        <div class="glass-card regime-card border-blue">
            <div class="card-head">
                <span class="dot bg-blue"></span>
                <h3>Состояние 0: Стабильность</h3>
            </div>
            <div class="card-body">
                <p class="desc">Динамическое равновесие без ярко выраженного направления. Рынок стабилизируется, волатильность минимальна.</p>
                <div class="metrics-table">
                    <div class="m-row"><span>Количество дней</span> <strong>272</strong></div>
                    <div class="m-row"><span>Доля периода</span> <strong>70.8%</strong></div>
                    <div class="m-row"><span>Ср. доходность</span> <strong class="text-blue">+0.005%</strong></div>
                    <div class="m-row"><span>Волатильность</span> <strong>0.375%</strong></div>
                    <div class="m-row"><span>Устойчивость</span> <strong>0.9632</strong></div>
                    <div class="m-row"><span>Ожид. длительность</span> <strong>27.2 дня</strong></div>
                </div>
            </div>
        </div>

        <!-- Decline -->
        <div class="glass-card regime-card border-red">
            <div class="card-head">
                <span class="dot bg-red"></span>
                <h3>Состояние 1: Падение</h3>
            </div>
            <div class="card-body">
                <p class="desc">Фаза понижательного тренда с высокой волатильностью. "Липкое" состояние с короткими отскоками.</p>
                <div class="metrics-table">
                    <div class="m-row"><span>Количество дней</span> <strong>60</strong></div>
                    <div class="m-row"><span>Доля периода</span> <strong>15.6%</strong></div>
                    <div class="m-row"><span>Ср. доходность</span> <strong class="text-red">-0.039%</strong></div>
                    <div class="m-row"><span>Волатильность</span> <strong>0.652%</strong></div>
                    <div class="m-row"><span>Устойчивость</span> <strong>0.6667</strong></div>
                    <div class="m-row"><span>Ожид. длительность</span> <strong>3.0 дня</strong></div>
                </div>
            </div>
        </div>

        <!-- Growth -->
        <div class="glass-card regime-card border-green">
            <div class="card-head">
                <span class="dot bg-green"></span>
                <h3>Состояние 2: Рост</h3>
            </div>
            <div class="card-body">
                <p class="desc">Периоды возрастающего тренда. Систематический рост стоимости активов с умеренными колебаниями.</p>
                <div class="metrics-table">
                    <div class="m-row"><span>Количество дней</span> <strong>52</strong></div>
                    <div class="m-row"><span>Доля периода</span> <strong>13.5%</strong></div>
                    <div class="m-row"><span>Ср. доходность</span> <strong class="text-green">+0.036%</strong></div>
                    <div class="m-row"><span>Волатильность</span> <strong>0.479%</strong></div>
                    <div class="m-row"><span>Устойчивость</span> <strong>0.6471</strong></div>
                    <div class="m-row"><span>Ожид. длительность</span> <strong>2.8 дня</strong></div>
                </div>
            </div>
        </div>
    </div>

    <!-- 2. TRANSITION & STATIONARY ANALYSIS -->
    <div class="grid-2 mb-6">
        
        <!-- Transition Matrix Heatmap -->
        <div class="glass-card panel">
            <div class="panel-header">
                <h3>Матрица переходов (Transition Matrix)</h3>
            </div>
            <div class="heatmap-container">
                <div class="heatmap-grid">
                    <div class="h-label">From \ To</div>
                    <div class="h-col-header text-blue">Стаб</div>
                    <div class="h-col-header text-red">Падение</div>
                    <div class="h-col-header text-green">Рост</div>

                    <!-- Row 0 -->
                    <div class="h-row-header text-blue">Стаб</div>
                    <div class="h-cell" style="background: rgba(59, 130, 246, 0.8)">0.96</div>
                    <div class="h-cell" style="background: rgba(248, 113, 113, 0.05)">0.02</div>
                    <div class="h-cell" style="background: rgba(74, 222, 128, 0.05)">0.01</div>

                    <!-- Row 1 -->
                    <div class="h-row-header text-red">Падение</div>
                    <div class="h-cell" style="background: rgba(59, 130, 246, 0.1)">0.08</div>
                    <div class="h-cell" style="background: rgba(248, 113, 113, 0.6)">0.67</div>
                    <div class="h-cell" style="background: rgba(74, 222, 128, 0.2)">0.25</div>

                    <!-- Row 2 -->
                    <div class="h-row-header text-green">Рост</div>
                    <div class="h-cell" style="background: rgba(59, 130, 246, 0.1)">0.08</div>
                    <div class="h-cell" style="background: rgba(248, 113, 113, 0.2)">0.27</div>
                    <div class="h-cell" style="background: rgba(74, 222, 128, 0.6)">0.65</div>
                </div>
                <div class="analysis-note mt-4">
                    <p>• <strong>Стабильность</strong> имеет наивысшую инерцию (0.96).<br>• Из <strong>Падения</strong> выход в Рост (25%) вероятнее, чем в Стабильность (8%).</p>
                </div>
            </div>
        </div>

        <!-- Stationary Distribution & Forecast -->
        <div class="glass-card panel flex-col">
            <div class="panel-header">
                <h3>Прогноз вероятностей</h3>
                <span class="sub-label">Начальное состояние: <b>Рост</b></span>
            </div>
            
            <div class="table-wrapper">
                <table class="glass-table">
                    <thead>
                        <tr>
                            <th class="text-left pl-2">Горизонт</th>
                            <th class="text-blue text-right">P(Стаб)</th>
                            <th class="text-red text-right">P(Пад)</th>
                            <th class="text-green text-right">P(Рост)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td class="pl-2">1 день</td><td class="text-right">7.8%</td><td class="text-right">27.5%</td><td class="text-right">64.7%</td></tr>
                        <tr><td class="pl-2">5 дней</td><td class="text-right">31.7%</td><td class="text-right">35.2%</td><td class="text-right">33.1%</td></tr>
                        <tr><td class="pl-2">10 дней</td><td class="text-right">49.0%</td><td class="text-right">26.8%</td><td class="text-right">24.2%</td></tr>
                        <tr class="stationary">
                            <td class="pl-2 text-orange font-bold">∞ (Long-run)</td>
                            <td class="text-right font-bold text-orange">70.8%</td>
                            <td class="text-right font-bold text-orange">15.6%</td>
                            <td class="text-right font-bold text-orange">13.5%</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="chart-mini mt-4">
                <div class="chart-label-sm">Сходимость к стационарному состоянию</div>
                <svg viewBox="0 0 400 60" class="svg-curves">
                     <!-- Simplified curves showing convergence -->
                     <path d="M0,50 Q100,45 200,30 T400,10" fill="none" stroke="#3b82f6" stroke-width="2"/>
                     <path d="M0,10 Q100,20 200,30 T400,45" fill="none" stroke="#4ade80" stroke-width="2"/>
                     <line x1="0" y1="10" x2="400" y2="10" stroke="rgba(255,255,255,0.1)" stroke-dasharray="4"/>
                     <line x1="0" y1="50" x2="400" y2="50" stroke="rgba(255,255,255,0.1)" stroke-dasharray="4"/>
                </svg>
            </div>
        </div>

    </div>

    <!-- 3. VISUALIZATION: HISTOGRAMS & COMPARISON -->
    <div class="grid-2 mb-6">
        
        <!-- Distribution Histograms -->
        <div class="glass-card panel">
            <div class="panel-header">
                <h3>Распределение доходностей по режимам</h3>
            </div>
            <div class="chart-container-rect">
                <svg viewBox="0 0 600 250" class="svg-chart">
                    <!-- Axes -->
                    <line x1="50" y1="220" x2="550" y2="220" stroke="rgba(255,255,255,0.1)" />
                    <line x1="300" y1="20" x2="300" y2="220" stroke="rgba(255,255,255,0.1)" stroke-dasharray="4" /> <!-- Zero line -->

                    <!-- Stability (Blue) - Narrow, Tall, Centered -->
                    <path d="M150,220 Q300,-100 450,220" fill="rgba(59, 130, 246, 0.1)" stroke="#3b82f6" stroke-width="2" />
                    
                    <!-- Decline (Red) - Wide, Shifted Left -->
                    <path d="M50,220 Q200,50 400,220" fill="rgba(248, 113, 113, 0.1)" stroke="#f87171" stroke-width="2" />
                    
                    <!-- Growth (Green) - Shifted Right -->
                    <path d="M200,220 Q380,50 500,220" fill="rgba(74, 222, 128, 0.1)" stroke="#4ade80" stroke-width="2" />
                    
                    <!-- Labels -->
                    <text x="310" y="30" fill="#3b82f6" font-size="10" font-weight="600">Стабильность (Low σ)</text>
                    <text x="100" y="100" fill="#f87171" font-size="10" font-weight="600">Падение (Neg μ)</text>
                    <text x="450" y="100" fill="#4ade80" font-size="10" font-weight="600">Рост (Pos μ)</text>
                </svg>
            </div>
            <p class="chart-caption">Распределение изменений доходностей. Режим «Падение» имеет "толстый хвост" слева.</p>
        </div>

        <!-- Comparative Bars -->
        <div class="glass-card panel">
             <div class="panel-header">
                <h3>Характеристики режимов (Vol vs Ret)</h3>
            </div>
             <div class="chart-container-rect">
                <svg viewBox="0 0 500 250" class="svg-chart">
                    <!-- Bar Groups -->
                    <!-- Stability -->
                    <rect x="50" y="150" width="40" height="50" fill="#3b82f6" opacity="0.8" rx="4" /> <!-- Vol -->
                    <rect x="100" y="195" width="40" height="5" fill="#3b82f6" opacity="0.3" rx="4" /> <!-- Ret -->
                    
                    <!-- Decline -->
                    <rect x="200" y="50" width="40" height="150" fill="#f87171" opacity="0.8" rx="4" /> <!-- Vol High -->
                    <rect x="250" y="200" width="40" height="40" fill="#f87171" opacity="0.3" rx="4" /> <!-- Ret Negative (down) -->
                    
                    <!-- Growth -->
                    <rect x="350" y="100" width="40" height="100" fill="#4ade80" opacity="0.8" rx="4" /> <!-- Vol Med -->
                    <rect x="400" y="160" width="40" height="40" fill="#4ade80" opacity="0.3" rx="4" /> <!-- Ret Positive -->

                    <!-- Labels -->
                    <text x="95" y="240" fill="rgba(255,255,255,0.6)" text-anchor="middle" font-size="12">Стабильность</text>
                    <text x="245" y="240" fill="rgba(255,255,255,0.6)" text-anchor="middle" font-size="12">Падение</text>
                    <text x="395" y="240" fill="rgba(255,255,255,0.6)" text-anchor="middle" font-size="12">Рост</text>

                    <!-- Legend -->
                    <rect x="340" y="20" width="10" height="10" fill="#fff" opacity="0.8" rx="2" /> <text x="360" y="30" fill="#fff" font-size="10">Волатильность (σ)</text>
                    <rect x="340" y="40" width="10" height="10" fill="#fff" opacity="0.3" rx="2" /> <text x="360" y="50" fill="#fff" font-size="10">Доходность (|μ|)</text>
                </svg>
            </div>
        </div>

    </div>
    
  </div>
</template>

<script setup lang="ts">
// Logic is mostly static visualization of the report data
// In a real app, this data would come from the backend HMM result object
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.page-container {
  display: flex; flex-direction: column; gap: 24px; padding: 24px 32px;
  max-width: 1400px; margin: 0 auto; height: 100%;
}

.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px; }
.section-title { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }

/* ============================================
   GLASS COMPONENTS
   ============================================ */
.glass-card {
  background: rgba(30, 32, 40, 0.4); backdrop-filter: blur(30px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px;
  box-shadow: 0 20px 40px -10px rgba(0,0,0,0.4);
  padding: 24px;
}

.glass-pill {
  display: flex; align-items: center; gap: 8px; padding: 4px 12px;
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 99px; height: 36px;
}

/* Grids */
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.grid-2 { display: grid; grid-template-columns: 3fr 2fr; gap: 24px; }

/* Panels */
.panel { display: flex; flex-direction: column; }
.panel-header { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
.panel-header h3 { margin: 0; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: rgba(255,255,255,0.8); }
.sub-label { font-size: 11px; color: rgba(255,255,255,0.5); }

/* Regime Cards */
.regime-card { position: relative; border-top: 2px solid transparent; transition: transform 0.2s; }
.regime-card:hover { transform: translateY(-2px); background: rgba(30, 32, 40, 0.6); }
.regime-card.border-blue { border-color: #3b82f6; }
.regime-card.border-red { border-color: #f87171; }
.regime-card.border-green { border-color: #4ade80; }

.card-head { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.card-head h3 { margin: 0; font-size: 16px; font-weight: 700; color: #fff; }
.desc { font-size: 12px; color: rgba(255,255,255,0.6); line-height: 1.5; margin-bottom: 20px; height: 36px; }

/* Metrics Table */
.metrics-table { display: flex; flex-direction: column; gap: 8px; }
.m-row { display: flex; justify-content: space-between; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 6px; }
.m-row span { color: rgba(255,255,255,0.5); font-weight: 500; }
.m-row strong { font-family: "SF Mono", monospace; color: #fff; }

/* Heatmap */
.heatmap-container { display: flex; flex-direction: column; align-items: center; }
.heatmap-grid { display: grid; grid-template-columns: 60px repeat(3, 1fr); gap: 4px; width: 100%; }
.h-label { font-size: 10px; color: rgba(255,255,255,0.3); grid-column: 1; grid-row: 1; display: flex; align-items: center; justify-content: center; }
.h-col-header { text-align: center; font-size: 11px; font-weight: 700; padding: 8px; text-transform: uppercase; }
.h-row-header { display: flex; align-items: center; justify-content: flex-end; padding-right: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.h-cell { display: flex; align-items: center; justify-content: center; height: 44px; border-radius: 6px; font-family: "SF Mono", monospace; font-weight: 700; color: #fff; font-size: 13px; text-shadow: 0 1px 2px rgba(0,0,0,0.5); }

/* Analysis Note */
.analysis-note { background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px; font-size: 12px; color: rgba(255,255,255,0.6); line-height: 1.5; width: 100%; margin-top: 16px; border: 1px solid rgba(255,255,255,0.05); }

/* Forecast Table */
.table-wrapper { width: 100%; overflow-x: auto; }
.glass-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.glass-table th { padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); opacity: 0.8; font-weight: 600; }
.glass-table td { padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-family: "SF Mono", monospace; color: #fff; }
.stationary td { font-weight: 700; border-top: 1px solid rgba(255,255,255,0.1); border-bottom: none; padding-top: 16px; }

/* Mini Chart */
.chart-mini { background: rgba(0,0,0,0.2); border-radius: 12px; padding: 12px; border: 1px solid rgba(255,255,255,0.05); margin-top: auto; }
.chart-label-sm { font-size: 10px; color: rgba(255,255,255,0.4); margin-bottom: 4px; text-transform: uppercase; }
.svg-curves { width: 100%; height: 60px; }

/* SVG Charts */
.chart-container-rect { width: 100%; height: 250px; position: relative; }
.svg-chart { width: 100%; height: 100%; }
.chart-caption { font-size: 11px; color: rgba(255,255,255,0.4); text-align: center; margin-top: 8px; font-style: italic; }

/* Utility */
.dot { width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 8px currentColor; }
.bg-blue { background: #3b82f6; color: #3b82f6; } .text-blue { color: #3b82f6; }
.bg-red { background: #f87171; color: #f87171; } .text-red { color: #f87171; }
.bg-green { background: #4ade80; color: #4ade80; } .text-green { color: #4ade80; }
.text-orange { color: #fbbf24; }
.text-white { color: #fff; }
.text-muted { color: rgba(255,255,255,0.4); }
.text-right { text-align: right; }
.text-left { text-align: left; }
.pl-2 { padding-left: 8px; }
.font-bold { font-weight: 700; }
.mb-6 { margin-bottom: 24px; }
.flex-col { display: flex; flex-direction: column; }

@media (max-width: 1200px) {
  .grid-3 { grid-template-columns: 1fr; }
  .grid-2 { grid-template-columns: 1fr; }
}
</style>