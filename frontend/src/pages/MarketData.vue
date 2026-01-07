<!-- src/pages/MarketData.vue -->
<template>
  <div class="market-data-page">
    
    <!-- Left Sidebar -->
    <aside class="market-sidebar">
      <!-- Logo/Title -->
      <div class="sidebar-header">
        <h1 class="sidebar-title">ТЕРМИНАЛ</h1>
        <p class="sidebar-subtitle">Потоковые данные в режиме реального времени</p>
        <router-link to="/" class="back-to-dashboard">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          <span>На Главную</span>
        </router-link>
      </div>

      <!-- Navigation Buttons -->
      <nav class="sidebar-nav">
        <!-- Markets link - navigates to separate page -->
        <router-link
          to="/markets"
          class="nav-btn nav-link"
        >
          РЫНКИ
          <span class="nav-external-icon">↗</span>
        </router-link>
        
        <!-- Tab buttons -->
        <button
          v-for="tab in sidebarNavItems"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="nav-btn"
          :class="{ active: activeTab === tab.id }"
        >
          {{ tab.label }}
        </button>
      </nav>

      <!-- Live Status -->
      <div class="sidebar-status">
        <div class="status-indicator">
          <span class="status-dot pulse"></span>
          <span class="status-text">LIVE</span>
        </div>
        <div class="status-time">{{ currentTime }}</div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="market-main">
      <!-- Main Grid Layout -->
      <div class="main-grid">
        
        <!-- Left: Regional Markets Grid -->
        <div class="markets-panel">
          
          <!-- Markets Overview Block -->
          <div class="markets-overview-block">
            <div class="markets-overview-header">
              <span class="markets-overview-title">Обзор рынков</span>
              <span class="markets-overview-update">обновлено: {{ marketsUpdateTime }}</span>
            </div>
            <div class="markets-overview-content">
              <table class="markets-table">
                <thead>
                  <tr>
                    <th v-for="region in allRegions" :key="region.id">{{ region.name }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="rowIndex in maxDataRows" :key="rowIndex">
                    <td v-for="region in allRegions" :key="region.id + '-' + rowIndex">
                      <template v-if="region.data[rowIndex - 1]">
                        <span class="index-name">{{ region.data[rowIndex - 1].index }}</span>
                        <span class="data-value">{{ region.data[rowIndex - 1].value }}</span>
                        <span class="data-change" :class="region.data[rowIndex - 1].change >= 0 ? 'positive' : 'negative'">
                          {{ region.data[rowIndex - 1].change >= 0 ? '+' : '' }}{{ region.data[rowIndex - 1].change.toFixed(2) }}%
                        </span>
                      </template>
                      <template v-else>
                        <span class="data-empty">—</span>
                      </template>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Index Charts Row -->
          <div class="index-charts-row">
            <!-- IMOEX Chart -->
            <div class="index-chart-block">
              <div class="index-chart-header">
                <div class="index-chart-title">
                  <span class="index-chart-name">IMOEX</span>
                  <span class="index-chart-freq">обновление: 2 сек</span>
                </div>
                <span class="index-chart-value" :class="imoexChange >= 0 ? 'positive' : 'negative'">
                  {{ imoexChange >= 0 ? '+' : '' }}{{ imoexChange.toFixed(2) }}%
                </span>
              </div>
              <div class="index-chart-container">
                <svg class="index-chart-svg" viewBox="0 0 200 200" preserveAspectRatio="none">
                  <defs>
                    <linearGradient :id="'imoex-gradient'" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" :stop-color="imoexChange >= 0 ? 'rgba(0, 255, 136, 0.3)' : 'rgba(255, 51, 102, 0.3)'"/>
                      <stop offset="100%" stop-color="transparent"/>
                    </linearGradient>
                  </defs>
                  <path :d="imoexAreaPath" :fill="'url(#imoex-gradient)'" />
                  <path :d="imoexLinePath" fill="none" :stroke="imoexChange >= 0 ? '#00ff88' : '#ff3366'" stroke-width="2"/>
                </svg>
              </div>
            </div>

            <!-- RTS Chart -->
            <div class="index-chart-block">
              <div class="index-chart-header">
                <div class="index-chart-title">
                  <span class="index-chart-name">RTS</span>
                  <span class="index-chart-freq">обновление: 2 сек</span>
                </div>
                <span class="index-chart-value" :class="rtsChange >= 0 ? 'positive' : 'negative'">
                  {{ rtsChange >= 0 ? '+' : '' }}{{ rtsChange.toFixed(2) }}%
                </span>
              </div>
              <div class="index-chart-container">
                <svg class="index-chart-svg" viewBox="0 0 200 200" preserveAspectRatio="none">
                  <defs>
                    <linearGradient :id="'rts-gradient'" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" :stop-color="rtsChange >= 0 ? 'rgba(0, 255, 136, 0.3)' : 'rgba(255, 51, 102, 0.3)'"/>
                      <stop offset="100%" stop-color="transparent"/>
                    </linearGradient>
                  </defs>
                  <path :d="rtsAreaPath" :fill="'url(#rts-gradient)'" />
                  <path :d="rtsLinePath" fill="none" :stroke="rtsChange >= 0 ? '#00ff88' : '#ff3366'" stroke-width="2"/>
                </svg>
              </div>
            </div>
          </div>

          <!-- News Section -->
          <div class="news-block">
            <div class="news-block-header">Новости</div>
            <div class="news-carousel">
              <TransitionGroup name="news-list" tag="div" class="news-carousel-inner">
                <div 
                  v-for="news in currentNewsGroup" 
                  :key="news.text"
                  class="news-item-row"
                >
                  <span class="news-region">{{ news.region }}</span>
                  <p class="news-text">{{ news.text }}</p>
                </div>
              </TransitionGroup>
            </div>
          </div>
        </div>

        <!-- Right: AI Insights -->
        <div class="insights-panel">
          <!-- Sparkline Charts: VIX, BRENT, Gold -->
          <div class="sparkline-block">
            <div class="sparkline-header">
              <span class="sparkline-title">Индикаторы</span>
              <span class="sparkline-update">обновление: 3 сек</span>
            </div>
            <div class="sparkline-content">
              <!-- VIX -->
              <div class="sparkline-item">
                <div class="sparkline-info">
                  <span class="sparkline-name">VIX</span>
                  <span class="sparkline-value">{{ vixData.value.toFixed(2) }}</span>
                  <span class="sparkline-change" :class="vixData.change >= 0 ? 'positive' : 'negative'">
                    {{ vixData.change >= 0 ? '+' : '' }}{{ vixData.change.toFixed(2) }}%
                  </span>
                </div>
                <div class="sparkline-chart">
                  <svg viewBox="0 0 100 30" preserveAspectRatio="none" class="sparkline-svg">
                    <path :d="vixSparklinePath" fill="none" stroke="rgba(255, 255, 255, 0.9)" stroke-width="1.5"/>
                  </svg>
                </div>
              </div>
              <!-- URALS -->
              <div class="sparkline-item">
                <div class="sparkline-info">
                  <span class="sparkline-name">URALS</span>
                  <span class="sparkline-value">${{ uralsData.value.toFixed(2) }}</span>
                  <span class="sparkline-change" :class="uralsData.change >= 0 ? 'positive' : 'negative'">
                    {{ uralsData.change >= 0 ? '+' : '' }}{{ uralsData.change.toFixed(2) }}%
                  </span>
                </div>
                <div class="sparkline-chart">
                  <svg viewBox="0 0 100 30" preserveAspectRatio="none" class="sparkline-svg">
                    <path :d="uralsSparklinePath" fill="none" stroke="rgba(255, 255, 255, 0.9)" stroke-width="1.5"/>
                  </svg>
                </div>
              </div>
              <!-- Gold -->
              <div class="sparkline-item">
                <div class="sparkline-info">
                  <span class="sparkline-name">ЗОЛОТО</span>
                  <span class="sparkline-value">${{ goldData.value.toFixed(2) }}</span>
                  <span class="sparkline-change" :class="goldData.change >= 0 ? 'positive' : 'negative'">
                    {{ goldData.change >= 0 ? '+' : '' }}{{ goldData.change.toFixed(2) }}%
                  </span>
                </div>
                <div class="sparkline-chart">
                  <svg viewBox="0 0 100 30" preserveAspectRatio="none" class="sparkline-svg">
                    <path :d="goldSparklinePath" fill="none" stroke="rgba(255, 255, 255, 0.9)" stroke-width="1.5"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- AI Аналитика -->
          <div class="ai-insights-block">
            <div class="ai-insights-header">
              <span class="ai-insights-title">AI Аналитика</span>
            </div>
            <div class="ai-insights-content">
              <div class="ai-signals">
                <div class="ai-signal-item" v-for="(insight, idx) in aiInsights" :key="idx">
                  <span class="ai-signal-icon" :class="insight.type">{{ insight.type === 'buy' ? '▲' : '▼' }}</span>
                  <span class="ai-signal-action" :class="insight.type">{{ insight.action }}</span>
                  <span class="ai-signal-symbol">{{ insight.symbol }}</span>
                  <span class="ai-signal-value" :class="insight.type">{{ insight.value }}</span>
                </div>
              </div>
              <div class="ai-section">
                <div class="ai-section-title">
                  <span class="section-title-icon">◈</span>
                  Оповещения
                  <span class="alerts-count">{{ alerts.length }}</span>
                </div>
                <div class="ai-alerts">
                  <div 
                    class="alert-item" 
                    v-for="(alert, idx) in alerts" 
                    :key="idx"
                    :class="getAlertType(alert.text)"
                  >
                    <div class="alert-icon-wrapper">
                      <span class="alert-icon">{{ getAlertIcon(alert.text) }}</span>
                      <span class="alert-pulse"></span>
                    </div>
                    <div class="alert-content">
                      <span class="alert-text">{{ alert.text }}</span>
                      <span class="alert-time">{{ getAlertTime(idx) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Signal Matrix Block -->
          <div class="signal-matrix-block">
            <div class="signal-matrix-header">
              <span class="signal-matrix-title">SIGNAL MATRIX</span>
              <span class="signal-matrix-update">●</span>
            </div>
            <div class="signal-matrix-content">
              <div class="signal-matrix-grid">
                <div 
                  v-for="(row, rowIdx) in signalMatrix" 
                  :key="rowIdx" 
                  class="signal-matrix-row"
                >
                  <div 
                    v-for="(cell, colIdx) in row" 
                    :key="colIdx" 
                    class="signal-matrix-cell"
                    :style="{ backgroundColor: getSignalColor(cell) }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </main>
  </div>

  <!-- Legacy content hidden -->
  <div style="display: none;">
      <div class="content-area">
        
        <!-- Tab: Акции / Индексы / Облигации / Форекс -->
        <section v-if="activeTab !== 'news'" class="instruments-section">
          
          <!-- Indices Cards (if tab is indices) -->
          <div v-if="activeTab === 'indices'" class="indices-grid">
            <article
              v-for="index in getCurrentIndices()"
              :key="index.symbol"
              class="index-card"
              :data-symbol="index.symbol"
              @click="openAssetDetail(index)"
            >
              <header class="card-header">
                <h3 class="card-title">{{ index.symbol }}</h3>
                <span class="card-badge" :class="index.change >= 0 ? 'positive' : 'negative'">
                  {{ index.change >= 0 ? '+' : '' }}{{ index.change.toFixed(2) }}%
                </span>
              </header>
              <div class="card-body">
                <div class="card-value">{{ formatPrice(index.price) }}</div>
                <div class="card-name">{{ index.name }}</div>
              </div>
            </article>
          </div>

          <!-- Instruments Cards Grid -->
          <div v-else class="instruments-grid">
            <article
              v-for="instrument in getFilteredInstruments()"
              :key="instrument.symbol"
              class="instrument-card"
              :data-symbol="instrument.symbol"
              :data-market="activeMarket"
              @click="openAssetDetail(instrument)"
            >
              <header class="card-header">
                <h3 class="card-title">{{ instrument.symbol }}</h3>
                <span class="card-badge" :class="instrument.change >= 0 ? 'positive' : 'negative'">
                  {{ instrument.change >= 0 ? '+' : '' }}{{ instrument.change.toFixed(2) }}%
                </span>
              </header>
              <div class="card-body">
                <div class="card-price">{{ formatPrice(instrument.price) }}</div>
                <div class="card-name">{{ instrument.name }}</div>
                <div class="card-quotes">
                  <span class="quote-item">
                    <span class="quote-label">Bid:</span>
                    <span class="quote-value">{{ formatPrice((instrument as any).bid || instrument.price * 0.9995) }}</span>
                  </span>
                  <span class="quote-item">
                    <span class="quote-label">Ask:</span>
                    <span class="quote-value">{{ formatPrice((instrument as any).ask || instrument.price * 1.0005) }}</span>
                  </span>
                </div>
              </div>
            </article>
          </div>

          <!-- Data Table (Full Width) -->
          <div class="data-table-section">
            <header class="table-header">
              <h2 class="table-title">{{ getTabTitle() }}</h2>
            </header>
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th @click="sortTable('symbol')" class="sortable">
                      SYMBOL
                      <span v-if="sortColumn === 'symbol'" class="sort-icon">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                    </th>
                    <th @click="sortTable('bid')" class="sortable">
                      BID
                      <span v-if="sortColumn === 'bid'" class="sort-icon">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                    </th>
                    <th @click="sortTable('ask')" class="sortable">
                      ASK
                      <span v-if="sortColumn === 'ask'" class="sort-icon">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                    </th>
                    <th @click="sortTable('price')" class="sortable">
                      LAST PRICE
                      <span v-if="sortColumn === 'price'" class="sort-icon">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                    </th>
                    <th @click="sortTable('change')" class="sortable">
                      CHANGE
                      <span v-if="sortColumn === 'change'" class="sort-icon">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                    </th>
                    <th @click="sortTable('changePercent')" class="sortable">
                      %CHANGE
                      <span v-if="sortColumn === 'changePercent'" class="sort-icon">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="item in getSortedData()"
                    :key="item.symbol"
                    class="table-row"
                    :data-symbol="item.symbol"
                    @click="openAssetDetail(item)"
                  >
                    <td class="cell-symbol">
                      <strong>{{ item.symbol }}</strong>
                      <span class="cell-name">{{ item.name }}</span>
                    </td>
                    <td class="cell-bid">{{ formatPrice((item as any).bid || item.price * 0.9995) }}</td>
                    <td class="cell-ask">{{ formatPrice((item as any).ask || item.price * 1.0005) }}</td>
                    <td class="cell-price">{{ formatPrice(item.price) }}</td>
                    <td class="cell-change" :class="item.change >= 0 ? 'positive' : 'negative'">
                      {{ item.change >= 0 ? '+' : '' }}{{ formatChange(item.change) }}
                    </td>
                    <td class="cell-pchange" :class="item.change >= 0 ? 'positive' : 'negative'">
                      {{ item.change >= 0 ? '+' : '' }}{{ item.change.toFixed(2) }}%
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 3D Surfaces Section (Integrated) -->
          <section class="surfaces-section">
            <header class="section-header">
              <h2 class="section-title">3D Analytics</h2>
            </header>
            <div class="surfaces-grid">
              <div class="surface-card">
                <div class="surface-header">
                  <span>3D LIQUIDITY SURFACE</span>
                </div>
                <canvas class="surface-canvas"></canvas>
              </div>
              <div class="surface-card">
                <div class="surface-header">
                  <span>CHARTS</span>
                </div>
                <div class="charts-container">
                  <div
                    v-for="(chart, i) in selectedCharts"
                    :key="i"
                    class="chart-card"
                  >
                    <div class="chart-header">
                      <span>{{ chart.symbol }} {{ getStockName(chart.symbol) }}</span>
                    </div>
                    <canvas
                      :ref="el => {
                        if (el && 'tagName' in el && el.tagName === 'CANVAS') {
                          chartRefs[chart.symbol] = el as HTMLCanvasElement
                        }
                      }"
                      class="chart-canvas"
                      :data-symbol="chart.symbol"
                    ></canvas>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </section>

        <!-- Tab: Новости (2 колонны) -->
        <section v-if="activeTab === 'news'" class="news-section">
          <div class="news-grid">
            <!-- Left Column: Corporate News -->
            <div class="news-column">
              <header class="news-column-header">
                <h2 class="news-column-title">Корпоративные новости</h2>
              </header>
              <div class="news-list">
                <article
                  v-for="(news, i) in corporateNews"
                  :key="i"
                  class="news-card"
                  :data-sentiment="news.sentiment"
                >
                  <header class="news-card-header">
                    <h3 class="news-title">{{ news.title }}</h3>
                    <span class="sentiment-badge" :class="news.sentiment">
                      {{ getSentimentLabel(news.sentiment) }}
                    </span>
                  </header>
                  <p class="news-description">{{ news.description }}</p>
                  <footer class="news-footer">
                    <span class="news-time">{{ news.time }}</span>
                    <span class="news-source">{{ news.source }}</span>
                  </footer>
                </article>
              </div>
            </div>

            <!-- Right Column: Macro News -->
            <div class="news-column">
              <header class="news-column-header">
                <h2 class="news-column-title">Макроэкономические новости</h2>
              </header>
              <div class="news-list">
                <article
                  v-for="(news, i) in macroNews"
                  :key="i"
                  class="news-card"
                  :data-sentiment="news.sentiment"
                >
                  <header class="news-card-header">
                    <h3 class="news-title">{{ news.title }}</h3>
                    <span class="sentiment-badge" :class="news.sentiment">
                      {{ getSentimentLabel(news.sentiment) }}
                    </span>
                  </header>
                  <p class="news-description">{{ news.description }}</p>
                  <footer class="news-footer">
                    <span class="news-time">{{ news.time }}</span>
                    <span class="news-source">{{ news.source }}</span>
                  </footer>
                </article>
              </div>
            </div>
          </div>
        </section>
      </div>
    <!-- Legacy main end -->


    <!-- Tabs Navigation -->
    <div class="tabs-navigation-market">
      <button
        v-for="tab in legacyTabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="tab-item-market"
        :class="{ active: activeTab === tab.id }"
      >
        <span class="tab-label-market">{{ tab.name }}</span>
      </button>
    </div>

    <!-- Tab Content: Обзор рынка -->
    <div v-show="activeTab === 'overview'" class="tab-content-market">
      <!-- Main Grid -->
      <div class="dashboard-grid">
      
      <!-- Left Column: Major Indices -->
      <div class="col-left">
        
        <!-- Major Indices -->
        <div class="glass-card">
          <div class="card-header">
            <h3>Основные индексы</h3>
            <span class="badge-live">Live</span>
          </div>
          <div class="indices-list">
            <div 
              v-for="index in majorIndices" 
              :key="index.symbol" 
              class="index-item"
              @click="openAssetDetail({ symbol: index.symbol, name: index.name, price: index.price, change: index.change, volume: index.volume, type: 'index' })"
              style="cursor: pointer;"
            >
              <div class="index-left">
                <div class="index-symbol">{{ index.symbol }}</div>
                <div class="index-name">{{ index.name }}</div>
              </div>
              <div class="index-right">
                <div class="index-price">{{ formatPrice(index.price) }}</div>
                <div class="index-change" :class="index.change >= 0 ? 'text-green' : 'text-red'">
                  <span>{{ index.change >= 0 ? '+' : '' }}{{ index.change.toFixed(2) }}%</span>
                  <span class="index-volume">Vol: {{ formatVolume(index.volume) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Currency Pairs -->
        <div class="glass-card">
          <div class="card-header">
            <h3>Валютные пары</h3>
          </div>
          <div class="currency-grid">
            <div 
              v-for="pair in currencyPairs" 
              :key="pair.symbol" 
              class="currency-item"
              @click="openAssetDetail({ symbol: pair.symbol, name: pair.symbol, price: parseFloat(pair.price.replace(',', '.')), change: pair.change, type: 'currency' })"
              style="cursor: pointer;"
            >
              <div class="currency-symbol">{{ pair.symbol }}</div>
              <div class="currency-price">{{ pair.price }}</div>
              <div class="currency-change" :class="pair.change >= 0 ? 'text-green' : 'text-red'">
                {{ pair.change >= 0 ? '+' : '' }}{{ pair.change.toFixed(3) }}%
              </div>
            </div>
          </div>
        </div>

        <!-- Commodities -->
        <div class="glass-card">
          <div class="card-header">
            <h3>Сырьевые товары</h3>
          </div>
          <div class="commodities-list">
            <div 
              v-for="commodity in commodities" 
              :key="commodity.symbol" 
              class="commodity-item"
              @click="openAssetDetail({ symbol: commodity.symbol, name: commodity.name, price: commodity.price, change: commodity.change, type: 'commodity' })"
              style="cursor: pointer;"
            >
              <div class="commodity-left">
                <div class="commodity-symbol">{{ commodity.symbol }}</div>
                <div class="commodity-name">{{ commodity.name }}</div>
              </div>
              <div class="commodity-right">
                <div class="commodity-price">{{ formatPrice(commodity.price) }}</div>
                <div class="commodity-change" :class="commodity.change >= 0 ? 'text-green' : 'text-red'">
                  {{ commodity.change >= 0 ? '+' : '' }}{{ commodity.change.toFixed(2) }}%
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Right Column: Stocks & Bonds -->
      <div class="col-right">
        
        <!-- Market Statistics -->
        <div class="glass-card">
          <div class="card-header">
            <h3>Рыночная статистика</h3>
          </div>
          <div class="stats-grid-overview">
            <div class="stat-item-overview">
              <div class="stat-label-overview">RVI Index</div>
              <div class="stat-value-overview" :class="marketStats.rvi >= 20 ? 'text-red' : 'text-green'">
                {{ marketStats.rvi.toFixed(2) }}
              </div>
              <div class="stat-change-overview" :class="marketStats.rviChange >= 0 ? 'text-red' : 'text-green'">
                {{ marketStats.rviChange >= 0 ? '+' : '' }}{{ marketStats.rviChange.toFixed(2) }}
              </div>
            </div>
            <div class="stat-item-overview">
              <div class="stat-label-overview">Капитализация</div>
              <div class="stat-value-overview">{{ formatCurrency(marketStats.totalMarketCap) }}</div>
              <div class="stat-change-overview" :class="marketStats.marketCapChange >= 0 ? 'text-green' : 'text-red'">
                {{ marketStats.marketCapChange >= 0 ? '+' : '' }}{{ marketStats.marketCapChange.toFixed(2) }}%
              </div>
            </div>
            <div class="stat-item-overview">
              <div class="stat-label-overview">Растущие / Падающие</div>
              <div class="stat-value-overview">{{ marketStats.advancing }} / {{ marketStats.declining }}</div>
              <div class="stat-change-overview text-muted">Ratio: {{ (marketStats.advancing / marketStats.declining).toFixed(2) }}</div>
            </div>
            <div class="stat-item-overview">
              <div class="stat-label-overview">Новые максимумы / минимумы</div>
              <div class="stat-value-overview">{{ marketStats.newHighs }} / {{ marketStats.newLows }}</div>
              <div class="stat-change-overview text-muted">52 недели</div>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>

    <!-- Tab Content: Акции -->
    <div v-show="activeTab === 'stocks'" class="tab-content-market">
      <div class="dashboard-grid">
        <!-- Top Stocks -->
        <div class="glass-card full-width">
          <div class="card-header">
            <h3>Топ акций российского рынка</h3>
            <span class="badge-live">Live</span>
          </div>
          <div class="stocks-table">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Тикер</th>
                  <th>Цена</th>
                  <th>Изменение</th>
                  <th>Объем</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="stock in topStocks" 
                  :key="stock.symbol" 
                  class="stock-row"
                  @click="openAssetDetail({ symbol: stock.symbol, name: stock.name, price: stock.price, change: stock.change, volume: stock.volume, type: 'stock' })"
                  style="cursor: pointer;"
                >
                  <td class="stock-symbol">
                    <div style="font-weight: 700;">{{ stock.symbol }}</div>
                    <div style="font-size: 10px; color: rgba(255,255,255,0.5);">{{ stock.name }}</div>
                  </td>
                  <td class="stock-price">{{ formatPrice(stock.price) }} ₽</td>
                  <td class="stock-change" :class="stock.change >= 0 ? 'text-green' : 'text-red'">
                    {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
                  </td>
                  <td class="stock-volume">{{ formatVolume(stock.volume) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab Content: Облигации -->
    <div v-show="activeTab === 'bonds'" class="tab-content-market">
      <div class="dashboard-grid">
        <!-- Government Bonds -->
        <div class="glass-card">
          <div class="card-header">
            <h3>ОФЗ (Облигации федерального займа)</h3>
            <span class="badge-live">Live</span>
          </div>
          <div class="bonds-list">
            <div 
              v-for="bond in governmentBonds" 
              :key="bond.symbol" 
              class="bond-item"
              @click="openAssetDetail({ symbol: bond.symbol, name: bond.symbol, price: 100, change: bond.change, type: 'bond', yield: bond.yield })"
              style="cursor: pointer;"
            >
              <div class="bond-left">
                <div class="bond-symbol">{{ bond.symbol }}</div>
                <div class="bond-maturity">{{ bond.maturity }}</div>
              </div>
              <div class="bond-right">
                <div class="bond-yield">{{ bond.yield }}%</div>
                <div class="bond-change" :class="bond.change >= 0 ? 'text-red' : 'text-green'">
                  {{ bond.change >= 0 ? '+' : '' }}{{ bond.change.toFixed(2) }} б.п.
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Corporate Bonds -->
        <div class="glass-card">
          <div class="card-header">
            <h3>Корпоративные облигации</h3>
          </div>
          <div class="bonds-list">
            <div 
              v-for="bond in corporateBonds" 
              :key="bond.symbol" 
              class="bond-item"
              @click="openAssetDetail({ symbol: bond.symbol, name: bond.symbol, price: 100, change: bond.change, type: 'bond', yield: bond.yield })"
              style="cursor: pointer;"
            >
              <div class="bond-left">
                <div class="bond-symbol">{{ bond.symbol }}</div>
                <div class="bond-maturity">{{ bond.maturity }}</div>
              </div>
              <div class="bond-right">
                <div class="bond-yield">{{ bond.yield }}%</div>
                <div class="bond-change" :class="bond.change >= 0 ? 'text-red' : 'text-green'">
                  {{ bond.change >= 0 ? '+' : '' }}{{ bond.change.toFixed(2) }} б.п.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab Content: ПИФы -->
    <div v-show="activeTab === 'funds'" class="tab-content-market">
      <div class="dashboard-grid">
        <div class="glass-card full-width">
          <div class="card-header">
            <h3>Паевые инвестиционные фонды (ПИФы)</h3>
            <span class="badge-live">Live</span>
          </div>
          <div class="funds-table">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Название фонда</th>
                  <th>Стоимость пая</th>
                  <th>Изменение</th>
                  <th>Доходность (год)</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="fund in pifs" 
                  :key="fund.name" 
                  class="stock-row"
                  @click="openAssetDetail({ symbol: fund.name, name: fund.name, price: fund.price, change: fund.change, type: 'fund', yield: fund.yield })"
                  style="cursor: pointer;"
                >
                  <td class="stock-symbol">{{ fund.name }}</td>
                  <td class="stock-price">{{ formatPrice(fund.price) }} ₽</td>
                  <td class="stock-change" :class="fund.change >= 0 ? 'text-green' : 'text-red'">
                    {{ fund.change >= 0 ? '+' : '' }}{{ fund.change.toFixed(2) }}%
                  </td>
                  <td class="stock-volume" :class="fund.yield >= 0 ? 'text-green' : 'text-red'">
                    {{ fund.yield >= 0 ? '+' : '' }}{{ fund.yield.toFixed(2) }}%
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab Content: Количественный анализ -->
    <div v-show="activeTab === 'quant'" class="tab-content-market">
      
      <!-- LIQUIDITY SURFACE DASHBOARD -->
      <div class="liquidity-dashboard-section">
        <div class="glass-panel liquidity-panel">
          
          <!-- Header -->
          <div class="liquidity-header">
            <div class="liquidity-title-group">
              <h2 class="liquidity-title">LATENT MANIFOLD</h2>
              <div class="liquidity-subtitle-group">
                <span class="liquidity-subtitle">Surface inference</span>
                <span class="liquidity-value">{{ (liquidityParams.flowPressure * 15.36).toFixed(2) }}</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="opacity: 0.6;">
                  <circle cx="12" cy="12" r="10"/>
                </svg>
              </div>
            </div>
          </div>

          <!-- Main Grid -->
          <div class="liquidity-grid">
            
            <!-- Left: 3D Surface -->
            <div class="liquidity-3d-container">
              <canvas class="liquidity-3d-canvas"></canvas>
              <div class="liquidity-3d-info">
                <div class="surface-param">
                  <span class="param-label">Flow Pressure (Forced Selling)</span>
                </div>
                <div class="surface-param">
                  <span class="param-label">Liquidity</span>
                </div>
                <div class="surface-param time-horizon">
                  <span class="param-label">TIME HORIZON</span>
                  <span class="param-value-date">{{ liquidityTimestamp.split(' ')[0] }}</span>
                </div>
                <div class="surface-param">
                  <span class="param-label">Dep</span>
                </div>
              </div>
            </div>

            <!-- Center: Price Stream & Signal Matrix -->
            <div class="liquidity-center">
              
              <!-- Live Price Stream -->
              <div class="price-stream-container">
                <div class="price-stream-header">
                  <div class="price-info">
                    <div class="equity-stream-title">
                      <span class="live-dot-green"></span>
                      <span class="equity-title-text">LIVE EQUITY STREAM</span>
                    </div>
                    <div class="strategy-pnl">
                      <span class="pnl-label">STRATEGY PNL</span>
                      <span class="pnl-value text-green">${{ (currentPrice * 0.37).toFixed(2) }}</span>
                      <span class="pnl-subvalue">{{ Math.floor(currentPrice * 0.4) }}</span>
                    </div>
                  </div>
                  <button class="now-button">NOW</button>
                </div>
                <svg ref="priceStreamChart" class="price-stream-svg" viewBox="0 0 800 200" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="grad-price" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="rgba(16, 185, 129, 0.2)"/>
                      <stop offset="100%" stop-color="rgba(16, 185, 129, 0)"/>
                    </linearGradient>
                    <filter id="glow-price">
                      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                      <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                      </feMerge>
                    </filter>
                  </defs>
                  <!-- Grid -->
                  <g class="grid-price">
                    <line v-for="i in 5" :key="'h'+i" 
                      :x1="0" :y1="(i * 40)" :x2="800" :y2="(i * 40)" 
                      stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
                    <line v-for="i in 8" :key="'v'+i" 
                      :x1="(i * 100)" :y1="0" :x2="(i * 100)" :y2="200" 
                      stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
                  </g>
                  <!-- Price Area -->
                  <path 
                    :d="priceAreaPath" 
                    fill="url(#grad-price)" 
                    stroke="none"
                  />
                  <!-- Price Line -->
                  <path 
                    :d="priceLinePath" 
                    fill="none" 
                    stroke="#10b981" 
                    stroke-width="2"
                    filter="url(#glow-price)"
                  />
                  <!-- Current Price Indicator -->
                  <circle 
                    cx="800" 
                    :cy="priceEndY" 
                    r="4" 
                    fill="#10b981"
                    filter="url(#glow-price)"
                  />
                  <!-- Axis Labels -->
                  <text x="10" y="15" fill="rgba(255,255,255,0.4)" font-size="10" font-family="monospace">Цена (₽)</text>
                  <text x="750" y="195" fill="rgba(255,255,255,0.4)" font-size="10" font-family="monospace">Время</text>
                </svg>
              </div>

              <!-- Signal Matrix Heatmap -->
              <div class="signal-matrix-container">
                <div class="signal-matrix-header">
                  <span class="matrix-title">SIGNAL MATRIX</span>
                </div>
                <div class="signal-matrix-placeholder"></div>
              </div>

            </div>

            <!-- Right: L2 Order Flow -->
            <div class="liquidity-metrics-panel">
              <div class="metrics-header-liquidity">
                <span class="metrics-title-liquidity">L2 ORDER FLOW</span>
              </div>
              
              <!-- Order Flow Table -->
              <div class="order-flow-table">
                <div class="order-flow-row">
                  <span class="order-flow-label">BUY</span>
                  <span class="order-flow-value">{{ (bidFlow / 100).toFixed(3) }}</span>
                  <span class="order-flow-value">{{ (bidFlow * 2.78).toFixed(2) }}</span>
                </div>
                <div class="order-flow-row">
                  <span class="order-flow-label">SELL</span>
                  <span class="order-flow-value">{{ (askFlow / 13.1).toFixed(3) }}</span>
                  <span class="order-flow-value">{{ (askFlow * 3.46).toFixed(2) }}</span>
                </div>
              </div>

            </div>
          </div>

        </div>
      </div>
      
      <!-- QUANTLATENT v9.2 DASHBOARD -->
    <div class="quantlatent-section">
      <div class="glass-panel quantlatent-panel">
        
        <!-- Header -->
        <div class="quantlatent-header">
          <div class="quantlatent-title-group">
            <h2 class="quantlatent-title">КВАНТЛАТЕНТ v9.2</h2>
            <span class="quantlatent-subtitle">Топология рынка и поток ликвидности</span>
          </div>
          <div class="quantlatent-status-group">
            <div class="status-indicator-quantlatent">
              <span class="status-dot-quantlatent"></span>
              <span class="status-text-quantlatent">РЕАЛ-ТАЙМ</span>
            </div>
            <div class="status-epoch">
              <span class="epoch-label">ЭПОХА</span>
              <span class="epoch-value">{{ currentEpoch }}</span>
            </div>
            <div class="status-percent">
              <span class="percent-value">{{ liquidityPercent.toFixed(2) }}%</span>
            </div>
          </div>
        </div>

        <!-- Main Grid -->
        <div class="quantlatent-grid">
          
          <!-- Left: 3D Wireframe -->
          <div class="quantlatent-wireframe-container">
            <div class="wireframe-header">
              <span class="wireframe-label">Топология рынка</span>
            </div>
            <canvas ref="wireframeCanvas" class="wireframe-canvas"></canvas>
            <div class="wireframe-controls">
              <div class="control-param">
                <span class="param-label">Частота:</span>
                <span class="param-value">{{ wireframeParams.frequency.toFixed(2) }}</span>
              </div>
              <div class="control-param">
                <span class="param-label">Амплитуда:</span>
                <span class="param-value">{{ wireframeParams.amplitude.toFixed(2) }}</span>
              </div>
            </div>
          </div>

          <!-- Center: Charts & Orderbook -->
          <div class="quantlatent-center">
            
            <!-- Growth Chart -->
            <div class="growth-chart-container">
              <div class="chart-header-quantlatent">
                <span class="chart-title-quantlatent">Поток ликвидности</span>
                <span class="chart-time-range">{{ growthData.length }} периодов</span>
              </div>
              <svg ref="growthChart" class="growth-chart-svg" viewBox="0 0 800 200" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="grad-growth" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="rgba(16, 185, 129, 0.3)"/>
                    <stop offset="100%" stop-color="rgba(16, 185, 129, 0)"/>
                  </linearGradient>
                  <filter id="glow-growth">
                    <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                    <feMerge>
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>
                <!-- Grid -->
                <line x1="0" y1="100" x2="800" y2="100" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
                <line x1="0" y1="50" x2="800" y2="50" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
                <line x1="0" y1="150" x2="800" y2="150" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
                <!-- Area -->
                <path :d="growthAreaPath" fill="url(#grad-growth)" stroke="none"/>
                <!-- Line -->
                <path 
                  :d="growthLinePath" 
                  fill="none" 
                  stroke="#10b981" 
                  stroke-width="2"
                  filter="url(#glow-growth)"
                />
                <!-- Start point -->
                <circle 
                  :cx="0" 
                  :cy="growthStartY" 
                  r="3" 
                  fill="#10b981"
                  filter="url(#glow-growth)"
                />
                <!-- End point -->
                <circle 
                  :cx="800" 
                  :cy="growthEndY" 
                  r="4" 
                  fill="#10b981"
                  filter="url(#glow-growth)"
                />
              </svg>
            </div>

            <!-- Orderbook -->
            <div class="orderbook-container">
              <div class="orderbook-header">
                <span class="orderbook-title">РАНГ ЛИКВИДНОСТИ</span>
              </div>
              <div class="orderbook-table">
                <div 
                  v-for="(row, i) in orderbookData" 
                  :key="i"
                  class="orderbook-row"
                  :class="{ 'row-even': i % 2 === 0 }"
                >
                  <div class="orderbook-name">{{ row.name }}</div>
                  <div class="orderbook-value">{{ row.value.toFixed(2) }}</div>
                </div>
              </div>
            </div>

          </div>

          <!-- Right: Metrics Panel -->
          <div class="quantlatent-metrics-panel">
            <div class="metrics-header">
              <span class="metrics-title">КЛЮЧЕВЫЕ МЕТРИКИ</span>
            </div>
            <div class="metrics-list">
              <div class="metric-item-quantlatent">
                <div class="metric-value-large text-green">{{ metricsQuantlatent.sharpe.toFixed(2) }}</div>
                <div class="metric-label-small">КОЭФ. ШАРПА</div>
              </div>
              <div class="metric-item-quantlatent">
                <div class="metric-value-large text-white">{{ metricsQuantlatent.latency.toFixed(2) }}</div>
                <div class="metric-label-small">ЗАДЕРЖКА_МС</div>
              </div>
              <div class="metric-item-quantlatent">
                <div class="metric-value-large text-green">{{ metricsQuantlatent.maxReturn.toFixed(1) }}</div>
                <div class="metric-label-small">МАКС_ДОХОДНОСТЬ</div>
              </div>
            </div>
            
            <!-- Additional Metrics -->
            <div class="metrics-secondary">
              <div class="metric-secondary">
                <span class="metric-label-secondary">ПРОСАДКА</span>
                <span class="metric-value-secondary text-red">{{ metricsQuantlatent.drawdown.toFixed(2) }}%</span>
              </div>
              <div class="metric-secondary">
                <span class="metric-label-secondary">ВОЛАТИЛЬНОСТЬ</span>
                <span class="metric-value-secondary">{{ metricsQuantlatent.volatility.toFixed(2) }}%</span>
              </div>
              <div class="metric-secondary">
                <span class="metric-label-secondary">ПОТОК</span>
                <span class="metric-value-secondary text-green">{{ metricsQuantlatent.flow.toFixed(1) }}М</span>
              </div>
            </div>
          </div>

        </div>

        <!-- Scanline Effect -->
        <div class="scanline"></div>

      </div>
    </div>

    <!-- VOLATILITY TRADING SYSTEM DASHBOARD -->
    <div class="volatility-dashboard-section">
      <div class="glass-panel volatility-panel">
        
        <!-- Dashboard Header -->
        <div class="volatility-header">
          <div class="volatility-title-group">
            <h2 class="volatility-title">TANGO VIX 2.8</h2>
            <p class="volatility-subtitle">Количественная торговая система на основе волатильности</p>
            <div class="volatility-meta">
              <span class="meta-item">Модель агрегации сигналов</span>
              <span class="meta-item">Период: 2021-09 по 2021-12</span>
              <span class="meta-item">Начальный капитал: $100,000</span>
            </div>
          </div>
        </div>

        <!-- Main Dashboard Grid -->
        <div class="volatility-grid">
          
          <!-- Left: 3D P&L Surface -->
          <div class="volatility-3d-container">
            <div class="volatility-3d-header">
              <h3 class="section-title-volatility">Поверхность распределения P&L</h3>
              <div class="surface-controls">
                <span class="control-hint">Вращение: Мышь | Масштаб: Колесо</span>
              </div>
            </div>
            <div id="pnl-surface-3d" class="pnl-surface-container"></div>
            <div class="surface-info">
              <div class="info-item-surface">
                <span class="info-label-surface">X: Время/Дата</span>
                <span class="info-label-surface">Y: Режим волатильности</span>
                <span class="info-label-surface">Z: Накопленный P&L ($)</span>
              </div>
            </div>
          </div>

          <!-- Right: Equity Curve & Stats -->
          <div class="volatility-right-panel">
            
            <!-- Equity Curve -->
            <div class="equity-curve-container">
              <div class="equity-header">
                <h3 class="section-title-volatility">Сравнение производительности</h3>
                <div class="equity-legend">
                  <div class="legend-item-equity">
                    <span class="legend-square" style="background: #00ff88;"></span>
                    <span class="legend-text">TANGO VIX 2.8</span>
                  </div>
                  <div class="legend-item-equity">
                    <span class="legend-square" style="background: #888888;"></span>
                    <span class="legend-text">S&P 500 B&H</span>
                  </div>
                </div>
              </div>
              <svg ref="equityChart" class="equity-chart-svg" viewBox="0 0 1000 400" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="grad-equity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="rgba(0, 255, 136, 0.3)"/>
                    <stop offset="100%" stop-color="rgba(0, 255, 136, 0)"/>
                  </linearGradient>
                  <filter id="glow-equity">
                    <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                    <feMerge>
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>
                <!-- Grid -->
                <g class="grid-lines">
                  <line v-for="i in 5" :key="'h'+i" 
                    :x1="0" :y1="(i * 80)" :x2="1000" :y2="(i * 80)" 
                    stroke="#1a1a1a" stroke-width="1"/>
                  <line v-for="i in 10" :key="'v'+i" 
                    :x1="(i * 100)" :y1="0" :x2="(i * 100)" :y2="400" 
                    stroke="#1a1a1a" stroke-width="1"/>
                </g>
                <!-- S&P 500 Area (dashed) -->
                <path 
                  :d="benchmarkLinePath" 
                  fill="none" 
                  stroke="#888888" 
                  stroke-width="1.5"
                  stroke-dasharray="4,4"
                />
                <!-- Strategy Area -->
                <path 
                  :d="strategyAreaPath" 
                  fill="url(#grad-equity)" 
                  stroke="none"
                />
                <!-- Strategy Line -->
                <path 
                  :d="strategyLinePath" 
                  fill="none" 
                  stroke="#00ff88" 
                  stroke-width="3"
                  filter="url(#glow-equity)"
                />
                <!-- Crosshair (on hover) -->
                <g v-if="hoverPoint" class="crosshair">
                  <line 
                    :x1="hoverPoint.x" y1="0" 
                    :x2="hoverPoint.x" y2="400" 
                    stroke="rgba(255,255,255,0.3)" 
                    stroke-width="1"
                    stroke-dasharray="2,2"
                  />
                  <circle 
                    :cx="hoverPoint.x" 
                    :cy="hoverPoint.yStrategy" 
                    r="4" 
                    fill="#00ff88"
                    filter="url(#glow-equity)"
                  />
                  <circle 
                    :cx="hoverPoint.x" 
                    :cy="hoverPoint.yBenchmark" 
                    r="3" 
                    fill="#888888"
                  />
                  <!-- Tooltip -->
                  <g class="tooltip-equity" :transform="`translate(${hoverPoint.x}, ${hoverPoint.yStrategy - 30})`">
                    <rect x="-60" y="-40" width="120" height="60" rx="4" fill="rgba(0,0,0,0.9)" stroke="#00ff88" stroke-width="1"/>
                    <text x="0" y="-20" text-anchor="middle" fill="#00ff88" font-size="10" font-weight="600">
                      Стратегия: ${{ hoverPoint.strategyValue.toLocaleString() }}
                    </text>
                    <text x="0" y="-5" text-anchor="middle" fill="#888888" font-size="9">
                      S&P 500: ${{ hoverPoint.benchmarkValue.toLocaleString() }}
                    </text>
                    <text x="0" y="10" text-anchor="middle" fill="rgba(255,255,255,0.6)" font-size="8">
                      {{ hoverPoint.date }}
                    </text>
                  </g>
                </g>
              </svg>
            </div>

            <!-- Statistics Panel -->
            <div class="stats-panel-volatility">
              <h3 class="section-title-volatility">Метрики производительности</h3>
              <div class="stats-list-volatility">
                <div class="stat-row-volatility">
                  <span class="stat-label-volatility">Общая доходность</span>
                  <span class="stat-value-volatility text-green">+{{ performanceStats.totalReturn.toFixed(1) }}%</span>
                </div>
                <div class="stat-row-volatility">
                  <span class="stat-label-volatility">Коэффициент Шарпа</span>
                  <span class="stat-value-volatility">{{ performanceStats.sharpe.toFixed(2) }}</span>
                </div>
                <div class="stat-row-volatility">
                  <span class="stat-label-volatility">Максимальная просадка</span>
                  <span class="stat-value-volatility text-red">{{ performanceStats.maxDrawdown.toFixed(1) }}%</span>
                </div>
                <div class="stat-row-volatility">
                  <span class="stat-label-volatility">Процент прибыльных сделок</span>
                  <span class="stat-value-volatility">{{ performanceStats.winRate.toFixed(1) }}%</span>
                </div>
                <div class="stat-row-volatility">
                  <span class="stat-label-volatility">Среднее П/У</span>
                  <span class="stat-value-volatility">{{ performanceStats.avgWinLoss.toFixed(1) }}</span>
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>

    <!-- QUANT ALPHA TERMINAL -->
    <div class="quant-terminal-section">
      <div class="glass-panel terminal-panel">
        
        <!-- Terminal Header -->
        <div class="terminal-header">
          <div class="terminal-title-group">
            <h2 class="terminal-title">КВАНТ АЛЬФА ТЕРМИНАЛ</h2>
            <div class="terminal-vix">
              <span class="vix-label">РЫНОЧНЫЙ VIX</span>
              <span class="vix-value" :class="terminalVix >= 20 ? 'text-red' : 'text-green'">
                {{ terminalVix.toFixed(2) }}%
              </span>
            </div>
            <div class="terminal-time">
              <span class="mono">{{ currentTime }}</span>
            </div>
          </div>
          <div class="terminal-controls">
            <button 
              class="btn-terminal" 
              :class="{ active: isLive }"
              @click="toggleLive"
            >
              {{ isLive ? 'АКТИВНЫЙ ИНФЕРЕНС' : 'ПАУЗА ИНФЕРЕНСА' }}
            </button>
          </div>
        </div>

        <!-- Main Terminal Grid -->
        <div class="terminal-grid">
          
          <!-- Left: 3D Visualization -->
          <div class="terminal-3d-container">
            <div class="terminal-3d-header">
              <span class="terminal-label">Латентное поле волатильности</span>
              <span class="terminal-badge">3D Многообразие</span>
            </div>
            <canvas ref="threeCanvas" class="three-canvas"></canvas>
            <div class="terminal-3d-info">
              <div class="info-item">
                <span class="info-label">Дрейф (μ):</span>
                <span class="info-value">{{ gbmParams.drift.toFixed(3) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Волатильность (σ):</span>
                <span class="info-value">{{ gbmParams.volatility.toFixed(3) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Окно анализа:</span>
                <span class="info-value">{{ gbmParams.lookback }}</span>
              </div>
            </div>
          </div>

          <!-- Center: Charts -->
          <div class="terminal-charts">
            
            <!-- Backtest Chart -->
            <div class="chart-container-terminal">
              <div class="chart-header-terminal">
                <span class="chart-title-terminal">Производительность бэктеста</span>
                <div class="chart-legend-terminal">
                  <span class="legend-item-terminal">
                    <span class="legend-dot" style="background: #4ade80;"></span>
                    ПОКУПКА_И_УДЕРЖАНИЕ
                  </span>
                  <span class="legend-item-terminal">
                    <span class="legend-dot" style="background: #22d3ee;"></span>
                    ORCA I_1
                  </span>
                </div>
              </div>
              <svg ref="backtestChart" class="chart-svg" viewBox="0 0 800 300" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="grad-buyhold" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="rgba(74, 222, 128, 0.3)"/>
                    <stop offset="100%" stop-color="rgba(74, 222, 128, 0)"/>
                  </linearGradient>
                  <linearGradient id="grad-orca" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="rgba(34, 211, 238, 0.3)"/>
                    <stop offset="100%" stop-color="rgba(34, 211, 238, 0)"/>
                  </linearGradient>
                </defs>
                <!-- Grid -->
                <line x1="0" y1="150" x2="800" y2="150" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
                <line x1="0" y1="75" x2="800" y2="75" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
                <line x1="0" y1="225" x2="800" y2="225" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
                <!-- Buy & Hold Area -->
                <path 
                  :d="buyHoldAreaPath" 
                  fill="url(#grad-buyhold)" 
                  stroke="none"
                />
                <!-- Buy & Hold Line -->
                <path 
                  :d="buyHoldLinePath" 
                  fill="none" 
                  stroke="#4ade80" 
                  stroke-width="2"
                  filter="drop-shadow(0 0 4px rgba(74, 222, 128, 0.5))"
                />
                <!-- ORCA Area -->
                <path 
                  :d="orcaAreaPath" 
                  fill="url(#grad-orca)" 
                  stroke="none"
                />
                <!-- ORCA Line -->
                <path 
                  :d="orcaLinePath" 
                  fill="none" 
                  stroke="#22d3ee" 
                  stroke-width="2"
                  filter="drop-shadow(0 0 4px rgba(34, 211, 238, 0.5))"
                />
              </svg>
            </div>

            <!-- Volatility Charts -->
            <div class="volatility-charts-row">
              <!-- Red Chart (Descending) -->
              <div class="vol-chart-container">
                <div class="vol-chart-header">
                  <span class="vol-chart-label">ВЕРСИЯ</span>
                  <span class="vol-chart-label">ДВИЖОК</span>
                  <span class="vol-chart-label">R3F_V8</span>
                </div>
                <svg ref="redVolChart" class="vol-chart-svg" viewBox="0 0 400 150" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="grad-red" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="rgba(239, 68, 68, 0.4)"/>
                      <stop offset="100%" stop-color="rgba(239, 68, 68, 0)"/>
                    </linearGradient>
                  </defs>
                  <path :d="redVolAreaPath" fill="url(#grad-red)" stroke="none"/>
                  <path :d="redVolLinePath" fill="none" stroke="#ef4444" stroke-width="2"/>
                </svg>
              </div>

              <!-- Green Chart (Ascending) -->
              <div class="vol-chart-container">
                <div class="vol-chart-header">
                  <span class="vol-chart-label">МАКС_ПРОСАДКА</span>
                  <span class="vol-chart-label">ШАРП</span>
                  <span class="vol-chart-label">ЗАДЕРЖКА</span>
                </div>
                <svg ref="greenVolChart" class="vol-chart-svg" viewBox="0 0 400 150" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="grad-green-vol" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="rgba(74, 222, 128, 0.4)"/>
                      <stop offset="100%" stop-color="rgba(74, 222, 128, 0)"/>
                    </linearGradient>
                  </defs>
                  <path :d="greenVolAreaPath" fill="url(#grad-green-vol)" stroke="none"/>
                  <path :d="greenVolLinePath" fill="none" stroke="#4ade80" stroke-width="2"/>
                </svg>
              </div>
            </div>

          </div>

          <!-- Right: Terminal Console & Controls -->
          <div class="terminal-sidebar">
            
            <!-- Parameters Sliders -->
            <div class="terminal-controls-panel">
              <div class="control-group-terminal">
                <label class="control-label-terminal">
                  ДРЕЙФ (μ)
                  <span class="control-value-terminal">{{ gbmParams.drift.toFixed(3) }}</span>
                </label>
                <input 
                  type="range" 
                  v-model.number="gbmParams.drift" 
                  min="0" 
                  max="0.1" 
                  step="0.001"
                  class="slider-terminal"
                  @input="updateGBMSimulation"
                />
              </div>
              
              <div class="control-group-terminal">
                <label class="control-label-terminal">
                  ВОЛАТИЛЬНОСТЬ (σ)
                  <span class="control-value-terminal">{{ gbmParams.volatility.toFixed(3) }}</span>
                </label>
                <input 
                  type="range" 
                  v-model.number="gbmParams.volatility" 
                  min="0.05" 
                  max="0.5" 
                  step="0.001"
                  class="slider-terminal"
                  @input="updateGBMSimulation"
                />
              </div>
              
              <div class="control-group-terminal">
                <label class="control-label-terminal">
                  ОКНО АНАЛИЗА
                  <span class="control-value-terminal">{{ gbmParams.lookback }}</span>
                </label>
                <input 
                  type="range" 
                  v-model.number="gbmParams.lookback" 
                  min="50" 
                  max="500" 
                  step="10"
                  class="slider-terminal"
                  @input="updateGBMSimulation"
                />
              </div>
            </div>

            <!-- Metrics -->
            <div class="terminal-metrics">
              <div class="metric-terminal">
                <span class="metric-label-terminal">Коэффициент Шарпа</span>
                <span class="metric-value-terminal text-green">{{ metrics.sharpe.toFixed(2) }}</span>
              </div>
              <div class="metric-terminal">
                <span class="metric-label-terminal">Максимальная просадка</span>
                <span class="metric-value-terminal text-red">{{ metrics.maxDrawdown.toFixed(2) }}%</span>
              </div>
              <div class="metric-terminal">
                <span class="metric-label-terminal">VaR (95%)</span>
                <span class="metric-value-terminal text-orange">{{ metrics.var.toFixed(2) }}%</span>
              </div>
              <div class="metric-terminal">
                <span class="metric-label-terminal">Общая доходность</span>
                <span class="metric-value-terminal" :class="metrics.totalReturn >= 0 ? 'text-green' : 'text-red'">
                  {{ metrics.totalReturn >= 0 ? '+' : '' }}{{ metrics.totalReturn.toFixed(2) }}%
                </span>
              </div>
            </div>

            <!-- Terminal Console -->
            <div class="terminal-console">
              <div class="console-header">
                <span class="console-title">СИСТЕМНЫЙ ЛОГ</span>
                <span class="console-status" :class="isLive ? 'text-green' : 'text-muted'">
                  {{ isLive ? '● АКТИВЕН' : '○ ПАУЗА' }}
                </span>
              </div>
              <div class="console-content" ref="consoleContent">
                <div 
                  v-for="(log, i) in terminalLogs" 
                  :key="i" 
                  class="console-line"
                  :class="log.type"
                >
                  <span class="console-time">{{ log.time }}</span>
                  <span class="console-message">{{ log.message }}</span>
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
    <!-- End Tab Content: Количественный анализ -->

    </div>
  </div>
  <!-- End Legacy Hidden Content -->

  <!-- Asset Detail Modal -->
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="selectedAsset" class="asset-modal-backdrop" @click="closeAssetDetail">
        <div class="asset-modal-container" @click.stop>
          
          <!-- Modal Header -->
          <div class="asset-modal-header">
            <div class="asset-modal-title-group">
              <h2 class="asset-modal-title">{{ selectedAsset.symbol }}</h2>
              <p class="asset-modal-subtitle" v-if="selectedAsset.name">{{ selectedAsset.name }}</p>
            </div>
            <button class="asset-modal-close" @click="closeAssetDetail" aria-label="Закрыть">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <!-- Modal Content -->
          <div class="asset-modal-content">
            
            <!-- Price Info -->
            <div class="asset-price-section">
              <div class="asset-current-price">
                <span class="price-label">Текущая цена</span>
                <span class="price-value">{{ formatPrice(selectedAsset.price) }} ₽</span>
                <span class="price-change-badge-large" :class="selectedAsset.change >= 0 ? 'text-green' : 'text-red'">
                  {{ selectedAsset.change >= 0 ? '+' : '' }}{{ selectedAsset.change.toFixed(2) }}%
                </span>
              </div>
              <div class="asset-meta-info">
                <div class="meta-item">
                  <span class="meta-label">Объем</span>
                  <span class="meta-value">{{ formatVolume(selectedAsset.volume || 0) }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">Тип</span>
                  <span class="meta-value">{{ getAssetTypeLabel(selectedAsset.type) }}</span>
                </div>
              </div>
            </div>

            <!-- Price Chart -->
            <div class="asset-chart-section">
              <div class="chart-header-asset">
                <h3 class="chart-title-asset">Изменение цены</h3>
                <div class="chart-controls-asset">
                  <div class="chart-type-toggle">
                    <button 
                      @click="chartType = 'line'"
                      class="chart-type-btn"
                      :class="{ active: chartType === 'line' }"
                    >
                      Линия
                    </button>
                    <button 
                      @click="chartType = 'candlestick'"
                      class="chart-type-btn"
                      :class="{ active: chartType === 'candlestick' }"
                    >
                      Свечи
                    </button>
                  </div>
                  <div class="chart-timeframe">
                    <button 
                      v-for="tf in timeframes" 
                      :key="tf"
                      @click="selectedTimeframe = tf"
                      class="timeframe-btn"
                      :class="{ active: selectedTimeframe === tf }"
                    >
                      {{ tf }}
                    </button>
                  </div>
                </div>
              </div>
              <div class="chart-container-asset">
                <canvas ref="assetPriceChart" class="asset-price-chart"></canvas>
              </div>
            </div>

            <!-- Order Book -->
            <div class="asset-orderbook-section">
              <h3 class="orderbook-title-asset">Стакан заявок</h3>
              <div class="orderbook-container-asset">
                <!-- Ask Side (Продажа) -->
                <div class="orderbook-side orderbook-ask">
                  <div class="orderbook-header-row">
                    <span>Цена</span>
                    <span>Объем</span>
                    <span>Кол-во</span>
                  </div>
                  <div 
                    v-for="(order, i) in orderBook.asks" 
                    :key="'ask-' + i"
                    class="orderbook-row orderbook-ask-row"
                    :style="{ opacity: 1 - (i * 0.08) }"
                  >
                    <span class="order-price text-red">{{ order.price.toFixed(2) }}</span>
                    <span class="order-volume">{{ order.volume.toLocaleString() }}</span>
                    <span class="order-count">{{ order.count }}</span>
                  </div>
                </div>

                <!-- Spread -->
                <div class="orderbook-spread">
                  <div class="spread-value">
                    <span class="spread-label">Спред</span>
                    <span class="spread-amount">{{ orderBook.spread.toFixed(4) }}</span>
                  </div>
                  <div class="spread-percent">
                    {{ ((orderBook.spread / selectedAsset.price) * 100).toFixed(3) }}%
                  </div>
                </div>

                <!-- Bid Side (Покупка) -->
                <div class="orderbook-side orderbook-bid">
                  <div 
                    v-for="(order, i) in orderBook.bids" 
                    :key="'bid-' + i"
                    class="orderbook-row orderbook-bid-row"
                    :style="{ opacity: 1 - (i * 0.08) }"
                  >
                    <span class="order-price text-green">{{ order.price.toFixed(2) }}</span>
                    <span class="order-volume">{{ order.volume.toLocaleString() }}</span>
                    <span class="order-count">{{ order.count }}</span>
                  </div>
                  <div class="orderbook-header-row">
                    <span>Цена</span>
                    <span>Объем</span>
                    <span>Кол-во</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Additional Info -->
            <div class="asset-info-section">
              <div class="info-grid-asset">
                <div class="info-card-asset">
                  <span class="info-label-asset">Максимум дня</span>
                  <span class="info-value-asset text-green">{{ formatPrice(assetDetails.dayHigh) }} ₽</span>
                </div>
                <div class="info-card-asset">
                  <span class="info-label-asset">Минимум дня</span>
                  <span class="info-value-asset text-red">{{ formatPrice(assetDetails.dayLow) }} ₽</span>
                </div>
                <div class="info-card-asset">
                  <span class="info-label-asset">Открытие</span>
                  <span class="info-value-asset">{{ formatPrice(assetDetails.open) }} ₽</span>
                </div>
                <div class="info-card-asset">
                  <span class="info-label-asset">Закрытие вчера</span>
                  <span class="info-value-asset">{{ formatPrice(assetDetails.previousClose) }} ₽</span>
                </div>
              </div>
            </div>

          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch, nextTick } from 'vue'
import { Teleport, Transition } from 'vue'
import * as THREE from 'three'
import Chart from 'chart.js/auto'

// ============================================
// NEW DESIGN DATA (Matching the image)
// ============================================

// Sidebar Navigation Items
const sidebarNavItems = ref([
  { id: 'indices', label: 'ИНДЕКСЫ' },
  { id: 'bonds', label: 'ОБЛИГАЦИИ' },
  { id: 'forex', label: 'ФОРЕКС' },
  { id: 'crypto', label: 'КРИПТО' },
  { id: 'news', label: 'НОВОСТИ' },
  { id: 'technicals', label: 'ТЕХАНАЛИЗ' },
  { id: 'ai', label: 'AI АНАЛИТИКА' }
])

// Top Regions (РОССИЯ, ЕВРОПА, США)
const topRegions = ref([
  {
    id: 'russia',
    name: 'РОССИЯ',
    data: [
      { index: 'IMOEX', value: '3,250.80', change: 1.25 },
      { index: 'RTS', value: '1,125.40', change: -0.45 },
      { index: 'MOEXBC', value: '1,850.20', change: 0.82 },
      { index: 'RGBI', value: '108.65', change: -0.15 }
    ]
  },
  {
    id: 'europe',
    name: 'ЕВРОПА',
    data: [
      { index: 'STOXX 50', value: '4,485.20', change: 0.65 },
      { index: 'DAX', value: '18,235.45', change: 0.42 },
      { index: 'IBEX 35', value: '11,245.80', change: 0.38 },
      { index: 'CAC 40', value: '7,890.15', change: 0.55 }
    ]
  },
  {
    id: 'usa',
    name: 'США',
    data: [
      { index: 'S&P 500', value: '5,234.18', change: 0.85 },
      { index: 'NASDAQ', value: '16,428.82', change: 1.24 },
      { index: 'Dow Jones', value: '39,512.84', change: 0.32 },
      { index: 'Russell 2000', value: '2,058.92', change: -0.68 }
    ]
  }
])

// Bottom Regions (АЗИЯ, КИТАЙ, ВЕЛИКОБРИТАНИЯ)
const bottomRegions = ref([
  {
    id: 'asia',
    name: 'АЗИЯ',
    data: [
      { index: 'Nikkei 225', value: '38,487.90', change: 1.85 },
      { index: 'Hang Seng', value: '17,915.55', change: -1.22 },
      { index: 'KOSPI', value: '2,687.45', change: 0.45 },
      { index: 'ASX 200', value: '7,825.30', change: 0.28 }
    ]
  },
  {
    id: 'china',
    name: 'КИТАЙ',
    data: [
      { index: 'Shanghai', value: '3,088.33', change: 0.96 },
      { index: 'Shenzhen', value: '1,808.81', change: 0.18 },
      { index: 'CSI 300', value: '3,542.65', change: 0.72 },
      { index: 'ChiNext', value: '1,892.40', change: 1.15 }
    ]
  },
  {
    id: 'uk',
    name: 'БРИТАНИЯ',
    data: [
      { index: 'FTSE 100', value: '8,125.30', change: -0.28 },
      { index: 'FTSE 250', value: '20,485.60', change: 0.42 },
      { index: 'FTSE AIM', value: '725.45', change: -0.15 },
      { index: 'FTSE 350', value: '4,512.80', change: 0.18 }
    ]
  }
])

// All regions combined for table (порядок: РОССИЯ, США, КИТАЙ, ЕВРОПА, ВЕЛИКОБРИТАНИЯ, АЗИЯ)
const allRegions = computed(() => {
  const russia = topRegions.value.find(r => r.id === 'russia')
  const usa = topRegions.value.find(r => r.id === 'usa')
  const china = bottomRegions.value.find(r => r.id === 'china')
  const europe = topRegions.value.find(r => r.id === 'europe')
  const uk = bottomRegions.value.find(r => r.id === 'uk')
  const asia = bottomRegions.value.find(r => r.id === 'asia')
  return [russia, usa, china, europe, uk, asia].filter((r): r is NonNullable<typeof r> => r !== undefined)
})

// Max number of data rows across all regions
const maxDataRows = computed(() => {
  const lengths = allRegions.value.map(r => r.data.length)
  return lengths.length > 0 ? Math.max(...lengths) : 0
})

// Markets update time
const marketsUpdateTime = ref('')

const updateMarketsUpdateTime = () => {
  const now = new Date()
  marketsUpdateTime.value = now.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

// Update markets data
const updateMarketsData = () => {
  // Update top regions
  topRegions.value.forEach(region => {
    region.data.forEach(item => {
      const currentValue = parseFloat(item.value.replace(/,/g, ''))
      const change = (Math.random() - 0.5) * currentValue * 0.002
      const newValue = currentValue + change
      item.value = newValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
      item.change = item.change + (Math.random() - 0.5) * 0.3
    })
  })
  
  // Update bottom regions
  bottomRegions.value.forEach(region => {
    region.data.forEach(item => {
      const currentValue = parseFloat(item.value.replace(/,/g, ''))
      const change = (Math.random() - 0.5) * currentValue * 0.002
      const newValue = currentValue + change
      item.value = newValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
      item.change = item.change + (Math.random() - 0.5) * 0.3
    })
  })
  
  updateMarketsUpdateTime()
}

// Sparkline Data (VIX, URALS, Gold)
const vixHistory = ref<number[]>([])
const uralsHistory = ref<number[]>([])
const goldHistory = ref<number[]>([])

const vixData = ref({ value: 18.5, change: -2.35 })
const uralsData = ref({ value: 68.45, change: 1.12 })
const goldData = ref({ value: 2345.80, change: 0.45 })

// Generate initial sparkline data
const generateSparklineData = () => {
  const vix: number[] = []
  const urals: number[] = []
  const gold: number[] = []
  
  let vixPrice = 18.5
  let uralsPrice = 68.45
  let goldPrice = 2345.80
  
  for (let i = 0; i < 20; i++) {
    vixPrice += (Math.random() - 0.5) * 1.5
    uralsPrice += (Math.random() - 0.48) * 1.2
    goldPrice += (Math.random() - 0.48) * 15
    
    vix.push(Math.max(10, Math.min(40, vixPrice)))
    urals.push(Math.max(50, Math.min(90, uralsPrice)))
    gold.push(Math.max(2200, Math.min(2500, goldPrice)))
  }
  
  vixHistory.value = vix
  uralsHistory.value = urals
  goldHistory.value = gold
  
  vixData.value.value = vix[vix.length - 1]
  uralsData.value.value = urals[urals.length - 1]
  goldData.value.value = gold[gold.length - 1]
}

// Update sparkline data
const updateSparklineData = () => {
  // VIX
  const newVix = vixData.value.value + (Math.random() - 0.5) * 1.2
  const clampedVix = Math.max(10, Math.min(40, newVix))
  vixHistory.value.push(clampedVix)
  if (vixHistory.value.length > 20) vixHistory.value.shift()
  const prevVix = vixData.value.value
  vixData.value.value = clampedVix
  vixData.value.change = ((clampedVix - prevVix) / prevVix) * 100
  
  // URALS
  const newUrals = uralsData.value.value + (Math.random() - 0.48) * 0.8
  const clampedUrals = Math.max(50, Math.min(90, newUrals))
  uralsHistory.value.push(clampedUrals)
  if (uralsHistory.value.length > 20) uralsHistory.value.shift()
  const prevUrals = uralsData.value.value
  uralsData.value.value = clampedUrals
  uralsData.value.change = ((clampedUrals - prevUrals) / prevUrals) * 100
  
  // Gold
  const newGold = goldData.value.value + (Math.random() - 0.48) * 10
  const clampedGold = Math.max(2200, Math.min(2500, newGold))
  goldHistory.value.push(clampedGold)
  if (goldHistory.value.length > 20) goldHistory.value.shift()
  const prevGold = goldData.value.value
  goldData.value.value = clampedGold
  goldData.value.change = ((clampedGold - prevGold) / prevGold) * 100
}

// Generate sparkline SVG path
const generateSparklinePath = (data: number[]): string => {
  if (data.length < 2) return ''
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  
  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * 100
    const y = 30 - ((val - min) / range) * 28
    return `${x},${y}`
  })
  
  return `M ${points.join(' L ')}`
}

const vixSparklinePath = computed(() => generateSparklinePath(vixHistory.value))
const uralsSparklinePath = computed(() => generateSparklinePath(uralsHistory.value))
const goldSparklinePath = computed(() => generateSparklinePath(goldHistory.value))

// AI Insights
// AI Insights stocks pool
const aiStocksPool = [
  { symbol: 'SBER', basePrice: 285.40 },
  { symbol: 'LKOH', basePrice: 7125.00 },
  { symbol: 'GAZP', basePrice: 156.80 },
  { symbol: 'YNDX', basePrice: 3450.00 },
  { symbol: 'ROSN', basePrice: 512.30 },
  { symbol: 'NVTK', basePrice: 1285.60 },
  { symbol: 'GMKN', basePrice: 14520.00 },
  { symbol: 'POLY', basePrice: 425.80 },
  { symbol: 'MTSS', basePrice: 298.50 },
  { symbol: 'MGNT', basePrice: 5840.00 },
  { symbol: 'AFLT', basePrice: 42.15 },
  { symbol: 'VTBR', basePrice: 0.024 },
  { symbol: 'TATN', basePrice: 685.40 },
  { symbol: 'NLMK', basePrice: 185.20 },
  { symbol: 'CHMF', basePrice: 1425.00 }
]

const aiInsights = ref([
  { type: 'buy', action: 'ПОКУПКА', symbol: 'SBER', value: '₽ 285.40' },
  { type: 'buy', action: 'ПОКУПКА', symbol: 'LKOH', value: '₽ 7,125.00' },
  { type: 'sell', action: 'ПРОДАЖА', symbol: 'GAZP', value: '₽ 156.80' },
  { type: 'buy', action: 'ПОКУПКА', symbol: 'YNDX', value: '₽ 3,450.00' }
])

// Update AI Insights
const updateAiInsights = () => {
  const newInsights: typeof aiInsights.value = []
  const usedIndices = new Set<number>()
  
  for (let i = 0; i < 4; i++) {
    let randomIndex: number
    do {
      randomIndex = Math.floor(Math.random() * aiStocksPool.length)
    } while (usedIndices.has(randomIndex))
    usedIndices.add(randomIndex)
    
    const stock = aiStocksPool[randomIndex]
    const priceChange = (Math.random() - 0.5) * stock.basePrice * 0.04
    const newPrice = stock.basePrice + priceChange
    const type = Math.random() > 0.4 ? 'buy' : 'sell'
    
    let formattedPrice: string
    if (newPrice < 1) {
      formattedPrice = `₽ ${newPrice.toFixed(4)}`
    } else if (newPrice < 100) {
      formattedPrice = `₽ ${newPrice.toFixed(2)}`
    } else {
      formattedPrice = `₽ ${newPrice.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    }
    
    newInsights.push({
      type,
      action: type === 'buy' ? 'ПОКУПКА' : 'ПРОДАЖА',
      symbol: stock.symbol,
      value: formattedPrice
    })
  }
  
  aiInsights.value = newInsights
}

// IMOEX & RTS Chart Data
const imoexData = ref<number[]>([])
const rtsData = ref<number[]>([])
const imoexChange = ref(1.25)
const rtsChange = ref(-0.45)

// Generate initial chart data
const generateChartData = () => {
  const imoex: number[] = []
  const rts: number[] = []
  let imoexPrice = 3250
  let rtsPrice = 1125
  
  for (let i = 0; i < 30; i++) {
    imoexPrice += (Math.random() - 0.48) * 20
    rtsPrice += (Math.random() - 0.52) * 10
    imoex.push(imoexPrice)
    rts.push(rtsPrice)
  }
  
  imoexData.value = imoex
  rtsData.value = rts
  imoexChange.value = ((imoex[imoex.length - 1] - imoex[0]) / imoex[0]) * 100
  rtsChange.value = ((rts[rts.length - 1] - rts[0]) / rts[0]) * 100
}

// Generate SVG path for chart
const generatePath = (data: number[], width: number, height: number, isArea: boolean = false) => {
  if (data.length === 0) return ''
  
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  
  const points = data.map((val, idx) => {
    const x = (idx / (data.length - 1)) * width
    const y = height - ((val - min) / range) * height * 0.8 - height * 0.1
    return { x, y }
  })
  
  let path = `M ${points[0].x} ${points[0].y}`
  for (let i = 1; i < points.length; i++) {
    path += ` L ${points[i].x} ${points[i].y}`
  }
  
  if (isArea) {
    path += ` L ${width} ${height} L 0 ${height} Z`
  }
  
  return path
}

const imoexLinePath = computed(() => generatePath(imoexData.value, 200, 200))
const imoexAreaPath = computed(() => generatePath(imoexData.value, 200, 200, true))
const rtsLinePath = computed(() => generatePath(rtsData.value, 200, 200))
const rtsAreaPath = computed(() => generatePath(rtsData.value, 200, 200, true))

// Update chart data periodically
const updateIndexCharts = () => {
  if (imoexData.value.length > 0) {
    const newImoex = [...imoexData.value.slice(1)]
    const lastImoex = newImoex[newImoex.length - 1] + (Math.random() - 0.48) * 15
    newImoex.push(lastImoex)
    imoexData.value = newImoex
    imoexChange.value = ((newImoex[newImoex.length - 1] - newImoex[0]) / newImoex[0]) * 100
  }
  
  if (rtsData.value.length > 0) {
    const newRts = [...rtsData.value.slice(1)]
    const lastRts = newRts[newRts.length - 1] + (Math.random() - 0.52) * 8
    newRts.push(lastRts)
    rtsData.value = newRts
    rtsChange.value = ((newRts[newRts.length - 1] - newRts[0]) / newRts[0]) * 100
  }
}

// Recommendations
const recommendations = ref([
  { label: 'Портфель:', value: 'Диверсифицировать' },
  { label: 'Риск-профиль:', value: 'Умеренный' },
  { label: 'Горизонт:', value: '6-12 месяцев' }
])

// Alerts
const alerts = ref([
  { text: 'IMOEX приближается к уровню сопротивления 3,300' },
  { text: 'Высокая волатильность в секторе нефтегаза' },
  { text: 'Рубль укрепился до 88.5 за доллар' }
])

// Alert helper functions
const getAlertType = (text: string): string => {
  if (text.includes('сопротивлен') || text.includes('поддержк')) return 'alert-resistance'
  if (text.includes('волатильность') || text.includes('риск')) return 'alert-warning'
  if (text.includes('укрепи') || text.includes('рост')) return 'alert-positive'
  if (text.includes('ослаб') || text.includes('падени')) return 'alert-negative'
  return 'alert-info'
}

const getAlertIcon = (text: string): string => {
  if (text.includes('сопротивлен') || text.includes('поддержк')) return '◉'
  if (text.includes('волатильность') || text.includes('риск')) return '⚡'
  if (text.includes('укрепи') || text.includes('рост')) return '↗'
  if (text.includes('ослаб') || text.includes('падени')) return '↘'
  return '●'
}

const getAlertTime = (idx: number): string => {
  const times = ['2 мин назад', '8 мин назад', '15 мин назад', '32 мин назад', '1 час назад']
  return times[idx % times.length]
}

// Signal Matrix Data (3 rows x 12 columns)
const signalMatrix = ref<number[][]>([])

// Generate initial signal matrix
const generateSignalMatrix = () => {
  const matrix: number[][] = []
  for (let i = 0; i < 3; i++) {
    const row: number[] = []
    for (let j = 0; j < 12; j++) {
      row.push(Math.random())
    }
    matrix.push(row)
  }
  signalMatrix.value = matrix
}

// Update signal matrix
const updateSignalMatrix = () => {
  signalMatrix.value = signalMatrix.value.map(row => 
    row.map(cell => {
      const change = (Math.random() - 0.5) * 0.3
      return Math.max(0, Math.min(1, cell + change))
    })
  )
}

// Get color for signal matrix cell
const getSignalColor = (value: number): string => {
  // Color palette: cream/yellow -> orange -> magenta -> purple
  if (value < 0.25) {
    // Cream/Yellow
    const t = value / 0.25
    return `rgb(${255}, ${230 - t * 30}, ${180 - t * 80})`
  } else if (value < 0.5) {
    // Orange
    const t = (value - 0.25) / 0.25
    return `rgb(${255 - t * 50}, ${200 - t * 80}, ${100 - t * 50})`
  } else if (value < 0.75) {
    // Magenta
    const t = (value - 0.5) / 0.25
    return `rgb(${205 - t * 80}, ${120 - t * 60}, ${50 + t * 100})`
  } else {
    // Purple
    const t = (value - 0.75) / 0.25
    return `rgb(${125 - t * 45}, ${60 + t * 20}, ${150 + t * 50})`
  }
}

// News Feed
const newsList = ref([
  { region: 'РОССИЯ', text: 'Индекс Мосбиржи обновил максимум с начала года на фоне роста нефтяных котировок' },
  { region: 'США', text: 'ФРС сохранила ключевую ставку на уровне 5.25-5.50%, рынки ожидают снижения' },
  { region: 'КИТАЙ', text: 'Народный банк Китая снизил ставку по кредитам для поддержки экономики' },
  { region: 'ЕВРОПА', text: 'ЕЦБ начал цикл смягчения политики, снизив ставку на 25 базисных пунктов' },
  { region: 'АЗИЯ', text: 'Nikkei 225 достиг исторического максимума благодаря ослаблению иены' },
  { region: 'РОССИЯ', text: 'Сбербанк отчитался о рекордной чистой прибыли за первое полугодие' },
  { region: 'США', text: 'Apple и Microsoft продолжают гонку за звание самой дорогой компании' },
  { region: 'КИТАЙ', text: 'Alibaba и JD.com показали рост выручки выше ожиданий аналитиков' },
  { region: 'ЕВРОПА', text: 'Акции LVMH под давлением на фоне замедления спроса на luxury-товары' },
  { region: 'АЗИЯ', text: 'Samsung анонсировал инвестиции в производство чипов нового поколения' },
  { region: 'РОССИЯ', text: 'Газпром нарастил поставки газа в Китай до рекордных объёмов' },
  { region: 'США', text: 'NVIDIA стала третьей компанией с капитализацией выше $3 трлн' },
  { region: 'КИТАЙ', text: 'BYD обогнал Tesla по продажам электромобилей в мире' },
  { region: 'ЕВРОПА', text: 'Volkswagen инвестирует €180 млрд в электрификацию до 2030 года' },
  { region: 'АЗИЯ', text: 'Индия стала пятой по величине экономикой мира, обогнав Великобританию' }
])

const currentNewsIndex = ref(0)

// Возвращает 3 новости начиная с текущего индекса
const currentNewsGroup = computed(() => {
  const result: typeof newsList.value = []
  for (let i = 0; i < 3; i++) {
    const idx = (currentNewsIndex.value + i) % newsList.value.length
    result.push(newsList.value[idx])
  }
  return result
})

// News rotation interval
let newsInterval: ReturnType<typeof setInterval> | null = null

const startNewsRotation = () => {
  newsInterval = setInterval(() => {
    currentNewsIndex.value = (currentNewsIndex.value + 1) % newsList.value.length
  }, 4000) // меняется по одной каждые 4 секунды
}

const stopNewsRotation = () => {
  if (newsInterval) {
    clearInterval(newsInterval)
    newsInterval = null
  }
}


// Legacy tabs (kept for backward compatibility with old sections)
const legacyTabs = [
  { id: 'overview', name: 'Обзор рынка' },
  { id: 'stocks', name: 'Акции' },
  { id: 'bonds', name: 'Облигации' },
  { id: 'funds', name: 'ПИФы' },
  { id: 'quant', name: 'Количественный анализ' }
]

// Search Query
const searchQuery = ref('')

const handleSearch = () => {
  // Search is handled by getFilteredInstruments()
  console.log('Searching for:', searchQuery.value)
}

const clearSearch = () => {
  searchQuery.value = ''
  handleSearch()
}

// Asset Detail Modal
const selectedAsset = ref<{
  symbol: string
  name?: string
  price: number
  change: number
  volume?: number
  type?: string
} | null>(null)

const selectedTimeframe = ref('1D')
const timeframes = ['1H', '1D', '1W', '1M', '3M']

const chartType = ref<'line' | 'candlestick'>('line')

const assetPriceChart = ref<HTMLCanvasElement | null>(null)
let assetChart: Chart | null = null

// Candlestick data
const candlestickData = ref<Array<{ open: number, high: number, low: number, close: number }>>([])

// Order Book Data
const orderBook = ref({
  bids: [] as Array<{ price: number, volume: number, count: number }>,
  asks: [] as Array<{ price: number, volume: number, count: number }>,
  spread: 0
})

// Asset Details
const assetDetails = ref({
  dayHigh: 0,
  dayLow: 0,
  open: 0,
  previousClose: 0
})

// Price History for Chart
const assetPriceHistory = ref<number[]>([])

// Open Asset Detail
const openAssetDetail = (asset: any) => {
  selectedAsset.value = {
    symbol: asset.symbol,
    name: asset.name,
    price: asset.price,
    change: asset.change,
    volume: asset.volume,
    type: asset.type || 'stock'
  }
  
  // Generate order book
  generateOrderBook(asset.price)
  
  // Generate price history
  generatePriceHistory(asset.price)
  
  // Calculate asset details
  assetDetails.value = {
    dayHigh: asset.price * (1 + Math.random() * 0.02),
    dayLow: asset.price * (1 - Math.random() * 0.02),
    open: asset.price * (1 + (Math.random() - 0.5) * 0.01),
    previousClose: asset.price / (1 + asset.change / 100)
  }
  
  // Initialize chart
  setTimeout(() => {
    initAssetPriceChart()
  }, 100)
}

// Close Asset Detail
const closeAssetDetail = () => {
  selectedAsset.value = null
  if (assetChart) {
    assetChart.destroy()
    assetChart = null
  }
}

// Generate Order Book
const generateOrderBook = (currentPrice: number) => {
  const bids: Array<{ price: number, volume: number, count: number }> = []
  const asks: Array<{ price: number, volume: number, count: number }> = []
  
  // Generate bids (below current price)
  for (let i = 0; i < 10; i++) {
    const price = currentPrice * (1 - (i + 1) * 0.001 - Math.random() * 0.0005)
    bids.push({
      price,
      volume: Math.floor(Math.random() * 100000) + 10000,
      count: Math.floor(Math.random() * 20) + 1
    })
  }
  
  // Generate asks (above current price)
  for (let i = 0; i < 10; i++) {
    const price = currentPrice * (1 + (i + 1) * 0.001 + Math.random() * 0.0005)
    asks.push({
      price,
      volume: Math.floor(Math.random() * 100000) + 10000,
      count: Math.floor(Math.random() * 20) + 1
    })
  }
  
  // Sort bids descending, asks ascending
  bids.sort((a, b) => b.price - a.price)
  asks.sort((a, b) => a.price - b.price)
  
  orderBook.value = {
    bids,
    asks,
    spread: asks[0]?.price - bids[0]?.price || 0
  }
}

// Generate Price History
const generatePriceHistory = (currentPrice: number) => {
  const history: number[] = []
  const candles: Array<{ open: number, high: number, low: number, close: number }> = []
  const n = 100
  let price = currentPrice * 0.95
  
  for (let i = 0; i < n; i++) {
    const change = (Math.random() - 0.45) * 0.01
    price = Math.max(currentPrice * 0.9, Math.min(currentPrice * 1.1, price * (1 + change)))
    history.push(price)
    
    // Generate OHLC for candlestick
    const open = i === 0 ? price : candles[i - 1].close
    const volatility = currentPrice * 0.01
    const high = Math.max(open, price) + Math.random() * volatility
    const low = Math.min(open, price) - Math.random() * volatility
    const close = price
    
    candles.push({ open, high, low, close })
  }
  
  assetPriceHistory.value = history
  candlestickData.value = candles
}

// Initialize Asset Price Chart
const initAssetPriceChart = () => {
  if (!assetPriceChart.value || !selectedAsset.value) return
  
  const ctx = assetPriceChart.value.getContext('2d')
  if (!ctx) return
  
  if (assetChart) {
    assetChart.destroy()
  }
  
  const labels = Array.from({ length: assetPriceHistory.value.length }, (_, i) => {
    const date = new Date()
    date.setMinutes(date.getMinutes() - (assetPriceHistory.value.length - i))
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  })
  
  if (chartType.value === 'line') {
    // Line Chart
    assetChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Цена',
          data: assetPriceHistory.value,
          borderColor: selectedAsset.value.change >= 0 ? '#10b981' : '#ef4444',
          backgroundColor: selectedAsset.value.change >= 0 
            ? 'rgba(16, 185, 129, 0.1)' 
            : 'rgba(239, 68, 68, 0.1)',
          fill: true,
          tension: 0.4,
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            padding: 12,
            displayColors: false,
            callbacks: {
              label: (context: any) => {
                return `${formatPrice(context.parsed.y)} ₽`
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.05)'
            },
            border: {
              display: false
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.4)',
              font: {
                size: 10
              },
              maxTicksLimit: 8
            }
          },
          y: {
            grid: {
              color: 'rgba(255, 255, 255, 0.05)'
            },
            border: {
              display: false
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.4)',
              font: {
                size: 10
              },
              callback: (value) => formatPrice(Number(value))
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        }
      }
    })
  } else if (chartType.value === 'candlestick') {
    // Candlestick chart would go here
    // For now, just use line chart
    assetChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Цена',
          data: assetPriceHistory.value,
          borderColor: selectedAsset.value.change >= 0 ? '#10b981' : '#ef4444',
          backgroundColor: selectedAsset.value.change >= 0 
            ? 'rgba(16, 185, 129, 0.1)' 
            : 'rgba(239, 68, 68, 0.1)',
          fill: true,
          tension: 0.4,
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            padding: 12,
            displayColors: false,
            callbacks: {
              label: (context: any) => {
                return `${formatPrice(context.parsed.y)} ₽`
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.05)'
            },
            border: {
              display: false
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.4)',
              font: {
                size: 10
              },
              maxTicksLimit: 8
            }
          },
          y: {
            grid: {
              color: 'rgba(255, 255, 255, 0.05)'
            },
            border: {
              display: false
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.4)',
              font: {
                size: 10
              },
              callback: (value) => formatPrice(Number(value))
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        }
      }
    })
  }
}

// Watch chart type changes
watch(chartType, () => {
  if (selectedAsset.value) {
    setTimeout(() => {
      initAssetPriceChart()
    }, 100)
  }
})

// Get Asset Type Label
const getAssetTypeLabel = (type?: string) => {
  const labels: Record<string, string> = {
    'stock': 'Акция',
    'index': 'Индекс',
    'bond': 'Облигация',
    'fund': 'ПИФ',
    'currency': 'Валюта',
    'commodity': 'Сырье'
  }
  return labels[type || 'stock'] || 'Актив'
}

// Time (defined later)

// Market Selection
const activeMarket = ref('russia')
const markets = ref([
  { id: 'russia', name: 'Россия', code: 'MOEX', flag: '🇷🇺' },
  { id: 'usa', name: 'США', code: 'NYSE/NASDAQ', flag: '🇺🇸' },
  { id: 'europe', name: 'Европа', code: 'XETRA', flag: '🇪🇺' },
  { id: 'asia', name: 'Азия', code: 'Hong Kong', flag: '🌏' },
  { id: 'uk', name: 'Великобритания', code: 'LSE', flag: '🇬🇧' },
  { id: 'canada', name: 'Канада', code: 'TSX', flag: '🇨🇦' }
])

// Navigation Tabs
const activeTab = ref('stocks')
const navigationTabs = ref([
  { id: 'stocks', label: 'Акции', icon: '📈' },
  { id: 'indices', label: 'Индексы', icon: '📊' },
  { id: 'bonds', label: 'Облигации', icon: '💵' },
  { id: 'forex', label: 'Форекс', icon: '💱' },
  { id: 'news', label: 'Новости', icon: '📰' }
])

// Sorting
const sortColumn = ref<string | null>(null)
const sortDirection = ref<'asc' | 'desc'>('asc')

// Live Status
const isLive = ref(true)

// News Data
const corporateNews = ref([
  {
    title: 'Apple Announces Record Earnings',
    description: 'Компания Apple сообщила о рекордной прибыли в четвертом квартале, превысив ожидания аналитиков.',
    time: '5m ago',
    source: 'Bloomberg',
    sentiment: 'positive'
  },
  {
    title: 'Tesla Unveils New Model',
    description: 'Tesla представила новую модель электромобиля с улучшенной батареей и увеличенным запасом хода.',
    time: '1m ago',
    source: 'Reuters',
    sentiment: 'positive'
  },
  {
    title: 'Microsoft Cloud Revenue Surges',
    description: 'Microsoft сообщила о росте доходов от облачных сервисов на 25% в годовом исчислении.',
    time: '8m ago',
    source: 'CNBC',
    sentiment: 'positive'
  },
  {
    title: 'Amazon Expands Logistics Network',
    description: 'Amazon объявила о расширении логистической сети в Европе и Азии.',
    time: '12m ago',
    source: 'WSJ',
    sentiment: 'neutral'
  }
])

const macroNews = ref([
  {
    title: 'Global Inflation Concerns Rise',
    description: 'Международные эксперты выражают обеспокоенность ростом инфляции в развитых странах.',
    time: '3m ago',
    source: 'Financial Times',
    sentiment: 'negative'
  },
  {
    title: 'Interest Rates Held Steady by Fed',
    description: 'Федеральная резервная система США сохранила ключевую ставку на прежнем уровне.',
    time: '5m ago',
    source: 'Fed',
    sentiment: 'neutral'
  },
  {
    title: 'Russian Market Shows Strong Growth',
    description: 'Российский фондовый рынок демонстрирует устойчивый рост на фоне стабилизации экономики.',
    time: '7m ago',
    source: 'MOEX',
    sentiment: 'positive'
  },
  {
    title: 'OFZ Yields Decline',
    description: 'Доходность облигаций федерального займа снизилась на фоне улучшения макроэкономических показателей.',
    time: '10m ago',
    source: 'CBR',
    sentiment: 'positive'
  }
])

// Chart Refs
const chartRefs = ref<Record<string, HTMLCanvasElement | null>>({})
const selectedCharts = ref([
  { symbol: 'SBER' },
  { symbol: 'GAZP' },
  { symbol: 'LKOH' }
])

// Initialize Mini Charts (Candlestick style)
const initMiniCharts = () => {
  selectedCharts.value.forEach(chart => {
    const canvas = chartRefs.value[chart.symbol]
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    // Get stock data
    const stock = topStocks.value.find(s => s.symbol === chart.symbol)
    if (!stock) return
    
    // Generate candlestick data
    const candles: Array<{open: number, high: number, low: number, close: number}> = []
    const labels: string[] = []
    let price = stock.price
    for (let i = 0; i < 30; i++) {
      const open = price
      const change = (Math.random() - 0.5) * 0.03
      price = price * (1 + change)
      const close = price
      const high = Math.max(open, close) * (1 + Math.random() * 0.01)
      const low = Math.min(open, close) * (1 - Math.random() * 0.01)
      candles.push({ open, high, low, close })
      labels.push('')
    }
    
    // Create line chart that looks like candlestick
    const closePrices = candles.map(c => c.close)
    const isUp = closePrices[closePrices.length - 1] >= closePrices[0]
    
    new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: chart.symbol,
          data: closePrices,
          borderColor: isUp ? '#10b981' : '#ef4444',
          backgroundColor: isUp 
            ? 'rgba(16, 185, 129, 0.15)' 
            : 'rgba(239, 68, 68, 0.15)',
          fill: true,
          tension: 0.1,
          borderWidth: 1.5,
          pointRadius: 0,
          pointHoverRadius: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false }
        },
        scales: {
          x: { 
            display: false,
            grid: { display: false }
          },
          y: { 
            display: false,
            grid: { display: false }
          }
        },
        elements: {
          point: { radius: 0 }
        }
      }
    })
  })
}

// Major Indices (moved before marketData)
const majorIndices = ref([
  { symbol: 'IMOEX', name: 'Индекс МосБиржи', price: 3250.80, change: 0.28, volume: 125000000 },
  { symbol: 'RTSI', name: 'Индекс РТС', price: 1125.40, change: -0.15, volume: 45000000 },
  { symbol: 'MOEXBC', name: 'Индекс голубых фишек', price: 1850.20, change: 0.42, volume: 85000000 },
  { symbol: 'MOEXINN', name: 'Индекс инноваций', price: 2850.60, change: 0.35, volume: 35000000 },
  { symbol: 'MOEXIT', name: 'Индекс IT', price: 1450.30, change: 0.58, volume: 25000000 }
])

// Market Data by Region
const marketData = ref<Record<string, {
  stocks: Array<{symbol: string, name: string, price: number, change: number, volume: number}>
  indices: Array<{symbol: string, name: string, price: number, change: number, volume: number}>
}>>({
  russia: {
    stocks: [
      { symbol: 'SBER', name: 'Сбербанк', price: 285.50, change: 0.85, volume: 45200000 },
      { symbol: 'GAZP', name: 'Газпром', price: 178.20, change: 1.25, volume: 28500000 },
      { symbol: 'LKOH', name: 'Лукойл', price: 7420.80, change: 0.65, volume: 18500000 },
      { symbol: 'GMKN', name: 'Норникель', price: 15240.40, change: 1.15, volume: 32500000 },
      { symbol: 'YNDX', name: 'Яндекс', price: 2848.90, change: -0.45, volume: 12500000 },
      { symbol: 'ROSN', name: 'Роснефть', price: 485.20, change: 2.35, volume: 45000000 }
    ],
    indices: majorIndices.value
  },
  usa: {
    stocks: [
      { symbol: 'AAPL', name: 'Apple Inc.', price: 185.50, change: 1.25, volume: 85000000 },
      { symbol: 'MSFT', name: 'Microsoft', price: 380.20, change: 0.95, volume: 45000000 },
      { symbol: 'TSLA', name: 'Tesla', price: 245.80, change: -1.15, volume: 120000000 },
      { symbol: 'AMZN', name: 'Amazon', price: 152.30, change: 0.65, volume: 65000000 },
      { symbol: 'GOOGL', name: 'Alphabet', price: 142.50, change: 1.05, volume: 35000000 },
      { symbol: 'NVDA', name: 'NVIDIA', price: 485.20, change: 2.35, volume: 55000000 }
    ],
    indices: [
      { symbol: 'SPX', name: 'S&P 500', price: 4850.20, change: 0.45, volume: 0 },
      { symbol: 'DJI', name: 'Dow Jones', price: 39800.50, change: 0.25, volume: 0 },
      { symbol: 'IXIC', name: 'NASDAQ', price: 16250.80, change: 0.65, volume: 0 }
    ]
  },
  europe: {
    stocks: [
      { symbol: 'SAP', name: 'SAP SE', price: 145.20, change: 0.85, volume: 2500000 },
      { symbol: 'SIE', name: 'Siemens', price: 185.50, change: 1.15, volume: 1800000 },
      { symbol: 'ASML', name: 'ASML', price: 785.30, change: 0.95, volume: 1200000 }
    ],
    indices: [
      { symbol: 'DAX', name: 'DAX Index', price: 18500.20, change: 0.35, volume: 0 },
      { symbol: 'CAC', name: 'CAC 40', price: 7850.50, change: 0.25, volume: 0 }
    ]
  },
  asia: {
    stocks: [
      { symbol: 'TCEHY', name: 'Tencent', price: 45.20, change: 1.25, volume: 15000000 },
      { symbol: 'BABA', name: 'Alibaba', price: 85.50, change: -0.45, volume: 12000000 },
      { symbol: 'BIDU', name: 'Baidu', price: 125.80, change: 0.65, volume: 8500000 }
    ],
    indices: [
      { symbol: 'HSI', name: 'Hang Seng', price: 18500.20, change: 0.45, volume: 0 },
      { symbol: 'N225', name: 'Nikkei 225', price: 38500.50, change: 0.35, volume: 0 }
    ]
  },
  uk: {
    stocks: [
      { symbol: 'HSBC', name: 'HSBC Holdings', price: 685.20, change: 0.85, volume: 8500000 },
      { symbol: 'SHEL', name: 'Shell', price: 2850.50, change: 1.15, volume: 12000000 },
      { symbol: 'ULVR', name: 'Unilever', price: 4250.80, change: 0.45, volume: 5500000 }
    ],
    indices: [
      { symbol: 'FTSE', name: 'FTSE 100', price: 7850.20, change: 0.25, volume: 0 }
    ]
  },
  canada: {
    stocks: [
      { symbol: 'RCI', name: 'Rogers', price: 65.20, change: 0.85, volume: 2500000 },
      { symbol: 'BN', name: 'Brookfield', price: 45.50, change: 1.05, volume: 1800000 },
      { symbol: 'MSFT', name: 'Microsoft', price: 380.20, change: 0.95, volume: 45000000 }
    ],
    indices: [
      { symbol: 'TSX', name: 'TSX Composite', price: 21500.20, change: 0.35, volume: 0 }
    ]
  }
})

// Get Current Data Functions
const getCurrentIndices = () => {
  return marketData.value[activeMarket.value]?.indices || []
}

const getCurrentInstruments = () => {
  switch (activeTab.value) {
    case 'stocks':
      return marketData.value[activeMarket.value]?.stocks || []
    case 'bonds':
      return [...governmentBonds.value, ...corporateBonds.value].map((b: any) => ({
        symbol: b.symbol,
        name: b.maturity || '',
        price: 100,
        change: b.change,
        volume: 0,
        yield: b.yield
      }))
    case 'forex':
      return currencyPairs.value.map(c => ({
        symbol: c.symbol,
        name: c.symbol,
        price: parseFloat(c.price.replace(',', '.')),
        change: c.change,
        volume: 0
      }))
    default:
      return []
  }
}

const getFilteredInstruments = () => {
  const instruments = getCurrentInstruments()
  if (!searchQuery.value.trim()) return instruments
  const query = searchQuery.value.toLowerCase()
  return instruments.filter(item => 
    item.symbol.toLowerCase().includes(query) || 
    item.name.toLowerCase().includes(query)
  )
}

const getSortedData = () => {
  const data = getFilteredInstruments().map(item => ({
    ...item,
    bid: item.price * 0.9995,
    ask: item.price * 1.0005,
    changePercent: item.change
  }))
  
  if (!sortColumn.value) return data
  
  return [...data].sort((a, b) => {
    const aVal = (a as any)[sortColumn.value!]
    const bVal = (b as any)[sortColumn.value!]
    const comparison = aVal > bVal ? 1 : aVal < bVal ? -1 : 0
    return sortDirection.value === 'asc' ? comparison : -comparison
  })
}

const sortTable = (column: string) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'asc'
  }
}

const getActiveMarketName = () => {
  const market = markets.value.find(m => m.id === activeMarket.value)
  return market ? `${market.flag} ${market.name} (${market.code})` : 'Рынок'
}

const getTabTitle = () => {
  const tab = navigationTabs.value.find(t => t.id === activeTab.value)
  return tab ? tab.label : 'Данные'
}

const getSentimentLabel = (sentiment: string) => {
  const labels: Record<string, string> = {
    positive: 'Позитивно',
    negative: 'Негативно',
    neutral: 'Нейтрально'
  }
  return labels[sentiment] || 'Нейтрально'
}

// Current Time
const currentTime = ref('')
const updateCurrentTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('ru-RU', { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit'
  })
}

const getStockName = (symbol: string) => {
  const stock = topStocks.value.find(s => s.symbol === symbol)
  return stock?.name || symbol
}

// Market Ticker (Российские индексы и инструменты)
const marketTicker = ref([
  { symbol: 'IMOEX', price: 3250.80, change: 0.28 },
  { symbol: 'RTSI', price: 1125.40, change: -0.15 },
  { symbol: 'MOEXBC', price: 1850.20, change: 0.42 },
  { symbol: 'MOEXINN', price: 2850.60, change: 0.35 },
  { symbol: 'RVI', price: 18.45, change: -1.20 },
  { symbol: 'USD/RUB', price: 92.45, change: -0.25 },
  { symbol: 'EUR/RUB', price: 101.30, change: -0.18 },
  { symbol: 'CNY/RUB', price: 12.85, change: 0.12 },
  { symbol: 'Нефть Brent', price: 78.20, change: -0.35 },
  { symbol: 'Золото', price: 6250.50, change: 0.42 }
])


// Currency Pairs (Российские валютные пары)
const currencyPairs = ref([
  { symbol: 'USD/RUB', price: '92.45', change: -0.25 },
  { symbol: 'EUR/RUB', price: '101.30', change: -0.18 },
  { symbol: 'CNY/RUB', price: '12.85', change: 0.12 },
  { symbol: 'GBP/RUB', price: '117.20', change: 0.08 },
  { symbol: 'JPY/RUB', price: '0.62', change: 0.05 },
  { symbol: 'TRY/RUB', price: '2.85', change: -0.15 }
])

// Commodities (Сырьевые товары)
const commodities = ref([
  { symbol: 'BRENT', name: 'Нефть Brent', price: 78.20, change: -0.35 },
  { symbol: 'WTI', name: 'Нефть WTI', price: 73.50, change: -0.42 },
  { symbol: 'GOLD', name: 'Золото', price: 6250.50, change: 0.42 },
  { symbol: 'SILVER', name: 'Серебро', price: 75.20, change: 0.68 },
  { symbol: 'GAS', name: 'Природный газ', price: 2850.00, change: 1.25 }
])

// Top Stocks (Российские акции)
const topStocks = ref([
  { symbol: 'SBER', name: 'Сбербанк', price: 285.50, change: 0.85, volume: 45200000 },
  { symbol: 'GAZP', name: 'Газпром', price: 178.20, change: 1.25, volume: 28500000 },
  { symbol: 'LKOH', name: 'Лукойл', price: 7420.80, change: 0.65, volume: 18500000 },
  { symbol: 'GMKN', name: 'Норникель', price: 15240.40, change: 1.15, volume: 32500000 },
  { symbol: 'YNDX', name: 'Яндекс', price: 2848.90, change: -0.45, volume: 12500000 },
  { symbol: 'ROSN', name: 'Роснефть', price: 485.20, change: 2.35, volume: 45000000 },
  { symbol: 'NVTK', name: 'Новатэк', price: 1365.80, change: 0.95, volume: 18500000 },
  { symbol: 'TATN', name: 'Татнефть', price: 625.60, change: 0.55, volume: 8500000 },
  { symbol: 'MGNT', name: 'Магнит', price: 7850.30, change: -0.25, volume: 12000000 },
  { symbol: 'ALRS', name: 'Алроса', price: 95.40, change: 1.85, volume: 15000000 },
  { symbol: 'PLZL', name: 'Полюс', price: 12580.50, change: 1.45, volume: 8500000 },
  { symbol: 'CHMF', name: 'Северсталь', price: 1850.20, change: 0.75, volume: 12000000 },
  { symbol: 'MOEX', name: 'МосБиржа', price: 245.80, change: -0.15, volume: 5500000 },
  { symbol: 'VTBR', name: 'ВТБ', price: 0.035, change: 0.12, volume: 850000000 },
  { symbol: 'AFKS', name: 'АФК Система', price: 12.85, change: -0.35, volume: 25000000 }
])

// Government Bonds (ОФЗ)
const governmentBonds = ref([
  { symbol: 'ОФЗ 26207', maturity: '2025', yield: 13.25, change: -0.05 },
  { symbol: 'ОФЗ 26208', maturity: '2027', yield: 13.45, change: -0.08 },
  { symbol: 'ОФЗ 26209', maturity: '2030', yield: 13.65, change: -0.12 },
  { symbol: 'ОФЗ 26210', maturity: '2033', yield: 13.85, change: -0.15 },
  { symbol: 'ОФЗ 26211', maturity: '2035', yield: 14.05, change: -0.18 },
  { symbol: 'ОФЗ 26212', maturity: '2040', yield: 14.20, change: -0.20 }
])

// Corporate Bonds (Корпоративные облигации)
const corporateBonds = ref([
  { symbol: 'СберБ-001Р-05', maturity: '2025', yield: 14.25, change: -0.10 },
  { symbol: 'Газпром-32', maturity: '2026', yield: 14.45, change: -0.12 },
  { symbol: 'Лукойл-002Р-03', maturity: '2027', yield: 14.65, change: -0.15 },
  { symbol: 'Роснефть-001Р-04', maturity: '2028', yield: 14.85, change: -0.18 },
  { symbol: 'ВТБ-20-1', maturity: '2029', yield: 15.05, change: -0.20 },
  { symbol: 'Альфа-Банк-001Р-02', maturity: '2030', yield: 15.25, change: -0.22 }
])

// ПИФы (Паевые инвестиционные фонды)
const pifs = ref([
  { name: 'Сбербанк - Фонд облигаций', price: 1250.50, change: 0.25, yield: 12.5 },
  { name: 'ВТБ - Фонд акций', price: 1850.30, change: 0.85, yield: 15.2 },
  { name: 'Альфа-Капитал - Сбалансированный', price: 1520.80, change: 0.45, yield: 13.8 },
  { name: 'Газпромбанк - Фонд облигаций', price: 1120.20, change: 0.15, yield: 11.9 },
  { name: 'Райффайзен - Фонд акций', price: 1950.60, change: 1.25, yield: 16.5 },
  { name: 'Открытие - Индексный фонд', price: 1450.40, change: 0.35, yield: 14.2 },
  { name: 'Тинькофф - Фонд облигаций', price: 1180.90, change: 0.20, yield: 12.1 },
  { name: 'Сбербанк - Фонд акций', price: 1750.70, change: 0.95, yield: 15.8 }
])

// Market Statistics (Российский рынок)
const marketStats = ref({
  rvi: 18.45,  // RVI Index (аналог VIX для России)
  rviChange: -1.20,
  totalMarketCap: 45000000000000,  // Капитализация в рублях
  marketCapChange: 0.45,
  advancing: 1850,
  declining: 1250,
  newHighs: 125,
  newLows: 45
})

// Update functions
const updateMarketData = () => {
  // Update ticker
  marketTicker.value.forEach(item => {
    const change = (Math.random() - 0.5) * 0.1
    item.price = Math.max(0, item.price * (1 + change / 100))
    item.change += change
  })

  // Update indices
  majorIndices.value.forEach(index => {
    const change = (Math.random() - 0.5) * 0.15
    index.price = Math.max(0, index.price * (1 + change / 100))
    index.change += change
    index.volume = Math.floor(index.volume * (0.9 + Math.random() * 0.2))
  })

  // Update stocks
  topStocks.value.forEach(stock => {
    const change = (Math.random() - 0.5) * 0.2
    stock.price = Math.max(0, stock.price * (1 + change / 100))
    stock.change += change
    stock.volume = Math.floor(stock.volume * (0.8 + Math.random() * 0.4))
  })

  // Update PIFs
  pifs.value.forEach(fund => {
    const change = (Math.random() - 0.5) * 0.15
    fund.price = Math.max(0, fund.price * (1 + change / 100))
    fund.change += change
  })

  // Update bonds (smaller changes)
  governmentBonds.value.forEach(bond => {
    const change = (Math.random() - 0.5) * 0.05
    bond.yield = Math.max(0, bond.yield + change)
    bond.change += change
  })

  // Update stats
  marketStats.value.rvi = Math.max(10, Math.min(30, marketStats.value.rvi + (Math.random() - 0.5) * 0.5))
  marketStats.value.rviChange = (Math.random() - 0.5) * 0.3
  marketStats.value.marketCapChange = (Math.random() - 0.5) * 0.2
}

// Formatting functions
const formatPrice = (price: number): string => {
  if (price >= 1000) {
    return price.toLocaleString('ru-RU', { maximumFractionDigits: 2 })
  }
  return price.toFixed(2)
}

const formatVolume = (volume: number): string => {
  if (volume >= 1000000000) {
    return (volume / 1000000000).toFixed(2) + 'B'
  }
  if (volume >= 1000000) {
    return (volume / 1000000).toFixed(2) + 'M'
  }
  if (volume >= 1000) {
    return (volume / 1000).toFixed(2) + 'K'
  }
  return volume.toString()
}

const formatCurrency = (value: number): string => {
  if (value >= 1000000000000) {
    return (value / 1000000000000).toFixed(2) + 'T'
  }
  if (value >= 1000000000) {
    return (value / 1000000000).toFixed(2) + 'B'
  }
  return value.toLocaleString('ru-RU')
}

const formatChange = (change: number): string => {
  const absChange = Math.abs(change)
  if (absChange >= 100) {
    return absChange.toFixed(2)
  }
  if (absChange >= 10) {
    return absChange.toFixed(2)
  }
  return absChange.toFixed(2)
}

// ============================================
// LIQUIDITY SURFACE DASHBOARD
// ============================================

const priceStreamChart = ref<SVGElement | null>(null)
const signalMatrixChart = ref<SVGElement | null>(null)

// Liquidity State
const liquidityTimestamp = ref('2018-01-23 15:42:18')
const liquidityParams = ref({
  flowPressure: 0.75,
  liquidity: 0.65,
  timeEvolution: 0.0
})

// Price Stream Data
const priceStreamData = ref<number[]>([])
const currentPrice = ref(285.50)
const priceChange = ref(0.85)
const priceEndY = ref(100)

// Flow Metrics
const bidFlow = ref(45.2)
const askFlow = ref(38.7)
const maxFlow = ref(100)
const volume24h = ref(125.8)
const avgVolume = ref(95.3)
const peakVolume = ref(185.6)
const liquidityStress = ref(0.35)
const avgSpread = ref(0.0012)

// Generate Price Stream Data
const generatePriceStream = () => {
  const n = 200
  const data: number[] = []
  let price = currentPrice.value
  
  for (let i = 0; i < n; i++) {
    // Brownian motion with drift
    const drift = 0.01
    const volatility = 0.3
    const random = (Math.random() * 2 - 1) * Math.sqrt(3)
    price = Math.max(250, Math.min(320, price + drift + volatility * random))
    data.push(price)
  }
  
  priceStreamData.value = data
  currentPrice.value = price
  priceEndY.value = 200 - ((price - 250) / 70) * 200
}

// Price Stream Paths
const priceLinePath = computed(() => {
  if (priceStreamData.value.length === 0) return ''
  const width = 800
  const height = 200
  const n = priceStreamData.value.length
  const minPrice = 250
  const maxPrice = 320
  const range = maxPrice - minPrice
  
  let path = `M 0 ${height - ((priceStreamData.value[0] - minPrice) / range) * height}`
  for (let i = 1; i < n; i++) {
    const x = (i / (n - 1)) * width
    const y = height - ((priceStreamData.value[i] - minPrice) / range) * height
    path += ` L ${x} ${y}`
  }
  return path
})

const priceAreaPath = computed(() => {
  if (priceStreamData.value.length === 0) return ''
  const line = priceLinePath.value
  const width = 800
  const height = 200
  return `${line} L ${width} ${height} L 0 ${height} Z`
})

// Update Liquidity Data
const updateLiquidityData = () => {
  // Update timestamp
  const now = new Date()
  liquidityTimestamp.value = now.toISOString().slice(0, 19).replace('T', ' ')
  
  // Update price stream
  if (priceStreamData.value.length > 0) {
    const lastPrice = priceStreamData.value[priceStreamData.value.length - 1]
    const drift = 0.01
    const volatility = 0.3
    const random = (Math.random() * 2 - 1) * Math.sqrt(3)
    const newPrice = Math.max(250, Math.min(320, lastPrice + drift + volatility * random))
    priceStreamData.value.push(newPrice)
    
    if (priceStreamData.value.length > 200) {
      priceStreamData.value.shift()
    }
    
    currentPrice.value = newPrice
    priceChange.value = ((newPrice - priceStreamData.value[0]) / priceStreamData.value[0]) * 100
    priceEndY.value = 200 - ((newPrice - 250) / 70) * 200
  }
  
  // Update signal matrix
  generateSignalMatrix()
  
  // Update flow metrics
  bidFlow.value = Math.max(20, Math.min(80, bidFlow.value + (Math.random() - 0.5) * 2))
  askFlow.value = Math.max(20, Math.min(80, askFlow.value + (Math.random() - 0.5) * 2))
  maxFlow.value = Math.max(bidFlow.value, askFlow.value) * 1.2
  
  // Update volume
  volume24h.value = 120 + Math.random() * 20
  avgVolume.value = 90 + Math.random() * 15
  peakVolume.value = 180 + Math.random() * 20
  
  // Update liquidity stress
  const imbalance = Math.abs(bidFlow.value - askFlow.value) / maxFlow.value
  liquidityStress.value = Math.max(0, Math.min(1, imbalance + (Math.random() - 0.5) * 0.1))
  
  // Update spread
  avgSpread.value = 0.001 + liquidityStress.value * 0.002 + (Math.random() - 0.5) * 0.0005
  
  // Update surface parameters
  liquidityParams.value.flowPressure = 0.5 + Math.sin(liquidityParams.value.timeEvolution) * 0.3
  liquidityParams.value.liquidity = 0.4 + Math.cos(liquidityParams.value.timeEvolution * 0.7) * 0.3
}

// ============================================
// PLOTLY LOADER
// ============================================
let Plotly: any = null
const loadPlotly = async () => {
  if (typeof window !== 'undefined' && !(window as any).Plotly) {
    return new Promise((resolve) => {
      const script = document.createElement('script')
      script.src = 'https://cdn.plot.ly/plotly-latest.min.js'
      script.async = true
      script.onload = () => {
        Plotly = (window as any).Plotly
        resolve(Plotly)
      }
      document.head.appendChild(script)
    })
  }
  Plotly = (window as any).Plotly
  return Plotly
}

// ============================================
// QUANTLATENT v9.2
// ============================================

// QuantLatent State
const wireframeCanvas = ref<HTMLCanvasElement | null>(null)
const growthChart = ref<SVGElement | null>(null)
const currentEpoch = ref(1)
const liquidityPercent = ref(10.78)

// Wireframe Parameters
const wireframeParams = ref({
  frequency: 0.5,
  amplitude: 2.0
})

// Wireframe Animation
let wireframeTime = 0
let wireframeAnimationId: number | null = null

// Growth Chart Data
const growthData = ref<number[]>([])
const growthStartY = ref(150)
const growthEndY = ref(50)

// Orderbook Data
const orderbookData = ref([
  { name: 'SPX_LIQ', value: 3.02 },
  { name: 'NDX_FLOW', value: 2.87 },
  { name: 'RTS_VOL', value: 2.34 },
  { name: 'EUR_FX', value: 2.15 },
  { name: 'BTC_SPOT', value: 1.98 },
  { name: 'GOLD_FUT', value: 1.76 },
  { name: 'OIL_WTI', value: 1.54 },
  { name: 'BOND_10Y', value: 1.32 }
])

// QuantLatent Metrics
const metricsQuantlatent = ref({
  sharpe: 99.98,
  latency: 1.04,
  maxReturn: 18.2,
  drawdown: -2.45,
  volatility: 12.8,
  flow: 245.6
})

// Generate Wireframe Points
const generateWireframe = (time: number) => {
  const points: Array<{ x: number, y: number, z: number }> = []
  const step = 0.5
  const range = 5
  
  for (let x = -range; x <= range; x += step) {
    for (let y = -range; y <= range; y += step) {
      const z = Math.sin(x * wireframeParams.value.frequency + time) * Math.cos(y * wireframeParams.value.frequency + time) * wireframeParams.value.amplitude
      points.push({ x, y, z })
    }
  }
  
  return points
}

// Project 3D to 2D (Isometric)
const project3D = (x: number, y: number, z: number, width: number, height: number) => {
  const scale = 15
  const isoX = (x - y) * Math.cos(Math.PI / 6) * scale
  const isoY = ((x + y) * Math.sin(Math.PI / 6) - z) * scale
  return {
    x: width / 2 + isoX,
    y: height / 2 + isoY
  }
}

// Draw Wireframe
const drawWireframe = () => {
  if (!wireframeCanvas.value) return
  
  const canvas = wireframeCanvas.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const width = canvas.width
  const height = canvas.height
  
  // Clear
  ctx.fillStyle = '#000000'
  ctx.fillRect(0, 0, width, height)
  
  // Generate points
  const points = generateWireframe(wireframeTime)
  const gridSize = Math.sqrt(points.length)
  
  // Draw wireframe
  ctx.strokeStyle = '#2a2a2a'
  ctx.lineWidth = 0.5
  
  // Draw horizontal lines
  for (let i = 0; i < gridSize; i++) {
    ctx.beginPath()
    let first = true
    for (let j = 0; j < gridSize; j++) {
      const idx = i * gridSize + j
      const point = points[idx]
      const proj = project3D(point.x, point.y, point.z, width, height)
      
      if (first) {
        ctx.moveTo(proj.x, proj.y)
        first = false
      } else {
        ctx.lineTo(proj.x, proj.y)
      }
    }
    ctx.stroke()
  }
  
  // Draw vertical lines
  for (let j = 0; j < gridSize; j++) {
    ctx.beginPath()
    let first = true
    for (let i = 0; i < gridSize; i++) {
      const idx = i * gridSize + j
      const point = points[idx]
      const proj = project3D(point.x, point.y, point.z, width, height)
      
      if (first) {
        ctx.moveTo(proj.x, proj.y)
        first = false
      } else {
        ctx.lineTo(proj.x, proj.y)
      }
    }
    ctx.stroke()
  }
  
  // Update time
  wireframeTime += 0.02
}

// Initialize Wireframe
const initWireframe = () => {
  if (!wireframeCanvas.value) return
  
  const canvas = wireframeCanvas.value
  canvas.width = 400
  canvas.height = 200
  
  const animate = () => {
    drawWireframe()
    wireframeAnimationId = requestAnimationFrame(animate)
  }
  animate()
}

// Generate Growth Data
const generateGrowthData = () => {
  const n = 500
  const data: number[] = []
  let value = 50
  
  for (let i = 0; i < n; i++) {
    // Brownian Motion with upward drift
    const drift = 0.05
    const volatility = 0.3
    const random = (Math.random() * 2 - 1) * Math.sqrt(3) // Approximate normal
    value = Math.max(10, Math.min(190, value + drift + volatility * random))
    data.push(value)
  }
  
  growthData.value = data
  growthStartY.value = 200 - data[0]
  growthEndY.value = 200 - data[data.length - 1]
}

// Growth Chart Paths
const growthLinePath = computed(() => {
  if (growthData.value.length === 0) return ''
  const width = 800
  const height = 200
  const n = growthData.value.length
  
  let path = `M 0 ${height - growthData.value[0]}`
  for (let i = 1; i < n; i++) {
    const x = (i / (n - 1)) * width
    const y = height - growthData.value[i]
    path += ` L ${x} ${y}`
  }
  return path
})

const growthAreaPath = computed(() => {
  if (growthData.value.length === 0) return ''
  const line = growthLinePath.value
  const width = 800
  const height = 200
  return `${line} L ${width} ${height} L 0 ${height} Z`
})

// Update QuantLatent Data
const updateQuantLatentData = () => {
  // Update epoch
  currentEpoch.value++
  
  // Update liquidity percent (Brownian Motion)
  const drift = 0.01
  const volatility = 0.5
  const random = (Math.random() * 2 - 1) * Math.sqrt(3)
  liquidityPercent.value = Math.max(5, Math.min(20, liquidityPercent.value + drift + volatility * random))
  
  // Update orderbook (small random changes)
  orderbookData.value.forEach(row => {
    const change = (Math.random() - 0.5) * 0.1
    row.value = Math.max(1.0, row.value + change)
  })
  
  // Sort orderbook by value
  orderbookData.value.sort((a, b) => b.value - a.value)
  
  // Update metrics
  metricsQuantlatent.value.sharpe = 99.0 + Math.random() * 2
  metricsQuantlatent.value.latency = 0.8 + Math.random() * 0.5
  metricsQuantlatent.value.maxReturn = 17.5 + Math.random() * 1.5
  metricsQuantlatent.value.drawdown = -2.0 - Math.random() * 1.0
  metricsQuantlatent.value.volatility = 12.0 + Math.random() * 2.0
  metricsQuantlatent.value.flow = 240 + Math.random() * 15
  
  // Update growth data (append new point)
  if (growthData.value.length > 0) {
    const lastValue = growthData.value[growthData.value.length - 1]
    const drift = 0.05
    const volatility = 0.3
    const random = (Math.random() * 2 - 1) * Math.sqrt(3)
    const newValue = Math.max(10, Math.min(190, lastValue + drift + volatility * random))
    growthData.value.push(newValue)
    
    // Keep only last 500 points
    if (growthData.value.length > 500) {
      growthData.value.shift()
    }
    
    growthEndY.value = 200 - newValue
  }
  
  // Update wireframe parameters (slow drift)
  wireframeParams.value.frequency = 0.45 + Math.sin(wireframeTime * 0.1) * 0.1
  wireframeParams.value.amplitude = 1.8 + Math.cos(wireframeTime * 0.15) * 0.4
}

// ============================================
// VOLATILITY TRADING SYSTEM DASHBOARD
// ============================================

// Equity Chart
const equityChart = ref<SVGElement | null>(null)
const hoverPoint = ref<{ x: number, yStrategy: number, yBenchmark: number, strategyValue: number, benchmarkValue: number, date: string } | null>(null)

// Equity Curve Data
const equityData = ref<Array<{ date: Date, strategyValue: number, benchmarkValue: number }>>([])

// Performance Statistics
const performanceStats = ref({
  totalReturn: 47.2,
  sharpe: 2.34,
  maxDrawdown: -8.5,
  winRate: 67.8,
  avgWinLoss: 2.1
})

// Signal Aggregation Model
const calculatePosition = (signals: number[], riskBudget: number, threshold: number = 0.5): number => {
  const J = signals.length
  const confirmingSignals = signals.filter(s => s > threshold).length
  return (riskBudget / J) * confirmingSignals
}

// Generate P&L Surface
const generatePnLSurface = (timePoints: number = 30, regimePoints: number = 20): number[][] => {
  const surface: number[][] = []
  
  for (let t = 0; t < timePoints; t++) {
    const row: number[] = []
    for (let r = 0; r < regimePoints; r++) {
      // Симуляция P&L с учетом волатильности
      const volatility = Math.sin(r * 0.1) * 0.5 + 1
      const trend = t * 1000  // Восходящий тренд
      const noise = (Math.random() - 0.5) * 2000
      
      row.push(trend * volatility + noise)
    }
    surface.push(row)
  }
  
  return surface
}

// Calculate Equity Curve
const calculateEquityCurve = (initialCapital: number = 100000, days: number = 90): Array<{ date: Date, strategyValue: number, benchmarkValue: number }> => {
  const data: Array<{ date: Date, strategyValue: number, benchmarkValue: number }> = []
  let strategyEquity = initialCapital
  let benchmarkEquity = initialCapital
  
  // Генерируем дневные доходности для стратегии (более волатильные, но с положительным трендом)
  for (let i = 0; i < days; i++) {
    // Стратегия: более высокая доходность с волатильностью
    const strategyReturn = (Math.random() - 0.3) * 0.02 + 0.003  // Средняя доходность ~0.3% в день
    strategyEquity *= (1 + strategyReturn)
    
    // Бенчмарк: стабильный рост S&P 500
    const benchmarkReturn = 0.0003  // ~0.03% в день
    benchmarkEquity *= (1 + benchmarkReturn)
    
    data.push({
      date: new Date(2021, 8, i + 1), // Сентябрь 2021
      strategyValue: strategyEquity,
      benchmarkValue: benchmarkEquity
    })
  }
  
  return data
}

// Equity Chart Paths
const strategyLinePath = computed(() => {
  if (equityData.value.length === 0) return ''
  const width = 1000
  const height = 400
  const n = equityData.value.length
  
  const minValue = Math.min(
    ...equityData.value.map(d => Math.min(d.strategyValue, d.benchmarkValue))
  )
  const maxValue = Math.max(
    ...equityData.value.map(d => Math.max(d.strategyValue, d.benchmarkValue))
  )
  const range = maxValue - minValue || 1
  
  let path = `M 0 ${height - ((equityData.value[0].strategyValue - minValue) / range) * height}`
  for (let i = 1; i < n; i++) {
    const x = (i / (n - 1)) * width
    const y = height - ((equityData.value[i].strategyValue - minValue) / range) * height
    path += ` L ${x} ${y}`
  }
  return path
})

const strategyAreaPath = computed(() => {
  if (equityData.value.length === 0) return ''
  const line = strategyLinePath.value
  const width = 1000
  const height = 400
  return `${line} L ${width} ${height} L 0 ${height} Z`
})

const benchmarkLinePath = computed(() => {
  if (equityData.value.length === 0) return ''
  const width = 1000
  const height = 400
  const n = equityData.value.length
  
  const minValue = Math.min(
    ...equityData.value.map(d => Math.min(d.strategyValue, d.benchmarkValue))
  )
  const maxValue = Math.max(
    ...equityData.value.map(d => Math.max(d.strategyValue, d.benchmarkValue))
  )
  const range = maxValue - minValue || 1
  
  let path = `M 0 ${height - ((equityData.value[0].benchmarkValue - minValue) / range) * height}`
  for (let i = 1; i < n; i++) {
    const x = (i / (n - 1)) * width
    const y = height - ((equityData.value[i].benchmarkValue - minValue) / range) * height
    path += ` L ${x} ${y}`
  }
  return path
})

// Initialize P&L Surface with Plotly
const initPnLSurface = async () => {
  try {
    await loadPlotly()
    if (!Plotly) {
      console.error('Plotly not loaded')
      return
    }
    
    const container = document.getElementById('pnl-surface-3d')
    if (!container) {
      console.error('Container pnl-surface-3d not found')
      return
    }
    
    const timePoints = 30
    const regimePoints = 20
    
    // Generate surface data
    const z = generatePnLSurface(timePoints, regimePoints)
    const x = Array.from({ length: timePoints }, (_, i) => i)
    const y = Array.from({ length: regimePoints }, (_, i) => i / regimePoints)
    
    const trace = {
      x: x,
      y: y,
      z: z,
      type: 'surface',
      colorscale: [
        [0, '#ef4444'],    // Red for losses
        [0.5, '#888888'],  // Gray for neutral
        [1, '#00ff88']     // Green for profits
      ],
      showscale: true,
      colorbar: {
        title: 'P&L ($)',
        titlefont: { color: 'rgba(255,255,255,0.9)', size: 11 },
        tickfont: { color: 'rgba(255,255,255,0.7)', size: 9 }
      },
      wireframe: {
        show: true,
        color: '#000000'
      },
      lighting: {
        ambient: 0.4,
        diffuse: 0.6,
        specular: 0.2
      }
    }
    
    const layout = {
      scene: {
        xaxis: { 
          title: 'Time/Date',
          backgroundcolor: 'rgba(0,0,0,0)',
          gridcolor: 'rgba(255,255,255,0.1)',
          showbackground: true,
          titlefont: { color: 'rgba(255,255,255,0.9)', size: 12 },
          tickfont: { size: 10, color: 'rgba(255,255,255,0.6)' }
        },
        yaxis: { 
          title: 'Volatility Regime',
          backgroundcolor: 'rgba(0,0,0,0)',
          gridcolor: 'rgba(255,255,255,0.1)',
          showbackground: true,
          titlefont: { color: 'rgba(255,255,255,0.9)', size: 12 },
          tickfont: { size: 10, color: 'rgba(255,255,255,0.6)' }
        },
        zaxis: { 
          title: 'Cumulative P&L ($)',
          backgroundcolor: 'rgba(0,0,0,0)',
          gridcolor: 'rgba(255,255,255,0.1)',
          showbackground: true,
          titlefont: { color: 'rgba(255,255,255,0.9)', size: 12 },
          tickfont: { size: 10, color: 'rgba(255,255,255,0.6)' }
        },
        camera: {
          eye: { x: 1.5, y: 1.5, z: 1.3 },
          center: { x: 0, y: 0, z: 0 },
          up: { x: 0, y: 0, z: 1 }
        },
        bgcolor: 'rgba(0,0,0,0)'
      },
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: { color: '#fff', family: 'system-ui' },
      margin: { l: 0, r: 0, b: 0, t: 0 },
      autosize: true
    }
    
    const config = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
      modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
      toImageButtonOptions: {
        format: 'png',
        filename: 'pnl-surface'
      }
    }
    
    Plotly.newPlot(container, [trace], layout, config)
    
    // Hover tooltip is handled automatically by Plotly
    
  } catch (err) {
    console.error('Error initializing P&L Surface:', err)
  }
}

// Setup Equity Chart Hover
const setupEquityChartHover = () => {
  if (!equityChart.value) return
  
  equityChart.value.addEventListener('mousemove', (e) => {
    const rect = equityChart.value!.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width) * 1000
    const index = Math.round((x / 1000) * (equityData.value.length - 1))
    
    if (index >= 0 && index < equityData.value.length) {
      const point = equityData.value[index]
      const height = 400
      const minValue = Math.min(
        ...equityData.value.map(d => Math.min(d.strategyValue, d.benchmarkValue))
      )
      const maxValue = Math.max(
        ...equityData.value.map(d => Math.max(d.strategyValue, d.benchmarkValue))
      )
      const range = maxValue - minValue || 1
      
      hoverPoint.value = {
        x,
        yStrategy: height - ((point.strategyValue - minValue) / range) * height,
        yBenchmark: height - ((point.benchmarkValue - minValue) / range) * height,
        strategyValue: point.strategyValue,
        benchmarkValue: point.benchmarkValue,
        date: point.date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
      }
    }
  })
  
  equityChart.value.addEventListener('mouseleave', () => {
    hoverPoint.value = null
  })
}

// Calculate Performance Stats
const calculatePerformanceStats = () => {
  if (equityData.value.length === 0) return
  
  const initialValue = 100000
  const finalValue = equityData.value[equityData.value.length - 1].strategyValue
  performanceStats.value.totalReturn = ((finalValue - initialValue) / initialValue) * 100
  
  // Calculate returns
  const returns: number[] = []
  for (let i = 1; i < equityData.value.length; i++) {
    const ret = (equityData.value[i].strategyValue - equityData.value[i - 1].strategyValue) / equityData.value[i - 1].strategyValue
    returns.push(ret)
  }
  
  // Sharpe Ratio (simplified)
  const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length
  const stdDev = Math.sqrt(
    returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length
  )
  performanceStats.value.sharpe = stdDev > 0 ? (avgReturn / stdDev) * Math.sqrt(252) : 0
  
  // Max Drawdown
  let peak = initialValue
  let maxDD = 0
  for (let i = 0; i < equityData.value.length; i++) {
    if (equityData.value[i].strategyValue > peak) peak = equityData.value[i].strategyValue
    const dd = ((equityData.value[i].strategyValue - peak) / peak) * 100
    if (dd < maxDD) maxDD = dd
  }
  performanceStats.value.maxDrawdown = maxDD
  
  // Win Rate
  const wins = returns.filter(r => r > 0).length
  performanceStats.value.winRate = (wins / returns.length) * 100
  
  // Avg Win/Loss
  const winsList = returns.filter(r => r > 0)
  const lossesList = returns.filter(r => r < 0)
  const avgWin = winsList.length > 0 ? winsList.reduce((a, b) => a + b, 0) / winsList.length : 0
  const avgLoss = lossesList.length > 0 ? Math.abs(lossesList.reduce((a, b) => a + b, 0) / lossesList.length) : 1
  performanceStats.value.avgWinLoss = avgLoss > 0 ? avgWin / avgLoss : 0
}

// ============================================
// QUANT ALPHA TERMINAL
// ============================================

// Terminal State
const terminalVix = ref(14.20)
const threeCanvas = ref<HTMLCanvasElement | null>(null)
const backtestChart = ref<SVGElement | null>(null)
const redVolChart = ref<SVGElement | null>(null)
const greenVolChart = ref<SVGElement | null>(null)
const consoleContent = ref<HTMLElement | null>(null)

// Three.js variables
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let renderer: THREE.WebGLRenderer | null = null
let mesh: THREE.Mesh | null = null
let animationId: number | null = null
let mouseX = 0
let mouseY = 0

// GBM Parameters
const gbmParams = ref({
  drift: 0.05,
  volatility: 0.15,
  lookback: 200
})

// GBM Simulation Data
const gbmData = ref<number[]>([])
const backtestData = ref<{ buyHold: number[], orca: number[] }>({
  buyHold: [],
  orca: []
})
const redVolData = ref<number[]>([])
const greenVolData = ref<number[]>([])

// Metrics
const metrics = ref({
  sharpe: 1.42,
  maxDrawdown: -12.5,
  var: -2.8,
  totalReturn: 24.5
})

// Terminal Logs
const terminalLogs = ref<Array<{ time: string, message: string, type: string }>>([
  { time: '10:42:15', message: 'System initialized', type: 'info' },
  { time: '10:42:16', message: 'GBM simulation started', type: 'info' },
  { time: '10:42:17', message: '3D manifold rendering...', type: 'info' },
  { time: '10:42:18', message: 'Latent volatility field computed', type: 'success' },
  { time: '10:42:19', message: 'Sharpe ratio: 1.42', type: 'metric' },
  { time: '10:42:20', message: 'Max DD: -12.5%', type: 'warning' }
])

// Geometric Brownian Motion Simulation
const generateGBM = (S0: number = 100, n: number = 200): number[] => {
  const dt = 1 / 252 // Daily
  const data: number[] = [S0]
  
  for (let i = 1; i < n; i++) {
    const dW = Math.sqrt(dt) * (Math.random() * 2 - 1) * Math.sqrt(3) // Approximate normal
    const dS = gbmParams.value.drift * data[i - 1] * dt + gbmParams.value.volatility * data[i - 1] * dW
    data.push(Math.max(0, data[i - 1] + dS))
  }
  
  return data
}

// Generate Backtest Data
const generateBacktestData = () => {
  const n = gbmParams.value.lookback
  const buyHold = generateGBM(100, n)
  const orca = generateGBM(100, n).map((val, i) => {
    // ORCA strategy with some alpha
    const alpha = 0.02 * Math.sin(i / 20)
    return val * (1 + alpha)
  })
  
  backtestData.value = { buyHold, orca }
  gbmData.value = buyHold
  
  // Calculate metrics
  calculateMetrics(buyHold, orca)
}

// Calculate Performance Metrics
const calculateMetrics = (buyHold: number[], orca: number[]) => {
  // Returns
  const buyHoldReturns = buyHold.slice(1).map((val, i) => (val - buyHold[i]) / buyHold[i])
  const orcaReturns = orca.slice(1).map((val, i) => (val - orca[i]) / orca[i])
  
  // Total Return
  const buyHoldReturn = ((buyHold[buyHold.length - 1] - buyHold[0]) / buyHold[0]) * 100
  const orcaReturn = ((orca[orca.length - 1] - orca[0]) / orca[0]) * 100
  
  metrics.value.totalReturn = orcaReturn
  
  // Sharpe Ratio (simplified)
  const avgReturn = orcaReturns.reduce((a, b) => a + b, 0) / orcaReturns.length
  const stdDev = Math.sqrt(
    orcaReturns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / orcaReturns.length
  )
  metrics.value.sharpe = stdDev > 0 ? (avgReturn / stdDev) * Math.sqrt(252) : 0
  
  // Max Drawdown
  let peak = orca[0]
  let maxDD = 0
  for (let i = 1; i < orca.length; i++) {
    if (orca[i] > peak) peak = orca[i]
    const dd = ((orca[i] - peak) / peak) * 100
    if (dd < maxDD) maxDD = dd
  }
  metrics.value.maxDrawdown = maxDD
  
  // VaR (95%)
  const sortedReturns = [...orcaReturns].sort((a, b) => a - b)
  const varIndex = Math.floor(sortedReturns.length * 0.05)
  metrics.value.var = sortedReturns[varIndex] * 100
}

// Generate Volatility Data
const generateVolatilityData = () => {
  const n = 100
  redVolData.value = Array.from({ length: n }, (_, i) => {
    return 50 - (i / n) * 30 + Math.sin(i / 10) * 5 + Math.random() * 3
  })
  
  greenVolData.value = Array.from({ length: n }, (_, i) => {
    return 20 + (i / n) * 40 + Math.cos(i / 8) * 5 + Math.random() * 3
  })
}

// SVG Path Generators
const buyHoldLinePath = computed(() => {
  if (backtestData.value.buyHold.length === 0) return ''
  const data = backtestData.value.buyHold
  const n = data.length
  const width = 800
  const height = 300
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  
  let path = `M 0 ${height - ((data[0] - min) / range) * height}`
  for (let i = 1; i < n; i++) {
    const x = (i / (n - 1)) * width
    const y = height - ((data[i] - min) / range) * height
    path += ` L ${x} ${y}`
  }
  return path
})

const buyHoldAreaPath = computed(() => {
  if (backtestData.value.buyHold.length === 0) return ''
  const line = buyHoldLinePath.value
  const width = 800
  const height = 300
  return `${line} L ${width} ${height} L 0 ${height} Z`
})

const orcaLinePath = computed(() => {
  if (backtestData.value.orca.length === 0) return ''
  const data = backtestData.value.orca
  const n = data.length
  const width = 800
  const height = 300
  const min = Math.min(...backtestData.value.buyHold, ...data)
  const max = Math.max(...backtestData.value.buyHold, ...data)
  const range = max - min || 1
  
  let path = `M 0 ${height - ((data[0] - min) / range) * height}`
  for (let i = 1; i < n; i++) {
    const x = (i / (n - 1)) * width
    const y = height - ((data[i] - min) / range) * height
    path += ` L ${x} ${y}`
  }
  return path
})

const orcaAreaPath = computed(() => {
  if (backtestData.value.orca.length === 0) return ''
  const line = orcaLinePath.value
  const width = 800
  const height = 300
  return `${line} L ${width} ${height} L 0 ${height} Z`
})

const redVolLinePath = computed(() => {
  if (redVolData.value.length === 0) return ''
  const data = redVolData.value
  const n = data.length
  const width = 400
  const height = 150
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  
  let path = `M 0 ${height - ((data[0] - min) / range) * height}`
  for (let i = 1; i < n; i++) {
    const x = (i / (n - 1)) * width
    const y = height - ((data[i] - min) / range) * height
    path += ` L ${x} ${y}`
  }
  return path
})

const redVolAreaPath = computed(() => {
  if (redVolData.value.length === 0) return ''
  const line = redVolLinePath.value
  const width = 400
  const height = 150
  return `${line} L ${width} ${height} L 0 ${height} Z`
})

const greenVolLinePath = computed(() => {
  if (greenVolData.value.length === 0) return ''
  const data = greenVolData.value
  const n = data.length
  const width = 400
  const height = 150
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  
  let path = `M 0 ${height - ((data[0] - min) / range) * height}`
  for (let i = 1; i < n; i++) {
    const x = (i / (n - 1)) * width
    const y = height - ((data[i] - min) / range) * height
    path += ` L ${x} ${y}`
  }
  return path
})

const greenVolAreaPath = computed(() => {
  if (greenVolData.value.length === 0) return ''
  const line = greenVolLinePath.value
  const width = 400
  const height = 150
  return `${line} L ${width} ${height} L 0 ${height} Z`
})

// Three.js Initialization
const initThreeJS = () => {
  if (!threeCanvas.value) return
  
  const width = threeCanvas.value.clientWidth
  const height = threeCanvas.value.clientHeight
  
  // Scene
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x000000)
  
  // Camera
  camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
  camera.position.set(8, 8, 8)
  camera.lookAt(0, 0, 0)
  
  // Renderer
  renderer = new THREE.WebGLRenderer({ 
    canvas: threeCanvas.value, 
    antialias: true,
    alpha: true
  })
  renderer.setSize(width, height)
  renderer.setPixelRatio(window.devicePixelRatio)
  
  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
  scene.add(ambientLight)
  
  const pointLight1 = new THREE.PointLight(0x22d3ee, 1, 100)
  pointLight1.position.set(10, 10, 10)
  scene.add(pointLight1)
  
  const pointLight2 = new THREE.PointLight(0x4ade80, 0.8, 100)
  pointLight2.position.set(-10, -10, 10)
  scene.add(pointLight2)
  
  // Build 3D Manifold
  buildManifold()
  
  // Mouse controls
  setupMouseControls()
  
  // Animation loop
  const animate = () => {
    animationId = requestAnimationFrame(animate)
    
    if (mesh && isLive.value) {
      // Rotate based on mouse or auto-rotate
      mesh.rotation.y += 0.005 + mouseX * 0.001
      mesh.rotation.x += mouseY * 0.001
      
      // Update manifold based on GBM params
      updateManifold()
    }
    
    if (renderer && scene && camera) {
      renderer.render(scene, camera)
    }
  }
  animate()
}

// Build 3D Manifold (Latent Volatility Field)
const buildManifold = () => {
  if (!scene) return
  
  const segments = 50
  const geometry = new THREE.PlaneGeometry(10, 10, segments, segments)
  const material = new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 },
      drift: { value: gbmParams.value.drift },
      volatility: { value: gbmParams.value.volatility }
    },
    vertexShader: `
      uniform float time;
      uniform float drift;
      uniform float volatility;
      varying vec3 vPosition;
      varying float vElevation;
      
      void main() {
        vPosition = position;
        float x = position.x;
        float y = position.y;
        
        // Parametric equation for manifold deformation
        float r = sqrt(x * x + y * y);
        float theta = atan(y, x);
        
        // Latent volatility field
        float elevation = sin(r * 2.0 + time) * cos(theta * 3.0 + time * 0.5) * volatility * 2.0;
        elevation += sin(r * 4.0 - time) * drift * 3.0;
        elevation += cos(r * 1.5 + time * 0.3) * 0.5;
        
        vElevation = elevation;
        vec3 newPosition = position;
        newPosition.z = elevation;
        
        gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
      }
    `,
    fragmentShader: `
      varying vec3 vPosition;
      varying float vElevation;
      
      void main() {
        // Glow effect based on elevation
        vec3 color1 = vec3(0.13, 0.53, 0.93); // Blue
        vec3 color2 = vec3(0.13, 0.87, 0.50); // Green
        vec3 color3 = vec3(0.97, 0.44, 0.44); // Red
        
        float t = (vElevation + 2.0) / 4.0;
        t = clamp(t, 0.0, 1.0);
        
        vec3 color;
        if (t < 0.5) {
          color = mix(color1, color2, t * 2.0);
        } else {
          color = mix(color2, color3, (t - 0.5) * 2.0);
        }
        
        float glow = abs(vElevation) * 0.3 + 0.7;
        gl_FragColor = vec4(color * glow, 0.9);
      }
    `,
    wireframe: false,
    transparent: true
  })
  
  mesh = new THREE.Mesh(geometry, material)
  mesh.rotation.x = -Math.PI / 4
  scene.add(mesh)
}

// Update Manifold
const updateManifold = () => {
  if (mesh && mesh.material instanceof THREE.ShaderMaterial) {
    mesh.material.uniforms.time.value += 0.02
    mesh.material.uniforms.drift.value = gbmParams.value.drift
    mesh.material.uniforms.volatility.value = gbmParams.value.volatility
  }
}

// Mouse Controls
const setupMouseControls = () => {
  if (!threeCanvas.value) return
  
  threeCanvas.value.addEventListener('mousemove', (e) => {
    const rect = threeCanvas.value!.getBoundingClientRect()
    mouseX = (e.clientX - rect.left) / rect.width - 0.5
    mouseY = (e.clientY - rect.top) / rect.height - 0.5
  })
  
  // Handle window resize
  const handleResize = () => {
    if (!threeCanvas.value || !camera || !renderer) return
    const width = threeCanvas.value.clientWidth
    const height = threeCanvas.value.clientHeight
    camera.aspect = width / height
    camera.updateProjectionMatrix()
    renderer.setSize(width, height)
  }
  
  window.addEventListener('resize', handleResize)
  
  return () => {
    window.removeEventListener('resize', handleResize)
  }
}

// Update GBM Simulation
const updateGBMSimulation = () => {
  generateBacktestData()
  generateVolatilityData()
  addTerminalLog('info', `Parameters updated: μ=${gbmParams.value.drift.toFixed(3)}, σ=${gbmParams.value.volatility.toFixed(3)}`)
}

// Terminal Functions
const toggleLive = () => {
  isLive.value = !isLive.value
  addTerminalLog(isLive.value ? 'success' : 'warning', isLive.value ? 'Live inference enabled' : 'Inference paused')
}

const addTerminalLog = (type: string, message: string) => {
  const time = new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  terminalLogs.value.push({ time, message, type })
  
  // Keep only last 20 logs
  if (terminalLogs.value.length > 20) {
    terminalLogs.value.shift()
  }
  
  // Auto-scroll
  setTimeout(() => {
    if (consoleContent.value) {
      consoleContent.value.scrollTop = consoleContent.value.scrollHeight
    }
  }, 10)
}

// Update Terminal Data
const updateTerminalData = () => {
  if (!isLive.value) return
  
  // Update VIX
  terminalVix.value = Math.max(10, Math.min(30, terminalVix.value + (Math.random() - 0.5) * 0.3))
  
  // Update GBM data
  if (gbmData.value.length > 0) {
    const lastPrice = gbmData.value[gbmData.value.length - 1]
    const dt = 1 / 252
    const dW = Math.sqrt(dt) * (Math.random() * 2 - 1) * Math.sqrt(3)
    const dS = gbmParams.value.drift * lastPrice * dt + gbmParams.value.volatility * lastPrice * dW
    const newPrice = Math.max(0, lastPrice + dS)
    
    gbmData.value.push(newPrice)
    if (gbmData.value.length > gbmParams.value.lookback) {
      gbmData.value.shift()
    }
    
    // Update backtest data
    generateBacktestData()
  }
  
  // Update volatility data
  if (redVolData.value.length > 0) {
    redVolData.value.push(50 - Math.random() * 30)
    greenVolData.value.push(20 + Math.random() * 40)
    
    if (redVolData.value.length > 100) {
      redVolData.value.shift()
      greenVolData.value.shift()
    }
  }
  
  // Add periodic logs
  if (Math.random() > 0.95) {
    const messages = [
      'Latent field updated',
      'GBM simulation running',
      `Sharpe: ${metrics.value.sharpe.toFixed(2)}`,
      `Max DD: ${metrics.value.maxDrawdown.toFixed(2)}%`,
      'Manifold deformation computed'
    ]
    addTerminalLog('info', messages[Math.floor(Math.random() * messages.length)])
  }
}

// Lifecycle
let timeInterval: any = null
let dataInterval: any = null
let terminalInterval: any = null

onMounted(() => {
  updateCurrentTime()
  timeInterval = setInterval(updateCurrentTime, 1000)
  dataInterval = setInterval(updateMarketData, 2000)
  
  // Start news rotation
  startNewsRotation()
  
  // Initialize index charts
  generateChartData()
  setInterval(updateIndexCharts, 2000)
  
  // Initialize markets data updates
  updateMarketsUpdateTime()
  setInterval(updateMarketsData, 5000)
  
  // Initialize sparkline charts
  generateSparklineData()
  setInterval(updateSparklineData, 3000)
  
  // Initialize AI Insights updates
  setInterval(updateAiInsights, 4000)
  
  // Initialize Signal Matrix
  generateSignalMatrix()
  setInterval(updateSignalMatrix, 2000)

  // Initialize QuantLatent
  generateGrowthData()
  setTimeout(() => {
    initWireframe()
  }, 300)
  
  // Initialize Mini Charts (legacy)
  setTimeout(() => {
    initMiniCharts()
  }, 500)
  
  // Update current time
  updateCurrentTime()
  setInterval(updateCurrentTime, 1000)

  // Update QuantLatent data every 100ms
  setInterval(updateQuantLatentData, 100)
  
  // Initialize Volatility Dashboard
  equityData.value = calculateEquityCurve(100000, 90)
  calculatePerformanceStats()
  setTimeout(() => {
    initPnLSurface()
    setupEquityChartHover()
  }, 1000)
  
  // Initialize Liquidity Dashboard
  generatePriceStream()
  generateSignalMatrix()
  
  // Update liquidity data every 2 seconds
  setInterval(updateLiquidityData, 2000)
  
  // Initialize terminal
  generateBacktestData()
  generateVolatilityData()
  
  setTimeout(() => {
    initThreeJS()
  }, 500)
  
  terminalInterval = setInterval(updateTerminalData, 1000)
})

onBeforeUnmount(() => {
  // Cleanup intervals
  if (timeInterval) clearInterval(timeInterval)
  if (dataInterval) clearInterval(dataInterval)
  if (terminalInterval) clearInterval(terminalInterval)
  stopNewsRotation()
  
  // Cleanup animation frames
  if (animationId !== null) cancelAnimationFrame(animationId)
  if (wireframeAnimationId !== null) cancelAnimationFrame(wireframeAnimationId)
  
  // Cleanup THREE.js renderers and scenes
  if (renderer) {
    renderer.dispose()
    scene = null
    camera = null
    renderer = null
    mesh = null
  }
  
  // Cleanup Chart.js instances
  if (assetChart) {
    assetChart.destroy()
    assetChart = null
  }
})
</script>

<style scoped>
/* ============================================
   MARKET DATA PAGE - NEW DESIGN SYSTEM
   ============================================ */

/* ============================================
   FUTURISTIC GLASS + DARK NEON ORANGE
   ============================================ */

.market-data-page {
  /* Основные цвета фона */
  --primary-bg: #050810;
  --secondary-bg: #080c18;
  --tertiary-bg: #0c1428;
  
  /* Glassmorphism */
  --glass-dark: rgba(15, 21, 40, 0.7);
  --glass-light: rgba(30, 45, 75, 0.3);
  --glass-subtle: rgba(15, 21, 40, 0.5);
  
  /* Неоновые акценты */
  --accent-orange: #ff8c00;
  --accent-orange-dark: #ff6a00;
  --accent-cyan: #00d9ff;
  --accent-lime: #00ff88;
  --accent-red: #ff3366;
  --accent-yellow: #ffd60a;
  
  /* Текст */
  --text-primary: #e8f0ff;
  --text-secondary: #a0afc8;
  --text-muted: #5a6f8f;
  --text-dim: #3a4f6f;
  
  /* Свечения */
  --glow-orange: 0 0 10px rgba(255, 140, 0, 0.5);
  --glow-cyan: 0 0 10px rgba(0, 217, 255, 0.5);
  --glow-lime: 0 0 10px rgba(0, 255, 136, 0.5);
  --shadow-deep: 0 8px 32px rgba(0, 0, 0, 0.4);
  --shadow-light: inset 0 1px 0 rgba(255, 255, 255, 0.1);
  
  /* Legacy compatibility */
  --primary: var(--primary-bg);
  --secondary: var(--secondary-bg);
  --accent: var(--accent-orange);
  --success: var(--accent-lime);
  --danger: var(--accent-red);
  --glass: var(--glass-dark);
}

.market-data-page {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary-bg) 0%, var(--tertiary-bg) 100%);
  color: var(--text-primary);
  display: flex;
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
  font-size: 12px;
  position: relative;
  margin: 0;
  padding: 0;
}

/* ============================================
   NEW SIDEBAR DESIGN (Glassmorphism Style)
   ============================================ */
.market-sidebar {
  position: fixed;
  left: 16px;
  top: 16px;
  width: 260px;
  height: calc(100vh - 32px);
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  z-index: 100;
  box-shadow:
    0 20px 40px -10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

/* Sidebar Header */
.sidebar-header {
  padding-bottom: 20px;
  border-bottom: 1.5px solid rgba(255, 140, 0, 0.2);
  margin-bottom: 10px;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin: 0 0 6px 0;
}

.sidebar-subtitle {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0 0 14px 0;
  font-weight: 400;
  letter-spacing: 0.5px;
  line-height: 1.4;
}

.back-to-dashboard {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 12px;
  font-weight: 500;
  padding: 10px 14px;
  background: transparent;
  border: 1.5px solid rgba(255, 140, 0, 0.2);
  border-radius: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.back-to-dashboard:hover {
  border-color: var(--accent-orange);
  background: rgba(255, 140, 0, 0.08);
  color: var(--accent-orange);
  box-shadow: var(--glow-orange);
}

.back-to-dashboard svg {
  width: 14px;
  height: 14px;
}

/* Header Links Container */
.header-links {
  display: flex;
  gap: 8px;
}

/* Back to Markets Button */
.back-to-markets {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--accent-cyan);
  text-decoration: none;
  font-size: 12px;
  font-weight: 500;
  padding: 10px 14px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(0, 150, 200, 0.04));
  border: 1.5px solid rgba(0, 212, 255, 0.3);
  border-radius: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.back-to-markets:hover {
  border-color: var(--accent-cyan);
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(0, 150, 200, 0.08));
  color: var(--accent-cyan);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
}

.back-to-markets svg {
  width: 14px;
  height: 14px;
}

/* Navigation Buttons */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.nav-btn {
  padding: 14px 16px;
  background: transparent;
  border: 1.5px solid rgba(255, 140, 0, 0.2);
  border-radius: 20px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-light);
}

.nav-btn:hover {
  border-color: var(--accent-orange);
  background: rgba(255, 140, 0, 0.08);
  color: var(--text-primary);
  box-shadow: 0 0 10px rgba(255, 140, 0, 0.2);
  transform: translateY(-2px);
}

.nav-btn.active {
  border-color: var(--accent-orange);
  border-left: 3px solid var(--accent-orange);
  background: rgba(255, 140, 0, 0.12);
  color: var(--accent-orange);
  box-shadow: inset 0 0 10px rgba(255, 140, 0, 0.2), var(--glow-orange);
}

/* Navigation Link (to Markets page) */
.nav-btn.nav-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  text-decoration: none;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(0, 150, 200, 0.04));
  border-color: rgba(0, 212, 255, 0.3);
  color: var(--accent-cyan);
}

.nav-btn.nav-link:hover {
  border-color: var(--accent-cyan);
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(0, 150, 200, 0.08));
  color: var(--accent-cyan);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}

.nav-external-icon {
  font-size: 12px;
  opacity: 0.7;
  transition: transform 0.3s ease;
}

.nav-btn.nav-link:hover .nav-external-icon {
  transform: translate(2px, -2px);
  opacity: 1;
}

/* Sidebar Status */
.sidebar-status {
  margin-top: auto;
  padding-top: 20px;
  border-top: 1.5px solid rgba(255, 140, 0, 0.2);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-lime);
  box-shadow: var(--glow-lime);
}

.status-dot.pulse {
  animation: pulse 2s infinite;
}

.status-text {
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-lime);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.status-time {
  font-size: 10px;
  color: var(--text-muted);
  font-family: 'Monaco', 'Courier New', monospace;
}

/* ============================================
   MAIN CONTENT AREA
   ============================================ */
.market-main {
  margin-left: 292px;
  flex: 1;
  padding: 16px 16px 16px 0;
  min-height: 100vh;
  overflow-y: auto;
  box-sizing: border-box;
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 16px;
  align-items: flex-start;
}

/* Markets Panel (Left) */
.markets-panel {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 28px;
  box-shadow:
    0 20px 40px -10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* Markets Overview Block */
.markets-overview-block {
  background: rgba(20, 25, 35, 0.6);
  border: 2px solid var(--accent-orange);
  border-radius: 20px;
  overflow: hidden;
  box-shadow:
    0 0 20px rgba(255, 140, 0, 0.3),
    0 0 40px rgba(255, 140, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.markets-overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(255, 140, 0, 0.1);
  border-bottom: 1px solid rgba(255, 140, 0, 0.3);
}

.markets-overview-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-orange);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  text-shadow: 0 0 10px rgba(255, 140, 0, 0.5);
}

.markets-overview-update {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.35);
  font-weight: 400;
}

.markets-overview-content {
  padding: 0;
}

/* Markets Table */
.markets-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
  table-layout: fixed;
}

.markets-table thead th {
  padding: 10px 6px;
  background: rgba(10, 15, 25, 0.6);
  color: var(--text-primary);
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  white-space: nowrap;
}

.markets-table tbody td {
  padding: 8px 6px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  vertical-align: middle;
}

.markets-table tbody tr:last-child td {
  border-bottom: none;
}

.markets-table tbody tr:hover {
  background: rgba(255, 140, 0, 0.05);
}

.markets-table .data-value {
  display: block;
  color: var(--text-primary);
  font-weight: 500;
  font-family: 'Monaco', 'Courier New', monospace;
  margin-bottom: 2px;
}

.markets-table .data-change {
  display: block;
  font-size: 11px;
  font-weight: 600;
  font-family: 'Monaco', 'Courier New', monospace;
}

.markets-table .data-change.positive {
  color: var(--accent-lime);
}

.markets-table .data-change.negative {
  color: var(--accent-red);
}

.markets-table .index-name {
  display: block;
  color: var(--accent-orange);
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
  opacity: 0.9;
}

.markets-table .data-empty {
  color: var(--text-muted);
  font-size: 11px;
  line-height: 1.4;
}

.data-value {
  color: var(--text-secondary);
  font-family: 'Monaco', 'Courier New', monospace;
}

.data-change {
  font-weight: 600;
  font-family: 'Monaco', 'Courier New', monospace;
}

.data-change.positive {
  color: var(--accent-lime);
  text-shadow: 0 0 6px rgba(0, 255, 136, 0.3);
}

.data-change.negative {
  color: var(--accent-red);
  text-shadow: 0 0 6px rgba(255, 51, 102, 0.3);
}

/* Index Charts Row */
.index-charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.index-chart-block {
  background: rgba(20, 25, 35, 0.6);
  border: 2px solid var(--accent-orange);
  border-radius: 16px;
  overflow: hidden;
  box-shadow:
    0 0 15px rgba(255, 140, 0, 0.2),
    0 0 30px rgba(255, 140, 0, 0.1);
}

.index-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: rgba(255, 140, 0, 0.1);
  border-bottom: 1px solid rgba(255, 140, 0, 0.3);
}

.index-chart-title {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.index-chart-name {
  font-size: 12px;
  font-weight: 700;
  color: var(--accent-orange);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.index-chart-freq {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.35);
  font-weight: 400;
}

.index-chart-value {
  font-size: 12px;
  font-weight: 700;
  font-family: 'Monaco', 'Courier New', monospace;
}

.index-chart-value.positive {
  color: var(--accent-lime);
}

.index-chart-value.negative {
  color: var(--accent-red);
}

.index-chart-container {
  height: 240px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
}

.index-chart-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.index-chart-svg path {
  transition: d 0.8s cubic-bezier(0.4, 0, 0.2, 1), 
              stroke 0.3s ease,
              fill 0.3s ease;
}

/* News Block */
.news-block {
  background: rgba(20, 25, 35, 0.6);
  border: 2px solid var(--accent-orange);
  border-radius: 20px;
  overflow: hidden;
  box-shadow:
    0 0 20px rgba(255, 140, 0, 0.3),
    0 0 40px rgba(255, 140, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.news-block-header {
  padding: 16px 20px;
  background: rgba(255, 140, 0, 0.1);
  border-bottom: 1px solid rgba(255, 140, 0, 0.3);
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-orange);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  text-shadow: 0 0 10px rgba(255, 140, 0, 0.5);
}

.news-carousel {
  padding: 16px 20px;
  overflow: hidden;
}

.news-carousel-inner {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.news-item-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 10px;
  border-left: 3px solid transparent;
  transition: all 0.3s ease;
}

.news-item-row:hover {
  background: rgba(255, 140, 0, 0.05);
  border-left-color: var(--accent-orange);
}

.news-region {
  flex-shrink: 0;
  padding: 4px 8px;
  background: rgba(255, 140, 0, 0.15);
  border: 1px solid rgba(255, 140, 0, 0.3);
  border-radius: 8px;
  font-size: 9px;
  font-weight: 700;
  color: var(--accent-orange);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  min-width: 60px;
  text-align: center;
}

.news-block .news-text {
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-secondary);
  margin: 0;
  flex: 1;
}

/* News List Animation */
.news-list-move,
.news-list-enter-active,
.news-list-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.news-list-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.news-list-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}

.news-list-leave-active {
  position: absolute;
  left: 0;
  right: 0;
}

.news-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.news-text {
  font-size: 11px;
  line-height: 1.5;
  color: var(--text-secondary);
  margin: 0;
}

.news-text.secondary {
  color: var(--text-muted);
}

/* Insights Panel (Right) */
.insights-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* Sparkline Block */
.sparkline-block {
  background: rgba(20, 25, 35, 0.6);
  border: 2px solid var(--accent-orange);
  border-radius: 20px;
  overflow: hidden;
  box-shadow:
    0 0 20px rgba(255, 140, 0, 0.3),
    0 0 40px rgba(255, 140, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.sparkline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: rgba(255, 140, 0, 0.1);
  border-bottom: 1px solid rgba(255, 140, 0, 0.3);
}

.sparkline-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-orange);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  text-shadow: 0 0 10px rgba(255, 140, 0, 0.5);
}

.sparkline-update {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.35);
  font-weight: 400;
}

.sparkline-content {
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sparkline-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  transition: background 0.2s ease;
}

.sparkline-item:hover {
  background: rgba(255, 140, 0, 0.08);
}

.sparkline-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 90px;
}

.sparkline-name {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sparkline-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'Monaco', 'Courier New', monospace;
}

.sparkline-change {
  font-size: 10px;
  font-weight: 600;
  font-family: 'Monaco', 'Courier New', monospace;
}

.sparkline-change.positive {
  color: var(--accent-lime);
}

.sparkline-change.negative {
  color: var(--accent-red);
}

.sparkline-chart {
  flex: 1;
  height: 30px;
  min-width: 80px;
}

.sparkline-svg {
  width: 100%;
  height: 100%;
}

.sparkline-svg path {
  transition: d 0.5s ease-out;
}

/* AI Insights Block - стилистика как у "Обзор рынков" */
.ai-insights-block {
  background: rgba(20, 25, 35, 0.6);
  border: 2px solid var(--accent-orange);
  border-radius: 20px;
  overflow: hidden;
  box-shadow:
    0 0 20px rgba(255, 140, 0, 0.3),
    0 0 40px rgba(255, 140, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.ai-insights-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(255, 140, 0, 0.1);
  border-bottom: 1px solid rgba(255, 140, 0, 0.3);
}

.ai-insights-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-orange);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  text-shadow: 0 0 10px rgba(255, 140, 0, 0.5);
}

.ai-insights-content {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ai-signals {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-signal-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  transition: background 0.2s ease;
}

.ai-signal-item:hover {
  background: rgba(255, 140, 0, 0.08);
}

.ai-signal-icon {
  font-size: 10px;
}

.ai-signal-icon.buy {
  color: var(--accent-lime);
}

.ai-signal-icon.sell {
  color: var(--accent-red);
}

.ai-signal-action {
  font-weight: 700;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  min-width: 70px;
}

.ai-signal-action.buy {
  color: var(--accent-lime);
}

.ai-signal-action.sell {
  color: var(--accent-red);
}

.ai-signal-symbol {
  color: var(--text-primary);
  font-weight: 600;
  flex: 1;
}

.ai-signal-value {
  font-family: 'Monaco', 'Courier New', monospace;
  font-weight: 600;
  font-size: 11px;
}

.ai-signal-value.buy {
  color: var(--accent-lime);
}

.ai-signal-value.sell {
  color: var(--accent-red);
}

.ai-section {
  margin-top: 0;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 140, 0, 0.2);
}

.ai-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 700;
  color: var(--accent-orange);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 14px;
  text-shadow: 0 0 6px rgba(255, 140, 0, 0.3);
}

.section-title-icon {
  font-size: 10px;
  opacity: 0.7;
  animation: pulse-icon 2s ease-in-out infinite;
}

@keyframes pulse-icon {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

.alerts-count {
  background: linear-gradient(135deg, rgba(255, 140, 0, 0.3), rgba(255, 100, 0, 0.2));
  color: var(--accent-orange);
  font-size: 9px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 10px;
  margin-left: auto;
  border: 1px solid rgba(255, 140, 0, 0.3);
  box-shadow: 0 0 8px rgba(255, 140, 0, 0.2);
}

.ai-recommendations,
.ai-alerts {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rec-item {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}

.rec-label {
  color: var(--text-secondary);
}

.rec-value {
  color: var(--text-primary);
  font-weight: 500;
}

/* Alert Items - Enhanced Styling */
.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-size: 11px;
  color: var(--text-secondary);
  padding: 12px 14px;
  background: linear-gradient(135deg, rgba(30, 35, 50, 0.8), rgba(20, 25, 40, 0.6));
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.alert-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  border-radius: 3px 0 0 3px;
}

.alert-item:hover {
  transform: translateX(4px);
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* Alert Type Variants */
.alert-item.alert-resistance::before {
  background: linear-gradient(180deg, var(--accent-cyan), var(--accent-blue));
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.alert-item.alert-warning::before {
  background: linear-gradient(180deg, var(--accent-yellow), var(--accent-orange));
  box-shadow: 0 0 10px rgba(255, 200, 0, 0.5);
}

.alert-item.alert-positive::before {
  background: linear-gradient(180deg, var(--accent-lime), var(--accent-green));
  box-shadow: 0 0 10px rgba(180, 255, 100, 0.5);
}

.alert-item.alert-negative::before {
  background: linear-gradient(180deg, var(--accent-red), var(--accent-magenta));
  box-shadow: 0 0 10px rgba(255, 100, 100, 0.5);
}

.alert-item.alert-info::before {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.2));
}

/* Alert Icon Wrapper */
.alert-icon-wrapper {
  position: relative;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.alert-icon {
  font-size: 14px;
  z-index: 1;
}

.alert-item.alert-resistance .alert-icon { color: var(--accent-cyan); }
.alert-item.alert-warning .alert-icon { color: var(--accent-yellow); }
.alert-item.alert-positive .alert-icon { color: var(--accent-lime); }
.alert-item.alert-negative .alert-icon { color: var(--accent-red); }
.alert-item.alert-info .alert-icon { color: rgba(255, 255, 255, 0.6); }

.alert-pulse {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.15;
  animation: alert-pulse-anim 2s ease-out infinite;
}

.alert-item.alert-resistance .alert-pulse { background: var(--accent-cyan); }
.alert-item.alert-warning .alert-pulse { background: var(--accent-yellow); }
.alert-item.alert-positive .alert-pulse { background: var(--accent-lime); }
.alert-item.alert-negative .alert-pulse { background: var(--accent-red); }

@keyframes alert-pulse-anim {
  0% { transform: scale(0.8); opacity: 0.2; }
  50% { transform: scale(1.2); opacity: 0.1; }
  100% { transform: scale(0.8); opacity: 0.2; }
}

/* Alert Content */
.alert-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 0;
}

.alert-text {
  line-height: 1.5;
  color: var(--text-primary);
  font-weight: 500;
}

.alert-time {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.35);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Signal Matrix Block */
.signal-matrix-block {
  background: rgba(20, 25, 35, 0.6);
  border: 2px solid var(--accent-orange);
  border-radius: 20px;
  overflow: hidden;
  box-shadow:
    0 0 20px rgba(255, 140, 0, 0.3),
    0 0 40px rgba(255, 140, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.signal-matrix-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: rgba(255, 140, 0, 0.1);
  border-bottom: 1px solid rgba(255, 140, 0, 0.3);
}

.signal-matrix-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--accent-orange);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  text-shadow: 0 0 10px rgba(255, 140, 0, 0.5);
}

.signal-matrix-update {
  font-size: 8px;
  color: var(--accent-lime);
  animation: pulse 1.5s infinite;
}

.signal-matrix-content {
  padding: 16px 18px;
}

.signal-matrix-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.signal-matrix-row {
  display: flex;
  gap: 4px;
}

.signal-matrix-cell {
  flex: 1;
  height: 28px;
  border-radius: 4px;
  transition: background-color 0.5s ease;
}

/* ============================================
   ANIMATIONS
   ============================================ */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.2);
  }
}

@keyframes textGlow {
  0%, 100% {
    text-shadow: 0 0 8px rgba(255, 140, 0, 0.3);
  }
  50% {
    text-shadow: 0 0 16px rgba(255, 140, 0, 0.6);
  }
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(255, 140, 0, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(255, 140, 0, 0.6);
  }
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1200px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
  
  .insights-panel {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
  }
  
  .ai-insights-card {
    grid-column: span 2;
  }
}

@media (max-width: 1024px) {
  .market-sidebar {
    position: fixed;
    left: -280px;
    top: 0;
    height: 100vh;
    border-radius: 0 24px 24px 0;
    transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  
  .market-sidebar.open {
    left: 0;
  }
  
  .market-main {
    margin-left: 16px;
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .markets-row {
    grid-template-columns: 1fr;
  }
  
  .insights-panel {
    grid-template-columns: 1fr;
  }
  
  .ai-insights-card {
    grid-column: span 1;
  }
}

/* ============================================
   LEGACY SIDEBAR STYLES (keeping for compatibility)
   ============================================ */

.sidebar-search {
  position: relative;
  margin-bottom: 10px;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  background: var(--glass-subtle);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1.5px solid rgba(255, 140, 0, 0.3);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-light);
}

.search-input::placeholder {
  color: var(--text-dim);
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-orange);
  box-shadow: var(--glow-orange), var(--shadow-light);
  background: var(--glass-light);
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.5);
  pointer-events: none;
}

/* Market Selection Grid (2x3) */
.market-selection {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.market-selection .section-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.market-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.market-card {
  padding: 14px 12px;
  background: var(--glass-subtle);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1.5px solid rgba(255, 140, 0, 0.3);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  text-align: center;
  box-shadow: var(--shadow-light);
}

.market-card:hover {
  transform: translateY(-2px);
  border-color: var(--accent-orange);
  background: rgba(255, 140, 0, 0.08);
  box-shadow: var(--glow-orange), var(--shadow-light);
}

.market-card.active {
  border-color: var(--accent-orange);
  background: rgba(255, 140, 0, 0.12);
  box-shadow: var(--glow-orange), inset 0 0 10px rgba(255, 140, 0, 0.2);
}

.market-flag {
  font-size: 24px;
}

.market-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.market-code {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  font-family: monospace;
}

/* Navigation Tabs */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 10px;
}

.nav-tab {
  padding: 14px 16px;
  background: transparent;
  border: 1.5px solid rgba(255, 140, 0, 0.2);
  border-left: 3px solid transparent;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 12px;
  border-radius: 10px;
  margin-bottom: 8px;
  box-shadow: var(--shadow-light);
}

.nav-tab:hover {
  border-color: var(--accent-orange);
  background: rgba(255, 140, 0, 0.08);
  color: var(--text-primary);
  box-shadow: 0 0 10px rgba(255, 140, 0, 0.2);
  transform: translateY(-2px);
}

.nav-tab.active {
  border-left-color: var(--accent-orange);
  border-color: var(--accent-orange);
  background: rgba(255, 140, 0, 0.12);
  color: var(--accent-orange);
  box-shadow: inset 0 0 10px rgba(255, 140, 0, 0.2), var(--glow-orange);
}

.nav-icon {
  font-size: 18px;
}

.nav-label {
  font-weight: 500;
}

/* Sidebar Status */
.sidebar-status {
  margin-top: auto;
  padding-top: 20px;
  border-top: 1.5px solid rgba(255, 140, 0, 0.2);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-lime);
  box-shadow: var(--glow-lime);
}

.status-dot.pulse {
  animation: pulse 2s infinite;
}

.status-text {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.status-time {
  font-size: 10px;
  color: var(--text-muted);
  font-family: 'Monaco', 'Courier New', monospace;
}


.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  text-shadow: 0 0 8px rgba(255, 140, 0, 0.3);
}

.live-badge-main {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(0, 255, 136, 0.1);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1.5px solid rgba(0, 255, 136, 0.3);
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--accent-lime);
  box-shadow: var(--glow-lime), var(--shadow-light);
}

.live-dot-main {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent-lime);
  box-shadow: var(--glow-lime);
  animation: pulse 2s infinite;
}

/* Content Area */
.content-area {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* ============================================
   INDICES GRID
   ============================================ */
.indices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.index-card {
  background: var(--glass-dark);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1.5px solid rgba(255, 140, 0, 0.3);
  border-top: 3px solid var(--accent-orange);
  border-radius: 14px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeIn 0.4s ease, slideUp 0.4s ease;
  box-shadow: var(--shadow-light);
}

.index-card:hover {
  transform: translateY(-2px);
  border-color: var(--accent-orange);
  box-shadow: 0 0 20px rgba(255, 140, 0, 0.15), var(--shadow-light);
  background: var(--glass-light);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 140, 0, 0.2);
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.card-badge {
  padding: 4px 12px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  font-family: 'Monaco', 'Courier New', monospace;
}

.card-badge.positive {
  background: rgba(0, 255, 136, 0.15);
  color: var(--accent-lime);
  text-shadow: 0 0 6px rgba(0, 255, 136, 0.3);
}

.card-badge.negative {
  background: rgba(255, 51, 102, 0.15);
  color: var(--accent-red);
  text-shadow: 0 0 6px rgba(255, 51, 102, 0.3);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'Monaco', 'Courier New', monospace;
}

.card-name {
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.4;
}

/* ============================================
   INSTRUMENTS GRID
   ============================================ */
.instruments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.instrument-card {
  background: var(--glass-dark);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1.5px solid rgba(255, 140, 0, 0.3);
  border-top: 3px solid var(--accent-orange);
  border-radius: 14px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeIn 0.4s ease, slideUp 0.4s ease;
  box-shadow: var(--shadow-light);
}

.instrument-card:hover {
  transform: translateY(-2px);
  border-color: var(--accent-orange);
  box-shadow: 0 0 20px rgba(255, 140, 0, 0.15), var(--shadow-light);
  background: var(--glass-light);
}

.card-price {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 8px 0;
  font-family: 'Monaco', 'Courier New', monospace;
}

.card-quotes {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 140, 0, 0.15);
}

.quote-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.quote-label {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.quote-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'Monaco', 'Courier New', monospace;
}

/* ============================================
   DATA TABLE
   ============================================ */
.data-table-section {
  margin-bottom: 30px;
}

.table-header {
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--accent-orange);
}

.table-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--accent-orange);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 2px;
  text-shadow: 0 0 8px rgba(255, 140, 0, 0.3);
}

.table-container {
  overflow-x: auto;
  background: var(--glass-dark);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border-radius: 14px;
  border: 1.5px solid rgba(255, 140, 0, 0.2);
  border-top: 3px solid var(--accent-orange);
  box-shadow: var(--shadow-light);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: rgba(255, 140, 0, 0.08);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  position: sticky;
  top: 0;
  z-index: 10;
  border-bottom: 2px solid rgba(255, 140, 0, 0.3);
}

.data-table th {
  padding: 12px 14px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: color 0.2s ease;
}

.data-table th.sortable:hover {
  color: var(--accent-orange);
}

.sort-icon {
  margin-left: 8px;
  color: var(--accent-orange);
}

.data-table td {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(30, 45, 75, 0.5);
  color: var(--text-secondary);
  font-size: 11px;
  line-height: 1.4;
}

.table-row {
  cursor: pointer;
  transition: background 0.2s ease;
}

.table-row:hover {
  background: rgba(255, 140, 0, 0.05);
}

.cell-symbol {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cell-symbol strong {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.cell-name {
  font-size: 10px;
  color: var(--text-muted);
}

.cell-bid,
.cell-ask,
.cell-price {
  font-family: 'Monaco', 'Courier New', monospace;
  font-weight: 600;
  color: var(--text-primary);
}

.cell-change,
.cell-pchange {
  font-weight: 700;
  font-family: monospace;
}

.cell-change.positive,
.cell-pchange.positive {
  color: var(--accent-lime);
  font-weight: 600;
  text-shadow: 0 0 6px rgba(0, 255, 136, 0.3);
}

.cell-change.negative,
.cell-pchange.negative {
  color: var(--accent-red);
  font-weight: 600;
  text-shadow: 0 0 6px rgba(255, 51, 102, 0.3);
}

/* ============================================
   NEWS SECTION (2 COLUMNS)
   ============================================ */
.news-section {
  margin-bottom: 30px;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
}

.news-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.news-column-header {
  padding-bottom: 10px;
  border-bottom: 2px solid var(--accent-orange);
  margin-bottom: 20px;
}

.news-column-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--accent-orange);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 2px;
  text-shadow: 0 0 8px rgba(255, 140, 0, 0.3);
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.news-card {
  background: rgba(30, 45, 75, 0.2);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 140, 0, 0.15);
  border-radius: 10px;
  padding: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeIn 0.4s ease;
  box-shadow: var(--shadow-light);
}

.news-card:hover {
  border-color: rgba(255, 140, 0, 0.6);
  background: rgba(30, 45, 75, 0.4);
  box-shadow: 0 0 15px rgba(255, 140, 0, 0.1);
  transform: translateY(-2px);
}

.news-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 12px;
}

.news-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  flex: 1;
  line-height: 1.4;
}

.sentiment-badge {
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

.sentiment-badge.positive {
  background: rgba(0, 255, 136, 0.15);
  color: var(--accent-lime);
  border: 1px solid rgba(0, 255, 136, 0.3);
}

.sentiment-badge.negative {
  background: rgba(255, 51, 102, 0.15);
  color: var(--accent-red);
  border: 1px solid rgba(255, 51, 102, 0.3);
}

.sentiment-badge.neutral {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.news-description {
  font-size: 11px;
  line-height: 1.4;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 10px;
  color: var(--text-muted);
  padding-top: 12px;
  border-top: 1px solid rgba(255, 140, 0, 0.15);
}

.news-time {
  font-family: 'Monaco', 'Courier New', monospace;
}

.news-source {
  font-weight: 500;
  color: var(--text-secondary);
}

/* ============================================
   3D SURFACES SECTION
   ============================================ */
.surfaces-section {
  margin-top: 30px;
}

.section-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--accent-orange);
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--accent-orange);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 2px;
  text-shadow: 0 0 8px rgba(255, 140, 0, 0.3);
}

.surfaces-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.surface-card {
  background: var(--glass-dark);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1.5px solid rgba(255, 140, 0, 0.2);
  border-top: 3px solid var(--accent-orange);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: var(--shadow-light);
}

.surface-header {
  padding: 14px 18px;
  background: rgba(255, 140, 0, 0.08);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border-bottom: 1px solid rgba(255, 140, 0, 0.2);
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--accent-orange);
  text-shadow: 0 0 8px rgba(255, 140, 0, 0.3);
}

.surface-canvas {
  width: 100%;
  height: 400px;
  display: block;
  background: #000;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
}

.chart-card {
  background: rgba(30, 45, 75, 0.2);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 140, 0, 0.15);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: var(--shadow-light);
}

.chart-header {
  padding: 12px 14px;
  background: rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid rgba(255, 140, 0, 0.15);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.chart-canvas {
  width: 100%;
  height: 120px;
  display: block;
  background: #000;
}

/* ============================================
   ANIMATIONS
   ============================================ */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(10px);
  }
  to {
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(255, 140, 0, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(255, 140, 0, 0.6);
  }
}

@keyframes buttonHover {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(-2px);
  }
}

@keyframes textGlow {
  0%, 100% {
    text-shadow: 0 0 8px rgba(255, 140, 0, 0.3);
  }
  50% {
    text-shadow: 0 0 16px rgba(255, 140, 0, 0.6);
  }
}

/* ============================================
   RESPONSIVE DESIGN
   ============================================ */
@media (max-width: 1400px) {
  .surfaces-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
}

@media (max-width: 1024px) {
  .market-data-page {
    grid-template-columns: 1fr;
  }
  
  .market-main {
    margin-left: 0;
  }
  
  .market-sidebar {
    position: fixed;
    left: -260px;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    width: 200px;
  }
  
  .market-sidebar.open {
    left: 0;
  }
  
  .news-grid {
    grid-template-columns: 1fr;
  }
  
  .indices-grid,
  .instruments-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}

@media (max-width: 768px) {
  .market-main {
    padding: 20px;
  }
  
  .indices-grid,
  .instruments-grid {
    grid-template-columns: 1fr;
  }
  
  .surfaces-grid {
    grid-template-columns: 1fr;
  }
  
  .page-title {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .market-main {
    padding: 16px;
  }
  
  .market-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .news-grid {
    grid-template-columns: 1fr;
  }
}

/* Top Market Navigation */
.top-market-nav {
  display: flex;
  gap: 0;
  background: rgba(5, 8, 16, 0.98);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding: 0;
  backdrop-filter: blur(20px);
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.market-nav-btn {
  padding: 14px 28px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 2px solid transparent;
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-family-mono);
  position: relative;
}

.market-nav-btn:hover {
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.03);
}

.market-nav-btn.active {
  color: #fff;
  border-bottom-color: #f97316;
  background: rgba(249, 115, 22, 0.12);
}

.market-nav-btn.active svg {
  color: #f97316;
}

/* Asset Class Navigation */
.asset-class-nav {
  display: flex;
  gap: 0;
  background: rgba(5, 8, 16, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding: 0;
  backdrop-filter: blur(20px);
  z-index: 9;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.asset-class-btn {
  padding: 16px 32px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 2px solid transparent;
  font-family: var(--font-family-mono);
  position: relative;
}

.asset-class-btn:hover {
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.03);
}

.asset-class-btn.active {
  color: #fff;
  border-bottom-color: #f97316;
  background: rgba(249, 115, 22, 0.18);
  border: 1px solid rgba(249, 115, 22, 0.5);
  border-bottom: 2px solid #f97316;
  box-shadow: 0 2px 8px rgba(249, 115, 22, 0.2);
}

/* Main Grid: Three Panels */
.trading-platform-grid {
  display: grid;
  grid-template-columns: 300px 1fr 380px;
  gap: 0;
  flex: 1;
  overflow: hidden;
  background: #0a0e1a;
  min-height: 0;
}

/* Panel Common Styles */
.panel-left,
.panel-center,
.panel-right {
  background: rgba(5, 8, 16, 0.92);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.panel-right {
  border-right: none;
}

.panel-header {
  padding: 14px 20px;
  background: rgba(0, 0, 0, 0.5);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 48px;
}

.panel-header h3 {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
  font-family: var(--font-family-mono);
}

.panel-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #10b981;
  font-family: var(--font-family-mono);
}

.live-indicator-right {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 8px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #10b981;
  font-family: var(--font-family-mono);
  padding: 4px 8px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 4px;
}

.live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.8);
  animation: pulse-dot 2s infinite;
}

.live-dot-small {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.8);
  animation: pulse-dot 2s infinite;
}

/* Left Panel: News Feeds */
.news-feeds-list {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.news-item {
  padding: 14px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  cursor: pointer;
  transition: background 0.2s ease;
}

.news-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.news-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 10px;
}

.news-category {
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: rgba(255, 255, 255, 0.6);
  font-family: var(--font-family-mono);
}

.news-title {
  font-size: 12px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 500;
}

.news-time {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.45);
  font-family: var(--font-family-mono);
}

.news-time svg {
  width: 11px;
  height: 11px;
  opacity: 0.6;
}

/* Center Panel: Data Table */
.data-table-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: auto;
}

.trading-data-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-family-mono);
  font-size: 11px;
}

.trading-data-table thead {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(10px);
}

.trading-data-table th {
  padding: 14px 18px;
  text-align: left;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: rgba(255, 255, 255, 0.75);
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  font-size: 9px;
  white-space: nowrap;
}

.trading-data-table td {
  padding: 14px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.95);
  font-size: 11px;
}

.data-row {
  cursor: pointer;
  transition: background 0.15s ease;
}

.data-row:hover {
  background: rgba(255, 255, 255, 0.04);
}

.symbol-cell {
  font-weight: 700;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.symbol-cell strong {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.95);
}

.symbol-name {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.55);
  font-weight: 400;
  text-transform: none;
  letter-spacing: 0;
}

.bid-cell,
.ask-cell,
.price-cell {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  font-size: 11px;
}

.change-cell {
  font-weight: 700;
  font-size: 11px;
}

.pchange-cell {
  font-weight: 700;
  font-size: 11px;
}

/* Right Panel: Charts & Surfaces */
.charts-section {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  max-height: 50%;
  overflow-y: auto;
}

.chart-mini-container {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  overflow: hidden;
  min-height: 140px;
}

.chart-header-mini {
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.chart-symbol {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.95);
  font-family: var(--font-family-mono);
}

.chart-mini {
  width: 100%;
  height: 120px;
  display: block;
  background: #000;
}

.surfaces-section {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.surface-mini-container {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  overflow: hidden;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.surface-header-mini {
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.surface-header-mini span {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(255, 255, 255, 0.9);
  font-family: var(--font-family-mono);
}

.surface-mini {
  width: 100%;
  flex: 1;
  min-height: 250px;
  display: block;
  background: #000;
}

/* Bottom Status Bar */
.status-bar {
  display: flex;
  align-items: center;
  gap: 40px;
  padding: 14px 28px;
  background: rgba(0, 0, 0, 0.85);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  font-family: var(--font-family-mono);
  font-size: 11px;
  flex-shrink: 0;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-label {
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: rgba(255, 255, 255, 0.65);
  font-size: 10px;
}

.status-value {
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  font-size: 12px;
  letter-spacing: 0.02em;
}

.status-change {
  font-weight: 600;
  font-size: 11px;
}

.status-live {
  margin-left: auto;
  margin-right: 0;
}

.live-badge {
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: rgba(255, 255, 255, 0.75);
  padding: 6px 16px;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: 4px;
}

/* Scrollbar Styling */
.news-feeds-list::-webkit-scrollbar,
.data-table-container::-webkit-scrollbar {
  width: 6px;
}

.news-feeds-list::-webkit-scrollbar-track,
.data-table-container::-webkit-scrollbar-track {
  background: transparent;
}

.news-feeds-list::-webkit-scrollbar-thumb,
.data-table-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.news-feeds-list::-webkit-scrollbar-thumb:hover,
.data-table-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Pulse Animation */
@keyframes pulse-dot {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

/* Responsive Design */
@media (max-width: 1400px) {
  .trading-platform-grid {
    grid-template-columns: 260px 1fr 340px;
  }
}

@media (max-width: 1200px) {
  .trading-platform-grid {
    grid-template-columns: 220px 1fr 280px;
  }
  
  .panel-header h3 {
    font-size: 10px;
  }
  
  .trading-data-table {
    font-size: 10px;
  }
  
  .trading-data-table th,
  .trading-data-table td {
    padding: 12px 14px;
  }
  
  .chart-mini {
    height: 100px;
  }
}

@media (max-width: 968px) {
  .trading-platform-grid {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
  }
  
  .panel-left,
  .panel-center,
  .panel-right {
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .panel-right {
    border-bottom: none;
  }
  
  .top-market-nav,
  .asset-class-nav {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .market-nav-btn,
  .asset-class-btn {
    flex-shrink: 0;
  }
  
  .status-bar {
    flex-wrap: wrap;
    gap: 16px;
    padding: 10px 16px;
  }
}

@media (max-width: 640px) {
  .top-market-nav {
    padding: 0;
  }
  
  .market-nav-btn {
    padding: 10px 16px;
    font-size: 10px;
  }
  
  .asset-class-btn {
    padding: 12px 20px;
    font-size: 11px;
  }
  
  .panel-header {
    padding: 12px 16px;
  }
  
  .trading-data-table {
    font-size: 9px;
  }
  
  .trading-data-table th,
  .trading-data-table td {
    padding: 8px 10px;
  }
  
  .chart-mini {
    height: 100px;
  }
  
  .surface-mini {
    min-height: 150px;
  }
}

/* .page-container уже определен в main.css */

/* ============================================
   TABS NAVIGATION (Legacy - можно удалить если не используется)
   ============================================ */
.tabs-navigation-market {
  display: flex;
  gap: 0;
  background: var(--control-bg);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: var(--radius-md);
  padding: 4px;
  border: 1px solid var(--glass-border);
}

.tab-item-market {
  flex: 1;
  padding: 12px 20px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  position: relative;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  border-radius: var(--radius-sm);
  text-align: center;
}

.tab-item-market:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.tab-item-market.active {
  color: var(--text-primary);
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
}

.tab-label-market {
  display: block;
}

.tab-content-market {
  animation: fadeIn 0.3s ease-in;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.full-width {
  grid-column: 1 / -1;
}

.stats-grid-overview {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-item-overview {
  padding: 20px 16px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.06);
  text-align: center;
  transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.stat-item-overview::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.6), rgba(147, 51, 234, 0.6));
  opacity: 0;
  transition: opacity 0.25s ease;
}

.stat-item-overview:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.stat-item-overview:hover::before {
  opacity: 1;
}

.stat-label-overview {
  font-size: 10px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 12px;
  font-weight: 600;
  opacity: 0.7;
}

.stat-value-overview {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  margin-bottom: 6px;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.stat-change-overview {
  font-size: 12px;
  font-weight: 600;
  line-height: 1.3;
}

/* ============================================
   SECTION HEADER ENHANCEMENTS
   ============================================ */
.section-header {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 6px 0;
  letter-spacing: -0.03em;
  line-height: 1.2;
}

.section-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 400;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-to-dashboard {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--control-bg);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--control-border);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  white-space: nowrap;
  margin-bottom: 4px;
}

.back-to-dashboard:hover {
  background: var(--control-bg-focus);
  border-color: var(--control-border-focus);
  color: var(--text-primary);
}

.back-to-dashboard svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* Search Input */
.search-wrapper-market {
  position: relative;
  display: flex;
  align-items: center;
  min-width: 280px;
  height: 36px;
  background: var(--control-bg);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--control-border);
  border-radius: var(--radius-sm);
  padding: 0 12px;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.search-wrapper-market:focus-within {
  background: var(--control-bg-focus);
  border-color: var(--control-border-focus);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.05);
}

.search-icon-market {
  width: 16px;
  height: 16px;
  color: var(--text-tertiary);
  flex-shrink: 0;
  margin-right: 8px;
}

.search-input-market {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 13px;
  font-family: var(--font-family-base);
  padding: 0;
  height: 100%;
}

.search-input-market::placeholder {
  color: var(--text-tertiary);
}

.search-clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  flex-shrink: 0;
  margin-left: 8px;
  padding: 0;
}

.search-clear-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.search-clear-btn svg {
  width: 14px;
  height: 14px;
}

.status-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  font-size: 12px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.bg-green {
  background: #4ade80;
  box-shadow: 0 0 8px rgba(74, 222, 128, 0.6);
}

.dot.pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

/* ============================================
   TICKER
   ============================================ */
.ticker-wrapper {
  background: var(--control-bg);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  padding: 12px 0;
  overflow: hidden;
  position: relative;
}

.ticker-track {
  display: flex;
  animation: ticker-scroll 60s linear infinite;
  white-space: nowrap;
}

@keyframes ticker-scroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

.ticker-group {
  display: flex;
  gap: 32px;
  padding: 0 24px;
}

.ticker-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
}

.t-symbol {
  font-weight: 600;
  color: var(--text-primary);
  min-width: 80px;
}

.t-price {
  font-family: var(--font-family-mono);
  color: var(--text-primary);
  min-width: 100px;
  text-align: right;
}

.t-change {
  font-family: var(--font-family-mono);
  font-weight: 600;
  min-width: 70px;
  text-align: right;
}

/* ============================================
   GRID LAYOUT
   ============================================ */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.dashboard-grid:last-child {
  margin-bottom: 0;
}

.col-left,
.col-right {
  display: flex;
  flex-direction: column;
  gap: 24px !important;
}

.col-left > .glass-card,
.col-right > .glass-card {
  margin-bottom: 0 !important;
}

/* ============================================
   GLASS CARDS - используем стили из main.css
   ============================================ */
/* .glass-card уже определен в main.css */

.glass-card {
  margin-bottom: 24px !important;
  background: var(--glass-tint);
  backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat));
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: 0 20px 50px -10px rgba(0, 0, 0, 0.6), 
              inset 0 1px 0 rgba(255, 255, 255, 0.1), 
              inset 0 0 0 1px rgba(255, 255, 255, 0.05);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-card:hover {
  background: var(--glass-tint-hover);
  border-color: var(--glass-highlight);
  box-shadow: 0 25px 60px -10px rgba(0, 0, 0, 0.7), 
              inset 0 1px 0 rgba(255, 255, 255, 0.15), 
              inset 0 0 0 1px rgba(255, 255, 255, 0.08);
}

.glass-card:last-child {
  margin-bottom: 0 !important;
}

/* ============================================
   CARD HEADER ENHANCEMENTS
   ============================================ */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.card-header h3 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: -0.01em;
}

.badge-live {
  font-size: 10px;
  background: rgba(74, 222, 128, 0.15);
  color: #4ade80;
  padding: 5px 10px;
  border-radius: var(--radius-sm);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid rgba(74, 222, 128, 0.3);
  box-shadow: 0 0 8px rgba(74, 222, 128, 0.2);
}

/* ============================================
   INDICES LIST
   ============================================ */
.indices-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.index-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.index-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.6), rgba(147, 51, 234, 0.6));
  opacity: 0;
  transition: opacity 0.25s ease;
}

.index-item:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.index-item:hover::before {
  opacity: 1;
}

.index-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.index-symbol {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  letter-spacing: -0.02em;
}

.index-name {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.index-right {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.index-price {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.index-change {
  font-size: 13px;
  font-weight: 600;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 3px;
  line-height: 1.3;
}

.index-volume {
  font-size: 10px;
  color: var(--text-tertiary);
  font-weight: 500;
  opacity: 0.7;
}

/* ============================================
   CURRENCY GRID
   ============================================ */
.currency-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.currency-item {
  padding: 16px 12px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.06);
  text-align: center;
  transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.currency-item::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.4), transparent);
  opacity: 0;
  transition: opacity 0.25s ease;
}

.currency-item:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.currency-item:hover::after {
  opacity: 1;
}

.currency-symbol {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-family: var(--font-family-mono);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.8;
}

.currency-price {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  margin-bottom: 6px;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.currency-change {
  font-size: 12px;
  font-weight: 600;
  line-height: 1.3;
}

/* ============================================
   COMMODITIES
   ============================================ */
.commodities-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.commodity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.commodity-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  background: linear-gradient(180deg, rgba(251, 146, 60, 0.6), rgba(234, 179, 8, 0.6));
  opacity: 0;
  transition: opacity 0.25s ease;
}

.commodity-item:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.commodity-item:hover::before {
  opacity: 1;
}

.commodity-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.commodity-symbol {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  letter-spacing: -0.02em;
}

.commodity-name {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.commodity-right {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.commodity-price {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.commodity-change {
  font-size: 13px;
  font-weight: 600;
  line-height: 1.3;
}

.commodity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.commodity-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  background: linear-gradient(180deg, rgba(251, 146, 60, 0.6), rgba(234, 179, 8, 0.6));
  opacity: 0;
  transition: opacity 0.25s ease;
}

.commodity-item:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.commodity-item:hover::before {
  opacity: 1;
}

.commodity-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.commodity-symbol {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  letter-spacing: -0.02em;
}

.commodity-name {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.commodity-right {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.commodity-price {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.commodity-change {
  font-size: 13px;
  font-weight: 600;
  line-height: 1.3;
}

.commodity-price {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  margin-bottom: 4px;
}

.commodity-change {
  font-size: 11px;
  font-weight: 500;
}

/* ============================================
   STOCKS TABLE
   ============================================ */
.market-select {
  background: var(--control-bg);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid var(--control-border);
  color: var(--text-primary);
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  cursor: pointer;
  outline: none;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.market-select:focus {
  background: var(--control-bg-focus);
  border-color: var(--control-border-focus);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead th {
  text-align: left;
  padding: 10px 0;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--glass-border);
}

.data-table tbody td {
  padding: 12px 0;
  font-size: 13px;
  border-bottom: 1px solid var(--glass-border-soft);
}

.data-table tbody tr {
  cursor: pointer;
  transition: background 0.2s;
}

.data-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.stock-symbol {
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
}

.stock-price {
  font-family: var(--font-family-mono);
  color: var(--text-primary);
}

.stock-change {
  font-weight: 600;
  font-family: 'SF Mono', monospace;
}

.stock-volume {
  font-family: var(--font-family-mono);
  color: var(--text-secondary);
  font-size: 11px;
}

/* ============================================
   BONDS
   ============================================ */
.bonds-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bond-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border-radius: var(--radius-sm);
  border: 1px solid var(--glass-border-soft);
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  cursor: pointer;
}

.bond-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--glass-border);
}

.bond-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.bond-symbol {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
}

.bond-maturity {
  font-size: 11px;
  color: var(--text-secondary);
}

.bond-right {
  text-align: right;
}

.bond-yield {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  margin-bottom: 4px;
}

.bond-change {
  font-size: 11px;
  font-weight: 500;
}

/* ============================================
   CRYPTO
   ============================================ */
.crypto-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.crypto-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.crypto-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-sm);
}

.crypto-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.crypto-symbol {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  font-family: 'SF Mono', monospace;
}

.crypto-name {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
}

.crypto-price {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  font-family: 'SF Mono', monospace;
  text-align: right;
  min-width: 100px;
}

.crypto-change {
  font-size: 11px;
  font-weight: 500;
  text-align: right;
  min-width: 60px;
}

/* ============================================
   STATS SECTION
   ============================================ */
.stats-section {
  margin-top: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border-radius: var(--radius-md);
  border: 1px solid var(--glass-border-soft);
}

.stat-label {
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  margin-bottom: 4px;
}

.stat-change {
  font-size: 11px;
  font-weight: 500;
}

/* ============================================
   UTILITIES
   ============================================ */
.text-green { color: #4ade80; }
.text-red { color: #ef4444; }
.text-muted { color: var(--text-tertiary); }
.mono { font-family: var(--font-family-mono); }

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
    gap: 16px;
  }
  
  .section-title {
    font-size: 22px;
  }
  
  .currency-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .crypto-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .ticker-group {
    gap: 20px;
    padding: 0 16px;
  }
  
  .ticker-item {
    font-size: 11px;
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
  
  .currency-grid {
    grid-template-columns: 1fr;
  }
  
  .ticker-item {
    font-size: 10px;
    gap: 8px;
  }
  
  .t-symbol {
    min-width: 60px;
  }
  
  .t-price {
    min-width: 80px;
  }
}

/* ============================================
   QUANTLATENT v9.2
   ============================================ */
.quantlatent-section {
  margin-top: 32px !important;
  margin-bottom: 32px !important;
}

.quantlatent-panel {
  /* Используем стили из main.css для .glass-panel */
  background: var(--glass-tint);
  backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat));
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: 
    0 20px 50px -10px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    inset 0 0 0 1px rgba(255, 255, 255, 0.05);
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.quantlatent-panel:hover {
  background: var(--glass-tint-hover);
  border-color: var(--glass-highlight);
  box-shadow: 
    0 25px 60px -10px rgba(0, 0, 0, 0.7),
    inset 0 1px 0 rgba(255, 255, 255, 0.15),
    inset 0 0 0 1px rgba(255, 255, 255, 0.08);
}

.quantlatent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.quantlatent-title-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.quantlatent-title {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.15em;
  color: var(--text-primary);
  margin: 0;
  font-family: var(--font-family-mono);
  text-transform: uppercase;
}

.quantlatent-subtitle {
  font-size: 10px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-family: var(--font-family-mono);
}

.quantlatent-status-group {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-indicator-quantlatent {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.status-dot-quantlatent {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.2); }
}

.status-text-quantlatent {
  font-size: 9px;
  color: #10b981;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-family: 'SF Mono', monospace;
}

.status-epoch {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.epoch-label {
  font-size: 8px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-family: var(--font-family-mono);
}

.epoch-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
}

.status-percent {
  padding: 6px 12px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.percent-value {
  font-size: 14px;
  font-weight: 700;
  color: #10b981;
  font-family: 'SF Mono', monospace;
}

/* QuantLatent Grid */
.quantlatent-grid {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr 0.7fr;
  gap: 20px;
}

/* Wireframe Container */
.quantlatent-wireframe-container {
  background: rgba(0, 0, 0, 0.5);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 12px;
  position: relative;
}

.wireframe-header {
  margin-bottom: 8px;
}

.wireframe-label {
  font-size: 9px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-family: var(--font-family-mono);
}

.wireframe-canvas {
  width: 100%;
  height: 200px;
  display: block;
  background: #000000;
  border-radius: 8px;
}

.wireframe-controls {
  margin-top: 8px;
  display: flex;
  justify-content: space-between;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.control-param {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.param-label {
  font-size: 8px;
  color: rgba(255, 255, 255, 0.3);
  text-transform: uppercase;
  font-family: 'SF Mono', monospace;
}

.param-value {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  font-family: 'SF Mono', monospace;
}

/* Center Section */
.quantlatent-center {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Growth Chart */
.growth-chart-container {
  background: rgba(0, 0, 0, 0.5);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 12px;
}

.chart-header-quantlatent {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.chart-title-quantlatent {
  font-size: 9px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-family: var(--font-family-mono);
}

.chart-time-range {
  font-size: 8px;
  color: var(--text-tertiary);
  font-family: var(--font-family-mono);
}

.growth-chart-svg {
  width: 100%;
  height: 200px;
}

/* Orderbook */
.orderbook-container {
  background: rgba(0, 0, 0, 0.5);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 12px;
  flex: 1;
}

.orderbook-header {
  margin-bottom: 8px;
}

.orderbook-title {
  font-size: 9px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-family: var(--font-family-mono);
}

.orderbook-table {
  display: flex;
  flex-direction: column;
}

.orderbook-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  font-family: 'SF Mono', monospace;
  font-size: 10px;
  border-radius: 4px;
  transition: background 0.2s;
}

.orderbook-row.row-even {
  background: rgba(15, 15, 15, 0.5);
}

.orderbook-row:not(.row-even) {
  background: rgba(26, 26, 26, 0.5);
}

.orderbook-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

.orderbook-name {
  color: var(--text-secondary);
  font-weight: 500;
}

.orderbook-value {
  color: var(--text-primary);
  font-weight: 600;
}

/* Metrics Panel */
.quantlatent-metrics-panel {
  background: rgba(0, 0, 0, 0.5);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.metrics-header {
  margin-bottom: 4px;
}

.metrics-title {
  font-size: 9px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-family: var(--font-family-mono);
}

.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metric-item-quantlatent {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.metric-value-large {
  font-size: 24px;
  font-weight: 700;
  font-family: 'SF Mono', monospace;
  line-height: 1;
}

.metric-label-small {
  font-size: 8px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-family: var(--font-family-mono);
  margin-top: 4px;
}

.metrics-secondary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.metric-secondary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  font-family: 'SF Mono', monospace;
}

.metric-label-secondary {
  font-size: 9px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-value-secondary {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-primary);
}

/* Scanline Effect */
.scanline {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(
    to bottom,
    transparent,
    rgba(16, 185, 129, 0.1),
    transparent
  );
  animation: scanline 8s linear infinite;
  pointer-events: none;
  z-index: 1000;
}

@keyframes scanline {
  0% {
    top: 0;
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    top: 100%;
    opacity: 0;
  }
}

/* Responsive */
@media (max-width: 1200px) {
  .quantlatent-grid {
    grid-template-columns: 1fr;
  }
  
  .wireframe-canvas {
    height: 250px;
  }
}

@media (max-width: 768px) {
  .quantlatent-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .quantlatent-status-group {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .wireframe-canvas {
    height: 200px;
  }
  
  .growth-chart-svg {
    height: 150px;
  }
}

@media (max-width: 480px) {
  .quantlatent-panel {
    padding: 16px;
  }
  
  .quantlatent-title {
    font-size: 14px;
  }
  
  .wireframe-canvas {
    height: 150px;
  }
  
  .growth-chart-svg {
    height: 120px;
  }
  
  .metric-value-large {
    font-size: 20px;
  }
}

/* ============================================
   VOLATILITY TRADING SYSTEM DASHBOARD
   ============================================ */
.volatility-dashboard-section {
  margin-top: 32px !important;
  margin-bottom: 32px !important;
}

.volatility-panel {
  /* Используем стили из main.css для .glass-panel */
  background: var(--glass-tint);
  backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat));
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: 
    0 20px 50px -10px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    inset 0 0 0 1px rgba(255, 255, 255, 0.05);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.volatility-panel:hover {
  background: var(--glass-tint-hover);
  border-color: var(--glass-highlight);
  box-shadow: 
    0 25px 60px -10px rgba(0, 0, 0, 0.7),
    inset 0 1px 0 rgba(255, 255, 255, 0.15),
    inset 0 0 0 1px rgba(255, 255, 255, 0.08);
}

.volatility-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.volatility-title-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.volatility-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--text-primary);
  margin: 0;
  font-family: var(--font-family-mono);
}

.volatility-subtitle {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
}

.volatility-meta {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 10px;
  color: var(--text-tertiary);
  font-family: var(--font-family-mono);
}

/* Volatility Grid */
.volatility-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

/* 3D Surface Container */
.volatility-3d-container {
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px;
}

.volatility-3d-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title-volatility {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.surface-controls {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.4);
  font-family: 'SF Mono', monospace;
}

.pnl-surface-container {
  width: 100%;
  height: 350px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: var(--radius-md);
}

.surface-info {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.info-item-surface {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.info-label-surface {
  font-size: 9px;
  color: var(--text-tertiary);
  font-family: var(--font-family-mono);
}

/* Right Panel */
.volatility-right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Equity Curve */
.equity-curve-container {
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px;
}

.equity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.equity-legend {
  display: flex;
  gap: 16px;
}

.legend-item-equity {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-square {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-text {
  font-size: 10px;
  color: var(--text-secondary);
  font-family: var(--font-family-mono);
}

.equity-chart-svg {
  width: 100%;
  height: 400px;
}

.grid-lines line {
  pointer-events: none;
}

.crosshair {
  pointer-events: none;
}

.tooltip-equity {
  pointer-events: none;
}

.tooltip-equity text {
  font-family: 'SF Mono', monospace;
}

/* Stats Panel */
.stats-panel-volatility {
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px;
}

.stats-list-volatility {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.stat-row-volatility {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-label-volatility {
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: var(--font-family-mono);
}

.stat-value-volatility {
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-family-mono);
  color: var(--text-primary);
}

/* Responsive */
@media (max-width: 1200px) {
  .volatility-grid {
    grid-template-columns: 1fr;
  }
  
  .pnl-surface-container {
    height: 300px;
  }
  
  .equity-chart-svg {
    height: 300px;
  }
}

@media (max-width: 768px) {
  .volatility-panel {
    padding: 16px;
  }
  
  .volatility-title {
    font-size: 16px;
  }
  
  .volatility-meta {
    flex-direction: column;
    gap: 8px;
  }
  
  .pnl-surface-container {
    height: 250px;
  }
  
  .equity-chart-svg {
    height: 250px;
  }
  
  .equity-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .volatility-panel {
    padding: 12px;
  }
  
  .pnl-surface-container {
    height: 200px;
  }
  
  .equity-chart-svg {
    height: 200px;
  }
  
  .stat-value-volatility {
    font-size: 12px;
  }
}

/* ============================================
   LIQUIDITY SURFACE DASHBOARD
   ============================================ */
.liquidity-dashboard-section {
  margin-top: 0;
  margin-bottom: 32px;
}

.liquidity-panel {
  /* Используем стили из main.css для .glass-panel */
  background: var(--glass-tint);
  backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat));
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: 
    0 20px 50px -10px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    inset 0 0 0 1px rgba(255, 255, 255, 0.05);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.liquidity-panel:hover {
  background: var(--glass-tint-hover);
  border-color: var(--glass-highlight);
  box-shadow: 
    0 25px 60px -10px rgba(0, 0, 0, 0.7),
    inset 0 1px 0 rgba(255, 255, 255, 0.15),
    inset 0 0 0 1px rgba(255, 255, 255, 0.08);
}

.liquidity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.liquidity-title-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.liquidity-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--text-primary);
  margin: 0;
  font-family: var(--font-family-mono);
  text-transform: uppercase;
}

.liquidity-subtitle-group {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}

.liquidity-subtitle {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: var(--font-family-mono);
  text-transform: lowercase;
  font-weight: 400;
}

.liquidity-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  letter-spacing: -0.02em;
}

.liquidity-timestamp {
  display: flex;
  align-items: center;
  gap: 8px;
}

.timestamp-label {
  font-size: 10px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: var(--font-family-mono);
}

.timestamp-value {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: var(--font-family-mono);
}

/* Liquidity Grid */
.liquidity-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 0.8fr;
  gap: 24px;
}

/* 3D Surface Container */
.liquidity-3d-container {
  position: relative;
  background: rgba(0, 0, 0, 0.5);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 12px;
  overflow: visible;
  min-height: 450px;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.liquidity-3d-canvas {
  width: 100% !important;
  height: 400px !important;
  min-height: 400px !important;
  display: block !important;
  background: #000000;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.liquidity-3d-info {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.surface-param {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.surface-param.time-horizon {
  margin-top: 8px;
}

.param-label {
  font-size: 10px;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-family: var(--font-family-mono);
  letter-spacing: 0.05em;
  font-weight: 500;
}

.param-value {
  font-size: 12px;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  font-weight: 600;
}

.param-value-date {
  font-size: 14px;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  font-weight: 700;
  margin-top: 4px;
  letter-spacing: 0.02em;
}

/* Center Section */
.liquidity-center {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Price Stream */
.price-stream-container {
  background: rgba(0, 0, 0, 0.5);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 16px;
}

.price-stream-header {
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.equity-stream-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.live-dot-green {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
  animation: pulse-dot 2s infinite;
}

.equity-title-text {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.strategy-pnl {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.pnl-label {
  font-size: 10px;
  color: var(--text-secondary);
  font-family: var(--font-family-mono);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.pnl-value {
  font-size: 20px;
  font-weight: 700;
  font-family: var(--font-family-mono);
  letter-spacing: -0.02em;
}

.pnl-subvalue {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.4);
  font-family: var(--font-family-mono);
  font-weight: 400;
}

.now-button {
  padding: 6px 16px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: var(--radius-sm);
  color: #10b981;
  font-size: 11px;
  font-weight: 700;
  font-family: var(--font-family-mono);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.2s ease;
}

.now-button:hover {
  background: rgba(16, 185, 129, 0.25);
  border-color: rgba(16, 185, 129, 0.5);
}

.current-price-label {
  font-size: 10px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: var(--font-family-mono);
}

.current-price-value {
  font-size: 20px;
  font-weight: 700;
  font-family: var(--font-family-mono);
}

.price-change-badge {
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  font-family: 'SF Mono', monospace;
}

.equity-stream-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.live-dot-green {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
  animation: pulse-dot 2s infinite;
}

.equity-title-text {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.strategy-pnl {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.pnl-label {
  font-size: 10px;
  color: var(--text-secondary);
  font-family: var(--font-family-mono);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.pnl-value {
  font-size: 20px;
  font-weight: 700;
  font-family: var(--font-family-mono);
  letter-spacing: -0.02em;
}

.pnl-subvalue {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.4);
  font-family: var(--font-family-mono);
  font-weight: 400;
}

.now-button {
  padding: 6px 16px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: var(--radius-sm);
  color: #10b981;
  font-size: 11px;
  font-weight: 700;
  font-family: var(--font-family-mono);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.2s ease;
}

.now-button:hover {
  background: rgba(16, 185, 129, 0.25);
  border-color: rgba(16, 185, 129, 0.5);
}

.price-stream-svg {
  width: 100%;
  height: 200px;
}

.grid-price line {
  pointer-events: none;
}

/* Signal Matrix */
.signal-matrix-container {
  background: rgba(0, 0, 0, 0.5);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 16px;
}

.signal-matrix-header {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.matrix-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: var(--font-family-mono);
}

.signal-matrix-svg {
  width: 100%;
  height: 150px;
}

/* Metrics Panel */
.liquidity-metrics-panel {
  background: rgba(0, 0, 0, 0.5);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.metrics-header-liquidity {
  margin-bottom: 4px;
}

.metrics-title-liquidity {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: var(--font-family-mono);
}

.order-flow-table {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.order-flow-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.order-flow-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  min-width: 50px;
}

.order-flow-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  letter-spacing: -0.01em;
}

/* Flow Metrics */
.flow-metrics {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.flow-metric {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.flow-label {
  font-size: 10px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: var(--font-family-mono);
}

.flow-value {
  font-size: 18px;
  font-weight: 700;
  font-family: var(--font-family-mono);
}

.flow-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.flow-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* Volume Indicators */
.volume-indicators {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.volume-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
}

.volume-label {
  font-size: 10px;
  color: var(--text-secondary);
  font-family: var(--font-family-mono);
}

.volume-value {
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-family-mono);
  color: var(--text-primary);
}

/* Stress Indicators */
.stress-indicators {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.stress-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.stress-label {
  font-size: 10px;
  color: var(--text-secondary);
  font-family: var(--font-family-mono);
}

.stress-value {
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-family-mono);
}

/* Responsive */
@media (max-width: 1200px) {
  .liquidity-grid {
    grid-template-columns: 1fr;
  }
  
  .liquidity-3d-canvas {
    height: 300px;
  }
}

@media (max-width: 768px) {
  .liquidity-panel {
    padding: 16px;
  }
  
  .liquidity-title {
    font-size: 14px;
  }
  
  .liquidity-3d-canvas {
    height: 250px;
  }
  
  .price-stream-svg {
    height: 150px;
  }
  
  .signal-matrix-svg {
    height: 100px;
  }
}

@media (max-width: 480px) {
  .liquidity-panel {
    padding: 12px;
  }
  
  .liquidity-3d-canvas {
    height: 200px;
  }
  
  .price-stream-svg {
    height: 120px;
  }
  
  .signal-matrix-svg {
    height: 80px;
  }
}

/* ============================================
   QUANT ALPHA TERMINAL
   ============================================ */
.quant-terminal-section {
  margin-top: 32px !important;
  margin-bottom: 32px !important;
}

.terminal-panel {
  /* Используем стили из main.css для .glass-panel */
  background: var(--glass-tint);
  backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat));
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: 
    0 20px 50px -10px rgba(0, 0, 0, 0.6),
    0 0 40px rgba(34, 211, 238, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    inset 0 0 0 1px rgba(255, 255, 255, 0.05);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.terminal-panel:hover {
  background: var(--glass-tint-hover);
  border-color: var(--glass-highlight);
  box-shadow: 
    0 25px 60px -10px rgba(0, 0, 0, 0.7),
    0 0 50px rgba(34, 211, 238, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.15),
    inset 0 0 0 1px rgba(255, 255, 255, 0.08);
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.terminal-title-group {
  display: flex;
  align-items: center;
  gap: 24px;
}

.terminal-title {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--text-primary);
  margin: 0;
  font-family: var(--font-family-mono);
  text-transform: uppercase;
}

.terminal-vix {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.vix-label {
  font-size: 10px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.vix-value {
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-family-mono);
}

.terminal-time {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: var(--font-family-mono);
}

.terminal-controls {
  display: flex;
  gap: 12px;
}

.btn-terminal {
  padding: 8px 16px;
  background: var(--control-bg);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--control-border);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  font-family: var(--font-family-mono);
}

.btn-terminal:hover {
  background: var(--control-bg-focus);
  border-color: var(--control-border-focus);
  color: var(--text-primary);
}

.btn-terminal.active {
  background: rgba(34, 211, 238, 0.2);
  border-color: rgba(34, 211, 238, 0.5);
  color: #22d3ee;
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.3);
}

/* Terminal Grid */
.terminal-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr 0.8fr;
  gap: 24px;
}

/* 3D Container */
.terminal-3d-container {
  position: relative;
  background: rgba(0, 0, 0, 0.4);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.terminal-3d-header {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 10;
}

.terminal-label {
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.terminal-badge {
  font-size: 9px;
  padding: 4px 8px;
  background: rgba(34, 211, 238, 0.2);
  color: #22d3ee;
  border-radius: 4px;
  font-weight: 700;
  text-transform: uppercase;
}

.three-canvas {
  width: 100%;
  height: 400px;
  display: block;
}

.terminal-3d-info {
  position: absolute;
  bottom: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  justify-content: space-between;
  background: rgba(0, 0, 0, 0.6);
  padding: 8px 12px;
  border-radius: 8px;
  z-index: 10;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: 9px;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.info-value {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
}

/* Charts Container */
.terminal-charts {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-container-terminal {
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px;
}

.chart-header-terminal {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chart-title-terminal {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.chart-legend-terminal {
  display: flex;
  gap: 16px;
}

.legend-item-terminal {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  color: var(--text-secondary);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.chart-svg {
  width: 100%;
  height: 300px;
}

/* Volatility Charts */
.volatility-charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.vol-chart-container {
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px;
}

.vol-chart-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.vol-chart-label {
  font-size: 9px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.vol-chart-svg {
  width: 100%;
  height: 150px;
}

/* Terminal Sidebar */
.terminal-sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.terminal-controls-panel {
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px;
}

.control-group-terminal {
  margin-bottom: 20px;
}

.control-group-terminal:last-child {
  margin-bottom: 0;
}

.control-label-terminal {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
  font-weight: 600;
}

.control-value-terminal {
  font-family: 'SF Mono', monospace;
  color: #22d3ee;
  font-weight: 700;
}

.slider-terminal {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}

.slider-terminal::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: #22d3ee;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(34, 211, 238, 0.5);
  transition: all 0.2s;
}

.slider-terminal::-webkit-slider-thumb:hover {
  background: #4ade80;
  box-shadow: 0 0 15px rgba(74, 222, 128, 0.7);
  transform: scale(1.1);
}

.slider-terminal::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #22d3ee;
  border-radius: 50%;
  cursor: pointer;
  border: none;
  box-shadow: 0 0 10px rgba(34, 211, 238, 0.5);
}

/* Terminal Metrics */
.terminal-metrics {
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-terminal {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.metric-label-terminal {
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-value-terminal {
  font-size: 16px;
  font-weight: 700;
  font-family: var(--font-family-mono);
}

/* Terminal Console */
.terminal-console {
  background: rgba(0, 0, 0, 0.5);
  border-radius: var(--radius-md);
  border: 1px solid rgba(34, 211, 238, 0.2);
  padding: 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 300px;
  font-family: 'SF Mono', monospace;
}

.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.console-title {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.console-status {
  font-size: 9px;
  font-weight: 600;
}

.console-content {
  flex: 1;
  overflow-y: auto;
  font-size: 10px;
  line-height: 1.6;
}

.console-line {
  margin-bottom: 4px;
  display: flex;
  gap: 12px;
  padding: 2px 0;
}

.console-line.info {
  color: rgba(255, 255, 255, 0.7);
}

.console-line.success {
  color: #4ade80;
}

.console-line.warning {
  color: #fbbf24;
}

.console-line.metric {
  color: #22d3ee;
}

.console-time {
  color: var(--text-tertiary);
  min-width: 70px;
}

.console-message {
  flex: 1;
}

.text-orange {
  color: #f97316;
}

/* Responsive */
@media (max-width: 1200px) {
  .terminal-grid {
    grid-template-columns: 1fr;
  }
  
  .three-canvas {
    height: 300px;
  }
}

@media (max-width: 768px) {
  .terminal-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .terminal-title-group {
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .volatility-charts-row {
    grid-template-columns: 1fr;
  }
  
  .three-canvas {
    height: 250px;
  }
  
  .chart-svg {
    height: 200px;
  }
  
  .vol-chart-svg {
    height: 120px;
  }
}

@media (max-width: 480px) {
  .terminal-panel {
    padding: 16px;
  }
  
  .terminal-title {
    font-size: 14px;
  }
  
  .three-canvas {
    height: 200px;
  }
  
  .chart-svg {
    height: 150px;
  }
}
/* ============================================
   ASSET DETAIL MODAL
   ============================================ */
.asset-modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow-y: auto;
}

.asset-modal-container {
  width: 100%;
  max-width: 1200px;
  max-height: 90vh;
  background: var(--glass-tint);
  backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat));
  -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow: 
    0 20px 50px -10px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    inset 0 0 0 1px rgba(255, 255, 255, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.asset-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.asset-modal-title-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.asset-modal-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  font-family: var(--font-family-mono);
}

.asset-modal-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

.asset-modal-close {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--control-bg);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--control-border);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.asset-modal-close:hover {
  background: var(--control-bg-focus);
  border-color: var(--control-border-focus);
  color: var(--text-primary);
}

.asset-modal-content {
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Price Section */
.asset-price-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.asset-current-price {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.price-label {
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: var(--font-family-mono);
}

.price-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
}

.price-change-badge-large {
  padding: 6px 12px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  font-family: 'SF Mono', monospace;
}

.asset-meta-info {
  display: flex;
  gap: 24px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-label {
  font-size: 10px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: var(--font-family-mono);
}

.meta-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
}

/* Chart Section */
.asset-chart-section {
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 20px;
}

.chart-header-asset {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-title-asset {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.chart-timeframe {
  display: flex;
  gap: 8px;
}

.timeframe-btn {
  padding: 6px 12px;
  background: var(--control-bg);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid var(--control-border);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  font-family: var(--font-family-mono);
}

.timeframe-btn:hover {
  background: var(--control-bg-focus);
  border-color: var(--control-border-focus);
  color: var(--text-primary);
}

.timeframe-btn.active {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.4);
  color: var(--text-primary);
}

.chart-container-asset {
  width: 100%;
  height: 300px;
  position: relative;
}

.asset-price-chart {
  width: 100% !important;
  height: 300px !important;
  max-height: 300px !important;
}

.chart-controls-asset {
  display: flex;
  gap: 12px;
  align-items: center;
}

.chart-type-toggle {
  display: flex;
  gap: 4px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 2px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.chart-type-btn {
  padding: 6px 12px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  font-family: var(--font-family-mono);
  border-radius: var(--radius-sm);
}

.chart-type-btn:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.chart-type-btn.active {
  background: rgba(59, 130, 246, 0.2);
  color: var(--text-primary);
  border: 1px solid rgba(59, 130, 246, 0.4);
}

/* Order Book Section */
.asset-orderbook-section {
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 20px;
}

.orderbook-title-asset {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 16px 0;
}

.orderbook-container-asset {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 16px;
}

.orderbook-side {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.orderbook-ask {
  order: 1;
}

.orderbook-bid {
  order: 3;
}

.orderbook-header-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  padding: 8px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: 'SF Mono', monospace;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 4px;
}

.orderbook-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  padding: 6px 8px;
  font-size: 11px;
  font-family: 'SF Mono', monospace;
  border-radius: 4px;
  transition: background 0.2s;
}

.orderbook-ask-row {
  background: rgba(239, 68, 68, 0.05);
}

.orderbook-ask-row:hover {
  background: rgba(239, 68, 68, 0.1);
}

.orderbook-bid-row {
  background: rgba(16, 185, 129, 0.05);
}

.orderbook-bid-row:hover {
  background: rgba(16, 185, 129, 0.1);
}

.order-price {
  font-weight: 600;
  color: var(--text-primary);
}

.order-volume {
  color: var(--text-secondary);
  text-align: right;
}

.order-count {
  color: var(--text-tertiary);
  text-align: right;
  font-size: 10px;
}

.orderbook-spread {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.1);
  min-width: 120px;
}

.spread-value {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.spread-label {
  font-size: 9px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: var(--font-family-mono);
}

.spread-amount {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
}

.spread-percent {
  font-size: 11px;
  color: var(--text-secondary);
  font-family: var(--font-family-mono);
}

/* Info Section */
.asset-info-section {
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 20px;
}

.info-grid-asset {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-card-asset {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.info-label-asset {
  font-size: 10px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: var(--font-family-mono);
}

.info-value-asset {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  font-family: var(--font-family-mono);
}

/* Modal Transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .asset-modal-container,
.modal-fade-leave-active .asset-modal-container {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-fade-enter-from .asset-modal-container,
.modal-fade-leave-to .asset-modal-container {
  transform: scale(0.95) translateY(20px);
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .asset-modal-container {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }
  
  .asset-modal-content {
    padding: 16px;
  }
  
  .asset-price-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .orderbook-container-asset {
    grid-template-columns: 1fr;
  }
  
  .orderbook-spread {
    order: 2;
  }
  
  .info-grid-asset {
    grid-template-columns: 1fr;
  }
}
</style>
