<!-- src/views/PortfolioView.vue - FINAL VERSION -->
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
            {{ portfolioMetrics ? portfolioMetrics.var_95_percent.toFixed(1) + '%' : '1.2%' }}
          </div>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-white">
            {{ portfolioMetrics ? portfolioMetrics.var_95_percent.toFixed(2) + '%' : '2.45%' }}
          </div>
          <div class="kpi-sub">
            Дневной риск
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

    <!-- Main Dashboard Grid -->
    <div class="dashboard-grid">
      <!-- LEFT COLUMN -->
      <div class="col-main">
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

        <!-- Correlation Matrix -->
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Матрица Корреляций</h3>
          </div>
          <div class="panel-body heatmap-body">
            <div class="heatmap-wrapper">
              <div class="heatmap-header-row">
                <div class="heatmap-empty" />
                <div
                  v-for="col in correlationMatrix.slice(0, 10)"
                  :key="col.label"
                  class="heatmap-th"
                >
                  {{ col.label }}
                </div>
              </div>
              <div
                v-for="(row, r) in correlationMatrix.slice(0, 10)"
                :key="r"
                class="heatmap-row"
              >
                <div class="heatmap-rh">
                  {{ row.label }}
                </div>
                <div 
                  v-for="(val, c) in row.values.slice(0, 10)" 
                  :key="c" 
                  class="heatmap-cell"
                  :style="{ backgroundColor: getHeatmapColor(val) }"
                >
                  {{ val === 1 ? '1.0' : val.toFixed(2) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 3D Correlation Heatmap - Full Width -->
        <div
          class="glass-panel heatmap-panel"
          style="margin-bottom: 0;"
        >
          <div class="panel-header">
            <h3>3D Тепловая карта активов</h3>
            <span class="panel-badge">Интерактивная визуализация</span>
          </div>
          <div
            class="panel-body"
            style="padding: 8px 10px 0 10px; position: relative; margin-bottom: 0;"
          >
            <p
              class="section-description"
              style="margin-bottom: 8px; padding: 6px 10px; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; background: rgba(0,0,0,0.2); font-size: 11px; line-height: 1.4;"
            >
              Каждый актив представлен шариком. Размер = вес в портфеле, цвет = цвет актива. 
              Позиция в 3D пространстве основана на корреляциях между активами.
              <br><strong>Наведите на шарик</strong> для детализации позиции.
            </p>
            <div
              id="correlation-3d-heatmap"
              style="width:100%; height:500px; position: relative; min-height: 500px; background: rgba(0,0,0,0.1); border-radius: 8px; margin-bottom: 0; display: block; visibility: visible; opacity: 1;"
            />
            <div
              v-if="hoveredAsset"
              class="asset-tooltip-3d"
            >
              <div class="tooltip-header">
                <div
                  class="asset-icon"
                  :style="{ background: hoveredAsset.color }"
                >
                  {{ hoveredAsset.symbol[0] }}
                </div>
                <div>
                  <div class="tooltip-symbol">
                    {{ hoveredAsset.symbol }}
                  </div>
                  <div class="tooltip-name">
                    {{ hoveredAsset.name }}
                  </div>
                </div>
              </div>
              <div class="tooltip-details">
                <div class="tooltip-row">
                  <span>Тип:</span>
                  <strong>{{ (hoveredAsset.symbol.includes('ОФЗ') || hoveredAsset.symbol.includes('Облигац')) ? 'Облигация' : 'Акция' }}</strong>
                </div>
                <div
                  v-if="hoveredAsset.volatility !== undefined"
                  class="tooltip-row"
                >
                  <span>Волатильность:</span>
                  <strong>{{ hoveredAsset.volatility?.toFixed(1) || 'Н/Д' }}%</strong>
                </div>
                <div
                  v-if="hoveredAsset.avgCorrelation !== undefined"
                  class="tooltip-row"
                >
                  <span>Ср. корреляция:</span>
                  <strong>{{ hoveredAsset.avgCorrelation?.toFixed(2) || 'Н/Д' }}</strong>
                </div>
                <div class="tooltip-row">
                  <span>Вес в портфеле:</span>
                  <strong>{{ hoveredAsset.allocation?.toFixed(2) || hoveredAsset.allocation }}%</strong>
                </div>
                <div class="tooltip-row">
                  <span>Цена:</span>
                  <strong>{{ hoveredAsset.price?.toLocaleString('ru-RU') || hoveredAsset.price }} ₽</strong>
                </div>
                <div class="tooltip-row">
                  <span>Дневное изм.:</span>
                  <strong :class="hoveredAsset.dayChange >= 0 ? 'text-green' : 'text-red'">
                    {{ hoveredAsset.dayChange >= 0 ? '+' : '' }}{{ hoveredAsset.dayChange?.toFixed(2) || hoveredAsset.dayChange }}%
                  </strong>
                </div>
                <div
                  v-if="hoveredAsset.notional"
                  class="tooltip-row"
                >
                  <span>Позиция:</span>
                  <strong>${{ (hoveredAsset.notional / 1000).toFixed(1) }}k</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN -->
      <aside class="col-side-flex">
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

        <!-- CCMV OPTIMIZATION LINK -->
        <div class="glass-panel optimizer-link-card">
          <div class="optimizer-link-content">
            <div class="optimizer-link-icon">
              <svg
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
              >
                <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 class="optimizer-link-title">
              Оптимизация портфеля
            </h3>
            <p class="optimizer-link-description">
              Стохастическое оптимизирование с HJB-стратегией и CCMV модель оптимизации
            </p>
            <div class="optimizer-link-features">
              <span class="feature-tag">HJB-стратегия</span>
              <span class="feature-tag">CCMV</span>
            </div>
            <router-link
              to="/CCMVoptimization"
              class="btn-glass primary w-full optimizer-link-btn"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M9 5l7 7-7 7" />
              </svg>
              Перейти к оптимизации
            </router-link>
          </div>
        </div>
              
        <!-- Риск и Статистика (объединенный блок) -->
        <div class="glass-panel combined-metrics metrics-panel">
          <div class="panel-header-mini">
            <span class="panel-title-mini">Риск и Статистика</span>
          </div>

          <!-- Все метрики в виде строк -->
          <div class="metrics-section">
            <div class="metric-row">
              <div class="metric-label">
                <span>Expected Shortfall</span>
                <span class="meta-hint">CVaR 95%</span>
              </div>
              <div class="metric-value text-red">
                -3.78%
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>Max Drawdown</span>
                <span class="meta-hint">От пика до минимума</span>
              </div>
              <div class="metric-value text-red">
                {{ portfolioMetrics ? (portfolioMetrics.max_drawdown * 100).toFixed(2) + '%' : '-18.24%' }}
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>Calmar Ratio</span>
                <span class="meta-hint">Доходность / Max DD</span>
              </div>
              <div class="metric-value text-white">
                1.41
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>Скользящая волатильность (30Д)</span>
                <span class="meta-hint">Годовая</span>
              </div>
              <div class="metric-value text-white">
                12.8%
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>Доходность с начала года</span>
                <span class="meta-hint">YTD</span>
              </div>
              <div class="metric-value text-green">
                +8.42%
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>Процент выигрышей</span>
                <span class="meta-hint">% прибыльных</span>
              </div>
              <div class="metric-value text-green">
                58.3%
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>Фактор прибыли</span>
                <span class="meta-hint">Валовая П / Валовая У</span>
              </div>
              <div class="metric-value text-white">
                1.87x
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>Средняя сделка</span>
                <span class="meta-hint">Средняя доходность</span>
              </div>
              <div class="metric-value text-white">
                +0.34%
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>Sharpe Ratio</span>
                <span class="meta-hint">Скорректированный на риск</span>
              </div>
              <div class="metric-value text-green">
                {{ portfolioMetrics ? portfolioMetrics.sharpe_ratio.toFixed(2) : '1.52' }}
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>Sortino Ratio</span>
                <span class="meta-hint">Риск снижения</span>
              </div>
              <div class="metric-value text-green">
                {{ portfolioMetrics ? portfolioMetrics.sortino_ratio.toFixed(2) : '2.14' }}
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>Beta</span>
                <span class="meta-hint">относительно бенчмарка</span>
              </div>
              <div class="metric-value text-white">
                {{ portfolioMetrics ? portfolioMetrics.beta.toFixed(2) : '0.87' }}
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>Alpha</span>
                <span class="meta-hint">Избыточная доходность</span>
              </div>
              <div
                class="metric-value"
                :class="portfolioMetrics?.alpha && portfolioMetrics.alpha >= 0 ? 'text-green' : 'text-red'"
              >
                {{ portfolioMetrics ? (portfolioMetrics.alpha >= 0 ? '+' : '') + (portfolioMetrics.alpha * 100).toFixed(2) + '%' : '+2.31%' }}
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>VaR (95%)</span>
                <span class="meta-hint">Дневной</span>
              </div>
              <div class="metric-value text-red">
                {{ portfolioMetrics ? (portfolioMetrics.var_95_percent * -1).toFixed(2) + '%' : '-2.15%' }}
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>Information Ratio</span>
                <span class="meta-hint">Активная доходность / Ошибка отслеживания</span>
              </div>
              <div class="metric-value text-green">
                0.94
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>Treynor Ratio</span>
                <span class="meta-hint">Доходность / Beta</span>
              </div>
              <div class="metric-value text-white">
                9.67%
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-label">
                <span>Tracking Error</span>
                <span class="meta-hint">относительно индекса</span>
              </div>
              <div class="metric-value text-white">
                3.42%
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- 3D Correlation Scatter Plot - Full Width -->
    <div class="glass-panel scatter-3d-panel">
      <div class="panel-header">
        <h3>3D Визуализация Корреляций</h3>
        <span class="panel-badge">Интерактивный анализ</span>
      </div>
      <div class="panel-body scatter-3d-body">
        <CorrelationScatter3D :available-assets="topAssetsFor3D" />
      </div>
    </div>


    <!-- 4️⃣ LATENT VOLATILITY SECTION - 3D SURFACE -->
    <!-- ЗАКОММЕНТИРОВАНО: Может понадобиться позже -->
    <!--
    <div class="glass-panel">
      <div class="panel-header">
        <h3>🤯 INSANE Quant Latent Volatility Model</h3>
        <span class="panel-badge alert">Leading Indicator</span>
      </div>
      <div class="panel-body" style="padding-top: 16px;">
        <p class="section-description" style="margin-bottom: 12px; padding: 8px 12px; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; background: rgba(0,0,0,0.2); font-size: 12px; line-height: 1.5;">
          3D поверхность волатильности детектирует предварительные сигналы сдвига пика волатильности до того, как это отразится в ценах.
          <br><strong>Цветовая карта:</strong> 
          <span style="color: #3b82f6;">🔵 Синий</span> = низкий Z-Score (нормальная волатильность), 
          <span style="color: #10b981;">🟢 Зеленый</span> = норма (стабильное состояние), 
          <span style="color: #fbbf24;">🟡 Желтый</span> = повышенный Z-Score (внимание, возможен сдвиг), 
          <span style="color: #f97316;">🟠 Оранжевый</span> = высокий Z-Score (предупреждение о сдвиге), 
          <span style="color: #ef4444;">🔴 Красный</span> = экстремальный Z-Score (критический сигнал, рекомендуется снижение позиций).
          <br>Пик на поверхности показывает текущее положение максимума волатильности. Сдвиг пика влево/вправо предупреждает о потенциальных изменениях.
        </p>

        <div class="latent-vol-status" :class="'status-' + latentVolAlert.severity" style="margin-bottom: 0;">
          <div class="status-indicator" :class="'indicator-' + latentVolAlert.severity"></div>
          <div class="status-info">
            <p class="status-state">{{ latentVolAlert.severity === 'critical' ? '🔴 PRE-SHOCK WARNING' : '🟢 Normal' }}</p>
            <p class="status-zscore">Z-Score Shift: {{ latentVolMetrics.currentZscore.toFixed(2) }}</p>
          </div>
        </div>

        <div id="latent-vol-surface-3d"
             style="width:100%; height:800px; margin: -20px; margin-bottom: 16px; margin-top: -15px;"></div>

        <div class="latent-vol-legend">
          <div class="legend-item">
            <span class="legend-color" style="background: #7f1d1d;"></span>
            <span>Low Vol Peak Position</span>
          </div>
          <div class="legend-item">
            <span class="legend-color" style="background: #dc2626;"></span>
            <span>Medium Vol Peak</span>
          </div>
          <div class="legend-item">
            <span class="legend-color" style="background: #ef4444;"></span>
            <span>High Vol Peak</span>
          </div>
          <div class="legend-item">
            <span class="legend-color" style="background: #f97316;"></span>
            <span>Elevated Risk</span>
          </div>
          <div class="legend-item">
            <span class="legend-color" style="background: #fbbf24;"></span>
            <span>Warning Zone</span>
          </div>
          <div class="legend-item">
            <span class="legend-color" style="background: #fcd34d;"></span>
            <span>Critical Alert</span>
          </div>
        </div>

        <div class="latent-vol-metrics" style="margin-top: 16px;">
          <div class="metric">
            <p class="metric-label">Alert Precision</p>
            <p class="metric-value">{{ latentVolMetrics.precision }}%</p>
          </div>
          <div class="metric">
            <p class="metric-label">Alert Recall</p>
            <p class="metric-value">{{ latentVolMetrics.recall }}%</p>
          </div>
          <div class="metric">
            <p class="metric-label">Recent Alerts (30d)</p>
            <p class="metric-value">{{ latentVolMetrics.recentAlerts }}</p>
          </div>
          <div class="metric">
            <p class="metric-label">True Positives</p>
            <p class="metric-value">{{ latentVolMetrics.truePositives }}</p>
          </div>
        </div>

        <div class="alert-history-table" style="margin-top: 16px;">
          <div style="font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.6); margin-bottom: 8px;">Alert History (Last 10 Days)</div>
          <div style="max-height: 150px; overflow-y: auto;">
            <div v-for="(alert, i) in latentVolMetrics.alertHistory" :key="i" class="alert-history-row">
              <span class="alert-date">{{ alert.date }}</span>
              <span class="alert-zscore">{{ alert.zscore.toFixed(2) }}</span>
              <span :class="['alert-outcome', alert.outcome ? 'text-green' : 'text-red']">
                {{ alert.outcome ? '✓ Drawdown' : '✗ False' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    -->

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
import CorrelationScatter3D from '../components/common/CorrelationScatter3D.vue'
import { usePortfolioStore, defaultBank } from '../stores/portfolio'
import { calculatePortfolioMetrics, type PortfolioMetricsResponse } from '../services/portfolioService'

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

// Динамический импорт Plotly
let Plotly: any = null
const loadPlotly = async () => {
  if (typeof window === 'undefined') {
    console.error('Window is undefined')
    return null
  }
  
  // Проверяем, уже ли загружен Plotly
  if ((window as any).Plotly) {
    Plotly = (window as any).Plotly
    return Plotly
  }
  
  // Проверяем, не загружается ли уже скрипт
  const existingScript = document.querySelector('script[src*="plotly"]')
  if (existingScript) {
    return new Promise((resolve) => {
      const checkInterval = trackInterval(() => {
        if ((window as any).Plotly) {
          clearInterval(checkInterval)
          activeIntervalIds.delete(checkInterval)
          Plotly = (window as any).Plotly
          resolve(Plotly)
        }
      }, 100)

      // Таймаут на случай, если скрипт не загрузится
      trackTimeout(() => {
        clearInterval(checkInterval)
        activeIntervalIds.delete(checkInterval)
        console.error('Plotly script timeout')
        resolve(null)
      }, 10000)
    })
  }
  
  // Создаем новый скрипт
  const script = document.createElement('script')
  script.src = 'https://cdn.plot.ly/plotly-latest.min.js'
  script.async = true
  script.crossOrigin = 'anonymous'
  
  return new Promise((resolve, reject) => {
    script.onload = () => {
      if ((window as any).Plotly) {
        Plotly = (window as any).Plotly
        resolve(Plotly)
      } else {
        console.error('Plotly not found after script load')
        reject(new Error('Plotly not found'))
      }
    }
    
    script.onerror = (error) => {
      console.error('Failed to load Plotly script:', error)
      reject(error)
    }
    
    document.head.appendChild(script)
  })
}

// ============================================================================
// WAVE_σ.9 STATE
// ============================================================================
const waveRegime = ref({
  currentRegime: 'TRENDING',
  positionSize: 100,
  lambda: 5,
  jaggedness: 0.42,
  pctChoppy: 32,
  volRatio: 1.5,
  history: ['TRENDING', 'TRENDING', 'CHOPPY', 'TRENDING', 'TRENDING', 'TRENDING', 'CHOPPY', 'CHOPPY', 'CHOPPY', 'TRENDING', 'TRENDING', 'TRENDING', 'TRENDING', 'TRENDING', 'CHOPPY', 'CHOPPY', 'TRENDING', 'TRENDING', 'TRENDING', 'TRENDING']
})

// ============================================================================
// LATENT VOL STATE
// ============================================================================
const latentVolAlert = ref({
  isActive: false,
  severity: 'normal',
  title: 'Предварительный сигнал тревоги',
  message: 'Пик волатильности сдвинулся. Рекомендуется снизить long-позиции на 50%'
})

const latentVolMetrics = ref({
  currentZscore: 0.12,
  precision: 42,
  recall: 35,
  recentAlerts: 3,
  truePositives: 2,
  alertHistory: [
    { date: '2026-01-06', zscore: 0.12, outcome: false },
    { date: '2026-01-05', zscore: -0.45, outcome: false },
    { date: '2026-01-04', zscore: 2.12, outcome: true },
    { date: '2026-01-03', zscore: 1.85, outcome: true },
    { date: '2026-01-02', zscore: -0.32, outcome: false },
  ]
})

// ============================================================================
// ============================================================================
// EXISTING STATE
// ============================================================================
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
    // Российские акции
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
    // Российские облигации
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
    // Российские акции
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
    // Российские облигации
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
    // Российские акции
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
    // Российские облигации
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
    // Российские акции
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
    // Российские облигации
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
// (Оставлено для совместимости, но используем store.positions)
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
// BANK SELECTOR - используем store
// ============================================================================
const { selectedBank, positions, banks } = storeToRefs(portfolioStore)

const isBankMenuOpen = ref(false)
const bankSearchQuery = ref('')

const selectedAsset = ref<any>(null)
const hoveredAsset = ref<any>(null)

// Функция для загрузки метрик портфеля из API
const loadPortfolioMetrics = async () => {
  if (!positions.value || positions.value.length === 0) {
    portfolioMetrics.value = null
    return
  }

  isLoadingMetrics.value = true
  try {
    // Преобразуем позиции в формат для API
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
    console.error('Failed to load portfolio metrics:', error)
    // В случае ошибки оставляем null, будут использоваться значения по умолчанию
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
  // Загружаем метрики при изменении портфеля
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
  // Блокируем прокрутку body при открытии модального окна
  if (typeof document !== 'undefined') {
    document.body.style.overflow = 'hidden'
  }
}

const closePortfolioDetails = () => {
  isPortfolioDetailsOpen.value = false
  // Разблокируем прокрутку body при закрытии модального окна
  if (typeof document !== 'undefined') {
    document.body.style.overflow = ''
  }
}

// Генерация детерминированной матрицы корреляций на основе текущего портфеля (все 25 активов)
const correlationMatrix = computed(() => {
  // Берем все активы портфеля для полной картины корреляций
  const allAssets = [...positions.value]
  
  // Функция для получения детерминированного значения корреляции на основе символов
  const getCorrelation = (symbol1: string, symbol2: string): number => {
    if (symbol1 === symbol2) return 1.0
    
    // Определяем тип актива
    const isBond1 = symbol1.includes('SU') || symbol1.includes('RU000')
    const isBond2 = symbol2.includes('SU') || symbol2.includes('RU000')
    
    // Простая хеш-функция для детерминированных значений
    const hash = (str: string) => {
      let hash = 0
      for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) - hash) + str.charCodeAt(i)
        hash = hash & hash
      }
      return Math.abs(hash)
    }
    
    // Корреляция между облигациями выше
    if (isBond1 && isBond2) {
      const seed = hash(symbol1 + symbol2) % 100
      return 0.7 + (seed / 100) * 0.2 // 0.7-0.9
    }
    
    // Корреляция между акциями
    if (!isBond1 && !isBond2) {
      // Акции одного сектора имеют более высокую корреляцию
      const sameSector = 
        (symbol1.includes('SBER') && symbol2.includes('VTBR')) ||
        (symbol1.includes('VTBR') && symbol2.includes('SBER')) ||
        (symbol1.includes('GAZP') && symbol2.includes('ROSN')) ||
        (symbol1.includes('ROSN') && symbol2.includes('GAZP')) ||
        (symbol1.includes('LKOH') && symbol2.includes('TATN')) ||
        (symbol1.includes('TATN') && symbol2.includes('LKOH')) ||
        (symbol1.includes('NVTK') && symbol2.includes('GAZP')) ||
        (symbol1.includes('GAZP') && symbol2.includes('NVTK'))
      
      if (sameSector) {
        const seed = hash(symbol1 + symbol2) % 100
        return 0.6 + (seed / 100) * 0.3 // 0.6-0.9
      }
      const seed = hash(symbol1 + symbol2) % 100
      return 0.3 + (seed / 100) * 0.4 // 0.3-0.7
    }
    
    // Корреляция между акциями и облигациями (обычно низкая или отрицательная)
    const seed = hash(symbol1 + symbol2) % 100
    return -0.1 + (seed / 100) * 0.3 // -0.1 до 0.2
  }
  
  // Генерируем матрицу корреляций для активов портфеля
  return allAssets.map((asset) => {
    const values = allAssets.map((otherAsset) => {
      return getCorrelation(asset.symbol, otherAsset.symbol)
    })
    
    return {
      label: asset.symbol,
      values: values
    }
  })
})

// Получаем топ-10 активов для 3D визуализации (по весу)
const topAssetsFor3D = computed(() => {
  return [...positions.value]
    .sort((a, b) => b.allocation - a.allocation)
    .slice(0, 10)
    .map(asset => asset.symbol)
})

// ============================================================================
// 3D CORRELATION HEATMAP
// ============================================================================
const initCorrelation3DHeatmap = async () => {
  try {
    const plotlyResult = await loadPlotly()
    if (!plotlyResult) {
      console.error('Plotly not loaded')
      return
    }
    Plotly = plotlyResult
    
    const container = document.getElementById('correlation-3d-heatmap')
    if (!container) {
      console.error('Container correlation-3d-heatmap not found')
      return
    }
    
    // Проверяем, что контейнер видим и имеет размеры
    if (container.clientWidth === 0 || container.clientHeight === 0) {
      console.warn('Container has zero dimensions, waiting for layout...')
      // Ждем следующего кадра для завершения layout
      await new Promise(resolve => requestAnimationFrame(resolve))
      if (container.clientWidth === 0 || container.clientHeight === 0) {
        console.error('Container still has zero dimensions after wait')
        return
      }
    }

    // Берем все активы для визуализации (акции и облигации)
    const allAssets = [...positions.value]

    if (allAssets.length === 0) return
    
    // Получаем матрицу корреляций для этих активов
    const matrix = correlationMatrix.value
    
    // Вычисляем 3D координаты на основе метрик (Волатильность, Средняя корреляция, Вес)
    const calculate3DPositions = (assets: any[], corrMatrix: any[]) => {
      return assets.map((asset) => {
        // Определяем тип актива
        const isBond = asset.symbol.includes('SU') || asset.symbol.includes('RU000')
        
        // Цвет: Акции - зеленый (#10b981), Облигации - синий (#3b82f6)
        const assetColor = isBond ? '#3b82f6' : '#10b981'
        
        // X: Волатильность (берем из объекта актива, если нет - генерируем на основе типа)
        const volatility = isBond ? (3 + Math.random() * 4) : (15 + Math.random() * 20)
        
        // Y: Коррелятивная связь (средняя корреляция со всеми активами в матрице)
        const matrixIndex = corrMatrix.findIndex(row => row.label === asset.symbol)
        let avgCorrelation = 0
        if (matrixIndex !== -1) {
          const values = corrMatrix[matrixIndex].values
          avgCorrelation = values.reduce((a: number, b: number) => a + b, 0) / values.length
        }
        
        // Z: Вес в портфеле (allocation)
        const weight = asset.allocation
        
        return { 
          x: volatility, 
          y: avgCorrelation, 
          z: weight, 
          asset: { ...asset, color: assetColor } 
        }
      })
    }
    
    const positions3D = calculate3DPositions(allAssets, matrix)
    
    if (positions3D.length === 0) {
      console.error('No 3D positions calculated')
      return
    }
    
    // Нормализуем данные в диапазон 0-10 для равномерного масштаба осей
    const xValues = positions3D.map(p => p.x)
    const yValues = positions3D.map(p => p.y)
    const zValues = positions3D.map(p => p.z)
    
    const xMin = Math.min(...xValues), xMax = Math.max(...xValues)
    const yMin = Math.min(...yValues), yMax = Math.max(...yValues)
    const zMin = Math.min(...zValues), zMax = Math.max(...zValues)
    
    const normalize = (val: number, min: number, max: number) => {
      if (max === min) return 5
      return ((val - min) / (max - min)) * 10
    }
    
    // Нормализованные позиции
    const normalizedPositions = positions3D.map(p => ({
      ...p,
      nx: normalize(p.x, xMin, xMax),
      ny: normalize(p.y, yMin, yMax),
      nz: normalize(p.z, zMin, zMax)
    }))
    
    // Функция генерации сферы (теперь с одинаковым радиусом по всем осям)
    const createSphere = (cx: number, cy: number, cz: number, r: number, color: string, asset: any) => {
      const x: number[] = []
      const y: number[] = []
      const z: number[] = []
      
      const steps = 16 // Детализация сферы
      
      for (let i = 0; i < steps; i++) {
        const t = (i / (steps - 1)) * Math.PI
        for (let j = 0; j < steps; j++) {
          const p = (j / (steps - 1)) * 2 * Math.PI
          
          // Одинаковый радиус по всем осям = идеальная сфера
          x.push(cx + r * Math.sin(t) * Math.cos(p))
          y.push(cy + r * Math.sin(t) * Math.sin(p))
          z.push(cz + r * Math.cos(t))
        }
      }
      
      return {
        type: 'mesh3d',
      x: x,
      y: y,
      z: z,
        color: color,
        alphahull: 0,
        opacity: 1,
        flatshading: false,
      lighting: {
        ambient: 0.6,
          diffuse: 0.9,
          specular: 1.0,
          roughness: 0.1,
          fresnel: 0.8
        },
        lightposition: {
          x: 10,
          y: 10,
          z: 20
        },
        hoverinfo: 'none', // Отключаем стандартный Plotly tooltip, используем кастомный
        customdata: asset, // Добавляем данные актива для обработки hover (не массив)
        name: asset.symbol
      }
    }

    // Создаем trace-сферу для каждого актива + scatter для hover
    const traces: any[] = []
    
    // 1. Добавляем сферы
    normalizedPositions.forEach((pos) => {
      const asset = pos.asset
      const size = 0.3 + (asset.allocation / 25) // Радиус пропорционален весу
      
      traces.push(createSphere(pos.nx, pos.ny, pos.nz, size, asset.color, asset))
    })
    
    // 2. Добавляем точки для hover с детализированным tooltip (ВАЖНО: этот trace должен быть последним!)
    traces.push({
      x: normalizedPositions.map(p => p.nx),
      y: normalizedPositions.map(p => p.ny),
      z: normalizedPositions.map(p => p.nz),
      mode: 'markers',
      type: 'scatter3d',
      marker: {
        size: normalizedPositions.map(p => Math.max(40, (0.3 + p.asset.allocation/25) * 40)), // Размер для перехвата событий
        color: 'rgba(255,255,255,0)', // Полностью прозрачный
        opacity: 0, // Полностью невидимый
        line: {
          width: 0
        }
      },
      hoverinfo: 'skip', // Полностью отключаем стандартный Plotly tooltip
      customdata: normalizedPositions.map(p => p.asset)
    })

    const layout = {
      showlegend: false,
      hovermode: 'closest', // Включаем hover для перехвата событий (стандартный tooltip отключен через hoverinfo)
      scene: {
        xaxis: { 
          title: 'РИСК (Волатильность %)',
          backgroundcolor: 'rgba(20, 22, 28, 0.8)',
          gridcolor: 'rgba(255,255,255,0.08)',
          zeroline: false,
          showbackground: true,
          titlefont: { color: '#ffffff', size: 12, weight: 'bold' },
          tickfont: { size: 9, color: 'rgba(255,255,255,0.6)' },
          tickvals: [0, 2.5, 5, 7.5, 10],
          ticktext: [
            xMin.toFixed(0) + '%',
            ((xMin + xMax) / 4 * 1 + xMin * 3/4).toFixed(0) + '%',
            ((xMin + xMax) / 2).toFixed(0) + '%',
            ((xMin + xMax) / 4 * 3 + xMax * 1/4).toFixed(0) + '%',
            xMax.toFixed(0) + '%'
          ],
          showspikes: false
        },
        yaxis: { 
          title: 'СВЯЗЬ (Корреляция)',
          backgroundcolor: 'rgba(30, 32, 38, 0.6)',
          gridcolor: 'rgba(255,255,255,0.08)',
          zeroline: false,
          showbackground: true,
          titlefont: { color: '#ffffff', size: 12, weight: 'bold' },
          tickfont: { size: 9, color: 'rgba(255,255,255,0.6)' },
          tickvals: [0, 2.5, 5, 7.5, 10],
          ticktext: [
            yMin.toFixed(2),
            ((yMin + yMax) / 4 * 1 + yMin * 3/4).toFixed(2),
            ((yMin + yMax) / 2).toFixed(2),
            ((yMin + yMax) / 4 * 3 + yMax * 1/4).toFixed(2),
            yMax.toFixed(2)
          ],
          showspikes: false
        },
        zaxis: { 
          title: 'ДОЛЯ (Вес %)',
          backgroundcolor: 'rgba(20, 22, 28, 0.8)',
          gridcolor: 'rgba(255,255,255,0.08)',
          zeroline: false,
          showbackground: true,
          titlefont: { color: '#ffffff', size: 12, weight: 'bold' },
          tickfont: { size: 9, color: 'rgba(255,255,255,0.6)' },
          tickvals: [0, 2.5, 5, 7.5, 10],
          ticktext: [
            zMin.toFixed(1) + '%',
            ((zMin + zMax) / 4 * 1 + zMin * 3/4).toFixed(1) + '%',
            ((zMin + zMax) / 2).toFixed(1) + '%',
            ((zMin + zMax) / 4 * 3 + zMax * 1/4).toFixed(1) + '%',
            zMax.toFixed(1) + '%'
          ],
          showspikes: false
        },
        bgcolor: 'rgba(0,0,0,0)',
        camera: {
          eye: { x: 1.8, y: 1.8, z: 1.2 },
          center: { x: 0, y: 0, z: 0 },
          up: { x: 0, y: 0, z: 1 }
        },
        aspectmode: 'cube'
      },
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: { color: '#fff', family: 'system-ui' },
      margin: { l: 0, r: 0, b: 0, t: 0 },
      autosize: true
    }

    const config = {
      responsive: true,
      displayModeBar: false,
      staticPlot: false,
      displaylogo: false
    }

    try {
      Plotly.newPlot(container, traces, layout, config)
    } catch (error) {
      console.error('Portfolio: Error creating 3D plot:', error)
      return
    }
    
    // Обработчик hover для кастомного tooltip в правом нижнем углу
    const plotlyContainer = container as any
    
    plotlyContainer.on('plotly_hover', (data: any) => {
      if (data && data.points && data.points.length > 0) {
        // Обрабатываем все точки - ищем customdata или актив по индексу
        for (const point of data.points) {
          // Проверяем customdata (может быть в mesh3d или scatter)
          if (point.customdata) {
            // customdata в mesh3d это массив с одним элементом
            const asset = Array.isArray(point.customdata) ? point.customdata[0] : point.customdata
            if (asset) {
              hoveredAsset.value = asset
              return
            }
          }
          
          // Если это scatter3d trace (последний в массиве), используем индекс
          const scatterTraceIndex = traces.length - 1
          if (point.curveNumber === scatterTraceIndex && point.pointNumber !== undefined) {
            const index = point.pointNumber
            if (index >= 0 && index < normalizedPositions.length && normalizedPositions[index]) {
              hoveredAsset.value = normalizedPositions[index].asset
              return
            }
          }
          
          // Если это mesh3d trace, находим по индексу trace
          if (point.curveNumber < scatterTraceIndex && point.curveNumber < normalizedPositions.length) {
            const index = point.curveNumber
            if (normalizedPositions[index]) {
              hoveredAsset.value = normalizedPositions[index].asset
              return
            }
          }
        }
      }
    })
    
    plotlyContainer.on('plotly_unhover', () => {
      hoveredAsset.value = null
    })
    
  } catch (err) {
    console.error('Error initializing 3D Correlation Heatmap:', err)
  }
}

// Обновляем график при изменении портфеля (только при смене банка)
watch([positions, selectedBank], () => {
  if (positions.length > 0) {
    trackTimeout(() => {
      initCorrelation3DHeatmap()
    }, 200)
  }
}, { deep: false })


// ============================================================================
// LATENT VOL 3D SURFACE
// ============================================================================
// ЗАКОММЕНТИРОВАНО: Может понадобиться позже
/*
const initLatentVol3D = async () => {
  try {
    await loadPlotly()
    if (!Plotly) {
      console.error('Plotly not loaded for Latent Vol')
      return
    }
    
    const container = document.getElementById('latent-vol-surface-3d')
    if (!container) {
      console.error('Container latent-vol-surface-3d not found')
      return
    }
    
    const generateLatentSurface = (offset: number) => {
    const n = 40
    const x = Array.from({ length: n }, (_, i) => i / (n - 1) * 100) // Peak position %
    const y = Array.from({ length: n }, (_, i) => i / (n - 1) * 30)  // Period (days)

    const centerX = 50 + Math.sin(offset / 30) * 25
    const centerY = 15 + Math.cos(offset / 40) * 8

    const z = Array.from({ length: n }, (_, i) =>
      Array.from({ length: n }, (_, j) => {
        const dx = (j / (n - 1) * 100 - centerX) / 25
        const dy = (i / (n - 1) * 30 - centerY) / 10
        const gaussian = Math.exp(-(dx * dx + dy * dy) / 2) * 100
        const noise = Math.sin(i / 8 + offset / 2) * Math.cos(j / 8 + offset / 2) * 10
        return Math.max(0, gaussian + noise + Math.abs(latentVolMetrics.value.currentZscore) * 15)
      })
    )
    return { x, y, z }
  }

  const { x, y, z } = generateLatentSurface(0)
  
  // Вычисляем min и max для нормализации
  const zFlat = z.flat()
  const zMin = Math.min(...zFlat)
  const zMax = Math.max(...zFlat)

  // Красочная цветовая карта для Latent Volatility
  // Показывает уровень Z-Score и риск сдвига волатильности
  const colorscale = [
    [0.0, '#1e3a8a'],      // Темно-синий - очень низкий Z-Score (норма)
    [0.15, '#3b82f6'],     // Синий - низкий Z-Score
    [0.3, '#22d3ee'],      // Голубой - умеренно низкий
    [0.5, '#10b981'],      // Зеленый - нормальный уровень
    [0.65, '#84cc16'],     // Лайм - умеренно повышенный
    [0.8, '#fbbf24'],      // Желтый - повышенный Z-Score (внимание)
    [0.9, '#f97316'],      // Оранжевый - высокий Z-Score (предупреждение)
    [1.0, '#ef4444']       // Красный - экстремальный Z-Score (тревога)
  ]

  const trace = {
    x, y, z,
    type: 'surface',
    colorscale,
    showscale: true,
    colorbar: {
      title: {
        text: 'Z-Score (Уровень риска)',
        font: { color: 'rgba(255,255,255,0.9)', size: 12 }
      },
      tickfont: { color: 'rgba(255,255,255,0.7)', size: 10 },
      tickmode: 'array',
      tickvals: [0, 0.25, 0.5, 0.75, 1],
      ticktext: ['Низкий', 'Умеренный', 'Норма', 'Высокий', 'Экстремальный'],
      len: 0.6,
      thickness: 15,
      x: 1.02,
      xpad: 10
    },
    contours: {
      z: {
        show: true,
        usecolorscale: true,
        project: { z: true },
        width: 2,
        color: 'rgba(255,255,255,0.3)'
      },
      x: {
        show: true,
        highlight: true,
        highlightcolor: 'rgba(255,255,255,0.5)',
        highlightwidth: 2
      },
      y: {
        show: true,
        highlight: true,
        highlightcolor: 'rgba(255,255,255,0.5)',
        highlightwidth: 2
      }
    },
    lighting: {
      ambient: 0.6,
      diffuse: 0.8,
      specular: 0.3,
      roughness: 0.5,
      fresnel: 0.2
    },
    lightposition: { x: 100, y: 100, z: 100 }
  }

  const layout = {
    scene: {
      xaxis: { 
        title: 'Vol Peak Position (%)',
        backgroundcolor: 'rgba(0,0,0,0)',
        gridcolor: 'rgba(255,255,255,0.15)',
        showbackground: true,
        titlefont: { color: 'rgba(255,255,255,0.9)', size: 14, family: 'system-ui' },
        tickfont: { size: 11, color: 'rgba(255,255,255,0.6)' }
      },
      yaxis: { 
        title: 'Period (Days)',
        backgroundcolor: 'rgba(0,0,0,0)',
        gridcolor: 'rgba(255,255,255,0.15)',
        showbackground: true,
        titlefont: { color: 'rgba(255,255,255,0.9)', size: 14, family: 'system-ui' },
        tickfont: { size: 11, color: 'rgba(255,255,255,0.6)' }
      },
      zaxis: { 
        title: 'Z-Score Shift',
        backgroundcolor: 'rgba(0,0,0,0)',
        gridcolor: 'rgba(255,255,255,0.15)',
        showbackground: true,
        titlefont: { color: 'rgba(255,255,255,0.9)', size: 14, family: 'system-ui' },
        tickfont: { size: 11, color: 'rgba(255,255,255,0.6)' }
      },
      camera: { 
        eye: { x: 3.0, y: 3.0, z: 2.5 },
        center: { x: 0, y: 0, z: 0 },
        up: { x: 0, y: 0, z: 1 }
      },
      aspectratio: { x: 2.5, y: 1.8, z: 1.5 }
    },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: '#fff', family: 'system-ui' },
    margin: { l: 0, r: 80, b: 0, t: 30 },
    title: {
      text: 'Цветовая карта: от синего (норма) до красного (экстремальный риск)',
      font: { color: 'rgba(255,255,255,0.7)', size: 11 },
      x: 0.5,
      xanchor: 'center',
      y: 0.98,
      yanchor: 'top'
    }
  }

    Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false })

    let frame = 0
    const latentInterval = setInterval(() => {
      frame += 0.15
      const { x: newX, y: newY, z: newZ } = generateLatentSurface(frame)
      Plotly.restyle(container, { z: [newZ], x: [newX], y: [newY] })
    }, 20)

    // ===== УПРАВЛЕНИЕ МЫШКОЙ ОТКЛЮЧЕНО - СТАТИЧНАЯ КАМЕРА =====
    // setupWaveControls(container)
    
  } catch (err) {
    console.error('Error initializing Latent Vol graph:', err)
  }
}
*/


// Sync heights of metrics panels
const syncPanelHeights = () => {
  if (typeof window === 'undefined') return

  trackTimeout(() => {
    // Больше не синхронизируем heatmap-panel, чтобы она не растягивалась под правую колонку
    const metricsPanel = document.querySelector('.metrics-panel') as HTMLElement
    // Можно добавить синхронизацию других панелей здесь, если нужно
  }, 100)
}

onMounted(async () => {
  // Убеждаемся, что selectedBank инициализирован
  if (!selectedBank.value) {
    portfolioStore.setSelectedBank(defaultBank)
  }
  
  if (positions?.value?.length > 0 && !selectedAsset.value) {
    selectedAsset.value = positions.value[0]
  }
  
  // Sync panel heights
  syncPanelHeights()
  
  // Инициализируем 3D тепловую карту корреляций
  trackTimeout(async () => {
    try {
      await initCorrelation3DHeatmap()
    } catch (err) {
      console.error('Failed to initialize 3D Correlation Heatmap:', err)
    }
  }, 500)
  
  // Инициализируем графики последовательно с задержкой
  // ЗАКОММЕНТИРОВАНО: Latent Vol график отключен
  // setTimeout(async () => {
  //   await initLatentVol3D()
  // }, 500)
  
  // ЗАКОММЕНТИРОВАНО: Latent Vol alert отключен
  // setTimeout(() => {
  //   latentVolAlert.value.isActive = true
  //   latentVolAlert.value.severity = 'warning'
  //   latentVolMetrics.value.currentZscore = 2.15
  //   // Re-sync heights after content loads
  //   syncPanelHeights()
  // }, 2000)
  
  // Re-sync on window resize
  window.addEventListener('resize', syncPanelHeights)
  
  // Обработчик клика вне меню банков
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('resize', syncPanelHeights)
  document.removeEventListener('click', handleClickOutside)
})

const selectAsset = (pos: any) => selectedAsset.value = pos

const recalcPortfolio = async () => {
  isRecalcing.value = true
  const newRegime = Math.random() > 0.5 ? 'TRENDING' : 'CHOPPY'
  waveRegime.value.currentRegime = newRegime
  waveRegime.value.positionSize = newRegime === 'TRENDING' ? 100 : 50
  waveRegime.value.lambda = newRegime === 'TRENDING' ? 5 : 10
  waveRegime.value.jaggedness = Math.random() * 0.8
  latentVolMetrics.value.currentZscore = (Math.random() - 0.5) * 3
  if (Math.abs(latentVolMetrics.value.currentZscore) > 2.0) {
    latentVolAlert.value.isActive = true
    latentVolAlert.value.severity = 'critical'
  }
  await new Promise(resolve => trackTimeout(resolve, 1500))
  lastUpdate.value = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
  isRecalcing.value = false
  showToast('Портфель пересчитан (Latent Vol обновлен)', 'success')
}

const exportPdf = () => {
  showToast('PDF экспорт инициирован...', 'info')
  trackTimeout(() => {
    showToast('Файл portfolio_2026-01-06.pdf загружен', 'success')
  }, 1200)
}

const filterPositions = (e: any) => {
  searchFilter.value = e.target.value
}

const openAnalysis = () => {
  if (selectedAsset.value) {
    showToast(`Открыт анализ ${selectedAsset.value.symbol}`, 'info')
  }
}

const showToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
  toast.value = { show: true, message, type }
  trackTimeout(() => {
    toast.value.show = false
  }, 3000)
}

const getHeatmapColor = (val: number) => {
   const alpha = Math.abs(val)
   if (val === 1) return 'rgba(255,255,255,0.05)'
   return val > 0 ? `rgba(59, 130, 246, ${alpha})` : `rgba(239, 68, 68, ${alpha})`
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
/* All CSS styling from previous version - preserved in full */
.portfolio-page { padding: 24px 32px; max-width: 100%; margin: 0 auto; display: flex; flex-direction: column; gap: 28px; min-height: 100vh; margin-top: 20px; }
.charts-row-two-col { display: grid; grid-template-columns: 1fr; gap: 24px; }
.dashboard-grid { display: grid; grid-template-columns: 1fr 340px; gap: 24px; }
.col-main { display: flex; flex-direction: column; gap: 24px; }
.col-side-flex { display: flex; flex-direction: column; gap: 16px; height: 100%; }

/* Heatmap Panel - Full Width */
.heatmap-panel {
  display: block;
  width: 100%;
  min-height: auto;
  height: auto;
}

.heatmap-panel .panel-body {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.treemap-tall {
  flex: 1;
  display: flex;
  min-height: 280px;
}

/* Metrics Panel - in right column, aligned with heatmap */
.metrics-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: auto;
  padding: 16px;
}

.metrics-panel .panel-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-header-mini {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-title-mini {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metrics-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metrics-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 16px 0;
}

/* 3D Scatter Panel - optimized space */
.scatter-3d-panel {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.scatter-3d-body {
  padding: 12px !important;
  display: flex;
  flex-direction: column;
  min-height: 0;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.latent-vol-legend {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  padding: 12px;
  background: rgba(0,0,0,0.2);
  border-radius: 8px;
  margin-bottom: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 10px;
  color: rgba(255,255,255,0.6);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

/* Alert Banner - полный стиль */
.alert-banner { width: 100%; backdrop-filter: blur(10px); border: 2px solid; border-radius: 12px; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; animation: slideDown 0.3s ease-out; margin-bottom: 20px; }
.alert-banner.alert-warning { background: rgba(251, 191, 36, 0.15); border-color: #fbbf24; }
.alert-banner.alert-critical { background: rgba(239, 68, 68, 0.15); border-color: #ef4444; }
.alert-content { display: flex; gap: 16px; align-items: flex-start; flex: 1; }
.alert-icon { font-size: 18px; flex-shrink: 0; }
.alert-text p { margin: 0; line-height: 1.4; }
.alert-title { font-size: 12px; font-weight: 700; color: #fff; text-transform: uppercase; }
.alert-message { font-size: 11px; color: rgba(255, 255, 255, 0.8); margin-top: 2px; }
.alert-close { background: none; border: none; color: #fff; font-size: 24px; cursor: pointer; opacity: 0.6; transition: opacity 0.2s; }
.alert-close:hover { opacity: 1; }

@keyframes slideDown {
  from { transform: translateY(-100%); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Regime, Metrics, Latent Vol Styles */
.regime-indicator-compact { display: flex; align-items: center; gap: 20px; padding: 10px 16px; background: rgba(20, 22, 28, 0.5); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; backdrop-filter: blur(20px); width: 100%; }
.regime-badge { display: flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 8px; font-weight: 600; font-size: 12px; }
.regime-dot { width: 6px; height: 6px; border-radius: 50%; animation: pulse 2s infinite; }
.regime-trending { background: rgba(74, 222, 128, 0.1); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.2); }
.regime-trending .regime-dot { background: #4ade80; box-shadow: 0 0 8px #4ade80; }
.regime-choppy { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }
.regime-choppy .regime-dot { background: #ef4444; box-shadow: 0 0 8px #ef4444; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.regime-details { display: flex; gap: 24px; font-size: 11px; color: rgba(255, 255, 255, 0.7); }
.regime-details span { display: flex; align-items: center; gap: 6px; }
.regime-details strong { color: #fff; font-weight: 600; }

/* Section Description & Panel Badge */
.section-description { font-size: 11px; color: rgba(255, 255, 255, 0.6); line-height: 1.6; margin-bottom: 16px; }
.panel-badge { font-size: 8px; padding: 3px 8px; background: rgba(59, 130, 246, 0.2); color: #60a5fa; border-radius: 4px; text-transform: uppercase; font-weight: 600; }
.panel-badge.alert { background: rgba(239, 68, 68, 0.2); color: #f87171; }

/* Wave Metrics & Charts */
.wave-metrics-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
.wave-metric { background: rgba(0, 0, 0, 0.2); padding: 12px; border-radius: 8px; text-align: center; }
.metric-label { font-size: 9px; color: rgba(255, 255, 255, 0.4); text-transform: uppercase; font-weight: 600; margin-bottom: 4px; }
.metric-value { font-size: 13px; font-weight: 700; color: #fff; }
.text-green { color: #4ade80 !important; }
.text-red { color: #ef4444 !important; }

.regime-history-chart { background: rgba(0, 0, 0, 0.2); padding: 12px; border-radius: 8px; }
.chart-title { font-size: 10px; color: rgba(255, 255, 255, 0.4); margin-bottom: 8px; font-weight: 600; }
.chart-bars-horizontal { display: flex; gap: 2px; height: 24px; }
.regime-bar { flex: 1; border-radius: 4px; transition: all 0.2s; }
.regime-bar.regime-trending { background: rgba(74, 222, 128, 0.6); }
.regime-bar.regime-choppy { background: rgba(239, 68, 68, 0.6); }
.regime-bar:hover { opacity: 1; transform: scaleY(1.2); }

/* Latent Vol Status & Metrics */
.latent-vol-status { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 8px; margin-bottom: 16px; border-left: 3px solid; }
.latent-vol-status.status-normal { background: rgba(74, 222, 128, 0.1); border-left-color: #4ade80; }
.latent-vol-status.status-warning { background: rgba(251, 191, 36, 0.1); border-left-color: #fbbf24; }
.latent-vol-status.status-critical { background: rgba(239, 68, 68, 0.1); border-left-color: #ef4444; }
.status-indicator { width: 10px; height: 10px; border-radius: 50%; animation: pulse 2s infinite; }
.status-indicator.indicator-normal { background: #4ade80; box-shadow: 0 0 8px #4ade80; }
.status-indicator.indicator-critical { background: #ef4444; box-shadow: 0 0 8px #ef4444; }
.status-info { display: flex; flex-direction: column; gap: 2px; }
.status-state { font-size: 11px; font-weight: 700; margin: 0; color: #fff; }
.status-zscore { font-size: 10px; margin: 0; color: rgba(255, 255, 255, 0.6); }

.latent-vol-metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.latent-vol-metrics .metric { background: rgba(0, 0, 0, 0.2); padding: 10px; border-radius: 6px; text-align: center; }

.alert-history-table { border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 12px; }
.alert-history-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; font-size: 10px; padding: 6px; border-bottom: 1px solid rgba(255, 255, 255, 0.02); }
.alert-date { color: rgba(255, 255, 255, 0.5); }
.alert-zscore { color: #fff; font-weight: 600; }
.alert-outcome { text-align: right; }

/* Hero & KPI */
.hero-section { display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 8px; }
.hero-title-row { margin-bottom: 16px; }
.hero-left h1 { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; display: flex; align-items: center; flex-wrap: nowrap; gap: 12px; white-space: nowrap; }
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
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  user-select: none;
  min-width: 280px;
}
.bank-selector:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
.bank-selector.is-open {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
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
  color: rgba(255, 255, 255, 0.95);
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
  color: rgba(255, 255, 255, 0.5);
  font-family: "SF Mono", monospace;
  line-height: 1.2;
  white-space: nowrap;
}
.bank-selector-chevron {
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.6);
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
  min-width: 400px;
}

.bank-dropdown-search {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.bank-dropdown-search svg {
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.4);
  width: 14px;
  height: 14px;
}
.bank-search-input {
  flex: 1;
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
.bank-search-input:focus {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}
.bank-search-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.bank-dropdown-list {
  max-height: 400px;
  overflow-y: auto;
}
.bank-dropdown-list::-webkit-scrollbar {
  width: 6px;
}
.bank-dropdown-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}
.bank-dropdown-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}
.bank-dropdown-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.bank-dropdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.15s;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
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
  color: rgba(255, 255, 255, 0.9);
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
  color: rgba(255, 255, 255, 0.5);
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
.glass-pill { font-size: 12px; padding: 6px 12px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 99px; color: rgba(255,255,255,0.8); display: flex; align-items: center; gap: 6px; backdrop-filter: blur(4px); }
.glass-pill strong { color: #fff; font-weight: 600; }
.risk-aggressive { background: rgba(251, 191, 36, 0.1); border-color: rgba(251, 191, 36, 0.2); color: #fbbf24; }
.status-dot { width: 6px; height: 6px; background: currentColor; border-radius: 50%; box-shadow: 0 0 6px currentColor; }
.hero-actions { display: flex; align-items: center; gap: 16px; }
.last-update { font-size: 12px; color: rgba(255,255,255,0.4); margin-right: 8px; }

/* Buttons */
.btn-glass { height: 36px; padding: 0 16px; border-radius: 10px; font-weight: 600; font-size: 13px; display: flex; align-items: center; justify-content: center; gap: 8px; cursor: pointer; transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1); border: 1px solid transparent; }
.btn-glass.primary { background: rgba(255, 255, 255, 0.9); color: #000; box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2); }
.btn-glass.primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(255, 255, 255, 0.3); }
.btn-glass.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-glass.outline { background: rgba(255, 255, 255, 0.05); color: #fff; border-color: rgba(255, 255, 255, 0.1); }
.btn-glass.outline:hover { background: rgba(255, 255, 255, 0.1); border-color: rgba(255, 255, 255, 0.2); }
.btn-glass.compact { height: 32px; font-size: 11px; padding: 0 12px; }
.spinner { width: 14px; height: 14px; border: 2px solid #000; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* KPI Grid */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.glass-card {
  position: relative;
  overflow: hidden;
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 
    0 20px 40px -10px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
  box-shadow: 
    0 25px 50px -10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}
.glass-card.glow-green::before { content: ""; position: absolute; top: -50px; right: -50px; width: 100px; height: 100px; background: #4ade80; filter: blur(60px); opacity: 0.15; pointer-events: none; }
.glass-card.glow-blue::before { content: ""; position: absolute; top: -50px; right: -50px; width: 100px; height: 100px; background: #3b82f6; filter: blur(60px); opacity: 0.15; pointer-events: none; }
.kpi-header { display: flex; justify-content: space-between; align-items: flex-start; }
.kpi-label { font-size: 11px; text-transform: uppercase; color: rgba(255,255,255,0.5); font-weight: 700; letter-spacing: 0.05em; }
.trend-badge { font-size: 11px; font-weight: 700; padding: 4px 8px; border-radius: 99px; display: flex; align-items: center; gap: 4px; }
.trend-badge.positive { color: #4ade80; background: rgba(74, 222, 128, 0.1); border: 1px solid rgba(74, 222, 128, 0.1); }
.trend-badge.negative { color: #f87171; background: rgba(248, 113, 113, 0.1); border: 1px solid rgba(248, 113, 113, 0.1); }
.kpi-value { font-size: 26px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.1; }
.kpi-value small { font-size: 14px; color: rgba(255,255,255,0.4); font-weight: 500; margin-left: 4px; }
.kpi-sub { font-size: 11px; color: rgba(255,255,255,0.4); }

/* Glass Panel */
.glass-panel {
  background: rgba(20, 22, 28, 0.6);
  backdrop-filter: blur(50px) saturate(200%);
  -webkit-backdrop-filter: blur(50px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  box-shadow: 
    0 30px 60px -15px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.panel-header { padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.02); flex-shrink: 0; }
.panel-header h3 { font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.9); margin: 0; text-transform: uppercase; letter-spacing: 0.05em; }
.panel-subtitle { font-size: 10px; color: rgba(255,255,255,0.4); margin-top: 2px; display: block; }
.panel-header-actions { display: flex; gap: 8px; align-items: center; }
.panel-body { padding: 16px 20px; overflow: hidden; }
.panel-body.p-0 { padding: 0; }
.heatmap-body { min-height: 380px !important; padding: 24px 20px !important; }
.panel-body-optimizer { padding: 16px 20px; flex: 1; display: flex; flex-direction: column; gap: 12px; overflow: hidden; }

/* Optimizer Link Card */
.optimizer-link-card {
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

.optimizer-link-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 16px;
}

.optimizer-link-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #10b981;
}

.optimizer-link-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.optimizer-link-description {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.5;
  margin: 0;
  max-width: 280px;
}

.optimizer-link-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.feature-tag {
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.optimizer-link-btn {
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-decoration: none;
}

.optimizer-link-btn svg {
  transition: transform 0.2s;
}

.optimizer-link-btn:hover svg {
  transform: translateX(4px);
}

/* Search */
.search-sm { position: relative; width: 140px; }
.search-sm svg { position: absolute; left: 8px; top: 50%; transform: translateY(-50%); color: rgba(255,255,255,0.3); }
.input-reset { width: 100%; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 4px 8px 4px 24px; color: #fff; font-size: 11px; outline: none; transition: all 0.2s; }
.input-reset:focus { background: rgba(0,0,0,0.4); border-color: rgba(255,255,255,0.3); }

/* Table */
.table-container { overflow-x: auto; }
.glass-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.glass-table th { text-align: left; padding: 12px 20px; color: rgba(255,255,255,0.4); font-weight: 600; font-size: 10px; text-transform: uppercase; border-bottom: 1px solid rgba(255,255,255,0.05); }
.glass-table tr { transition: background 0.15s; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.02); }
.glass-table tr:last-child { border-bottom: none; }
.glass-table tr:hover { background: rgba(255,255,255,0.04); }
.glass-table tr.active { background: rgba(59, 130, 246, 0.15); box-shadow: inset 3px 0 0 #3b82f6; }
.glass-table td { padding: 12px 20px; color: rgba(255,255,255,0.9); }
.asset-cell { display: flex; align-items: center; gap: 12px; }
.asset-icon { width: 32px; height: 32px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.2); box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
.asset-info { display: flex; flex-direction: column; }
.asset-info .symbol { font-weight: 600; font-size: 13px; color: #fff; }
.asset-info .name { font-size: 10px; color: rgba(255,255,255,0.4); }
.change-pill { font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
.text-muted { color: rgba(255,255,255,0.3); }
.drift-val { font-size: 11px; font-weight: 600; font-family: "SF Mono", monospace; }

/* Heatmap & Treemap */
.heatmap-wrapper { display: flex; flex-direction: column; gap: 8px; padding: 12px; background: rgba(0,0,0,0.15); border-radius: 12px; }
.heatmap-header-row { display: flex; margin-bottom: 12px; gap: 2px; }
.heatmap-empty { width: 50px; }
.heatmap-th { flex: 1; text-align: center; font-size: 11px; color: rgba(255,255,255,0.5); font-weight: 700; padding: 8px 4px; }
.heatmap-row { display: flex; align-items: stretch; gap: 2px; min-height: 48px; }
.heatmap-rh { width: 50px; font-size: 11px; font-weight: 700; color: rgba(255,255,255,0.6); display: flex; align-items: center; justify-content: center; }
.heatmap-cell { flex: 1; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.95); transition: transform 0.2s, box-shadow 0.2s; cursor: pointer; }
.heatmap-cell:hover { transform: scale(1.15); z-index: 10; box-shadow: 0 6px 16px rgba(0,0,0,0.6), inset 0 0 8px rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.3); }
.treemap-tall { display: flex; flex-wrap: wrap; height: 280px; width: 100%; border-radius: 8px; overflow: hidden; }
.treemap-item { display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; border: 1px solid rgba(0,0,0,0.2); color: #fff; transition: filter 0.2s; min-width: 60px; }
.treemap-item:hover { filter: brightness(1.15); z-index: 2; }
.tm-symbol { font-size: 12px; font-weight: 700; }
.tm-val { font-size: 10px; opacity: 0.8; margin-top: 2px; }

/* Inspector & Optimizer */
.inspector-card { flex-shrink: 0; }
.inspector-header-top { display: flex; align-items: center; gap: 10px; flex: 1; }
.asset-lg-icon { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; color: #fff; box-shadow: 0 4px 10px rgba(0,0,0,0.3); flex-shrink: 0; }
.inspector-title h2 { margin: 0; font-size: 16px; color: #fff; line-height: 1.2; }
.inspector-title span { font-size: 10px; color: rgba(255,255,255,0.4); display: block; }
.badge-glass { font-size: 9px; padding: 3px 6px; background: rgba(255,255,255,0.1); border-radius: 4px; color: rgba(255,255,255,0.8); flex-shrink: 0; margin-left: auto; }
.inspector-card .panel-body { display: flex; flex-direction: column; gap: 12px; }
.mini-chart-container { background: rgba(0,0,0,0.2); border-radius: 8px; padding: 8px; border: 1px solid rgba(255,255,255,0.05); min-height: 50px; }
.chart-bars { height: 40px; display: flex; align-items: flex-end; gap: 1px; margin-bottom: 4px; }
.chart-bar { flex: 1; border-radius: 1px 1px 0 0; min-width: 2px; }
.chart-meta { display: flex; justify-content: space-between; font-size: 8px; color: rgba(255,255,255,0.2); }
.chart-meta span.active { color: rgba(255,255,255,0.6); font-weight: 600; }
.inspector-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.metric-cell { background: rgba(255,255,255,0.03); padding: 6px 8px; border-radius: 6px; display: flex; flex-direction: column; justify-content: center; }
.metric-cell label { font-size: 8px; text-transform: uppercase; color: rgba(255,255,255,0.3); margin-bottom: 2px; font-weight: 600; line-height: 1; }
.metric-cell span { font-size: 11px; font-weight: 700; font-family: monospace; color: #fff; line-height: 1; }
.micro-metrics { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; padding: 8px; background: rgba(0,0,0,0.15); border-radius: 6px; }
.micro-metric { display: flex; flex-direction: column; align-items: center; text-align: center; min-height: 50px; justify-content: center; }
.micro-metric .label { font-size: 8px; color: rgba(255,255,255,0.3); font-weight: 600; text-transform: uppercase; margin-bottom: 3px; line-height: 1; }
.micro-metric .value { font-size: 11px; font-weight: 700; color: #fff; line-height: 1; }

/* Controls */
.control-group { display: flex; flex-direction: column; gap: 4px; }
.control-group.compact { gap: 3px; }
.control-group.compact label { font-size: 9px !important; margin-bottom: 1px !important; font-weight: 600; color: rgba(255,255,255,0.7); }
.custom-select { position: relative; }
.custom-select select { width: 100%; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 6px 10px; color: #fff; font-size: 11px; appearance: none; outline: none; }
.custom-select .chevron { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); pointer-events: none; opacity: 0.5; }
.range-inputs-row { display: flex; align-items: center; gap: 6px; }
.glass-input-wrapper { flex: 1; display: flex; align-items: center; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 0 6px; height: 28px; transition: all 0.2s; }
.glass-input-wrapper:focus-within { background: rgba(0,0,0,0.35); border-color: rgba(255,255,255,0.3); box-shadow: 0 0 0 2px rgba(255,255,255,0.05); }
.glass-input-wrapper input { width: 100%; background: transparent !important; border: none !important; box-shadow: none !important; color: #fff; text-align: right; padding: 0; margin-right: 3px; font-family: "SF Mono", monospace; outline: none; font-size: 11px; height: 100%; }
.glass-input-wrapper span { font-size: 11px; color: rgba(255,255,255,0.3); font-weight: 500; }
.dash { color: rgba(255,255,255,0.15); font-weight: 600; font-size: 11px; }
.flex-spacer { flex: 1; min-height: 4px; }
.ios-slider-sm { -webkit-appearance: none; width: 100%; height: 2px; background: rgba(255,255,255,0.15); border-radius: 2px; outline: none; }
.ios-slider-sm::-webkit-slider-thumb { -webkit-appearance: none; width: 14px; height: 14px; background: #fff; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.3); cursor: grab; margin-top: -6px; border: 0.5px solid rgba(0,0,0,0.1); }
.toggle-row { display: flex !important; flex-direction: row !important; justify-content: space-between !important; align-items: center !important; min-height: 28px; width: 100%; }
.ios-toggle-sm { position: relative; display: inline-block; width: 28px; height: 16px; }
.ios-toggle-sm input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(255,255,255,0.1); border-radius: 20px; transition: .3s; }
.slider:before { position: absolute; content: ""; height: 12px; width: 12px; left: 2px; bottom: 2px; background-color: white; border-radius: 50%; transition: .3s; box-shadow: 0 1px 3px rgba(0,0,0,0.3); }
input:checked + .slider { background-color: #34c759; }
input:checked + .slider:before { transform: translateX(12px); }

/* Metrics Tabs */
.combined-metrics { 
  display: flex; 
  flex-direction: column; 
  height: 100%; 
  min-height: 0;
  flex: 1;
}
.combined-tabs { display: flex; gap: 0; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 0 20px; flex-shrink: 0; }
.tab-button { flex: 1; padding: 12px 16px; background: transparent; border: none; color: rgba(255,255,255,0.4); font-size: 11px; font-weight: 600; text-transform: uppercase; cursor: pointer; position: relative; transition: color 0.2s; }
.tab-button:hover { color: rgba(255,255,255,0.6); }
.tab-button.active { color: rgba(255,255,255,0.9); }
.tab-button.active::after { content: ''; position: absolute; bottom: -1px; left: 0; right: 0; height: 2px; background: #3b82f6; }
.tab-content { padding: 16px 20px; display: flex; flex-direction: column; gap: 8px; flex: 1; min-height: 0; }
.combined-metrics .tab-content { overflow-y: auto; }
.metric-row { display: flex; justify-content: space-between; align-items: center; padding: 8px; background: rgba(0,0,0,0.15); border-radius: 6px; border-left: 2px solid rgba(255,255,255,0.1); }
.metric-label { display: flex; flex-direction: column; gap: 1px; }
.metric-label span:first-child { font-size: 10px; font-weight: 600; color: rgba(255,255,255,0.85); line-height: 1.2; }
.meta-hint { font-size: 8px !important; color: rgba(255,255,255,0.25) !important; font-weight: 400 !important; }
.metric-value { font-size: 11px; font-weight: 700; font-family: monospace; white-space: nowrap; }
.stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.stat-item { display: flex; flex-direction: column; align-items: center; padding: 10px; background: rgba(0,0,0,0.15); border-radius: 6px; text-align: center; min-height: 50px; justify-content: center; }
.stat-label { font-size: 9px; color: rgba(255,255,255,0.3); font-weight: 600; text-transform: uppercase; margin-bottom: 4px; line-height: 1.2; }
.stat-value { font-size: 13px; font-weight: 700; font-family: monospace; color: #fff; line-height: 1; }
.btn-icon-xs { width: 22px; height: 22px; padding: 0; border: none; background: rgba(255,255,255,0.05); color: #fff; cursor: pointer; border-radius: 4px; font-size: 11px; transition: all 0.2s; display: flex; align-items: center; justify-content: center; }
.btn-icon-xs:hover { background: rgba(255,255,255,0.1); }
.spinner-sm { width: 10px; height: 10px; border: 1.5px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite; }

/* Regime Info Box */
.regime-info-box { padding: 12px; border-radius: 8px; margin-bottom: 12px; border-left: 3px solid; }
.regime-info-box.regime-trending { background: rgba(74, 222, 128, 0.1); border-left-color: #4ade80; }
.regime-info-box.regime-choppy { background: rgba(239, 68, 68, 0.1); border-left-color: #ef4444; }
.regime-info-label { font-size: 9px; color: rgba(255, 255, 255, 0.4); text-transform: uppercase; margin: 0 0 4px 0; }
.regime-info-value { font-size: 13px; font-weight: 700; color: #fff; margin: 0 0 2px 0; }
.regime-info-sub { font-size: 10px; color: rgba(255, 255, 255, 0.5); margin: 0; }

/* Tournament */
.tournament-mini { display: flex; flex-direction: column; gap: 8px; }
.tournament-row { display: grid; grid-template-columns: 20px 1fr 50px; align-items: center; padding: 8px; background: rgba(0, 0, 0, 0.2); border-radius: 6px; gap: 8px; font-size: 10px; }
.tournament-rank { font-weight: 700; color: rgba(255, 255, 255, 0.6); }
.tournament-name { color: #fff; font-weight: 500; }
.tournament-sharpe { text-align: right; color: #60a5fa; font-weight: 700; }

/* Toast */
.toast-notification { position: fixed; bottom: 24px; right: 24px; padding: 14px 20px; border-radius: 12px; font-size: 13px; font-weight: 600; max-width: 320px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); z-index: 1000; backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); }
.toast-success { background: rgba(74, 222, 128, 0.2); color: #4ade80; border-color: rgba(74, 222, 128, 0.3); }
.toast-error { background: rgba(248, 113, 113, 0.2); color: #f87171; border-color: rgba(248, 113, 113, 0.3); }
.toast-info { background: rgba(96, 165, 250, 0.2); color: #60a5fa; border-color: rgba(96, 165, 250, 0.3); }

/* 3D Correlation Heatmap Tooltip */
.asset-tooltip-3d {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 16px;
  min-width: 240px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  z-index: 100;
  animation: fadeIn 0.2s ease-out;
  pointer-events: none;
}

.tooltip-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.asset-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  color: #fff;
  flex-shrink: 0;
}

.tooltip-symbol {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 2px;
}

.tooltip-name {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.3;
}

.tooltip-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.tooltip-row span {
  color: rgba(255, 255, 255, 0.6);
}

.tooltip-row strong {
  color: #fff;
  font-weight: 600;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Utilities */
.text-right { text-align: right; }
.text-gradient-green { background: linear-gradient(to right, #4ade80, #22c55e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-gradient-blue { background: linear-gradient(to right, #60a5fa, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-white { color: #fff; }
.mono { font-family: "SF Mono", monospace; }
.opacity-50 { opacity: 0.5; }
.opacity-80 { opacity: 0.8; }
.font-bold { font-weight: 700; }
.w-full { width: 100%; }
.mt-3 { margin-top: 12px; }
.mb-1 { margin-bottom: 4px; }
.flex { display: flex; }
.flex-center { display: flex; align-items: center; gap: 4px; }
.justify-between { justify-content: space-between; }
.val-highlight { color: #3b82f6; font-weight: 600; font-size: 9px; }

/* Modal */
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
  align-items: flex-start;
  justify-content: center;
  padding: 20px;
  padding-top: 80px;
  overflow: hidden;
}

.modal-container {
  background: rgba(20, 22, 28, 0.95);
  backdrop-filter: blur(50px) saturate(200%);
  -webkit-backdrop-filter: blur(50px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  box-shadow: 
    0 30px 60px -15px rgba(0, 0, 0, 0.8),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
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
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.modal-search svg {
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.4);
}

.modal-search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 13px;
  outline: none;
  font-family: inherit;
}

.modal-search-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.modal-table-container {
  flex: 1;
  overflow-y: auto;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.2);
}

.modal-table {
  width: 100%;
}

.modal-table tbody tr {
  cursor: pointer;
}

.modal-footer {
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.modal-stats {
  display: flex;
  gap: 24px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.modal-stats strong {
  color: rgba(255, 255, 255, 0.9);
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
@media (max-width: 1400px) { 
  .dashboard-grid { grid-template-columns: 1fr; } 
  .heatmap-metrics-row { grid-template-columns: 1fr; }
}

@media (max-width: 1024px) { 
  .kpi-grid { grid-template-columns: repeat(2, 1fr); } 
  .stats-grid { grid-template-columns: 1fr 1fr; } 
  .charts-row-two-col { grid-template-columns: 1fr; } 
  .heatmap-metrics-row { grid-template-columns: 1fr; }
  .portfolio-page {
    padding: 16px 20px;
  }
}

@media (max-width: 1024px) {
  .portfolio-page {
    padding: 20px;
  }
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .col-side-flex {
    width: 100%;
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
  .dashboard-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .charts-row-two-col {
    grid-template-columns: 1fr;
  }
  .chart-container {
    height: 300px;
  }
  .chart-container.tall {
    height: 400px;
  }
  .glass-panel {
    border-radius: 16px;
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
  /* Wave metrics */
  .wave-metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .latent-vol-metrics {
    grid-template-columns: repeat(2, 1fr);
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
  .chart-container {
    height: 250px;
  }
  .chart-container.tall {
    height: 300px;
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
    border-radius: 12px;
  }
  .panel-header {
    padding: 10px 12px;
  }
  .panel-body {
    padding: 10px 12px;
  }
  .wave-metrics-row {
    grid-template-columns: 1fr;
  }
  .latent-vol-metrics {
    grid-template-columns: 1fr;
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