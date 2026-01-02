<!-- src/pages/MonteCarlo.vue -->
<template>
  <div class="page-container">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Симуляция траекторий методом Монте-Карло</h1>
        <p class="section-subtitle">Генерация стохастических сценариев и оценка хвостовых рисков</p>
      </div>
      <div class="header-actions">
         <span class="status-badge" :class="isRunning ? 'pulse' : ''">
             <span class="dot" :class="isRunning ? 'bg-orange' : 'bg-green'"></span>
             {{ isRunning ? 'Вычисление...' : 'Готов к запуску' }}
         </span>
      </div>
    </div>

    <div class="mc-grid-layout">
        
        <!-- LEFT COLUMN: CONTROLS -->
        <aside class="controls-column">
            <!-- Settings Card -->
            <div class="card glass-panel settings-card">
                <div class="panel-header-sm">
                    <h3>Параметры модели</h3>
                </div>

                <div class="controls-form">
                    <!-- Initial Price (Scrubbable) -->
                    <div class="input-group">
                        <label class="lbl">Начальная цена (S₀)</label>
                        <ScrubInput 
                           v-model="params.startPrice" 
                           :step="1" :min="1" :max="5000" prefix="$"
                           @change="runSimulationFast"
                        />
                    </div>

                    <!-- Volatility (Scrubbable) -->
                    <div class="input-group">
                        <label class="lbl">Волатильность (σ)</label>
                        <ScrubInput 
                           v-model="params.volatility" 
                           :step="0.5" :min="1" :max="200" :decimals="1" suffix="%"
                           @change="runSimulationFast"
                        />
                    </div>

                    <!-- Drift (Scrubbable) -->
                    <div class="input-group">
                        <label class="lbl">Ожидаемая доходность (μ)</label>
                        <ScrubInput 
                           v-model="params.drift" 
                           :step="0.5" :min="-50" :max="100" :decimals="1" suffix="%"
                           @change="runSimulationFast"
                        />
                    </div>

                    <div class="divider"></div>

                    <!-- Time & Paths -->
                    <div class="row-2-col">
                        <div class="input-group">
                            <label class="lbl">Горизонт (T)</label>
                            <input v-model.number="params.days" type="number" class="glass-input" placeholder="252" />
                        </div>
                        <div class="input-group">
                            <label class="lbl">Количество путей (N)</label>
                            <input v-model.number="params.paths" type="number" step="1000" class="glass-input" />
                        </div>
                    </div>

                    <button @click="runSimulationFull" :disabled="isRunning" class="btn btn-primary-gradient btn-full-width">
                        <span v-if="!isRunning">Запустить симуляцию</span>
                        <span v-else>Расчет...</span>
                    </button>
                </div>
            </div>

            <!-- Statistics Card -->
            <div v-if="results" class="card glass-panel stats-card">
                <div class="panel-header-sm">
                    <h3>Статистика прогона</h3>
                </div>
                <ul class="simple-list">
                    <li>
                        <span>Мин. значение</span>
                        <span class="mono text-red">{{ formatCurrency(results.min) }}</span>
                    </li>
                    <li>
                        <span>Макс. значение</span>
                        <span class="mono text-green">{{ formatCurrency(results.max) }}</span>
                    </li>
                    <li>
                        <span>Медиана</span>
                        <span class="mono text-blue">{{ formatCurrency(results.median) }}</span>
                    </li>
                </ul>
            </div>
        </aside>

        <!-- RIGHT COLUMN: VISUALIZATION -->
        <main class="viz-column">
            
            <!-- Key Metrics Cards -->
            <div class="metrics-row">
                <div class="kpi-card-mini">
                    <span class="kpi-lbl">Математическое ожидание (E)</span>
                    <span class="kpi-val" :class="getColor(results?.meanChange)">
                        {{ results ? formatCurrency(results.mean) : '—' }}
                    </span>
                </div>
                <div class="kpi-card-mini">
                    <span class="kpi-lbl">VaR (95%)</span>
                    <span class="kpi-val text-red">
                        {{ results ? formatCurrency(results.var95) : '—' }}
                    </span>
                </div>
                <div class="kpi-card-mini">
                    <span class="kpi-lbl">Вероятность роста</span>
                    <span class="kpi-val text-green">
                        {{ results ? results.winProb + '%' : '—' }}
                    </span>
                </div>
                <div class="kpi-card-mini">
                    <span class="kpi-lbl">Текущий день симуляции</span>
                    <span class="kpi-val text-blue">
                        {{ playbackStep }} <span class="text-sm text-muted">/ {{ params.days }}</span>
                    </span>
                </div>
            </div>

            <!-- Main Chart Area -->
            <div class="card glass-panel chart-panel">
                <div class="chart-header">
                    <h3>
                        Траектории симуляции
                        <span v-if="isPlaying" class="live-badge">● LIVE PLAYBACK</span>
                    </h3>
                    
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

                        <!-- Start Price Reference Line -->
                        <line 
                            x1="0" 
                            :y1="scaleY(params.startPrice)" 
                            x2="1000" 
                            :y2="scaleY(params.startPrice)" 
                            stroke="rgba(255,255,255,0.3)" 
                            stroke-dasharray="4" 
                        />

                        <!-- Dynamic Paths -->
                        <path 
                            v-for="(path, i) in chartData.displayPaths" 
                            :key="`path-${i}`"
                            :d="generatePathD(path, playbackStep)"
                            fill="none" 
                            stroke="rgba(59, 130, 246, 0.15)" 
                            stroke-width="1" 
                        />

                        <!-- Confidence Area (5-95%) -->
                        <path 
                            :d="generateAreaD(chartData.q05, chartData.q95, playbackStep)"
                            fill="rgba(59, 130, 246, 0.1)" 
                            stroke="none" 
                        />

                        <!-- Median Path (Bold) -->
                        <path 
                            :d="generatePathD(chartData.medianPath, playbackStep)"
                            fill="none" 
                            stroke="#3b82f6" 
                            stroke-width="3" 
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

                    <div v-else class="empty-chart">
                        <div class="spinner-large" v-if="isRunning"></div>
                        <span v-else>Запустите симуляцию для отображения графиков</span>
                    </div>
                </div>
            </div>

        </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useTaskStore } from '@/stores/tasks'
import ScrubInput from '@/components/common/ScrubInput.vue'

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

// Playback State
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

const runSimulationFast = () => {
    generateData()
    calculateMetrics()
    if (playbackStep.value >= params.days) {
        playbackStep.value = params.days
    }
}

const runSimulationFull = async () => {
    if (isRunning.value) return
    isRunning.value = true
    results.value = null 
    stopPlay()
    
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
        }, 150)
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
    
    const nextStep = playbackStep.value + 2
    
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

// --- SVG & Helpers ---

const boxMullerRandom = (): number => {
    let u = 0
    let v = 0
    while (u === 0) u = Math.random()
    while (v === 0) v = Math.random()
    return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v)
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
    new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'USD', 
        maximumFractionDigits: 0 
    }).format(val)

const getColor = (val: number | string): string => {
    const numVal = typeof val === 'string' ? parseFloat(val) : val
    return numVal > 0 ? 'text-green' : 'text-red'
}

onUnmounted(() => {
    if (animationFrame) {
        cancelAnimationFrame(animationFrame)
    }
})

onMounted(() => {
    // Optional initialization
})
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.page-container {
    display: flex;
    flex-direction: column;
    gap: 24px;
    padding: 28px;
    max-width: 1600px;
    margin: 0 auto;
    min-height: 100vh;
    overflow-y: auto;
}

/* ============================================
   HEADER SECTION
   ============================================ */
.section-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 8px;
}

.header-left {
    flex: 1;
}

.section-title {
    font-size: 28px;
    font-weight: 700;
    color: #fff;
    margin: 0;
}

.section-subtitle {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.5);
    margin: 4px 0 0 0;
}

.status-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.status-badge.pulse {
    border-color: rgba(251, 191, 36, 0.4);
    color: #fbbf24;
}

.dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
}

/* ============================================
   GRID LAYOUT
   ============================================ */
.mc-grid-layout {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 24px;
    flex: 1;
}

/* ============================================
   CONTROLS COLUMN
   ============================================ */
.controls-column {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.settings-card {
    flex-shrink: 0;
}

.stats-card {
    flex-shrink: 0;
    margin-top: auto;
}

.card {
    border-radius: 18px;
    overflow: hidden;
    background: rgba(20, 22, 28, 0.25);
    backdrop-filter: blur(40px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5);
}

.glass-panel {
    padding: 20px;
}

.panel-header-sm h3 {
    margin: 0 0 16px 0;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    color: rgba(255, 255, 255, 0.4);
    letter-spacing: 0.05em;
}

/* ============================================
   FORM CONTROLS
   ============================================ */
.controls-form {
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.input-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.lbl {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.5);
    font-weight: 500;
}

.row-2-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.glass-input,
.glass-select {
    width: 100%;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #fff;
    padding: 10px;
    border-radius: 8px;
    font-family: var(--font-family-mono);
    font-size: 13px;
    outline: none;
    transition: 0.2s;
}

.glass-input:focus,
.glass-select:focus {
    border-color: #3b82f6;
}

.simple-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.simple-list li {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding-bottom: 6px;
    color: rgba(255, 255, 255, 0.7);
}

/* ============================================
   VISUALIZATION COLUMN
   ============================================ */
.viz-column {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.metrics-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}

.kpi-card-mini {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.kpi-lbl {
    font-size: 10px;
    color: rgba(255, 255, 255, 0.4);
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.05em;
}

.kpi-val {
    font-size: 20px;
    font-weight: 700;
    color: #fff;
    font-family: var(--font-family-mono);
}

.text-sm {
    font-size: 12px;
}

/* ============================================
   CHART PANEL
   ============================================ */
.chart-panel {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 500px;
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    min-height: 32px;
}

.chart-header h3 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: #fff;
}

/* ============================================
   PLAYBACK CONTROLS
   ============================================ */
.playback-controls {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(0, 0, 0, 0.3);
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.icon-btn {
    background: none;
    border: none;
    color: #fff;
    cursor: pointer;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: 0.2s;
    font-size: 12px;
}

.icon-btn:hover {
    background: rgba(255, 255, 255, 0.1);
}

.timeline-wrapper {
    position: relative;
    width: 140px;
    height: 4px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    display: flex;
    align-items: center;
}

.timeline-slider {
    position: absolute;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
    z-index: 2;
    margin: 0;
}

.timeline-track {
    height: 100%;
    background: #3b82f6;
    border-radius: 2px;
    pointer-events: none;
    transition: width 0.05s linear;
}

.live-badge {
    font-size: 10px;
    color: #ef4444;
    margin-left: 8px;
    animation: blink 1s infinite;
}

@keyframes blink {
    50% {
        opacity: 0.5;
    }
}

/* ============================================
   CHART CONTAINER
   ============================================ */
.chart-container {
    flex-grow: 1;
    position: relative;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 8px;
    overflow: hidden;
    min-height: 350px;
}

.main-svg {
    width: 100%;
    height: 100%;
}

.empty-chart {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: rgba(255, 255, 255, 0.3);
    font-size: 13px;
    gap: 12px;
}

/* ============================================
   BUTTONS
   ============================================ */
.btn {
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    color: white;
    transition: 0.2s;
    text-align: center;
}

.btn-primary-gradient {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.btn-primary-gradient:hover:not(:disabled) {
    filter: brightness(1.1);
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.btn-full-width {
    width: 100%;
    margin-top: 4px;
}

/* ============================================
   UTILITY CLASSES
   ============================================ */
.text-green {
    color: #4ade80;
}

.text-red {
    color: #f87171;
}

.text-blue {
    color: #60a5fa;
}

.bg-green {
    background: #4ade80;
}

.bg-red {
    background: #f87171;
}

.bg-blue {
    background: #3b82f6;
}

.bg-orange {
    background: #fbbf24;
}

.text-muted {
    color: rgba(255, 255, 255, 0.4);
}

.mono {
    font-family: var(--font-family-mono);
}

.divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.1);
    margin: 6px 0;
}

.pl-6 {
    padding-left: 24px;
}

/* ============================================
   SPINNER
   ============================================ */
.spinner-large {
    width: 32px;
    height: 32px;
    border: 3px solid rgba(255, 255, 255, 0.1);
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
    .mc-grid-layout {
        grid-template-columns: 1fr;
    }

    .metrics-row {
        grid-template-columns: 1fr 1fr;
    }
}

@media (max-width: 640px) {
    .page-container {
        padding: 16px;
        gap: 16px;
    }

    .section-title {
        font-size: 22px;
    }

    .metrics-row {
        grid-template-columns: 1fr;
    }

    .playback-controls {
        width: 100%;
    }

    .timeline-wrapper {
        flex: 1;
    }
}
</style>