<!-- src/pages/SettingsView.vue -->
<template>
  <div class="page-container">

    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Настройки</h1>
        <p class="section-subtitle">Конфигурация моделей и интерфейса</p>
      </div>
      <button @click="saveSettings" class="btn-glass primary btn-save" :class="{ 'has-changes': hasChanges }" :disabled="!hasChanges">
        <span v-if="hasChanges">Сохранить</span>
        <span v-else>Сохранено</span>
      </button>
    </div>

    <!-- Horizontal Tabs Navigation -->
    <div class="tabs-navigation">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="tab-item"
        :class="{ active: activeTab === tab.id }"
      >
        <span class="tab-label">{{ tab.name }}</span>
      </button>
    </div>

    <!-- Content Grid Layout -->
    <div class="settings-grid">

      <!-- Tab: GENERAL -->
      <transition name="fade" mode="out-in">
      <div v-show="activeTab === 'general'" class="grid-content">

        <div class="glass-panel settings-block">
          <h3 class="block-title">Интерфейс</h3>
          <div class="control-group">
            <div class="control-row">
              <label>Тема оформления</label>
              <div class="segmented-control">
                <button :class="{ active: settings.general.theme === 'dark' }" @click="settings.general.theme = 'dark'">Тёмная</button>
                <button :class="{ active: settings.general.theme === 'light' }" @click="settings.general.theme = 'light'">Светлая</button>
                <button :class="{ active: settings.general.theme === 'auto' }" @click="settings.general.theme = 'auto'">Авто</button>
              </div>
            </div>

            <div class="divider"></div>

            <div class="control-row">
              <label>Язык интерфейса</label>
              <div class="control-right">
                <select v-model="settings.general.language" class="glass-select">
                  <option value="ru">Русский</option>
                  <option value="en">English</option>
                  <option value="de">Deutsch</option>
                </select>
              </div>
            </div>

            <div class="divider"></div>

            <div class="control-row">
              <label>Валюта портфеля</label>
              <div class="control-right">
                <select v-model="settings.general.currency" class="glass-select">
                  <option value="RUB">RUB (₽)</option>
                  <option value="RUB">RUB (₽)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="CNY">CNY (¥)</option>
                </select>
              </div>
            </div>
          </div>
        </div>

      </div>
      </transition>

      <!-- Tab: MODELS -->
      <transition name="fade" mode="out-in">
      <div v-show="activeTab === 'models'" class="grid-content">

        <div class="glass-panel settings-block">
          <h3 class="block-title">Модели Оптимизации</h3>
          <div class="control-group">
            <div class="control-row">
              <div class="label-group">
                <label>Алгоритм весов</label>
                <span class="sub-label">Метод ребалансировки портфеля</span>
              </div>
              <div class="control-right">
                <select v-model="settings.models.portfolioModel" class="glass-select">
                  <option value="markowitz">Markowitz (Mean-Variance)</option>
                  <option value="black-litterman">Black-Litterman</option>
                  <option value="risk-parity">Risk Parity (ERC)</option>
                  <option value="hrp">Hierarchical Risk Parity</option>
                </select>
              </div>
            </div>

            <div class="divider"></div>

            <div class="control-row">
              <div class="label-group">
                <label>Модель VaR</label>
                <span class="sub-label">Оценка хвостового риска</span>
              </div>
              <div class="control-right">
                <select v-model="settings.models.varModel" class="glass-select">
                  <option value="historical">Историческая (Historical)</option>
                  <option value="parametric">Параметрическая (Normal)</option>
                  <option value="cornish">Cornish-Fisher (Modified)</option>
                  <option value="gpd">Extreme Value Theory (GPD)</option>
                </select>
              </div>
            </div>

            <div class="divider"></div>

            <div class="control-row">
              <label>Доверительный интервал</label>
              <div class="control-right">
                <select v-model="settings.models.varConfidence" class="glass-select">
                  <option value="0.90">90.0%</option>
                  <option value="0.95">95.0%</option>
                  <option value="0.99">99.0%</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div class="glass-panel settings-block">
          <h3 class="block-title">Обработка данных</h3>
          <div class="control-group">
            <div class="control-row">
              <label>Скользящее окно (Rolling Window)</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.models.useRollingWindow">
                <span class="slider"></span>
              </label>
            </div>

            <div class="divider"></div>

            <div class="control-row">
              <label>EWMA (Экспоненциальное взвешивание)</label>
              <label class="switch">
                <input type="checkbox" v-model="settings.models.exponentialWeighting">
                <span class="slider"></span>
              </label>
            </div>
          </div>
        </div>

      </div>
      </transition>

      <!-- Tab: RISK -->
      <transition name="fade" mode="out-in">
      <div v-show="activeTab === 'risk'" class="grid-content">

        <div class="glass-panel settings-block">
          <h3 class="block-title">Глобальные Лимиты</h3>
          <div class="control-group risk-limits">
            <div class="control-row">
              <label>Макс. VaR портфеля</label>
              <div class="input-wrapper">
                <input type="number" v-model.number="settings.risk.maxVaR" class="glass-input right-align">
                <span class="unit">%</span>
              </div>
            </div>

            <div class="divider"></div>

            <div class="control-row">
              <label>Макс. концентрация (на актив)</label>
              <div class="input-wrapper">
                <input type="number" v-model.number="settings.risk.maxConcentration" class="glass-input right-align">
                <span class="unit">%</span>
              </div>
            </div>

            <div class="divider"></div>

            <div class="control-row">
              <label>Мин. коэффициент Шарпа</label>
              <div class="input-wrapper">
                <input type="number" v-model.number="settings.risk.minSharpeRatio" class="glass-input right-align" step="0.1">
              </div>
            </div>
          </div>
        </div>

        <div class="glass-panel settings-block">
          <h3 class="block-title">Автоматизация</h3>
          <div class="control-group">
            <div class="control-row">
              <div class="label-group">
                <label>Автоматическое стресс-тестирование</label>
                <span class="sub-label">Запускать при каждом обновлении весов</span>
              </div>
              <label class="switch">
                <input type="checkbox" v-model="settings.risk.enableStressTesting">
                <span class="slider"></span>
              </label>
            </div>
          </div>
        </div>

      </div>
      </transition>

      <!-- Tab: CONNECTIONS -->
      <transition name="fade" mode="out-in">
      <div v-show="activeTab === 'connections'" class="grid-content">

        <!-- Backend URL -->
        <div class="glass-panel settings-block">
          <h3 class="block-title">Backend URL</h3>
          <div class="control-group">
            <div class="control-row">
              <label>Режим подключения</label>
              <div class="segmented-control">
                <button :class="{ active: backendMode === 'cloud' }" @click="setBackendMode('cloud')">Cloud</button>
                <button :class="{ active: backendMode === 'local' }" @click="setBackendMode('local')">Local</button>
              </div>
            </div>
            <div class="divider"></div>
            <div class="control-row vertical">
              <label>URL бэкенда</label>
              <input
                type="text"
                v-model="backendUrl"
                class="glass-input full font-mono"
                :placeholder="backendMode === 'cloud' ? 'https://zeta-terminal-backend.onrender.com' : 'http://localhost:8000'"
                :disabled="backendMode === 'cloud'"
              >
            </div>
          </div>
          <div class="status-footer">
            <button class="btn-glass xs" @click="testBackendConnection" :disabled="backendTestLoading">
              {{ backendTestLoading ? 'Проверка...' : 'Проверить' }}
            </button>
            <span class="status-text" :class="backendTestStatus.class">
              {{ backendTestStatus.text }}
            </span>
          </div>
        </div>

        <!-- Cbonds API Section -->
        <div class="glass-panel settings-block">
          <h3 class="block-title">Cbonds API</h3>
          <div class="control-group">
            <div class="control-row vertical">
              <label>Login</label>
              <input type="text" v-model="settings.api.cbondsLogin" class="glass-input full" placeholder="username@company.com">
            </div>
            <div class="divider"></div>
            <div class="control-row vertical">
              <label>Password</label>
              <input type="password" v-model="settings.api.cbondsPassword" class="glass-input full" placeholder="••••••••">
            </div>
          </div>
          <div class="status-footer">
            <button class="btn-glass xs" @click="testConnection('cbonds')">Проверить</button>
            <span class="status-text" :class="getConnectionStatus('cbonds').class">
              {{ getConnectionStatus('cbonds').text }}
            </span>
          </div>
        </div>

        <!-- RuData API Section -->
        <div class="glass-panel settings-block">
          <h3 class="block-title">RuData / Interfax</h3>
          <div class="control-group">
            <div class="control-row vertical">
              <label>Login</label>
              <input type="text" v-model="settings.api.rudataLogin" class="glass-input full" placeholder="login">
            </div>
            <div class="divider"></div>
            <div class="control-row vertical">
              <label>Password</label>
              <input type="password" v-model="settings.api.rudataPassword" class="glass-input full" placeholder="••••••••">
            </div>
          </div>
          <div class="status-footer">
            <button class="btn-glass xs" @click="testConnection('rudata')">Проверить</button>
            <span class="status-text" :class="getConnectionStatus('rudata').class">
              {{ getConnectionStatus('rudata').text }}
            </span>
          </div>
        </div>

      </div>
      </transition>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, reactive, computed, onMounted } from 'vue'
import {
  createSession as createRuDataSession,
  hasActiveSession as hasRuDataSession,
  getSessionLogin as getRuDataSessionLogin,
} from '@/services/rudataService'
import { getApiBaseUrl, setApiBaseUrl } from '@/utils/apiBase'

const activeTab = ref('general')
const hasChanges = ref(true)

// Backend URL state
const backendMode = ref<'cloud' | 'local'>('cloud')
const backendUrl = ref('')
const backendTestLoading = ref(false)
const backendTestResult = ref<'idle' | 'success' | 'error'>('idle')
const backendTestMessage = ref('')

const backendTestStatus = computed(() => {
  if (backendTestResult.value === 'success') return { text: 'OK', class: 'text-green' }
  if (backendTestResult.value === 'error') return { text: backendTestMessage.value || 'Error', class: 'text-red' }
  return { text: '', class: 'text-muted' }
})

function setBackendMode(mode: 'cloud' | 'local') {
  backendMode.value = mode
  backendTestResult.value = 'idle'
  if (mode === 'cloud') {
    backendUrl.value = import.meta.env.VITE_API_BASE_URL || ''
    setApiBaseUrl('')
  } else {
    backendUrl.value = 'http://localhost:8000'
  }
}

async function testBackendConnection() {
  const url = backendMode.value === 'cloud'
    ? (import.meta.env.VITE_API_BASE_URL || '')
    : backendUrl.value.replace(/\/+$/, '')
  backendTestLoading.value = true
  backendTestResult.value = 'idle'
  try {
    const resp = await fetch(`${url}/health`, { method: 'GET' })
    if (resp.ok) {
      backendTestResult.value = 'success'
      if (backendMode.value === 'local') {
        setApiBaseUrl(backendUrl.value.replace(/\/+$/, ''))
      }
    } else {
      backendTestResult.value = 'error'
      backendTestMessage.value = `HTTP ${resp.status}`
    }
  } catch {
    backendTestResult.value = 'error'
    backendTestMessage.value = 'Connection failed'
  } finally {
    backendTestLoading.value = false
  }
}

const tabs = [
  { id: 'general', name: 'Общие' },
  { id: 'models', name: 'Модели' },
  { id: 'risk', name: 'Риск' },
  { id: 'connections', name: 'Подключения' },
]

// Connection States
const connectionStates = reactive({
    cbonds: { status: 'idle', message: '' },
    rudata: { status: 'idle', message: '' }
})

const settings = reactive({
  general: { theme: 'dark', language: 'ru', currency: 'RUB' },
  models: {
    portfolioModel: 'markowitz', varModel: 'parametric', varConfidence: '0.95',
    useRollingWindow: true, exponentialWeighting: false
  },
  risk: {
    maxVaR: 5.0, maxConcentration: 25, minSharpeRatio: 1.2, enableStressTesting: true
  },
  api: {
      cbondsLogin: '', cbondsPassword: '',
      rudataLogin: '', rudataPassword: '',
      bloombergKey: '', webhookUrl: ''
  },
})

// Загрузка сохраненных credentials при монтировании
onMounted(() => {
  // Check if a server-side RuData session is active (memory-only)
  if (hasRuDataSession()) {
    const login = getRuDataSessionLogin()
    if (login) {
      settings.api.rudataLogin = login
    }
    connectionStates.rudata.status = 'saved'
  }

  // Загружаем другие настройки из localStorage
  const savedSettings = localStorage.getItem('app_settings')
  if (savedSettings) {
    try {
      const parsed = JSON.parse(savedSettings)
      if (parsed.general) Object.assign(settings.general, parsed.general)
      if (parsed.models) Object.assign(settings.models, parsed.models)
      if (parsed.risk) Object.assign(settings.risk, parsed.risk)
      if (parsed.api?.cbondsLogin) settings.api.cbondsLogin = parsed.api.cbondsLogin
      if (parsed.api?.cbondsPassword) settings.api.cbondsPassword = parsed.api.cbondsPassword
    } catch (e) {
      // Failed to load settings
    }
  }

  // Загружаем backend URL state
  const savedUrl = getApiBaseUrl()
  const defaultUrl = import.meta.env.VITE_API_BASE_URL || ''
  if (savedUrl && savedUrl !== defaultUrl) {
    backendMode.value = 'local'
    backendUrl.value = savedUrl
  } else {
    backendMode.value = 'cloud'
    backendUrl.value = defaultUrl
  }

  hasChanges.value = false
})

// UI Helpers
const getConnectionStatus = (provider: 'cbonds' | 'rudata') => {
    const s = connectionStates[provider].status
    const msg = connectionStates[provider].message
    if (s === 'checking') return { text: 'Проверка...', class: 'text-blue' }
    if (s === 'success') return { text: 'Подключено', class: 'text-green' }
    if (s === 'error') return { text: msg || 'Ошибка авторизации', class: 'text-red' }
    if (s === 'saved') return { text: 'Сохранено', class: 'text-muted' }
    return { text: 'Не подключено', class: 'text-muted' }
}

const testConnection = async (provider: 'cbonds' | 'rudata') => {
    connectionStates[provider].status = 'checking'
    connectionStates[provider].message = ''

    if (provider === 'rudata') {
      // Реальная проверка подключения к RuData API
      const login = settings.api.rudataLogin
      const password = settings.api.rudataPassword

      if (!login || !password) {
        connectionStates[provider].status = 'error'
        connectionStates[provider].message = 'Введите логин и пароль'
        return
      }

      try {
        const result = await createRuDataSession({ login, password })

        if (result.success) {
          connectionStates[provider].status = 'success'
          connectionStates[provider].message = result.message
        } else {
          connectionStates[provider].status = 'error'
          connectionStates[provider].message = result.message
        }
      } catch (error: unknown) {
        const msg = error instanceof Error ? error.message : String(error)
        connectionStates[provider].status = 'error'
        connectionStates[provider].message = msg || 'Ошибка соединения'
      }
    } else if (provider === 'cbonds') {
      // Cbonds пока симулируем
      setTimeout(() => {
        if (settings.api.cbondsLogin && settings.api.cbondsPassword) {
          connectionStates[provider].status = 'success'
        } else {
          connectionStates[provider].status = 'error'
          connectionStates[provider].message = 'Введите логин и пароль'
        }
      }, 1200)
    }
}

const saveSettings = () => {
  // RuData credentials are cached server-side via createSession (no localStorage)

  // Сохраняем остальные настройки в localStorage
  const settingsToSave = {
    general: settings.general,
    models: settings.models,
    risk: settings.risk,
    api: {
      cbondsLogin: settings.api.cbondsLogin,
      cbondsPassword: settings.api.cbondsPassword,
      bloombergKey: settings.api.bloombergKey,
      webhookUrl: settings.api.webhookUrl
    }
  }

  localStorage.setItem('app_settings', JSON.stringify(settingsToSave))

  // Сохраняем backend URL
  if (backendMode.value === 'local' && backendUrl.value) {
    setApiBaseUrl(backendUrl.value.replace(/\/+$/, ''))
  } else {
    setApiBaseUrl('')
  }

  hasChanges.value = false
  setTimeout(() => hasChanges.value = true, 2000)
}

watch(settings, () => { hasChanges.value = true }, { deep: true })
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.page-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px 32px;
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  flex-direction: column;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 4px 0;
  letter-spacing: -0.01em;
}

.section-subtitle {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  margin: 0;
}

.btn-save {
  height: 36px;
  padding: 0 16px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

/* ============================================
   HORIZONTAL TABS
   ============================================ */
.tabs-navigation {
  display: flex;
  gap: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  flex-shrink: 0;
  padding-bottom: 0;
  overflow-x: auto;
  scrollbar-width: none;
}

.tabs-navigation::-webkit-scrollbar {
  display: none;
}

.tab-item {
  position: relative;
  padding: 12px 20px;
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.4);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  transition: color 0.2s;
  white-space: nowrap;
  letter-spacing: 0.05em;
}

.tab-item:hover {
  color: rgba(255,255,255,0.6);
}

.tab-item.active {
  color: rgba(255,255,255,0.9);
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #3b82f6;
}

/* ============================================
   GRID CONTENT LAYOUT
   ============================================ */
.settings-grid {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.grid-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  gap: 20px;
  width: 100%;
  padding-right: 4px;
  overflow-y: auto;
  overflow-x: hidden;
}

.grid-content::-webkit-scrollbar {
  width: 6px;
}

.grid-content::-webkit-scrollbar-track {
  background: transparent;
}

.grid-content::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.1);
  border-radius: 3px;
}

.grid-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.15);
}

/* ============================================
   GLASS PANELS
   ============================================ */
.glass-panel {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px) saturate(160%);
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 10px 30px -10px rgba(0,0,0,0.3);
  overflow: hidden;
}

.settings-block {
  display: flex;
  flex-direction: column;
}

.block-title {
  margin: 0;
  padding: 16px 20px 8px 20px;
  font-size: 11px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 600;
  letter-spacing: 0.05em;
}

/* ============================================
   CONTROLS
   ============================================ */
.control-group {
  background: rgba(255, 255, 255, 0.03);
  margin: 0 16px 16px;
  padding: 0 16px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.control-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 4px;
  min-height: 48px;
}

.control-row.vertical {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  min-height: auto;
}

.control-row label {
  font-size: 13px;
  color: #fff;
  font-weight: 500;
}

.control-right {
  display: flex;
  align-items: center;
}

.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.05);
  margin: 0 -4px;
}

/* INPUT ELEMENTS */
.glass-select {
  appearance: none;
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  text-align: right;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 140px;
}

.glass-select:focus {
  border-color: #3b82f6;
  background: rgba(0,0,0,0.4);
}

.glass-select option {
  background: #1c1c1e;
  color: #fff;
}

.glass-input {
  background: rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  transition: all 0.2s;
}

.glass-input:focus {
  border-color: #3b82f6;
  background: rgba(0,0,0,0.4);
}

.glass-input.full {
  width: 100%;
  box-sizing: border-box;
}

.glass-input.right-align {
  text-align: right;
  width: 100%;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
}

.unit {
  font-size: 12px;
  color: rgba(255,255,255,0.4);
  flex-shrink: 0;
}

/* SWITCH */
.switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 22px;
  flex-shrink: 0;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background-color: rgba(255,255,255,0.15);
  border-radius: 22px;
  transition: .3s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  border-radius: 50%;
  transition: .3s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

input:checked + .slider {
  background-color: #34c759;
}

input:checked + .slider:before {
  transform: translateX(18px);
}

/* SEGMENTED CONTROL */
.segmented-control {
  background: rgba(0,0,0,0.3);
  border-radius: 8px;
  padding: 2px;
  display: flex;
  gap: 2px;
}

.segmented-control button {
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.6);
  padding: 4px 12px;
  font-size: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.segmented-control button.active {
  background: rgba(255,255,255,0.15);
  color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

/* BUTTONS */
.btn-glass {
  height: 34px;
  padding: 0 16px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
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

.btn-glass.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: rgba(255,255,255,0.1);
  box-shadow: none;
}

.btn-glass.xs {
  height: 28px;
  padding: 0 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  flex-shrink: 0;
}

.btn-glass.xs:hover {
  background: rgba(255,255,255,0.1);
}

/* ============================================
   CONNECTIONS SECTION SPECIFIC
   ============================================ */
.status-footer {
  padding: 12px 20px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255,255,255,0.02);
}

.status-text {
  font-size: 11px;
  font-weight: 500;
}

/* ============================================
   UTILITIES
   ============================================ */
.label-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sub-label {
  font-size: 11px;
  color: rgba(255,255,255,0.4);
}

.text-green { color: #4ade80; }
.text-red { color: #ef4444; }
.text-blue { color: #60a5fa; }
.text-muted { color: rgba(255,255,255,0.4); }

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .page-container {
    padding: 16px 24px;
  }

  .grid-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-container {
    gap: 16px;
    padding: 16px;
  }

  .section-title {
    font-size: 24px;
  }

  .tabs-navigation {
    gap: 4px;
  }

  .tab-item {
    padding: 10px 14px;
    font-size: 11px;
  }

  .grid-content {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 12px;
    gap: 12px;
  }

  .section-title {
    font-size: 20px;
  }

  .section-subtitle {
    font-size: 11px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .btn-save {
    width: 100%;
  }

  .tabs-navigation {
    gap: 2px;
  }

  .tab-item {
    padding: 8px 10px;
    font-size: 10px;
  }

  .grid-content {
    gap: 12px;
  }

  .settings-block {
    padding: 12px;
  }

  .block-title {
    padding: 12px 16px 6px 16px;
    font-size: 10px;
  }

  .control-group {
    margin: 0 12px 12px;
    padding: 0 12px;
  }

  .control-row {
    padding: 10px 2px;
    min-height: 40px;
  }

  .control-row label {
    font-size: 12px;
  }

  .glass-select,
  .glass-input {
    font-size: 12px;
    padding: 6px 10px;
    min-height: 44px;
  }

  /* Touch-friendly switches */
  .switch {
    min-width: 44px;
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Segmented control touch targets */
  .segmented-control button {
    min-height: 44px;
  }
}

@media (max-width: 375px) {
  .page-container {
    padding: 10px;
    gap: 10px;
  }

  .section-title {
    font-size: 18px;
  }

  .section-subtitle {
    font-size: 10px;
  }

  .tabs-navigation {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    padding-bottom: 4px;
  }

  .tab-item {
    padding: 6px 8px;
    font-size: 9px;
    white-space: nowrap;
  }

  .settings-block {
    padding: 10px;
    border-radius: 12px;
  }

  .block-title {
    padding: 10px 12px 4px 12px;
    font-size: 9px;
  }

  .control-group {
    margin: 0 8px 8px;
    padding: 0 8px;
  }

  .control-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .control-right {
    width: 100%;
  }

  .glass-select,
  .glass-input {
    width: 100%;
  }
}
</style>
