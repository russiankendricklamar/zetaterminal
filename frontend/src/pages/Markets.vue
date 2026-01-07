<!-- src/pages/Markets.vue -->
<template>
  <div class="markets-page">
    
    <!-- Left Sidebar -->
    <aside class="market-sidebar">
      <!-- Logo/Title -->
      <div class="sidebar-header">
        <h1 class="sidebar-title">ТЕРМИНАЛ</h1>
        <p class="sidebar-subtitle">Потоковые данные в режиме реального времени</p>
        <router-link to="/data" class="back-to-terminal">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          <span>К терминалу</span>
        </router-link>
      </div>

      <!-- Navigation Buttons -->
      <nav class="sidebar-nav">
        <!-- ИНДЕКСЫ - current page (active) -->
        <button class="nav-btn active">
          ИНДЕКСЫ
        </button>
        
        <!-- Other tabs - link to MarketData page -->
        <router-link
          v-for="tab in sidebarNavItems"
          :key="tab.id"
          :to="{ path: '/data', query: { tab: tab.id } }"
          class="nav-btn nav-link-tab"
        >
          {{ tab.label }}
        </router-link>
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
      
      <!-- Ticker / Marquee -->
      <div class="ticker-wrapper">
        <div class="ticker-track">
          <div class="ticker-content">
            <div 
              v-for="index in indices" 
              :key="'ticker-' + index.symbol"
              class="ticker-item"
              :class="{ positive: index.change >= 0, negative: index.change < 0 }"
            >
              <span class="ticker-flag">{{ index.flag }}</span>
              <span class="ticker-symbol">{{ index.symbol }}</span>
              <span class="ticker-price">{{ formatNumber(index.price) }}</span>
              <span class="ticker-change" :class="index.change >= 0 ? 'positive' : 'negative'">
                {{ index.change >= 0 ? '+' : '' }}{{ index.change.toFixed(2) }}%
              </span>
            </div>
          </div>
          <!-- Duplicate for seamless loop -->
          <div class="ticker-content">
            <div 
              v-for="index in indices" 
              :key="'ticker-dup-' + index.symbol"
              class="ticker-item"
              :class="{ positive: index.change >= 0, negative: index.change < 0 }"
            >
              <span class="ticker-flag">{{ index.flag }}</span>
              <span class="ticker-symbol">{{ index.symbol }}</span>
              <span class="ticker-price">{{ formatNumber(index.price) }}</span>
              <span class="ticker-change" :class="index.change >= 0 ? 'positive' : 'negative'">
                {{ index.change >= 0 ? '+' : '' }}{{ index.change.toFixed(2) }}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Grid -->
      <div class="main-grid">
        
        <!-- Left Panel: Indices -->
        <div class="markets-panel">
          
          <!-- Header Bar -->
          <div class="indices-header-bar">
              <!-- Indices Dropdown Button -->
              <div class="indices-dropdown-wrapper">
                <button 
                  class="indices-dropdown-btn"
                  @click="toggleIndicesCatalog"
                >
                  <svg class="dropdown-icon-svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 3v18h18"/>
                    <path d="M18 17V9"/>
                    <path d="M13 17V5"/>
                    <path d="M8 17v-3"/>
                  </svg>
                  <span class="dropdown-label">Индексы</span>
                  <svg 
                    class="dropdown-arrow" 
                    :class="{ open: showIndicesCatalog }"
                    width="12" 
                    height="12" 
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor" 
                    stroke-width="2"
                  >
                    <polyline points="6 9 12 15 18 9"/>
                  </svg>
                </button>
                
                <!-- Dropdown Catalog -->
                <Transition name="dropdown">
                  <div v-if="showIndicesCatalog" class="indices-catalog">
                    <div class="catalog-header">
                      <span class="catalog-title">Каталог индексов</span>
                      <span class="catalog-count">{{ indices.length }} индексов</span>
                    </div>
                    
                    <!-- Region Tabs -->
                    <div class="catalog-regions">
                      <button
                        v-for="region in regions"
                        :key="region.id"
                        class="catalog-region-btn"
                        :class="{ active: activeRegion === region.id }"
                        @click="selectRegion(region.id); activeCountry = 'all'"
                      >
                        <span class="region-name">{{ region.name }}</span>
                        <span class="region-count">{{ getRegionCount(region.id) }}</span>
                      </button>
                    </div>
                    
                    <!-- Country Tabs (show when region is selected) -->
                    <div v-if="activeRegion !== 'all' && getRegionCountries(activeRegion).length > 1" class="catalog-countries">
                      <button
                        class="catalog-country-btn"
                        :class="{ active: activeCountry === 'all' }"
                        @click="activeCountry = 'all'"
                      >
                        <span class="country-name">Все</span>
                        <span class="country-count">{{ getRegionCount(activeRegion) }}</span>
                      </button>
                      <button
                        v-for="country in getRegionCountries(activeRegion)"
                        :key="country.id"
                        class="catalog-country-btn"
                        :class="{ active: activeCountry === country.id }"
                        @click="activeCountry = country.id"
                      >
                        <span class="country-name">{{ country.name }}</span>
                        <span class="country-count">{{ getCountryCount(country.id) }}</span>
                      </button>
                    </div>
                    
                    <div class="catalog-list">
                      <div 
                        v-for="index in catalogIndices" 
                        :key="'catalog-' + index.symbol"
                        class="catalog-item"
                        :class="{ positive: index.change >= 0, negative: index.change < 0 }"
                        @click="scrollToIndex(index.symbol)"
                      >
                        <span class="catalog-item-country">{{ getCountryName(index.country) }}</span>
                        <span class="catalog-item-symbol">{{ index.symbol }}</span>
                        <span class="catalog-item-name">{{ index.name }}</span>
                        <span class="catalog-item-change" :class="index.change >= 0 ? 'positive' : 'negative'">
                          {{ index.change >= 0 ? '+' : '' }}{{ index.change.toFixed(2) }}%
                        </span>
                      </div>
                    </div>
                  </div>
                </Transition>
              </div>

              <!-- Search Box -->
              <div class="search-box-large">
                <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="M21 21l-4.35-4.35"/>
                </svg>
                <input 
                  type="text" 
                  v-model="searchQuery" 
                  placeholder="Поиск по названию или символу..." 
                  class="search-input-large"
                />
                <button v-if="searchQuery" class="search-clear-large" @click="searchQuery = ''">✕</button>
              </div>
          </div>

          <!-- Indices Content -->
          <div class="indices-content">
            <!-- Empty State -->
            <div v-if="!detailViewIndex" class="empty-state">
              <div class="empty-state-icon">
                <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                  <path d="M3 3v18h18"/>
                  <path d="M18 17V9"/>
                  <path d="M13 17V5"/>
                  <path d="M8 17v-3"/>
                </svg>
              </div>
              <h3 class="empty-state-title">Выберите индекс для анализа</h3>
              <p class="empty-state-text">
                Нажмите на кнопку "Индексы" выше, чтобы открыть каталог<br>
                и выбрать интересующий вас индекс
              </p>
              <button class="empty-state-btn" @click="showIndicesCatalog = true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 3v18h18"/>
                  <path d="M18 17V9"/>
                  <path d="M13 17V5"/>
                  <path d="M8 17v-3"/>
                </svg>
                Открыть каталог индексов
              </button>
            </div>
            
            <!-- Detail View -->
            <div v-else class="detail-view">
              <!-- Brief Info -->
              <div class="detail-header">
                <div class="detail-brief">
                  <span class="detail-country">{{ detailViewIndex.country }}</span>
                  <span class="detail-symbol">{{ detailViewIndex.symbol }}</span>
                  <span class="detail-name">{{ detailViewIndex.name }}</span>
                  <span class="detail-price">{{ formatNumber(detailViewIndex.price) }}</span>
                  <span class="detail-change" :class="detailViewIndex.change >= 0 ? 'positive' : 'negative'">
                    {{ detailViewIndex.change >= 0 ? '+' : '' }}{{ detailViewIndex.change.toFixed(2) }}%
                    ({{ detailViewIndex.changePoints >= 0 ? '+' : '' }}{{ formatNumber(detailViewIndex.changePoints) }})
                  </span>
                </div>
              </div>
              
              <!-- Charts Grid -->
              <div class="detail-charts-grid">
                <!-- Left: Volatility Surface (Large) -->
                <div class="detail-volatility-section">
                  <div class="chart-card cyberpunk">
                    <div class="chart-card-header">
                      <span class="chart-title">Поверхность волатильности</span>
                      <span class="chart-subtitle">Implied Volatility Surface</span>
                    </div>
                    <div id="volatility-surface-detail" class="chart-container-large"></div>
                  </div>
                </div>
                
                <!-- Right Column: WAVE + INSANE -->
                <div class="detail-right-column">
                  <!-- WAVE Chart -->
                  <div class="chart-card">
                    <div class="chart-card-header">
                      <span class="chart-title">Взаимосвязь между импульсом и волатильностью</span>
                      <span class="chart-badge">WAVE_σ.9</span>
                    </div>
                    <div id="wave-surface-detail" class="chart-container-medium"></div>
                  </div>
                  
                  <!-- INSANE Chart -->
                  <div class="chart-card neon">
                    <div class="chart-card-header">
                      <span class="chart-title">Сигналы сдвига пика волатильности</span>
                      <span class="chart-badge neon">INSANE λ</span>
                    </div>
                    <div id="insane-surface-detail" class="chart-container-medium"></div>
                  </div>
                </div>
              </div>
              
              <!-- Price Chart -->
              <div class="detail-price-chart">
                <div class="chart-card wide">
                  <div class="chart-card-header">
                    <span class="chart-title">Динамика индекса</span>
                    <div class="timeframe-tabs">
                      <button 
                        v-for="tf in [{id: '1D', label: '1Д'}, {id: '1W', label: '1Н'}, {id: '1M', label: '1М'}, {id: '3M', label: '3М'}, {id: '1Y', label: '1Г'}]" 
                        :key="tf.id"
                        class="timeframe-btn"
                        :class="{ active: activeTimeframe === tf.id }"
                        @click="activeTimeframe = tf.id"
                      >{{ tf.label }}</button>
                    </div>
                  </div>
                  <div class="price-chart-container">
                    <svg class="detail-price-svg" viewBox="0 0 800 200" preserveAspectRatio="none">
                      <defs>
                        <linearGradient id="detail-price-gradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" :stop-color="detailViewIndex.change >= 0 ? 'rgba(0, 255, 136, 0.4)' : 'rgba(255, 51, 102, 0.4)'"/>
                          <stop offset="100%" stop-color="transparent"/>
                        </linearGradient>
                      </defs>
                      <path :d="generateAreaPath(detailViewIndex.history, 800, 200)" fill="url(#detail-price-gradient)" />
                      <path :d="generateSparkline(detailViewIndex.history, 800, 200)" :stroke="detailViewIndex.change >= 0 ? '#00ff88' : '#ff3366'" fill="none" stroke-width="2"/>
                    </svg>
                  </div>
                </div>
              </div>
              
              <!-- Detailed Info -->
              <div class="detail-info-section">
                <div class="info-card">
                  <h4 class="info-card-title">Торговая информация</h4>
                  <div class="info-grid">
                    <div class="info-row">
                      <span class="info-label">Открытие</span>
                      <span class="info-value">{{ formatNumber(detailViewIndex.open) }}</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">Максимум</span>
                      <span class="info-value positive">{{ formatNumber(detailViewIndex.high) }}</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">Минимум</span>
                      <span class="info-value negative">{{ formatNumber(detailViewIndex.low) }}</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">Изменение (пп)</span>
                      <span class="info-value" :class="detailViewIndex.changePoints >= 0 ? 'positive' : 'negative'">
                        {{ detailViewIndex.changePoints >= 0 ? '+' : '' }}{{ formatNumber(detailViewIndex.changePoints) }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="info-card">
                  <h4 class="info-card-title">Технические индикаторы</h4>
                  <div class="info-grid">
                    <div class="info-row">
                      <span class="info-label">RSI (14)</span>
                      <span class="info-value">{{ (45 + Math.random() * 30).toFixed(1) }}</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">MA 20</span>
                      <span class="info-value">{{ formatNumber(detailViewIndex.price * (0.98 + Math.random() * 0.04)) }}</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">MA 50</span>
                      <span class="info-value">{{ formatNumber(detailViewIndex.price * (0.95 + Math.random() * 0.1)) }}</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">Волатильность</span>
                      <span class="info-value">{{ (15 + Math.abs(detailViewIndex.change) * 3).toFixed(1) }}%</span>
                    </div>
                  </div>
                </div>
                <div class="info-card">
                  <h4 class="info-card-title">Спецификация индекса</h4>
                  <div class="info-grid">
                    <div class="info-row" v-if="detailViewIndex.constituentsCount">
                      <span class="info-label">Состав</span>
                      <span class="info-value">{{ detailViewIndex.constituentsCount }} компонентов</span>
                    </div>
                    <div class="info-row" v-if="detailViewIndex.totalMarketCap">
                      <span class="info-label">Капитализация</span>
                      <span class="info-value">{{ formatMarketCap(detailViewIndex.totalMarketCap, detailViewIndex.currency || (detailViewIndex.region === 'russia' ? 'RUB' : detailViewIndex.region === 'usa' ? 'USD' : detailViewIndex.region === 'europe' ? 'EUR' : '')) }}</span>
                    </div>
                    <div class="info-row" v-if="detailViewIndex.indexMarketCap">
                      <span class="info-label">Кап. в индексе</span>
                      <span class="info-value">{{ formatMarketCap(detailViewIndex.indexMarketCap, detailViewIndex.currency || (detailViewIndex.region === 'russia' ? 'RUB' : detailViewIndex.region === 'usa' ? 'USD' : detailViewIndex.region === 'europe' ? 'EUR' : '')) }}</span>
                    </div>
                    <div class="info-row" v-if="detailViewIndex.calculationMethod">
                      <span class="info-label">Метод расчета</span>
                      <span class="info-value">{{ detailViewIndex.calculationMethod }}</span>
                    </div>
                    <div class="info-row" v-if="detailViewIndex.baseDate">
                      <span class="info-label">Базовая дата</span>
                      <span class="info-value">{{ detailViewIndex.baseDate }}</span>
                    </div>
                    <div class="info-row" v-if="detailViewIndex.baseValue">
                      <span class="info-label">Базовое значение</span>
                      <span class="info-value">{{ formatNumber(detailViewIndex.baseValue) }}</span>
                    </div>
                    <div class="info-row" v-if="detailViewIndex.exchange">
                      <span class="info-label">Биржа</span>
                      <span class="info-value">{{ detailViewIndex.exchange }}</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">Валюта</span>
                      <span class="info-value">{{ detailViewIndex.currency || (detailViewIndex.region === 'russia' ? 'RUB' : detailViewIndex.region === 'usa' ? 'USD' : detailViewIndex.region === 'europe' ? 'EUR' : 'Local') }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>
    </main>

    <!-- Index Detail Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="selectedIndex" class="index-modal-overlay" @click.self="closeIndexDetail">
          <div class="index-modal index-modal-large">
            <!-- Modal Header -->
            <div class="modal-header">
              <div class="modal-title-row">
                <span class="modal-country-badge">{{ selectedIndex.country }}</span>
                <div class="modal-title-info">
                  <h2 class="modal-symbol">{{ selectedIndex.symbol }}</h2>
                  <span class="modal-name">{{ selectedIndex.name }}</span>
                </div>
              </div>
              <button class="modal-close" @click="closeIndexDetail">✕</button>
            </div>

            <!-- Price Section -->
            <div class="modal-price-section">
              <div class="modal-price">{{ formatNumber(selectedIndex.price) }}</div>
              <div class="modal-change" :class="selectedIndex.change >= 0 ? 'positive' : 'negative'">
                <span class="change-arrow">{{ selectedIndex.change >= 0 ? '▲' : '▼' }}</span>
                <span class="change-value">{{ selectedIndex.change >= 0 ? '+' : '' }}{{ selectedIndex.change.toFixed(2) }}%</span>
                <span class="change-points">({{ selectedIndex.changePoints >= 0 ? '+' : '' }}{{ selectedIndex.changePoints.toFixed(2) }})</span>
              </div>
            </div>

            <!-- Modal Content Grid -->
            <div class="modal-content-grid">
              <!-- Left Column: Charts -->
              <div class="modal-left-column">
                <!-- Chart Section -->
                <div class="modal-chart-section">
                  <div class="chart-header">
                    <span class="chart-title">График индекса</span>
                    <div class="chart-controls">
                      <div class="chart-type-toggle">
                        <button 
                          class="chart-type-btn"
                          :class="{ active: chartType === 'line' }"
                          @click="chartType = 'line'"
                          title="Линейный график"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                          </svg>
                        </button>
                        <button 
                          class="chart-type-btn"
                          :class="{ active: chartType === 'candle' }"
                          @click="chartType = 'candle'"
                          title="Японские свечи"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="6" y="4" width="4" height="16" rx="1"/>
                            <rect x="14" y="8" width="4" height="8" rx="1"/>
                            <line x1="8" y1="1" x2="8" y2="4"/>
                            <line x1="8" y1="20" x2="8" y2="23"/>
                            <line x1="16" y1="5" x2="16" y2="8"/>
                            <line x1="16" y1="16" x2="16" y2="19"/>
                          </svg>
                        </button>
                      </div>
                      <div class="chart-timeframes">
                        <button 
                          v-for="tf in timeframes" 
                          :key="tf.id" 
                          class="tf-btn"
                          :class="{ active: activeTimeframe === tf.id }"
                          @click="activeTimeframe = tf.id"
                        >
                          {{ tf.label }}
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Line Chart -->
                  <div class="modal-chart" v-if="chartType === 'line'">
                    <svg class="detail-chart" viewBox="0 0 800 300" preserveAspectRatio="none">
                      <defs>
                        <!-- Green gradient for area above center line -->
                        <linearGradient id="gradient-up" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stop-color="rgba(0, 255, 136, 0.3)"/>
                          <stop offset="100%" stop-color="rgba(0, 255, 136, 0.05)"/>
                        </linearGradient>
                        <!-- Red gradient for area below center line -->
                        <linearGradient id="gradient-down" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stop-color="rgba(255, 51, 102, 0.05)"/>
                          <stop offset="100%" stop-color="rgba(255, 51, 102, 0.3)"/>
                        </linearGradient>
                        <!-- Clip paths for above/below center -->
                        <clipPath id="clip-above">
                          <rect x="0" y="0" width="800" height="150"/>
                        </clipPath>
                        <clipPath id="clip-below">
                          <rect x="0" y="150" width="800" height="150"/>
                        </clipPath>
                        <!-- Grid pattern -->
                        <pattern id="grid-pattern" width="50" height="50" patternUnits="userSpaceOnUse">
                          <path d="M 50 0 L 0 0 0 50" fill="none" stroke="rgba(255,255,255,0.04)" stroke-width="0.5"/>
                        </pattern>
                      </defs>
                      <!-- Grid background -->
                      <rect width="800" height="300" fill="url(#grid-pattern)" />
                      <!-- Center line (current price level) -->
                      <line x1="0" y1="150" x2="800" y2="150" stroke="rgba(255,255,255,0.15)" stroke-width="1" stroke-dasharray="4,4"/>
                      <!-- Green area (above center) -->
                      <g clip-path="url(#clip-above)">
                        <path :d="generateAreaPathFromCenter(selectedIndex.history, 800, 300)" fill="url(#gradient-up)" />
                      </g>
                      <!-- Red area (below center) -->
                      <g clip-path="url(#clip-below)">
                        <path :d="generateAreaPathFromCenter(selectedIndex.history, 800, 300)" fill="url(#gradient-down)" />
                      </g>
                      <!-- Price line - green above, red below -->
                      <g clip-path="url(#clip-above)">
                        <path :d="generateSparkline(selectedIndex.history, 800, 300, true)" stroke="#00ff88" fill="none" stroke-width="2.5"/>
                      </g>
                      <g clip-path="url(#clip-below)">
                        <path :d="generateSparkline(selectedIndex.history, 800, 300, true)" stroke="#ff3366" fill="none" stroke-width="2.5"/>
                      </g>
                    </svg>
                  </div>

                  <!-- Candlestick Chart -->
                  <div class="modal-chart candlestick-chart" v-if="chartType === 'candle'">
                    <svg class="detail-chart" viewBox="0 0 800 300" preserveAspectRatio="none">
                      <g v-for="(candle, idx) in getCandlestickData(selectedIndex)" :key="idx">
                        <!-- Wick (shadow) -->
                        <line 
                          :x1="candle.x" 
                          :y1="candle.wickTop" 
                          :x2="candle.x" 
                          :y2="candle.wickBottom"
                          :stroke="candle.bullish ? '#00ff88' : '#ff3366'"
                          stroke-width="1"
                        />
                        <!-- Body -->
                        <rect 
                          :x="candle.x - candle.width / 2" 
                          :y="candle.bodyTop" 
                          :width="candle.width" 
                          :height="Math.max(candle.bodyHeight, 1)"
                          :fill="candle.bullish ? '#00ff88' : '#ff3366'"
                          :stroke="candle.bullish ? '#00ff88' : '#ff3366'"
                          stroke-width="1"
                          rx="1"
                        />
                      </g>
                    </svg>
                  </div>
                </div>

                <!-- WAVE Surface Section -->
                <div class="modal-wave-section">
                  <div class="wave-header">
                    <h3 class="wave-title">🌊 WAVE_σ.9 Momentum-Volatility Surface</h3>
                    <span class="wave-badge">Режимная индикация</span>
                  </div>
                  <div class="wave-description">
                    3D поверхность показывает взаимосвязь между импульсом, волатильностью и неровностью рынка.
                    <span class="wave-legend">
                      <span class="legend-item blue">🔵 Синий = низкий риск</span>
                      <span class="legend-item green">🟢 Зелёный = умеренный</span>
                      <span class="legend-item red">🔴 Красный = высокий риск</span>
                    </span>
                  </div>
                  <div :id="'wave-surface-' + selectedIndex.symbol" class="wave-surface-container"></div>
                  <div class="wave-metrics">
                    <div class="wave-metric">
                      <span class="metric-label">Режим</span>
                      <span class="metric-value" :class="getWaveRegimeClass(selectedIndex)">{{ getWaveRegime(selectedIndex) }}</span>
                    </div>
                    <div class="wave-metric">
                      <span class="metric-label">Momentum</span>
                      <span class="metric-value">{{ getWaveMomentum(selectedIndex).toFixed(2) }}</span>
                    </div>
                    <div class="wave-metric">
                      <span class="metric-label">Volatility</span>
                      <span class="metric-value">{{ getWaveVolatility(selectedIndex).toFixed(2) }}</span>
                    </div>
                    <div class="wave-metric">
                      <span class="metric-label">Jaggedness</span>
                      <span class="metric-value">{{ getWaveJaggedness(selectedIndex).toFixed(2) }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Right Column: Stats and Info -->
              <div class="modal-right-column">

                <!-- Stats Grid -->
                <div class="modal-stats-grid">
                  <div class="stat-card">
                    <span class="stat-label">Открытие</span>
                    <span class="stat-value">{{ formatNumber(selectedIndex.open) }}</span>
                  </div>
                  <div class="stat-card">
                    <span class="stat-label">Максимум</span>
                    <span class="stat-value high">{{ formatNumber(selectedIndex.high) }}</span>
                  </div>
                  <div class="stat-card">
                    <span class="stat-label">Минимум</span>
                    <span class="stat-value low">{{ formatNumber(selectedIndex.low) }}</span>
                  </div>
                  <div class="stat-card">
                    <span class="stat-label">Объём</span>
                    <span class="stat-value">{{ formatVolume(getIndexVolume(selectedIndex.symbol)) }}</span>
                  </div>
                  <div class="stat-card">
                    <span class="stat-label">Капитализация</span>
                    <span class="stat-value">{{ formatMarketCap(getIndexMarketCap(selectedIndex.symbol) / 1e9, selectedIndex.currency || (selectedIndex.region === 'russia' ? 'RUB' : selectedIndex.region === 'usa' ? 'USD' : selectedIndex.region === 'europe' ? 'EUR' : '')) }}</span>
                  </div>
                  <div class="stat-card">
                    <span class="stat-label">P/E</span>
                    <span class="stat-value">{{ getIndexPE(selectedIndex.symbol).toFixed(2) }}</span>
                  </div>
                </div>

                <!-- Additional Info -->
                <div class="modal-info-section">
                  <h4 class="info-section-title">Динамика</h4>
                  <div class="info-row">
                    <span class="info-label">52 нед. макс</span>
                    <span class="info-value">{{ formatNumber(selectedIndex.high * 1.15) }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">52 нед. мин</span>
                    <span class="info-value">{{ formatNumber(selectedIndex.low * 0.85) }}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">Изм. за неделю</span>
                    <span class="info-value" :class="getWeekChange(selectedIndex) >= 0 ? 'positive' : 'negative'">
                      {{ getWeekChange(selectedIndex) >= 0 ? '+' : '' }}{{ getWeekChange(selectedIndex).toFixed(2) }}%
                    </span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">Изм. за месяц</span>
                    <span class="info-value" :class="getMonthChange(selectedIndex) >= 0 ? 'positive' : 'negative'">
                      {{ getMonthChange(selectedIndex) >= 0 ? '+' : '' }}{{ getMonthChange(selectedIndex).toFixed(2) }}%
                    </span>
                  </div>
                  <div class="info-row">
                    <span class="info-label">Изм. за год</span>
                    <span class="info-value" :class="getYearChange(selectedIndex) >= 0 ? 'positive' : 'negative'">
                      {{ getYearChange(selectedIndex) >= 0 ? '+' : '' }}{{ getYearChange(selectedIndex).toFixed(2) }}%
                    </span>
                  </div>
                </div>

                <!-- Technical Indicators -->
                <div class="modal-technicals-section">
                  <h4 class="info-section-title">Техническая картина</h4>
                  <div class="technical-row">
                    <span class="tech-label">RSI (14)</span>
                    <span class="tech-value" :class="getRSIClass(selectedIndex)">{{ getRSI(selectedIndex).toFixed(1) }}</span>
                  </div>
                  <div class="technical-row">
                    <span class="tech-label">MA (20)</span>
                    <span class="tech-value">{{ formatNumber(getMA20(selectedIndex)) }}</span>
                  </div>
                  <div class="technical-row">
                    <span class="tech-label">MA (50)</span>
                    <span class="tech-value">{{ formatNumber(getMA50(selectedIndex)) }}</span>
                  </div>
                  <div class="technical-row">
                    <span class="tech-label">Тренд</span>
                    <span class="tech-value" :class="getTrendClass(selectedIndex)">{{ getTrend(selectedIndex) }}</span>
                  </div>
                  <div class="technical-row">
                    <span class="tech-label">Волатильность</span>
                    <span class="tech-value">{{ getVolatilityPercent(selectedIndex).toFixed(2) }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Constituents Table -->
            <div class="modal-constituents-section" v-if="getIndexConstituents(selectedIndex.symbol).length > 0">
              <div class="constituents-header">
                <h3 class="constituents-title">Инструменты индекса</h3>
                <span class="constituents-count">{{ getIndexConstituents(selectedIndex.symbol).length }} бумаг</span>
              </div>
              <div class="constituents-table-wrapper">
                <table class="constituents-table">
                  <thead>
                    <tr>
                      <th class="th-ticker">Тикер</th>
                      <th class="th-name">Название</th>
                      <th class="th-price">Цена</th>
                      <th class="th-change">Изм. %</th>
                      <th class="th-shares">Эфф. кол-во ЦБ</th>
                      <th class="th-cap">Капитализация</th>
                      <th class="th-index-cap">Кап. в индексе</th>
                      <th class="th-weight">Вес</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="constituent in getIndexConstituents(selectedIndex.symbol)" :key="constituent.ticker">
                      <td class="td-ticker">
                        <span class="ticker-badge">{{ constituent.ticker }}</span>
                      </td>
                      <td class="td-name">{{ constituent.name }}</td>
                      <td class="td-price">{{ formatConstituentPrice(constituent.price, selectedIndex.symbol) }}</td>
                      <td class="td-change" :class="constituent.change >= 0 ? 'positive' : 'negative'">
                        {{ constituent.change >= 0 ? '+' : '' }}{{ constituent.change.toFixed(2) }}%
                      </td>
                      <td class="td-shares">{{ formatShares(constituent.effectiveShares) }}</td>
                      <td class="td-cap">{{ formatConstituentCap(constituent.marketCap, selectedIndex.symbol) }}</td>
                      <td class="td-index-cap">{{ formatConstituentCap(constituent.indexCap, selectedIndex.symbol) }}</td>
                      <td class="td-weight">
                        <div class="weight-cell">
                          <span class="weight-value">{{ constituent.weight.toFixed(1) }}%</span>
                          <div class="weight-bar">
                            <div class="weight-bar-fill" :style="{ width: constituent.weight + '%' }"></div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Actions -->
            <div class="modal-actions">
              <button class="action-btn secondary" @click="closeIndexDetail">Закрыть</button>
              <router-link to="/data" class="action-btn primary">
                Открыть в терминале
              </router-link>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Teleport, Transition } from 'vue'

// ============================================
// TYPES
// ============================================

interface IndexData {
  symbol: string
  name: string
  price: number
  change: number
  changePoints: number
  open: number
  high: number
  low: number
  flag: string
  country: string
  region: string
  history: number[]
  // Спецификация индекса
  constituentsCount?: number // Количество компонентов
  totalMarketCap?: number // Общая капитализация (млрд)
  indexMarketCap?: number // Капитализация индекса (млрд)
  baseDate?: string // Базовая дата
  baseValue?: number // Базовое значение
  calculationMethod?: string // Метод расчета
  currency?: string // Валюта
  exchange?: string // Биржа
}

// ============================================
// STATE
// ============================================

const currentTime = ref('')
const activeRegion = ref('all')
const activeCountry = ref('all')
const searchQuery = ref('')
const showIndicesCatalog = ref(false)
const selectedIndex = ref<IndexData | null>(null)
const detailViewIndex = ref<IndexData | null>(null)
const activeTimeframe = ref('1D')
const chartType = ref<'line' | 'candle'>('line')
let waveAnimationInterval: ReturnType<typeof setInterval> | null = null
let insaneAnimationInterval: ReturnType<typeof setInterval> | null = null

// Dynamic Plotly loader
let Plotly: any = null
const loadPlotly = async () => {
  if (typeof window !== 'undefined' && !(window as any).Plotly) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = 'https://cdn.plot.ly/plotly-latest.min.js'
      script.onload = () => {
        Plotly = (window as any).Plotly
        resolve(Plotly)
      }
      script.onerror = reject
      document.head.appendChild(script)
    })
  }
  Plotly = (window as any).Plotly
  return Plotly
}

// Timeframes for chart
const timeframes = ref([
  { id: '1H', label: '1Ч' },
  { id: '1D', label: '1Д' },
  { id: '1W', label: '1Н' },
  { id: '1M', label: '1М' },
  { id: '1Y', label: '1Г' }
])

// Candlestick data interface
interface Candle {
  x: number
  wickTop: number
  wickBottom: number
  bodyTop: number
  bodyHeight: number
  width: number
  bullish: boolean
}

// Sidebar Navigation Items (same as MarketData.vue)
const sidebarNavItems = ref([
  { id: 'bonds', label: 'ОБЛИГАЦИИ' },
  { id: 'forex', label: 'ФОРЕКС' },
  { id: 'crypto', label: 'КРИПТО' },
  { id: 'news', label: 'НОВОСТИ' },
  { id: 'technicals', label: 'КОЛИЧЕСТВЕННАЯ АНАЛИТИКА' },
  { id: 'ai', label: 'AI АНАЛИТИКА' }
])

// Regions
const regions = ref([
  { id: 'all', name: 'Все' },
  { id: 'russia', name: 'Россия' },
  { id: 'usa', name: 'США' },
  { id: 'europe', name: 'Европа' },
  { id: 'asia', name: 'Азия' },
  { id: 'latam', name: 'Лат. Америка' },
  { id: 'middle_east', name: 'Бл. Восток' }
])

// Countries within regions
const countries = ref<Record<string, { id: string; name: string; region: string }[]>>({
  russia: [
    { id: 'RU', name: 'Россия', region: 'russia' }
  ],
  usa: [
    { id: 'US', name: 'США', region: 'usa' }
  ],
  europe: [
    { id: 'DE', name: 'Германия', region: 'europe' },
    { id: 'GB', name: 'Великобритания', region: 'europe' },
    { id: 'FR', name: 'Франция', region: 'europe' },
    { id: 'EU', name: 'Еврозона', region: 'europe' },
    { id: 'ES', name: 'Испания', region: 'europe' },
    { id: 'IT', name: 'Италия', region: 'europe' },
    { id: 'NL', name: 'Нидерланды', region: 'europe' },
    { id: 'CH', name: 'Швейцария', region: 'europe' },
    { id: 'BE', name: 'Бельгия', region: 'europe' },
    { id: 'AT', name: 'Австрия', region: 'europe' },
    { id: 'SE', name: 'Швеция', region: 'europe' },
    { id: 'PT', name: 'Португалия', region: 'europe' }
  ],
  asia: [
    { id: 'JP', name: 'Япония', region: 'asia' },
    { id: 'CN', name: 'Китай', region: 'asia' },
    { id: 'HK', name: 'Гонконг', region: 'asia' },
    { id: 'KR', name: 'Южная Корея', region: 'asia' },
    { id: 'TW', name: 'Тайвань', region: 'asia' },
    { id: 'IN', name: 'Индия', region: 'asia' },
    { id: 'SG', name: 'Сингапур', region: 'asia' },
    { id: 'TH', name: 'Таиланд', region: 'asia' },
    { id: 'ID', name: 'Индонезия', region: 'asia' },
    { id: 'MY', name: 'Малайзия', region: 'asia' },
    { id: 'AU', name: 'Австралия', region: 'asia' },
    { id: 'NZ', name: 'Новая Зеландия', region: 'asia' }
  ],
  latam: [
    { id: 'BR', name: 'Бразилия', region: 'latam' },
    { id: 'MX', name: 'Мексика', region: 'latam' },
    { id: 'AR', name: 'Аргентина', region: 'latam' },
    { id: 'CL', name: 'Чили', region: 'latam' },
    { id: 'CO', name: 'Колумбия', region: 'latam' }
  ],
  middle_east: [
    { id: 'SA', name: 'Саудовская Аравия', region: 'middle_east' },
    { id: 'AE', name: 'ОАЭ', region: 'middle_east' },
    { id: 'QA', name: 'Катар', region: 'middle_east' },
    { id: 'IL', name: 'Израиль', region: 'middle_east' },
    { id: 'EG', name: 'Египет', region: 'middle_east' }
  ]
})

// Global Indices Data
const indices = ref([
  // Russia
  { symbol: 'IMOEX', name: 'Индекс МосБиржи', price: 3245.67, change: 1.24, changePoints: 39.82, open: 3210.50, high: 3258.90, low: 3198.45, flag: '🇷🇺', country: 'RU', region: 'russia', history: [] as number[], constituentsCount: 25, totalMarketCap: 43.5, indexMarketCap: 43.5, baseDate: '1997-09-22', baseValue: 100, calculationMethod: 'Взвешенная по капитализации', currency: 'RUB', exchange: 'Московская биржа' },
  { symbol: 'RTS', name: 'Индекс РТС', price: 1156.34, change: 0.87, changePoints: 9.98, open: 1148.20, high: 1162.50, low: 1142.30, flag: '🇷🇺', country: 'RU', region: 'russia', history: [] as number[], constituentsCount: 12, totalMarketCap: 0.48, indexMarketCap: 0.48, baseDate: '1995-09-01', baseValue: 100, calculationMethod: 'Взвешенная по капитализации', currency: 'USD', exchange: 'Московская биржа' },
  { symbol: 'RGBI', name: 'Индекс гособлигаций', price: 128.45, change: -0.15, changePoints: -0.19, open: 128.60, high: 128.78, low: 128.12, flag: '🇷🇺', country: 'RU', region: 'russia', history: [] as number[] },
  { symbol: 'MOEXBC', name: 'Индекс голубых фишек', price: 21567.89, change: 1.12, changePoints: 238.45, open: 21350.00, high: 21620.50, low: 21290.30, flag: '🇷🇺', country: 'RU', region: 'russia', history: [] as number[] },
  { symbol: 'MOEXOG', name: 'Нефть и газ', price: 8456.23, change: 0.78, changePoints: 65.34, open: 8400.00, high: 8490.80, low: 8380.45, flag: '🇷🇺', country: 'RU', region: 'russia', history: [] as number[] },
  { symbol: 'MOEXFN', name: 'Финансы', price: 12345.67, change: -0.34, changePoints: -42.12, open: 12400.00, high: 12420.50, low: 12300.30, flag: '🇷🇺', country: 'RU', region: 'russia', history: [] as number[] },
  { symbol: 'MOEXMM', name: 'Металлы и добыча', price: 9876.54, change: 0.56, changePoints: 54.89, open: 9830.00, high: 9910.40, low: 9800.20, flag: '🇷🇺', country: 'RU', region: 'russia', history: [] as number[] },
  
  // USA
  { symbol: 'S&P 500', name: 'Standard & Poor\'s 500', price: 5234.18, change: 0.45, changePoints: 23.45, open: 5215.00, high: 5248.90, low: 5208.30, flag: '🇺🇸', country: 'US', region: 'usa', history: [] as number[], constituentsCount: 500, totalMarketCap: 40250.0, indexMarketCap: 40250.0, baseDate: '1957-03-04', baseValue: 10, calculationMethod: 'Взвешенная по капитализации', currency: 'USD', exchange: 'NYSE, NASDAQ' },
  { symbol: 'NASDAQ', name: 'NASDAQ Composite', price: 16742.39, change: 0.78, changePoints: 129.67, open: 16650.00, high: 16789.50, low: 16612.20, flag: '🇺🇸', country: 'US', region: 'usa', history: [] as number[], constituentsCount: 3000, totalMarketCap: 18500.0, indexMarketCap: 18500.0, baseDate: '1971-02-05', baseValue: 100, calculationMethod: 'Взвешенная по капитализации', currency: 'USD', exchange: 'NASDAQ' },
  { symbol: 'DOW', name: 'Dow Jones Industrial', price: 39127.80, change: 0.32, changePoints: 124.56, open: 39050.00, high: 39198.45, low: 38985.30, flag: '🇺🇸', country: 'US', region: 'usa', history: [] as number[], constituentsCount: 30, totalMarketCap: 9850.0, indexMarketCap: 9850.0, baseDate: '1896-05-26', baseValue: 40.94, calculationMethod: 'Ценово-взвешенный', currency: 'USD', exchange: 'NYSE' },
  { symbol: 'NDX', name: 'NASDAQ 100', price: 18234.56, change: 0.92, changePoints: 166.23, open: 18100.00, high: 18290.80, low: 18050.45, flag: '🇺🇸', country: 'US', region: 'usa', history: [] as number[] },
  { symbol: 'RUT', name: 'Russell 2000', price: 2045.67, change: -0.23, changePoints: -4.71, open: 2052.00, high: 2058.90, low: 2038.30, flag: '🇺🇸', country: 'US', region: 'usa', history: [] as number[] },
  { symbol: 'VIX', name: 'CBOE Volatility Index', price: 14.56, change: -2.34, changePoints: -0.35, open: 14.90, high: 15.20, low: 14.30, flag: '🇺🇸', country: 'US', region: 'usa', history: [] as number[] },
  { symbol: 'DJT', name: 'Dow Jones Transport', price: 15678.90, change: 0.45, changePoints: 70.12, open: 15620.00, high: 15720.50, low: 15580.30, flag: '🇺🇸', country: 'US', region: 'usa', history: [] as number[] },
  { symbol: 'SOX', name: 'PHLX Semiconductor', price: 4567.89, change: 1.89, changePoints: 84.67, open: 4490.00, high: 4590.80, low: 4470.45, flag: '🇺🇸', country: 'US', region: 'usa', history: [] as number[] },
  
  // Europe
  { symbol: 'DAX', name: 'DAX 40', price: 18456.78, change: -0.28, changePoints: -52.34, open: 18520.00, high: 18545.90, low: 18412.30, flag: '🇩🇪', country: 'DE', region: 'europe', history: [] as number[], constituentsCount: 40, totalMarketCap: 1850.0, indexMarketCap: 1850.0, baseDate: '1987-12-30', baseValue: 1000, calculationMethod: 'Взвешенная по капитализации', currency: 'EUR', exchange: 'XETRA' },
  { symbol: 'FTSE', name: 'FTSE 100', price: 8234.56, change: 0.15, changePoints: 12.34, open: 8225.00, high: 8256.80, low: 8198.45, flag: '🇬🇧', country: 'GB', region: 'europe', history: [] as number[], constituentsCount: 100, totalMarketCap: 2150.0, indexMarketCap: 2150.0, baseDate: '1984-01-03', baseValue: 1000, calculationMethod: 'Взвешенная по капитализации', currency: 'GBP', exchange: 'LSE' },
  { symbol: 'CAC', name: 'CAC 40', price: 7845.23, change: -0.42, changePoints: -33.12, open: 7890.00, high: 7912.50, low: 7820.30, flag: '🇫🇷', country: 'FR', region: 'europe', history: [] as number[], constituentsCount: 40, totalMarketCap: 1850.0, indexMarketCap: 1850.0, baseDate: '1987-12-31', baseValue: 1000, calculationMethod: 'Взвешенная по капитализации', currency: 'EUR', exchange: 'Euronext Paris' },
  { symbol: 'STOXX50', name: 'Euro Stoxx 50', price: 4987.65, change: 0.23, changePoints: 11.45, open: 4980.00, high: 5010.90, low: 4965.30, flag: '🇪🇺', country: 'EU', region: 'europe', history: [] as number[] },
  { symbol: 'IBEX', name: 'IBEX 35', price: 11234.56, change: 0.67, changePoints: 74.89, open: 11170.00, high: 11280.80, low: 11150.45, flag: '🇪🇸', country: 'ES', region: 'europe', history: [] as number[] },
  { symbol: 'FTSEMIB', name: 'FTSE MIB', price: 33456.78, change: -0.15, changePoints: -50.23, open: 33520.00, high: 33580.50, low: 33380.30, flag: '🇮🇹', country: 'IT', region: 'europe', history: [] as number[] },
  { symbol: 'AEX', name: 'AEX Amsterdam', price: 876.54, change: 0.34, changePoints: 2.97, open: 874.00, high: 880.90, low: 872.45, flag: '🇳🇱', country: 'NL', region: 'europe', history: [] as number[] },
  { symbol: 'SMI', name: 'Swiss Market Index', price: 12345.67, change: 0.18, changePoints: 22.12, open: 12330.00, high: 12380.50, low: 12300.30, flag: '🇨🇭', country: 'CH', region: 'europe', history: [] as number[] },
  { symbol: 'BEL20', name: 'BEL 20', price: 3789.45, change: -0.28, changePoints: -10.67, open: 3800.00, high: 3815.80, low: 3775.20, flag: '🇧🇪', country: 'BE', region: 'europe', history: [] as number[] },
  { symbol: 'ATX', name: 'ATX Vienna', price: 3567.89, change: 0.45, changePoints: 15.98, open: 3555.00, high: 3580.50, low: 3545.30, flag: '🇦🇹', country: 'AT', region: 'europe', history: [] as number[] },
  { symbol: 'OMX30', name: 'OMX Stockholm 30', price: 2345.67, change: 0.56, changePoints: 13.05, open: 2335.00, high: 2358.90, low: 2328.45, flag: '🇸🇪', country: 'SE', region: 'europe', history: [] as number[] },
  { symbol: 'PSI20', name: 'PSI 20', price: 6789.12, change: 0.23, changePoints: 15.56, open: 6775.00, high: 6810.80, low: 6760.45, flag: '🇵🇹', country: 'PT', region: 'europe', history: [] as number[] },
  
  // Asia
  { symbol: 'NIKKEI', name: 'Nikkei 225', price: 38456.78, change: 1.56, changePoints: 591.23, open: 37950.00, high: 38520.90, low: 37890.45, flag: '🇯🇵', country: 'JP', region: 'asia', history: [] as number[], constituentsCount: 225, totalMarketCap: 4850.0, indexMarketCap: 4850.0, baseDate: '1950-05-16', baseValue: 176.21, calculationMethod: 'Ценово-взвешенный', currency: 'JPY', exchange: 'TSE' },
  { symbol: 'HSI', name: 'Hang Seng Index', price: 18234.56, change: -0.89, changePoints: -163.78, open: 18420.00, high: 18478.90, low: 18156.30, flag: '🇭🇰', country: 'HK', region: 'asia', history: [] as number[] },
  { symbol: 'SSE', name: 'Shanghai Composite', price: 3089.45, change: 0.34, changePoints: 10.45, open: 3080.00, high: 3098.90, low: 3065.30, flag: '🇨🇳', country: 'CN', region: 'asia', history: [] as number[] },
  { symbol: 'SZSE', name: 'Shenzhen Component', price: 9876.54, change: 0.67, changePoints: 65.78, open: 9820.00, high: 9910.80, low: 9800.45, flag: '🇨🇳', country: 'CN', region: 'asia', history: [] as number[] },
  { symbol: 'KOSPI', name: 'KOSPI', price: 2567.89, change: -0.45, changePoints: -11.56, open: 2580.00, high: 2590.90, low: 2555.30, flag: '🇰🇷', country: 'KR', region: 'asia', history: [] as number[] },
  { symbol: 'TWII', name: 'Taiwan Weighted', price: 21345.67, change: 1.23, changePoints: 259.45, open: 21100.00, high: 21400.50, low: 21050.30, flag: '🇹🇼', country: 'TW', region: 'asia', history: [] as number[] },
  { symbol: 'SENSEX', name: 'BSE Sensex', price: 72345.67, change: 0.78, changePoints: 559.23, open: 71850.00, high: 72500.90, low: 71700.45, flag: '🇮🇳', country: 'IN', region: 'asia', history: [] as number[] },
  { symbol: 'NIFTY', name: 'Nifty 50', price: 21987.65, change: 0.82, changePoints: 178.45, open: 21850.00, high: 22050.80, low: 21800.30, flag: '🇮🇳', country: 'IN', region: 'asia', history: [] as number[] },
  { symbol: 'STI', name: 'Straits Times Index', price: 3234.56, change: 0.23, changePoints: 7.42, open: 3228.00, high: 3245.90, low: 3220.45, flag: '🇸🇬', country: 'SG', region: 'asia', history: [] as number[] },
  { symbol: 'SET', name: 'SET Index', price: 1456.78, change: -0.34, changePoints: -4.97, open: 1462.00, high: 1468.90, low: 1450.30, flag: '🇹🇭', country: 'TH', region: 'asia', history: [] as number[] },
  { symbol: 'JKSE', name: 'Jakarta Composite', price: 7234.56, change: 0.45, changePoints: 32.34, open: 7210.00, high: 7260.80, low: 7195.45, flag: '🇮🇩', country: 'ID', region: 'asia', history: [] as number[] },
  { symbol: 'KLCI', name: 'FTSE Bursa Malaysia', price: 1567.89, change: 0.12, changePoints: 1.88, open: 1566.00, high: 1572.90, low: 1562.30, flag: '🇲🇾', country: 'MY', region: 'asia', history: [] as number[] },
  { symbol: 'ASX200', name: 'ASX 200', price: 7856.34, change: 0.56, changePoints: 43.78, open: 7820.00, high: 7880.90, low: 7805.45, flag: '🇦🇺', country: 'AU', region: 'asia', history: [] as number[] },
  { symbol: 'NZX50', name: 'NZX 50', price: 11567.89, change: 0.34, changePoints: 39.12, open: 11535.00, high: 11590.50, low: 11520.30, flag: '🇳🇿', country: 'NZ', region: 'asia', history: [] as number[] },
  
  // Latin America
  { symbol: 'BOVESPA', name: 'Bovespa', price: 128456.78, change: 1.23, changePoints: 1559.45, open: 127000.00, high: 128900.90, low: 126500.45, flag: '🇧🇷', country: 'BR', region: 'latam', history: [] as number[] },
  { symbol: 'IPC', name: 'IPC Mexico', price: 54678.90, change: -0.45, changePoints: -247.12, open: 54950.00, high: 55100.50, low: 54500.30, flag: '🇲🇽', country: 'MX', region: 'latam', history: [] as number[] },
  { symbol: 'MERVAL', name: 'MERVAL', price: 987654.32, change: 2.34, changePoints: 22567.89, open: 970000.00, high: 995000.90, low: 965000.45, flag: '🇦🇷', country: 'AR', region: 'latam', history: [] as number[] },
  { symbol: 'IPSA', name: 'IPSA Chile', price: 6234.56, change: 0.67, changePoints: 41.45, open: 6200.00, high: 6260.80, low: 6180.45, flag: '🇨🇱', country: 'CL', region: 'latam', history: [] as number[] },
  { symbol: 'COLCAP', name: 'COLCAP', price: 1345.67, change: -0.23, changePoints: -3.10, open: 1350.00, high: 1358.90, low: 1340.30, flag: '🇨🇴', country: 'CO', region: 'latam', history: [] as number[] },
  
  // Middle East
  { symbol: 'TASI', name: 'Tadawul All Share', price: 12345.67, change: 0.89, changePoints: 109.12, open: 12250.00, high: 12400.90, low: 12200.45, flag: '🇸🇦', country: 'SA', region: 'middle_east', history: [] as number[] },
  { symbol: 'ADX', name: 'Abu Dhabi Index', price: 9234.56, change: 0.45, changePoints: 41.34, open: 9200.00, high: 9260.80, low: 9180.45, flag: '🇦🇪', country: 'AE', region: 'middle_east', history: [] as number[] },
  { symbol: 'DFM', name: 'Dubai Financial Market', price: 4123.45, change: 0.67, changePoints: 27.45, open: 4100.00, high: 4140.90, low: 4090.30, flag: '🇦🇪', country: 'AE', region: 'middle_east', history: [] as number[] },
  { symbol: 'QE', name: 'Qatar Exchange', price: 10567.89, change: -0.34, changePoints: -36.12, open: 10610.00, high: 10640.50, low: 10540.30, flag: '🇶🇦', country: 'QA', region: 'middle_east', history: [] as number[] },
  { symbol: 'TA35', name: 'TA-35 Tel Aviv', price: 1987.65, change: 0.56, changePoints: 11.08, open: 1978.00, high: 1995.90, low: 1970.45, flag: '🇮🇱', country: 'IL', region: 'middle_east', history: [] as number[] },
  { symbol: 'EGX30', name: 'EGX 30', price: 27654.32, change: 0.78, changePoints: 214.23, open: 27450.00, high: 27800.90, low: 27380.45, flag: '🇪🇬', country: 'EG', region: 'middle_east', history: [] as number[] }
])

// Index Constituents (instruments for each index)
interface IndexConstituent {
  ticker: string
  name: string
  price: number
  change: number
  effectiveShares: number // Эффективное кол-во ЦБ (млн шт)
  marketCap: number // Капитализация (млрд руб)
  indexCap: number // Капитализация в индексе (млрд руб)
  weight: number // Вес в индексе (%)
}

const indexConstituents = ref<Record<string, IndexConstituent[]>>({
  'IMOEX': [
    { ticker: 'SBER', name: 'Сбербанк', price: 298.45, change: 2.34, effectiveShares: 21587, marketCap: 6443.2, indexCap: 6443.2, weight: 14.8 },
    { ticker: 'LKOH', name: 'ЛУКОЙЛ', price: 7234.50, change: 1.12, effectiveShares: 693, marketCap: 5013.5, indexCap: 5013.5, weight: 11.5 },
    { ticker: 'GAZP', name: 'Газпром', price: 167.89, change: -0.56, effectiveShares: 23673, marketCap: 3973.8, indexCap: 3973.8, weight: 9.1 },
    { ticker: 'NVTK', name: 'НОВАТЭК', price: 1456.78, change: 1.89, effectiveShares: 3036, marketCap: 4424.6, indexCap: 4424.6, weight: 10.2 },
    { ticker: 'ROSN', name: 'Роснефть', price: 578.90, change: 0.45, effectiveShares: 10598, marketCap: 6135.3, indexCap: 3067.7, weight: 7.0 },
    { ticker: 'GMKN', name: 'Норникель', price: 15678.00, change: 0.78, effectiveShares: 158, marketCap: 2477.1, indexCap: 2477.1, weight: 5.7 },
    { ticker: 'PLZL', name: 'Полюс', price: 14234.00, change: 2.45, effectiveShares: 133, marketCap: 1893.1, indexCap: 1893.1, weight: 4.4 },
    { ticker: 'TATN', name: 'Татнефть', price: 712.30, change: 0.67, effectiveShares: 2326, marketCap: 1656.5, indexCap: 1656.5, weight: 3.8 },
    { ticker: 'SNGS', name: 'Сургутнефтегаз', price: 28.45, change: 0.34, effectiveShares: 35725, marketCap: 1016.4, indexCap: 1016.4, weight: 2.3 },
    { ticker: 'YNDX', name: 'Яндекс', price: 3456.78, change: -1.23, effectiveShares: 361, marketCap: 1247.9, indexCap: 1247.9, weight: 2.9 },
    { ticker: 'TCSG', name: 'ТКС Холдинг', price: 2876.50, change: 1.56, effectiveShares: 199, marketCap: 572.4, indexCap: 572.4, weight: 1.3 },
    { ticker: 'VTBR', name: 'ВТБ', price: 0.0234, change: -0.89, effectiveShares: 12960000, marketCap: 303.3, indexCap: 303.3, weight: 0.7 },
    { ticker: 'MTSS', name: 'МТС', price: 287.45, change: -0.34, effectiveShares: 1998, marketCap: 574.2, indexCap: 574.2, weight: 1.3 },
    { ticker: 'MGNT', name: 'Магнит', price: 5678.90, change: 0.89, effectiveShares: 102, marketCap: 579.2, indexCap: 579.2, weight: 1.3 },
    { ticker: 'ALRS', name: 'АЛРОСА', price: 76.45, change: -0.78, effectiveShares: 7365, marketCap: 563.0, indexCap: 563.0, weight: 1.3 },
    { ticker: 'CHMF', name: 'Северсталь', price: 1456.80, change: 1.23, effectiveShares: 837, marketCap: 1219.3, indexCap: 1219.3, weight: 2.8 },
    { ticker: 'NLMK', name: 'НЛМК', price: 189.45, change: 0.67, effectiveShares: 5993, marketCap: 1135.0, indexCap: 1135.0, weight: 2.6 },
    { ticker: 'PHOR', name: 'ФосАгро', price: 6789.00, change: 0.45, effectiveShares: 129, marketCap: 875.8, indexCap: 875.8, weight: 2.0 },
    { ticker: 'MOEX', name: 'Мосбиржа', price: 234.56, change: 0.56, effectiveShares: 2276, marketCap: 534.0, indexCap: 534.0, weight: 1.2 },
    { ticker: 'PIKK', name: 'ПИК', price: 789.45, change: -0.34, effectiveShares: 660, marketCap: 521.0, indexCap: 521.0, weight: 1.2 },
    { ticker: 'POLY', name: 'Polymetal', price: 456.78, change: 1.89, effectiveShares: 473, marketCap: 216.1, indexCap: 216.1, weight: 0.5 },
    { ticker: 'IRAO', name: 'Интер РАО', price: 4.12, change: 0.23, effectiveShares: 104300, marketCap: 429.7, indexCap: 429.7, weight: 1.0 },
    { ticker: 'RUAL', name: 'РУСАЛ', price: 34.56, change: -1.12, effectiveShares: 15193, marketCap: 524.9, indexCap: 262.5, weight: 0.6 },
    { ticker: 'AFLT', name: 'Аэрофлот', price: 45.67, change: 0.89, effectiveShares: 2444, marketCap: 111.6, indexCap: 111.6, weight: 0.3 },
    { ticker: 'FEES', name: 'ФСК ЕЭС', price: 0.123, change: 0.45, effectiveShares: 1274536, marketCap: 156.8, indexCap: 156.8, weight: 0.4 }
  ],
  'RTS': [
    { ticker: 'SBER', name: 'Сбербанк', price: 3.32, change: 2.34, effectiveShares: 21587, marketCap: 71.7, indexCap: 71.7, weight: 14.8 },
    { ticker: 'LKOH', name: 'ЛУКОЙЛ', price: 80.56, change: 1.12, effectiveShares: 693, marketCap: 55.9, indexCap: 55.9, weight: 11.5 },
    { ticker: 'GAZP', name: 'Газпром', price: 1.87, change: -0.56, effectiveShares: 23673, marketCap: 44.3, indexCap: 44.3, weight: 9.1 },
    { ticker: 'NVTK', name: 'НОВАТЭК', price: 16.23, change: 1.89, effectiveShares: 3036, marketCap: 49.3, indexCap: 49.3, weight: 10.2 },
    { ticker: 'ROSN', name: 'Роснефть', price: 6.44, change: 0.45, effectiveShares: 10598, marketCap: 68.3, indexCap: 34.1, weight: 7.0 },
    { ticker: 'GMKN', name: 'Норникель', price: 174.64, change: 0.78, effectiveShares: 158, marketCap: 27.6, indexCap: 27.6, weight: 5.7 },
    { ticker: 'PLZL', name: 'Полюс', price: 158.48, change: 2.45, effectiveShares: 133, marketCap: 21.1, indexCap: 21.1, weight: 4.4 },
    { ticker: 'TATN', name: 'Татнефть', price: 7.93, change: 0.67, effectiveShares: 2326, marketCap: 18.4, indexCap: 18.4, weight: 3.8 },
    { ticker: 'SNGS', name: 'Сургутнефтегаз', price: 0.32, change: 0.34, effectiveShares: 35725, marketCap: 11.3, indexCap: 11.3, weight: 2.3 },
    { ticker: 'YNDX', name: 'Яндекс', price: 38.50, change: -1.23, effectiveShares: 361, marketCap: 13.9, indexCap: 13.9, weight: 2.9 },
    { ticker: 'CHMF', name: 'Северсталь', price: 16.22, change: 1.23, effectiveShares: 837, marketCap: 13.6, indexCap: 13.6, weight: 2.8 },
    { ticker: 'NLMK', name: 'НЛМК', price: 2.11, change: 0.67, effectiveShares: 5993, marketCap: 12.6, indexCap: 12.6, weight: 2.6 }
  ],
  'RGBI': [
    { ticker: 'SU26238', name: 'ОФЗ 26238', price: 56.78, change: -0.12, effectiveShares: 450, marketCap: 25.6, indexCap: 25.6, weight: 8.5 },
    { ticker: 'SU26243', name: 'ОФЗ 26243', price: 89.45, change: 0.08, effectiveShares: 380, marketCap: 34.0, indexCap: 34.0, weight: 11.3 },
    { ticker: 'SU26240', name: 'ОФЗ 26240', price: 72.34, change: -0.05, effectiveShares: 420, marketCap: 30.4, indexCap: 30.4, weight: 10.1 },
    { ticker: 'SU26241', name: 'ОФЗ 26241', price: 85.67, change: 0.15, effectiveShares: 350, marketCap: 30.0, indexCap: 30.0, weight: 10.0 },
    { ticker: 'SU26239', name: 'ОФЗ 26239', price: 67.89, change: -0.08, effectiveShares: 400, marketCap: 27.2, indexCap: 27.2, weight: 9.0 },
    { ticker: 'SU26244', name: 'ОФЗ 26244', price: 94.56, change: 0.12, effectiveShares: 280, marketCap: 26.5, indexCap: 26.5, weight: 8.8 },
    { ticker: 'SU26233', name: 'ОФЗ 26233', price: 78.90, change: -0.03, effectiveShares: 320, marketCap: 25.2, indexCap: 25.2, weight: 8.4 },
    { ticker: 'SU26235', name: 'ОФЗ 26235', price: 82.34, change: 0.06, effectiveShares: 290, marketCap: 23.9, indexCap: 23.9, weight: 7.9 },
    { ticker: 'SU26230', name: 'ОФЗ 26230', price: 98.12, change: 0.02, effectiveShares: 220, marketCap: 21.6, indexCap: 21.6, weight: 7.2 },
    { ticker: 'SU26234', name: 'ОФЗ 26234', price: 75.45, change: -0.10, effectiveShares: 280, marketCap: 21.1, indexCap: 21.1, weight: 7.0 }
  ],
  'S&P 500': [
    { ticker: 'AAPL', name: 'Apple Inc.', price: 185.92, change: 0.45, effectiveShares: 15441, marketCap: 2870.5, indexCap: 2870.5, weight: 7.1 },
    { ticker: 'MSFT', name: 'Microsoft Corp.', price: 378.91, change: 1.23, effectiveShares: 7432, marketCap: 2815.8, indexCap: 2815.8, weight: 7.0 },
    { ticker: 'AMZN', name: 'Amazon.com Inc.', price: 178.25, change: -0.34, effectiveShares: 10334, marketCap: 1842.0, indexCap: 1842.0, weight: 4.6 },
    { ticker: 'NVDA', name: 'NVIDIA Corp.', price: 495.22, change: 2.89, effectiveShares: 2469, marketCap: 1223.1, indexCap: 1223.1, weight: 3.0 },
    { ticker: 'GOOGL', name: 'Alphabet Inc. A', price: 141.80, change: 0.67, effectiveShares: 5915, marketCap: 838.8, indexCap: 838.8, weight: 2.1 },
    { ticker: 'GOOG', name: 'Alphabet Inc. C', price: 143.12, change: 0.72, effectiveShares: 5756, marketCap: 823.7, indexCap: 823.7, weight: 2.0 },
    { ticker: 'META', name: 'Meta Platforms', price: 505.95, change: 1.56, effectiveShares: 2580, marketCap: 1305.4, indexCap: 1305.4, weight: 3.2 },
    { ticker: 'TSLA', name: 'Tesla Inc.', price: 248.48, change: -1.78, effectiveShares: 3178, marketCap: 789.7, indexCap: 789.7, weight: 2.0 },
    { ticker: 'BRK.B', name: 'Berkshire Hathaway B', price: 363.54, change: 0.23, effectiveShares: 2172, marketCap: 789.6, indexCap: 789.6, weight: 2.0 },
    { ticker: 'UNH', name: 'UnitedHealth Group', price: 527.84, change: -0.45, effectiveShares: 935, marketCap: 493.5, indexCap: 493.5, weight: 1.2 },
    { ticker: 'JNJ', name: 'Johnson & Johnson', price: 156.23, change: 0.34, effectiveShares: 2408, marketCap: 376.2, indexCap: 376.2, weight: 0.9 },
    { ticker: 'V', name: 'Visa Inc.', price: 279.45, change: 0.89, effectiveShares: 1654, marketCap: 462.3, indexCap: 462.3, weight: 1.1 },
    { ticker: 'XOM', name: 'Exxon Mobil Corp.', price: 104.56, change: 1.12, effectiveShares: 4011, marketCap: 419.5, indexCap: 419.5, weight: 1.0 },
    { ticker: 'JPM', name: 'JPMorgan Chase', price: 198.34, change: 0.67, effectiveShares: 2867, marketCap: 568.6, indexCap: 568.6, weight: 1.4 },
    { ticker: 'PG', name: 'Procter & Gamble', price: 158.90, change: 0.23, effectiveShares: 2360, marketCap: 375.0, indexCap: 375.0, weight: 0.9 },
    { ticker: 'MA', name: 'Mastercard Inc.', price: 456.78, change: 1.05, effectiveShares: 934, marketCap: 426.6, indexCap: 426.6, weight: 1.1 },
    { ticker: 'HD', name: 'Home Depot Inc.', price: 345.67, change: -0.56, effectiveShares: 1003, marketCap: 346.7, indexCap: 346.7, weight: 0.9 },
    { ticker: 'CVX', name: 'Chevron Corp.', price: 151.23, change: 0.78, effectiveShares: 1834, marketCap: 277.4, indexCap: 277.4, weight: 0.7 },
    { ticker: 'MRK', name: 'Merck & Co.', price: 125.89, change: 0.45, effectiveShares: 2535, marketCap: 319.1, indexCap: 319.1, weight: 0.8 },
    { ticker: 'ABBV', name: 'AbbVie Inc.', price: 178.45, change: 0.34, effectiveShares: 1767, marketCap: 315.3, indexCap: 315.3, weight: 0.8 }
  ],
  'NASDAQ': [
    { ticker: 'AAPL', name: 'Apple Inc.', price: 185.92, change: 0.45, effectiveShares: 15441, marketCap: 2870.5, indexCap: 2870.5, weight: 11.2 },
    { ticker: 'MSFT', name: 'Microsoft Corp.', price: 378.91, change: 1.23, effectiveShares: 7432, marketCap: 2815.8, indexCap: 2815.8, weight: 10.9 },
    { ticker: 'AMZN', name: 'Amazon.com Inc.', price: 178.25, change: -0.34, effectiveShares: 10334, marketCap: 1842.0, indexCap: 1842.0, weight: 7.2 },
    { ticker: 'NVDA', name: 'NVIDIA Corp.', price: 495.22, change: 2.89, effectiveShares: 2469, marketCap: 1223.1, indexCap: 1223.1, weight: 4.8 },
    { ticker: 'GOOGL', name: 'Alphabet Inc. A', price: 141.80, change: 0.67, effectiveShares: 5915, marketCap: 838.8, indexCap: 838.8, weight: 3.3 },
    { ticker: 'GOOG', name: 'Alphabet Inc. C', price: 143.12, change: 0.72, effectiveShares: 5756, marketCap: 823.7, indexCap: 823.7, weight: 3.2 },
    { ticker: 'META', name: 'Meta Platforms', price: 505.95, change: 1.56, effectiveShares: 2580, marketCap: 1305.4, indexCap: 1305.4, weight: 5.1 },
    { ticker: 'TSLA', name: 'Tesla Inc.', price: 248.48, change: -1.78, effectiveShares: 3178, marketCap: 789.7, indexCap: 789.7, weight: 3.1 },
    { ticker: 'AVGO', name: 'Broadcom Inc.', price: 1234.56, change: 1.45, effectiveShares: 416, marketCap: 513.6, indexCap: 513.6, weight: 2.0 },
    { ticker: 'COST', name: 'Costco Wholesale', price: 745.89, change: 0.67, effectiveShares: 443, marketCap: 330.4, indexCap: 330.4, weight: 1.3 },
    { ticker: 'PEP', name: 'PepsiCo Inc.', price: 172.34, change: 0.23, effectiveShares: 1375, marketCap: 236.9, indexCap: 236.9, weight: 0.9 },
    { ticker: 'CSCO', name: 'Cisco Systems', price: 52.45, change: 0.89, effectiveShares: 4023, marketCap: 211.0, indexCap: 211.0, weight: 0.8 },
    { ticker: 'ADBE', name: 'Adobe Inc.', price: 567.89, change: -0.45, effectiveShares: 449, marketCap: 255.0, indexCap: 255.0, weight: 1.0 },
    { ticker: 'NFLX', name: 'Netflix Inc.', price: 478.90, change: 2.12, effectiveShares: 432, marketCap: 206.9, indexCap: 206.9, weight: 0.8 },
    { ticker: 'AMD', name: 'AMD Inc.', price: 156.78, change: 3.45, effectiveShares: 1617, marketCap: 253.5, indexCap: 253.5, weight: 1.0 },
    { ticker: 'INTC', name: 'Intel Corp.', price: 34.56, change: -1.23, effectiveShares: 4225, marketCap: 146.0, indexCap: 146.0, weight: 0.6 },
    { ticker: 'QCOM', name: 'Qualcomm Inc.', price: 167.89, change: 1.78, effectiveShares: 1116, marketCap: 187.4, indexCap: 187.4, weight: 0.7 },
    { ticker: 'INTU', name: 'Intuit Inc.', price: 634.56, change: 0.56, effectiveShares: 281, marketCap: 178.3, indexCap: 178.3, weight: 0.7 },
    { ticker: 'CMCSA', name: 'Comcast Corp.', price: 43.21, change: 0.34, effectiveShares: 3856, marketCap: 166.6, indexCap: 166.6, weight: 0.7 },
    { ticker: 'TXN', name: 'Texas Instruments', price: 178.90, change: 0.89, effectiveShares: 910, marketCap: 162.8, indexCap: 162.8, weight: 0.6 }
  ],
  'DOW': [
    { ticker: 'UNH', name: 'UnitedHealth Group', price: 527.84, change: -0.45, effectiveShares: 935, marketCap: 493.5, indexCap: 493.5, weight: 8.9 },
    { ticker: 'GS', name: 'Goldman Sachs', price: 456.78, change: 1.23, effectiveShares: 327, marketCap: 149.4, indexCap: 149.4, weight: 7.7 },
    { ticker: 'MSFT', name: 'Microsoft Corp.', price: 378.91, change: 1.23, effectiveShares: 7432, marketCap: 2815.8, indexCap: 2815.8, weight: 6.4 },
    { ticker: 'HD', name: 'Home Depot Inc.', price: 345.67, change: -0.56, effectiveShares: 1003, marketCap: 346.7, indexCap: 346.7, weight: 5.8 },
    { ticker: 'CAT', name: 'Caterpillar Inc.', price: 312.45, change: 0.89, effectiveShares: 509, marketCap: 159.0, indexCap: 159.0, weight: 5.3 },
    { ticker: 'AMGN', name: 'Amgen Inc.', price: 287.90, change: 0.67, effectiveShares: 536, marketCap: 154.3, indexCap: 154.3, weight: 4.9 },
    { ticker: 'V', name: 'Visa Inc.', price: 279.45, change: 0.89, effectiveShares: 1654, marketCap: 462.3, indexCap: 462.3, weight: 4.7 },
    { ticker: 'CRM', name: 'Salesforce Inc.', price: 267.89, change: -0.34, effectiveShares: 973, marketCap: 260.7, indexCap: 260.7, weight: 4.5 },
    { ticker: 'MCD', name: 'McDonald\'s Corp.', price: 265.34, change: 0.45, effectiveShares: 719, marketCap: 190.8, indexCap: 190.8, weight: 4.5 },
    { ticker: 'AXP', name: 'American Express', price: 234.56, change: 1.12, effectiveShares: 729, marketCap: 171.0, indexCap: 171.0, weight: 4.0 },
    { ticker: 'TRV', name: 'Travelers Cos.', price: 223.45, change: 0.56, effectiveShares: 232, marketCap: 51.8, indexCap: 51.8, weight: 3.8 },
    { ticker: 'JPM', name: 'JPMorgan Chase', price: 198.34, change: 0.67, effectiveShares: 2867, marketCap: 568.6, indexCap: 568.6, weight: 3.4 },
    { ticker: 'IBM', name: 'IBM Corp.', price: 187.65, change: 0.89, effectiveShares: 909, marketCap: 170.5, indexCap: 170.5, weight: 3.2 },
    { ticker: 'AAPL', name: 'Apple Inc.', price: 185.92, change: 0.45, effectiveShares: 15441, marketCap: 2870.5, indexCap: 2870.5, weight: 3.1 },
    { ticker: 'HON', name: 'Honeywell Int\'l', price: 198.76, change: 0.34, effectiveShares: 654, marketCap: 130.0, indexCap: 130.0, weight: 3.4 }
  ],
  'DAX': [
    { ticker: 'SAP', name: 'SAP SE', price: 176.42, change: 0.89, effectiveShares: 1229, marketCap: 216.8, indexCap: 216.8, weight: 10.3 },
    { ticker: 'SIE', name: 'Siemens AG', price: 172.56, change: 0.45, effectiveShares: 800, marketCap: 138.0, indexCap: 138.0, weight: 6.6 },
    { ticker: 'ALV', name: 'Allianz SE', price: 254.80, change: -0.23, effectiveShares: 412, marketCap: 105.0, indexCap: 105.0, weight: 5.0 },
    { ticker: 'DTE', name: 'Deutsche Telekom', price: 22.34, change: 0.67, effectiveShares: 4978, marketCap: 111.2, indexCap: 111.2, weight: 5.3 },
    { ticker: 'AIR', name: 'Airbus SE', price: 145.67, change: 1.23, effectiveShares: 789, marketCap: 114.9, indexCap: 114.9, weight: 5.5 },
    { ticker: 'MBG', name: 'Mercedes-Benz Group', price: 72.34, change: -0.78, effectiveShares: 1069, marketCap: 77.3, indexCap: 77.3, weight: 3.7 },
    { ticker: 'BMW', name: 'BMW AG', price: 98.45, change: 0.56, effectiveShares: 588, marketCap: 57.9, indexCap: 57.9, weight: 2.8 },
    { ticker: 'MRK', name: 'Merck KGaA', price: 152.65, change: 1.12, effectiveShares: 434, marketCap: 66.3, indexCap: 66.3, weight: 3.2 },
    { ticker: 'DHL', name: 'DHL Group', price: 41.23, change: 0.34, effectiveShares: 1199, marketCap: 49.4, indexCap: 49.4, weight: 2.4 },
    { ticker: 'MUV2', name: 'Munich Re', price: 423.56, change: 0.89, effectiveShares: 140, marketCap: 59.3, indexCap: 59.3, weight: 2.8 },
    { ticker: 'BAS', name: 'BASF SE', price: 45.78, change: -0.45, effectiveShares: 891, marketCap: 40.8, indexCap: 40.8, weight: 1.9 },
    { ticker: 'BAYN', name: 'Bayer AG', price: 28.90, change: -1.23, effectiveShares: 982, marketCap: 28.4, indexCap: 28.4, weight: 1.4 },
    { ticker: 'IFX', name: 'Infineon Tech.', price: 34.56, change: 2.34, effectiveShares: 1304, marketCap: 45.1, indexCap: 45.1, weight: 2.1 },
    { ticker: 'VOW3', name: 'Volkswagen AG', price: 112.34, change: 0.67, effectiveShares: 501, marketCap: 56.3, indexCap: 56.3, weight: 2.7 },
    { ticker: 'ADS', name: 'Adidas AG', price: 234.56, change: 1.56, effectiveShares: 178, marketCap: 41.8, indexCap: 41.8, weight: 2.0 }
  ],
  'FTSE': [
    { ticker: 'SHEL', name: 'Shell PLC', price: 27.45, change: 0.78, effectiveShares: 6234, marketCap: 171.1, indexCap: 171.1, weight: 8.2 },
    { ticker: 'AZN', name: 'AstraZeneca PLC', price: 112.34, change: 0.45, effectiveShares: 1556, marketCap: 174.8, indexCap: 174.8, weight: 8.4 },
    { ticker: 'HSBA', name: 'HSBC Holdings', price: 6.78, change: 0.34, effectiveShares: 19789, marketCap: 134.2, indexCap: 134.2, weight: 6.4 },
    { ticker: 'ULVR', name: 'Unilever PLC', price: 43.56, change: 0.23, effectiveShares: 2534, marketCap: 110.4, indexCap: 110.4, weight: 5.3 },
    { ticker: 'BP', name: 'BP PLC', price: 5.12, change: 1.12, effectiveShares: 17856, marketCap: 91.4, indexCap: 91.4, weight: 4.4 },
    { ticker: 'GSK', name: 'GSK PLC', price: 15.67, change: 0.67, effectiveShares: 4056, marketCap: 63.6, indexCap: 63.6, weight: 3.0 },
    { ticker: 'RIO', name: 'Rio Tinto PLC', price: 54.32, change: -0.45, effectiveShares: 1623, marketCap: 88.2, indexCap: 88.2, weight: 4.2 },
    { ticker: 'DGE', name: 'Diageo PLC', price: 28.90, change: 0.56, effectiveShares: 2234, marketCap: 64.6, indexCap: 64.6, weight: 3.1 },
    { ticker: 'BATS', name: 'BAT PLC', price: 25.67, change: -0.34, effectiveShares: 2145, marketCap: 55.1, indexCap: 55.1, weight: 2.6 },
    { ticker: 'REL', name: 'RELX PLC', price: 34.56, change: 0.89, effectiveShares: 1923, marketCap: 66.5, indexCap: 66.5, weight: 3.2 },
    { ticker: 'LLOY', name: 'Lloyds Banking', price: 0.52, change: 0.23, effectiveShares: 63456, marketCap: 33.0, indexCap: 33.0, weight: 1.6 },
    { ticker: 'BARC', name: 'Barclays PLC', price: 2.12, change: 0.78, effectiveShares: 15234, marketCap: 32.3, indexCap: 32.3, weight: 1.5 }
  ],
  'CAC': [
    { ticker: 'MC', name: 'LVMH', price: 789.45, change: 0.89, effectiveShares: 502, marketCap: 396.4, indexCap: 396.4, weight: 12.8 },
    { ticker: 'OR', name: 'L\'Oreal', price: 412.34, change: 0.45, effectiveShares: 538, marketCap: 221.8, indexCap: 221.8, weight: 7.2 },
    { ticker: 'RMS', name: 'Hermes Int\'l', price: 2134.56, change: 1.23, effectiveShares: 105, marketCap: 224.1, indexCap: 224.1, weight: 7.2 },
    { ticker: 'TTE', name: 'TotalEnergies', price: 62.34, change: 0.67, effectiveShares: 2345, marketCap: 146.2, indexCap: 146.2, weight: 4.7 },
    { ticker: 'SAN', name: 'Sanofi', price: 89.56, change: 0.34, effectiveShares: 1256, marketCap: 112.5, indexCap: 112.5, weight: 3.6 },
    { ticker: 'SU', name: 'Schneider Electric', price: 198.45, change: 1.12, effectiveShares: 567, marketCap: 112.5, indexCap: 112.5, weight: 3.6 },
    { ticker: 'AI', name: 'Air Liquide', price: 178.90, change: 0.56, effectiveShares: 523, marketCap: 93.6, indexCap: 93.6, weight: 3.0 },
    { ticker: 'BNP', name: 'BNP Paribas', price: 62.34, change: -0.45, effectiveShares: 1234, marketCap: 76.9, indexCap: 76.9, weight: 2.5 },
    { ticker: 'KER', name: 'Kering', price: 345.67, change: -1.23, effectiveShares: 123, marketCap: 42.5, indexCap: 42.5, weight: 1.4 },
    { ticker: 'CDI', name: 'Christian Dior', price: 678.90, change: 0.78, effectiveShares: 178, marketCap: 120.8, indexCap: 120.8, weight: 3.9 }
  ],
  'NIKKEI': [
    { ticker: '7203', name: 'Toyota Motor', price: 2845.50, change: 0.78, effectiveShares: 16314, marketCap: 46420.5, indexCap: 46420.5, weight: 4.8 },
    { ticker: '6758', name: 'Sony Group', price: 12450.00, change: 1.34, effectiveShares: 1261, marketCap: 15699.5, indexCap: 15699.5, weight: 1.6 },
    { ticker: '9984', name: 'SoftBank Group', price: 8234.00, change: -0.56, effectiveShares: 1478, marketCap: 12170.1, indexCap: 12170.1, weight: 1.3 },
    { ticker: '6861', name: 'Keyence Corp', price: 62340.00, change: 0.89, effectiveShares: 243, marketCap: 15148.6, indexCap: 15148.6, weight: 1.6 },
    { ticker: '9432', name: 'NTT Corp', price: 178.50, change: 0.12, effectiveShares: 90591, marketCap: 16170.5, indexCap: 16170.5, weight: 1.7 },
    { ticker: '6501', name: 'Hitachi Ltd', price: 9876.00, change: 0.67, effectiveShares: 968, marketCap: 9560.1, indexCap: 9560.1, weight: 1.0 },
    { ticker: '7267', name: 'Honda Motor', price: 1567.50, change: 0.45, effectiveShares: 5134, marketCap: 8047.5, indexCap: 8047.5, weight: 0.8 },
    { ticker: '8306', name: 'MUFG Bank', price: 1423.00, change: 0.34, effectiveShares: 12890, marketCap: 18342.5, indexCap: 18342.5, weight: 1.9 },
    { ticker: '9433', name: 'KDDI Corp', price: 4567.00, change: 0.23, effectiveShares: 2290, marketCap: 10458.4, indexCap: 10458.4, weight: 1.1 },
    { ticker: '4063', name: 'Shin-Etsu Chemical', price: 5678.00, change: 1.56, effectiveShares: 1978, marketCap: 11231.1, indexCap: 11231.1, weight: 1.2 },
    { ticker: '4502', name: 'Takeda Pharma', price: 4123.00, change: -0.34, effectiveShares: 1561, marketCap: 6436.0, indexCap: 6436.0, weight: 0.7 },
    { ticker: '7974', name: 'Nintendo Co', price: 7890.00, change: 2.12, effectiveShares: 1298, marketCap: 10241.2, indexCap: 10241.2, weight: 1.1 },
    { ticker: '6902', name: 'Denso Corp', price: 2345.00, change: 0.56, effectiveShares: 3156, marketCap: 7400.8, indexCap: 7400.8, weight: 0.8 },
    { ticker: '8035', name: 'Tokyo Electron', price: 23456.00, change: 1.89, effectiveShares: 471, marketCap: 11047.8, indexCap: 11047.8, weight: 1.1 },
    { ticker: '6594', name: 'Nidec Corp', price: 5678.00, change: -0.78, effectiveShares: 1189, marketCap: 6751.1, indexCap: 6751.1, weight: 0.7 }
  ],
  'HSI': [
    { ticker: '0700', name: 'Tencent Holdings', price: 378.60, change: 1.23, effectiveShares: 9456, marketCap: 3580.1, indexCap: 3580.1, weight: 9.8 },
    { ticker: '9988', name: 'Alibaba Group', price: 89.45, change: -0.56, effectiveShares: 20123, marketCap: 1800.0, indexCap: 1800.0, weight: 4.9 },
    { ticker: '0939', name: 'CCB', price: 5.67, change: 0.34, effectiveShares: 250000, marketCap: 1417.5, indexCap: 1417.5, weight: 3.9 },
    { ticker: '1398', name: 'ICBC', price: 4.56, change: 0.23, effectiveShares: 356789, marketCap: 1626.9, indexCap: 1626.9, weight: 4.5 },
    { ticker: '0005', name: 'HSBC Holdings', price: 67.80, change: 0.45, effectiveShares: 19523, marketCap: 1323.9, indexCap: 1323.9, weight: 3.6 },
    { ticker: '3690', name: 'Meituan', price: 123.45, change: 2.34, effectiveShares: 6123, marketCap: 755.9, indexCap: 755.9, weight: 2.1 },
    { ticker: '0941', name: 'China Mobile', price: 72.34, change: 0.67, effectiveShares: 21456, marketCap: 1552.1, indexCap: 1552.1, weight: 4.3 },
    { ticker: '2318', name: 'Ping An Insurance', price: 45.67, change: -0.89, effectiveShares: 18234, marketCap: 832.7, indexCap: 832.7, weight: 2.3 },
    { ticker: '0883', name: 'CNOOC', price: 18.90, change: 1.12, effectiveShares: 44567, marketCap: 842.3, indexCap: 842.3, weight: 2.3 },
    { ticker: '1810', name: 'Xiaomi Corp', price: 17.56, change: 3.45, effectiveShares: 25123, marketCap: 441.2, indexCap: 441.2, weight: 1.2 },
    { ticker: '9618', name: 'JD.com', price: 134.56, change: 0.78, effectiveShares: 3145, marketCap: 423.1, indexCap: 423.1, weight: 1.2 },
    { ticker: '0388', name: 'HK Exchanges', price: 289.45, change: 0.56, effectiveShares: 1267, marketCap: 366.7, indexCap: 366.7, weight: 1.0 }
  ],
  'SSE': [
    { ticker: '601398', name: 'ICBC', price: 5.23, change: 0.34, effectiveShares: 356789, marketCap: 1866.0, indexCap: 1866.0, weight: 3.8 },
    { ticker: '601288', name: 'ABC', price: 3.78, change: 0.23, effectiveShares: 350000, marketCap: 1323.0, indexCap: 1323.0, weight: 2.7 },
    { ticker: '600519', name: 'Kweichow Moutai', price: 1789.00, change: 0.89, effectiveShares: 1256, marketCap: 2247.0, indexCap: 2247.0, weight: 4.6 },
    { ticker: '601318', name: 'Ping An Insurance', price: 52.34, change: -0.45, effectiveShares: 18290, marketCap: 957.3, indexCap: 957.3, weight: 1.9 },
    { ticker: '600036', name: 'China Merchants Bank', price: 34.56, change: 0.67, effectiveShares: 25234, marketCap: 872.1, indexCap: 872.1, weight: 1.8 },
    { ticker: '601166', name: 'Industrial Bank', price: 18.90, change: 0.34, effectiveShares: 20789, marketCap: 392.9, indexCap: 392.9, weight: 0.8 },
    { ticker: '600028', name: 'Sinopec Corp', price: 6.78, change: 1.23, effectiveShares: 121071, marketCap: 820.9, indexCap: 820.9, weight: 1.7 },
    { ticker: '601857', name: 'PetroChina', price: 8.45, change: 0.78, effectiveShares: 183021, marketCap: 1546.5, indexCap: 1546.5, weight: 3.1 },
    { ticker: '600900', name: 'CYPC', price: 23.45, change: 0.45, effectiveShares: 22500, marketCap: 527.6, indexCap: 527.6, weight: 1.1 },
    { ticker: '601012', name: 'LONGi Green', price: 28.90, change: -1.56, effectiveShares: 7567, marketCap: 218.7, indexCap: 218.7, weight: 0.4 },
    { ticker: '600309', name: 'Wanhua Chemical', price: 89.45, change: 0.67, effectiveShares: 3134, marketCap: 280.3, indexCap: 280.3, weight: 0.6 },
    { ticker: '601888', name: 'China Tourism', price: 78.90, change: 1.12, effectiveShares: 2067, marketCap: 163.1, indexCap: 163.1, weight: 0.3 }
  ]
})

// Get constituents for selected index
const getIndexConstituents = (indexSymbol: string): IndexConstituent[] => {
  return indexConstituents.value[indexSymbol] || []
}



// ============================================
// COMPUTED
// ============================================

const totalMarkets = computed(() => indices.value.length)
const growingMarkets = computed(() => indices.value.filter(i => i.change >= 0).length)
const fallingMarkets = computed(() => indices.value.filter(i => i.change < 0).length)

const filteredIndices = computed(() => {
  let result = indices.value

  // Filter by region
  if (activeRegion.value !== 'all') {
    result = result.filter(i => i.region === activeRegion.value)
  }

  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    result = result.filter(i =>
      i.symbol.toLowerCase().includes(query) ||
      i.name.toLowerCase().includes(query)
    )
  }

  return result
})

// Indices for catalog dropdown
const catalogIndices = computed(() => {
  let result = indices.value
  
  if (activeRegion.value !== 'all') {
    result = result.filter(i => i.region === activeRegion.value)
  }
  
  if (activeCountry.value !== 'all') {
    result = result.filter(i => i.country === activeCountry.value)
  }
  
  return result
})


// ============================================
// METHODS
// ============================================

const formatNumber = (num: number): string => {
  return num.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatMarketCap = (num: number, currency: string = ''): string => {
  if (num >= 1000) {
    return `${(num / 1000).toLocaleString('ru-RU', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} трлн ${currency}`
  } else {
    return `${num.toLocaleString('ru-RU', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} млрд ${currency}`
  }
}

// Dropdown catalog methods
const toggleIndicesCatalog = () => {
  showIndicesCatalog.value = !showIndicesCatalog.value
}

const selectRegion = (regionId: string) => {
  activeRegion.value = regionId
}

const getRegionCount = (regionId: string): number => {
  if (regionId === 'all') return indices.value.length
  return indices.value.filter(i => i.region === regionId).length
}

const getRegionCountries = (regionId: string) => {
  return countries.value[regionId] || []
}

const getCountryCount = (countryId: string): number => {
  return indices.value.filter(i => i.country === countryId).length
}

const getCountryName = (countryId: string): string => {
  for (const regionCountries of Object.values(countries.value)) {
    const country = regionCountries.find(c => c.id === countryId)
    if (country) return country.name
  }
  return countryId
}

const scrollToIndex = (symbol: string) => {
  showIndicesCatalog.value = false
  searchQuery.value = ''
  const index = indices.value.find(i => i.symbol === symbol)
  if (index) {
    showDetailView(index)
  }
}

const showDetailView = (index: IndexData) => {
  detailViewIndex.value = index
  // Initialize charts after DOM update
  setTimeout(() => {
    initVolatilitySurface()
    initWaveSurfaceDetail()
    initInsaneSurface()
  }, 100)
}

const closeDetailView = () => {
  detailViewIndex.value = null
  cleanupDetailCharts()
}

const cleanupDetailCharts = () => {
  if (waveAnimationInterval) {
    clearInterval(waveAnimationInterval)
    waveAnimationInterval = null
  }
  if (insaneAnimationInterval) {
    clearInterval(insaneAnimationInterval)
    insaneAnimationInterval = null
  }
}

const generateSparkline = (data: number[], width = 100, height = 30, centerLastPoint = false): string => {
  if (data.length < 2) {
    const randomData = Array.from({ length: 20 }, () => Math.random() * 10 + 45)
    data = randomData
  }

  const lastValue = data[data.length - 1]
  let min: number, max: number, range: number
  
  if (centerLastPoint) {
    // Center the last point vertically - show deviation from current price
    const deviations = data.map(v => v - lastValue)
    const maxDev = Math.max(...deviations.map(Math.abs)) || 1
    // Scale to use ~80% of height, centered
    const margin = height * 0.1
    const usableHeight = height - margin * 2
    
    // Calculate points with last point centered
    const points = data.map((value, index) => ({
      x: (index / (data.length - 1)) * width,
      y: height / 2 - ((value - lastValue) / maxDev) * (usableHeight / 2)
    }))
    
    if (points.length < 2) return ''
    
    // Generate smooth bezier curve path
    let path = `M ${points[0].x},${points[0].y}`
    
    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[Math.max(0, i - 1)]
      const p1 = points[i]
      const p2 = points[i + 1]
      const p3 = points[Math.min(points.length - 1, i + 2)]
      
      const tension = 0.4
      const cp1x = p1.x + (p2.x - p0.x) * tension
      const cp1y = p1.y + (p2.y - p0.y) * tension
      const cp2x = p2.x - (p3.x - p1.x) * tension
      const cp2y = p2.y - (p3.y - p1.y) * tension
      
      path += ` C ${cp1x},${cp1y} ${cp2x},${cp2y} ${p2.x},${p2.y}`
    }
    
    return path
  }
  
  // Original behavior for mini charts
  min = Math.min(...data)
  max = Math.max(...data)
  range = max - min || 1

  const points = data.map((value, index) => ({
    x: (index / (data.length - 1)) * width,
    y: height - ((value - min) / range) * height
  }))

  if (points.length < 2) return ''

  let path = `M ${points[0].x},${points[0].y}`

  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[Math.max(0, i - 1)]
    const p1 = points[i]
    const p2 = points[i + 1]
    const p3 = points[Math.min(points.length - 1, i + 2)]

    const tension = 0.4
    const cp1x = p1.x + (p2.x - p0.x) * tension
    const cp1y = p1.y + (p2.y - p0.y) * tension
    const cp2x = p2.x - (p3.x - p1.x) * tension
    const cp2y = p2.y - (p3.y - p1.y) * tension

    path += ` C ${cp1x},${cp1y} ${cp2x},${cp2y} ${p2.x},${p2.y}`
  }

  return path
}

const generateAreaPath = (data: number[], width = 100, height = 30, centerLastPoint = false): string => {
  const linePath = generateSparkline(data, width, height, centerLastPoint)
  if (!linePath) return ''

  const lastX = width
  const firstX = 0
  
  // For centered charts, fill to middle line
  const baseY = centerLastPoint ? height / 2 : height

  return `${linePath} L ${lastX},${baseY} L ${firstX},${baseY} Z`
}

// Generate area path that fills from center line
const generateAreaPathFromCenter = (data: number[], width: number, height: number): string => {
  const linePath = generateSparkline(data, width, height, true)
  if (!linePath) return ''

  const centerY = height / 2
  return `${linePath} L ${width},${centerY} L 0,${centerY} Z`
}

// Get Y position of the last point for the price dot (always centered)
const getLastPointY = (data: number[], height: number, centered = false): number => {
  if (centered || data.length === 0) return height / 2
  
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  const lastValue = data[data.length - 1]

  return height - ((lastValue - min) / range) * height
}

const updateCurrentTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const generateHistoryData = () => {
  indices.value.forEach(index => {
    const basePrice = index.price
    // Generate smooth initial data - gradual trend
    let currentPrice = basePrice * 0.998 // Start slightly lower
    index.history = Array.from({ length: 80 }, (_, i) => {
      // Very smooth random walk towards current price
      const targetBias = (basePrice - currentPrice) * 0.02 // Pull towards base price
      const randomStep = (Math.random() - 0.5) * basePrice * 0.0008
      currentPrice += targetBias + randomStep
      return currentPrice
    })
    // Ensure last point is close to actual price
    index.history[index.history.length - 1] = basePrice
  })
}

const updateMarketData = () => {
  indices.value.forEach(index => {
    // Smooth change updates
    const change = (Math.random() - 0.5) * 0.01
    index.change += change
    index.change = Math.max(-5, Math.min(5, index.change))
    index.changePoints = index.price * (index.change / 100)

    if (index.history.length > 0) {
      index.history.shift()
      // Very smooth price movement - tiny steps
      const lastPrice = index.history[index.history.length - 1] || index.price
      const direction = index.change > 0 ? 1 : -1
      const trendBias = direction * index.price * 0.00005 // Slight trend bias
      const randomStep = (Math.random() - 0.5) * index.price * 0.0003
      const newPrice = lastPrice + trendBias + randomStep
      index.history.push(newPrice)
    }
  })

}

// ============================================
// INDEX DETAIL MODAL METHODS
// ============================================

const openIndexDetail = (index: IndexData) => {
  selectedIndex.value = index
  chartType.value = 'line'
  document.body.style.overflow = 'hidden'
  
  // Init WAVE surface after DOM update
  setTimeout(() => {
    initWaveSurface(index.symbol)
  }, 100)
}

const closeIndexDetail = () => {
  cleanupWaveSurface()
  selectedIndex.value = null
  document.body.style.overflow = ''
}

const formatVolume = (volume: number): string => {
  if (volume >= 1e9) return (volume / 1e9).toFixed(2) + ' млрд'
  if (volume >= 1e6) return (volume / 1e6).toFixed(2) + ' млн'
  if (volume >= 1e3) return (volume / 1e3).toFixed(2) + ' тыс'
  return volume.toFixed(0)
}

// formatMarketCap теперь определена выше с поддержкой валюты

const getIndexVolume = (symbol: string): number => {
  const volumes: Record<string, number> = {
    'IMOEX': 85.6e9,
    'RTS': 42.3e9,
    'RGBI': 12.8e9,
    'S&P 500': 4.2e12,
    'NASDAQ': 3.8e12,
    'DOW': 2.1e12,
    'DAX': 1.5e12,
    'FTSE': 1.2e12,
    'CAC': 980e9,
    'NIKKEI': 2.8e12,
    'HSI': 1.6e12,
    'SSE': 3.2e12
  }
  return volumes[symbol] || 50e9
}

const getIndexMarketCap = (symbol: string): number => {
  const caps: Record<string, number> = {
    'IMOEX': 58.2e12,
    'RTS': 58.2e12,
    'RGBI': 15.4e12,
    'S&P 500': 42.5e12,
    'NASDAQ': 21.8e12,
    'DOW': 12.4e12,
    'DAX': 2.1e12,
    'FTSE': 2.8e12,
    'CAC': 2.4e12,
    'NIKKEI': 6.2e12,
    'HSI': 4.8e12,
    'SSE': 7.5e12
  }
  return caps[symbol] || 10e12
}

const getIndexPE = (symbol: string): number => {
  const pes: Record<string, number> = {
    'IMOEX': 5.2,
    'RTS': 5.2,
    'RGBI': 0,
    'S&P 500': 24.5,
    'NASDAQ': 32.8,
    'DOW': 21.3,
    'DAX': 14.2,
    'FTSE': 11.8,
    'CAC': 13.5,
    'NIKKEI': 22.1,
    'HSI': 9.8,
    'SSE': 12.4
  }
  return pes[symbol] || 15
}

const getWeekChange = (index: IndexData): number => {
  return index.change * 2.5 + (Math.random() - 0.5) * 2
}

const getMonthChange = (index: IndexData): number => {
  return index.change * 5 + (Math.random() - 0.5) * 5
}

const getYearChange = (index: IndexData): number => {
  return index.change * 15 + (Math.random() - 0.5) * 20
}

// Format constituent price based on index region
const formatConstituentPrice = (price: number, indexSymbol: string): string => {
  const isRussian = ['IMOEX', 'RTS', 'RGBI'].includes(indexSymbol)
  const isJapanese = ['NIKKEI'].includes(indexSymbol)
  
  if (isRussian && indexSymbol !== 'RTS') {
    return price.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' ₽'
  } else if (indexSymbol === 'RTS') {
    return '$' + price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  } else if (isJapanese) {
    return '¥' + price.toLocaleString('ja-JP', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
  } else {
    return '$' + price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  }
}

// Format shares in millions
const formatShares = (shares: number): string => {
  if (shares >= 1000) {
    return (shares / 1000).toFixed(1) + ' млрд'
  }
  return shares.toFixed(1) + ' млн'
}

// Format constituent capitalization
const formatConstituentCap = (cap: number, indexSymbol: string): string => {
  const isRussian = ['IMOEX', 'RTS', 'RGBI'].includes(indexSymbol)
  const isJapanese = ['NIKKEI'].includes(indexSymbol)
  
  if (isRussian) {
    if (cap >= 1000) {
      return (cap / 1000).toFixed(2) + ' трлн ₽'
    }
    return cap.toFixed(1) + ' млрд ₽'
  } else if (isJapanese) {
    if (cap >= 1000) {
      return '¥' + (cap / 1000).toFixed(2) + ' трлн'
    }
    return '¥' + cap.toFixed(1) + ' млрд'
  } else {
    if (cap >= 1000) {
      return '$' + (cap / 1000).toFixed(2) + ' трлн'
    }
    return '$' + cap.toFixed(1) + ' млрд'
  }
}

// Generate candlestick data from history
const getCandlestickData = (index: IndexData): Candle[] => {
  const history = index.history
  if (history.length < 4) return []

  const candles: Candle[] = []
  const candleCount = 40
  const chartWidth = 800
  const chartHeight = 300
  const padding = 25
  const candleWidth = (chartWidth - padding * 2) / candleCount * 0.65
  
  const min = Math.min(...history)
  const max = Math.max(...history)
  const range = max - min || 1
  
  for (let i = 0; i < candleCount; i++) {
    const startIdx = Math.floor(i * history.length / candleCount)
    const endIdx = Math.floor((i + 1) * history.length / candleCount)
    const segment = history.slice(startIdx, endIdx)
    
    if (segment.length === 0) continue
    
    const open = segment[0]
    const close = segment[segment.length - 1]
    const high = Math.max(...segment)
    const low = Math.min(...segment)
    const bullish = close >= open
    
    const x = padding + (i + 0.5) * (chartWidth - padding * 2) / candleCount
    const scaleY = (v: number) => chartHeight - padding - ((v - min) / range) * (chartHeight - padding * 2)
    
    candles.push({
      x,
      wickTop: scaleY(high),
      wickBottom: scaleY(low),
      bodyTop: scaleY(Math.max(open, close)),
      bodyHeight: Math.abs(scaleY(open) - scaleY(close)),
      width: candleWidth,
      bullish
    })
  }
  
  return candles
}

// Technical Indicators
const getRSI = (index: IndexData): number => {
  // Mock RSI calculation based on change
  const base = 50 + index.change * 5
  return Math.max(0, Math.min(100, base + (Math.random() - 0.5) * 10))
}

const getRSIClass = (index: IndexData): string => {
  const rsi = getRSI(index)
  if (rsi > 70) return 'overbought'
  if (rsi < 30) return 'oversold'
  return 'neutral'
}

const getMA20 = (index: IndexData): number => {
  return index.price * (1 - index.change / 100 * 0.5)
}

const getMA50 = (index: IndexData): number => {
  return index.price * (1 - index.change / 100 * 1.2)
}

const getTrend = (index: IndexData): string => {
  if (index.change > 1) return '↑ Восходящий'
  if (index.change < -1) return '↓ Нисходящий'
  return '→ Боковой'
}

const getTrendClass = (index: IndexData): string => {
  if (index.change > 1) return 'bullish'
  if (index.change < -1) return 'bearish'
  return 'neutral'
}

const getVolatilityPercent = (index: IndexData): number => {
  return Math.abs(index.high - index.low) / index.price * 100
}

// WAVE Surface functions
const getWaveRegime = (index: IndexData): string => {
  const volatility = getVolatilityPercent(index)
  if (volatility > 2) return 'CHOPPY'
  if (index.change > 1) return 'TRENDING UP'
  if (index.change < -1) return 'TRENDING DOWN'
  return 'STABLE'
}

const getWaveRegimeClass = (index: IndexData): string => {
  const regime = getWaveRegime(index)
  if (regime === 'CHOPPY') return 'regime-choppy'
  if (regime === 'TRENDING UP') return 'regime-up'
  if (regime === 'TRENDING DOWN') return 'regime-down'
  return 'regime-stable'
}

const getWaveMomentum = (index: IndexData): number => {
  return index.change / 2 + (Math.random() - 0.5) * 0.5
}

const getWaveVolatility = (index: IndexData): number => {
  return getVolatilityPercent(index) / 2 + (Math.random() - 0.5) * 0.3
}

const getWaveJaggedness = (index: IndexData): number => {
  const volatility = getVolatilityPercent(index)
  return Math.min(1, volatility / 3 + (Math.random() - 0.5) * 0.2)
}

// Initialize WAVE Surface with Plotly
const initWaveSurface = async (indexSymbol: string) => {
  // Load Plotly if needed
  await loadPlotly()
  if (!Plotly) {
    console.warn('Plotly not loaded, skipping WAVE surface')
    return
  }
  
  const containerId = `wave-surface-${indexSymbol}`
  const container = document.getElementById(containerId)
  if (!container) {
    console.warn(`Container ${containerId} not found`)
    return
  }
  
  const index = selectedIndex.value
  if (!index) return
  
  const isChoppy = getWaveRegime(index) === 'CHOPPY'
  
  const generateSurface = (offset: number) => {
    const n = 60 // More points for smoother surface
    const x = Array.from({length: n}, (_, i) => i / (n - 1))
    const y = Array.from({length: n}, (_, i) => i / (n - 1))
    
    const z = Array.from({length: n}, (_, i) => {
      return Array.from({length: n}, (_, j) => {
        // Smoother wave equations with longer wavelengths
        const wave1 = Math.sin((i + offset * 0.3) / 8) * Math.cos((j + offset * 0.3) / 8)
        const wave2 = Math.sin((i + j + offset * 0.2) / 12) * 0.5
        const base = wave1 + wave2
        const roughness = isChoppy ? 
          Math.sin((i + offset * 0.1) / 4) * Math.sin((j + offset * 0.1) / 4) * 0.3 : 
          Math.sin((i + offset * 0.05) / 15) * 0.1
        return base + roughness + getWaveJaggedness(index) * 0.5
      })
    })
    return { x, y, z }
  }

  const { x, y, z } = generateSurface(0)
  
  // Classic blue colorscale
  const colorscale = [
    [0.0, '#1e3a8a'],
    [0.15, '#3b82f6'],
    [0.3, '#22d3ee'],
    [0.45, '#10b981'],
    [0.6, '#84cc16'],
    [0.75, '#fbbf24'],
    [0.9, '#f97316'],
    [1.0, '#ef4444']
  ]

  const trace = {
    x: x,
    y: y,
    z: z,
    type: 'surface',
    colorscale: colorscale,
    showscale: true,
    colorbar: {
      title: { text: 'Риск', font: { color: 'rgba(255,255,255,0.9)', size: 11 } },
      tickfont: { color: 'rgba(255,255,255,0.7)', size: 10 },
      len: 0.6,
      thickness: 15,
      x: 1.02
    },
    contours: {
      z: { show: true, usecolorscale: true, project: { z: true }, width: 1 }
    },
    lighting: {
      ambient: 0.7,
      diffuse: 0.8,
      specular: 0.2,
      roughness: 0.6,
      fresnel: 0.1
    }
  }

  const layout = {
    scene: {
      xaxis: { 
        title: 'Momentum',
        backgroundcolor: 'rgba(0,0,0,0)',
        gridcolor: 'rgba(255,255,255,0.1)',
        titlefont: { color: 'rgba(255,255,255,0.8)', size: 12 },
        tickfont: { size: 9, color: 'rgba(255,255,255,0.5)' }
      },
      yaxis: { 
        title: 'Volatility',
        backgroundcolor: 'rgba(0,0,0,0)',
        gridcolor: 'rgba(255,255,255,0.1)',
        titlefont: { color: 'rgba(255,255,255,0.8)', size: 12 },
        tickfont: { size: 9, color: 'rgba(255,255,255,0.5)' }
      },
      zaxis: { 
        title: 'Jaggedness',
        backgroundcolor: 'rgba(0,0,0,0)',
        gridcolor: 'rgba(255,255,255,0.1)',
        titlefont: { color: 'rgba(255,255,255,0.8)', size: 12 },
        tickfont: { size: 9, color: 'rgba(255,255,255,0.5)' }
      },
      bgcolor: 'rgba(0,0,0,0)',
      camera: { eye: { x: 2.0, y: 2.0, z: 1.5 } },
      aspectratio: { x: 1.4, y: 1.1, z: 0.9 }
    },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: '#fff', size: 11 },
    margin: { l: 0, r: 60, b: 0, t: 10 },
    showlegend: false,
    autosize: true
  }

  const config = {
    responsive: true,
    displayModeBar: false,
    staticPlot: false
  }

  Plotly.newPlot(container, [trace], layout, config)

  // Smooth animation with small increments
  let frame = 0
  waveAnimationInterval = setInterval(() => {
    frame += 0.5 // Very small step for smooth animation
    const { x: newX, y: newY, z: newZ } = generateSurface(frame)
    Plotly.restyle(container, { z: [newZ], x: [newX], y: [newY] })
  }, 100) // Update every 100ms for smooth motion
}

// Cleanup WAVE animation
const cleanupWaveSurface = () => {
  if (waveAnimationInterval) {
    clearInterval(waveAnimationInterval)
    waveAnimationInterval = null
  }
}

// ============================================
// DETAIL VIEW CHARTS
// ============================================

// Initialize Static Volatility Surface (Cyberpunk style)
const initVolatilitySurface = async () => {
  await loadPlotly()
  if (!Plotly || !detailViewIndex.value) return
  
  const container = document.getElementById('volatility-surface-detail')
  if (!container) return
  
  const index = detailViewIndex.value
  const n = 80 // Increased for smoother surface
  const strikeRange = Array.from({length: n}, (_, i) => 80 + (i / (n - 1)) * 40) // 80-120%
  const timeRange = Array.from({length: n}, (_, i) => 0.1 + (i / (n - 1)) * 2) // 0.1-2.1 years
  
  // Generate smooth volatility surface based on index characteristics
  const baseVol = Math.abs(index.change) * 5 + 15
  const z = Array.from({length: n}, (_, i) => {
    return Array.from({length: n}, (_, j) => {
      const strike = strikeRange[i]
      const time = timeRange[j]
      // Volatility smile + term structure (smooth, no random noise)
      const moneyness = (strike - 100) / 100
      const smile = baseVol + 15 * moneyness * moneyness
      const termStructure = smile * (1 - 0.1 * Math.sqrt(time))
      const skew = -5 * moneyness * (1 - time / 2)
      // Smooth interpolation instead of random noise
      const smoothNoise = Math.sin(i * 0.1) * Math.cos(j * 0.1) * 0.5
      return termStructure + skew + smoothNoise
    })
  })

  // Classic blue-gray colorscale for volatility surface
  const colorscale = [
    [0.0, '#1a1a2e'],
    [0.1, '#16213e'],
    [0.2, '#0f3460'],
    [0.3, '#1e3a8a'],
    [0.4, '#3b82f6'],
    [0.5, '#60a5fa'],
    [0.6, '#93c5fd'],
    [0.7, '#bfdbfe'],
    [0.8, '#dbeafe'],
    [0.9, '#e0e7ff'],
    [1.0, '#f3f4f6']
  ]

  const trace = {
    x: strikeRange,
    y: timeRange,
    z: z,
    type: 'surface',
    colorscale: colorscale,
    showscale: true,
    colorbar: {
      title: { text: 'IV %', font: { color: 'rgba(255,255,255,0.9)', size: 11 } },
      tickfont: { color: 'rgba(255,255,255,0.7)', size: 10 },
      len: 0.7,
      thickness: 12,
      x: 1.02
    },
    contours: {
      z: { show: true, usecolorscale: true, project: { z: true }, width: 1 },
      x: { show: true, color: 'rgba(255,255,255,0.15)', width: 1 },
      y: { show: true, color: 'rgba(255,255,255,0.15)', width: 1 }
    },
    lighting: {
      ambient: 0.5,
      diffuse: 0.7,
      specular: 0.6,
      roughness: 0.4,
      fresnel: 0.2
    },
    lightposition: { x: 100, y: 200, z: 0 }
  }

  const layout = {
    scene: {
      xaxis: {
        title: { text: 'Strike %', font: { color: 'rgba(255,255,255,0.8)' } },
        backgroundcolor: 'transparent',
        gridcolor: 'rgba(255,255,255,0.1)',
        zerolinecolor: 'rgba(255,255,255,0.2)',
        tickfont: { size: 9, color: 'rgba(255,255,255,0.6)' },
        showbackground: false
      },
      yaxis: {
        title: { text: 'Срок (лет)', font: { color: 'rgba(255,255,255,0.8)' } },
        backgroundcolor: 'transparent',
        gridcolor: 'rgba(255,255,255,0.1)',
        zerolinecolor: 'rgba(255,255,255,0.2)',
        tickfont: { size: 9, color: 'rgba(255,255,255,0.6)' },
        showbackground: false
      },
      zaxis: {
        title: { text: 'Волатильность %', font: { color: 'rgba(255,255,255,0.8)' } },
        backgroundcolor: 'transparent',
        gridcolor: 'rgba(255,255,255,0.08)',
        tickfont: { size: 9, color: 'rgba(255,255,255,0.6)' },
        showbackground: false
      },
      bgcolor: 'transparent',
      camera: { eye: { x: 2.2, y: 1.5, z: 1.8 } }, // Raised higher for volatility surface
      aspectratio: { x: 1.3, y: 1, z: 0.75 }
    },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: 'rgba(255,255,255,0.9)', family: 'JetBrains Mono, monospace' },
    margin: { l: 0, r: 50, b: 0, t: 0 },
    showlegend: false,
    autosize: true
  }

  const config = {
    responsive: true,
    displayModeBar: false,
    scrollZoom: true,
    doubleClick: 'reset'
  }

  Plotly.newPlot(container, [trace], layout, config)

  // Enable camera rotation
  container.on('plotly_relayout', (eventData: any) => {
    if (eventData['scene.camera']) {
      // Camera was rotated, update layout
      layout.scene.camera = eventData['scene.camera']
    }
  })
}

// Initialize WAVE Surface for Detail View
const initWaveSurfaceDetail = async () => {
  await loadPlotly()
  if (!Plotly || !detailViewIndex.value) return
  
  const container = document.getElementById('wave-surface-detail')
  if (!container) return
  
  const index = detailViewIndex.value
  const n = 50 // Increased for smoother surface
  
  const generateSurface = (offset: number) => {
    const x = Array.from({length: n}, (_, i) => i / (n - 1))
    const y = Array.from({length: n}, (_, i) => i / (n - 1))
    const z = Array.from({length: n}, (_, i) => {
      return Array.from({length: n}, (_, j) => {
        // Smoother waves without random noise
        const wave1 = Math.sin((i + offset * 0.2) / 8) * Math.cos((j + offset * 0.2) / 8)
        const wave2 = Math.sin((i + j + offset * 0.15) / 12) * 0.4
        const wave3 = Math.sin((i - j + offset * 0.1) / 15) * 0.2
        return wave1 + wave2 + wave3
      })
    })
    return { x, y, z }
  }

  const { x, y, z } = generateSurface(0)
  
  // Classic blue-green colorscale for WAVE
  const trace = {
    x, y, z,
    type: 'surface',
    colorscale: [[0, '#1e3a8a'], [0.3, '#3b82f6'], [0.5, '#22d3ee'], [0.7, '#10b981'], [1, '#84cc16']],
    showscale: true,
    colorbar: { 
      title: { text: 'σ', font: { color: 'rgba(255,255,255,0.9)', size: 10 } }, 
      tickfont: { color: 'rgba(255,255,255,0.7)', size: 9 }, 
      len: 0.6
    },
    lighting: { ambient: 0.6, diffuse: 0.7, specular: 0.3 }
  }

  const layout = {
    scene: {
      xaxis: { 
        title: 'Momentum', 
        gridcolor: 'rgba(255,255,255,0.1)', 
        tickfont: { size: 8, color: 'rgba(255,255,255,0.5)' }, 
        titlefont: { color: 'rgba(255,255,255,0.8)' },
        backgroundcolor: 'transparent',
        showbackground: false
      },
      yaxis: { 
        title: 'Volatility', 
        gridcolor: 'rgba(255,255,255,0.1)', 
        tickfont: { size: 8, color: 'rgba(255,255,255,0.5)' }, 
        titlefont: { color: 'rgba(255,255,255,0.8)' },
        backgroundcolor: 'transparent',
        showbackground: false
      },
      zaxis: { 
        title: 'σ', 
        gridcolor: 'rgba(255,255,255,0.1)', 
        tickfont: { size: 8, color: 'rgba(255,255,255,0.5)' }, 
        titlefont: { color: 'rgba(255,255,255,0.8)' },
        backgroundcolor: 'transparent',
        showbackground: false
      },
      bgcolor: 'transparent',
      camera: { eye: { x: 1.8, y: 1.5, z: 1.2 } }, // Lowered camera for WAVE surface
      aspectratio: { x: 1.5, y: 1, z: 0.8 } // Wider aspect ratio
    },
    paper_bgcolor: 'transparent',
    font: { color: 'rgba(255,255,255,0.9)' },
    margin: { l: 0, r: 40, b: 0, t: 0 },
    autosize: true
  }

  const config = {
    responsive: true,
    displayModeBar: false,
    scrollZoom: true,
    doubleClick: 'reset'
  }

  Plotly.newPlot(container, [trace], layout, config)

  // Enable camera rotation
  container.on('plotly_relayout', (eventData: any) => {
    if (eventData['scene.camera']) {
      // Camera was rotated, update layout
      layout.scene.camera = eventData['scene.camera']
    }
  })

  let frame = 0
  waveAnimationInterval = setInterval(() => {
    frame += 0.15 // Slower increment for smoother animation
    const { z: newZ } = generateSurface(frame)
    Plotly.restyle(container, { z: [newZ] }, [0])
  }, 250) // Slower update interval
}

// Initialize INSANE Quant Latent Volatility Model
const initInsaneSurface = async () => {
  await loadPlotly()
  if (!Plotly || !detailViewIndex.value) return
  
  const container = document.getElementById('insane-surface-detail')
  if (!container) return
  
  const index = detailViewIndex.value
  const n = 50 // Increased for larger, smoother surface
  
  const generateLatentSurface = (offset: number) => {
    const x = Array.from({length: n}, (_, i) => -2 + (i / (n - 1)) * 4)
    const y = Array.from({length: n}, (_, i) => -2 + (i / (n - 1)) * 4)
    const z = Array.from({length: n}, (_, i) => {
      return Array.from({length: n}, (_, j) => {
        const xi = x[i], yj = y[j]
        // Smooth latent volatility peaks without random noise
        const peak1 = 2 * Math.exp(-((xi - 1 + offset * 0.08) ** 2 + (yj - 0.5) ** 2) / 1.5)
        const peak2 = 1.5 * Math.exp(-((xi + 0.5) ** 2 + (yj + 1 - offset * 0.06) ** 2) / 1.2)
        const peak3 = 1.8 * Math.exp(-((xi - offset * 0.04) ** 2 + (yj - 1.5) ** 2) / 1.8)
        // Smooth interpolation instead of noise
        const smoothWave = Math.sin(xi * 0.5 + offset * 0.1) * Math.cos(yj * 0.5) * 0.1
        return peak1 + peak2 + peak3 + smoothWave
      })
    })
    return { x, y, z }
  }

  const { x, y, z } = generateLatentSurface(0)
  
  // Classic purple-blue colorscale for INSANE model
  const colorscale = [
    [0.0, '#1a1a2e'],
    [0.2, '#16213e'],
    [0.4, '#0f3460'],
    [0.6, '#533483'],
    [0.8, '#8b5cf6'],
    [1.0, '#a78bfa']
  ]

  const trace = {
    x, y, z,
    type: 'surface',
    colorscale: colorscale,
    showscale: true,
    colorbar: { 
      title: { text: 'λ', font: { color: 'rgba(255,255,255,0.9)', size: 10 } }, 
      tickfont: { color: 'rgba(255,255,255,0.7)', size: 9 }, 
      len: 0.6
    },
    contours: {
      z: { show: true, usecolorscale: true, highlightcolor: 'rgba(139,92,246,0.5)', project: { z: true } }
    },
    lighting: { ambient: 0.5, diffuse: 0.6, specular: 0.5, roughness: 0.4 }
  }

  const layout = {
    scene: {
      xaxis: { 
        title: 'Latent X', 
        gridcolor: 'rgba(255,255,255,0.1)', 
        tickfont: { size: 8, color: 'rgba(255,255,255,0.5)' }, 
        titlefont: { color: 'rgba(255,255,255,0.8)' },
        backgroundcolor: 'transparent',
        showbackground: false
      },
      yaxis: { 
        title: 'Latent Y', 
        gridcolor: 'rgba(255,255,255,0.1)', 
        tickfont: { size: 8, color: 'rgba(255,255,255,0.5)' }, 
        titlefont: { color: 'rgba(255,255,255,0.8)' },
        backgroundcolor: 'transparent',
        showbackground: false
      },
      zaxis: { 
        title: 'Peak λ', 
        gridcolor: 'rgba(255,255,255,0.1)', 
        tickfont: { size: 8, color: 'rgba(255,255,255,0.5)' }, 
        titlefont: { color: 'rgba(255,255,255,0.8)' },
        backgroundcolor: 'transparent',
        showbackground: false
      },
      bgcolor: 'transparent',
      camera: { eye: { x: 2.5, y: 2.2, z: 1.8 } }, // Zoomed out and rotated counter-clockwise for INSANE surface
      aspectratio: { x: 1.4, y: 1, z: 0.9 } // Wider aspect ratio for better overview
    },
    paper_bgcolor: 'transparent',
    font: { color: 'rgba(255,255,255,0.9)' },
    margin: { l: -20, r: 50, b: 0, t: 0 }, // Shifted left to show colorbar
    autosize: true
  }

  const config = {
    responsive: true,
    displayModeBar: false,
    scrollZoom: true,
    doubleClick: 'reset'
  }

  Plotly.newPlot(container, [trace], layout, config)

  // Enable camera rotation
  container.on('plotly_relayout', (eventData: any) => {
    if (eventData['scene.camera']) {
      // Camera was rotated, update layout
      layout.scene.camera = eventData['scene.camera']
    }
  })

  let frame = 0
  insaneAnimationInterval = setInterval(() => {
    frame += 0.1 // Slower increment for smoother animation
    const { z: newZ } = generateLatentSurface(frame)
    Plotly.restyle(container, { z: [newZ] }, [0])
  }, 300) // Slower update interval
}

// ============================================
// LIFECYCLE
// ============================================

let timeInterval: ReturnType<typeof setInterval> | null = null
let dataInterval: ReturnType<typeof setInterval> | null = null

// Click outside handler for dropdown
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.indices-dropdown-wrapper')) {
    showIndicesCatalog.value = false
  }
}

onMounted(() => {
  updateCurrentTime()
  generateHistoryData()

  timeInterval = setInterval(updateCurrentTime, 1000)
  dataInterval = setInterval(updateMarketData, 1000) // Update every second

  document.addEventListener('click', handleClickOutside)
  
  // Set IMOEX as default index
  const imoex = indices.value.find(i => i.symbol === 'IMOEX')
  if (imoex) {
    showDetailView(imoex)
  }
})

onBeforeUnmount(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (dataInterval) clearInterval(dataInterval)
  document.removeEventListener('click', handleClickOutside)
  cleanupWaveSurface()
  cleanupDetailCharts()
})
</script>

<style scoped>
/* ============================================
   MARKETS PAGE - MATCHING MARKETDATA.VUE DESIGN
   ============================================ */

/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* ============================================
   FUTURISTIC GLASS + DARK NEON ORANGE
   ============================================ */

.markets-page {
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

.markets-page {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary-bg) 0%, var(--tertiary-bg) 100%);
  color: var(--text-primary);
  display: flex;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
  font-size: 12px;
  font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  position: relative;
  margin: 0;
  padding: 0;
}

/* ============================================
   SIDEBAR (matching MarketData.vue)
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
}

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

/* Back to Terminal Button */
.back-to-terminal {
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

.back-to-terminal:hover {
  border-color: var(--accent-cyan);
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(0, 150, 200, 0.08));
  color: var(--accent-cyan);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
}

.back-to-terminal svg {
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
  cursor: default;
}

/* Navigation Link Tab (goes to MarketData page) */
.nav-btn.nav-link-tab {
  text-decoration: none;
  display: block;
}

.nav-btn.nav-link-tab:hover {
  border-color: var(--accent-orange);
  background: rgba(255, 140, 0, 0.08);
  color: var(--text-primary);
  box-shadow: 0 0 10px rgba(255, 140, 0, 0.2);
  transform: translateY(-2px);
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

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
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
  font-family: 'JetBrains Mono', 'SF Mono', 'Monaco', monospace;
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
}

/* ============================================
   TICKER / MARQUEE
   ============================================ */
.ticker-wrapper {
  background: linear-gradient(135deg, rgba(20, 25, 35, 0.9), rgba(15, 18, 28, 0.95));
  border: 1px solid rgba(255, 140, 0, 0.3);
  border-radius: 16px;
  padding: 12px 0;
  margin-bottom: 16px;
  overflow: hidden;
  position: relative;
}

.ticker-wrapper::before,
.ticker-wrapper::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  width: 60px;
  z-index: 2;
  pointer-events: none;
}

.ticker-wrapper::before {
  left: 0;
  background: linear-gradient(to right, rgba(20, 25, 35, 1), transparent);
}

.ticker-wrapper::after {
  right: 0;
  background: linear-gradient(to left, rgba(20, 25, 35, 1), transparent);
}

.ticker-track {
  display: flex;
  animation: ticker-scroll 60s linear infinite;
}

.ticker-track:hover {
  animation-play-state: paused;
}

@keyframes ticker-scroll {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

.ticker-content {
  display: flex;
  gap: 8px;
  padding: 0 4px;
}

.ticker-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 8px 14px;
  white-space: nowrap;
  transition: all 0.3s ease;
  cursor: default;
}

.ticker-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 140, 0, 0.3);
}

.ticker-item.positive {
  border-left: 2px solid var(--accent-lime);
}

.ticker-item.negative {
  border-left: 2px solid var(--accent-red);
}

.ticker-flag {
  font-size: 14px;
}

.ticker-symbol {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

.ticker-price {
  font-size: 11px;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  color: var(--text-secondary);
}

.ticker-change {
  font-size: 10px;
  font-weight: 700;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  padding: 2px 6px;
  border-radius: 4px;
}

.ticker-change.positive {
  background: rgba(0, 255, 136, 0.15);
  color: var(--accent-lime);
}

.ticker-change.negative {
  background: rgba(255, 51, 102, 0.15);
  color: var(--accent-red);
}

.main-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Markets Panel */
.markets-panel {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  box-shadow:
    0 20px 40px -10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* ============================================
   HEADER BAR
   ============================================ */
.indices-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 24px;
  background: linear-gradient(90deg, var(--accent-orange), rgba(255, 160, 0, 0.9));
  border-radius: 12px;
  margin-bottom: 16px;
  gap: 16px;
  box-shadow: 
    0 4px 20px rgba(255, 140, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

/* ============================================
   INDICES CONTENT
   ============================================ */
.indices-content {
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 0;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.indices-content:has(.detail-view) {
  max-height: none;
  overflow-y: visible;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 500px;
  text-align: center;
  padding: 40px;
}

.empty-state-icon {
  color: rgba(255, 140, 0, 0.3);
  margin-bottom: 24px;
}

.empty-state-icon svg {
  stroke-width: 0.8;
}

.empty-state-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.empty-state-text {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 28px;
}

.empty-state-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, var(--accent-orange), rgba(255, 160, 0, 0.9));
  border: none;
  border-radius: 12px;
  padding: 14px 28px;
  color: #000;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(255, 140, 0, 0.3);
}

.empty-state-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(255, 140, 0, 0.4);
}

.empty-state-btn svg {
  stroke: #000;
}

/* ============================================
   INDICES DROPDOWN
   ============================================ */
.indices-dropdown-wrapper {
  position: relative;
}

.indices-dropdown-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  padding: 10px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.indices-dropdown-btn:hover {
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(0, 0, 0, 0.3);
}

.dropdown-icon-svg {
  color: #fff;
}

.dropdown-label {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.dropdown-arrow {
  color: #fff;
  transition: transform 0.3s ease;
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

/* Dropdown Catalog */
.indices-catalog {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  width: 420px;
  max-height: 500px;
  background: linear-gradient(135deg, rgba(25, 30, 45, 0.98), rgba(15, 18, 28, 0.98));
  border: 1px solid rgba(255, 140, 0, 0.4);
  border-radius: 16px;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.5),
    0 0 30px rgba(255, 140, 0, 0.2);
  z-index: 100;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.catalog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: rgba(255, 140, 0, 0.1);
  border-bottom: 1px solid rgba(255, 140, 0, 0.2);
}

.catalog-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--accent-orange);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.catalog-count {
  font-size: 11px;
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace;
}

.catalog-regions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.catalog-region-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 6px 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.catalog-region-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 140, 0, 0.3);
}

.catalog-region-btn.active {
  background: rgba(255, 140, 0, 0.2);
  border-color: var(--accent-orange);
}

.catalog-region-btn .region-name {
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 500;
}

.catalog-region-btn.active .region-name {
  color: var(--accent-orange);
}

.catalog-region-btn .region-count {
  font-size: 9px;
  color: var(--text-muted);
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 5px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
}

/* Country Tabs */
.catalog-countries {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 10px 16px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.catalog-country-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  padding: 4px 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.catalog-country-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.1);
}

.catalog-country-btn.active {
  background: rgba(0, 200, 255, 0.15);
  border-color: var(--accent-cyan);
}

.catalog-country-btn .country-name {
  font-size: 10px;
  color: var(--text-muted);
}

.catalog-country-btn.active .country-name {
  color: var(--accent-cyan);
}

.catalog-country-btn .country-count {
  font-size: 8px;
  color: var(--text-muted);
  background: rgba(0, 0, 0, 0.3);
  padding: 1px 4px;
  border-radius: 3px;
  font-family: 'JetBrains Mono', monospace;
}

.catalog-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  max-height: 350px;
}

.catalog-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 2px solid transparent;
}

.catalog-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.catalog-item.positive {
  border-left-color: var(--accent-lime);
}

.catalog-item.negative {
  border-left-color: var(--accent-red);
}

.catalog-item-country {
  font-size: 9px;
  font-weight: 600;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
  min-width: 24px;
  text-align: center;
}

.catalog-item-symbol {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  min-width: 70px;
}

.catalog-item-name {
  flex: 1;
  font-size: 11px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.catalog-item-change {
  font-size: 11px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  padding: 3px 8px;
  border-radius: 6px;
}

.catalog-item-change.positive {
  background: rgba(0, 255, 136, 0.15);
  color: var(--accent-lime);
}

.catalog-item-change.negative {
  background: rgba(255, 51, 102, 0.15);
  color: var(--accent-red);
}

/* Dropdown Transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* ============================================
   LARGE SEARCH BOX (on orange bar)
   ============================================ */
.search-box-large {
  display: flex;
  align-items: center;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 10px;
  padding: 10px 16px;
  gap: 10px;
  flex: 1;
  max-width: 350px;
  transition: all 0.3s ease;
}

.search-box-large:focus-within {
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(0, 0, 0, 0.25);
}

.search-box-large .search-icon {
  color: rgba(255, 255, 255, 0.7);
  flex-shrink: 0;
}

.search-input-large {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 14px;
  flex: 1;
  outline: none;
}

.search-input-large::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.search-clear-large {
  background: rgba(0, 0, 0, 0.2);
  border: none;
  color: rgba(255, 255, 255, 0.8);
  width: 22px;
  height: 22px;
  border-radius: 50%;
  font-size: 11px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.search-clear-large:hover {
  background: rgba(0, 0, 0, 0.4);
  color: #fff;
}

/* ============================================
   INDICES GRID
   ============================================ */
.indices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 14px;
}

.index-card {
  background: linear-gradient(135deg, rgba(30, 35, 50, 0.8), rgba(20, 25, 40, 0.6));
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 16px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.index-card:hover {
  transform: translateY(-4px);
  border-color: var(--accent-orange);
  box-shadow: 0 10px 40px rgba(255, 140, 0, 0.2);
}

.index-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.index-symbol-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.index-country-code {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.06);
  padding: 3px 6px;
  border-radius: 4px;
  letter-spacing: 0.5px;
}

.index-symbol {
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0.5px;
}

.index-change-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 8px;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
}

.index-change-badge.positive {
  background: rgba(0, 255, 136, 0.15);
  color: var(--accent-lime);
}

.index-change-badge.negative {
  background: rgba(255, 51, 102, 0.15);
  color: var(--accent-red);
}

.index-name {
  font-size: 10px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.index-price {
  font-size: 20px;
  font-weight: 700;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  margin-bottom: 12px;
}

.index-chart {
  height: 35px;
  margin-bottom: 12px;
}

.mini-chart {
  width: 100%;
  height: 100%;
}

.mini-chart path {
  transition: d 1s ease-out;
}

.index-meta {
  display: flex;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.meta-label {
  font-size: 8px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.meta-value {
  font-size: 10px;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  color: var(--text-secondary);
}

.meta-value.high { color: var(--accent-lime); }
.meta-value.low { color: var(--accent-red); }

/* ============================================
   RESPONSIVE
   ============================================ */

@media (max-width: 900px) {
  .market-sidebar {
    position: relative;
    left: 0;
    top: 0;
    width: 100%;
    height: auto;
    border-radius: 0;
  }
  
  .market-main {
    margin-left: 0;
    padding: 16px;
  }
  
  .sidebar-nav {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .indices-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }

  .ticker-wrapper {
    border-radius: 0;
    margin: 0 -16px 16px -16px;
  }

  .ticker-item {
    padding: 6px 10px;
  }

  .ticker-symbol {
    font-size: 10px;
  }

  .ticker-price {
    font-size: 10px;
  }

  .ticker-change {
    font-size: 9px;
  }

  .indices-header-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    padding: 12px 16px;
  }

  .indices-dropdown-wrapper {
    width: 100%;
  }

  .indices-dropdown-btn {
    width: 100%;
    justify-content: center;
  }

  .indices-catalog {
    width: 100%;
    left: 0;
    right: 0;
  }

  .search-box-large {
    max-width: 100%;
  }

  .indices-content {
    max-height: calc(100vh - 280px);
  }
}

/* Modal Responsive */
@media (max-width: 1400px) {
  .index-modal.index-modal-large {
    max-width: 98vw;
  }

  .modal-content-grid {
    grid-template-columns: 1fr 320px;
  }
}

@media (max-width: 1100px) {
  .modal-content-grid {
    grid-template-columns: 1fr;
  }

  .modal-left-column {
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  }

  .modal-stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .wave-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .index-modal.index-modal-large {
    max-height: 100vh;
    border-radius: 0;
  }

  .modal-stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .chart-controls {
    flex-direction: column;
    gap: 8px;
    align-items: flex-end;
  }
  
  .wave-surface-container {
    height: 350px;
  }
}

/* ============================================
   INDEX CARD CLICK HINT
   ============================================ */
.card-click-hint {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 9px;
  color: rgba(255, 255, 255, 0.3);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.index-card {
  cursor: pointer;
}

.index-card:hover .card-click-hint {
  opacity: 1;
}

/* ============================================
   DETAIL VIEW (Inline)
   ============================================ */
.detail-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: var(--glass-dark);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1.5px solid rgba(255, 140, 0, 0.3);
  border-radius: 14px;
  padding: 24px;
  box-shadow: var(--shadow-light);
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--accent-orange);
  margin-bottom: 8px;
}

.detail-back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: 1.5px solid rgba(255, 140, 0, 0.2);
  border-radius: 20px;
  padding: 10px 14px;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-light);
}

.detail-back-btn:hover {
  border-color: var(--accent-orange);
  background: rgba(255, 140, 0, 0.08);
  color: var(--accent-orange);
  box-shadow: var(--glow-orange);
}

.detail-brief {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.detail-country {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.05);
  padding: 4px 10px;
  border-radius: 6px;
}

.detail-symbol {
  font-size: 24px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: 1px;
}

.detail-name {
  font-size: 14px;
  color: var(--text-muted);
}

.detail-price {
  font-size: 24px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-primary);
}

.detail-change {
  font-size: 14px;
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
  padding: 6px 12px;
  border-radius: 8px;
}

.detail-change.positive {
  background: rgba(0, 255, 136, 0.15);
  color: var(--accent-lime);
}

.detail-change.negative {
  background: rgba(255, 51, 102, 0.15);
  color: var(--accent-red);
}

/* Charts Grid */
.detail-charts-grid {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 24px;
  margin-bottom: 4px;
  align-items: stretch;
}

.detail-volatility-section {
  display: flex;
  flex-direction: column;
  height: 100%;
  align-self: stretch;
}

.detail-right-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

/* Chart Cards */
.chart-card {
  background: var(--glass-dark);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1.5px solid rgba(255, 140, 0, 0.3);
  border-top: 3px solid var(--accent-orange);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: var(--shadow-light);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Убираем среднюю границу у chart-card внутри detail-view */
.detail-view .chart-card {
  border: none !important;
  border-top: none !important;
  background: transparent !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  box-shadow: none !important;
}

/* Убираем границы у wide карточки внутри detail-view */
.detail-view .chart-card.wide {
  border: none !important;
  border-top: none !important;
  background: transparent !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  box-shadow: none !important;
  border-radius: 0 !important;
}

/* Дополнительно убираем границы у wide карточки в detail-price-chart */
.detail-view .detail-price-chart .chart-card.wide {
  border: none !important;
  border-top: none !important;
  border-bottom: none !important;
  border-left: none !important;
  border-right: none !important;
  background: transparent !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  box-shadow: none !important;
  border-radius: 0 !important;
  outline: none !important;
}

.chart-card:hover {
  transform: translateY(-2px);
  border-color: var(--accent-orange);
  box-shadow: 0 0 20px rgba(255, 140, 0, 0.15), var(--shadow-light);
  background: var(--glass-light);
}

/* Убираем hover эффекты у chart-card внутри detail-view */
.detail-view .chart-card:hover {
  transform: none !important;
  border: none !important;
  border-top: none !important;
  box-shadow: none !important;
  background: transparent !important;
}

.chart-card.cyberpunk {
  background: var(--glass-dark);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1.5px solid rgba(255, 140, 0, 0.3);
  border-top: 3px solid var(--accent-orange);
  box-shadow: var(--shadow-light);
}

.chart-card.cyberpunk:hover {
  transform: translateY(-2px);
  border-color: var(--accent-orange);
  box-shadow: 0 0 20px rgba(255, 140, 0, 0.15), var(--shadow-light);
  background: var(--glass-light);
}

.detail-view .chart-card.cyberpunk {
  border: none;
  border-top: none;
  background: transparent;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  box-shadow: none;
}

.detail-view .chart-card.cyberpunk:hover {
  transform: none;
  border: none;
  box-shadow: none;
  background: transparent;
}

.chart-card.neon {
  background: var(--glass-dark);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1.5px solid rgba(255, 140, 0, 0.3);
  border-top: 3px solid var(--accent-orange);
  box-shadow: var(--shadow-light);
}

.chart-card.neon:hover {
  transform: translateY(-2px);
  border-color: var(--accent-orange);
  box-shadow: 0 0 20px rgba(255, 140, 0, 0.15), var(--shadow-light);
  background: var(--glass-light);
}

.detail-view .chart-card.neon {
  border: none;
  border-top: none;
  background: transparent;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  box-shadow: none;
}

.detail-view .chart-card.neon:hover {
  transform: none;
  border: none;
  box-shadow: none;
  background: transparent;
}

.chart-card.wide {
  grid-column: 1 / -1;
}

.chart-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(255, 140, 0, 0.08);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border-bottom: 1px solid rgba(255, 140, 0, 0.2);
}

.detail-view .chart-card-header {
  background: transparent;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  border-bottom: none;
  padding: 16px 0;
}

.chart-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.chart-subtitle {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  margin-left: 12px;
  font-weight: 400;
  font-style: italic;
}

.chart-badge {
  font-size: 10px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 5px 12px;
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.chart-badge.neon {
  color: rgba(167, 139, 250, 1);
  background: rgba(139, 92, 246, 0.15);
  border-color: rgba(139, 92, 246, 0.4);
  box-shadow: 0 2px 10px rgba(139, 92, 246, 0.2);
}

.chart-container-large {
  flex: 1;
  min-height: 500px;
  padding: 16px;
  width: 100%;
  background: rgba(0, 0, 0, 0.2);
  position: relative;
}

.chart-container-medium {
  height: 280px;
  padding: 14px;
  width: 100%;
  background: rgba(0, 0, 0, 0.2);
  position: relative;
}

.chart-legend {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
  padding: 14px 20px;
  background: rgba(255, 140, 0, 0.05);
  border-top: 1px solid rgba(255, 140, 0, 0.2);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
}

.chart-legend.cyberpunk {
  border-top-color: rgba(255, 140, 0, 0.2);
  background: rgba(255, 140, 0, 0.05);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  padding: 4px 10px;
  background: rgba(255, 140, 0, 0.08);
  border-radius: 6px;
  border: 1px solid rgba(255, 140, 0, 0.2);
}

.legend-item .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  box-shadow: 0 0 8px currentColor, 0 0 4px currentColor;
  flex-shrink: 0;
}

/* Price Chart */
.detail-price-chart {
  margin-top: 20px;
  background: transparent;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  border: none;
  border-top: none;
  border-radius: 0;
  overflow: visible;
  box-shadow: none;
}

.timeframe-tabs {
  display: flex;
  gap: 8px;
  align-items: center;
}

.timeframe-btn {
  background: transparent;
  border: 1.5px solid rgba(255, 140, 0, 0.2);
  color: var(--text-secondary);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: 'JetBrains Mono', monospace;
  box-shadow: var(--shadow-light);
}

.timeframe-btn:hover {
  border-color: var(--accent-orange);
  background: rgba(255, 140, 0, 0.08);
  color: var(--accent-orange);
  box-shadow: var(--glow-orange);
  transform: translateY(-2px);
}

.timeframe-btn.active {
  background: linear-gradient(135deg, var(--accent-orange), rgba(255, 160, 0, 0.9));
  border-color: var(--accent-orange);
  color: #000;
  font-weight: 700;
  box-shadow: 0 2px 12px rgba(255, 140, 0, 0.3);
}

.price-chart-container {
  padding: 20px;
  height: 220px;
  background: var(--glass-dark);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border-radius: 0 0 14px 14px;
  border-top: 1px solid rgba(255, 140, 0, 0.2);
}

.detail-price-svg {
  width: 100%;
  height: 100%;
}

/* Info Section */
.detail-info-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 10px;
}

.info-card {
  background: var(--glass-dark);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border: 1.5px solid rgba(255, 140, 0, 0.3);
  border-top: 3px solid var(--accent-orange);
  border-radius: 14px;
  padding: 16px;
  box-shadow: var(--shadow-light);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.info-card:hover {
  transform: translateY(-2px);
  border-color: var(--accent-orange);
  box-shadow: 0 0 20px rgba(255, 140, 0, 0.15), var(--shadow-light);
  background: var(--glass-light);
}

/* Убираем среднюю границу у info-card внутри detail-view */
.detail-view .info-card {
  border: none;
  border-top: none;
  background: transparent;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  box-shadow: none;
}

.detail-view .info-card:hover {
  transform: none;
  border: none;
  box-shadow: none;
  background: transparent;
}

.info-card-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-orange);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--accent-orange);
  text-shadow: 0 0 8px rgba(255, 140, 0, 0.3);
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 12px;
  color: var(--text-muted);
}

.info-value {
  font-size: 13px;
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-primary);
}

.info-value.positive { color: var(--accent-lime); }
.info-value.negative { color: var(--accent-red); }

/* Responsive Detail View */
@media (max-width: 1200px) {
  .detail-charts-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .detail-volatility-section {
    min-height: 450px;
  }
  
  .detail-right-column {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
  
  .chart-container-large {
    height: 450px;
  }
  
  .chart-container-medium {
    height: 260px;
  }
}

@media (max-width: 900px) {
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .detail-brief {
    gap: 10px;
  }
  
  .detail-symbol {
    font-size: 20px;
  }
  
  .detail-price {
    font-size: 20px;
  }
  
  .detail-charts-grid {
    gap: 16px;
  }
  
  .detail-right-column {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .detail-info-section {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .chart-container-large {
    height: 380px;
    padding: 12px;
  }
  
  .chart-container-medium {
    height: 240px;
    padding: 12px;
  }
  
  .chart-card-header {
    padding: 12px 16px;
  }
  
  .chart-title {
    font-size: 12px;
  }
}

/* ============================================
   INDEX DETAIL MODAL
   ============================================ */
.index-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(5, 8, 15, 0.95);
  backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.index-modal {
  background: var(--primary-bg);
  border: 1px solid rgba(255, 140, 0, 0.3);
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow:
    0 0 60px rgba(255, 140, 0, 0.15),
    0 0 120px rgba(255, 140, 0, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

/* Large Modal Variant */
.index-modal.index-modal-large {
  max-width: 1600px;
  max-height: 95vh;
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(180deg, rgba(255, 140, 0, 0.08), transparent);
  border-bottom: 1px solid rgba(255, 140, 0, 0.3);
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(10px);
}

.modal-title-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.modal-country-badge {
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-orange);
  background: rgba(255, 140, 0, 0.15);
  border: 1px solid rgba(255, 140, 0, 0.3);
  padding: 8px 14px;
  border-radius: 10px;
  letter-spacing: 1px;
}

.modal-title-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.modal-symbol {
  font-size: 24px;
  font-weight: 800;
  margin: 0;
  letter-spacing: 1px;
}

.modal-name {
  font-size: 12px;
  color: var(--text-secondary);
}

.modal-close {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: var(--text-secondary);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(255, 100, 100, 0.2);
  color: var(--accent-red);
}

/* Price Section */
.modal-price-section {
  padding: 16px 24px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(0, 0, 0, 0.15);
}

.modal-price {
  font-size: 36px;
  font-weight: 800;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  margin-bottom: 6px;
  background: linear-gradient(135deg, #fff, rgba(255, 255, 255, 0.8));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.modal-change {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
}

.modal-change.positive { color: var(--accent-lime); }
.modal-change.negative { color: var(--accent-red); }

.change-arrow {
  font-size: 14px;
}

.change-points {
  font-size: 14px;
  opacity: 0.7;
}

/* Modal Content Grid */
.modal-content-grid {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 0;
}

.modal-left-column {
  border-right: 1px solid rgba(255, 255, 255, 0.06);
}

.modal-right-column {
  background: rgba(0, 0, 0, 0.2);
}

/* Chart Section */
.modal-chart-section {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-type-toggle {
  display: flex;
  gap: 4px;
  background: rgba(0, 0, 0, 0.3);
  padding: 4px;
  border-radius: 8px;
}

.chart-type-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-type-btn:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.1);
}

.chart-type-btn.active {
  background: var(--accent-orange);
  color: #000;
}

.chart-type-btn svg {
  width: 16px;
  height: 16px;
}

.chart-timeframes {
  display: flex;
  gap: 4px;
}

.tf-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tf-btn:hover {
  border-color: var(--accent-orange);
  color: var(--text-primary);
}

.tf-btn.active {
  background: var(--accent-orange);
  border-color: var(--accent-orange);
  color: #000;
  font-weight: 600;
}

.modal-chart {
  height: 300px;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.15));
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.modal-chart.candlestick-chart {
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0.15));
}

.detail-chart {
  width: 100%;
  height: 100%;
}

.detail-chart path {
  transition: d 1s ease-out;
}

/* WAVE Surface Section */
.modal-wave-section {
  padding: 20px 24px;
}

.wave-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.wave-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-cyan);
  margin: 0;
}

.wave-badge {
  font-size: 9px;
  color: var(--accent-orange);
  background: rgba(255, 140, 0, 0.1);
  padding: 4px 8px;
  border-radius: 10px;
  border: 1px solid rgba(255, 140, 0, 0.2);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.wave-description {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  line-height: 1.5;
}

.wave-legend {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.legend-item {
  font-size: 10px;
  opacity: 0.8;
}

.wave-surface-container {
  height: 500px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
}

.wave-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.wave-metric {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  padding: 12px;
  text-align: center;
}

.wave-metric .metric-label {
  font-size: 9px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: block;
  margin-bottom: 4px;
}

.wave-metric .metric-value {
  font-size: 12px;
  font-weight: 700;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
}

.wave-metric .metric-value.regime-choppy { color: #ef4444; }
.wave-metric .metric-value.regime-up { color: var(--accent-lime); }
.wave-metric .metric-value.regime-down { color: var(--accent-red); }
.wave-metric .metric-value.regime-stable { color: var(--accent-cyan); }

/* Technical Indicators Section */
.modal-technicals-section {
  padding: 12px 16px;
}

.info-section-title {
  font-size: 10px;
  font-weight: 700;
  color: var(--accent-orange);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin: 0 0 10px 0;
}

.technical-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.technical-row:last-child {
  border-bottom: none;
}

.tech-label {
  font-size: 10px;
  color: var(--text-secondary);
}

.tech-value {
  font-size: 11px;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-weight: 600;
}

.tech-value.overbought { color: #ef4444; }
.tech-value.oversold { color: #22c55e; }
.tech-value.neutral { color: var(--text-primary); }
.tech-value.bullish { color: var(--accent-lime); }
.tech-value.bearish { color: var(--accent-red); }

/* Stats Grid */
.modal-stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  padding: 16px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 10px;
  padding: 12px;
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 140, 0, 0.05);
  border-color: rgba(255, 140, 0, 0.15);
}

.stat-card .stat-label {
  font-size: 9px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: block;
  margin-bottom: 4px;
}

.stat-card .stat-value {
  font-size: 13px;
  font-weight: 700;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
}

.stat-card .stat-value.high { color: var(--accent-lime); }
.stat-card .stat-value.low { color: var(--accent-red); }

/* ============================================
   CONSTITUENTS TABLE
   ============================================ */
.modal-constituents-section {
  padding: 20px 24px;
}

.constituents-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.constituents-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--accent-orange);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0;
}

.constituents-count {
  font-size: 10px;
  color: var(--text-muted);
  background: rgba(255, 140, 0, 0.1);
  padding: 4px 10px;
  border-radius: 12px;
  border: 1px solid rgba(255, 140, 0, 0.2);
}

.constituents-table-wrapper {
  overflow-x: auto;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(0, 0, 0, 0.2);
}

.constituents-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
  min-width: 750px;
}

.constituents-table thead {
  background: rgba(255, 140, 0, 0.08);
}

.constituents-table th {
  padding: 12px 10px;
  text-align: left;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--accent-orange);
  border-bottom: 1px solid rgba(255, 140, 0, 0.2);
  white-space: nowrap;
}

.constituents-table th.th-ticker { width: 70px; }
.constituents-table th.th-name { width: 140px; }
.constituents-table th.th-price { text-align: right; }
.constituents-table th.th-change { text-align: right; width: 70px; }
.constituents-table th.th-shares { text-align: right; }
.constituents-table th.th-cap { text-align: right; }
.constituents-table th.th-index-cap { text-align: right; }
.constituents-table th.th-weight { width: 100px; }

.constituents-table tbody tr {
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  transition: background 0.2s ease;
}

.constituents-table tbody tr:hover {
  background: rgba(255, 140, 0, 0.05);
}

.constituents-table tbody tr:last-child {
  border-bottom: none;
}

.constituents-table td {
  padding: 10px 10px;
  vertical-align: middle;
}

.td-ticker {
  font-weight: 700;
}

.ticker-badge {
  display: inline-block;
  background: linear-gradient(135deg, rgba(255, 140, 0, 0.15), rgba(255, 100, 0, 0.1));
  color: var(--accent-orange);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
}

.td-name {
  color: var(--text-secondary);
  font-size: 10px;
}

.td-price {
  text-align: right;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-weight: 600;
}

.td-change {
  text-align: right;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-weight: 600;
}

.td-change.positive { color: var(--accent-lime); }
.td-change.negative { color: var(--accent-red); }

.td-shares {
  text-align: right;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  color: var(--text-secondary);
  font-size: 10px;
}

.td-cap,
.td-index-cap {
  text-align: right;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 10px;
}

.td-weight {
  padding-right: 12px;
}

.weight-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.weight-value {
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-weight: 700;
  font-size: 11px;
  color: var(--accent-cyan);
}

.weight-bar {
  height: 3px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.weight-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-cyan), var(--accent-orange));
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* Info Section */
.modal-info-section {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 10px;
  color: var(--text-secondary);
}

.info-value {
  font-size: 11px;
  font-weight: 600;
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
}

.info-value.positive { color: var(--accent-lime); }
.info-value.negative { color: var(--accent-red); }

/* Modal Actions */
.modal-actions {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  background: rgba(0, 0, 0, 0.3);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  position: sticky;
  bottom: 0;
}

.action-btn {
  flex: 1;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  text-decoration: none;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
}

.action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.action-btn.primary {
  background: linear-gradient(135deg, var(--accent-orange), var(--accent-orange-dark));
  border: none;
  color: #000;
}

.action-btn.primary:hover {
  box-shadow: 0 0 20px rgba(255, 140, 0, 0.5);
  transform: translateY(-2px);
}

/* Modal Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .index-modal,
.modal-leave-to .index-modal {
  transform: scale(0.9) translateY(20px);
}

.modal-enter-to .index-modal,
.modal-leave-from .index-modal {
  transform: scale(1) translateY(0);
}
</style>
