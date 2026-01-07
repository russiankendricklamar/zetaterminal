<template>
  <div class="correlation-scatter-3d">
    <!-- Main Layout: Controls and Plot side by side -->
    <div class="main-layout">
      <!-- Left: Controls -->
      <div class="controls-column">
        <!-- Control Panel -->
        <div class="control-panel">
          <!-- Two Column Layout -->
          <div class="controls-two-column">
            <!-- First Column -->
            <div class="controls-col-1">
              <!-- Asset Selection - Vertical Stack -->
              <div class="control-group">
                <label>Актив 1 (X):</label>
                <select v-model="selectedAssets[0]" @change="updatePlot">
                  <option v-for="asset in availableAssets" :key="asset" :value="asset">{{ asset }}</option>
                </select>
              </div>
              <div class="control-group">
                <label>Актив 2 (Y):</label>
                <select v-model="selectedAssets[1]" @change="updatePlot">
                  <option v-for="asset in availableAssets" :key="asset" :value="asset">{{ asset }}</option>
                </select>
              </div>
              <div class="control-group">
                <label>Актив 3 (Z):</label>
                <select v-model="selectedAssets[2]" @change="updatePlot">
                  <option v-for="asset in availableAssets" :key="asset" :value="asset">{{ asset }}</option>
                </select>
              </div>

              <!-- Time Range Slider - Full Width -->
              <div class="control-group full-width">
                <label>Период: {{ dateRange[0] }} - {{ dateRange[1] }}</label>
                <input 
                  type="range" 
                  :min="0" 
                  :max="filteredData.length - 1" 
                  v-model="timeRange" 
                  @input="updateTimeRange"
                  class="time-slider full-width-slider"
                />
              </div>

              <!-- Reset Button -->
              <button class="btn-reset full-width" @click="resetView">
                <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                Сброс
              </button>
            </div>

            <!-- Second Column -->
            <div class="controls-col-2">
              <!-- View Mode -->
              <div class="control-group">
                <label>Режим:</label>
                <div class="toggle-buttons">
                  <button 
                    :class="['toggle-btn', { active: viewMode === '3d' }]"
                    @click="viewMode = '3d'; updatePlot()"
                  >
                    3D
                  </button>
                  <button 
                    :class="['toggle-btn', { active: viewMode === '2d' }]"
                    @click="viewMode = '2d'; updatePlot()"
                  >
                    2D
                  </button>
                </div>
              </div>

              <!-- Space Toggle -->
              <div class="control-group">
                <label>Пространство:</label>
                <div class="toggle-buttons">
                  <button 
                    :class="['toggle-btn', { active: spaceMode === 'correlation' }]"
                    @click="spaceMode = 'correlation'; updatePlot()"
                  >
                    Correlation
                  </button>
                  <button 
                    :class="['toggle-btn', { active: spaceMode === 'pca' }]"
                    @click="spaceMode = 'pca'; updatePlot()"
                  >
                    PCA
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Regime Filters - In One Row -->
          <div class="controls-row regime-row">
            <label class="regime-filter-label">Режимы:</label>
            <label class="regime-checkbox" v-for="regime in regimes" :key="regime.id">
              <input 
                type="checkbox" 
                :value="regime.id" 
                v-model="visibleRegimes"
                @change="updatePlot"
              />
              <span class="regime-dot" :style="{ backgroundColor: regime.color }"></span>
              {{ regime.name }}
            </label>
          </div>

          <!-- Advanced Controls - Dropdown -->
          <div class="control-group">
            <div class="dropdown-controls">
              <button 
                class="dropdown-toggle"
                @click="showAdvancedDropdown = !showAdvancedDropdown"
              >
                <span>Дополнительные настройки</span>
                <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="showAdvancedDropdown ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'"></path>
                </svg>
              </button>
              <div v-show="showAdvancedDropdown" class="dropdown-content">
                <label class="checkbox-item">
                  <input type="checkbox" v-model="showTrajectory" @change="updatePlot" />
                  <span>Траектория</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="showRegressions" @change="updatePlot" />
                  <span>Регрессии</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="showOutliers" @change="updatePlot" />
                  <span>Outliers</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="showEllipsoids" @change="updatePlot" />
                  <span>Эллипсоиды</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="showClusters" @change="updatePlot" />
                  <span>Кластеры</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="showCentroids" @change="updatePlot" />
                  <span>Центроиды</span>
                </label>
              </div>
            </div>
          </div>

      <!-- Playback Controls -->
      <div class="controls-row playback-controls" v-if="showTrajectory">
        <button 
          :class="['btn-playback', { active: isPlaying }]"
          @click="togglePlayback"
        >
          {{ isPlaying ? '⏸' : '▶' }}
        </button>
        <input 
          type="range" 
          :min="0" 
          :max="100" 
          v-model="playbackProgress"
          @input="updatePlaybackPosition"
          class="playback-slider"
        />
        <input 
          type="range" 
          :min="1" 
          :max="10" 
          v-model="playbackSpeed"
          class="speed-slider"
          title="Speed"
        />
        <span class="speed-label">{{ playbackSpeed }}x</span>
        </div>
      </div>

        <!-- Statistics Panel -->
        <div class="stats-panel">
          <div class="stats-section">
            <h4>Корреляции</h4>
            <div class="correlation-stats">
              <div class="stat-item">
                <span class="stat-label-large">{{ selectedAssets[0] }} ↔ {{ selectedAssets[1] }}</span>
                <span class="stat-value-large">{{ correlationMatrix[0][1].toFixed(3) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label-large">{{ selectedAssets[0] }} ↔ {{ selectedAssets[2] }}</span>
                <span class="stat-value-large">{{ correlationMatrix[0][2].toFixed(3) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label-large">{{ selectedAssets[1] }} ↔ {{ selectedAssets[2] }}</span>
                <span class="stat-value-large">{{ correlationMatrix[1][2].toFixed(3) }}</span>
              </div>
            </div>
          </div>

          <div class="stats-section">
            <h4>Статистика</h4>
            <div class="stats-grid-compact">
              <div class="stat-item-compact" v-for="(stat, idx) in axisStats" :key="idx">
                <span class="stat-label-large">{{ selectedAssets[idx] }}</span>
                <div class="stat-details-large">
                  <span>μ: {{ stat.mean.toFixed(2) }}%</span>
                  <span>σ: {{ stat.std.toFixed(2) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Plot Container -->
      <div class="plot-column">
        <!-- Loading Indicator -->
        <div v-if="isLoading" class="loading-overlay">
      <div class="spinner-large"></div>
      <p>Загрузка данных...</p>
    </div>

        <!-- Plot Container -->
        <div ref="plotContainer" class="plot-container"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'

// Types
interface DataPoint {
  date: string
  returns: { [key: string]: number }
  regime: string
  volume: number
  index: number
}

interface Regime {
  id: string
  name: string
  color: string
}

interface AxisStats {
  mean: number
  std: number
  min: number
  max: number
}

// Props
const props = defineProps<{
  availableAssets?: string[]
}>()

// Reactive state
const plotContainer = ref<HTMLElement | null>(null)
const isLoading = ref(true)
const Plotly: any = ref(null)

const availableAssets = ref(props.availableAssets || ['SPY', 'TLT', 'GLD', 'QQQ', 'BTC'])
const selectedAssets = ref([availableAssets.value[0], availableAssets.value[1], availableAssets.value[2]])
const viewMode = ref<'3d' | '2d'>('3d')
const spaceMode = ref<'correlation' | 'pca'>('correlation')
const timeRange = ref(0)
const dateRange = ref<[string, string]>(['', ''])
const visibleRegimes = ref<string[]>(['low', 'medium', 'high'])
const showTrajectory = ref(false)
const showEllipsoids = ref(false)
const showRegressions = ref(false)
const showClusters = ref(false)
const showCentroids = ref(false)
const showOutliers = ref(true)
const showAdvancedDropdown = ref(false)

// Playback state
const isPlaying = ref(false)
const playbackProgress = ref(0)
const playbackSpeed = ref(1)
let playbackInterval: number | null = null

// Data
const allData = ref<DataPoint[]>([])
const filteredData = computed(() => {
  return allData.value.filter((point, idx) => {
    if (idx < timeRange.value) return false
    return visibleRegimes.value.includes(point.regime)
  })
})

const regimes: Regime[] = [
  { id: 'low', name: 'Low', color: '#10b981' },
  { id: 'medium', name: 'Medium', color: '#fbbf24' },
  { id: 'high', name: 'High', color: '#ef4444' }
]

// Statistics
const axisStats = ref<AxisStats[]>([
  { mean: 0, std: 0, min: 0, max: 0 },
  { mean: 0, std: 0, min: 0, max: 0 },
  { mean: 0, std: 0, min: 0, max: 0 }
])

const correlationMatrix = ref<number[][]>([
  [1.0, 0.0, 0.0],
  [0.0, 1.0, 0.0],
  [0.0, 0.0, 1.0]
])

// PCA components (computed)
const pcaComponents = ref<number[][]>([])

// Load Plotly
const loadPlotly = async () => {
  if (typeof window !== 'undefined' && !window.Plotly) {
    const script = document.createElement('script')
    script.src = 'https://cdn.plot.ly/plotly-latest.min.js'
    script.async = true
    document.head.appendChild(script)
    return new Promise((resolve) => {
      script.onload = () => {
        Plotly.value = window.Plotly
        resolve(Plotly.value)
      }
    })
  }
  Plotly.value = window.Plotly
  return Plotly.value
}

// Generate mock data
const generateMockData = (): DataPoint[] => {
  const days = 252
  const data: DataPoint[] = []
  const startDate = new Date('2024-01-01')
  
  // Correlation matrix between assets
  const correlations: { [key: string]: { [key: string]: number } } = {
    'SPY': { 'TLT': -0.35, 'GLD': 0.15, 'QQQ': 0.92, 'BTC': 0.45 },
    'TLT': { 'SPY': -0.35, 'GLD': 0.25, 'QQQ': -0.42, 'BTC': -0.15 },
    'GLD': { 'SPY': 0.15, 'TLT': 0.25, 'QQQ': 0.10, 'BTC': 0.20 },
    'QQQ': { 'SPY': 0.92, 'TLT': -0.42, 'GLD': 0.10, 'BTC': 0.55 },
    'BTC': { 'SPY': 0.45, 'TLT': -0.15, 'GLD': 0.20, 'QQQ': 0.55 }
  }

  // Regime parameters
  const regimeParams = {
    low: { vol: 0.008, trend: 0.001 },
    medium: { vol: 0.015, trend: 0.0005 },
    high: { vol: 0.030, trend: -0.001 }
  }

  let currentRegime = 'low'
  let regimeDays = 0
  let regimeLength = 30 + Math.random() * 60 // 30-90 days per regime

  const returns: { [key: string]: number[] } = {}
  availableAssets.value.forEach(asset => {
    returns[asset] = []
  })

  for (let i = 0; i < days; i++) {
    // Regime switching logic
    regimeDays++
    if (regimeDays > regimeLength) {
      const rand = Math.random()
      if (currentRegime === 'low') {
        currentRegime = rand > 0.7 ? 'high' : 'medium'
      } else if (currentRegime === 'medium') {
        currentRegime = rand > 0.6 ? 'high' : 'low'
      } else {
        currentRegime = rand > 0.7 ? 'low' : 'medium'
      }
      regimeDays = 0
      regimeLength = 30 + Math.random() * 60
    }

    const params = regimeParams[currentRegime as keyof typeof regimeParams]
    
    // Generate correlated returns using Cholesky decomposition approximation
    const dailyReturns: { [key: string]: number } = {}
    
    // Start with first asset (SPY as base)
    const baseAsset = availableAssets.value[0]
    const baseReturn = (Math.random() - 0.5) * params.vol * 2 + params.trend
    returns[baseAsset].push(baseReturn)
    dailyReturns[baseAsset] = baseReturn

    // Generate other assets based on correlations
    for (let j = 1; j < availableAssets.value.length; j++) {
      const asset = availableAssets.value[j]
      const prevAsset = availableAssets.value[j - 1]
      const corr = correlations[prevAsset]?.[asset] || 0
      
      const independent = (Math.random() - 0.5) * params.vol * 2
      const correlated = corr * returns[prevAsset][i]
      const assetReturn = correlated + Math.sqrt(1 - corr * corr) * independent + params.trend
      
      returns[asset].push(assetReturn)
      dailyReturns[asset] = assetReturn
    }

    const date = new Date(startDate)
    date.setDate(date.getDate() + i)

    data.push({
      date: date.toISOString().split('T')[0],
      returns: dailyReturns,
      regime: currentRegime,
      volume: Math.random() * 1000000 + 100000,
      index: i
    })
  }

  return data
}

// Compute PCA
const computePCA = (data: DataPoint[]) => {
  if (data.length === 0) return

  const asset1 = selectedAssets.value[0]
  const asset2 = selectedAssets.value[1]
  const asset3 = selectedAssets.value[2]

  const x = data.map(d => d.returns[asset1] || 0)
  const y = data.map(d => d.returns[asset2] || 0)
  const z = data.map(d => d.returns[asset3] || 0)

  // Compute covariance matrix
  const n = data.length
  const meanX = x.reduce((a, b) => a + b, 0) / n
  const meanY = y.reduce((a, b) => a + b, 0) / n
  const meanZ = z.reduce((a, b) => a + b, 0) / n

  const covXX = x.reduce((sum, val) => sum + (val - meanX) ** 2, 0) / n
  const covYY = y.reduce((sum, val) => sum + (val - meanY) ** 2, 0) / n
  const covZZ = z.reduce((sum, val) => sum + (val - meanZ) ** 2, 0) / n
  const covXY = x.reduce((sum, val, i) => sum + (val - meanX) * (y[i] - meanY), 0) / n
  const covXZ = x.reduce((sum, val, i) => sum + (val - meanX) * (z[i] - meanZ), 0) / n
  const covYZ = y.reduce((sum, val, i) => sum + (val - meanY) * (z[i] - meanZ), 0) / n

  // Simplified 2x2 PCA (PC1, PC2) for visualization
  const covMatrix2D = [
    [covXX, covXY],
    [covXY, covYY]
  ]

  // Eigenvalues and eigenvectors (simplified)
  const trace = covMatrix2D[0][0] + covMatrix2D[1][1]
  const det = covMatrix2D[0][0] * covMatrix2D[1][1] - covMatrix2D[0][1] ** 2
  const discriminant = trace ** 2 - 4 * det

  if (discriminant < 0) return

  const eigenval1 = (trace + Math.sqrt(discriminant)) / 2
  const eigenval2 = (trace - Math.sqrt(discriminant)) / 2

  const eigenvec1 = [
    covMatrix2D[0][1],
    eigenval1 - covMatrix2D[0][0]
  ]
  const len1 = Math.sqrt(eigenvec1[0] ** 2 + eigenvec1[1] ** 2)
  if (len1 > 0) {
    eigenvec1[0] /= len1
    eigenvec1[1] /= len1
  }

  const eigenvec2 = [
    covMatrix2D[0][1],
    eigenval2 - covMatrix2D[0][0]
  ]
  const len2 = Math.sqrt(eigenvec2[0] ** 2 + eigenvec2[1] ** 2)
  if (len2 > 0) {
    eigenvec2[0] /= len2
    eigenvec2[1] /= len2
  }

  // Project data onto PC1 and PC2
  pcaComponents.value = data.map((d, i) => {
    const xNorm = x[i] - meanX
    const yNorm = y[i] - meanY
    const zNorm = z[i] - meanZ

    const pc1 = xNorm * eigenvec1[0] + yNorm * eigenvec1[1]
    const pc2 = xNorm * eigenvec2[0] + yNorm * eigenvec2[1]

    return [pc1, pc2, zNorm]
  })
}

// K-means clustering
const kMeansClusters = ref<number[]>([])
const computeKMeans = (data: DataPoint[], k: number = 3) => {
  const asset1 = selectedAssets.value[0]
  const asset2 = selectedAssets.value[1]
  const asset3 = selectedAssets.value[2]

  const points = data.map(d => [
    d.returns[asset1] || 0,
    d.returns[asset2] || 0,
    d.returns[asset3] || 0
  ])

  if (points.length === 0) return

  // Initialize centroids randomly
  let centroids: number[][] = []
  for (let i = 0; i < k; i++) {
    const randomIdx = Math.floor(Math.random() * points.length)
    centroids.push([...points[randomIdx]])
  }

  let clusters: number[] = []
  let iterations = 0
  const maxIterations = 100

  while (iterations < maxIterations) {
    // Assign points to nearest centroid
    clusters = points.map(point => {
      let minDist = Infinity
      let closestCentroid = 0
      centroids.forEach((centroid, idx) => {
        const dist = Math.sqrt(
          (point[0] - centroid[0]) ** 2 +
          (point[1] - centroid[1]) ** 2 +
          (point[2] - centroid[2]) ** 2
        )
        if (dist < minDist) {
          minDist = dist
          closestCentroid = idx
        }
      })
      return closestCentroid
    })

    // Update centroids
    const newCentroids: number[][] = Array(k).fill(null).map(() => [0, 0, 0])
    const counts = Array(k).fill(0)

    points.forEach((point, idx) => {
      const cluster = clusters[idx]
      newCentroids[cluster][0] += point[0]
      newCentroids[cluster][1] += point[1]
      newCentroids[cluster][2] += point[2]
      counts[cluster]++
    })

    let converged = true
    newCentroids.forEach((centroid, idx) => {
      if (counts[idx] > 0) {
        centroid[0] /= counts[idx]
        centroid[1] /= counts[idx]
        centroid[2] /= counts[idx]
        
        const oldCentroid = centroids[idx]
        const dist = Math.sqrt(
          (centroid[0] - oldCentroid[0]) ** 2 +
          (centroid[1] - oldCentroid[1]) ** 2 +
          (centroid[2] - oldCentroid[2]) ** 2
        )
        if (dist > 0.001) converged = false
      }
    })

    if (converged) break
    centroids = newCentroids
    iterations++
  }

  kMeansClusters.value = clusters
}

// Compute statistics
const computeStatistics = () => {
  const asset1 = selectedAssets.value[0]
  const asset2 = selectedAssets.value[1]
  const asset3 = selectedAssets.value[2]

  const returns1 = filteredData.value.map(d => (d.returns[asset1] || 0) * 100)
  const returns2 = filteredData.value.map(d => (d.returns[asset2] || 0) * 100)
  const returns3 = filteredData.value.map(d => (d.returns[asset3] || 0) * 100)

  const computeStats = (arr: number[]): AxisStats => {
    if (arr.length === 0) return { mean: 0, std: 0, min: 0, max: 0 }
    const mean = arr.reduce((a, b) => a + b, 0) / arr.length
    const variance = arr.reduce((sum, val) => sum + (val - mean) ** 2, 0) / arr.length
    const std = Math.sqrt(variance)
    return {
      mean,
      std,
      min: Math.min(...arr),
      max: Math.max(...arr)
    }
  }

  axisStats.value = [
    computeStats(returns1),
    computeStats(returns2),
    computeStats(returns3)
  ]

  // Compute correlation matrix
  const n = filteredData.value.length
  if (n > 1) {
    const mean1 = axisStats.value[0].mean / 100
    const mean2 = axisStats.value[1].mean / 100
    const mean3 = axisStats.value[2].mean / 100

    const std1 = axisStats.value[0].std / 100
    const std2 = axisStats.value[1].std / 100
    const std3 = axisStats.value[2].std / 100

    const corr12 = filteredData.value.reduce((sum, d) => {
      const r1 = (d.returns[asset1] || 0) - mean1
      const r2 = (d.returns[asset2] || 0) - mean2
      return sum + r1 * r2
    }, 0) / (n * std1 * std2)

    const corr13 = filteredData.value.reduce((sum, d) => {
      const r1 = (d.returns[asset1] || 0) - mean1
      const r3 = (d.returns[asset3] || 0) - mean3
      return sum + r1 * r3
    }, 0) / (n * std1 * std3)

    const corr23 = filteredData.value.reduce((sum, d) => {
      const r2 = (d.returns[asset2] || 0) - mean2
      const r3 = (d.returns[asset3] || 0) - mean3
      return sum + r2 * r3
    }, 0) / (n * std2 * std3)

    correlationMatrix.value = [
      [1.0, corr12, corr13],
      [corr12, 1.0, corr23],
      [corr13, corr23, 1.0]
    ]
  }
}

// Update plot
const updatePlot = async () => {
  if (!Plotly.value || !plotContainer.value) return

  const data = filteredData.value
  if (data.length === 0) return

  // Compute PCA if needed
  if (spaceMode.value === 'pca') {
    computePCA(data)
  }

  // Compute clusters if needed
  if (showClusters.value) {
    computeKMeans(data, 3)
  }

  // Compute statistics
  computeStatistics()

  // Prepare data arrays
  const asset1 = selectedAssets.value[0]
  const asset2 = selectedAssets.value[1]
  const asset3 = selectedAssets.value[2]

  let x: number[], y: number[], z: number[]

  if (spaceMode.value === 'pca' && pcaComponents.value.length > 0) {
    x = pcaComponents.value.map(pc => pc[0] * 100)
    y = pcaComponents.value.map(pc => pc[1] * 100)
    z = pcaComponents.value.map(pc => pc[2] * 100)
  } else {
    x = data.map(d => (d.returns[asset1] || 0) * 100)
    y = data.map(d => (d.returns[asset2] || 0) * 100)
    z = data.map(d => (d.returns[asset3] || 0) * 100)
  }

  const colors = data.map(d => {
    const regime = regimes.find(r => r.id === d.regime)
    return regime ? regime.color : '#888'
  })

  const sizes = data.map(d => Math.sqrt(d.volume / 10000))
  const texts = data.map((d, i) => 
    `${d.date}<br>${asset1}: ${x[i].toFixed(2)}%<br>${asset2}: ${y[i].toFixed(2)}%<br>${asset3}: ${z[i].toFixed(2)}%<br>Режим: ${regimes.find(r => r.id === d.regime)?.name || d.regime}`
  )

  // Detect outliers (3 standard deviations)
  const outliers: boolean[] = []
  const stats1 = axisStats.value[0]
  const stats2 = axisStats.value[1]
  const stats3 = axisStats.value[2]

  data.forEach((d, i) => {
    const isOutlier = 
      Math.abs(x[i] - stats1.mean) > 3 * stats1.std ||
      Math.abs(y[i] - stats2.mean) > 3 * stats2.std ||
      Math.abs(z[i] - stats3.mean) > 3 * stats3.std
    outliers.push(isOutlier)
  })

  // Prepare traces
  const traces: any[] = []

  // Main scatter plot by regime
  regimes.forEach(regime => {
    if (!visibleRegimes.value.includes(regime.id)) return

    const regimeIndices = data
      .map((d, i) => ({ d, i }))
      .filter(({ d }) => d.regime === regime.id)
      .map(({ i }) => i)

    if (regimeIndices.length === 0) return

    const regimeX = regimeIndices.map(i => x[i])
    const regimeY = regimeIndices.map(i => y[i])
    const regimeZ = regimeIndices.map(i => z[i])
    const regimeColors = regimeIndices.map(i => colors[i])
    const regimeSizes = regimeIndices.map(i => sizes[i])
    const regimeTexts = regimeIndices.map(i => texts[i])
    const regimeOutliers = regimeIndices.map(i => outliers[i])

    // Regular points
    const regularIndices = regimeIndices.filter((_, idx) => !regimeOutliers[idx] || !showOutliers.value)
    if (regularIndices.length > 0) {
      traces.push({
        x: regularIndices.map(i => x[i]),
        y: regularIndices.map(i => y[i]),
        z: viewMode.value === '3d' ? regularIndices.map(i => z[i]) : undefined,
        mode: showTrajectory.value ? 'lines+markers' : 'markers',
        type: viewMode.value === '3d' ? 'scatter3d' : 'scatter',
        name: regime.name,
        marker: {
          color: regime.color,
          size: regularIndices.map(i => sizes[i]),
          sizeref: 0.1,
          sizemode: 'diameter',
          opacity: 0.7,
          line: {
            color: 'rgba(0,0,0,0.2)',
            width: 1
          }
        },
        line: showTrajectory.value ? {
          color: regime.color,
          width: 1,
          opacity: 0.3
        } : undefined,
        text: regularIndices.map(i => texts[i]),
        hovertemplate: '<b>%{text}</b><extra></extra>',
        showlegend: true
      })
    }

    // Outliers
    if (showOutliers.value) {
      const outlierIndices = regimeIndices.filter((_, idx) => regimeOutliers[idx])
      if (outlierIndices.length > 0) {
        traces.push({
          x: outlierIndices.map(i => x[i]),
          y: outlierIndices.map(i => y[i]),
          z: viewMode.value === '3d' ? outlierIndices.map(i => z[i]) : undefined,
          mode: 'markers',
          type: viewMode.value === '3d' ? 'scatter3d' : 'scatter',
          name: `${regime.name} (Outliers)`,
          marker: {
            color: '#ff00ff',
            size: 12,
            symbol: 'x',
            opacity: 0.9,
            line: {
              color: '#fff',
              width: 2
            }
          },
          text: outlierIndices.map(i => texts[i]),
          hovertemplate: '<b>%{text}</b><br><b>OUTLIER</b><extra></extra>',
          showlegend: true
        })
      }
    }
  })

  // Trajectory line (connected points)
  if (showTrajectory.value && data.length > 1) {
    traces.push({
      x: x,
      y: y,
      z: viewMode.value === '3d' ? z : undefined,
      mode: 'lines',
      type: viewMode.value === '3d' ? 'scatter3d' : 'scatter',
      name: 'Траектория',
      line: {
        color: 'rgba(255,255,255,0.2)',
        width: 2
      },
      showlegend: false,
      hoverinfo: 'skip'
    })
  }

  // Ellipsoids (confidence ellipsoids) - simplified as ellipses for each regime
  if (showEllipsoids.value) {
    regimes.forEach(regime => {
      if (!visibleRegimes.value.includes(regime.id)) return

      const regimeData = data.filter(d => d.regime === regime.id)
      if (regimeData.length < 3) return

      const regimeX = regimeData.map(d => (d.returns[asset1] || 0) * 100)
      const regimeY = regimeData.map(d => (d.returns[asset2] || 0) * 100)
      const regimeZ = regimeData.map(d => (d.returns[asset3] || 0) * 100)

      const meanX = regimeX.reduce((a, b) => a + b, 0) / regimeX.length
      const meanY = regimeY.reduce((a, b) => a + b, 0) / regimeY.length
      const meanZ = regimeZ.reduce((a, b) => a + b, 0) / regimeZ.length

      const stdX = Math.sqrt(regimeX.reduce((sum, val) => sum + (val - meanX) ** 2, 0) / regimeX.length)
      const stdY = Math.sqrt(regimeY.reduce((sum, val) => sum + (val - meanY) ** 2, 0) / regimeY.length)
      const stdZ = Math.sqrt(regimeZ.reduce((sum, val) => sum + (val - meanZ) ** 2, 0) / regimeZ.length)

      // Draw ellipsoid as wireframe (simplified - 2D ellipse for 2D view)
      if (viewMode.value === '2d') {
        const theta = Array.from({ length: 50 }, (_, i) => (i / 50) * 2 * Math.PI)
        const ellipseX = theta.map(t => meanX + 2 * stdX * Math.cos(t))
        const ellipseY = theta.map(t => meanY + 2 * stdY * Math.sin(t))
        
        traces.push({
          x: ellipseX,
          y: ellipseY,
          mode: 'lines',
          type: 'scatter',
          name: `${regime.name} Ellipse`,
          line: {
            color: regime.color,
            width: 1,
            dash: 'dash'
          },
          showlegend: false,
          hoverinfo: 'skip'
        })
      }
    })
  }

  // Regression lines
  if (showRegressions.value && viewMode.value === '2d') {
    // Simple linear regression for X vs Y
    const n = x.length
    const sumX = x.reduce((a, b) => a + b, 0)
    const sumY = y.reduce((a, b) => a + b, 0)
    const sumXY = x.reduce((sum, val, i) => sum + val * y[i], 0)
    const sumXX = x.reduce((sum, val) => sum + val * val, 0)

    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX)
    const intercept = (sumY - slope * sumX) / n

    const minX = Math.min(...x)
    const maxX = Math.max(...x)
    const regX = [minX, maxX]
    const regY = regX.map(x => slope * x + intercept)

    traces.push({
      x: regX,
      y: regY,
      mode: 'lines',
      type: 'scatter',
      name: 'Регрессия',
      line: {
        color: 'rgba(96, 165, 250, 0.5)',
        width: 2,
        dash: 'dot'
      },
      showlegend: false,
      hoverinfo: 'skip'
    })
  }

  // Centroids
  if (showCentroids.value) {
    regimes.forEach(regime => {
      if (!visibleRegimes.value.includes(regime.id)) return

      const regimeData = data.filter(d => d.regime === regime.id)
      if (regimeData.length === 0) return

      const meanX = regimeData.reduce((sum, d) => sum + (d.returns[asset1] || 0) * 100, 0) / regimeData.length
      const meanY = regimeData.reduce((sum, d) => sum + (d.returns[asset2] || 0) * 100, 0) / regimeData.length
      const meanZ = regimeData.reduce((sum, d) => sum + (d.returns[asset3] || 0) * 100, 0) / regimeData.length

      traces.push({
        x: [meanX],
        y: [meanY],
        z: viewMode.value === '3d' ? [meanZ] : undefined,
        mode: 'markers',
        type: viewMode.value === '3d' ? 'scatter3d' : 'scatter',
        name: `${regime.name} Центроид`,
        marker: {
          color: regime.color,
          size: 20,
          symbol: 'diamond',
          line: {
            color: '#fff',
            width: 2
          }
        },
        showlegend: false,
        hoverinfo: 'skip'
      })
    })
  }

  // Layout
  const layout: any = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: '#fff', family: 'system-ui' },
    margin: { l: 50, r: 20, t: 30, b: 50 },
    showlegend: true,
    legend: {
      bgcolor: 'rgba(0,0,0,0.3)',
      bordercolor: 'rgba(255,255,255,0.1)',
      borderwidth: 1,
      font: { color: '#fff', size: 10 },
      x: 0.98,
      y: 1,
      xanchor: 'right'
    },
    autosize: true,
    height: undefined // Let it fill container
  }

  if (viewMode.value === '3d') {
    layout.scene = {
      xaxis: {
        title: `${asset1} Доходность (%)`,
        backgroundcolor: 'rgba(0,0,0,0)',
        gridcolor: 'rgba(255,255,255,0.15)',
        showbackground: true,
        titlefont: { color: 'rgba(255,255,255,0.9)', size: 12 },
        tickfont: { size: 10, color: 'rgba(255,255,255,0.6)' }
      },
      yaxis: {
        title: `${asset2} Доходность (%)`,
        backgroundcolor: 'rgba(0,0,0,0)',
        gridcolor: 'rgba(255,255,255,0.15)',
        showbackground: true,
        titlefont: { color: 'rgba(255,255,255,0.9)', size: 12 },
        tickfont: { size: 10, color: 'rgba(255,255,255,0.6)' }
      },
      zaxis: {
        title: `${asset3} Доходность (%)`,
        backgroundcolor: 'rgba(0,0,0,0)',
        gridcolor: 'rgba(255,255,255,0.15)',
        showbackground: true,
        titlefont: { color: 'rgba(255,255,255,0.9)', size: 12 },
        tickfont: { size: 10, color: 'rgba(255,255,255,0.6)' }
      },
      bgcolor: 'rgba(0,0,0,0)',
      camera: {
        eye: { x: 1.5, y: 1.5, z: 1.5 },
        center: { x: 0, y: 0, z: 0 },
        up: { x: 0, y: 0, z: 1 }
      },
      aspectratio: { x: 1, y: 1, z: 1 }
    }
  } else {
    layout.xaxis = {
      title: `${asset1} Доходность (%)`,
      gridcolor: 'rgba(255,255,255,0.1)',
      titlefont: { color: 'rgba(255,255,255,0.9)', size: 12 },
      tickfont: { size: 10, color: 'rgba(255,255,255,0.6)' }
    }
    layout.yaxis = {
      title: `${asset2} Доходность (%)`,
      gridcolor: 'rgba(255,255,255,0.1)',
      titlefont: { color: 'rgba(255,255,255,0.9)', size: 12 },
      tickfont: { size: 10, color: 'rgba(255,255,255,0.6)' }
    }
  }

  const config = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    toImageButtonOptions: {
      format: 'png',
      filename: 'correlation_scatter',
      height: 800,
      width: 1200,
      scale: 2
    },
    fillFrame: true,
    frameMargins: 0
  }

  await Plotly.value.newPlot(plotContainer.value, traces, layout, config)
  
  // Force resize to use full container
  if (Plotly.value.Plots && plotContainer.value) {
    Plotly.value.Plots.resize(plotContainer.value)
  }
}

// Time range update
const updateTimeRange = () => {
  const data = allData.value
  if (data.length === 0) return

  const startIdx = timeRange.value
  dateRange.value = [
    data[startIdx]?.date || '',
    data[data.length - 1]?.date || ''
  ]
  updatePlot()
}

// Playback functions
const togglePlayback = () => {
  isPlaying.value = !isPlaying.value
  
  if (isPlaying.value) {
    const step = () => {
      if (!isPlaying.value) return
      
      playbackProgress.value += playbackSpeed.value
      if (playbackProgress.value >= 100) {
        playbackProgress.value = 100
        isPlaying.value = false
        return
      }
      
      timeRange.value = Math.floor((playbackProgress.value / 100) * (allData.value.length - 1))
      updateTimeRange()
      
      if (isPlaying.value) {
        playbackInterval = window.setTimeout(step, 100)
      }
    }
    step()
  } else {
    if (playbackInterval) {
      clearTimeout(playbackInterval)
      playbackInterval = null
    }
  }
}

const updatePlaybackPosition = () => {
  timeRange.value = Math.floor((playbackProgress.value / 100) * (allData.value.length - 1))
  updateTimeRange()
}

// Reset view
const resetView = () => {
  if (!Plotly.value || !plotContainer.value) return
  timeRange.value = 0
  playbackProgress.value = 0
  isPlaying.value = false
  if (playbackInterval) {
    clearTimeout(playbackInterval)
    playbackInterval = null
  }
  updateTimeRange()
  Plotly.value.relayout(plotContainer.value, {
    'scene.camera.eye': { x: 1.5, y: 1.5, z: 1.5 },
    'scene.camera.center': { x: 0, y: 0, z: 0 }
  })
}

// Export PNG
const exportPNG = async () => {
  if (!Plotly.value || !plotContainer.value) return
  await Plotly.value.downloadImage(plotContainer.value, {
    format: 'png',
    filename: 'correlation_scatter_3d',
    height: 800,
    width: 1200,
    scale: 2
  })
}

// Initialize
onMounted(async () => {
  isLoading.value = true
  await loadPlotly()
  
  // Generate mock data
  allData.value = generateMockData()
  
  // Initialize time range
  if (allData.value.length > 0) {
    timeRange.value = 0
    dateRange.value = [
      allData.value[0].date,
      allData.value[allData.value.length - 1].date
    ]
  }
  
  // Initial plot
  await updatePlot()
  isLoading.value = false

  // Handle window resize with debounce
  let resizeTimeout: number | null = null
  const handleResize = () => {
    if (resizeTimeout) clearTimeout(resizeTimeout)
    resizeTimeout = window.setTimeout(() => {
      if (Plotly.value && plotContainer.value) {
        Plotly.value.Plots.resize(plotContainer.value)
      }
    }, 250)
  }
  window.addEventListener('resize', handleResize)
  
  // Also resize after initial render to ensure proper sizing
  setTimeout(() => {
    if (Plotly.value && plotContainer.value) {
      Plotly.value.Plots.resize(plotContainer.value)
    }
  }, 500)

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
    if (resizeTimeout) clearTimeout(resizeTimeout)
    if (playbackInterval) clearTimeout(playbackInterval)
  })
})

// Watch for asset changes
watch(() => selectedAssets.value, () => {
  updatePlot()
}, { deep: true })

// Extend window type
declare global {
  interface Window {
    Plotly?: any
  }
}
</script>

<style scoped>
.correlation-scatter-3d {
  display: flex;
  flex-direction: column;
  gap: 0;
  width: 100%;
  max-width: 100%;
  min-height: 100%;
  height: auto;
  box-sizing: border-box;
  overflow: visible;
}

.main-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 12px;
  min-height: 700px;
  height: auto;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: visible;
  align-items: start;
}

.controls-column {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow: visible;
  min-height: 100%;
}

.plot-column {
  display: flex;
  flex-direction: column;
  position: relative;
  min-height: 0;
  flex: 1;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.control-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.controls-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

/* Two Column Layout */
.controls-two-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.controls-col-1,
.controls-col-2 {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  width: 100%;
}

.control-group.full-width {
  grid-column: 1 / -1;
}

.control-group label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  text-transform: uppercase;
}

.control-group select,
.control-group input[type="range"] {
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #fff;
  font-size: 11px;
  outline: none;
}

.control-group select {
  cursor: pointer;
}

.control-group select:focus {
  border-color: rgba(255, 255, 255, 0.3);
}

.toggle-buttons {
  display: flex;
  gap: 4px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  padding: 2px;
}

.toggle-btn {
  padding: 6px 12px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.toggle-btn:hover {
  color: #fff;
}

.time-slider {
  width: 100%;
  height: 4px;
  -webkit-appearance: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  outline: none;
}

.time-slider.full-width-slider {
  width: 100%;
}

.time-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 12px;
  height: 12px;
  background: #fff;
  border-radius: 50%;
  cursor: pointer;
}

.time-slider::-moz-range-thumb {
  width: 12px;
  height: 12px;
  background: #fff;
  border-radius: 50%;
  cursor: pointer;
  border: none;
}

.btn-reset {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s;
  width: 100%;
}

.btn-reset.full-width {
  width: 100%;
}

.btn-reset:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.regime-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: nowrap;
  margin-bottom: 16px;
}

.regime-filter-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  text-transform: uppercase;
  margin-right: 4px;
  flex-shrink: 0;
}

.regime-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
}

.regime-checkbox input[type="checkbox"] {
  cursor: pointer;
}

.regime-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

/* Dropdown Controls */
.dropdown-controls {
  width: 100%;
}

.dropdown-toggle {
  width: 100%;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  transition: all 0.2s;
}

.dropdown-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.dropdown-toggle svg {
  transition: transform 0.2s;
  flex-shrink: 0;
}

.dropdown-content {
  margin-top: 8px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.checkbox-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.checkbox-item input[type="checkbox"] {
  cursor: pointer;
}

.playback-controls {
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.btn-playback {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-playback:hover,
.btn-playback.active {
  background: rgba(255, 255, 255, 0.2);
}

.playback-slider {
  flex: 1;
  max-width: 300px;
  height: 4px;
}

.speed-slider {
  width: 60px;
  height: 4px;
}

.speed-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  min-width: 30px;
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
  border-radius: 12px;
}

.spinner-large {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.plot-container {
  position: relative;
  width: 100%;
  max-width: 100%;
  height: 100%;
  min-height: 680px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  flex: 1;
  box-sizing: border-box;
}

.stats-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
  min-height: auto;
  overflow: visible;
}

.stats-section {
  margin-bottom: 12px;
}

.stats-section:last-child {
  margin-bottom: 0;
}

.stats-section h4 {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  text-transform: uppercase;
  margin: 0 0 8px 0;
}

.correlation-stats {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stats-grid-compact {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-item {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-item-compact {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.5);
}

.stat-label-small {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
}

.stat-label-large {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
}

.stat-value {
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  font-family: monospace;
}

.stat-value-large {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  font-family: monospace;
}

.stat-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 9px;
  color: rgba(255, 255, 255, 0.6);
  font-family: monospace;
}

.stat-details-compact {
  display: flex;
  flex-direction: column;
  gap: 1px;
  font-size: 8px;
  color: rgba(255, 255, 255, 0.5);
  font-family: monospace;
}

.stat-details-large {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  font-family: monospace;
  font-weight: 500;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.8);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

@media (max-width: 1024px) {
  .main-layout {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .controls-column {
    max-height: none;
  }

  .stats-panel {
    max-height: none;
  }

  .plot-container {
    min-height: 500px;
  }
}

@media (max-width: 768px) {
  .controls-row {
    flex-direction: column;
    align-items: stretch;
  }

  .control-group {
    width: 100%;
  }

  .plot-container {
    min-height: 400px;
  }
}
</style>
