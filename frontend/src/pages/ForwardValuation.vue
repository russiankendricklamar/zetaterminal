<!-- src/pages/ForwardValuation.vue -->
<template>
  <div class="forward-valuation-page">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          Оценка форвардов
        </h1>
        <p class="page-subtitle">
          Справедливая стоимость и анализ форвардных контрактов
        </p>
      </div>
      
      <div class="header-right">
        <!-- Excel Upload -->
        <div class="control-group">
          <label class="control-label">Реестр:</label>
          <input 
            id="excel-upload" 
            ref="fileInputRef"
            type="file" 
            accept=".xlsx,.xls"
            style="display: none"
            @change="handleFileUpload"
          >
          <button 
            class="btn-secondary" 
            title="Загрузить реестр контрактов из Excel"
            @click="() => { if (fileInputRef) fileInputRef.click() }"
          >
            Загрузить Excel
          </button>
        </div>

        <!-- Forward Type -->
        <div class="control-group">
          <label class="control-label">Тип форварда:</label>
          <select
            v-model="selectedForwardType"
            class="forward-type-select"
            @change="updateValuation"
          >
            <option value="bond">
              Форвард на облигацию
            </option>
            <option value="fx">
              Валютный форвард
            </option>
            <option value="commodity">
              Форвард на товар
            </option>
            <option value="equity">
              Форвард на акцию
            </option>
            <option value="rate">
              Форвард на ставку
            </option>
          </select>
        </div>

        <!-- Add to Registry Button -->
        <button 
          class="btn-secondary" 
          title="Добавить текущий форвард в реестр"
          @click="addForwardManually"
        >
          ➕ Добавить в реестр
        </button>

        <!-- Calculation Button -->
        <button 
          class="btn-primary" 
          :disabled="calculating"
          @click="calculateValuation"
        >
          <span v-if="!calculating">Пересчитать</span>
          <span v-else>↺ Считаю...</span>
        </button>
      </div>
    </div>

    <!-- Error Message -->
    <div
      v-if="error"
      class="error-message"
    >
      ⚠️ {{ error }}
    </div>

    <!-- Registry Table (if loaded) -->
    <div
      v-if="loadedContracts.length > 0"
      class="card full-width"
      style="margin-bottom: 24px;"
    >
      <div
        class="card-header"
        style="display: flex; justify-content: space-between; align-items: center;"
      >
        <div>
          <h3>Реестр контрактов</h3>
          <span class="card-subtitle">Загружено контрактов: {{ loadedContracts.length }}</span>
        </div>
        <div style="display: flex; gap: 8px;">
          <button 
            class="btn-secondary" 
            :disabled="loadedContracts.length === 0"
            style="font-size: 11px; padding: 6px 12px;"
            title="Выгрузить реестр в Excel"
            @click="exportRegistryToExcel"
          >
            📥 Выгрузить Excel
          </button>
          <button 
            class="btn-secondary" 
            :disabled="loadedContracts.length === 0 || savingParquet"
            style="font-size: 11px; padding: 6px 12px;"
            title="Сохранить реестр (parquet)"
            @click="saveRegistryToParquetHandler"
          >
            <span v-if="!savingParquet">💾 Сохранить в БД</span>
            <span v-else>↺ Сохранение...</span>
          </button>
          <button 
            class="btn-secondary" 
            :disabled="calculatingAll"
            style="font-size: 11px; padding: 6px 12px;"
            @click="calculateAllContracts"
          >
            <span v-if="!calculatingAll">Рассчитать все</span>
            <span v-else>↺ Считаю...</span>
          </button>
          <button 
            class="btn-secondary" 
            style="font-size: 11px; padding: 6px 12px; background: rgba(239, 68, 68, 0.2); border-color: rgba(239, 68, 68, 0.3);"
            @click="clearRegistry"
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
              <th v-if="selectedForwardType === 'fx'">
                Валюта продажи
              </th>
              <th v-if="selectedForwardType === 'fx'">
                Валюта покупки
              </th>
              <th v-if="selectedForwardType === 'fx'">
                Сумма продажи
              </th>
              <th v-if="selectedForwardType === 'fx'">
                Сумма покупки
              </th>
              <th v-if="selectedForwardType !== 'fx'">
                Спот цена
              </th>
              <th>Дата оценки</th>
              <th>Дата экспирации</th>
              <th>Рыночная цена</th>
              <th v-if="contractResults.length > 0">
                Справедливая цена
              </th>
              <th v-if="contractResults.length > 0">
                Стоимость
              </th>
              <th>Действие</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(contract, idx) in loadedContracts" 
              :key="idx"
              :class="{ 'selected': selectedContractIndex === idx }"
              @click="selectContract(idx)"
            >
              <td>{{ idx + 1 }}</td>
              <td>{{ contract.forwardType || selectedForwardType }}</td>
              <td v-if="selectedForwardType === 'fx'">
                {{ contract.fxSellCurrency || '-' }}
              </td>
              <td v-if="selectedForwardType === 'fx'">
                {{ contract.fxBuyCurrency || '-' }}
              </td>
              <td
                v-if="selectedForwardType === 'fx'"
                class="mono"
              >
                {{ contract.fxSellAmount ? formatCompactCurrency(contract.fxSellAmount) : '-' }}
              </td>
              <td
                v-if="selectedForwardType === 'fx'"
                class="mono"
              >
                {{ contract.fxBuyAmount ? formatCompactCurrency(contract.fxBuyAmount) : '-' }}
              </td>
              <td
                v-if="selectedForwardType !== 'fx'"
                class="mono"
              >
                {{ contract.spotPrice ? formatCurrency(contract.spotPrice) : '-' }}
              </td>
              <td class="mono">
                {{ contract.valuationDate || '-' }}
              </td>
              <td class="mono">
                {{ contract.expirationDate || '-' }}
              </td>
              <td class="mono">
                {{ contract.marketForwardPrice ? formatCurrency(contract.marketForwardPrice) : '-' }}
              </td>
              <td
                v-if="contractResults.length > 0 && contractResults[idx]"
                class="mono accent"
              >
                {{ contractResults[idx]?.fairForwardPrice ? formatCurrency(contractResults[idx].fairForwardPrice) : '-' }}
              </td>
              <td
                v-if="contractResults.length > 0 && contractResults[idx]"
                class="mono"
                :class="(contractResults[idx]?.forwardValue || 0) >= 0 ? 'positive' : 'negative'"
              >
                {{ contractResults[idx]?.forwardValue ? formatCompactCurrency(contractResults[idx].forwardValue) : '-' }}
              </td>
              <td>
                <button 
                  class="btn-small" 
                  title="Загрузить в форму"
                  @click.stop="loadContractToForm(idx)"
                >
                  📝
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Input Parameters -->
    <div class="grid-2">
      <!-- Валютный форвард (FX) -->
      <template v-if="selectedForwardType === 'fx'">
        <!-- Продаваемая валюта (слева) -->
        <div class="card">
          <div class="card-header">
            <h3>Продаваемая валюта</h3>
          </div>
          <div class="parameter-group">
            <div class="param-row">
              <label>Валюта</label>
              <select
                v-model="params.fxSellCurrency"
                class="param-input"
                @change="updateValuation"
              >
                <option value="CNY">
                  CNY
                </option>
                <option value="RUB">
                  RUB
                </option>
                <option value="EUR">
                  EUR
                </option>
                <option value="GBP">
                  GBP
                </option>
                <option value="JPY">
                  JPY
                </option>
              </select>
            </div>
            <div class="param-row">
              <label>Сумма продажи</label>
              <input
                v-model.number="params.fxSellAmount"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Ставка для {{ params.fxSellCurrency }} (%)</label>
              <input
                v-model.number="params.fxExternalRate"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
          </div>
        </div>

        <!-- Покупаемая валюта (справа) -->
        <div class="card">
          <div class="card-header">
            <h3>Покупаемая валюта</h3>
          </div>
          <div class="parameter-group">
            <div class="param-row">
              <label>Валюта</label>
              <select
                v-model="params.fxBuyCurrency"
                class="param-input"
                @change="updateValuation"
              >
                <option value="RUB">
                  RUB
                </option>
                <option value="EUR">
                  EUR
                </option>
                <option value="CNY">
                  CNY
                </option>
                <option value="GBP">
                  GBP
                </option>
                <option value="JPY">
                  JPY
                </option>
              </select>
            </div>
            <div class="param-row">
              <label>Сумма покупки</label>
              <input
                v-model.number="params.fxBuyAmount"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Ставка для {{ params.fxBuyCurrency }} (%)</label>
              <input
                v-model.number="params.fxInternalRate"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
          </div>
        </div>

        <!-- Даты и курсы (внизу) -->
        <div class="card full-width">
          <div class="card-header">
            <h3>Даты и курсы</h3>
          </div>
          <div class="parameter-group">
            <div class="param-row">
              <label>Дата сделки</label>
              <input
                v-model="params.fxDealDate"
                type="date"
                class="param-input"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Дата оценки</label>
              <input
                v-model="params.fxValuationDate"
                type="date"
                class="param-input"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Дата экспирации</label>
              <input
                v-model="params.fxExpirationDate"
                type="date"
                class="param-input"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Спот курс</label>
              <input
                v-model.number="params.spotPrice"
                type="number"
                class="param-input"
                step="0.0001"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Курс сделки (форвард)</label>
              <input
                v-model.number="params.marketForwardPrice"
                type="number"
                class="param-input"
                step="0.0001"
                @change="updateValuation"
              >
            </div>
          </div>
        </div>
      </template>

      <!-- Форвард на облигацию -->
      <template v-if="selectedForwardType === 'bond'">
        <!-- Параметры облигации (слева) -->
        <div class="card">
          <div class="card-header">
            <h3>Параметры облигации</h3>
          </div>
          <div class="parameter-group">
            <div class="param-row">
              <label>Спот цена (clean, %)</label>
              <input
                v-model.number="params.spotPrice"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Номинал</label>
              <input
                v-model.number="params.faceValue"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Купонная ставка (%)</label>
              <input
                v-model.number="params.couponRate"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Частота купонов (раз/год)</label>
              <select
                v-model.number="params.couponFrequency"
                class="param-input"
                @change="updateValuation"
              >
                <option :value="1">
                  1 (ежегодно)
                </option>
                <option :value="2">
                  2 (раз в полгода)
                </option>
                <option :value="4">
                  4 (ежеквартально)
                </option>
                <option :value="12">
                  12 (ежемесячно)
                </option>
              </select>
            </div>
            <div class="param-row">
              <label>Накопленный купонный доход (НКД)</label>
              <input
                v-model.number="params.accruedInterest"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Дата последнего купона</label>
              <input
                v-model="params.lastCouponDate"
                type="date"
                class="param-input"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Дата погашения</label>
              <input
                v-model="params.maturityDate"
                type="date"
                class="param-input"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Конвенция подсчета дней</label>
              <select
                v-model="params.dayCountConvention"
                class="param-input"
                @change="updateValuation"
              >
                <option value="ACT/ACT">
                  ACT/ACT (ISDA)
                </option>
                <option value="ACT/365">
                  ACT/365
                </option>
                <option value="ACT/360">
                  ACT/360
                </option>
                <option value="30/360">
                  30/360
                </option>
              </select>
            </div>
            <div class="param-row">
              <label>
                <input
                  v-model="params.autoCalculateAI"
                  type="checkbox"
                  @change="updateValuation"
                >
                Автоматически рассчитывать НКД
              </label>
            </div>
          </div>
        </div>

        <!-- Параметры форварда (справа) -->
        <div class="card">
          <div class="card-header">
            <h3>Параметры форварда</h3>
          </div>
          <div class="parameter-group">
            <div class="param-row">
              <label>Дата оценки</label>
              <input
                v-model="params.bondValuationDate"
                type="date"
                class="param-input"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Дата экспирации</label>
              <input
                v-model="params.bondExpirationDate"
                type="date"
                class="param-input"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Время до экспирации (лет)</label>
              <input
                v-model.number="params.timeToMaturity"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Репо ставка (%)</label>
              <input
                v-model.number="params.repoRate"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Безрисковая ставка (%)</label>
              <input
                v-model.number="params.riskFreeRate"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Рыночная цена форварда (clean, %)</label>
              <input
                v-model.number="params.marketForwardPrice"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Размер контракта (шт.)</label>
              <input
                v-model.number="params.contractSize"
                type="number"
                class="param-input"
                step="1"
                @change="updateValuation"
              >
            </div>
          </div>
        </div>

        <!-- Кривая доходности (внизу) -->
        <div class="card full-width">
          <div class="card-header">
            <h3>Кривая доходности</h3>
            <span class="card-subtitle">Используйте кривую доходности или плоскую ставку (репо)</span>
          </div>
          <div class="parameter-group">
            <div class="param-row">
              <label>
                <input
                  v-model="params.useYieldCurve"
                  type="checkbox"
                  @change="updateValuation"
                >
                Использовать кривую доходности
              </label>
            </div>
            <div
              v-if="params.useYieldCurve"
              class="yield-curve-inputs"
            >
              <div
                v-for="(point, idx) in params.yieldCurvePoints"
                :key="idx"
                class="param-row"
              >
                <label>{{ point.tenor }} мес.</label>
                <input
                  v-model.number="point.rate"
                  type="number"
                  class="param-input"
                  step="0.01"
                  @change="updateValuation"
                >
                <span style="color: rgba(255,255,255,0.5); margin-left: 8px;">%</span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Cost-of-Carry форварды (commodity, equity, rate) -->
      <template v-else-if="selectedForwardType !== 'fx'">
        <!-- Underlying Asset Parameters -->
        <div class="card">
          <div class="card-header">
            <h3>Параметры базового актива</h3>
          </div>
          <div class="parameter-group">
            <div class="param-row">
              <label>Спот цена (S₀)</label>
              <input
                v-model.number="params.spotPrice"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div
              v-if="selectedForwardType === 'equity'"
              class="param-row"
            >
              <label>Дивиденды (%)</label>
              <input
                v-model.number="params.dividendYield"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div
              v-if="selectedForwardType === 'commodity'"
              class="param-row"
            >
              <label>Стоимость хранения (%)</label>
              <input
                v-model.number="params.carryingCost"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div
              v-if="selectedForwardType === 'commodity'"
              class="param-row"
            >
              <label>Удобство владения (Convenience Yield, %)</label>
              <input
                v-model.number="params.convenienceYield"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
          </div>
        </div>

        <!-- Forward Parameters -->
        <div class="card">
          <div class="card-header">
            <h3>Параметры форварда</h3>
          </div>
          <div class="parameter-group">
            <div class="param-row">
              <label>Время до экспирации (лет)</label>
              <input
                v-model.number="params.timeToMaturity"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Безрисковая ставка (%)</label>
              <input
                v-model.number="params.riskFreeRate"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
            <div class="param-row">
              <label>Рыночная цена форварда</label>
              <input
                v-model.number="params.marketForwardPrice"
                type="number"
                class="param-input"
                step="0.01"
                @change="updateValuation"
              >
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- Fair Value Results -->
    <div class="grid-3">
      <!-- Forward Price (Theoretical) -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Справедливая стоимость форвардного контракта</h3>
          <span class="metric-unit">Справедливая цена</span>
        </div>
        <div class="metric-value accent">
          {{ formatCurrency(valuationResults.fairForwardPrice) }}
        </div>
        <div class="metric-detail">
          <span class="detail-label">Модель:</span>
          <span class="detail-value">{{ selectedForwardType === 'fx' ? 'Валютный форвард' : 'Cost-of-Carry' }}</span>
        </div>
      </div>

      <!-- Market Price -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Рыночная цена форвардного контракта</h3>
          <span class="metric-unit">Рыночная цена</span>
        </div>
        <div class="metric-value blue">
          {{ formatCurrency(params.marketForwardPrice) }}
        </div>
        <div class="metric-detail">
          <span class="detail-label">Источник:</span>
          <span class="detail-value">Рыночные данные</span>
        </div>
      </div>

      <!-- Forward Value (Per Unit) -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Стоимость форвардного контракта</h3>
          <span class="metric-unit">По единице</span>
        </div>
        <div
          class="metric-value"
          :class="valuationResults.forwardValue >= 0 ? 'positive' : 'negative'"
        >
          {{ formatCurrency(valuationResults.forwardValue) }}
        </div>
        <div class="metric-detail">
          <span class="detail-label">За контракт:</span>
          <!-- Для FX форвардов forwardValue уже рассчитан с учетом buy_amount, не умножаем на contractSize -->
          <span
            v-if="selectedForwardType === 'fx'"
            class="detail-value"
          >
            {{ formatCompactCurrency(valuationResults.forwardValue) }}
          </span>
          <!-- Для других типов форвардов используем contractSize -->
          <span
            v-else
            class="detail-value"
          >
            {{ formatCompactCurrency(valuationResults.forwardValue * params.contractSize) }}
          </span>
        </div>
      </div>
    </div>

    <!-- FX Forward Details (только для валютных форвардов) -->
    <template v-if="selectedForwardType === 'fx' && valuationResults.currencyPair">
      <div class="card full-width">
        <div class="card-header">
          <h3>Детали валютного форварда</h3>
        </div>
        <div class="grid-3">
          <div class="metric-card">
            <div class="metric-header">
              <h3>Валютная пара</h3>
            </div>
            <div class="metric-value accent">
              {{ valuationResults.currencyPair }}
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-header">
              <h3>Форвардный курс (мин)</h3>
            </div>
            <div class="metric-value blue">
              {{ valuationResults.forwardRateMin?.toFixed(3) || 'N/A' }}
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-header">
              <h3>Форвардный курс (макс)</h3>
            </div>
            <div class="metric-value blue">
              {{ valuationResults.forwardRateMax?.toFixed(3) || 'N/A' }}
            </div>
          </div>
        </div>
        <div
          class="grid-2"
          style="margin-top: 20px;"
        >
          <div class="card">
            <div class="card-header">
              <h3>Дисконт-факторы</h3>
            </div>
            <div class="parameter-group">
              <div class="param-row">
                <label>Внутренняя валюта ({{ params.fxBuyCurrency }})</label>
                <span class="param-value">{{ valuationResults.discountFactorInternal?.toFixed(3) || 'N/A' }}</span>
              </div>
              <div class="param-row">
                <label>Внешняя валюта ({{ params.fxSellCurrency }})</label>
                <span class="param-value">{{ valuationResults.discountFactorExternal?.toFixed(3) || 'N/A' }}</span>
              </div>
            </div>
          </div>
          <div class="card">
            <div class="card-header">
              <h3>Справедливая стоимость</h3>
            </div>
            <div class="parameter-group">
              <div class="param-row">
                <label>Минимальная (тыс. {{ params.settlementCurrency || 'RUB' }})</label>
                <span class="param-value">{{ valuationResults.fairValueMin?.toFixed(3) || 'N/A' }}</span>
              </div>
              <div class="param-row">
                <label>Максимальная (тыс. {{ params.settlementCurrency || 'RUB' }})</label>
                <span class="param-value">{{ valuationResults.fairValueMax?.toFixed(3) || 'N/A' }}</span>
              </div>
              <div
                v-if="valuationResults.forwardDiff !== undefined"
                class="param-row"
              >
                <label>Расхождение с курсом сделки</label>
                <span
                  class="param-value"
                  :class="typeof valuationResults.forwardDiff === 'string' ? '' : (valuationResults.forwardDiff >= 0 ? 'positive' : 'negative')"
                >
                  {{ typeof valuationResults.forwardDiff === 'string' ? valuationResults.forwardDiff : valuationResults.forwardDiff.toFixed(3) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Cost-of-Carry Breakdown (только для не-FX форвардов) -->
    <div
      v-if="selectedForwardType !== 'fx'"
      class="card full-width"
    >
      <div class="card-header">
        <h3>Модель Cost-of-Carry</h3>
      </div>
      <div class="carry-breakdown">
        <div class="carry-item">
          <span class="carry-label">Спот цена актива (S₀)</span>
          <span class="carry-value accent">{{ formatCurrency(params.spotPrice) }}</span>
        </div>
        <div class="carry-item">
          <span class="carry-label">+ Безрисковая ставка (r)</span>
          <span class="carry-value">{{ (params.riskFreeRate).toFixed(3) }}%</span>
        </div>
        <div class="carry-item">
          <span class="carry-label">+ Стоимость хранения (c)</span>
          <span class="carry-value">{{ (params.carryingCost).toFixed(3) }}%</span>
        </div>
        <div class="carry-item">
          <span class="carry-label">- Дивиденды/Купоны (d)</span>
          <span class="carry-value negative">{{ (params.dividendYield).toFixed(3) }}%</span>
        </div>
        <div class="carry-item">
          <span class="carry-label">- Удобство владения (y)</span>
          <span class="carry-value negative">{{ (params.convenienceYield).toFixed(3) }}%</span>
        </div>
        <div class="carry-item total">
          <span class="carry-label">= Чистый Carry</span>
          <span class="carry-value cyan">
            {{ (params.riskFreeRate + params.carryingCost - params.dividendYield - params.convenienceYield).toFixed(3) }}%
          </span>
        </div>
        <div class="carry-item final">
          <span class="carry-label">= Справедливая стоимость форварда F</span>
          <span
            class="carry-value"
            :class="valuationResults.fairForwardPrice >= params.spotPrice ? 'positive' : 'negative'"
          >
            {{ formatCurrency(valuationResults.fairForwardPrice) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Forward Value Components (только для не-FX форвардов) -->
    <div
      v-if="selectedForwardType !== 'fx'"
      class="grid-3"
    >
      <!-- Intrinsic Value -->
      <div class="card">
        <div class="card-header">
          <h3>Внутренняя стоимость</h3>
          <span class="card-subtitle">Текущая стоимость позиции</span>
        </div>
        <div class="value-breakdown">
          <div class="item">
            <span class="label">Спот цена</span>
            <span class="value accent">{{ formatCurrency(params.spotPrice) }}</span>
          </div>
          <div class="item">
            <span class="label">Цена исполнения</span>
            <span class="value blue">{{ formatCurrency(params.marketForwardPrice) }}</span>
          </div>
          <div class="item total">
            <span class="label">Внутренняя стоимость</span>
            <span
              class="value"
              :class="valuationResults.intrinsicValue >= 0 ? 'positive' : 'negative'"
            >
              {{ valuationResults.intrinsicValue >= 0 ? '+' : '' }}{{ formatCurrency(valuationResults.intrinsicValue) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Time Value -->
      <div class="card">
        <div class="card-header">
          <h3>Временная стоимость</h3>
          <span class="card-subtitle">Временная стоимость</span>
        </div>
        <div class="value-breakdown">
          <div class="item">
            <span class="label">Справедливая форвардная цена</span>
            <span class="value accent">{{ formatCurrency(valuationResults.fairForwardPrice) }}</span>
          </div>
          <div class="item">
            <span class="label">Цена исполнения</span>
            <span class="value blue">{{ formatCurrency(params.marketForwardPrice) }}</span>
          </div>
          <div class="item total">
            <span class="label">Временная стоимость</span>
            <span
              class="value"
              :class="valuationResults.timeValue >= 0 ? 'positive' : 'negative'"
            >
              {{ valuationResults.timeValue >= 0 ? '+' : '' }}{{ formatCurrency(valuationResults.timeValue) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Total Value -->
      <div class="card">
        <div class="card-header">
          <h3>Общая стоимость форварда</h3>
          <span class="card-subtitle">Справедливая стоимость позиции</span>
        </div>
        <div class="value-breakdown">
          <div class="item">
            <span class="label">Внутренняя стоимость</span>
            <span
              class="value"
              :class="valuationResults.intrinsicValue >= 0 ? 'positive' : 'negative'"
            >
              {{ valuationResults.intrinsicValue >= 0 ? '+' : '' }}{{ formatCurrency(valuationResults.intrinsicValue) }}
            </span>
          </div>
          <div class="item">
            <span class="label">Временная стоимость</span>
            <span
              class="value"
              :class="valuationResults.timeValue >= 0 ? 'positive' : 'negative'"
            >
              {{ valuationResults.timeValue >= 0 ? '+' : '' }}{{ formatCurrency(valuationResults.timeValue) }}
            </span>
          </div>
          <div class="item total">
            <span class="label">Общая стоимость</span>
            <span class="value accent">
              {{ valuationResults.totalValue >= 0 ? '+' : '' }}{{ formatCurrency(valuationResults.totalValue) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Bond Forward Details (только для облигаций) -->
    <template v-if="selectedForwardType === 'bond' && valuationResults.couponSchedule">
      <!-- Coupon Payment Table -->
      <div class="card full-width">
        <div class="card-header">
          <h3>Расписание купонных платежей</h3>
          <span class="card-subtitle">Купоны между датой оценки и экспирацией</span>
        </div>
        <div class="scenario-table-container">
          <table class="scenario-table">
            <thead>
              <tr>
                <th>№</th>
                <th>Дата купона</th>
                <th>Дней до платежа</th>
                <th>Лет до платежа</th>
                <th>Сумма купона</th>
                <th>Ставка дисконтирования (%)</th>
                <th>Дисконт-фактор</th>
                <th>Приведенная стоимость</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="coupon in valuationResults.couponSchedule"
                :key="coupon.couponNumber"
              >
                <td>{{ coupon.couponNumber }}</td>
                <td>{{ formatDate(coupon.couponDate) }}</td>
                <td class="mono">
                  {{ coupon.daysToPayment }}
                </td>
                <td class="mono">
                  {{ coupon.yearsToPayment.toFixed(4) }}
                </td>
                <td class="mono">
                  {{ formatCurrency(coupon.couponAmount) }}
                </td>
                <td class="mono">
                  {{ coupon.discountRate.toFixed(3) }}%
                </td>
                <td class="mono">
                  {{ coupon.discountFactor.toFixed(6) }}
                </td>
                <td class="mono positive">
                  {{ formatCurrency(coupon.presentValue) }}
                </td>
              </tr>
              <tr class="base">
                <td
                  colspan="7"
                  style="text-align: right; font-weight: 600;"
                >
                  Итого PV купонов:
                </td>
                <td
                  class="mono accent"
                  style="font-weight: 700;"
                >
                  {{ formatCurrency(valuationResults.pvCoupons || 0) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Formula Breakdown -->
      <div
        v-if="valuationResults.formulaBreakdown"
        class="card full-width"
      >
        <div class="card-header">
          <h3>Детальный разбор формулы</h3>
          <span class="card-subtitle">F = [(S₀ + AI₀) × (1 + r_repo × T) - Σ(Cᵢ × DFᵢ)] / DF(T) - AI_T</span>
        </div>
        <div class="parameter-group">
          <div class="param-row">
            <label>Спот цена (clean, S₀)</label>
            <span class="param-value">{{ formatCurrency(valuationResults.formulaBreakdown.spotCleanPrice) }}</span>
          </div>
          <div class="param-row">
            <label>НКД на дату оценки (AI₀)</label>
            <span class="param-value">{{ formatCurrency(valuationResults.formulaBreakdown.accruedInterestSpot) }}</span>
          </div>
          <div class="param-row">
            <label>Спот цена (dirty, S₀ + AI₀)</label>
            <span class="param-value accent">{{ formatCurrency(valuationResults.formulaBreakdown.spotDirtyPrice) }}</span>
          </div>
          <div class="param-row">
            <label>Репо ставка (r_repo)</label>
            <span class="param-value">{{ valuationResults.formulaBreakdown.repoRate.toFixed(3) }}%</span>
          </div>
          <div class="param-row">
            <label>Время до экспирации (T)</label>
            <span class="param-value">{{ valuationResults.formulaBreakdown.timeToMaturity.toFixed(4) }} лет</span>
          </div>
          <div class="param-row">
            <label>Стоимость финансирования (S × r × T)</label>
            <span class="param-value">{{ formatCurrency(valuationResults.formulaBreakdown.financingCost) }}</span>
          </div>
          <div class="param-row">
            <label>PV купонов (Σ(Cᵢ × DFᵢ))</label>
            <span class="param-value negative">-{{ formatCurrency(valuationResults.formulaBreakdown.totalCouponsPV) }}</span>
          </div>
          <div class="param-row total">
            <label>Форвард цена (dirty, до вычета НКД)</label>
            <span class="param-value accent">{{ formatCurrency(valuationResults.formulaBreakdown.forwardDirtyPriceBeforeAI) }}</span>
          </div>
          <div class="param-row">
            <label>НКД на дату экспирации (AI_T)</label>
            <span class="param-value negative">-{{ formatCurrency(valuationResults.formulaBreakdown.accruedInterestForward) }}</span>
          </div>
          <div class="param-row final">
            <label>Справедливая форвардная цена (clean, F)</label>
            <span
              class="param-value accent"
              style="font-size: 16px; font-weight: 700;"
            >{{ formatCurrency(valuationResults.formulaBreakdown.forwardCleanPrice) }}</span>
          </div>
        </div>
      </div>

      <!-- Extended Greeks -->
      <div
        v-if="valuationResults.dv01 !== undefined"
        class="grid-3"
      >
        <div class="card">
          <div class="card-header">
            <h3>DV01</h3>
            <span class="card-subtitle">Изменение цены на 1 bp</span>
          </div>
          <div class="metric-value accent">
            {{ valuationResults.dv01.toFixed(6) }}
          </div>
          <div class="metric-detail">
            <span class="detail-label">На контракт:</span>
            <span class="detail-value">{{ formatCompactCurrency(valuationResults.dv01 * params.contractSize * params.faceValue / 100) }}</span>
          </div>
        </div>
        <div class="card">
          <div class="card-header">
            <h3>Convexity</h3>
            <span class="card-subtitle">Вторая производная</span>
          </div>
          <div class="metric-value blue">
            {{ valuationResults.convexity?.toFixed(2) || 'N/A' }}
          </div>
          <div class="metric-detail">
            <span class="detail-label">Нелинейность:</span>
            <span class="detail-value">{{ (valuationResults.convexity || 0) > 0 ? 'Положительная' : 'Отрицательная' }}</span>
          </div>
        </div>
        <div class="card">
          <div class="card-header">
            <h3>Repo Sensitivity</h3>
            <span class="card-subtitle">Чувствительность к репо (1 bp)</span>
          </div>
          <div
            class="metric-value"
            :class="(valuationResults.repoSensitivity || 0) >= 0 ? 'positive' : 'negative'"
          >
            {{ valuationResults.repoSensitivity?.toFixed(6) || 'N/A' }}
          </div>
          <div class="metric-detail">
            <span class="detail-label">На контракт:</span>
            <span class="detail-value">{{ formatCompactCurrency((valuationResults.repoSensitivity || 0) * params.contractSize * params.faceValue / 100) }}</span>
          </div>
        </div>
      </div>
    </template>

    <!-- Forward Price Profile -->
    <div class="grid-2">
      <!-- Price vs Spot -->
      <div class="card">
        <div class="chart-header">
          <h3>{{ selectedForwardType === 'fx' ? 'Профиль форвардного курса' : 'Профиль форвардной цены' }}</h3>
          <span class="chart-subtitle">
            {{ selectedForwardType === 'fx' ? 'Зависимость форвардного курса от спот курса' : 'F(S) зависимость от спот цены' }}
          </span>
        </div>
        <div class="chart-container">
          <canvas ref="priceProfileRef" />
        </div>
      </div>

      <!-- Value vs Time -->
      <div class="card">
        <div class="chart-header">
          <h3>{{ selectedForwardType === 'fx' ? 'NPV контракта vs Время' : 'Стоимость форварда vs Время' }}</h3>
          <span class="chart-subtitle">
            {{ selectedForwardType === 'fx' ? 'Эволюция NPV по времени до экспирации' : 'Эволюция стоимости по времени' }}
          </span>
        </div>
        <div class="chart-container">
          <canvas ref="valueVsTimeRef" />
        </div>
      </div>
    </div>

    <!-- Scenario Analysis -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Анализ сценариев</h3>
        <span class="card-subtitle">Стоимость форварда при различных движениях спота</span>
      </div>
      <div class="scenario-table-container">
        <table class="scenario-table">
          <thead>
            <tr>
              <th>Сценарий</th>
              <th>Спот цена</th>
              <th>% Изменение</th>
              <th>Стоимость форварда</th>
              <th>P&L (Лонг)</th>
              <th>P&L (Шорт)</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="scenario in scenarioAnalysis"
              :key="scenario.id"
              :class="scenario.isBase ? 'base' : ''"
            >
              <td class="scenario-name">
                {{ scenario.name }}
              </td>
              <td class="spot-price mono">
                {{ formatCurrency(scenario.spotPrice) }}
              </td>
              <td
                class="change mono"
                :class="scenario.change >= 0 ? 'positive' : 'negative'"
              >
                {{ scenario.change >= 0 ? '+' : '' }}{{ scenario.change.toFixed(1) }}%
              </td>
              <td
                class="forward-value mono"
                :class="scenario.forwardValue >= 0 ? 'positive' : 'negative'"
              >
                {{ scenario.forwardValue >= 0 ? '+' : '' }}{{ formatCurrency(scenario.forwardValue) }}
              </td>
              <td
                class="pnl mono"
                :class="scenario.pnlLong >= 0 ? 'positive' : 'negative'"
              >
                {{ scenario.pnlLong >= 0 ? '+' : '' }}{{ formatCompactCurrency(scenario.pnlLong) }}
              </td>
              <td
                class="pnl mono"
                :class="scenario.pnlShort >= 0 ? 'positive' : 'negative'"
              >
                {{ scenario.pnlShort >= 0 ? '+' : '' }}{{ formatCompactCurrency(scenario.pnlShort) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Sensitivity Analysis (только для не-FX форвардов) -->
    <div
      v-if="selectedForwardType !== 'fx'"
      class="grid-2"
    >
      <!-- Sensitivity to Spot Price -->
      <div class="card">
        <div class="chart-header">
          <h3>Delta (∂F/∂S)</h3>
          <span class="chart-subtitle">Чувствительность к спот цене</span>
        </div>
        <div class="sensitivity-metrics">
          <div class="sens-item">
            <span class="label">Дельта (Delta)</span>
            <span class="value accent">{{ valuationResults.delta.toFixed(3) }}</span>
          </div>
          <div class="sens-item">
            <span class="label">P&L на 1% спота</span>
            <span class="value blue">{{ formatCompactCurrency(params.spotPrice * params.contractSize * 0.01 * valuationResults.delta) }}</span>
          </div>
          <div class="sens-item">
            <span class="label">Цена безубыточности</span>
            <span class="value cyan">{{ formatCurrency(params.marketForwardPrice) }}</span>
          </div>
        </div>
      </div>

      <!-- Sensitivity to Interest Rates -->
      <div class="card">
        <div class="chart-header">
          <h3>Rho (∂F/∂r)</h3>
          <span class="chart-subtitle">Чувствительность к ставкам</span>
        </div>
        <div class="sensitivity-metrics">
          <div class="sens-item">
            <span class="label">Rho (Rho)</span>
            <span class="value accent">{{ valuationResults.rho.toFixed(3) }}</span>
          </div>
          <div class="sens-item">
            <span class="label">P&L на 1% ставки</span>
            <span class="value blue">{{ formatCompactCurrency(valuationResults.rho * params.contractSize * 0.01) }}</span>
          </div>
          <div class="sens-item">
            <span class="label">Текущая ставка</span>
            <span class="value cyan">{{ (params.riskFreeRate).toFixed(3) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span v-if="selectedForwardType === 'fx'">• Модель: Валютный форвард (дисконт-факторы)</span>
      <span v-else-if="selectedForwardType === 'bond'">• Модель: Форвард на облигацию (репо ставка)</span>
      <span v-else>• Модель: Cost-of-Carry (без арбитража)</span>
      <span>• Метод: {{ selectedForwardType === 'fx' ? 'Дисконтирование денежных потоков' : (selectedForwardType === 'bond' ? 'Репо финансирование' : 'Непрерывное начисление') }}</span>
      <span>• Обновление: В реальном времени</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import Chart from 'chart.js/auto'
import * as XLSX from 'xlsx'
import { valuateForward, saveRegistryToParquet, type ForwardValuationResponse } from '@/services/forwardService'
import { useForwardRegistryStore } from '@/stores/forwardRegistry'

// Используем store для реестра форвардов
const forwardRegistryStore = useForwardRegistryStore()

const selectedForwardType = ref('fx')
const calculating = ref(false)
const calculatingAll = ref(false)
const error = ref('')
const fileInputRef = ref<HTMLInputElement | null>(null)
const selectedContractIndex = ref<number | null>(null)
const savingParquet = ref(false)

// Используем данные из store
const loadedContracts = computed(() => forwardRegistryStore.registryForwards)
const contractResults = computed(() => forwardRegistryStore.forwardResults)

// Parameters
const params = ref({
  // Общие параметры
  spotPrice: 100,
  timeToMaturity: 0.25,         // лет
  marketForwardPrice: 101.50,   // рыночная цена форварда
  contractSize: 1_000_000,      // условных единиц
  
  // Cost-of-Carry параметры (для commodity, equity, rate)
  dividendYield: 2.5,           // % (дивиденды)
  carryingCost: 0.5,            // % (стоимость хранения)
  convenienceYield: 0,          // % (удобство владения)
  riskFreeRate: 4.25,           // %
  repoRate: 4.2,                // %
  
  // Bond параметры (для форварда на облигацию)
  accruedInterest: 0.5,        // Накопленный купонный доход (НКД)
  couponRate: 7.5,              // % (купонная ставка)
  couponFrequency: 2,           // Частота купонов (1, 2, 4, 12)
  faceValue: 100.0,              // Номинал облигации
  lastCouponDate: '',           // Дата последнего купона
  maturityDate: '',             // Дата погашения
  dayCountConvention: 'ACT/365', // Конвенция подсчета дней
  autoCalculateAI: true,         // Автоматически рассчитывать НКД
  bondValuationDate: new Date().toISOString().split('T')[0],
  bondExpirationDate: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  useYieldCurve: false,          // Использовать кривую доходности
  yieldCurvePoints: [            // Точки кривой доходности
    { tenor: 1, rate: 4.0 },
    { tenor: 3, rate: 4.2 },
    { tenor: 6, rate: 4.5 },
    { tenor: 12, rate: 4.8 },
    { tenor: 24, rate: 5.0 },
    { tenor: 36, rate: 5.2 }
  ],
  
  // FX параметры (для валютных форвардов)
  fxBuyCurrency: 'RUB',
  fxSellCurrency: 'CNY',
  fxBuyAmount: 407160000,
  fxSellAmount: 30000000,
  fxDealDate: new Date().toISOString().split('T')[0],
  fxValuationDate: new Date().toISOString().split('T')[0],
  fxExpirationDate: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // +90 дней по умолчанию
  settlementCurrency: 'RUB',
  fxInternalRate: 15.0,  // Ставка для покупаемой валюты (%)
  fxExternalRate: 1.7    // Ставка для продаваемой валюты (%)
})

// Valuation Results
const valuationResults = ref<ForwardValuationResponse>({
  fairForwardPrice: 0,
  forwardValue: 0,
  intrinsicValue: 0,
  timeValue: 0,
  totalValue: 0,
  delta: 0,
  rho: 0,
  netCarry: 0,
  scenarios: []
})

// Scenario Analysis - используем данные из API
const scenarioAnalysis = computed(() => {
  return valuationResults.value.scenarios || []
})

// Chart References
const priceProfileRef = ref<HTMLCanvasElement | null>(null)
const valueVsTimeRef = ref<HTMLCanvasElement | null>(null)

let priceProfileChart: Chart | null = null
let valueVsTimeChart: Chart | null = null

// Methods
const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 3,
    maximumFractionDigits: 3
  }).format(val)
}

const formatCompactCurrency = (val: number) => {
  if (Math.abs(val) >= 1_000_000) {
    return (val / 1_000_000).toFixed(3) + 'М'
  }
  return '₽' + (val / 1000).toFixed(3) + 'K'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU')
}

const updateValuation = () => {
  // Обновляем графики после расчета
  setTimeout(() => {
    initCharts()
  }, 100)
}

const calculateValuation = async () => {
  calculating.value = true
  error.value = ''
  
  try {
    const request: Record<string, unknown> = {
      forwardType: selectedForwardType.value,
      spotPrice: params.value.spotPrice,
      timeToMaturity: params.value.timeToMaturity,
      marketForwardPrice: params.value.marketForwardPrice,
      contractSize: params.value.contractSize
    }
    
    // Добавляем параметры в зависимости от типа форварда
    if (selectedForwardType.value === 'fx') {
      request.buyCurrency = params.value.fxBuyCurrency
      request.sellCurrency = params.value.fxSellCurrency
      request.buyAmount = params.value.fxBuyAmount
      request.sellAmount = params.value.fxSellAmount
      request.dealDate = params.value.fxDealDate
      request.valuationDate = params.value.fxValuationDate
      request.expirationDate = params.value.fxExpirationDate
      request.settlementCurrency = params.value.settlementCurrency || 'RUB'
      request.internalRate = params.value.fxInternalRate
      request.externalRate = params.value.fxExternalRate
    } else if (selectedForwardType.value === 'bond') {
      // Параметры для форварда на облигацию
      request.accruedInterest = params.value.accruedInterest
      request.couponRate = params.value.couponRate
      request.couponFrequency = params.value.couponFrequency
      request.faceValue = params.value.faceValue
      request.riskFreeRate = params.value.riskFreeRate
      request.repoRate = params.value.repoRate
      request.lastCouponDate = params.value.lastCouponDate || null
      request.maturityDate = params.value.maturityDate || null
      request.dayCountConvention = params.value.dayCountConvention || 'ACT/365'
      request.autoCalculateAI = params.value.autoCalculateAI !== false
      request.valuationDate = params.value.bondValuationDate || null
      request.expirationDate = params.value.bondExpirationDate || null
      
      // Кривая доходности
      if (params.value.useYieldCurve && params.value.yieldCurvePoints) {
        request.yieldCurveTenors = params.value.yieldCurvePoints.map(p => p.tenor / 12.0) // Конвертируем месяцы в годы
        request.yieldCurveRates = params.value.yieldCurvePoints.map(p => p.rate)
      }
    } else {
      // Параметры для других типов (commodity, equity, rate)
      request.dividendYield = params.value.dividendYield
      request.carryingCost = params.value.carryingCost
      request.convenienceYield = params.value.convenienceYield
      request.riskFreeRate = params.value.riskFreeRate
      if (params.value.repoRate) {
        request.repoRate = params.value.repoRate
      }
    }
    
    const result = await valuateForward(request)
    valuationResults.value = result
    updateValuation()
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Ошибка при расчете форварда'
  } finally {
    calculating.value = false
  }
}

const initCharts = () => {
  if (priceProfileChart) priceProfileChart.destroy()
  if (valueVsTimeChart) valueVsTimeChart.destroy()

  // Forward Price Profile
  if (priceProfileRef.value?.getContext('2d')) {
    const spotRange = []
    const fairForwardPrices = []
    const marketForwardPrices = []
    
    if (selectedForwardType.value === 'fx') {
      // FX Forward: используем Covered Interest Parity
      const spot = params.value.spotPrice
      const internalRate = (params.value.fxInternalRate || 4.2) / 100
      const externalRate = (params.value.fxExternalRate || 11.7) / 100
      const T = params.value.timeToMaturity
      const marketForward = params.value.marketForwardPrice
      
      for (let i = 0.7; i <= 1.3; i += 0.05) {
        const spotVariation = spot * i
        spotRange.push(spotVariation)
        
        // Covered Interest Parity: F = S × (1 + r_sell × T) / (1 + r_buy × T)
        // Для EUR/RUB: r_sell = RUB rate, r_buy = EUR rate
        const fairForward = spotVariation * (1 + externalRate * T) / (1 + internalRate * T)
        fairForwardPrices.push(fairForward)
        marketForwardPrices.push(marketForward)
      }
    } else {
      // Cost-of-Carry для других типов форвардов
      for (let i = 0.7; i <= 1.3; i += 0.05) {
        const spot = params.value.spotPrice * i
        spotRange.push(spot)
        
        const r = params.value.riskFreeRate / 100
        const d = params.value.dividendYield / 100
        const c = params.value.carryingCost / 100
        const y = params.value.convenienceYield / 100
        const T = params.value.timeToMaturity
        
        const forwardPrice = spot * Math.exp((r + c - d - y) * T)
        fairForwardPrices.push(forwardPrice)
        marketForwardPrices.push(params.value.marketForwardPrice)
      }
    }

    priceProfileChart = new Chart(priceProfileRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: spotRange.map(s => s.toFixed(2)),
        datasets: [
          {
            label: 'Fair Forward Price',
            data: fairForwardPrices,
            borderColor: '#60a5fa',
            backgroundColor: 'rgba(96, 165, 250, 0.08)',
            fill: true,
            tension: 0.4,
            pointRadius: 2,
            borderWidth: 2
          },
          {
            label: 'Market Price',
            data: marketForwardPrices,
            borderColor: '#f59e0b',
            backgroundColor: 'transparent',
            fill: false,
            tension: 0,
            borderDash: [5, 5],
            pointRadius: 0,
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: 'rgba(255,255,255,0.6)' } } },
        scales: {
          x: { 
            title: { display: true, text: 'Spot Price', color: 'rgba(255,255,255,0.5)' },
            grid: { display: false }, 
            ticks: { color: 'rgba(255,255,255,0.3)' } 
          },
          y: { 
            title: { display: true, text: 'Forward Price', color: 'rgba(255,255,255,0.5)' },
            grid: { color: 'rgba(255,255,255,0.05)' }, 
            ticks: { color: 'rgba(255,255,255,0.3)' } 
          }
        }
      }
    } as any)
  }

  // Forward Value vs Time
  if (valueVsTimeRef.value?.getContext('2d')) {
    const timePoints = []
    const values = []
    
    if (selectedForwardType.value === 'fx') {
      // FX Forward: NPV эволюция по времени
      const spot = params.value.spotPrice
      const marketForward = params.value.marketForwardPrice
      const internalRate = (params.value.fxInternalRate || 4.2) / 100
      const externalRate = (params.value.fxExternalRate || 11.7) / 100
      const buyAmount = params.value.fxBuyAmount || 1_000_000
      
      // Рассчитываем T из дат, если доступны
      let T = params.value.timeToMaturity
      if (params.value.fxValuationDate && params.value.fxExpirationDate) {
        const valDate = new Date(params.value.fxValuationDate)
        const expDate = new Date(params.value.fxExpirationDate)
        const daysDiff = (expDate.getTime() - valDate.getTime()) / (1000 * 60 * 60 * 24)
        T = daysDiff / 365.0
      }
      
      for (let i = 0; i <= 12; i++) {
        const t = (T * i) / 12
        const remainingT = T - t
        
        if (remainingT > 0) {
          // Справедливый форвард на момент t (спот остается тем же, но время до экспирации уменьшается)
          const fairForwardAtT = spot * (1 + externalRate * remainingT) / (1 + internalRate * remainingT)
          // PnL на экспирацию
          const pnlAtMaturity = (marketForward - fairForwardAtT) * buyAmount
          // NPV с дисконтированием по оставшемуся времени (дисконтируем по ставке settlement currency = RUB)
          const npv = pnlAtMaturity / (1 + externalRate * remainingT)
          values.push(npv)
        } else {
          values.push(0)
        }
        timePoints.push((t * 12).toFixed(0))
      }
    } else {
      // Cost-of-Carry для других типов
      for (let t = 0; t <= params.value.timeToMaturity; t += params.value.timeToMaturity / 12) {
        const r = params.value.riskFreeRate / 100
        const S0 = params.value.spotPrice
        const K = params.value.marketForwardPrice
        
        const forwardValue = (S0 - K) / Math.exp(r * t)
        timePoints.push((t * 12).toFixed(0))
        values.push(forwardValue)
      }
    }

    valueVsTimeChart = new Chart(valueVsTimeRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: timePoints,
        datasets: [{
          label: selectedForwardType.value === 'fx' ? 'NPV Contract (RUB)' : 'Forward Value',
          data: values,
          borderColor: '#38bdf8',
          backgroundColor: 'rgba(56, 189, 248, 0.08)',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { 
            title: { display: true, text: 'Months to Maturity', color: 'rgba(255,255,255,0.5)' },
            grid: { display: false }, 
            ticks: { color: 'rgba(255,255,255,0.3)' } 
          },
          y: { 
            title: { display: true, text: selectedForwardType.value === 'fx' ? 'NPV (RUB)' : 'Value', color: 'rgba(255,255,255,0.5)' },
            grid: { color: 'rgba(255,255,255,0.05)' }, 
            ticks: { color: 'rgba(255,255,255,0.3)' } 
          }
        }
      }
    } as any)
  }
}

// Обновляем графики при изменении типа форварда
watch(selectedForwardType, () => {
  setTimeout(() => {
    initCharts()
  }, 100)
})

// Обновляем графики при изменении параметров (debounce)
let chartUpdateTimeout: ReturnType<typeof setTimeout> | null = null
watch(() => [
  params.value.spotPrice,
  params.value.marketForwardPrice,
  params.value.timeToMaturity,
  params.value.fxInternalRate,
  params.value.fxExternalRate,
  params.value.fxBuyAmount,
  params.value.riskFreeRate,
  params.value.dividendYield
], () => {
  if (chartUpdateTimeout) clearTimeout(chartUpdateTimeout)
  chartUpdateTimeout = setTimeout(() => {
    if (priceProfileRef.value && valueVsTimeRef.value) {
      initCharts()
    }
  }, 300)
}, { deep: true })

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
    const contracts: Record<string, unknown>[] = []
    
    for (const row of jsonData as any[]) {
      const contract: Record<string, unknown> = {
        forwardType: row['Тип'] || row['Type'] || row['type'] || selectedForwardType.value,
      }

      // FX форварды
      if (contract.forwardType === 'fx' || selectedForwardType.value === 'fx') {
        contract.fxSellCurrency = row['Валюта продажи'] || row['Sell Currency'] || row['sell_currency'] || 'CNY'
        contract.fxBuyCurrency = row['Валюта покупки'] || row['Buy Currency'] || row['buy_currency'] || 'RUB'
        contract.fxSellAmount = parseFloat(row['Сумма продажи'] || row['Sell Amount'] || row['sell_amount'] || '0')
        contract.fxBuyAmount = parseFloat(row['Сумма покупки'] || row['Buy Amount'] || row['buy_amount'] || '0')
        contract.fxInternalRate = parseFloat(row['Ставка покупки'] || row['Internal Rate'] || row['internal_rate'] || '15.0')
        contract.fxExternalRate = parseFloat(row['Ставка продажи'] || row['External Rate'] || row['external_rate'] || '1.7')
        contract.spotPrice = parseFloat(row['Спот курс'] || row['Spot Rate'] || row['spot_rate'] || row['Spot'] || '0')
        contract.marketForwardPrice = parseFloat(row['Курс сделки'] || row['Forward Rate'] || row['forward_rate'] || row['Market Forward'] || '0')
      } else {
        // Другие типы форвардов
        contract.spotPrice = parseFloat(row['Спот цена'] || row['Spot Price'] || row['spot_price'] || row['Spot'] || '0')
        contract.marketForwardPrice = parseFloat(row['Рыночная цена'] || row['Market Forward'] || row['market_forward'] || row['Forward'] || '0')
        contract.riskFreeRate = parseFloat(row['Безрисковая ставка'] || row['Risk Free Rate'] || row['risk_free_rate'] || '4.25')
        contract.timeToMaturity = parseFloat(row['Время до экспирации'] || row['Time to Maturity'] || row['time_to_maturity'] || '0.25')
        
        // Для облигаций
        if (contract.forwardType === 'bond' || selectedForwardType.value === 'bond') {
          contract.couponRate = parseFloat(row['Купонная ставка'] || row['Coupon Rate'] || row['coupon_rate'] || '7.5')
          contract.faceValue = parseFloat(row['Номинал'] || row['Face Value'] || row['face_value'] || '100')
          contract.repoRate = parseFloat(row['Репо ставка'] || row['Repo Rate'] || row['repo_rate'] || '4.2')
        }
      }

      // Общие поля
      contract.valuationDate = row['Дата оценки'] || row['Valuation Date'] || row['valuation_date'] || new Date().toISOString().split('T')[0]
      contract.expirationDate = row['Дата экспирации'] || row['Expiration Date'] || row['expiration_date'] || new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      contract.contractSize = parseFloat(row['Размер контракта'] || row['Contract Size'] || row['contract_size'] || '1000000')

      // Проверяем, что есть минимальные данные
      if (contract.spotPrice > 0 || contract.fxSellAmount > 0) {
        contracts.push(contract)
      }
    }

    // Сохраняем реестр в store
    forwardRegistryStore.loadRegistry(contracts)
    selectedContractIndex.value = null
    error.value = ''
  } catch (err: unknown) {
    error.value = `Ошибка при загрузке файла: ${err instanceof Error ? err.message : String(err)}`
  }
}

// Select contract from registry
const selectContract = (index: number) => {
  selectedContractIndex.value = index
}

// Load contract to form
const loadContractToForm = (index: number) => {
  const contract = forwardRegistryStore.getForwardByIndex(index)
  if (!contract) return

  selectedForwardType.value = contract.forwardType || selectedForwardType.value

  // Загружаем параметры в форму
  if (contract.forwardType === 'fx' || selectedForwardType.value === 'fx') {
    params.value.fxSellCurrency = contract.fxSellCurrency || params.value.fxSellCurrency
    params.value.fxBuyCurrency = contract.fxBuyCurrency || params.value.fxBuyCurrency
    params.value.fxSellAmount = contract.fxSellAmount || params.value.fxSellAmount
    params.value.fxBuyAmount = contract.fxBuyAmount || params.value.fxBuyAmount
    params.value.fxInternalRate = contract.fxInternalRate || params.value.fxInternalRate
    params.value.fxExternalRate = contract.fxExternalRate || params.value.fxExternalRate
    params.value.spotPrice = contract.spotPrice || params.value.spotPrice
    params.value.fxValuationDate = contract.valuationDate || params.value.fxValuationDate
    params.value.fxExpirationDate = contract.expirationDate || params.value.fxExpirationDate
  } else {
    params.value.spotPrice = contract.spotPrice || params.value.spotPrice
    params.value.marketForwardPrice = contract.marketForwardPrice || params.value.marketForwardPrice
    params.value.riskFreeRate = contract.riskFreeRate || params.value.riskFreeRate
    params.value.timeToMaturity = contract.timeToMaturity || params.value.timeToMaturity
    
    if (contract.forwardType === 'bond' || selectedForwardType.value === 'bond') {
      params.value.couponRate = contract.couponRate || params.value.couponRate
      params.value.faceValue = contract.faceValue || params.value.faceValue
      params.value.repoRate = contract.repoRate || params.value.repoRate
      params.value.bondValuationDate = contract.valuationDate || params.value.bondValuationDate
      params.value.bondExpirationDate = contract.expirationDate || params.value.bondExpirationDate
    }
  }

  params.value.contractSize = contract.contractSize || params.value.contractSize
  
  // Автоматически рассчитываем после загрузки
  setTimeout(() => {
    calculateValuation()
  }, 100)
}

// Calculate all contracts
const calculateAllContracts = async () => {
  calculatingAll.value = true
  error.value = ''

  try {
    const results: (ForwardValuationResponse | null)[] = []
    
    for (let i = 0; i < forwardRegistryStore.registryForwards.length; i++) {
      const contract = forwardRegistryStore.registryForwards[i]
      const request: Record<string, unknown> = {
        forwardType: contract.forwardType || selectedForwardType.value,
        spotPrice: contract.spotPrice || 0,
        timeToMaturity: contract.timeToMaturity || 0.25,
        marketForwardPrice: contract.marketForwardPrice || 0,
        contractSize: contract.contractSize || 1_000_000
      }

      // Добавляем параметры в зависимости от типа
      if (contract.forwardType === 'fx' || selectedForwardType.value === 'fx') {
        request.buyCurrency = contract.fxBuyCurrency
        request.sellCurrency = contract.fxSellCurrency
        request.buyAmount = contract.fxBuyAmount
        request.sellAmount = contract.fxSellAmount
        request.valuationDate = contract.valuationDate
        request.expirationDate = contract.expirationDate
        request.internalRate = contract.fxInternalRate
        request.externalRate = contract.fxExternalRate
      } else if (contract.forwardType === 'bond' || selectedForwardType.value === 'bond') {
        request.couponRate = contract.couponRate
        request.faceValue = contract.faceValue
        request.repoRate = contract.repoRate
        request.riskFreeRate = contract.riskFreeRate
        request.valuationDate = contract.valuationDate
        request.expirationDate = contract.expirationDate
      } else {
        request.riskFreeRate = contract.riskFreeRate
      }

      try {
        const result = await valuateForward(request)
        results.push(result)
        forwardRegistryStore.setForwardResult(i, result)
      } catch (err: unknown) {
        const errorResult: ForwardValuationResponse = {
          fairForwardPrice: 0,
          forwardValue: 0,
          intrinsicValue: 0,
          timeValue: 0,
          totalValue: 0,
          delta: 0,
          rho: 0,
          netCarry: 0,
          scenarios: []
        }
        results.push(errorResult)
        forwardRegistryStore.setForwardResult(i, errorResult)
      }
    }
    
    // Сохраняем все результаты в store
    forwardRegistryStore.setAllResults(results)
  } catch (err: unknown) {
    error.value = `Ошибка при расчете контрактов: ${err instanceof Error ? err.message : String(err)}`
  } finally {
    calculatingAll.value = false
  }
}

// Export registry to Excel
const exportRegistryToExcel = () => {
  if (forwardRegistryStore.registryForwards.length === 0) {
    alert('Нет данных для экспорта. Загрузите реестр форвардов.')
    return
  }

  // Check if any contracts were calculated
  const hasCalculatedContracts = forwardRegistryStore.forwardResults.length > 0 && forwardRegistryStore.forwardResults.some(r => r && r.fairForwardPrice !== null && r.fairForwardPrice !== undefined)
  
  if (!hasCalculatedContracts) {
    const confirmExport = confirm('Контракты еще не рассчитаны. Экспортировать только входные параметры?')
    if (!confirmExport) return
  }

  // Prepare data for export with all available information
  const exportData = forwardRegistryStore.registryForwards.map((contract, idx) => {
    const result = forwardRegistryStore.getResultByIndex(idx)
    const contractType = contract.forwardType || selectedForwardType.value
    
    const baseData: Record<string, unknown> = {
      '№': idx + 1,
      'Тип': contractType.toUpperCase(),
      'Дата оценки': contract.valuationDate || '',
      'Дата экспирации': contract.expirationDate || '',
      'Рыночная цена': contract.marketForwardPrice || 0,
      'Размер контракта': contract.contractSize || 1_000_000
    }

    // FX форварды
    if (contractType === 'fx' || selectedForwardType.value === 'fx') {
      baseData['Валюта продажи'] = contract.fxSellCurrency || ''
      baseData['Валюта покупки'] = contract.fxBuyCurrency || ''
      baseData['Сумма продажи'] = contract.fxSellAmount || 0
      baseData['Сумма покупки'] = contract.fxBuyAmount || 0
      baseData['Спот курс'] = contract.spotPrice || 0
      baseData['Ставка покупки (%)'] = contract.fxInternalRate || 0
      baseData['Ставка продажи (%)'] = contract.fxExternalRate || 0
    } else {
      // Другие типы форвардов
      baseData['Спот цена'] = contract.spotPrice || 0
      baseData['Время до экспирации (лет)'] = contract.timeToMaturity || 0
      baseData['Безрисковая ставка (%)'] = contract.riskFreeRate || 0
      
      if (contractType === 'bond' || selectedForwardType.value === 'bond') {
        baseData['Купонная ставка (%)'] = contract.couponRate || 0
        baseData['Номинал'] = contract.faceValue || 0
        baseData['Репо ставка (%)'] = contract.repoRate || 0
        baseData['Частота купонов'] = contract.couponFrequency || 2
        baseData['НКД'] = contract.accruedInterest || 0
      } else if (contractType === 'equity') {
        baseData['Дивиденды (%)'] = contract.dividendYield || 0
      } else if (contractType === 'commodity') {
        baseData['Стоимость хранения (%)'] = contract.carryingCost || 0
        baseData['Удобство владения (%)'] = contract.convenienceYield || 0
      }
    }

    // Результаты расчетов
    if (result) {
      baseData['Справедливая цена'] = result.fairForwardPrice !== null && result.fairForwardPrice !== undefined ? result.fairForwardPrice.toFixed(6) : ''
      baseData['Стоимость (на единицу)'] = result.forwardValue !== null && result.forwardValue !== undefined ? result.forwardValue.toFixed(6) : ''
      baseData['Стоимость (на контракт)'] = result.forwardValue !== null && result.forwardValue !== undefined 
        ? (result.forwardValue * (contract.contractSize || 1_000_000)).toFixed(2) : ''
      baseData['Внутренняя стоимость'] = result.intrinsicValue !== null && result.intrinsicValue !== undefined ? result.intrinsicValue.toFixed(6) : ''
      baseData['Временная стоимость'] = result.timeValue !== null && result.timeValue !== undefined ? result.timeValue.toFixed(6) : ''
      baseData['Общая стоимость'] = result.totalValue !== null && result.totalValue !== undefined ? result.totalValue.toFixed(6) : ''
      baseData['Delta (Δ)'] = result.delta !== null && result.delta !== undefined ? result.delta.toFixed(6) : ''
      baseData['Rho (ρ)'] = result.rho !== null && result.rho !== undefined ? result.rho.toFixed(6) : ''
      baseData['Net Carry'] = result.netCarry !== null && result.netCarry !== undefined ? (result.netCarry * 100).toFixed(4) + '%' : ''
      
      // FX специфичные поля
      if (contractType === 'fx' || selectedForwardType.value === 'fx') {
        baseData['Валютная пара'] = result.currencyPair || ''
        baseData['Форвардный курс (мин)'] = result.forwardRateMin !== null && result.forwardRateMin !== undefined ? result.forwardRateMin.toFixed(6) : ''
        baseData['Форвардный курс (макс)'] = result.forwardRateMax !== null && result.forwardRateMax !== undefined ? result.forwardRateMax.toFixed(6) : ''
        baseData['Дисконт-фактор (внутр.)'] = result.discountFactorInternal !== null && result.discountFactorInternal !== undefined ? result.discountFactorInternal.toFixed(6) : ''
        baseData['Дисконт-фактор (внешн.)'] = result.discountFactorExternal !== null && result.discountFactorExternal !== undefined ? result.discountFactorExternal.toFixed(6) : ''
        baseData['Справедливая стоимость (мин)'] = result.fairValueMin !== null && result.fairValueMin !== undefined ? result.fairValueMin.toFixed(2) : ''
        baseData['Справедливая стоимость (макс)'] = result.fairValueMax !== null && result.fairValueMax !== undefined ? result.fairValueMax.toFixed(2) : ''
        if (result.forwardDiff !== undefined) {
          baseData['Расхождение с курсом сделки'] = typeof result.forwardDiff === 'string' ? result.forwardDiff : result.forwardDiff.toFixed(6)
        }
      }
      
      // Bond специфичные поля
      if (contractType === 'bond' || selectedForwardType.value === 'bond') {
        baseData['DV01'] = result.dv01 !== null && result.dv01 !== undefined ? result.dv01.toFixed(6) : ''
        baseData['Convexity'] = result.convexity !== null && result.convexity !== undefined ? result.convexity.toFixed(4) : ''
        baseData['Repo Sensitivity'] = result.repoSensitivity !== null && result.repoSensitivity !== undefined ? result.repoSensitivity.toFixed(6) : ''
        baseData['PV купонов'] = result.pvCoupons !== null && result.pvCoupons !== undefined ? result.pvCoupons.toFixed(2) : ''
        baseData['Спот цена (dirty)'] = result.spotDirtyPrice !== null && result.spotDirtyPrice !== undefined ? result.spotDirtyPrice.toFixed(6) : ''
        baseData['Форвард цена (dirty)'] = result.forwardDirtyPrice !== null && result.forwardDirtyPrice !== undefined ? result.forwardDirtyPrice.toFixed(6) : ''
        baseData['НКД на экспирацию'] = result.aiForward !== null && result.aiForward !== undefined ? result.aiForward.toFixed(6) : ''
        
        if (result.formulaBreakdown) {
          baseData['Спот цена (clean)'] = result.formulaBreakdown.spotCleanPrice.toFixed(6)
          baseData['НКД на дату оценки'] = result.formulaBreakdown.accruedInterestSpot.toFixed(6)
          baseData['Стоимость финансирования'] = result.formulaBreakdown.financingCost.toFixed(6)
          baseData['PV купонов (детально)'] = result.formulaBreakdown.totalCouponsPV.toFixed(6)
        }
      }
      
      baseData['Статус расчета'] = 'Рассчитан'
    } else {
      baseData['Статус расчета'] = 'Не рассчитан'
    }

    return baseData
  })

  // Create workbook with multiple sheets
  const wb = XLSX.utils.book_new()
  
  // Main registry sheet
  const ws = XLSX.utils.json_to_sheet(exportData)
  
  // Set column widths for better readability
  const colWidths: Record<string, number>[] = []
  const maxCols = Math.max(...exportData.map(row => Object.keys(row).length))
  for (let i = 0; i < maxCols; i++) {
    colWidths.push({ wch: 18 })
  }
  ws['!cols'] = colWidths
  
  XLSX.utils.book_append_sheet(wb, ws, 'Реестр форвардов')

  // Add scenarios sheet if there are calculated contracts
  if (hasCalculatedContracts) {
    const scenariosData: Record<string, unknown>[] = []
    
    loadedContracts.value.forEach((contract, contractIdx) => {
      const result = contractResults.value[contractIdx]
      if (result && result.scenarios && result.scenarios.length > 0) {
        result.scenarios.forEach((scenario, scenarioIdx) => {
          scenariosData.push({
            '№ контракта': contractIdx + 1,
            'Тип': contract.forwardType || selectedForwardType.value,
            '№ сценария': scenarioIdx + 1,
            'Название сценария': scenario.name,
            'Спот цена': scenario.spotPrice.toFixed(6),
            '% Изменение': (scenario.change >= 0 ? '+' : '') + scenario.change.toFixed(2) + '%',
            'Стоимость форварда': scenario.forwardValue.toFixed(6),
            'P&L (Лонг)': scenario.pnlLong.toFixed(2),
            'P&L (Шорт)': scenario.pnlShort.toFixed(2),
            'Базовый сценарий': scenario.isBase ? 'Да' : 'Нет'
          })
        })
      }
    })
    
    if (scenariosData.length > 0) {
      const wsScenarios = XLSX.utils.json_to_sheet(scenariosData)
      const scenarioColWidths = [
        { wch: 10 }, { wch: 10 }, { wch: 10 }, { wch: 20 }, { wch: 15 }, { wch: 15 }, { wch: 18 }, { wch: 15 }, { wch: 15 }, { wch: 15 }
      ]
      wsScenarios['!cols'] = scenarioColWidths
      XLSX.utils.book_append_sheet(wb, wsScenarios, 'Сценарии')
    }
  }

  // Add coupon schedule sheet for bond forwards
  if (hasCalculatedContracts) {
    const couponScheduleData: Record<string, unknown>[] = []
    
    forwardRegistryStore.registryForwards.forEach((contract, contractIdx) => {
      const result = forwardRegistryStore.getResultByIndex(contractIdx)
      if (result && result.couponSchedule && result.couponSchedule.length > 0) {
        result.couponSchedule.forEach((coupon) => {
          couponScheduleData.push({
            '№ контракта': contractIdx + 1,
            'Тип': contract.forwardType || selectedForwardType.value,
            '№ купона': coupon.couponNumber,
            'Дата купона': formatDate(coupon.couponDate),
            'Дней до платежа': coupon.daysToPayment,
            'Лет до платежа': coupon.yearsToPayment.toFixed(4),
            'Сумма купона': coupon.couponAmount.toFixed(2),
            'Ставка дисконтирования (%)': coupon.discountRate.toFixed(3),
            'Дисконт-фактор': coupon.discountFactor.toFixed(6),
            'Приведенная стоимость': coupon.presentValue.toFixed(2)
          })
        })
      }
    })
    
    if (couponScheduleData.length > 0) {
      const wsCoupons = XLSX.utils.json_to_sheet(couponScheduleData)
      const couponColWidths = [
        { wch: 10 }, { wch: 10 }, { wch: 10 }, { wch: 12 }, { wch: 15 }, { wch: 15 }, { wch: 15 }, { wch: 20 }, { wch: 15 }, { wch: 18 }
      ]
      wsCoupons['!cols'] = couponColWidths
      XLSX.utils.book_append_sheet(wb, wsCoupons, 'Расписание купонов')
    }
  }

  // Generate filename with date and time
  const now = new Date()
  const dateStr = now.toISOString().split('T')[0]
  const timeStr = now.toTimeString().split(' ')[0].replace(/:/g, '-')
  const fileName = `реестр_форвардов_${dateStr}_${timeStr}.xlsx`

  // Save file
  try {
    XLSX.writeFile(wb, fileName)
    alert(`Реестр успешно экспортирован: ${fileName}\n${hasCalculatedContracts ? 'Включая все расчеты, сценарии и расписание купонов.' : 'Только входные параметры (контракты не рассчитаны).'}`)
  } catch (err: unknown) {
    alert(`Ошибка при экспорте файла: ${err instanceof Error ? err.message : String(err)}`)
  }
}

// Save registry to parquet
const saveRegistryToParquetHandler = async () => {
  if (forwardRegistryStore.registryForwards.length === 0) return

  savingParquet.value = true
  error.value = ''

  try {
    const result = await saveRegistryToParquet(forwardRegistryStore.registryForwards)
    if (result.success) {
      error.value = `Реестр успешно сохранен: ${result.data.file_name}`
      setTimeout(() => {
        error.value = ''
      }, 5000)
    }
  } catch (err: unknown) {
    error.value = `Ошибка при сохранении реестра: ${err instanceof Error ? err.message : String(err)}`
  } finally {
    savingParquet.value = false
  }
}

// Clear registry
const clearRegistry = () => {
  forwardRegistryStore.clearRegistry()
  selectedContractIndex.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

// Add forward manually (сохраняем возможность ручного добавления)
const addForwardManually = () => {
  const newForward: Record<string, unknown> = {
    forwardType: selectedForwardType.value,
    spotPrice: params.value.spotPrice,
    timeToMaturity: params.value.timeToMaturity,
    marketForwardPrice: params.value.marketForwardPrice,
    contractSize: params.value.contractSize,
    riskFreeRate: params.value.riskFreeRate,
    valuationDate: selectedForwardType.value === 'fx' ? params.value.fxValuationDate : params.value.bondValuationDate,
    expirationDate: selectedForwardType.value === 'fx' ? params.value.fxExpirationDate : params.value.bondExpirationDate
  }
  
  // Добавляем специфичные параметры
  if (selectedForwardType.value === 'fx') {
    newForward.fxBuyCurrency = params.value.fxBuyCurrency
    newForward.fxSellCurrency = params.value.fxSellCurrency
    newForward.fxBuyAmount = params.value.fxBuyAmount
    newForward.fxSellAmount = params.value.fxSellAmount
    newForward.fxInternalRate = params.value.fxInternalRate
    newForward.fxExternalRate = params.value.fxExternalRate
  } else if (selectedForwardType.value === 'bond') {
    newForward.couponRate = params.value.couponRate
    newForward.faceValue = params.value.faceValue
    newForward.repoRate = params.value.repoRate
    newForward.accruedInterest = params.value.accruedInterest
    newForward.couponFrequency = params.value.couponFrequency
  } else {
    newForward.dividendYield = params.value.dividendYield
    newForward.carryingCost = params.value.carryingCost
    newForward.convenienceYield = params.value.convenienceYield
  }
  
  forwardRegistryStore.addForward(newForward)
}

onMounted(() => {
  calculateValuation()
})

onBeforeUnmount(() => {
  if (chartUpdateTimeout) clearTimeout(chartUpdateTimeout)
  if (priceProfileChart) priceProfileChart.destroy()
  if (valueVsTimeChart) valueVsTimeChart.destroy()
})
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.forward-valuation-page {
  width: 100%;
  padding: 24px;
  background: linear-gradient(180deg, rgba(15,20,25,0.5) 0%, rgba(26,31,46,0.3) 100%);
  color: #fff;
  min-height: 100vh;
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
}

/* ============================================
   HEADER
   ============================================ */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  gap: 24px;
  flex-wrap: wrap;
}

.header-left {
  flex: 1;
  min-width: 300px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  letter-spacing: -0.01em;
}

.page-subtitle {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
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

.forward-type-select {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  padding: 4px 8px;
  cursor: pointer;
}

.forward-type-select option {
  background: #1e1f28;
  color: #fff;
}

.btn-primary {
  padding: 8px 16px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  white-space: nowrap;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
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

.scenario-table tr.selected {
  background: rgba(59, 130, 246, 0.15);
  border-left: 3px solid #3b82f6;
}

/* ============================================
   GRID LAYOUTS
   ============================================ */
.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.full-width {
  grid-column: 1 / -1;
}

/* ============================================
   CARDS
   ============================================ */
.card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 
    0 20px 40px -10px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
  margin-bottom: 20px;
}

.card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
}

.card:hover {
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
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

/* ============================================
   PARAMETERS
   ============================================ */
.parameter-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.param-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.param-row label {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
  min-width: 180px;
}

.param-input {
  flex: 1;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-family: "SF Mono", monospace;
}

.param-input:focus {
  outline: none;
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.05);
}

.param-value {
  flex: 1;
  color: #fff;
  font-size: 12px;
  font-family: "SF Mono", monospace;
  text-align: right;
  font-weight: 600;
}

.param-value.positive {
  color: #4ade80;
}

.param-value.negative {
  color: #f87171;
}

/* ============================================
   METRIC CARDS
   ============================================ */
.metric-card {
  background: rgba(30, 32, 40, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-header {
  margin-bottom: 8px;
}

.metric-header h3 {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  margin: 0;
}

.metric-unit {
  font-size: 10px;
  color: rgba(255,255,255,0.3);
  display: block;
  margin-top: 4px;
}

.metric-value {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.metric-value.accent {
  color: #f59e0b;
}

.metric-value.blue {
  color: #60a5fa;
}

.metric-value.positive {
  color: #4ade80;
}

.metric-value.negative {
  color: #f87171;
}

.metric-detail {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: rgba(255,255,255,0.4);
}

/* ============================================
   CARRY BREAKDOWN
   ============================================ */
.carry-breakdown {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.carry-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: rgba(255,255,255,0.02);
  border-radius: 6px;
  font-size: 12px;
}

.carry-label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.carry-value {
  font-weight: 700;
  font-family: "SF Mono", monospace;
  color: #fff;
}

.carry-value.negative {
  color: #f87171;
}

.carry-value.cyan {
  color: #06b6d4;
}

.carry-item.total {
  background: rgba(255,255,255,0.04);
  border-top: 1px solid rgba(255,255,255,0.1);
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.carry-item.final {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

/* ============================================
   VALUE BREAKDOWN
   ============================================ */
.value-breakdown {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.item .label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.item .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.item .value.accent {
  color: #f59e0b;
}

.item .value.blue {
  color: #60a5fa;
}

.item .value.positive {
  color: #4ade80;
}

.item .value.negative {
  color: #f87171;
}

.item.total {
  border-top: 1px solid rgba(255,255,255,0.1);
  border-bottom: none;
  padding-top: 10px;
}

/* ============================================
   CHARTS
   ============================================ */
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  flex-direction: column;
  gap: 4px;
}

.chart-header h3 {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  margin: 0;
}

.chart-subtitle {
  font-size: 10px;
  color: rgba(255,255,255,0.3);
  font-weight: normal;
}

.chart-container {
  position: relative;
  width: 100%;
  height: 360px;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(107, 114, 128, 0.08);
}

.chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

/* ============================================
   SCENARIO TABLE
   ============================================ */
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

.scenario-name {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
}

.spot-price,
.change,
.forward-value,
.pnl {
  font-family: "SF Mono", monospace;
}

.scenario-table .positive {
  color: #4ade80;
}

.scenario-table .negative {
  color: #f87171;
}

.scenario-table tr.base {
  background: rgba(59, 130, 246, 0.1);
}

/* ============================================
   SENSITIVITY METRICS
   ============================================ */
.sensitivity-metrics {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sens-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.sens-item .label {
  color: rgba(255,255,255,0.6);
}

.sens-item .value {
  font-weight: 600;
  font-family: "SF Mono", monospace;
}

.sens-item .value.accent {
  color: #f59e0b;
}

.sens-item .value.blue {
  color: #60a5fa;
}

.sens-item .value.cyan {
  color: #06b6d4;
}

/* ============================================
   ARBITRAGE ANALYSIS
   ============================================ */
.arbitrage-analysis {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.arb-section {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  padding: 16px;
}

.arb-section h4 {
  font-size: 12px;
  color: rgba(255,255,255,0.7);
  margin: 0 0 10px 0;
  font-weight: 600;
}

.arb-strategy {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.strategy-label {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.strategy-steps {
  margin: 6px 0;
  padding-left: 20px;
  font-size: 10px;
  color: rgba(255,255,255,0.5);
}

.strategy-steps li {
  margin: 2px 0;
}

.profit-value {
  font-size: 12px;
  font-weight: 700;
  font-family: "SF Mono", monospace;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.profit-value.positive {
  color: #4ade80;
}

/* ============================================
   FORMULAS GRID
   ============================================ */
.formulas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.formula-card {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.formula-card h4 {
  font-size: 11px;
  color: rgba(255,255,255,0.7);
  margin: 0;
  font-weight: 600;
}

.formula {
  font-size: 10px;
  color: #60a5fa;
  font-family: "SF Mono", monospace;
  background: rgba(96, 165, 250, 0.1);
  padding: 6px;
  border-radius: 4px;
}

.description {
  font-size: 9px;
  color: rgba(255,255,255,0.4);
}

/* ============================================
   ERROR MESSAGE
   ============================================ */
.error-message {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  color: #fca5a5;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ============================================
   FOOTER
   ============================================ */
.page-footer {
  display: flex;
  gap: 16px;
  justify-content: center;
  font-size: 11px;
  color: rgba(255,255,255,0.3);
  margin-top: 24px;
  flex-wrap: wrap;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .page-header {
    flex-direction: column;
  }

  .header-right {
    width: 100%;
    flex-direction: column;
  }

  .control-group {
    width: 100%;
  }

  .grid-2,
  .grid-3 {
    grid-template-columns: 1fr;
  }

  .arbitrage-analysis {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .forward-valuation-page {
    padding: 16px;
  }

  .param-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .param-row label {
    min-width: unset;
  }

  .param-input {
    width: 100%;
  }

  .chart-container {
    height: 300px;
  }

  .scenario-table {
    font-size: 10px;
  }

  .scenario-table th,
  .scenario-table td {
    padding: 6px;
  }

  .formulas-grid {
    grid-template-columns: 1fr;
  }
}
</style>
