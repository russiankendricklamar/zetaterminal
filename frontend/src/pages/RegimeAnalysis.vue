<!-- src/pages/RegimeAnalysis.vue -->
<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Анализ рыночных режимов</h1>
        <p class="section-subtitle">HMM: Классификация скрытых состояний рынка</p>
      </div>
      
      <div class="header-actions">
         <div class="glass-pill status-pill">
            <span class="dot" :class="currentRegimeColor"></span>
            <span class="status-label">Текущий режим: <b class="text-white">{{ currentRegimeLabel }}</b></span>
         </div>
      </div>
    </div>

    <div class="dashboard-grid">
        
        <!-- LEFT PANEL: Controls, Matrix, Stats -->
        <aside class="left-panel">
            
            <!-- Controls Card -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Параметры модели</h3></div>
                
                <div class="controls-form">
                    <!-- Asset Select -->
                    <div class="input-group">
                        <label class="lbl">Актив</label>
                        <div class="select-wrapper">
                            <select v-model="selectedAsset" class="glass-select full-width">
                                <option value="SPY">S&P 500 (SPY)</option>
                                <option value="QQQ">Nasdaq 100 (QQQ)</option>
                                <option value="BTC">Bitcoin (BTC)</option>
                                <option value="IMOEX">IMOEX Index</option>
                            </select>
                        </div>
                    </div>
                    
                    <!-- N States -->
                    <div class="input-group mt-2">
                        <label class="lbl">Количество режимов</label>
                        <div class="scrub-row">
                            <ScrubInput 
                                v-model="nComponents" 
                                :min="2" :max="4" :step="1" 
                                class="text-accent font-bold"
                            />
                            <span class="unit">states</span>
                        </div>
                    </div>

                    <!-- Shock Multiplier -->
                    <div class="input-group mt-2">
                        <label class="lbl">Множитель шока (Vol Shock)</label>
                        <div class="scrub-row">
                            <ScrubInput 
                                v-model="shockMultiplier" 
                                :min="0.5" :max="3.0" :step="0.1" :decimals="1"
                                suffix="x"
                                class="text-accent font-bold"
                            />
                        </div>
                    </div>

                    <!-- Run Button -->
                    <button @click="runHMM" :disabled="isLoading" class="btn-primary-gradient mt-6">
                        <span v-if="!isLoading">Запустить анализ</span>
                        <span v-else class="flex items-center gap-2">
                            <span class="spinner-mini"></span> Обучение...
                        </span>
                    </button>
                </div>
            </div>

            <!-- Transition Matrix -->
            <transition name="fade">
            <div class="glass-card panel" v-if="transitionMatrix">
                <div class="panel-header"><h3>Матрица переходов</h3></div>
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
            </transition>

            <!-- Regime Stats Legend -->
            <transition name="fade">
            <div class="glass-card panel" v-if="regimeStats.length">
                 <div class="panel-header"><h3>Статистика режимов</h3></div>
                 <div class="stats-list">
                     <div class="stat-item" v-for="(stat, i) in regimeStats" :key="i">
                         <div class="stat-head">
                             <span class="dot" :class="getRegimeColorClass(i)"></span> 
                             <span class="s-name">{{ getRegimeName(i) }}</span>
                         </div>
                         <div class="stat-metrics">
                             <span :class="parseFloat(stat.ret) > 0 ? 'text-green' : 'text-red'">μ: {{ stat.ret }}%</span>
                             <span class="text-muted">σ: {{ stat.vol }}%</span>
                         </div>
                     </div>
                 </div>
            </div>
            </transition>

        </aside>

        <!-- RIGHT PANEL: Visualization -->
        <main class="main-panel">
            
            <!-- Chart 1: Price with Regimes (UPDATED HEIGHT: 400px) -->
            <div class="glass-card chart-card">
                <div class="chart-header">
                    <div class="ch-left">
                        <h3>Динамика цены и режимы</h3>
                        <span v-if="isPlaying" class="badge-live">● LIVE</span>
                    </div>
                    
                    <!-- PLAYBACK CONTROLS -->
                    <div class="playback-controls" v-if="chartData.length">
                        <button class="icon-btn" @click="togglePlay" title="Play/Pause">
                            <span v-if="isPlaying">⏸</span>
                            <span v-else>▶</span>
                        </button>
                        
                        <div class="timeline-wrapper">
                            <input 
                                type="range" min="0" :max="chartData.length - 1" 
                                v-model.number="playbackIndex" 
                                @input="stopPlay" 
                                class="timeline-slider"
                            >
                            <div class="timeline-track" :style="{ width: progressPercent + '%' }"></div>
                            <div class="timeline-thumb" :style="{ left: progressPercent + '%' }"></div>
                        </div>

                        <button class="icon-btn" @click="resetPlayback" title="Reset">↺</button>
                    </div>
                </div>

                <div class="chart-container">
                    <!-- VIEWBOX UPDATED TO 800 400 -->
                    <svg v-if="chartData.length" viewBox="0 0 800 400" preserveAspectRatio="none" class="regime-svg">
                         <!-- Background Bars -->
                         <rect v-for="(d, i) in chartData" :key="'bg-'+i"
                               v-show="i <= playbackIndex"
                               :x="scaleX(i)" y="0" 
                               :width="barWidth + 0.5" height="400"
                               :fill="getRegimeColor(d.regime, 0.15)"
                         />
                        
                        <!-- Grid Lines (re-calculated for 400px) -->
                        <line x1="0" y1="100" x2="800" y2="100" stroke="rgba(255,255,255,0.05)" />
                        <line x1="0" y1="200" x2="800" y2="200" stroke="rgba(255,255,255,0.05)" />
                        <line x1="0" y1="300" x2="800" y2="300" stroke="rgba(255,255,255,0.05)" />

                        <!-- Price Line -->
                        <path :d="slicedPricePath" fill="none" stroke="#fff" stroke-width="2" stroke-linejoin="round" filter="drop-shadow(0 0 4px rgba(0,0,0,0.5))" />
                        
                        <!-- Cursor Line -->
                        <line v-if="playbackIndex < chartData.length - 1"
                              :x1="scaleX(playbackIndex)" y1="0" 
                              :x2="scaleX(playbackIndex)" y2="400" 
                              stroke="rgba(255,255,255,0.8)" stroke-dasharray="3" />
                    </svg>

                    <div v-else class="empty-state">
                        <div v-if="isLoading" class="spinner-large"></div>
                        <span v-else>Нажмите «Запустить анализ» для генерации</span>
                    </div>
                </div>
            </div>

            <!-- Chart 2: Rolling Volatility (UPDATED HEIGHT: 160px) -->
            <div class="glass-card chart-card mt-4">
                <div class="chart-header">
                    <h3>Скользящая волатильность (20D Rolling Vol)</h3>
                </div>
                <div class="chart-container-sm">
                    <!-- VIEWBOX UPDATED TO 800 160 -->
                    <svg v-if="chartData.length" viewBox="0 0 800 160" preserveAspectRatio="none" class="regime-svg">
                        <line v-for="i in 3" :key="i" x1="0" :y1="i*40" x2="800" :y2="i*40" stroke="rgba(255,255,255,0.05)" />
                        
                        <!-- Colored Dots -->
                        <circle 
                            v-for="(d, i) in chartData" 
                            v-show="i <= playbackIndex"
                            :key="'v-'+i"
                            :cx="scaleX(i)" 
                            :cy="scaleYVol(d.vol)" 
                            r="2"
                            :fill="getRegimeColorHex(d.regime)"
                        />
                    </svg>
                </div>
            </div>

            <!-- Chart 3: Predicted Hidden States (UPDATED HEIGHT: 160px) -->
            <div class="glass-card chart-card mt-4">
                <div class="chart-header">
                    <h3>Предсказанные скрытые состояния</h3>
                </div>
                <div class="chart-container-sm">
                    <!-- VIEWBOX UPDATED TO 800 160 -->
                    <svg v-if="chartData.length" viewBox="0 0 800 160" preserveAspectRatio="none" class="regime-svg">
                        <!-- State Lines -->
                        <line v-for="s in [0, 1, 2]" :key="'g-'+s" x1="0" :y1="scaleYState(s)" x2="800" :y2="scaleYState(s)" stroke="rgba(255,255,255,0.05)" stroke-dasharray="4"/>
                        
                        <!-- Labels -->
                        <text x="10" :y="scaleYState(0) - 8" fill="rgba(255,255,255,0.2)" font-size="10">Stable (0)</text>
                        <text x="10" :y="scaleYState(1) - 8" fill="rgba(255,255,255,0.2)" font-size="10">Growth (1)</text>
                        <text x="10" :y="scaleYState(2) - 8" fill="rgba(255,255,255,0.2)" font-size="10">Stress (2)</text>

                        <!-- Scatter Points -->
                        <circle 
                            v-for="(d, i) in chartData" 
                            v-show="i <= playbackIndex"
                            :key="'s-'+i"
                            :cx="scaleX(i)" 
                            :cy="scaleYState(d.regime)" 
                            r="3"
                            :fill="getRegimeColorHex(d.regime)"
                        />
                    </svg>
                </div>
            </div>

        </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
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

const playbackIndex = ref(0)
const isPlaying = ref(false)
let animationFrame: number | null = null

const progressPercent = computed(() => {
    if (!chartData.value.length) return 0
    return (playbackIndex.value / (chartData.value.length - 1)) * 100
})

const runHMM = async () => {
    if (isLoading.value) return
    isLoading.value = true
    stopPlay()
    
    const taskId = taskStore.addTask(`Обучение HMM на ${selectedAsset.value}...`, 'simulation')

    try {
        taskStore.updateProgress(taskId, 10)
        await new Promise(r => setTimeout(r, 600)) 

        for(let i=30; i<=90; i+=20) {
            await new Promise(r => setTimeout(r, 300))
            taskStore.updateProgress(taskId, i)
        }

        generateMockResults()
        taskStore.updateProgress(taskId, 100)
        
        playbackIndex.value = 0
        togglePlay()

    } catch (e) {
        taskStore.failTask(taskId)
    } finally {
        isLoading.value = false
    }
}

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
    const nextIdx = playbackIndex.value + 3 
    if (nextIdx >= chartData.value.length) {
        playbackIndex.value = chartData.value.length - 1
        stopPlay()
    } else {
        playbackIndex.value = nextIdx
        animationFrame = requestAnimationFrame(animate)
    }
}

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

    for(let i=0; i<300; i++) {
        const rand = Math.random()
        const probs = transitionMatrix.value[regime] || transitionMatrix.value[0]
        let cum = 0
        for(let k=0; k<probs.length; k++) {
            cum += probs[k]
            if(rand < cum) { regime = k; break; }
        }

        let drift = 0
        let shock = 0
        if(regime === 0) { drift = 0.0005; shock = 0.008 * shockMultiplier.value; } 
        else if(regime === 1) { drift = 0.0015; shock = 0.012 * shockMultiplier.value; } 
        else if(regime === 2) { drift = -0.003; shock = 0.035 * shockMultiplier.value; } 
        else { drift = -0.001; shock = 0.015 * shockMultiplier.value; } 

        const ret = drift + (Math.random() - 0.5) * 2 * shock
        price = price * (1 + ret)
        vol = vol * 0.94 + (Math.abs(ret) * Math.sqrt(252)) * 0.06 

        data.push({ price, regime, vol })
    }
    chartData.value = data
    playbackIndex.value = data.length - 1

    regimeStats.value = [
        { ret: '8.5', vol: (12.0 * shockMultiplier.value).toFixed(1) }, 
        { ret: '22.0', vol: (18.5 * shockMultiplier.value).toFixed(1) }, 
        { ret: '-15.4', vol: (45.2 * shockMultiplier.value).toFixed(1) },
        { ret: '-5.2', vol: (25.1 * shockMultiplier.value).toFixed(1) }
    ].slice(0, nComponents.value)
}

// --- Visual Scales (UPDATED FOR NEW HEIGHTS) ---
const barWidth = computed(() => 800 / (chartData.value.length || 1))
const scaleX = (i: number) => i * barWidth.value

// Updated for 400px height
const scaleY = (p: number, min: number, max: number) => {
    const range = max - min || 1
    // Map to 400px height, leave 20px padding top/bottom
    return 400 - ((p - min) / range) * 360 - 20
}

// Updated for 160px height
const scaleYVol = (v: number) => {
    const maxVol = 0.80 
    const minVol = 0
    let norm = (v - minVol) / (maxVol - minVol)
    if(norm > 1) norm = 1
    if(norm < 0) norm = 0
    return 160 - (norm * 140) - 10
}

// Updated for 160px height
const scaleYState = (s: number) => {
    // 3 states: 0, 1, 2 distributed in 160px
    if (s === 0) return 130 // Stable (Bottom)
    if (s === 1) return 80  // Growth (Middle)
    return 30               // Stress (Top)
}

const slicedPricePath = computed(() => {
    if (!chartData.value.length) return ''
    const sliced = chartData.value.slice(0, playbackIndex.value + 1)
    const prices = chartData.value.map(d => d.price)
    const min = Math.min(...prices)
    const max = Math.max(...prices)
    return 'M ' + sliced.map((d, i) => `${scaleX(i).toFixed(1)},${scaleY(d.price, min, max).toFixed(1)}`).join(' L ')
})

const getRegimeName = (r: number) => {
    if(r===0) return 'Stable (Low Vol)'
    if(r===1) return 'Growth (Bull)'
    if(r===2) return 'Stress (Bear)'
    return 'Correction'
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
    if (!chartData.value.length) return '—'
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
</script>

<style scoped>
/* Main Layout */
.page-container { padding: 24px 32px; max-width: 1500px; margin: 0 auto; height: 100%; display: flex; flex-direction: column; gap: 24px; }
.dashboard-grid { display: grid; grid-template-columns: 320px 1fr; gap: 24px; flex: 1; min-height: 0; }
.left-panel, .main-panel { display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }

/* Header */
.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px; flex-shrink: 0; }
.section-title { font-size: 28px; font-weight: 700; margin: 0; color: #fff; letter-spacing: -0.01em; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }

/* Glass Components */
.glass-card {
  background: rgba(30, 32, 40, 0.4); backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 24px;
  box-shadow: 0 20px 50px -10px rgba(0,0,0,0.5);
}
.glass-pill {
  display: flex; align-items: center; gap: 8px; padding: 4px 12px;
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 99px; height: 36px;
}
.panel { padding: 24px; }
.panel-header h3 { margin: 0 0 16px 0; font-size: 11px; text-transform: uppercase; color: rgba(255,255,255,0.5); font-weight: 700; letter-spacing: 0.05em; }

/* Controls */
.controls-form { display: flex; flex-direction: column; gap: 14px; }
.input-group { display: flex; flex-direction: column; gap: 6px; }
.lbl { font-size: 11px; color: rgba(255,255,255,0.5); font-weight: 600; text-transform: uppercase; }
.glass-select { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: #fff; padding: 10px 12px; border-radius: 12px; width: 100%; outline: none; transition: 0.2s; cursor: pointer; }
.glass-select:focus { border-color: #3b82f6; background: rgba(0,0,0,0.5); }
.divider { height: 1px; background: rgba(255,255,255,0.1); margin: 8px 0; }
.scrub-row { display: flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05); padding: 8px 12px; border-radius: 12px; }
.unit { font-size: 12px; color: rgba(255,255,255,0.4); }

/* Buttons */
.btn-primary-gradient {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none; padding: 12px; border-radius: 12px;
  color: #fff; font-weight: 700; font-size: 13px; cursor: pointer;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4); transition: all 0.2s;
}
.btn-primary-gradient:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 12px 25px rgba(37, 99, 235, 0.5); }
.btn-primary-gradient:disabled { opacity: 0.6; cursor: not-allowed; }

/* Matrix */
.matrix-grid { display: grid; gap: 4px; }
.matrix-row-group { display: contents; }
.matrix-cell { padding: 12px 8px; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #fff; font-size: 12px; }
.m-val { font-weight: 700; font-family: "SF Mono", monospace; font-size: 14px; }
.m-lbl { font-size: 9px; opacity: 0.7; margin-top: 2px; }

/* Stats */
.stats-list { display: flex; flex-direction: column; gap: 10px; }
.stat-item { display: flex; justify-content: space-between; align-items: center; font-size: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05); }
.stat-head { display: flex; align-items: center; gap: 10px; }
.stat-metrics { display: flex; gap: 12px; font-family: "SF Mono", monospace; font-weight: 600; }
.s-name { font-weight: 600; color: #fff; }

/* Charts */
.chart-card { padding: 24px; display: flex; flex-direction: column; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.ch-left { display: flex; align-items: center; gap: 12px; }
.chart-header h3 { margin: 0; font-size: 13px; font-weight: 700; color: #fff; text-transform: uppercase; letter-spacing: 0.05em; }
.badge-live { font-size: 10px; color: #ef4444; font-weight: 700; animation: blink 1.5s infinite; }
@keyframes blink { 50% { opacity: 0.5; } }

/* Playback */
.playback-controls { display: flex; align-items: center; gap: 14px; background: rgba(0, 0, 0, 0.4); padding: 6px 14px; border-radius: 99px; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
.icon-btn { background: none; border: none; color: #fff; cursor: pointer; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; opacity: 0.8; transition: 0.2s; font-size: 14px; }
.icon-btn:hover { opacity: 1; background: rgba(255,255,255,0.1); border-radius: 50%; transform: scale(1.1); }
.timeline-wrapper { position: relative; width: 200px; height: 6px; background: rgba(255, 255, 255, 0.1); border-radius: 3px; display: flex; align-items: center; }
.timeline-slider { position: absolute; width: 100%; height: 20px; top: 50%; transform: translateY(-50%); opacity: 0; cursor: pointer; z-index: 3; margin: 0; }
.timeline-track { height: 100%; background: #3b82f6; border-radius: 3px; pointer-events: none; }
.timeline-thumb { position: absolute; top: 50%; width: 12px; height: 12px; background: #fff; border-radius: 50%; transform: translate(-50%, -50%); box-shadow: 0 0 10px rgba(59, 130, 246, 0.5); z-index: 2; pointer-events: none; transition: transform 0.1s; }
.timeline-wrapper:hover .timeline-thumb { transform: translate(-50%, -50%) scale(1.3); }

/* SVG */
.chart-container { flex: 1; width: 100%; position: relative; min-height: 400px; } /* Increased Height */
.chart-container-sm { height: 160px; width: 100%; position: relative; } /* Increased Height */
.regime-svg { width: 100%; height: 100%; }
.empty-state { height: 400px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: rgba(255,255,255,0.3); font-size: 13px; gap: 12px; }

/* Colors & Utils */
.dot { width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 6px currentColor; }
.bg-green { background: #4ade80; color: #4ade80; }
.bg-red { background: #f87171; color: #f87171; }
.bg-blue { background: #3b82f6; color: #3b82f6; }
.bg-orange { background: #fbbf24; color: #fbbf24; }
.bg-grey { background: #555; }
.text-green { color: #4ade80; }
.text-red { color: #f87171; }
.text-muted { color: rgba(255,255,255,0.4); }
.text-accent { color: #3b82f6; }
.font-bold { font-weight: 700; }
.mt-2 { margin-top: 8px; }
.mt-4 { margin-top: 16px; }
.mt-6 { margin-top: 24px; }

.spinner-mini { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 1s linear infinite; }
.spinner-large { width: 32px; height: 32px; border: 3px solid rgba(255,255,255,0.1); border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .dashboard-grid { grid-template-columns: 1fr; }
}
</style>