<!-- src/pages/ModelComparison.vue -->
<template>
  <div class="page-container custom-scroll">
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">
          Сравнение моделей ценообразования
        </h1>
        <p class="section-subtitle">
          Black-Scholes, Heston, Merton, Bates, SABR, Variance Gamma
        </p>
      </div>
      
      <div class="header-actions">
        <div class="glass-pill status-pill">
          <span class="dot bg-blue" />
          <span class="status-label">Активных моделей: <b class="text-white">6</b></span>
        </div>
      </div>
    </div>

    <div class="dashboard-grid">
      <!-- LEFT PANEL: Controls -->
      <aside class="left-panel">
        <!-- Base Parameters Card -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Базовые параметры</h3>
          </div>
                
          <div class="controls-form">
            <div class="input-group">
              <label class="lbl">S (Spot)</label>
              <input
                v-model.number="baseParams.S"
                type="number"
                step="0.01"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>
                    
            <div class="input-group">
              <label class="lbl">K (Strike)</label>
              <input
                v-model.number="baseParams.K"
                type="number"
                step="0.01"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">r (Rate), %</label>
              <input
                v-model.number="baseParams.r"
                type="number"
                step="0.01"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">σ (Vol), %</label>
              <input
                v-model.number="baseParams.sigma"
                type="number"
                step="0.01"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">T (Time), лет</label>
              <input
                v-model.number="baseParams.T"
                type="number"
                step="0.01"
                min="0.001"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">q (Див. доходность), %</label>
              <input
                v-model.number="baseParams.q"
                type="number"
                step="0.01"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>
          </div>
        </div>

        <!-- Heston Parameters -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Параметры Heston</h3>
          </div>
                
          <div class="controls-form">
            <div class="input-group">
              <label class="lbl">v0 (Начальная Vol²)</label>
              <input
                v-model.number="hestonParams.v0"
                type="number"
                step="0.001"
                min="0.001"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>
                    
            <div class="input-group">
              <label class="lbl">κ (Возврат к среднему)</label>
              <input
                v-model.number="hestonParams.kappa"
                type="number"
                step="0.01"
                min="0.01"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">θ (Долгосрочная Vol²)</label>
              <input
                v-model.number="hestonParams.theta"
                type="number"
                step="0.001"
                min="0.001"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">σ_v (Волатильность волатильности)</label>
              <input
                v-model.number="hestonParams.sigma_v"
                type="number"
                step="0.01"
                min="0.01"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">ρ (Корреляция)</label>
              <input
                v-model.number="hestonParams.rho"
                type="number"
                step="0.01"
                min="-1"
                max="1"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>
          </div>
        </div>

        <!-- Merton Parameters -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Параметры Merton</h3>
          </div>
                
          <div class="controls-form">
            <div class="input-group">
              <label class="lbl">λ (Интенсивность скачков)</label>
              <input
                v-model.number="mertonParams.lambda"
                type="number"
                step="0.01"
                min="0"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>
                    
            <div class="input-group">
              <label class="lbl">μ_j (Среднее скачка)</label>
              <input
                v-model.number="mertonParams.mu_j"
                type="number"
                step="0.01"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">σ_j (Волатильность скачка)</label>
              <input
                v-model.number="mertonParams.sigma_j"
                type="number"
                step="0.01"
                min="0.01"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>
          </div>
        </div>

        <!-- Bates Parameters -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Параметры Bates</h3>
          </div>
                
          <div class="controls-form">
            <div class="input-group">
              <label class="lbl">λ (Интенсивность скачков)</label>
              <input
                v-model.number="batesParams.lambda"
                type="number"
                step="0.01"
                min="0"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">μ_j (Среднее скачка)</label>
              <input
                v-model.number="batesParams.mu_j"
                type="number"
                step="0.01"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">σ_j (Волатильность скачка)</label>
              <input
                v-model.number="batesParams.sigma_j"
                type="number"
                step="0.01"
                min="0.01"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>
          </div>
        </div>

        <!-- SABR Parameters -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Параметры SABR</h3>
          </div>
                
          <div class="controls-form">
            <div class="input-group">
              <label class="lbl">α (Начальная волатильность)</label>
              <input
                v-model.number="sabrParams.alpha"
                type="number"
                step="0.001"
                min="0.001"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">β (Эластичность)</label>
              <input
                v-model.number="sabrParams.beta"
                type="number"
                step="0.01"
                min="0"
                max="1"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">ρ (Корреляция)</label>
              <input
                v-model.number="sabrParams.rho"
                type="number"
                step="0.01"
                min="-1"
                max="1"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">ν (Волатильность волатильности)</label>
              <input
                v-model.number="sabrParams.nu"
                type="number"
                step="0.01"
                min="0.01"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>
          </div>
        </div>

        <!-- Variance Gamma Parameters -->
        <div class="glass-card panel">
          <div class="panel-header">
            <h3>Параметры Variance Gamma</h3>
          </div>
                
          <div class="controls-form">
            <div class="input-group">
              <label class="lbl">θ (Дрифт)</label>
              <input
                v-model.number="vgParams.theta"
                type="number"
                step="0.01"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">σ (Волатильность)</label>
              <input
                v-model.number="vgParams.sigma"
                type="number"
                step="0.001"
                min="0.001"
                class="glass-input"
                @change="calculateAllModels"
              >
            </div>

            <div class="input-group">
              <label class="lbl">ν (Параметр формы)</label>
              <input
                v-model.number="vgParams.nu"
                type="number"
                step="0.001"
                min="0.001"
                class="glass-input"
                @change="calculateAllModels"
              >
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
                  <td class="model-name">
                    Black-Scholes
                  </td>
                  <td class="value">
                    {{ models.bsm.callPrice?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.bsm.putPrice?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.bsm.callDelta?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.bsm.putDelta?.toFixed(4) || '-' }}
                  </td>
                  <td class="note">
                    Базовая модель
                  </td>
                </tr>
                <tr>
                  <td class="model-name">
                    Heston
                  </td>
                  <td class="value">
                    {{ models.heston.callPrice?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.heston.putPrice?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.heston.callDelta?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.heston.putDelta?.toFixed(4) || '-' }}
                  </td>
                  <td class="note">
                    Стохастическая волатильность
                  </td>
                </tr>
                <tr>
                  <td class="model-name">
                    Merton
                  </td>
                  <td class="value">
                    {{ models.merton.callPrice?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.merton.putPrice?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.merton.callDelta?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.merton.putDelta?.toFixed(4) || '-' }}
                  </td>
                  <td class="note">
                    Модель скачков
                  </td>
                </tr>
                <tr>
                  <td class="model-name">
                    Bates
                  </td>
                  <td class="value">
                    {{ models.bates.callPrice?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.bates.putPrice?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.bates.callDelta?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.bates.putDelta?.toFixed(4) || '-' }}
                  </td>
                  <td class="note">
                    Heston + Скачки
                  </td>
                </tr>
                <tr>
                  <td class="model-name">
                    SABR
                  </td>
                  <td class="value">
                    {{ models.sabr.callPrice?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.sabr.putPrice?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.sabr.callDelta?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.sabr.putDelta?.toFixed(4) || '-' }}
                  </td>
                  <td class="note">
                    Процентные опционы
                  </td>
                </tr>
                <tr>
                  <td class="model-name">
                    Variance Gamma
                  </td>
                  <td class="value">
                    {{ models.vg.callPrice?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.vg.putPrice?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.vg.callDelta?.toFixed(4) || '-' }}
                  </td>
                  <td class="value">
                    {{ models.vg.putDelta?.toFixed(4) || '-' }}
                  </td>
                  <td class="note">
                    Процесс Леви
                  </td>
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
                  <td class="model-name">
                    Heston
                  </td>
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
                  <td class="model-name">
                    Merton
                  </td>
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
                  <td class="model-name">
                    Bates
                  </td>
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
                  <td class="model-name">
                    SABR
                  </td>
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
                  <td class="model-name">
                    Variance Gamma
                  </td>
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

// ---------------------------------------------------------------------------
// Numerical integration helper (Simpson's rule)
// ---------------------------------------------------------------------------
const integrate = (f: (x: number) => number, a: number, b: number, n: number = 128): number => {
  const h = (b - a) / n
  let sum = f(a) + f(b)
  for (let i = 1; i < n; i++) {
    sum += (i % 2 === 0 ? 2 : 4) * f(a + i * h)
  }
  return (h / 3) * sum
}

// BSM call from implied vol (used by SABR)
const bsmCall = (S: number, K: number, r: number, q: number, vol: number, T: number): number => {
  if (vol <= 0 || T <= 0) return Math.max(S * Math.exp(-q * T) - K * Math.exp(-r * T), 0)
  const d1 = (Math.log(S / K) + (r - q + 0.5 * vol * vol) * T) / (vol * Math.sqrt(T))
  const d2 = d1 - vol * Math.sqrt(T)
  return S * Math.exp(-q * T) * normalCdf(d1) - K * Math.exp(-r * T) * normalCdf(d2)
}

// ---------------------------------------------------------------------------
// Complex arithmetic helpers
// ---------------------------------------------------------------------------
type C2 = [number, number] // [re, im]
const cMul = (a: C2, b: C2): C2 => [a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]]
const cDiv = (a: C2, b: C2): C2 => {
  const d = b[0]*b[0]+b[1]*b[1]
  return [(a[0]*b[0]+a[1]*b[1])/d, (a[1]*b[0]-a[0]*b[1])/d]
}
const cAdd = (a: C2, b: C2): C2 => [a[0]+b[0], a[1]+b[1]]
const cSub = (a: C2, b: C2): C2 => [a[0]-b[0], a[1]-b[1]]
const cSqrt = (z: C2): C2 => {
  const r = Math.sqrt(Math.sqrt(z[0]*z[0]+z[1]*z[1]))
  const th = Math.atan2(z[1], z[0]) / 2
  return [r*Math.cos(th), r*Math.sin(th)]
}
const cExp = (z: C2): C2 => {
  const m = Math.exp(z[0])
  return [m*Math.cos(z[1]), m*Math.sin(z[1])]
}
const cLog = (z: C2): C2 => [0.5*Math.log(z[0]*z[0]+z[1]*z[1]), Math.atan2(z[1], z[0])]
const cScale = (s: number, z: C2): C2 => [s*z[0], s*z[1]]

// ---------------------------------------------------------------------------
// Heston (1993) — standard two-integral formulation
// C = S·e^{-qT}·P1 - K·e^{-rT}·P2
// Pj = 1/2 + (1/π) ∫₀^∞ Re[fj(u)] du,  j=1,2
// Using "Heston trap" formulation (Albrecher et al. 2007)
// ---------------------------------------------------------------------------
const hestonPj = (
  u: number, j: number, // j=1 or 2
  S: number, K: number, r: number, q: number, T: number,
  v0: number, kappa: number, theta: number, xi: number, rho: number
): number => {
  const x = Math.log(S)
  const iu: C2 = [0, u]

  const bj = j === 1 ? kappa - rho * xi : kappa
  const uj = j === 1 ? 0.5 : -0.5

  // d² = bj² + ξ²u²(1-ρ²) - 2iξu(bjρ+ξuj)
  const d2_re = bj * bj + xi * xi * u * u * (1 - rho * rho)
  const d2_im = -2 * xi * u * (bj * rho + xi * uj)
  const d: C2 = cSqrt([d2_re, d2_im])

  // alpha = bj - ρξiu
  const alpha: C2 = [bj, -rho * xi * u]
  const gNum: C2 = cAdd(alpha, d)
  const gDen: C2 = cSub(alpha, d)
  const g: C2 = cDiv(gNum, gDen)

  // D = (bj - rho*xi*iu + d)/(xi^2) * (1 - exp(dT))/(1 - g*exp(dT))
  const edT: C2 = cExp(cScale(T, d))                       // exp(d*T)
  const gedT: C2 = cMul(g, edT)                            // g*exp(d*T)
  const D: C2 = cMul(
    cDiv(gNum, [xi * xi, 0]),
    cDiv(cSub([1, 0], edT), cSub([1, 0], gedT))
  )

  // C = (r-q)*iu*T + kappa*theta/(xi^2) * ( (bj - rho*xi*iu + d)*T - 2*ln((1-g*exp(dT))/(1-g)) )
  const logArg: C2 = cDiv(cSub([1, 0], gedT), cSub([1, 0], g))
  const Cval: C2 = cAdd(
    cScale(T, cMul([(r - q), 0], iu)),
    cScale(kappa * theta / (xi * xi),
      cSub(cScale(T, gNum), cScale(2, cLog(logArg)))
    )
  )

  // f = exp(C + D*v0 + iu*x)
  const exponent: C2 = cAdd(cAdd(Cval, cScale(v0, D)), cMul(iu, [x, 0]))
  const f: C2 = cExp(exponent)

  // Integrand: Re[ exp(-iu*ln(K)) * f / (iu) ]
  const eiuK: C2 = cExp(cScale(-1, cMul(iu, [Math.log(K), 0])))
  const prod: C2 = cDiv(cMul(eiuK, f), iu)

  return prod[0] // Re[...]
}

const hestonCallPrice = (
  S: number, K: number, r: number, q: number, T: number,
  v0: number, kappa: number, theta: number, sigmaV: number, rho: number
): number => {
  const P1 = 0.5 + (1 / Math.PI) * integrate(
    (u: number) => u < 1e-8 ? 0 : hestonPj(u, 1, S, K, r, q, T, v0, kappa, theta, sigmaV, rho), 1e-6, 100, 256)
  const P2 = 0.5 + (1 / Math.PI) * integrate(
    (u: number) => u < 1e-8 ? 0 : hestonPj(u, 2, S, K, r, q, T, v0, kappa, theta, sigmaV, rho), 1e-6, 100, 256)
  return Math.max(S * Math.exp(-q * T) * P1 - K * Math.exp(-r * T) * P2, 0)
}

// ---------------------------------------------------------------------------
// Merton Jump-Diffusion: truncated Poisson series (Hull Ch. 27)
// C_merton = Σ_{n=0}^{N} (e^{-λ'T} (λ'T)^n / n!) * BSM(S, K, r_n, σ_n, T)
// ---------------------------------------------------------------------------
const mertonCallPrice = (
  S: number, K: number, r: number, q: number, T: number, sigma: number,
  lambda: number, muJ: number, sigmaJ: number
): number => {
  const k = Math.exp(muJ + 0.5 * sigmaJ * sigmaJ) - 1
  const lambdaPrime = lambda * (1 + k)
  let price = 0
  let factorial = 1
  const N = 20 // truncation
  for (let n = 0; n <= N; n++) {
    if (n > 0) factorial *= n
    const sigmaN = Math.sqrt(sigma * sigma + n * sigmaJ * sigmaJ / T)
    const rN = r - lambda * k + n * Math.log(1 + k) / T
    const weight = Math.exp(-lambdaPrime * T) * Math.pow(lambdaPrime * T, n) / factorial
    price += weight * bsmCall(S, K, rN, q, sigmaN, T)
  }
  return price
}

// ---------------------------------------------------------------------------
// Bates = Heston CF × Merton jump CF
// ---------------------------------------------------------------------------
const batesCallPrice = (
  S: number, K: number, r: number, q: number, T: number,
  v0: number, kappa: number, theta: number, sigmaV: number, rho: number,
  lambda: number, muJ: number, sigmaJ: number
): number => {
  // Use Heston as base + Merton correction
  const hestonPrice = hestonCallPrice(S, K, r, q, T, v0, kappa, theta, sigmaV, rho)
  // Jump adjustment: ratio of Merton/BSM prices
  const sigma = Math.sqrt(v0)
  const bsmPrice = bsmCall(S, K, r, q, sigma, T)
  const mertonPrice = mertonCallPrice(S, K, r, q, T, sigma, lambda, muJ, sigmaJ)
  const jumpRatio = bsmPrice > 1e-8 ? mertonPrice / bsmPrice : 1.0
  return hestonPrice * jumpRatio
}

// ---------------------------------------------------------------------------
// SABR: Hagan (2002) implied volatility formula
// σ_impl(K) = α / (FK)^{(1-β)/2} * z/x(z) * (1 + corrections)
// ---------------------------------------------------------------------------
const sabrImpliedVol = (
  F: number, K: number, T: number,
  alpha: number, beta: number, rho: number, nu: number
): number => {
  if (Math.abs(F - K) < 1e-8) {
    // ATM formula: σ = α/F^{1-β} * (1 + [(1-β)²α²/(24F^{2-2β}) + ραβν/(4F^{1-β}) + (2-3ρ²)ν²/24]*T)
    const Fb = Math.pow(F, 1 - beta)
    const term1 = ((1 - beta) * (1 - beta) * alpha * alpha) / (24 * Math.pow(F, 2 - 2 * beta))
    const term2 = (rho * alpha * beta * nu) / (4 * Fb)
    const term3 = (2 - 3 * rho * rho) * nu * nu / 24
    return (alpha / Fb) * (1 + (term1 + term2 + term3) * T)
  }

  const FK = F * K
  const FKbeta = Math.pow(FK, (1 - beta) / 2)
  const logFK = Math.log(F / K)
  const z = (nu / alpha) * FKbeta * logFK
  const xz = Math.log((Math.sqrt(1 - 2 * rho * z + z * z) + z - rho) / (1 - rho))

  const zOverXz = Math.abs(xz) > 1e-8 ? z / xz : 1.0

  const term1 = ((1 - beta) * (1 - beta) / 24) * (alpha * alpha / Math.pow(FK, 1 - beta))
  const term2 = (rho * beta * nu * alpha) / (4 * FKbeta)
  const term3 = (2 - 3 * rho * rho) * nu * nu / 24

  const denom = FKbeta * (1 + ((1 - beta) * (1 - beta) / 24) * logFK * logFK + ((1 - beta) ** 4 / 1920) * logFK ** 4)

  return (alpha / denom) * zOverXz * (1 + (term1 + term2 + term3) * T)
}

// ---------------------------------------------------------------------------
// Variance Gamma via Carr-Madan FFT with damping (α=1.5)
// φ_VG(u) = exp(iuμT) * (1 - iθνu + 0.5σ²νu²)^{-T/ν}
// C = (e^{-rT}/π) ∫₀^∞ Re[e^{-iu·lnK} · ψ(u)] du,  Carr-Madan with α damping
// ---------------------------------------------------------------------------
const vgCallPrice = (
  S: number, K: number, r: number, q: number, T: number,
  thetaVG: number, sigmaVG: number, nu: number
): number => {
  // Risk-neutral drift: ω = (1/ν)·ln(1 - θν - 0.5σ²ν)
  const denom_check = 1 - thetaVG * nu - 0.5 * sigmaVG * sigmaVG * nu
  if (denom_check <= 0) return bsmCall(S, K, r, q, sigmaVG > 0 ? sigmaVG : 0.2, T) // fallback
  const omega = (1 / nu) * Math.log(denom_check)
  const x = Math.log(S) + (r - q + omega) * T

  // CF of log-price: φ(u) = exp(iu·x) · (1 - iθνu + 0.5σ²νu²)^{-T/ν}
  const vgCF = (u_re: number, u_im: number): C2 => {
    // base = 1 + 0.5σ²ν(u_re + i·u_im)² - iθν(u_re + i·u_im)
    // (u_re+i·u_im)² = u_re²-u_im² + 2i·u_re·u_im
    const usq_re = u_re * u_re - u_im * u_im
    const usq_im = 2 * u_re * u_im
    const base_re = 1 + 0.5 * sigmaVG * sigmaVG * nu * usq_re + thetaVG * nu * u_im
    const base_im = 0.5 * sigmaVG * sigmaVG * nu * usq_im - thetaVG * nu * u_re
    // base^{-T/ν}
    const pw: C2 = cExp(cScale(-T / nu, cLog([base_re, base_im])))
    // exp(i(u_re+i·u_im)·x) = exp(-u_im·x + i·u_re·x)
    const phase: C2 = cExp([-u_im * x, u_re * x])
    return cMul(phase, pw)
  }

  // Carr-Madan: C = (e^{-αk}/π) ∫₀^∞ Re[e^{-iuk} · ψ(u)] du
  // ψ(u) = e^{-rT}·φ(u-(α+1)i) / (α²+α-u²+iu(2α+1))
  const alpha_cm = 1.5 // damping
  const k = Math.log(K)

  const integrand = (u: number): number => {
    if (u < 1e-8) return 0
    const phi: C2 = vgCF(u, -(alpha_cm + 1))
    const denom_re = alpha_cm * alpha_cm + alpha_cm - u * u
    const denom_im = u * (2 * alpha_cm + 1)
    const psi: C2 = cDiv(cScale(Math.exp(-r * T), phi), [denom_re, denom_im])
    // Re[e^{-iuk} · ψ] = Re[(cos(uk) - i·sin(uk)) · ψ]
    const cos_uk = Math.cos(u * k)
    const sin_uk = Math.sin(u * k)
    return cos_uk * psi[0] + sin_uk * psi[1]
  }

  const integral = integrate(integrand, 1e-6, 80, 256)
  return Math.max(Math.exp(-alpha_cm * k) / Math.PI * integral, 0)
}

// ---------------------------------------------------------------------------
// Delta via finite difference: Δ = (C(S+h) - C(S-h)) / (2h)
// ---------------------------------------------------------------------------
const finiteDiffDelta = (
  pricer: (S: number) => number,
  S: number
): number => {
  const h = S * 0.001
  return (pricer(S + h) - pricer(S - h)) / (2 * h)
}

// ---------------------------------------------------------------------------
// Main calculation
// ---------------------------------------------------------------------------
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

  // === Heston (characteristic function + numerical integration) ===
  const hCall = hestonCallPrice(S, K, r, q, T,
    hestonParams.v0, hestonParams.kappa, hestonParams.theta, hestonParams.sigma_v, hestonParams.rho)
  models.heston.callPrice = hCall
  models.heston.putPrice = hCall - S * Math.exp(-q * T) + K * Math.exp(-r * T) // put-call parity
  models.heston.callDelta = finiteDiffDelta(
    (s) => hestonCallPrice(s, K, r, q, T, hestonParams.v0, hestonParams.kappa, hestonParams.theta, hestonParams.sigma_v, hestonParams.rho), S)
  models.heston.putDelta = models.heston.callDelta - Math.exp(-q * T)

  // === Merton Jump-Diffusion (truncated Poisson series, Hull Ch. 27) ===
  const mCall = mertonCallPrice(S, K, r, q, T, sigma,
    mertonParams.lambda, mertonParams.mu_j, mertonParams.sigma_j)
  models.merton.callPrice = mCall
  models.merton.putPrice = mCall - S * Math.exp(-q * T) + K * Math.exp(-r * T)
  models.merton.callDelta = finiteDiffDelta(
    (s) => mertonCallPrice(s, K, r, q, T, sigma, mertonParams.lambda, mertonParams.mu_j, mertonParams.sigma_j), S)
  models.merton.putDelta = models.merton.callDelta - Math.exp(-q * T)

  // === Bates (Heston + Merton jumps) ===
  const bCall = batesCallPrice(S, K, r, q, T,
    hestonParams.v0, hestonParams.kappa, hestonParams.theta, hestonParams.sigma_v, hestonParams.rho,
    batesParams.lambda, batesParams.mu_j, batesParams.sigma_j)
  models.bates.callPrice = bCall
  models.bates.putPrice = bCall - S * Math.exp(-q * T) + K * Math.exp(-r * T)
  models.bates.callDelta = finiteDiffDelta(
    (s) => batesCallPrice(s, K, r, q, T, hestonParams.v0, hestonParams.kappa, hestonParams.theta, hestonParams.sigma_v, hestonParams.rho, batesParams.lambda, batesParams.mu_j, batesParams.sigma_j), S)
  models.bates.putDelta = models.bates.callDelta - Math.exp(-q * T)

  // === SABR (Hagan 2002 implied vol → BSM) ===
  const F = S * Math.exp((r - q) * T)
  const sabrVol = sabrImpliedVol(F, K, T, sabrParams.alpha, sabrParams.beta, sabrParams.rho, sabrParams.nu)
  const sCall = bsmCall(S, K, r, q, Math.max(sabrVol, 1e-6), T)
  models.sabr.callPrice = sCall
  models.sabr.putPrice = sCall - S * Math.exp(-q * T) + K * Math.exp(-r * T)
  models.sabr.callDelta = finiteDiffDelta(
    (s) => {
      const Fs = s * Math.exp((r - q) * T)
      const sv = sabrImpliedVol(Fs, K, T, sabrParams.alpha, sabrParams.beta, sabrParams.rho, sabrParams.nu)
      return bsmCall(s, K, r, q, Math.max(sv, 1e-6), T)
    }, S)
  models.sabr.putDelta = models.sabr.callDelta - Math.exp(-q * T)

  // === Variance Gamma (characteristic function + Gil-Pelaez) ===
  const vCall = vgCallPrice(S, K, r, q, T, vgParams.theta, vgParams.sigma, vgParams.nu)
  models.vg.callPrice = vCall
  models.vg.putPrice = vCall - S * Math.exp(-q * T) + K * Math.exp(-r * T)
  models.vg.callDelta = finiteDiffDelta(
    (s) => vgCallPrice(s, K, r, q, T, vgParams.theta, vgParams.sigma, vgParams.nu), S)
  models.vg.putDelta = models.vg.callDelta - Math.exp(-q * T)
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