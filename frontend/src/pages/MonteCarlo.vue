<!-- src/pages/MonteCarlo.vue - Brutalist Design -->
<template>
  <div class="page-container">

    <!-- Header -->
    <PageHeader
      title="Симуляция Монте-Карло"
      subtitle="Генерация стохастических сценариев (GBM Model)"
    >
      <template #actions>
        <div class="action-pill action-pill--status">
          <span class="dot" :class="isRunning ? '' : 'dot--green'"></span>
          <span class="font-mono">{{ isRunning ? 'Вычисление...' : 'Готов к запуску' }}</span>
        </div>
      </template>
    </PageHeader>

    <div class="dashboard-layout dashboard-layout--sidebar-left">

      <!-- LEFT COLUMN: CONTROLS -->
      <aside class="controls-column">
        <!-- Settings Panel -->
        <BrutalistCard title="Параметры модели">
          <div class="form-section">
            <!-- Initial Price -->
            <div class="form-group">
              <label class="form-label">Начальная цена (S₀)</label>
              <div class="input-wrapper">
                <input v-model.number="params.startPrice" type="number" class="form-control" />
                <span class="input-suffix font-mono">$</span>
              </div>
            </div>

            <!-- Volatility -->
            <div class="form-group">
              <label class="form-label">Волатильность (σ)</label>
              <div class="input-wrapper">
                <input v-model.number="params.volatility" type="number" step="0.1" class="form-control" />
                <span class="input-suffix font-mono">%</span>
              </div>
            </div>

            <!-- Drift -->
            <div class="form-group">
              <label class="form-label">Доходность (μ)</label>
              <div class="input-wrapper">
                <input v-model.number="params.drift" type="number" step="0.1" class="form-control" />
                <span class="input-suffix font-mono">%</span>
              </div>
            </div>

            <div class="divider"></div>

            <!-- Time & Paths -->
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Дней (T)</label>
                <input v-model.number="params.days" type="number" class="form-control" />
              </div>
              <div class="form-group">
                <label class="form-label">Путей (N)</label>
                <input v-model.number="params.paths" type="number" step="1000" class="form-control" />
              </div>
            </div>

            <button @click="runSimulationFull" :disabled="isRunning" class="btn btn-primary btn-full">
              <span v-if="!isRunning">Запустить симуляцию</span>
              <span v-else>Расчет...</span>
            </button>
          </div>
        </BrutalistCard>

        <!-- Statistics Panel -->
        <transition name="fade">
          <BrutalistCard v-if="results" :title="`Результаты (T=${params.days})`">
            <div class="metrics-row">
              <div class="metric-item">
                <span class="metric-label">Мин. цена</span>
                <span class="metric-value metric-value--negative font-mono">{{ formatCurrency(results.min) }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Макс. цена</span>
                <span class="metric-value metric-value--positive font-mono">{{ formatCurrency(results.max) }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Медиана</span>
                <span class="metric-value font-mono">{{ formatCurrency(results.median) }}</span>
              </div>
            </div>
          </BrutalistCard>
        </transition>
      </aside>

      <!-- RIGHT COLUMN: VISUALIZATION -->
      <main class="viz-column">

        <!-- Key Metrics Cards -->
        <div class="kpi-grid">
          <StatCard
            label="Среднее (Mean)"
            :value="results ? formatCurrency(results.mean) : '—'"
            :variant="results?.meanChange > 0 ? 'positive' : 'negative'"
          />
          <StatCard
            label="VaR (95%)"
            :value="results ? formatCurrency(results.var95) : '—'"
            variant="negative"
          />
          <StatCard
            label="Вероятность роста"
            :value="results ? results.winProb + '%' : '—'"
            variant="positive"
          />
          <StatCard
            label="День симуляции"
            :value="`${playbackStep} / ${params.days}`"
          />
        </div>

        <!-- Main Chart Area -->
        <BrutalistCard variant="dark">
          <template #header>
            <div class="chart-header-content">
              <div class="chart-title-group">
                <h3 class="panel-title font-oswald">Траектории</h3>
                <span v-if="isPlaying" class="live-badge font-mono">● LIVE</span>
              </div>

              <!-- Playback Controls -->
              <div class="playback-controls" v-if="chartData.paths.length">
                <button class="control-btn" @click="togglePlay" title="Play/Pause">
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

                <button class="control-btn" @click="resetPlayback" title="Reset">↺</button>
              </div>
            </div>
          </template>

          <div class="chart-container">
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
                stroke="rgba(220, 38, 38, 0.15)"
                stroke-width="1"
              />

              <!-- Confidence Area -->
              <path
                :d="generateAreaD(chartData.q05, chartData.q95, playbackStep)"
                fill="rgba(220, 38, 38, 0.08)"
                stroke="none"
              />

              <!-- Median Path -->
              <path
                :d="generatePathD(chartData.medianPath, playbackStep)"
                fill="none"
                stroke="#DC2626"
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
                stroke="#22c55e"
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
              <span v-else class="font-mono">Нажмите «Запустить» для генерации</span>
            </div>
          </div>
        </BrutalistCard>

      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { useTaskStore } from '@/stores/tasks'
import PageHeader from '@/components/common/PageHeader.vue'
import BrutalistCard from '@/components/common/BrutalistCard.vue'
import StatCard from '@/components/common/StatCard.vue'

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
  let u = 0, v = 0
  while(u === 0) u = Math.random()
  while(v === 0) v = Math.random()
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
  new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(val)

onUnmounted(() => {
  if (animationFrame) cancelAnimationFrame(animationFrame)
})
</script>

<style scoped>
/* ============================================
   LAYOUT
   ============================================ */
.controls-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.viz-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ============================================
   FORM STYLES
   ============================================ */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: var(--bg-primary);
  border: 1px solid var(--border-dark);
  transition: border-color 0.2s;
}

.input-wrapper:focus-within {
  border-color: var(--accent-red);
}

.input-wrapper .form-control {
  border: none;
  background: transparent;
  text-align: right;
  padding-right: 8px;
}

.input-suffix {
  padding: 0 12px;
  color: var(--text-muted);
  font-size: 12px;
  border-left: 1px solid var(--border-dark);
  height: 40px;
  display: flex;
  align-items: center;
}

.btn-full {
  width: 100%;
  margin-top: 16px;
}

/* ============================================
   CHART STYLES
   ============================================ */
.chart-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.chart-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.live-badge {
  font-size: 10px;
  color: var(--accent-red);
  animation: blink 1.5s infinite;
}

@keyframes blink {
  50% { opacity: 0.5; }
}

.playback-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-dark);
}

.control-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-dark);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.control-btn:hover {
  background: var(--accent-red);
  border-color: var(--accent-red);
  color: #000;
}

.timeline-wrapper {
  position: relative;
  width: 120px;
  height: 4px;
  background: var(--border-dark);
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
  background: var(--accent-red);
  pointer-events: none;
}

.chart-container {
  position: relative;
  background: var(--bg-primary);
  border: 1px solid var(--border-dark);
  min-height: 400px;
}

.main-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: var(--text-muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-dark);
  border-top-color: var(--accent-red);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ============================================
   TRANSITIONS
   ============================================ */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .chart-container {
    min-height: 350px;
  }
}

@media (max-width: 768px) {
  .chart-header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .chart-container {
    min-height: 300px;
  }

  .playback-controls {
    width: 100%;
    justify-content: space-between;
  }

  .timeline-wrapper {
    flex: 1;
  }
}
</style>
