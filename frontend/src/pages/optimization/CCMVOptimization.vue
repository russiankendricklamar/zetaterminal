<template>
  <div>
    <!-- Hero Section CCMV -->
    <div class="hero-section">
      <div class="hero-left">
        <h1>CCMV Optimization</h1>
        <div class="hero-meta">
          <span class="glass-pill">Метод: <strong>{{ params.method === 'delta' ? 'Δ-CCMV' : 'α-CCMV' }}</strong></span>
          <span class="glass-pill">Кластеров: <strong>{{ clusteringResult.numClusters }}</strong></span>
          <span class="glass-pill">Банк: <strong>{{ selectedBank.name }}</strong></span>
          <span class="glass-pill">Активов: <strong>{{ portfolioPositions.length }}</strong></span>
        </div>
      </div>
      <div class="hero-actions">
        <button class="btn-glass primary" @click="handleRecompute" :disabled="isComputing">
          <svg v-if="!isComputing" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <span v-else class="spinner"></span>
          {{ isComputing ? 'Расчёт...' : 'Пересчитать' }}
        </button>
      </div>
    </div>

    <!-- Portfolio Composition -->
    <div class="dashboard-grid hjb-grid">
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

      <!-- RIGHT: Optimization Parameters -->
      <div class="col-3d-right">
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Параметры оптимизации</h3>
            <div class="header-tabs">
              <button
                :class="['tab-btn', { active: paramsTab === 'basic' }]"
                @click="paramsTab = 'basic'"
              >
                Основные
              </button>
              <button
                :class="['tab-btn', { active: paramsTab === 'methodology' }]"
                @click="paramsTab = 'methodology'"
              >
                Методология
              </button>
            </div>
          </div>
          <div class="panel-body params-body">
            <div v-if="paramsTab === 'basic'">
              <div class="param-group">
                <label>Максимум активов (Δ)</label>
                <div class="param-input-group">
                  <input type="number" v-model.number="params.Delta" min="1" :max="clusteringResult.numAssets" />
                  <span class="param-hint">из {{ clusteringResult.numAssets }}</span>
                </div>
              </div>
              <div class="param-group">
                <label>Макс. вес на актив (w̄)</label>
                <div class="param-input-group">
                  <input type="number" v-model.number="params.bar_w" min="0.01" max="1" step="0.01" />
                  <span class="param-hint">{{ (params.bar_w * 100).toFixed(1) }}%</span>
                </div>
              </div>
              <div class="param-group">
                <label>Коэффициент неприятия риска (γ)</label>
                <div class="param-input-group">
                  <input type="number" v-model.number="params.gamma" min="0.1" max="10" step="0.1" />
                  <span class="param-hint">выше = консервативнее</span>
                </div>
              </div>
            </div>

            <div v-if="paramsTab === 'methodology'">
              <div class="param-group">
                <label>Методология</label>
                <div class="radio-group">
                  <label class="radio-item">
                    <input type="radio" v-model="params.method" value="delta" />
                    <span>Δ-CCMV (по количеству активов)</span>
                  </label>
                  <label class="radio-item">
                    <input type="radio" v-model="params.method" value="alpha" />
                    <span>α-CCMV (по распределению)</span>
                  </label>
                </div>
              </div>
            </div>
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
                <span class="comp-value text-red">{{ objectiveComponents.variance.toFixed(6) }}</span>
              </div>
              <div class="component">
                <span class="comp-label">Возврат</span>
                <span class="comp-value text-green">{{ (objectiveComponents.return * params.gamma).toFixed(6) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Weights Comparison and Clustering -->
    <div class="dashboard-grid hjb-grid">
      <div class="col-portfolio-wide">
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
              <div class="weights-table-container">
                <table class="weights-table">
                  <thead>
                    <tr>
                      <th>Инструмент</th>
                      <th class="text-right">Текущий вес</th>
                      <th class="text-right">Оптимальный вес</th>
                      <th class="text-right">Изменение</th>
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
                      <td class="text-right mono">{{ pos.allocation }}%</td>
                      <td class="text-right mono font-bold">{{ getOptimalWeight(pos.symbol).toFixed(1) }}%</td>
                      <td class="text-right mono">
                        <span :class="['change-pill', getDeltaClass(getWeightDelta(pos))]">
                          {{ getWeightDelta(pos) > 0 ? '+' : '' }}{{ getWeightDelta(pos).toFixed(1) }}%
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div v-if="weightsTab === 'optimal'" class="weights-optimal">
              <div class="weight-chart">
                <div v-for="pos in portfolioPositions" :key="pos.symbol" class="weight-bar-container">
                  <div class="weight-bar-info">
                    <div class="asset-icon-small" :style="{ background: pos.color }">{{ pos.symbol[0] }}</div>
                    <div class="weight-bar-label">{{ pos.symbol }}</div>
                  </div>
                  <div class="weight-bar-bg">
                    <div class="weight-bar-fill" :style="{ width: getOptimalWeight(pos.symbol) + '%', background: pos.color }" />
                  </div>
                  <div class="weight-bar-value mono">{{ getOptimalWeight(pos.symbol).toFixed(1) }}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT: Clustering Info -->
      <div class="col-3d-right">
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
                <span class="value mono">{{ portfolioPositions.length }}</span>
              </div>
              <div class="info-row">
                <span class="label">Метрика расстояния:</span>
                <span class="value mono">1 - ρ (корреляция)</span>
              </div>
              <div class="info-row">
                <span class="label">Метод кластеризации:</span>
                <span class="value mono">Иерархическая (Ward)</span>
              </div>
            </div>
            <div class="clusters-list">
              <div class="cluster-row" v-for="(cluster, idx) in clusteringResult.clusters" :key="idx">
                <div class="cluster-badge" :style="{ background: clusterColors[idx % clusterColors.length] }">
                  C{{ idx + 1 }}
                </div>
                <div class="cluster-detail">
                  <div class="cluster-label">Кластер {{ idx + 1 }}</div>
                  <div class="cluster-assets">
                    <div class="asset-tag" v-for="symbol in cluster.assets" :key="symbol">
                      <span class="asset-tag-symbol">{{ symbol }}</span>
                      <span class="asset-tag-weight" v-if="getAssetAllocation(symbol)">{{ getAssetAllocation(symbol) }}%</span>
                    </div>
                  </div>
                </div>
                <div class="cluster-count">{{ cluster.assets.length }} {{ cluster.assets.length === 1 ? 'актив' : cluster.assets.length < 5 ? 'актива' : 'активов' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="dashboard-grid">
      <!-- Cluster Metrics -->
      <div class="col-grid">
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
      </div>

      <!-- Cluster Allocation -->
      <div class="col-grid">
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Распределение по кластерам</h3>
          </div>
          <div class="panel-body allocation-body">
            <div class="allocation-chart">
              <div v-for="(alloc, idx) in clusterAllocations" :key="idx" class="alloc-segment" :style="{ flexGrow: alloc.percentage, background: clusterColors[idx] }">
                <span class="alloc-label">C{{ idx + 1 }}<br/>{{ alloc.percentage.toFixed(1) }}%</span>
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
      </div>

      <!-- Portfolio Statistics -->
      <div class="col-grid">
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useCCMVOptimization } from '../../composables/optimization/useCCMVOptimization'

const emit = defineEmits<{
  toast: [payload: { message: string; type: 'success' | 'error' | 'info' }]
}>()

const weightsTab = ref<'comparison' | 'optimal'>('comparison')
const paramsTab = ref<'basic' | 'methodology'>('basic')

const {
  isComputing,
  params,
  clusterColors,
  clusteringResult,
  clusterMetrics,
  objectiveValue,
  objectiveComponents,
  portfolioStats,
  clusterAllocations,
  getDeltaClass,
  getOptimalWeight,
  getWeightDelta,
  getAssetAllocation,
  recomputeOptimization,
  portfolioPositions,
  selectedBank
} = useCCMVOptimization()

const handleRecompute = () => {
  recomputeOptimization((msg: string, type: 'success' | 'error' | 'info') => {
    emit('toast', { message: msg, type })
  })
}
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

/* GRID */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  align-items: stretch;
  width: 100%;
}

.col-grid {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.col-grid .glass-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
}

.col-grid .glass-panel .panel-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
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
  position: relative;
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

/* HJB-GRID (reused for CCMV layout) */
.hjb-grid {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr);
  align-items: stretch;
  gap: 8px;
  margin-top: 8px;
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

.col-3d-right .glass-panel:last-child {
  flex: 0 0 auto;
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

.col-3d-right .glass-panel .panel-body.params-body {
  overflow: visible;
  gap: 14px;
}

.col-3d-right .glass-panel .panel-body:not(.params-body) {
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

.portfolio-composition-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
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

.weights-table .change-pill.text-green,
.weights-table .change-pill.positive {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
}

.weights-table .change-pill.text-red,
.weights-table .change-pill.negative {
  background: rgba(248, 113, 113, 0.15);
  color: #f87171;
}

.weights-table .change-pill.neutral {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.5);
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

/* PARAMS */
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

/* METRICS CARD */
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
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}

.asset-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  font-size: 9px;
}

.asset-tag-symbol {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.asset-tag-weight {
  color: rgba(255, 255, 255, 0.5);
  font-size: 8px;
}

.cluster-count {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
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

/* WEIGHTS BAR CHART */
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
  gap: 12px;
  padding: 8px 0;
}

.weight-bar-info {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 100px;
}

.asset-icon-small {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  flex-shrink: 0;
}

.weight-bar-label {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
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
  border-radius: 4px;
  transition: width 0.3s ease;
  min-width: 2px;
}

.weight-bar-value {
  width: 45px;
  text-align: right;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-family: 'SF Mono', monospace;
}

/* RESPONSIVE */
@media (max-width: 1400px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .hjb-grid {
    grid-template-columns: 1fr;
  }
  .col-portfolio-wide,
  .col-3d-right,
  .col-grid {
    grid-column: 1;
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
}
</style>
