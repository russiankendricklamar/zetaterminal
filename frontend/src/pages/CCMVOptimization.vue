<!-- src/views/CCMVOptimizationPage.vue -->
<template>
  <div class="ccmv-page">
    <!-- Method Selector Tabs -->
    <div class="method-selector">
      <button
        :class="['method-tab', { active: activeMethod === 'hjb' }]"
        @click="activeMethod = 'hjb'"
      >
        <div class="method-icon hjb">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
        <div class="method-info">
          <span class="method-title">HJB-стратегия</span>
          <span class="method-subtitle">Стохастическое оптимизирование</span>
        </div>
      </button>
      <button
        :class="['method-tab', { active: activeMethod === 'ccmv' }]"
        @click="activeMethod = 'ccmv'"
      >
        <div class="method-icon ccmv">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
          </svg>
        </div>
        <div class="method-info">
          <span class="method-title">CCMV модель</span>
          <span class="method-subtitle">Кластерная оптимизация</span>
        </div>
      </button>
    </div>

    <!-- HJB Strategy Section -->
    <template v-if="activeMethod === 'hjb'">
      <!-- Hero Section HJB -->
      <div class="hero-section">
        <div class="hero-left">
          <h1>Стохастическое оптимизирование (HJB)</h1>
          <div class="hero-meta">
            <span class="glass-pill">Стратегия: <strong>Hamilton-Jacobi-Bellman</strong></span>
            <span class="glass-pill">Горизонт: <strong>{{ hjbParams.horizon }} мес.</strong></span>
            <span class="glass-pill">Банк: <strong>{{ selectedBank.name }}</strong></span>
            <span class="glass-pill">Активов: <strong>{{ portfolioPositions.length }}</strong></span>
          </div>
        </div>
        <div class="hero-actions">
          <button class="btn-glass primary" @click="runHJBOptimization" :disabled="isComputing">
            <svg v-if="!isComputing" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            <span v-else class="spinner"></span>
            {{ isComputing ? 'Расчёт...' : 'Запустить оптимизацию' }}
          </button>
        </div>
      </div>

      <!-- HJB Parameters Row (Top) -->
      <div class="glass-panel hjb-params-row">
        <div class="panel-header">
          <h3>Параметры HJB модели</h3>
        </div>
        <div class="panel-body params-row-body">
          <div class="param-group-horizontal">
            <label>Коэффициент неприятия риска (γ)</label>
            <div class="param-input-group">
              <input
                type="number"
                v-model.number="hjbParams.gamma"
                min="0.1"
                max="20"
                step="0.1"
              />
            </div>
          </div>

          <div class="param-group-horizontal">
            <label>Инвестиционный горизонт (T), лет</label>
            <div class="param-input-group">
              <input
                type="number"
                v-model.number="hjbParams.horizon"
                min="0.1"
                max="50"
                step="0.1"
              />
            </div>
          </div>

          <div class="param-group-horizontal">
            <label>Безрисковая ставка (r)</label>
            <div class="param-input-group">
              <input
                type="number"
                v-model.number="hjbParams.riskFreeRate"
                min="0"
                max="0.2"
                step="0.001"
              />
            </div>
          </div>

          <div class="param-group-horizontal">
            <label>Волатильность рынка (σ)</label>
            <div class="param-input-group">
              <input
                type="number"
                v-model.number="hjbParams.marketVol"
                min="0.05"
                max="0.8"
                step="0.01"
              />
            </div>
          </div>

          <div class="param-group-horizontal">
            <label>Ожидаемая доходность (μ)</label>
            <div class="param-input-group">
              <input
                type="number"
                v-model.number="hjbParams.expectedReturn"
                min="0"
                max="0.5"
                step="0.01"
              />
            </div>
          </div>

          <div class="param-group-horizontal">
            <label>Количество траекторий Монте-Карло</label>
            <div class="param-input-group">
              <input
                type="number"
                v-model.number="hjbParams.monteCarloTrajectories"
                min="100"
                max="100000"
                step="100"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- HJB Main Grid -->
      <div class="dashboard-grid hjb-grid">
        <!-- LEFT: Portfolio Composition (spans 2 columns) -->
        <div class="col-portfolio-wide">
          <!-- Portfolio Composition -->
          <div class="glass-panel portfolio-composition-panel">
            <div class="panel-header">
              <h3>Состав портфеля</h3>
            </div>
            <div class="panel-body weights-body">
              <div class="weights-comparison">
                <div class="weights-table-container">
                  <table class="weights-table">
                    <thead>
                      <tr>
                        <th>Инструмент</th>
                        <th class="text-right">Цена</th>
                        <th class="text-right">День %</th>
                        <th class="text-right">Позиция</th>
                        <th class="text-right">Вес</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="pos in portfolioPositions" :key="pos.symbol">
                        <td>
                          <div class="asset-cell">
                            <div class="asset-icon" :style="{ background: pos.color }">{{ pos.symbol[0] }}</div>
                            <div class="asset-info">
                              <span class="symbol">{{ pos.symbol }}</span>
                              <span class="name">{{ pos.name }}</span>
                            </div>
                          </div>
                        </td>
                        <td class="text-right mono">₽{{ pos.price }}</td>
                        <td class="text-right mono">
                          <span :class="['change-pill', pos.dayChange > 0 ? 'text-green' : 'text-red']">
                            {{ pos.dayChange > 0 ? '+' : '' }}{{ pos.dayChange }}%
                          </span>
                        </td>
                        <td class="text-right mono opacity-80">₽{{ (pos.notional / 1000).toFixed(1) }}k</td>
                        <td class="text-right mono font-bold">{{ pos.allocation }}%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT: 3D Heatmap (1 column) -->
        <div class="col-3d-right">
          <!-- 3D Correlation Heatmap -->
          <div class="glass-panel correlation-3d-panel">
            <div class="panel-header">
              <h3>3D Тепловая карта активов</h3>
            </div>
            <div class="panel-body correlation-3d-body">
              <div id="correlation-3d-heatmap" class="static-3d-plot" style="width:100%; height:500px; position: relative; min-height: 500px; background: transparent; border-radius: 8px;"></div>
              <div v-if="hoveredAsset" class="asset-tooltip-3d">
                <div class="tooltip-header">
                  <div class="asset-icon" :style="{ background: hoveredAsset.color }">{{ hoveredAsset.symbol[0] }}</div>
                  <div>
                    <div class="tooltip-symbol">{{ hoveredAsset.symbol }}</div>
                    <div class="tooltip-name">{{ hoveredAsset.name }}</div>
                  </div>
                </div>
                <div class="tooltip-details">
                  <div class="tooltip-row">
                    <span>Тип:</span>
                    <strong>{{ (hoveredAsset.symbol.includes('SU') || hoveredAsset.symbol.includes('RU000')) ? 'Облигация' : 'Акция' }}</strong>
                  </div>
                  <div class="tooltip-row" v-if="hoveredAsset.volatility !== undefined">
                    <span>Волатильность:</span>
                    <strong>{{ hoveredAsset.volatility?.toFixed(1) || 'N/A' }}%</strong>
                  </div>
                  <div class="tooltip-row" v-if="hoveredAsset.avgCorrelation !== undefined">
                    <span>Ср. корреляция:</span>
                    <strong>{{ hoveredAsset.avgCorrelation?.toFixed(2) || 'N/A' }}</strong>
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
                  <div class="tooltip-row" v-if="hoveredAsset.notional">
                    <span>Позиция:</span>
                    <strong>₽{{ (hoveredAsset.notional / 1000).toFixed(1) }}k</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- GARCH Volatility Modeling - Full Width -->
      <div class="garch-full-width">
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Моделирование волатильности (GARCH)</h3>
          </div>
          <div class="panel-body">
            <div class="garch-container-full">
              <div class="garch-chart-placeholder-full">
                <canvas ref="garchChart" id="garch-chart"></canvas>
              </div>
              <div class="garch-params-full">
                <div class="garch-param-row">
                  <span class="param-name">GARCH(1,1):</span>
                  <span class="param-value">σ²<sub>t</sub> = ω + αε²<sub>t-1</sub> + βσ²<sub>t-1</sub></span>
                </div>
                <div class="garch-stats">
                  <div class="garch-stat">
                    <span class="stat-label">α (ARCH)</span>
                    <span class="stat-val">{{ garchData?.result?.parameters?.alpha?.toFixed(3) || '0.082' }}</span>
                  </div>
                  <div class="garch-stat">
                    <span class="stat-label">β (GARCH)</span>
                    <span class="stat-val">{{ garchData?.result?.parameters?.beta?.toFixed(3) || '0.893' }}</span>
                  </div>
                  <div class="garch-stat">
                    <span class="stat-label">ω</span>
                    <span class="stat-val">{{ garchData?.result?.parameters?.omega?.toFixed(6) || '0.000025' }}</span>
                  </div>
                  <div class="garch-stat">
                    <span class="stat-label">Long-term Vol</span>
                    <span class="stat-val">{{ garchData?.result?.long_term_volatility ? (garchData.result.long_term_volatility * 100).toFixed(1) + '%' : '18.2%' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Reports Row: GARCH Filtering and Yield Report in 2 columns -->
      <div class="dashboard-grid hjb-reports-grid">
        <!-- LEFT: GARCH Filtering Report -->
        <div class="col-report-left">
          <div class="glass-panel report-panel">
            <div class="panel-header">
              <h3>Фильтрация активов по GARCH</h3>
            </div>
            <div class="panel-body">
              <div class="filtering-report">
                <div class="report-summary">
                  <div class="summary-item">
                    <span class="summary-label">Всего активов</span>
                    <span class="summary-value">{{ portfolioPositions.length }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="summary-label">Прошли фильтр</span>
                    <span class="summary-value text-green">{{ garchFilteredCount }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="summary-label">Отклонены</span>
                    <span class="summary-value text-red">{{ portfolioPositions.length - garchFilteredCount }}</span>
                  </div>
                </div>
                <div class="filtering-criteria">
                  <div class="criteria-title">Критерии фильтрации:</div>
                  <div class="criteria-list">
                    <div class="criteria-item">
                      <span class="criteria-check">✓</span>
                      <span>GARCH волатильность ≤ 30%</span>
                    </div>
                    <div class="criteria-item">
                      <span class="criteria-check">✓</span>
                      <span>Стабильность параметров (α + β < 1)</span>
                    </div>
                    <div class="criteria-item">
                      <span class="criteria-check">✓</span>
                      <span>Достаточная ликвидность</span>
                    </div>
                  </div>
                </div>
                <div class="filtered-assets">
                  <div class="filtered-title">Прошедшие фильтр (топ-10):</div>
                  <div class="filtered-list">
                    <div v-for="(asset, idx) in garchFilteredAssets.slice(0, 10)" :key="idx" class="filtered-asset">
                      <span class="asset-symbol">{{ asset.symbol }}</span>
                      <span class="asset-garch">{{ asset.garchVol }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT: Historical & Dividend Yield Report -->
        <div class="col-report-right">
          <div class="glass-panel report-panel">
            <div class="panel-header">
              <h3>Историческая и дивидендная доходность</h3>
            </div>
            <div class="panel-body weights-body">
              <div class="weights-comparison">
                <div class="weights-table-container">
                  <table class="weights-table">
                    <thead>
                      <tr>
                        <th>Актив</th>
                        <th class="text-right">Историческая</th>
                        <th class="text-right">Дивидендная</th>
                        <th class="text-right">Итого</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(asset, idx) in yieldReportData.slice(0, 10)" :key="idx">
                        <td>
                          <div class="asset-cell">
                            <div class="asset-icon" :style="{ background: asset.color }">{{ asset.symbol[0] }}</div>
                            <div class="asset-info">
                              <span class="symbol">{{ asset.symbol }}</span>
                              <span class="name">{{ asset.name }}</span>
                            </div>
                          </div>
                        </td>
                        <td class="text-right mono">{{ (asset.historicalYield * 100).toFixed(2) }}%</td>
                        <td class="text-right mono">{{ (asset.dividendYield * 100).toFixed(2) }}%</td>
                        <td class="text-right mono font-bold text-green">{{ (asset.totalYield * 100).toFixed(2) }}%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="yield-summary">
                <div class="yield-summary-item">
                  <span class="summary-label">Средняя историческая доходность</span>
                  <span class="summary-value">{{ (avgHistoricalYield * 100).toFixed(2) }}%</span>
                </div>
                <div class="yield-summary-item">
                  <span class="summary-label">Средняя дивидендная доходность</span>
                  <span class="summary-value">{{ (avgDividendYield * 100).toFixed(2) }}%</span>
                </div>
                <div class="yield-summary-item">
                  <span class="summary-label">Средняя общая доходность</span>
                  <span class="summary-value text-green font-bold">{{ (avgTotalYield * 100).toFixed(2) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Monte Carlo Trajectories Visualization -->
      <div class="glass-panel trajectories-panel">
        <div class="panel-header">
          <div class="trajectories-header-left">
            <h3>Траектории симуляции методом Монте-Карло</h3>
            <span v-if="isPlayingTrajectories" class="live-badge">● LIVE</span>
          </div>
          
          <!-- Playback Controls -->
          <div class="playback-controls" v-if="trajectoriesData.paths.length">
            <button class="icon-btn" @click="togglePlayTrajectories" title="Play/Pause">
              <span v-if="isPlayingTrajectories">⏸</span>
              <span v-else>▶</span>
            </button>
            
            <div class="timeline-wrapper">
              <input 
                type="range" 
                min="0" 
                :max="trajectoriesDays" 
                v-model.number="playbackStepTrajectories"
                @input="stopPlayTrajectories"
                class="timeline-slider"
              />
              <div class="timeline-track" :style="{ width: (playbackStepTrajectories / trajectoriesDays * 100) + '%' }"></div>
            </div>

            <div class="playback-day-info">
              День: <span class="mono">{{ playbackStepTrajectories }}</span> / <span class="mono">{{ trajectoriesDays }}</span>
            </div>

            <button class="icon-btn" @click="resetPlaybackTrajectories" title="Reset">↺</button>
          </div>
        </div>
        
        <div class="panel-body">
          <div class="trajectories-chart-container" ref="trajectoriesChartContainer">
            <svg v-if="trajectoriesData.paths.length > 0" viewBox="0 0 1000 400" preserveAspectRatio="none" class="trajectories-svg">
              <!-- Grid Lines -->
              <line x1="0" y1="350" x2="1000" y2="350" stroke="rgba(255,255,255,0.05)" />
              <line x1="0" y1="200" x2="1000" y2="200" stroke="rgba(255,255,255,0.05)" />
              <line x1="0" y1="50" x2="1000" y2="50" stroke="rgba(255,255,255,0.05)" />

              <!-- Start Price Line -->
              <line 
                x1="0" 
                :y1="scaleYTrajectories(initialPrice)" 
                x2="1000" 
                :y2="scaleYTrajectories(initialPrice)" 
                stroke="rgba(255,255,255,0.2)" 
                stroke-dasharray="4" 
              />

              <!-- Paths -->
              <path 
                v-for="(path, i) in trajectoriesData.displayPaths" 
                :key="`trajectory-path-${i}`"
                :d="generatePathDTrajectories(path, playbackStepTrajectories)"
                fill="none" 
                stroke="rgba(59, 130, 246, 0.2)" 
                stroke-width="1" 
              />

              <!-- Confidence Area -->
              <path 
                :d="generateAreaDTrajectories(trajectoriesData.q05, trajectoriesData.q95, playbackStepTrajectories)"
                fill="rgba(59, 130, 246, 0.1)" 
                stroke="none" 
              />

              <!-- Median Path -->
              <path 
                :d="generatePathDTrajectories(trajectoriesData.medianPath, playbackStepTrajectories)"
                fill="none" 
                stroke="#3b82f6" 
                stroke-width="2.5" 
              />
                
              <!-- Quantile Lines -->
              <path 
                :d="generatePathDTrajectories(trajectoriesData.q05, playbackStepTrajectories)" 
                fill="none" 
                stroke="#f87171" 
                stroke-width="1.5" 
                stroke-dasharray="4"
              />
              <path 
                :d="generatePathDTrajectories(trajectoriesData.q95, playbackStepTrajectories)" 
                fill="none" 
                stroke="#34d399" 
                stroke-width="1.5" 
                stroke-dasharray="4"
              />
              
              <!-- Current Time Marker -->
              <line 
                v-if="playbackStepTrajectories > 0"
                :x1="scaleXTrajectories(playbackStepTrajectories)" 
                y1="0" 
                :x2="scaleXTrajectories(playbackStepTrajectories)" 
                y2="400" 
                stroke="rgba(255,255,255,0.4)" 
                stroke-dasharray="2" 
              />
            </svg>

            <div v-else class="trajectories-empty-state">
              <span>Генерация траекторий на основе параметров HJB модели</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 3D Trajectories Visualization -->
      <div class="glass-panel trajectories-3d-panel">
        <div class="panel-header">
          <div class="trajectories-3d-header-left">
            <h3>3D визуализация траекторий</h3>
            <span v-if="isPlaying3D" class="live-badge">● LIVE</span>
          </div>
          
          <!-- Playback Controls -->
          <div class="playback-controls" v-if="simulationResult3D && simulationResult3D.paths.length">
            <button class="icon-btn" @click="togglePlay3D" title="Play/Pause">
              <span v-if="isPlaying3D">⏸</span>
              <span v-else>▶</span>
            </button>
            
            <div class="timeline-wrapper">
              <input 
                type="range" 
                min="0" 
                :max="maxStep3D" 
                v-model.number="playbackStep3D"
                @input="stopPlay3D"
                class="timeline-slider"
              />
              <div class="timeline-track" :style="{ width: (maxStep3D > 0 ? (playbackStep3D / maxStep3D * 100) : 0) + '%' }"></div>
            </div>

            <div class="playback-day-info">
              Шаг: <span class="mono">{{ playbackStep3D }}</span> / <span class="mono">{{ maxStep3D }}</span>
            </div>

            <button class="icon-btn" @click="resetPlayback3D" title="Reset">↺</button>
          </div>
        </div>
        <div class="panel-body">
          <div class="trajectories-3d-container">
            <canvas ref="trajectories3DCanvas" class="trajectories-3d-canvas"></canvas>
          </div>
        </div>
      </div>

      <!-- Simulation Metrics Summary -->
      <div class="glass-panel metrics-summary-panel" v-if="simulationResult3D && simulationResult3D.paths.length">
        <div class="panel-header">
          <h3>Итоги симуляций</h3>
        </div>
        <div class="panel-body">
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-label">Средняя доходность портфеля</div>
              <div class="metric-value" :class="averageReturn >= 0 ? 'text-green' : 'text-red'">
                {{ formatPercent(averageReturn) }}
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-label">Медианная доходность портфеля</div>
              <div class="metric-value" :class="medianReturn >= 0 ? 'text-green' : 'text-red'">
                {{ formatPercent(medianReturn) }}
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-label">Sharpe Ratio</div>
              <div class="metric-value" :class="sharpeRatio >= 0 ? 'text-green' : 'text-red'">
                {{ sharpeRatio.toFixed(2) }}
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-label">VaR (95%)</div>
              <div class="metric-value text-red">
                {{ formatPercent(var95) }}
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-label">CVaR (95%)</div>
              <div class="metric-value text-red">
                {{ formatPercent(cvar95) }}
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-label">Средний MDD</div>
              <div class="metric-value text-red">
                {{ formatPercent(averageMDD) }}
              </div>
            </div>
          </div>
        </div>
      </div>

    </template>

    <!-- CCMV Section (original content) -->
    <template v-else>
      <!-- Hero Section CCMV -->
    <div class="hero-section">
      <div class="hero-left">
        <h1>CCMV Optimization</h1>
        <div class="hero-meta">
          <span class="glass-pill">Метод: <strong>{{ params.method === 'delta' ? 'Δ-CCMV' : 'α-CCMV' }}</strong></span>
          <span class="glass-pill">Кластеров: <strong>{{ clusteringResult.numClusters }}</strong></span>
          <span class="glass-pill">Банк: <strong>{{ selectedBank.name }}</strong></span>
          <span class="glass-pill">Активов: <strong>{{ portfolioPositions.length }}</strong></span>
        </div>
      </div>
      <div class="hero-actions">
        <button class="btn-glass primary" @click="recomputeOptimization" :disabled="isComputing">
          <svg v-if="!isComputing" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          <span v-else class="spinner"></span>
          {{ isComputing ? 'Расчёт...' : 'Пересчитать' }}
        </button>
      </div>
    </div>

    <!-- Portfolio Composition -->
    <div class="dashboard-grid hjb-grid">
      <div class="col-portfolio-wide">
        <div class="glass-panel portfolio-composition-panel">
          <div class="panel-header">
            <h3>Состав портфеля</h3>
          </div>
          <div class="panel-body weights-body">
            <div class="weights-comparison">
              <div class="weights-table-container">
                <table class="weights-table">
                  <thead>
                    <tr>
                      <th>Инструмент</th>
                      <th class="text-right">Цена</th>
                      <th class="text-right">День %</th>
                      <th class="text-right">Позиция</th>
                      <th class="text-right">Вес</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="pos in portfolioPositions" :key="pos.symbol">
                      <td>
                        <div class="asset-cell">
                          <div class="asset-icon" :style="{ background: pos.color }">{{ pos.symbol[0] }}</div>
                          <div class="asset-info">
                            <span class="symbol">{{ pos.symbol }}</span>
                            <span class="name">{{ pos.name }}</span>
                          </div>
                        </div>
                      </td>
                      <td class="text-right mono">₽{{ pos.price }}</td>
                      <td class="text-right mono">
                        <span :class="['change-pill', pos.dayChange > 0 ? 'text-green' : 'text-red']">
                          {{ pos.dayChange > 0 ? '+' : '' }}{{ pos.dayChange }}%
                        </span>
                      </td>
                      <td class="text-right mono opacity-80">₽{{ (pos.notional / 1000).toFixed(1) }}k</td>
                      <td class="text-right mono font-bold">{{ pos.allocation }}%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT: Optimization Parameters -->
      <div class="col-3d-right">
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Параметры оптимизации</h3>
            <div class="header-tabs">
              <div class="tab-slider" :style="paramsTabSliderStyle"></div>
              <button
                ref="el => paramsTabButtons.basic = el"
                :class="['tab-btn', { active: paramsTab === 'basic' }]"
                @click="paramsTab = 'basic'"
              >
                Основные
              </button>
              <button
                ref="el => paramsTabButtons.methodology = el"
                :class="['tab-btn', { active: paramsTab === 'methodology' }]"
                @click="paramsTab = 'methodology'"
              >
                Методология
              </button>
            </div>
          </div>
          <div class="panel-body params-body">
            <div v-if="paramsTab === 'basic'">
              <div class="param-group">
                <label>Максимум активов (Δ)</label>
                <div class="param-input-group">
                  <input
                    type="number"
                    v-model.number="params.Delta"
                    min="1"
                    :max="clusteringResult.numAssets"
                    @input="recomputeOptimization"
                  />
                  <span class="param-hint">из {{ clusteringResult.numAssets }}</span>
                </div>
              </div>

              <div class="param-group">
                <label>Макс. вес на актив (w̄)</label>
                <div class="param-input-group">
                  <input
                    type="number"
                    v-model.number="params.bar_w"
                    min="0.01"
                    max="1"
                    step="0.01"
                    @input="recomputeOptimization"
                  />
                  <span class="param-hint">{{ (params.bar_w * 100).toFixed(1) }}%</span>
                </div>
              </div>

              <div class="param-group">
                <label>Коэффициент неприятия риска (γ)</label>
                <div class="param-input-group">
                  <input
                    type="number"
                    v-model.number="params.gamma"
                    min="0.1"
                    max="10"
                    step="0.1"
                    @input="recomputeOptimization"
                  />
                  <span class="param-hint">выше = консервативнее</span>
                </div>
              </div>
            </div>

            <div v-if="paramsTab === 'methodology'">
              <div class="param-group">
                <label>Методология</label>
                <div class="radio-group">
                  <label class="radio-item">
                    <input
                      type="radio"
                      v-model="params.method"
                      value="delta"
                      @change="recomputeOptimization"
                    />
                    <span>Δ-CCMV (по количеству активов)</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      v-model="params.method"
                      value="alpha"
                      @change="recomputeOptimization"
                    />
                    <span>α-CCMV (по распределению)</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Objective Function Value -->
        <div class="glass-panel metrics-card">
          <div class="panel-header">
            <h3>Целевая функция</h3>
          </div>
          <div class="panel-body metrics-value">
            <div class="obj-value">
              <span class="label">f*(Δ, α) =</span>
              <span class="value">{{ objectiveValue.toFixed(6) }}</span>
            </div>
            <div class="obj-components">
              <div class="component">
                <span class="comp-label">Риск</span>
                <span class="comp-value text-red">{{ (objectiveComponents.variance).toFixed(6) }}</span>
              </div>
              <div class="component">
                <span class="comp-label">Возврат</span>
                <span class="comp-value text-green">{{ (objectiveComponents.return * params.gamma).toFixed(6) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Weights Comparison and Clustering -->
    <div class="dashboard-grid hjb-grid">
      <div class="col-portfolio-wide">
        <!-- Weights Comparison -->
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Сравнение весов</h3>
            <div class="header-tabs">
              <div class="tab-slider" :style="weightsTabSliderStyle"></div>
              <button
                ref="el => weightsTabButtons.comparison = el"
                :class="['tab-btn', { active: weightsTab === 'comparison' }]"
                @click="weightsTab = 'comparison'"
              >
                Сравнение
              </button>
              <button
                ref="el => weightsTabButtons.optimal = el"
                :class="['tab-btn', { active: weightsTab === 'optimal' }]"
                @click="weightsTab = 'optimal'"
              >
                Оптимальные
              </button>
            </div>
          </div>
          <div class="panel-body weights-body">
            <div v-if="weightsTab === 'comparison'" class="weights-comparison">
              <div class="weights-table-container">
                <table class="weights-table">
                  <thead>
                    <tr>
                      <th>Инструмент</th>
                      <th class="text-right">Текущий вес</th>
                      <th class="text-right">Оптимальный вес</th>
                      <th class="text-right">Изменение</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="pos in portfolioPositions" :key="pos.symbol">
                      <td>
                        <div class="asset-cell">
                          <div class="asset-icon" :style="{ background: pos.color }">{{ pos.symbol[0] }}</div>
                          <div class="asset-info">
                            <span class="symbol">{{ pos.symbol }}</span>
                            <span class="name">{{ pos.name }}</span>
                          </div>
                        </div>
                      </td>
                      <td class="text-right mono">{{ pos.allocation }}%</td>
                      <td class="text-right mono font-bold">
                        {{ getOptimalWeight(pos.symbol).toFixed(1) }}%
                      </td>
                      <td class="text-right mono">
                        <span :class="['change-pill', getDeltaClass(getWeightDelta(pos))]">
                          {{ getWeightDelta(pos) > 0 ? '+' : '' }}{{ getWeightDelta(pos).toFixed(1) }}%
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div v-if="weightsTab === 'optimal'" class="weights-optimal">
              <div class="weight-chart">
                <div
                  v-for="pos in portfolioPositions"
                  :key="pos.symbol"
                  class="weight-bar-container"
                >
                  <div class="weight-bar-info">
                    <div class="asset-icon-small" :style="{ background: pos.color }">{{ pos.symbol[0] }}</div>
                    <div class="weight-bar-label">{{ pos.symbol }}</div>
                  </div>
                  <div class="weight-bar-bg">
                    <div
                      class="weight-bar-fill"
                      :style="{ width: getOptimalWeight(pos.symbol) + '%', background: pos.color }"
                    />
                  </div>
                  <div class="weight-bar-value mono">{{ getOptimalWeight(pos.symbol).toFixed(1) }}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT: Clustering Info -->
      <div class="col-3d-right">
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Иерархическая кластеризация</h3>
          </div>
          <div class="panel-body">
            <div class="cluster-info">
              <div class="info-row">
                <span class="label">Количество кластеров:</span>
                <span class="value mono">{{ clusteringResult.numClusters }}</span>
              </div>
              <div class="info-row">
                <span class="label">Активов в портфеле:</span>
                <span class="value mono">{{ portfolioPositions.length }}</span>
              </div>
              <div class="info-row">
                <span class="label">Метрика расстояния:</span>
                <span class="value mono">1 - ρ (корреляция)</span>
              </div>
              <div class="info-row">
                <span class="label">Метод кластеризации:</span>
                <span class="value mono">Иерархическая (Ward)</span>
              </div>
            </div>

            <!-- Clusters breakdown -->
            <div class="clusters-list">
              <div class="cluster-row" v-for="(cluster, idx) in clusteringResult.clusters" :key="idx">
                <div class="cluster-badge" :style="{ background: clusterColors[idx % clusterColors.length] }">
                  C{{ idx + 1 }}
                </div>
                <div class="cluster-detail">
                  <div class="cluster-label">Кластер {{ idx + 1 }}</div>
                  <div class="cluster-assets">
                    <div class="asset-tag" v-for="symbol in cluster.assets" :key="symbol">
                      <span class="asset-tag-symbol">{{ symbol }}</span>
                      <span class="asset-tag-weight" v-if="getAssetAllocation(symbol)">
                        {{ getAssetAllocation(symbol) }}%
                      </span>
                    </div>
                  </div>
                </div>
                <div class="cluster-count">{{ cluster.assets.length }} {{ cluster.assets.length === 1 ? 'актив' : cluster.assets.length < 5 ? 'актива' : 'активов' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="dashboard-grid">
      <!-- Cluster Metrics -->
      <div class="col-grid">
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Метрики по кластерам</h3>
          </div>
          <div class="panel-body metrics-table-body">
            <table class="metrics-table">
              <thead>
                <tr>
                  <th>Кластер</th>
                  <th>μ (E[R])</th>
                  <th>σ (Vol)</th>
                  <th>ρ̄</th>
                  <th>Δₖ</th>
                  <th>αₖ</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(metric, idx) in clusterMetrics" :key="idx">
                  <td>
                    <div class="cluster-cell">
                      <div class="cluster-dot" :style="{ background: clusterColors[idx] }"></div>
                      <span>C{{ idx + 1 }}</span>
                    </div>
                  </td>
                  <td class="mono text-right">{{ (metric.expectedReturn * 100).toFixed(2) }}%</td>
                  <td class="mono text-right">{{ (metric.volatility * 100).toFixed(2) }}%</td>
                  <td class="mono text-right">{{ metric.avgCorrelation.toFixed(3) }}</td>
                  <td class="mono text-right font-bold">{{ metric.deltaK }}</td>
                  <td class="mono text-right font-bold">{{ (metric.alphaK * 100).toFixed(1) }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Cluster Allocation -->
      <div class="col-grid">
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Распределение по кластерам</h3>
          </div>
          <div class="panel-body allocation-body">
            <div class="allocation-chart">
              <div
                v-for="(alloc, idx) in clusterAllocations"
                :key="idx"
                class="alloc-segment"
                :style="{ 
                  flexGrow: alloc.percentage,
                  background: clusterColors[idx]
                }"
              >
                <span class="alloc-label">
                  C{{ idx + 1 }}<br/>{{ alloc.percentage.toFixed(1) }}%
                </span>
              </div>
            </div>
            <div class="allocation-details">
              <div v-for="(alloc, idx) in clusterAllocations" :key="idx" class="alloc-row">
                <div class="alloc-dot" :style="{ background: clusterColors[idx] }"></div>
                <span class="alloc-name">Кластер {{ idx + 1 }}</span>
                <span class="alloc-pct mono">{{ alloc.percentage.toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Portfolio Statistics -->
      <div class="col-grid">
        <div class="glass-panel metrics-card">
          <div class="panel-header">
            <h3>Статистика портфеля</h3>
          </div>
          <div class="panel-body">
            <div class="stat-row">
              <span class="stat-label">Expected Return</span>
              <span class="stat-val text-green">{{ (portfolioStats.expectedReturn * 100).toFixed(2) }}%</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Volatility</span>
              <span class="stat-val">{{ (portfolioStats.volatility * 100).toFixed(2) }}%</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Sharpe Ratio</span>
              <span class="stat-val">{{ portfolioStats.sharpeRatio.toFixed(3) }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Кол-во позиций</span>
              <span class="stat-val mono">{{ portfolioStats.numPositions }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    </template>

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
import { ref, computed, onMounted, onUnmounted, watch, reactive, nextTick } from 'vue'
import { usePortfolioStore } from '../stores/portfolio'
import { useRiskMetricsStore } from '../stores/riskMetrics'
import { optimizeHJBPortfolio, type HJBResponse } from '../services/hjbService'
import { optimizeCCMVPortfolio, type CCMVResponse, type CCMVCluster } from '../services/ccmvService'
import { calculateGARCH, type GARCHResponse } from '../services/computeService'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

// Динамический импорт Plotly
let Plotly: any = null
let plotlyLoadPromise: Promise<any> | null = null

const loadPlotly = async () => {
  if (typeof window !== 'undefined') {
    const win = window as any
    
    // Если Plotly уже загружен
    if (win.Plotly) {
      Plotly = win.Plotly
      return Plotly
    }
    
    // Если уже идёт загрузка, ждём её завершения
    if (plotlyLoadPromise) {
      return plotlyLoadPromise
    }
    
    // Проверяем, есть ли уже скрипт на странице
    const existingScript = document.querySelector('script[src*="plotly"]')
    if (existingScript) {
      // Ждём загрузки существующего скрипта
      plotlyLoadPromise = new Promise((resolve) => {
        const checkInterval = setInterval(() => {
          if (win.Plotly) {
            clearInterval(checkInterval)
            Plotly = win.Plotly
            resolve(Plotly)
          }
        }, 100)
        // Timeout после 10 секунд
        setTimeout(() => {
          clearInterval(checkInterval)
          resolve(null)
        }, 10000)
      })
      return plotlyLoadPromise
    }
    
    // Загружаем новый скрипт
    plotlyLoadPromise = new Promise((resolve) => {
      const script = document.createElement('script')
      script.src = 'https://cdn.plot.ly/plotly-2.27.0.min.js'
      script.async = true
      script.onload = () => {
        Plotly = win.Plotly
        resolve(Plotly)
      }
      script.onerror = () => {
        console.error('Failed to load Plotly')
        resolve(null)
      }
      document.head.appendChild(script)
    })
    
    return plotlyLoadPromise
  }
  return null
}

interface Cluster {
  assets: string[]
}

interface ClusterMetric {
  expectedReturn: number
  volatility: number
  avgCorrelation: number
  deltaK: number
  alphaK: number
}

// Stores
const portfolioStore = usePortfolioStore()
const riskMetricsStore = useRiskMetricsStore()

// Method selector
const activeMethod = ref<'hjb' | 'ccmv'>('hjb')

const isComputing = ref(false)
const weightsTab = ref<'comparison' | 'optimal'>('comparison')
const paramsTab = ref<'basic' | 'methodology'>('basic')

// Refs for tab buttons to calculate slider position
const paramsTabButtons = ref<{ basic: HTMLElement | null; methodology: HTMLElement | null }>({
  basic: null,
  methodology: null
})
const weightsTabButtons = ref<{ comparison: HTMLElement | null; optimal: HTMLElement | null }>({
  comparison: null,
  optimal: null
})

// Computed slider styles for params tabs
const paramsTabSliderStyle = computed(() => {
  const activeTab = paramsTab.value
  const button = paramsTabButtons.value[activeTab]
  if (!button) return { width: '0px', left: '0px', opacity: 0 }
  
  // Use offsetLeft and offsetWidth for more reliable positioning
  const left = button.offsetLeft
  const width = button.offsetWidth
  
  return {
    width: `${width}px`,
    left: `${left}px`,
    opacity: 1
  }
})

// Computed slider styles for weights tabs
const weightsTabSliderStyle = computed(() => {
  const activeTab = weightsTab.value
  const button = weightsTabButtons.value[activeTab]
  if (!button) return { width: '0px', left: '0px', opacity: 0 }
  
  // Use offsetLeft and offsetWidth for more reliable positioning
  const left = button.offsetLeft
  const width = button.offsetWidth
  
  return {
    width: `${width}px`,
    left: `${left}px`,
    opacity: 1
  }
})

// Portfolio composition from store
const portfolioPositions = computed(() => portfolioStore.positions)
const correlationMatrix = computed(() => portfolioStore.correlationMatrix)
const selectedBank = computed(() => portfolioStore.selectedBank)
const hoveredAsset = ref<any>(null)

// ==================== HJB PARAMETERS ====================
const hjbParams = ref({
  gamma: 2.0,           // Risk aversion coefficient
  horizon: 1.0,         // Investment horizon (years)
  riskFreeRate: 0.045,  // Risk-free rate
  marketVol: 0.18,      // Market volatility
  expectedReturn: 0.10, // Expected return
  monteCarloTrajectories: 10000 // Number of Monte Carlo trajectories
})

// HJB Optimal allocation (Merton's formula)
const hjbOptimalAllocation = computed(() => {
  const { expectedReturn, riskFreeRate, gamma, marketVol } = hjbParams.value
  const excessReturn = expectedReturn - riskFreeRate
  const allocation = excessReturn / (gamma * marketVol * marketVol)
  return Math.max(0, Math.min(allocation, 2)) // Capped between 0 and 200%
})

// Portfolio expected return
const hjbExpectedPortfolioReturn = computed(() => {
  const pi = hjbOptimalAllocation.value
  const { expectedReturn, riskFreeRate } = hjbParams.value
  return riskFreeRate + pi * (expectedReturn - riskFreeRate)
})

// Portfolio volatility
const hjbPortfolioVol = computed(() => {
  const pi = hjbOptimalAllocation.value
  return pi * hjbParams.value.marketVol
})

// Sharpe ratio
const hjbSharpeRatio = computed(() => {
  const { expectedReturn, riskFreeRate, marketVol } = hjbParams.value
  return (expectedReturn - riskFreeRate) / marketVol
})

// Certainty equivalent
const hjbCertaintyEquivalent = computed(() => {
  const { gamma } = hjbParams.value
  const excessReturn = hjbExpectedPortfolioReturn.value - hjbParams.value.riskFreeRate
  const variance = hjbPortfolioVol.value * hjbPortfolioVol.value
  return hjbParams.value.riskFreeRate + excessReturn - 0.5 * gamma * variance
})

// ==================== MONTE CARLO TRAJECTORIES ====================
const playbackStepTrajectories = ref(0)
const isPlayingTrajectories = ref(false)
let animationFrameTrajectories: number | null = null
const trajectoriesChartContainer = ref<HTMLElement | null>(null)
const initialPrice = ref(0)

// Convert horizon from years to days (252 trading days per year)
const trajectoriesDays = computed(() => {
  return Math.round(hjbParams.value.horizon * 252)
})

const trajectoriesData = reactive({
  paths: [] as number[][],       
  displayPaths: [] as number[][],
  medianPath: [] as number[],
  q05: [] as number[],
  q95: [] as number[],
  minY: 0,
  maxY: 200
})

// Watch monteCarloTrajectories to update display paths
watch(() => hjbParams.value.monteCarloTrajectories, () => {
  // If we have backend data, just update display paths and 3D visualization
  if (hjbOptimizationResult.value?.monte_carlo) {
    // Update display paths from backend data
    if (trajectoriesData.paths.length > 0) {
      updateDisplayPaths()
    }
    // Update 3D visualization with new path count
    if (activeMethod.value === 'hjb') {
      update3DVisualizationFromBackend(hjbOptimizationResult.value.monte_carlo)
    }
  } else {
    // If no backend data, regenerate trajectories locally
    generateTrajectories()
    // Also regenerate 3D if initialized
    if (activeMethod.value === 'hjb' && trajectories3DCanvas.value && renderer3D) {
      const basePrice = initialPrice.value * 10000
      // Используем значение из параметра без ограничений
      const config: SimulationConfig3D = {
        initialPrice: basePrice,
        drift: hjbParams.value.expectedReturn,
        volatility: hjbParams.value.marketVol,
        timeSteps: trajectoriesDays.value,
        numPaths: hjbParams.value.monteCarloTrajectories,
        dt: 1 / 252,
        jumpIntensity: 2.0,
        jumpMean: 0.05,
        jumpSd: 0.15
      }
      simulationResult3D.value = runMonteCarlo3D(config)
      const maxStep = simulationResult3D.value.paths[0]?.length || 0
      currentStep3D.value = maxStep
      playbackStep3D.value = maxStep
      cameraPositioned = false
      stopPlay3D()
      update3DTrajectories()
    }
  }
})

// Watch hjbParams to regenerate trajectories when parameters change
// Only generate locally if we don't have backend data
watch(() => [
  hjbParams.value.horizon,
  hjbParams.value.expectedReturn,
  hjbParams.value.marketVol,
  hjbParams.value.riskFreeRate
], () => {
  // Only generate locally if we don't have backend results
  if (!hjbOptimizationResult.value?.monte_carlo) {
    generateTrajectories()
  }
}, { deep: true })

// Generate trajectories based on HJB parameters
const generateTrajectories = () => {
  const { horizon, expectedReturn, marketVol, riskFreeRate, monteCarloTrajectories } = hjbParams.value
  const days = trajectoriesDays.value // Convert years to days
  const dt = 1 / 252
  const mu = expectedReturn
  const sigma = marketVol
  
  const newPaths: number[][] = []
  
  for (let i = 0; i < monteCarloTrajectories; i++) {
    const path = [initialPrice.value]
    let currentPrice = initialPrice.value
    
    for (let t = 1; t <= days; t++) {
      const Z = boxMullerRandomTrajectories()
      const driftTerm = (mu - 0.5 * sigma * sigma) * dt
      const shockTerm = sigma * Math.sqrt(dt) * Z
      currentPrice = currentPrice * Math.exp(driftTerm + shockTerm)
      path.push(currentPrice)
    }
    newPaths.push(path)
  }
  
  // Calculate quantiles
  const steps = days + 1
  const medianPath: number[] = []
  const q05Path: number[] = []
  const q95Path: number[] = []
  let globalMin = initialPrice.value
  let globalMax = initialPrice.value

  for (let t = 0; t < steps; t++) {
    const pricesAtT = newPaths.map(p => p[t]).sort((a, b) => a - b)
    const med = pricesAtT[Math.floor(monteCarloTrajectories * 0.5)]
    const q05 = pricesAtT[Math.floor(monteCarloTrajectories * 0.05)]
    const q95 = pricesAtT[Math.floor(monteCarloTrajectories * 0.95)]
    
    medianPath.push(med)
    q05Path.push(q05)
    q95Path.push(q95)

    if (q05 < globalMin) globalMin = q05
    if (q95 > globalMax) globalMax = q95
  }

  trajectoriesData.paths = newPaths
  // Обновляем displayPaths на основе текущего значения monteCarloTrajectories
  updateDisplayPaths()
  trajectoriesData.medianPath = medianPath
  trajectoriesData.q05 = q05Path
  trajectoriesData.q95 = q95Path
  trajectoriesData.minY = globalMin * 0.9
  trajectoriesData.maxY = globalMax * 1.1
  
  if (!isPlayingTrajectories.value) {
    playbackStepTrajectories.value = days
  }
}

// Function to update displayPaths based on monteCarloTrajectories parameter
const updateDisplayPaths = () => {
  if (!trajectoriesData.paths.length) return
  
  // Используем все доступные траектории или количество из параметра
  const numPaths = Math.min(
    hjbParams.value.monteCarloTrajectories,
    trajectoriesData.paths.length
  )
  trajectoriesData.displayPaths = trajectoriesData.paths.slice(0, numPaths)
}

// Playback controls
const togglePlayTrajectories = () => {
  if (isPlayingTrajectories.value) {
    stopPlayTrajectories()
  } else {
    if (playbackStepTrajectories.value >= trajectoriesDays.value) {
      playbackStepTrajectories.value = 0
    }
    isPlayingTrajectories.value = true
    animateTrajectories()
  }
}

const stopPlayTrajectories = () => {
  isPlayingTrajectories.value = false
  if (animationFrameTrajectories) {
    cancelAnimationFrame(animationFrameTrajectories)
  }
}

const resetPlaybackTrajectories = () => {
  stopPlayTrajectories()
  playbackStepTrajectories.value = 0
}

const animateTrajectories = () => {
  if (!isPlayingTrajectories.value) return
  
  const days = trajectoriesDays.value
  const nextStep = playbackStepTrajectories.value + Math.max(1, Math.floor(days / 100))
  
  if (nextStep >= days) {
    playbackStepTrajectories.value = days
    stopPlayTrajectories()
  } else {
    playbackStepTrajectories.value = nextStep
    animationFrameTrajectories = requestAnimationFrame(animateTrajectories)
  }
}

// ==================== 3D TRAJECTORIES VISUALIZATION ====================
interface PathPoint3D {
  x: number // Time
  y: number // Price/Value
  z: number // Simulation Index
  isJump?: boolean
}

interface SimulationResult3D {
  paths: PathPoint3D[][]
  jumps: PathPoint3D[]
  stats: {
    meanFinalPrice: number
    maxPrice: number
    minPrice: number
    stdDev: number
  }
}

interface SimulationConfig3D {
  initialPrice: number
  drift: number
  volatility: number
  timeSteps: number
  numPaths: number
  dt: number
  jumpIntensity: number
  jumpMean: number
  jumpSd: number
}

const trajectories3DCanvas = ref<HTMLCanvasElement | null>(null)
let scene3D: THREE.Scene | null = null
let camera3D: THREE.PerspectiveCamera | null = null
let renderer3D: THREE.WebGLRenderer | null = null
let controls3D: any = null
let animationId3D: number | null = null
let currentStep3D = ref(0)
let cameraPositioned = false
const simulationResult3D = ref<SimulationResult3D | null>(null)
const trajectories3DLines: THREE.Line[] = []
let lastUpdateTime = 0
const UPDATE_THROTTLE_MS = 100 // Update trajectories max once per 100ms
let cachedScaleParams: { scaleX: number; scaleY: number; scaleZ: number; stats: any; boxWidth: number; boxDepth: number } | null = null

// 3D Playback controls
const isPlaying3D = ref(false)
const playbackStep3D = ref(0)
let animationFrame3D: number | null = null

// Computed max step for 3D
const maxStep3D = computed(() => {
  if (!simulationResult3D.value || !simulationResult3D.value.paths.length) return 0
  return simulationResult3D.value.paths[0].length - 1
})

// Helper function to format percentage
const formatPercent = (value: number): string => {
  return (value * 100).toFixed(2) + '%'
}

// Calculate portfolio returns from simulation paths
const getPortfolioReturns = (): number[] => {
  if (!simulationResult3D.value || !simulationResult3D.value.paths.length) return []
  
  const paths = simulationResult3D.value.paths
  const returns: number[] = []
  
  // Find initial price from first point of first path
  const initialPrice = paths[0]?.[0]?.y || 1000000
  
  // Calculate return for each path (final price / initial price - 1)
  for (const path of paths) {
    if (path.length > 0) {
      const finalPrice = path[path.length - 1].y
      const return_ = (finalPrice / initialPrice) - 1
      returns.push(return_)
    }
  }
  
  return returns
}

// Average return
const averageReturn = computed(() => {
  const returns = getPortfolioReturns()
  if (returns.length === 0) return 0
  return returns.reduce((sum, r) => sum + r, 0) / returns.length
})

// Median return
const medianReturn = computed(() => {
  const returns = getPortfolioReturns()
  if (returns.length === 0) return 0
  const sorted = [...returns].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0
    ? (sorted[mid - 1] + sorted[mid]) / 2
    : sorted[mid]
})

// Sharpe Ratio (assuming risk-free rate = 0)
const sharpeRatio = computed(() => {
  const returns = getPortfolioReturns()
  if (returns.length === 0) return 0
  
  const mean = averageReturn.value
  const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length
  const stdDev = Math.sqrt(variance)
  
  // Annualize based on simulation period
  const simulationDays = trajectoriesDays.value || 252
  const years = simulationDays / 252
  const annualMean = mean / years
  const annualStdDev = stdDev / Math.sqrt(years)
  
  if (annualStdDev === 0) return 0
  return annualMean / annualStdDev
})

// VaR (95%) - Value at Risk
const var95 = computed(() => {
  const returns = getPortfolioReturns()
  if (returns.length === 0) return 0
  
  const sorted = [...returns].sort((a, b) => a - b)
  const index = Math.floor(sorted.length * 0.05) // 5th percentile (worst 5%)
  return sorted[index] || 0
})

// CVaR (95%) - Conditional Value at Risk (Expected Shortfall)
const cvar95 = computed(() => {
  const returns = getPortfolioReturns()
  if (returns.length === 0) return 0
  
  const sorted = [...returns].sort((a, b) => a - b)
  const varIndex = Math.floor(sorted.length * 0.05)
  const tailReturns = sorted.slice(0, varIndex + 1)
  
  if (tailReturns.length === 0) return 0
  return tailReturns.reduce((sum, r) => sum + r, 0) / tailReturns.length
})

// Average Maximum Drawdown (MDD)
const averageMDD = computed(() => {
  if (!simulationResult3D.value || !simulationResult3D.value.paths.length) return 0
  
  const paths = simulationResult3D.value.paths
  const mddValues: number[] = []
  
  for (const path of paths) {
    if (path.length === 0) continue
    
    let peak = path[0].y
    let maxDrawdown = 0
    
    for (const point of path) {
      if (point.y > peak) {
        peak = point.y
      }
      const drawdown = (peak - point.y) / peak
      if (drawdown > maxDrawdown) {
        maxDrawdown = drawdown
      }
    }
    
    mddValues.push(maxDrawdown)
  }
  
  if (mddValues.length === 0) return 0
  return mddValues.reduce((sum, mdd) => sum + mdd, 0) / mddValues.length
})

// 3D Playback functions
const togglePlay3D = () => {
  if (isPlaying3D.value) {
    stopPlay3D()
  } else {
    if (playbackStep3D.value >= maxStep3D.value) {
      playbackStep3D.value = 0
    }
    isPlaying3D.value = true
    animate3D()
  }
}

const stopPlay3D = () => {
  isPlaying3D.value = false
  if (animationFrame3D) {
    cancelAnimationFrame(animationFrame3D)
    animationFrame3D = null
  }
}

const resetPlayback3D = () => {
  stopPlay3D()
  playbackStep3D.value = 0
  currentStep3D.value = 0
  update3DTrajectories()
}

const animate3D = () => {
  if (!isPlaying3D.value) return
  
  const maxStep = maxStep3D.value
  const nextStep = playbackStep3D.value + Math.max(1, Math.floor(maxStep / 100))
  
  if (nextStep >= maxStep) {
    playbackStep3D.value = maxStep
    currentStep3D.value = maxStep
    stopPlay3D()
    update3DTrajectories()
  } else {
    playbackStep3D.value = nextStep
    currentStep3D.value = nextStep
    update3DTrajectories()
    animationFrame3D = requestAnimationFrame(animate3D)
  }
}

// Watch playback step changes from slider
watch(playbackStep3D, (newStep) => {
  if (!isPlaying3D.value) {
    currentStep3D.value = newStep
    update3DTrajectories()
  }
})

const runMonteCarlo3D = (config: SimulationConfig3D): SimulationResult3D => {
  const { 
    initialPrice, drift, volatility, timeSteps, numPaths, dt,
    jumpIntensity, jumpMean, jumpSd 
  } = config
  
  const paths: PathPoint3D[][] = []
  const allJumps: PathPoint3D[] = []
  
  let totalFinalPrice = 0
  let maxPrice = -Infinity
  let minPrice = Infinity
  const finalPrices: number[] = []

  for (let i = 0; i < numPaths; i++) {
    const path: PathPoint3D[] = []
    let currentPrice = initialPrice
    
    // Start at t=0
    path.push({ x: 0, y: currentPrice, z: i })

    for (let t = 1; t <= timeSteps; t++) {
      // 1. Standard Geometric Brownian Motion Component
      const u1 = Math.random()
      const u2 = Math.random()
      const z = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2)
      
      let diffusion = (drift - 0.5 * volatility * volatility) * dt + volatility * Math.sqrt(dt) * z

      // 2. Jump Component (Poisson Process)
      let jumpMultiplier = 1
      let isJumpStep = false

      // Poisson check: does a jump occur?
      if (Math.random() < jumpIntensity * dt) {
        isJumpStep = true
        // Generate jump size (Log-normal distribution)
        const jU1 = Math.random()
        const jU2 = Math.random()
        const jZ = Math.sqrt(-2.0 * Math.log(jU1)) * Math.cos(2.0 * Math.PI * jU2)
        
        // Jump magnitude
        const jumpMagnitude = jumpMean + jumpSd * jZ
        jumpMultiplier = Math.exp(jumpMagnitude)
      }

      // Calculate new price
      // S(t) = S(t-1) * exp(diffusion) * jumpMultiplier
      currentPrice = currentPrice * Math.exp(diffusion) * jumpMultiplier
      
      const point: PathPoint3D = { x: t, y: currentPrice, z: i, isJump: isJumpStep }
      path.push(point)

      if (isJumpStep) {
        allJumps.push(point)
      }
      
      maxPrice = Math.max(maxPrice, currentPrice)
      minPrice = Math.min(minPrice, currentPrice)
    }
    
    paths.push(path)
    totalFinalPrice += currentPrice
    finalPrices.push(currentPrice)
  }

  const meanFinalPrice = totalFinalPrice / numPaths
  const variance = finalPrices.reduce((acc, p) => acc + Math.pow(p - meanFinalPrice, 2), 0) / numPaths
  const stdDev = Math.sqrt(variance)

  return {
    paths,
    jumps: allJumps,
    stats: {
      meanFinalPrice,
      maxPrice,
      minPrice,
      stdDev
    }
  }
}

const init3DTrajectories = async () => {
  if (!trajectories3DCanvas.value || activeMethod.value !== 'hjb') {
    console.log('3D init skipped:', { canvas: !!trajectories3DCanvas.value, method: activeMethod.value })
    return
  }
  
  // Cleanup existing scene if any
  if (renderer3D) {
    renderer3D.dispose()
    renderer3D = null
  }
  if (animationId3D) {
    cancelAnimationFrame(animationId3D)
    animationId3D = null
  }
    cameraPositioned = false // Reset camera positioning flag
    cachedScaleParams = null // Clear cache
    lastUpdateTime = 0
  
  const container = trajectories3DCanvas.value.parentElement as HTMLElement
  if (!container) {
    console.error('3D container not found')
    return
  }
  
  const width = container.clientWidth || 800
  const height = container.clientHeight || 600
  
  if (width === 0 || height === 0) {
    console.warn('3D container has zero dimensions, retrying...')
    setTimeout(() => {
      if (activeMethod.value === 'hjb' && trajectories3DCanvas.value) {
        init3DTrajectories()
      }
    }, 500)
    return
  }
  
  console.log('Initializing 3D trajectories:', { width, height })

  // Scene
  scene3D = new THREE.Scene()
  scene3D.background = null // Transparent background

  // Camera
  camera3D = new THREE.PerspectiveCamera(45, width / height, 0.1, 50000)
  
  // Renderer
  renderer3D = new THREE.WebGLRenderer({ 
    canvas: trajectories3DCanvas.value,
    antialias: true, 
    alpha: true 
  })
  renderer3D.setSize(width, height)
  renderer3D.setPixelRatio(window.devicePixelRatio)

  // Orbit Controls
  controls3D = new OrbitControls(camera3D, renderer3D.domElement)
  controls3D.enableDamping = true
  controls3D.dampingFactor = 0.1
  controls3D.rotateSpeed = 0.5

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 3)
  scene3D.add(ambientLight)

  // Use backend data if available, otherwise generate locally
  if (hjbOptimizationResult.value?.monte_carlo) {
    // Use backend Monte Carlo data
    update3DVisualizationFromBackend(hjbOptimizationResult.value.monte_carlo)
    console.log('3D visualization updated from backend:', {
      paths: simulationResult3D.value?.paths.length,
      stats: simulationResult3D.value?.stats
    })
  } else {
    // Generate initial simulation locally
    // Use higher initial price for better visualization (scale 1M like in original)
    const basePrice = initialPrice.value * 10000 // Scale to 1M range for better 3D visualization
    // Используем значение из параметра без ограничений
    const config: SimulationConfig3D = {
      initialPrice: basePrice,
      drift: hjbParams.value.expectedReturn,
      volatility: hjbParams.value.marketVol,
      timeSteps: trajectoriesDays.value,
      numPaths: hjbParams.value.monteCarloTrajectories,
      dt: 1 / 252,
      jumpIntensity: 2.0,
      jumpMean: 0.05,
      jumpSd: 0.15
    }

    simulationResult3D.value = runMonteCarlo3D(config)
    console.log('3D simulation generated locally:', {
      paths: simulationResult3D.value.paths.length,
      stats: simulationResult3D.value.stats,
      firstPathLength: simulationResult3D.value.paths[0]?.length
    })
    
    // Initialize current step and playback step to show all trajectories
    const maxStep = simulationResult3D.value.paths[0]?.length || 0
    currentStep3D.value = maxStep
    playbackStep3D.value = maxStep
    
    update3DTrajectories()
  }

  // Initial camera position - set after trajectories are created
  // Will be set in update3DTrajectories after first render

  // Animation loop - render only (playback controlled by user)
  const animate = () => {
    animationId3D = requestAnimationFrame(animate)
    
    // Always update controls and render
    if (controls3D) controls3D.update()
    if (renderer3D && scene3D && camera3D) {
      renderer3D.render(scene3D, camera3D)
    }
  }
  
  animate()

  // Handle resize
  const handleResize = () => {
    if (!container || !camera3D || !renderer3D) return
    const newWidth = container.clientWidth
    const newHeight = container.clientHeight || 500
    
    camera3D.aspect = newWidth / newHeight
    camera3D.updateProjectionMatrix()
    renderer3D.setSize(newWidth, newHeight)
  }
  
  window.addEventListener('resize', handleResize)
  
  // Cleanup on unmount
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
    if (animationId3D) {
      cancelAnimationFrame(animationId3D)
    }
    if (renderer3D) {
      renderer3D.dispose()
    }
  })
}

const update3DTrajectories = () => {
  if (!scene3D || !simulationResult3D.value) return

  // Clear existing lines
  trajectories3DLines.forEach(line => {
    scene3D?.remove(line)
    line.geometry.dispose()
    if ((line.material as THREE.Material).dispose) {
      (line.material as THREE.Material).dispose()
    }
  })
  trajectories3DLines.length = 0

  const { paths, stats } = simulationResult3D.value
  // Cache scale parameters if not cached
  if (!cachedScaleParams || cachedScaleParams.stats !== stats) {
    const scaleX = 3.0
    const scaleZ = 8.0 // Increased for better Z-axis visibility
    const targetVisualHeight = 300 // Increased for better Y-axis visibility
    const priceRange = stats.maxPrice - stats.minPrice
    const safeRange = Math.max(priceRange, stats.meanFinalPrice * 0.05, 1.0)
    const scaleY = targetVisualHeight / safeRange // Increased scale for Y-axis
    
    const boxWidth = paths[0].length * scaleX
    const boxDepth = paths.length * scaleZ
    
    cachedScaleParams = { scaleX, scaleY, scaleZ, stats, boxWidth, boxDepth }
  }
  
  const { scaleX, scaleY, scaleZ, boxWidth, boxDepth } = cachedScaleParams
  
  // Start from zero - no negative offsets
  const dataOffsetX = 0
  const dataOffsetZ = 0
  
  // Y starts from zero (minPrice maps to 0)
  const maxY = (stats.maxPrice - stats.minPrice) * scaleY
  const targetY = maxY / 2 // Center of Y range
  const boxCenterX = boxWidth / 2 // Center of X range
  const boxCenterZ = boxDepth / 2 // Center of Z range
  
  // Update camera position to view the data (only once)
  if (camera3D && controls3D && !cameraPositioned) {
    const cameraDistance = Math.max(boxWidth, boxDepth, maxY) * 0.8
    camera3D.position.set(cameraDistance, targetY + cameraDistance * 0.5, cameraDistance)
    controls3D.target.set(boxCenterX, targetY, boxCenterZ)
    controls3D.update()
    cameraPositioned = true
    console.log('Camera positioned:', {
      position: camera3D.position.toArray(),
      target: [boxCenterX, targetY, boxCenterZ],
      distance: cameraDistance
    })
  }
  
  // Cache materials for reuse
  const primaryMaterial = new THREE.LineBasicMaterial({ 
    color: 0x00f0ff, 
    transparent: true, 
    opacity: 0.6,
    linewidth: 1.5
  })
  const whiteMaterial = new THREE.LineBasicMaterial({ 
    color: 0xffffff, 
    transparent: true, 
    opacity: 1.0,
    linewidth: 2.5
  })

  // Clear existing lines only if count changed
  if (trajectories3DLines.length !== paths.length) {
    trajectories3DLines.forEach(line => {
      scene3D?.remove(line)
      line.geometry.dispose()
    })
    trajectories3DLines.length = 0
  }

  paths.forEach((path, idx) => {
    const finalVal = path[path.length - 1].y
    const isOutlier = Math.abs(finalVal - paths[0][0].y) > (stats.stdDev * 1.5)
    const material = isOutlier ? whiteMaterial : primaryMaterial

    // Limit to current step
    const limit = Math.max(2, Math.min(path.length, currentStep3D.value))
    const activePoints = path.slice(0, limit)
    
    if (activePoints.length < 2) return

    // Reuse existing line or create new one
    let line = trajectories3DLines[idx]
    if (!line) {
      const points: THREE.Vector3[] = activePoints.map(p => {
        return new THREE.Vector3(
          (p.x * scaleX) + dataOffsetX,
          (p.y - stats.minPrice) * scaleY, // Start Y from 0
          (p.z * scaleZ) + dataOffsetZ
        )
      })
      const geometry = new THREE.BufferGeometry().setFromPoints(points)
      line = new THREE.Line(geometry, material)
      if (scene3D) {
        scene3D.add(line)
        trajectories3DLines[idx] = line
      }
    } else {
      // Update existing geometry instead of recreating
      const positions: number[] = []
      activePoints.forEach(p => {
        positions.push(
          (p.x * scaleX) + dataOffsetX,
          (p.y - stats.minPrice) * scaleY,
          (p.z * scaleZ) + dataOffsetZ
        )
      })
      line.geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
      line.geometry.setDrawRange(0, activePoints.length)
      // Update material if outlier status changed
      const finalVal = path[path.length - 1].y
      const isOutlier = Math.abs(finalVal - paths[0][0].y) > (stats.stdDev * 1.5)
      line.material = isOutlier ? whiteMaterial : primaryMaterial
    }
  })
  
  // Remove excess lines if paths count decreased
  while (trajectories3DLines.length > paths.length) {
    const line = trajectories3DLines.pop()
    if (line && scene3D) {
      scene3D.remove(line)
      line.geometry.dispose()
    }
  }

  // Update grids if needed
  update3DGrids(stats, scaleX, scaleY, scaleZ, boxWidth, boxDepth)
  
  // Force render
  if (renderer3D && scene3D && camera3D) {
    renderer3D.render(scene3D, camera3D)
  }
}

let gridObjects: THREE.Group[] = []
let axisLabels: THREE.Sprite[] = []

// Helper function to create axis label sprite
const createAxisLabelSprite = (text: string, position: THREE.Vector3, size: number = 8): THREE.Sprite => {
  const canvas = document.createElement('canvas')
  canvas.width = 6144
  canvas.height = 3072
  const ctx = canvas.getContext('2d')!
  ctx.fillStyle = '#ffffff'
  ctx.strokeStyle = '#000000'
  ctx.lineWidth = 24
  ctx.font = `bold ${600}px Arial`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  // Draw text with stroke for better visibility
  ctx.strokeText(text, 3072, 1536)
  ctx.fillText(text, 3072, 1536)
  
  const texture = new THREE.CanvasTexture(canvas)
  const spriteMaterial = new THREE.SpriteMaterial({ map: texture })
  const sprite = new THREE.Sprite(spriteMaterial)
  sprite.scale.set(size, size / 2, 1)
  sprite.position.copy(position)
  return sprite
}

const update3DGrids = (stats: any, scaleX: number, scaleY: number, scaleZ: number, boxWidth: number, boxDepth: number) => {
  // Remove old grids
  if (!scene3D) return
  gridObjects.forEach(grid => {
    if (scene3D) {
      scene3D.remove(grid)
    }
    grid.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.geometry.dispose()
        if (child.material instanceof THREE.Material) {
          child.material.dispose()
        }
      }
    })
  })
  gridObjects.length = 0

  // Remove old axis labels
  axisLabels.forEach(sprite => {
    if (scene3D) {
      scene3D.remove(sprite)
    }
    if (sprite.material instanceof THREE.SpriteMaterial) {
      sprite.material.map?.dispose()
      sprite.material.dispose()
    }
  })
  axisLabels.length = 0

  if (!scene3D) return

  // All axes start from zero
  const boxHeight = (stats.maxPrice - stats.minPrice) * scaleY * 1.2
  const targetY = boxHeight / 2 // Center of Y range (starts from 0)
  
  const gridGroup = new THREE.Group()
  
  // Helper function to create positive-only grid (starts from 0,0)
  const createPositiveGrid = (width: number, height: number, color: number = 0x0088aa, sectionColor: number = 0x003344) => {
    const gridGroup = new THREE.Group()
    const cellSize = 50
    const sectionSize = 250
    
    // Create grid lines only in positive quadrant
    const lineMaterial = new THREE.LineBasicMaterial({ color: color, opacity: 0.3, transparent: true })
    const sectionMaterial = new THREE.LineBasicMaterial({ color: sectionColor, opacity: 0.5, transparent: true })
    
    // Vertical lines (along width)
    for (let i = 0; i <= width; i += cellSize) {
      const isSection = i % sectionSize === 0
      const material = isSection ? sectionMaterial : lineMaterial
      const geometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(i, 0, 0),
        new THREE.Vector3(i, 0, height)
      ])
      const line = new THREE.Line(geometry, material)
      gridGroup.add(line)
    }
    
    // Horizontal lines (along height)
    for (let i = 0; i <= height; i += cellSize) {
      const isSection = i % sectionSize === 0
      const material = isSection ? sectionMaterial : lineMaterial
      const geometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, i),
        new THREE.Vector3(width, 0, i)
      ])
      const line = new THREE.Line(geometry, material)
      gridGroup.add(line)
    }
    
    return gridGroup
  }

  // Helper function to create grid for YZ plane (height x depth)
  // YZ plane is vertical, lines are in YZ plane (parallel to Y and Z axes)
  const createYZGrid = (height: number, depth: number, color: number = 0x0088aa, sectionColor: number = 0x003344) => {
    const gridGroup = new THREE.Group()
    const cellSize = 50
    const sectionSize = 250
    
    const lineMaterial = new THREE.LineBasicMaterial({ color: color, opacity: 0.3, transparent: true })
    const sectionMaterial = new THREE.LineBasicMaterial({ color: sectionColor, opacity: 0.5, transparent: true })
    
    // Lines parallel to Y-axis (vertical in YZ plane) - along Z
    for (let z = 0; z <= depth; z += cellSize) {
      const isSection = z % sectionSize === 0
      const material = isSection ? sectionMaterial : lineMaterial
      const geometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, z),
        new THREE.Vector3(0, height, z)
      ])
      const line = new THREE.Line(geometry, material)
      gridGroup.add(line)
    }
    
    // Lines parallel to Z-axis (horizontal in YZ plane) - along Y
    for (let y = 0; y <= height; y += cellSize) {
      const isSection = y % sectionSize === 0
      const material = isSection ? sectionMaterial : lineMaterial
      const geometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, y, 0),
        new THREE.Vector3(0, y, depth)
      ])
      const line = new THREE.Line(geometry, material)
      gridGroup.add(line)
    }
    
    return gridGroup
  }

  // Helper function to create grid for XY plane (width x height)
  // XY plane is vertical, lines are in XY plane (parallel to X and Y axes)
  const createXYGrid = (width: number, height: number, color: number = 0x0088aa, sectionColor: number = 0x003344) => {
    const gridGroup = new THREE.Group()
    const cellSize = 50
    const sectionSize = 250
    
    const lineMaterial = new THREE.LineBasicMaterial({ color: color, opacity: 0.3, transparent: true })
    const sectionMaterial = new THREE.LineBasicMaterial({ color: sectionColor, opacity: 0.5, transparent: true })
    
    // Lines parallel to Y-axis (vertical in XY plane) - along X
    for (let x = 0; x <= width; x += cellSize) {
      const isSection = x % sectionSize === 0
      const material = isSection ? sectionMaterial : lineMaterial
      const geometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(x, 0, 0),
        new THREE.Vector3(x, height, 0)
      ])
      const line = new THREE.Line(geometry, material)
      gridGroup.add(line)
    }
    
    // Lines parallel to X-axis (horizontal in XY plane) - along Y
    for (let y = 0; y <= height; y += cellSize) {
      const isSection = y % sectionSize === 0
      const material = isSection ? sectionMaterial : lineMaterial
      const geometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, y, 0),
        new THREE.Vector3(width, y, 0)
      ])
      const line = new THREE.Line(geometry, material)
      gridGroup.add(line)
    }
    
    return gridGroup
  }

  // Floor Grid (XZ plane) - starts at y=0, only positive quadrant (X and Z from 0)
  // This grid is horizontal, parallel to XZ plane
  const floorGrid = createPositiveGrid(boxWidth, boxDepth)
  floorGrid.position.set(0, 0, 0) // Start from origin (0,0,0)
  gridGroup.add(floorGrid)

  // Back Wall Grid (XY plane) - starts at z=0, only positive quadrant (X and Y from 0)
  // XY plane is vertical, perpendicular to Z axis
  // Lines are already in XY plane (x varies, y varies, z=0), no rotation needed
  const backGrid = createXYGrid(boxWidth, boxHeight)
  backGrid.position.set(0, 0, 0) // Start from origin (0,0,0)
  gridGroup.add(backGrid)

  // Side Wall Grid (YZ plane) - starts at x=0, only positive quadrant (Y and Z from 0)
  // YZ plane is vertical, perpendicular to X axis
  // Lines are already in YZ plane (x=0, y varies, z varies), no rotation needed
  const sideGrid = createYZGrid(boxHeight, boxDepth)
  sideGrid.position.set(0, 0, 0) // Start from origin (0,0,0)
  gridGroup.add(sideGrid)

  // Create visible axes with grid ticks
  const axesLength = Math.max(boxWidth, boxDepth, boxHeight)
  const lineWidth = 3
  const axesColor = 0xffffff
  const axesMaterial = new THREE.LineBasicMaterial({ color: axesColor, linewidth: lineWidth })
  const tickMaterial = new THREE.LineBasicMaterial({ color: 0xaaaaaa, opacity: 0.8, transparent: true })
  const tickSize = axesLength * 0.03
  const cellSize = 50
  const sectionSize = 250
  
  // X-axis (red) - along width (time)
  const xAxisGeometry = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(boxWidth, 0, 0)
  ])
  const xAxisLine = new THREE.Line(xAxisGeometry, axesMaterial)
  gridGroup.add(xAxisLine)
  
  // X-axis ticks (grid marks along X axis)
  for (let x = 0; x <= boxWidth; x += cellSize) {
    const isSection = x % sectionSize === 0
    const material = isSection ? axesMaterial : tickMaterial
    const tickLength = isSection ? tickSize * 1.5 : tickSize
    const geometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(x, -tickLength, 0),
      new THREE.Vector3(x, tickLength, 0)
    ])
    const tick = new THREE.Line(geometry, material)
    gridGroup.add(tick)
  }

  // Y-axis (green) - along height (capital)
  const yAxisGeometry = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0, boxHeight, 0)
  ])
  const yAxisLine = new THREE.Line(yAxisGeometry, axesMaterial)
  gridGroup.add(yAxisLine)
  
  // Y-axis ticks (grid marks along Y axis)
  for (let y = 0; y <= boxHeight; y += cellSize) {
    const isSection = y % sectionSize === 0
    const material = isSection ? axesMaterial : tickMaterial
    const tickLength = isSection ? tickSize * 1.5 : tickSize
    const geometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-tickLength, y, 0),
      new THREE.Vector3(tickLength, y, 0)
    ])
    const tick = new THREE.Line(geometry, material)
    gridGroup.add(tick)
  }

  // Z-axis (blue) - along depth (paths)
  const zAxisGeometry = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0, 0, boxDepth)
  ])
  const zAxisLine = new THREE.Line(zAxisGeometry, axesMaterial)
  gridGroup.add(zAxisLine)
  
  // Z-axis ticks (grid marks along Z axis)
  for (let z = 0; z <= boxDepth; z += cellSize) {
    const isSection = z % sectionSize === 0
    const material = isSection ? axesMaterial : tickMaterial
    const tickLength = isSection ? tickSize * 1.5 : tickSize
    const geometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-tickLength, 0, z),
      new THREE.Vector3(tickLength, 0, z)
    ])
    const tick = new THREE.Line(geometry, material)
    gridGroup.add(tick)
  }

  // Add axis labels - positioned at the middle of each axis (large and visible)
  // X-axis label (TIME) - at the middle of X axis, close to the axis
  const xLabel = createAxisLabelSprite('ВРЕМЯ (t)', new THREE.Vector3(boxWidth / 2, -120, 0), 150)
  axisLabels.push(xLabel)
  scene3D.add(xLabel)

  // Y-axis label (CAPITAL) - at the middle of Y axis, close to the axis
  const yLabel = createAxisLabelSprite('Капитал', new THREE.Vector3(-150, boxHeight / 2, 0), 150)
  axisLabels.push(yLabel)
  scene3D.add(yLabel)

  // Z-axis label (PATHS) - at the middle of Z axis, close to the axis
  const zLabel = createAxisLabelSprite('ТРАЕКТОРИИ (N)', new THREE.Vector3(-120, -120, boxDepth / 2), 150)
  axisLabels.push(zLabel)
  scene3D.add(zLabel)

  if (scene3D) {
    scene3D.add(gridGroup)
    gridObjects.push(gridGroup)
  }
}

// Function to convert backend Monte Carlo data to 3D format
const update3DVisualizationFromBackend = (monteCarloData: NonNullable<HJBResponse['monte_carlo']>) => {
  if (!monteCarloData || !monteCarloData.paths.length) return
  
  const paths3D: PathPoint3D[][] = []
  const tGrid = monteCarloData.t_grid || monteCarloData.paths[0].map((_, i) => i)
  
  // Convert each path from backend to 3D format
  // Используем значение из параметра monteCarloTrajectories или все доступные траектории
  const numPaths = Math.min(
    hjbParams.value.monteCarloTrajectories,
    monteCarloData.paths.length
  )
  
  for (let i = 0; i < numPaths; i++) {
    const path = monteCarloData.paths[i]
    const path3D: PathPoint3D[] = []
    
    for (let t = 0; t < path.length; t++) {
      path3D.push({
        x: tGrid[t] || t, // Time step
        y: path[t],       // Capital value
        z: i              // Path index
      })
    }
    
    paths3D.push(path3D)
  }
  
  // Calculate stats from backend data
  const finalPrices = monteCarloData.paths.map(path => path[path.length - 1])
  const stats = {
    meanFinalPrice: monteCarloData.stats.mean_final || finalPrices.reduce((a, b) => a + b, 0) / finalPrices.length,
    maxPrice: monteCarloData.stats.max_final || Math.max(...finalPrices),
    minPrice: monteCarloData.stats.min_final || Math.min(...finalPrices),
    stdDev: monteCarloData.stats.std_final || 0
  }
  
  // Update 3D simulation result
  simulationResult3D.value = {
    paths: paths3D,
    jumps: [], // Backend doesn't provide jump data separately
    stats
  }
  
  // Update playback controls
  if (paths3D.length > 0 && paths3D[0].length > 0) {
    const maxStep = paths3D[0].length - 1
    currentStep3D.value = maxStep
    playbackStep3D.value = maxStep
    cameraPositioned = false // Reset camera positioning
    stopPlay3D() // Stop any ongoing playback
    
    // Initialize 3D visualization if not already initialized
    if (activeMethod.value === 'hjb' && trajectories3DCanvas.value) {
      if (!renderer3D) {
        // Initialize 3D if not already done
        init3DTrajectories().then(() => {
          // After initialization, update with backend data if available
          if (renderer3D) {
            update3DTrajectories()
          }
        })
      } else {
        // Update 3D visualization if already initialized
        update3DTrajectories()
      }
    }
  }
}

// Watch for backend optimization results to update 3D visualization
watch(() => hjbOptimizationResult.value?.monte_carlo, (monteCarloData) => {
  if (monteCarloData && activeMethod.value === 'hjb') {
    update3DVisualizationFromBackend(monteCarloData)
  }
}, { deep: true })

// Watch for trajectory data changes to update 3D visualization
// Only regenerate locally if we don't have backend data
watch([trajectoriesData, hjbParams], () => {
  // Skip local generation if we have backend data
  if (hjbOptimizationResult.value?.monte_carlo) {
    return
  }
  
  if (activeMethod.value === 'hjb' && trajectories3DCanvas.value && renderer3D) {
    // Regenerate 3D simulation when parameters change (only if no backend data)
    const basePrice = initialPrice.value * 10000
    // Используем значение из параметра без ограничений
    const config: SimulationConfig3D = {
      initialPrice: basePrice,
      drift: hjbParams.value.expectedReturn,
      volatility: hjbParams.value.marketVol,
      timeSteps: trajectoriesDays.value,
      numPaths: hjbParams.value.monteCarloTrajectories,
      dt: 1 / 252,
      jumpIntensity: 2.0,
      jumpMean: 0.05,
      jumpSd: 0.15
    }
    
    simulationResult3D.value = runMonteCarlo3D(config)
    const maxStep = simulationResult3D.value.paths[0]?.length || 0
    currentStep3D.value = maxStep
    playbackStep3D.value = maxStep
    cameraPositioned = false // Reset camera positioning
    stopPlay3D() // Stop any ongoing playback
    update3DTrajectories()
  }
}, { deep: true })

// Initialize 3D when switching to HJB method and canvas is ready
watch([activeMethod, trajectories3DCanvas], ([method, canvas]) => {
  if (method === 'hjb' && canvas) {
    // Wait for DOM to be ready
    setTimeout(() => {
      const container = canvas.parentElement as HTMLElement
      if (container && container.clientWidth > 0 && container.clientHeight > 0) {
        init3DTrajectories()
      } else {
        // Retry if container not ready
        setTimeout(() => {
          if (activeMethod.value === 'hjb' && trajectories3DCanvas.value) {
            init3DTrajectories()
          }
        }, 500)
      }
    }, 200)
  } else {
    // Cleanup when switching away
    if (animationId3D) {
      cancelAnimationFrame(animationId3D)
      animationId3D = null
    }
    if (renderer3D) {
      renderer3D.dispose()
      renderer3D = null
    }
    scene3D = null
    camera3D = null
    controls3D = null
    trajectories3DLines.length = 0
    gridObjects.length = 0
    // Cleanup axis labels
    axisLabels.forEach(sprite => {
      if (sprite.material instanceof THREE.SpriteMaterial) {
        sprite.material.map?.dispose()
        sprite.material.dispose()
      }
    })
    axisLabels.length = 0
  }
}, { immediate: true })

// Helper functions
const boxMullerRandomTrajectories = (): number => {
  let u = 0, v = 0;
  while(u === 0) u = Math.random();
  while(v === 0) v = Math.random();
  return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}

const scaleXTrajectories = (t: number): number => {
  const days = trajectoriesDays.value
  return (t / days) * 1000
}

const scaleYTrajectories = (price: number): number => {
  const range = trajectoriesData.maxY - trajectoriesData.minY
  const normalized = (price - trajectoriesData.minY) / range
  return 400 - normalized * 400
}

const generatePathDTrajectories = (path: number[], limit: number): string => {
  if (!path.length) return ''
  const sliced = path.slice(0, limit + 1)
  return 'M ' + sliced.map((p, i) => `${scaleXTrajectories(i).toFixed(1)},${scaleYTrajectories(p).toFixed(1)}`).join(' L ')
}

const generateAreaDTrajectories = (lower: number[], upper: number[], limit: number): string => {
  if (!lower.length) return ''
  const lSliced = lower.slice(0, limit + 1)
  const uSliced = upper.slice(0, limit + 1)
  
  let d = 'M ' + lSliced.map((p, i) => `${scaleXTrajectories(i).toFixed(1)},${scaleYTrajectories(p).toFixed(1)}`).join(' L ')
  for (let i = uSliced.length - 1; i >= 0; i--) {
    d += ` L ${scaleXTrajectories(i).toFixed(1)},${scaleYTrajectories(uSliced[i]).toFixed(1)}`
  }
  d += ' Z'
  return d
}


// HJB Optimization Result
const hjbOptimizationResult = ref<HJBResponse | null>(null)

const runHJBOptimization = async () => {
  isComputing.value = true
  try {
    // Вычисляем mu и cov_matrix из portfolio данных
    const positions = portfolioPositions.value
    const n = positions.length
    
    // Ожидаемые доходности (используем dayChange как приближение)
    // В реальном приложении это должны быть исторические доходности
    const mu = positions.map(pos => {
      // Преобразуем dayChange из процентов в доли и добавляем базовую доходность
      const dailyReturn = pos.dayChange / 100
      const annualReturn = dailyReturn * 252 // Упрощенное преобразование
      return Math.max(0.01, 0.05 + annualReturn) // Минимум 1% годовых
    })
    
    // Ковариационная матрица из корреляционной матрицы
    const corrMatrix = correlationMatrix.value
    const covMatrix: number[][] = []
    
    // Для упрощения используем фиксированную волатильность
    const volatilities = positions.map(() => 0.2) // 20% волатильность
    
    for (let i = 0; i < n; i++) {
      const row: number[] = []
      for (let j = 0; j < n; j++) {
        const corr = corrMatrix[i]?.values[j] || (i === j ? 1 : 0)
        const cov = corr * volatilities[i] * volatilities[j]
        row.push(cov)
      }
      covMatrix.push(row)
    }
    
    // Параметры Монте-Карло
    const monteCarloParams = {
      initial_capital: 1000000,
      horizon_years: hjbParams.value.horizon,
      n_paths: hjbParams.value.monteCarloTrajectories,
      n_steps: trajectoriesDays.value,
      random_seed: 42
    }
    
    // Вызов API
    const result = await optimizeHJBPortfolio({
      mu,
      cov_matrix: covMatrix,
      risk_free_rate: hjbParams.value.riskFreeRate,
      gamma: hjbParams.value.gamma,
      asset_names: positions.map(p => p.symbol),
      monte_carlo: monteCarloParams
    })
    
    hjbOptimizationResult.value = result
    
    // Обновляем траектории если есть результаты Монте-Карло
    if (result.monte_carlo) {
      // Обновляем 2D визуализацию
      trajectoriesData.paths = result.monte_carlo.paths
      // Обновляем displayPaths на основе текущего значения monteCarloTrajectories
      updateDisplayPaths()
      trajectoriesData.medianPath = result.monte_carlo.median_path
      trajectoriesData.q05 = result.monte_carlo.q05_path
      trajectoriesData.q95 = result.monte_carlo.q95_path
      
      // Обновляем масштаб Y
      const allValues = [
        ...result.monte_carlo.q05_path,
        ...result.monte_carlo.q95_path
      ]
      trajectoriesData.minY = Math.min(...allValues) * 0.9
      trajectoriesData.maxY = Math.max(...allValues) * 1.1
      
      playbackStepTrajectories.value = trajectoriesDays.value
      
      // Обновляем 3D визуализацию
      update3DVisualizationFromBackend(result.monte_carlo)
    }
    
    // Обновляем риск-метрики в store для использования в GreekParameters
    const portfolioValue = 2400000 // Базовая стоимость портфеля
    const stats = result.portfolio_stats
    const varMetrics = riskMetricsStore.calculateVaR(portfolioValue, stats.volatility, 0.95, 1)
    const var99Metrics = riskMetricsStore.calculateVaR(portfolioValue, stats.volatility, 0.99, 1)
    
    // Вычисляем Risk Contributions
    const riskContributions = riskMetricsStore.calculateRiskContributions(
      positions.map(p => ({
        symbol: p.symbol,
        allocation: p.allocation,
        notional: p.notional,
        color: p.color
      })),
      stats.volatility,
      correlationMatrix.value,
      portfolioValue
    )
    
    // Обновляем метрики в store
    riskMetricsStore.updateMetrics({
      var95: varMetrics.var,
      var99: var99Metrics.var,
      cvar95: varMetrics.cvar,
      cvar99: var99Metrics.cvar,
      expectedReturn: stats.expected_return,
      volatility: stats.volatility,
      sharpeRatio: stats.sharpe_ratio,
      portfolioBeta: 0.85, // Можно вычислить из беты активов
      riskContributions: riskContributions,
      maxDrawdown: result.monte_carlo?.stats?.mean_max_drawdown || averageMDD.value || 0.124
    })
    
    showToast(
      `HJB оптимизация завершена: Sharpe = ${result.portfolio_stats.sharpe_ratio.toFixed(2)}`,
      'success'
    )
  } catch (error) {
    console.error('HJB Optimization Error:', error)
    showToast(
      `Ошибка оптимизации: ${error instanceof Error ? error.message : 'Unknown error'}`,
      'error'
    )
  } finally {
  isComputing.value = false
  }
}

// ==================== GARCH FILTERING ====================
const garchFilteredAssets = computed(() => {
  return portfolioPositions.value
    .map(asset => ({
      symbol: asset.symbol,
      name: asset.name,
      garchVol: 15 + Math.random() * 20, // Mock GARCH volatility
      passed: true
    }))
    .filter(asset => asset.garchVol <= 30)
    .sort((a, b) => a.garchVol - b.garchVol)
})

const garchFilteredCount = computed(() => garchFilteredAssets.value.length)

// ==================== YIELD REPORT ====================
const yieldReportData = computed(() => {
  return portfolioPositions.value.map(asset => {
    const historicalYield = 0.05 + Math.random() * 0.15 // 5-20%
    const dividendYield = 0.02 + Math.random() * 0.08  // 2-10%
    return {
      symbol: asset.symbol,
      name: asset.name,
      color: asset.color,
      historicalYield,
      dividendYield,
      totalYield: historicalYield + dividendYield
    }
  }).sort((a, b) => b.totalYield - a.totalYield)
})

const avgHistoricalYield = computed(() => {
  if (yieldReportData.value.length === 0) return 0
  return yieldReportData.value.reduce((sum, a) => sum + a.historicalYield, 0) / yieldReportData.value.length
})

const avgDividendYield = computed(() => {
  if (yieldReportData.value.length === 0) return 0
  return yieldReportData.value.reduce((sum, a) => sum + a.dividendYield, 0) / yieldReportData.value.length
})

const avgTotalYield = computed(() => {
  if (yieldReportData.value.length === 0) return 0
  return yieldReportData.value.reduce((sum, a) => sum + a.totalYield, 0) / yieldReportData.value.length
})

// ==================== 3D CORRELATION HEATMAP ====================
const initCorrelation3DHeatmap = async () => {
  try {
    // Проверяем, что активен метод HJB
    if (activeMethod.value !== 'hjb') {
      console.log('Not HJB method, skipping 3D init')
      return
    }
    
    await loadPlotly()
    if (!Plotly) {
      console.error('Plotly not loaded')
      return
    }
    
    const container = document.getElementById('correlation-3d-heatmap')
    if (!container) {
      console.error('Container correlation-3d-heatmap not found')
      return
    }
    
    // Берем все активы для визуализации (акции и облигации)
    const allAssets = [...portfolioPositions.value]
    
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

    Plotly.newPlot(container, traces, layout, config)
    
    // Обработчик hover для кастомного tooltip в правом нижнем углу
    const plotlyContainer = container as any
    
    plotlyContainer.on('plotly_hover', (data: any) => {
      if (data && data.points && data.points.length > 0) {
        for (const point of data.points) {
          if (point.customdata) {
            const asset = Array.isArray(point.customdata) ? point.customdata[0] : point.customdata
            if (asset) {
              hoveredAsset.value = asset
              return
            }
          }
          
          const scatterTraceIndex = traces.length - 1
          if (point.curveNumber === scatterTraceIndex && point.pointNumber !== undefined) {
            const index = point.pointNumber
            if (index >= 0 && index < normalizedPositions.length && normalizedPositions[index]) {
              hoveredAsset.value = normalizedPositions[index].asset
              return
            }
          }
          
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

// Обновляем график при изменении портфеля или метода
watch([portfolioPositions, selectedBank, activeMethod], () => {
  if (activeMethod.value === 'hjb') {
    // Очищаем старый observer
    if (resizeObserver) {
      resizeObserver.disconnect()
      resizeObserver = null
    }
    
    if (portfolioPositions.value.length > 0) {
      setTimeout(() => {
        syncPanelHeights()
        setupResizeObserver()
      }, 400)
    }
  } else {
    // Очищаем observer при переключении на другой метод
    if (resizeObserver) {
      resizeObserver.disconnect()
      resizeObserver = null
    }
  }
}, { deep: false })

// ==================== GARCH CHART ====================
const garchChart = ref<HTMLCanvasElement | null>(null)
const garchData = ref<GARCHResponse | null>(null)
const garchAnimationFrame = ref<number | null>(null)
const garchAnimationStep = ref(0)
const isGARCHAnimating = ref(false)

let resizeObserver: ResizeObserver | null = null

const syncPanelHeights = () => {
  if (activeMethod.value !== 'hjb') return
  
  setTimeout(() => {
    const portfolioPanel = document.querySelector('.portfolio-composition-panel') as HTMLElement
    const correlationPanel = document.querySelector('.correlation-3d-panel') as HTMLElement
    
    if (portfolioPanel && correlationPanel) {
      // Получаем реальные высоты панелей
      const portfolioHeight = portfolioPanel.offsetHeight || portfolioPanel.scrollHeight
      const correlationHeight = correlationPanel.offsetHeight || correlationPanel.scrollHeight
      
      // Используем максимальную высоту, но не больше 500px
      const targetHeight = Math.min(Math.max(portfolioHeight, correlationHeight, 450), 500)
      
      // Устанавливаем одинаковую высоту
      portfolioPanel.style.height = targetHeight + 'px'
      correlationPanel.style.height = targetHeight + 'px'
      
      // Пересчитываем высоту 3D контейнера после синхронизации
      setTimeout(() => {
        initCorrelation3DHeatmap()
      }, 200)
    }
    
    // Синхронизируем высоты блоков отчетов
    const reportPanels = document.querySelectorAll('.report-panel') as NodeListOf<HTMLElement>
    if (reportPanels.length >= 2) {
      const leftPanel = reportPanels[0]
      const rightPanel = reportPanels[1]
      
      if (leftPanel && rightPanel) {
        const leftHeight = leftPanel.offsetHeight || leftPanel.scrollHeight
        const rightHeight = rightPanel.offsetHeight || rightPanel.scrollHeight
        const targetReportHeight = Math.max(leftHeight, rightHeight)
        
        leftPanel.style.height = targetReportHeight + 'px'
        rightPanel.style.height = targetReportHeight + 'px'
      }
    }
  }, 100)
}

// Создаем ResizeObserver для автоматической синхронизации
const setupResizeObserver = () => {
  if (typeof ResizeObserver === 'undefined') return
  
  const portfolioPanel = document.querySelector('.portfolio-composition-panel') as HTMLElement
  const correlationPanel = document.querySelector('.correlation-3d-panel') as HTMLElement
  const reportPanels = document.querySelectorAll('.report-panel') as NodeListOf<HTMLElement>
  
  if (portfolioPanel && correlationPanel) {
    resizeObserver = new ResizeObserver(() => {
      syncPanelHeights()
    })
    
    resizeObserver.observe(portfolioPanel)
    resizeObserver.observe(correlationPanel)
    
    // Отслеживаем изменения высоты блоков отчетов
    reportPanels.forEach(panel => {
      resizeObserver?.observe(panel)
    })
  }
}

// Watch for tab changes to update slider position
watch([paramsTab, weightsTab], async () => {
  await nextTick()
  // Force recalculation of slider position
  // The computed properties will automatically update
}, { immediate: false })

// Watch for window resize to update slider position
const handleResize = () => {
  // Force recalculation by accessing computed properties
  paramsTabSliderStyle.value
  weightsTabSliderStyle.value
}

// Watch portfolio positions to update GARCH data
watch(() => portfolioPositions.value, () => {
  if (garchChart.value) {
    loadGARCHData()
  }
}, { deep: true })

onMounted(() => {
  // Generate initial trajectories
  generateTrajectories()
  
  // Add resize listener for slider position updates
  window.addEventListener('resize', handleResize)
  
  setTimeout(() => {
    if (garchChart.value) {
      initGARCHChart()
      // Добавляем обработчик изменения размера для перерисовки графика
      const resizeObserver = new ResizeObserver(() => {
        if (garchChart.value && garchData.value) {
          // Перерисовываем график с текущими данными
          animateGARCHChart()
        }
      })
      if (garchChart.value.parentElement) {
        resizeObserver.observe(garchChart.value.parentElement)
      }
    }
    // Синхронизируем высоты панелей
    syncPanelHeights()
    // Настраиваем ResizeObserver для автоматической синхронизации
    setupResizeObserver()
    // Инициализируем 3D график только для HJB метода
    if (activeMethod.value === 'hjb') {
      console.log('Initializing 3D chart for HJB method...')
      setTimeout(() => {
        initCorrelation3DHeatmap()
      }, 1000)
      
      // Initialize 3D trajectories visualization
      setTimeout(() => {
        if (trajectories3DCanvas.value && activeMethod.value === 'hjb') {
          console.log('Initializing 3D trajectories visualization...')
          init3DTrajectories()
        }
      }, 1500)
    }
  }, 500)
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (animationFrameTrajectories) {
    cancelAnimationFrame(animationFrameTrajectories)
  }
  stopGARCHAnimation()
  window.removeEventListener('resize', handleResize)
})

// Функция для получения доходностей из портфеля для GARCH
const getPortfolioReturnsForGARCH = (): number[] => {
  const positions = portfolioPositions.value
  if (positions.length === 0) return []
  
  // Генерируем доходности на основе dayChange
  const returns: number[] = []
  for (let i = 0; i < 500; i++) {
    // Используем dayChange как базовую доходность и добавляем случайный шум
    const baseReturn = positions.reduce((sum, pos) => {
      const dailyReturn = (pos.dayChange / 100) / 252 // Преобразуем в дневную доходность
      return sum + dailyReturn * (pos.allocation || 0)
    }, 0)
    
    // Добавляем случайный шум для реалистичности
    const noise = (Math.random() - 0.5) * 0.02
    returns.push(baseReturn + noise)
  }
  
  return returns
}

// Загрузка данных GARCH из бэкенда
const loadGARCHData = async () => {
  try {
    const returns = getPortfolioReturnsForGARCH()
    if (returns.length === 0) return
    
    const result = await calculateGARCH({
      returns,
      omega: 0.000025,
      alpha: 0.082,
      beta: 0.893
    })
    
    garchData.value = result
    garchAnimationStep.value = 0
    startGARCHAnimation()
  } catch (error) {
    console.error('Failed to load GARCH data:', error)
    // Fallback to local generation
    generateLocalGARCHData()
  }
}

// Генерация локальных данных GARCH (fallback)
const generateLocalGARCHData = () => {
  const returns = getPortfolioReturnsForGARCH()
  if (returns.length === 0) {
    // Генерируем случайные данные
    const dataPoints = 500
    const volatilities: number[] = []
    let currentVol = 0.18
    
    for (let i = 0; i < dataPoints; i++) {
      const noise = (Math.random() - 0.5) * 0.05
      currentVol = Math.max(0.05, Math.min(0.5, currentVol * 0.95 + noise))
      volatilities.push(currentVol)
    }
    
    garchData.value = {
      result: {
        variances: volatilities.map(v => v * v),
        volatilities,
        residuals: returns.length > 0 ? returns : Array(dataPoints).fill(0).map(() => (Math.random() - 0.5) * 0.3),
        parameters: {
          omega: 0.000025,
          alpha: 0.082,
          beta: 0.893
        },
        long_term_volatility: 0.182,
        mean_variance: 0.033,
        mean_volatility: 0.18
      },
      status: 'success',
      timestamp: new Date().toISOString()
    }
    garchAnimationStep.value = 0
    startGARCHAnimation()
  }
}

// Анимация GARCH графика
const startGARCHAnimation = () => {
  if (isGARCHAnimating.value) return
  isGARCHAnimating.value = true
  garchAnimationStep.value = 0
  animateGARCHChart()
}

const stopGARCHAnimation = () => {
  isGARCHAnimating.value = false
  if (garchAnimationFrame.value) {
    cancelAnimationFrame(garchAnimationFrame.value)
    garchAnimationFrame.value = null
  }
}

const animateGARCHChart = () => {
  if (!isGARCHAnimating.value || !garchData.value) {
    return
  }
  
  const canvas = document.getElementById('garch-chart') as HTMLCanvasElement
  if (!canvas) {
    stopGARCHAnimation()
    return
  }
  
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    stopGARCHAnimation()
    return
  }
  
  const width = canvas.offsetWidth || 1200
  const height = 200
  canvas.width = width
  canvas.height = height
  
  const volatilities = garchData.value.result.volatilities
  const dataPoints = volatilities.length
  
  // Увеличиваем шаг анимации
  garchAnimationStep.value += 2
  const currentLength = Math.min(garchAnimationStep.value, dataPoints)
  
  // Очищаем canvas
  ctx.fillStyle = 'rgba(20, 22, 28, 0.5)'
  ctx.fillRect(0, 0, width, height)
  
  // Рисуем центральную линию (ноль)
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'
  ctx.lineWidth = 1
  ctx.setLineDash([5, 5])
  ctx.beginPath()
  ctx.moveTo(0, height / 2)
  ctx.lineTo(width, height / 2)
  ctx.stroke()
  ctx.setLineDash([])
  
  if (currentLength > 0) {
    // Нормализуем волатильности для отображения (центрируем вокруг нуля)
    const meanVol = garchData.value.result.mean_volatility
    const maxDev = Math.max(...volatilities.slice(0, currentLength).map(v => Math.abs(v - meanVol))) * 1.2
    const rangeY = maxDev * 2 || 0.1
    
    // Рисуем график волатильности
    ctx.strokeStyle = '#60a5fa'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i < currentLength; i++) {
      const x = (i / (dataPoints - 1)) * width
      const normalizedVol = (volatilities[i] - meanVol) / rangeY
      const y = height / 2 - normalizedVol * (height * 0.8)
      
      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    }
    
    ctx.stroke()
    
    // Добавляем заливку под графиком
    ctx.fillStyle = 'rgba(96, 165, 250, 0.15)'
    if (currentLength > 0) {
      const lastX = ((currentLength - 1) / (dataPoints - 1)) * width
      const lastY = height / 2
      ctx.lineTo(lastX, lastY)
      ctx.lineTo(0, lastY)
      ctx.closePath()
      ctx.fill()
    }
    
    // Рисуем точки данных
    ctx.fillStyle = '#60a5fa'
    for (let i = 0; i < currentLength; i += 10) {
      const x = (i / (dataPoints - 1)) * width
      const normalizedVol = (volatilities[i] - meanVol) / rangeY
      const y = height / 2 - normalizedVol * (height * 0.8)
      ctx.beginPath()
      ctx.arc(x, y, 2, 0, Math.PI * 2)
      ctx.fill()
    }
    
    // Рисуем индикатор текущей позиции
    if (currentLength < dataPoints) {
      const currentX = ((currentLength - 1) / (dataPoints - 1)) * width
      ctx.strokeStyle = '#fbbf24'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(currentX, 0)
      ctx.lineTo(currentX, height)
      ctx.stroke()
    }
  }
  
  // Продолжаем анимацию, если еще не достигли конца
  if (currentLength < dataPoints) {
    garchAnimationFrame.value = requestAnimationFrame(animateGARCHChart)
  } else {
    // Анимация завершена, перезапускаем через 2 секунды
    setTimeout(() => {
      garchAnimationStep.value = 0
      garchAnimationFrame.value = requestAnimationFrame(animateGARCHChart)
    }, 2000)
  }
}

const initGARCHChart = () => {
  const canvas = document.getElementById('garch-chart') as HTMLCanvasElement
  if (!canvas) return
  
  // Загружаем данные из бэкенда
  loadGARCHData()
}

// ==================== CCMV PARAMETERS ====================

const toast = ref<{ show: boolean; message: string; type: 'success' | 'error' | 'info' }>({
  show: false,
  message: '',
  type: 'success'
})

// Clustering result from API
const clusteringResult = computed(() => {
  if (!ccmvOptimizationResult.value) {
    // Fallback to mock data if no result yet
  const positions = portfolioPositions.value
  const numAssets = positions.length
  const sorted = [...positions].sort((a, b) => b.allocation - a.allocation)
  const clusterSize = Math.ceil(sorted.length / 3)
  
  const clusters: Cluster[] = []
  for (let i = 0; i < sorted.length; i += clusterSize) {
    const clusterAssets = sorted.slice(i, i + clusterSize).map(p => p.symbol)
    if (clusterAssets.length > 0) {
      clusters.push({ assets: clusterAssets })
    }
  }
  
  return {
    numClusters: clusters.length || 3,
    numAssets: numAssets,
    clusters: clusters.length > 0 ? clusters : [
      { assets: sorted.slice(0, Math.ceil(sorted.length / 3)).map(p => p.symbol) },
      { assets: sorted.slice(Math.ceil(sorted.length / 3), Math.ceil(sorted.length * 2 / 3)).map(p => p.symbol) },
      { assets: sorted.slice(Math.ceil(sorted.length * 2 / 3)).map(p => p.symbol) }
    ].filter(c => c.assets.length > 0) as Cluster[]
    }
  }
  
  // Use results from API
  const result = ccmvOptimizationResult.value
  return {
    numClusters: result.clusters.length,
    numAssets: result.optimal_weights.length,
    clusters: result.clusters.map(c => ({ assets: c.assets })) as Cluster[]
  }
})

const clusterColors = [
  '#3b82f6', // blue
  '#10b981', // green
  '#f59e0b'  // amber
]

// Parameters
const params = ref({
  Delta: 3,
  bar_w: 0.25,
  gamma: 2.0,
  method: 'delta' as 'delta' | 'alpha'
})

// Current portfolio weights (mock)
const currentWeights = ref({
  SPY: 0.35,
  QQQ: 0.12,
  TLT: 0.25,
  BND: 0.0,
  GLD: 0.18,
  DXY: 0.15
})

// Cluster metrics from API
const clusterMetrics = computed<ClusterMetric[]>(() => {
  if (!ccmvOptimizationResult.value) {
    // Fallback to mock data
    return [
    {
      expectedReturn: 0.085,
      volatility: 0.18,
      avgCorrelation: 0.75,
      deltaK: 2,
      alphaK: params.value.method === 'delta' ? 0.33 : 0.35
    },
    {
      expectedReturn: 0.045,
      volatility: 0.08,
      avgCorrelation: 0.65,
      deltaK: 1,
      alphaK: params.value.method === 'delta' ? 0.33 : 0.30
    },
    {
      expectedReturn: 0.055,
      volatility: 0.12,
      avgCorrelation: 0.40,
      deltaK: 1,
      alphaK: params.value.method === 'delta' ? 0.34 : 0.35
    }
  ]
  }
  
  // Compute metrics from API results
  const result = ccmvOptimizationResult.value
  const corrMatrix = correlationMatrix.value
  
  return result.clusters.map(cluster => {
    // Вычисляем среднюю корреляцию для кластера
    let avgCorr = 0
    let corrCount = 0
    for (let i = 0; i < cluster.asset_indices.length; i++) {
      for (let j = i + 1; j < cluster.asset_indices.length; j++) {
        const idx1 = cluster.asset_indices[i]
        const idx2 = cluster.asset_indices[j]
        const corr = corrMatrix[idx1]?.values[idx2] || 0
        avgCorr += corr
        corrCount++
      }
    }
    avgCorr = corrCount > 0 ? avgCorr / corrCount : 0
    
    // Используем веса кластера для вычисления доходности и волатильности
    // Упрощенный расчет - в реальном приложении нужно использовать mu и Sigma
    const expectedReturn = 0.06  // Примерное значение
    const volatility = 0.15  // Примерное значение
    
    return {
      expectedReturn,
      volatility,
      avgCorrelation: avgCorr,
      deltaK: cluster.delta_k,
      alphaK: cluster.alpha_k
    }
  })
})

// Optimization result from API
const optimizationResult = computed(() => {
  if (!ccmvOptimizationResult.value) {
    // Fallback to current allocation
  const weights: Record<string, number> = {}
  portfolioPositions.value.forEach(pos => {
      weights[pos.symbol] = pos.allocation / 100
    })
    return {
      weights: weights,
      method: params.value.method
    }
  }
  
  // Use results from API
  const result = ccmvOptimizationResult.value
  const weights: Record<string, number> = {}
  
  result.optimal_weights.forEach((weight, idx) => {
    const symbol = portfolioPositions.value[idx]?.symbol
    if (symbol) {
      weights[symbol] = weight
    }
  })
  
  return {
    weights: weights,
    method: result.method
  }
})

// Objective function from API
const objectiveValue = computed(() => {
  if (!ccmvOptimizationResult.value) {
    return 0.0185 - params.value.gamma * 0.0625
  }
  return ccmvOptimizationResult.value.portfolio_stats.objective_value
})

const objectiveComponents = computed(() => {
  if (!ccmvOptimizationResult.value) {
    return {
  variance: 0.0185,
  return: 0.0625
    }
  }
  const stats = ccmvOptimizationResult.value.portfolio_stats
  return {
    variance: stats.volatility * stats.volatility,
    return: stats.expected_return
  }
})

// Portfolio statistics from API
const portfolioStats = computed(() => {
  if (!ccmvOptimizationResult.value) {
    return {
  expectedReturn: 0.0625,
  volatility: 0.136,
  sharpeRatio: (0.0625 - 0.042) / 0.136,
  numPositions: Object.values(optimizationResult.value.weights).filter(w => w > 0.001).length
    }
  }
  
  const result = ccmvOptimizationResult.value
  const stats = result.portfolio_stats
  return {
    expectedReturn: stats.expected_return,
    volatility: stats.volatility,
    sharpeRatio: stats.sharpe_ratio,
    numPositions: result.optimal_weights.filter((w: number) => w > 0.001).length
  }
})

// Cluster allocations from API
const clusterAllocations = computed(() => {
  if (!ccmvOptimizationResult.value) {
  const alloc = clusterMetrics.value.map(m => m.alphaK)
  return alloc.map(a => ({ percentage: a * 100 }))
  }
  
  return ccmvOptimizationResult.value.clusters.map(c => ({
    percentage: c.alpha_k * 100
  }))
})

const getDeltaClass = (delta: number): string => {
  if (Math.abs(delta) < 0.1) return 'neutral'
  return delta > 0 ? 'positive' : 'negative'
}

// Get optimal weight for an asset
const getOptimalWeight = (symbol: string): number => {
  // Get from optimizationResult (now computed from portfolioPositions)
  const weights = optimizationResult.value.weights as Record<string, number>
  const optWeight = weights[symbol]
  if (optWeight !== undefined && optWeight !== null) {
    return optWeight * 100
  }
  // Fallback: use current allocation if optimization result not available
  const currentPos = portfolioPositions.value.find(p => p.symbol === symbol)
  return currentPos?.allocation || 0
}

// Get weight delta (optimal - current)
const getWeightDelta = (pos: any): number => {
  const optimal = getOptimalWeight(pos.symbol)
  return optimal - pos.allocation
}

// Get asset allocation percentage (from API results or current allocation)
const getAssetAllocation = (symbol: string): number | null => {
  // Use optimal weight from API if available
  if (ccmvOptimizationResult.value) {
    const idx = portfolioPositions.value.findIndex(p => p.symbol === symbol)
    if (idx >= 0 && idx < ccmvOptimizationResult.value.optimal_weights.length) {
      const weight = ccmvOptimizationResult.value.optimal_weights[idx]
      return weight > 0.001 ? weight * 100 : null
    }
  }
  
  // Fallback to current allocation
  const pos = portfolioPositions.value.find(p => p.symbol === symbol)
  return pos?.allocation || null
}

// CCMV Optimization Result
const ccmvOptimizationResult = ref<CCMVResponse | null>(null)

const recomputeOptimization = async () => {
  isComputing.value = true
  try {
    const positions = portfolioPositions.value
    const n = positions.length
    
    if (n === 0) {
      throw new Error('Портфель пуст')
    }
    
    // Генерируем матрицу доходностей R (time_steps x num_assets)
    // Для простоты используем симуляцию на основе текущих данных
    const timeSteps = 252  // Один год торговых дней
    const R: number[][] = []
    
    for (let t = 0; t < timeSteps; t++) {
      const row: number[] = []
      positions.forEach(pos => {
        // Генерируем доходность на основе dayChange (волатильности)
        const dailyReturn = (pos.dayChange / 100) / 252 + (Math.random() - 0.5) * (pos.dayChange / 100) / 10
        row.push(dailyReturn)
      })
      R.push(row)
    }
    
    // Вычисляем mu из позиций
    const mu = positions.map(pos => {
      const dailyReturn = pos.dayChange / 100
      const annualReturn = dailyReturn * 252  // Упрощенное преобразование
      return Math.max(0.01, 0.05 + annualReturn)  // Минимум 1% годовых
    })
    
    // Вычисляем ковариационную матрицу из корреляционной матрицы
    const corrMatrix = correlationMatrix.value
    const volatilities = positions.map(() => 0.2)  // 20% волатильность
    
    const covMatrix: number[][] = []
    for (let i = 0; i < n; i++) {
      const row: number[] = []
      for (let j = 0; j < n; j++) {
        const corr = corrMatrix[i]?.values[j] || (i === j ? 1 : 0)
        const cov = corr * volatilities[i] * volatilities[j]
        row.push(cov)
      }
      covMatrix.push(row)
    }
    
    // Вызов API
    const result = await optimizeCCMVPortfolio({
      R,
      mu,
      cov_matrix: covMatrix,
      Delta: params.value.Delta,
      bar_w: params.value.bar_w,
      gamma: params.value.gamma,
      method: params.value.method,
      asset_names: positions.map(p => p.symbol)
    })
    
    ccmvOptimizationResult.value = result
    
    // Обновляем риск-метрики в store для использования в GreekParameters
    const portfolioValue = 2400000 // Базовая стоимость портфеля
    const stats = result.portfolio_stats
    const varMetrics = riskMetricsStore.calculateVaR(portfolioValue, stats.volatility, 0.95, 1)
    const var99Metrics = riskMetricsStore.calculateVaR(portfolioValue, stats.volatility, 0.99, 1)
    
    // Вычисляем Risk Contributions на основе оптимальных весов
    const optimizedPositions = positions.map((pos, idx) => {
      const optimalWeight = result.optimal_weights[idx] || 0
      return {
        symbol: pos.symbol,
        allocation: optimalWeight * 100,
        notional: portfolioValue * optimalWeight,
        color: pos.color
      }
    })
    
    const riskContributions = riskMetricsStore.calculateRiskContributions(
      optimizedPositions,
      stats.volatility,
      correlationMatrix.value,
      portfolioValue
    )
    
    // Обновляем метрики в store
    riskMetricsStore.updateMetrics({
      var95: varMetrics.var,
      var99: var99Metrics.var,
      cvar95: varMetrics.cvar,
      cvar99: var99Metrics.cvar,
      expectedReturn: stats.expected_return,
      volatility: stats.volatility,
      sharpeRatio: stats.sharpe_ratio,
      portfolioBeta: 0.85, // Можно вычислить из беты активов
      riskContributions: riskContributions,
      maxDrawdown: 0.124 // 12.4% - примерное значение
    })
    
    showToast(
      `Оптимизация завершена (${params.value.method === 'delta' ? 'Δ-CCMV' : 'α-CCMV'}). Sharpe = ${result.portfolio_stats.sharpe_ratio.toFixed(2)}`,
      'success'
    )
  } catch (error) {
    console.error('CCMV Optimization Error:', error)
    showToast(
      `Ошибка оптимизации: ${error instanceof Error ? error.message : 'Unknown error'}`,
      'error'
    )
  } finally {
  isComputing.value = false
  }
}

const showToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}
</script>

<style scoped>
/* LAYOUT */
.ccmv-page {
  padding: 24px 32px;
  max-width: 1800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 100vh;
}

/* HERO */
.hero-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding-bottom: 8px;
}

.hero-left h1 {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 16px 0;
  letter-spacing: -0.01em;
}

.hero-meta {
  display: flex;
  gap: 10px;
}

.glass-pill {
  font-size: 12px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 99px;
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  gap: 6px;
  backdrop-filter: blur(4px);
}

.glass-pill strong {
  color: #fff;
  font-weight: 600;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-glass {
  height: 36px;
  padding: 0 16px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  border: 1px solid transparent;
}

.btn-glass.primary {
  background: rgba(255, 255, 255, 0.9);
  color: #000;
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2);
}

.btn-glass.primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(255, 255, 255, 0.3);
}

.btn-glass.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #000;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* MAIN GRID */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  align-items: stretch;
  width: 100%;
}

.col-grid {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.col-grid .glass-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
}

.col-grid .glass-panel .panel-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* GLASS PANEL */
.glass-panel {
  background: rgba(20, 22, 28, 0.5);
  backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.02);
  flex-shrink: 0;
}

.panel-header h3 {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.header-tabs {
  display: flex;
  gap: 6px;
  position: relative;
  padding-bottom: 2px;
}

.tab-btn {
  font-size: 10px;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
  z-index: 2;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.tab-btn.active {
  color: #60a5fa;
  border-color: rgba(59, 130, 246, 0.5);
}

.tab-slider {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 1px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
  z-index: 3;
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.4);
}

.panel-body {
  padding: 16px 20px;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.panel-body.params-body {
  gap: 14px;
}

.panel-body.metrics-table-body {
  padding: 0;
}

.panel-body.metrics-value {
  gap: 16px;
}

.panel-body.weights-body {
  padding: 0;
}

.panel-body.allocation-body {
  gap: 14px;
}

/* CLUSTER INFO */
.cluster-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.label {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.value {
  color: #fff;
  font-weight: 600;
}

.mono {
  font-family: 'SF Mono', monospace;
}

/* CLUSTERS LIST */
.clusters-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cluster-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 11px;
  transition: all 0.2s;
}

.cluster-row:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.15);
}

.cluster-badge {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
  font-size: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.cluster-detail {
  flex: 1;
  min-width: 0;
}

.cluster-label {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2px;
  font-size: 10px;
}

.cluster-assets {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  word-break: break-word;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}

.asset-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  font-size: 9px;
}

.asset-tag-symbol {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.asset-tag-weight {
  color: rgba(255, 255, 255, 0.5);
  font-size: 8px;
}

.cluster-count {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

/* PARAMETERS */
.param-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.param-group label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.param-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.param-input-group input {
  flex: 1;
  height: 28px;
  padding: 0 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #fff;
  font-size: 11px;
  font-family: 'SF Mono', monospace;
  outline: none;
  transition: all 0.2s;
}

.param-input-group input:focus {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.param-hint {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
  flex-shrink: 0;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
}

.radio-item input {
  accent-color: #3b82f6;
}

/* METRICS TABLE */
.metrics-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.metrics-table th {
  text-align: left;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 9px;
  letter-spacing: 0.05em;
}

.metrics-table td {
  padding: 8px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.9);
}

.metrics-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.cluster-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.cluster-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.text-right {
  text-align: right;
}

.font-bold {
  font-weight: 600;
}

/* METRICS CARDS */
.metrics-card {
  gap: 0;
}

.obj-value {
  display: flex;
  align-items: baseline;
  gap: 10px;
  padding: 10px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.obj-value .label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.obj-value .value {
  font-size: 14px;
  font-weight: 700;
  color: #60a5fa;
  font-family: 'SF Mono', monospace;
}

.obj-components {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.component {
  background: rgba(255, 255, 255, 0.02);
  padding: 8px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.comp-label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
}

.comp-value {
  font-size: 11px;
  font-weight: 600;
  font-family: 'SF Mono', monospace;
}

.text-red {
  color: #f87171;
}

.text-green {
  color: #4ade80;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  font-size: 11px;
}

.stat-label {
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.stat-val {
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

/* WEIGHTS */
.weights-comparison {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.weights-table-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

.weights-table-container::-webkit-scrollbar {
  width: 6px;
}

.weights-table-container::-webkit-scrollbar-track {
  background: transparent;
}

.weights-table-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.weights-table-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.weights-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.weights-table thead {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(20, 22, 28, 0.98);
  backdrop-filter: blur(10px);
}

.weights-table th {
  padding: 10px 8px;
  text-align: left;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 9px;
  letter-spacing: 0.05em;
}

.weights-table th.text-right {
  text-align: right;
}

.weights-table tbody tr {
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  transition: background 0.15s;
}

.weights-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.weights-table td {
  padding: 8px;
  color: rgba(255, 255, 255, 0.9);
  vertical-align: middle;
}

.weights-table td.text-right {
  text-align: right;
}

.weights-table .change-pill {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 10px;
}

.weights-table .change-pill.text-green {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
}

.weights-table .change-pill.text-red {
  background: rgba(248, 113, 113, 0.15);
  color: #f87171;
}

.weights-table .change-pill.neutral {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.5);
}

.weights-table .change-pill.positive {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
}

.weights-table .change-pill.negative {
  background: rgba(248, 113, 113, 0.15);
  color: #f87171;
}

.weights-optimal {
  padding: 8px;
}

.weight-chart {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.weight-bar-container {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.weight-bar-info {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 100px;
}

.asset-icon-small {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  flex-shrink: 0;
}

.weight-bar-label {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.weight-bar-bg {
  flex: 1;
  height: 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.weight-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.8), #3b82f6);
  border-radius: 4px;
  transition: width 0.3s ease;
  min-width: 2px;
}

.weight-bar-value {
  min-width: 50px;
  text-align: right;
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.weight-bar-value {
  width: 45px;
  text-align: right;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-family: 'SF Mono', monospace;
}

/* ALLOCATION */
.allocation-chart {
  display: flex;
  height: 80px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.alloc-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.alloc-label {
  line-height: 1.1;
  text-align: center;
}

.allocation-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.alloc-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px;
  font-size: 10px;
}

.alloc-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.alloc-name {
  flex: 1;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.alloc-pct {
  color: rgba(255, 255, 255, 0.5);
  font-size: 9px;
}

/* TOAST */
.toast-notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 14px 20px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  max-width: 320px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.toast-success {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
  border-color: rgba(74, 222, 128, 0.3);
}

.toast-error {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.3);
}

.toast-info {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
  border-color: rgba(96, 165, 250, 0.3);
}

/* TRANSITIONS */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.slide-up-enter-from {
  transform: translateY(20px);
  opacity: 0;
}

.slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

/* ==================== METHOD SELECTOR ==================== */
.method-selector {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.method-tab {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: rgba(20, 22, 28, 0.5);
  backdrop-filter: blur(30px);
  border: 2px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
  text-align: left;
}

.method-tab:hover {
  background: rgba(30, 32, 40, 0.6);
  border-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.method-tab.active {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.5);
  box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.method-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s;
}

.method-icon.hjb {
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: #60a5fa;
}

.method-icon.ccmv {
  background: rgba(34, 197, 94, 0.2);
  border: 1px solid rgba(34, 197, 94, 0.4);
  color: #4ade80;
}

.method-tab.active .method-icon.hjb {
  background: rgba(59, 130, 246, 0.3);
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

.method-tab.active .method-icon.ccmv {
  background: rgba(34, 197, 94, 0.3);
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
}

.method-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.method-title {
  font-size: 16px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
}

.method-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.method-tab.active .method-title {
  color: #fff;
}

.method-tab.active .method-subtitle {
  color: rgba(255, 255, 255, 0.7);
}

/* ==================== HJB SPECIFIC STYLES ==================== */
.hjb-grid {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr);
  align-items: stretch;
  gap: 8px;
  margin-top: 8px;
}

.hjb-reports-grid {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  align-items: stretch;
  gap: 8px;
  margin-top: 8px;
}

.hjb-grid-bottom {
  grid-template-columns: minmax(0, 1fr);
  align-items: stretch;
  gap: 8px;
  margin-top: 8px;
}

.col-report-left,
.col-report-right {
  display: flex;
  flex-direction: column;
}

.report-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.col-portfolio-wide {
  grid-column: 1 / 3;
  display: flex;
  flex-direction: column;
  height: 450px;
}

.col-3d-right {
  grid-column: 3;
  display: flex;
  flex-direction: column;
  height: 450px;
  gap: 16px;
  justify-content: flex-start;
}

.col-3d-right .glass-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.col-3d-right .glass-panel:first-child {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.col-3d-right .glass-panel:last-child {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
}

.col-3d-right .glass-panel:only-child {
  flex: 1 1 auto;
  height: 100%;
}

.col-3d-right .glass-panel:only-child .panel-body {
  flex: 1;
}

.col-3d-right .glass-panel:last-child:not(:only-child) .panel-body {
  flex: 0 0 auto;
}

.col-3d-right .glass-panel .panel-body {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.col-3d-right .glass-panel:first-child .panel-body {
  flex: 1;
  overflow: visible;
}

.col-3d-right .glass-panel .panel-body.params-body {
  overflow: visible;
  gap: 14px;
}

.col-3d-right .glass-panel .panel-body:not(.params-body) {
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

.col-3d-right .glass-panel .panel-body:not(.params-body)::-webkit-scrollbar {
  width: 6px;
}

.col-3d-right .glass-panel .panel-body:not(.params-body)::-webkit-scrollbar-track {
  background: transparent;
}

.col-3d-right .glass-panel .panel-body:not(.params-body)::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.col-3d-right .glass-panel .panel-body:not(.params-body)::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.portfolio-composition-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.col-portfolio-wide > .glass-panel:not(.portfolio-composition-panel) {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.correlation-3d-panel {
  display: flex;
  flex-direction: column;
  height: 450px;
  margin-bottom: 8px;
}

.col-left-bottom,
.col-right-bottom {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.portfolio-composition-panel .panel-body,
.correlation-3d-panel .panel-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.correlation-3d-body {
  padding: 8px 10px 0 10px !important;
  position: relative;
  margin-bottom: 0;
}

.static-3d-plot {
  width: 100% !important;
  flex: 1 !important;
  min-height: 500px !important;
  height: 500px !important;
  background: transparent;
  border-radius: 8px;
  margin-bottom: 0;
}

/* HJB Parameters Row (Horizontal) */
.hjb-params-row {
  margin-bottom: 8px;
}

.hjb-params-row .panel-body {
  flex-direction: row !important;
}

.params-row-body {
  padding: 16px 20px;
  display: flex !important;
  flex-direction: row !important;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: nowrap;
}

.param-group-horizontal {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.param-group-horizontal label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  white-space: nowrap;
  line-height: 1.2;
}

.param-group-horizontal .param-input-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.param-group-horizontal .param-input-group input {
  flex: 1;
  min-width: 70px;
  width: 100%;
  height: 32px;
  padding: 0 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #fff;
  font-size: 11px;
  font-family: 'SF Mono', monospace;
  outline: none;
  transition: all 0.2s;
}

.param-group-horizontal .param-input-group input:focus {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.param-group-horizontal .param-hint {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
  flex-shrink: 0;
}

.theory-panel .panel-body {
  padding: 20px;
}

.theory-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.theory-text {
  font-size: 12px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.theory-text strong {
  color: #60a5fa;
}

.formula-box {
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.formula-box.highlight {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
}

.formula-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
  display: block;
}

.formula {
  font-size: 18px;
  font-family: 'Times New Roman', serif;
  font-style: italic;
  color: #fff;
  text-align: center;
}

.formula-box.highlight .formula {
  color: #93c5fd;
}

/* HJB Result Card */
.hjb-result-card {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 14px;
}

.result-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.result-value {
  font-size: 32px;
  font-weight: 700;
  color: #60a5fa;
  font-family: 'SF Mono', monospace;
}

.result-breakdown {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.breakdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.breakdown-label {
  width: 120px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  flex-shrink: 0;
}

.breakdown-bar {
  flex: 1;
  height: 24px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.bar-fill {
  height: 100%;
  transition: width 0.5s ease;
}

.bar-fill.risky {
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.8), #3b82f6);
}

.bar-fill.safe {
  background: linear-gradient(90deg, rgba(34, 197, 94, 0.8), #4ade80);
}

.breakdown-value {
  width: 60px;
  text-align: right;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  font-family: 'SF Mono', monospace;
}

/* Sensitivity Chart */
.sensitivity-chart {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 120px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.sensitivity-bar {
  flex: 1;
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.8), rgba(59, 130, 246, 0.3));
  border-radius: 4px 4px 0 0;
  min-height: 8px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  transition: all 0.3s;
  cursor: pointer;
}

.sensitivity-bar:hover {
  background: linear-gradient(180deg, #3b82f6, rgba(59, 130, 246, 0.5));
}

.sensitivity-label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.7);
  padding-bottom: 4px;
  font-weight: 600;
}

.sensitivity-legend {
  text-align: center;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 8px;
}

/* Strategy Info */
.strategy-info {
  margin-bottom: 16px;
}

.info-note {
  font-size: 11px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border-left: 3px solid rgba(168, 85, 247, 0.5);
}

.info-note strong {
  color: #60a5fa;
}

/* Timeline */
.timeline-visualization {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding-left: 12px;
  border-left: 2px solid rgba(59, 130, 246, 0.3);
}

.timeline-point {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  position: relative;
}

.point-marker {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #3b82f6;
  position: absolute;
  left: -18px;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
}

.point-info {
  display: flex;
  justify-content: space-between;
  flex: 1;
  font-size: 11px;
}

.point-time {
  color: rgba(255, 255, 255, 0.5);
}

.point-value {
  color: #60a5fa;
  font-weight: 600;
  font-family: 'SF Mono', monospace;
}

/* Constraints */
.constraints-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.constraint-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
}

.constraint-icon {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  flex-shrink: 0;
}

.constraint-icon.warning {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
}

.constraint-icon.info {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
}

.constraint-icon.success {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

/* ==================== PORTFOLIO TABLE ==================== */
.portfolio-table-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  position: relative;
  height: 100%;
}

.portfolio-table-wrapper {
  flex: 1 1 auto;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 200px;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

.portfolio-table-wrapper::-webkit-scrollbar {
  width: 6px;
}

.portfolio-table-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.portfolio-table-wrapper::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.portfolio-table-wrapper::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.portfolio-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.portfolio-table thead {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(20, 22, 28, 0.98);
  backdrop-filter: blur(10px);
}

.portfolio-table th {
  text-align: left;
  padding: 10px 8px;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 9px;
  letter-spacing: 0.05em;
}

.portfolio-table td {
  padding: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.9);
}

.portfolio-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.asset-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.asset-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 10px;
  color: #fff;
  flex-shrink: 0;
}

.asset-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.symbol {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  font-size: 11px;
}

.name {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.5);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.change-pill {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
}

.portfolio-table-footer {
  padding: 12px;
  text-align: center;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  background: rgba(20, 22, 28, 0.95);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  position: sticky;
  bottom: 0;
  z-index: 10;
  backdrop-filter: blur(10px);
  flex-shrink: 0;
}

.portfolio-table-footer strong {
  color: #fff;
  font-weight: 600;
}

.opacity-80 {
  opacity: 0.8;
}

/* ==================== CONSTRAINTS TABLE ==================== */
.constraints-table {
  width: 100%;
  border-collapse: collapse;
}

.constraints-table td {
  padding: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.constraint-name {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.constraint-value {
  text-align: right;
}

.constraint-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  font-family: 'SF Mono', monospace;
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.constraint-badge.active {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
  border-color: rgba(34, 197, 94, 0.3);
}

/* ==================== 3D CORRELATION HEATMAP ==================== */
.panel-badge {
  font-size: 9px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.section-description {
  font-size: 11px;
  line-height: 1.4;
  color: rgba(255, 255, 255, 0.7);
}

/* 3D Correlation Heatmap - Static Plot */
.static-3d-plot {
  width: 100% !important;
  height: 100% !important;
  min-height: 500px !important;
  min-width: 300px !important;
  position: relative;
  display: block;
}

.static-3d-plot .plotly {
  cursor: default !important;
  width: 100% !important;
  height: 100% !important;
}

.static-3d-plot .plotly .modebar {
  display: none !important;
}

.static-3d-plot .plotly .scene-container {
  pointer-events: auto !important;
  touch-action: none !important;
  width: 100% !important;
  height: 100% !important;
}

.static-3d-plot .plotly .scene {
  width: 100% !important;
  height: 100% !important;
}

.static-3d-plot .plotly .scene .scene-controls {
  display: none !important;
}

.correlation-3d-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  position: relative;
  width: 100%;
  height: 100%;
}

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

.tooltip-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
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

/* ==================== GARCH CHART ==================== */
.garch-full-width {
  width: 100%;
  margin-top: 8px;
  margin-bottom: 8px;
}

.garch-container-full {
  display: flex;
  flex-direction: row;
  gap: 24px;
  align-items: flex-start;
}

.garch-chart-placeholder-full {
  flex: 1;
  height: 200px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
  min-width: 0;
}

.garch-params-full {
  flex-shrink: 0;
  width: 300px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.garch-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.garch-chart-placeholder {
  height: 200px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

#garch-chart {
  width: 100%;
  height: 100%;
  display: block;
}

.garch-params {
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.garch-param-row {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 12px;
  font-family: 'SF Mono', monospace;
}

.param-name {
  color: rgba(255, 255, 255, 0.5);
  margin-right: 8px;
}

.garch-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.garch-stat {
  display: flex;
  justify-content: space-between;
  padding: 6px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
  font-size: 10px;
}

.stat-label {
  color: rgba(255, 255, 255, 0.6);
}

.stat-val {
  color: #fff;
  font-weight: 600;
  font-family: 'SF Mono', monospace;
}

/* ==================== FILTERING REPORT ==================== */
.filtering-report {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.summary-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
}

.summary-value {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  font-family: 'SF Mono', monospace;
}

.filtering-criteria {
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.criteria-title {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}

.criteria-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.criteria-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
}

.criteria-check {
  color: #4ade80;
  font-weight: 700;
}

.filtered-assets {
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.filtered-title {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}

.filtered-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 150px;
  overflow-y: auto;
}

.filtered-asset {
  display: flex;
  justify-content: space-between;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
  font-size: 10px;
}

.asset-symbol {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.asset-garch {
  color: rgba(255, 255, 255, 0.6);
  font-family: 'SF Mono', monospace;
}

/* ==================== YIELD REPORT ==================== */
.yield-report {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.yield-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

.yield-table th {
  text-align: left;
  padding: 8px 6px;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  font-size: 9px;
}

.yield-table td {
  padding: 6px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.9);
}

.yield-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.yield-asset {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.yield-summary {
  padding: 12px;
  margin-top: 16px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.yield-summary-item {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
}

/* METRICS SUMMARY */
.metrics-summary-panel {
  margin-top: 24px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.metric-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: all 0.2s;
}

.metric-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
}

.metric-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}

.metric-value {
  font-size: 20px;
  font-weight: 700;
  font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
  color: rgba(255, 255, 255, 0.9);
}

.metric-value.text-green {
  color: #34d399;
}

.metric-value.text-red {
  color: #f87171;
}

/* RESPONSIVE */
@media (max-width: 1400px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .hjb-grid {
    grid-template-columns: 1fr;
  }
  
  .hjb-grid-bottom {
    grid-template-columns: 1fr;
  }
  
  .hjb-reports-grid {
    grid-template-columns: 1fr;
  }
  
  .col-portfolio-wide,
  .col-3d-right,
  .col-report-left,
  .col-report-right,
  .col-grid {
    grid-column: 1;
  }
  
  .method-selector {
    flex-direction: column;
  }
  
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .ccmv-page {
    padding: 16px;
    gap: 20px;
  }

  .hero-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .method-tab {
    padding: 16px;
  }
  
  .method-icon {
    width: 40px;
    height: 40px;
  }
  
  .method-title {
    font-size: 14px;
  }

  .params-row-body {
    flex-direction: column;
    gap: 16px;
  }

  .param-group-horizontal {
    min-width: 100%;
  }

  .garch-container-full {
    flex-direction: column;
  }

  .garch-params-full {
    width: 100%;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .metric-value {
    font-size: 18px;
  }
}

/* ==================== MONTE CARLO TRAJECTORIES ==================== */
.trajectories-panel {
  margin-top: 16px;
}

.trajectories-header-left,
.trajectories-3d-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trajectories-header-left h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.live-badge {
  font-size: 10px;
  color: #ef4444;
  font-weight: 700;
  animation: blink 1.5s infinite;
}

@keyframes blink {
  50% {
    opacity: 0.5;
  }
}

.playback-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(0, 0, 0, 0.3);
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.icon-btn {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  border-radius: 50%;
  transition: 0.2s;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.timeline-wrapper {
  position: relative;
  width: 140px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  display: flex;
  align-items: center;
}

.timeline-slider {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 2;
  margin: 0;
}

.timeline-track {
  height: 100%;
  background: #3b82f6;
  border-radius: 2px;
  pointer-events: none;
}

.playback-day-info {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.playback-day-info .mono {
  font-family: "SF Mono", monospace;
  color: #60a5fa;
  font-weight: 600;
}

.trajectories-chart-container {
  position: relative;
  width: 100%;
  height: 400px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  overflow: hidden;
}

.trajectories-svg {
  width: 100%;
  height: 100%;
}

.trajectories-3d-container {
  position: relative;
  width: 100%;
  height: 600px;
  min-height: 600px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  overflow: hidden;
}

.trajectories-3d-canvas {
  width: 100%;
  height: 100%;
  display: block;
  cursor: grab;
}

.trajectories-3d-canvas:active {
  cursor: grabbing;
}

.trajectories-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.3);
  font-size: 13px;
}
</style>