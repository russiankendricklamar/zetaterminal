<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Стресс-тестирование</h1>
        <p class="section-subtitle">Симуляция экстремальных рыночных шоков</p>
      </div>
      
      <div class="header-right">
        <!-- Selected Bank -->
        <div class="glass-pill control-pill">
           <span class="lbl-mini">Банк:</span>
           <span class="text-white font-bold">{{ selectedBank.name }}</span>
        </div>
        
        <!-- Severity Multiplier -->
        <div class="glass-pill control-pill">
            <span class="lbl-mini">Множитель шока:</span>
            <div class="scrub-wrapper">
                <input 
                    type="range"
                    v-model.number="shockMultiplier"
                    :step="0.1"
                    :min="0.5"
                    :max="3.0"
                    class="range-slider"
                />
                <span class="scrub-val text-accent">{{ shockMultiplier.toFixed(1) }}x</span>
            </div>
        </div>

        <button @click="runAllStressTests" class="btn-glass primary" :disabled="isRunning">
          <span v-if="!isRunning" class="flex items-center gap-2">
             <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
             <span>Запустить все</span>
          </span>
          <span v-else class="flex items-center gap-2">
             <span class="spinner-mini"></span> Тестирую...
          </span>
        </button>
      </div>
    </div>

    <!-- Scenarios Grid -->
    <div class="scenarios-grid">
      <div 
        v-for="scenario in scenarios" 
        :key="scenario.id"
        @click="selectScenario(scenario)"
        class="glass-card scenario-card"
        :class="{ active: selectedScenario?.id === scenario.id }"
      >
        <div class="sc-header">
          <span class="sc-name">{{ scenario.name }}</span>
          <div class="sc-header-actions">
          <span class="badge" :class="scenario.severity">{{ scenario.severity }}</span>
            <div class="sc-actions" @click.stop>
              <button @click="editScenario(scenario)" class="btn-icon-sm" title="Редактировать">
                <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
              </button>
              <button @click="deleteScenario(scenario.id)" class="btn-icon-sm" title="Удалить" v-if="scenario.custom">
                <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
        <p class="sc-desc">{{ scenario.description }}</p>
        <div class="sc-footer">
            <span class="sc-impact" :class="getScenarioPnLImpact(scenario) < 0 ? 'text-red' : 'text-green'">
                {{ formatCurrencyCompact(getScenarioPnLImpact(scenario)) }}
            </span>
            <span class="sc-prob">Вероятность: {{ (scenario.probability * 100).toFixed(0) }}%</span>
        </div>
      </div>
      
      <!-- Add New Scenario Card -->
      <div @click="openScenarioEditor()" class="glass-card scenario-card add-scenario-card">
        <div class="add-scenario-content">
          <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          <span class="add-scenario-text">Создать сценарий</span>
        </div>
      </div>
    </div>

    <!-- Selected Scenario Detail (Split View) -->
    <transition name="fade" mode="out-in">
    <div v-if="selectedScenario" class="dashboard-grid">
        
        <!-- Left: Impact Analysis & Stats -->
        <div class="col-left">
            <div class="glass-card panel">
                <div class="panel-header">
                    <h3>Влияние сценария: <span class="text-white">{{ selectedScenario.name }}</span></h3>
                </div>
                
                <!-- 4 Key Metrics -->
                <div class="impact-metrics-grid">
                    <div class="metric-box">
                        <span class="lbl">Влияние на P&L</span>
                        <span class="val text-red">{{ formatCurrency(getScenarioPnLImpact(selectedScenario)) }}</span>
                    </div>
                    <div class="metric-box">
                        <span class="lbl">Изменение VaR</span>
                        <span class="val" :class="getScenarioVaRChange(selectedScenario) < 0 ? 'text-red' : 'text-green'">
                            {{ getScenarioVaRChange(selectedScenario).toFixed(1) }}%
                        </span>
                    </div>
                    <div class="metric-box">
                        <span class="lbl">Длительность</span>
                        <span class="val text-white">{{ selectedScenario.duration }}</span>
                    </div>
                     <div class="metric-box">
                        <span class="lbl">Вероятность</span>
                        <span class="val text-orange">{{ (selectedScenario.probability * 100).toFixed(1) }}%</span>
                    </div>
                </div>

                <div class="divider"></div>

                <!-- Asset Impact Bars -->
                <div class="panel-header">
                    <h3>Влияние на классы активов</h3>
                </div>
                <div class="impact-bars-list">
                    <div v-for="(baseImpact, asset) in selectedScenario.assetImpact" :key="asset" class="bar-row">
                        <span class="bar-label">{{ asset }}</span>
                        <div class="bar-track">
                             <div class="bar-fill" 
                                  :class="baseImpact < 0 ? 'bg-red' : 'bg-green'"
                                  :style="{ width: Math.min(100, Math.abs(baseImpact * shockMultiplier * 1.5)) + '%' }">
                             </div>
                        </div>
                        <span class="bar-val" :class="baseImpact < 0 ? 'text-red' : 'text-green'">
                            {{ baseImpact > 0 ? '+' : '' }}{{ (baseImpact * shockMultiplier).toFixed(1) }}%
                        </span>
                    </div>
                </div>

                <div class="divider"></div>

                <!-- Stats Mini Panel -->
                <div class="panel-header">
                    <h3>Статистика риска</h3>
                </div>
                <div class="stats-grid-row">
                     <div class="stat-box">
                         <span class="lbl-sm">Средний убыток</span>
                         <span class="val-sm text-red">{{ formatCurrencyCompact(avgLoss * shockMultiplier) }}</span>
                     </div>
                     <div class="stat-box">
                         <span class="lbl-sm">Max Drawdown</span>
                         <span class="val-sm text-red">{{ formatCurrencyCompact(maxLoss * shockMultiplier) }}</span>
                     </div>
                     <div class="stat-box">
                         <span class="lbl-sm">Expected Shortfall</span>
                         <span class="val-sm text-orange">{{ formatCurrencyCompact(expectedLoss * shockMultiplier) }}</span>
                     </div>
                </div>
            </div>
        </div>

        <!-- Right: Market Conditions -->
        <aside class="col-right">
            <div class="glass-card panel sticky-panel">
                <div class="panel-header">
                    <h3>Рыночные условия</h3>
                </div>
                <div class="market-changes-list">
                    <div v-for="(change, key) in selectedScenario.marketChanges" :key="key" class="market-row">
                        <span class="m-key">{{ formatLabel(key) }}</span>
                        <span class="m-val" :class="change.includes('-') ? 'text-red' : 'text-green'">{{ change }}</span>
                    </div>
                </div>
                <div class="divider"></div>
                <div class="info-block">
                    <p class="text-xs text-muted">
                        Метрики пересчитаны с учетом коэффициента шока: <b class="text-white">{{ shockMultiplier.toFixed(1) }}x</b>.
                    </p>
                </div>
            </div>
        </aside>
    </div>
    </transition>

    <!-- Comparison Table -->
    <div class="glass-card panel">
      <div class="panel-header">
        <h3>Сравнение сценариев</h3>
      </div>
      <div class="table-wrapper">
        <table class="glass-table">
          <thead>
            <tr>
              <th class="col-left pl-4">Сценарий</th>
              <th>Влияние на P&L</th>
              <th>Изменение VaR</th>
              <th>Длительность</th>
              <th>Вер.</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="scenario in scenarios" :key="scenario.id" 
                class="hover-row"
                :class="{ 'row-active': selectedScenario?.id === scenario.id }"
                @click="selectScenario(scenario)">
              <td class="col-left pl-4">
                <span class="sc-name-sm">{{ scenario.name }}</span>
              </td>
              <td :class="getScenarioPnLImpact(scenario) < 0 ? 'text-red' : 'text-green'">
                {{ formatCurrency(getScenarioPnLImpact(scenario)) }}
              </td>
              <td :class="getScenarioVaRChange(scenario) < 0 ? 'text-red' : 'text-green'">
                {{ getScenarioVaRChange(scenario).toFixed(1) }}%
              </td>
              <td class="text-muted">{{ scenario.duration }}</td>
              <td class="text-orange">{{ (scenario.probability * 100).toFixed(1) }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Footer Notes -->
    <div class="footer-notes">
        <span class="note-item">Данные основаны на исторических корреляциях</span>
        <span class="note-item">•</span>
        <span class="note-item">Рекомендуется ежеквартальный пересмотр</span>
    </div>

    <!-- Scenario Editor Modal -->
    <transition name="modal-fade">
      <div v-if="isEditorOpen" class="modal-overlay" @click="closeEditor">
        <div class="modal-container scenario-editor-modal" @click.stop>
          <div class="modal-header">
            <h2>{{ editingScenario ? 'Редактировать сценарий' : 'Создать сценарий' }}</h2>
            <button class="modal-close" @click="closeEditor">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          
          <div class="modal-body">
            <form @submit.prevent="saveScenario" class="scenario-form">
              <!-- Basic Info -->
              <div class="form-section">
                <h3 class="section-title">Основная информация</h3>
                <div class="form-grid">
                  <div class="form-group">
                    <label>Название сценария</label>
                    <input 
                      type="text" 
                      v-model="formData.name" 
                      class="glass-input"
                      placeholder="Например: Кризис ликвидности"
                      required
                    />
                  </div>
                  <div class="form-group">
                    <label>Описание</label>
                    <textarea 
                      v-model="formData.description" 
                      class="glass-input"
                      rows="2"
                      placeholder="Краткое описание сценария"
                    ></textarea>
                  </div>
                  <div class="form-group">
                    <label>Длительность</label>
                    <input 
                      type="text" 
                      v-model="formData.duration" 
                      class="glass-input"
                      placeholder="Например: 1–3 дня"
                    />
                  </div>
                  <div class="form-group">
                    <label>Вероятность (%)</label>
                    <input 
                      type="number" 
                      v-model.number="formData.probability" 
                      class="glass-input"
                      min="0"
                      max="100"
                      step="0.1"
                      required
                    />
                  </div>
                  <div class="form-group">
                    <label>Уровень серьезности</label>
                    <select v-model="formData.severity" class="glass-input">
                      <option value="critical">Критический</option>
                      <option value="high">Высокий</option>
                      <option value="medium">Средний</option>
                      <option value="low">Низкий</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Shock Type -->
              <div class="form-section">
                <h3 class="section-title">Тип шока</h3>
                <div class="form-group">
                  <label>Тип стресс-теста</label>
                  <select v-model="formData.type" class="glass-input" @change="onShockTypeChange">
                    <option value="return_shock">Шок доходности</option>
                    <option value="volatility_shock">Шок волатильности</option>
                    <option value="correlation_shock">Шок корреляции</option>
                  </select>
                </div>
                
                <div class="form-grid" v-if="formData.type === 'return_shock'">
                  <div class="form-group">
                    <label>Множитель доходности</label>
                    <input 
                      type="number" 
                      v-model.number="formData.return_multiplier" 
                      class="glass-input"
                      min="0"
                      max="2"
                      step="0.1"
                      placeholder="0.5"
                    />
                    <span class="form-hint">Множитель для ожидаемой доходности (0.5 = снижение на 50%)</span>
                  </div>
                </div>
                
                <div class="form-grid" v-if="formData.type === 'volatility_shock'">
                  <div class="form-group">
                    <label>Множитель волатильности</label>
                    <input 
                      type="number" 
                      v-model.number="formData.volatility_multiplier" 
                      class="glass-input"
                      min="0.5"
                      max="5"
                      step="0.1"
                      placeholder="1.5"
                    />
                    <span class="form-hint">Множитель для волатильности (1.5 = увеличение на 50%)</span>
                  </div>
                </div>
                
                <div class="form-grid" v-if="formData.type === 'correlation_shock'">
                  <div class="form-group">
                    <label>Множитель корреляции</label>
                    <input 
                      type="number" 
                      v-model.number="formData.correlation_multiplier" 
                      class="glass-input"
                      min="0.5"
                      max="2"
                      step="0.1"
                      placeholder="1.3"
                    />
                    <span class="form-hint">Множитель для корреляций (1.3 = увеличение на 30%)</span>
                  </div>
                </div>
              </div>

              <!-- Market Changes -->
              <div class="form-section">
                <h3 class="section-title">Рыночные изменения</h3>
                <div class="market-changes-editor">
                  <div 
                    v-for="(value, key, index) in formData.marketChanges" 
                    :key="index"
                    class="market-change-row"
                  >
                    <input 
                      type="text" 
                      v-model="marketChangeKeys[index]" 
                      class="glass-input"
                      placeholder="Параметр (например: VIX)"
                      @input="updateMarketChange(key, marketChangeKeys[index], value)"
                    />
                    <input 
                      type="text" 
                      v-model="marketChangeValues[index]" 
                      class="glass-input"
                      placeholder="Изменение (например: +20 pts)"
                      @input="updateMarketChange(key, marketChangeKeys[index], marketChangeValues[index])"
                    />
                    <button 
                      type="button" 
                      @click="removeMarketChange(key)"
                      class="btn-icon-sm btn-danger"
                    >
                      <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </button>
                  </div>
                  <button 
                    type="button" 
                    @click="addMarketChange"
                    class="btn-glass outline btn-add"
                  >
                    <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                    </svg>
                    Добавить параметр
                  </button>
                </div>
              </div>

              <!-- Asset Impact -->
              <div class="form-section">
                <h3 class="section-title">Влияние на классы активов (%)</h3>
                <div class="asset-impact-editor">
                  <div 
                    v-for="(value, asset, index) in formData.assetImpact" 
                    :key="index"
                    class="asset-impact-row"
                  >
                    <input 
                      type="text" 
                      v-model="assetImpactKeys[index]" 
                      class="glass-input"
                      placeholder="Класс актива (например: Акции)"
                      @input="updateAssetImpact(asset, assetImpactKeys[index], value)"
                    />
                    <input 
                      type="number" 
                      v-model.number="assetImpactValues[index]" 
                      class="glass-input"
                      placeholder="Влияние (%)"
                      step="0.1"
                      @input="updateAssetImpact(asset, assetImpactKeys[index], assetImpactValues[index])"
                    />
                    <button 
                      type="button" 
                      @click="removeAssetImpact(asset)"
                      class="btn-icon-sm btn-danger"
                    >
                      <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </button>
                  </div>
                  <button 
                    type="button" 
                    @click="addAssetImpact"
                    class="btn-glass outline btn-add"
                  >
                    <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                    </svg>
                    Добавить класс актива
                  </button>
                </div>
              </div>

              <!-- Form Actions -->
              <div class="form-actions">
                <button type="button" @click="closeEditor" class="btn-glass outline">Отмена</button>
                <button type="submit" class="btn-glass primary">Сохранить сценарий</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { runStressTests, type StressScenario, type StressTestResponse } from '@/services/stressService'
import { usePortfolioStore } from '@/stores/portfolio'

const portfolioStore = usePortfolioStore()

const selectedBank = computed(() => portfolioStore.selectedBank)

const isRunning = ref(false)
const shockMultiplier = ref(1.0)
const stressTestResults = ref<StressTestResponse | null>(null)

// Helper function for toast notifications
const showToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
  console.log(`[${type.toUpperCase()}] ${message}`)
  // TODO: Integrate with toast notification system if available
}

const scenarios = ref([
  {
    id: 1,
    name: '«Чёрный лебедь»',
    description: 'Глобальный рыночный крах (как COVID-19)',
    pnlImpact: -185000,
    varChange: -45.5,
    duration: '1–3 дня',
    probability: 0.01,
    severity: 'critical',
    marketChanges: { 'Волатильность': '+25%', 'Bonds Yield': '+150 bps', 'Correlation': '+0.50', 'Spreads': '+100 bps' },
    assetImpact: { 'Акции': -35, 'Облигации': -12, 'Товары': -25, 'Валюта': -8 },
    key: 'black_swan',
    type: 'return_shock' as const,
    return_multiplier: 0.5,
    custom: false
  },
  {
    id: 2,
    name: 'Скачок волатильности',
    description: 'Резкий рост индекса VIX > 40',
    pnlImpact: -67500,
    varChange: -18.2,
    duration: '1–5 дней',
    probability: 0.05,
    severity: 'high',
    marketChanges: { 'VIX': '+20 pts', 'Range': '+15%', 'Liquidity': '-10%' },
    assetImpact: { 'Акции': -18, 'Облигации': -5, 'Опционы': -40, 'Валюта': -3 },
    key: 'volatility_spike',
    type: 'volatility_shock' as const,
    volatility_multiplier: 1.5,
    custom: false
  },
  {
    id: 3,
    name: 'Рост ставок ЦБ',
    description: 'Неожиданное повышение ставки на 100 б.п.',
    pnlImpact: -45200,
    varChange: -12.5,
    duration: '1–10 дней',
    probability: 0.15,
    severity: 'high',
    marketChanges: { 'Key Rate': '+100 bps', 'Spreads': '+50 bps', 'FX Rate': '-5%' },
    assetImpact: { 'Акции': -12, 'Облигации': -22, 'Недвижимость': -15, 'Валюта': -6 },
    key: 'rate_hike',
    type: 'return_shock' as const,
    return_multiplier: 0.7,
    custom: false
  },
  {
    id: 4,
    name: 'Техническая коррекция',
    description: 'Умеренное снижение S&P 500 на 10%',
    pnlImpact: -12400,
    varChange: -5.2,
    duration: '5–20 дней',
    probability: 0.35,
    severity: 'medium',
    marketChanges: { 'Index': '-8%', 'Volatility': '+10%', 'Spreads': '+20 bps' },
    assetImpact: { 'Акции': -8, 'Облигации': 2, 'Товары': -5, 'Валюта': -2 },
    key: 'correction',
    type: 'correlation_shock' as const,
    correlation_multiplier: 1.3,
    custom: false
  }
])

// Scenario Editor State
const isEditorOpen = ref(false)
const editingScenario = ref<any>(null)
const nextScenarioId = ref(5)

const formData = ref({
  name: '',
  description: '',
  duration: '',
  probability: 1,
  severity: 'medium',
  type: 'return_shock' as 'return_shock' | 'volatility_shock' | 'correlation_shock',
  return_multiplier: 0.5,
  volatility_multiplier: 1.5,
  correlation_multiplier: 1.3,
  marketChanges: {} as Record<string, string>,
  assetImpact: {} as Record<string, number>
})

const marketChangeKeys = ref<string[]>([])
const marketChangeValues = ref<string[]>([])
const assetImpactKeys = ref<string[]>([])
const assetImpactValues = ref<number[]>([])

// Load custom scenarios from localStorage
const loadCustomScenarios = () => {
  try {
    const saved = localStorage.getItem('custom_stress_scenarios')
    if (saved) {
      const custom = JSON.parse(saved)
      scenarios.value = [...scenarios.value.filter(s => !s.custom), ...custom]
      const maxId = Math.max(...scenarios.value.map(s => s.id))
      nextScenarioId.value = maxId + 1
    }
  } catch (e) {
    console.error('Failed to load custom scenarios:', e)
  }
}

// Save custom scenarios to localStorage
const saveCustomScenarios = () => {
  try {
    const custom = scenarios.value.filter(s => s.custom)
    localStorage.setItem('custom_stress_scenarios', JSON.stringify(custom))
  } catch (e) {
    console.error('Failed to save custom scenarios:', e)
  }
}

const openScenarioEditor = (scenario?: any) => {
  if (scenario) {
    editingScenario.value = scenario
    formData.value = {
      name: scenario.name,
      description: scenario.description || '',
      duration: scenario.duration || '',
      probability: (scenario.probability || 0.01) * 100,
      severity: scenario.severity || 'medium',
      type: scenario.type || 'return_shock',
      return_multiplier: scenario.return_multiplier || 0.5,
      volatility_multiplier: scenario.volatility_multiplier || 1.5,
      correlation_multiplier: scenario.correlation_multiplier || 1.3,
      marketChanges: scenario.marketChanges ? { ...scenario.marketChanges } : {},
      assetImpact: scenario.assetImpact ? { ...scenario.assetImpact } : {}
    }
  } else {
    editingScenario.value = null
    formData.value = {
      name: '',
      description: '',
      duration: '',
      probability: 1,
      severity: 'medium',
      type: 'return_shock',
      return_multiplier: 0.5,
      volatility_multiplier: 1.5,
      correlation_multiplier: 1.3,
      marketChanges: {},
      assetImpact: {}
    }
  }
  
  // Initialize arrays for editing
  marketChangeKeys.value = Object.keys(formData.value.marketChanges)
  marketChangeValues.value = Object.values(formData.value.marketChanges)
  assetImpactKeys.value = Object.keys(formData.value.assetImpact)
  assetImpactValues.value = Object.values(formData.value.assetImpact)
  
  isEditorOpen.value = true
}

const closeEditor = () => {
  isEditorOpen.value = false
  editingScenario.value = null
}

const onShockTypeChange = () => {
  // Reset multipliers when type changes
  if (formData.value.type === 'return_shock') {
    formData.value.volatility_multiplier = undefined
    formData.value.correlation_multiplier = undefined
  } else if (formData.value.type === 'volatility_shock') {
    formData.value.return_multiplier = undefined
    formData.value.correlation_multiplier = undefined
  } else if (formData.value.type === 'correlation_shock') {
    formData.value.return_multiplier = undefined
    formData.value.volatility_multiplier = undefined
  }
}

const updateMarketChange = (oldKey: string, newKey: string, value: string) => {
  const index = marketChangeKeys.value.indexOf(oldKey)
  if (index > -1) {
    if (oldKey !== newKey) {
      delete formData.value.marketChanges[oldKey]
    }
    if (newKey) {
      formData.value.marketChanges[newKey] = value
      marketChangeKeys.value[index] = newKey
      marketChangeValues.value[index] = value
    }
  }
}

const addMarketChange = () => {
  const newKey = `Параметр${Object.keys(formData.value.marketChanges).length + 1}`
  formData.value.marketChanges[newKey] = ''
  marketChangeKeys.value.push(newKey)
  marketChangeValues.value.push('')
}

const removeMarketChange = (key: string) => {
  delete formData.value.marketChanges[key]
  const index = marketChangeKeys.value.indexOf(key)
  if (index > -1) {
    marketChangeKeys.value.splice(index, 1)
    marketChangeValues.value.splice(index, 1)
  }
}

const updateAssetImpact = (oldKey: string, newKey: string, value: number) => {
  const index = assetImpactKeys.value.indexOf(oldKey)
  if (index > -1) {
    if (oldKey !== newKey) {
      delete formData.value.assetImpact[oldKey]
    }
    if (newKey) {
      formData.value.assetImpact[newKey] = value
      assetImpactKeys.value[index] = newKey
      assetImpactValues.value[index] = value
    }
  }
}

const addAssetImpact = () => {
  const newKey = `Актив${Object.keys(formData.value.assetImpact).length + 1}`
  formData.value.assetImpact[newKey] = 0
  assetImpactKeys.value.push(newKey)
  assetImpactValues.value.push(0)
}

const removeAssetImpact = (key: string) => {
  delete formData.value.assetImpact[key]
  const index = assetImpactKeys.value.indexOf(key)
  if (index > -1) {
    assetImpactKeys.value.splice(index, 1)
    assetImpactValues.value.splice(index, 1)
  }
}

const saveScenario = () => {
  // Generate key from name
  const key = formData.value.name.toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
  
  const scenarioData: any = {
    id: editingScenario?.value?.id || nextScenarioId.value++,
    name: formData.value.name,
    description: formData.value.description,
    duration: formData.value.duration,
    probability: formData.value.probability / 100,
    severity: formData.value.severity,
    key: editingScenario?.value?.key || `custom_${key}`,
    type: formData.value.type,
    marketChanges: { ...formData.value.marketChanges },
    assetImpact: { ...formData.value.assetImpact },
    custom: true
  }
  
  // Add multiplier based on type
  if (formData.value.type === 'return_shock' && formData.value.return_multiplier) {
    scenarioData.return_multiplier = formData.value.return_multiplier
  } else if (formData.value.type === 'volatility_shock' && formData.value.volatility_multiplier) {
    scenarioData.volatility_multiplier = formData.value.volatility_multiplier
  } else if (formData.value.type === 'correlation_shock' && formData.value.correlation_multiplier) {
    scenarioData.correlation_multiplier = formData.value.correlation_multiplier
  }
  
  // Initialize impact values
  scenarioData.pnlImpact = 0
  scenarioData.varChange = 0
  
  if (editingScenario.value) {
    // Update existing scenario
    const index = scenarios.value.findIndex(s => s.id === editingScenario.value.id)
    if (index > -1) {
      scenarios.value[index] = { ...scenarios.value[index], ...scenarioData }
    }
  } else {
    // Add new scenario
    scenarios.value.push(scenarioData)
  }
  
  saveCustomScenarios()
  closeEditor()
  showToast(editingScenario.value ? 'Сценарий обновлен' : 'Сценарий создан', 'success')
}

const editScenario = (scenario: any) => {
  openScenarioEditor(scenario)
}

const deleteScenario = (id: number) => {
  if (confirm('Удалить этот сценарий?')) {
    scenarios.value = scenarios.value.filter(s => s.id !== id)
    saveCustomScenarios()
    if (selectedScenario.value?.id === id) {
      selectedScenario.value = scenarios.value[0] || null
    }
    showToast('Сценарий удален', 'success')
  }
}

// Load custom scenarios on mount
loadCustomScenarios()

const selectedScenario = ref(scenarios.value[0])
const selectScenario = (scenario: any) => selectedScenario.value = scenario

// Helpers
const getImpact = (val: number) => val * shockMultiplier.value
const formatCurrency = (val: number) => new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(val)
const formatCurrencyCompact = (val: number) => '₽' + (val / 1000).toFixed(0) + 'k'
const formatLabel = (key: string) => key.charAt(0).toUpperCase() + key.slice(1)

// Computed properties для отображения данных из API результатов
const getScenarioMetrics = (scenarioKey: string) => {
  if (!stressTestResults.value || !stressTestResults.value.results[scenarioKey]) {
    return null
  }
  return stressTestResults.value.results[scenarioKey].metrics
}

const getScenarioPnLImpact = (scenario: any) => {
  const metrics = getScenarioMetrics(scenario.key)
  if (metrics) {
    // Вычисляем P&L Impact из метрик
    const baselineCapital = stressTestResults.value?.baseline.initial_capital || 1000000
    return -(baselineCapital - metrics.mean_final) * shockMultiplier.value
  }
  return scenario.pnlImpact * shockMultiplier.value
}

const getScenarioVaRChange = (scenario: any) => {
  const metrics = getScenarioMetrics(scenario.key)
  if (metrics) {
    const baselineCapital = stressTestResults.value?.baseline.initial_capital || 1000000
    const varChange = ((baselineCapital - metrics.var_95) / baselineCapital) * 100
    return varChange * shockMultiplier.value
  }
  return scenario.varChange * shockMultiplier.value
}

const avgLoss = computed(() => {
  if (stressTestResults.value) {
    const losses = Object.values(stressTestResults.value.results).map(r => 
      -(stressTestResults.value!.baseline.initial_capital - r.metrics.mean_final)
    )
    return losses.reduce((sum, l) => sum + l, 0) / losses.length * shockMultiplier.value
  }
  return scenarios.value.reduce((sum, s) => sum + s.pnlImpact, 0) / scenarios.value.length * shockMultiplier.value
})

const maxLoss = computed(() => {
  if (stressTestResults.value) {
    const losses = Object.values(stressTestResults.value.results).map(r => 
      -(stressTestResults.value!.baseline.initial_capital - r.metrics.mean_final)
    )
    return Math.min(...losses) * shockMultiplier.value
  }
  return Math.min(...scenarios.value.map(s => s.pnlImpact)) * shockMultiplier.value
})

const expectedLoss = computed(() => {
  if (stressTestResults.value) {
    return Object.values(stressTestResults.value.results).reduce((sum, r, idx) => {
      const scenario = scenarios.value[idx]
      const loss = -(stressTestResults.value!.baseline.initial_capital - r.metrics.mean_final)
      return sum + loss * (scenario?.probability || 0)
    }, 0) * shockMultiplier.value
  }
  return scenarios.value.reduce((sum, s) => sum + s.pnlImpact * s.probability, 0) * shockMultiplier.value
})

const runAllStressTests = async () => {
  if (isRunning.value) return
  isRunning.value = true
  
  try {
    // Генерируем mock данные для mu и cov_matrix
    const nAssets = portfolioStore.positions.length || 23
    const assetNames = portfolioStore.positions.map(p => p.symbol)
    
    // Mock ожидаемые доходности (5-15% годовых)
    const mu = Array.from({ length: nAssets }, () => 0.05 + Math.random() * 0.10)
    
    // Mock ковариационная матрица (на основе корреляционной матрицы)
    const correlationMatrix = portfolioStore.correlationMatrix
    const volatilities = Array.from({ length: nAssets }, () => 0.15 + Math.random() * 0.15) // 15-30% волатильность
    
    const covMatrix: number[][] = []
    for (let i = 0; i < nAssets; i++) {
      const row: number[] = []
      for (let j = 0; j < nAssets; j++) {
        let correlation = 0.3
        if (correlationMatrix.length > i && correlationMatrix[i]?.values?.[j] !== undefined) {
          correlation = correlationMatrix[i].values[j]
        } else if (i === j) {
          correlation = 1.0
        }
        row.push(correlation * volatilities[i] * volatilities[j])
      }
      covMatrix.push(row)
    }
    
    // Преобразуем сценарии в формат API
    const apiScenarios: StressScenario[] = scenarios.value.map(s => ({
      name: s.name,
      key: s.key,
      type: s.type,
      return_multiplier: s.return_multiplier,
      volatility_multiplier: s.volatility_multiplier,
      correlation_multiplier: s.correlation_multiplier,
      seed: 42
    }))
    
    // Вызываем API
    const response = await runStressTests({
      mu,
      cov_matrix: covMatrix,
      initial_capital: 1000000,
      risk_free_rate: 0.1394, // 13.94% безрисковая ставка
      gamma: 3.0,
      scenarios: apiScenarios,
      asset_names: assetNames,
      n_paths: 1000,
      seed: 42
    })
    
    stressTestResults.value = response
    
    // Обновляем данные сценариев с результатами API
    scenarios.value.forEach(scenario => {
      const result = response.results[scenario.key]
      if (result) {
        const baselineCapital = response.baseline.initial_capital
        scenario.pnlImpact = -(baselineCapital - result.metrics.mean_final)
        scenario.varChange = ((baselineCapital - result.metrics.var_95) / baselineCapital) * 100
      }
    })
    
    showToast('Стресс-тестирование завершено', 'success')
  } catch (e) {
    console.error('Ошибка стресс-тестирования:', e)
    showToast('Ошибка при выполнении стресс-тестирования', 'error')
  } finally {
    isRunning.value = false
  }
}
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.page-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px 32px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 4px;
  flex-shrink: 0;
  gap: 20px;
}

.header-left {
  display: flex;
  flex-direction: column;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #fff;
  letter-spacing: -0.01em;
}

.section-subtitle {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  margin: 0;
}

/* ============================================
   GLASS COMPONENTS
   ============================================ */
.glass-card {
  border-radius: 20px;
  overflow: hidden;
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 20px 40px -10px rgba(0,0,0,0.4);
}

.glass-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 16px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 99px;
  height: 40px;
  flex-shrink: 0;
}

.lbl-mini {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.scrub-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 80px;
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  outline: none;
  cursor: pointer;
}

.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 14px;
  height: 14px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: grab;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.range-slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: grab;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
  border: none;
}

.scrub-val {
  font-family: "SF Mono", monospace;
  font-weight: 700;
  font-size: 13px;
  width: 35px;
  text-align: right;
  white-space: nowrap;
}

.panel {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-header h3 {
  margin: 0;
  font-size: 11px;
  font-weight: 600;
  color: rgba(255,255,255,0.5);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.divider {
  height: 1px;
  background: rgba(255,255,255,0.08);
  margin: 4px 0;
}

/* ============================================
   SCENARIOS GRID
   ============================================ */
.scenarios-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.scenario-card {
  padding: 20px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 160px;
  position: relative;
  transition: all 0.2s;
}

.scenario-card:hover {
  transform: translateY(-3px);
  background: rgba(255,255,255,0.05);
}

.scenario-card.active {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.4);
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.15);
}

.sc-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  gap: 8px;
}

.sc-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sc-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.scenario-card:hover .sc-actions {
  opacity: 1;
}

.btn-icon-sm {
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  background: rgba(255,255,255,0.1);
  border-radius: 6px;
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon-sm:hover {
  background: rgba(255,255,255,0.2);
  color: #fff;
}

.btn-icon-sm.btn-danger:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.add-scenario-card {
  border: 2px dashed rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.02);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 160px;
}

.add-scenario-card:hover {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.05);
}

.add-scenario-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: rgba(255,255,255,0.5);
}

.add-scenario-text {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
}

.sc-name {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
  flex: 1;
}

.sc-desc {
  font-size: 12px;
  color: rgba(255,255,255,0.5);
  line-height: 1.4;
  flex-grow: 1;
  margin: 0;
}

.sc-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-top: 12px;
  gap: 8px;
}

.sc-impact {
  font-family: "SF Mono", monospace;
  font-weight: 700;
  font-size: 16px;
  letter-spacing: -0.02em;
}

.sc-prob {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
  font-weight: 500;
}

.badge {
  font-size: 9px;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 700;
  letter-spacing: 0.05em;
  white-space: nowrap;
  flex-shrink: 0;
}

.badge.critical {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.badge.high {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
}

.badge.medium {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

/* ============================================
   DASHBOARD SPLIT VIEW
   ============================================ */
.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  align-items: start;
}

.col-left,
.col-right {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sticky-panel {
  position: sticky;
  top: 20px;
}

/* Impact Metrics */
.impact-metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.metric-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: rgba(255,255,255,0.03);
  padding: 12px;
  border-radius: 10px;
}

.metric-box .lbl {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.metric-box .val {
  font-family: "SF Mono", monospace;
  font-weight: 600;
  font-size: 16px;
  line-height: 1;
}

/* Asset Bars */
.impact-bars-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bar-row {
  display: grid;
  grid-template-columns: 100px 1fr 60px;
  align-items: center;
  gap: 12px;
}

.bar-label {
  font-size: 12px;
  color: rgba(255,255,255,0.7);
  font-weight: 500;
}

.bar-track {
  height: 6px;
  background: rgba(255,255,255,0.05);
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.bar-val {
  font-family: "SF Mono", monospace;
  font-size: 12px;
  text-align: right;
  font-weight: 600;
}

/* Stats Grid Row */
.stats-grid-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: rgba(255,255,255,0.03);
  padding: 10px;
  border-radius: 8px;
}

.lbl-sm {
  font-size: 9px;
  color: rgba(255,255,255,0.4);
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.val-sm {
  font-family: "SF Mono", monospace;
  font-weight: 600;
  font-size: 13px;
}

/* Market Changes */
.market-changes-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.market-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  padding-bottom: 8px;
  font-size: 13px;
}

.market-row:last-child {
  border-bottom: none;
}

.m-key {
  color: rgba(255,255,255,0.6);
  font-weight: 500;
}

.m-val {
  font-family: "SF Mono", monospace;
  font-weight: 600;
}

.info-block {
  background: rgba(255,255,255,0.02);
  padding: 12px;
  border-radius: 8px;
  border-left: 2px solid rgba(59, 130, 246, 0.3);
}

.text-xs {
  font-size: 11px;
  line-height: 1.5;
}

/* ============================================
   TABLE
   ============================================ */
.table-wrapper {
  overflow-x: auto;
  border-radius: 0 0 20px 20px;
}

.glass-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.glass-table th {
  text-align: right;
  padding: 12px 12px;
  color: rgba(255,255,255,0.4);
  font-weight: 600;
  font-size: 10px;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.02);
}

.glass-table th.col-left {
  text-align: left;
  padding-left: 20px;
}

.glass-table td {
  text-align: right;
  padding: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  font-family: "SF Mono", monospace;
  color: #fff;
  font-weight: 500;
}

.glass-table td.col-left {
  text-align: left;
  font-family: inherit;
  font-weight: 500;
  padding-left: 20px;
}

.hover-row {
  cursor: pointer;
  transition: background 0.1s;
}

.hover-row:hover {
  background: rgba(255,255,255,0.05);
}

.row-active {
  background: rgba(59, 130, 246, 0.1) !important;
}

.sc-name-sm {
  font-weight: 600;
  font-size: 13px;
}

.pl-4 {
  padding-left: 20px !important;
}

/* ============================================
   BUTTONS & UTILS
   ============================================ */
.btn-glass {
  height: 40px;
  padding: 0 16px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-glass.primary {
  background: #3b82f6;
  color: #fff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-glass.primary:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-glass:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.footer-notes {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  font-size: 11px;
  justify-content: center;
  color: rgba(255,255,255,0.3);
  flex-wrap: wrap;
}

.note-item {
  white-space: nowrap;
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.gap-2 {
  gap: 8px;
}

.text-red { color: #f87171; }
.text-green { color: #4ade80; }
.text-orange { color: #fbbf24; }
.text-white { color: #fff; }
.text-accent { color: #3b82f6; }
.text-muted { color: rgba(255,255,255,0.4); }
.font-bold { font-weight: 700; }

.bg-red { background: #f87171; }
.bg-green { background: #4ade80; }

.spinner-mini {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ============================================
   MODAL & FORM
   ============================================ */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow-y: auto;
}

.scenario-editor-modal {
  background: rgba(20, 22, 28, 0.95);
  backdrop-filter: blur(50px) saturate(200%);
  -webkit-backdrop-filter: blur(50px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  box-shadow: 
    0 30px 60px -15px rgba(0, 0, 0, 0.8),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.02);
  flex-shrink: 0;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  letter-spacing: -0.01em;
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.scenario-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  font-size: 12px;
  font-weight: 700;
  color: rgba(255,255,255,0.5);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.glass-input {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 10px 14px;
  color: #fff;
  font-size: 13px;
  font-family: inherit;
  outline: none;
  transition: all 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.glass-input:focus {
  background: rgba(0, 0, 0, 0.4);
  border-color: rgba(59, 130, 246, 0.5);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.glass-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.form-hint {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
  font-style: italic;
}

.market-changes-editor,
.asset-impact-editor {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.market-change-row,
.asset-impact-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 10px;
  align-items: center;
}

.btn-add {
  margin-top: 4px;
  width: 100%;
  justify-content: center;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.08);
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .scenario-editor-modal,
.modal-fade-leave-to .scenario-editor-modal {
  transform: scale(0.95) translateY(20px);
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1200px) {
  .scenarios-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .impact-metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-grid-row {
    grid-template-columns: 1fr;
  }

  .sticky-panel {
    position: relative;
    top: 0;
  }
}

@media (max-width: 768px) {
  .page-container {
    gap: 16px;
    padding: 16px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-right {
    width: 100%;
    flex-direction: column;
  }

  .glass-pill {
    width: 100%;
    justify-content: space-between;
  }

  .btn-glass {
    flex: 1;
  }

  .scenarios-grid {
    grid-template-columns: 1fr;
  }

  .section-title {
    font-size: 24px;
  }

  .table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 12px;
    gap: 12px;
  }
  .section-title {
    font-size: 18px;
  }
  .chart-container {
    height: 250px;
  }
  .chart-container.tall {
    height: 300px;
  }
  .scenarios-grid {
    gap: 12px;
  }
  .impact-metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .scenario-editor-modal {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }
  
  .modal-body {
    padding: 16px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .market-change-row,
  .asset-impact-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions .btn-glass {
    width: 100%;
  }
}

@media (max-width: 375px) {
  .page-container {
    padding: 10px;
    gap: 10px;
  }

  .section-title {
    font-size: 16px;
  }

  .section-subtitle {
    font-size: 10px;
  }

  .chart-container {
    height: 200px;
  }

  .chart-container.tall {
    height: 250px;
  }

  .scenarios-grid {
    gap: 10px;
  }

  .scenario-card {
    padding: 12px;
  }

  .modal-body {
    padding: 12px;
  }

  .btn-glass {
    min-height: 44px;
  }
}
</style>