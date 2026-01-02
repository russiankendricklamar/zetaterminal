<!-- src/pages/RegimeAnalysis.vue -->
<template>
  <div class="page-container">
    
    <!-- Header -->
    <div class="section-header">
      <div>
        <h1 class="section-title">Выявление скрытых рыночных режимов</h1>
        <p class="section-subtitle">Классификация режимов скрытой марковской цепи и анализ волатильности</p>
      </div>
      <div class="header-actions">
         <div class="status-pill">
            <span class="dot" :class="currentRegimeColor"></span>
            Текущий режим: {{ currentRegimeLabel }}
         </div>
      </div>
    </div>

    <div class="dashboard-grid">
        
        <!-- LEFT: Controls & Stats -->
        <aside class="left-panel">
            
            <!-- Controls -->
            <div class="card glass-panel mb-4">
                <div class="panel-header-sm"><h3>Параметры модели</h3></div>
                <div class="controls-form">
                    <div class="input-group">
                        <label class="lbl">Актив</label>
                        <select v-model="selectedAsset" class="glass-select">
                            <option value="SPY">S&P 500 (SPY)</option>
                            <option value="QQQ">Nasdaq 100 (QQQ)</option>
                            <option value="IWM">Russell 2000 (IWM)</option>
                            <option value="BTC">Bitcoin (BTC)</option>
                        </select>
                    </div>
                    
                    <div class="input-group">
                        <label class="lbl">Количество скрытых режимов</label>
                        <ScrubInput 
                            v-model="nComponents" 
                            :min="2" :max="5" :step="1" 
                            class="text-accent"
                        />
                    </div>

                    <div class="divider"></div>

                    <div class="input-group">
                        <label class="lbl">Мультипликатор шока по режиму</label>
                         <ScrubInput 
                            v-model="shockMultiplier" 
                            :min="0.5" :max="3.0" :step="0.1" :decimals="1"
                            suffix="x"
                        />
                    </div>

                    <button @click="runHMM" :disabled="isLoading" class="btn btn-primary-gradient w-full mt-2">
                        <span v-if="!isLoading">Запустить анализ</span>
                        <span v-else class="flex-center">
                            <span class="spinner-mini mr-2"></span> Вычисляется...
                        </span>
                    </button>
                </div>
            </div>

            <!-- Transition Matrix -->
            <div class="card glass-panel" v-if="transitionMatrix">
                <div class="panel-header-sm"><h3>Матрица переходов</h3></div>
                <div class="matrix-grid" :style="{ gridTemplateColumns: `repeat(${nComponents}, 1fr)` }">
                    <div v-for="(row, i) in transitionMatrix" :key="i" class="matrix-row-group">
                        <div v-for="(prob, j) in row" :key="j" class="matrix-cell" 
                             :style="{ backgroundColor: `rgba(59, 130, 246, ${prob * 0.8})` }">
                            <span class="m-val">{{ (prob * 100).toFixed(0) }}%</span>
                            <span class="m-lbl">S{{i}}→S{{j}}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Regime Stats Legend -->
            <div class="card glass-panel mt-4" v-if="regimeStats.length">
                 <div class="panel-header-sm"><h3>Статистики режимов</h3></div>
                 <div class="stats-list">
                     <div class="stat-item" v-for="(stat, i) in regimeStats" :key="i">
                         <div class="stat-head">
                             <span class="dot" :class="getRegimeColorClass(i)"></span> 
                             <span class="s-name">{{ getRegimeName(i) }}</span>
                         </div>
                         <div class="stat-metrics">
                             <span>μ: {{ stat.ret }}%</span>
                             <span class="text-muted">σ: {{ stat.vol }}%</span>
                         </div>
                     </div>
                 </div>
            </div>

        </aside>

        <!-- RIGHT: Visualization -->
        <main class="main-panel">
            
            <!-- Chart 1: Price with Regimes -->
            <div class="card glass-panel chart-card">
                <div class="chart-header">
                    <h3>
                        Режимно-зависимое изменение цены актива
                        <span v-if="isPlaying" class="live-badge">● LIVE PLAYBACK</span>
                    </h3>
                    
                    <!-- PLAYBACK CONTROLS -->
                    <div class="playback-controls" v-if="chartData.length">
                        <button class="icon-btn" @click="togglePlay" title="Play/Pause">
                            <span v-if="isPlaying">⏸</span>
                            <span v-else>▶</span>
                        </button>
                        <div class="timeline-wrapper">
                            <input 
                                type="range" min="0" :max="chartData.length - 1" 
                                v-model.number="playbackIndex" @input="stopPlay" class="timeline-slider"
                            >
                            <div class="timeline-track" :style="{ width: (playbackIndex / (chartData.length - 1) * 100) + '%' }"></div>
                        </div>
                        <button class="icon-btn" @click="resetPlayback" title="Reset">↺</button>
                    </div>
                </div>

                <div class="chart-container">
                    <svg v-if="chartData.length" viewBox="0 0 800 250" preserveAspectRatio="none" class="regime-svg">
                         <!-- Background Bars (Sliced) -->
                         <rect v-for="(d, i) in chartData" :key="'bg-'+i"
                               v-show="i <= playbackIndex"
                               :x="scaleX(i)" y="0" 
                               :width="barWidth" height="250"
                               :fill="getRegimeColor(d.regime, 0.15)"
                         />
                        <!-- Price Line (Sliced) -->
                        <path :d="slicedPricePath" fill="none" stroke="#fff" stroke-width="1.5" />
                        
                        <!-- Cursor Line -->
                        <line v-if="playbackIndex < chartData.length - 1"
                              :x1="scaleX(playbackIndex)" y1="0" 
                              :x2="scaleX(playbackIndex)" y2="250" 
                              stroke="rgba(255,255,255,0.5)" stroke-dasharray="2" />
                    </svg>
                </div>
            </div>

            <!-- Chart 2: Rolling Volatility -->
            <div class="card glass-panel chart-card mt-4">
                <div class="chart-header">
                    <h3>Скользящая волатильность (20-дневное окно)</h3>
                </div>
                <div class="chart-container">
                    <svg v-if="chartData.length" viewBox="0 0 800 250" preserveAspectRatio="none" class="regime-svg">
                        <line v-for="i in 5" :key="i" x1="0" :y1="i*50" x2="800" :y2="i*50" stroke="rgba(255,255,255,0.05)" />
                        
                        <!-- Volatility Path (Sliced) -->
                        <path :d="slicedVolPath" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1" />
                        
                        <!-- Dots (Sliced) -->
                        <circle 
                            v-for="(d, i) in chartData" 
                            v-show="i <= playbackIndex"
                            :key="'v-'+i"
                            :cx="scaleX(i)" 
                            :cy="scaleYVol(d.vol)" 
                            r="2"
                            :fill="getRegimeColorHex(d.regime)"
                        />
                         <!-- Cursor Line -->
                        <line v-if="playbackIndex < chartData.length - 1"
                              :x1="scaleX(playbackIndex)" y1="0" 
                              :x2="scaleX(playbackIndex)" y2="250" 
                              stroke="rgba(255,255,255,0.3)" stroke-dasharray="2" />
                    </svg>
                </div>
            </div>

            <!-- Chart 3: Predicted Hidden States -->
            <div class="card glass-panel chart-card mt-4">
                <div class="chart-header">
                    <h3>Предсказанные скрытые состояния</h3>
                </div>
                <div class="chart-container">
                    <svg v-if="chartData.length" viewBox="0 0 800 200" preserveAspectRatio="none" class="regime-svg">
                        <line v-for="s in [0, 1, 2]" :key="'g-'+s" x1="0" :y1="scaleYState(s)" x2="800" :y2="scaleYState(s)" stroke="rgba(255,255,255,0.05)" stroke-dasharray="4"/>
                        <text x="10" :y="scaleYState(0) - 10" fill="rgba(255,255,255,0.3)" font-size="10">Stable (0)</text>
                        <text x="10" :y="scaleYState(1) - 10" fill="rgba(255,255,255,0.3)" font-size="10">Growth (1)</text>
                        <text x="10" :y="scaleYState(2) - 10" fill="rgba(255,255,255,0.3)" font-size="10">Stress (2)</text>

                        <!-- Scatter Points (Sliced) -->
                        <circle 
                            v-for="(d, i) in chartData" 
                            v-show="i <= playbackIndex"
                            :key="'s-'+i"
                            :cx="scaleX(i)" 
                            :cy="scaleYState(d.regime)" 
                            r="3"
                            :fill="getRegimeColorHex(d.regime)"
                            opacity="0.8"
                        />
                    </svg>
                </div>
            </div>

        </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useTaskStore } from '@/stores/tasks'
import ScrubInput from '@/components/common/ScrubInput.vue'

const taskStore = useTaskStore()
const selectedAsset = ref('SPY')
const nComponents = ref(3) 
const shockMultiplier = ref(1.0)
const isLoading = ref(false)

const transitionMatrix = ref<number[][] | null>(null)
const chartData = ref<any[]>([])
const regimeStats = ref<any[]>([])

// --- Playback State ---
const playbackIndex = ref(0)
const isPlaying = ref(false)
let animationFrame: number | null = null

// --- DYNAMIC ISLAND INTEGRATION ---
const runHMM = async () => {
    if (isLoading.value) return
    isLoading.value = true
    stopPlay() // Stop if running
    
    const taskId = taskStore.addTask(`Обучение HMM на ${selectedAsset.value}...`, 'simulation')

    try {
        taskStore.updateProgress(taskId, 15)
        await new Promise(r => setTimeout(r, 500)) 

        for(let i=30; i<=90; i+=15) {
            await new Promise(r => setTimeout(r, 200))
            taskStore.updateProgress(taskId, i)
        }

        generateMockResults()
        taskStore.updateProgress(taskId, 100)
        
        // Auto-Start Playback
        playbackIndex.value = 0
        togglePlay()

    } catch (e) {
        taskStore.failTask(taskId)
    } finally {
        isLoading.value = false
    }
}

// --- Playback Logic ---
const togglePlay = () => {
    if (isPlaying.value) {
        stopPlay()
    } else {
        if (playbackIndex.value >= chartData.value.length - 1) playbackIndex.value = 0
        isPlaying.value = true
        animate()
    }
}

const stopPlay = () => {
    isPlaying.value = false
    if (animationFrame) cancelAnimationFrame(animationFrame)
}

const resetPlayback = () => {
    stopPlay()
    playbackIndex.value = 0
}

const animate = () => {
    if (!isPlaying.value) return
    
    // Speed: 2 frames per tick
    const nextIdx = playbackIndex.value + 2
    if (nextIdx >= chartData.value.length) {
        playbackIndex.value = chartData.value.length - 1
        stopPlay()
    } else {
        playbackIndex.value = nextIdx
        animationFrame = requestAnimationFrame(animate)
    }
}

// Mock Logic
const generateMockResults = () => {
    const rows = nComponents.value
    const matrix = []
    for(let i=0; i<rows; i++) {
        const row = new Array(rows).fill(0.05)
        row[i] = 1 - (0.05 * (rows - 1)) 
        matrix.push(row)
    }
    transitionMatrix.value = matrix

    const data = []
    let price = 100
    let regime = 0
    let vol = 0.10 

    for(let i=0; i<250; i++) {
        const rand = Math.random()
        const probs = transitionMatrix.value[regime] || transitionMatrix.value[0]
        let cum = 0
        for(let k=0; k<probs.length; k++) {
            cum += probs[k]
            if(rand < cum) { regime = k; break; }
        }

        let drift = 0
        let shock = 0
        if(regime === 0) { drift = 0.0002; shock = 0.008 * shockMultiplier.value; } 
        else if(regime === 1) { drift = 0.001; shock = 0.012 * shockMultiplier.value; } 
        else { drift = -0.002; shock = 0.025 * shockMultiplier.value; } 

        const ret = drift + (Math.random() - 0.5) * 2 * shock
        price = price * (1 + ret)
        vol = vol * 0.9 + (Math.abs(ret) * Math.sqrt(252)) * 0.1 

        data.push({ price, regime, vol })
    }
    chartData.value = data
    playbackIndex.value = data.length - 1 // Default to end if not playing

    regimeStats.value = [
        { ret: '8.5', vol: (12.0 * shockMultiplier.value).toFixed(1) }, 
        { ret: '22.0', vol: (18.5 * shockMultiplier.value).toFixed(1) }, 
        { ret: '-15.4', vol: (45.2 * shockMultiplier.value).toFixed(1) } 
    ].slice(0, nComponents.value)
}

// --- Visual Helpers ---
const barWidth = computed(() => 800 / (chartData.value.length || 1))
const scaleX = (i: number) => i * barWidth.value

const scaleY = (p: number, min: number, max: number) => 250 - ((p - min) / (max - min)) * 230 - 10

const scaleYVol = (v: number) => {
    const maxVol = 0.80 
    const minVol = 0
    let norm = (v - minVol) / (maxVol - minVol)
    if(norm > 1) norm = 1
    if(norm < 0) norm = 0
    return 250 - (norm * 230) - 10
}

const scaleYState = (s: number) => {
    const step = 200 / (nComponents.value + 1)
    return 200 - (step * (s + 1))
}

// Sliced Paths for Animation
const slicedPricePath = computed(() => {
    if (!chartData.value.length) return ''
    const sliced = chartData.value.slice(0, playbackIndex.value + 1)
    
    // Scale based on GLOBAL min/max to avoid jumping
    const prices = chartData.value.map(d => d.price)
    const min = Math.min(...prices)
    const max = Math.max(...prices)
    
    return 'M ' + sliced.map((d, i) => 
        `${scaleX(i).toFixed(1)},${scaleY(d.price, min, max).toFixed(1)}`
    ).join(' L ')
})

const slicedVolPath = computed(() => {
    if (!chartData.value.length) return ''
    const sliced = chartData.value.slice(0, playbackIndex.value + 1)
    return 'M ' + sliced.map((d, i) => 
        `${scaleX(i).toFixed(1)},${scaleYVol(d.vol).toFixed(1)}`
    ).join(' L ')
})

// Labels & Colors
const getRegimeName = (r: number) => {
    if(r===0) return 'Stable'
    if(r===1) return 'Growth'
    return 'Stress'
}

const getRegimeColor = (r: number, alpha: number) => {
    if (r === 1) return `rgba(74, 222, 128, ${alpha})` 
    if (r === 2) return `rgba(248, 113, 113, ${alpha})` 
    return `rgba(59, 130, 246, ${alpha})` 
}

const getRegimeColorHex = (r: number) => {
    if (r === 1) return '#4ade80'
    if (r === 2) return '#f87171'
    return '#3b82f6'
}

const getRegimeColorClass = (r: number) => {
    if (r === 1) return 'bg-green'
    if (r === 2) return 'bg-red'
    return 'bg-blue'
}

const currentRegimeLabel = computed(() => {
    if (!chartData.value.length) return 'Unknown'
    const idx = Math.min(playbackIndex.value, chartData.value.length - 1)
    return getRegimeName(chartData.value[idx].regime)
})

const currentRegimeColor = computed(() => {
    if (!chartData.value.length) return 'bg-grey'
    const idx = Math.min(playbackIndex.value, chartData.value.length - 1)
    return getRegimeColorClass(chartData.value[idx].regime)
})

onUnmounted(() => {
    if (animationFrame) cancelAnimationFrame(animationFrame)
})

onMounted(() => {
    // Optionally auto-run on mount
    // runHMM()
})
</script>

<style scoped>
/* Reuse previous styles + specific ones */
.page-container { padding: 28px; max-width: 1400px; margin: 0 auto; height: 100vh; overflow-y: auto; color: #fff; }
.dashboard-grid { display: grid; grid-template-columns: 280px 1fr; gap: 24px; }
.left-panel { display: flex; flex-direction: column; gap: 20px; }
.main-panel { display: flex; flex-direction: column; gap: 20px; }

/* Header */
.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; }
.section-title { font-size: 24px; font-weight: 700; margin: 0; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }

/* Cards & Panels */
.card { background: rgba(20, 22, 28, 0.4); backdrop-filter: blur(40px); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; }
.glass-panel { box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
.panel-header-sm h3 { margin: 0 0 12px 0; font-size: 11px; text-transform: uppercase; color: rgba(255,255,255,0.5); font-weight: 600; }

/* Status Pill */
.status-pill { display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.05); padding: 6px 12px; border-radius: 20px; font-size: 12px; border: 1px solid rgba(255,255,255,0.1); transition: all 0.2s; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.bg-green { background: #4ade80; }
.bg-red { background: #f87171; }
.bg-blue { background: #3b82f6; } 
.bg-grey { background: #555; }

/* Playback Controls (NEW) */
.playback-controls { display: flex; align-items: center; gap: 12px; background: rgba(0,0,0,0.3); padding: 4px 12px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); }
.icon-btn { background: none; border: none; color: #fff; cursor: pointer; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; border-radius: 50%; }
.icon-btn:hover { background: rgba(255,255,255,0.1); }
.timeline-wrapper { position: relative; width: 140px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; display: flex; align-items: center; }
.timeline-slider { position: absolute; width: 100%; height: 100%; opacity: 0; cursor: pointer; z-index: 2; margin: 0; }
.timeline-track { height: 100%; background: #3b82f6; border-radius: 2px; pointer-events: none; }
.live-badge { font-size: 10px; color: #ef4444; margin-left: 8px; animation: blink 1s infinite; }
@keyframes blink { 50% { opacity: 0.5; } }

/* Matrix */
.matrix-grid { display: grid; gap: 4px; }
.matrix-row-group { display: contents; }
.matrix-cell { padding: 8px; border-radius: 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #fff; font-size: 11px; }
.m-val { font-weight: 700; }
.m-lbl { font-size: 9px; opacity: 0.7; }

/* Stats List */
.stats-list { display: flex; flex-direction: column; gap: 12px; }
.stat-item { display: flex; justify-content: space-between; align-items: center; font-size: 13px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05); }
.stat-item:last-child { border-bottom: none; }
.stat-head { display: flex; align-items: center; gap: 8px; }
.stat-metrics { display: flex; gap: 12px; font-family: monospace; }
.text-muted { color: rgba(255,255,255,0.4); }
.text-accent { color: #3b82f6; }

/* Charts */
.chart-card { min-height: 250px; display: flex; flex-direction: column; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; height: 32px; }
.chart-header h3 { margin: 0; font-size: 14px; font-weight: 600; }
.sub-label { font-size: 11px; color: rgba(255,255,255,0.4); font-style: italic; }
.legend { display: flex; gap: 12px; font-size: 11px; }
.l-item { display: flex; align-items: center; gap: 6px; color: rgba(255,255,255,0.7); }
.chart-container { flex: 1; position: relative; width: 100%; overflow: hidden; }
.regime-svg { width: 100%; height: 100%; }

/* Form Controls */
.controls-form { display: flex; flex-direction: column; gap: 12px; }
.input-group { display: flex; flex-direction: column; gap: 4px; }
.lbl { font-size: 11px; color: rgba(255,255,255,0.5); }
.glass-select { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: #fff; padding: 8px; border-radius: 6px; width: 100%; outline: none; }
.divider { height: 1px; background: rgba(255,255,255,0.1); margin: 6px 0; }
.btn { border: none; padding: 10px; border-radius: 8px; cursor: pointer; color: #fff; font-weight: 600; font-size: 12px; }
.btn-primary-gradient { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.btn-primary-gradient:disabled { opacity: 0.7; cursor: not-allowed; }
.flex-center { display: flex; align-items: center; justify-content: center; }
.mr-2 { margin-right: 8px; }
.mt-4 { margin-top: 16px; }
.mt-2 { margin-top: 8px; }
.w-full { width: 100%; }
.spinner-mini { width: 12px; height: 12px; border: 2px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>

