<template>
  <div class="page-container">
    
    <!-- Header -->
    <div class="section-header">
      <div>
        <h1 class="section-title">Детальный анализ режимов</h1>
        <p class="section-subtitle">Метрики устойчивости, матрицы переходов и сценарное прогнозирование</p>
      </div>
      <div class="header-controls">
         <span class="date-badge">Data: 01.11.2025</span>
      </div>
    </div>

    <!-- 1. KEY METRICS CARDS (Upper Section) -->
    <div class="grid-3 mb-6">
        <!-- Stability -->
        <div class="card glass-panel regime-card border-blue">
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
        <div class="card glass-panel regime-card border-red">
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
        <div class="card glass-panel regime-card border-green">
            <div class="card-head">
                <span class="dot bg-green"></span>
                <h3>Состояние 2: Рост</h3>
            </div>
            <div class="card-body">
                <p class="desc">Периоды возрастающего тренда. Систематический рост стоимости облигаций с умеренными колебаниями.</p>
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

    <!-- 2. TRANSITION & STATIONARY ANALYSIS (Middle Section) -->
    <div class="grid-2 mb-6">
        
        <!-- Transition Matrix Heatmap -->
        <div class="card glass-panel">
            <div class="panel-header">
                <h3>Матрица переходов</h3>
            </div>
            <div class="heatmap-container">
                <div class="heatmap-grid">
                    <div class="h-label">From \ To</div>
                    <div class="h-col-header text-blue">Стаб</div>
                    <div class="h-col-header text-red">Падение</div>
                    <div class="h-col-header text-green">Рост</div>

                    <!-- Row 0 -->
                    <div class="h-row-header text-blue">Стаб</div>
                    <div class="h-cell" style="background: rgba(59, 130, 246, 0.96)">0.9632</div>
                    <div class="h-cell" style="background: rgba(248, 113, 113, 0.02)">0.0221</div>
                    <div class="h-cell" style="background: rgba(74, 222, 128, 0.01)">0.0147</div>

                    <!-- Row 1 -->
                    <div class="h-row-header text-red">Падение</div>
                    <div class="h-cell" style="background: rgba(59, 130, 246, 0.08)">0.0833</div>
                    <div class="h-cell" style="background: rgba(248, 113, 113, 0.66)">0.6667</div>
                    <div class="h-cell" style="background: rgba(74, 222, 128, 0.25)">0.2500</div>

                    <!-- Row 2 -->
                    <div class="h-row-header text-green">Рост</div>
                    <div class="h-cell" style="background: rgba(59, 130, 246, 0.07)">0.0784</div>
                    <div class="h-cell" style="background: rgba(248, 113, 113, 0.27)">0.2745</div>
                    <div class="h-cell" style="background: rgba(74, 222, 128, 0.64)">0.6471</div>
                </div>
                <div class="analysis-note mt-4">
                    <p>• <strong>Стабильность</strong> имеет наивысшую инерцию (0.96).<br>• Из <strong>Падения</strong> выход в Рост (25%) вероятнее, чем в Стабильность (8%).</p>
                </div>
            </div>
        </div>

        <!-- Stationary Distribution & Forecast -->
        <div class="card glass-panel flex-col">
            <div class="panel-header">
                <h3>Прогноз вероятностей</h3>
                <span class="sub">Начальное состояние: Рост</span>
            </div>
            
            <div class="forecast-table-wrapper">
                <table class="simple-table">
                    <thead>
                        <tr>
                            <th>Горизонт</th>
                            <th class="text-blue">P(Стаб)</th>
                            <th class="text-red">P(Пад)</th>
                            <th class="text-green">P(Рост)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>1 день</td><td>7.84%</td><td>27.45%</td><td>64.71%</td></tr>
                        <tr><td>5 дней</td><td>31.74%</td><td>35.18%</td><td>33.08%</td></tr>
                        <tr><td>10 дней</td><td>48.98%</td><td>26.79%</td><td>24.23%</td></tr>
                        <tr><td>20 дней</td><td>63.13%</td><td>19.51%</td><td>17.36%</td></tr>
                        <tr class="stationary">
                            <td>∞ (Стационарное состояние)</td>
                            <td>70.8%</td>
                            <td>15.6%</td>
                            <td>13.5%</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="chart-mini mt-4">
                <h4>Сходимость к стационарному состоянию</h4>
                <svg viewBox="0 0 400 100" class="svg-curves">
                     <!-- Simplified curves showing convergence -->
                     <path d="M0,90 Q50,80 100,50 T400,30" fill="none" stroke="#3b82f6" stroke-width="2"/>
                     <path d="M0,10 Q50,40 100,60 T400,85" fill="none" stroke="#4ade80" stroke-width="2"/>
                </svg>
            </div>
        </div>

    </div>

    <!-- 3. VISUALIZATION: HISTOGRAMS & COMPARISON (Bottom Section) -->
    <div class="grid-2 mb-6">
        
        <!-- Distribution Histograms -->
        <div class="card glass-panel">
            <div class="panel-header">
                <h3>Распределение доходностей по режимам</h3>
            </div>
            <div class="chart-container-rect">
                <svg viewBox="0 0 600 250" class="svg-chart">
                    <!-- Axes -->
                    <line x1="50" y1="220" x2="550" y2="220" stroke="#555" />
                    <line x1="300" y1="20" x2="300" y2="220" stroke="#444" stroke-dasharray="4" /> <!-- Zero line -->

                    <!-- Stability (Blue) - Narrow, Tall, Centered -->
                    <path d="M150,220 Q300,-100 450,220" fill="rgba(59, 130, 246, 0.2)" stroke="#3b82f6" stroke-width="2" />
                    
                    <!-- Decline (Red) - Wide, Shifted Left -->
                    <path d="M50,220 Q200,50 400,220" fill="rgba(248, 113, 113, 0.2)" stroke="#f87171" stroke-width="2" />
                    
                    <!-- Growth (Green) - Shifted Right -->
                    <path d="M200,220 Q380,50 500,220" fill="rgba(74, 222, 128, 0.2)" stroke="#4ade80" stroke-width="2" />
                    
                    <!-- Labels -->
                    <text x="310" y="30" fill="#3b82f6" font-size="10">Стабильность (Low σ)</text>
                    <text x="100" y="100" fill="#f87171" font-size="10">Падение (Negative μ)</text>
                    <text x="450" y="100" fill="#4ade80" font-size="10">Рост (Positive μ)</text>
                </svg>
            </div>
            <p class="chart-caption">Распределение изменений доходностей. Падение имеет "толстый хвост" слева.</p>
        </div>

        <!-- Comparative Bars -->
        <div class="card glass-panel">
             <div class="panel-header">
                <h3>Характеристики режимов</h3>
            </div>
             <div class="chart-container-rect">
                <svg viewBox="0 0 500 250" class="svg-chart">
                    <!-- Bar Groups -->
                    <!-- Stability -->
                    <rect x="50" y="150" width="40" height="50" fill="#3b82f6" opacity="0.8" /> <!-- Vol -->
                    <rect x="100" y="195" width="40" height="5" fill="#3b82f6" opacity="0.4" /> <!-- Ret -->
                    
                    <!-- Decline -->
                    <rect x="200" y="50" width="40" height="150" fill="#f87171" opacity="0.8" /> <!-- Vol High -->
                    <rect x="250" y="200" width="40" height="40" fill="#f87171" opacity="0.4" /> <!-- Ret Negative (shown as down visually or just diff color) -->
                    
                    <!-- Growth -->
                    <rect x="350" y="100" width="40" height="100" fill="#4ade80" opacity="0.8" /> <!-- Vol Med -->
                    <rect x="400" y="160" width="40" height="40" fill="#4ade80" opacity="0.4" /> <!-- Ret Positive -->

                    <!-- Labels -->
                    <text x="75" y="240" fill="#aaa" text-anchor="middle" font-size="12">Стабильность</text>
                    <text x="245" y="240" fill="#aaa" text-anchor="middle" font-size="12">Падение</text>
                    <text x="395" y="240" fill="#aaa" text-anchor="middle" font-size="12">Рост</text>

                    <!-- Legend -->
                    <rect x="350" y="20" width="10" height="10" fill="#fff" opacity="0.8" /> <text x="370" y="30" fill="#fff" font-size="10">Волатильность</text>
                    <rect x="350" y="40" width="10" height="10" fill="#fff" opacity="0.4" /> <text x="370" y="50" fill="#fff" font-size="10">Доходность (Abs)</text>
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
.page-container { padding: 32px; max-width: 1400px; margin: 0 auto; color: #fff; padding-bottom: 80px; }

/* Headers */
.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 32px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 20px; }
.section-title { font-size: 28px; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
.section-subtitle { color: rgba(255,255,255,0.5); margin: 6px 0 0 0; }
.date-badge { background: rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 6px; font-family: monospace; font-size: 12px; }

/* Grids */
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }

/* Cards */
.card { background: rgba(20, 22, 28, 0.6); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 24px; height: 100%; display: flex; flex-direction: column; }
.panel-header { margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 12px; }
.panel-header h3 { margin: 0; font-size: 16px; font-weight: 600; }
.sub { font-size: 12px; color: rgba(255,255,255,0.4); display: block; margin-top: 4px; }

/* Regime Cards */
.regime-card.border-blue { border-top: 3px solid #3b82f6; }
.regime-card.border-red { border-top: 3px solid #f87171; }
.regime-card.border-green { border-top: 3px solid #4ade80; }

.card-head { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.card-head h3 { margin: 0; font-size: 16px; font-weight: 700; }
.desc { font-size: 13px; color: rgba(255,255,255,0.6); line-height: 1.5; margin-bottom: 20px; height: 40px; }

.metrics-table { display: flex; flex-direction: column; gap: 10px; }
.m-row { display: flex; justify-content: space-between; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 6px; }
.m-row span { color: rgba(255,255,255,0.5); }
.m-row strong { font-family: monospace; font-size: 14px; }

/* Heatmap */
.heatmap-container { display: flex; flex-direction: column; align-items: center; }
.heatmap-grid { display: grid; grid-template-columns: 80px repeat(3, 1fr); gap: 4px; width: 100%; }
.h-label { font-size: 11px; color: rgba(255,255,255,0.3); grid-column: 1; grid-row: 1; display: flex; align-items: center; justify-content: center; }
.h-col-header { text-align: center; font-size: 12px; font-weight: 700; padding: 8px; }
.h-row-header { display: flex; align-items: center; justify-content: flex-end; padding-right: 12px; font-size: 12px; font-weight: 700; }
.h-cell { display: flex; align-items: center; justify-content: center; height: 50px; border-radius: 6px; font-family: monospace; font-weight: 700; color: #fff; font-size: 14px; text-shadow: 0 1px 2px rgba(0,0,0,0.5); }

/* Analysis Note */
.analysis-note { background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px; font-size: 12px; color: rgba(255,255,255,0.6); line-height: 1.5; width: 100%; box-sizing: border-box; }

/* Forecast Table */
.forecast-table-wrapper { width: 100%; overflow-x: auto; }
.simple-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.simple-table th { text-align: left; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); opacity: 0.8; }
.simple-table td { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); font-family: monospace; }
.stationary td { font-weight: 700; color: #fbbf24; border-top: 2px solid rgba(255,255,255,0.1); }

/* SVG Charts */
.chart-container-rect { width: 100%; height: 250px; }
.svg-chart { width: 100%; height: 100%; }
.chart-caption { font-size: 12px; color: rgba(255,255,255,0.4); text-align: center; margin-top: 12px; font-style: italic; }

/* Utility */
.dot { width: 10px; height: 10px; border-radius: 50%; }
.bg-blue { background: #3b82f6; } .text-blue { color: #3b82f6; }
.bg-red { background: #f87171; } .text-red { color: #f87171; }
.bg-green { background: #4ade80; } .text-green { color: #4ade80; }
.mt-4 { margin-top: 16px; }
.mb-6 { margin-bottom: 24px; }
</style>

