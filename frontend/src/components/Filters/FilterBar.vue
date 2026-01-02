<template>
  <div class="filter-bar-container">
    <div class="filter-bar">
      <!-- Date Range -->
      <div class="filter-group">
        <label class="filter-label">
          <svg class="filter-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
          </svg>
          Период
        </label>
        <div class="date-range-inputs">
          <input
            v-model="dateFrom"
            type="date"
            class="filter-input"
            placeholder="От"
            @change="applyFilters"
          />
          <span class="date-separator">—</span>
          <input
            v-model="dateTo"
            type="date"
            class="filter-input"
            placeholder="До"
            @change="applyFilters"
          />
        </div>
      </div>

      <!-- Portfolio Selector -->
      <div class="filter-group">
        <label class="filter-label">
          <svg class="filter-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
          </svg>
          Портфель
        </label>
        <select 
          v-model="selectedPortfolio"
          class="filter-input select-input"
          @change="applyFilters"
        >
          <option value="">Все портфели</option>
          <option value="main">Основной портфель</option>
          <option value="hedge">Хеджирующий портфель</option>
          <option value="spec">Спекулятивный</option>
        </select>
      </div>

      <!-- Model Selector -->
      <div class="filter-group">
        <label class="filter-label">
          <svg class="filter-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
            <polyline points="13 2 13 9 20 9" />
          </svg>
          Модель
        </label>
        <select
          v-model="store.selectedModel"
          class="filter-input select-input"
          @change="applyFilters"
        >
          <option value="gaussian">Gaussian (Black-Scholes)</option>
          <option value="levy">Lévy Process</option>
          <option value="jump">Jump-Diffusion</option>
          <option value="hmm">Hidden Markov Model</option>
        </select>
      </div>

      <!-- Spacer -->
      <div class="filter-spacer"></div>

      <!-- Action Buttons -->
      <div class="filter-actions">
        <button
          @click="applyFilters"
          class="btn-apply"
          :disabled="isLoading"
        >
          <svg v-if="!isLoading" class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12" />
          </svg>
          <span v-else class="spinner-mini"></span>
          {{ isLoading ? 'Загрузка...' : 'Применить' }}
        </button>

        <button
          @click="resetFilters"
          class="btn-reset"
          title="Вернуть стандартные значения"
        >
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10" />
            <polyline points="1 20 1 14 7 14" />
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36M20.49 15a9 9 0 0 1-14.85 3.36" />
          </svg>
          Сброс
        </button>
      </div>
    </div>

    <!-- Quick Filters Chips -->
    <div class="quick-filters">
      <button 
        v-for="preset in timePresets" 
        :key="preset.id"
        @click="applyPreset(preset)"
        class="filter-chip"
        :class="{ active: isPresetActive(preset) }"
      >
        {{ preset.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'

const store = usePortfolioStore()

// State
const selectedPortfolio = ref('')
const dateFrom = ref(getDefaultDateFrom())
const dateTo = ref(new Date().toISOString().split('T')[0])
const isLoading = ref(false)

// Time presets
const timePresets = [
  { id: '1w', label: '1W', days: 7 },
  { id: '1m', label: '1M', days: 30 },
  { id: '3m', label: '3M', days: 90 },
  { id: '6m', label: '6M', days: 180 },
  { id: '1y', label: '1Y', days: 365 }
]

// Methods
function getDefaultDateFrom() {
  const date = new Date()
  date.setDate(date.getDate() - 60) // 60 дней назад
  return date.toISOString().split('T')[0]
}

function applyFilters() {
  isLoading.value = true
  setTimeout(() => {
    console.log('Filters applied:', {
      portfolio: selectedPortfolio.value,
      dateFrom: dateFrom.value,
      dateTo: dateTo.value,
      model: store.selectedModel
    })
    store.fetchPriceHistory('SPY', 60)
    store.fetchHeatmapData()
    isLoading.value = false
  }, 300)
}

function resetFilters() {
  selectedPortfolio.value = ''
  dateFrom.value = getDefaultDateFrom()
  dateTo.value = new Date().toISOString().split('T')[0]
  store.selectedModel = 'gaussian'
  applyFilters()
}

function applyPreset(preset: any) {
  const today = new Date()
  const from = new Date(today)
  from.setDate(from.getDate() - preset.days)
  
  dateFrom.value = from.toISOString().split('T')[0]
  dateTo.value = today.toISOString().split('T')[0]
  applyFilters()
}

function isPresetActive(preset: any) {
  const from = new Date(dateFrom.value)
  const to = new Date(dateTo.value)
  const today = new Date()
  const expectedFrom = new Date(today)
  expectedFrom.setDate(expectedFrom.getDate() - preset.days)
  
  return from.toDateString() === expectedFrom.toDateString() &&
         to.toDateString() === today.toDateString()
}
</script>

<style scoped lang="css">
:root {
  --color-bg-primary: #0f0f1e;
  --color-bg-secondary: #1a1a2e;
  --color-bg-tertiary: #16213e;
  --color-bg-glass: rgba(26, 26, 46, 0.4);
  --color-accent-primary: #00d9ff;
  --color-accent-secondary: #ff006e;
  --color-accent-success: #00ff88;
  --color-text-primary: #e0e0e0;
  --color-text-secondary: #a0a0a0;
  --color-text-tertiary: #707080;
  --color-border: rgba(255, 255, 255, 0.08);
  --color-border-hover: rgba(255, 255, 255, 0.16);
  --spacing-xs: 0.5rem;
  --spacing-sm: 1rem;
  --spacing-md: 1.5rem;
  --spacing-lg: 2rem;
  --radius-md: 1rem;
  --duration-normal: 300ms;
}

[data-theme="light"] {
  --color-bg-secondary: #f8f9fa;
  --color-bg-tertiary: #f0f1f5;
  --color-bg-glass: rgba(248, 249, 250, 0.7);
  --color-text-primary: #1a1a2e;
  --color-text-secondary: #6b7280;
  --color-text-tertiary: #9ca3af;
}

.filter-bar-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.filter-bar {
  display: flex;
  gap: var(--spacing-md);
  align-items: flex-end;
  flex-wrap: wrap;
  padding: var(--spacing-md);
  background: var(--color-bg-glass);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  min-width: 160px;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.filter-icon {
  width: 14px;
  height: 14px;
  opacity: 0.7;
}

.date-range-inputs {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.filter-input {
  padding: 10px 12px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  color: var(--color-text-primary);
  font-size: 0.9rem;
  outline: none;
  transition: all var(--duration-normal);
  font-family: 'Courier New', monospace;
  min-width: 0;
}

.filter-input:focus {
  border-color: var(--color-accent-primary);
  box-shadow: 0 0 12px rgba(0, 217, 255, 0.2);
  background: var(--color-bg-tertiary);
}

.filter-input::placeholder {
  color: var(--color-text-tertiary);
}

.select-input {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2300d9ff' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 28px;
}

.date-separator {
  color: var(--color-text-tertiary);
  font-weight: 600;
  flex-shrink: 0;
}

.filter-spacer {
  flex: 1;
}

.filter-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.btn-apply,
.btn-reset {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: 10px 16px;
  border: none;
  border-radius: 0.75rem;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all var(--duration-normal);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.btn-apply {
  background: linear-gradient(135deg, var(--color-accent-primary), #00d9ff);
  color: var(--color-bg-primary);
}

.btn-apply:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 217, 255, 0.4);
}

.btn-apply:disabled {
  opacity: 0.8;
  cursor: wait;
}

.btn-reset {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
}

.btn-reset:hover {
  border-color: var(--color-border-hover);
  color: var(--color-text-primary);
  background: var(--color-bg-secondary);
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.spinner-mini {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(15, 15, 30, 0.3);
  border-top: 2px solid var(--color-bg-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Quick Filters */
.quick-filters {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
  padding: 0 var(--spacing-md);
}

.filter-chip {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 2rem;
  color: var(--color-text-secondary);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  transition: all var(--duration-normal);
}

.filter-chip:hover {
  border-color: var(--color-border-hover);
  color: var(--color-text-primary);
}

.filter-chip.active {
  background: linear-gradient(135deg, rgba(0, 217, 255, 0.2), rgba(255, 0, 110, 0.2));
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
}

/* Responsive */
@media (max-width: 1024px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    min-width: 100%;
  }

  .filter-spacer {
    display: none;
  }

  .filter-actions {
    width: 100%;
  }

  .btn-apply,
  .btn-reset {
    flex: 1;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .filter-bar {
    padding: var(--spacing-sm);
    gap: var(--spacing-sm);
  }

  .quick-filters {
    padding: 0 var(--spacing-sm);
  }

  .filter-input,
  .btn-apply,
  .btn-reset {
    font-size: 0.85rem;
    padding: 8px 10px;
  }

  .date-range-inputs {
    width: 100%;
  }

  .filter-input {
    flex: 1;
  }
}
</style>