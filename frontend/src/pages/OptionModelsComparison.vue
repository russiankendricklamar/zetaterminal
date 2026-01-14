<!-- src/pages/ModelComparison.vue -->
<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Сравнение моделей ценообразования</h1>
        <p class="section-subtitle">Black-Scholes, Heston, Merton, Bates, SABR, Variance Gamma</p>
      </div>
      
      <div class="header-actions">
         <div class="glass-pill status-pill">
            <span class="dot bg-blue"></span>
            <span class="status-label">Активных моделей: <b class="text-white">6</b></span>
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
                        <label class="lbl">T (Time), лет</label>
                        <input v-model.number="baseParams.T" type="number" step="0.01" min="0.001" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">q (Див. доходность), %</label>
                        <input v-model.number="baseParams.q" type="number" step="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>
                </div>
            </div>

            <!-- Heston Parameters -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Параметры Heston</h3></div>
                
                <div class="controls-form">
                    <div class="input-group">
                        <label class="lbl">v0 (Начальная Vol²)</label>
                        <input v-model.number="hestonParams.v0" type="number" step="0.001" min="0.001" class="glass-input" @change="calculateAllModels" />
                    </div>
                    
                    <div class="input-group">
                        <label class="lbl">κ (Возврат к среднему)</label>
                        <input v-model.number="hestonParams.kappa" type="number" step="0.01" min="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">θ (Долгосрочная Vol²)</label>
                        <input v-model.number="hestonParams.theta" type="number" step="0.001" min="0.001" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">σ_v (Волатильность волатильности)</label>
                        <input v-model.number="hestonParams.sigma_v" type="number" step="0.01" min="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">ρ (Корреляция)</label>
                        <input v-model.number="hestonParams.rho" type="number" step="0.01" min="-1" max="1" class="glass-input" @change="calculateAllModels" />
                    </div>
                </div>
            </div>

            <!-- Merton Parameters -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Параметры Merton</h3></div>
                
                <div class="controls-form">
                    <div class="input-group">
                        <label class="lbl">λ (Интенсивность скачков)</label>
                        <input v-model.number="mertonParams.lambda" type="number" step="0.01" min="0" class="glass-input" @change="calculateAllModels" />
                    </div>
                    
                    <div class="input-group">
                        <label class="lbl">μ_j (Среднее скачка)</label>
                        <input v-model.number="mertonParams.mu_j" type="number" step="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">σ_j (Волатильность скачка)</label>
                        <input v-model.number="mertonParams.sigma_j" type="number" step="0.01" min="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>
                </div>
            </div>

            <!-- Bates Parameters -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Параметры Bates</h3></div>
                
                <div class="controls-form">
                    <div class="input-group">
                        <label class="lbl">λ (Интенсивность скачков)</label>
                        <input v-model.number="batesParams.lambda" type="number" step="0.01" min="0" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">μ_j (Среднее скачка)</label>
                        <input v-model.number="batesParams.mu_j" type="number" step="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">σ_j (Волатильность скачка)</label>
                        <input v-model.number="batesParams.sigma_j" type="number" step="0.01" min="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>
                </div>
            </div>

            <!-- SABR Parameters -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Параметры SABR</h3></div>
                
                <div class="controls-form">
                    <div class="input-group">
                        <label class="lbl">α (Начальная волатильность)</label>
                        <input v-model.number="sabrParams.alpha" type="number" step="0.001" min="0.001" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">β (Эластичность)</label>
                        <input v-model.number="sabrParams.beta" type="number" step="0.01" min="0" max="1" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">ρ (Корреляция)</label>
                        <input v-model.number="sabrParams.rho" type="number" step="0.01" min="-1" max="1" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">ν (Волатильность волатильности)</label>
                        <input v-model.number="sabrParams.nu" type="number" step="0.01" min="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>
                </div>
            </div>

            <!-- Variance Gamma Parameters -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Параметры Variance Gamma</h3></div>
                
                <div class="controls-form">
                    <div class="input-group">
                        <label class="lbl">θ (Дрифт)</label>
                        <input v-model.number="vgParams.theta" type="number" step="0.01" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">σ (Волатильность)</label>
                        <input v-model.number="vgParams.sigma" type="number" step="0.001" min="0.001" class="glass-input" @change="calculateAllModels" />
                    </div>

                    <div class="input-group">
                        <label class="lbl">ν (Параметр формы)</label>
                        <input v-model.number="vgParams.nu" type="number" step="0.001" min="0.001" class="glass-input" @change="calculateAllModels" />
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
                                <td class="note">Стохастическая волатильность</td>
                            </tr>
                            <tr>
                                <td class="model-name">Merton</td>
                                <td class="value">{{ models.merton.callPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.merton.putPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.merton.callDelta?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.merton.putDelta?.toFixed(4) || '-' }}</td>
                                <td class="note">Модель скачков</td>
                            </tr>
                            <tr>
                                <td class="model-name">Bates</td>
                                <td class="value">{{ models.bates.callPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.bates.putPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.bates.callDelta?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.bates.putDelta?.toFixed(4) || '-' }}</td>
                                <td class="note">Heston + Скачки</td>
                            </tr>
                            <tr>
                                <td class="model-name">SABR</td>
                                <td class="value">{{ models.sabr.callPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.sabr.putPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.sabr.callDelta?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.sabr.putDelta?.toFixed(4) || '-' }}</td>
                                <td class="note">Процентные опционы</td>
                            </tr>
                            <tr>
                                <td class="model-name">Variance Gamma</td>
                                <td class="value">{{ models.vg.callPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.vg.putPrice?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.vg.callDelta?.toFixed(4) || '-' }}</td>
                                <td class="value">{{ models.vg.putDelta?.toFixed(4) || '-' }}</td>
                                <td class="note">Процесс Леви</td>
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
                                <td class="model-name">Merton</td>
                                <td :class="{ positive: (models.merton.callPrice || 0) - (models.bsm.callPrice || 0) > 0, negative: (models.merton.callPrice || 0) - (models.bsm.callPrice || 0) < 0 }">
                                    {{ ((models.merton.callPrice || 0) - (models.bsm.callPrice || 0)).toFixed(4) }}
                                </td>
                                <td :class="{ positive: (models.merton.callPrice || 0) - (models.bsm.callPrice || 0) > 0, negative: (models.merton.callPrice || 0) - (models.bsm.callPrice || 0) < 0 }">
                                    {{ (((models.merton.callPrice || 0) - (models.bsm.callPrice || 0)) / (models.bsm.callPrice || 1) * 100).toFixed(2) }}%
                                </td>
                                <td :class="{ positive: (models.merton.putPrice || 0) - (models.bsm.putPrice || 0) > 0, negative: (models.merton.putPrice || 0) - (models.bsm.putPrice || 0) < 0 }">
                                    {{ ((models.merton.putPrice || 0) - (models.bsm.putPrice || 0)).toFixed(4) }}
                                </td>
                                <td :class="{ positive: (models.merton.putPrice || 0) - (models.bsm.putPrice || 0) > 0, negative: (models.merton.putPrice || 0) - (models.bsm.putPrice || 0) < 0 }">
                                    {{ (((models.merton.putPrice || 0) - (models.bsm.putPrice || 0)) / (models.bsm.putPrice || 1) * 100).toFixed(2) }}%
                                </td>
                            </tr>
                            <tr>
                                <td class="model-name">Bates</td>
                                <td :class="{ positive: (models.bates.callPrice || 0) - (models.bsm.callPrice || 0) > 0, negative: (models.bates.callPrice || 0) - (models.bsm.callPrice || 0) < 0 }">
                                    {{ ((models.bates.callPrice || 0) - (models.bsm.callPrice || 0)).toFixed(4) }}
                                </td>
                                <td :class="{ positive: (models.bates.callPrice || 0) - (models.bsm.callPrice || 0) > 0, negative: (models.bates.callPrice || 0) - (models.bsm.callPrice || 0) < 0 }">
                                    {{ (((models.bates.callPrice || 0) - (models.bsm.callPrice || 0)) / (models.bsm.callPrice || 1) * 100).toFixed(2) }}%
                                </td>
                                <td :class="{ positive: (models.bates.putPrice || 0) - (models.bsm.putPrice || 0) > 0, negative: (models.bates.putPrice || 0) - (models.bsm.putPrice || 0) < 0 }">
                                    {{ ((models.bates.putPrice || 0) - (models.bsm.putPrice || 0)).toFixed(4) }}
                                </td>
                                <td :class="{ positive: (models.bates.putPrice || 0) - (models.bsm.putPrice || 0) > 0, negative: (models.bates.putPrice || 0) - (models.bsm.putPrice || 0) < 0 }">
                                    {{ (((models.bates.putPrice || 0) - (models.bsm.putPrice || 0)) / (models.bsm.putPrice || 1) * 100).toFixed(2) }}%
                                </td>
                            </tr>
                            <tr>
                                <td class="model-name">SABR</td>
                                <td :class="{ positive: (models.sabr.callPrice || 0) - (models.bsm.callPrice || 0) > 0, negative: (models.sabr.callPrice || 0) - (models.bsm.callPrice || 0) < 0 }">
                                    {{ ((models.sabr.callPrice || 0) - (models.bsm.callPrice || 0)).toFixed(4) }}
                                </td>
                                <td :class="{ positive: (models.sabr.callPrice || 0) - (models.bsm.callPrice || 0) > 0, negative: (models.sabr.callPrice || 0) - (models.bsm.callPrice || 0) < 0 }">
                                    {{ (((models.sabr.callPrice || 0) - (models.bsm.callPrice || 0)) / (models.bsm.callPrice || 1) * 100).toFixed(2) }}%
                                </td>
                                <td :class="{ positive: (models.sabr.putPrice || 0) - (models.bsm.putPrice || 0) > 0, negative: (models.sabr.putPrice || 0) - (models.bsm.putPrice || 0) < 0 }">
                                    {{ ((models.sabr.putPrice || 0) - (models.bsm.putPrice || 0)).toFixed(4) }}
                                </td>
                                <td :class="{ positive: (models.sabr.putPrice || 0) - (models.bsm.putPrice || 0) > 0, negative: (models.sabr.putPrice || 0) - (models.bsm.putPrice || 0) < 0 }">
                                    {{ (((models.sabr.putPrice || 0) - (models.bsm.putPrice || 0)) / (models.bsm.putPrice || 1) * 100).toFixed(2) }}%
                                </td>
                            </tr>
                            <tr>
                                <td class="model-name">Variance Gamma</td>
                                <td :class="{ positive: (models.vg.callPrice || 0) - (models.bsm.callPrice || 0) > 0, negative: (models.vg.callPrice || 0) - (models.bsm.callPrice || 0) < 0 }">
                                    {{ ((models.vg.callPrice || 0) - (models.bsm.callPrice || 0)).toFixed(4) }}
                                </td>
                                <td :class="{ positive: (models.vg.callPrice || 0) - (models.bsm.callPrice || 0) > 0, negative: (models.vg.callPrice || 0) - (models.bsm.callPrice || 0) < 0 }">
                                    {{ (((models.vg.callPrice || 0) - (models.bsm.callPrice || 0)) / (models.bsm.callPrice || 1) * 100).toFixed(2) }}%
                                </td>
                                <td :class="{ positive: (models.vg.putPrice || 0) - (models.bsm.putPrice || 0) > 0, negative: (models.vg.putPrice || 0) - (models.bsm.putPrice || 0) < 0 }">
                                    {{ ((models.vg.putPrice || 0) - (models.bsm.putPrice || 0)).toFixed(4) }}
                                </td>
                                <td :class="{ positive: (models.vg.putPrice || 0) - (models.bsm.putPrice || 0) > 0, negative: (models.vg.putPrice || 0) - (models.bsm.putPrice || 0) < 0 }">
                                    {{ (((models.vg.putPrice || 0) - (models.bsm.putPrice || 0)) / (models.bsm.putPrice || 1) * 100).toFixed(2) }}%
                                </td>
                            </tr>
                        </tbody>
                    </table>
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

const mertonParams = reactive({
  lambda: 0.1,
  mu_j: -0.05,
  sigma_j: 0.15,
})

const batesParams = reactive({
  lambda: 0.1,
  mu_j: -0.05,
  sigma_j: 0.15,
})

const sabrParams = reactive({
  alpha: 0.2,
  beta: 0.5,
  rho: -0.3,
  nu: 0.4,
})

const vgParams = reactive({
  theta: -0.1,
  sigma: 0.2,
  nu: 0.3,
})

const models = reactive({
  bsm: { callPrice: null, putPrice: null, callDelta: null, putDelta: null },
  heston: { callPrice: null, putPrice: null, callDelta: null, putDelta: null },
  merton: { callPrice: null, putPrice: null, callDelta: null, putDelta: null },
  bates: { callPrice: null, putPrice: null, callDelta: null, putDelta: null },
  sabr: { callPrice: null, putPrice: null, callDelta: null, putDelta: null },
  vg: { callPrice: null, putPrice: null, callDelta: null, putDelta: null },
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

  // === Merton (Jump Diffusion) ===
  const jumpAdj = mertonParams.lambda * (Math.exp(mertonParams.mu_j + 0.5 * mertonParams.sigma_j * mertonParams.sigma_j) - 1)
  const adjSigmaMerton = Math.sqrt(sigma * sigma + mertonParams.lambda * (mertonParams.mu_j * mertonParams.mu_j + mertonParams.sigma_j * mertonParams.sigma_j))
  const d1_merton = (Math.log(S / K) + (r - q - jumpAdj + 0.5 * adjSigmaMerton * adjSigmaMerton) * T) / (adjSigmaMerton * Math.sqrt(T))
  const d2_merton = d1_merton - adjSigmaMerton * Math.sqrt(T)

  models.merton.callPrice = S * Math.exp(-q * T) * normalCdf(d1_merton) - K * Math.exp(-r * T) * normalCdf(d2_merton)
  models.merton.putPrice = K * Math.exp(-r * T) * normalCdf(-d2_merton) - S * Math.exp(-q * T) * normalCdf(-d1_merton)
  models.merton.callDelta = Math.exp(-q * T) * normalCdf(d1_merton)
  models.merton.putDelta = -Math.exp(-q * T) * normalCdf(-d1_merton)

  // === Bates (Heston + Jumps) ===
  const batesJumpAdj = batesParams.lambda * (Math.exp(batesParams.mu_j + 0.5 * batesParams.sigma_j * batesParams.sigma_j) - 1)
  const adjSigmaBates = Math.sqrt(adjSigma * adjSigma + batesParams.lambda * (batesParams.mu_j * batesParams.mu_j + batesParams.sigma_j * batesParams.sigma_j))
  const d1_bates = (Math.log(S / K) + (r - q - batesJumpAdj + 0.5 * adjSigmaBates * adjSigmaBates) * T) / (adjSigmaBates * Math.sqrt(T))
  const d2_bates = d1_bates - adjSigmaBates * Math.sqrt(T)

  models.bates.callPrice = S * Math.exp(-q * T) * normalCdf(d1_bates) - K * Math.exp(-r * T) * normalCdf(d2_bates)
  models.bates.putPrice = K * Math.exp(-r * T) * normalCdf(-d2_bates) - S * Math.exp(-q * T) * normalCdf(-d1_bates)
  models.bates.callDelta = Math.exp(-q * T) * normalCdf(d1_bates)
  models.bates.putDelta = -Math.exp(-q * T) * normalCdf(-d1_bates)

  // === SABR (Stochastic Alpha Beta Rho) ===
  const sabrVol = sabrParams.alpha * Math.pow(S / K, sabrParams.beta) * (1 + sabrParams.rho * sabrParams.nu * Math.log(S / K))
  const d1_sabr = (Math.log(S / K) + (r - q + 0.5 * sabrVol * sabrVol) * T) / (sabrVol * Math.sqrt(T))
  const d2_sabr = d1_sabr - sabrVol * Math.sqrt(T)

  models.sabr.callPrice = S * Math.exp(-q * T) * normalCdf(d1_sabr) - K * Math.exp(-r * T) * normalCdf(d2_sabr)
  models.sabr.putPrice = K * Math.exp(-r * T) * normalCdf(-d2_sabr) - S * Math.exp(-q * T) * normalCdf(-d1_sabr)
  models.sabr.callDelta = Math.exp(-q * T) * normalCdf(d1_sabr)
  models.sabr.putDelta = -Math.exp(-q * T) * normalCdf(-d1_sabr)

  // === Variance Gamma ===
  const vgAdj = vgParams.theta + 0.5 * vgParams.sigma * vgParams.sigma
  const adjSigmaVG = Math.sqrt(sigma * sigma + vgParams.sigma * vgParams.sigma / vgParams.nu)
  const d1_vg = (Math.log(S / K) + (r - q + vgAdj) * T) / (adjSigmaVG * Math.sqrt(T))
  const d2_vg = d1_vg - adjSigmaVG * Math.sqrt(T)

  models.vg.callPrice = S * Math.exp(-q * T) * normalCdf(d1_vg) - K * Math.exp(-r * T) * normalCdf(d2_vg)
  models.vg.putPrice = K * Math.exp(-r * T) * normalCdf(-d2_vg) - S * Math.exp(-q * T) * normalCdf(-d1_vg)
  models.vg.callDelta = Math.exp(-q * T) * normalCdf(d1_vg)
  models.vg.putDelta = -Math.exp(-q * T) * normalCdf(-d1_vg)
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
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px 20px;
  }

  .data-table th,
  .data-table td {
    padding: 6px 4px;
    font-size: 10px;
  }
}
</style>