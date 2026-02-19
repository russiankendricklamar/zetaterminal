<template>
  <div>
    <!-- Hero Section HJB -->
    <div class="hero-section">
      <div class="hero-left">
        <h1>Стохастическое оптимизирование (HJB)</h1>
        <div class="hero-meta">
          <span class="glass-pill">Стратегия: <strong>Hamilton-Jacobi-Bellman</strong></span>
          <span class="glass-pill">Горизонт: <strong>{{ hjbParams.horizon }} мес.</strong></span>
          <span class="glass-pill">Банк: <strong>{{ selectedBank.name }}</strong></span>
          <span class="glass-pill">Активов: <strong>{{ portfolioPositions.length }}</strong></span>
        </div>
      </div>
      <div class="hero-actions">
        <button class="btn-glass primary" @click="handleRunOptimization" :disabled="isComputing">
          <svg v-if="!isComputing" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <span v-else class="spinner"></span>
          {{ isComputing ? 'Расчёт...' : 'Запустить оптимизацию' }}
        </button>
      </div>
    </div>

    <!-- HJB Parameters Row (Top) -->
    <div class="glass-panel hjb-params-row">
      <div class="panel-header">
        <h3>Параметры HJB модели</h3>
      </div>
      <div class="panel-body params-row-body">
        <div class="param-group-horizontal">
          <label>Коэффициент неприятия риска (γ)</label>
          <div class="param-input-group">
            <input type="number" v-model.number="hjbParams.gamma" min="0.1" max="20" step="0.1" />
          </div>
        </div>
        <div class="param-group-horizontal">
          <label>Инвестиционный горизонт (T), лет</label>
          <div class="param-input-group">
            <input type="number" v-model.number="hjbParams.horizon" min="0.1" max="50" step="0.1" />
          </div>
        </div>
        <div class="param-group-horizontal">
          <label>Безрисковая ставка (r)</label>
          <div class="param-input-group">
            <input type="number" v-model.number="hjbParams.riskFreeRate" min="0" max="0.2" step="0.001" />
          </div>
        </div>
        <div class="param-group-horizontal">
          <label>Волатильность рынка (σ)</label>
          <div class="param-input-group">
            <input type="number" v-model.number="hjbParams.marketVol" min="0.05" max="0.8" step="0.01" />
          </div>
        </div>
        <div class="param-group-horizontal">
          <label>Ожидаемая доходность (μ)</label>
          <div class="param-input-group">
            <input type="number" v-model.number="hjbParams.expectedReturn" min="0" max="0.5" step="0.01" />
          </div>
        </div>
        <div class="param-group-horizontal">
          <label>Количество траекторий Монте-Карло</label>
          <div class="param-input-group">
            <input type="number" v-model.number="hjbParams.monteCarloTrajectories" min="100" max="100000" step="100" />
          </div>
        </div>
      </div>
    </div>

    <!-- HJB Main Grid -->
    <div class="dashboard-grid hjb-grid">
      <!-- LEFT: Portfolio Composition (spans 2 columns) -->
      <div class="col-portfolio-wide">
        <div class="glass-panel portfolio-composition-panel">
          <div class="panel-header">
            <h3>Состав портфеля</h3>
          </div>
          <div class="panel-body weights-body">
            <div class="weights-comparison">
              <div class="weights-table-container">
                <table class="weights-table">
                  <thead>
                    <tr>
                      <th>Инструмент</th>
                      <th class="text-right">Цена</th>
                      <th class="text-right">День %</th>
                      <th class="text-right">Позиция</th>
                      <th class="text-right">Вес</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="pos in portfolioPositions" :key="pos.symbol">
                      <td>
                        <div class="asset-cell">
                          <div class="asset-icon" :style="{ background: pos.color }">{{ pos.symbol[0] }}</div>
                          <div class="asset-info">
                            <span class="symbol">{{ pos.symbol }}</span>
                            <span class="name">{{ pos.name }}</span>
                          </div>
                        </div>
                      </td>
                      <td class="text-right mono">₽{{ pos.price }}</td>
                      <td class="text-right mono">
                        <span :class="['change-pill', pos.dayChange > 0 ? 'text-green' : 'text-red']">
                          {{ pos.dayChange > 0 ? '+' : '' }}{{ pos.dayChange }}%
                        </span>
                      </td>
                      <td class="text-right mono opacity-80">₽{{ (pos.notional / 1000).toFixed(1) }}k</td>
                      <td class="text-right mono font-bold">{{ pos.allocation }}%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT: 3D Heatmap -->
      <div class="col-3d-right">
        <div class="glass-panel correlation-3d-panel">
          <div class="panel-header">
            <h3>3D Тепловая карта активов</h3>
          </div>
          <div class="panel-body correlation-3d-body">
            <div id="correlation-3d-heatmap" class="static-3d-plot" style="width:100%; height:500px; position: relative; min-height: 500px; background: transparent; border-radius: 8px;"></div>
            <div v-if="hoveredAsset" class="asset-tooltip-3d">
              <div class="tooltip-header">
                <div class="asset-icon" :style="{ background: hoveredAsset.color }">{{ hoveredAsset.symbol[0] }}</div>
                <div>
                  <div class="tooltip-symbol">{{ hoveredAsset.symbol }}</div>
                  <div class="tooltip-name">{{ hoveredAsset.name }}</div>
                </div>
              </div>
              <div class="tooltip-details">
                <div class="tooltip-row">
                  <span>Тип:</span>
                  <strong>{{ (hoveredAsset.symbol.includes('SU') || hoveredAsset.symbol.includes('RU000')) ? 'Облигация' : 'Акция' }}</strong>
                </div>
                <div class="tooltip-row" v-if="hoveredAsset.volatility !== undefined">
                  <span>Волатильность:</span>
                  <strong>{{ hoveredAsset.volatility?.toFixed(1) || 'N/A' }}%</strong>
                </div>
                <div class="tooltip-row" v-if="hoveredAsset.avgCorrelation !== undefined">
                  <span>Ср. корреляция:</span>
                  <strong>{{ hoveredAsset.avgCorrelation?.toFixed(2) || 'N/A' }}</strong>
                </div>
                <div class="tooltip-row">
                  <span>Вес в портфеле:</span>
                  <strong>{{ hoveredAsset.allocation?.toFixed(2) || hoveredAsset.allocation }}%</strong>
                </div>
                <div class="tooltip-row">
                  <span>Цена:</span>
                  <strong>{{ hoveredAsset.price?.toLocaleString('ru-RU') || hoveredAsset.price }} ₽</strong>
                </div>
                <div class="tooltip-row">
                  <span>Дневное изм.:</span>
                  <strong :class="hoveredAsset.dayChange >= 0 ? 'text-green' : 'text-red'">
                    {{ hoveredAsset.dayChange >= 0 ? '+' : '' }}{{ hoveredAsset.dayChange?.toFixed(2) || hoveredAsset.dayChange }}%
                  </strong>
                </div>
                <div class="tooltip-row" v-if="hoveredAsset.notional">
                  <span>Позиция:</span>
                  <strong>₽{{ (hoveredAsset.notional / 1000).toFixed(1) }}k</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- GARCH Volatility Modeling - Full Width -->
    <div class="garch-full-width">
      <div class="glass-panel">
        <div class="panel-header">
          <h3>Моделирование волатильности (GARCH)</h3>
        </div>
        <div class="panel-body">
          <div class="garch-container-full">
            <div class="garch-chart-placeholder-full">
              <canvas ref="garchChartRef" id="garch-chart"></canvas>
            </div>
            <div class="garch-params-full">
              <div class="garch-param-row">
                <span class="param-name">GARCH(1,1):</span>
                <span class="param-value">σ²<sub>t</sub> = ω + αε²<sub>t-1</sub> + βσ²<sub>t-1</sub></span>
              </div>
              <div class="garch-stats">
                <div class="garch-stat">
                  <span class="stat-label">α (ARCH)</span>
                  <span class="stat-val">{{ garchData?.result?.parameters?.alpha?.toFixed(3) || '0.082' }}</span>
                </div>
                <div class="garch-stat">
                  <span class="stat-label">β (GARCH)</span>
                  <span class="stat-val">{{ garchData?.result?.parameters?.beta?.toFixed(3) || '0.893' }}</span>
                </div>
                <div class="garch-stat">
                  <span class="stat-label">ω</span>
                  <span class="stat-val">{{ garchData?.result?.parameters?.omega?.toFixed(6) || '0.000025' }}</span>
                </div>
                <div class="garch-stat">
                  <span class="stat-label">Long-term Vol</span>
                  <span class="stat-val">{{ garchData?.result?.long_term_volatility ? (garchData.result.long_term_volatility * 100).toFixed(1) + '%' : '18.2%' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reports Row -->
    <div class="dashboard-grid hjb-reports-grid">
      <!-- LEFT: GARCH Filtering Report -->
      <div class="col-report-left">
        <div class="glass-panel report-panel">
          <div class="panel-header">
            <h3>Фильтрация активов по GARCH</h3>
          </div>
          <div class="panel-body">
            <div class="filtering-report">
              <div class="report-summary">
                <div class="summary-item">
                  <span class="summary-label">Всего активов</span>
                  <span class="summary-value">{{ portfolioPositions.length }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">Прошли фильтр</span>
                  <span class="summary-value text-green">{{ garchFilteredCount }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">Отклонены</span>
                  <span class="summary-value text-red">{{ portfolioPositions.length - garchFilteredCount }}</span>
                </div>
              </div>
              <div class="filtering-criteria">
                <div class="criteria-title">Критерии фильтрации:</div>
                <div class="criteria-list">
                  <div class="criteria-item">
                    <span class="criteria-check">✓</span>
                    <span>GARCH волатильность ≤ 30%</span>
                  </div>
                  <div class="criteria-item">
                    <span class="criteria-check">✓</span>
                    <span>Стабильность параметров (α + β &lt; 1)</span>
                  </div>
                  <div class="criteria-item">
                    <span class="criteria-check">✓</span>
                    <span>Достаточная ликвидность</span>
                  </div>
                </div>
              </div>
              <div class="filtered-assets">
                <div class="filtered-title">Прошедшие фильтр (топ-10):</div>
                <div class="filtered-list">
                  <div v-for="(asset, idx) in garchFilteredAssets.slice(0, 10)" :key="idx" class="filtered-asset">
                    <span class="asset-symbol">{{ asset.symbol }}</span>
                    <span class="asset-garch">{{ asset.garchVol }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT: Historical & Dividend Yield Report -->
      <div class="col-report-right">
        <div class="glass-panel report-panel">
          <div class="panel-header">
            <h3>Историческая и дивидендная доходность</h3>
          </div>
          <div class="panel-body weights-body">
            <div class="weights-comparison">
              <div class="weights-table-container">
                <table class="weights-table">
                  <thead>
                    <tr>
                      <th>Актив</th>
                      <th class="text-right">Историческая</th>
                      <th class="text-right">Дивидендная</th>
                      <th class="text-right">Итого</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(asset, idx) in yieldReportData.slice(0, 10)" :key="idx">
                      <td>
                        <div class="asset-cell">
                          <div class="asset-icon" :style="{ background: asset.color }">{{ asset.symbol[0] }}</div>
                          <div class="asset-info">
                            <span class="symbol">{{ asset.symbol }}</span>
                            <span class="name">{{ asset.name }}</span>
                          </div>
                        </div>
                      </td>
                      <td class="text-right mono">{{ (asset.historicalYield * 100).toFixed(2) }}%</td>
                      <td class="text-right mono">{{ (asset.dividendYield * 100).toFixed(2) }}%</td>
                      <td class="text-right mono font-bold text-green">{{ (asset.totalYield * 100).toFixed(2) }}%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="yield-summary">
              <div class="yield-summary-item">
                <span class="summary-label">Средняя историческая доходность</span>
                <span class="summary-value">{{ (avgHistoricalYield * 100).toFixed(2) }}%</span>
              </div>
              <div class="yield-summary-item">
                <span class="summary-label">Средняя дивидендная доходность</span>
                <span class="summary-value">{{ (avgDividendYield * 100).toFixed(2) }}%</span>
              </div>
              <div class="yield-summary-item">
                <span class="summary-label">Средняя общая доходность</span>
                <span class="summary-value text-green font-bold">{{ (avgTotalYield * 100).toFixed(2) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Monte Carlo Trajectories Visualization -->
    <div class="glass-panel trajectories-panel">
      <div class="panel-header">
        <div class="trajectories-header-left">
          <h3>Траектории симуляции методом Монте-Карло</h3>
          <span v-if="isPlayingTrajectories" class="live-badge">● LIVE</span>
        </div>
        <div class="playback-controls" v-if="trajectoriesData.paths.length">
          <button class="icon-btn" @click="togglePlayTrajectories" title="Play/Pause">
            <span v-if="isPlayingTrajectories">⏸</span>
            <span v-else>▶</span>
          </button>
          <div class="timeline-wrapper">
            <input type="range" min="0" :max="trajectoriesDays" v-model.number="playbackStepTrajectories" @input="stopPlayTrajectories" class="timeline-slider" />
            <div class="timeline-track" :style="{ width: (playbackStepTrajectories / trajectoriesDays * 100) + '%' }"></div>
          </div>
          <div class="playback-day-info">
            День: <span class="mono">{{ playbackStepTrajectories }}</span> / <span class="mono">{{ trajectoriesDays }}</span>
          </div>
          <button class="icon-btn" @click="resetPlaybackTrajectories" title="Reset">↺</button>
        </div>
      </div>
      <div class="panel-body">
        <div class="trajectories-chart-container" ref="trajectoriesChartContainer">
          <svg v-if="trajectoriesData.paths.length > 0" viewBox="0 0 1000 400" preserveAspectRatio="none" class="trajectories-svg">
            <line x1="0" y1="350" x2="1000" y2="350" stroke="rgba(255,255,255,0.05)" />
            <line x1="0" y1="200" x2="1000" y2="200" stroke="rgba(255,255,255,0.05)" />
            <line x1="0" y1="50" x2="1000" y2="50" stroke="rgba(255,255,255,0.05)" />
            <line x1="0" :y1="scaleY(initialPrice)" x2="1000" :y2="scaleY(initialPrice)" stroke="rgba(255,255,255,0.2)" stroke-dasharray="4" />
            <path v-for="(path, i) in trajectoriesData.displayPaths" :key="`trajectory-path-${i}`" :d="generatePathD(path, playbackStepTrajectories)" fill="none" stroke="rgba(59, 130, 246, 0.2)" stroke-width="1" />
            <path :d="generateAreaD(trajectoriesData.q05, trajectoriesData.q95, playbackStepTrajectories)" fill="rgba(59, 130, 246, 0.1)" stroke="none" />
            <path :d="generatePathD(trajectoriesData.medianPath, playbackStepTrajectories)" fill="none" stroke="#3b82f6" stroke-width="2.5" />
            <path :d="generatePathD(trajectoriesData.q05, playbackStepTrajectories)" fill="none" stroke="#f87171" stroke-width="1.5" stroke-dasharray="4" />
            <path :d="generatePathD(trajectoriesData.q95, playbackStepTrajectories)" fill="none" stroke="#34d399" stroke-width="1.5" stroke-dasharray="4" />
            <line v-if="playbackStepTrajectories > 0" :x1="scaleX(playbackStepTrajectories)" y1="0" :x2="scaleX(playbackStepTrajectories)" y2="400" stroke="rgba(255,255,255,0.4)" stroke-dasharray="2" />
          </svg>
          <div v-else class="trajectories-empty-state">
            <span>Генерация траекторий на основе параметров HJB модели</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 3D Trajectories Visualization -->
    <div class="glass-panel trajectories-3d-panel">
      <div class="panel-header">
        <div class="trajectories-3d-header-left">
          <h3>3D визуализация траекторий</h3>
          <span v-if="isPlaying3D" class="live-badge">● LIVE</span>
        </div>
        <div class="playback-controls" v-if="simulationResult3D && simulationResult3D.paths.length">
          <button class="icon-btn" @click="togglePlay3D" title="Play/Pause">
            <span v-if="isPlaying3D">⏸</span>
            <span v-else>▶</span>
          </button>
          <div class="timeline-wrapper">
            <input type="range" min="0" :max="maxStep3D" v-model.number="playbackStep3D" @input="stopPlay3D" class="timeline-slider" />
            <div class="timeline-track" :style="{ width: (maxStep3D > 0 ? (playbackStep3D / maxStep3D * 100) : 0) + '%' }"></div>
          </div>
          <div class="playback-day-info">
            Шаг: <span class="mono">{{ playbackStep3D }}</span> / <span class="mono">{{ maxStep3D }}</span>
          </div>
          <button class="icon-btn" @click="resetPlayback3D" title="Reset">↺</button>
        </div>
      </div>
      <div class="panel-body">
        <div class="trajectories-3d-container">
          <canvas ref="trajectories3DCanvas" class="trajectories-3d-canvas"></canvas>
        </div>
      </div>
    </div>

    <!-- Simulation Metrics Summary -->
    <div class="glass-panel metrics-summary-panel" v-if="simulationResult3D && simulationResult3D.paths.length">
      <div class="panel-header">
        <h3>Итоги симуляций</h3>
      </div>
      <div class="panel-body">
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-label">Средняя доходность портфеля</div>
            <div class="metric-value" :class="averageReturn >= 0 ? 'text-green' : 'text-red'">
              {{ formatPercent(averageReturn) }}
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Медианная доходность портфеля</div>
            <div class="metric-value" :class="medianReturn >= 0 ? 'text-green' : 'text-red'">
              {{ formatPercent(medianReturn) }}
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Sharpe Ratio</div>
            <div class="metric-value" :class="sharpeRatio >= 0 ? 'text-green' : 'text-red'">
              {{ sharpeRatio.toFixed(2) }}
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-label">VaR (95%)</div>
            <div class="metric-value text-red">
              {{ formatPercent(var95) }}
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-label">CVaR (95%)</div>
            <div class="metric-value text-red">
              {{ formatPercent(cvar95) }}
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Средний MDD</div>
            <div class="metric-value text-red">
              {{ formatPercent(averageMDD) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch, nextTick, computed } from 'vue'
import { usePortfolioStore } from '../../stores/portfolio'
import { useHJBOptimization } from '../../composables/optimization/useHJBOptimization'
import { useMonteCarlo2D } from '../../composables/optimization/useMonteCarlo2D'
import { useMonteCarlo3D } from '../../composables/optimization/useMonteCarlo3D'
import { useCorrelationHeatmap } from '../../composables/optimization/useCorrelationHeatmap'
import { useGARCHChart } from '../../composables/optimization/useGARCHChart'

const emit = defineEmits<{
  toast: [payload: { message: string; type: 'success' | 'error' | 'info' }]
}>()

const portfolioStore = usePortfolioStore()
const selectedBank = computed(() => portfolioStore.selectedBank)
const correlationMatrix = computed(() => portfolioStore.correlationMatrix)

// HJB optimization composable
const {
  hjbParams,
  hjbOptimizationResult,
  isComputing,
  trajectoriesDays,
  runHJBOptimization,
  garchFilteredAssets,
  garchFilteredCount,
  yieldReportData,
  avgHistoricalYield,
  avgDividendYield,
  avgTotalYield,
  portfolioPositions
} = useHJBOptimization()

// Monte Carlo 2D
const {
  playbackStepTrajectories,
  isPlayingTrajectories,
  trajectoriesChartContainer,
  initialPrice,
  trajectoriesData,
  scaleX,
  scaleY,
  generatePathD,
  generateAreaD,
  updateDisplayPaths,
  generateTrajectories,
  togglePlayTrajectories,
  stopPlayTrajectories,
  resetPlaybackTrajectories,
  updateFromBackend
} = useMonteCarlo2D(hjbParams, trajectoriesDays)

// Monte Carlo 3D
const {
  trajectories3DCanvas,
  simulationResult3D,
  playbackStep3D,
  isPlaying3D,
  maxStep3D,
  averageReturn,
  medianReturn,
  sharpeRatio,
  var95,
  cvar95,
  averageMDD,
  init3DTrajectories,
  togglePlay3D,
  stopPlay3D,
  resetPlayback3D,
  update3DVisualizationFromBackend
} = useMonteCarlo3D(hjbParams, trajectoriesDays, initialPrice)

// Correlation heatmap
const { hoveredAsset, initCorrelation3DHeatmap } = useCorrelationHeatmap(portfolioPositions, correlationMatrix)

// GARCH chart
const { garchData, initGARCHChart } = useGARCHChart(portfolioPositions)

const formatPercent = (val: number): string => {
  return (val * 100).toFixed(2) + '%'
}

const showToast = (msg: string, type: 'success' | 'error' | 'info') => {
  emit('toast', { message: msg, type })
}

const handleRunOptimization = async () => {
  await runHJBOptimization(showToast, (mc) => {
    // Update 2D trajectories from backend
    updateFromBackend(mc)
    // Update 3D visualization from backend
    update3DVisualizationFromBackend(mc)
  })
}

// Watch monteCarloTrajectories to update display paths
watch(() => hjbParams.value.monteCarloTrajectories, () => {
  if (hjbOptimizationResult.value?.monte_carlo) {
    if (trajectoriesData.paths.length > 0) {
      updateDisplayPaths()
    }
    update3DVisualizationFromBackend(hjbOptimizationResult.value.monte_carlo)
  } else {
    generateTrajectories()
  }
})

// Watch hjbParams to regenerate trajectories locally when no backend data
watch(() => [
  hjbParams.value.horizon,
  hjbParams.value.expectedReturn,
  hjbParams.value.marketVol,
  hjbParams.value.riskFreeRate
], () => {
  if (!hjbOptimizationResult.value?.monte_carlo) {
    generateTrajectories()
  }
}, { deep: true })

onMounted(async () => {
  // Set initial price
  const positions = portfolioPositions.value
  if (positions.length > 0) {
    initialPrice.value = positions.reduce((sum, p) => sum + p.allocation, 0)
  } else {
    initialPrice.value = 100
  }

  // Generate initial trajectories
  generateTrajectories()

  await nextTick()

  // Init 3D trajectories
  init3DTrajectories()

  // Init correlation heatmap
  initCorrelation3DHeatmap()

  // Init GARCH chart
  initGARCHChart()
})
</script>

<style scoped>
/* HERO */
.hero-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding-bottom: 8px;
}

.hero-left h1 {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 16px 0;
  letter-spacing: -0.01em;
}

.hero-meta {
  display: flex;
  gap: 10px;
}

.glass-pill {
  font-size: 12px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 99px;
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  gap: 6px;
  backdrop-filter: blur(4px);
}

.glass-pill strong {
  color: #fff;
  font-weight: 600;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-glass {
  height: 36px;
  padding: 0 16px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  border: 1px solid transparent;
}

.btn-glass.primary {
  background: rgba(255, 255, 255, 0.9);
  color: #000;
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2);
}

.btn-glass.primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(255, 255, 255, 0.3);
}

.btn-glass.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #000;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* MAIN GRID */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  align-items: stretch;
  width: 100%;
}

/* GLASS PANEL */
.glass-panel {
  background: rgba(20, 22, 28, 0.5);
  backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.02);
  flex-shrink: 0;
}

.panel-header h3 {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.panel-body {
  padding: 16px 20px;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.panel-body.weights-body {
  padding: 0;
}

.mono {
  font-family: 'SF Mono', monospace;
}

.text-right {
  text-align: right;
}

.font-bold {
  font-weight: 600;
}

.text-red {
  color: #f87171;
}

.text-green {
  color: #4ade80;
}

.opacity-80 {
  opacity: 0.8;
}

/* WEIGHTS TABLE */
.weights-comparison {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.weights-table-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

.weights-table-container::-webkit-scrollbar {
  width: 6px;
}

.weights-table-container::-webkit-scrollbar-track {
  background: transparent;
}

.weights-table-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.weights-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.weights-table thead {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(20, 22, 28, 0.98);
  backdrop-filter: blur(10px);
}

.weights-table th {
  padding: 10px 8px;
  text-align: left;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 9px;
  letter-spacing: 0.05em;
}

.weights-table th.text-right {
  text-align: right;
}

.weights-table tbody tr {
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  transition: background 0.15s;
}

.weights-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.weights-table td {
  padding: 8px;
  color: rgba(255, 255, 255, 0.9);
  vertical-align: middle;
}

.weights-table td.text-right {
  text-align: right;
}

.weights-table .change-pill {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 10px;
}

.weights-table .change-pill.text-green {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
}

.weights-table .change-pill.text-red {
  background: rgba(248, 113, 113, 0.15);
  color: #f87171;
}

/* ASSET */
.asset-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.asset-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 10px;
  color: #fff;
  flex-shrink: 0;
}

.asset-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.symbol {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  font-size: 11px;
}

.name {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.5);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.change-pill {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
}

/* HJB SPECIFIC */
.hjb-grid {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr);
  align-items: stretch;
  gap: 8px;
  margin-top: 8px;
}

.hjb-reports-grid {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  align-items: stretch;
  gap: 8px;
  margin-top: 8px;
}

.col-report-left,
.col-report-right {
  display: flex;
  flex-direction: column;
}

.report-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.col-portfolio-wide {
  grid-column: 1 / 3;
  display: flex;
  flex-direction: column;
  height: 450px;
}

.col-3d-right {
  grid-column: 3;
  display: flex;
  flex-direction: column;
  height: 450px;
  gap: 16px;
  justify-content: flex-start;
}

.col-3d-right .glass-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.col-3d-right .glass-panel:first-child {
  flex: 1 1 auto;
  min-height: 0;
}

.col-3d-right .glass-panel:only-child {
  flex: 1 1 auto;
  height: 100%;
}

.col-3d-right .glass-panel:only-child .panel-body {
  flex: 1;
}

.col-3d-right .glass-panel .panel-body {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.col-3d-right .glass-panel:first-child .panel-body {
  flex: 1;
  overflow: visible;
}

.portfolio-composition-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.correlation-3d-panel {
  display: flex;
  flex-direction: column;
  height: 450px;
  margin-bottom: 8px;
}

.correlation-3d-body {
  padding: 8px 10px 0 10px !important;
  position: relative;
  margin-bottom: 0;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  width: 100%;
  height: 100%;
}

.static-3d-plot {
  width: 100% !important;
  flex: 1 !important;
  min-height: 500px !important;
  height: 500px !important;
  background: transparent;
  border-radius: 8px;
  margin-bottom: 0;
}

/* HJB Parameters Row */
.hjb-params-row {
  margin-bottom: 8px;
}

.hjb-params-row .panel-body {
  flex-direction: row !important;
}

.params-row-body {
  padding: 16px 20px;
  display: flex !important;
  flex-direction: row !important;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: nowrap;
}

.param-group-horizontal {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.param-group-horizontal label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  white-space: nowrap;
  line-height: 1.2;
}

.param-group-horizontal .param-input-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.param-group-horizontal .param-input-group input {
  flex: 1;
  min-width: 70px;
  width: 100%;
  height: 32px;
  padding: 0 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #fff;
  font-size: 11px;
  font-family: 'SF Mono', monospace;
  outline: none;
  transition: all 0.2s;
}

.param-group-horizontal .param-input-group input:focus {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

/* GARCH */
.garch-full-width {
  width: 100%;
  margin-top: 8px;
  margin-bottom: 8px;
}

.garch-container-full {
  display: flex;
  flex-direction: row;
  gap: 24px;
  align-items: flex-start;
}

.garch-chart-placeholder-full {
  flex: 1;
  height: 200px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
  min-width: 0;
}

.garch-params-full {
  flex-shrink: 0;
  width: 300px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

#garch-chart {
  width: 100%;
  height: 100%;
  display: block;
}

.garch-param-row {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 12px;
  font-family: 'SF Mono', monospace;
}

.param-name {
  color: rgba(255, 255, 255, 0.5);
  margin-right: 8px;
}

.garch-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.garch-stat {
  display: flex;
  justify-content: space-between;
  padding: 6px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
  font-size: 10px;
}

.stat-label {
  color: rgba(255, 255, 255, 0.6);
}

.stat-val {
  color: #fff;
  font-weight: 600;
  font-family: 'SF Mono', monospace;
}

/* FILTERING REPORT */
.filtering-report {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.summary-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
}

.summary-value {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  font-family: 'SF Mono', monospace;
}

.filtering-criteria {
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.criteria-title {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}

.criteria-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.criteria-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
}

.criteria-check {
  color: #4ade80;
  font-weight: 700;
}

.filtered-assets {
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.filtered-title {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}

.filtered-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 150px;
  overflow-y: auto;
}

.filtered-asset {
  display: flex;
  justify-content: space-between;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
  font-size: 10px;
}

.asset-symbol {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.asset-garch {
  color: rgba(255, 255, 255, 0.6);
  font-family: 'SF Mono', monospace;
}

/* YIELD */
.yield-summary {
  padding: 12px;
  margin-top: 16px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.yield-summary-item {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
}

/* TOOLTIP */
.asset-tooltip-3d {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 16px;
  min-width: 240px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  z-index: 100;
  animation: fadeIn 0.2s ease-out;
  pointer-events: none;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.tooltip-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tooltip-symbol {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 2px;
}

.tooltip-name {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

.tooltip-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.tooltip-row span {
  color: rgba(255, 255, 255, 0.6);
}

.tooltip-row strong {
  color: #fff;
  font-weight: 600;
}

/* TRAJECTORIES */
.trajectories-panel {
  margin-top: 16px;
}

.trajectories-header-left,
.trajectories-3d-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trajectories-header-left h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.live-badge {
  font-size: 10px;
  color: #ef4444;
  font-weight: 700;
  animation: blink 1.5s infinite;
}

@keyframes blink {
  50% { opacity: 0.5; }
}

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
  font-size: 12px;
  border-radius: 50%;
  transition: 0.2s;
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
}

.playback-day-info {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.playback-day-info .mono {
  font-family: "SF Mono", monospace;
  color: #60a5fa;
  font-weight: 600;
}

.trajectories-chart-container {
  position: relative;
  width: 100%;
  height: 400px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  overflow: hidden;
}

.trajectories-svg {
  width: 100%;
  height: 100%;
}

.trajectories-3d-container {
  position: relative;
  width: 100%;
  height: 600px;
  min-height: 600px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  overflow: hidden;
}

.trajectories-3d-canvas {
  width: 100%;
  height: 100%;
  display: block;
  cursor: grab;
}

.trajectories-3d-canvas:active {
  cursor: grabbing;
}

.trajectories-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.3);
  font-size: 13px;
}

/* METRICS SUMMARY */
.metrics-summary-panel {
  margin-top: 24px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.metric-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: all 0.2s;
}

.metric-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
}

.metric-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}

.metric-value {
  font-size: 20px;
  font-weight: 700;
  font-family: 'SF Mono', monospace;
  color: rgba(255, 255, 255, 0.9);
}

.metric-value.text-green {
  color: #34d399;
}

.metric-value.text-red {
  color: #f87171;
}

/* RESPONSIVE */
@media (max-width: 1400px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .hjb-grid {
    grid-template-columns: 1fr;
  }
  .hjb-reports-grid {
    grid-template-columns: 1fr;
  }
  .col-portfolio-wide,
  .col-3d-right,
  .col-report-left,
  .col-report-right {
    grid-column: 1;
  }
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .hero-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .params-row-body {
    flex-direction: column;
    gap: 16px;
  }
  .param-group-horizontal {
    min-width: 100%;
  }
  .garch-container-full {
    flex-direction: column;
  }
  .garch-params-full {
    width: 100%;
  }
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  .metric-value {
    font-size: 18px;
  }
}
</style>
