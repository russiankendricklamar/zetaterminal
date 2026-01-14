<!-- src/pages/OptionPricingAnalyzer.vue -->
<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Справедливая стоимость опционов</h1>
        <p class="section-subtitle">Black-Scholes, модель Хестона, процессы Леви, FFT-ценообразование</p>
      </div>
      
      <div class="header-actions">
        <div class="header-controls">
          <div class="control-group">
            <label class="control-label">Реестр:</label>
            <input 
              type="file" 
              ref="fileInputRef"
              @change="handleFileUpload" 
              accept=".xlsx,.xls"
              style="display: none"
              id="excel-upload"
            />
            <button 
              @click="() => { if (fileInputRef) fileInputRef.click() }" 
              class="btn-secondary"
              title="Загрузить реестр опционов из Excel"
            >
              Загрузить Excel
            </button>
          </div>
        </div>
        <div class="glass-pill status-pill">
          <span class="dot" :class="params.optionType === 'call' ? 'bg-green' : 'bg-red'"></span>
          <span class="status-label">Модель: <b class="text-white">{{ params.model === 'bsm' ? 'Black-Scholes' : 'Heston' }}</b></span>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="glass-card full-width" style="margin-bottom: 24px; background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3);">
      <div style="padding: 12px; color: rgba(239, 68, 68, 0.9); font-size: 13px;">
        {{ error }}
      </div>
    </div>

    <!-- Registry Table (if loaded) -->
    <div v-if="loadedOptions.length > 0" class="glass-card full-width" style="margin-bottom: 24px;">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h3>Реестр опционов</h3>
          <span class="card-subtitle">Загружено опционов: {{ loadedOptions.length }}</span>
        </div>
        <div style="display: flex; gap: 8px;">
          <button 
            @click="calculateAllOptions" 
            class="btn-secondary"
            :disabled="calculatingAll"
            style="font-size: 11px; padding: 6px 12px;"
          >
            <span v-if="!calculatingAll">Рассчитать все</span>
            <span v-else>↺ Считаю...</span>
          </button>
          <button 
            @click="exportRegistryToExcel" 
            class="btn-secondary"
            :disabled="loadedOptions.length === 0"
            style="font-size: 11px; padding: 6px 12px;"
            title="Выгрузить реестр в Excel"
          >
            📥 Выгрузить Excel
          </button>
          <button 
            @click="saveRegistryToParquetHandler" 
            class="btn-secondary"
            :disabled="loadedOptions.length === 0 || savingParquet"
            style="font-size: 11px; padding: 6px 12px;"
            title="Сохранить реестр в Parquet"
          >
            <span v-if="!savingParquet">💾 Сохранить в DB</span>
            <span v-else>↺ Сохранение...</span>
          </button>
          <button 
            @click="clearRegistry" 
            class="btn-secondary"
            style="font-size: 11px; padding: 6px 12px; background: rgba(239, 68, 68, 0.2); border-color: rgba(239, 68, 68, 0.3);"
          >
            ✕ Очистить
          </button>
        </div>
      </div>
      <div class="scenario-table-container">
        <table class="scenario-table">
          <thead>
            <tr>
              <th>№</th>
              <th>Тип</th>
              <th>Spot (S)</th>
              <th>Strike (K)</th>
              <th>Волатильность (σ)</th>
              <th>Ставка (r)</th>
              <th>Время (T)</th>
              <th>Дата экспирации</th>
              <th v-if="optionResults.length > 0">Цена</th>
              <th v-if="optionResults.length > 0">Дельта</th>
              <th>Действие</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(option, idx) in loadedOptions" 
              :key="idx"
              :class="{ 'selected': selectedOptionIndex === idx }"
              @click="selectOption(idx)"
            >
              <td>{{ idx + 1 }}</td>
              <td>{{ option.optionType === 'call' ? 'Call' : 'Put' }}</td>
              <td class="mono">{{ option.S ? option.S.toFixed(2) : '-' }}</td>
              <td class="mono">{{ option.K ? option.K.toFixed(2) : '-' }}</td>
              <td class="mono">{{ option.sigma ? option.sigma.toFixed(2) + '%' : '-' }}</td>
              <td class="mono">{{ option.r ? option.r.toFixed(2) + '%' : '-' }}</td>
              <td class="mono">{{ option.T ? option.T.toFixed(4) : '-' }}</td>
              <td class="mono">{{ option.expirationDate || '-' }}</td>
              <td v-if="optionResults.length > 0 && optionResults[idx]" class="mono accent">
                {{ optionResults[idx]?.price ? optionResults[idx].price.toFixed(4) : '-' }}
              </td>
              <td v-if="optionResults.length > 0 && optionResults[idx]" class="mono">
                {{ optionResults[idx]?.delta ? optionResults[idx].delta.toFixed(4) : '-' }}
              </td>
              <td>
                <button 
                  @click.stop="loadOptionToForm(idx)" 
                  class="btn-small"
                  title="Загрузить в форму"
                >
                  Загрузить
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="dashboard-grid">
        
        <!-- LEFT PANEL: Controls -->
        <aside class="left-panel">
            
            <!-- Parameters Card -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Входные параметры</h3></div>
                
                <div class="controls-form">
                    <!-- Asset Selection -->
                    <div class="input-group">
                        <label class="lbl">Актив</label>
                        <div class="custom-select-wrapper" @click="toggleAssetDropdown">
                            <div class="custom-select" :class="{ 'open': assetDropdownOpen }">
                                <div class="select-selected">
                                    <span class="select-icon icon-asset">{{ getAssetIcon(params.asset) }}</span>
                                    <span class="select-text">{{ getAssetName(params.asset) }}</span>
                                    <svg class="select-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <polyline points="6 9 12 15 18 9" />
                                    </svg>
                                </div>
                                <transition name="dropdown">
                                    <div class="select-options" v-if="assetDropdownOpen">
                                        <div 
                                            v-for="asset in availableAssets" 
                                            :key="asset.value"
                                            class="select-option" 
                                            :class="{ 'selected': params.asset === asset.value }"
                                            @click.stop="selectAsset(asset.value)"
                                        >
                                            <span class="option-icon icon-asset">{{ asset.icon }}</span>
                                            <div style="flex: 1; display: flex; flex-direction: column; gap: 2px;">
                                                <span class="option-text">{{ asset.label }}</span>
                                                <span class="option-subtext" v-if="asset.description">{{ asset.description }}</span>
                                            </div>
                                            <span class="option-badge" v-if="params.asset === asset.value">✓</span>
                                        </div>
                                    </div>
                                </transition>
                            </div>
                        </div>
                    </div>

                    <!-- Spot Price -->
                    <div class="input-group">
                        <label class="lbl">S (Spot)</label>
                        <input v-model.number="params.S" type="number" step="0.01" class="glass-input" @change="calculatePrice" />
                    </div>
                    
                    <!-- Strike -->
                    <div class="input-group">
                        <label class="lbl">K (Strike)</label>
                        <input v-model.number="params.K" type="number" step="0.01" class="glass-input" @change="calculatePrice" />
                    </div>

                    <!-- Rate -->
                    <div class="input-group">
                        <label class="lbl">r (Rate), %</label>
                        <input v-model.number="params.r" type="number" step="0.01" class="glass-input" @change="calculatePrice" />
                    </div>

                    <!-- Volatility -->
                    <div class="input-group">
                        <label class="lbl">σ (Vol), %</label>
                        <input v-model.number="params.sigma" type="number" step="0.01" class="glass-input" @change="calculatePrice" />
                    </div>

                    <!-- Valuation Date -->
                    <div class="input-group">
                        <label class="lbl">Дата оценки</label>
                        <input v-model="params.valuationDate" type="date" class="glass-input" @change="updateTimeFromDates" />
                    </div>

                    <!-- Expiration Date -->
                    <div class="input-group">
                        <label class="lbl">Дата экспирации</label>
                        <input v-model="params.expirationDate" type="date" class="glass-input" @change="updateTimeFromDates" />
                    </div>

                    <!-- Time to Maturity -->
                    <div class="input-group">
                        <label class="lbl">T (Time), лет</label>
                        <input v-model.number="params.T" type="number" step="0.01" min="0.001" class="glass-input" @change="calculatePrice" />
                    </div>

                    <!-- Dividend Yield -->
                    <div class="input-group">
                        <label class="lbl">q (Див. доходность), %</label>
                        <input v-model.number="params.q" type="number" step="0.01" class="glass-input" @change="calculatePrice" />
                    </div>

                    <!-- Exercise Style -->
                    <div class="input-group">
                        <label class="lbl">Стиль исполнения</label>
                        <div class="custom-select-wrapper" @click="toggleExerciseStyleDropdown">
                            <div class="custom-select" :class="{ 'open': exerciseStyleDropdownOpen }">
                                <div class="select-selected">
                                    <span class="select-icon" :class="getExerciseStyleIconClass(params.exerciseStyle)">
                                        {{ getExerciseStyleIcon(params.exerciseStyle) }}
                                    </span>
                                    <span class="select-text">{{ getExerciseStyleName(params.exerciseStyle) }}</span>
                                    <svg class="select-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <polyline points="6 9 12 15 18 9" />
                                    </svg>
                                </div>
                                <transition name="dropdown">
                                    <div class="select-options" v-if="exerciseStyleDropdownOpen">
                                        <div 
                                            v-for="style in availableExerciseStyles" 
                                            :key="style.value"
                                            class="select-option" 
                                            :class="{ 'selected': params.exerciseStyle === style.value }"
                                            @click.stop="selectExerciseStyle(style.value)"
                                        >
                                            <span class="option-icon" :class="style.iconClass">{{ style.icon }}</span>
                                            <div style="flex: 1; display: flex; flex-direction: column; gap: 2px;">
                                                <span class="option-text">{{ style.label }}</span>
                                                <span class="option-subtext">{{ style.description }}</span>
                                            </div>
                                            <span class="option-badge" v-if="params.exerciseStyle === style.value">✓</span>
                                        </div>
                                    </div>
                                </transition>
                            </div>
                        </div>
                    </div>

                    <!-- Option Type -->
                    <div class="input-group">
                        <label class="lbl">Тип опциона</label>
                        <div class="custom-select-wrapper" @click="toggleOptionTypeDropdown">
                            <div class="custom-select" :class="{ 'open': optionTypeDropdownOpen }">
                                <div class="select-selected">
                                    <span class="select-icon" :class="params.optionType === 'call' ? 'icon-call' : 'icon-put'">
                                        {{ params.optionType === 'call' ? '↑' : '↓' }}
                                    </span>
                                    <span class="select-text">{{ params.optionType === 'call' ? 'Call' : 'Put' }}</span>
                                    <svg class="select-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <polyline points="6 9 12 15 18 9" />
                                    </svg>
                                </div>
                                <transition name="dropdown">
                                    <div class="select-options" v-if="optionTypeDropdownOpen">
                                        <div 
                                            class="select-option" 
                                            :class="{ 'selected': params.optionType === 'call' }"
                                            @click.stop="selectOptionType('call')"
                                        >
                                            <span class="option-icon icon-call">↑</span>
                                            <span class="option-text">Call</span>
                                            <span class="option-badge" v-if="params.optionType === 'call'">✓</span>
                                        </div>
                                        <div 
                                            class="select-option" 
                                            :class="{ 'selected': params.optionType === 'put' }"
                                            @click.stop="selectOptionType('put')"
                                        >
                                            <span class="option-icon icon-put">↓</span>
                                            <span class="option-text">Put</span>
                                            <span class="option-badge" v-if="params.optionType === 'put'">✓</span>
                                        </div>
                                    </div>
                                </transition>
                            </div>
                        </div>
                    </div>

                    <!-- Model Type -->
                    <div class="input-group">
                        <label class="lbl">Модель</label>
                        <div class="custom-select-wrapper" @click="toggleModelDropdown">
                            <div class="custom-select" :class="{ 'open': modelDropdownOpen }">
                                <div class="select-selected">
                                    <span class="select-icon" :class="params.model === 'bsm' ? 'icon-bsm' : 'icon-heston'">
                                        {{ params.model === 'bsm' ? 'BS' : 'H' }}
                                    </span>
                                    <span class="select-text">{{ params.model === 'bsm' ? 'Black-Scholes' : 'Heston' }}</span>
                                    <svg class="select-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <polyline points="6 9 12 15 18 9" />
                                    </svg>
                                </div>
                                <transition name="dropdown">
                                    <div class="select-options" v-if="modelDropdownOpen">
                                        <div 
                                            class="select-option" 
                                            :class="{ 'selected': params.model === 'bsm' }"
                                            @click.stop="selectModel('bsm')"
                                        >
                                            <span class="option-icon icon-bsm">BS</span>
                                            <div style="flex: 1; display: flex; flex-direction: column; gap: 2px;">
                                                <span class="option-text">Black-Scholes</span>
                                                <span class="option-subtext">BSM</span>
                                            </div>
                                            <span class="option-badge" v-if="params.model === 'bsm'">✓</span>
                                        </div>
                                        <div 
                                            class="select-option" 
                                            :class="{ 'selected': params.model === 'heston' }"
                                            @click.stop="selectModel('heston')"
                                        >
                                            <span class="option-icon icon-heston">H</span>
                                            <div style="flex: 1; display: flex; flex-direction: column; gap: 2px;">
                                                <span class="option-text">Heston</span>
                                                <span class="option-subtext">Stochastic Volatility</span>
                                            </div>
                                            <span class="option-badge" v-if="params.model === 'heston'">✓</span>
                                        </div>
                                        <div 
                                            class="select-option" 
                                            :class="{ 'selected': params.model === 'merton' }"
                                            @click.stop="selectModel('merton')"
                                        >
                                            <span class="option-icon icon-merton">M</span>
                                            <div style="flex: 1; display: flex; flex-direction: column; gap: 2px;">
                                                <span class="option-text">Merton</span>
                                                <span class="option-subtext">Jump Diffusion</span>
                                            </div>
                                            <span class="option-badge" v-if="params.model === 'merton'">✓</span>
                                        </div>
                                        <div 
                                            class="select-option" 
                                            :class="{ 'selected': params.model === 'bates' }"
                                            @click.stop="selectModel('bates')"
                                        >
                                            <span class="option-icon icon-bates">B</span>
                                            <div style="flex: 1; display: flex; flex-direction: column; gap: 2px;">
                                                <span class="option-text">Bates</span>
                                                <span class="option-subtext">Heston + Jumps</span>
                                            </div>
                                            <span class="option-badge" v-if="params.model === 'bates'">✓</span>
                                        </div>
                                        <div 
                                            class="select-option" 
                                            :class="{ 'selected': params.model === 'sabr' }"
                                            @click.stop="selectModel('sabr')"
                                        >
                                            <span class="option-icon icon-sabr">S</span>
                                            <div style="flex: 1; display: flex; flex-direction: column; gap: 2px;">
                                                <span class="option-text">SABR</span>
                                                <span class="option-subtext">Stochastic Alpha Beta Rho</span>
                                            </div>
                                            <span class="option-badge" v-if="params.model === 'sabr'">✓</span>
                                        </div>
                                        <div 
                                            class="select-option" 
                                            :class="{ 'selected': params.model === 'vg' }"
                                            @click.stop="selectModel('vg')"
                                        >
                                            <span class="option-icon icon-vg">VG</span>
                                            <div style="flex: 1; display: flex; flex-direction: column; gap: 2px;">
                                                <span class="option-text">Variance Gamma</span>
                                                <span class="option-subtext">VG Process</span>
                                            </div>
                                            <span class="option-badge" v-if="params.model === 'vg'">✓</span>
                                        </div>
                                    </div>
                                </transition>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </aside>

        <!-- RIGHT PANEL: Analysis -->
        <main class="main-panel">
            
            <!-- Price & Greeks Stats -->
            <transition name="fade">
            <div class="glass-card chart-card" v-if="results.price !== null">
                 <div class="chart-header">
                     <h3>Цена и греки</h3>
                 </div>
                 <div class="stats-list">
                     <div class="stat-item price-highlight">
                         <div class="stat-head">
                             <span class="stat-icon"></span> 
                             <span class="s-name">Цена опциона</span>
                         </div>
                         <span class="val mono" style="font-size: 16px; color: #3b82f6;">{{ results.price.toFixed(4) }}</span>
                     </div>

                     <div class="divider"></div>

                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">Δ</span> 
                             <span class="s-name">Дельта</span>
                         </div>
                         <span class="val mono">{{ results.delta?.toFixed(4) }}</span>
                     </div>
                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">Γ</span> 
                             <span class="s-name">Гамма</span>
                         </div>
                         <span class="val mono">{{ results.gamma?.toFixed(6) }}</span>
                     </div>
                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">ν</span> 
                             <span class="s-name">Вега</span>
                         </div>
                         <span class="val mono">{{ results.vega?.toFixed(4) }}</span>
                     </div>
                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">Θ</span> 
                             <span class="s-name">Тета</span>
                         </div>
                         <span class="val mono" :class="(results.theta || 0) < 0 ? 'text-red' : 'text-green'">{{ results.theta?.toFixed(4) || '0.0000' }}</span>
                     </div>
                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">ρ</span> 
                             <span class="s-name">Ро</span>
                         </div>
                         <span class="val mono">{{ results.rho?.toFixed(4) }}</span>
                     </div>
                 </div>
            </div>
            </transition>
            
            <!-- Price Decomposition -->
            <div class="glass-card chart-card">
                <div class="chart-header">
                    <h3>Декомпозиция стоимости</h3>
                </div>

                <div class="decomposition-grid" v-if="results.price !== null">
                    <div class="decomp-item">
                        <div class="decomp-label">Внутренняя стоимость</div>
                        <div class="decomp-value">{{ results.intrinsicValue?.toFixed(4) || '0.0000' }}</div>
                        <div class="decomp-percent">{{ results.price ? ((results.intrinsicValue || 0) / results.price * 100).toFixed(1) : '0.0' }}%</div>
                    </div>
                    <div class="decomp-item">
                        <div class="decomp-label">Временная стоимость</div>
                        <div class="decomp-value">{{ results.timeValue?.toFixed(4) || '0.0000' }}</div>
                        <div class="decomp-percent">{{ results.price ? ((results.timeValue || 0) / results.price * 100).toFixed(1) : '0.0' }}%</div>
                    </div>
                    <div class="decomp-item">
                        <div class="decomp-label">Moneyness</div>
                        <div class="decomp-value">{{ (params.S / params.K).toFixed(4) }}</div>
                        <div class="decomp-percent" :class="params.S/params.K > 1 ? 'text-green' : params.S/params.K < 1 ? 'text-red' : ''">
                            {{ params.S > params.K ? 'ITM' : params.S < params.K ? 'OTM' : 'ATM' }}
                        </div>
                    </div>
                </div>

                <div class="empty-state" v-else>
                    <span>Рассчитайте стоимость для анализа</span>
                </div>
            </div>

            <!-- Greeks Sensitivity -->
            <div class="glass-card chart-card mt-4">
                <div class="chart-header">
                    <h3>Матрица чувствительности (S × σ)</h3>
                </div>
                
                <div class="sensitivity-table" v-if="sensitivityMatrix.length">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>S \ σ</th>
                                <th>σ - 5%</th>
                                <th>σ - 2.5%</th>
                                <th>σ базовое</th>
                                <th>σ + 2.5%</th>
                                <th>σ + 5%</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(row, i) in sensitivityMatrix" :key="i">
                                <td class="row-header">{{ [-20, -10, 0, 10, 20][i] }}%</td>
                                <td v-for="(val, j) in row" :key="j" :class="{ positive: results.price !== null && val > results.price, negative: results.price !== null && val < results.price }">
                                    {{ val.toFixed(3) }}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="empty-state" v-else>
                    <span>Матрица будет заполнена после расчёта</span>
                </div>
            </div>

            <!-- Payoff Diagram -->
            <div class="glass-card chart-card mt-4">
                <div class="chart-header">
                    <h3>Payoff диаграмма</h3>
                </div>
                
                <div class="chart-container">
                    <svg v-if="payoffData.length" viewBox="0 0 800 300" preserveAspectRatio="none" class="payoff-svg">
                        <!-- Grid -->
                        <line x1="0" y1="150" x2="800" y2="150" stroke="rgba(255,255,255,0.1)" stroke-dasharray="2" />
                        <line v-for="x in [0, 200, 400, 600, 800]" :key="x" :x1="x" y1="140" :x2="x" y2="160" stroke="rgba(255,255,255,0.2)" />
                        
                        <!-- Strike line -->
                        <line :x1="strikeX" y1="0" :x2="strikeX" y2="300" stroke="rgba(148, 163, 184, 0.3)" stroke-dasharray="4" />
                        
                        <!-- Payoff line -->
                        <polyline :points="payoffPath" fill="none" stroke="#3b82f6" stroke-width="3" stroke-linejoin="round" />
                        
                        <!-- Current price marker -->
                        <circle :cx="currentPriceX" :cy="currentPriceY" r="5" fill="#ef4444" />
                    </svg>
                    <div v-else class="empty-state">
                        <span>График будет построен после расчёта</span>
                    </div>
                </div>
            </div>

        </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import * as XLSX from 'xlsx'
import { saveRegistryToParquet } from '@/services/optionService'

const params = reactive({
  S: 100,
  K: 100,
  r: 5,
  sigma: 20,
  T: 0.25,
  q: 0,
  optionType: 'call',
  model: 'bsm',
  exerciseStyle: 'european',
  asset: 'stock',
  valuationDate: new Date().toISOString().split('T')[0],
  expirationDate: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
})

const fileInputRef = ref<HTMLInputElement | null>(null)
const loadedOptions = ref<any[]>([])
const selectedOptionIndex = ref<number | null>(null)
const optionResults = ref<any[]>([])
const calculatingAll = ref(false)
const savingParquet = ref(false)
const error = ref('')
const optionTypeDropdownOpen = ref(false)
const modelDropdownOpen = ref(false)
const assetDropdownOpen = ref(false)
const exerciseStyleDropdownOpen = ref(false)

// Available assets
const availableAssets = [
  { value: 'stock', label: 'Акция', icon: 'S', description: 'Обыкновенная акция' },
  { value: 'index', label: 'Индекс', icon: 'I', description: 'Индексный опцион' },
  { value: 'currency', label: 'Валюта', icon: 'FX', description: 'Валютная пара' },
  { value: 'commodity', label: 'Товар', icon: 'C', description: 'Сырьевой товар' },
  { value: 'crypto', label: 'Криптовалюта', icon: 'CR', description: 'Криптоактив' },
  { value: 'bond', label: 'Облигация', icon: 'B', description: 'Облигационный опцион' },
]

const getAssetIcon = (asset: string) => {
  const found = availableAssets.find(a => a.value === asset)
  return found?.icon || 'S'
}

const getAssetName = (asset: string) => {
  const found = availableAssets.find(a => a.value === asset)
  return found?.label || 'Акция'
}

// Available exercise styles
const availableExerciseStyles = [
  { 
    value: 'european', 
    label: 'Европейский', 
    icon: 'EU', 
    iconClass: 'icon-european',
    description: 'Исполнение только в дату экспирации' 
  },
  { 
    value: 'american', 
    label: 'Американский', 
    icon: 'US', 
    iconClass: 'icon-american',
    description: 'Исполнение в любой момент до экспирации' 
  },
  { 
    value: 'bermudan', 
    label: 'Бермудский', 
    icon: 'BM', 
    iconClass: 'icon-bermudan',
    description: 'Исполнение в определенные даты до экспирации' 
  },
  { 
    value: 'asian', 
    label: 'Азиатский', 
    icon: 'AS', 
    iconClass: 'icon-asian',
    description: 'Цена основана на средней цене актива' 
  },
  { 
    value: 'barrier', 
    label: 'Барьерный', 
    icon: 'BR', 
    iconClass: 'icon-barrier',
    description: 'Опцион с триггерами активации/деактивации' 
  },
  { 
    value: 'digital', 
    label: 'Дигитальный', 
    icon: 'DG', 
    iconClass: 'icon-digital',
    description: 'Фиксированная выплата при исполнении' 
  },
  { 
    value: 'lookback', 
    label: 'Lookback', 
    icon: 'LB', 
    iconClass: 'icon-lookback',
    description: 'Исполнение по лучшей цене за период' 
  },
  { 
    value: 'knockout', 
    label: 'Knock-out', 
    icon: 'KO', 
    iconClass: 'icon-knockout',
    description: 'Аннулируется при достижении барьера' 
  },
]

const getExerciseStyleName = (style: string) => {
  const found = availableExerciseStyles.find(s => s.value === style)
  return found?.label || 'Европейский'
}

const getExerciseStyleIcon = (style: string) => {
  const found = availableExerciseStyles.find(s => s.value === style)
  return found?.icon || 'EU'
}

const getExerciseStyleIconClass = (style: string) => {
  const found = availableExerciseStyles.find(s => s.value === style)
  return found?.iconClass || 'icon-european'
}

const results = reactive({
  price: null as number | null,
  delta: null as number | null,
  gamma: null as number | null,
  vega: null as number | null,
  theta: null as number | null,
  rho: null as number | null,
  intrinsicValue: null as number | null,
  timeValue: null as number | null,
})

const sensitivityMatrix = ref<number[][]>([])
const payoffData = ref<number[]>([])

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

const calculateOptionPrice = (S: number, K: number, r: number, sigma: number, T: number, q: number, optionType: string): number => {
  if (sigma <= 0 || T <= 0) return 0
  const d1 = (Math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T))
  const d2 = d1 - sigma * Math.sqrt(T)

  if (optionType === 'call') {
    return S * Math.exp(-q * T) * normalCdf(d1) - K * Math.exp(-r * T) * normalCdf(d2)
  } else {
    return K * Math.exp(-r * T) * normalCdf(-d2) - S * Math.exp(-q * T) * normalCdf(-d1)
  }
}

const calculatePrice = () => {
  const S = params.S
  const K = params.K
  const r = params.r / 100
  const sigma = params.sigma / 100
  const T = params.T
  const q = params.q / 100

  if (S <= 0 || K <= 0 || T <= 0 || sigma <= 0) {
    results.price = null
    results.delta = null
    results.gamma = null
    results.vega = null
    results.theta = null
    results.rho = null
    sensitivityMatrix.value = []
    payoffData.value = []
    return
  }

  const d1 = (Math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T))
  const d2 = d1 - sigma * Math.sqrt(T)

  const Nd1 = normalCdf(d1)
  const Nd2 = normalCdf(d2)
  const N_d1 = normalCdf(-d1)
  const N_d2 = normalCdf(-d2)
  const nd1 = normalPdf(d1)

  let price: number
  if (params.optionType === 'call') {
    price = S * Math.exp(-q * T) * Nd1 - K * Math.exp(-r * T) * Nd2
    results.delta = Math.exp(-q * T) * Nd1
  } else {
    price = K * Math.exp(-r * T) * N_d2 - S * Math.exp(-q * T) * N_d1
    results.delta = -Math.exp(-q * T) * N_d1
  }

  results.gamma = (Math.exp(-q * T) * nd1) / (S * sigma * Math.sqrt(T))
  results.vega = S * Math.exp(-q * T) * nd1 * Math.sqrt(T) / 100
  results.rho = (params.optionType === 'call' 
    ? K * T * Math.exp(-r * T) * Nd2 
    : -K * T * Math.exp(-r * T) * N_d2) / 100

  if (params.optionType === 'call') {
    results.theta = (-S * Math.exp(-q * T) * nd1 * sigma / (2 * Math.sqrt(T)) + q * S * Math.exp(-q * T) * Nd1 - r * K * Math.exp(-r * T) * Nd2) / 365
  } else {
    results.theta = (-S * Math.exp(-q * T) * nd1 * sigma / (2 * Math.sqrt(T)) - q * S * Math.exp(-q * T) * N_d1 + r * K * Math.exp(-r * T) * N_d2) / 365
  }

  results.price = price
  
  if (params.optionType === 'call') {
    results.intrinsicValue = Math.max(S - K, 0)
  } else {
    results.intrinsicValue = Math.max(K - S, 0)
  }
  results.timeValue = Math.max(price - results.intrinsicValue, 0)

  // === Sensitivity Matrix ===
  const spotShifts = [-20, -10, 0, 10, 20]
  const volShifts = [-5, -2.5, 0, 2.5, 5]

  sensitivityMatrix.value = spotShifts.map(dS => {
    return volShifts.map(dVol => {
      const newS = S * (1 + dS / 100)
      const newSigma = sigma + dVol / 100
      return calculateOptionPrice(newS, K, r, newSigma, T, q, params.optionType)
    })
  })

  // === Payoff Diagram ===
  payoffData.value = []
  const minS = K * 0.5
  const maxS = K * 1.5
  for (let s = minS; s <= maxS; s += (maxS - minS) / 50) {
    let payoff = 0
    if (params.optionType === 'call') {
      payoff = Math.max(s - K, 0)
    } else {
      payoff = Math.max(K - s, 0)
    }
    payoffData.value.push(payoff)
  }
}

const payoffPath = computed(() => {
  if (!payoffData.value.length) return ''
  const minS = params.K * 0.5
  const maxS = params.K * 1.5
  const maxPayoff = Math.max(...payoffData.value)
  
  return payoffData.value.map((p, i) => {
    const x = (i / payoffData.value.length) * 800
    const y = 300 - (p / (maxPayoff || 1)) * 250 - 25
    return `${x},${y}`
  }).join(' ')
})

const strikeX = computed(() => {
  const minS = params.K * 0.5
  const maxS = params.K * 1.5
  return ((params.K - minS) / (maxS - minS)) * 800
})

const currentPriceX = computed(() => {
  const minS = params.K * 0.5
  const maxS = params.K * 1.5
  return ((params.S - minS) / (maxS - minS)) * 800
})

const currentPriceY = computed(() => {
  if (!payoffData.value.length) return 0
  const maxPayoff = Math.max(...payoffData.value)
  let payoff = 0
  if (params.optionType === 'call') {
    payoff = Math.max(params.S - params.K, 0)
  } else {
    payoff = Math.max(params.K - params.S, 0)
  }
  return 300 - (payoff / (maxPayoff || 1)) * 250 - 25
})

// Update time from dates
const updateTimeFromDates = () => {
  if (params.valuationDate && params.expirationDate) {
    const valDate = new Date(params.valuationDate)
    const expDate = new Date(params.expirationDate)
    const daysDiff = (expDate.getTime() - valDate.getTime()) / (1000 * 60 * 60 * 24)
    params.T = daysDiff / 365.0
    if (params.T > 0) {
      calculatePrice()
    }
  }
}

// Excel File Upload Handler
const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    const arrayBuffer = await file.arrayBuffer()
    const workbook = XLSX.read(arrayBuffer, { type: 'array' })
    const firstSheetName = workbook.SheetNames[0]
    const worksheet = workbook.Sheets[firstSheetName]
    const jsonData = XLSX.utils.sheet_to_json(worksheet, { raw: false })

    // Парсим данные из Excel
    const options: any[] = []
    
    for (const row of jsonData as any[]) {
      const option: any = {
        S: parseFloat(row['Spot'] || row['S'] || row['s'] || row['Спот'] || '0'),
        K: parseFloat(row['Strike'] || row['K'] || row['k'] || row['Страйк'] || '0'),
        r: parseFloat(row['Rate'] || row['r'] || row['Ставка'] || row['Безрисковая ставка'] || '5'),
        sigma: parseFloat(row['Volatility'] || row['Vol'] || row['sigma'] || row['Волатильность'] || row['σ'] || '20'),
        q: parseFloat(row['Dividend'] || row['q'] || row['Дивиденды'] || row['Див. доходность'] || '0'),
        optionType: (row['Type'] || row['type'] || row['Тип'] || 'call').toLowerCase(),
        model: (row['Model'] || row['model'] || row['Модель'] || 'bsm').toLowerCase(),
      }

      // Даты
      option.valuationDate = row['Valuation Date'] || row['valuation_date'] || row['Дата оценки'] || params.valuationDate
      option.expirationDate = row['Expiration Date'] || row['expiration_date'] || row['Дата экспирации'] || row['Expiry'] || ''
      
      // Время до экспирации
      if (option.expirationDate && option.valuationDate) {
        const valDate = new Date(option.valuationDate)
        const expDate = new Date(option.expirationDate)
        const daysDiff = (expDate.getTime() - valDate.getTime()) / (1000 * 60 * 60 * 24)
        option.T = daysDiff / 365.0
      } else {
        option.T = parseFloat(row['Time'] || row['T'] || row['t'] || row['Время'] || row['Time to Maturity'] || '0.25')
      }

      // Нормализация типов
      if (option.optionType !== 'call' && option.optionType !== 'put') {
        option.optionType = option.optionType.includes('call') || option.optionType.includes('колл') ? 'call' : 'put'
      }
      if (option.model !== 'bsm' && option.model !== 'heston') {
        option.model = option.model.includes('bs') || option.model.includes('black') ? 'bsm' : 'heston'
      }

      // Проверяем, что есть минимальные данные
      if (option.S > 0 && option.K > 0 && option.T > 0) {
        options.push(option)
      }
    }

    loadedOptions.value = options
    selectedOptionIndex.value = null
    optionResults.value = []
  } catch (err: any) {
    console.error('Excel parsing error:', err)
    alert(`Ошибка при загрузке файла: ${err.message}`)
  }
}

// Select option from registry
const selectOption = (index: number) => {
  selectedOptionIndex.value = index
}

// Load option to form
const loadOptionToForm = (index: number) => {
  const option = loadedOptions.value[index]
  if (!option) return

  params.S = option.S || params.S
  params.K = option.K || params.K
  params.r = option.r || params.r
  params.sigma = option.sigma || params.sigma
  params.T = option.T || params.T
  params.q = option.q || params.q
  params.optionType = option.optionType || params.optionType
  params.model = option.model || params.model
  params.valuationDate = option.valuationDate || params.valuationDate
  params.expirationDate = option.expirationDate || params.expirationDate

  // Автоматически рассчитываем после загрузки
  setTimeout(() => {
    calculatePrice()
  }, 100)
}

// Calculate all options
const calculateAllOptions = async () => {
  calculatingAll.value = true
  optionResults.value = []

  try {
    for (let i = 0; i < loadedOptions.value.length; i++) {
      const option = loadedOptions.value[i]
      const S = option.S
      const K = option.K
      const r = option.r / 100
      const sigma = option.sigma / 100
      const T = option.T
      const q = option.q / 100
      const optionType = option.optionType

      try {
        const price = calculateOptionPrice(S, K, r, sigma, T, q, optionType)
        
        // Рассчитываем греки
        const d1 = (Math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T))
        const d2 = d1 - sigma * Math.sqrt(T)
        const Nd1 = normalCdf(d1)
        const N_d1 = normalCdf(-d1)
        const nd1 = normalPdf(d1)

        let delta: number
        if (optionType === 'call') {
          delta = Math.exp(-q * T) * Nd1
        } else {
          delta = -Math.exp(-q * T) * N_d1
        }

        optionResults.value.push({
          price,
          delta,
          gamma: (Math.exp(-q * T) * nd1) / (S * sigma * Math.sqrt(T)),
          vega: S * Math.exp(-q * T) * nd1 * Math.sqrt(T) / 100,
        })
      } catch (err: any) {
        optionResults.value.push({
          price: 0,
          delta: 0,
          gamma: 0,
          vega: 0,
        })
        console.error(`Error calculating option ${i + 1}:`, err)
      }
    }
  } catch (err: any) {
    console.error('Error calculating options:', err)
    alert(`Ошибка при расчете опционов: ${err.message}`)
  } finally {
    calculatingAll.value = false
  }
}

// Export registry to Excel
const exportRegistryToExcel = () => {
  if (loadedOptions.value.length === 0) return

  // Prepare data for export
  const exportData = loadedOptions.value.map((option, idx) => ({
    '№': idx + 1,
    'Тип': option.optionType === 'call' ? 'Call' : 'Put',
    'Модель': option.model === 'bsm' ? 'Black-Scholes' : 'Heston',
    'Spot (S)': option.S || 0,
    'Strike (K)': option.K || 0,
    'Волатильность (σ, %)': option.sigma || 0,
    'Безрисковая ставка (r, %)': option.r || 0,
    'Дивидендная доходность (q, %)': option.q || 0,
    'Время до экспирации (T, лет)': option.T || 0,
    'Дата оценки': option.valuationDate || '',
    'Дата экспирации': option.expirationDate || '',
    'Цена опциона': optionResults.value[idx]?.price || '',
    'Дельта': optionResults.value[idx]?.delta || '',
    'Гамма': optionResults.value[idx]?.gamma || '',
    'Вега': optionResults.value[idx]?.vega || ''
  }))

  // Create workbook
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Реестр опционов')

  // Generate filename with date
  const dateStr = new Date().toISOString().split('T')[0]
  const fileName = `реестр_опционов_${dateStr}.xlsx`

  // Save file
  XLSX.writeFile(wb, fileName)
}

// Save registry to parquet
const saveRegistryToParquetHandler = async () => {
  if (loadedOptions.value.length === 0) return

  savingParquet.value = true
  error.value = ''

  try {
    const result = await saveRegistryToParquet(loadedOptions.value)
    if (result.success) {
      error.value = `Реестр успешно сохранен: ${result.data.file_name}`
      setTimeout(() => {
        error.value = ''
      }, 5000)
    }
  } catch (err: any) {
    console.error('Error saving registry to parquet:', err)
    error.value = `Ошибка при сохранении реестра: ${err.message}`
  } finally {
    savingParquet.value = false
  }
}

// Clear registry
const clearRegistry = () => {
  loadedOptions.value = []
  selectedOptionIndex.value = null
  optionResults.value = []
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

// Dropdown handlers
const toggleOptionTypeDropdown = () => {
  optionTypeDropdownOpen.value = !optionTypeDropdownOpen.value
  if (optionTypeDropdownOpen.value) {
    modelDropdownOpen.value = false
    assetDropdownOpen.value = false
    exerciseStyleDropdownOpen.value = false
  }
}

const toggleModelDropdown = () => {
  modelDropdownOpen.value = !modelDropdownOpen.value
  if (modelDropdownOpen.value) {
    optionTypeDropdownOpen.value = false
    assetDropdownOpen.value = false
    exerciseStyleDropdownOpen.value = false
  }
}

const toggleAssetDropdown = () => {
  assetDropdownOpen.value = !assetDropdownOpen.value
  if (assetDropdownOpen.value) {
    optionTypeDropdownOpen.value = false
    modelDropdownOpen.value = false
    exerciseStyleDropdownOpen.value = false
  }
}

const toggleExerciseStyleDropdown = () => {
  exerciseStyleDropdownOpen.value = !exerciseStyleDropdownOpen.value
  if (exerciseStyleDropdownOpen.value) {
    optionTypeDropdownOpen.value = false
    modelDropdownOpen.value = false
    assetDropdownOpen.value = false
  }
}

const selectOptionType = (type: 'call' | 'put') => {
  params.optionType = type
  optionTypeDropdownOpen.value = false
  calculatePrice()
}

const selectModel = (model: 'bsm' | 'heston' | 'merton' | 'bates' | 'sabr' | 'vg') => {
  params.model = model
  modelDropdownOpen.value = false
  calculatePrice()
}

const selectAsset = (asset: string) => {
  params.asset = asset
  assetDropdownOpen.value = false
  calculatePrice()
}

const selectExerciseStyle = (style: string) => {
  params.exerciseStyle = style
  exerciseStyleDropdownOpen.value = false
  calculatePrice()
}

// Close dropdowns when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.custom-select-wrapper')) {
    optionTypeDropdownOpen.value = false
    modelDropdownOpen.value = false
    assetDropdownOpen.value = false
    exerciseStyleDropdownOpen.value = false
  }
}

onMounted(() => {
  updateTimeFromDates()
  calculatePrice()
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Main Layout */
.page-container {
  padding: 24px 32px;
  max-width: 1500px;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  flex: 0;
  min-height: auto;
}

.left-panel, .main-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: visible;
}

/* Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 4px;
  flex-shrink: 0;
  flex-wrap: wrap;
  gap: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255,255,255,0.04);
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.08);
}

.control-label {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.btn-secondary {
  padding: 8px 16px;
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.25);
  border-color: rgba(59, 130, 246, 0.5);
  transform: translateY(-1px);
}

.btn-secondary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-small {
  padding: 4px 8px;
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-small:hover {
  background: rgba(59, 130, 246, 0.25);
  border-color: rgba(59, 130, 246, 0.5);
}

.full-width {
  width: 100%;
}

.card-header {
  margin-bottom: 16px;
}

.card-header h3 {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.card-subtitle {
  font-size: 11px;
  color: rgba(255,255,255,0.4);
  display: block;
  margin-top: 4px;
  font-weight: normal;
  text-transform: none;
  letter-spacing: 0;
}

.scenario-table-container {
  overflow-x: auto;
}

.scenario-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.scenario-table th,
.scenario-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.scenario-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 10px;
}

.scenario-table td {
  color: rgba(226, 232, 240, 0.9);
}

.scenario-table tr.selected {
  background: rgba(59, 130, 246, 0.15);
  border-left: 3px solid #3b82f6;
}

.scenario-table .accent {
  color: #f59e0b;
  font-weight: 600;
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
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  box-shadow: 
    0 20px 50px -10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
}

.glass-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 99px;
  height: 36px;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-pill:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
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
  gap: 14px;
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
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 10px 12px;
  border-radius: 12px;
  width: 100%;
  outline: none;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  font-size: 12px;
}

.glass-input:focus {
  border-color: rgba(255, 255, 255, 0.25);
  background: rgba(0, 0, 0, 0.3);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.05);
}

.radio-group {
  display: flex;
  gap: 12px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  cursor: pointer;
}

.radio-label input {
  cursor: pointer;
  accent-color: #3b82f6;
}

/* Custom Select Dropdown */
.custom-select-wrapper {
  position: relative;
  width: 100%;
}

.custom-select {
  position: relative;
  width: 100%;
}

.select-selected {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  user-select: none;
}

.select-selected:hover {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.3);
}

.custom-select.open .select-selected {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(0, 0, 0, 0.3);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.select-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
  line-height: 1;
}

.icon-call {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.icon-put {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.icon-bsm {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.icon-heston {
  background: rgba(168, 85, 247, 0.2);
  color: #a855f7;
}

.icon-merton {
  background: rgba(236, 72, 153, 0.2);
  color: #ec4899;
}

.icon-bates {
  background: rgba(139, 92, 246, 0.2);
  color: #8b5cf6;
}

.icon-sabr {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.icon-vg {
  background: rgba(251, 146, 60, 0.2);
  color: #fb923c;
}

.icon-asset {
  background: rgba(99, 102, 241, 0.2);
  color: #6366f1;
}

.icon-european {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.icon-american {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.icon-bermudan {
  background: rgba(14, 165, 233, 0.2);
  color: #0ea5e9;
}

.icon-asian {
  background: rgba(236, 72, 153, 0.2);
  color: #ec4899;
}

.icon-barrier {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.icon-digital {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.icon-lookback {
  background: rgba(168, 85, 247, 0.2);
  color: #a855f7;
}

.icon-knockout {
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
}

.select-text {
  flex: 1;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.select-arrow {
  width: 12px;
  height: 12px;
  color: rgba(255, 255, 255, 0.5);
  transition: transform 0.2s;
  flex-shrink: 0;
}

.custom-select.open .select-arrow {
  transform: rotate(180deg);
}

.select-options {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  z-index: 10000;
  background: rgba(20, 25, 35, 0.95);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 
    0 20px 50px -10px rgba(0, 0, 0, 0.7),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  overflow: hidden;
  margin-top: 4px;
}

.select-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  cursor: pointer;
  transition: all 0.15s;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
}

.select-option:last-child {
  border-bottom: none;
}

.select-option:hover {
  background: rgba(255, 255, 255, 0.05);
}

.select-option.selected {
  background: rgba(59, 130, 246, 0.15);
  border-left: 3px solid #3b82f6;
}

.option-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
  line-height: 1;
}

.option-text {
  flex: 1;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.option-subtext {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 400;
}

.option-badge {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.3);
  color: #60a5fa;
  border-radius: 50%;
  font-size: 10px;
  font-weight: 700;
  flex-shrink: 0;
}

/* Dropdown Animation */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  transform-origin: top;
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

/* Stats */
.stats-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  transition: all 0.2s;
}

.stat-item:hover {
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.1);
}

.stat-item.price-highlight {
  grid-column: 1 / -1;
  background: rgba(59, 130, 246, 0.15);
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  margin-bottom: 0;
}

.stat-head {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-icon {
  font-size: 14px;
}

.greek-symbol {
  font-size: 16px;
  font-weight: 700;
  color: #3b82f6;
  width: 20px;
}

.s-name {
  font-weight: 600;
  color: #fff;
}

.val {
  font-family: "SF Mono", monospace;
  font-weight: 600;
  color: #fff;
}

.divider {
  grid-column: 1 / -1;
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0;
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

/* Decomposition */
.decomposition-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.decomp-item {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.decomp-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  margin-bottom: 8px;
}

.decomp-value {
  font-size: 16px;
  font-weight: 700;
  color: #3b82f6;
  margin-bottom: 4px;
}

.decomp-percent {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

/* Table */
.sensitivity-table {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.data-table th {
  text-align: center;
  padding: 10px 4px;
  background: rgba(59, 130, 246, 0.1);
  font-weight: 600;
  color: rgba(209, 213, 219, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.data-table td {
  text-align: center;
  padding: 8px 4px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  color: rgba(226, 232, 240, 0.9);
}

.row-header {
  font-weight: 600;
  background: rgba(59, 130, 246, 0.05);
}

.positive {
  color: #4ade80;
  font-weight: 600;
}

.negative {
  color: #f87171;
  font-weight: 600;
}

/* Chart */
.chart-container {
  width: 100%;
  height: 300px;
  position: relative;
}

.payoff-svg {
  width: 100%;
  height: 100%;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
}

/* Utilities */
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  box-shadow: 0 0 6px currentColor;
}

.bg-green {
  background: #4ade80;
  color: #4ade80;
}

.bg-red {
  background: #f87171;
  color: #f87171;
}

.text-white {
  color: #fff;
}

.text-green {
  color: #4ade80;
}

.text-red {
  color: #f87171;
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

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .decomposition-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .page-container {
    padding: 16px 20px;
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
  .decomposition-grid {
    grid-template-columns: 1fr;
  }
  .left-panel {
    padding: 12px;
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
  .left-panel {
    padding: 10px;
  }
  .chart-container {
    height: 250px;
  }
  .chart-container.tall {
    height: 300px;
  }
  .input-group {
    margin-bottom: 12px;
  }
  .lbl {
    font-size: 11px;
  }
  .glass-input {
    font-size: 12px;
    padding: 8px 12px;
  }
}
</style>