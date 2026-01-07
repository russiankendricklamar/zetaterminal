<!--
  3D Визуализация пространства скрытых состояний (HMM Regime Space)
  Инновационная визуализация рыночных режимов в 3D пространстве
-->

<template>
  <div class="regime-space-3d">
    <!-- Main Layout -->
    <div class="main-layout">
      <!-- Left Panel: Controls -->
      <aside class="controls-panel">
        <!-- Controls Card -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Управление</h3>
          </div>

          <div class="controls-section">
            <!-- Asset Selection -->
            <div class="input-group">
              <label class="lbl">Актив</label>
              <select v-model="selectedAsset" class="glass-select" @change="onAssetChange">
                <option value="SPY">S&P 500 (SPY)</option>
                <option value="QQQ">Nasdaq 100 (QQQ)</option>
                <option value="BTC">Bitcoin (BTC)</option>
                <option value="IMOEX">IMOEX Index</option>
              </select>
            </div>

            <!-- Number of States -->
            <div class="input-group">
              <label class="lbl">Количество режимов</label>
              <div class="scrub-row">
                <ScrubInput 
                  v-model="nStates" 
                  :min="2" :max="5" :step="1" 
                  class="text-accent font-bold"
                  @update:modelValue="onStatesChange"
                />
                <span class="unit">states</span>
              </div>
            </div>

            <!-- Time Period -->
            <div class="input-group">
              <label class="lbl">Временной период</label>
              <select v-model="timePeriod" class="glass-select" @change="onTimePeriodChange">
                <option value="3M">3 месяца</option>
                <option value="6M">6 месяцев</option>
                <option value="1Y">1 год</option>
                <option value="2Y">2 года</option>
                <option value="ALL">Все данные</option>
              </select>
            </div>

            <!-- Run Button -->
            <button @click="runAnalysis" :disabled="isLoading" class="btn-primary-gradient">
              <span v-if="!isLoading">Запустить анализ</span>
              <span v-else class="flex items-center gap-2">
                <span class="spinner-mini"></span> Обучение HMM...
              </span>
            </button>
          </div>
        </div>

        <!-- View Controls -->
        <div class="glass-card panel" v-if="hasData">
          <div class="panel-header">
            <h3>Вид</h3>
          </div>

          <div class="view-controls">
            <label class="checkbox-label">
              <input type="checkbox" v-model="showTrajectory" @change="onVisibilityChange" />
              <span>Траектория</span>
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="showEllipsoids" @change="onVisibilityChange" />
              <span>Эллипсоиды</span>
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="showCentroids" @change="onVisibilityChange" />
              <span>Центроиды</span>
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="showGrid" @change="onVisibilityChange" />
              <span>Сетка</span>
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="showTransitionArrows" @change="onTransitionArrowsChange" />
              <span>Стрелки переходов</span>
            </label>
          </div>

          <!-- Camera Presets -->
          <div class="camera-presets">
            <h4 class="presets-title">Вид камеры</h4>
            <div class="preset-buttons">
              <button 
                v-for="preset in cameraPresets" 
                :key="preset.name"
                @click="setCameraPreset(preset)"
                class="btn-preset"
              >
                {{ preset.label }}
              </button>
            </div>
            <label class="checkbox-label">
              <input type="checkbox" v-model="autoRotate" @change="onAutoRotateChange" />
              <span>Авто-вращение</span>
            </label>
          </div>
        </div>

        <!-- Current Regime Info -->
        <div class="glass-card panel" v-if="currentRegimeInfo">
          <div class="panel-header">
            <h3>Текущий режим</h3>
          </div>
          <div class="regime-info">
            <div class="regime-badge" :style="{ borderColor: currentRegimeInfo.color }">
              <span class="regime-dot" :style="{ backgroundColor: currentRegimeInfo.color }"></span>
              <span class="regime-name">{{ currentRegimeInfo.name }}</span>
            </div>
            <div class="regime-stats">
              <div class="stat-row">
                <span class="stat-label">Вероятность:</span>
                <span class="stat-value">{{ (currentRegimeInfo.probability * 100).toFixed(1) }}%</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Доходность:</span>
                <span class="stat-value" :class="currentRegimeInfo.meanReturn >= 0 ? 'text-green' : 'text-red'">
                  {{ currentRegimeInfo.meanReturn.toFixed(2) }}%
                </span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Волатильность:</span>
                <span class="stat-value">{{ currentRegimeInfo.meanVolatility.toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Transition Matrix -->
        <transition name="fade">
          <div class="glass-card panel" v-if="transitionMatrix">
            <div class="panel-header">
              <h3>Матрица переходов</h3>
            </div>
            <div class="matrix-grid" :style="{ gridTemplateColumns: `repeat(${nStates}, 1fr)` }">
              <div v-for="(row, i) in transitionMatrix" :key="i" class="matrix-row-group">
                <div 
                  v-for="(prob, j) in row" 
                  :key="j" 
                  class="matrix-cell"
                  :style="{ backgroundColor: `rgba(59, 130, 246, ${prob * 0.8})` }"
                >
                  <span class="m-val">{{ (prob * 100).toFixed(0) }}%</span>
                  <span class="m-lbl">S{{i}}→S{{j}}</span>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </aside>

      <!-- Main Content: 3D Visualization -->
      <main class="main-content">
        <!-- Header with Timeline Controls -->
        <div class="visualization-header" v-if="hasData">
          <div class="header-left">
            <h2 class="vis-title">Пространство скрытых состояний</h2>
            <p class="vis-subtitle">3D визуализация рыночных режимов (HMM)</p>
          </div>

          <!-- Timeline Controls -->
          <div class="timeline-controls">
            <button 
              @click="togglePlayback" 
              class="btn-play"
              :class="{ active: isPlaying }"
            >
              {{ isPlaying ? '⏸' : '▶' }}
            </button>

            <div class="timeline-wrapper">
              <input 
                type="range" 
                :min="0" 
                :max="filteredData.length - 1" 
                v-model.number="currentTimeIndex" 
                @input="onTimelineChange"
                class="timeline-slider"
              />
              <div class="timeline-track" :style="{ width: timelineProgress + '%' }"></div>
              <div class="timeline-thumb" :style="{ left: timelineProgress + '%' }"></div>
            </div>

            <select v-model="playbackSpeed" class="speed-select">
              <option value="0.5">0.5x</option>
              <option value="1">1x</option>
              <option value="2">2x</option>
              <option value="5">5x</option>
            </select>

            <button @click="resetPlayback" class="btn-reset">↺</button>

            <div class="current-date">{{ currentDate }}</div>
          </div>
        </div>

        <!-- 3D Canvas Container -->
        <div ref="canvasContainer" class="canvas-container" :class="{ loading: isLoading }">
          <div v-if="isLoading" class="loading-overlay">
            <div class="spinner-large"></div>
            <p>Инициализация 3D пространства...</p>
          </div>
        </div>

        <!-- Bottom Panel: Statistics -->
        <div class="stats-panel" v-if="hasData">
          <!-- Stationary Distribution -->
          <div class="stats-card">
            <h4>Стационарное распределение</h4>
            <div class="distribution-bars">
              <div 
                v-for="(prob, i) in stationaryDistribution" 
                :key="i"
                class="dist-bar"
                :style="{ 
                  width: (prob * 100) + '%',
                  backgroundColor: regimeConfigs[i]?.color || '#888'
                }"
              >
                <span class="dist-label">S{{i}}: {{ (prob * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>

          <!-- Expected Durations -->
          <div class="stats-card">
            <h4>Ожидаемая длительность режимов</h4>
            <div class="duration-list">
              <div 
                v-for="(duration, i) in expectedDurations" 
                :key="i"
                class="duration-item"
              >
                <span class="duration-dot" :style="{ backgroundColor: regimeConfigs[i]?.color || '#888' }"></span>
                <span class="duration-name">{{ regimeConfigs[i]?.name || `Режим ${i}` }}</span>
                <span class="duration-value">{{ duration.toFixed(1) }} дней</span>
              </div>
            </div>
          </div>

          <!-- Export Buttons -->
          <div class="export-section">
            <button @click="exportScreenshot" class="btn-export">
              📷 Скриншот
            </button>
            <button @click="exportData" class="btn-export">
              📊 CSV
            </button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { HMMModel, generateMockMarketData, type MarketPoint } from '@/composables/useHMMModel'
import { RegimeSpaceRenderer, type RegimeConfig, type CameraPreset } from '@/composables/useRegimeSpace3D'
import ScrubInput from './ScrubInput.vue'

// Props
const props = defineProps<{
  initialAsset?: string
  initialNStates?: number
}>()

// State
const canvasContainer = ref<HTMLElement | null>(null)
const isLoading = ref(false)
const hasData = ref(false)
const selectedAsset = ref(props.initialAsset || 'SPY')
const nStates = ref(props.initialNStates || 4)
const timePeriod = ref('1Y')
const currentTimeIndex = ref(0)
const isPlaying = ref(false)
const playbackSpeed = ref(1)
const autoRotate = ref(false)

// Visualization toggles
const showTrajectory = ref(true)
const showEllipsoids = ref(true)
const showCentroids = ref(true)
const showGrid = ref(true)
const showTransitionArrows = ref(false)

// Data
const allMarketData = ref<MarketPoint[]>([])
const filteredData = computed(() => {
  if (timePeriod.value === 'ALL') return allMarketData.value
  
  const daysMap: Record<string, number> = {
    '3M': 90,
    '6M': 180,
    '1Y': 252,
    '2Y': 504
  }
  
  const days = daysMap[timePeriod.value] || 252
  return allMarketData.value.slice(-days)
})

// HMM Model
const hmmModel = ref<HMMModel | null>(null)
const transitionMatrix = ref<number[][] | null>(null)
const stationaryDistribution = ref<number[]>([])
const expectedDurations = ref<number[]>([])

// Renderer
let renderer: RegimeSpaceRenderer | null = null

// Regime Configs
const regimeConfigs = ref<RegimeConfig[]>([
  { id: 0, name: 'Low Vol / Accumulation', color: '#00ff00', mean: [0.15, 8.0, 0.8] },
  { id: 1, name: 'Normal / Trending', color: '#00ffff', mean: [0.08, 15.0, 0.6] },
  { id: 2, name: 'High Vol / Distribution', color: '#ff00ff', mean: [-0.05, 35.0, 0.4] },
  { id: 3, name: 'Crisis / Panic', color: '#ff0000', mean: [-0.20, 60.0, 0.2] },
  { id: 4, name: 'Recovery', color: '#ffff00', mean: [0.12, 20.0, 0.5] }
])

// Camera Presets
const cameraPresets: (CameraPreset & { label: string })[] = [
  { 
    name: 'top', 
    label: 'Сверху',
    position: [0, 100, 0], 
    target: [0, 0, 0] 
  },
  { 
    name: 'side', 
    label: 'Сбоку',
    position: [0, 40, 80], 
    target: [0, 0, 0] 
  },
  { 
    name: 'isometric', 
    label: 'Изометрия',
    position: [50, 50, 50], 
    target: [0, 0, 0] 
  },
  { 
    name: 'front', 
    label: 'Спереди',
    position: [0, 0, 80], 
    target: [0, 0, 0] 
  }
]

// Playback
let playbackInterval: number | null = null

// Computed
const timelineProgress = computed(() => {
  if (filteredData.value.length === 0) return 0
  return (currentTimeIndex.value / (filteredData.value.length - 1)) * 100
})

const currentDate = computed(() => {
  if (filteredData.value.length === 0) return '—'
  const point = filteredData.value[currentTimeIndex.value]
  return point?.date || '—'
})

const currentRegimeInfo = computed(() => {
  if (filteredData.value.length === 0 || !filteredData.value[currentTimeIndex.value]) return null
  
  const point = filteredData.value[currentTimeIndex.value]
  const regimeId = point.regime || 0
  const config = regimeConfigs.value[regimeId]
  if (!config) return null

  const prob = point.probability ? point.probability[regimeId] : 0
  const mean = hmmModel.value?.getEmissionMeans()[regimeId] || [0, 0, 0]

  return {
    ...config,
    probability: prob,
    meanReturn: mean[0],
    meanVolatility: mean[1]
  }
})

// Methods
const runAnalysis = async () => {
  if (!canvasContainer.value) {
    console.error('Canvas container not found')
    return
  }
  
  console.log('Starting HMM analysis...', {
    asset: selectedAsset.value,
    nStates: nStates.value,
    containerSize: {
      width: canvasContainer.value.clientWidth,
      height: canvasContainer.value.clientHeight
    }
  })
  
  isLoading.value = true
  hasData.value = false
  
  try {
    // Generate mock data (в реальном приложении - загрузка с API)
    await new Promise(resolve => setTimeout(resolve, 500))
    allMarketData.value = generateMockMarketData(500)
    
    // Initialize HMM Model with correct number of states
    // First, create a default model, then update it with computed transition matrix
    hmmModel.value = new HMMModel()
    
    // Update model to use correct number of states
    const defaultMatrix = hmmModel.value.getTransitionMatrix()
    const defaultMeans = hmmModel.value.getEmissionMeans()
    const defaultCovs = hmmModel.value.getEmissionCovariances()
    
    // Adjust to match nStates
    const adjustedMatrix: number[][] = []
    const adjustedMeans: number[][] = []
    const adjustedCovs: number[][][] = []
    
    for (let i = 0; i < nStates.value; i++) {
      const row: number[] = []
      for (let j = 0; j < nStates.value; j++) {
        if (i < defaultMatrix.length && j < defaultMatrix[i].length) {
          row.push(defaultMatrix[i][j])
        } else {
          // Equal probability for new states
          row.push(1 / nStates.value)
        }
      }
      // Normalize row
      const sum = row.reduce((a, b) => a + b, 0)
      row.forEach((val, idx) => row[idx] = val / sum)
      adjustedMatrix.push(row)
      
      if (i < defaultMeans.length) {
        adjustedMeans.push(defaultMeans[i])
        adjustedCovs.push(defaultCovs[i])
      } else {
        // Use last regime's parameters for extra states
        adjustedMeans.push([...defaultMeans[defaultMeans.length - 1]])
        adjustedCovs.push(defaultCovs[defaultCovs.length - 1].map(row => [...row]))
      }
    }
    
    hmmModel.value.setParameters({
      nStates: nStates.value,
      transitionMatrix: adjustedMatrix,
      initialStateDistribution: Array(nStates.value).fill(1 / nStates.value),
      emissionMeans: adjustedMeans,
      emissionCovariances: adjustedCovs
    })
    
    // Compute transition matrix from data
    computeTransitionMatrixFromData()
    
    // Compute stationary distribution
    if (hmmModel.value) {
      stationaryDistribution.value = hmmModel.value.computeStationaryDistribution()
      
      // Compute expected durations
      expectedDurations.value = []
      for (let i = 0; i < nStates.value; i++) {
        expectedDurations.value.push(hmmModel.value.computeExpectedDuration(i))
      }
    }
    
    // Update transition matrix display
    if (hmmModel.value) {
      transitionMatrix.value = hmmModel.value.getTransitionMatrix()
    }
    
    // Initialize renderer
    if (canvasContainer.value && !renderer) {
      // Ensure container has dimensions
      if (canvasContainer.value.clientWidth === 0 || canvasContainer.value.clientHeight === 0) {
        console.warn('Canvas container has zero dimensions, retrying...')
        setTimeout(() => runAnalysis(), 200)
        return
      }
      
      renderer = new RegimeSpaceRenderer(canvasContainer.value)
      
      // Handle window resize
      const handleResize = () => {
        if (renderer && canvasContainer.value) {
          const width = canvasContainer.value.clientWidth
          const height = canvasContainer.value.clientHeight
          if (width > 0 && height > 0) {
            renderer.resize(width, height)
          }
        }
      }
      window.addEventListener('resize', handleResize)
      onUnmounted(() => {
        window.removeEventListener('resize', handleResize)
      })
      
      // Force resize after initialization
      setTimeout(() => {
        if (renderer && canvasContainer.value) {
          const width = canvasContainer.value.clientWidth
          const height = canvasContainer.value.clientHeight
          if (width > 0 && height > 0) {
            renderer.resize(width, height)
          }
        }
      }, 100)
    }
    
    // Update visualization
    if (renderer && hmmModel.value) {
      const configs = regimeConfigs.value.slice(0, nStates.value)
      renderer.setData(filteredData.value, hmmModel.value, configs)
    }
    
    currentTimeIndex.value = filteredData.value.length - 1
    hasData.value = true
    
    console.log('HMM analysis completed successfully', {
      dataPoints: filteredData.value.length,
      rendererInitialized: !!renderer,
      hmmModelInitialized: !!hmmModel.value
    })
    
  } catch (error) {
    console.error('Error running analysis:', error)
    // Show error to user
    alert('Ошибка при запуске анализа: ' + (error as Error).message)
  } finally {
    isLoading.value = false
  }
}

const computeTransitionMatrixFromData = () => {
  if (!hmmModel.value || allMarketData.value.length === 0) return
  
  // Count transitions
  const transitions: number[][] = Array(nStates.value)
    .fill(0)
    .map(() => Array(nStates.value).fill(0))
  
  for (let i = 1; i < allMarketData.value.length; i++) {
    const prev = allMarketData.value[i - 1].regime || 0
    const curr = allMarketData.value[i].regime || 0
    transitions[prev][curr]++
  }
  
  // Normalize to probabilities
  const matrix: number[][] = []
  for (let i = 0; i < nStates.value; i++) {
    const row: number[] = []
    const total = transitions[i].reduce((a, b) => a + b, 0) || 1
    for (let j = 0; j < nStates.value; j++) {
      row.push(transitions[i][j] / total)
    }
    matrix.push(row)
  }
  
  // Update model (simplified - в реальности нужен Baum-Welch)
  hmmModel.value.setParameters({ transitionMatrix: matrix })
}

const onAssetChange = () => {
  runAnalysis()
}

const onStatesChange = () => {
  // Update regime configs
  if (nStates.value > regimeConfigs.value.length) {
    // Add more configs if needed
  }
  if (renderer && hmmModel.value) {
    const configs = regimeConfigs.value.slice(0, nStates.value)
    renderer.setData(filteredData.value, hmmModel.value, configs)
  }
}

const onTimePeriodChange = () => {
  if (renderer && hmmModel.value) {
    const configs = regimeConfigs.value.slice(0, nStates.value)
    renderer.setData(filteredData.value, hmmModel.value, configs)
    currentTimeIndex.value = Math.min(currentTimeIndex.value, filteredData.value.length - 1)
  }
}

const onVisibilityChange = () => {
  if (!renderer) return
  renderer.setShowTrajectory(showTrajectory.value)
  renderer.setShowEllipsoids(showEllipsoids.value)
  renderer.setShowCentroids(showCentroids.value)
  renderer.setShowGrid(showGrid.value)
}

const onTransitionArrowsChange = () => {
  if (!renderer) return
  renderer.setShowTransitionArrows(showTransitionArrows.value)
}

const setCameraPreset = (preset: CameraPreset) => {
  if (renderer) {
    renderer.setCameraPreset(preset)
  }
}

const onAutoRotateChange = () => {
  if (renderer) {
    renderer.setAutoRotate(autoRotate.value)
  }
}

const onTimelineChange = () => {
  if (renderer) {
    renderer.setTimeIndex(currentTimeIndex.value)
    // Update transition arrows if shown
    if (showTransitionArrows.value) {
      renderer.setShowTransitionArrows(false)
      setTimeout(() => {
        if (renderer) renderer.setShowTransitionArrows(true)
      }, 100)
    }
  }
}

const togglePlayback = () => {
  isPlaying.value = !isPlaying.value
  
  if (isPlaying.value) {
    startPlayback()
  } else {
    stopPlayback()
  }
}

const startPlayback = () => {
  stopPlayback()
  
  const step = () => {
    if (!isPlaying.value) return
    
    const speed = parseFloat(playbackSpeed.value.toString())
    currentTimeIndex.value += speed
    
    if (currentTimeIndex.value >= filteredData.value.length - 1) {
      currentTimeIndex.value = filteredData.value.length - 1
      stopPlayback()
      return
    }
    
    onTimelineChange()
    playbackInterval = window.setTimeout(step, 50)
  }
  
  step()
}

const stopPlayback = () => {
  if (playbackInterval) {
    clearTimeout(playbackInterval)
    playbackInterval = null
  }
  isPlaying.value = false
}

const resetPlayback = () => {
  stopPlayback()
  currentTimeIndex.value = 0
  onTimelineChange()
}

const exportScreenshot = () => {
  if (renderer) {
    renderer.exportScreenshot(`regime-space-${selectedAsset.value}-${Date.now()}.png`)
  }
}

const exportData = () => {
  const csv = [
    ['Date', 'Return', 'Volatility', 'Liquidity', 'Regime', 'Probability'].join(','),
    ...filteredData.value.map(p => [
      p.date,
      p.return.toFixed(4),
      p.volatility.toFixed(4),
      p.liquidity.toFixed(4),
      p.regime || 0,
      p.probability ? Math.max(...p.probability).toFixed(4) : '0'
    ].join(','))
  ].join('\n')
  
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `regime-data-${selectedAsset.value}-${Date.now()}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

// Watch
watch(() => filteredData.value, () => {
  if (renderer && hmmModel.value && filteredData.value.length > 0) {
    const configs = regimeConfigs.value.slice(0, nStates.value)
    renderer.setData(filteredData.value, hmmModel.value, configs)
  }
}, { deep: true })

// Lifecycle
onMounted(() => {
  // Auto-run analysis on mount with a small delay to ensure DOM is ready
  setTimeout(() => {
    if (canvasContainer.value && !isLoading.value && !hasData.value) {
      runAnalysis()
    }
  }, 100)
})

onUnmounted(() => {
  stopPlayback()
  if (renderer) {
    renderer.dispose()
    renderer = null
  }
})
</script>

<style scoped>
.regime-space-3d {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #000;
}

.main-layout {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 20px;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
}

.controls-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  max-height: 100%;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

.panel {
  padding: 20px;
}

.panel-header h3 {
  margin: 0 0 16px 0;
  font-size: 11px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 700;
  letter-spacing: 0.05em;
}

.controls-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.lbl {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 600;
  text-transform: uppercase;
}

.glass-select {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 10px 12px;
  border-radius: 12px;
  width: 100%;
  outline: none;
  transition: 0.2s;
  cursor: pointer;
}

.glass-select:focus {
  border-color: #3b82f6;
  background: rgba(0, 0, 0, 0.5);
}

.scrub-row {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 8px 12px;
  border-radius: 12px;
}

.unit {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

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

.view-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
}

.camera-presets {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.presets-title {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  margin: 0 0 10px 0;
  font-weight: 600;
}

.preset-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
  margin-bottom: 10px;
}

.btn-preset {
  padding: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #fff;
  font-size: 11px;
  cursor: pointer;
  transition: 0.2s;
}

.btn-preset:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.regime-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.regime-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid;
  border-radius: 12px;
}

.regime-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  box-shadow: 0 0 10px currentColor;
}

.regime-name {
  font-weight: 600;
  color: #fff;
  font-size: 13px;
}

.regime-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.stat-label {
  color: rgba(255, 255, 255, 0.5);
}

.stat-value {
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.matrix-grid {
  display: grid;
  gap: 4px;
}

.matrix-row-group {
  display: contents;
}

.matrix-cell {
  padding: 12px 8px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
}

.m-val {
  font-weight: 700;
  font-family: "SF Mono", monospace;
  font-size: 14px;
}

.m-lbl {
  font-size: 9px;
  opacity: 0.7;
  margin-top: 2px;
}

.visualization-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.vis-title {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.vis-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 4px 0 0 0;
}

.timeline-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(0, 0, 0, 0.4);
  padding: 8px 16px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-play {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.2s;
}

.btn-play:hover,
.btn-play.active {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.timeline-wrapper {
  position: relative;
  width: 300px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  display: flex;
  align-items: center;
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
  margin: 0;
}

.timeline-track {
  height: 100%;
  background: #3b82f6;
  border-radius: 3px;
  pointer-events: none;
  transition: width 0.1s;
}

.timeline-thumb {
  position: absolute;
  top: 50%;
  width: 12px;
  height: 12px;
  background: #fff;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
  z-index: 2;
  pointer-events: none;
  transition: left 0.1s;
}

.speed-select {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 11px;
  cursor: pointer;
}

.btn-reset {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: 0.2s;
}

.btn-reset:hover {
  background: rgba(255, 255, 255, 0.15);
}

.current-date {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  font-family: "SF Mono", monospace;
  min-width: 100px;
  text-align: right;
}

.canvas-container {
  flex: 1;
  position: relative;
  background: #0a0a0f;
  border-radius: 16px;
  overflow: hidden;
  min-height: 600px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.canvas-container.loading {
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  z-index: 100;
}

.spinner-large {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-mini {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.stats-panel {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 16px;
  align-items: start;
}

.stats-card {
  background: rgba(0, 0, 0, 0.3);
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stats-card h4 {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  margin: 0 0 12px 0;
  font-weight: 600;
}

.distribution-bars {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.dist-bar {
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  transition: width 0.3s;
}

.dist-label {
  font-size: 10px;
  color: #fff;
  font-weight: 600;
  white-space: nowrap;
}

.duration-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.duration-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
}

.duration-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.duration-name {
  flex: 1;
  color: rgba(255, 255, 255, 0.8);
}

.duration-value {
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.export-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.btn-export {
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
  transition: 0.2s;
  white-space: nowrap;
}

.btn-export:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.text-green { color: #4ade80; }
.text-red { color: #f87171; }
.text-accent { color: #3b82f6; }
.font-bold { font-weight: 700; }

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 1400px) {
  .main-layout {
    grid-template-columns: 300px 1fr;
  }
}

@media (max-width: 1024px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
  
  .controls-panel {
    max-height: 400px;
  }
  
  .stats-panel {
    grid-template-columns: 1fr;
  }
}
</style>
