<template>
  <div class="repo-page">
    <!-- Header -->
    <div class="page-header">
      <h1 class="font-anton page-title">
        REPO ANALYSIS
      </h1>
      <p class="font-mono page-subtitle">
        CONCENTRATION / COLLATERAL / LIQUIDITY / SYSTEMIC / STRESS
      </p>
    </div>

    <!-- Upload Zone -->
    <div
      v-if="!result"
      class="upload-zone"
      :class="{ 'drag-over': isDragOver }"
      @dragover.prevent="isDragOver = true"
      @dragleave.prevent="isDragOver = false"
      @drop.prevent="handleDrop"
    >
      <div class="upload-content">
        <div class="font-anton upload-title">
          UPLOAD DATA
        </div>
        <p class="font-mono upload-hint">
          CSV or Excel (.xlsx) with REPO transaction data
        </p>
        <p class="font-mono upload-hint-cols">
          Required: seller, buyer, loan_amount, repayment_amount, collateral_value, price, units, days
        </p>
        <label class="btn btn-primary font-oswald">
          SELECT FILE
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            hidden
            @change="handleFileSelect"
          >
        </label>
      </div>
    </div>

    <!-- Loading -->
    <div
      v-if="loading"
      class="loading-state"
    >
      <div class="loading-spinner" />
      <p class="font-mono">
        Analyzing REPO data...
      </p>
    </div>

    <!-- Error -->
    <div
      v-if="error"
      class="error-banner font-mono"
    >
      {{ error }}
      <button
        class="btn btn-outline font-oswald"
        @click="reset"
      >
        RETRY
      </button>
    </div>

    <!-- Results -->
    <div v-if="result && !loading">
      <!-- Summary bar -->
      <div class="summary-bar">
        <div class="summary-item">
          <span class="font-mono summary-label">ROWS</span>
          <span class="font-mono summary-value">{{ result.summary.total_rows }}</span>
        </div>
        <div class="summary-item">
          <span class="font-mono summary-label">OVERALL</span>
          <span
            class="font-mono summary-value"
            :class="'light-' + result.traffic_light.overall"
          >
            {{ result.traffic_light.overall.toUpperCase() }}
          </span>
        </div>
        <button
          class="btn btn-outline font-oswald"
          @click="reset"
        >
          NEW FILE
        </button>
      </div>

      <!-- Tab Navigation -->
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab font-oswald"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Concentration -->
        <div v-if="activeTab === 'concentration'">
          <div class="metrics-grid">
            <div class="metric-card">
              <span class="font-mono metric-label">HHI</span>
              <span class="font-mono metric-value">{{ result.concentration.hhi }}</span>
            </div>
            <div class="metric-card">
              <span class="font-mono metric-label">ENTROPY</span>
              <span class="font-mono metric-value">{{ result.concentration.entropy }}</span>
            </div>
            <div class="metric-card">
              <span class="font-mono metric-label">CR3</span>
              <span class="font-mono metric-value">{{ result.concentration.cr3 }}%</span>
            </div>
            <div class="metric-card">
              <span class="font-mono metric-label">CR5</span>
              <span class="font-mono metric-value">{{ result.concentration.cr5 }}%</span>
            </div>
            <div class="metric-card">
              <span class="font-mono metric-label">CR10</span>
              <span class="font-mono metric-value">{{ result.concentration.cr10 }}%</span>
            </div>
            <div class="metric-card">
              <span class="font-mono metric-label">GINI</span>
              <span class="font-mono metric-value">{{ result.concentration.gini }}</span>
            </div>
          </div>

          <h3 class="font-oswald section-title">
            TOP PARTICIPANTS
          </h3>
          <table class="data-table">
            <thead>
              <tr>
                <th class="font-mono">
                  NAME
                </th>
                <th class="font-mono">
                  VOLUME
                </th>
                <th class="font-mono">
                  SHARE %
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="p in result.concentration.top_participants"
                :key="p.name"
              >
                <td class="font-mono">
                  {{ p.name }}
                </td>
                <td class="font-mono">
                  {{ formatNumber(p.volume) }}
                </td>
                <td class="font-mono">
                  {{ p.share_pct.toFixed(2) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Collateral -->
        <div v-if="activeTab === 'collateral'">
          <div class="metrics-grid">
            <div class="metric-card">
              <span class="font-mono metric-label">ISSUER HHI</span>
              <span class="font-mono metric-value">{{ result.collateral.issuer_hhi ?? 'N/A' }}</span>
            </div>
            <div class="metric-card">
              <span class="font-mono metric-label">VaR 99% 10d</span>
              <span class="font-mono metric-value">{{ result.collateral.var_99_10d != null ? result.collateral.var_99_10d.toFixed(4) : 'N/A' }}</span>
            </div>
          </div>

          <div
            v-if="result.collateral.haircut_stats"
            class="subsection"
          >
            <h3 class="font-oswald section-title">
              HAIRCUT STATISTICS
            </h3>
            <div class="metrics-grid">
              <div
                v-for="(val, key) in result.collateral.haircut_stats"
                :key="key"
                class="metric-card"
              >
                <span class="font-mono metric-label">{{ String(key).toUpperCase() }}</span>
                <span class="font-mono metric-value">{{ val != null ? (val * 100).toFixed(2) + '%' : 'N/A' }}</span>
              </div>
            </div>
          </div>

          <div
            v-if="result.coverage.coverage_ratio"
            class="subsection"
          >
            <h3 class="font-oswald section-title">
              COVERAGE RATIO
            </h3>
            <div class="metrics-grid">
              <div class="metric-card">
                <span class="font-mono metric-label">MEAN</span>
                <span class="font-mono metric-value">{{ result.coverage.coverage_ratio.mean.toFixed(4) }}</span>
              </div>
              <div class="metric-card">
                <span class="font-mono metric-label">MEDIAN</span>
                <span class="font-mono metric-value">{{ result.coverage.coverage_ratio.median.toFixed(4) }}</span>
              </div>
              <div class="metric-card">
                <span class="font-mono metric-label">MIN</span>
                <span class="font-mono metric-value">{{ result.coverage.coverage_ratio.min.toFixed(4) }}</span>
              </div>
              <div class="metric-card">
                <span class="font-mono metric-label">BELOW 1.0</span>
                <span class="font-mono metric-value light-red">{{ result.coverage.coverage_ratio.below_1 }}</span>
              </div>
            </div>
          </div>

          <div
            v-if="result.coverage.wrong_way_risk"
            class="subsection"
          >
            <h3 class="font-oswald section-title">
              WRONG-WAY RISK
            </h3>
            <div class="metrics-grid">
              <div class="metric-card">
                <span class="font-mono metric-label">COUNT</span>
                <span class="font-mono metric-value">{{ result.coverage.wrong_way_risk.count }}</span>
              </div>
              <div class="metric-card">
                <span class="font-mono metric-label">VOLUME</span>
                <span class="font-mono metric-value">{{ formatNumber(result.coverage.wrong_way_risk.volume) }}</span>
              </div>
              <div class="metric-card">
                <span class="font-mono metric-label">% OF TOTAL</span>
                <span class="font-mono metric-value">{{ result.coverage.wrong_way_risk.pct_of_total }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Liquidity -->
        <div v-if="activeTab === 'liquidity'">
          <div class="metrics-grid">
            <div class="metric-card">
              <span class="font-mono metric-label">TOTAL VOLUME</span>
              <span class="font-mono metric-value">{{ formatNumber(result.liquidity.total_volume) }}</span>
            </div>
            <div class="metric-card">
              <span class="font-mono metric-label">ROLLOVER RISK</span>
              <span
                class="font-mono metric-value"
                :class="result.liquidity.rollover_risk_pct >= 40 ? 'light-red' : result.liquidity.rollover_risk_pct >= 20 ? 'light-yellow' : 'light-green'"
              >
                {{ result.liquidity.rollover_risk_pct }}%
              </span>
            </div>
          </div>

          <h3 class="font-oswald section-title">
            TENOR BUCKETS
          </h3>
          <table class="data-table">
            <thead>
              <tr>
                <th class="font-mono">
                  BUCKET
                </th>
                <th class="font-mono">
                  VOLUME
                </th>
                <th class="font-mono">
                  SHARE %
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="b in result.liquidity.tenor_buckets"
                :key="b.bucket"
              >
                <td class="font-mono">
                  {{ b.bucket }}
                </td>
                <td class="font-mono">
                  {{ formatNumber(b.volume) }}
                </td>
                <td class="font-mono">
                  {{ b.share_pct.toFixed(2) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Systemic -->
        <div v-if="activeTab === 'systemic'">
          <div class="metrics-grid">
            <div class="metric-card">
              <span class="font-mono metric-label">NODES</span>
              <span class="font-mono metric-value">{{ result.systemic.num_nodes }}</span>
            </div>
            <div class="metric-card">
              <span class="font-mono metric-label">EDGES</span>
              <span class="font-mono metric-value">{{ result.systemic.num_edges }}</span>
            </div>
            <div class="metric-card">
              <span class="font-mono metric-label">DENSITY</span>
              <span class="font-mono metric-value">{{ result.systemic.density }}</span>
            </div>
            <div class="metric-card">
              <span class="font-mono metric-label">MAX DEBTRANK</span>
              <span
                class="font-mono metric-value"
                :class="result.systemic.max_debt_rank >= 0.25 ? 'light-red' : result.systemic.max_debt_rank >= 0.1 ? 'light-yellow' : 'light-green'"
              >
                {{ result.systemic.max_debt_rank }}
              </span>
            </div>
          </div>

          <h3 class="font-oswald section-title">
            CENTRALITY TABLE
          </h3>
          <div class="table-scroll">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="font-mono">
                    NODE
                  </th>
                  <th class="font-mono">
                    DEGREE
                  </th>
                  <th class="font-mono">
                    BETWEENNESS
                  </th>
                  <th class="font-mono">
                    PAGERANK
                  </th>
                  <th class="font-mono">
                    EIGENVECTOR
                  </th>
                  <th class="font-mono">
                    DEBTRANK
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="c in result.systemic.centrality_table"
                  :key="c.node"
                >
                  <td class="font-mono">
                    {{ c.node }}
                  </td>
                  <td class="font-mono">
                    {{ c.degree }}
                  </td>
                  <td class="font-mono">
                    {{ c.betweenness }}
                  </td>
                  <td class="font-mono">
                    {{ c.pagerank }}
                  </td>
                  <td class="font-mono">
                    {{ c.eigenvector }}
                  </td>
                  <td class="font-mono">
                    {{ c.debt_rank }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Stress -->
        <div v-if="activeTab === 'stress'">
          <h3 class="font-oswald section-title">
            SCENARIO RESULTS
          </h3>
          <div class="table-scroll">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="font-mono">
                    SCENARIO
                  </th>
                  <th class="font-mono">
                    HAIRCUT
                  </th>
                  <th class="font-mono">
                    RATE
                  </th>
                  <th class="font-mono">
                    COLLATERAL
                  </th>
                  <th class="font-mono">
                    COVERAGE
                  </th>
                  <th class="font-mono">
                    LOSS
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="s in result.stress.scenarios"
                  :key="s.scenario"
                >
                  <td class="font-mono">
                    {{ s.scenario }}
                  </td>
                  <td class="font-mono">
                    {{ (s.stressed_haircut * 100).toFixed(2) }}%
                  </td>
                  <td class="font-mono">
                    {{ (s.stressed_rate * 100).toFixed(2) }}%
                  </td>
                  <td class="font-mono">
                    {{ formatNumber(s.stressed_collateral) }}
                  </td>
                  <td class="font-mono">
                    {{ s.coverage_ratio.toFixed(4) }}
                  </td>
                  <td
                    class="font-mono"
                    :class="s.potential_loss > 0 ? 'light-red' : ''"
                  >
                    {{ formatNumber(s.potential_loss) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div
            v-if="result.stress.adversarial"
            class="subsection"
          >
            <h3 class="font-oswald section-title">
              ADVERSARIAL STRESS
            </h3>
            <div class="metrics-grid">
              <div class="metric-card">
                <span class="font-mono metric-label">HAIRCUT SHOCK</span>
                <span class="font-mono metric-value">{{ (result.stress.adversarial.optimal_haircut_shock * 100).toFixed(2) }}%</span>
              </div>
              <div class="metric-card">
                <span class="font-mono metric-label">PRICE SHOCK</span>
                <span class="font-mono metric-value">{{ (result.stress.adversarial.optimal_price_shock * 100).toFixed(2) }}%</span>
              </div>
              <div class="metric-card">
                <span class="font-mono metric-label">MAX LOSS</span>
                <span class="font-mono metric-value light-red">{{ formatNumber(result.stress.adversarial.max_loss) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Traffic Light -->
        <div v-if="activeTab === 'traffic'">
          <div class="traffic-dashboard">
            <div
              v-for="m in result.traffic_light.metrics"
              :key="m.metric"
              class="traffic-card"
              :class="'border-' + m.light"
            >
              <div
                class="traffic-indicator"
                :class="'bg-' + m.light"
              />
              <div class="traffic-info">
                <span class="font-oswald traffic-metric">{{ m.metric }}</span>
                <span class="font-mono traffic-value">{{ m.value != null ? m.value : 'N/A' }}</span>
              </div>
              <span
                class="font-mono traffic-light-label"
                :class="'light-' + m.light"
              >{{ m.light.toUpperCase() }}</span>
            </div>
          </div>

          <div
            v-if="result.traffic_light.recommendations.length > 0"
            class="recommendations"
          >
            <h3 class="font-oswald section-title">
              RECOMMENDATIONS
            </h3>
            <div
              v-for="(rec, i) in result.traffic_light.recommendations"
              :key="i"
              class="rec-item font-mono"
            >
              {{ rec }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { analyzeRepo, type RepoAnalysisResponse } from '@/services/repoService'

const result = ref<RepoAnalysisResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const isDragOver = ref(false)
const activeTab = ref('concentration')

const tabs = [
  { key: 'concentration', label: 'CONCENTRATION' },
  { key: 'collateral', label: 'COLLATERAL' },
  { key: 'liquidity', label: 'LIQUIDITY' },
  { key: 'systemic', label: 'SYSTEMIC' },
  { key: 'stress', label: 'STRESS' },
  { key: 'traffic', label: 'TRAFFIC LIGHT' },
]

const formatNumber = (n: number): string => {
  if (Math.abs(n) >= 1e9) return (n / 1e9).toFixed(2) + 'B'
  if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(2) + 'M'
  if (Math.abs(n) >= 1e3) return (n / 1e3).toFixed(2) + 'K'
  return n.toFixed(2)
}

const processFile = async (file: File) => {
  loading.value = true
  error.value = null
  result.value = null
  try {
    result.value = await analyzeRepo(file)
    activeTab.value = 'concentration'
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Analysis failed'
  } finally {
    loading.value = false
  }
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    processFile(input.files[0])
  }
}

const handleDrop = (e: DragEvent) => {
  isDragOver.value = false
  if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
    processFile(e.dataTransfer.files[0])
  }
}

const reset = () => {
  result.value = null
  error.value = null
  loading.value = false
}
</script>

<style scoped>
.repo-page {
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
  border-bottom: 1px solid var(--border, #1A1A1A);
  padding-bottom: 16px;
}

.page-title {
  font-size: 32px;
  color: var(--text-primary, #F5F5F5);
  letter-spacing: 0.05em;
}

.page-subtitle {
  font-size: 11px;
  color: var(--text-muted, #888888);
  letter-spacing: 0.1em;
  margin-top: 4px;
}

/* Upload Zone */
.upload-zone {
  border: 2px dashed var(--border, #1A1A1A);
  padding: 64px 32px;
  text-align: center;
  transition: border-color 0.2s;
}

.upload-zone.drag-over {
  border-color: var(--accent, #DC2626);
}

.upload-title {
  font-size: 24px;
  color: var(--text-primary, #F5F5F5);
  margin-bottom: 8px;
}

.upload-hint {
  color: var(--text-muted, #888888);
  font-size: 12px;
  margin-bottom: 4px;
}

.upload-hint-cols {
  color: var(--text-muted, #888888);
  font-size: 10px;
  margin-bottom: 24px;
}

.btn {
  display: inline-block;
  padding: 10px 24px;
  font-size: 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  cursor: pointer;
  border: 1px solid var(--border, #1A1A1A);
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent, #DC2626);
  color: #000;
  border-color: var(--accent, #DC2626);
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-outline {
  background: transparent;
  color: var(--text-primary, #F5F5F5);
  border-color: var(--border, #1A1A1A);
}

.btn-outline:hover {
  border-color: var(--accent, #DC2626);
  color: var(--accent, #DC2626);
}

/* Loading */
.loading-state {
  text-align: center;
  padding: 64px;
  color: var(--text-muted, #888888);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 2px solid var(--border, #1A1A1A);
  border-top-color: var(--accent, #DC2626);
  border-radius: 50%;
  margin: 0 auto 16px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error */
.error-banner {
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid var(--accent, #DC2626);
  color: var(--accent, #DC2626);
  padding: 16px 24px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

/* Summary bar */
.summary-bar {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 12px 20px;
  border: 1px solid var(--border, #1A1A1A);
  margin-bottom: 24px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.summary-label {
  font-size: 9px;
  color: var(--text-muted, #888888);
  letter-spacing: 0.1em;
}

.summary-value {
  font-size: 14px;
  color: var(--text-primary, #F5F5F5);
}

/* Tabs */
.tabs {
  display: flex;
  border-bottom: 1px solid var(--border, #1A1A1A);
  margin-bottom: 24px;
  overflow-x: auto;
}

.tab {
  padding: 12px 20px;
  font-size: 11px;
  letter-spacing: 0.05em;
  color: var(--text-muted, #888888);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.tab:hover {
  color: var(--text-primary, #F5F5F5);
}

.tab.active {
  color: var(--accent, #DC2626);
  border-bottom-color: var(--accent, #DC2626);
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.metric-card {
  border: 1px solid var(--border, #1A1A1A);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-label {
  font-size: 9px;
  color: var(--text-muted, #888888);
  letter-spacing: 0.1em;
}

.metric-value {
  font-size: 18px;
  color: var(--text-primary, #F5F5F5);
}

/* Data Tables */
.table-scroll {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 10px 14px;
  text-align: left;
  font-size: 11px;
  border-bottom: 1px solid var(--border, #1A1A1A);
}

.data-table th {
  color: var(--text-muted, #888888);
  font-size: 9px;
  letter-spacing: 0.1em;
  font-weight: normal;
}

.data-table td {
  color: var(--text-primary, #F5F5F5);
}

.data-table tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

/* Section title */
.section-title {
  font-size: 13px;
  color: var(--text-primary, #F5F5F5);
  letter-spacing: 0.05em;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border, #1A1A1A);
}

.subsection {
  margin-top: 32px;
}

/* Traffic Light */
.traffic-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.traffic-card {
  border: 1px solid var(--border, #1A1A1A);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.traffic-card.border-green { border-left: 3px solid #22C55E; }
.traffic-card.border-yellow { border-left: 3px solid #F59E0B; }
.traffic-card.border-red { border-left: 3px solid #DC2626; }
.traffic-card.border-gray { border-left: 3px solid #525252; }

.traffic-indicator {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  flex-shrink: 0;
}

.bg-green { background: #22C55E; }
.bg-yellow { background: #F59E0B; }
.bg-red { background: #DC2626; }
.bg-gray { background: #525252; }

.traffic-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.traffic-metric {
  font-size: 12px;
  color: var(--text-primary, #F5F5F5);
  letter-spacing: 0.05em;
}

.traffic-value {
  font-size: 16px;
  color: var(--text-primary, #F5F5F5);
}

.traffic-light-label {
  font-size: 10px;
  letter-spacing: 0.1em;
}

/* Color utilities */
.light-green { color: #22C55E; }
.light-yellow { color: #F59E0B; }
.light-red { color: #DC2626; }
.light-gray { color: #525252; }

/* Recommendations */
.recommendations {
  margin-top: 24px;
}

.rec-item {
  padding: 12px 16px;
  border: 1px solid var(--border, #1A1A1A);
  margin-bottom: 8px;
  font-size: 11px;
  color: var(--text-primary, #F5F5F5);
}

/* Responsive */
@media (max-width: 768px) {
  .repo-page {
    padding: 16px;
  }
  .page-title {
    font-size: 24px;
  }
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .tabs {
    gap: 0;
  }
  .tab {
    padding: 10px 12px;
    font-size: 10px;
  }
}
</style>
