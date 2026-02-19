<template>
  <div>
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-left">
        <h1>Black-Litterman Optimization</h1>
        <div class="hero-meta">
          <span class="glass-pill">Метод: <strong>Байесовская оптимизация</strong></span>
          <span class="glass-pill">τ: <strong>{{ params.tau }}</strong></span>
          <span class="glass-pill">δ: <strong>{{ params.delta }}</strong></span>
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

    <!-- Parameters + Views Row -->
    <div class="dashboard-grid params-grid">
      <!-- LEFT: Model Parameters -->
      <div class="col-params">
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Параметры модели</h3>
          </div>
          <div class="panel-body params-body">
            <div class="param-group">
              <label>Скаляр неопределённости (τ)</label>
              <div class="param-input-group">
                <input type="number" v-model.number="params.tau" min="0.001" max="1" step="0.01" />
                <span class="param-hint">Типично 0.01–0.10</span>
              </div>
            </div>
            <div class="param-group">
              <label>Неприятие риска (δ)</label>
              <div class="param-input-group">
                <input type="number" v-model.number="params.delta" min="0.1" max="20" step="0.1" />
                <span class="param-hint">Типично 2.0–3.5</span>
              </div>
            </div>
            <div class="param-group">
              <label>Безрисковая ставка (r)</label>
              <div class="param-input-group">
                <input type="number" v-model.number="params.riskFreeRate" min="0" max="0.3" step="0.005" />
                <span class="param-hint">{{ (params.riskFreeRate * 100).toFixed(1) }}%</span>
              </div>
            </div>
            <div class="param-group">
              <label>Макс. вес на актив</label>
              <div class="param-input-group">
                <input type="number" v-model.number="params.maxWeight" min="0.05" max="1" step="0.05" />
                <span class="param-hint">{{ (params.maxWeight * 100).toFixed(0) }}%</span>
              </div>
            </div>
            <div class="formula-box">
              <span class="formula-label">Black-Litterman Formula</span>
              <div class="formula">E[R] = [(τΣ)⁻¹ + P'Ω⁻¹P]⁻¹ [(τΣ)⁻¹π + P'Ω⁻¹Q]</div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT: Investor Views -->
      <div class="col-views">
        <div class="glass-panel views-panel">
          <div class="panel-header">
            <h3>Взгляды инвестора (Views)</h3>
            <button class="btn-add-view" @click="addView">+ Добавить</button>
          </div>
          <div class="panel-body views-body">
            <div v-for="(view, idx) in views" :key="view.id" class="view-card">
              <div class="view-header">
                <span class="view-badge">V{{ idx + 1 }}</span>
                <div class="view-type-toggle">
                  <button
                    :class="['type-btn', { active: view.type === 'absolute' }]"
                    @click="view.type = 'absolute'"
                  >Абсолютный</button>
                  <button
                    :class="['type-btn', { active: view.type === 'relative' }]"
                    @click="view.type = 'relative'"
                  >Относительный</button>
                </div>
                <button class="btn-remove-view" @click="removeView(view.id)">×</button>
              </div>
              <div class="view-body">
                <div class="view-row">
                  <div class="view-field">
                    <label>{{ view.type === 'absolute' ? 'Актив' : 'Актив 1 (long)' }}</label>
                    <select v-model.number="view.asset1Index">
                      <option
                        v-for="(pos, i) in portfolioPositions"
                        :key="pos.symbol"
                        :value="i"
                      >{{ pos.symbol }}</option>
                    </select>
                  </div>
                  <div class="view-field" v-if="view.type === 'relative'">
                    <label>Актив 2 (short)</label>
                    <select v-model.number="view.asset2Index">
                      <option
                        v-for="(pos, i) in portfolioPositions"
                        :key="pos.symbol"
                        :value="i"
                      >{{ pos.symbol }}</option>
                    </select>
                  </div>
                </div>
                <div class="view-row">
                  <div class="view-field">
                    <label>Ожидаемая доходность</label>
                    <div class="param-input-group">
                      <input type="number" v-model.number="view.expectedReturn" step="0.01" />
                      <span class="param-hint">{{ (view.expectedReturn * 100).toFixed(1) }}%</span>
                    </div>
                  </div>
                  <div class="view-field">
                    <label>Уверенность</label>
                    <div class="confidence-slider">
                      <input type="range" v-model.number="view.confidence" min="0.01" max="1" step="0.01" />
                      <span class="confidence-val" :class="confidenceClass(view.confidence)">
                        {{ (view.confidence * 100).toFixed(0) }}%
                      </span>
                    </div>
                  </div>
                </div>
                <div class="view-description">
                  <template v-if="view.type === 'absolute'">
                    {{ getAssetName(view.asset1Index) }} вернёт
                    <strong :class="view.expectedReturn >= 0 ? 'text-green' : 'text-red'">
                      {{ (view.expectedReturn * 100).toFixed(1) }}%
                    </strong>
                  </template>
                  <template v-else>
                    {{ getAssetName(view.asset1Index) }} обгонит {{ getAssetName(view.asset2Index) }} на
                    <strong :class="view.expectedReturn >= 0 ? 'text-green' : 'text-red'">
                      {{ (view.expectedReturn * 100).toFixed(1) }}%
                    </strong>
                  </template>
                </div>
              </div>
            </div>
            <div v-if="views.length === 0" class="views-empty">
              Нет взглядов. Нажмите «+ Добавить» чтобы задать прогнозы.
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Portfolio Composition + Returns Comparison -->
    <div class="dashboard-grid main-grid">
      <!-- LEFT: Portfolio Composition -->
      <div class="col-portfolio-wide">
        <div class="glass-panel portfolio-composition-panel">
          <div class="panel-header">
            <h3>Сравнение весов</h3>
            <div class="header-tabs">
              <button :class="['tab-btn', { active: weightsTab === 'comparison' }]" @click="weightsTab = 'comparison'">
                Сравнение
              </button>
              <button :class="['tab-btn', { active: weightsTab === 'bars' }]" @click="weightsTab = 'bars'">
                Визуализация
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
                      <th class="text-right">Рыночный вес</th>
                      <th class="text-right">Равновесный</th>
                      <th class="text-right">BL оптимальный</th>
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
                      <td class="text-right mono opacity-80">{{ pos.allocation.toFixed(1) }}%</td>
                      <td class="text-right mono">{{ getEquilibriumWeight(pos.symbol).toFixed(1) }}%</td>
                      <td class="text-right mono font-bold">{{ getOptimalWeight(pos.symbol).toFixed(1) }}%</td>
                      <td class="text-right mono">
                        <span :class="['change-pill', getDeltaClass(getWeightDelta(pos.symbol))]">
                          {{ getWeightDelta(pos.symbol) > 0 ? '+' : '' }}{{ getWeightDelta(pos.symbol).toFixed(1) }}%
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div v-if="weightsTab === 'bars'" class="weights-bars-view">
              <div v-for="pos in portfolioPositions" :key="pos.symbol" class="weight-bar-container">
                <div class="weight-bar-info">
                  <div class="asset-icon-small" :style="{ background: pos.color }">{{ pos.symbol[0] }}</div>
                  <div class="weight-bar-label">{{ pos.symbol }}</div>
                </div>
                <div class="weight-bars-group">
                  <div class="weight-bar-row-dual">
                    <span class="bar-label-sm">Рынок</span>
                    <div class="weight-bar-bg">
                      <div class="weight-bar-fill eq" :style="{ width: pos.allocation + '%' }" />
                    </div>
                    <span class="weight-bar-value mono">{{ pos.allocation.toFixed(1) }}%</span>
                  </div>
                  <div class="weight-bar-row-dual">
                    <span class="bar-label-sm">BL</span>
                    <div class="weight-bar-bg">
                      <div class="weight-bar-fill bl" :style="{ width: getOptimalWeight(pos.symbol) + '%', background: pos.color }" />
                    </div>
                    <span class="weight-bar-value mono font-bold">{{ getOptimalWeight(pos.symbol).toFixed(1) }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT: Returns Comparison -->
      <div class="col-returns-right">
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Доходности: Равновесные vs Апостериорные</h3>
          </div>
          <div class="panel-body weights-body">
            <div class="weights-comparison">
              <div class="weights-table-container">
                <table class="weights-table">
                  <thead>
                    <tr>
                      <th>Актив</th>
                      <th class="text-right">π (равнов.)</th>
                      <th class="text-right">E[R] (BL)</th>
                      <th class="text-right">Δ</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(pos, idx) in portfolioPositions" :key="pos.symbol">
                      <td>
                        <div class="asset-cell">
                          <div class="asset-icon" :style="{ background: pos.color }">{{ pos.symbol[0] }}</div>
                          <span class="symbol">{{ pos.symbol }}</span>
                        </div>
                      </td>
                      <td class="text-right mono">{{ formatPct(equilibriumReturns[idx]) }}</td>
                      <td class="text-right mono font-bold" :class="posteriorReturns[idx] >= 0 ? 'text-green' : 'text-red'">
                        {{ formatPct(posteriorReturns[idx]) }}
                      </td>
                      <td class="text-right mono">
                        <span :class="['change-pill', posteriorReturns[idx] - equilibriumReturns[idx] >= 0 ? 'positive' : 'negative']">
                          {{ (posteriorReturns[idx] - equilibriumReturns[idx]) >= 0 ? '+' : '' }}{{ formatPct(posteriorReturns[idx] - equilibriumReturns[idx]) }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Views Impact Panel -->
    <div class="glass-panel views-impact-panel" v-if="viewsImpact.length > 0">
      <div class="panel-header">
        <h3>Влияние взглядов на портфель</h3>
      </div>
      <div class="panel-body">
        <div class="impact-grid">
          <div v-for="(impact, idx) in viewsImpact" :key="idx" class="impact-card">
            <div class="impact-header">
              <span class="view-badge-sm">V{{ idx + 1 }}</span>
              <span class="impact-assets">{{ impact.affected_assets.join(', ') }}</span>
            </div>
            <div class="impact-metrics">
              <div class="impact-metric">
                <span class="metric-label">Ожидаемая доходность</span>
                <span class="metric-value" :class="impact.view_return >= 0 ? 'text-green' : 'text-red'">
                  {{ formatPct(impact.view_return) }}
                </span>
              </div>
              <div class="impact-metric">
                <span class="metric-label">Уверенность</span>
                <span class="metric-value" :class="confidenceClass(impact.confidence)">
                  {{ (impact.confidence * 100).toFixed(0) }}%
                </span>
              </div>
              <div class="impact-metric">
                <span class="metric-label">Сдвиг веса</span>
                <span class="metric-value" :class="impact.weight_shift >= 0 ? 'text-green' : 'text-red'">
                  {{ impact.weight_shift >= 0 ? '+' : '' }}{{ (impact.weight_shift * 100).toFixed(2) }}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Risk Contributions -->
    <div class="glass-panel" v-if="blResult">
      <div class="panel-header">
        <h3>Вклад в риск портфеля</h3>
      </div>
      <div class="panel-body">
        <div class="risk-bars">
          <div v-for="(pos, idx) in portfolioPositions" :key="pos.symbol" class="risk-bar-row">
            <div class="risk-bar-info">
              <div class="asset-icon-small" :style="{ background: pos.color }">{{ pos.symbol[0] }}</div>
              <span class="risk-bar-label">{{ pos.symbol }}</span>
            </div>
            <div class="weight-bar-bg">
              <div
                class="weight-bar-fill"
                :style="{
                  width: Math.min(Math.abs(riskContributions[idx]) / maxRiskContrib * 100, 100) + '%',
                  background: pos.color
                }"
              />
            </div>
            <span class="risk-bar-value mono">{{ formatPct(riskContributions[idx]) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Metrics Summary -->
    <div class="dashboard-grid metrics-grid-row">
      <!-- BL Portfolio Stats -->
      <div class="col-metric">
        <div class="glass-panel metrics-card">
          <div class="panel-header">
            <h3>BL Портфель (с Views)</h3>
          </div>
          <div class="panel-body">
            <div class="stat-row">
              <span class="stat-label">Expected Return</span>
              <span class="stat-val text-green">{{ formatPct(portfolioStats.expectedReturn) }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Volatility</span>
              <span class="stat-val">{{ formatPct(portfolioStats.volatility) }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Sharpe Ratio</span>
              <span class="stat-val" :class="portfolioStats.sharpeRatio >= 0 ? 'text-green' : 'text-red'">
                {{ portfolioStats.sharpeRatio.toFixed(3) }}
              </span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Позиций</span>
              <span class="stat-val mono">{{ portfolioStats.numPositions }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Equilibrium Stats -->
      <div class="col-metric">
        <div class="glass-panel metrics-card">
          <div class="panel-header">
            <h3>Равновесный (без Views)</h3>
          </div>
          <div class="panel-body">
            <div class="stat-row">
              <span class="stat-label">Expected Return</span>
              <span class="stat-val">{{ formatPct(equilibriumStats.expectedReturn) }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Volatility</span>
              <span class="stat-val">{{ formatPct(equilibriumStats.volatility) }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Sharpe Ratio</span>
              <span class="stat-val">{{ equilibriumStats.sharpeRatio.toFixed(3) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Improvement Delta -->
      <div class="col-metric">
        <div class="glass-panel metrics-card">
          <div class="panel-header">
            <h3>Прирост от Views</h3>
          </div>
          <div class="panel-body">
            <div class="stat-row">
              <span class="stat-label">Δ Return</span>
              <span class="stat-val" :class="returnDelta >= 0 ? 'text-green' : 'text-red'">
                {{ returnDelta >= 0 ? '+' : '' }}{{ formatPct(returnDelta) }}
              </span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Δ Volatility</span>
              <span class="stat-val" :class="volDelta <= 0 ? 'text-green' : 'text-red'">
                {{ volDelta >= 0 ? '+' : '' }}{{ formatPct(volDelta) }}
              </span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Δ Sharpe</span>
              <span class="stat-val" :class="sharpeDelta >= 0 ? 'text-green' : 'text-red'">
                {{ sharpeDelta >= 0 ? '+' : '' }}{{ sharpeDelta.toFixed(3) }}
              </span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Взглядов</span>
              <span class="stat-val mono">{{ views.length }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useBlackLittermanOptimization } from '../../composables/optimization/useBlackLittermanOptimization'

const emit = defineEmits<{
  toast: [payload: { message: string; type: 'success' | 'error' | 'info' }]
}>()

const weightsTab = ref<'comparison' | 'bars'>('comparison')

const {
  isComputing,
  params,
  views,
  blResult,
  portfolioPositions,
  selectedBank,
  equilibriumReturns,
  posteriorReturns,
  portfolioStats,
  equilibriumStats,
  viewsImpact,
  riskContributions,
  addView,
  removeView,
  getOptimalWeight,
  getEquilibriumWeight,
  getWeightDelta,
  getDeltaClass,
  runOptimization,
} = useBlackLittermanOptimization()

const handleRunOptimization = () => {
  runOptimization((msg, type) => {
    emit('toast', { message: msg, type })
  })
}

const formatPct = (v: number): string => `${(v * 100).toFixed(2)}%`

const getAssetName = (idx: number): string => {
  return portfolioPositions.value[idx]?.symbol ?? `Asset_${idx}`
}

const confidenceClass = (c: number): string => {
  if (c >= 0.7) return 'conf-high'
  if (c >= 0.4) return 'conf-mid'
  return 'conf-low'
}

const maxRiskContrib = computed(() => {
  const vals = riskContributions.value.map(Math.abs)
  return Math.max(...vals, 0.001)
})

const returnDelta = computed(() =>
  portfolioStats.value.expectedReturn - equilibriumStats.value.expectedReturn
)
const volDelta = computed(() =>
  portfolioStats.value.volatility - equilibriumStats.value.volatility
)
const sharpeDelta = computed(() =>
  portfolioStats.value.sharpeRatio - equilibriumStats.value.sharpeRatio
)
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
  flex-wrap: wrap;
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
  gap: 8px;
  align-items: stretch;
  width: 100%;
  margin-top: 8px;
}

.params-grid {
  grid-template-columns: minmax(0, 1fr) minmax(0, 2fr);
}

.main-grid {
  grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
}

.metrics-grid-row {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.col-params,
.col-views,
.col-portfolio-wide,
.col-returns-right,
.col-metric {
  display: flex;
  flex-direction: column;
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
  color: #c084fc;
  border-color: rgba(168, 85, 247, 0.5);
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

.panel-body.views-body {
  gap: 8px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

.panel-body.weights-body {
  padding: 0;
}

.mono { font-family: 'SF Mono', monospace; }
.text-right { text-align: right; }
.font-bold { font-weight: 600; }
.text-red { color: #f87171; }
.text-green { color: #4ade80; }
.opacity-80 { opacity: 0.8; }

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

.param-input-group input[type="number"] {
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
  border-color: rgba(168, 85, 247, 0.5);
  background: rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.1);
}

.param-hint {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
  flex-shrink: 0;
}

.formula-box {
  padding: 14px;
  background: rgba(168, 85, 247, 0.08);
  border: 1px solid rgba(168, 85, 247, 0.25);
  border-radius: 10px;
  margin-top: 4px;
}

.formula-label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
  display: block;
}

.formula {
  font-size: 13px;
  font-family: 'Times New Roman', serif;
  font-style: italic;
  color: #c084fc;
  text-align: center;
}

/* VIEWS */
.views-panel {
  min-height: 400px;
}

.btn-add-view {
  font-size: 11px;
  padding: 4px 12px;
  border-radius: 6px;
  border: 1px solid rgba(168, 85, 247, 0.4);
  background: rgba(168, 85, 247, 0.15);
  color: #c084fc;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-add-view:hover {
  background: rgba(168, 85, 247, 0.25);
  border-color: rgba(168, 85, 247, 0.6);
}

.view-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
}

.view-card:hover {
  border-color: rgba(168, 85, 247, 0.3);
}

.view-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.view-badge {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(168, 85, 247, 0.2);
  border: 1px solid rgba(168, 85, 247, 0.4);
  color: #c084fc;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 10px;
  flex-shrink: 0;
}

.view-badge-sm {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: rgba(168, 85, 247, 0.2);
  border: 1px solid rgba(168, 85, 247, 0.4);
  color: #c084fc;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 9px;
  flex-shrink: 0;
}

.view-type-toggle {
  display: flex;
  gap: 4px;
  flex: 1;
}

.type-btn {
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.15s;
}

.type-btn.active {
  background: rgba(168, 85, 247, 0.15);
  border-color: rgba(168, 85, 247, 0.4);
  color: #c084fc;
}

.btn-remove-view {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 1px solid rgba(248, 113, 113, 0.3);
  background: rgba(248, 113, 113, 0.1);
  color: #f87171;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-remove-view:hover {
  background: rgba(248, 113, 113, 0.2);
  border-color: rgba(248, 113, 113, 0.5);
}

.view-body {
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.view-row {
  display: flex;
  gap: 10px;
}

.view-field {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.view-field label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.view-field select {
  height: 28px;
  padding: 0 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #fff;
  font-size: 11px;
  outline: none;
  cursor: pointer;
}

.view-field select:focus {
  border-color: rgba(168, 85, 247, 0.5);
}

.confidence-slider {
  display: flex;
  align-items: center;
  gap: 8px;
}

.confidence-slider input[type="range"] {
  flex: 1;
  height: 4px;
  appearance: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  outline: none;
}

.confidence-slider input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #c084fc;
  cursor: pointer;
  border: 2px solid rgba(20, 22, 28, 0.8);
}

.confidence-val {
  font-size: 11px;
  font-weight: 600;
  font-family: 'SF Mono', monospace;
  min-width: 32px;
  text-align: right;
}

.conf-high { color: #4ade80; }
.conf-mid { color: #fbbf24; }
.conf-low { color: #f87171; }

.view-description {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  padding: 6px 8px;
  background: rgba(168, 85, 247, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(168, 85, 247, 0.1);
}

.views-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 120px;
  color: rgba(255, 255, 255, 0.3);
  font-size: 13px;
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

.weights-table-container::-webkit-scrollbar { width: 6px; }
.weights-table-container::-webkit-scrollbar-track { background: transparent; }
.weights-table-container::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 3px; }

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

.weights-table th.text-right { text-align: right; }

.weights-table tbody tr {
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  transition: background 0.15s;
}

.weights-table tbody tr:hover { background: rgba(255, 255, 255, 0.02); }

.weights-table td {
  padding: 8px;
  color: rgba(255, 255, 255, 0.9);
  vertical-align: middle;
}

.weights-table td.text-right { text-align: right; }

.weights-table .change-pill {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 10px;
}

.change-pill.positive,
.weights-table .change-pill.positive {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
}

.change-pill.negative,
.weights-table .change-pill.negative {
  background: rgba(248, 113, 113, 0.15);
  color: #f87171;
}

.change-pill.neutral,
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

.asset-icon-small {
  width: 20px;
  height: 20px;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 600;
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

/* WEIGHT BARS */
.weights-bars-view {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

.weight-bar-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.weight-bar-info {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 80px;
}

.weight-bar-label {
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.weight-bars-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.weight-bar-row-dual {
  display: flex;
  align-items: center;
  gap: 6px;
}

.bar-label-sm {
  font-size: 8px;
  color: rgba(255, 255, 255, 0.4);
  width: 32px;
  text-align: right;
  flex-shrink: 0;
}

.weight-bar-bg {
  flex: 1;
  height: 10px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 3px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.weight-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
  min-width: 2px;
}

.weight-bar-fill.eq {
  background: rgba(255, 255, 255, 0.2);
}

.weight-bar-fill.bl {
  background: #c084fc;
}

.weight-bar-value {
  width: 45px;
  text-align: right;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
}

/* VIEWS IMPACT */
.views-impact-panel {
  margin-top: 8px;
}

.impact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 10px;
}

.impact-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
}

.impact-card:hover {
  border-color: rgba(168, 85, 247, 0.3);
  background: rgba(255, 255, 255, 0.03);
}

.impact-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.impact-assets {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.impact-metrics {
  display: flex;
  gap: 12px;
  padding: 10px 12px;
}

.impact-metric {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric-label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
}

.metric-value {
  font-size: 12px;
  font-weight: 600;
  font-family: 'SF Mono', monospace;
  color: #fff;
}

/* RISK BARS */
.risk-bars {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.risk-bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.risk-bar-info {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 80px;
}

.risk-bar-label {
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.risk-bar-value {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  min-width: 55px;
  text-align: right;
}

/* METRICS */
.metrics-card {
  height: 100%;
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

/* RESPONSIVE */
@media (max-width: 1400px) {
  .params-grid {
    grid-template-columns: 1fr;
  }
  .main-grid {
    grid-template-columns: 1fr;
  }
  .metrics-grid-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .impact-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .hero-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .params-grid,
  .main-grid,
  .metrics-grid-row {
    grid-template-columns: 1fr;
  }
  .impact-grid {
    grid-template-columns: 1fr;
  }
  .view-row {
    flex-direction: column;
  }
}
</style>
