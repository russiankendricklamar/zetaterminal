<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Оценка облигаций</h1>
        <p class="section-subtitle">Моделирование денежных потоков на данных MOEX ISS API</p>
      </div>
      <div class="header-actions">
        <div class="control-group">
          <label class="control-label">Реестр:</label>
          <input 
            type="file" 
            ref="fileInputRef"
            @change="handleFileUpload" 
            accept=".xlsx,.xls,.xlsm"
            style="display: none"
            id="bond-excel-upload"
          />
          <button 
            @click="() => { if (fileInputRef) fileInputRef.click() }" 
            class="btn-glass secondary"
            title="Загрузить реестр облигаций из Excel"
          >
            📂 Загрузить Excel
          </button>
        </div>
        <button 
          @click="exportRegistryToExcel" 
          class="btn-glass secondary"
          :disabled="registryBonds.length === 0"
          title="Выгрузить реестр в Excel"
        >
          📥 Выгрузить Excel
        </button>
        <button class="btn-glass primary" @click="calculateBond" :disabled="loading">
            <span v-if="!loading">Рассчитать</span>
            <span v-else class="flex-center"><span class="spinner-mini"></span> Загрузка...</span>
        </button>
      </div>
    </div>

    <!-- Registry Table (if loaded) -->
    <div v-if="registryBonds.length > 0" class="glass-card panel" style="margin-bottom: 24px;">
      <div class="panel-header" style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h3>Реестр облигаций</h3>
          <span class="card-subtitle">Загружено облигаций: {{ registryBonds.length }}</span>
        </div>
        <div style="display: flex; gap: 8px;">
          <button 
            @click="saveRegistryToParquetHandler" 
            class="btn-glass secondary"
            :disabled="registryBonds.length === 0 || savingParquet"
            style="font-size: 11px; padding: 6px 12px;"
            title="Сохранить реестр (parquet)"
          >
            <span v-if="!savingParquet">💾 Сохранить в БД</span>
            <span v-else>↺ Сохранение...</span>
          </button>
          <button 
            @click="calculateAllBonds" 
            class="btn-glass secondary"
            :disabled="calculatingAll"
            style="font-size: 11px; padding: 6px 12px;"
          >
            <span v-if="!calculatingAll">Рассчитать все</span>
            <span v-else>↺ Считаю...</span>
          </button>
          <button 
            @click="clearRegistry" 
            class="btn-glass secondary"
            style="font-size: 11px; padding: 6px 12px; background: rgba(239, 68, 68, 0.2); border-color: rgba(239, 68, 68, 0.3);"
          >
            ✕ Очистить
          </button>
        </div>
      </div>
      <div class="table-wrapper custom-scroll">
        <table class="glass-table">
          <thead>
            <tr>
              <th>№</th>
              <th>ISIN</th>
              <th>Дата оценки</th>
              <th>Y аналога (%)</th>
              <th>Y индекса (%)</th>
              <th>Рыночная доходность (%)</th>
              <th>Активность рынка</th>
              <th v-if="bondResults.length > 0">Dirty Price (Сценарий 1)</th>
              <th v-if="bondResults.length > 0">Dirty Price (Сценарий 2)</th>
              <th>Действие</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(bond, idx) in registryBonds" 
              :key="idx"
              :class="{ 'selected': selectedBondIndex === idx }"
              @click="selectBond(idx)"
            >
              <td>{{ idx + 1 }}</td>
              <td class="mono">{{ bond.secid || '-' }}</td>
              <td class="mono">{{ bond.valuationDate || '-' }}</td>
              <td class="mono">{{ bond.discountYield1 ? formatNumber(bond.discountYield1, 2) : '-' }}%</td>
              <td class="mono">{{ bond.discountYield2 ? formatNumber(bond.discountYield2, 2) : '-' }}%</td>
              <td class="mono">{{ bond.marketYield ? formatNumber(bond.marketYield, 2) : '-' }}%</td>
              <td>
                <span class="market-activity-badge" :class="bond.marketActivity || 'unknown'">
                  {{ getMarketActivityLabel(bond.marketActivity) }}
                </span>
              </td>
              <td v-if="bondResults.length > 0 && bondResults[idx]" class="mono text-blue">
                {{ bondResults[idx]?.scenario1?.dirtyPrice ? formatNumber(bondResults[idx].scenario1.dirtyPrice, 2) : '-' }} ₽
              </td>
              <td v-if="bondResults.length > 0 && bondResults[idx]" class="mono text-green">
                {{ bondResults[idx]?.scenario2?.dirtyPrice ? formatNumber(bondResults[idx].scenario2.dirtyPrice, 2) : '-' }} ₽
              </td>
              <td>
                <button 
                  @click.stop="loadBondToForm(idx)" 
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
        
        <!-- LEFT COLUMN: Inputs & Dual Scenario Results -->
        <div class="left-panel">
            
            <!-- Basic Parameters -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Параметры оценки</h3></div>
                <div class="controls-form">
                    <div class="form-group">
                        <label class="lbl">ISIN Облигации</label>
                        <input v-model="params.secid" type="text" class="glass-input" placeholder="RU000..." />
                    </div>

                    <div class="form-group">
                        <label class="lbl">Дата оценки</label>
                        <input v-model="params.valuationDate" type="date" class="glass-input" />
                    </div>

                    <div class="form-group">
                        <label class="lbl">Базис расчета дней</label>
                        <select v-model="params.dayCountConvention" class="glass-input day-count-select">
                            <option value="">Actual/365F (по умолчанию)</option>
                            <option value="Actual/365F">Actual/365F (Fixed 365)</option>
                            <option value="Actual/360">Actual/360 (French)</option>
                            <option value="Actual/Actual (ISDA)">Actual/Actual (ISDA)</option>
                            <option value="30/360 (US)">30/360 (US Municipal Bond Basis)</option>
                            <option value="30E/360 (ISDA)">30E/360 (ISDA) / 30/360 German</option>
                            <option value="30E/360">30E/360 (Eurobond Basis)</option>
                            <option value="Actual/Actual (ISMA)">Actual/Actual (ISMA) / Actual/Actual (ICMA)</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label class="lbl">
                            <input type="checkbox" v-model="params.useMarketYield" @change="onUseMarketYieldChange" />
                            Использовать доходность из MOEX API
                        </label>
                        <span class="form-hint">Если включено, доходности будут загружены из MOEX на дату оценки</span>
                    </div>

                    <div class="form-group" v-if="params.useMarketYield">
                        <label class="lbl">Рыночная доходность (%)</label>
                        <input 
                            v-model.number="params.marketYield" 
                            type="number" 
                            step="0.1" 
                            class="glass-input" 
                            placeholder="15.5"
                        />
                        <span class="form-hint">
                            Введите вручную или загрузите из MOEX API
                        </span>
                    </div>
                </div>
            </div>

            <!-- SCENARIO 1: Доходность Аналога (Input Block) -->
            <div class="glass-card panel input-scenario scenario-1-input" v-if="!params.useMarketYield">
                <div class="panel-header">
                    <h3>Сценарий 1: Y аналога</h3>
                </div>
                <div class="scenario-input-group">
                    <label class="lbl">Ставка дисконтирования (%)</label>
                    <input v-model.number="params.discountYield1" type="number" step="0.1" class="glass-input scenario-input" placeholder="14.0" />
                </div>
            </div>

            <!-- SCENARIO 2: Доходность индекса (Input Block) -->
            <div class="glass-card panel input-scenario scenario-2-input" v-if="!params.useMarketYield">
                <div class="panel-header">
                    <h3>Сценарий 2: Y индекса</h3>
                </div>
                <div class="scenario-input-group">
                    <label class="lbl">Ставка дисконтирования (%)</label>
                    <input v-model.number="params.discountYield2" type="number" step="0.1" class="glass-input scenario-input" placeholder="16.0" />
                </div>
            </div>

            <!-- Market Yield Info (when using MOEX API) -->
            <div class="glass-card panel input-scenario scenario-1-input" v-if="params.useMarketYield">
                <div class="panel-header">
                    <h3>Доходность из MOEX API</h3>
                </div>
                <div class="scenario-input-group">
                    <label class="lbl">Рыночная доходность на дату оценки (%)</label>
                    <input 
                        v-model.number="params.marketYield" 
                        type="number" 
                        step="0.1" 
                        class="glass-input scenario-input" 
                        placeholder="Введите или загрузите из MOEX"
                    />
                    <button 
                        @click="fetchMarketYield" 
                        class="btn-glass secondary"
                        :disabled="loadingMarketYield || !params.secid || !params.valuationDate"
                        style="margin-top: 8px; width: 100%;"
                    >
                        <span v-if="!loadingMarketYield">🔄 Загрузить из MOEX</span>
                        <span v-else>↺ Загрузка...</span>
                    </button>
                    <span class="form-hint" style="margin-top: 8px;">
                        Доходность будет использована для оценки вместо двух сценариев
                    </span>
                </div>
            </div>

            <!-- Error Alert -->
            <transition name="fade">
                <div v-if="error" class="error-banner">
                    <span class="icon">⚠</span> {{ error }}
                </div>
            </transition>

            <!-- Bond Info -->
            <transition name="fade">
            <div v-if="results" class="glass-card panel info-panel">
                <div class="panel-header"><h3>Паспорт бумаги</h3></div>
                <div class="info-list">
                    <div class="info-row"><span>SECID</span> <strong>{{ results.secid }}</strong></div>
                    <div class="info-row"><span>Номинал</span> <strong>{{ formatNumber(results.faceValue, 0) }} ₽</strong></div>
                    <div class="info-row"><span>Купон</span> <strong>{{ results.couponPercent }}%</strong></div>
                    <div class="info-row"><span>Погашение</span> <strong>{{ formatDate(results.maturityDate) }}</strong></div>
                    <div class="info-row"><span>Частота</span> <strong>{{ results.paymentsPerYear }} / год</strong></div>
                </div>
            </div>
            </transition>

        </div>

        <!-- RIGHT COLUMN: Tables & Scenarios -->
        <div class="main-panel">
            
            <!-- Scenario Comparison -->
            <transition name="fade">
            <div v-if="results" class="glass-card panel comparison-panel h-auto">
                <div class="panel-header">
                    <h3>Сравнение сценариев</h3>
                </div>
                <div class="comparison-table-wrapper">
                    <table class="comparison-table">
                        <thead>
                            <tr>
                                <th>Метрика</th>
                                <th class="scenario-col">
                                    <span class="scenario-label">Сценарий 1</span>
                                    <span class="scenario-rate">{{ formatNumber(params.discountYield1, 1) }}%</span>
                                </th>
                                <th class="scenario-col">
                                    <span class="scenario-label">Сценарий 2</span>
                                    <span class="scenario-rate variant-2">{{ formatNumber(params.discountYield2, 1) }}%</span>
                                </th>
                                <th class="diff-col">
                                    <span class="scenario-label">Разница</span>
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>Dirty Price</strong></td>
                                <td class="mono text-gradient-blue">{{ formatNumber(results.scenario1.dirtyPrice, 2) }} ₽</td>
                                <td class="mono text-gradient-green">{{ formatNumber(results.scenario2.dirtyPrice, 2) }} ₽</td>
                                <td class="mono" :class="results.scenario1.dirtyPrice > results.scenario2.dirtyPrice ? 'text-green' : 'text-red'">
                                    {{ formatNumber(results.scenario1.dirtyPrice - results.scenario2.dirtyPrice, 2) }} ₽
                                </td>
                            </tr>
                            <tr>
                                <td><strong>Clean Price</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.cleanPrice, 2) }} ₽</td>
                                <td class="mono">{{ formatNumber(results.scenario2.cleanPrice, 2) }} ₽</td>
                                <td class="mono" :class="results.scenario1.cleanPrice > results.scenario2.cleanPrice ? 'text-green' : 'text-red'">
                                    {{ formatNumber(results.scenario1.cleanPrice - results.scenario2.cleanPrice, 2) }} ₽
                                </td>
                            </tr>
                            <tr>
                                <td><strong>% от номинала</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.pricePercent, 2) }}%</td>
                                <td class="mono">{{ formatNumber(results.scenario2.pricePercent, 2) }}%</td>
                                <td class="mono" :class="results.scenario1.pricePercent > results.scenario2.pricePercent ? 'text-green' : 'text-red'">
                                    {{ formatNumber(results.scenario1.pricePercent - results.scenario2.pricePercent, 2) }}%
                                </td>
                            </tr>
                            <tr>
                                <td><strong>Дюрация Маколея</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.duration, 4) }} лет</td>
                                <td class="mono">{{ formatNumber(results.scenario2.duration, 4) }} лет</td>
                                <td class="mono" :class="results.scenario1.duration > results.scenario2.duration ? 'text-green' : 'text-red'">
                                    {{ formatNumber(results.scenario1.duration - results.scenario2.duration, 4) }} лет
                                </td>
                            </tr>
                            <tr v-if="results.scenario1.modifiedDuration !== undefined">
                                <td><strong>Модифицированная дюрация</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.modifiedDuration, 4) }} лет</td>
                                <td class="mono">{{ formatNumber(results.scenario2.modifiedDuration || 0, 4) }} лет</td>
                                <td class="mono" :class="(results.scenario1.modifiedDuration || 0) > (results.scenario2.modifiedDuration || 0) ? 'text-green' : 'text-red'">
                                    {{ formatNumber((results.scenario1.modifiedDuration || 0) - (results.scenario2.modifiedDuration || 0), 4) }} лет
                                </td>
                            </tr>
                            <tr v-if="results.scenario1.currentYield !== undefined">
                                <td><strong>Текущая доходность (CY)</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.currentYield, 2) }}%</td>
                                <td class="mono">{{ formatNumber(results.scenario2.currentYield || 0, 2) }}%</td>
                                <td class="mono" :class="(results.scenario1.currentYield || 0) > (results.scenario2.currentYield || 0) ? 'text-green' : 'text-red'">
                                    {{ formatNumber((results.scenario1.currentYield || 0) - (results.scenario2.currentYield || 0), 2) }}%
                                </td>
                            </tr>
                            <tr v-if="results.scenario1.adjustedCurrentYield !== undefined">
                                <td><strong>Скорректированная CY (ACY)</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.adjustedCurrentYield, 2) }}%</td>
                                <td class="mono">{{ formatNumber(results.scenario2.adjustedCurrentYield || 0, 2) }}%</td>
                                <td class="mono" :class="(results.scenario1.adjustedCurrentYield || 0) > (results.scenario2.adjustedCurrentYield || 0) ? 'text-green' : 'text-red'">
                                    {{ formatNumber((results.scenario1.adjustedCurrentYield || 0) - (results.scenario2.adjustedCurrentYield || 0), 2) }}%
                                </td>
                            </tr>
                            <tr v-if="results.scenario1.simpleYield !== undefined">
                                <td><strong>Простая доходность (SY)</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.simpleYield, 2) }}%</td>
                                <td class="mono">{{ formatNumber(results.scenario2.simpleYield || 0, 2) }}%</td>
                                <td class="mono" :class="(results.scenario1.simpleYield || 0) > (results.scenario2.simpleYield || 0) ? 'text-green' : 'text-red'">
                                    {{ formatNumber((results.scenario1.simpleYield || 0) - (results.scenario2.simpleYield || 0), 2) }}%
                                </td>
                            </tr>
                            <tr v-if="results.scenario1.ytmPercent !== undefined">
                                <td><strong>YTM (доходность к погашению)</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.ytmPercent, 2) }}%</td>
                                <td class="mono">{{ formatNumber(results.scenario2.ytmPercent || 0, 2) }}%</td>
                                <td class="mono" :class="(results.scenario1.ytmPercent || 0) > (results.scenario2.ytmPercent || 0) ? 'text-green' : 'text-red'">
                                    {{ formatNumber((results.scenario1.ytmPercent || 0) - (results.scenario2.ytmPercent || 0), 2) }}%
                                </td>
                            </tr>
                            <tr v-if="results.scenario1.nominalYield !== undefined">
                                <td><strong>Номинальная доходность (NY)</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.nominalYield, 2) }}%</td>
                                <td class="mono">{{ formatNumber(results.scenario2.nominalYield || 0, 2) }}%</td>
                                <td class="mono" :class="(results.scenario1.nominalYield || 0) > (results.scenario2.nominalYield || 0) ? 'text-green' : 'text-red'">
                                    {{ formatNumber((results.scenario1.nominalYield || 0) - (results.scenario2.nominalYield || 0), 2) }}%
                                </td>
                            </tr>
                            <tr v-if="results.scenario1.convexity !== undefined">
                                <td><strong>Выпуклость (Convexity)</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.convexity, 2) }}</td>
                                <td class="mono">{{ formatNumber(results.scenario2.convexity || 0, 2) }}</td>
                                <td class="mono" :class="(results.scenario1.convexity || 0) > (results.scenario2.convexity || 0) ? 'text-green' : 'text-red'">
                                    {{ formatNumber((results.scenario1.convexity || 0) - (results.scenario2.convexity || 0), 2) }}
                                </td>
                            </tr>
                            <tr v-if="results.scenario1.pvbp !== undefined">
                                <td><strong>PVBP/DV01 (% от номинала)</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.pvbp, 4) }}%</td>
                                <td class="mono">{{ formatNumber(results.scenario2.pvbp || 0, 4) }}%</td>
                                <td class="mono" :class="(results.scenario1.pvbp || 0) > (results.scenario2.pvbp || 0) ? 'text-green' : 'text-red'">
                                    {{ formatNumber((results.scenario1.pvbp || 0) - (results.scenario2.pvbp || 0), 4) }}%
                                </td>
                            </tr>
                            <tr v-if="results.scenario1.pvbpAbsolute !== undefined">
                                <td><strong>PVBP/DV01 (абсолютное)</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.pvbpAbsolute, 2) }} ₽</td>
                                <td class="mono">{{ formatNumber(results.scenario2.pvbpAbsolute || 0, 2) }} ₽</td>
                                <td class="mono" :class="(results.scenario1.pvbpAbsolute || 0) > (results.scenario2.pvbpAbsolute || 0) ? 'text-green' : 'text-red'">
                                    {{ formatNumber((results.scenario1.pvbpAbsolute || 0) - (results.scenario2.pvbpAbsolute || 0), 2) }} ₽
                                </td>
                            </tr>
                            <tr v-if="results.scenario1.discountMargin !== null && results.scenario1.discountMargin !== undefined">
                                <td><strong>Discount Margin (DM)</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.discountMargin, 2) }} bp</td>
                                <td class="mono">{{ formatNumber(results.scenario2.discountMargin || 0, 2) }} bp</td>
                                <td class="mono" :class="(results.scenario1.discountMargin || 0) > (results.scenario2.discountMargin || 0) ? 'text-green' : 'text-red'">
                                    {{ formatNumber((results.scenario1.discountMargin || 0) - (results.scenario2.discountMargin || 0), 2) }} bp
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            </transition>

            <!-- Sensitivity Scenarios (Scenario 1) -->
            <transition name="fade">
            <div v-if="results && results.scenario1.sensitivityScenarios && results.scenario1.sensitivityScenarios.length > 0" class="glass-card panel h-auto">
                <div class="panel-header">
                    <h3>Анализ чувствительности цены (Сценарий 1)</h3>
                    <div class="glass-pill">{{ results.scenario1.sensitivityScenarios.length }} сценариев</div>
                </div>
                
                <div class="table-wrapper custom-scroll">
                    <table class="glass-table">
                        <thead>
                            <tr>
                                <th>Δ Доходность (bp)</th>
                                <th class="text-right">Δ Доходность (%)</th>
                                <th class="text-right">Δ Цена (%)</th>
                                <th class="text-right">Δ Цена (₽)</th>
                                <th class="text-right">Новая цена (₽)</th>
                                <th class="text-right">Новая YTM (%)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(scenario, idx) in results.scenario1.sensitivityScenarios" :key="idx">
                                <td class="mono" :class="scenario.yieldChangeBps > 0 ? 'text-red' : scenario.yieldChangeBps < 0 ? 'text-green' : ''">
                                    {{ scenario.yieldChangeBps > 0 ? '+' : '' }}{{ scenario.yieldChangeBps }} bp
                                </td>
                                <td class="text-right mono" :class="scenario.yieldChangePercent > 0 ? 'text-red' : scenario.yieldChangePercent < 0 ? 'text-green' : ''">
                                    {{ scenario.yieldChangePercent > 0 ? '+' : '' }}{{ formatNumber(scenario.yieldChangePercent, 2) }}%
                                </td>
                                <td class="text-right mono" :class="scenario.priceChangePercent > 0 ? 'text-green' : scenario.priceChangePercent < 0 ? 'text-red' : ''">
                                    {{ scenario.priceChangePercent > 0 ? '+' : '' }}{{ formatNumber(scenario.priceChangePercent, 2) }}%
                                </td>
                                <td class="text-right mono" :class="scenario.priceChangeAbsolute > 0 ? 'text-green' : scenario.priceChangeAbsolute < 0 ? 'text-red' : ''">
                                    {{ scenario.priceChangeAbsolute > 0 ? '+' : '' }}{{ formatNumber(scenario.priceChangeAbsolute, 2) }} ₽
                                </td>
                                <td class="text-right mono font-bold">{{ formatNumber(scenario.newDirtyPrice, 2) }} ₽</td>
                                <td class="text-right mono">{{ formatNumber(scenario.newYtmPercent, 2) }}%</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            </transition>

            <!-- Sensitivity Scenarios (Scenario 2) -->
            <transition name="fade">
            <div v-if="results && results.scenario2.sensitivityScenarios && results.scenario2.sensitivityScenarios.length > 0" class="glass-card panel h-auto">
                <div class="panel-header">
                    <h3>Анализ чувствительности цены (Сценарий 2)</h3>
                    <div class="glass-pill">{{ results.scenario2.sensitivityScenarios.length }} сценариев</div>
                </div>
                
                <div class="table-wrapper custom-scroll">
                    <table class="glass-table">
                        <thead>
                            <tr>
                                <th>Δ Доходность (bp)</th>
                                <th class="text-right">Δ Доходность (%)</th>
                                <th class="text-right">Δ Цена (%)</th>
                                <th class="text-right">Δ Цена (₽)</th>
                                <th class="text-right">Новая цена (₽)</th>
                                <th class="text-right">Новая YTM (%)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(scenario, idx) in results.scenario2.sensitivityScenarios" :key="idx">
                                <td class="mono" :class="scenario.yieldChangeBps > 0 ? 'text-red' : scenario.yieldChangeBps < 0 ? 'text-green' : ''">
                                    {{ scenario.yieldChangeBps > 0 ? '+' : '' }}{{ scenario.yieldChangeBps }} bp
                                </td>
                                <td class="text-right mono" :class="scenario.yieldChangePercent > 0 ? 'text-red' : scenario.yieldChangePercent < 0 ? 'text-green' : ''">
                                    {{ scenario.yieldChangePercent > 0 ? '+' : '' }}{{ formatNumber(scenario.yieldChangePercent, 2) }}%
                                </td>
                                <td class="text-right mono" :class="scenario.priceChangePercent > 0 ? 'text-green' : scenario.priceChangePercent < 0 ? 'text-red' : ''">
                                    {{ scenario.priceChangePercent > 0 ? '+' : '' }}{{ formatNumber(scenario.priceChangePercent, 2) }}%
                                </td>
                                <td class="text-right mono" :class="scenario.priceChangeAbsolute > 0 ? 'text-green' : scenario.priceChangeAbsolute < 0 ? 'text-red' : ''">
                                    {{ scenario.priceChangeAbsolute > 0 ? '+' : '' }}{{ formatNumber(scenario.priceChangeAbsolute, 2) }} ₽
                                </td>
                                <td class="text-right mono font-bold">{{ formatNumber(scenario.newDirtyPrice, 2) }} ₽</td>
                                <td class="text-right mono">{{ formatNumber(scenario.newYtmPercent, 2) }}%</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            </transition>

            <!-- Cash Flows (Scenario 1) -->
            <transition name="fade">
            <div v-if="results && results.cashFlows1" class="glass-card panel h-auto">
                <div class="panel-header">
                    <h3>Денежные потоки (Сценарий 1)</h3>
                    <div class="glass-pill">{{ results.cashFlows1.length }} платежей</div>
                </div>
                
                <div class="table-wrapper custom-scroll">
                    <table class="glass-table">
                        <thead>
                            <tr>
                                <th>Дата</th>
                                <th class="text-right">T (лет)</th>
                                <th class="text-right">CF (₽)</th>
                                <th class="text-right">DF</th>
                                <th class="text-right">PV (₽)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(cf, idx) in results.cashFlows1" :key="idx">
                                <td class="text-muted">{{ formatDate(cf.date) }}</td>
                                <td class="text-right mono text-muted">{{ formatNumber(cf.t, 3) }}</td>
                                <td class="text-right mono">{{ formatNumber(cf.cf, 2) }}</td>
                                <td class="text-right mono text-muted">{{ formatNumber(cf.df, 4) }}</td>
                                <td class="text-right mono font-bold text-blue">{{ formatNumber(cf.pv, 2) }}</td>
                            </tr>
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colspan="4" class="text-right text-muted">Общая PV (Dirty):</td>
                                <td class="text-right mono text-blue font-bold">{{ formatNumber(results.scenario1.dirtyPrice, 2) }}</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
            </transition>

            <!-- Cash Flows (Scenario 2) -->
            <transition name="fade">
            <div v-if="results && results.cashFlows2" class="glass-card panel h-auto">
                <div class="panel-header">
                    <h3>Денежные потоки (Сценарий 2)</h3>
                    <div class="glass-pill">{{ results.cashFlows2.length }} платежей</div>
                </div>
                
                <div class="table-wrapper custom-scroll">
                    <table class="glass-table">
                        <thead>
                            <tr>
                                <th>Дата</th>
                                <th class="text-right">T (лет)</th>
                                <th class="text-right">CF (₽)</th>
                                <th class="text-right">DF</th>
                                <th class="text-right">PV (₽)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(cf, idx) in results.cashFlows2" :key="idx">
                                <td class="text-muted">{{ formatDate(cf.date) }}</td>
                                <td class="text-right mono text-muted">{{ formatNumber(cf.t, 3) }}</td>
                                <td class="text-right mono">{{ formatNumber(cf.cf, 2) }}</td>
                                <td class="text-right mono text-muted">{{ formatNumber(cf.df, 4) }}</td>
                                <td class="text-right mono font-bold text-green">{{ formatNumber(cf.pv, 2) }}</td>
                            </tr>
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colspan="4" class="text-right text-muted">Общая PV (Dirty):</td>
                                <td class="text-right mono text-green font-bold">{{ formatNumber(results.scenario2.dirtyPrice, 2) }}</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
            </transition>

            <!-- Coupon Schedule (улучшенная вёрстка) -->
            <transition name="fade">
            <div v-if="results && results.allCoupons" class="glass-card panel h-auto">
                <div class="panel-header">
                    <h3>График купонных выплат</h3>
                    <div class="schedule-stats">
                        <span class="stat-badge paid">{{ results.allCoupons.filter(c => c.isPaid).length }} выплачено</span>
                        <span class="stat-badge future">{{ results.allCoupons.filter(c => !c.isPaid).length }} будущих</span>
                    </div>
                </div>
                <div class="schedule-grid">
                    <div v-for="(coupon, idx) in results.allCoupons" :key="idx" class="coupon-card" :class="coupon.isPaid ? 'paid' : 'future'">
                        <div class="coupon-index">{{ idx + 1 }}</div>
                        <div class="coupon-content">
                            <div class="coupon-date">{{ formatDate(coupon.date) }}</div>
                            <div class="coupon-amount">{{ formatNumber(coupon.value, 2) }} ₽</div>
                        </div>
                        <div class="coupon-status">
                            <span class="status-badge" :class="coupon.isPaid ? 'paid' : 'future'">
                                {{ coupon.isPaid ? '✓ Выплачен' : '◯ Будущий' }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            </transition>

            <!-- Empty State -->
            <div v-if="!results && !loading" class="empty-placeholder">
                <div class="placeholder-content">
                    <span class="icon-lg">📊</span>
                    <h3>Введите параметры и нажмите «Рассчитать»</h3>
                    <p>Для загрузки данных о купонах используется MOEX API</p>
                </div>
            </div>

        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import * as XLSX from 'xlsx'
import { valuateBond, saveRegistryToParquet, type BondValuationResponse } from '@/services/bondService'
import { getApiHeaders } from '@/utils/apiHeaders'

// --- Types ---
interface CashFlow {
  date: string; t: number; cf: number; df: number; pv: number
}

interface Coupon {
  date: string; value: number; isPaid: boolean
}

interface SensitivityScenario {
  yieldChangeBps: number
  yieldChangePercent: number
  priceChangePercent: number
  priceChangeAbsolute: number
  newDirtyPrice: number
  newYtmPercent: number
}

interface ScenarioResults {
  dirtyPrice: number
  cleanPrice: number
  pricePercent: number
  currentYield?: number
  adjustedCurrentYield?: number
  simpleYield?: number
  ytm?: number
  ytmPercent?: number
  nominalYield?: number
  duration: number
  modifiedDuration?: number
  convexity?: number
  pvbp?: number
  pvbpAbsolute?: number
  sensitivityScenarios?: SensitivityScenario[]
  discountMargin?: number | null
}

interface BondResults {
  secid: string; faceValue: number; couponPercent: number; issueDate: string; maturityDate: string; paymentsPerYear: number
  accruedInterest: number
  scenario1: ScenarioResults
  scenario2: ScenarioResults
  cashFlows1: CashFlow[]
  cashFlows2: CashFlow[]
  allCoupons: Coupon[]
}

interface BondParams {
  secid: string
  valuationDate: string
  discountYield1: number
  discountYield2: number
  dayCount?: number
  dayCountConvention?: string
  useMarketYield?: boolean
  marketYield?: number
}

// --- State ---
const params = ref<BondParams>({
  secid: 'RU000A10AU99',
  valuationDate: new Date().toISOString().split('T')[0],
  discountYield1: 14.0,
  discountYield2: 16.0,
  dayCount: 365,
  dayCountConvention: '',
  useMarketYield: false,
  marketYield: undefined
})

const results = ref<BondResults | null>(null)
const loading = ref(false)
const loadingMarketYield = ref(false)
const error = ref('')
const fileInputRef = ref<HTMLInputElement | null>(null)
const registryBonds = ref<any[]>([])
const selectedBondIndex = ref<number | null>(null)
const bondResults = ref<(BondValuationResponse | null)[]>([])
const calculatingAll = ref(false)
const savingParquet = ref(false)

// --- Methods ---

const fetchMarketYield = async () => {
  if (!params.value.secid || !params.value.valuationDate) {
    error.value = 'Введите ISIN и дату оценки'
    return
  }

  loadingMarketYield.value = true
  error.value = ''

  try {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
    const response = await fetch(
      `${API_BASE_URL}/api/bond/market-yield?secid=${params.value.secid.trim()}&date=${params.value.valuationDate}`,
      {
        method: 'GET',
        headers: getApiHeaders(),
      }
    )

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    if (data.yield !== null && data.yield !== undefined) {
      params.value.marketYield = data.yield
    } else {
      error.value = 'Доходность не найдена для данной даты'
    }
  } catch (e: unknown) {
    console.error('Ошибка загрузки доходности:', e)
    error.value = e instanceof Error ? e.message : 'Ошибка загрузки доходности из MOEX API'
  } finally {
    loadingMarketYield.value = false
  }
}

const onUseMarketYieldChange = () => {
  if (params.value.useMarketYield && params.value.secid && params.value.valuationDate) {
    fetchMarketYield()
  }
}

const calculateBond = async () => {
  loading.value = true
  error.value = ''
  results.value = null

  // Validation
  if (!params.value.secid || !params.value.secid.trim()) {
    error.value = 'Введите ISIN облигации'
    loading.value = false
    return
  }

  // Если используется рыночная доходность, проверяем её наличие
  if (params.value.useMarketYield) {
    if (!params.value.marketYield || params.value.marketYield <= 0) {
      error.value = 'Загрузите рыночную доходность из MOEX API или введите вручную'
      loading.value = false
      return
    }
    // Используем рыночную доходность для обоих сценариев
    params.value.discountYield1 = params.value.marketYield
    params.value.discountYield2 = params.value.marketYield
  } else {
    // Проверяем оба сценария
    if (!params.value.discountYield1 || !params.value.discountYield2) {
      error.value = 'Заполните обе ставки дисконтирования'
      loading.value = false
      return
    }
  }

  try {
    const response = await valuateBond({
      secid: params.value.secid.trim(),
      valuationDate: params.value.valuationDate,
      discountYield1: params.value.discountYield1,
      discountYield2: params.value.discountYield2,
      dayCount: params.value.dayCount,
      dayCountConvention: params.value.dayCountConvention || undefined
    })
    
    results.value = response
  } catch (e: unknown) {
    console.error('Ошибка оценки облигации:', e)
    error.value = e instanceof Error ? e.message : 'Ошибка соединения с API или получения данных облигации'
  } finally {
    loading.value = false
  }
}

// --- Registry Management ---
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
    const bonds: Record<string, unknown>[] = []

    for (const row of jsonData as Record<string, string>[]) {
      const marketYieldStr = row['Рыночная доходность'] || row['Market Yield'] || row['market_yield'] || row['YTM'] || row['ytm'] || ''
      const marketYield = marketYieldStr ? parseFloat(marketYieldStr) : null
      
      // Определяем режим: если есть рыночная доходность, используем её, иначе два сценария
      const useMarketYield = marketYield !== null && marketYield > 0
      
      const bond: Record<string, unknown> = {
        secid: row['ISIN'] || row['isin'] || row['SECID'] || row['secid'] || row['Облигация'] || '',
        valuationDate: row['Дата оценки'] || row['Valuation Date'] || row['valuation_date'] || row['Дата'] || params.value.valuationDate,
        useMarketYield: useMarketYield,
        marketYield: marketYield,
        discountYield1: useMarketYield ? marketYield : parseFloat(row['Y аналога'] || row['Y Analogue'] || row['y_analogue'] || row['Доходность 1'] || row['Discount Yield 1'] || String(params.value.discountYield1) || '14.0'),
        discountYield2: useMarketYield ? marketYield : parseFloat(row['Y индекса'] || row['Y Index'] || row['y_index'] || row['Доходность 2'] || row['Discount Yield 2'] || String(params.value.discountYield2) || '16.0'),
        marketActivity: row['Активность рынка'] || row['Market Activity'] || row['market_activity'] || null,
        dayCountConvention: row['Базис расчета'] || row['Day Count'] || row['day_count'] || params.value.dayCountConvention || ''
      }

      // Проверяем, что есть минимальные данные
      if (bond.secid && bond.secid.trim()) {
        bonds.push(bond)
      }
    }
    
    // Если есть облигации с пустой рыночной доходностью, загружаем её из MOEX
    for (const bond of bonds) {
      if (bond.useMarketYield && (!bond.marketYield || bond.marketYield <= 0)) {
        // Будет загружена при расчете
        bond.marketYield = null
      }
    }

    registryBonds.value = bonds
    selectedBondIndex.value = null
    bondResults.value = []
    error.value = ''
  } catch (err: unknown) {
    console.error('Excel parsing error:', err)
    error.value = `Ошибка при загрузке файла: ${err instanceof Error ? err.message : String(err)}`
  }
}

const selectBond = (index: number) => {
  selectedBondIndex.value = index
}

const loadBondToForm = (index: number) => {
  const bond = registryBonds.value[index]
  if (!bond) return

  params.value.secid = bond.secid || params.value.secid
  params.value.valuationDate = bond.valuationDate || params.value.valuationDate
  params.value.discountYield1 = bond.discountYield1 || params.value.discountYield1
  params.value.discountYield2 = bond.discountYield2 || params.value.discountYield2
  params.value.dayCountConvention = bond.dayCountConvention || params.value.dayCountConvention

  // Автоматически рассчитываем после загрузки
  setTimeout(() => {
    calculateBond()
  }, 100)
}

const calculateAllBonds = async () => {
  calculatingAll.value = true
  bondResults.value = []
  error.value = ''

  try {
    for (let i = 0; i < registryBonds.value.length; i++) {
      const bond = registryBonds.value[i]
      try {
        // Если используется рыночная доходность и она не указана, загружаем из MOEX
        let discountYield1 = bond.discountYield1
        let discountYield2 = bond.discountYield2
        
        if (bond.useMarketYield) {
          if (!bond.marketYield || bond.marketYield <= 0) {
            // Загружаем из MOEX
            try {
              const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
              const yieldResponse = await fetch(
                `${API_BASE_URL}/api/bond/market-yield?secid=${bond.secid.trim()}&date=${bond.valuationDate}`,
                {
                  method: 'GET',
                  headers: getApiHeaders()
                }
              )
              
              if (yieldResponse.ok) {
                const yieldData = await yieldResponse.json()
                if (yieldData.yield !== null && yieldData.yield !== undefined) {
                  discountYield1 = yieldData.yield
                  discountYield2 = yieldData.yield
                  // Сохраняем загруженную доходность
                  registryBonds.value[i].marketYield = yieldData.yield
                }
              }
            } catch (yieldErr) {
              console.warn(`Could not fetch market yield for ${bond.secid}:`, yieldErr)
            }
          } else {
            discountYield1 = bond.marketYield
            discountYield2 = bond.marketYield
          }
        }
        
        const result = await valuateBond({
          secid: bond.secid.trim(),
          valuationDate: bond.valuationDate,
          discountYield1: discountYield1,
          discountYield2: discountYield2,
          dayCountConvention: bond.dayCountConvention || undefined
        })
        bondResults.value.push(result)
      } catch (err: unknown) {
        bondResults.value.push(null)
        console.error(`Error calculating bond ${i + 1}:`, err)
      }
    }
  } catch (err: unknown) {
    console.error('Error calculating bonds:', err)
    error.value = `Ошибка при расчете облигаций: ${err instanceof Error ? err.message : String(err)}`
  } finally {
    calculatingAll.value = false
  }
}

const exportRegistryToExcel = () => {
  if (registryBonds.value.length === 0) return

  // Prepare data for export
  const exportData = registryBonds.value.map((bond, idx) => ({
    '№': idx + 1,
    'ISIN': bond.secid || '',
    'Дата оценки': bond.valuationDate || '',
    'Y аналога (%)': bond.discountYield1 || 0,
    'Y индекса (%)': bond.discountYield2 || 0,
    'Рыночная доходность (%)': bond.marketYield || '',
    'Активность рынка': bond.marketActivity || '',
    'Базис расчета': bond.dayCountConvention || '',
    'Dirty Price (Сценарий 1)': bondResults.value[idx]?.scenario1?.dirtyPrice || '',
    'Dirty Price (Сценарий 2)': bondResults.value[idx]?.scenario2?.dirtyPrice || '',
    'Clean Price (Сценарий 1)': bondResults.value[idx]?.scenario1?.cleanPrice || '',
    'Clean Price (Сценарий 2)': bondResults.value[idx]?.scenario2?.cleanPrice || '',
    'Duration (Сценарий 1)': bondResults.value[idx]?.scenario1?.duration || '',
    'Duration (Сценарий 2)': bondResults.value[idx]?.scenario2?.duration || ''
  }))

  // Create workbook
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Реестр облигаций')

  // Generate filename with date
  const dateStr = new Date().toISOString().split('T')[0]
  const fileName = `реестр_облигаций_${dateStr}.xlsx`

  // Save file
  XLSX.writeFile(wb, fileName)
}

const clearRegistry = () => {
  registryBonds.value = []
  selectedBondIndex.value = null
  bondResults.value = []
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

const getMarketActivityLabel = (activity: string | null | undefined): string => {
  if (!activity) return 'Не определено'
  const labels: Record<string, string> = {
    'high': 'Высокая',
    'medium': 'Средняя',
    'low': 'Низкая',
    'unknown': 'Не определено'
  }
  return labels[activity.toLowerCase()] || activity
}

const saveRegistryToParquetHandler = async () => {
  if (registryBonds.value.length === 0) return

  savingParquet.value = true
  error.value = ''

  try {
    const result = await saveRegistryToParquet('bond', registryBonds.value)
    if (result.success) {
      error.value = `Реестр успешно сохранен: ${result.data.file_name}`
      setTimeout(() => {
        error.value = ''
      }, 5000)
    }
  } catch (err: unknown) {
    console.error('Error saving registry to parquet:', err)
    error.value = `Ошибка при сохранении реестра: ${err instanceof Error ? err.message : String(err)}`
  } finally {
    savingParquet.value = false
  }
}

// --- Formatters ---
const formatNumber = (val: number, decimals = 2) => val.toLocaleString('ru-RU', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
const formatDate = (dateStr: string) => new Date(dateStr).toLocaleDateString('ru-RU')
</script>

<style scoped>
/* ============================================
   LAYOUT
   ============================================ */
.page-container { padding: 24px 32px; max-width: 1600px; margin: 0 auto; min-height: 100vh; display: flex; flex-direction: column; gap: 24px; }
.dashboard-grid { display: grid; grid-template-columns: 380px 1fr; gap: 28px; flex: 1; }
.left-panel, .main-panel { display: flex; flex-direction: column; gap: 20px; }

/* Header */
.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px; flex-shrink: 0; }
.section-title { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }
.header-actions { display: flex; gap: 12px; }
.header-left { display: flex; flex-direction: column; }

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
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
}
.panel { padding: 24px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.panel-header h3 { margin: 0; font-size: 12px; font-weight: 700; text-transform: uppercase; color: rgba(255,255,255,0.5); letter-spacing: 0.05em; }

/* Controls */
.controls-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.lbl { font-size: 11px; color: rgba(255,255,255,0.6); font-weight: 600; text-transform: uppercase; }
.form-hint { font-size: 10px; color: rgba(255,255,255,0.4); display: block; margin-top: 4px; font-style: italic; }

.glass-input {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 10px 12px;
  border-radius: 10px;
  width: 100%;
  outline: none;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  font-family: "SF Mono", monospace;
  font-size: 13px;
}

.glass-input:focus {
  border-color: rgba(255, 255, 255, 0.25);
  background: rgba(0, 0, 0, 0.3);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.05);
}

.glass-input.day-count-select {
  padding: 12px 14px;
  min-height: 48px;
  height: auto;
}

/* Buttons */
.btn-glass {
    border: none; padding: 10px 20px; border-radius: 10px; cursor: pointer; color: #fff; font-weight: 600; font-size: 13px;
    display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s;
}
.btn-glass.primary { background: linear-gradient(135deg, #3b82f6, #2563eb); box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); }
.btn-glass.primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5); }
.btn-glass:disabled { opacity: 0.6; cursor: not-allowed; }

/* ============================================
   INPUT SCENARIOS (Left Panel)
   ============================================ */
.input-scenario { padding: 16px 24px; }
.input-scenario.scenario-1-input { border-top: 3px solid #3b82f6; }
.input-scenario.scenario-2-input { border-top: 3px solid #10b981; }

.scenario-input-group { display: flex; flex-direction: column; gap: 8px; }

/* ============================================
   RESULT SCENARIOS
   ============================================ */
.result-card { position: relative; overflow: hidden; margin-top: 12px; }
.result-card.scenario-1 { border-top: 3px solid #3b82f6; }
.result-card.scenario-2 { border-top: 3px solid #10b981; }

.scenario-badge { font-size: 10px; background: rgba(59, 130, 246, 0.2); padding: 4px 10px; border-radius: 6px; color: #60a5fa; font-weight: 600; }
.scenario-badge.variant-2 { background: rgba(16, 185, 129, 0.2); color: #4ade80; }

.scenario-results { display: flex; flex-direction: column; gap: 16px; }

.main-metric-small { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.metric-label-small { font-size: 10px; text-transform: uppercase; color: rgba(255,255,255,0.5); letter-spacing: 0.08em; }
.metric-value-small { font-size: 22px; font-weight: 700; font-family: "SF Mono", monospace; }

.metrics-grid-small { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.m-item-small { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 4px; padding: 10px; background: rgba(255,255,255,0.02); border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); }
.m-item-small .sub { font-size: 10px; color: rgba(255,255,255,0.4); }
.m-item-small .val-small { font-size: 13px; font-weight: 600; font-family: "SF Mono", monospace; color: #fff; }

/* Comparison Table */
.comparison-panel { margin-bottom: 12px; }
.comparison-table-wrapper { width: 100%; overflow-x: auto; }
.comparison-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.comparison-table th { text-align: left; padding: 12px; color: rgba(255,255,255,0.4); font-weight: 600; font-size: 10px; text-transform: uppercase; border-bottom: 1px solid rgba(255,255,255,0.1); }
.comparison-table td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }
.comparison-table tr:last-child td { border-bottom: none; }

.scenario-col { text-align: center; }
.scenario-label { display: block; font-size: 10px; text-transform: uppercase; color: rgba(255,255,255,0.5); margin-bottom: 4px; }
.scenario-rate { display: block; font-size: 13px; font-weight: 700; color: #60a5fa; font-family: "SF Mono", monospace; }
.scenario-rate.variant-2 { color: #4ade80; }

.diff-col { text-align: center; width: 100px; }

/* Info Panel */
.info-panel { padding-top: 16px; }
.info-list { display: flex; flex-direction: column; gap: 10px; }
.info-row { display: flex; justify-content: space-between; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px; }
.info-row:last-child { border: none; }
.info-row span { color: rgba(255,255,255,0.5); }
.info-row strong { font-weight: 500; color: #fff; }

/* ============================================
   SCHEDULE (Grid Layout - улучшено)
   ============================================ */
.schedule-stats { display: flex; gap: 8px; }
.stat-badge { font-size: 10px; padding: 3px 8px; border-radius: 4px; font-weight: 600; }
.stat-badge.paid { background: rgba(74, 222, 128, 0.15); color: #4ade80; }
.stat-badge.future { background: rgba(255, 255, 255, 0.1); color: rgba(255,255,255,0.5); }

.schedule-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }
.coupon-card {
  padding: 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.02); transition: all 0.2s;
  display: flex; flex-direction: column; gap: 10px;
}
.coupon-card.paid { border-left: 3px solid #4ade80; background: rgba(74, 222, 128, 0.04); }
.coupon-card.future { border-left: 3px solid rgba(255,255,255,0.3); background: rgba(255,255,255,0.01); }
.coupon-card:hover { border-color: rgba(255,255,255,0.2); background: rgba(255,255,255,0.04); }

.coupon-index { font-size: 10px; color: rgba(255,255,255,0.3); font-weight: 700; text-transform: uppercase; }
.coupon-content { display: flex; flex-direction: column; gap: 6px; }
.coupon-date { font-size: 11px; color: rgba(255,255,255,0.6); font-weight: 500; }
.coupon-amount { font-size: 14px; font-weight: 700; font-family: "SF Mono", monospace; color: #fff; }
.coupon-status { display: flex; justify-content: center; }

.status-badge { padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; text-transform: uppercase; display: inline-block; }
.status-badge.paid { background: rgba(74, 222, 128, 0.15); color: #4ade80; }
.status-badge.future { background: rgba(255, 255, 255, 0.1); color: rgba(255,255,255,0.5); }

/* ============================================
   TABLES
   ============================================ */
.table-wrapper { width: 100%; }
.glass-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.glass-table th { text-align: left; padding: 12px; color: rgba(255,255,255,0.4); font-weight: 600; font-size: 11px; text-transform: uppercase; border-bottom: 1px solid rgba(255,255,255,0.1); }
.glass-table td { padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); color: #e2e8f0; }
.glass-table tr:last-child td { border-bottom: none; }
.glass-table tfoot td { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 16px; }

.glass-pill { background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 99px; font-size: 11px; color: rgba(255,255,255,0.7); }

/* Empty State */
.empty-placeholder { height: 100%; display: flex; align-items: center; justify-content: center; opacity: 0.5; border: 2px dashed rgba(255,255,255,0.1); border-radius: 20px; }
.placeholder-content { text-align: center; }
.icon-lg { font-size: 48px; display: block; margin-bottom: 16px; }
.empty-placeholder h3 { font-size: 16px; color: #fff; margin: 0 0 8px 0; }
.empty-placeholder p { font-size: 13px; margin: 0; }

/* Utils */
.text-right { text-align: right; }
.text-center { text-align: center; }
.text-green { color: #4ade80; }
.text-blue { color: #3b82f6; }
.text-orange { color: #fbbf24; }
.text-red { color: #f87171; }
.text-muted { color: rgba(255,255,255,0.4); }
.mono { font-family: "SF Mono", monospace; }
.font-bold { font-weight: 700; }
.h-auto { height: auto; }
.flex-center { display: flex; align-items: center; gap: 8px; }

.text-gradient-blue { background: linear-gradient(to right, #60a5fa, #3b82f6); -webkit-background-clip: text; color: transparent; }
.text-gradient-green { background: linear-gradient(to right, #4ade80, #22c55e); -webkit-background-clip: text; color: transparent; }

.error-banner { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; padding: 12px; border-radius: 10px; margin-bottom: 20px; font-size: 13px; display: flex; align-items: center; gap: 8px; }
.spinner-mini { width: 14px; height: 14px; border: 2px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Transition */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* Custom scrollbar */
.custom-scroll::-webkit-scrollbar { width: 6px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
.custom-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
.custom-scroll::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

@media (max-width: 1280px) {
  .dashboard-grid { grid-template-columns: 340px 1fr; }
  .schedule-grid { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); }
}

@media (max-width: 1024px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .metrics-grid-small { grid-template-columns: 1fr; }
  .schedule-grid { grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }
  .page-container {
    padding: 16px 20px;
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
  .schedule-grid { 
    grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); 
    gap: 10px; 
  }
  .coupon-card { 
    padding: 12px; 
    gap: 8px; 
  }
  .left-panel,
  .main-panel {
    padding: 12px;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 12px;
  }
  .schedule-grid { 
    grid-template-columns: 1fr; 
    gap: 8px; 
  }
  .coupon-card { 
    padding: 10px; 
    gap: 6px; 
    font-size: 11px;
  }
  .left-panel,
  .main-panel {
    padding: 10px;
  }
}

/* Registry styles */
.btn-glass.secondary {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.btn-glass.secondary:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.25);
  border-color: rgba(59, 130, 246, 0.5);
}

.btn-glass.secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.market-activity-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.market-activity-badge.high {
  background: rgba(74, 222, 128, 0.15);
  color: #4ade80;
}

.market-activity-badge.medium {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
}

.market-activity-badge.low {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.market-activity-badge.unknown {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.5);
}

.glass-table tr.selected {
  background: rgba(59, 130, 246, 0.15);
  border-left: 3px solid #3b82f6;
}
</style>