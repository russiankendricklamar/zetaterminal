<template>
  <div class="page-container">
    
    <!-- Header & Controls -->
    <div class="section-header">
      <div>
        <h1 class="section-title">Анализ кривых доходности</h1>
        <p class="section-subtitle">Динамика рынка и стресс-сценарии</p>
      </div>
      
      <div class="header-controls">
        <button class="btn-refresh" @click="generateData">
             <span class="icon">↻</span> Обновить
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="analysis-grid">
        
        <!-- Left Column: Charts -->
        <div class="charts-column">
            
            <!-- Chart 1: Daily Changes (Volatile "Spaghetti") -->
            <div class="card glass-panel chart-container">
                <div class="panel-header">
                    <h3>Ежедневные изменения (%)</h3>
                    <div class="legend">
                         <span class="l-item faded"><span class="dot bg-gray"></span> Кластеры волатильности</span>
                         <span class="l-item"><span class="dot bg-green"></span> Выбросы</span>
                    </div>
                </div>
                
                <div class="chart-area big-chart">
                    <svg viewBox="0 0 1000 300" preserveAspectRatio="none" class="svg-chart">
                        <!-- Grid -->
                        <line v-for="i in 6" :key="'g1-'+i" x1="0" :y1="i*50" x2="1000" :y2="i*50" stroke="rgba(255,255,255,0.05)" />
                        <line x1="0" y1="150" x2="1000" y2="150" stroke="rgba(255,255,255,0.2)" stroke-dasharray="4"/> 

                        <!-- Daily Change Paths (Noise) -->
                        <path 
                            v-for="(path, idx) in dailyPaths" 
                            :key="'d-'+idx" 
                            :d="makePath(path, 10, -10)" 
                            fill="none" 
                            :stroke="getDailyColor(idx)" 
                            stroke-width="0.8"
                            opacity="0.6"
                        />
                         
                         <!-- Spike Highlighting (Optional overlay for extreme moves) -->
                         <path :d="makePath(dailyPaths[48], 10, -10)" fill="none" stroke="#4ade80" stroke-width="1.5" />
                    </svg>
                    <div class="chart-label">График 1: Изменения доходностей (%)</div>
                </div>
            </div>

            <!-- Chart 2: Cumulative Changes (Trends) -->
            <div class="card glass-panel chart-container">
                <div class="panel-header">
                    <h3>Накопленные изменения (%)</h3>
                    <div class="legend">
                         <span class="l-item"><span class="dot bg-blue"></span> US10Y</span>
                         <span class="l-item"><span class="dot bg-purple"></span> US02Y</span>
                    </div>
                </div>
                
                <div class="chart-area big-chart">
                    <svg viewBox="0 0 1000 300" preserveAspectRatio="none" class="svg-chart">
                        <line v-for="i in 6" :key="'g2-'+i" x1="0" :y1="i*50" x2="1000" :y2="i*50" stroke="rgba(255,255,255,0.05)" />
                        <line x1="0" y1="150" x2="1000" y2="150" stroke="rgba(255,255,255,0.2)" stroke-dasharray="4"/>

                        <!-- Cumulative Scenario Paths -->
                        <path 
                            v-for="(path, idx) in scenarioPaths" 
                            :key="'c-'+idx" 
                            :d="makePath(path, 40, -40)" 
                            fill="none" 
                            stroke="rgba(255,255,255,0.08)" 
                            stroke-width="1"
                        />

                        <!-- Real Asset Trends -->
                        <path :d="makePath(assetPaths.US10Y, 40, -40)" fill="none" stroke="#3b82f6" stroke-width="2.5" />
                        <path :d="makePath(assetPaths.US02Y, 40, -40)" fill="none" stroke="#a855f7" stroke-width="2.5" />
                    </svg>
                    <div class="chart-label">График 2: Накопленный итог (%)</div>
                </div>
            </div>

        </div>

        <!-- Right: Info & Stats -->
        <aside class="stats-column">
            <div class="card glass-panel h-full sticky-panel">
                <div class="panel-header-sm"><h3>Статистика волатильности</h3></div>
                
                <div class="stat-row">
                    <span class="lbl">Максимальный дневной всплеск</span>
                    <span class="val text-red">+8.4%</span>
                </div>
                <div class="stat-row">
                    <span class="lbl">Возврат к среднему</span>
                    <span class="val">0.45</span>
                </div>
                <div class="stat-row">
                    <span class="lbl">Эксцесс</span>
                    <span class="val text-orange">5.2</span>
                </div>
                
                <div class="divider"></div>

                <div class="panel-header-sm"><h3>Параметры</h3></div>
                <div class="stat-row">
                    <span class="lbl">Количество облигаций</span>
                    <span class="val">50</span>
                </div>
                <div class="stat-row">
                    <span class="lbl">Временной горизонт</span>
                    <span class="val">18M</span>
                </div>

                <div class="divider"></div>
                <div class="info-block">
                    <p>
                        <strong>График 1:</strong> Показывает "шум" и кластеры волатильности. 
                        Всплеск в конце графика (зеленая линия) указывает на шоковое событие.
                    </p>
                    <p class="mt-2">
                        <strong>График 2:</strong> Показывает долгосрочный тренд, который формируется из этих ежедневных изменений.
                    </p>
                </div>
            </div>
        </aside>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const dailyPaths = ref<number[][]>([])
const scenarioPaths = ref<number[][]>([])
const assetPaths = ref<{ [key: string]: number[] }>({ US10Y: [], US02Y: [] })

const generateData = () => {
    const points = 250
    
    // 1. Daily Changes (Noise/Spikes)
    const dailies = []
    const cumulatives = []
    
    for(let i=0; i<50; i++) {
        const dPath = []
        const cPath = [0]
        let cumVal = 0
        
        for(let j=0; j<points; j++) {
            // Generate daily change (mostly noise)
            let dailyChange = (Math.random() - 0.5) * 2
            
            // Add a "shock" event at the end (like in your screenshot)
            if (j > 220 && Math.random() > 0.8) {
                dailyChange *= 8 // Huge spike
            }
            
            dPath.push(dailyChange)
            
            cumVal += dailyChange
            cPath.push(cumVal)
        }
        dailies.push(dPath)
        cumulatives.push(cPath)
    }
    
    dailyPaths.value = dailies
    scenarioPaths.value = cumulatives

    // 2. Asset Trends
    const makeTrend = (drift: number) => {
        const p = [0]
        let v = 0
        for(let j=0; j<points; j++) {
            v += (Math.random() - 0.5) + drift
            p.push(v)
        }
        return p
    }
    assetPaths.value = {
        US10Y: makeTrend(0.1),
        US02Y: makeTrend(-0.05)
    }
}

// Helper: Color logic for daily "spaghetti"
const getDailyColor = (idx: number) => {
    // Randomize colors slightly to match the "messy" look of the screenshot
    const hue = Math.floor(Math.random() * 360)
    return `hsla(${hue}, 60%, 70%, 0.4)`
}

// Helper: SVG Path Builder with customizable Y-scale
const makePath = (data: number[], maxVal: number, minVal: number) => {
    if (!data || data.length === 0) return ''
    
    const width = 1000
    const height = 300
    
    const scaleX = (i: number) => (i / (data.length - 1)) * width
    const scaleY = (v: number) => height - ((v - minVal) / (maxVal - minVal)) * height

    return 'M ' + data.map((val, i) => 
        `${scaleX(i).toFixed(1)},${scaleY(val).toFixed(1)}`
    ).join(' L ')
}

onMounted(() => {
    generateData()
})
</script>

<style scoped>
/* Layout */
.page-container { padding: 28px; max-width: 1600px; margin: 0 auto; color: #fff; height: 100vh; overflow-y: auto; }
.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; }
.section-title { font-size: 24px; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }

.btn-refresh { 
    background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.1); 
    color: #fff; padding: 8px 16px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 8px; font-size: 13px;
    transition: all 0.2s;
}
.btn-refresh:hover { background: rgba(255,255,255,0.15); }

/* Grid */
.analysis-grid { display: grid; grid-template-columns: 1fr 300px; gap: 24px; }
.charts-column { display: flex; flex-direction: column; gap: 24px; }

/* Cards */
.card { background: rgba(20, 22, 28, 0.4); backdrop-filter: blur(40px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; }
.glass-panel { box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
.sticky-panel { position: sticky; top: 20px; }

.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.panel-header h3 { margin: 0; font-size: 14px; color: #fff; font-weight: 600; }
.legend { display: flex; gap: 12px; font-size: 11px; }
.l-item { display: flex; align-items: center; gap: 6px; color: rgba(255,255,255,0.7); }
.dot { width: 6px; height: 6px; border-radius: 50%; }
.bg-blue { background: #3b82f6; }
.bg-purple { background: #a855f7; }
.bg-green { background: #4ade80; }
.bg-gray { background: rgba(255,255,255,0.3); }

/* Charts */
.chart-container { position: relative; }
.chart-area.big-chart { height: 300px; width: 100%; overflow: hidden; position: relative; }
.svg-chart { width: 100%; height: 100%; }
.chart-label { position: absolute; bottom: 10px; right: 20px; font-size: 11px; color: rgba(255,255,255,0.3); font-style: italic; }

/* Stats Sidebar */
.h-full { height: auto; min-height: 100%; box-sizing: border-box; }
.panel-header-sm h3 { margin: 0 0 16px 0; font-size: 11px; text-transform: uppercase; color: rgba(255,255,255,0.4); letter-spacing: 0.05em; font-weight: 600; }
.stat-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 13px; }
.stat-row .lbl { color: rgba(255,255,255,0.6); }
.stat-row .val { font-weight: 500; font-family: monospace; color: #fff; }
.text-red { color: #f87171; }
.text-orange { color: #fbbf24; }

.divider { height: 1px; background: rgba(255,255,255,0.1); margin: 20px 0; }
.info-block p { font-size: 12px; line-height: 1.5; color: rgba(255,255,255,0.5); margin: 0; }
.mt-2 { margin-top: 12px; }

</style>