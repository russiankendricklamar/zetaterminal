<!-- src/pages/SettingsView.vue -->
<template>
  <div class="page-container">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Настройки</h1>
        <p class="section-subtitle">Настройки моделей и интерфейса</p>
      </div>
      <button @click="saveSettings" class="btn btn-save" :class="{ 'has-changes': hasChanges }" :disabled="!hasChanges">
        <span v-if="hasChanges">Сохранить изменения</span>
        <span v-else>Сохранено</span>
      </button>
    </div>

    <div class="settings-layout">
      
      <!-- Sidebar Navigation -->
      <div class="settings-sidebar">
        <div class="sidebar-menu glass-panel">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            class="menu-item"
            :class="{ active: activeTab === tab.id }"
          >
            <span class="menu-label">{{ tab.name }}</span>
            <span v-if="tab.id === 'api' && apiError" class="badge-dot"></span>
          </button>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="settings-content">
        
        <!-- Tab: GENERAL -->
        <div v-show="activeTab === 'general'" class="settings-view">
          <div class="settings-block glass-panel">
            <h3 class="block-title">Интерфейс</h3>
            <div class="control-group">
              <div class="control-row">
                <label>Тема оформления</label>
                <div class="segmented-control">
                  <button :class="{ active: settings.general.theme === 'dark' }" @click="settings.general.theme = 'dark'">Тёмная тема</button>
                  <button :class="{ active: settings.general.theme === 'light' }" @click="settings.general.theme = 'light'">Светлая тема</button>
                  <button :class="{ active: settings.general.theme === 'auto' }" @click="settings.general.theme = 'auto'">Как в системе</button>
                </div>
              </div>
              <div class="divider"></div>
              <div class="control-row">
                <label>Язык</label>
                <div class="control-right">
                  <select v-model="settings.general.language" class="glass-select">
                    <option value="ru">Русский</option>
                    <option value="en">English</option>
                    <option value="de">Deutsch</option>
                    <option value="ch">中國人</option>
                    <option value="ja">日本語</option>
                    <option value="qa">Қазақ</option>
                  </select>
                </div>
              </div>
              <div class="divider"></div>
               <div class="control-row">
                <label>Валюта портфеля</label>
                <div class="control-right">
                  <select v-model="settings.general.currency" class="glass-select">
                    <option value="RUB">RUB</option>
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="CNY">CNY</option>
                    <option value="CHF">CHF</option>
                    <option value="GBP">GBP</option>
                    <option value="JPY">JPY</option>
                    <option value="AED">AED</option>
                    <option value="QAR">QAR</option>
                    <option value="HKD">HKD</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab: MODELS -->
        <div v-show="activeTab === 'models'" class="settings-view">
          <div class="settings-block glass-panel">
            <h3 class="block-title">Оптимизация и VaR</h3>
            <div class="control-group">
              <div class="control-row">
                <div class="label-group">
                   <label>Модель оптимизации</label>
                   <span class="sub-label">Метод расчета весов</span>
                </div>
                <div class="control-right">
                  <select v-model="settings.models.portfolioModel" class="glass-select">
                    <option value="markowitz">Markowitz (Mean-Variance)</option>
                    <option value="black-litterman">Black-Litterman</option>
                    <option value="risk-parity">Risk Parity</option>
                    <option value="hrp">HRP (Hierarchical)</option>
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
                     <option value="historical">Историческая</option>
                     <option value="parametric">Параметрическая</option>
                     <option value="cornish">Cornish-Fisher</option>
                     <option value="gpd">EVT (GPD)</option>
                  </select>
                </div>
              </div>
              <div class="divider"></div>
              <div class="control-row">
                <label>Confidence Level</label>
                <div class="control-right">
                  <select v-model="settings.models.varConfidence" class="glass-select">
                    <option value="0.90">90%</option>
                    <option value="0.95">95%</option>
                    <option value="0.99">99%</option>
                  </select>
                </div>
              </div>
            </div>
            
            <h3 class="block-title mt-4">Параметры данных</h3>
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
                 <label>Экспоненциальное взвешивание (EWMA)</label>
                 <label class="switch">
                    <input type="checkbox" v-model="settings.models.exponentialWeighting">
                    <span class="slider"></span>
                 </label>
               </div>
            </div>
          </div>
        </div>

        <!-- Tab: RISK -->
        <div v-show="activeTab === 'risk'" class="settings-view">
          <div class="settings-block glass-panel">
            <h3 class="block-title">Лимиты</h3>
            <div class="control-group risk-limits">
               <div class="control-row">
                  <label>Макс. VaR портфеля</label>
                  <div class="input-wrapper">
                    <input type="number" v-model.number="settings.risk.maxVaR" class="glass-input">
                    <span class="unit">%</span>
                  </div>
               </div>
               <div class="divider"></div>
               <div class="control-row">
                  <label>Макс. концентрация (1 актив)</label>
                  <div class="input-wrapper">
                    <input type="number" v-model.number="settings.risk.maxConcentration" class="glass-input">
                    <span class="unit">%</span>
                  </div>
               </div>
               <div class="divider"></div>
               <div class="control-row">
                  <label>Мин. коэффициент Шарпа</label>
                  <div class="input-wrapper">
                    <input type="number" v-model.number="settings.risk.minSharpeRatio" class="glass-input" step="0.1">
                  </div>
               </div>
            </div>

            <h3 class="block-title mt-4">Автоматизация</h3>
             <div class="control-group">
               <div class="control-row">
                 <label>Стресс-тестирование</label>
                 <label class="switch">
                    <input type="checkbox" v-model="settings.risk.enableStressTesting">
                    <span class="slider"></span>
                 </label>
               </div>
            </div>
          </div>
        </div>

        <!-- Tab: API -->
        <div v-show="activeTab === 'api'" class="settings-view">
           
           <!-- Cbonds API Section -->
           <div class="settings-block glass-panel">
              <h3 class="block-title">Cbonds API</h3>
              <div class="control-group api-group">
                 <div class="control-row vertical">
                    <label>Логин</label>
                    <input type="text" v-model="settings.api.cbondsLogin" class="glass-input full" placeholder="username@company.com">
                 </div>
                 <div class="divider"></div>
                 <div class="control-row vertical">
                    <label>Пароль</label>
                    <input type="password" v-model="settings.api.cbondsPassword" class="glass-input full" placeholder="••••••••">
                 </div>
              </div>
              <div class="status-footer">
                  <button class="btn-xs" @click="testConnection('cbonds')">Проверить подключение</button>
                  <span class="status-text" :class="getConnectionStatus('cbonds').class">
                      {{ getConnectionStatus('cbonds').text }}
                  </span>
              </div>
           </div>

           <!-- RuData API Section -->
           <div class="settings-block glass-panel">
              <h3 class="block-title">RuData / Interfax</h3>
              <div class="control-group api-group">
                 <div class="control-row vertical">
                    <label>Логин</label>
                    <input type="text" v-model="settings.api.rudataLogin" class="glass-input full" placeholder="login">
                 </div>
                 <div class="divider"></div>
                 <div class="control-row vertical">
                    <label>Пароль</label>
                    <input type="password" v-model="settings.api.rudataPassword" class="glass-input full" placeholder="••••••••">
                 </div>
              </div>
              <div class="status-footer">
                  <button class="btn-xs" @click="testConnection('rudata')">Проверить подключение</button>
                  <span class="status-text" :class="getConnectionStatus('rudata').class">
                      {{ getConnectionStatus('rudata').text }}
                  </span>
              </div>
           </div>
           
           <!-- Global Providers -->
           <div class="settings-block glass-panel">
              <h3 class="block-title">Глобальные Провайдеры</h3>
              <div class="control-group">
                 <div class="control-row vertical">
                    <label>Bloomberg API Key</label>
                    <input type="password" v-model="settings.api.bloombergKey" placeholder="••••••••••••••••" class="glass-input full">
                 </div>
                 <div class="divider"></div>
                 <div class="control-row vertical">
                    <label>Webhook URL (Alerts)</label>
                    <input type="text" v-model="settings.api.webhookUrl" placeholder="https://hooks.slack.com/..." class="glass-input full">
                 </div>
              </div>
           </div>

           <!-- Connected Services Status -->
           <div class="settings-block glass-panel mt-4">
              <h3 class="block-title">Статус подключений</h3>
              <div class="services-list">
                 <div v-for="srv in settings.connectedServices" :key="srv.id" class="service-item">
                    <div class="srv-left">
                       <span class="srv-name">{{ srv.name }}</span>
                    </div>
                    <span class="status-indicator" :class="{ connected: srv.connected }">
                       {{ srv.connected ? 'Активно' : 'Отключено' }}
                    </span>
                 </div>
              </div>
           </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, reactive } from 'vue'

const activeTab = ref('general')
const hasChanges = ref(true)
const apiError = ref(false)

const tabs = [
  { id: 'general', name: 'Общие'},
  { id: 'models', name: 'Модели'},
  { id: 'risk', name: 'Риск-менеджмент'},
  { id: 'api', name: 'API и Данные'},
]

// Mock Connection States
const connectionStates = reactive({
    cbonds: { status: 'idle' }, 
    rudata: { status: 'idle' }
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
      cbondsLogin: '', 
      cbondsPassword: '', 
      rudataLogin: '', 
      rudataPassword: '',
      bloombergKey: '', 
      webhookUrl: '' 
  },
  connectedServices: [
    { id: 1, name: 'Cbonds', connected: false },
    { id: 2, name: 'RuData', connected: false },
    { id: 3, name: 'Bloomberg', connected: false },
    { id: 4, name: 'MOEX', connected: false }
  ]
})

// UI Helpers
const getConnectionStatus = (provider: 'cbonds' | 'rudata') => {
    const s = connectionStates[provider].status
    if (s === 'checking') return { text: 'Проверка...', class: 'text-blue' }
    if (s === 'success') return { text: 'Подключено успешно', class: 'text-green' }
    if (s === 'error') return { text: 'Ошибка авторизации', class: 'text-red' }
    return { text: 'Не проверено', class: 'text-muted' }
}

const testConnection = (provider: 'cbonds' | 'rudata') => {
    connectionStates[provider].status = 'checking'
    
    // Simulating API check
    setTimeout(() => {
        if (settings.api[`${provider}Login`] && settings.api[`${provider}Password`]) {
            connectionStates[provider].status = 'success'
            // Update the list status
            const srv = settings.connectedServices.find(s => s.name.toLowerCase().includes(provider))
            if(srv) srv.connected = true
        } else {
            connectionStates[provider].status = 'error'
        }
    }, 1200)
}

const saveSettings = () => {
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
  gap: 26px;
  padding: 28px;
  max-width: 1280px;
  margin: 0 auto;
  height: calc(100vh - 60px);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  color: #fff;
  letter-spacing: -0.02em;
}

.section-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin: 4px 0 0 0;
}

.settings-layout {
  display: flex;
  gap: 24px;
  flex: 1;
  overflow: hidden;
}

/* ============================================
   SIDEBAR
   ============================================ */
.settings-sidebar {
  width: 240px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.sidebar-menu {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
  position: relative;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.menu-item.active {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background: #f87171;
  border-radius: 50%;
  margin-left: auto;
}

/* ============================================
   CONTENT AREA
   ============================================ */
.settings-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 40px;
  padding-right: 4px;
}

.settings-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 700px;
}

.settings-block {
  padding: 0;
  overflow: hidden;
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

.mt-4 {
  margin-top: 24px;
}

.mb-group {
  margin-bottom: 16px;
}

/* ============================================
   CONTROL GROUP
   ============================================ */
.control-group {
  background: rgba(255, 255, 255, 0.03);
  margin: 0;
  padding: 0 16px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

/* API-specific control groups with extra margin */
.control-group.api-group {
  margin: 0 20px;
}

/* Risk Limits Group - выравнивание по левому краю */
.control-group.risk-limits .control-row {
  justify-content: flex-start;
  gap: 16px;
}

.control-group.risk-limits .control-row label {
  flex-shrink: 0;
  min-width: 200px;
  margin-right: 0;
}

.control-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 4px;
  min-height: 48px;
  box-sizing: border-box;
}

.control-row.vertical {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  padding: 14px 16px;
}

.control-row label {
  font-size: 13px;
  color: #fff;
  font-weight: 500;
  flex-shrink: 0;
  margin-right: 16px;
}

.control-right {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.label-group {
  display: flex;
  flex-direction: column;
}

.sub-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
}

.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.05);
  margin: 0 -4px;
}

.status-footer {
  padding: 12px 20px 16px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-text {
  font-size: 12px;
  font-weight: 500;
}

/* ============================================
   GLASS PANEL
   ============================================ */
.glass-panel {
  background: rgba(20, 22, 28, 0.4);
  backdrop-filter: blur(34px);
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

/* ============================================
   INPUTS & CONTROLS
   ============================================ */
.glass-select {
  appearance: none;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  text-align: right;
  max-width: 180px;
  flex-shrink: 0;
  cursor: pointer;
}

.glass-select:hover {
  background: rgba(0, 0, 0, 0.3);
}

.glass-select:focus {
  border-color: #60a5fa;
  background: rgba(0, 0, 0, 0.4);
}

.glass-select option {
  background: #1c1c1e;
  color: #fff;
}

.glass-input {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
}

.glass-input:focus {
  border-color: #60a5fa;
  background: rgba(0, 0, 0, 0.4);
}

.glass-input.full {
  width: 100%;
  text-align: left;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.unit {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
}

/* Segmented Control */
.segmented-control {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 3px;
  display: flex;
  gap: 2px;
  flex-shrink: 0;
}

.segmented-control button {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  padding: 4px 10px;
  font-size: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.segmented-control button:hover {
  color: #fff;
}

.segmented-control button.active {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

/* Switch */
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
  background-color: rgba(255, 255, 255, 0.15);
  border-radius: 22px;
  transition: 0.3s;
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
  transition: 0.3s;
}

input:checked + .slider {
  background-color: #4ade80;
}

input:checked + .slider:before {
  transform: translateX(18px);
}

/* Buttons */
.btn-save {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.4);
}

.btn-save.has-changes {
  background: linear-gradient(135deg, #0ea5e9, #2563eb);
  color: #fff;
  box-shadow: 0 0 15px rgba(37, 99, 235, 0.4);
}

.btn-save:disabled {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.4);
  cursor: default;
}

.btn-xs {
  padding: 6px 12px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  cursor: pointer;
  transition: 0.2s;
}

.btn-xs:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* Services List */
.services-list {
  display: flex;
  flex-direction: column;
  padding: 8px 20px;
}

.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.service-item:last-child {
  border-bottom: none;
}

.srv-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.srv-name {
  font-size: 13px;
  color: #fff;
}

.status-indicator {
  font-size: 11px;
  color: #f87171;
  flex-shrink: 0;
}

.status-indicator.connected {
  color: #4ade80;
}

/* Colors */
.text-green {
  color: #4ade80;
}

.text-red {
  color: #f87171;
}

.text-blue {
  color: #60a5fa;
}

.text-muted {
  color: rgba(255, 255, 255, 0.4);
}

@media (max-width: 1024px) {
  .settings-layout {
    flex-direction: column;
  }

  .settings-sidebar {
    width: 100%;
    flex-direction: row;
    align-items: center;
  }

  .sidebar-menu {
    flex-direction: row;
    width: 100%;
    overflow-x: auto;
  }

  .page-container {
    height: auto;
  }
}
</style>

