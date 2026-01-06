<!-- src/views/PortfolioView.vue - FINAL VERSION -->
<template>
  <div class="portfolio-page">
    
    <!-- ⚠️  LATENT VOLATILITY SHIFT ALERT BANNER -->
    <transition name="slide-down">
      <div v-if="latentVolAlert.isActive" class="alert-banner" :class="'alert-' + latentVolAlert.severity">
        <div class="alert-content">
          <span class="alert-icon">{{ latentVolAlert.severity === 'warning' ? '⚠️ ' : '🔴 ' }}</span>
          <div class="alert-text">
            <p class="alert-title">{{ latentVolAlert.title }}</p>
            <p class="alert-message">{{ latentVolAlert.message }}</p>
          </div>
        </div>
        <button class="alert-close" @click="latentVolAlert.isActive = false">×</button>
      </div>
    </transition>

    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-left">
        <h1>Управление портфелем</h1>
        <div class="hero-meta">
          <span class="glass-pill">Стратегия: <strong>Multi-Asset</strong></span>
          <span class="glass-pill">Ребалансировка: <strong>Monthly</strong></span>
          <span class="glass-pill risk-aggressive">
            <span class="status-dot"></span>
            Риск: Агрессивный
          </span>
        </div>
      </div>
      <div class="hero-actions">
        <div class="last-update">Обновлено: <span class="mono">{{ lastUpdate }}</span></div>
        <button class="btn-glass primary" @click="recalcPortfolio" :disabled="isRecalcing">
          <svg v-if="!isRecalcing" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          <span v-else class="spinner"></span>
          {{ isRecalcing ? 'Пересчет...' : 'Пересчитать' }}
        </button>
        <button class="btn-glass outline" @click="exportPdf">
          <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
          Экспорт PDF
        </button>
      </div>
    </div>

    <!-- KPI Grid -->
    <div class="kpi-grid">
      <div class="glass-card kpi-card glow-green">
        <div class="kpi-header">
          <span class="kpi-label">Total P&L</span>
          <div class="trend-badge positive">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4"><path d="M18 15l-6-6-6 6"/></svg>
            12.4%
          </div>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-gradient-green">452,109 <small>RUB</small></div>
          <div class="kpi-sub">NAV: 3.64M</div>
        </div>
      </div>

      <div class="glass-card kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">VaR 95%</span>
          <div class="trend-badge negative">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4"><path d="M6 9l6 6 6-6"/></svg>
            1.2%
          </div>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-white">2.45%</div>
          <div class="kpi-sub">Daily Risk</div>
        </div>
      </div>

      <div class="glass-card kpi-card glow-blue">
        <div class="kpi-header">
          <span class="kpi-label">Sharpe Ratio</span>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-gradient-blue">1.85</div>
          <div class="kpi-sub">Risk-Free Rate: 4.2%</div>
        </div>
      </div>

      <div class="glass-card kpi-card">
        <div class="kpi-header">
          <span class="kpi-label">Diversification</span>
        </div>
        <div class="kpi-content">
          <div class="kpi-value text-white">0.34</div>
          <div class="kpi-sub">Correlation Coeff</div>
        </div>
      </div>
    </div>

    <!-- WAVE_σ.9 REGIME INDICATOR -->
    <div class="regime-indicator-compact">
      <div class="regime-badge" :class="'regime-' + waveRegime.currentRegime.toLowerCase()">
        <span class="regime-dot"></span>
        <span class="regime-text">{{ waveRegime.currentRegime }}</span>
      </div>
      <div class="regime-details">
        <span>Position Size: <strong>{{ waveRegime.positionSize }}%</strong></span>
        <span>λ (Risk Aversion): <strong>{{ waveRegime.lambda }}</strong></span>
        <span>Jaggedness: <strong>{{ waveRegime.jaggedness.toFixed(2) }}</strong></span>
      </div>
    </div>

    <!-- Main Dashboard Grid -->
    <div class="dashboard-grid">
      
      <!-- LEFT COLUMN -->
      <div class="col-main">
        
        <!-- Positions Table -->
        <div class="glass-panel">
          <div class="panel-header">
            <h3>Открытые позиции</h3>
            <div class="search-sm">
               <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
               <input type="text" placeholder="Фильтр..." class="input-reset" @input="filterPositions">
            </div>
          </div>
          <div class="panel-body p-0">
             <div class="table-container">
               <table class="glass-table">
                 <thead>
                   <tr>
                     <th>Инструмент</th>
                     <th class="text-right">Цена</th>
                     <th class="text-right">День %</th>
                     <th class="text-right">Позиция</th>
                     <th class="text-right">Вес</th>
                     <th class="text-right">Таргет</th>
                     <th class="text-right">Дрифт</th>
                   </tr>
                 </thead>
                 <tbody>
                   <tr 
                      v-for="pos in filteredPositions" 
                      :key="pos.symbol"
                      @click="selectAsset(pos)"
                      :class="{ active: selectedAsset?.symbol === pos.symbol }"
                   >
                     <td>
                       <div class="asset-cell">
                         <div class="asset-icon" :style="{ background: pos.color }">{{ pos.symbol[0] }}</div>
                         <div class="asset-info">
                           <span class="symbol">{{ pos.symbol }}</span>
                           <span class="name">{{ pos.name }}</span>
                         </div>
                       </div>
                     </td>
                     <td class="text-right mono">${{ pos.price }}</td>
                     <td class="text-right mono">
                       <span :class="['change-pill', pos.dayChange > 0 ? 'text-green' : 'text-red']">{{ pos.dayChange > 0 ? '+' : '' }}{{ pos.dayChange }}%</span>
                     </td>
                     <td class="text-right mono opacity-80">${{ (pos.notional / 1000).toFixed(1) }}k</td>
                     <td class="text-right mono font-bold">{{ pos.allocation }}%</td>
                     <td class="text-right mono opacity-50">{{ pos.targetAllocation }}%</td>
                     <td class="text-right">
                        <div :class="['drift-val', getDriftClass(pos)]">{{ (pos.allocation - pos.targetAllocation).toFixed(1) }}%</div>
                     </td>
                   </tr>
                 </tbody>
               </table>
             </div>
          </div>
        </div>

        <!-- Charts Row -->
        <div class="charts-row-two-col">
            <!-- Correlation Matrix -->
            <div class="glass-panel">
               <div class="panel-header">
                  <h3>Матрица Корреляций</h3>
               </div>
               <div class="panel-body heatmap-body">
                  <div class="heatmap-wrapper">
                     <div class="heatmap-header-row">
                        <div class="heatmap-empty"></div>
                        <div v-for="col in correlationMatrix" :key="col.label" class="heatmap-th">{{ col.label }}</div>
                     </div>
                     <div class="heatmap-row" v-for="(row, r) in correlationMatrix" :key="r">
                        <div class="heatmap-rh">{{ row.label }}</div>
                        <div 
                          class="heatmap-cell" 
                          v-for="(val, c) in row.values" 
                          :key="c"
                          :style="{ backgroundColor: getHeatmapColor(val) }"
                        >
                          {{ val === 1 ? '1.0' : val.toFixed(2) }}
                        </div>
                     </div>
                  </div>
               </div>
            </div>
            
            <!-- Market Map -->
            <div class="glass-panel">
               <div class="panel-header">
                  <h3>Тепловая карта</h3>
               </div>
               <div class="panel-body" style="min-height: 280px; padding: 0;">
                  <div class="treemap-tall">
                     <div 
                        v-for="pos in positions" 
                        :key="pos.symbol"
                        class="treemap-item"
                        :style="{ 
                           flexGrow: pos.allocation, 
                           backgroundColor: pos.dayChange > 0 ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)'
                        }"
                     >
                        <span class="tm-symbol">{{ pos.symbol }}</span>
                        <span class="tm-val">{{ pos.dayChange > 0 ? '+' : '' }}{{ pos.dayChange }}%</span>
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
        <div class="glass-panel inspector-card" v-if="selectedAsset">
          <div class="panel-header">
             <div class="inspector-header-top">
                 <div class="asset-lg-icon" :style="{ background: selectedAsset.color }">{{ selectedAsset.symbol[0] }}</div>
                 <div class="inspector-title">
                     <h2>{{ selectedAsset.symbol }}</h2>
                     <span>{{ selectedAsset.name }}</span>
                 </div>
             </div>
             <div class="badge-glass">Equity</div>
          </div>
          <div class="panel-body">
             <div class="mini-chart-container">
                 <div class="chart-bars">
                    <div 
                       v-for="(h, i) in getMockHistogram(selectedAsset.symbol)" 
                       :key="i"
                       class="chart-bar"
                       :style="{ height: h + '%', backgroundColor: i > 15 ? '#4ade80' : 'rgba(255,255,255,0.2)' }"
                    ></div>
                 </div>
                 <div class="chart-meta">
                    <span class="active">1D</span><span>1W</span><span>1M</span><span>3M</span><span>1Y</span>
                 </div>
             </div>

             <div class="inspector-grid">
                <div class="metric-cell">
                   <label>Return</label>
                   <span class="text-green">+14.2%</span>
                </div>
                <div class="metric-cell">
                   <label>Volatility</label>
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
             
             <button class="btn-glass primary w-full mt-3" @click="openAnalysis">Открыть анализ</button>
          </div>
        </div>
        </transition>

        <!-- REGIME-AWARE OPTIMIZER -->
        <div class="glass-panel optimizer-card">
           <div class="panel-header">
              <h3>⚙️ Оптимизатор (Regime-Aware)</h3>
              <button class="btn-icon-xs" @click="resetOptimizer" title="Сброс">↺</button>
           </div>
           <div class="panel-body-optimizer">
              
              <!-- Regime Info -->
              <div class="regime-info-box" :class="'regime-' + waveRegime.currentRegime.toLowerCase()">
                 <p class="regime-info-label">Текущий режим</p>
                 <p class="regime-info-value">{{ waveRegime.currentRegime }}</p>
                 <p class="regime-info-sub">λ автоматически: {{ waveRegime.lambda }}</p>
              </div>

              <div class="control-group compact">
                 <label>Модель</label>
                 <div class="custom-select">
                    <select v-model="optimizer.model">
                       <option>Mean-Variance</option>
                       <option>Black-Litterman</option>
                       <option>Risk Parity</option>
                    </select>
                    <svg class="chevron" width="10" height="6" viewBox="0 0 10 6" fill="none" stroke="currentColor"><path d="M1 1L5 5L9 1" stroke-width="1.5"/></svg>
                 </div>
              </div>
              
              <div class="control-group compact">
                 <div class="flex justify-between mb-1">
                    <label>Веса (%)</label>
                 </div>
                 <div class="range-inputs-row">
                    <div class="glass-input-wrapper">
                       <input type="number" v-model.number="optimizer.minWeight" @change="validateWeights">
                       <span>%</span>
                    </div>
                    <div class="dash">-</div>
                    <div class="glass-input-wrapper">
                       <input type="number" v-model.number="optimizer.maxWeight" @change="validateWeights">
                       <span>%</span>
                    </div>
                 </div>
              </div>

              <div class="control-group compact">
                 <div class="flex justify-between mb-1">
                    <label>Target Vol</label>
                    <span class="val-highlight">{{ optimizer.targetVol }}%</span>
                 </div>
                 <input type="range" class="ios-slider-sm" min="5" max="30" v-model.number="optimizer.targetVol">
              </div>
              
              <div class="control-group toggle-row compact">
                 <label style="margin: 0; flex: 1;">Ребалансировка</label>
                 <label class="ios-toggle-sm" style="margin: 0; flex-shrink: 0;">
                    <input type="checkbox" v-model="optimizer.rebalance">
                    <span class="slider"></span>
                 </label>
              </div>

              <div class="flex-spacer"></div>

              <button class="btn-glass primary w-full compact" @click="calculateOptimization" :disabled="isOptimizing">
                <span v-if="!isOptimizing">Рассчитать</span>
                <span v-else class="flex-center"><span class="spinner-sm"></span> Расчет...</span>
              </button>

              <!-- Info -->
              <div style="font-size: 10px; color: rgba(255,255,255,0.4); margin-top: 8px; text-align: center; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px;">
                 Веса автоматически подстраиваются на основе {{ waveRegime.currentRegime === 'TRENDING' ? 'тренда' : 'боковика' }}
              </div>
           </div>
        </div>

        <!-- Combined Metrics with Tournament Tab -->
        <div class="glass-panel combined-metrics">
           <div class="combined-tabs">
              <button 
                 :class="['tab-button', { active: activeMetricsTab === 'risk' }]"
                 @click="activeMetricsTab = 'risk'"
              >
                 Риск
              </button>
              <button 
                 :class="['tab-button', { active: activeMetricsTab === 'stats' }]"
                 @click="activeMetricsTab = 'stats'"
              >
                 Статистика
              </button>
              <button 
                 :class="['tab-button', { active: activeMetricsTab === 'tournament' }]"
                 @click="activeMetricsTab = 'tournament'"
              >
                 🏆 Турнир
              </button>
           </div>

           <!-- Risk Tab -->
           <div class="tab-content" v-show="activeMetricsTab === 'risk'">
              <div class="metric-row">
                 <div class="metric-label">
                    <span>Expected Shortfall</span>
                    <span class="meta-hint">CVaR 95%</span>
                 </div>
                 <div class="metric-value text-red">-3.78%</div>
              </div>
              <div class="metric-row">
                 <div class="metric-label">
                    <span>Max Drawdown</span>
                    <span class="meta-hint">Peak-to-Trough</span>
                 </div>
                 <div class="metric-value text-red">-18.24%</div>
              </div>
              <div class="metric-row">
                 <div class="metric-label">
                    <span>Calmar Ratio</span>
                    <span class="meta-hint">Return / Max DD</span>
                 </div>
                 <div class="metric-value text-white">1.41</div>
              </div>
              <div class="metric-row">
                 <div class="metric-label">
                    <span>Rolling Vol (30D)</span>
                    <span class="meta-hint">Annualized</span>
                 </div>
                 <div class="metric-value text-white">12.8%</div>
              </div>
           </div>

           <!-- Stats Tab -->
           <div class="tab-content" v-show="activeMetricsTab === 'stats'">
              <div class="stats-grid">
                 <div class="stat-item">
                    <span class="stat-label">YTD Return</span>
                    <span class="stat-value text-green">+8.42%</span>
                 </div>
                 <div class="stat-item">
                    <span class="stat-label">Win Rate</span>
                    <span class="stat-value text-green">58.3%</span>
                 </div>
                 <div class="stat-item">
                    <span class="stat-label">Profit Factor</span>
                    <span class="stat-value text-white">1.87x</span>
                 </div>
                 <div class="stat-item">
                    <span class="stat-label">Avg Trade</span>
                    <span class="stat-value text-white">+0.34%</span>
                 </div>
              </div>
           </div>

           <!-- Tournament Tab -->
           <div class="tab-content" v-show="activeMetricsTab === 'tournament'">
              <div class="tournament-mini">
                 <div style="font-size: 10px; color: rgba(255,255,255,0.5); margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    Рейтинг моделей (20-летний бэктест)
                 </div>
                 <div v-for="(model, i) in tournamentResults" :key="i" class="tournament-row">
                    <span class="tournament-rank">{{ i + 1 }}</span>
                    <span class="tournament-name">{{ model.name }}</span>
                    <span class="tournament-sharpe">{{ model.sharpe.toFixed(2) }}</span>
                 </div>
              </div>
              <router-link to="/tournament" class="btn-glass primary w-full mt-3" style="text-decoration: none; text-align: center; display: inline-flex; align-items: center; justify-content: center;">
                 Открыть полный турнир →
              </router-link>
           </div>
        </div>

      </aside>
    </div>

    <!-- 3️⃣ WAVE_σ.9 SURFACE -->
    <div class="glass-panel">
       <div class="panel-header">
          <h3>🌊 WAVE_σ.9 Momentum-Volatility Surface</h3>
          <span class="panel-badge">Режимная индикация</span>
       </div>
       <div class="panel-body" style="padding-top: 16px;">
          <p class="section-description" style="margin-bottom: 0; padding: 8px 12px; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; background: rgba(0,0,0,0.2); font-size: 12px; line-height: 1.5;">
             3D поверхность показывает взаимосвязь между импульсом (Momentum), волатильностью (Volatility) и неровностью (Jaggedness). 
             <br><strong>Цветовая карта:</strong> 
             <span style="color: #3b82f6;">🔵 Синий</span> = низкий риск (безопасная зона), 
             <span style="color: #10b981;">🟢 Зеленый</span> = норма (торгуемый импульс), 
             <span style="color: #fbbf24;">🟡 Желтый</span> = внимание (повышенная волатильность), 
             <span style="color: #f97316;">🟠 Оранжевый</span> = предупреждение (высокий риск), 
             <span style="color: #ef4444;">🔴 Красный</span> = экстремальный риск (шум, не торгуемо).
             <br>Используется для динамической подстройки размера позиции на основе режима рынка.
          </p>
          
          <!-- 3D Surface Plotly -->
          <div id="wave-surface-3d" style="width:100%; height:750px; margin-bottom: 16px; margin-top: -30px;"></div>

          <!-- Regime Metrics -->
          <div class="wave-metrics-row">
             <div class="wave-metric">
                <p class="metric-label">Текущее состояние</p>
                <p class="metric-value" :class="'text-' + (waveRegime.currentRegime === 'TRENDING' ? 'green' : 'red')">
                   {{ waveRegime.currentRegime }}
                </p>
             </div>
             <div class="wave-metric">
                <p class="metric-label">Jaggedness Score</p>
                <p class="metric-value">{{ waveRegime.jaggedness.toFixed(3) }}</p>
             </div>
             <div class="wave-metric">
                <p class="metric-label">% Time CHOPPY (30d)</p>
                <p class="metric-value">{{ waveRegime.pctChoppy }}%</p>
             </div>
             <div class="wave-metric">
                <p class="metric-label">Vol Ratio (Choppy/Trend)</p>
                <p class="metric-value">{{ waveRegime.volRatio.toFixed(2) }}x</p>
             </div>
          </div>

          <!-- Regime History -->
          <div class="regime-history-chart">
             <div class="chart-title">Режим за последние 20 дней</div>
             <div class="chart-bars-horizontal">
                <div v-for="(regime, i) in waveRegime.history" :key="i" 
                     :class="['regime-bar', 'regime-' + regime.toLowerCase()]"
                     :title="regime">
                </div>
             </div>
          </div>
       </div>
    </div>

    <!-- 4️⃣ LATENT VOLATILITY SECTION - 3D SURFACE -->
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

        <!-- 3D Latent Vol Surface -->
        <div id="latent-vol-surface-3d"
             style="width:100%; height:800px; margin: -20px; margin-bottom: 16px; margin-top: -15px;"></div>

        <!-- Legend -->
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

        <!-- Metrics -->
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

        <!-- Alert History -->
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

    <!-- Toast -->
    <transition name="slide-up">
      <div v-if="toast.show" class="toast-notification" :class="'toast-' + toast.type">
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'

// Динамический импорт Plotly
let Plotly: any = null
const loadPlotly = async () => {
  if (typeof window !== 'undefined' && !window.Plotly) {
    const script = document.createElement('script')
    script.src = 'https://cdn.plot.ly/plotly-latest.min.js'
    script.async = true
    document.head.appendChild(script)
    return new Promise((resolve) => {
      script.onload = () => {
        Plotly = window.Plotly
        resolve(Plotly)
      }
    })
  }
  Plotly = window.Plotly
  return Plotly
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
// TOURNAMENT
// ============================================================================
const tournamentResults = ref([
  { name: 'WAVE_σ.9', sharpe: 1.35 },
  { name: 'Latent Vol', sharpe: 1.22 },
  { name: 'Buy & Hold', sharpe: 1.15 }
])

// ============================================================================
// EXISTING STATE
// ============================================================================
const positions = ref([
  { symbol: 'SPY', name: 'S&P 500 ETF', price: '142.50', dayChange: 1.24, notional: 850000, allocation: 35, targetAllocation: 30, color: '#3b82f6' },
  { symbol: 'TLT', name: 'US Bonds 20Y', price: '87.30', dayChange: -0.48, notional: 620000, allocation: 25, targetAllocation: 28, color: '#10b981' },
  { symbol: 'GLD', name: 'Gold ETF', price: '198.75', dayChange: 0.92, notional: 450000, allocation: 18, targetAllocation: 15, color: '#fbbf24' },
  { symbol: 'DXY', name: 'US Dollar Idx', price: '104.20', dayChange: -0.15, notional: 380000, allocation: 15, targetAllocation: 17, color: '#8b5cf6' },
  { symbol: 'QQQ', name: 'Nasdaq 100', price: '325.48', dayChange: 2.15, notional: 310000, allocation: 12, targetAllocation: 10, color: '#ec4899' }
])

const selectedAsset = ref(positions.value[0])
const lastUpdate = ref(new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}))
const isRecalcing = ref(false)
const isOptimizing = ref(false)
const searchFilter = ref('')
const activeMetricsTab = ref('risk')
const toast = ref({ show: false, message: '', type: 'success' })

const optimizer = ref({
  model: 'Mean-Variance',
  minWeight: 0,
  maxWeight: 25,
  targetVol: 15,
  rebalance: true
})

const filteredPositions = computed(() => {
  if (!searchFilter.value) return positions.value
  const query = searchFilter.value.toLowerCase()
  return positions.value.filter(p => 
    p.symbol.toLowerCase().includes(query) || p.name.toLowerCase().includes(query)
  )
})

const correlationMatrix = [
   { label: 'SPY', values: [1.0, 0.6, 0.3, -0.2, 0.8] },
   { label: 'TLT', values: [0.6, 1.0, 0.1, 0.4, 0.5] },
   { label: 'GLD', values: [0.3, 0.1, 1.0, 0.2, 0.3] },
   { label: 'DXY', values: [-0.2, 0.4, 0.2, 1.0, -0.1] },
   { label: 'QQQ', values: [0.8, 0.5, 0.3, -0.1, 1.0] },
]

// ============================================================================
// 3D WAVE VISUALIZATION
// ============================================================================
const initWave3D = async () => {
  try {
    await loadPlotly()
    if (!Plotly) {
      console.error('Plotly not loaded')
      return
    }
    
    const container = document.getElementById('wave-surface-3d')
    if (!container) {
      console.error('Container wave-surface-3d not found')
      return
    }
    
    console.log('Initializing WAVE_σ.9 graph')

    const generateSurface = (offset: number) => {
      const n = 50
      const x = Array.from({length: n}, (_, i) => i / (n - 1))
      const y = Array.from({length: n}, (_, i) => i / (n - 1))
      
      const isChoppy = waveRegime.value.currentRegime === 'CHOPPY'
      const z = Array.from({length: n}, (_, i) => {
        return Array.from({length: n}, (_, j) => {
          const base = Math.sin((i + offset) / 5) * Math.cos((j + offset) / 5)
          const roughness = isChoppy ? 
            Math.sin((i + offset) / 2) * Math.sin((j + offset) / 2) * 0.5 : 
            Math.sin((i + offset) / 8) * 0.15
          return base + roughness + waveRegime.value.jaggedness * 0.8
        })
      })
      return { x, y, z }
    }

    const { x, y, z } = generateSurface(0)
    
    // Вычисляем min и max для нормализации цветов
    const zFlat = z.flat()
    const zMin = Math.min(...zFlat)
    const zMax = Math.max(...zFlat)
    const zRange = zMax - zMin

    // Красочная цветовая карта с градиентом от синего (низкие) к красному (высокие)
    // Показывает разные уровни риска/волатильности
    const colorscale = [
      [0.0, '#1e3a8a'],      // Темно-синий - очень низкие значения (безопасная зона)
      [0.2, '#3b82f6'],      // Синий - низкие значения
      [0.35, '#22d3ee'],     // Голубой - умеренно низкие
      [0.5, '#10b981'],      // Зеленый - средние значения (нормальная зона)
      [0.65, '#84cc16'],     // Лайм - умеренно высокие
      [0.8, '#fbbf24'],      // Желтый - высокие значения (внимание)
      [0.9, '#f97316'],      // Оранжевый - очень высокие (предупреждение)
      [1.0, '#ef4444']       // Красный - экстремальные значения (опасная зона)
    ]

    const trace = {
      x: x,
      y: y,
      z: z,
      type: 'surface',
      colorscale: colorscale,
      showscale: true,
      colorbar: {
        title: {
          text: 'Уровень риска',
          font: { color: 'rgba(255,255,255,0.9)', size: 12 }
        },
        tickfont: { color: 'rgba(255,255,255,0.7)', size: 10 },
        tickmode: 'array',
        tickvals: [0, 0.25, 0.5, 0.75, 1],
        ticktext: ['Низкий', 'Умеренный', 'Средний', 'Высокий', 'Экстремальный'],
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
          title: 'Momentum (Импульс)',
          backgroundcolor: 'rgba(0,0,0,0)',
          gridcolor: 'rgba(255,255,255,0.15)',
          showbackground: true,
          titlefont: { color: 'rgba(255,255,255,0.9)', size: 14, family: 'system-ui' },
          tickfont: { size: 11, color: 'rgba(255,255,255,0.6)' }
        },
        yaxis: { 
          title: 'Volatility (Волатильность)',
          backgroundcolor: 'rgba(0,0,0,0)',
          gridcolor: 'rgba(255,255,255,0.15)',
          showbackground: true,
          titlefont: { color: 'rgba(255,255,255,0.9)', size: 14, family: 'system-ui' },
          tickfont: { size: 11, color: 'rgba(255,255,255,0.6)' }
        },
        zaxis: { 
          title: 'Jaggedness (Неровность)',
          backgroundcolor: 'rgba(0,0,0,0)',
          gridcolor: 'rgba(255,255,255,0.15)',
          showbackground: true,
          titlefont: { color: 'rgba(255,255,255,0.9)', size: 14, family: 'system-ui' },
          tickfont: { size: 11, color: 'rgba(255,255,255,0.6)' }
        },
        bgcolor: 'rgba(0,0,0,0)',
        camera: {
          eye: { x: 2.5, y: 2.5, z: 2.0 },
          center: { x: 0.5, y: 0.5, z: 0.5 },
          up: { x: 0, y: 0, z: 1 }
        },
        aspectratio: { x: 3.0, y: 2.0, z: 1.5 },
      },
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: { color: '#fff', family: 'system-ui' },
      margin: { l: 0, r: 80, b: 0, t: 30 },
      showlegend: false,
      autosize: true,
      title: {
        text: 'Цветовая карта: от синего (низкий риск) до красного (высокий риск)',
        font: { color: 'rgba(255,255,255,0.7)', size: 11 },
        x: 0.5,
        xanchor: 'center',
        y: 0.98,
        yanchor: 'top'
      }
    }

    const config = {
      responsive: true,
      displayModeBar: false,
      staticPlot: false,
      displaylogo: false
    }

    Plotly.newPlot(container, [trace], layout, config)

    // ===== АНИМАЦИЯ ВОЛНЫ =====
    let frame = 0
    const waveInterval = setInterval(() => {
      frame += 12.5
      const { x: newX, y: newY, z: newZ } = generateSurface(frame)
      
      Plotly.restyle(container, { 
        z: [newZ],
        x: [newX],
        y: [newY]
      })
    }, 10)

    // ===== УПРАВЛЕНИЕ МЫШКОЙ ОТКЛЮЧЕНО - СТАТИЧНАЯ КАМЕРА =====
    // setupWaveControls(container)

    return () => {
      clearInterval(waveInterval)
    }
  } catch (err) {
    console.error('Error:', err)
  }
}

// Функция управления (Three.js стиль) - улучшенная версия
const setupWaveControls = (container: HTMLElement) => {
  let isDragging = false
  let previousMousePosition = { x: 0, y: 0 }
  let rotation = { x: 0, y: 0 }
  let cameraDistance = 2.0
  let animationFrameId: number | null = null
  let pendingEye: { x: number; y: number; z: number } | null = null

  // Визуальная обратная связь
  container.style.cursor = 'grab'
  container.style.userSelect = 'none'

  const updateCamera = () => {
    if (pendingEye) {
      Plotly.relayout(container, {
        'scene.camera.eye': pendingEye
      })
      pendingEye = null
    }
    animationFrameId = null
  }

  const scheduleCameraUpdate = (eye: { x: number; y: number; z: number }) => {
    pendingEye = eye
    if (!animationFrameId && typeof window !== 'undefined') {
      animationFrameId = window.requestAnimationFrame(updateCamera)
    }
  }

  container.addEventListener('mousedown', (e) => {
    isDragging = true
    container.style.cursor = 'grabbing'
    previousMousePosition = { x: e.clientX, y: e.clientY }
    e.preventDefault()
  })

  container.addEventListener('mouseup', () => {
    isDragging = false
    container.style.cursor = 'grab'
  })

  container.addEventListener('mouseleave', () => {
    isDragging = false
    container.style.cursor = 'grab'
  })

  container.addEventListener('mousemove', (e) => {
    if (isDragging) {
      const deltaX = e.clientX - previousMousePosition.x
      const deltaY = e.clientY - previousMousePosition.y

      // Улучшенная чувствительность с учетом размера контейнера
      const sensitivity = 0.008
      rotation.y += deltaX * sensitivity
      rotation.x += deltaY * sensitivity
      rotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, rotation.x))

      const eye = {
        x: cameraDistance * Math.sin(rotation.y) * Math.cos(rotation.x),
        y: cameraDistance * Math.sin(rotation.x),
        z: cameraDistance * Math.cos(rotation.y) * Math.cos(rotation.x)
      }

      scheduleCameraUpdate(eye)
      previousMousePosition = { x: e.clientX, y: e.clientY }
    }
  })

  container.addEventListener('wheel', (e) => {
    e.preventDefault()
    // Более плавный зум с учетом направления
    const zoomSpeed = 0.05
    const zoomDelta = e.deltaY > 0 ? zoomSpeed : -zoomSpeed
    cameraDistance = Math.max(1.2, Math.min(4, cameraDistance + zoomDelta))

    const eye = {
      x: cameraDistance * Math.sin(rotation.y) * Math.cos(rotation.x),
      y: cameraDistance * Math.sin(rotation.x),
      z: cameraDistance * Math.cos(rotation.y) * Math.cos(rotation.x)
    }

    scheduleCameraUpdate(eye)
  })

  // Поддержка touch-событий для мобильных устройств
  let touchStartDistance = 0
  let touchStartRotation = { x: rotation.x, y: rotation.y }

  container.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) {
      isDragging = true
      const touch = e.touches[0]
      previousMousePosition = { x: touch.clientX, y: touch.clientY }
      touchStartRotation = { x: rotation.x, y: rotation.y }
    } else if (e.touches.length === 2) {
      const touch1 = e.touches[0]
      const touch2 = e.touches[1]
      touchStartDistance = Math.hypot(
        touch2.clientX - touch1.clientX,
        touch2.clientY - touch1.clientY
      )
    }
    e.preventDefault()
  })

  container.addEventListener('touchmove', (e) => {
    if (e.touches.length === 1 && isDragging) {
      const touch = e.touches[0]
      const deltaX = touch.clientX - previousMousePosition.x
      const deltaY = touch.clientY - previousMousePosition.y

      const sensitivity = 0.01
      rotation.y = touchStartRotation.y + deltaX * sensitivity
      rotation.x = touchStartRotation.x + deltaY * sensitivity
      rotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, rotation.x))

      const eye = {
        x: cameraDistance * Math.sin(rotation.y) * Math.cos(rotation.x),
        y: cameraDistance * Math.sin(rotation.x),
        z: cameraDistance * Math.cos(rotation.y) * Math.cos(rotation.x)
      }

      scheduleCameraUpdate(eye)
      previousMousePosition = { x: touch.clientX, y: touch.clientY }
    } else if (e.touches.length === 2) {
      const touch1 = e.touches[0]
      const touch2 = e.touches[1]
      const currentDistance = Math.hypot(
        touch2.clientX - touch1.clientX,
        touch2.clientY - touch1.clientY
      )
      const zoomDelta = (touchStartDistance - currentDistance) * 0.01
      cameraDistance = Math.max(1.2, Math.min(4, cameraDistance + zoomDelta))
      touchStartDistance = currentDistance

      const eye = {
        x: cameraDistance * Math.sin(rotation.y) * Math.cos(rotation.x),
        y: cameraDistance * Math.sin(rotation.x),
        z: cameraDistance * Math.cos(rotation.y) * Math.cos(rotation.x)
      }

      scheduleCameraUpdate(eye)
    }
    e.preventDefault()
  })

  container.addEventListener('touchend', () => {
    isDragging = false
  })
}

// ============================================================================
// LATENT VOL 3D SURFACE
// ============================================================================
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
    
    console.log('Initializing Latent Vol graph')

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
    
    console.log('Latent Vol graph initialized successfully')
  } catch (err) {
    console.error('Error initializing Latent Vol graph:', err)
  }
}

// Обновляем график при изменении режима
watch(() => waveRegime.value.currentRegime, () => {
  initWave3D()
})

onMounted(async () => {
  if (positions.value?.length > 0) selectedAsset.value = positions.value[0]
  
  // Инициализируем графики последовательно с задержкой
  setTimeout(async () => {
    await initWave3D()
  }, 500)
  
  setTimeout(async () => {
    await initLatentVol3D()
  }, 800)
  
  setTimeout(() => {
    latentVolAlert.value.isActive = true
    latentVolAlert.value.severity = 'warning'
    latentVolMetrics.value.currentZscore = 2.15
  }, 2000)
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
  await new Promise(resolve => setTimeout(resolve, 1500))
  lastUpdate.value = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
  isRecalcing.value = false
  showToast('Портфель пересчитан (WAVE_σ.9 + Latent Vol обновлены)', 'success')
}

const exportPdf = () => {
  showToast('PDF экспорт инициирован...', 'info')
  setTimeout(() => {
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

const calculateOptimization = async () => {
  isOptimizing.value = true
  const regimeAdjustment = waveRegime.value.currentRegime === 'CHOPPY' ? ' (режим: консервативный)' : ' (режим: стандартный)'
  await new Promise(resolve => setTimeout(resolve, 2000))
  isOptimizing.value = false
  showToast(`Оптимизация завершена (λ=${waveRegime.value.lambda}${regimeAdjustment})`, 'success')
}

const resetOptimizer = () => {
  optimizer.value = {
    model: 'Mean-Variance',
    minWeight: 0,
    maxWeight: 25,
    targetVol: 15,
    rebalance: true
  }
  showToast('Оптимизатор сброшен', 'info')
}

const validateWeights = () => {
  if (optimizer.value.minWeight > optimizer.value.maxWeight) {
    optimizer.value.maxWeight = optimizer.value.minWeight + 5
  }
}

const showToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
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
.hero-left h1 { font-size: 28px; font-weight: 700; color: #fff; margin: 0 0 16px 0; letter-spacing: -0.01em; }
.hero-meta { display: flex; gap: 10px; }
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
.panel-body { padding: 16px 20px; overflow: hidden; }
.panel-body.p-0 { padding: 0; }
.heatmap-body { min-height: 380px !important; padding: 24px 20px !important; }
.panel-body-optimizer { padding: 16px 20px; flex: 1; display: flex; flex-direction: column; gap: 12px; overflow: hidden; }

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
.combined-metrics { flex-shrink: 0; display: flex; flex-direction: column; min-height: 330px; }
.combined-tabs { display: flex; gap: 0; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 0 20px; flex-shrink: 0; }
.tab-button { flex: 1; padding: 12px 16px; background: transparent; border: none; color: rgba(255,255,255,0.4); font-size: 11px; font-weight: 600; text-transform: uppercase; cursor: pointer; position: relative; transition: color 0.2s; }
.tab-button:hover { color: rgba(255,255,255,0.6); }
.tab-button.active { color: rgba(255,255,255,0.9); }
.tab-button.active::after { content: ''; position: absolute; bottom: -1px; left: 0; right: 0; height: 2px; background: #3b82f6; }
.tab-content { padding: 16px 20px; display: flex; flex-direction: column; gap: 8px; flex: 1; }
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

/* Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1); }
.slide-up-enter-from { transform: translateY(20px); opacity: 0; }
.slide-up-leave-to { transform: translateY(20px); opacity: 0; }

/* Responsive */
@media (max-width: 1400px) { 
  .dashboard-grid { grid-template-columns: 1fr; } 
}

@media (max-width: 1024px) { 
  .kpi-grid { grid-template-columns: repeat(2, 1fr); } 
  .stats-grid { grid-template-columns: 1fr 1fr; } 
  .charts-row-two-col { grid-template-columns: 1fr; } 
  .portfolio-page {
    padding: 16px 20px;
  }
}

@media (max-width: 768px) { 
  .portfolio-page { 
    padding: 16px; 
  } 
  .hero-section { 
    flex-direction: column; 
    gap: 16px; 
  } 
  .hero-actions { 
    width: 100%; 
    flex-wrap: wrap; 
  } 
  .kpi-grid { 
    grid-template-columns: 1fr; 
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
}

@media (max-width: 480px) {
  .portfolio-page {
    padding: 12px;
  }
  .hero-section {
    gap: 12px;
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
}
</style>