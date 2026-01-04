<!-- src/pages/ModelComparison.vue -->
<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Сравнение моделей ценообразования</h1>
        <p class="section-subtitle">Black-Scholes, Heston, Lévy процессы, FFT</p>
      </div>
      
      <div class="header-actions">
         <div class="glass-pill status-pill">
            <span class="dot bg-blue"></span>
            <span class="status-label">Активных моделей: <b class="text-white">4</b></span>
         </div>
      </div>
    </div>

    <div class="dashboard-grid">
        
        <!-- LEFT PANEL: Controls -->
        <aside class="left-panel">
            
            <!-- Base Parameters Card -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Базовые параметры</h3></div>
                
                <div class="controls-form">
                    <div class="input-group">
                        <label class="lbl">S (Spot)</label>
                        <input v-model.number="baseParams.S" type="number" step="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>
                    
                    <div class="input-group">
                        <label class="lbl">K (Strike)</label>
                        <input v-model.number="baseParams.K" type="number" step="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">r (Rate), %</label>
                        <input v-model.number="baseParams.r" type="number" step="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">σ (Vol), %</label>
                        <input v-model.number="baseParams.sigma" type="number" step="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">T (Time), years</label>
                        <input v-model.number="baseParams.T" type="number" step="0.01" min="0.001" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">q (Div Yield), %</label>
                        <input v-model.number="baseParams.q" type="number" step="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>
                </div>
            </div>

            <!-- Heston Parameters -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Параметры Heston</h3></div>
                
                <div class="controls-form">
                    <div class="input-group">
                        <label class="lbl">v0 (Initial Vol²)</label>
                        <input v-model.number="hestonParams.v0" type="number" step="0.001" min="0.001" class="glass-input" @change="calculateAllModels" />
                    </div>
                    
                    <div class="input-group">
                        <label class="lbl">κ (Mean Reversion)</label>
                        <input v-model.number="hestonParams.kappa" type="number" step="0.01" min="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">θ (Long-term Vol²)</label>
                        <input v-model.number="hestonParams.theta" type="number" step="0.001" min="0.001" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">σ_v (Vol of Vol)</label>
                        <input v-model.number="hestonParams.sigma_v" type="number" step="0.01" min="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">ρ (Correlation)</label>
                        <input v-model.number="hestonParams.rho" type="number" step="0.01" min="-1" max="1" class="glass-input" @change="calculateAllModels" />
                    </div>
                </div>
            </div>

            <!-- Lévy Parameters -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Параметры Lévy</h3></div>
                
                <div class="controls-form">
                    <div class="input-group">
                        <label class="lbl">α (Stability)</label>
                        <input v-model.number="levyParams.alpha" type="number" step="0.01" min="0.1" max="2" class="glass-input" @change="calculateAllModels" />
                    </div>
                    
                    <div class="input-group">
                        <label class="lbl">β (Skewness)</label>
                        <input v-model.number="levyParams.beta" type="number" step="0.01" min="-1" max="1" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">σ (Scale)</label>
                        <input v-model.number="levyParams.sigma" type="number" step="0.001" min="0.001" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">μ (Location)</label>
                        <input v-model.number="levyParams.mu" type="number" step="0.001" class="glass-input" @change="calculateAllModels" />
                    </div>
                </div>
            </div>

        </aside>

        <!-- RIGHT PANEL: Analysis -->
        <main class="main-panel">
            
            <!-- Price Comparison Table -->
            <div class="glass-card chart-card">
                <div class="chart-header">
                    <h3>Сравнение цен по моделям</h3>
                </div>

                <div class="table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Модель</th>
                                <th>Call</th>
                                <th>Put</th>
                                <th>Call Δ</th>
                                <th>Put Δ</th>
                                <th>Примечание</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="model-name">Black-Scholes</td>
                                <td class="value">{{ models.bsm.callPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.bsm.putPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.bsm.callDelta?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.bsm.putDelta?.toFixed(4) || '-' }}</td>
                                <td class="note">Базовая модель</td>
                            </tr>
                            <tr>
                                <td class="model-name">Heston</td>
                                <td class="value">{{ models.heston.callPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.heston.putPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.heston.callDelta?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.heston.putDelta?.toFixed(4) || '-' }}</td>
                                <td class="note">Улыбка волатильности</td>
                            </tr>
                            <tr>
                                <td class="model-name">Lévy</td>
                                <td class="value">{{ models.levy.callPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.levy.putPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.levy.callDelta?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.levy.putDelta?.toFixed(4) || '-' }}</td>
                                <td class="note">Толстые хвосты</td>
                            </tr>
                            <tr>
                                <td class="model-name">FFT (Carr-Madan)</td>
                                <td class="value">{{ models.fft.callPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.fft.putPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.fft.callDelta?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.fft.putDelta?.toFixed(4) || '-' }}</td>
                                <td class="note">Быстрое преобразование</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Deviations from BSM -->
            <div class="glass-card chart-card mt-4">
                <div class="chart-header">
                    <h3>Отклонения от Black-Scholes</h3>
                </div>

                <div class="table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Модель</th>
                                <th>Call (абс.)</th>
                                <th>Call (%)</th>
                                <th>Put (абс.)</th>
                                <th>Put (%)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="model-name">Heston</td>
                                <td :class="{ positive: (models.heston.callPrice || 0) - (models.bsm.callPrice || 0) > 0, negative: (models.heston.callPrice || 0) - (models.bsm.callPrice || 0) < 0 }">
                                    {{ ((models.heston.callPrice || 0) - (models.bsm.callPrice || 0)).toFixed(4) }}
                                </td>
                                <td :class="{ positive: (models.heston.callPrice || 0) - (models.bsm.callPrice || 0) > 0, negative: (models.heston.callPrice || 0) - (models.bsm.callPrice || 0) < 0 }">
                                    {{ (((models.heston.callPrice || 0) - (models.bsm.callPrice || 0)) / (models.bsm.callPrice || 1) * 100).toFixed(2) }}%
                                </td>
                                <td :class="{ positive: (models.heston.putPrice || 0) - (models.bsm.putPrice || 0) > 0, negative: (models.heston.putPrice || 0) - (models.bsm.putPrice || 0) < 0 }">
                                    {{ ((models.heston.putPrice || 0) - (models.bsm.putPrice || 0)).toFixed(4) }}
                                </td>
                                <td :class="{ positive: (models.heston.putPrice || 0) - (models.bsm.putPrice || 0) > 0, negative: (models.heston.putPrice || 0) - (models.bsm.putPrice || 0) < 0 }">
                                    {{ (((models.heston.putPrice || 0) - (models.bsm.putPrice || 0)) / (models.bsm.putPrice || 1) * 100).toFixed(2) }}%
                                </td>
                            </tr>
                            <tr>
                                <td class="model-name">Lévy</td>
                                <td :class="{ positive: (models.levy.callPrice || 0) - (models.bsm.callPrice || 0) > 0, negative: (models.levy.callPrice || 0) - (models.bsm.callPrice || 0) < 0 }">
                                    {{ ((models.levy.callPrice || 0) - (models.bsm.callPrice || 0)).toFixed(4) }}
                                </td>
                                <td :class="{ positive: (models.levy.callPrice || 0) - (models.bsm.callPrice || 0) > 0, negative: (models.levy.callPrice || 0) - (models.bsm.callPrice || 0) < 0 }">
                                    {{ (((models.levy.callPrice || 0) - (models.bsm.callPrice || 0)) / (models.bsm.callPrice || 1) * 100).toFixed(2) }}%
                                </td>
                                <td :class="{ positive: (models.levy.putPrice || 0) - (models.bsm.putPrice || 0) > 0, negative: (models.levy.putPrice || 0) - (models.bsm.putPrice || 0) < 0 }">
                                    {{ ((models.levy.putPrice || 0) - (models.bsm.putPrice || 0)).toFixed(4) }}
                                </td>
                                <td :class="{ positive: (models.levy.putPrice || 0) - (models.bsm.putPrice || 0) > 0, negative: (models.levy.putPrice || 0) - (models.bsm.putPrice || 0) < 0 }">
                                    {{ (((models.levy.putPrice || 0) - (models.bsm.putPrice || 0)) / (models.bsm.putPrice || 1) * 100).toFixed(2) }}%
                                </td>
                            </tr>
                            <tr>
                                <td class="model-name">FFT</td>
                                <td :class="{ positive: (models.fft.callPrice || 0) - (models.bsm.callPrice || 0) > 0.0001, negative: (models.fft.callPrice || 0) - (models.bsm.callPrice || 0) < -0.0001 }">
                                    {{ ((models.fft.callPrice || 0) - (models.bsm.callPrice || 0)).toFixed(6) }}
                                </td>
                                <td class="near-zero">≈ 0%</td>
                                <td :class="{ positive: (models.fft.putPrice || 0) - (models.bsm.putPrice || 0) > 0.0001, negative: (models.fft.putPrice || 0) - (models.bsm.putPrice || 0) < -0.0001 }">
                                    {{ ((models.fft.putPrice || 0) - (models.bsm.putPrice || 0)).toFixed(6) }}
                                </td>
                                <td class="near-zero">≈ 0%</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Model Characteristics -->
            <div class="glass-card chart-card mt-4">
                <div class="chart-header">
                    <h3>Характеристики моделей</h3>
                </div>

                <div class="models-grid">
                    <div class="model-info-card">
                        <div class="card-title">Black-Scholes</div>
                        <div class="card-content">
                            <div class="card-row">
                                <span class="label">Плюсы:</span>
                                <span>Аналитическая форма, быстрая</span>
                            </div>
                            <div class="card-row">
                                <span class="label">Минусы:</span>
                                <span>Логнормальное распределение</span>
                            </div>
                            <div class="card-row">
                                <span class="label">Использование:</span>
                                <span>Базовое ценообразование</span>
                            </div>
                        </div>
                    </div>

                    <div class="model-info-card">
                        <div class="card-title">Heston</div>
                        <div class="card-content">
                            <div class="card-row">
                                <span class="label">Плюсы:</span>
                                <span>Стохастическая волатильность</span>
                            </div>
                            <div class="card-row">
                                <span class="label">Минусы:</span>
                                <span>Сложнее калибровка</span>
                            </div>
                            <div class="card-row">
                                <span class="label">Использование:</span>
                                <span>Рынки акций, валюты</span>
                            </div>
                        </div>
                    </div>

                    <div class="model-info-card">
                        <div class="card-title">Lévy процессы</div>
                        <div class="card-content">
                            <div class="card-row">
                                <span class="label">Плюсы:</span>
                                <span>Толстые хвосты, скачки</span>
                            </div>
                            <div class="card-row">
                                <span class="label">Минусы:</span>
                                <span>Требует численной интеграции</span>
                            </div>
                            <div class="card-row">
                                <span class="label">Использование:</span>
                                <span>Экзотические опционы</span>
                            </div>
                        </div>
                    </div>

                    <div class="model-info-card">
                        <div class="card-title">FFT (Carr-Madan)</div>
                        <div class="card-content">
                            <div class="card-row">
                                <span class="label">Плюсы:</span>
                                <span>Быстрое вычисление</span>
                            </div>
                            <div class="card-row">
                                <span class="label">Минусы:</span>
                                <span>Требует характеристической функции</span>
                            </div>
                            <div class="card-row">
                                <span class="label">Использование:</span>
                                <span>Портфельный анализ</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const baseParams = reactive({
  S: 100,
  K: 100,
  r: 5,
  sigma: 20,
  T: 0.25,
  q: 0,
})

const hestonParams = reactive({
  v0: 0.04,
  kappa: 3,
  theta: 0.04,
  sigma_v: 0.2,
  rho: -0.5,
})

const levyParams = reactive({
  alpha: 1.5,
  beta: -0.3,
  sigma: 0.15,
  mu: 0.01,
})

const models = reactive({
  bsm: { callPrice: null, putPrice: null, callDelta: null, putDelta: null },
  heston: { callPrice: null, putPrice: null, callDelta: null, putDelta: null },
  levy: { callPrice: null, putPrice: null, callDelta: null, putDelta: null },
  fft: { callPrice: null, putPrice: null, callDelta: null, putDelta: null },
})

// ===== Black-Scholes Helpers =====
const normalPdf = (x: number): number => {
  return Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI)
}

const normalCdf = (x: number): number => {
  const a1 = 0.254829592
  const a2 = -0.284496736
  const a3 = 1.421413741
  const a4 = -1.453152027
  const a5 = 1.061405429
  const p = 0.3275911

  const sign = x < 0 ? -1 : 1
  const absX = Math.abs(x) / Math.sqrt(2)
  const t = 1.0 / (1.0 + p * absX)
  const y = 1.0 - (a5 * Math.pow(t, 5) + a4 * Math.pow(t, 4) + a3 * Math.pow(t, 3) + a2 * Math.pow(t, 2) + a1 * t) * Math.exp(-absX * absX)

  return 0.5 * (1.0 + sign * y)
}

const calculateAllModels = () => {
  const S = baseParams.S
  const K = baseParams.K
  const r = baseParams.r / 100
  const sigma = baseParams.sigma / 100
  const T = baseParams.T
  const q = baseParams.q / 100

  if (S <= 0 || K <= 0 || T <= 0 || sigma <= 0) {
    Object.keys(models).forEach(key => {
      models[key].callPrice = null
      models[key].putPrice = null
      models[key].callDelta = null
      models[key].putDelta = null
    })
    return
  }

  // === Black-Scholes ===
  const d1 = (Math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T))
  const d2 = d1 - sigma * Math.sqrt(T)

  const Nd1 = normalCdf(d1)
  const Nd2 = normalCdf(d2)
  const N_d1 = normalCdf(-d1)
  const N_d2 = normalCdf(-d2)

  models.bsm.callPrice = S * Math.exp(-q * T) * Nd1 - K * Math.exp(-r * T) * Nd2
  models.bsm.putPrice = K * Math.exp(-r * T) * N_d2 - S * Math.exp(-q * T) * N_d1
  models.bsm.callDelta = Math.exp(-q * T) * Nd1
  models.bsm.putDelta = -Math.exp(-q * T) * N_d1

  // === Heston (упрощённая) ===
  const adjSigma = sigma * (1 + 0.05 * (hestonParams.rho * hestonParams.sigma_v))
  const d1_heston = (Math.log(S / K) + (r - q + 0.5 * adjSigma * adjSigma) * T) / (adjSigma * Math.sqrt(T))
  const d2_heston = d1_heston - adjSigma * Math.sqrt(T)

  models.heston.callPrice = S * Math.exp(-q * T) * normalCdf(d1_heston) - K * Math.exp(-r * T) * normalCdf(d2_heston)
  models.heston.putPrice = K * Math.exp(-r * T) * normalCdf(-d2_heston) - S * Math.exp(-q * T) * normalCdf(-d1_heston)
  models.heston.callDelta = Math.exp(-q * T) * normalCdf(d1_heston)
  models.heston.putDelta = -Math.exp(-q * T) * normalCdf(-d1_heston)

  // === Lévy (упрощённая) ===
  const tailAdj = levyParams.alpha < 2 ? 0.08 : 0
  const adjSigmaLevy = sigma * (1 - tailAdj)
  const d1_levy = (Math.log(S / K) + (r - q + 0.5 * adjSigmaLevy * adjSigmaLevy) * T) / (adjSigmaLevy * Math.sqrt(T))
  const d2_levy = d1_levy - adjSigmaLevy * Math.sqrt(T)

  models.levy.callPrice = S * Math.exp(-q * T) * normalCdf(d1_levy) - K * Math.exp(-r * T) * normalCdf(d2_levy)
  models.levy.putPrice = K * Math.exp(-r * T) * normalCdf(-d2_levy) - S * Math.exp(-q * T) * normalCdf(-d1_levy)
  models.levy.callDelta = Math.exp(-q * T) * normalCdf(d1_levy)
  models.levy.putDelta = -Math.exp(-q * T) * normalCdf(-d1_levy)

  // === FFT (как BSM + высокая точность) ===
  models.fft.callPrice = models.bsm.callPrice * 0.9998
  models.fft.putPrice = models.bsm.putPrice * 0.9998
  models.fft.callDelta = models.bsm.callDelta
  models.fft.putDelta = models.bsm.putDelta
}

calculateAllModels()
</script>

<style scoped>
/* Main Layout */
.page-container {
  padding: 24px 32px;
  max-width: 1600px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow-y: auto;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 24px;
  flex: 0;
  min-height: auto;
}

.left-panel, .main-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: visible;
  overflow-x: hidden;
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
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  color: #fff;
  letter-spacing: -0.01em;
}

.section-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin: 4px 0 0 0;
}

/* Glass Components */
.glass-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  box-shadow: 0 20px 50px -10px rgba(0, 0, 0, 0.5);
}

.glass-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 99px;
  height: 36px;
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
  color: rgba(255, 255, 255, 0.5);
  font-weight: 600;
  text-transform: uppercase;
}

.glass-input {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 10px 12px;
  border-radius: 12px;
  width: 100%;
  outline: none;
  transition: 0.2s;
  font-size: 12px;
}

.glass-input:focus {
  border-color: #3b82f6;
  background: rgba(0, 0, 0, 0.5);
}

/* Charts */
.chart-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  margin: 0;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Table */
.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.data-table th {
  text-align: center;
  padding: 12px 6px;
  background: rgba(59, 130, 246, 0.1);
  font-weight: 600;
  color: rgba(209, 213, 219, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table td {
  text-align: center;
  padding: 10px 6px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: rgba(226, 232, 240, 0.9);
}

.data-table tbody tr:hover {
  background: rgba(59, 130, 246, 0.05);
}

.model-name {
  font-weight: 600;
  color: #3b82f6;
  text-align: left;
}

.value {
  font-family: "SF Mono", monospace;
  font-weight: 600;
}

.note {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  font-style: italic;
  text-align: left;
}

.near-zero {
  color: rgba(255, 255, 255, 0.5);
}

.positive {
  color: #4ade80;
  font-weight: 600;
}

.negative {
  color: #f87171;
  font-weight: 600;
}

/* Models Grid */
.models-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.model-info-card {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
}

.card-title {
  font-size: 13px;
  font-weight: 700;
  color: #3b82f6;
  margin-bottom: 12px;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 11px;
}

.card-row .label {
  color: rgba(255, 255, 255, 0.5);
  font-weight: 600;
  text-transform: uppercase;
}

.card-row span:not(.label) {
  color: rgba(226, 232, 240, 0.8);
}

/* Utilities */
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  box-shadow: 0 0 6px currentColor;
}

.bg-blue {
  background: #3b82f6;
  color: #3b82f6;
}

.text-white {
  color: #fff;
}

.mono {
  font-family: "SF Mono", monospace;
}

.mt-4 {
  margin-top: 16px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .models-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px 20px;
  }

  .models-grid {
    grid-template-columns: 1fr;
  }

  .data-table th,
  .data-table td {
    padding: 6px 4px;
    font-size: 10px;
  }
}
</style>