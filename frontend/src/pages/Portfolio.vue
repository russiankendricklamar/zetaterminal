<!-- src/views/PortfolioView.vue - SIMPLIFIED VERSION -->
<template>
  <div class="portfolio-page">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-left">
        <div class="hero-title-row">
          <h1>
            Управление портфелем ценных бумаг банка: <span class="bank-selector-inline-wrapper">
              <div class="bank-selector-wrapper">
                <div
                  class="bank-selector"
                  :class="{ 'is-open': isBankMenuOpen }"
                  @click="toggleBankMenu"
                >
                  <div class="bank-selector-content">
                    <span class="bank-selector-name">{{ selectedBank?.name || 'Выберите банк' }}</span>
                    <span class="bank-selector-reg">№ {{ selectedBank?.regNumber || '' }}</span>
                  </div>
                  <svg
                    class="bank-selector-chevron"
                    width="12"
                    height="8"
                    viewBox="0 0 12 8"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path d="M1 1L6 6L11 1" />
                  </svg>
                </div>
                <transition name="dropdown-fade">
                  <div
                    v-if="isBankMenuOpen"
                    class="bank-dropdown"
                  >
                    <div class="bank-dropdown-search">
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                      >
                        <circle
                          cx="11"
                          cy="11"
                          r="8"
                        />
                        <line
                          x1="21"
                          y1="21"
                          x2="16.65"
                          y2="16.65"
                        />
                      </svg>
                      <input
                        v-model="bankSearchQuery"
                        type="text"
                        placeholder="Поиск банка..."
                        class="bank-search-input"
                        @click.stop
                      >
                    </div>
                    <div class="bank-dropdown-list">
                      <div
                        v-for="bank in filteredBanks"
                        :key="bank.regNumber"
                        class="bank-dropdown-item"
                        :class="{ 'is-selected': bank.regNumber === selectedBank.regNumber }"
                        @click="selectBank(bank)"
                      >
                        <div class="bank-item-content">
                          <span class="bank-item-name">{{ bank.name }}</span>
                          <span class="bank-item-reg">№ {{ bank.regNumber }}</span>
                        </div>
                        <svg
                          v-if="bank.regNumber === selectedBank.regNumber"
                          width="14"
                          height="14"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="3"
                        >
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      </div>
                    </div>
                  </div>
                </transition>
              </div>
            </span>
          </h1>
        </div>
        <div class="hero-meta">
          <span class="glass-pill">Стратегия: <strong>Мультиактив</strong></span>
          <span class="glass-pill">Ребалансировка: <strong>Ежемесячно</strong></span>
          <span class="glass-pill risk-aggressive">
            <span class="status-dot" />
            Риск: Агрессивный
          </span>
        </div>
      </div>
      <div class="hero-actions">
        <div class="last-update">
          Обновлено: <span class="mono">{{ lastUpdate }}</span>
        </div>
        <button
          class="btn-glass outline"
          @click="exportPdf"
        >
          <svg
            width="16"
            height="16"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          ><path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          /></svg>
          Экспорт PDF
        </button>
      </div>
    </div>

    <!-- KPI Grid -->
    <div class="kpi-grid">
      <div class="glass-card kpi-card glow-green">
        <div class="kpi-header">
          <span class="kpi-label">Общий P&L</span>
          <div
            class="trend-badge"
            :class="portfolioMetrics?.annual_return && portfolioMetrics.annual_return >= 0 ? 'positive' : 'negative'"
          >
            <svg
              width="10"
              height="10"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="4"
            >
              <path
                v-if="portfolioMetrics?.annual_return && portfolioMetrics.annual_return >= 0"
                d="M18 15l-6-6-6 6"
              />
              <path
                v-else
                d="M6 9l6 6 6-6"
              />
            </svg>
            {{ portfolioMetrics ? (portfolioMetrics.annual_return * 100).toFixed(1) + '%' : '12.4%' }}
          </div>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-gradient-green">
            {{ portfolioMetrics ? portfolioMetrics.total_pnl.toLocaleString('ru-RU', { maximumFractionDigits: 0 }) : '452,109' }}
            <small>RUB</small>
          </div>
          <div class="kpi-sub">
            ЧСА: {{ portfolioMetrics ? (portfolioMetrics.nav / 1000000).toFixed(2) + 'M' : '3.64M' }}
          </div>
        </div>
      </div>

      <div class="glass-card kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">VaR 95%</span>
          <div class="trend-badge negative">
            <svg
              width="10"
              height="10"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="4"
            ><path d="M6 9l6 6 6-6" /></svg>
            {{ varDisplay ? varDisplay.varPct + '%' : (portfolioMetrics ? portfolioMetrics.var_95_percent.toFixed(1) + '%' : '1.2%') }}
          </div>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-white">
            {{ varDisplay ? varDisplay.varPct + '%' : (portfolioMetrics ? portfolioMetrics.var_95_percent.toFixed(2) + '%' : '2.45%') }}
          </div>
          <div class="kpi-sub">
            <template v-if="isLoadingReturns || isLoadingVaR">Загрузка...</template>
            <template v-else-if="varDisplay">{{ varDisplay.method + (varDisplay.isGarch ? ' + GARCH' : '') }}</template>
            <template v-else>Дневной риск</template>
          </div>
        </div>
      </div>

      <div class="glass-card kpi-card glow-blue">
        <div class="kpi-header">
          <span class="kpi-label">Sharpe Ratio</span>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-gradient-blue">
            {{ portfolioMetrics ? portfolioMetrics.sharpe_ratio.toFixed(2) : '1.85' }}
          </div>
          <div class="kpi-sub">
            Безрисковая ставка: {{ portfolioMetrics ? (portfolioMetrics.risk_free_rate * 100).toFixed(1) + '%' : '4.2%' }}
          </div>
        </div>
      </div>

      <div class="glass-card kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">Диверсификация</span>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-white">
            {{ portfolioMetrics ? portfolioMetrics.diversification.toFixed(2) : '0.34' }}
          </div>
          <div class="kpi-sub">
            Коэфф. корреляции: {{ portfolioMetrics ? portfolioMetrics.avg_correlation.toFixed(2) : '0.34' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Content Grid -->
    <div class="content-grid">
      <!-- Positions Table -->
      <div class="glass-panel">
        <div class="panel-header">
          <div>
            <h3>Открытые позиции</h3>
            <span class="panel-subtitle">Топ-5 по весу в портфеле</span>
          </div>
          <div class="panel-header-actions">
            <button
              class="btn-glass outline compact"
              @click="openPortfolioDetails"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line
                  x1="16"
                  y1="13"
                  x2="8"
                  y2="13"
                />
                <line
                  x1="16"
                  y1="17"
                  x2="8"
                  y2="17"
                />
                <polyline points="10 9 9 9 8 9" />
              </svg>
              Детализация
            </button>
          </div>
        </div>
        <div class="panel-body p-0">
          <div class="table-container">
            <table class="glass-table">
              <thead>
                <tr>
                  <th>Инструмент</th>
                  <th class="text-right">
                    Цена
                  </th>
                  <th class="text-right">
                    День %
                  </th>
                  <th class="text-right">
                    Позиция
                  </th>
                  <th class="text-right">
                    Вес
                  </th>
                  <th class="text-right">
                    Таргет
                  </th>
                  <th class="text-right">
                    Дрифт
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="pos in top5Positions"
                  :key="pos.symbol"
                  :class="{ active: selectedAsset?.symbol === pos.symbol }"
                  @click="selectAsset(pos)"
                >
                  <td>
                    <div class="asset-cell">
                      <div
                        class="asset-icon"
                        :style="{ background: pos.color }"
                      >
                        {{ pos.symbol[0] }}
                      </div>
                      <div class="asset-info">
                        <span class="symbol">{{ pos.symbol }}</span>
                        <span class="name">{{ pos.name }}</span>
                      </div>
                    </div>
                  </td>
                  <td class="text-right mono">
                    ${{ pos.price }}
                  </td>
                  <td class="text-right mono">
                    <span :class="['change-pill', pos.dayChange > 0 ? 'text-green' : 'text-red']">{{ pos.dayChange > 0 ? '+' : '' }}{{ pos.dayChange }}%</span>
                  </td>
                  <td class="text-right mono opacity-80">
                    ${{ (pos.notional / 1000).toFixed(1) }}k
                  </td>
                  <td class="text-right mono font-bold">
                    {{ pos.allocation }}%
                  </td>
                  <td class="text-right mono opacity-50">
                    {{ pos.targetAllocation }}%
                  </td>
                  <td class="text-right">
                    <div :class="['drift-val', getDriftClass(pos)]">
                      {{ (pos.allocation - pos.targetAllocation).toFixed(1) }}%
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Asset Details -->
      <transition name="fade">
        <div
          v-if="selectedAsset"
          class="glass-panel inspector-card"
        >
          <div class="panel-header">
            <div class="inspector-header-top">
              <div
                class="asset-lg-icon"
                :style="{ background: selectedAsset.color }"
              >
                {{ selectedAsset.symbol[0] }}
              </div>
              <div class="inspector-title">
                <h2>{{ selectedAsset.symbol }}</h2>
                <span>{{ selectedAsset.name }}</span>
              </div>
            </div>
            <div class="badge-glass">
              {{ (selectedAsset.symbol.includes('ОФЗ') || selectedAsset.symbol.includes('Облигац') || selectedAsset.symbol.includes('обл')) ? 'Облигация' : 'Акция' }}
            </div>
          </div>
          <div class="panel-body">
            <div class="mini-chart-container">
              <div class="chart-bars">
                <div
                  v-for="(h, i) in getMockHistogram(selectedAsset.symbol)"
                  :key="i"
                  class="chart-bar"
                  :style="{ height: h + '%', backgroundColor: i > 15 ? '#4ade80' : 'rgba(255,255,255,0.2)' }"
                />
              </div>
              <div class="chart-meta">
                <span class="active">1Д</span><span>1Н</span><span>1М</span><span>3М</span><span>1Г</span>
              </div>
            </div>

            <div class="inspector-grid">
              <div class="metric-cell">
                <label>Доходность</label>
                <span class="text-green">+14.2%</span>
              </div>
              <div class="metric-cell">
                <label>Волатильность</label>
                <span>18.5%</span>
              </div>
              <div class="metric-cell">
                <label>Beta</label>
                <span>1.12</span>
              </div>
              <div class="metric-cell">
                <label>Max DD</label>
                <span class="text-red">-12.4%</span>
              </div>
            </div>

            <div class="micro-metrics">
              <div class="micro-metric">
                <span class="label">Sharpe</span>
                <span class="value">0.92</span>
              </div>
              <div class="micro-metric">
                <span class="label">Sortino</span>
                <span class="value">1.38</span>
              </div>
              <div class="micro-metric">
                <span class="label">Skew</span>
                <span class="value">-0.24</span>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- Portfolio Details Modal -->
    <transition name="modal-fade">
      <div
        v-if="isPortfolioDetailsOpen"
        class="modal-overlay"
        @click="closePortfolioDetails"
      >
        <div
          class="modal-container"
          :class="{ 'modal-compact': portfolioDetailsFiltered.length <= 20 }"
          @click.stop
        >
          <div class="modal-header">
            <h2>Детализация портфеля ценных бумаг</h2>
            <button
              class="modal-close"
              @click="closePortfolioDetails"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line
                  x1="18"
                  y1="6"
                  x2="6"
                  y2="18"
                />
                <line
                  x1="6"
                  y1="6"
                  x2="18"
                  y2="18"
                />
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="modal-search">
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <circle
                  cx="11"
                  cy="11"
                  r="8"
                />
                <line
                  x1="21"
                  y1="21"
                  x2="16.65"
                  y2="16.65"
                />
              </svg>
              <input
                v-model="portfolioDetailsSearch"
                type="text"
                placeholder="Поиск по инструменту или названию..."
                class="modal-search-input"
              >
            </div>
            <div class="modal-table-container">
              <table class="glass-table modal-table">
                <thead>
                  <tr>
                    <th>Инструмент</th>
                    <th class="text-right">
                      Цена
                    </th>
                    <th class="text-right">
                      День %
                    </th>
                    <th class="text-right">
                      Позиция
                    </th>
                    <th class="text-right">
                      Вес
                    </th>
                    <th class="text-right">
                      Таргет
                    </th>
                    <th class="text-right">
                      Дрифт
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="pos in portfolioDetailsFiltered"
                    :key="pos.symbol"
                    :class="{ active: selectedAsset?.symbol === pos.symbol }"
                    @click="selectAsset(pos); closePortfolioDetails()"
                  >
                    <td>
                      <div class="asset-cell">
                        <div
                          class="asset-icon"
                          :style="{ background: pos.color }"
                        >
                          {{ pos.symbol[0] }}
                        </div>
                        <div class="asset-info">
                          <span class="symbol">{{ pos.symbol }}</span>
                          <span class="name">{{ pos.name }}</span>
                        </div>
                      </div>
                    </td>
                    <td class="text-right mono">
                      ${{ pos.price }}
                    </td>
                    <td class="text-right mono">
                      <span :class="['change-pill', pos.dayChange > 0 ? 'text-green' : 'text-red']">{{ pos.dayChange > 0 ? '+' : '' }}{{ pos.dayChange }}%</span>
                    </td>
                    <td class="text-right mono opacity-80">
                      ${{ (pos.notional / 1000).toFixed(1) }}k
                    </td>
                    <td class="text-right mono font-bold">
                      {{ pos.allocation }}%
                    </td>
                    <td class="text-right mono opacity-50">
                      {{ pos.targetAllocation }}%
                    </td>
                    <td class="text-right">
                      <div :class="['drift-val', getDriftClass(pos)]">
                        {{ (pos.allocation - pos.targetAllocation).toFixed(1) }}%
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="modal-footer">
              <div class="modal-stats">
                <span>Всего позиций: <strong>{{ positions.length }}</strong></span>
                <span>Отображается: <strong>{{ portfolioDetailsFiltered.length }}</strong></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Toast -->
    <transition name="slide-up">
      <div
        v-if="toast.show"
        class="toast-notification"
        :class="'toast-' + toast.type"
      >
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { usePortfolioStore, defaultBank } from '../stores/portfolio'
import { calculatePortfolioMetrics, type PortfolioMetricsResponse } from '../services/portfolioService'
import { calculateVaR as fetchVaR, type VaRMethod, type VaRResult } from '../services/riskService'
import { getStockHistory, type StockHistoryPoint } from '../services/marketDataService'

// Timer cleanup tracking
const activeTimerIds: Set<ReturnType<typeof setTimeout>> = new Set()
const activeIntervalIds: Set<ReturnType<typeof setInterval>> = new Set()

const trackTimeout = (fn: () => void, delay: number): ReturnType<typeof setTimeout> => {
  const id = setTimeout(() => {
    activeTimerIds.delete(id)
    fn()
  }, delay)
  activeTimerIds.add(id)
  return id
}

const trackInterval = (fn: () => void, delay: number): ReturnType<typeof setInterval> => {
  const id = setInterval(fn, delay)
  activeIntervalIds.add(id)
  return id
}

const clearAllTimers = () => {
  activeTimerIds.forEach(id => clearTimeout(id))
  activeTimerIds.clear()
  activeIntervalIds.forEach(id => clearInterval(id))
  activeIntervalIds.clear()
}

// ============================================================================
// EXISTING STATE
// ============================================================================
// PORTFOLIO STORE
// ============================================================================
const portfolioStore = usePortfolioStore()

// ============================================================================
// PORTFOLIOS DATA - 5 разных портфелей по 25 активов
// (Оставлено для совместимости, но используем store.positions)
// ============================================================================
const portfolioTemplates = {
  portfolio1: [
    // Российские акции
    { symbol: 'SBER', name: 'Сбербанк', price: '285.50', dayChange: 1.24, notional: 850000, allocation: 12, targetAllocation: 10, color: '#3b82f6' },
    { symbol: 'GAZP', name: 'Газпром', price: '187.30', dayChange: -0.48, notional: 720000, allocation: 10, targetAllocation: 12, color: '#10b981' },
    { symbol: 'LKOH', name: 'Лукойл', price: '7456.75', dayChange: 0.92, notional: 650000, allocation: 9, targetAllocation: 8, color: '#fbbf24' },
    { symbol: 'GMKN', name: 'Норникель', price: '18420.20', dayChange: -0.15, notional: 580000, allocation: 8, targetAllocation: 9, color: '#8b5cf6' },
    { symbol: 'YNDX', name: 'Яндекс', price: '3254.48', dayChange: 2.15, notional: 510000, allocation: 7, targetAllocation: 6, color: '#ec4899' },
    { symbol: 'ROSN', name: 'Роснефть', price: '456.80', dayChange: 1.05, notional: 480000, allocation: 6, targetAllocation: 7, color: '#ef4444' },
    { symbol: 'NVTK', name: 'Новатэк', price: '1234.50', dayChange: -0.32, notional: 450000, allocation: 6, targetAllocation: 5, color: '#06b6d4' },
    { symbol: 'TATN', name: 'Татнефть', price: '567.90', dayChange: 0.78, notional: 420000, allocation: 5, targetAllocation: 6, color: '#84cc16' },
    { symbol: 'ALRS', name: 'Алроса', price: '89.45', dayChange: -0.12, notional: 380000, allocation: 5, targetAllocation: 4, color: '#f97316' },
    { symbol: 'MGNT', name: 'Магнит', price: '6789.00', dayChange: 1.45, notional: 350000, allocation: 4, targetAllocation: 5, color: '#a855f7' },
    { symbol: 'MOEX', name: 'Московская биржа', price: '234.56', dayChange: 0.67, notional: 320000, allocation: 4, targetAllocation: 4, color: '#14b8a6' },
    { symbol: 'POLY', name: 'Полиметалл', price: '456.78', dayChange: -0.89, notional: 300000, allocation: 4, targetAllocation: 3, color: '#eab308' },
    { symbol: 'CHMF', name: 'Северсталь', price: '1234.56', dayChange: 1.23, notional: 280000, allocation: 3, targetAllocation: 4, color: '#22c55e' },
    { symbol: 'PLZL', name: 'Полюс', price: '9876.54', dayChange: -0.45, notional: 260000, allocation: 3, targetAllocation: 3, color: '#3b82f6' },
    { symbol: 'VTBR', name: 'ВТБ', price: '0.0234', dayChange: 0.12, notional: 240000, allocation: 3, targetAllocation: 2, color: '#10b981' },
    // Российские облигации
    { symbol: 'SU26238', name: 'ОФЗ 26238', price: '98.50', dayChange: 0.15, notional: 220000, allocation: 3, targetAllocation: 3, color: '#6366f1' },
    { symbol: 'SU26239', name: 'ОФЗ 26239', price: '99.20', dayChange: 0.08, notional: 200000, allocation: 2, targetAllocation: 3, color: '#8b5cf6' },
    { symbol: 'SU26240', name: 'ОФЗ 26240', price: '97.80', dayChange: -0.05, notional: 180000, allocation: 2, targetAllocation: 2, color: '#a78bfa' },
    { symbol: 'RU000A0ZZZN2', name: 'Газпром обл', price: '101.50', dayChange: 0.22, notional: 160000, allocation: 2, targetAllocation: 2, color: '#c084fc' },
    { symbol: 'RU000A0JX0J6', name: 'Роснефть обл', price: '100.30', dayChange: 0.18, notional: 140000, allocation: 2, targetAllocation: 2, color: '#d946ef' },
    { symbol: 'RU000A0JX0K4', name: 'Лукойл обл', price: '99.90', dayChange: 0.12, notional: 120000, allocation: 1, targetAllocation: 2, color: '#ec4899' },
    { symbol: 'RU000A0JX0L2', name: 'Сбер обл', price: '102.10', dayChange: 0.25, notional: 100000, allocation: 1, targetAllocation: 1, color: '#f472b6' },
    { symbol: 'RU000A0JX0M0', name: 'ВТБ обл', price: '98.70', dayChange: 0.10, notional: 90000, allocation: 1, targetAllocation: 1, color: '#fb7185' },
    { symbol: 'RU000A0JX0N8', name: 'Альфа обл', price: '100.50', dayChange: 0.20, notional: 80000, allocation: 1, targetAllocation: 1, color: '#fda4af' },
    { symbol: 'RU000A0JX0P3', name: 'Россельхоз обл', price: '99.40', dayChange: 0.15, notional: 70000, allocation: 1, targetAllocation: 1, color: '#fecdd3' }
  ],
  portfolio2: [
    { symbol: 'SBER', name: 'Сбербанк', price: '285.50', dayChange: 1.24, notional: 920000, allocation: 13, targetAllocation: 11, color: '#3b82f6' },
    { symbol: 'NLMK', name: 'НЛМК', price: '145.30', dayChange: -0.28, notional: 680000, allocation: 9, targetAllocation: 10, color: '#10b981' },
    { symbol: 'RTKM', name: 'Ростелеком', price: '89.45', dayChange: 0.65, notional: 560000, allocation: 8, targetAllocation: 8, color: '#fbbf24' },
    { symbol: 'AFKS', name: 'АФК Система', price: '12.34', dayChange: -0.45, notional: 480000, allocation: 7, targetAllocation: 7, color: '#8b5cf6' },
    { symbol: 'FIVE', name: 'X5 Retail', price: '2345.67', dayChange: 1.85, notional: 420000, allocation: 6, targetAllocation: 6, color: '#ec4899' },
    { symbol: 'PHOR', name: 'ФосАгро', price: '5678.90', dayChange: -0.12, notional: 380000, allocation: 5, targetAllocation: 6, color: '#ef4444' },
    { symbol: 'HYDR', name: 'РусГидро', price: '0.678', dayChange: 0.34, notional: 340000, allocation: 5, targetAllocation: 5, color: '#06b6d4' },
    { symbol: 'IRAO', name: 'Интер РАО', price: '3.456', dayChange: -0.23, notional: 300000, allocation: 4, targetAllocation: 4, color: '#84cc16' },
    { symbol: 'FEES', name: 'ФСК ЕЭС', price: '0.189', dayChange: 0.12, notional: 280000, allocation: 4, targetAllocation: 4, color: '#f97316' },
    { symbol: 'SNGS', name: 'Сургутнефтегаз', price: '45.67', dayChange: 0.89, notional: 260000, allocation: 4, targetAllocation: 3, color: '#a855f7' },
    { symbol: 'SNGSP', name: 'Сургутнефтегаз-п', price: '34.56', dayChange: 0.67, notional: 240000, allocation: 3, targetAllocation: 3, color: '#14b8a6' },
    { symbol: 'AFLT', name: 'Аэрофлот', price: '56.78', dayChange: -1.23, notional: 220000, allocation: 3, targetAllocation: 3, color: '#eab308' },
    { symbol: 'PIKK', name: 'ПИК', price: '890.12', dayChange: 0.45, notional: 200000, allocation: 3, targetAllocation: 2, color: '#22c55e' },
    { symbol: 'LSRG', name: 'ЛСР', price: '456.78', dayChange: -0.34, notional: 180000, allocation: 2, targetAllocation: 2, color: '#3b82f6' },
    { symbol: 'UPRO', name: 'Юнипро', price: '12.34', dayChange: 0.56, notional: 160000, allocation: 2, targetAllocation: 2, color: '#10b981' },
    { symbol: 'SU26241', name: 'ОФЗ 26241', price: '98.90', dayChange: 0.18, notional: 140000, allocation: 2, targetAllocation: 2, color: '#6366f1' },
    { symbol: 'SU26242', name: 'ОФЗ 26242', price: '99.60', dayChange: 0.12, notional: 120000, allocation: 2, targetAllocation: 2, color: '#8b5cf6' },
    { symbol: 'SU26243', name: 'ОФЗ 26243', price: '97.50', dayChange: -0.08, notional: 100000, allocation: 1, targetAllocation: 2, color: '#a78bfa' },
    { symbol: 'RU000A0ZZZN3', name: 'Газпром обл', price: '101.80', dayChange: 0.28, notional: 90000, allocation: 1, targetAllocation: 1, color: '#c084fc' },
    { symbol: 'RU000A0JX0J7', name: 'Роснефть обл', price: '100.60', dayChange: 0.22, notional: 80000, allocation: 1, targetAllocation: 1, color: '#d946ef' },
    { symbol: 'RU000A0JX0K5', name: 'Лукойл обл', price: '100.20', dayChange: 0.15, notional: 70000, allocation: 1, targetAllocation: 1, color: '#ec4899' },
    { symbol: 'RU000A0JX0L3', name: 'Сбер обл', price: '102.40', dayChange: 0.30, notional: 60000, allocation: 1, targetAllocation: 1, color: '#f472b6' },
    { symbol: 'RU000A0JX0M1', name: 'ВТБ обл', price: '99.00', dayChange: 0.12, notional: 50000, allocation: 1, targetAllocation: 1, color: '#fb7185' },
    { symbol: 'RU000A0JX0N9', name: 'Альфа обл', price: '100.80', dayChange: 0.25, notional: 45000, allocation: 1, targetAllocation: 1, color: '#fda4af' },
    { symbol: 'RU000A0JX0P4', name: 'Россельхоз обл', price: '99.70', dayChange: 0.18, notional: 40000, allocation: 1, targetAllocation: 1, color: '#fecdd3' }
  ],
  portfolio3: [
    { symbol: 'GAZP', name: 'Газпром', price: '187.30', dayChange: -0.48, notional: 980000, allocation: 14, targetAllocation: 12, color: '#10b981' },
    { symbol: 'LKOH', name: 'Лукойл', price: '7456.75', dayChange: 0.92, notional: 780000, allocation: 11, targetAllocation: 11, color: '#fbbf24' },
    { symbol: 'GMKN', name: 'Норникель', price: '18420.20', dayChange: -0.15, notional: 640000, allocation: 9, targetAllocation: 9, color: '#8b5cf6' },
    { symbol: 'YNDX', name: 'Яндекс', price: '3254.48', dayChange: 2.15, notional: 520000, allocation: 7, targetAllocation: 7, color: '#ec4899' },
    { symbol: 'ROSN', name: 'Роснефть', price: '456.80', dayChange: 1.05, notional: 460000, allocation: 6, targetAllocation: 6, color: '#ef4444' },
    { symbol: 'NVTK', name: 'Новатэк', price: '1234.50', dayChange: -0.32, notional: 400000, allocation: 6, targetAllocation: 5, color: '#06b6d4' },
    { symbol: 'TATN', name: 'Татнефть', price: '567.90', dayChange: 0.78, notional: 360000, allocation: 5, targetAllocation: 5, color: '#84cc16' },
    { symbol: 'ALRS', name: 'Алроса', price: '89.45', dayChange: -0.12, notional: 320000, allocation: 4, targetAllocation: 4, color: '#f97316' },
    { symbol: 'MGNT', name: 'Магнит', price: '6789.00', dayChange: 1.45, notional: 300000, allocation: 4, targetAllocation: 4, color: '#a855f7' },
    { symbol: 'MOEX', name: 'Московская биржа', price: '234.56', dayChange: 0.67, notional: 280000, allocation: 4, targetAllocation: 3, color: '#14b8a6' },
    { symbol: 'POLY', name: 'Полиметалл', price: '456.78', dayChange: -0.89, notional: 260000, allocation: 4, targetAllocation: 3, color: '#eab308' },
    { symbol: 'CHMF', name: 'Северсталь', price: '1234.56', dayChange: 1.23, notional: 240000, allocation: 3, targetAllocation: 3, color: '#22c55e' },
    { symbol: 'PLZL', name: 'Полюс', price: '9876.54', dayChange: -0.45, notional: 220000, allocation: 3, targetAllocation: 3, color: '#3b82f6' },
    { symbol: 'VTBR', name: 'ВТБ', price: '0.0234', dayChange: 0.12, notional: 200000, allocation: 3, targetAllocation: 2, color: '#10b981' },
    { symbol: 'NLMK', name: 'НЛМК', price: '145.30', dayChange: -0.28, notional: 180000, allocation: 2, targetAllocation: 2, color: '#6366f1' },
    { symbol: 'SU26244', name: 'ОФЗ 26244', price: '98.30', dayChange: 0.20, notional: 160000, allocation: 2, targetAllocation: 2, color: '#8b5cf6' },
    { symbol: 'SU26245', name: 'ОФЗ 26245', price: '99.10', dayChange: 0.14, notional: 140000, allocation: 2, targetAllocation: 2, color: '#a78bfa' },
    { symbol: 'SU26246', name: 'ОФЗ 26246', price: '97.20', dayChange: -0.10, notional: 120000, allocation: 2, targetAllocation: 2, color: '#c084fc' },
    { symbol: 'RU000A0ZZZN4', name: 'Газпром обл', price: '102.10', dayChange: 0.32, notional: 100000, allocation: 1, targetAllocation: 2, color: '#d946ef' },
    { symbol: 'RU000A0JX0J8', name: 'Роснефть обл', price: '100.90', dayChange: 0.26, notional: 90000, allocation: 1, targetAllocation: 1, color: '#ec4899' },
    { symbol: 'RU000A0JX0K6', name: 'Лукойл обл', price: '100.50', dayChange: 0.18, notional: 80000, allocation: 1, targetAllocation: 1, color: '#f472b6' },
    { symbol: 'RU000A0JX0L4', name: 'Сбер обл', price: '102.70', dayChange: 0.35, notional: 70000, allocation: 1, targetAllocation: 1, color: '#fb7185' },
    { symbol: 'RU000A0JX0M2', name: 'ВТБ обл', price: '99.30', dayChange: 0.14, notional: 60000, allocation: 1, targetAllocation: 1, color: '#fda4af' },
    { symbol: 'RU000A0JX0N0', name: 'Альфа обл', price: '101.10', dayChange: 0.28, notional: 50000, allocation: 1, targetAllocation: 1, color: '#fecdd3' },
    { symbol: 'RU000A0JX0P5', name: 'Россельхоз обл', price: '100.00', dayChange: 0.20, notional: 45000, allocation: 1, targetAllocation: 1, color: '#fbbf24' }
  ],
  portfolio4: [
    { symbol: 'SBER', name: 'Сбербанк', price: '285.50', dayChange: 1.24, notional: 1100000, allocation: 15, targetAllocation: 13, color: '#3b82f6' },
    { symbol: 'RTKM', name: 'Ростелеком', price: '89.45', dayChange: 0.65, notional: 720000, allocation: 10, targetAllocation: 10, color: '#fbbf24' },
    { symbol: 'AFKS', name: 'АФК Система', price: '12.34', dayChange: -0.45, notional: 580000, allocation: 8, targetAllocation: 8, color: '#8b5cf6' },
    { symbol: 'FIVE', name: 'X5 Retail', price: '2345.67', dayChange: 1.85, notional: 500000, allocation: 7, targetAllocation: 7, color: '#ec4899' },
    { symbol: 'PHOR', name: 'ФосАгро', price: '5678.90', dayChange: -0.12, notional: 440000, allocation: 6, targetAllocation: 6, color: '#ef4444' },
    { symbol: 'HYDR', name: 'РусГидро', price: '0.678', dayChange: 0.34, notional: 400000, allocation: 6, targetAllocation: 5, color: '#06b6d4' },
    { symbol: 'IRAO', name: 'Интер РАО', price: '3.456', dayChange: -0.23, notional: 360000, allocation: 5, targetAllocation: 5, color: '#84cc16' },
    { symbol: 'FEES', name: 'ФСК ЕЭС', price: '0.189', dayChange: 0.12, notional: 320000, allocation: 4, targetAllocation: 4, color: '#f97316' },
    { symbol: 'SNGS', name: 'Сургутнефтегаз', price: '45.67', dayChange: 0.89, notional: 300000, allocation: 4, targetAllocation: 4, color: '#a855f7' },
    { symbol: 'SNGSP', name: 'Сургутнефтегаз-п', price: '34.56', dayChange: 0.67, notional: 280000, allocation: 4, targetAllocation: 3, color: '#14b8a6' },
    { symbol: 'AFLT', name: 'Аэрофлот', price: '56.78', dayChange: -1.23, notional: 260000, allocation: 4, targetAllocation: 3, color: '#eab308' },
    { symbol: 'PIKK', name: 'ПИК', price: '890.12', dayChange: 0.45, notional: 240000, allocation: 3, targetAllocation: 3, color: '#22c55e' },
    { symbol: 'LSRG', name: 'ЛСР', price: '456.78', dayChange: -0.34, notional: 220000, allocation: 3, targetAllocation: 2, color: '#3b82f6' },
    { symbol: 'UPRO', name: 'Юнипро', price: '12.34', dayChange: 0.56, notional: 200000, allocation: 3, targetAllocation: 2, color: '#10b981' },
    { symbol: 'MAGN', name: 'ММК', price: '45.67', dayChange: 0.23, notional: 180000, allocation: 2, targetAllocation: 2, color: '#6366f1' },
    { symbol: 'SU26247', name: 'ОФЗ 26247', price: '98.70', dayChange: 0.22, notional: 160000, allocation: 2, targetAllocation: 2, color: '#8b5cf6' },
    { symbol: 'SU26248', name: 'ОФЗ 26248', price: '99.50', dayChange: 0.16, notional: 140000, allocation: 2, targetAllocation: 2, color: '#a78bfa' },
    { symbol: 'SU26249', name: 'ОФЗ 26249', price: '97.00', dayChange: -0.12, notional: 120000, allocation: 2, targetAllocation: 2, color: '#c084fc' },
    { symbol: 'RU000A0ZZZN5', name: 'Газпром обл', price: '102.40', dayChange: 0.36, notional: 100000, allocation: 1, targetAllocation: 2, color: '#d946ef' },
    { symbol: 'RU000A0JX0J9', name: 'Роснефть обл', price: '101.20', dayChange: 0.30, notional: 90000, allocation: 1, targetAllocation: 1, color: '#ec4899' },
    { symbol: 'RU000A0JX0K7', name: 'Лукойл обл', price: '100.80', dayChange: 0.22, notional: 80000, allocation: 1, targetAllocation: 1, color: '#f472b6' },
    { symbol: 'RU000A0JX0L5', name: 'Сбер обл', price: '103.00', dayChange: 0.40, notional: 70000, allocation: 1, targetAllocation: 1, color: '#fb7185' },
    { symbol: 'RU000A0JX0M3', name: 'ВТБ обл', price: '99.60', dayChange: 0.16, notional: 60000, allocation: 1, targetAllocation: 1, color: '#fda4af' },
    { symbol: 'RU000A0JX0N1', name: 'Альфа обл', price: '101.40', dayChange: 0.30, notional: 50000, allocation: 1, targetAllocation: 1, color: '#fecdd3' },
    { symbol: 'RU000A0JX0P6', name: 'Россельхоз обл', price: '100.30', dayChange: 0.22, notional: 45000, allocation: 1, targetAllocation: 1, color: '#fbbf24' }
  ],
  portfolio5: [
    { symbol: 'LKOH', name: 'Лукойл', price: '7456.75', dayChange: 0.92, notional: 1200000, allocation: 16, targetAllocation: 14, color: '#fbbf24' },
    { symbol: 'GMKN', name: 'Норникель', price: '18420.20', dayChange: -0.15, notional: 840000, allocation: 12, targetAllocation: 12, color: '#8b5cf6' },
    { symbol: 'YNDX', name: 'Яндекс', price: '3254.48', dayChange: 2.15, notional: 640000, allocation: 9, targetAllocation: 9, color: '#ec4899' },
    { symbol: 'ROSN', name: 'Роснефть', price: '456.80', dayChange: 1.05, notional: 560000, allocation: 8, targetAllocation: 8, color: '#ef4444' },
    { symbol: 'NVTK', name: 'Новатэк', price: '1234.50', dayChange: -0.32, notional: 480000, allocation: 7, targetAllocation: 6, color: '#06b6d4' },
    { symbol: 'TATN', name: 'Татнефть', price: '567.90', dayChange: 0.78, notional: 420000, allocation: 6, targetAllocation: 6, color: '#84cc16' },
    { symbol: 'ALRS', name: 'Алроса', price: '89.45', dayChange: -0.12, notional: 380000, allocation: 5, targetAllocation: 5, color: '#f97316' },
    { symbol: 'MGNT', name: 'Магнит', price: '6789.00', dayChange: 1.45, notional: 340000, allocation: 5, targetAllocation: 4, color: '#a855f7' },
    { symbol: 'MOEX', name: 'Московская биржа', price: '234.56', dayChange: 0.67, notional: 300000, allocation: 4, targetAllocation: 4, color: '#14b8a6' },
    { symbol: 'POLY', name: 'Полиметалл', price: '456.78', dayChange: -0.89, notional: 280000, allocation: 4, targetAllocation: 4, color: '#eab308' },
    { symbol: 'CHMF', name: 'Северсталь', price: '1234.56', dayChange: 1.23, notional: 260000, allocation: 4, targetAllocation: 3, color: '#22c55e' },
    { symbol: 'PLZL', name: 'Полюс', price: '9876.54', dayChange: -0.45, notional: 240000, allocation: 3, targetAllocation: 3, color: '#3b82f6' },
    { symbol: 'VTBR', name: 'ВТБ', price: '0.0234', dayChange: 0.12, notional: 220000, allocation: 3, targetAllocation: 3, color: '#10b981' },
    { symbol: 'NLMK', name: 'НЛМК', price: '145.30', dayChange: -0.28, notional: 200000, allocation: 3, targetAllocation: 2, color: '#6366f1' },
    { symbol: 'RTKM', name: 'Ростелеком', price: '89.45', dayChange: 0.65, notional: 180000, allocation: 2, targetAllocation: 2, color: '#fbbf24' },
    { symbol: 'SU26250', name: 'ОФЗ 26250', price: '98.10', dayChange: 0.24, notional: 160000, allocation: 2, targetAllocation: 2, color: '#8b5cf6' },
    { symbol: 'SU26251', name: 'ОФЗ 26251', price: '99.00', dayChange: 0.18, notional: 140000, allocation: 2, targetAllocation: 2, color: '#a78bfa' },
    { symbol: 'SU26252', name: 'ОФЗ 26252', price: '96.80', dayChange: -0.14, notional: 120000, allocation: 2, targetAllocation: 2, color: '#c084fc' },
    { symbol: 'RU000A0ZZZN6', name: 'Газпром обл', price: '102.70', dayChange: 0.40, notional: 100000, allocation: 1, targetAllocation: 2, color: '#d946ef' },
    { symbol: 'RU000A0JX0J0', name: 'Роснефть обл', price: '101.50', dayChange: 0.34, notional: 90000, allocation: 1, targetAllocation: 1, color: '#ec4899' },
    { symbol: 'RU000A0JX0K8', name: 'Лукойл обл', price: '101.10', dayChange: 0.25, notional: 80000, allocation: 1, targetAllocation: 1, color: '#f472b6' },
    { symbol: 'RU000A0JX0L6', name: 'Сбер обл', price: '103.30', dayChange: 0.45, notional: 70000, allocation: 1, targetAllocation: 1, color: '#fb7185' },
    { symbol: 'RU000A0JX0M4', name: 'ВТБ обл', price: '99.90', dayChange: 0.18, notional: 60000, allocation: 1, targetAllocation: 1, color: '#fda4af' },
    { symbol: 'RU000A0JX0N2', name: 'Альфа обл', price: '101.70', dayChange: 0.35, notional: 50000, allocation: 1, targetAllocation: 1, color: '#fecdd3' },
    { symbol: 'RU000A0JX0P7', name: 'Россельхоз обл', price: '100.60', dayChange: 0.25, notional: 45000, allocation: 1, targetAllocation: 1, color: '#fbbf24' }
  ]
}

// Функция для получения портфеля по банку (распределение по остатку от деления regNumber на 5)
const getPortfolioByBank = (bankRegNumber: string): string => {
  const num = parseInt(bankRegNumber) % 5
  const portfolios = ['portfolio1', 'portfolio2', 'portfolio3', 'portfolio4', 'portfolio5']
  return portfolios[num]
}

const lastUpdate = ref(new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}))
const isRecalcing = ref(false)
const searchFilter = ref('')
const toast = ref({ show: false, message: '', type: 'success' })

// ============================================================================
// PORTFOLIO METRICS - из API
// ============================================================================
const portfolioMetrics = ref<PortfolioMetricsResponse | null>(null)
const isLoadingMetrics = ref(false)

// ============================================================================
// VAR ENGINE - historical returns, method selection, GARCH toggle
// ============================================================================
const varMethod = ref<VaRMethod>('parametric')
const useGarch = ref(false)
const varResult = ref<VaRResult | null>(null)
const isLoadingVaR = ref(false)
const isLoadingReturns = ref(false)

// Cache: portfolio-weighted daily returns computed from historical prices
const cachedReturns = ref<number[]>([])
const cachedReturnsTickers = ref<string>('')

const varMethodLabels: Record<VaRMethod, string> = {
  parametric: 'Parametric',
  historical: 'Historical',
  monte_carlo: 'Monte Carlo',
}

/**
 * Fetch 1Y daily history for each ticker, compute portfolio-weighted log returns.
 * Results are cached until portfolio tickers change.
 */
const loadHistoricalReturns = async (): Promise<number[]> => {
  if (!positions.value || positions.value.length === 0) return []

  const tickerKey = positions.value.map((p: any) => p.symbol).sort().join(',')
  if (tickerKey === cachedReturnsTickers.value && cachedReturns.value.length > 0) {
    return cachedReturns.value
  }

  isLoadingReturns.value = true
  try {
    const historyPromises = positions.value.map((pos: any) =>
      getStockHistory(pos.symbol, '1y', '1d').catch(() => [] as StockHistoryPoint[])
    )
    const histories = await Promise.all(historyPromises)

    const lengths = histories.map(h => h.length).filter(l => l > 1)
    if (lengths.length === 0) return []
    const minLen = Math.min(...lengths)

    const totalAlloc = positions.value.reduce((s: number, p: any) => s + (p.allocation || 0), 0)
    if (totalAlloc === 0) return []
    const weights = positions.value.map((p: any) => (p.allocation || 0) / totalAlloc)

    const portfolioReturns: number[] = []
    for (let t = 1; t < minLen; t++) {
      let dayReturn = 0
      for (let i = 0; i < positions.value.length; i++) {
        const h = histories[i]
        if (!h || h.length < minLen) continue
        const prevClose = h[t - 1].close
        const curClose = h[t].close
        if (prevClose > 0 && curClose > 0) {
          dayReturn += weights[i] * Math.log(curClose / prevClose)
        }
      }
      portfolioReturns.push(dayReturn)
    }

    cachedReturns.value = portfolioReturns
    cachedReturnsTickers.value = tickerKey
    return portfolioReturns
  } catch {
    return []
  } finally {
    isLoadingReturns.value = false
  }
}

const loadVaRFromEngine = async () => {
  if (!positions.value || positions.value.length === 0) return

  const returns = await loadHistoricalReturns()
  if (returns.length < 10) return

  const nav = portfolioMetrics.value?.nav ?? positions.value.reduce((s: number, p: any) => s + (p.notional || 0), 0)
  if (nav <= 0) return

  isLoadingVaR.value = true
  try {
    const result = await fetchVaR({
      returns,
      method: varMethod.value,
      confidence: 0.95,
      horizon: 1,
      portfolio_value: nav,
      use_garch: useGarch.value,
      garch_model: 'garch_11',
    })
    varResult.value = result
  } catch {
    varResult.value = null
  } finally {
    isLoadingVaR.value = false
  }
}

const varDisplay = computed(() => {
  if (!varResult.value || !portfolioMetrics.value) return null
  const nav = portfolioMetrics.value.nav
  if (nav <= 0) return null
  return {
    varPct: ((varResult.value.var / nav) * 100).toFixed(2),
    cvarPct: ((varResult.value.cvar / nav) * 100).toFixed(2),
    method: varMethodLabels[varResult.value.method],
    isGarch: varResult.value.use_garch,
  }
})

// ============================================================================
// BANK SELECTOR - используем store
// ============================================================================
const { selectedBank, positions, banks } = storeToRefs(portfolioStore)

const isBankMenuOpen = ref(false)
const bankSearchQuery = ref('')

const selectedAsset = ref<any>(null)

// Функция для загрузки метрик портфеля из API
const loadPortfolioMetrics = async () => {
  if (!positions.value || positions.value.length === 0) {
    portfolioMetrics.value = null
    return
  }

  isLoadingMetrics.value = true
  try {
    const positionsForAPI = positions.value.map((pos: any) => ({
      symbol: pos.symbol,
      name: pos.name,
      price: parseFloat(pos.price) || 0,
      dayChange: pos.dayChange || 0,
      notional: pos.notional || 0,
      allocation: pos.allocation || 0,
      targetAllocation: pos.targetAllocation || 0,
      color: pos.color || ''
    }))

    const metrics = await calculatePortfolioMetrics({
      positions: positionsForAPI,
      risk_free_rate: 0.042,
      market_return: 0.10,
      market_volatility: 0.15
    })

    portfolioMetrics.value = metrics
  } catch (error) {
    portfolioMetrics.value = null
  } finally {
    isLoadingMetrics.value = false
  }
}

// Обновляем selectedAsset при изменении портфеля
watch(positions, (newPositions) => {
  if (newPositions.length > 0 && (!selectedAsset.value || !newPositions.find(p => p.symbol === selectedAsset.value?.symbol))) {
    selectedAsset.value = newPositions[0]
  }
  loadPortfolioMetrics()
}, { immediate: true, deep: true })

const filteredBanks = computed(() => {
  if (!bankSearchQuery.value.trim()) {
    return banks.value
  }
  const query = bankSearchQuery.value.toLowerCase().trim()
  return banks.value.filter((bank: { name: string; regNumber: string }) =>
    bank.name.toLowerCase().includes(query) ||
    bank.regNumber.includes(query)
  )
})

const toggleBankMenu = () => {
  isBankMenuOpen.value = !isBankMenuOpen.value
  if (isBankMenuOpen.value) {
    bankSearchQuery.value = ''
  }
}

const selectBank = (bank: { name: string; regNumber: string }) => {
  portfolioStore.setSelectedBank(bank)
  isBankMenuOpen.value = false
  bankSearchQuery.value = ''
  showToast(`Выбран банк: ${bank.name} (№ ${bank.regNumber})`, 'info')
}

// Закрытие меню при клике вне его
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.bank-selector-wrapper')) {
    isBankMenuOpen.value = false
  }
}

// Топ-5 позиций по весу для основного блока
const top5Positions = computed(() => {
  return [...positions.value]
    .sort((a, b) => b.allocation - a.allocation)
    .slice(0, 5)
})

// Полный список для модального окна
const filteredPositions = computed(() => {
  if (!searchFilter.value) return positions.value
  const query = searchFilter.value.toLowerCase()
  return positions.value.filter((p: any) =>
    p.symbol.toLowerCase().includes(query) || p.name.toLowerCase().includes(query)
  )
})

// Состояние модального окна детализации
const isPortfolioDetailsOpen = ref(false)
const portfolioDetailsSearch = ref('')

const portfolioDetailsFiltered = computed(() => {
  if (!portfolioDetailsSearch.value) return positions.value
  const query = portfolioDetailsSearch.value.toLowerCase()
  return positions.value.filter((p: any) =>
    p.symbol.toLowerCase().includes(query) || p.name.toLowerCase().includes(query)
  )
})

const openPortfolioDetails = () => {
  isPortfolioDetailsOpen.value = true
  portfolioDetailsSearch.value = ''
  if (typeof document !== 'undefined') {
    document.body.style.overflow = 'hidden'
  }
}

const closePortfolioDetails = () => {
  isPortfolioDetailsOpen.value = false
  if (typeof document !== 'undefined') {
    document.body.style.overflow = ''
  }
}

onMounted(async () => {
  if (!selectedBank.value) {
    portfolioStore.setSelectedBank(defaultBank)
  }

  if (positions?.value?.length > 0 && !selectedAsset.value) {
    selectedAsset.value = positions.value[0]
  }

  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  clearAllTimers()
})

const selectAsset = (pos: any) => selectedAsset.value = pos

const exportPdf = () => {
  showToast('PDF экспорт инициирован...', 'info')
  trackTimeout(() => {
    showToast('Файл portfolio_2026-01-06.pdf загружен', 'success')
  }, 1200)
}

const filterPositions = (e: any) => {
  searchFilter.value = e.target.value
}

const showToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
  toast.value = { show: true, message, type }
  trackTimeout(() => {
    toast.value.show = false
  }, 3000)
}

const getDriftClass = (pos: any) => {
   const drift = Math.abs(pos.allocation - pos.targetAllocation)
   if (drift < 0.5) return 'text-muted'
   return (pos.allocation - pos.targetAllocation) > 0 ? 'text-green' : 'text-red'
}

const getMockHistogram = (symbol: string) => {
   return Array.from({length: 20}, () => Math.random() * 80 + 20)
}
</script>

<style scoped>
.portfolio-page { padding: 24px 32px; max-width: 100%; margin: 0 auto; display: flex; flex-direction: column; gap: 28px; min-height: 100vh; margin-top: 20px; }

/* Content Grid - Two Column Layout */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 16px;
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

/* Hero & KPI */
.hero-section { display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 8px; }
.hero-title-row { margin-bottom: 16px; }
.hero-left h1 { font-size: 28px; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.01em; display: flex; align-items: center; flex-wrap: nowrap; gap: 12px; white-space: nowrap; }
.hero-meta { display: flex; gap: 10px; }

/* Bank Selector */
.bank-selector-inline-wrapper { display: inline-flex; align-items: center; vertical-align: middle; }
.bank-selector-wrapper { position: relative; z-index: 10; display: inline-block; }
.bank-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  user-select: none;
  min-width: 280px;
}
.bank-selector:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}
.bank-selector.is-open {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}
.bank-selector-content {
  flex: 1;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-width: 0;
}
.bank-selector-name {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
  min-width: 0;
}
.bank-selector-reg {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  font-family: "SF Mono", monospace;
  line-height: 1.2;
  white-space: nowrap;
}
.bank-selector-chevron {
  flex-shrink: 0;
  color: var(--text-tertiary);
  transition: transform 0.2s;
}
.bank-selector.is-open .bank-selector-chevron {
  transform: rotate(180deg);
}

.bank-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: var(--bg-secondary);
  border: 1px solid var(--border-medium);
  border-radius: 6px;
  overflow: hidden;
  z-index: 1000;
  min-width: 400px;
}

.bank-dropdown-search {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-dark);
}
.bank-dropdown-search svg {
  flex-shrink: 0;
  color: var(--text-tertiary);
  width: 14px;
  height: 14px;
}
.bank-search-input {
  flex: 1;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-dark);
  border-radius: 4px;
  padding: 8px 12px;
  color: var(--text-primary);
  font-size: 12px;
  font-family: inherit;
  outline: none;
  transition: all 0.2s;
}
.bank-search-input:focus {
  border-color: var(--border-medium);
}
.bank-search-input::placeholder {
  color: var(--text-muted);
}

.bank-dropdown-list {
  max-height: 400px;
  overflow-y: auto;
}
.bank-dropdown-list::-webkit-scrollbar {
  width: 6px;
}
.bank-dropdown-list::-webkit-scrollbar-track {
  background: var(--bg-primary);
  border-radius: 3px;
}
.bank-dropdown-list::-webkit-scrollbar-thumb {
  background: var(--border-medium);
  border-radius: 3px;
}
.bank-dropdown-list::-webkit-scrollbar-thumb:hover {
  background: var(--border-light);
}

.bank-dropdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.15s;
  border-bottom: 1px solid var(--border-dark);
}
.bank-dropdown-item:last-child {
  border-bottom: none;
}
.bank-dropdown-item:hover {
  background: rgba(255, 255, 255, 0.08);
}
.bank-dropdown-item.is-selected {
  background: rgba(59, 130, 246, 0.15);
}
.bank-dropdown-item.is-selected svg {
  color: #60a5fa;
  flex-shrink: 0;
}

.bank-item-content {
  flex: 1;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-width: 0;
}
.bank-item-name {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.3;
  word-break: break-word;
  min-width: 0;
}
.bank-dropdown-item.is-selected .bank-item-name {
  color: #60a5fa;
  font-weight: 600;
}
.bank-item-reg {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  font-family: "SF Mono", monospace;
  line-height: 1.2;
  white-space: nowrap;
}
.bank-dropdown-item.is-selected .bank-item-reg {
  color: rgba(96, 165, 250, 0.8);
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
.glass-pill { font-size: 12px; padding: 6px 12px; background: rgba(255,255,255,0.06); border: 1px solid var(--border-dark); border-radius: 4px; color: var(--text-secondary); display: flex; align-items: center; gap: 6px; }
.glass-pill strong { color: var(--text-primary); font-weight: 600; }
.risk-aggressive { background: rgba(251, 191, 36, 0.1); border-color: rgba(251, 191, 36, 0.2); color: #fbbf24; }
.status-dot { width: 6px; height: 6px; background: currentColor; border-radius: 3px; }
.hero-actions { display: flex; align-items: center; gap: 16px; }
.last-update { font-size: 12px; color: var(--text-muted); margin-right: 8px; }

/* Buttons */
.btn-glass { height: 36px; padding: 0 16px; border-radius: 4px; font-weight: 600; font-size: 13px; display: flex; align-items: center; justify-content: center; gap: 8px; cursor: pointer; transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1); border: 1px solid transparent; }
.btn-glass.primary { background: rgba(255, 255, 255, 0.9); color: var(--bg-primary); }
.btn-glass.primary:hover:not(:disabled) { transform: translateY(-1px); }
.btn-glass.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-glass.outline { background: var(--bg-tertiary); color: var(--text-primary); border-color: var(--border-dark); }
.btn-glass.outline:hover { background: rgba(255, 255, 255, 0.1); border-color: var(--border-medium); }
.btn-glass.compact { height: 32px; font-size: 11px; padding: 0 12px; }

/* KPI Grid */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.glass-card {
  position: relative;
  overflow: hidden;
  background: var(--bg-secondary);
  border: 1px solid var(--border-dark);
  border-radius: 6px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-card:hover {
  border-color: var(--border-medium);
  transform: translateY(-2px);
}
.glass-card.glow-green::before { content: ""; position: absolute; top: -50px; right: -50px; width: 100px; height: 100px; background: #4ade80; filter: blur(60px); opacity: 0.15; pointer-events: none; }
.glass-card.glow-blue::before { content: ""; position: absolute; top: -50px; right: -50px; width: 100px; height: 100px; background: #3b82f6; filter: blur(60px); opacity: 0.15; pointer-events: none; }
.kpi-header { display: flex; justify-content: space-between; align-items: flex-start; }
.kpi-label { font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 700; letter-spacing: 0.05em; }
.trend-badge { font-size: 11px; font-weight: 700; padding: 4px 8px; border-radius: 4px; display: flex; align-items: center; gap: 4px; }
.trend-badge.positive { color: #4ade80; background: rgba(74, 222, 128, 0.1); border: 1px solid rgba(74, 222, 128, 0.1); }
.trend-badge.negative { color: #f87171; background: rgba(248, 113, 113, 0.1); border: 1px solid rgba(248, 113, 113, 0.1); }
.kpi-value { font-size: 26px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.1; }
.kpi-value small { font-size: 14px; color: var(--text-muted); font-weight: 500; margin-left: 4px; }
.kpi-sub { font-size: 11px; color: var(--text-muted); }

/* Glass Panel */
.glass-panel {
  background: var(--bg-secondary);
  border: 1px solid var(--border-dark);
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.panel-header { padding: 16px 20px; border-bottom: 1px solid var(--border-dark); display: flex; justify-content: space-between; align-items: center; background: var(--bg-tertiary); flex-shrink: 0; }
.panel-header h3 { font-size: 13px; font-weight: 600; color: var(--text-primary); margin: 0; text-transform: uppercase; letter-spacing: 0.05em; }
.panel-subtitle { font-size: 10px; color: var(--text-muted); margin-top: 2px; display: block; }
.panel-header-actions { display: flex; gap: 8px; align-items: center; }
.panel-body { padding: 16px 20px; overflow: hidden; }
.panel-body.p-0 { padding: 0; }

/* Table */
.table-container { overflow-x: auto; }
.glass-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.glass-table th { text-align: left; padding: 12px 20px; color: var(--text-muted); font-weight: 600; font-size: 10px; text-transform: uppercase; border-bottom: 1px solid var(--border-dark); }
.glass-table tr { transition: background 0.15s; cursor: pointer; border-bottom: 1px solid var(--border-dark); }
.glass-table tr:last-child { border-bottom: none; }
.glass-table tr:hover { background: rgba(255,255,255,0.04); }
.glass-table tr.active { background: rgba(59, 130, 246, 0.15); box-shadow: inset 3px 0 0 #3b82f6; }
.glass-table td { padding: 12px 20px; color: var(--text-primary); }
.asset-cell { display: flex; align-items: center; gap: 12px; }
.asset-icon { width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px; color: var(--text-primary); }
.asset-info { display: flex; flex-direction: column; }
.asset-info .symbol { font-weight: 600; font-size: 13px; color: var(--text-primary); }
.asset-info .name { font-size: 10px; color: var(--text-muted); }
.change-pill { font-size: 11px; padding: 2px 6px; border-radius: 3px; font-weight: 600; }
.text-muted { color: var(--text-muted); }
.text-green { color: #22c55e !important; }
.text-red { color: var(--accent-red) !important; }
.drift-val { font-size: 11px; font-weight: 600; font-family: "SF Mono", monospace; }

/* Inspector & Asset Details */
.inspector-card { flex-shrink: 0; }
.inspector-header-top { display: flex; align-items: center; gap: 10px; flex: 1; }
.asset-lg-icon { width: 36px; height: 36px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; color: var(--text-primary); flex-shrink: 0; }
.inspector-title h2 { margin: 0; font-size: 16px; color: var(--text-primary); line-height: 1.2; }
.inspector-title span { font-size: 10px; color: var(--text-muted); display: block; }
.badge-glass { font-size: 9px; padding: 3px 6px; background: var(--bg-tertiary); border-radius: 3px; color: var(--text-secondary); flex-shrink: 0; margin-left: auto; }
.inspector-card .panel-body { display: flex; flex-direction: column; gap: 12px; }
.mini-chart-container { background: var(--bg-primary); border-radius: 4px; padding: 8px; border: 1px solid var(--border-dark); min-height: 50px; }
.chart-bars { height: 40px; display: flex; align-items: flex-end; gap: 1px; margin-bottom: 4px; }
.chart-bar { flex: 1; border-radius: 1px 1px 0 0; min-width: 2px; }
.chart-meta { display: flex; justify-content: space-between; font-size: 8px; color: var(--text-muted); }
.chart-meta span.active { color: var(--text-secondary); font-weight: 600; }
.inspector-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.metric-cell { background: var(--bg-tertiary); padding: 6px 8px; border-radius: 4px; display: flex; flex-direction: column; justify-content: center; }
.metric-cell label { font-size: 8px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 2px; font-weight: 600; line-height: 1; }
.metric-cell span { font-size: 11px; font-weight: 700; font-family: monospace; color: var(--text-primary); line-height: 1; }
.micro-metrics { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; padding: 8px; background: var(--bg-primary); border-radius: 4px; }
.micro-metric { display: flex; flex-direction: column; align-items: center; text-align: center; min-height: 50px; justify-content: center; }
.micro-metric .label { font-size: 8px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; margin-bottom: 3px; line-height: 1; }
.micro-metric .value { font-size: 11px; font-weight: 700; color: var(--text-primary); line-height: 1; }

/* Toast */
.toast-notification { position: fixed; bottom: 24px; right: 24px; padding: 14px 20px; border-radius: 6px; font-size: 13px; font-weight: 600; max-width: 320px; z-index: 1000; border: 1px solid var(--border-dark); }
.toast-success { background: rgba(74, 222, 128, 0.2); color: #4ade80; border-color: rgba(74, 222, 128, 0.3); }
.toast-error { background: rgba(248, 113, 113, 0.2); color: #f87171; border-color: rgba(248, 113, 113, 0.3); }
.toast-info { background: rgba(96, 165, 250, 0.2); color: #60a5fa; border-color: rgba(96, 165, 250, 0.3); }

/* Utilities */
.text-right { text-align: right; }
.text-gradient-green { background: linear-gradient(to right, #4ade80, #22c55e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-gradient-blue { background: linear-gradient(to right, #60a5fa, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-white { color: var(--text-primary); }
.mono { font-family: "SF Mono", monospace; }
.opacity-50 { opacity: 0.5; }
.opacity-80 { opacity: 0.8; }
.font-bold { font-weight: 700; }
.w-full { width: 100%; }

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  z-index: 2000;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 20px;
  padding-top: 80px;
  overflow: hidden;
}

.modal-container {
  background: var(--bg-secondary);
  border: 1px solid var(--border-medium);
  border-radius: 6px;
  width: 100%;
  max-width: 1200px;
  max-height: calc(100vh - 100px);
  height: auto;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.modal-container.modal-compact {
  max-height: fit-content;
  height: auto;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-dark);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-tertiary);
  flex-shrink: 0;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: -0.01em;
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-dark);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--border-medium);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

.modal-search {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-dark);
  border-radius: 4px;
}

.modal-search svg {
  flex-shrink: 0;
  color: var(--text-muted);
}

.modal-search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
  font-family: inherit;
}

.modal-search-input::placeholder {
  color: var(--text-muted);
}

.modal-table-container {
  flex: 1;
  overflow-y: auto;
  border-radius: 4px;
  background: var(--bg-primary);
}

.modal-table {
  width: 100%;
}

.modal-table tbody tr {
  cursor: pointer;
}

.modal-footer {
  padding-top: 16px;
  border-top: 1px solid var(--border-dark);
}

.modal-stats {
  display: flex;
  gap: 24px;
  font-size: 12px;
  color: var(--text-muted);
}

.modal-stats strong {
  color: var(--text-primary);
  font-weight: 600;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .modal-container,
.modal-fade-leave-to .modal-container {
  transform: scale(0.95) translateY(20px);
}

/* Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1); }
.slide-up-enter-from { transform: translateY(20px); opacity: 0; }
.slide-up-leave-to { transform: translateY(20px); opacity: 0; }

/* Responsive */
@media (max-width: 1024px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .portfolio-page {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .portfolio-page {
    padding: 16px;
    margin-top: 0;
    gap: 20px;
  }
  .hero-section {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  .hero-left h1 {
    font-size: 18px;
    flex-wrap: wrap;
    white-space: normal;
  }
  .hero-actions {
    width: 100%;
    flex-wrap: wrap;
    justify-content: flex-start;
  }
  .btn-glass {
    height: 44px;
    min-width: 44px;
  }
  .kpi-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .kpi-value {
    font-size: 22px;
  }
  .glass-panel {
    border-radius: 4px;
  }
  .panel-header {
    padding: 12px 16px;
  }
  .panel-body {
    padding: 12px 16px;
  }
  /* Bank selector mobile */
  .bank-selector {
    min-width: unset;
    width: 100%;
    padding: 8px 12px;
  }
  .bank-selector-name {
    font-size: 11px;
  }
  .bank-dropdown {
    min-width: unset;
    left: -50px;
    right: -50px;
    max-width: calc(100vw - 32px);
  }
  /* Table horizontal scroll */
  .table-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .glass-table {
    min-width: 600px;
  }
  /* Hide some columns on mobile */
  .glass-table th:nth-child(4),
  .glass-table td:nth-child(4),
  .glass-table th:nth-child(6),
  .glass-table td:nth-child(6),
  .glass-table th:nth-child(7),
  .glass-table td:nth-child(7) {
    display: none;
  }
  /* Glass pills */
  .hero-meta {
    flex-wrap: wrap;
    gap: 8px;
  }
  .glass-pill {
    font-size: 10px;
    padding: 4px 8px;
  }
}

@media (max-width: 480px) {
  .portfolio-page {
    padding: 12px;
    gap: 16px;
  }
  .hero-section {
    gap: 12px;
  }
  .hero-left h1 {
    font-size: 16px;
  }
  .kpi-card {
    padding: 12px;
  }
  .kpi-value {
    font-size: 18px;
  }
  .kpi-label {
    font-size: 10px;
  }
  .glass-panel {
    border-radius: 4px;
  }
  .panel-header {
    padding: 10px 12px;
  }
  .panel-body {
    padding: 10px 12px;
  }
  /* Hide more table columns */
  .glass-table th:nth-child(3),
  .glass-table td:nth-child(3),
  .glass-table th:nth-child(5),
  .glass-table td:nth-child(5) {
    display: none;
  }
}

@media (max-width: 375px) {
  .portfolio-page {
    padding: 10px;
    gap: 12px;
  }
  .hero-left h1 {
    font-size: 14px;
  }
  .kpi-value {
    font-size: 16px;
  }
  .btn-glass {
    font-size: 11px;
    padding: 0 12px;
  }
  .btn-glass.compact {
    height: 40px;
    font-size: 10px;
    padding: 0 10px;
  }
}
</style>
