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
              <select
                v-model="selectedAsset"
                class="glass-select"
                @change="onAssetChange"
              >
                <option value="SPY">
                  S&P 500 (SPY)
                </option>
                <option value="QQQ">
                  Nasdaq 100 (QQQ)
                </option>
                <option value="BTC">
                  Bitcoin (BTC)
                </option>
                <option value="IMOEX">
                  IMOEX Index
                </option>
              </select>
            </div>

            <!-- Number of States -->
            <div class="input-group">
              <label class="lbl">Количество режимов</label>
              <div class="scrub-row">
                <ScrubInput 
                  v-model="nStates" 
                  :min="2"
                  :max="5"
                  :step="1" 
                  class="text-accent font-bold"
                  @update:model-value="onStatesChange"
                />
                <span class="unit">states</span>
              </div>
            </div>

            <!-- Time Period -->
            <div class="input-group">
              <label class="lbl">Временной период</label>
              <select
                v-model="timePeriod"
                class="glass-select"
                @change="onTimePeriodChange"
              >
                <option value="3M">
                  3 месяца
                </option>
                <option value="6M">
                  6 месяцев
                </option>
                <option value="1Y">
                  1 год
                </option>
                <option value="2Y">
                  2 года
                </option>
                <option value="ALL">
                  Все данные
                </option>
              </select>
            </div>

            <!-- Run Button -->
            <button
              :disabled="isLoading"
              class="btn-primary-gradient"
              @click="runAnalysis"
            >
              <span v-if="!isLoading">Запустить анализ</span>
              <span
                v-else
                class="flex items-center gap-2"
              >
                <span class="spinner-mini" /> Обучение HMM...
              </span>
            </button>
          </div>
        </div>

        <!-- View Controls -->
        <div
          v-if="hasData"
          class="glass-card panel"
        >
          <div class="panel-header">
            <h3>Вид</h3>
          </div>

          <div class="view-controls">
            <label class="checkbox-label">
              <input
                v-model="showTrajectory"
                type="checkbox"
                @change="onVisibilityChange"
              >
              <span>Траектория</span>
            </label>
            <label class="checkbox-label">
              <input
                v-model="showEllipsoids"
                type="checkbox"
                @change="onVisibilityChange"
              >
              <span>Эллипсоиды</span>
            </label>
            <label class="checkbox-label">
              <input
                v-model="showCentroids"
                type="checkbox"
                @change="onVisibilityChange"
              >
              <span>Центроиды</span>
            </label>
            <label class="checkbox-label">
              <input
                v-model="showGrid"
                type="checkbox"
                @change="onVisibilityChange"
              >
              <span>Сетка</span>
            </label>
          </div>

          <!-- Camera Presets -->
          <div class="camera-presets">
            <h4 class="presets-title">
              Вид камеры
            </h4>
            <div class="preset-buttons">
              <button 
                v-for="preset in cameraPresets" 
                :key="preset.name"
                class="btn-preset"
                @click="setCameraPreset(preset)"
              >
                {{ preset.label }}
              </button>
            </div>
            <label class="checkbox-label">
              <input
                v-model="autoRotate"
                type="checkbox"
                @change="onAutoRotateChange"
              >
              <span>Авто-вращение</span>
            </label>
          </div>
        </div>

        <!-- Current Regime Info -->
        <div
          v-if="currentRegimeInfo"
          class="glass-card panel"
        >
          <div class="panel-header">
            <h3>Текущий режим</h3>
          </div>
          <div class="regime-info">
            <div
              class="regime-badge"
              :style="{ borderColor: currentRegimeInfo.color }"
            >
              <span
                class="regime-dot"
                :style="{ backgroundColor: currentRegimeInfo.color }"
              />
              <span class="regime-name">{{ currentRegimeInfo.name }}</span>
            </div>
            <div class="regime-stats">
              <div class="stat-row">
                <span class="stat-label">Вероятность:</span>
                <span class="stat-value">{{ (currentRegimeInfo.probability * 100).toFixed(1) }}%</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Доходность:</span>
                <span
                  class="stat-value"
                  :class="currentRegimeInfo.meanReturn >= 0 ? 'text-green' : 'text-red'"
                >
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
          <div
            v-if="transitionMatrix"
            class="glass-card panel"
          >
            <div class="panel-header">
              <h3>Матрица переходов</h3>
            </div>
            <div
              class="matrix-grid"
              :style="{ gridTemplateColumns: `repeat(${nStates}, 1fr)` }"
            >
              <div
                v-for="(row, i) in transitionMatrix"
                :key="i"
                class="matrix-row-group"
              >
                <div 
                  v-for="(prob, j) in row" 
                  :key="j" 
                  class="matrix-cell"
                  :style="{ backgroundColor: `rgba(96, 165, 250, ${prob * 0.6})` }"
                >
                  <span class="m-val">{{ (prob * 100).toFixed(0) }}%</span>
                  <span class="m-lbl">S{{ i }}→S{{ j }}</span>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </aside>

      <!-- Main Content: 3D Visualization -->
      <main class="main-content">
        <!-- Header with Timeline Controls -->
        <div
          v-if="hasData"
          class="visualization-header"
        >
          <div class="header-left">
            <h2 class="vis-title">
              Пространство скрытых состояний
            </h2>
            <p class="vis-subtitle">
              3D визуализация рыночных режимов (HMM)
            </p>
          </div>

          <!-- Timeline Controls -->
          <div class="timeline-controls">
            <button 
              class="btn-play" 
              :class="{ active: isPlaying }"
              :disabled="!hasData || filteredData.length === 0"
              @click="togglePlayback"
            >
              {{ isPlaying ? '⏸' : '▶' }}
            </button>

            <div class="timeline-wrapper">
              <input 
                v-model.number="currentTimeIndex" 
                type="range" 
                :min="0" 
                :max="Math.max(0, (filteredData.length || 1) - 1)" 
                class="timeline-slider"
                :disabled="!hasData"
                @input="onTimelineChange"
              >
              <div
                class="timeline-track"
                :style="{ width: timelineProgress + '%' }"
              />
              <div
                class="timeline-thumb"
                :style="{ left: timelineProgress + '%' }"
              />
            </div>

            <select
              v-model="playbackSpeed"
              class="speed-select"
            >
              <option value="0.5">
                0.5x
              </option>
              <option value="1">
                1x
              </option>
              <option value="2">
                2x
              </option>
              <option value="5">
                5x
              </option>
            </select>

            <button
              class="btn-reset"
              :disabled="!hasData || filteredData.length === 0"
              @click="resetPlayback"
            >
              ↺
            </button>

            <div class="current-date">
              {{ currentDate }}
            </div>
          </div>
        </div>

        <!-- 3D Canvas Container -->
        <div
          ref="canvasContainer"
          class="canvas-container"
          :class="{ loading: isLoading }"
        >
          <div
            v-if="isLoading"
            class="loading-overlay"
          >
            <div class="spinner-large" />
            <p>Инициализация 3D пространства...</p>
          </div>
          
          <!-- Hover Info Tooltip (для ядер и эллипсоидов - вверху, для узлов траектории тоже вверху, но детализация внизу) -->
          <div 
            v-if="hoverInfo" 
            class="hover-tooltip"
            :style="{ 
              left: hoverPosition.x + 'px', 
              top: hoverPosition.y + 'px'
            }"
          >
            <div class="tooltip-header">
              <h4 class="tooltip-title">
                {{ hoverInfo.title }}
              </h4>
              <span class="tooltip-type">{{ hoverInfo.type }}</span>
            </div>
            <div class="tooltip-body">
              <div 
                v-for="(value, key) in filteredHoverData" 
                :key="key"
                class="tooltip-row"
              >
                <span class="tooltip-key">{{ key }}:</span>
                <span class="tooltip-value">{{ value }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Bottom Panel: Statistics -->
        <div
          v-if="hasData"
          class="stats-panel"
        >
          <!-- Stationary Distribution -->
          <div class="stats-card">
            <h4>Стационарное распределение</h4>
            <p class="info-hint">
              Долгосрочная вероятность каждого режима
            </p>
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
                <span class="dist-label">S{{ i }}: {{ (prob * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>

          <!-- Expected Durations -->
          <div class="stats-card">
            <h4>Ожидаемая длительность режимов</h4>
            <p class="info-hint">
              Средняя продолжительность режима в днях
            </p>
            <div class="duration-list">
              <div 
                v-for="(duration, i) in expectedDurations" 
                :key="i"
                class="duration-item"
              >
                <span
                  class="duration-dot"
                  :style="{ backgroundColor: regimeConfigs[i]?.color || '#888' }"
                />
                <span class="duration-name">{{ regimeConfigs[i]?.name || `Режим ${i}` }}</span>
                <span class="duration-value">{{ duration.toFixed(1) }} дней</span>
              </div>
            </div>
          </div>

          <!-- Hovered Trajectory Node Details -->
          <div
            v-if="hoveredTrajectoryNode"
            class="stats-card trajectory-node-details"
          >
            <h4>Детализация узла траектории</h4>
            <p class="info-hint">
              Информация о наведенном наблюдении
            </p>
            <div class="trajectory-node-data">
              <div class="data-row">
                <span class="data-label">Индекс:</span>
                <span class="data-value">{{ hoveredTrajectoryNode.timeIndex }}</span>
              </div>
              <div class="data-row">
                <span class="data-label">Дата:</span>
                <span class="data-value">{{ hoveredTrajectoryNode.point.date || 'N/A' }}</span>
              </div>
              <div class="data-row">
                <span class="data-label">Режим:</span>
                <span
                  class="data-value"
                  :style="{ color: regimeConfigs[hoveredTrajectoryNode.regimeId]?.color || '#fff' }"
                >
                  {{ regimeConfigs[hoveredTrajectoryNode.regimeId]?.name || `Режим ${hoveredTrajectoryNode.regimeId}` }}
                </span>
              </div>
              <div class="data-row">
                <span class="data-label">Доходность:</span>
                <span
                  class="data-value"
                  :class="hoveredTrajectoryNode.point.return && hoveredTrajectoryNode.point.return >= 0 ? 'text-green' : 'text-red'"
                >
                  {{ hoveredTrajectoryNode.point.return !== undefined ? (hoveredTrajectoryNode.point.return * 100).toFixed(2) + '%' : 'N/A' }}
                </span>
              </div>
              <div class="data-row">
                <span class="data-label">Волатильность:</span>
                <span class="data-value">{{ hoveredTrajectoryNode.point.volatility !== undefined ? hoveredTrajectoryNode.point.volatility.toFixed(2) + '%' : 'N/A' }}</span>
              </div>
              <div class="data-row">
                <span class="data-label">Ликвидность:</span>
                <span class="data-value">{{ hoveredTrajectoryNode.point.liquidity !== undefined ? hoveredTrajectoryNode.point.liquidity.toFixed(3) : 'N/A' }}</span>
              </div>
              <div
                v-if="hoveredTrajectoryNode.point.probability"
                class="data-row"
              >
                <span class="data-label">Вероятность режима:</span>
                <span class="data-value">{{ (hoveredTrajectoryNode.point.probability[hoveredTrajectoryNode.regimeId] * 100).toFixed(1) + '%' }}</span>
              </div>
            </div>
          </div>

          <!-- Export Buttons -->
          <div class="export-section">
            <button
              class="btn-export"
              @click="exportScreenshot"
            >
              📷 Скриншот
            </button>
            <button
              class="btn-export"
              @click="exportData"
            >
              📊 CSV
            </button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, shallowRef, computed, onMounted, onUnmounted, watch } from 'vue'
import { HMMModel, generateMockMarketData, type MarketPoint } from '@/composables/useHMMModel'
import { RegimeSpaceRenderer, type RegimeConfig, type CameraPreset, type HoverInfo } from '@/composables/useRegimeSpace3D'
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
// Visualization toggles - изначально включены сетка, эллипсоиды и траектория (для автоматической анимации)
const showTrajectory = ref(true)
const showEllipsoids = ref(true)
const showCentroids = ref(false)
const showGrid = ref(true)
const showTransitionArrows = ref(false)

// Hover интерактивность
const hoverInfo = ref<HoverInfo | null>(null)
const hoverPosition = ref({ x: 0, y: 0 })
const hoveredTrajectoryNode = ref<{ point: MarketPoint; timeIndex: number; regimeId: number } | null>(null)

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
const hmmModel = shallowRef<HMMModel | null>(null)
const transitionMatrix = ref<number[][] | null>(null)
const stationaryDistribution = ref<number[]>([])
const expectedDurations = ref<number[]>([])

// Renderer
let renderer: RegimeSpaceRenderer | null = null

// Regime Configs
// Цвета определяются по волатильности: низкая - голубой, средняя - оранжевый, высокая - красный
const regimeConfigs = ref<RegimeConfig[]>([
  { id: 0, name: 'Low Vol / Accumulation', color: '#60a5fa', mean: [0.15, 8.0, 0.8] }, // Голубой
  { id: 1, name: 'Normal / Trending', color: '#fb923c', mean: [0.08, 15.0, 0.6] }, // Оранжевый
  { id: 2, name: 'High Vol / Distribution', color: '#ef4444', mean: [-0.05, 35.0, 0.4] }, // Красный
  { id: 3, name: 'Crisis / Panic', color: '#dc2626', mean: [-0.20, 60.0, 0.2] }, // Темно-красный
  { id: 4, name: 'Recovery', color: '#fb923c', mean: [0.12, 20.0, 0.5] } // Оранжевый
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
  const regimeId = point.regime !== undefined ? Math.max(0, Math.min(point.regime, nStates.value - 1)) : 0
  
  // Clamp regimeId to valid range
  const clampedRegimeId = Math.max(0, Math.min(regimeId, regimeConfigs.value.length - 1))
  const config = regimeConfigs.value[clampedRegimeId]
  if (!config) return null

  const prob = point.probability && clampedRegimeId < point.probability.length 
    ? point.probability[clampedRegimeId] 
    : 0
    
  const means = hmmModel.value?.getEmissionMeans()
  const mean = means && clampedRegimeId < means.length 
    ? means[clampedRegimeId] 
    : [0, 0, 0]

  return {
    ...config,
    probability: prob,
    meanReturn: mean[0] || 0,
    meanVolatility: mean[1] || 0
  }
})

// Фильтрованные данные для hover tooltip (исключаем объекты и служебные поля)
const filteredHoverData = computed(() => {
  if (!hoverInfo.value || !hoverInfo.value.data) return {}
  
  const filtered: Record<string, string> = {}
  for (const [key, value] of Object.entries(hoverInfo.value.data)) {
    // Исключаем объекты, служебные поля и ID
    if (
      typeof value !== 'object' && 
      value !== null &&
      key !== 'point' && 
      key !== 'Индекс' && 
      key !== 'Режим ID'
    ) {
      filtered[key] = String(value)
    }
  }
  return filtered
})

// Helper function to get regime configs safely
const getRegimeConfigs = (): RegimeConfig[] => {
  const configs: RegimeConfig[] = []
  for (let i = 0; i < nStates.value; i++) {
    if (i < regimeConfigs.value.length) {
      configs.push(regimeConfigs.value[i])
    } else {
      // Create default config for missing states
      const defaultColors = ['#4ade80', '#60a5fa', '#a78bfa', '#f87171', '#fbbf24', '#fb923c', '#3b82f6']
      configs.push({
        id: i,
        name: `Режим ${i}`,
        color: defaultColors[i % defaultColors.length],
        mean: [0, 10, 0.5]
      })
    }
  }
  return configs
}

// Methods
const runAnalysis = async () => {
  if (!canvasContainer.value) {
    console.error('Canvas container not found')
    return
  }
  
  isLoading.value = true
  hasData.value = false
  
  try {
    // Загружаем данные из HMM модели
    const { getChartData, getRegimeStatistics, getTransitionMatrix } = await import('@/services/multivariateHmmService')
    const { usePortfolioStore } = await import('@/stores/portfolio')
    const portfolioStore = usePortfolioStore()
    
    // Получаем данные для визуализации
    const chartDataResponse = await getChartData()
    
    if (!chartDataResponse.success || !chartDataResponse.data || chartDataResponse.data.length === 0) {
      throw new Error('Нет данных HMM модели. Сначала запустите анализ на странице RegimeAnalysis.')
    }
    
    // Преобразуем данные в формат MarketPoint
    allMarketData.value = chartDataResponse.data.map((d, idx) => ({
      date: new Date(Date.now() - (chartDataResponse.data.length - idx) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      return: ((d.price ?? 100) - 100) / 100, // Приблизительная доходность
      volatility: d.vol ?? 0,
      liquidity: 0.5 + Math.random() * 0.5, // Заглушка для ликвидности
      regime: d.regime,
      probability: Array(nStates.value).fill(0).map((_: number, i: number) => i === d.regime ? 0.8 : 0.2 / (nStates.value - 1)),
      index: idx
    }))
    
    // Получаем матрицу переходов и статистику из HMM модели
    const [matrixResponse, statsResponse] = await Promise.all([
      getTransitionMatrix(),
      getRegimeStatistics()
    ])
    
    // Обновляем количество состояний на основе данных
    nStates.value = matrixResponse.n_regimes
    
    // Инициализируем HMM модель с данными из бэкенда
    hmmModel.value = new HMMModel()
    
    // Используем матрицу переходов из бэкенда
    const backendMatrix = matrixResponse.transition_matrix
    
    // Вычисляем средние и ковариации из статистики
    const adjustedMeans: number[][] = []
    const adjustedCovs: number[][][] = []
    
    for (let i = 0; i < statsResponse.statistics.length; i++) {
      const stat = statsResponse.statistics[i]
      // Преобразуем средние доходности в формат [return, volatility, liquidity]
      const meanReturn = stat.mean.reduce((a: number, b: number) => a + b, 0) / stat.mean.length
      const meanVol = stat.volatility_per_asset.reduce((a: number, b: number) => a + b, 0) / stat.volatility_per_asset.length
      adjustedMeans.push([meanReturn, meanVol, 0.5])
      
      // Создаем ковариационную матрицу из данных
      const cov = stat.covariance
      if (cov && cov.length >= 3 && cov[0].length >= 3) {
        adjustedCovs.push([
          [cov[0][0] || 0.01, cov[0][1] || 0, cov[0][2] || 0],
          [cov[1][0] || 0, cov[1][1] || 0.01, cov[1][2] || 0],
          [cov[2][0] || 0, cov[2][1] || 0, 0.1]
        ])
      } else {
        // Fallback ковариационная матрица
        adjustedCovs.push([
          [0.01, 0, 0],
          [0, 0.01, 0],
          [0, 0, 0.1]
        ])
      }
    }
    
    hmmModel.value.setParameters({
      nStates: nStates.value,
      transitionMatrix: backendMatrix,
      initialStateDistribution: Array(nStates.value).fill(1 / nStates.value),
      emissionMeans: adjustedMeans,
      emissionCovariances: adjustedCovs
    })
    
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
    transitionMatrix.value = backendMatrix
    
    // Initialize renderer
    if (canvasContainer.value && !renderer) {
      // Ensure container has dimensions
      if (canvasContainer.value.clientWidth === 0 || canvasContainer.value.clientHeight === 0) {
        console.warn('Canvas container has zero dimensions, retrying...')
        setTimeout(() => runAnalysis(), 200)
        return
      }
      
      renderer = new RegimeSpaceRenderer(canvasContainer.value)
      
      // Устанавливаем обработчик hover событий
      renderer.setOnHover((info) => {
        hoverInfo.value = info
        
        // Разделяем логику для узлов траектории и ядер/эллипсоидов
        if (info && info.type === 'trajectory-node') {
          // Для узлов траектории: показываем tooltip вверху И детализацию внизу
          hoverInfo.value = info
          const point = info.data['point'] as MarketPoint | undefined
          if (point) {
            hoveredTrajectoryNode.value = {
              point: point,
              timeIndex: parseInt(info.data['Индекс'] || '0'),
              regimeId: parseInt(info.data['Режим ID'] || '0')
            }
          }
        } else if (info && (info.type === 'centroid' || info.type === 'ellipsoid')) {
          // Для ядер и эллипсоидов: показываем только tooltip вверху
          hoverInfo.value = info
          hoveredTrajectoryNode.value = null
        } else {
          // Если нет hover или другой тип, очищаем всё
          hoverInfo.value = null
          hoveredTrajectoryNode.value = null
        }
      })
      
      // Обработчик движения мыши для позиции tooltip
      const handleMouseMove = (event: MouseEvent) => {
        if (canvasContainer.value && hoverInfo.value) {
          const rect = canvasContainer.value.getBoundingClientRect()
          hoverPosition.value = {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
          }
        }
      }
      canvasContainer.value.addEventListener('mousemove', handleMouseMove)
      onUnmounted(() => {
        if (canvasContainer.value) {
          canvasContainer.value.removeEventListener('mousemove', handleMouseMove)
        }
      })
      
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
      const configs = getRegimeConfigs()
      renderer.setData(filteredData.value, hmmModel.value, configs)
      
    }
    
    currentTimeIndex.value = filteredData.value.length - 1
    hasData.value = true
    
  } catch (error) {
    console.error('Error running analysis:', error)
    // Show error to user
    alert('Ошибка при запуске анализа: ' + (error as Error).message)
  } finally {
    isLoading.value = false
  }
}


const onAssetChange = () => {
  runAnalysis()
}

const onStatesChange = () => {
  // Update regime configs
  if (renderer && hmmModel.value) {
    const configs = getRegimeConfigs()
    renderer.setData(filteredData.value, hmmModel.value, configs)
  }
}

const onTimePeriodChange = () => {
  if (renderer && hmmModel.value) {
    const configs = getRegimeConfigs()
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
    // Ограничиваем индекс допустимыми значениями
    const maxIndex = Math.max(0, (filteredData.value.length || 1) - 1)
    currentTimeIndex.value = Math.max(0, Math.min(currentTimeIndex.value, maxIndex))
    
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
  
  if (!hasData.value || filteredData.value.length === 0) {
    return
  }
  
  const step = () => {
    if (!isPlaying.value || !hasData.value || filteredData.value.length === 0) {
      stopPlayback()
      return
    }
    
    const speed = parseFloat(playbackSpeed.value.toString())
    
    // Инкремент индекса в зависимости от скорости
    // Для скорости 1x делаем шаг 1, для 2x - шаг 2, и т.д.
    const stepSize = Math.max(1, Math.ceil(speed))
    currentTimeIndex.value = Math.min(
      currentTimeIndex.value + stepSize,
      filteredData.value.length - 1
    )
    
    if (currentTimeIndex.value >= filteredData.value.length - 1) {
      currentTimeIndex.value = filteredData.value.length - 1
      stopPlayback()
      return
    }
    
    onTimelineChange()
    // Адаптивная скорость интервала в зависимости от скорости воспроизведения
    // Быстрее скорость = меньше интервал между шагами для плавности
    const intervalDelay = Math.max(30, Math.min(200, 150 / speed)) // От 30ms до 200ms в зависимости от скорости
    playbackInterval = window.setTimeout(step, intervalDelay)
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
  if (hasData.value && filteredData.value.length > 0) {
    currentTimeIndex.value = 0
    onTimelineChange()
  }
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
    const configs = getRegimeConfigs()
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
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.main-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
  min-height: 0;
  padding: 24px 24px 24px 20px;
  box-sizing: border-box;
  align-items: start;
}

.controls-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: visible;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
  overflow: visible;
}

/* Glass Card Styles - matching RegimeAnalysis.vue */
.glass-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  box-shadow: 
    0 20px 50px -10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
}

.panel {
  padding: 24px;
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
  gap: 12px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.checkbox-label:hover {
  background: rgba(255, 255, 255, 0.05);
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
}

.camera-presets {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
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
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #fff;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  box-shadow: 0 2px 8px -2px rgba(0, 0, 0, 0.2);
}

.btn-preset:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.3);
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
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 2px solid;
  border-radius: 12px;
  box-shadow: 
    0 4px 12px -4px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
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
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-label {
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.stat-value {
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
  font-size: 13px;
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
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.matrix-cell:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.4);
  border-color: rgba(255, 255, 255, 0.1);
  z-index: 10;
}

.m-val {
  font-weight: 700;
  font-family: "SF Mono", monospace;
  font-size: 14px;
  line-height: 1.2;
}

.m-lbl {
  font-size: 9px;
  opacity: 0.7;
  margin-top: 2px;
  line-height: 1;
}

.visualization-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 16px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 16px;
}

.vis-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  letter-spacing: -0.01em;
}

.vis-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin: 4px 0 8px 0;
}


.timeline-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 8px 16px;
  border-radius: 24px;
  box-shadow: 
    0 10px 30px -10px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.btn-play {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  box-shadow: 0 4px 12px -4px rgba(0, 0, 0, 0.3);
}

.btn-play:hover:not(:disabled),
.btn-play.active:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px -4px rgba(0, 0, 0, 0.4);
}

.btn-play:disabled,
.btn-reset:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.timeline-wrapper {
  position: relative;
  width: 300px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border-radius: 3px;
  display: flex;
  align-items: center;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
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
  background: #60a5fa;
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
  box-shadow: 0 0 10px rgba(96, 165, 250, 0.4);
  z-index: 2;
  pointer-events: none;
  transition: left 0.1s;
}

.speed-select {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.speed-select:hover {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.4);
}

.speed-select:focus {
  border-color: #3b82f6;
  background: rgba(0, 0, 0, 0.5);
  outline: none;
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
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.canvas-container {
  flex: 1;
  position: relative;
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  overflow: hidden;
  min-height: 600px;
  height: 600px;
  max-height: 80vh;
  box-shadow: 
    0 20px 50px -10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
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
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  z-index: 100;
  border-radius: 24px;
}

.spinner-large {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #60a5fa;
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
  gap: 20px;
  align-items: start;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.stats-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 
    0 20px 50px -10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.stats-card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
}

.stats-card h4 {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  margin: 0 0 16px 0;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.distribution-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dist-bar {
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  padding: 0 12px;
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
  box-shadow: 
    0 2px 8px -2px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.2);
}

.dist-bar:hover {
  transform: scaleY(1.05);
  box-shadow: 
    0 4px 12px -2px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.1);
}

.dist-label {
  font-size: 10px;
  color: #fff;
  font-weight: 700;
  white-space: nowrap;
  font-family: "SF Mono", monospace;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.duration-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.duration-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.duration-item:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateX(4px);
}

.duration-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  box-shadow: 0 0 8px currentColor;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.duration-item:hover .duration-dot {
  transform: scale(1.2);
  box-shadow: 0 0 12px currentColor;
}

.duration-name {
  flex: 1;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.duration-value {
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
  font-size: 11px;
}

/* Trajectory Node Details Styles */
.trajectory-node-details {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(96, 165, 250, 0.1));
  border: 1px solid rgba(96, 165, 250, 0.3);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.trajectory-node-data {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}

.data-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.data-row:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateX(4px);
}

.data-label {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  font-size: 12px;
}

.data-value {
  color: #fff;
  font-weight: 700;
  font-family: "SF Mono", monospace;
  font-size: 12px;
}

.export-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.btn-export {
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  white-space: nowrap;
  box-shadow: 0 4px 12px -4px rgba(0, 0, 0, 0.3);
}

.btn-export:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px -4px rgba(0, 0, 0, 0.4);
}

.text-green { color: #4ade80; }
.text-red { color: #f87171; }
.text-accent { color: #3b82f6; }
.font-bold { font-weight: 700; }

/* Info hints and legends */
.info-hint {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0 0 12px 0;
  font-style: italic;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.legend-text {
  flex: 1;
}

/* Info overlay */
.info-overlay {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
  max-width: 280px;
}

.info-card {
  background: rgba(30, 32, 40, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.info-card h5 {
  margin: 0 0 12px 0;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-card p {
  margin: 0 0 10px 0;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
}

.info-card ul {
  margin: 0;
  padding-left: 18px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.6;
}

.info-card li {
  margin-bottom: 4px;
}

.info-card strong {
  color: #ffd700;
  font-weight: 600;
}


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
    grid-template-columns: 280px 1fr;
  }
}

@media (max-width: 1024px) {
  .main-layout {
    grid-template-columns: 1fr;
    padding: 16px;
    gap: 16px;
  }

  .controls-panel {
    overflow: visible;
  }

  .stats-panel {
    grid-template-columns: 1fr;
  }

  .visualization-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .timeline-controls {
    width: 100%;
    flex-wrap: wrap;
    padding: 12px;
    gap: 10px;
  }

  .timeline-wrapper {
    width: 100%;
    order: 3;
    margin-top: 8px;
  }

  .canvas-container {
    min-height: 400px;
    height: 400px;
  }
}

@media (max-width: 768px) {
  .main-layout {
    padding: 12px;
    gap: 12px;
  }

  .glass-card.panel {
    padding: 16px;
    border-radius: 16px;
  }

  .panel-header h3 {
    font-size: 10px;
    margin-bottom: 12px;
  }

  .input-group {
    gap: 4px;
  }

  .lbl {
    font-size: 10px;
  }

  .glass-select {
    padding: 10px;
    font-size: 13px;
    min-height: 44px; /* Touch target */
  }

  .scrub-row {
    padding: 10px;
  }

  .btn-primary-gradient {
    padding: 14px;
    font-size: 14px;
    min-height: 48px;
  }

  .checkbox-label {
    font-size: 13px;
    padding: 10px 8px;
    min-height: 44px;
  }

  .preset-buttons {
    gap: 8px;
  }

  .btn-preset {
    padding: 10px;
    font-size: 12px;
    min-height: 44px;
  }

  .regime-badge {
    padding: 14px;
    gap: 12px;
  }

  .regime-name {
    font-size: 14px;
  }

  .stat-row {
    font-size: 13px;
    padding: 8px 0;
  }

  .stat-value {
    font-size: 14px;
  }

  .matrix-cell {
    padding: 10px 6px;
  }

  .m-val {
    font-size: 12px;
  }

  .m-lbl {
    font-size: 8px;
  }

  .vis-title {
    font-size: 22px;
  }

  .vis-subtitle {
    font-size: 12px;
  }

  .timeline-controls {
    padding: 10px 12px;
    border-radius: 16px;
    gap: 8px;
  }

  .btn-play {
    width: 44px;
    height: 44px;
    font-size: 16px;
  }

  .speed-select {
    padding: 8px 10px;
    font-size: 12px;
    min-height: 40px;
  }

  .btn-reset {
    padding: 8px 14px;
    min-height: 40px;
  }

  .current-date {
    font-size: 10px;
    padding: 8px;
    min-width: 80px;
  }

  .canvas-container {
    min-height: 350px;
    height: 350px;
    border-radius: 16px;
  }

  .stats-card {
    padding: 16px;
    border-radius: 16px;
  }

  .stats-card h4 {
    font-size: 10px;
    margin-bottom: 12px;
  }

  .info-hint {
    font-size: 9px;
    margin-bottom: 10px;
  }

  .dist-bar {
    height: 32px;
    padding: 0 10px;
  }

  .dist-label {
    font-size: 11px;
  }

  .duration-item {
    font-size: 13px;
    padding: 10px;
  }

  .duration-value {
    font-size: 12px;
  }

  .data-row {
    padding: 10px;
  }

  .data-label,
  .data-value {
    font-size: 13px;
  }

  .btn-export {
    padding: 12px 16px;
    font-size: 13px;
    min-height: 44px;
  }

  .hover-tooltip {
    min-width: 200px;
    max-width: 280px;
    padding: 10px 12px;
    font-size: 11px;
  }

  .tooltip-title {
    font-size: 13px;
  }

  .tooltip-row {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .main-layout {
    padding: 8px;
    gap: 8px;
  }

  .glass-card.panel {
    padding: 12px;
    border-radius: 12px;
  }

  .vis-title {
    font-size: 18px;
  }

  .vis-subtitle {
    font-size: 11px;
  }

  .timeline-controls {
    padding: 8px 10px;
    border-radius: 12px;
  }

  .btn-play {
    width: 40px;
    height: 40px;
  }

  .canvas-container {
    min-height: 280px;
    height: 280px;
    border-radius: 12px;
  }

  .stats-card {
    padding: 12px;
    border-radius: 12px;
  }

  .matrix-cell {
    padding: 8px 4px;
  }

  .m-val {
    font-size: 10px;
  }

  .export-section {
    flex-direction: row;
    gap: 8px;
  }

  .btn-export {
    flex: 1;
    padding: 10px 12px;
    font-size: 11px;
  }
}

@media (max-width: 375px) {
  .canvas-container {
    min-height: 240px;
    height: 240px;
  }

  .vis-title {
    font-size: 16px;
  }

  .timeline-controls {
    padding: 6px 8px;
  }

  .btn-play {
    width: 36px;
    height: 36px;
  }

  .current-date {
    display: none;
  }
}

/* Hover Tooltip Styles */
.hover-tooltip {
  position: absolute;
  z-index: 1000;
  pointer-events: none;
  min-width: 240px;
  max-width: 320px;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.1);
  animation: tooltipFadeIn 0.2s ease-out;
  transform: translateX(15px) translateY(-50%);
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: translateX(25px) translateY(-50%);
  }
  to {
    opacity: 1;
    transform: translateX(15px) translateY(-50%);
  }
}

.tooltip-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tooltip-title {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.tooltip-type {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.tooltip-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  font-size: 12px;
  line-height: 1.5;
}

.tooltip-key {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  flex-shrink: 0;
  min-width: 100px;
}

.tooltip-value {
  color: #fff;
  font-weight: 600;
  font-family: "SF Mono", monospace;
  text-align: right;
  word-break: break-word;
}
</style>
