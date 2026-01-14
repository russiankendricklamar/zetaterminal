<!-- src/pages/SpectralRegimeAnalysis.vue -->
<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Комплексный анализ скрытых рыночных режимов</h1>
        <p class="section-subtitle">Спектральная декомпозиция через мероморфное расширение</p>
      </div>
      
      <div class="header-actions">
        <div class="glass-pill status-pill" v-if="analysisResult">
          <span class="dot" :style="{ background: currentRegimeColor }"></span>
          <span class="status-label">
            Режим: <b class="text-white">{{ currentRegimeType }}</b>
          </span>
        </div>
        <div class="glass-pill" v-if="analysisResult">
          <span :class="analysisResult.summary.stability.is_stable ? 'text-green' : 'text-red'">
            {{ analysisResult.summary.stability.is_stable ? 'Стабильный' : 'Нестабильный' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="dashboard-grid">
      
      <!-- LEFT PANEL: Controls -->
      <aside class="left-panel">
        
        <!-- Asset Selection -->
        <div class="glass-card panel">
          <div class="panel-header"><h3>Выбор актива</h3></div>
          
          <div class="controls-form">
            <!-- Category Select -->
            <div class="input-group">
              <label class="lbl">Категория</label>
              <select v-model="selectedCategory" class="glass-select full-width">
                <option value="stocks">Акции (US)</option>
                <option value="crypto">Криптовалюты</option>
                <option value="commodities">Сырьё</option>
                <option value="bonds">Облигации</option>
                <option value="forex">Валюты</option>
                <option value="russia">Россия</option>
              </select>
            </div>
            
            <!-- Asset Select -->
            <div class="input-group mt-2">
              <label class="lbl">Актив</label>
              <select v-model="selectedTicker" class="glass-select full-width">
                <option v-for="asset in availableAssets" :key="asset.ticker" :value="asset.ticker">
                  {{ asset.name }} ({{ asset.ticker }})
                </option>
              </select>
            </div>
            
            <!-- Period -->
            <div class="input-group mt-2">
              <label class="lbl">Период (дни)</label>
              <select v-model="periodDays" class="glass-select full-width">
                <option :value="126">6 месяцев (126)</option>
                <option :value="252">1 год (252)</option>
                <option :value="504">2 года (504)</option>
                <option :value="756">3 года (756)</option>
                <option :value="1260">5 лет (1260)</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Analysis Parameters -->
        <div class="glass-card panel">
          <div class="panel-header"><h3>Параметры анализа</h3></div>
          
          <div class="controls-form">
            <!-- N Poles -->
            <div class="input-group">
              <label class="lbl">Количество полюсов (M)</label>
              <div class="range-row">
                <input type="range" v-model.number="nPoles" min="3" max="12" step="1" class="range-slider" />
                <span class="range-value">{{ nPoles }}</span>
              </div>
              <span class="hint">Рекомендуется 5-8</span>
            </div>
            
            <!-- Window Size -->
            <div class="input-group mt-3">
              <label class="lbl">Размер окна (W)</label>
              <div class="range-row">
                <input type="range" v-model.number="windowSize" min="10" max="50" step="5" class="range-slider" />
                <span class="range-value">{{ windowSize }} дн.</span>
              </div>
              <span class="hint">Для динамического анализа</span>
            </div>
            
            <!-- Run Button -->
            <button @click="runAnalysis" :disabled="isLoading" class="btn-primary-gradient mt-6">
              <span v-if="!isLoading">Запустить анализ</span>
              <span v-else class="flex items-center gap-2">
                <span class="spinner-mini"></span> {{ loadingStatus }}
              </span>
            </button>
          </div>
        </div>

        <!-- Current Metrics -->
        <transition name="fade">
          <div class="glass-card panel" v-if="analysisResult">
            <div class="panel-header"><h3>Текущие метрики</h3></div>
            
            <div class="metrics-grid">
              <div class="metric-item">
                <span class="metric-label">Режимов</span>
                <span class="metric-value text-blue">{{ analysisResult.summary.n_regimes }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Полюсов</span>
                <span class="metric-value">{{ analysisResult.summary.n_poles }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Энтропия</span>
                <span class="metric-value" :class="entropyClass">
                  {{ entropyValue }}
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Качество</span>
                <span class="metric-value text-green">
                  {{ analysisResult.summary.reconstruction.pct_explained.toFixed(1) }}%
                </span>
              </div>
            </div>
            
            <!-- Stability Check -->
            <div class="stability-badge" :class="analysisResult.summary.stability.is_stable ? 'stable' : 'unstable'">
              <span v-if="analysisResult.summary.stability.is_stable">
                Все полюсы внутри единичного круга
              </span>
              <span v-else>
                {{ analysisResult.summary.stability.n_violations }} нестабильных полюсов
              </span>
            </div>
            
            <!-- Minimum Phase -->
            <div class="stability-badge mt-2" :class="analysisResult.summary.minimum_phase.is_minimum_phase ? 'stable' : 'warning'">
              <span v-if="analysisResult.summary.minimum_phase.is_minimum_phase">
                Минимально-фазовая система
              </span>
              <span v-else>
                Non-minimum phase (признак кризиса)
              </span>
            </div>
          </div>
        </transition>

        <!-- Regime Stats -->
        <transition name="fade">
          <div class="glass-card panel" v-if="analysisResult && regimeStats.length">
            <div class="panel-header"><h3>Параметры режимов</h3></div>
            
            <div class="regime-list">
              <div 
                v-for="(regime, idx) in regimeStats" 
                :key="idx" 
                class="regime-item"
                :class="{ active: currentRegimeIndex === idx }"
              >
                <div class="regime-header">
                  <span class="regime-dot" :style="{ background: getRegimeColor(idx) }"></span>
                  <span class="regime-name">Режим {{ idx }}</span>
                  <span class="regime-type" :style="{ color: getRegimeTypeColor(regime.type) }">
                    {{ getRegimeTypeName(regime.type) }}
                  </span>
                </div>
                <div class="regime-metrics">
                  <div class="rm-item">
                    <span class="rm-label">|λ|</span>
                    <span class="rm-value">{{ regime.radius.toFixed(3) }}</span>
                  </div>
                  <div class="rm-item">
                    <span class="rm-label">τ</span>
                    <span class="rm-value">{{ formatDuration(regime.duration) }}</span>
                  </div>
                  <div class="rm-item">
                    <span class="rm-label">I</span>
                    <span class="rm-value">{{ regime.intensity.toFixed(3) }}</span>
                  </div>
                </div>
                <div class="regime-bar">
                  <div 
                    class="regime-bar-fill" 
                    :style="{ 
                      width: getRegimeTimePercent(idx) + '%',
                      background: getRegimeColor(idx)
                    }"
                  ></div>
                  <span class="regime-bar-label">{{ getRegimeTimePercent(idx).toFixed(0) }}% времени</span>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </aside>

      <!-- RIGHT PANEL: Visualizations -->
      <main class="main-panel">
        
        <!-- Poles Diagram -->
        <div class="glass-card chart-card">
          <div class="chart-header">
            <h3>Диаграмма полюсов в комплексной плоскости</h3>
            <span class="badge-info" v-if="analysisResult">{{ analysisResult.summary.n_poles }} полюсов</span>
          </div>
          <div class="poles-container">
            <svg v-if="analysisResult" viewBox="-1.5 -1.5 3 3" preserveAspectRatio="xMidYMid meet" class="poles-svg">
              <!-- Grid -->
              <line x1="-1.5" y1="0" x2="1.5" y2="0" stroke="rgba(255,255,255,0.1)" stroke-width="0.01" />
              <line x1="0" y1="-1.5" x2="0" y2="1.5" stroke="rgba(255,255,255,0.1)" stroke-width="0.01" />
              
              <!-- Unit Circle -->
              <circle cx="0" cy="0" r="1" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="0.02" stroke-dasharray="0.05 0.03" />
              <circle cx="0" cy="0" r="0.5" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.01" />
              
              <!-- Stability zones -->
              <circle cx="0" cy="0" r="0.8" fill="rgba(74, 222, 128, 0.05)" stroke="none" />
              <circle cx="0" cy="0" r="0.95" fill="none" stroke="rgba(251, 191, 36, 0.2)" stroke-width="0.01" />
              
              <!-- All Poles -->
              <g v-for="(pole, i) in allPoles" :key="'pole-' + i">
                <circle 
                  :cx="pole.real" 
                  :cy="-pole.imag" 
                  r="0.04" 
                  :fill="getPoleColor(pole.radius)"
                  stroke="rgba(255,255,255,0.5)"
                  stroke-width="0.01"
                />
              </g>
              
              <!-- Regime Poles (larger) -->
              <g v-for="(pole, i) in regimePoles" :key="'regime-pole-' + i">
                <circle 
                  :cx="pole.real" 
                  :cy="-pole.imag" 
                  r="0.08" 
                  :fill="getRegimeColor(pole.regime)"
                  stroke="white"
                  stroke-width="0.015"
                  class="regime-pole-marker"
                />
                <text 
                  :x="pole.real + 0.1" 
                  :y="-pole.imag" 
                  fill="white" 
                  font-size="0.12"
                  alignment-baseline="middle"
                >
                  R{{ pole.regime }}
                </text>
              </g>
              
              <!-- Labels -->
              <text x="1.35" y="0.05" fill="rgba(255,255,255,0.4)" font-size="0.08">Re</text>
              <text x="0.05" y="-1.35" fill="rgba(255,255,255,0.4)" font-size="0.08">Im</text>
              <text x="1.02" y="0.12" fill="rgba(255,255,255,0.3)" font-size="0.06">|z|=1</text>
            </svg>
            <div v-else class="empty-state">
              <span>Запустите анализ для отображения диаграммы полюсов</span>
            </div>
          </div>
        </div>

        <!-- Price & Regimes Chart -->
        <div class="glass-card chart-card mt-4">
          <div class="chart-header">
            <div class="ch-left">
              <h3>Динамика и режимы</h3>
              <span class="badge-ticker" v-if="assetMetadata">{{ assetMetadata.ticker }}</span>
            </div>
            <div class="playback-controls" v-if="analysisResult">
              <button class="icon-btn" @click="togglePlayback" :title="isPlaying ? 'Пауза' : 'Воспроизвести'">
                <span v-if="isPlaying">⏸</span>
                <span v-else>▶</span>
              </button>
              <div class="timeline-wrapper">
                <input 
                  type="range" 
                  :min="0" 
                  :max="maxPlaybackIndex" 
                  v-model.number="playbackIndex" 
                  @input="stopPlayback"
                  class="timeline-slider"
                />
                <div class="timeline-track" :style="{ width: playbackProgress + '%' }"></div>
              </div>
              <button class="icon-btn" @click="resetPlayback" title="Сброс">↺</button>
            </div>
          </div>
          <div class="chart-container">
            <svg v-if="analysisResult && dynamicsData" viewBox="0 0 800 300" preserveAspectRatio="none" class="dynamics-svg">
              <!-- Background regime bars -->
              <rect 
                v-for="(regime, i) in visibleRegimes" 
                :key="'bg-' + i"
                :x="scaleX(i)" 
                y="0" 
                :width="barWidth + 0.5" 
                height="300"
                :fill="getRegimeColor(regime)" 
                fill-opacity="0.15"
              />
              
              <!-- Grid -->
              <line v-for="y in [75, 150, 225]" :key="'grid-' + y" x1="0" :y1="y" x2="800" :y2="y" stroke="rgba(255,255,255,0.05)" />
              
              <!-- Price line -->
              <path :d="pricePath" fill="none" stroke="white" stroke-width="1.5" stroke-linejoin="round" />
              
              <!-- Cursor -->
              <line 
                v-if="playbackIndex < maxPlaybackIndex"
                :x1="scaleX(playbackIndex)" 
                y1="0" 
                :x2="scaleX(playbackIndex)" 
                y2="300" 
                stroke="rgba(255,255,255,0.6)" 
                stroke-dasharray="4"
              />
            </svg>
            <div v-else class="empty-state">
              <div v-if="isLoading" class="spinner-large"></div>
              <span v-else>Нажмите «Запустить анализ»</span>
            </div>
          </div>
        </div>

        <!-- Regime Energies Chart -->
        <div class="glass-card chart-card mt-4">
          <div class="chart-header">
            <h3>Энергии режимов (нормализованные)</h3>
          </div>
          <div class="chart-container-sm">
            <svg v-if="analysisResult && dynamicsData" viewBox="0 0 800 160" preserveAspectRatio="none" class="energy-svg">
              <!-- Stacked area for each regime -->
              <g v-for="k in Array.from({length: analysisResult.summary.n_regimes}, (_, i) => i).reverse()" :key="'energy-' + k">
                <path 
                  :d="getEnergyPath(k)" 
                  :fill="getRegimeColor(k)" 
                  fill-opacity="0.6"
                  stroke="none"
                />
              </g>
            </svg>
            <div v-else-if="!isLoading" class="empty-state-sm">
              <span>Данные отсутствуют</span>
            </div>
          </div>
        </div>

        <!-- Entropy Chart -->
        <div class="glass-card chart-card mt-4">
          <div class="chart-header">
            <h3>Энтропия режимности</h3>
            <span class="badge-info" v-if="analysisResult">
              Средняя: {{ analysisResult.summary.entropy_stats.mean?.toFixed(3) || 'N/A' }}
            </span>
          </div>
          <div class="chart-container-sm">
            <svg v-if="analysisResult && dynamicsData" viewBox="0 0 800 120" preserveAspectRatio="none" class="entropy-svg">
              <!-- Entropy area -->
              <path :d="entropyPath" fill="rgba(139, 92, 246, 0.3)" stroke="#8b5cf6" stroke-width="1.5" />
              
              <!-- Max entropy line -->
              <line 
                x1="0" 
                :y1="scaleEntropy(Math.log(analysisResult.summary.n_regimes))" 
                x2="800" 
                :y2="scaleEntropy(Math.log(analysisResult.summary.n_regimes))" 
                stroke="rgba(255,255,255,0.2)" 
                stroke-dasharray="4"
              />
              <text 
                x="10" 
                :y="scaleEntropy(Math.log(analysisResult.summary.n_regimes)) - 5" 
                fill="rgba(255,255,255,0.3)" 
                font-size="9"
              >
                max entropy
              </text>
            </svg>
            <div v-else-if="!isLoading" class="empty-state-sm">
              <span>Данные отсутствуют</span>
            </div>
          </div>
        </div>

        <!-- Spectrum Chart -->
        <div class="glass-card chart-card mt-4">
          <div class="chart-header">
            <h3>Амплитудный спектр |H(e^iw)|</h3>
          </div>
          <div class="chart-container-sm">
            <svg v-if="analysisResult && spectrumData" viewBox="0 0 800 140" preserveAspectRatio="none" class="spectrum-svg">
              <!-- Spectrum line -->
              <path :d="spectrumPath" fill="none" stroke="#60a5fa" stroke-width="1.5" />
              
              <!-- Grid -->
              <line v-for="y in [35, 70, 105]" :key="'spec-grid-' + y" x1="0" :y1="y" x2="800" :y2="y" stroke="rgba(255,255,255,0.05)" />
              
              <!-- Frequency labels -->
              <text x="5" y="135" fill="rgba(255,255,255,0.3)" font-size="9">0</text>
              <text x="395" y="135" fill="rgba(255,255,255,0.3)" font-size="9">π/2</text>
              <text x="790" y="135" fill="rgba(255,255,255,0.3)" font-size="9">π</text>
            </svg>
            <div v-else-if="!isLoading" class="empty-state-sm">
              <span>Данные отсутствуют</span>
            </div>
          </div>
        </div>

      </main>
    </div>

    <!-- Error Message -->
    <transition name="fade">
      <div v-if="errorMessage" class="error-toast">
        {{ errorMessage }}
        <button @click="errorMessage = ''" class="close-btn">×</button>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import {
  getAvailableAssets,
  analyzeAssetRegimes,
  getRegimeTypeName,
  getRegimeTypeColor,
  getRegimeColor,
  formatDuration,
  type AssetCategory,
  type FullAssetAnalysisResponse,
  type RegimeParams,
  type AssetMetadata
} from '@/services/spectralRegimeService'

// Asset selection
const assetCategories = ref<AssetCategory | null>(null)
const selectedCategory = ref('stocks')
const selectedTicker = ref('SPY')
const periodDays = ref(252)

// Analysis parameters
const nPoles = ref(5)
const windowSize = ref(20)

// State
const isLoading = ref(false)
const loadingStatus = ref('Загрузка...')
const errorMessage = ref('')
const analysisResult = ref<FullAssetAnalysisResponse | null>(null)
const assetMetadata = ref<AssetMetadata | null>(null)

// Playback
const playbackIndex = ref(0)
const isPlaying = ref(false)
let animationFrame: number | null = null

// Computed: available assets for selected category
const availableAssets = computed(() => {
  if (!assetCategories.value) return []
  return assetCategories.value[selectedCategory.value as keyof AssetCategory] || []
})

// Watch category change
watch(selectedCategory, () => {
  const assets = availableAssets.value
  if (assets.length > 0) {
    selectedTicker.value = assets[0].ticker
  }
})

// Load available assets on mount
;(async () => {
  try {
    const response = await getAvailableAssets()
    if (response.success) {
      assetCategories.value = response.data
    }
  } catch (e) {
    console.error('Failed to load assets:', e)
  }
})()

// Computed: dynamics data
const dynamicsData = computed(() => {
  if (!analysisResult.value) return null
  return analysisResult.value.analysis.visualization.dynamics
})

// Computed: spectrum data
const spectrumData = computed(() => {
  if (!analysisResult.value) return null
  return analysisResult.value.analysis.visualization.spectrum
})

// Computed: all poles
const allPoles = computed(() => {
  if (!analysisResult.value) return []
  return analysisResult.value.analysis.visualization.poles
})

// Computed: regime poles
const regimePoles = computed(() => {
  if (!analysisResult.value) return []
  return analysisResult.value.analysis.visualization.regime_poles
})

// Computed: regime stats
const regimeStats = computed<RegimeParams[]>(() => {
  if (!analysisResult.value) return []
  const params = analysisResult.value.analysis.summary.regime_params
  return Object.values(params)
})

// Computed: current regime
const currentRegimeIndex = computed(() => {
  if (!analysisResult.value) return -1
  return analysisResult.value.analysis.summary.current_metrics.regime_index
})

const currentRegimeType = computed(() => {
  if (!analysisResult.value) return 'N/A'
  const type = analysisResult.value.analysis.summary.current_metrics.regime_type
  return getRegimeTypeName(type)
})

const currentRegimeColor = computed(() => {
  if (!analysisResult.value) return '#3b82f6'
  const idx = currentRegimeIndex.value
  return getRegimeColor(idx >= 0 ? idx : 0)
})

// Computed: entropy
const entropyValue = computed(() => {
  if (!analysisResult.value) return 'N/A'
  return analysisResult.value.analysis.summary.current_metrics.entropy.toFixed(3)
})

const entropyClass = computed(() => {
  if (!analysisResult.value) return ''
  const entropy = analysisResult.value.analysis.summary.current_metrics.entropy
  const maxEntropy = Math.log(analysisResult.value.analysis.summary.n_regimes)
  const ratio = entropy / maxEntropy
  if (ratio < 0.3) return 'text-green'
  if (ratio < 0.7) return 'text-yellow'
  return 'text-red'
})

// Playback
const maxPlaybackIndex = computed(() => {
  if (!dynamicsData.value) return 0
  return dynamicsData.value.regime_signal.length - 1
})

const playbackProgress = computed(() => {
  if (maxPlaybackIndex.value === 0) return 0
  return (playbackIndex.value / maxPlaybackIndex.value) * 100
})

const visibleRegimes = computed(() => {
  if (!dynamicsData.value) return []
  return dynamicsData.value.regime_signal.slice(0, playbackIndex.value + 1)
})

// Chart scales
const barWidth = computed(() => {
  if (!dynamicsData.value) return 1
  return 800 / dynamicsData.value.regime_signal.length
})

const scaleX = (i: number) => i * barWidth.value

// Price path
const pricePath = computed(() => {
  if (!dynamicsData.value || !dynamicsData.value.time_series.length) return ''
  const data = dynamicsData.value.time_series.slice(0, playbackIndex.value + 1)
  const min = Math.min(...dynamicsData.value.time_series)
  const max = Math.max(...dynamicsData.value.time_series)
  const range = max - min || 1
  
  return 'M ' + data.map((v, i) => {
    const x = scaleX(i)
    const y = 300 - ((v - min) / range) * 260 - 20
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' L ')
})

// Energy paths (stacked)
const getEnergyPath = (regimeIdx: number) => {
  if (!dynamicsData.value || !dynamicsData.value.regime_energies.length) return ''
  
  const energies = dynamicsData.value.regime_energies.slice(0, playbackIndex.value + 1)
  const n = energies.length
  
  // Calculate cumulative sums
  let points: string[] = []
  let bottomPoints: string[] = []
  
  for (let i = 0; i < n; i++) {
    const x = scaleX(i)
    
    // Sum of energies for regimes 0..regimeIdx-1 (bottom)
    let bottomSum = 0
    for (let k = 0; k < regimeIdx; k++) {
      bottomSum += energies[i][k] || 0
    }
    
    // Sum including current regime (top)
    const topSum = bottomSum + (energies[i][regimeIdx] || 0)
    
    const yTop = 160 - topSum * 150 - 5
    const yBottom = 160 - bottomSum * 150 - 5
    
    points.push(`${x.toFixed(1)},${yTop.toFixed(1)}`)
    bottomPoints.push(`${x.toFixed(1)},${yBottom.toFixed(1)}`)
  }
  
  // Create closed path
  return `M ${points[0]} L ${points.join(' L ')} L ${bottomPoints.reverse().join(' L ')} Z`
}

// Entropy path
const entropyPath = computed(() => {
  if (!dynamicsData.value || !dynamicsData.value.entropy.length) return ''
  
  const data = dynamicsData.value.entropy.slice(0, playbackIndex.value + 1)
  const maxE = Math.log(analysisResult.value?.analysis.summary.n_regimes || 3) * 1.1
  
  let path = `M 0,120 `
  data.forEach((e, i) => {
    const x = scaleX(i)
    const y = scaleEntropy(e)
    path += `L ${x.toFixed(1)},${y.toFixed(1)} `
  })
  path += `L ${scaleX(data.length - 1).toFixed(1)},120 Z`
  
  return path
})

const scaleEntropy = (e: number) => {
  const maxE = Math.log(analysisResult.value?.analysis.summary.n_regimes || 3) * 1.1
  return 115 - (e / maxE) * 100
}

// Spectrum path
const spectrumPath = computed(() => {
  if (!spectrumData.value || !spectrumData.value.amplitude.length) return ''
  
  const amp = spectrumData.value.amplitude
  const max = Math.max(...amp)
  const min = Math.min(...amp)
  const range = max - min || 1
  
  return 'M ' + amp.map((v, i) => {
    const x = (i / amp.length) * 800
    const y = 130 - ((v - min) / range) * 110 - 10
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' L ')
})

// Helpers
const getPoleColor = (radius: number) => {
  if (radius < 0.5) return '#94a3b8'
  if (radius < 0.8) return '#fbbf24'
  if (radius < 0.95) return '#4ade80'
  if (radius < 0.999) return '#f97316'
  return '#ef4444'
}

const getRegimeTimePercent = (idx: number) => {
  if (!analysisResult.value) return 0
  const stats = analysisResult.value.analysis.summary.regime_time_stats[String(idx)]
  return stats?.percentage || 0
}

// Playback controls
const togglePlayback = () => {
  if (isPlaying.value) {
    stopPlayback()
  } else {
    if (playbackIndex.value >= maxPlaybackIndex.value) {
      playbackIndex.value = 0
    }
    isPlaying.value = true
    animate()
  }
}

const stopPlayback = () => {
  isPlaying.value = false
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
    animationFrame = null
  }
}

const resetPlayback = () => {
  stopPlayback()
  playbackIndex.value = 0
}

const animate = () => {
  if (!isPlaying.value) return
  
  const next = playbackIndex.value + 2
  if (next >= maxPlaybackIndex.value) {
    playbackIndex.value = maxPlaybackIndex.value
    stopPlayback()
  } else {
    playbackIndex.value = next
    animationFrame = requestAnimationFrame(animate)
  }
}

// Run analysis
const runAnalysis = async () => {
  if (isLoading.value) return
  
  isLoading.value = true
  loadingStatus.value = 'Загрузка данных...'
  errorMessage.value = ''
  stopPlayback()
  
  try {
    loadingStatus.value = 'Загрузка данных...'
    await new Promise(r => setTimeout(r, 100))
    
    loadingStatus.value = 'Анализ спектра...'
    const result = await analyzeAssetRegimes(
      selectedTicker.value,
      periodDays.value,
      nPoles.value,
      windowSize.value
    )
    
    if (result.success) {
      analysisResult.value = result
      assetMetadata.value = result.asset_metadata
      
      // Start playback
      playbackIndex.value = 0
      setTimeout(() => {
        playbackIndex.value = maxPlaybackIndex.value
      }, 100)
    } else {
      errorMessage.value = 'Ошибка при выполнении анализа'
    }
    
  } catch (e: any) {
    console.error('Analysis error:', e)
    errorMessage.value = e.message || 'Неизвестная ошибка'
  } finally {
    isLoading.value = false
    loadingStatus.value = ''
  }
}

onUnmounted(() => {
  stopPlayback()
})
</script>

<style scoped>
/* Main Layout */
.page-container {
  padding: 24px 32px;
  max-width: 1600px;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 24px;
  flex: 1;
}

.left-panel, .main-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 4px;
  flex-shrink: 0;
}

.section-title {
  font-size: 26px;
  font-weight: 700;
  margin: 0;
  color: #fff;
  letter-spacing: -0.01em;
}

.section-subtitle {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  margin: 4px 0 0 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* Glass Components */
.glass-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  box-shadow: 0 20px 50px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
}

.glass-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 99px;
  font-size: 12px;
  color: rgba(255,255,255,0.7);
}

.panel {
  padding: 20px;
}

.panel-header h3 {
  margin: 0 0 16px 0;
  font-size: 11px;
  text-transform: uppercase;
  color: rgba(255,255,255,0.5);
  font-weight: 700;
  letter-spacing: 0.05em;
}

/* Controls */
.controls-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.lbl {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
}

.glass-select {
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  padding: 10px 12px;
  border-radius: 12px;
  width: 100%;
  outline: none;
  transition: 0.2s;
  cursor: pointer;
  font-size: 13px;
}

.glass-select:focus {
  border-color: #3b82f6;
  background: rgba(0,0,0,0.5);
}

.range-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.range-slider {
  flex: 1;
  -webkit-appearance: none;
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  outline: none;
}

.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
}

.range-value {
  font-size: 14px;
  font-weight: 600;
  color: #3b82f6;
  min-width: 50px;
  text-align: right;
}

.hint {
  font-size: 10px;
  color: rgba(255,255,255,0.3);
}

/* Button */
.btn-primary-gradient {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
  padding: 12px;
  border-radius: 12px;
  color: #fff;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
  transition: all 0.2s;
}

.btn-primary-gradient:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 25px rgba(37, 99, 235, 0.5);
}

.btn-primary-gradient:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Metrics */
.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px;
  background: rgba(0,0,0,0.2);
  border-radius: 10px;
}

.metric-label {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
  text-transform: uppercase;
}

.metric-value {
  font-size: 18px;
  font-weight: 700;
  font-family: "SF Mono", monospace;
}

.stability-badge {
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 11px;
  text-align: center;
}

.stability-badge.stable {
  background: rgba(74, 222, 128, 0.15);
  color: #4ade80;
  border: 1px solid rgba(74, 222, 128, 0.3);
}

.stability-badge.unstable {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.stability-badge.warning {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.3);
}

/* Regime List */
.regime-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.regime-item {
  padding: 12px;
  background: rgba(0,0,0,0.15);
  border-radius: 12px;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.regime-item.active {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.1);
}

.regime-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.regime-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.regime-name {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}

.regime-type {
  margin-left: auto;
  font-size: 11px;
  font-weight: 600;
}

.regime-metrics {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.rm-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.rm-label {
  font-size: 9px;
  color: rgba(255,255,255,0.4);
}

.rm-value {
  font-size: 12px;
  font-family: "SF Mono", monospace;
  color: #fff;
}

.regime-bar {
  position: relative;
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  overflow: hidden;
}

.regime-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s;
}

.regime-bar-label {
  position: absolute;
  right: 0;
  top: -14px;
  font-size: 9px;
  color: rgba(255,255,255,0.4);
}

/* Charts */
.chart-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.ch-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chart-header h3 {
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.badge-info {
  font-size: 10px;
  color: rgba(255,255,255,0.5);
  padding: 4px 8px;
  background: rgba(255,255,255,0.05);
  border-radius: 6px;
}

.badge-ticker {
  font-size: 11px;
  font-weight: 600;
  color: #3b82f6;
  padding: 4px 8px;
  background: rgba(59, 130, 246, 0.15);
  border-radius: 6px;
}

.poles-container {
  height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.poles-svg {
  width: 100%;
  height: 100%;
  max-width: 320px;
}

.regime-pole-marker {
  filter: drop-shadow(0 0 4px rgba(0,0,0,0.3));
}

.chart-container {
  height: 300px;
  position: relative;
}

.chart-container-sm {
  height: 160px;
  position: relative;
}

.dynamics-svg, .energy-svg, .entropy-svg, .spectrum-svg {
  width: 100%;
  height: 100%;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.3);
  font-size: 13px;
  gap: 12px;
}

.empty-state-sm {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.2);
  font-size: 12px;
}

/* Playback */
.playback-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(0, 0, 0, 0.4);
  padding: 6px 12px;
  border-radius: 99px;
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
  opacity: 0.8;
  transition: 0.2s;
  font-size: 14px;
}

.icon-btn:hover {
  opacity: 1;
  background: rgba(255,255,255,0.1);
  border-radius: 50%;
}

.timeline-wrapper {
  position: relative;
  width: 160px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.timeline-slider {
  position: absolute;
  width: 100%;
  height: 20px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0;
  cursor: pointer;
  z-index: 3;
}

.timeline-track {
  height: 100%;
  background: #60a5fa;
  border-radius: 3px;
  pointer-events: none;
}

/* Error Toast */
.error-toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: rgba(239, 68, 68, 0.9);
  color: white;
  padding: 12px 40px 12px 16px;
  border-radius: 12px;
  font-size: 13px;
  z-index: 1000;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.close-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  opacity: 0.7;
}

.close-btn:hover {
  opacity: 1;
}

/* Colors */
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.text-blue { color: #3b82f6; }
.text-green { color: #4ade80; }
.text-red { color: #ef4444; }
.text-yellow { color: #fbbf24; }
.text-white { color: #fff; }

.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 12px; }
.mt-4 { margin-top: 16px; }
.mt-6 { margin-top: 24px; }

.flex { display: flex; }
.items-center { align-items: center; }
.gap-2 { gap: 8px; }

/* Spinners */
.spinner-mini {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-large {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255,255,255,0.1);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .left-panel {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .poles-container {
    height: 280px;
  }
  
  .chart-container {
    height: 250px;
  }
}
</style>
