<!-- src/pages/MonteCarlo.vue -->
<template>
  <div class="page-container">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Симуляция Монте-Карло</h1>
        <p class="section-subtitle">Генерация стохастических сценариев (GBM Model)</p>
      </div>
      <div class="header-actions">
         <div class="glass-pill status-pill" :class="{ pulse: isRunning }">
             <span class="dot" :class="isRunning ? 'bg-orange' : 'bg-green'"></span>
             {{ isRunning ? 'Вычисление...' : 'Готов к запуску' }}
         </div>
      </div>
    </div>

    <div class="mc-grid-layout">
        
        <!-- LEFT COLUMN: CONTROLS -->
        <aside class="controls-column">
            <!-- Settings Card -->
            <div class="glass-card settings-card">
                <div class="panel-header-sm">
                    <h3>Параметры модели</h3>
                </div>

                <div class="controls-form">
                    <!-- Initial Price -->
                    <div class="input-group">
                        <label class="lbl">Начальная цена (S₀)</label>
                        <div class="glass-input-wrapper">
                            <input v-model.number="params.startPrice" type="number" class="reset-input" />
                            <span class="suffix">$</span>
                        </div>
                    </div>

                    <!-- Volatility -->
                    <div class="input-group">
                        <label class="lbl">Волатильность (σ)</label>
                        <div class="glass-input-wrapper">
                            <input v-model.number="params.volatility" type="number" step="0.1" class="reset-input" />
                            <span class="suffix">%</span>
                        </div>
                    </div>

                    <!-- Drift -->
                    <div class="input-group">
                        <label class="lbl">Доходность (μ)</label>
                        <div class="glass-input-wrapper">
                            <input v-model.number="params.drift" type="number" step="0.1" class="reset-input" />
                            <span class="suffix">%</span>
                        </div>
                    </div>

                    <div class="divider"></div>

                    <!-- Time & Paths -->
                    <div class="row-2-col">
                        <div class="input-group">
                            <label class="lbl">Дней (T)</label>
                            <div class="glass-input-wrapper">
                                <input v-model.number="params.days" type="number" class="reset-input" />
                            </div>
                        </div>
                        <div class="input-group">
                            <label class="lbl">Путей (N)</label>
                            <div class="glass-input-wrapper">
                                <input v-model.number="params.paths" type="number" step="1000" class="reset-input" />
                            </div>
                        </div>
                    </div>

                    <button @click="runSimulationFull" :disabled="isRunning" class="btn-glass primary w-full mt-4">
                        <span v-if="!isRunning">Запустить симуляцию</span>
                        <span v-else>Расчет...</span>
                    </button>
                </div>
            </div>

            <!-- Statistics Card -->
            <transition name="fade">
            <div v-if="results" class="glass-card stats-card">
                <div class="panel-header-sm">
                    <h3>Результаты (T={{ params.days }})</h3>
                </div>
                <ul class="simple-list">
                    <li>
                        <span>Мин. цена</span>
                        <span class="mono text-red">{{ formatCurrency(results.min) }}</span>
                    </li>
                    <li>
                        <span>Макс. цена</span>
                        <span class="mono text-green">{{ formatCurrency(results.max) }}</span>
                    </li>
                    <li>
                        <span>Медиана</span>
                        <span class="mono text-blue">{{ formatCurrency(results.median) }}</span>
                    </li>
                </ul>
            </div>
            </transition>
        </aside>

        <!-- RIGHT COLUMN: VISUALIZATION -->
        <main class="viz-column">
            
            <!-- Key Metrics Cards -->
            <div class="metrics-row">
                <div class="glass-card kpi-card-mini">
                    <span class="kpi-lbl">Среднее (Mean)</span>
                    <span class="kpi-val" :class="getColor(results?.meanChange)">
                        {{ results ? formatCurrency(results.mean) : '—' }}
                    </span>
                </div>
                <div class="glass-card kpi-card-mini">
                    <span class="kpi-lbl">VaR (95%)</span>
                    <span class="kpi-val text-red">
                        {{ results ? formatCurrency(results.var95) : '—' }}
                    </span>
                </div>
                <div class="glass-card kpi-card-mini">
                    <span class="kpi-lbl">Вероятность роста</span>
                    <span class="kpi-val text-green">
                        {{ results ? results.winProb + '%' : '—' }}
                    </span>
                </div>
                <div class="glass-card kpi-card-mini">
                    <span class="kpi-lbl">День симуляции</span>
                    <span class="kpi-val text-blue">
                        {{ playbackStep }} <span class="text-sm opacity-50">/ {{ params.days }}</span>
                    </span>
                </div>
            </div>

            <!-- Main Chart Area -->
            <div class="glass-card chart-panel">
                <div class="chart-header">
                    <div class="flex items-center gap-2">
                        <h3>Траектории</h3>
                        <span v-if="isPlaying" class="live-badge">● LIVE</span>
                    </div>
                    
                    <!-- Playback Controls -->
                    <div class="playback-controls" v-if="chartData.paths.length">
                        <button class="icon-btn" @click="togglePlay" title="Play/Pause">
                            <span v-if="isPlaying">⏸</span>
                            <span v-else>▶</span>
                        </button>
                        
                        <div class="timeline-wrapper">
                            <input 
                                type="range" 
                                min="0" 
                                :max="params.days" 
                                v-model.number="playbackStep"
                                @input="stopPlay"
                                class="timeline-slider"
                            />
                            <div class="timeline-track" :style="{ width: (playbackStep / params.days * 100) + '%' }"></div>
                        </div>

                        <button class="icon-btn" @click="resetPlayback" title="Reset">↺</button>
                    </div>
                </div>
                
                <div class="chart-container" ref="chartContainer">
                    <svg v-if="chartData.paths.length > 0" viewBox="0 0 1000 400" preserveAspectRatio="none" class="main-svg">
                        <!-- Grid Lines -->
                        <line x1="0" y1="350" x2="1000" y2="350" stroke="rgba(255,255,255,0.05)" />
                        <line x1="0" y1="200" x2="1000" y2="200" stroke="rgba(255,255,255,0.05)" />
                        <line x1="0" y1="50" x2="1000" y2="50" stroke="rgba(255,255,255,0.05)" />

                        <!-- Start Price Line -->
                        <line 
                            x1="0" 
                            :y1="scaleY(params.startPrice)" 
                            x2="1000" 
                            :y2="scaleY(params.startPrice)" 
                            stroke="rgba(255,255,255,0.2)" 
                            stroke-dasharray="4" 
                        />

                        <!-- Paths -->
                        <path 
                            v-for="(path, i) in chartData.displayPaths" 
                            :key="`path-${i}`"
                            :d="generatePathD(path, playbackStep)"
                            fill="none" 
                            stroke="rgba(59, 130, 246, 0.2)" 
                            stroke-width="1" 
                        />

                        <!-- Confidence Area -->
                        <path 
                            :d="generateAreaD(chartData.q05, chartData.q95, playbackStep)"
                            fill="rgba(59, 130, 246, 0.1)" 
                            stroke="none" 
                        />

                        <!-- Median Path -->
                        <path 
                            :d="generatePathD(chartData.medianPath, playbackStep)"
                            fill="none" 
                            stroke="#3b82f6" 
                            stroke-width="2.5" 
                        />
                              
                        <!-- Quantile Lines -->
                        <path 
                            :d="generatePathD(chartData.q05, playbackStep)" 
                            fill="none" 
                            stroke="#f87171" 
                            stroke-width="1.5" 
                            stroke-dasharray="4"
                        />
                        <path 
                            :d="generatePathD(chartData.q95, playbackStep)" 
                            fill="none" 
                            stroke="#34d399" 
                            stroke-width="1.5" 
                            stroke-dasharray="4"
                        />
                        
                        <!-- Current Time Marker -->
                        <line 
                            v-if="playbackStep > 0"
                            :x1="scaleX(playbackStep)" 
                            y1="0" 
                            :x2="scaleX(playbackStep)" 
                            y2="400" 
                            stroke="rgba(255,255,255,0.4)" 
                            stroke-dasharray="2" 
                        />
                    </svg>

                    <div v-else class="empty-state">
                        <div v-if="isRunning" class="spinner"></div>
                        <span v-else>Нажмите «Запустить» для генерации</span>
                    </div>
                </div>
            </div>

        </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { useTaskStore } from '@/stores/tasks'

// --- State ---
const taskStore = useTaskStore()
const isRunning = ref(false)
const params = reactive({
    startPrice: 100,
    volatility: 15.5,
    drift: 8.0,
    days: 252,
    paths: 1000,
    model: 'gbm'
})

const playbackStep = ref(0)
const isPlaying = ref(false)
let animationFrame: number | null = null

const results = ref<any>(null)
const chartData = reactive({
    paths: [] as number[][],       
    displayPaths: [] as number[][],
    medianPath: [] as number[],
    q05: [] as number[],
    q95: [] as number[],
    minY: 0,
    maxY: 200
})

// --- Simulation Logic ---

const runSimulationFull = async () => {
    if (isRunning.value) return
    isRunning.value = true
    results.value = null 
    stopPlay()
    
    // Эмуляция задачи
    const taskId = taskStore.addTask(`Monte Carlo (${params.paths} paths)`, 'simulation')

    try {
        let progress = 0
        const interval = setInterval(() => {
            progress += 10
            taskStore.updateProgress(taskId, progress)
            
            if (progress >= 100) {
                clearInterval(interval)
                generateData()
                calculateMetrics()
                isRunning.value = false
                
                playbackStep.value = 0
                togglePlay()
            }
        }, 100)
    } catch (e) {
        taskStore.failTask(taskId)
        isRunning.value = false
    }
}

// --- Playback Controls ---

const togglePlay = () => {
    if (isPlaying.value) {
        stopPlay()
    } else {
        if (playbackStep.value >= params.days) {
            playbackStep.value = 0
        }
        isPlaying.value = true
        animate()
    }
}

const stopPlay = () => {
    isPlaying.value = false
    if (animationFrame) {
        cancelAnimationFrame(animationFrame)
    }
}

const resetPlayback = () => {
    stopPlay()
    playbackStep.value = 0
}

const animate = () => {
    if (!isPlaying.value) return
    
    // Скорость анимации
    const nextStep = playbackStep.value + Math.max(1, Math.floor(params.days / 100))
    
    if (nextStep >= params.days) {
        playbackStep.value = params.days
        stopPlay()
    } else {
        playbackStep.value = nextStep
        animationFrame = requestAnimationFrame(animate)
    }
}

// --- Monte Carlo Engine (GBM) ---

const generateData = () => {
    const { startPrice, volatility, drift, days, paths } = params
    const dt = 1 / 252
    const mu = drift / 100
    const sigma = volatility / 100
    
    const newPaths: number[][] = []
    
    for (let i = 0; i < paths; i++) {
        const path = [startPrice]
        let currentPrice = startPrice
        
        for (let t = 1; t <= days; t++) {
            const Z = boxMullerRandom()
            const driftTerm = (mu - 0.5 * sigma * sigma) * dt
            const shockTerm = sigma * Math.sqrt(dt) * Z
            currentPrice = currentPrice * Math.exp(driftTerm + shockTerm)
            path.push(currentPrice)
        }
        newPaths.push(path)
    }
    
    // Calculate quantiles
    const steps = days + 1
    const medianPath: number[] = []
    const q05Path: number[] = []
    const q95Path: number[] = []
    let globalMin = startPrice
    let globalMax = startPrice

    for (let t = 0; t < steps; t++) {
        const pricesAtT = newPaths.map(p => p[t]).sort((a, b) => a - b)
        const med = pricesAtT[Math.floor(paths * 0.5)]
        const q05 = pricesAtT[Math.floor(paths * 0.05)]
        const q95 = pricesAtT[Math.floor(paths * 0.95)]
        
        medianPath.push(med)
        q05Path.push(q05)
        q95Path.push(q95)

        if (q05 < globalMin) globalMin = q05
        if (q95 > globalMax) globalMax = q95
    }

    chartData.paths = newPaths
    chartData.displayPaths = newPaths.slice(0, 50) 
    chartData.medianPath = medianPath
    chartData.q05 = q05Path
    chartData.q95 = q95Path
    chartData.minY = globalMin * 0.9
    chartData.maxY = globalMax * 1.1
    
    if (!isPlaying.value) {
        playbackStep.value = days
    }
}

const calculateMetrics = () => {
    const finalPrices = chartData.paths.map(p => p[p.length - 1])
    finalPrices.sort((a, b) => a - b)
    const n = finalPrices.length
    const mean = finalPrices.reduce((a, b) => a + b, 0) / n
    const var95 = finalPrices[Math.floor(n * 0.05)]
    const winCount = finalPrices.filter(p => p > params.startPrice).length
    
    results.value = {
        mean,
        min: finalPrices[0],
        max: finalPrices[n - 1],
        median: finalPrices[Math.floor(n * 0.5)],
        var95,
        meanChange: ((mean - params.startPrice) / params.startPrice * 100).toFixed(2),
        realizedVol: params.volatility,
        winProb: ((winCount / n) * 100).toFixed(1)
    }
}

// --- Helpers ---
const boxMullerRandom = (): number => {
    let u = 0, v = 0;
    while(u === 0) u = Math.random();
    while(v === 0) v = Math.random();
    return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}

const scaleX = (t: number): number => (t / params.days) * 1000

const scaleY = (price: number): number => {
    const range = chartData.maxY - chartData.minY
    const normalized = (price - chartData.minY) / range
    return 400 - normalized * 400
}

const generatePathD = (path: number[], limit: number): string => {
    if (!path.length) return ''
    const sliced = path.slice(0, limit + 1)
    return 'M ' + sliced.map((p, i) => `${scaleX(i).toFixed(1)},${scaleY(p).toFixed(1)}`).join(' L ')
}

const generateAreaD = (lower: number[], upper: number[], limit: number): string => {
    if (!lower.length) return ''
    const lSliced = lower.slice(0, limit + 1)
    const uSliced = upper.slice(0, limit + 1)
    
    let d = 'M ' + lSliced.map((p, i) => `${scaleX(i).toFixed(1)},${scaleY(p).toFixed(1)}`).join(' L ')
    for (let i = uSliced.length - 1; i >= 0; i--) {
        d += ` L ${scaleX(i).toFixed(1)},${scaleY(uSliced[i]).toFixed(1)}`
    }
    d += ' Z'
    return d
}

const formatCurrency = (val: number): string => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val)

const getColor = (val: number | string): string => {
    const numVal = typeof val === 'string' ? parseFloat(val) : val
    return numVal > 0 ? 'text-green' : 'text-red'
}

onUnmounted(() => {
    if (animationFrame) cancelAnimationFrame(animationFrame)
})
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.page-container {
    padding: 24px 32px; max-width: 1600px; margin: 0 auto;
    display: flex; flex-direction: column; gap: 24px; height: 100%;
}

/* ============================================
   HEADER
   ============================================ */
.section-header { display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 8px; }
.section-title { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; }
.section-subtitle { font-size: 13px; color: rgba(255, 255, 255, 0.5); margin: 4px 0 0 0; }

.glass-pill {
    display: flex; align-items: center; gap: 8px; padding: 6px 14px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 99px; font-size: 12px; color: rgba(255,255,255,0.8); font-weight: 500;
}
.glass-pill.pulse { border-color: rgba(251, 191, 36, 0.4); color: #fbbf24; }
.dot { width: 6px; height: 6px; border-radius: 50%; box-shadow: 0 0 6px currentColor; }
.bg-green { background: #4ade80; color: #4ade80; }
.bg-orange { background: #fbbf24; color: #fbbf24; }

/* ============================================
   GRID
   ============================================ */
.mc-grid-layout { display: grid; grid-template-columns: 300px 1fr; gap: 24px; flex: 1; min-height: 0; }
.controls-column { display: flex; flex-direction: column; gap: 16px; overflow-y: auto; }
.viz-column { display: flex; flex-direction: column; gap: 16px; min-height: 0; }

/* GLASS CARD */
.glass-card {
    border-radius: 20px; background: rgba(30, 32, 40, 0.4);
    backdrop-filter: blur(30px) saturate(160%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 20px 40px -10px rgba(0,0,0,0.4);
    padding: 20px;
}

/* ============================================
   INPUTS & CONTROLS
   ============================================ */
.panel-header-sm h3 { margin: 0 0 16px 0; font-size: 12px; font-weight: 700; text-transform: uppercase; color: rgba(255, 255, 255, 0.4); letter-spacing: 0.05em; }
.controls-form { display: flex; flex-direction: column; gap: 14px; }
.input-group { display: flex; flex-direction: column; gap: 6px; }
.lbl { font-size: 11px; color: rgba(255, 255, 255, 0.5); font-weight: 600; }

/* REFACTORED INPUTS */
.glass-input-wrapper {
  display: flex; align-items: center; background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0 10px; height: 36px;
  transition: all 0.2s;
}
.glass-input-wrapper:focus-within { background: rgba(0,0,0,0.35); border-color: rgba(255,255,255,0.3); }

.reset-input {
  width: 100%; background: transparent !important; border: none !important;
  color: #fff; text-align: right; padding: 0; margin-right: 4px;
  font-family: "SF Mono", monospace; outline: none; font-size: 13px; height: 100%;
}
.suffix { font-size: 13px; color: rgba(255,255,255,0.4); font-weight: 500; }

.row-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.divider { height: 1px; background: rgba(255, 255, 255, 0.1); margin: 4px 0; }

/* BTN */
.btn-glass {
  height: 40px; border-radius: 10px; font-weight: 600; font-size: 13px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s; border: none;
}
.btn-glass.primary { background: #3b82f6; color: #fff; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }
.btn-glass.primary:hover:not(:disabled) { background: #2563eb; transform: translateY(-1px); }
.btn-glass:disabled { opacity: 0.6; cursor: not-allowed; }
.mt-4 { margin-top: 16px; }

/* LIST */
.simple-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.simple-list li { display: flex; justify-content: space-between; font-size: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 6px; color: rgba(255, 255, 255, 0.7); }

/* ============================================
   VIZ METRICS
   ============================================ */
.metrics-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.kpi-card-mini { padding: 16px; display: flex; flex-direction: column; gap: 4px; align-items: flex-start; }
.kpi-lbl { font-size: 10px; color: rgba(255, 255, 255, 0.4); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; }
.kpi-val { font-size: 20px; font-weight: 700; color: #fff; font-family: "SF Mono", monospace; }

/* ============================================
   CHART
   ============================================ */
.chart-panel { flex: 1; display: flex; flex-direction: column; min-height: 400px; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.chart-header h3 { margin: 0; font-size: 14px; font-weight: 600; color: #fff; }
.live-badge { font-size: 10px; color: #ef4444; font-weight: 700; animation: blink 1.5s infinite; }
@keyframes blink { 50% { opacity: 0.5; } }

/* PLAYBACK */
.playback-controls { display: flex; align-items: center; gap: 12px; background: rgba(0,0,0,0.3); padding: 4px 12px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); }
.icon-btn { background: none; border: none; color: #fff; cursor: pointer; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 12px; border-radius: 50%; transition: 0.2s; }
.icon-btn:hover { background: rgba(255,255,255,0.1); }

.timeline-wrapper { position: relative; width: 140px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; display: flex; align-items: center; }
.timeline-slider { position: absolute; width: 100%; height: 100%; opacity: 0; cursor: pointer; z-index: 2; margin: 0; }
.timeline-track { height: 100%; background: #3b82f6; border-radius: 2px; pointer-events: none; }

.chart-container { flex: 1; position: relative; background: rgba(0,0,0,0.2); border-radius: 8px; overflow: hidden; }
.main-svg { width: 100%; height: 100%; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: rgba(255,255,255,0.3); font-size: 13px; }
.spinner { width: 24px; height: 24px; border: 2px solid rgba(255,255,255,0.1); border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 8px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* UTILS */
.text-green { color: #4ade80; }
.text-red { color: #f87171; }
.text-blue { color: #60a5fa; }
.mono { font-family: "SF Mono", monospace; }
.opacity-50 { opacity: 0.5; }
.w-full { width: 100%; }

@media (max-width: 1024px) {
    .mc-grid-layout { grid-template-columns: 1fr; }
    .metrics-row { grid-template-columns: 1fr 1fr; }
}
</style>