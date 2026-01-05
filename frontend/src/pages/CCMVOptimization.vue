<!-- src/views/CCMVOptimizationPage.vue -->
<template>
  <div class="ccmv-page">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-left">
        <h1>CCMV Optimization</h1>
        <div class="hero-meta">
          <span class="glass-pill">Метод: <strong>{{ params.method === 'delta' ? 'Δ-CCMV' : 'α-CCMV' }}</strong></span>
          <span class="glass-pill">Кластеров: <strong>{{ clusteringResult.numClusters }}</strong></span>
          <span class="glass-pill">Активов: <strong>{{ clusteringResult.numAssets }}</strong></span>
        </div>
      </div>
      <div class="hero-actions">
        <button class="btn-glass primary" @click="recomputeOptimization" :disabled="isComputing">
          <svg v-if="!isComputing" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <span v-else class="spinner"></span>
          {{ isComputing ? 'Расчёт...' : 'Пересчитать' }}
        </button>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="dashboard-grid">
      <!-- LEFT COLUMN -->
      <div class="col-main">
        <!-- Clustering Info -->
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Иерархическая кластеризация</h3>
          </div>
          <div class="panel-body">
            <div class="cluster-info">
              <div class="info-row">
                <span class="label">Количество кластеров:</span>
                <span class="value mono">{{ clusteringResult.numClusters }}</span>
              </div>
              <div class="info-row">
                <span class="label">Активов в портфеле:</span>
                <span class="value mono">{{ clusteringResult.numAssets }}</span>
              </div>
              <div class="info-row">
                <span class="label">Метрика расстояния:</span>
                <span class="value mono">1 - ρ (корреляция)</span>
              </div>
            </div>

            <!-- Clusters breakdown -->
            <div class="clusters-list">
              <div class="cluster-row" v-for="(cluster, idx) in clusteringResult.clusters" :key="idx">
                <div class="cluster-badge" :style="{ background: clusterColors[idx] }">
                  C{{ idx + 1 }}
                </div>
                <div class="cluster-detail">
                  <div class="cluster-label">Кластер {{ idx + 1 }}</div>
                  <div class="cluster-assets">{{ cluster.assets.join(', ') }}</div>
                </div>
                <div class="cluster-count">{{ cluster.assets.length }} активов</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Optimization Parameters -->
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Параметры оптимизации</h3>
          </div>
          <div class="panel-body params-body">
            <div class="param-group">
              <label>Максимум активов (Δ)</label>
              <div class="param-input-group">
                <input
                  type="number"
                  v-model.number="params.Delta"
                  min="1"
                  :max="clusteringResult.numAssets"
                  @input="recomputeOptimization"
                />
                <span class="param-hint">из {{ clusteringResult.numAssets }}</span>
              </div>
            </div>

            <div class="param-group">
              <label>Макс. вес на актив (w̄)</label>
              <div class="param-input-group">
                <input
                  type="number"
                  v-model.number="params.bar_w"
                  min="0.01"
                  max="1"
                  step="0.01"
                  @input="recomputeOptimization"
                />
                <span class="param-hint">{{ (params.bar_w * 100).toFixed(1) }}%</span>
              </div>
            </div>

            <div class="param-group">
              <label>Коэффициент неприятия риска (γ)</label>
              <div class="param-input-group">
                <input
                  type="number"
                  v-model.number="params.gamma"
                  min="0.1"
                  max="10"
                  step="0.1"
                  @input="recomputeOptimization"
                />
                <span class="param-hint">выше = консервативнее</span>
              </div>
            </div>

            <div class="param-group">
              <label>Методология</label>
              <div class="radio-group">
                <label class="radio-item">
                  <input
                    type="radio"
                    v-model="params.method"
                    value="delta"
                    @change="recomputeOptimization"
                  />
                  <span>Δ-CCMV (по количеству активов)</span>
                </label>
                <label class="radio-item">
                  <input
                    type="radio"
                    v-model="params.method"
                    value="alpha"
                    @change="recomputeOptimization"
                  />
                  <span>α-CCMV (по распределению)</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- CENTER: Cluster Metrics -->
      <div class="col-center">
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Метрики по кластерам</h3>
          </div>
          <div class="panel-body metrics-table-body">
            <table class="metrics-table">
              <thead>
                <tr>
                  <th>Кластер</th>
                  <th>μ (E[R])</th>
                  <th>σ (Vol)</th>
                  <th>ρ̄</th>
                  <th>Δₖ</th>
                  <th>αₖ</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(metric, idx) in clusterMetrics" :key="idx">
                  <td>
                    <div class="cluster-cell">
                      <div class="cluster-dot" :style="{ background: clusterColors[idx] }"></div>
                      <span>C{{ idx + 1 }}</span>
                    </div>
                  </td>
                  <td class="mono text-right">{{ (metric.expectedReturn * 100).toFixed(2) }}%</td>
                  <td class="mono text-right">{{ (metric.volatility * 100).toFixed(2) }}%</td>
                  <td class="mono text-right">{{ metric.avgCorrelation.toFixed(3) }}</td>
                  <td class="mono text-right font-bold">{{ metric.deltaK }}</td>
                  <td class="mono text-right font-bold">{{ (metric.alphaK * 100).toFixed(1) }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Objective Function Value -->
        <div class="glass-panel metrics-card">
          <div class="panel-header">
            <h3>Целевая функция</h3>
          </div>
          <div class="panel-body metrics-value">
            <div class="obj-value">
              <span class="label">f*(Δ, α) =</span>
              <span class="value">{{ objectiveValue.toFixed(6) }}</span>
            </div>
            <div class="obj-components">
              <div class="component">
                <span class="comp-label">Риск</span>
                <span class="comp-value text-red">{{ (objectiveComponents.variance).toFixed(6) }}</span>
              </div>
              <div class="component">
                <span class="comp-label">Возврат</span>
                <span class="comp-value text-green">{{ (objectiveComponents.return * params.gamma).toFixed(6) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Portfolio Statistics -->
        <div class="glass-panel metrics-card">
          <div class="panel-header">
            <h3>Статистика портфеля</h3>
          </div>
          <div class="panel-body">
            <div class="stat-row">
              <span class="stat-label">Expected Return</span>
              <span class="stat-val text-green">{{ (portfolioStats.expectedReturn * 100).toFixed(2) }}%</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Volatility</span>
              <span class="stat-val">{{ (portfolioStats.volatility * 100).toFixed(2) }}%</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Sharpe Ratio</span>
              <span class="stat-val">{{ portfolioStats.sharpeRatio.toFixed(3) }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Кол-во позиций</span>
              <span class="stat-val mono">{{ portfolioStats.numPositions }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN -->
      <aside class="col-side-flex">
        <!-- Weights Comparison -->
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Сравнение весов</h3>
            <div class="header-tabs">
              <button
                :class="['tab-btn', { active: weightsTab === 'comparison' }]"
                @click="weightsTab = 'comparison'"
              >
                Сравнение
              </button>
              <button
                :class="['tab-btn', { active: weightsTab === 'optimal' }]"
                @click="weightsTab = 'optimal'"
              >
                Оптимальные
              </button>
            </div>
          </div>
          <div class="panel-body weights-body">
            <div v-if="weightsTab === 'comparison'" class="weights-comparison">
              <div class="comp-header">
                <span class="col-label">Актив</span>
                <span class="col-label">Текущий</span>
                <span class="col-label">Оптимальный</span>
                <span class="col-label">Дельта</span>
              </div>
              <div
                v-for="(weight, symbol) in optimizationResult.weights"
                :key="symbol"
                class="weight-row"
              >
                <span class="asset-label">{{ symbol }}</span>
                <span class="weight-cell mono">{{ (currentWeights[symbol] * 100).toFixed(1) }}%</span>
                <span class="weight-cell mono font-bold">{{ (weight * 100).toFixed(1) }}%</span>
                <span class="weight-cell delta mono" :class="getDeltaClass(currentWeights[symbol] - weight)">
                  {{ ((currentWeights[symbol] - weight) * 100).toFixed(1) }}%
                </span>
              </div>
            </div>

            <div v-if="weightsTab === 'optimal'" class="weights-optimal">
              <div class="weight-chart">
                <div
                  v-for="(weight, symbol) in optimizationResult.weights"
                  :key="symbol"
                  class="weight-bar-container"
                >
                  <div class="weight-bar-label">{{ symbol }}</div>
                  <div class="weight-bar-bg">
                    <div
                      class="weight-bar-fill"
                      :style="{ width: (weight * 100) + '%' }"
                    />
                  </div>
                  <div class="weight-bar-value">{{ (weight * 100).toFixed(1) }}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Cluster Allocation -->
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Распределение по кластерам</h3>
          </div>
          <div class="panel-body allocation-body">
            <div class="allocation-chart">
              <div
                v-for="(alloc, idx) in clusterAllocations"
                :key="idx"
                class="alloc-segment"
                :style="{ 
                  flexGrow: alloc.percentage,
                  background: clusterColors[idx]
                }"
              >
                <span class="alloc-label">
                  C{{ idx + 1 }}<br/>{{ alloc.percentage.toFixed(1) }}%
                </span>
              </div>
            </div>
            <div class="allocation-details">
              <div v-for="(alloc, idx) in clusterAllocations" :key="idx" class="alloc-row">
                <div class="alloc-dot" :style="{ background: clusterColors[idx] }"></div>
                <span class="alloc-name">Кластер {{ idx + 1 }}</span>
                <span class="alloc-pct mono">{{ alloc.percentage.toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- Toast -->
    <transition name="slide-up">
      <div
        v-if="toast.show"
        class="toast-notification"
        :class="'toast-' + toast.type"
      >
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Cluster {
  assets: string[]
}

interface ClusterMetric {
  expectedReturn: number
  volatility: number
  avgCorrelation: number
  deltaK: number
  alphaK: number
}

const isComputing = ref(false)
const weightsTab = ref<'comparison' | 'optimal'>('comparison')

const toast = ref<{ show: boolean; message: string; type: 'success' | 'error' | 'info' }>({
  show: false,
  message: '',
  type: 'success'
})

// Clustering result (mock from notebook)
const clusteringResult = ref({
  numClusters: 3,
  numAssets: 5,
  clusters: [
    { assets: ['SPY', 'QQQ'] },
    { assets: ['TLT', 'BND'] },
    { assets: ['GLD', 'DXY'] }
  ] as Cluster[]
})

const clusterColors = [
  '#3b82f6', // blue
  '#10b981', // green
  '#f59e0b'  // amber
]

// Parameters
const params = ref({
  Delta: 3,
  bar_w: 0.25,
  gamma: 2.0,
  method: 'delta' as 'delta' | 'alpha'
})

// Current portfolio weights (mock)
const currentWeights = ref({
  SPY: 0.35,
  QQQ: 0.12,
  TLT: 0.25,
  BND: 0.0,
  GLD: 0.18,
  DXY: 0.15
})

// Cluster metrics
const clusterMetrics = computed<ClusterMetric[]>(() => {
  const mockMetrics: ClusterMetric[] = [
    {
      expectedReturn: 0.085,
      volatility: 0.18,
      avgCorrelation: 0.75,
      deltaK: 2,
      alphaK: params.value.method === 'delta' ? 0.33 : 0.35
    },
    {
      expectedReturn: 0.045,
      volatility: 0.08,
      avgCorrelation: 0.65,
      deltaK: 1,
      alphaK: params.value.method === 'delta' ? 0.33 : 0.30
    },
    {
      expectedReturn: 0.055,
      volatility: 0.12,
      avgCorrelation: 0.40,
      deltaK: 1,
      alphaK: params.value.method === 'delta' ? 0.34 : 0.35
    }
  ]
  return mockMetrics
})

// Optimization result (mock CCMV solution)
const optimizationResult = computed(() => {
  const baseWeights = {
    SPY: 0.38,
    QQQ: 0.10,
    TLT: 0.27,
    BND: 0.0,
    GLD: 0.15,
    DXY: 0.10
  }
  return {
    weights: baseWeights,
    method: params.value.method
  }
})

// Objective function
const objectiveValue = computed(() => {
  const variance = 0.0185
  const expectedReturn = 0.0625
  return variance - params.value.gamma * expectedReturn
})

const objectiveComponents = computed(() => ({
  variance: 0.0185,
  return: 0.0625
}))

// Portfolio statistics
const portfolioStats = computed(() => ({
  expectedReturn: 0.0625,
  volatility: 0.136,
  sharpeRatio: (0.0625 - 0.042) / 0.136,
  numPositions: Object.values(optimizationResult.value.weights).filter(w => w > 0.001).length
}))

// Cluster allocations
const clusterAllocations = computed(() => {
  const alloc = clusterMetrics.value.map(m => m.alphaK)
  return alloc.map(a => ({ percentage: a * 100 }))
})

const getDeltaClass = (delta: number) => {
  if (Math.abs(delta) < 0.001) return 'neutral'
  return delta > 0 ? 'positive' : 'negative'
}

const recomputeOptimization = async () => {
  isComputing.value = true
  await new Promise(r => setTimeout(r, 1200))
  isComputing.value = false
  showToast(`Оптимизация завершена (${params.value.method === 'delta' ? 'Δ-CCMV' : 'α-CCMV'})`, 'success')
}

const showToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}
</script>

<style scoped>
/* LAYOUT */
.ccmv-page {
  padding: 24px 32px;
  max-width: 1800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 28px;
  min-height: 100vh;
}

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
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr) minmax(0, 1.2fr);
  gap: 24px;
  align-items: flex-start;
}

.col-main,
.col-center,
.col-side-flex {
  display: flex;
  flex-direction: column;
  gap: 24px;
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

.header-tabs {
  display: flex;
  gap: 6px;
}

.tab-btn {
  font-size: 10px;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.15s;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.tab-btn.active {
  background: rgba(59, 130, 246, 0.3);
  color: #60a5fa;
  border-color: rgba(59, 130, 246, 0.5);
}

.panel-body {
  padding: 16px 20px;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.panel-body.params-body {
  gap: 14px;
}

.panel-body.metrics-table-body {
  padding: 0;
}

.panel-body.metrics-value {
  gap: 16px;
}

.panel-body.weights-body {
  padding: 0;
}

.panel-body.allocation-body {
  gap: 14px;
}

/* CLUSTER INFO */
.cluster-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.label {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.value {
  color: #fff;
  font-weight: 600;
}

.mono {
  font-family: 'SF Mono', monospace;
}

/* CLUSTERS LIST */
.clusters-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cluster-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 11px;
  transition: all 0.2s;
}

.cluster-row:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.15);
}

.cluster-badge {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
  font-size: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.cluster-detail {
  flex: 1;
  min-width: 0;
}

.cluster-label {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2px;
  font-size: 10px;
}

.cluster-assets {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.5);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cluster-count {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

/* PARAMETERS */
.param-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.param-group label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.param-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.param-input-group input {
  flex: 1;
  height: 28px;
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

.param-input-group input:focus {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.param-hint {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
  flex-shrink: 0;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
}

.radio-item input {
  accent-color: #3b82f6;
}

/* METRICS TABLE */
.metrics-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.metrics-table th {
  text-align: left;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 9px;
  letter-spacing: 0.05em;
}

.metrics-table td {
  padding: 8px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.9);
}

.metrics-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.cluster-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.cluster-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.text-right {
  text-align: right;
}

.font-bold {
  font-weight: 600;
}

/* METRICS CARDS */
.metrics-card {
  gap: 0;
}

.obj-value {
  display: flex;
  align-items: baseline;
  gap: 10px;
  padding: 10px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.obj-value .label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.obj-value .value {
  font-size: 14px;
  font-weight: 700;
  color: #60a5fa;
  font-family: 'SF Mono', monospace;
}

.obj-components {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.component {
  background: rgba(255, 255, 255, 0.02);
  padding: 8px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.comp-label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
}

.comp-value {
  font-size: 11px;
  font-weight: 600;
  font-family: 'SF Mono', monospace;
}

.text-red {
  color: #f87171;
}

.text-green {
  color: #4ade80;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  font-size: 11px;
}

.stat-label {
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.stat-val {
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

/* WEIGHTS */
.weights-comparison {
  max-height: 400px;
  overflow-y: auto;
}

.comp-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 9px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  position: sticky;
  top: 0;
  text-transform: uppercase;
}

.col-label {
  text-align: right;
}

.weight-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 8px;
  padding: 6px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  font-size: 11px;
  align-items: center;
}

.weight-row:hover {
  background: rgba(255, 255, 255, 0.02);
}

.asset-label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.weight-cell {
  text-align: right;
  color: rgba(255, 255, 255, 0.8);
}

.weight-cell.delta {
  font-weight: 600;
}

.weight-cell.delta.neutral {
  color: rgba(255, 255, 255, 0.4);
}

.weight-cell.delta.positive {
  color: #4ade80;
}

.weight-cell.delta.negative {
  color: #f87171;
}

.weights-optimal {
  padding: 8px;
}

.weight-chart {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.weight-bar-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.weight-bar-label {
  width: 40px;
  text-align: right;
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.weight-bar-bg {
  flex: 1;
  height: 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.weight-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.8), #3b82f6);
  transition: width 0.3s ease;
}

.weight-bar-value {
  width: 45px;
  text-align: right;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-family: 'SF Mono', monospace;
}

/* ALLOCATION */
.allocation-chart {
  display: flex;
  height: 80px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.alloc-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.alloc-label {
  line-height: 1.1;
  text-align: center;
}

.allocation-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.alloc-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px;
  font-size: 10px;
}

.alloc-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.alloc-name {
  flex: 1;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.alloc-pct {
  color: rgba(255, 255, 255, 0.5);
  font-size: 9px;
}

/* TOAST */
.toast-notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 14px 20px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  max-width: 320px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.toast-success {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
  border-color: rgba(74, 222, 128, 0.3);
}

.toast-error {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.3);
}

.toast-info {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
  border-color: rgba(96, 165, 250, 0.3);
}

/* TRANSITIONS */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.slide-up-enter-from {
  transform: translateY(20px);
  opacity: 0;
}

.slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

/* RESPONSIVE */
@media (max-width: 1400px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .ccmv-page {
    padding: 16px;
    gap: 20px;
  }

  .hero-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>