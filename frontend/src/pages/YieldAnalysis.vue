<template>
  <div class="page-container custom-scroll">
    
    <!-- Header & Controls -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Анализ кривых доходности</h1>
        <p class="section-subtitle">Сценарное моделирование и стресс-тестирование (Monte Carlo)</p>
      </div>
      
      <div class="header-actions">
        <!-- Selected Bank -->
        <div class="glass-pill control-pill">
           <span class="lbl-mini">Банк:</span>
           <span class="text-white font-bold">{{ selectedBank.name }}</span>
        </div>
        
        <!-- Asset Selector -->
        <div class="glass-pill control-pill asset-selector-pill" :class="{ 'is-open': isAssetMenuOpen }" @click.stop="toggleAssetMenu">
           <span class="lbl-mini">Активы:</span>
           <span class="text-white font-bold">{{ selectedAssets.length > 0 ? `${selectedAssets.length} выбрано` : 'Не выбрано' }}</span>
           <svg class="chevron" width="12" height="8" viewBox="0 0 12 8" fill="none" stroke="currentColor" stroke-width="2">
             <path d="M1 1L6 6L11 1"/>
           </svg>
        </div>
        
        <button class="btn-glass" @click="generateData">
             <span class="icon">↻</span> Обновить симуляцию
        </button>
      </div>
      
      <!-- Asset Selection Dropdown -->
      <transition name="dropdown-fade">
        <div v-if="isAssetMenuOpen" class="asset-dropdown" @click.stop>
          <div class="dropdown-header">
            <input 
              type="text" 
              v-model="assetSearchQuery" 
              placeholder="Поиск активов..."
              class="asset-search-input"
            />
            <div class="dropdown-actions">
              <button @click="selectAllAssets" class="btn-link-sm">Выбрать все</button>
              <button @click="deselectAllAssets" class="btn-link-sm">Снять все</button>
            </div>
          </div>
          <div class="asset-list">
            <label 
              v-for="asset in filteredAvailableAssets" 
              :key="asset.symbol"
              class="asset-checkbox-item"
              :class="{ 'is-selected': selectedAssets.includes(asset.symbol) }"
            >
              <input 
                type="checkbox" 
                :value="asset.symbol"
                v-model="selectedAssets"
                @change="onAssetSelectionChange"
              />
              <div class="asset-checkbox-content">
                <span class="asset-dot" :style="{ background: asset.color }"></span>
                <div class="asset-info">
                  <span class="asset-symbol">{{ asset.symbol }}</span>
                  <span class="asset-name">{{ asset.name }}</span>
                </div>
                <span class="asset-allocation">{{ asset.allocation }}%</span>
              </div>
            </label>
          </div>
        </div>
      </transition>
    </div>

    <!-- Main Content -->
    <div class="analysis-grid">
        
        <!-- Left Column: Charts -->
        <div class="charts-column">
            
            <!-- Chart 1: Daily Changes (Volatile "Spaghetti") -->
            <div class="glass-card chart-container">
                <div class="panel-header">
                    <h3>Ежедневные изменения</h3>
                    <div class="legend">
                         <span class="l-item faded"><span class="dot bg-gray"></span> Сценарии</span>
                         <span class="l-item"><span class="dot bg-green"></span> Выбросы</span>
                    </div>
                </div>
                
                <div class="chart-area big-chart">
                    <svg viewBox="0 0 1000 320" preserveAspectRatio="none" class="svg-chart">
                        <!-- Grid -->
                        <line v-for="i in 6" :key="'g1-'+i" x1="0" :y1="i*50" x2="1000" :y2="i*50" stroke="rgba(255,255,255,0.05)" />
                        <line x1="0" y1="160" x2="1000" y2="160" stroke="rgba(255,255,255,0.2)" stroke-dasharray="4"/> 

                        <!-- Daily Change Paths (Noise) -->
                        <path 
                            v-for="(path, idx) in dailyPaths" 
                            :key="'d-'+idx" 
                            :d="makePath(path, 12, -12)" 
                            fill="none" 
                            :stroke="getDailyColor(idx)" 
                            stroke-width="0.8"
                            opacity="0.5"
                            style="mix-blend-mode: screen;"
                        />
                         
                         <!-- Spike Highlighting (Green Line) -->
                         <path v-if="dailyPaths.length" :d="makePath(dailyPaths[48], 12, -12)" fill="none" stroke="#4ade80" stroke-width="2" filter="drop-shadow(0 0 4px rgba(74,222,128,0.5))" />
                    </svg>
                    <div class="chart-label">Симуляция волатильности (250 шагов)</div>
                </div>
            </div>

            <!-- Chart 2: Cumulative Changes (Trends) -->
            <div class="glass-card chart-container">
                <div class="panel-header">
                    <h3>Накопленная доходность</h3>
                    <div class="legend">
                         <span 
                           v-for="asset in selectedAssetsForDisplay" 
                           :key="asset.symbol"
                           class="l-item"
                         >
                           <span class="dot" :style="{ background: asset.color }"></span> 
                           {{ asset.symbol }}
                         </span>
                    </div>
                </div>
                
                <div class="chart-area big-chart">
                    <svg viewBox="0 0 1000 320" preserveAspectRatio="none" class="svg-chart">
                        <line v-for="i in 6" :key="'g2-'+i" x1="0" :y1="i*50" x2="1000" :y2="i*50" stroke="rgba(255,255,255,0.05)" />
                        <line x1="0" y1="160" x2="1000" y2="160" stroke="rgba(255,255,255,0.2)" stroke-dasharray="4"/>

                        <!-- Cumulative Scenario Paths (Background) -->
                        <path 
                            v-for="(path, idx) in scenarioPaths" 
                            :key="'c-'+idx" 
                            :d="makePath(path, 50, -50)" 
                            fill="none" 
                            stroke="rgba(255,255,255,0.05)" 
                            stroke-width="1"
                        />

                        <!-- Real Asset Trends (Foreground) - Dynamic based on selected assets -->
                        <path 
                          v-for="(path, symbol) in assetPaths" 
                          :key="symbol"
                          :d="makePath(path, 50, -50)" 
                          fill="none" 
                          :stroke="getAssetColor(symbol)"
                          stroke-width="3" 
                          :filter="`drop-shadow(0 0 6px ${getAssetColor(symbol)}40)`"
                        />
                    </svg>
                    <div class="chart-label">Долгосрочные тренды</div>
                </div>
            </div>

        </div>

        <!-- Right: Info & Stats -->
        <aside class="stats-column">
            <div class="glass-card sticky-panel">
                <div class="panel-header-sm"><h3>Статистика волатильности</h3></div>
                
                <div class="stat-list">
                    <div class="stat-row">
                        <span class="lbl">Макс. дневное изменение</span>
                        <span class="val text-red font-mono">+8.4%</span>
                    </div>
                    <div class="stat-row">
                        <span class="lbl">Возврат к среднему</span>
                        <span class="val font-mono">0.45</span>
                    </div>
                    <div class="stat-row">
                        <span class="lbl">Kurtosis (Эксцесс)</span>
                        <span class="val text-orange font-mono">5.2</span>
                    </div>
                </div>
                
                <div class="divider"></div>

                <div class="panel-header-sm"><h3>Параметры симуляции</h3></div>
                <div class="stat-list">
                    <div class="stat-row">
                        <span class="lbl">Количество сценариев</span>
                        <span class="val font-mono">50</span>
                    </div>
                    <div class="stat-row">
                        <span class="lbl">Горизонт</span>
                        <span class="val font-mono">250 дней</span>
                    </div>
                    <div class="stat-row">
                        <span class="lbl">Модель</span>
                        <span class="val font-mono text-blue">—</span>
                    </div>
                </div>

                <div class="divider"></div>
                <div class="info-block">
                    <div class="info-item">
                        <span class="icon">PARAMS</span>
                        <p><strong>График 1</strong> визуализирует "шум" и кластеризацию волатильности. Зеленая линия выделяет экстремальный сценарий (tail risk).</p>
                    </div>
                    <div class="info-item mt-4">
                        <span class="icon">TRENDS</span>
                        <p><strong>График 2</strong> показывает интегральные траектории (накопленный итог), формирующие долгосрочные тренды US10Y и US02Y.</p>
                    </div>
                </div>
            </div>
        </aside>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'

const portfolioStore = usePortfolioStore()
const selectedBank = computed(() => portfolioStore.selectedBank)
const availableAssets = computed(() => portfolioStore.positions)

// Asset Selection State
const isAssetMenuOpen = ref(false)
const assetSearchQuery = ref('')
const selectedAssets = ref<string[]>([])

// Filtered assets based on search
const filteredAvailableAssets = computed(() => {
  if (!assetSearchQuery.value.trim()) {
    return availableAssets.value
  }
  const query = assetSearchQuery.value.toLowerCase()
  return availableAssets.value.filter(asset => 
    asset.symbol.toLowerCase().includes(query) || 
    asset.name.toLowerCase().includes(query)
  )
})

// Selected assets for display (with full info)
const selectedAssetsForDisplay = computed(() => {
  return availableAssets.value.filter(asset => selectedAssets.value.includes(asset.symbol))
})

const dailyPaths = ref<number[][]>([])
const scenarioPaths = ref<number[][]>([])
const assetPaths = ref<{ [key: string]: number[] }>({})

const generateData = () => {
    if (selectedAssets.value.length === 0) {
      console.warn('No assets selected')
      return
    }
    
    const points = 250
    const pathsCount = 50
    
    // 1. Daily Changes (Noise/Spikes)
    const dailies = []
    const cumulatives = []
    
    for(let i=0; i<pathsCount; i++) {
        const dPath = []
        const cPath = [0]
        let cumVal = 0
        
        for(let j=0; j<points; j++) {
            // Generate daily change (mostly noise with volatility clustering simulation)
            // Simple GARCH-like behavior: vol depends on previous shock
            let vol = 1.0
            if (j > 0 && Math.abs(dPath[j-1]) > 2) vol = 2.5
            
            let dailyChange = (Math.random() - 0.5) * 2 * vol
            
            // Add a "shock" event at the end
            if (j > 220 && Math.random() > 0.95 && i === 48) { // Specific index for the green line
                dailyChange *= 6 // Huge spike
            }
            
            dPath.push(dailyChange)
            
            cumVal += dailyChange
            cPath.push(cumVal)
        }
        dailies.push(dPath)
        cumulatives.push(cPath)
    }
    
    dailyPaths.value = dailies
    scenarioPaths.value = cumulatives

    // 2. Asset Trends - Generate for selected assets
    const newAssetPaths: { [key: string]: number[] } = {}
    
    selectedAssets.value.forEach(symbol => {
      const asset = availableAssets.value.find(a => a.symbol === symbol)
      if (asset) {
        // Determine drift and volatility based on asset type and characteristics
        const isBond = symbol.includes('SU') || symbol.includes('RU000') || symbol.includes('обл')
        const allocation = asset.allocation || 0
        const dayChange = asset.dayChange || 0
        
        // Bonds typically have lower volatility and positive drift
        // Stocks have higher volatility
        const baseVolatility = isBond ? 0.8 : 1.5
        const baseDrift = isBond ? 0.08 : (dayChange / 100) * 0.5
        
        // Adjust based on allocation (larger positions might have different behavior)
        const volatility = baseVolatility * (1 + allocation / 100)
        const drift = baseDrift * (1 + Math.abs(dayChange) / 50)
        
        newAssetPaths[symbol] = makeTrend(drift, volatility)
      }
    })
    
    assetPaths.value = newAssetPaths
}

const makeTrend = (drift: number, volatility: number) => {
    const points = 250
    const p = [0]
    let v = 0
    for(let j=0; j<points; j++) {
        v += (Math.random() - 0.5) * volatility + drift
        p.push(v)
    }
    return p
}

// Helper: Color logic for daily "spaghetti"
const getDailyColor = (idx: number) => {
    // Randomize colors slightly to match the "messy" look
    // Using HSL for better control over lightness/saturation
    const hue = (idx * 137) % 360 // Deterministic random-looking hue
    return `hsla(${hue}, 70%, 75%, 0.6)`
}

// Get asset color from portfolio
const getAssetColor = (symbol: string) => {
  const asset = availableAssets.value.find(a => a.symbol === symbol)
  return asset?.color || '#3b82f6'
}

// Asset Selection Handlers
const toggleAssetMenu = () => {
  isAssetMenuOpen.value = !isAssetMenuOpen.value
  if (isAssetMenuOpen.value) {
    assetSearchQuery.value = ''
  }
}

const selectAllAssets = () => {
  selectedAssets.value = filteredAvailableAssets.value.map(a => a.symbol)
  generateData()
}

const deselectAllAssets = () => {
  selectedAssets.value = []
  assetPaths.value = {}
}

const onAssetSelectionChange = () => {
  generateData()
}

// Close dropdown when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.asset-selector-pill') && !target.closest('.asset-dropdown')) {
    isAssetMenuOpen.value = false
  }
}

// Initialize with top assets by allocation
const initializeDefaultSelection = () => {
  if (availableAssets.value.length > 0) {
    // Select top 5 assets by allocation, or all if less than 5
    const topAssets = [...availableAssets.value]
      .sort((a, b) => b.allocation - a.allocation)
      .slice(0, Math.min(5, availableAssets.value.length))
      .map(a => a.symbol)
    
    selectedAssets.value = topAssets
    generateData()
  }
}

// Watch for portfolio changes
watch(() => portfolioStore.positions, (newPositions) => {
  if (newPositions.length > 0) {
    // Reset selection if current assets are no longer in portfolio
    selectedAssets.value = selectedAssets.value.filter(symbol => 
      newPositions.some(p => p.symbol === symbol)
    )
    
    // If no assets selected, initialize with defaults
    if (selectedAssets.value.length === 0) {
      initializeDefaultSelection()
    } else {
      generateData()
    }
  }
}, { deep: true })

// Helper: SVG Path Builder with customizable Y-scale
const makePath = (data: number[], maxVal: number, minVal: number) => {
    if (!data || data.length === 0) return ''
    
    const width = 1000
    const height = 320
    
    const scaleX = (i: number) => (i / (data.length - 1)) * width
    const scaleY = (v: number) => {
        const range = maxVal - minVal
        const norm = (v - minVal) / range
        return height - (norm * height)
    }

    return 'M ' + data.map((val, i) => 
        `${scaleX(i).toFixed(1)},${scaleY(val).toFixed(1)}`
    ).join(' L ')
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  initializeDefaultSelection()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.page-container { padding: 24px 32px; max-width: 1600px; margin: 0 auto; min-height: 100vh; display: flex; flex-direction: column; gap: 24px; }

.section-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: flex-end; 
  margin-bottom: 4px; 
  flex-shrink: 0; 
  position: relative;
  gap: 12px;
}
.section-title { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  position: relative;
}

/* ============================================
   GLASS COMPONENTS
   ============================================ */
.glass-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  box-shadow: 
    0 20px 40px -10px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  padding: 24px;
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
}

.btn-glass {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.btn-glass:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
.icon { font-size: 14px; }

/* Asset Selector */
.glass-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 99px;
  height: 36px;
  font-size: 13px;
}

.control-pill {
  cursor: pointer;
  transition: all 0.2s;
}

.control-pill:hover {
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,255,255,0.2);
}

.asset-selector-pill {
  position: relative;
}

.asset-selector-pill.is-open {
  background: rgba(255,255,255,0.1);
  border-color: rgba(59, 130, 246, 0.4);
}

.lbl-mini {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.chevron {
  color: rgba(255,255,255,0.6);
  transition: transform 0.2s;
  flex-shrink: 0;
}

.asset-selector-pill.is-open .chevron {
  transform: rotate(180deg);
}

.asset-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 400px;
  max-width: 500px;
  background: rgba(20, 22, 28, 0.95);
  backdrop-filter: blur(40px) saturate(200%);
  -webkit-backdrop-filter: blur(40px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  box-shadow: 
    0 20px 40px -10px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  overflow: hidden;
  z-index: 1000;
  max-height: 500px;
  display: flex;
  flex-direction: column;
}

.dropdown-header {
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.asset-search-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 8px 12px;
  color: #fff;
  font-size: 12px;
  font-family: inherit;
  outline: none;
  transition: all 0.2s;
}

.asset-search-input:focus {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(59, 130, 246, 0.5);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.asset-search-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.dropdown-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-link-sm {
  background: none;
  border: none;
  color: rgba(59, 130, 246, 0.8);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-link-sm:hover {
  background: rgba(59, 130, 246, 0.1);
  color: #60a5fa;
}

.asset-list {
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
}

.asset-list::-webkit-scrollbar {
  width: 6px;
}

.asset-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.asset-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.asset-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.asset-checkbox-item {
  display: block;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  margin-bottom: 4px;
}

.asset-checkbox-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.asset-checkbox-item.is-selected {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.asset-checkbox-item input[type="checkbox"] {
  display: none;
}

.asset-checkbox-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.asset-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  flex-shrink: 0;
  box-shadow: 0 0 4px currentColor;
}

.asset-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.asset-symbol {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}

.asset-name {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.asset-allocation {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  font-family: "SF Mono", monospace;
  font-weight: 500;
  flex-shrink: 0;
}

.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.dropdown-fade-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ============================================
   GRID & LAYOUT
   ============================================ */
.analysis-grid { display: grid; grid-template-columns: 1fr 320px; gap: 24px; flex: 1; }
.charts-column { display: flex; flex-direction: column; gap: 24px; }
.stats-column { display: flex; flex-direction: column; }

.sticky-panel { position: sticky; top: 0; }

/* ============================================
   CHARTS
   ============================================ */
.chart-container { display: flex; flex-direction: column; min-height: 380px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.panel-header h3 { margin: 0; font-size: 14px; color: #fff; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }

.legend { display: flex; gap: 16px; font-size: 11px; }
.l-item { display: flex; align-items: center; gap: 6px; color: rgba(255,255,255,0.8); }
.l-item.faded { opacity: 0.6; }

.chart-area.big-chart { flex: 1; width: 100%; overflow: hidden; position: relative; border-radius: 12px; background: rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.03); }
.svg-chart { width: 100%; height: 100%; }
.chart-label { position: absolute; bottom: 12px; right: 16px; font-size: 10px; color: rgba(255,255,255,0.3); text-transform: uppercase; font-weight: 600; pointer-events: none; }

/* ============================================
   STATS SIDEBAR
   ============================================ */
.panel-header-sm h3 { margin: 0 0 16px 0; font-size: 11px; text-transform: uppercase; color: rgba(255,255,255,0.5); letter-spacing: 0.05em; font-weight: 700; }

.stat-list { display: flex; flex-direction: column; gap: 12px; }
.stat-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
.stat-row .lbl { color: rgba(255,255,255,0.6); }
.stat-row .val { font-weight: 600; color: #fff; }

.info-block { margin-top: 8px; }
.info-item { display: flex; flex-direction: column; gap: 4px; }
.info-item .icon { font-size: 9px; color: rgba(255,255,255,0.3); font-weight: 700; border: 1px solid rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; width: fit-content; }
.info-item p { font-size: 12px; line-height: 1.5; color: rgba(255,255,255,0.6); margin: 0; }

/* ============================================
   UTILS
   ============================================ */
.dot { width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 6px currentColor; }
.bg-blue { background: #3b82f6; color: #3b82f6; }
.bg-purple { background: #a855f7; color: #a855f7; }
.bg-green { background: #4ade80; color: #4ade80; }
.bg-gray { background: #9ca3af; color: #9ca3af; }

.text-red { color: #f87171; }
.text-orange { color: #fbbf24; }
.text-blue { color: #3b82f6; }
.text-white { color: #fff; }
.font-mono { font-family: "SF Mono", monospace; }
.font-bold { font-weight: 700; }

.divider { height: 1px; background: rgba(255,255,255,0.1); margin: 24px 0; }
.mt-4 { margin-top: 16px; }

@media (max-width: 1200px) {
  .analysis-grid { 
    grid-template-columns: 1fr; 
  }
  .stats-column { 
    display: none; 
  }
}

@media (max-width: 1024px) {
  .page-container {
    padding: 16px 20px;
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .glass-pill {
    flex: 1;
    min-width: 140px;
  }
  
  .asset-dropdown {
    right: auto;
    left: 0;
    min-width: 100%;
    max-width: 100%;
  }
  
  .chart-container {
    height: 300px;
  }
  .chart-container.tall {
    height: 400px;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 12px;
  }
  .chart-container {
    height: 250px;
  }
  .chart-container.tall {
    height: 300px;
  }
}
</style>