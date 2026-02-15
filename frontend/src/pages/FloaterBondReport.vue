<!-- src/pages/FloaterBondReport.vue -->
<template>
  <div class="page-container">

    <!-- Header Section -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title" v-if="report">
          {{ report.issuer }}, {{ report.isin }}
        </h1>
        <h1 class="section-title" v-else>Floater Bond Report</h1>
        <p class="section-subtitle" v-if="report">
          Отчет по облигации с плавающим купоном ISIN: <span class="text-accent">{{ report.isin }}</span>
        </p>
        <p class="section-subtitle" v-else>
          Отчет по облигации с плавающим купоном ISIN: <span class="text-accent">{{ isin || '—' }}</span>
        </p>
      </div>

      <div class="header-actions">
        <!-- Valuation Date -->
        <div class="glass-pill">
          <label class="lbl-mini">Дата оценки:</label>
          <input
            v-model="valuationDate"
            type="date"
            class="date-input-small"
            @change="onValuationDateChange"
          />
        </div>

        <!-- Edit Mode Toggle -->
        <button
          @click="toggleEditMode"
          class="btn-toggle-edit"
          :class="{ 'active': editMode }"
        >
          {{ editMode ? '✓ Режим редактирования' : '✎ Редактировать' }}
        </button>

        <!-- Export to Excel -->
        <button
          @click="exportToExcel"
          class="btn-export-excel"
          :disabled="!report"
        >
          📊 Excel
        </button>

        <!-- Search Control -->
        <div class="glass-pill">
          <label class="lbl-mini">ISIN:</label>
          <input
            v-model="localIsin"
            type="text"
            class="search-input"
            placeholder="RU000A108VW7"
            @keyup.enter="onChangeIsin"
          />
          <button class="btn-search" @click="onChangeIsin" :disabled="!localIsin">🔍</button>
        </div>
      </div>
    </div>

    <!-- States -->
    <section v-if="loading" class="state-section">
      <div class="glass-card">
        <span class="spinner"></span> {{ loadingMessage }}
      </div>
    </section>

    <section v-else-if="error" class="state-section">
      <div class="glass-card error">⚠ {{ error }}</div>
    </section>

    <section v-else-if="!report" class="state-section">
      <div class="glass-card">Введите ISIN для генерации отчёта</div>
    </section>

    <!-- Report Content -->
    <section v-else class="report-content">

      <!-- General Info Section -->
      <div class="grid-2">
        <div class="glass-card">
          <div class="card-header">
            <h3>Общие сведения</h3>
          </div>
          <table class="info-table">
            <tr>
              <td class="label">Эмитент</td>
              <td class="value">
                <input v-if="editMode && editableReport" v-model="editableReport.issuer" type="text" class="edit-input" />
                <span v-else>{{ report.issuer }}</span>
              </td>
            </tr>
            <tr><td class="label">ISIN</td><td class="value mono">{{ report.isin }}</td></tr>
            <tr>
              <td class="label">Страна риска</td>
              <td class="value">
                <input v-if="editMode && editableReport" v-model="editableReport.risk_country" type="text" class="edit-input" />
                <span v-else>{{ report.risk_country || '—' }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Сектор</td>
              <td class="value">
                <input v-if="editMode && editableReport" v-model="editableReport.sector" type="text" class="edit-input" />
                <span v-else>{{ report.sector || '—' }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Отрасль</td>
              <td class="value">
                <input v-if="editMode && editableReport" v-model="editableReport.industry" type="text" class="edit-input" />
                <span v-else>{{ report.industry || '—' }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Кол-во выпусков в обращении</td>
              <td class="value mono">
                <input v-if="editMode && editableReport" v-model.number="editableReport.issues_count" type="number" class="edit-input" />
                <span v-else>{{ report.issues_count || '—' }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Уровень листинга</td>
              <td class="value">{{ report.listing_level ? (report.listing_level + ' уровень') : '—' }}</td>
            </tr>
            <tr>
              <td class="label">Валюта</td>
              <td class="value">{{ report.currency || '—' }}</td>
            </tr>
          </table>
        </div>

        <div class="glass-card">
          <div class="card-header">
            <h3>Информация по выпуску</h3>
          </div>
          <table class="info-table">
            <tr>
              <td class="label">Дата выпуска</td>
              <td class="value mono">
                <input v-if="editMode && editableReport?.issue_info" v-model="editableReport.issue_info.issue_date" type="date" class="edit-input" />
                <span v-else>{{ formatDate(report.issue_info?.issue_date) }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Объем в обращении, RUB</td>
              <td class="value mono">
                <input v-if="editMode && editableReport" v-model.number="editableReport.outstanding_amount" type="number" class="edit-input" />
                <span v-else>{{ formatNumber(report.outstanding_amount) || '—' }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Дата погашения</td>
              <td class="value mono">
                <input v-if="editMode && editableReport?.issue_info" v-model="editableReport.issue_info.maturity_date" type="date" class="edit-input" />
                <span v-else>{{ formatDate(report.issue_info?.maturity_date) }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Купон, %</td>
              <td class="value accent">
                <input v-if="editMode && editableReport?.issue_info" v-model="editableReport.issue_info.coupon_formula" type="text" class="edit-input" />
                <span v-else>{{ report.issue_info?.coupon_formula || '—' }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Базовая ставка</td>
              <td class="value">
                <span v-if="report.base_rate_name" class="accent">
                  {{ report.base_rate_name }}
                  <span v-if="report.base_rate_value != null"> ({{ report.base_rate_value.toFixed(2) }}%)</span>
                </span>
                <span v-else>—</span>
              </td>
            </tr>
            <tr>
              <td class="label">Следующий купон</td>
              <td class="value accent">
                <input v-if="editMode && editableReport?.issue_info" v-model.number="editableReport.issue_info.next_coupon" type="number" step="0.001" class="edit-input" />
                <span v-else>{{ report.issue_info?.next_coupon ? ((report.issue_info.next_coupon * 100).toFixed(2) + '%') : '—' }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Номинал, RUB</td>
              <td class="value mono">
                <input v-if="editMode && editableReport?.issue_info" v-model.number="editableReport.issue_info.nominal" type="number" class="edit-input" />
                <span v-else>{{ report.issue_info?.nominal ? formatNumber(report.issue_info.nominal) : '—' }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Кол-во купонных платежей в год</td>
              <td class="value mono">
                <input v-if="editMode && editableReport?.issue_info" v-model.number="editableReport.issue_info.coupon_per_year" type="number" class="edit-input" />
                <span v-else>{{ report.issue_info?.coupon_per_year ?? '—' }}</span>
              </td>
            </tr>
            <tr>
              <td class="label">Оферта</td>
              <td class="value">
                <span v-if="report.issue_info?.offer && report.issue_info.offer.type !== 'Нет'" class="accent">
                  {{ report.issue_info.offer.type }} — {{ formatDate(report.issue_info.offer.date) }}
                </span>
                <span v-else>Нет</span>
              </td>
            </tr>
            <tr>
              <td class="label">Анализируемый период</td>
              <td class="value mono">
                <input v-if="editMode && editableReport" v-model="editableReport.analysis_period" type="text" class="edit-input" />
                <span v-else>{{ report.analysis_period || '—' }}</span>
              </td>
            </tr>
          </table>
        </div>
      </div>

      <!-- Ratings Section -->
      <div class="grid-3">
        <div class="glass-card">
          <div class="card-header">
            <h3>Рейтинг эмиссии</h3>
          </div>
          <div v-if="report.ratings?.issue?.length" class="ratings-list">
            <div v-for="(r, idx) in report.ratings.issue" :key="idx" class="rating-item">
              <span class="agency">{{ r.agency }}</span>
              <span class="grade">{{ r.rating }}</span>
              <span class="date mono">{{ formatDate(r.date) }}</span>
            </div>
          </div>
          <p v-else class="muted">Нет данных</p>
        </div>

        <div class="glass-card">
          <div class="card-header">
            <h3>Рейтинг эмитента</h3>
          </div>
          <div v-if="report.ratings?.issuer?.length" class="ratings-list">
            <div v-for="(r, idx) in report.ratings.issuer" :key="idx" class="rating-item">
              <span class="agency">{{ r.agency }}</span>
              <div class="rating-info">
                <span class="grade">{{ r.rating }}</span>
                <span class="outlook" v-if="r.outlook">{{ r.outlook }}</span>
              </div>
              <span class="date mono">{{ formatDate(r.date) }}</span>
            </div>
          </div>
          <p v-else class="muted">Нет данных</p>
        </div>

        <div class="glass-card">
          <div class="card-header">
            <h3>Рейтинг гаранта</h3>
          </div>
          <div v-if="report.ratings?.guarantor?.length" class="ratings-list">
            <div v-for="(r, idx) in report.ratings.guarantor" :key="idx" class="rating-item">
              <span class="agency">{{ r.agency }}</span>
              <span class="grade">{{ r.rating }}</span>
              <span class="date mono">{{ formatDate(r.date) }}</span>
            </div>
          </div>
          <p v-else class="muted">Нет данных</p>
        </div>
      </div>

      <!-- Market & Pricing Metrics -->
      <div class="grid-3">
        <div class="glass-card">
          <div class="card-header">
            <h3>Активность рынка</h3>
            <span class="status-badge fulfilled" v-if="report.market_activity?.is_active">АКТИВНЫЙ</span>
            <span class="status-badge inactive" v-else>НЕАКТИВНЫЙ</span>
          </div>
          <div class="metric-list">
            <div class="metric"><span>Кол-во торговых дней</span><span class="val">{{ report.market_activity?.trading_days ?? '—' }}</span></div>
            <div class="metric"><span>Кол-во сделок</span><span class="val">{{ report.market_activity?.trades ?? '—' }}</span></div>
            <div class="metric"><span>Объем торгов/выпуск</span><span class="val">{{ report.market_activity?.turnover_to_outstanding ? ((report.market_activity.turnover_to_outstanding * 100).toFixed(2) + '%') : '—' }}</span></div>
            <div class="metric"><span>Торги 30 дней</span><span class="val"><span v-if="report.market_activity?.traded_last_30d" class="status-badge fulfilled">Да</span><span v-else>Нет</span></span></div>
          </div>
        </div>

        <div class="glass-card">
          <div class="card-header">
            <h3>Котировка и доходность</h3>
          </div>
          <div class="metric-list">
            <div class="metric">
              <span>Чистая цена</span>
              <span class="val accent">
                <input v-if="editMode && editableReport?.pricing" v-model.number="editableReport.pricing.clean_price_pct" type="number" step="0.01" class="edit-input-inline" />
                <span v-else>{{ report.pricing?.clean_price_pct?.toFixed(2) }}%</span>
              </span>
            </div>
            <div class="metric">
              <span>{{ report.pricing?.yield_type || 'YTM' }}</span>
              <span class="val accent">
                <input v-if="editMode && editableReport?.pricing" v-model.number="editableReport.pricing.ytm" type="number" step="0.0001" class="edit-input-inline" />
                <span v-else>{{ report.pricing?.ytm_pct != null ? (report.pricing.ytm_pct.toFixed(2) + '%') : (report.pricing?.ytm ? ((report.pricing.ytm * 100).toFixed(2) + '%') : '—') }}</span>
              </span>
            </div>
            <div class="metric">
              <span>DM (Discount Margin)</span>
              <span class="val accent">{{ report.dm_bps != null ? (report.dm_bps.toFixed(2) + ' б.п.') : '—' }}</span>
            </div>
            <div class="metric">
              <span>QM (Quoted Margin)</span>
              <span class="val mono">{{ report.qm_bps != null ? (report.qm_bps.toFixed(2) + ' б.п.') : '—' }}</span>
            </div>
            <div class="metric">
              <span>G-spread</span>
              <span class="val mono">
                <input v-if="editMode && editableReport?.pricing" v-model.number="editableReport.pricing.g_spread_bps" type="number" class="edit-input-inline" />
                <span v-else>{{ report.pricing?.g_spread_bps ?? '—' }}<span v-if="report.pricing?.g_spread_bps"> bps</span></span>
              </span>
            </div>
            <div class="metric">
              <span>G-curve</span>
              <span class="val mono">
                <input v-if="editMode && editableReport?.pricing" v-model.number="editableReport.pricing.g_curve_yield" type="number" step="0.0001" class="edit-input-inline" />
                <span v-else>{{ report.pricing?.g_curve_pct != null ? (report.pricing.g_curve_pct.toFixed(2) + '%') : (report.pricing?.g_curve_yield ? ((report.pricing.g_curve_yield * 100).toFixed(2) + '%') : '—') }}</span>
              </span>
            </div>
            <div class="metric">
              <span>НКД</span>
              <span class="val mono">{{ report.nkd != null ? report.nkd.toFixed(2) : '—' }}</span>
            </div>
          </div>
          <p class="note-text">* Доходность, дюрация и следующий купон рассчитаны на основе рыночных значений форвардной кривой к ключевой ставке ЦБ РФ</p>
        </div>

        <div class="glass-card">
          <div class="card-header">
            <h3>Риск-метрики</h3>
          </div>
          <div class="metric-list">
            <div class="metric">
              <span>Мод. дюрация</span>
              <span class="val">
                <input v-if="editMode && editableReport?.risk_indicators" v-model.number="editableReport.risk_indicators.mod_duration" type="number" step="0.0001" class="edit-input-inline" />
                <span v-else>{{ report.risk_indicators?.mod_duration?.toFixed(4) || report.risk_indicators?.duration?.toFixed(4) || '—' }}</span>
              </span>
            </div>
            <div class="metric">
              <span>Дюрация</span>
              <span class="val">
                <input v-if="editMode && editableReport?.risk_indicators" v-model.number="editableReport.risk_indicators.duration" type="number" step="0.0001" class="edit-input-inline" />
                <span v-else>{{ report.risk_indicators?.duration?.toFixed(4) || '—' }}</span>
              </span>
            </div>
            <div class="metric">
              <span>Выпуклость</span>
              <span class="val">
                <input v-if="editMode && editableReport?.risk_indicators" v-model.number="editableReport.risk_indicators.convexity" type="number" step="0.01" class="edit-input-inline" />
                <span v-else>{{ report.risk_indicators?.convexity?.toFixed(2) || '—' }}</span>
              </span>
            </div>
            <div class="metric">
              <span>DV01</span>
              <span class="val">
                <input v-if="editMode && editableReport?.risk_indicators" v-model.number="editableReport.risk_indicators.dv01" type="number" step="0.01" class="edit-input-inline" />
                <span v-else>{{ formatNumber(report.risk_indicators?.dv01) }}</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- BLOCK 2: Price Chart -->
      <div class="glass-card full-width">
        <div class="chart-header">
          <h3>Динамика цен</h3>
          <button class="btn-export" @click="exportChart('price')">💾 PNG</button>
        </div>
        <div class="chart-container tall">
          <canvas ref="priceHistoryRef"></canvas>
        </div>
      </div>

      <!-- BLOCK 3: DM and QM Dynamics Chart -->
      <div class="glass-card full-width">
        <div class="chart-header">
          <h3>Динамика дисконтной маржи (DM) и фиксированной маржи (QM)</h3>
          <button class="btn-export" @click="exportChart('margin')">💾 PNG</button>
        </div>
        <div class="chart-container tall">
          <canvas ref="marginDynamicsRef"></canvas>
        </div>
      </div>

      <!-- Comparison with Indices -->
      <div class="glass-card full-width">
        <div class="card-header">
          <h3>Сравнение с индексами корпоративных облигаций Московской биржи</h3>
        </div>
        <div class="comparison-section">
          <table class="comparison-table">
            <thead>
              <tr>
                <th>Индекс</th>
                <th>Доходность, %</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Доходность индекса государственных облигаций</td>
                <td class="mono">{{ govIndexYield != null ? ((govIndexYield * 100).toFixed(2) + '%') : '—' }}</td>
              </tr>
              <tr>
                <td>Доходность индекса корпоративных облигаций с рейтингом ААА</td>
                <td class="mono">{{ report.indices?.corp_aaa != null ? ((report.indices.corp_aaa * 100).toFixed(2) + '%') : '—' }}</td>
              </tr>
              <tr>
                <td>Доходность индекса корпоративных облигаций с рейтингом АА</td>
                <td class="mono">{{ report.indices?.corp_aa != null ? ((report.indices.corp_aa * 100).toFixed(2) + '%') : '—' }}</td>
              </tr>
              <tr class="highlight-row">
                <td><strong>Оцениваемая облигация ({{ report.pricing?.yield_type || 'YTM' }})</strong></td>
                <td class="mono accent"><strong>{{ report.pricing?.ytm_pct != null ? (report.pricing.ytm_pct.toFixed(2) + '%') : (report.pricing?.ytm ? ((report.pricing.ytm * 100).toFixed(2) + '%') : '—') }}</strong></td>
              </tr>
              <tr>
                <td>Доходность индекса корпоративных облигаций с рейтингом А</td>
                <td class="mono">{{ report.indices?.corp_a != null ? ((report.indices.corp_a * 100).toFixed(2) + '%') : '—' }}</td>
              </tr>
              <tr>
                <td>Доходность индекса корпоративных облигаций с рейтингом ВВВ</td>
                <td class="mono">{{ report.indices?.corp_bbb != null ? ((report.indices.corp_bbb * 100).toFixed(2) + '%') : '—' }}</td>
              </tr>
            </tbody>
          </table>
          <div class="chart-container indices-chart">
            <canvas ref="indicesComparisonRef"></canvas>
          </div>
        </div>
      </div>

      <!-- BLOCK 5: Comparison with Analogous Bonds -->
      <div class="glass-card full-width">
        <div class="card-header">
          <h3>Сравнение с облигациями-аналогами</h3>
        </div>

        <!-- Input Section for Analogous Bonds -->
        <div class="analogous-input-section">
          <div class="glass-pill">
            <label class="lbl-mini">ISIN аналога:</label>
            <input
              v-model="newAnalogIsin"
              type="text"
              class="search-input"
              placeholder="RU000A10XXXX"
              @keyup.enter="addAnalogBond"
            />
            <button class="btn-search" @click="addAnalogBond" :disabled="!newAnalogIsin || loadingAnalogs">➕</button>
          </div>

          <!-- List of added analogs -->
          <div v-if="analogBondsList.length > 0" class="analogs-list">
            <div v-for="(bond, idx) in analogBondsList" :key="idx" class="analog-item">
              <span class="analog-isin mono">{{ bond.isin }}</span>
              <span class="analog-name">{{ bond.name || 'Загрузка...' }}</span>
              <button class="btn-remove" @click="removeAnalogBond(idx)" title="Удалить">×</button>
            </div>
          </div>
        </div>

        <div class="chart-container tall">
          <canvas ref="analogousBondsRef"></canvas>
        </div>
        <p v-if="report.analogous_bonds_note" class="note-text">{{ report.analogous_bonds_note }}</p>
      </div>

      <!-- BLOCK 6: Coupon Schedule -->
      <div class="glass-card full-width" v-if="report.coupon_schedule?.length">
        <div class="card-header">
          <h3>Купонное расписание (предстоящие)</h3>
          <span class="muted">{{ report.coupon_schedule.length }} выплат</span>
        </div>
        <div class="schedule-table-wrap">
          <table class="schedule-table">
            <thead>
              <tr>
                <th>Дата</th>
                <th>Ставка, %</th>
                <th>Сумма, руб.</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(cpn, idx) in report.coupon_schedule.slice(0, showAllCoupons ? undefined : 6)" :key="idx">
                <td class="mono">{{ formatDate(cpn.date) }}</td>
                <td class="mono">{{ cpn.valueprc ? cpn.valueprc.toFixed(2) : '—' }}</td>
                <td class="mono">{{ cpn.value ? cpn.value.toFixed(2) : '—' }}</td>
              </tr>
            </tbody>
          </table>
          <button
            v-if="report.coupon_schedule.length > 6"
            class="btn-show-more"
            @click="showAllCoupons = !showAllCoupons"
          >
            {{ showAllCoupons ? 'Свернуть' : `Показать все (${report.coupon_schedule.length})` }}
          </button>
        </div>
      </div>

      <!-- BLOCK 6b: Amortization Schedule -->
      <div class="glass-card full-width" v-if="report.amortization_schedule?.length">
        <div class="card-header">
          <h3>График амортизации</h3>
          <span class="muted">{{ report.amortization_schedule.length }} выплат</span>
        </div>
        <div class="schedule-table-wrap">
          <table class="schedule-table">
            <thead>
              <tr>
                <th>Дата</th>
                <th>% от номинала</th>
                <th>Сумма, руб.</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(amort, idx) in report.amortization_schedule" :key="idx">
                <td class="mono">{{ formatDate(amort.date) }}</td>
                <td class="mono">{{ amort.valueprc ? amort.valueprc.toFixed(2) + '%' : '—' }}</td>
                <td class="mono">{{ amort.value ? amort.value.toFixed(2) : '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- BLOCK 7: Corporate Events -->
      <div class="glass-card full-width">
        <div class="card-header">
          <h3>Корпоративные события</h3>
        </div>
        <div v-if="report.corporate_events?.length" class="events-list">
          <div v-for="(event, idx) in report.corporate_events" :key="idx" class="event-item">
            <span class="event-date mono">{{ formatDate(event.date) }}</span>
            <span class="event-description">{{ event.description }}</span>
          </div>
        </div>
        <p v-else class="muted">Нет данных о корпоративных событиях</p>
      </div>

    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Chart from 'chart.js/auto'
import * as XLSX from 'xlsx'
import {
  fetchFloaterBondReport,
  fetchAnalogBondData,
  type FloaterBondReport,
  type CouponPayment,
} from '@/services/bondReportService'

const route = useRoute()
const router = useRouter()

const isin = computed(() => (route.params.isin as string) || '')
const localIsin = ref(isin.value)

const govIndexYield = computed(() => {
  if (!report.value?.indices) return null
  const idx = report.value.indices
  return idx.gov_less_1y ?? idx.gov_1_3y ?? idx.gov_3_5y ?? idx.gov_5plus ?? null
})

const loading = ref(false)
const loadingMessage = ref('Загрузка данных...')
const error = ref<string | null>(null)
const report = ref<FloaterBondReport | null>(null)
const valuationDate = ref(new Date().toISOString().split('T')[0])
const editMode = ref(false)
const editableReport = ref<FloaterBondReport | null>(null)

// Analogous bonds management
const newAnalogIsin = ref('')
const loadingAnalogs = ref(false)
const analogBondsList = ref<Array<{
  isin: string
  name?: string
  duration?: number
  yield?: number
}>>([])

const showAllCoupons = ref(false)

const priceHistoryRef = ref<HTMLCanvasElement | null>(null)
const marginDynamicsRef = ref<HTMLCanvasElement | null>(null)
const indicesComparisonRef = ref<HTMLCanvasElement | null>(null)
const analogousBondsRef = ref<HTMLCanvasElement | null>(null)

let priceHistoryChart: Chart | null = null
let marginDynamicsChart: Chart | null = null
let indicesComparisonChart: Chart | null = null
let analogousBondsChart: Chart | null = null

const fetchReport = async (targetIsin: string) => {
  if (!targetIsin) return
  loading.value = true
  loadingMessage.value = 'Загрузка спецификации флоатера с MOEX ISS...'
  error.value = null
  report.value = null

  try {
    loadingMessage.value = 'Загрузка данных с MOEX ISS, ZCYC и RuData...'
    const result = await fetchFloaterBondReport(targetIsin, valuationDate.value)
    report.value = result
    setTimeout(() => initCharts(), 100)
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки данных'
    console.error('Floater bond report error:', e)
  } finally {
    loading.value = false
  }
}

const onChangeIsin = () => {
  if (!localIsin.value?.trim()) return
  router.push(`/floater-bond-report/${localIsin.value}`)
  fetchReport(localIsin.value)
}

const onValuationDateChange = () => {
  if (report.value?.isin) {
    fetchReport(report.value.isin)
  }
}

// Toggle edit mode
const toggleEditMode = () => {
  editMode.value = !editMode.value
  if (editMode.value && report.value) {
    editableReport.value = JSON.parse(JSON.stringify(report.value))
    if (editableReport.value && !editableReport.value.issue_info) {
      editableReport.value.issue_info = { issue_date: null, maturity_date: null, coupon_rate: null, coupon_per_year: null }
    }
    if (editableReport.value && !editableReport.value.pricing) {
      editableReport.value.pricing = { clean_price_pct: 0, ytm: 0, ytm_pct: 0, g_spread_bps: 0, g_curve_yield: 0, g_curve_pct: 0, yield_type: 'YTM' } as any
    }
    if (editableReport.value && !editableReport.value.risk_indicators) {
      editableReport.value.risk_indicators = { duration: 0, mod_duration: 0, convexity: 0, dv01: 0 }
    }
  } else if (!editMode.value && editableReport.value) {
    report.value = JSON.parse(JSON.stringify(editableReport.value))
  }
}

// Export to Excel
const exportToExcel = () => {
  const dataToExport = editMode.value && editableReport.value ? editableReport.value : report.value
  if (!dataToExport) return

  try {
    const data: any[][] = []
    data.push(['Отчет по облигации с плавающим купоном'])
    data.push(['Дата оценки:', valuationDate.value])
    data.push(['ISIN:', dataToExport.isin])
    data.push([])
    data.push(['ОБЩИЕ СВЕДЕНИЯ'])
    data.push(['Эмитент', dataToExport.issuer || ''])
    data.push(['ISIN', dataToExport.isin])
    data.push(['Страна риска', dataToExport.risk_country || ''])
    data.push(['Сектор', dataToExport.sector || ''])
    data.push(['Отрасль', dataToExport.industry || ''])
    data.push(['Кол-во выпусков в обращении', dataToExport.issues_count || ''])
    data.push([])
    data.push(['ИНФОРМАЦИЯ ПО ВЫПУСКУ'])
    data.push(['Дата выпуска', dataToExport.issue_info?.issue_date || ''])
    data.push(['Объем в обращении', dataToExport.outstanding_amount || ''])
    data.push(['Дата погашения', dataToExport.issue_info?.maturity_date || ''])
    data.push(['Купон', dataToExport.issue_info?.coupon_formula || ''])
    data.push(['Следующий купон', dataToExport.issue_info?.next_coupon ? (dataToExport.issue_info.next_coupon * 100).toFixed(2) + '%' : ''])
    data.push(['Номинал', dataToExport.issue_info?.nominal || ''])
    data.push(['Купонов в год', dataToExport.issue_info?.coupon_per_year || ''])
    data.push(['Анализируемый период', dataToExport.analysis_period || ''])
    data.push([])
    data.push(['КОТИРОВКА И ДОХОДНОСТЬ'])
    data.push(['Чистая цена', dataToExport.pricing?.clean_price_pct ? dataToExport.pricing.clean_price_pct.toFixed(2) + '%' : ''])
    data.push([dataToExport.pricing?.yield_type || 'YTM', dataToExport.pricing?.ytm_pct ? dataToExport.pricing.ytm_pct.toFixed(2) + '%' : (dataToExport.pricing?.ytm ? (dataToExport.pricing.ytm * 100).toFixed(2) + '%' : '')])
    data.push(['DM (Discount Margin)', dataToExport.dm_bps != null ? dataToExport.dm_bps.toFixed(2) + ' б.п.' : ''])
    data.push(['QM (Quoted Margin)', dataToExport.qm_bps != null ? dataToExport.qm_bps.toFixed(2) + ' б.п.' : ''])
    data.push(['G-spread', dataToExport.pricing?.g_spread_bps ? dataToExport.pricing.g_spread_bps + ' bps' : ''])
    data.push(['G-curve', dataToExport.pricing?.g_curve_pct ? dataToExport.pricing.g_curve_pct.toFixed(2) + '%' : (dataToExport.pricing?.g_curve_yield ? (dataToExport.pricing.g_curve_yield * 100).toFixed(2) + '%' : '')])
    data.push(['НКД', dataToExport.nkd != null ? dataToExport.nkd.toFixed(2) : ''])
    if (dataToExport.base_rate_name) {
      data.push(['Базовая ставка', `${dataToExport.base_rate_name}${dataToExport.base_rate_value != null ? ' (' + dataToExport.base_rate_value.toFixed(2) + '%)' : ''}`])
    }
    data.push([])
    data.push(['РИСК-МЕТРИКИ'])
    data.push(['Мод. дюрация', dataToExport.risk_indicators?.mod_duration?.toFixed(4) || ''])
    data.push(['Дюрация', dataToExport.risk_indicators?.duration?.toFixed(4) || ''])
    data.push(['Выпуклость', dataToExport.risk_indicators?.convexity?.toFixed(2) || ''])
    data.push(['DV01', dataToExport.risk_indicators?.dv01 || ''])
    data.push([])

    if (dataToExport.indices) {
      data.push(['СРАВНЕНИЕ С ИНДЕКСАМИ'])
      const govIdx = dataToExport.indices.gov_less_1y ?? dataToExport.indices.gov_1_3y ?? dataToExport.indices.gov_3_5y ?? dataToExport.indices.gov_5plus
      if (govIdx) data.push(['Индекс гос. облигаций', (govIdx * 100).toFixed(2) + '%'])
      if (dataToExport.indices.corp_aaa) data.push(['Индекс корп. облигаций (ААА)', (dataToExport.indices.corp_aaa * 100).toFixed(2) + '%'])
      if (dataToExport.indices.corp_aa) data.push(['Индекс корп. облигаций (АА)', (dataToExport.indices.corp_aa * 100).toFixed(2) + '%'])
      data.push([`Оцениваемая облигация (${dataToExport.pricing?.yield_type || 'YTM'})`, dataToExport.pricing?.ytm_pct ? dataToExport.pricing.ytm_pct.toFixed(2) + '%' : (dataToExport.pricing?.ytm ? (dataToExport.pricing.ytm * 100).toFixed(2) + '%' : '')])
      if (dataToExport.indices.corp_a) data.push(['Индекс корп. облигаций (А)', (dataToExport.indices.corp_a * 100).toFixed(2) + '%'])
      if (dataToExport.indices.corp_bbb) data.push(['Индекс корп. облигаций (ВВВ)', (dataToExport.indices.corp_bbb * 100).toFixed(2) + '%'])
      data.push([])
    }

    if (dataToExport.ratings?.issue?.length) {
      data.push(['РЕЙТИНГ ЭМИССИИ'])
      data.push(['Агентство', 'Рейтинг', 'Дата'])
      dataToExport.ratings.issue.forEach(r => data.push([r.agency, r.rating, r.date || '']))
      data.push([])
    }

    if (dataToExport.ratings?.issuer?.length) {
      data.push(['РЕЙТИНГ ЭМИТЕНТА'])
      data.push(['Агентство', 'Рейтинг', 'Прогноз', 'Дата'])
      dataToExport.ratings.issuer.forEach(r => data.push([r.agency, r.rating, r.outlook || '', r.date || '']))
      data.push([])
    }

    if (dataToExport.margin_history?.length) {
      data.push(['ДИНАМИКА DM/QM'])
      data.push(['Дата', 'DM (б.п.)', 'QM (б.п.)'])
      dataToExport.margin_history.forEach(m => data.push([m.date, m.dm?.toFixed(2) || '', m.qm?.toFixed(2) || '']))
      data.push([])
    }

    if (dataToExport.coupon_schedule?.length) {
      data.push(['КУПОННОЕ РАСПИСАНИЕ'])
      data.push(['Дата', 'Ставка, %', 'Сумма, руб.'])
      dataToExport.coupon_schedule.forEach(c => data.push([c.date || '', c.valueprc?.toFixed(2) || '', c.value?.toFixed(2) || '']))
      data.push([])
    }

    if (dataToExport.amortization_schedule?.length) {
      data.push(['ГРАФИК АМОРТИЗАЦИИ'])
      data.push(['Дата', '% от номинала', 'Сумма, руб.'])
      dataToExport.amortization_schedule.forEach(a => data.push([a.date || '', a.valueprc?.toFixed(2) || '', a.value?.toFixed(2) || '']))
      data.push([])
    }

    if (dataToExport.corporate_events?.length) {
      data.push(['КОРПОРАТИВНЫЕ СОБЫТИЯ'])
      data.push(['Дата', 'Описание'])
      dataToExport.corporate_events.forEach(ev => data.push([ev.date || '', ev.description]))
    }

    const ws = XLSX.utils.aoa_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Отчет')
    ws['!cols'] = [{ wch: 45 }, { wch: 30 }]

    const fileName = `Floater_Bond_Report_${dataToExport.isin}_${valuationDate.value}.xlsx`
    XLSX.writeFile(wb, fileName)
  } catch (err: any) {
    console.error('Export error:', err)
    alert(`Ошибка при экспорте: ${err.message}`)
  }
}

const formatDate = (dateStr?: string | null): string => {
  if (!dateStr) return '—'
  try {
    const date = new Date(dateStr)
    const day = String(date.getDate()).padStart(2, '0')
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const year = date.getFullYear()
    return `${day}.${month}.${year}`
  } catch {
    return dateStr
  }
}

const formatNumber = (num?: number | null): string => {
  if (num === undefined || num === null) return '—'
  return new Intl.NumberFormat('ru-RU').format(num)
}

const initCharts = () => {
  if (priceHistoryChart) priceHistoryChart.destroy()
  if (marginDynamicsChart) marginDynamicsChart.destroy()
  if (indicesComparisonChart) indicesComparisonChart.destroy()
  if (analogousBondsChart) analogousBondsChart.destroy()

  // Price History Chart — real data
  if (priceHistoryRef.value?.getContext('2d') && report.value?.price_history?.length) {
    const ph = report.value.price_history
    const labels = ph.map(p => {
      const d = new Date(p.date)
      return `${String(d.getDate()).padStart(2, '0')}.${String(d.getMonth() + 1).padStart(2, '0')}.${d.getFullYear()}`
    })
    const prices = ph.map(p => p.price)

    priceHistoryChart = new Chart(priceHistoryRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Цена, %',
          data: prices,
          borderColor: '#60a5fa',
          backgroundColor: 'rgba(96, 165, 250, 0.08)',
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          filler: { propagate: true }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 }, maxTicksLimit: 12 }
          },
          y: {
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } },
            title: {
              display: true,
              text: 'Цена, %',
              color: 'rgba(255,255,255,0.5)',
              font: { size: 11 }
            }
          }
        }
      }
    } as any)
  }

  // Margin Dynamics Chart (DM and QM) — real data
  if (marginDynamicsRef.value?.getContext('2d') && report.value?.margin_history?.length) {
    const mh = report.value.margin_history
    const labels = mh.map(p => {
      const d = new Date(p.date)
      return `${String(d.getDate()).padStart(2, '0')}.${String(d.getMonth() + 1).padStart(2, '0')}.${d.getFullYear()}`
    })
    const dm = mh.map(p => p.dm)
    const qm = mh.map(p => p.qm)

    marginDynamicsChart = new Chart(marginDynamicsRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'DM (дисконтная маржа)',
            data: dm,
            borderColor: '#60a5fa',
            backgroundColor: 'rgba(96, 165, 250, 0.08)',
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            borderWidth: 2
          },
          {
            label: 'QM (фиксированная маржа)',
            data: qm,
            borderColor: '#f59e0b',
            backgroundColor: 'transparent',
            fill: false,
            tension: 0.4,
            pointRadius: 0,
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: {
            display: true,
            labels: {
              color: 'rgba(255,255,255,0.6)',
              font: { size: 11 },
              usePointStyle: true
            },
            position: 'top'
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 }, maxTicksLimit: 12 }
          },
          y: {
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } },
            title: {
              display: true,
              text: 'б.п.',
              color: 'rgba(255,255,255,0.5)',
              font: { size: 11 }
            }
          }
        }
      }
    } as any)
  }

  // Indices Comparison Chart
  if (indicesComparisonRef.value?.getContext('2d') && report.value?.indices && report.value?.pricing) {
    const indices = report.value.indices
    const bondYtm = report.value.pricing.ytm_pct ?? ((report.value.pricing.ytm || 0) * 100)
    const govYield = (indices.gov_less_1y ?? indices.gov_1_3y ?? indices.gov_3_5y ?? indices.gov_5plus ?? 0) * 100
    const bondLabel = `Оцениваемая облигация (${report.value.pricing.yield_type || 'YTM'})`

    const dataPoints = [
      { label: 'Индекс гос. облигаций', value: govYield, color: '#9ca3af' },
      { label: 'Индекс корп. облигаций (ААА)', value: (indices.corp_aaa || 0) * 100, color: '#9ca3af' },
      { label: 'Индекс корп. облигаций (АА)', value: (indices.corp_aa || 0) * 100, color: '#9ca3af' },
      { label: bondLabel, value: bondYtm, color: '#ef4444' },
      { label: 'Индекс корп. облигаций (А)', value: (indices.corp_a || 0) * 100, color: '#9ca3af' },
      { label: 'Индекс корп. облигаций (ВВВ)', value: (indices.corp_bbb || 0) * 100, color: '#9ca3af' }
    ].filter(p => p.value > 0)

    indicesComparisonChart = new Chart(indicesComparisonRef.value.getContext('2d') as any, {
      type: 'scatter',
      data: {
        datasets: dataPoints.map((point) => ({
          label: point.label,
          data: [{ x: point.value, y: 0 }],
          backgroundColor: point.label.startsWith('Оцениваемая облигация') ? 'rgba(239, 68, 68, 0)' : point.color,
          borderColor: point.label.startsWith('Оцениваемая облигация') ? 'rgba(239, 68, 68, 0)' : point.color,
          pointRadius: point.label.startsWith('Оцениваемая облигация') ? 1 : 10,
          pointHoverRadius: point.label.startsWith('Оцениваемая облигация') ? 14 : 12,
          showLine: false
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 0 },
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            displayColors: false,
            backgroundColor: 'rgba(0, 0, 0, 0.9)',
            titleColor: 'rgba(255, 255, 255, 1)',
            bodyColor: 'rgba(255, 255, 255, 0.9)',
            borderColor: 'rgba(255, 255, 255, 0.3)',
            borderWidth: 1,
            padding: 14,
            titleFont: { size: 13, weight: 'bold' },
            bodyFont: { size: 12 },
            cornerRadius: 8,
            callbacks: {
              title: (context: any) => dataPoints[context[0].datasetIndex]?.label || '',
              label: (context: any) => `Доходность: ${dataPoints[context.datasetIndex]?.value.toFixed(2)}%`
            }
          }
        },
        scales: {
          x: {
            type: 'linear',
            position: 'bottom',
            grid: { color: 'rgba(255,255,255,0.05)', display: true },
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 }, stepSize: 1 },
            title: {
              display: true,
              text: 'Доходность, %',
              color: 'rgba(255,255,255,0.5)',
              font: { size: 11 }
            }
          },
          y: {
            type: 'linear',
            min: -0.5,
            max: 0.5,
            display: false,
            grid: { display: false },
            ticks: { display: false }
          }
        }
      },
      plugins: [{
        id: 'indicesTimeline',
        afterDraw: (chart: any) => {
          const ctx = chart.ctx
          const chartArea = chart.chartArea
          const yCenter = (chartArea.top + chartArea.bottom) / 2
          const barHeight = 40
          ctx.save()
          ctx.fillStyle = 'rgba(245, 245, 220, 0.3)'
          ctx.fillRect(chartArea.left, yCenter - barHeight / 2, chartArea.right - chartArea.left, barHeight)
          ctx.restore()
        }
      }, {
        id: 'blinkingRedPoint',
        afterDraw: (chart: any) => {
          const ctx = chart.ctx
          const redIdx = dataPoints.findIndex(p => p.label.startsWith('Оцениваемая облигация'))
          if (redIdx < 0) return
          const meta = chart.getDatasetMeta(redIdx)
          if (!meta?.data?.length) return
          const view = meta.data[0].getProps(['x', 'y'], true)
          const time = Date.now() / 1000
          const blink = Math.sin(time * 3) * 0.5 + 0.5
          const alpha = 0.5 + blink * 0.5
          const radius = 10 + blink * 4
          const gradient = ctx.createRadialGradient(view.x, view.y, 0, view.x, view.y, radius * 2)
          gradient.addColorStop(0, `rgba(239, 68, 68, ${alpha * 0.4})`)
          gradient.addColorStop(0.5, `rgba(239, 68, 68, ${alpha * 0.2})`)
          gradient.addColorStop(1, 'rgba(239, 68, 68, 0)')
          ctx.save()
          ctx.fillStyle = gradient
          ctx.beginPath()
          ctx.arc(view.x, view.y, radius * 2, 0, Math.PI * 2)
          ctx.fill()
          ctx.fillStyle = `rgba(239, 68, 68, ${alpha})`
          ctx.strokeStyle = `rgba(255, 255, 255, ${alpha * 0.9})`
          ctx.lineWidth = 2
          ctx.beginPath()
          ctx.arc(view.x, view.y, radius, 0, Math.PI * 2)
          ctx.fill()
          ctx.stroke()
          ctx.restore()
        }
      }]
    } as any)

    let indicesAnimationFrameId: number | null = null
    let isIndicesAnimating = true
    const animateIndices = () => {
      if (indicesComparisonChart && isIndicesAnimating) {
        try {
          indicesComparisonChart.draw()
          if (isIndicesAnimating) {
            indicesAnimationFrameId = requestAnimationFrame(animateIndices)
          }
        } catch (e) {
          isIndicesAnimating = false
        }
      }
    }
    animateIndices()

    if (indicesComparisonChart) {
      const chartRef = indicesComparisonChart as any
      chartRef.__animationFrameId = indicesAnimationFrameId
      chartRef.__stopAnimation = () => {
        isIndicesAnimating = false
        if (typeof chartRef.__animationFrameId === 'number') {
          cancelAnimationFrame(chartRef.__animationFrameId)
        }
      }
    }
  }

  // Analogous Bonds Scatter Chart
  if (analogousBondsRef.value?.getContext('2d') && report.value?.risk_indicators && report.value?.pricing) {
    const analogous = analogBondsList.value.filter(b => b.duration !== undefined && b.yield !== undefined)
    const bondDuration = report.value.risk_indicators.duration || 0
    const bondYield = (report.value.pricing.ytm || 0) * 100
    const bondName = report.value.issuer || 'Оцениваемая облигация'

    const datasets: any[] = []

    if (analogous.length > 0) {
      datasets.push({
        label: 'Облигации-аналоги',
        data: analogous.map(b => ({ x: b.duration!, y: b.yield! })),
        backgroundColor: 'rgba(96, 165, 250, 0.6)',
        borderColor: '#60a5fa',
        pointRadius: 8,
        pointStyle: 'diamond',
        borderWidth: 2
      })
    }

    datasets.push({
      label: bondName,
      data: [{ x: bondDuration, y: bondYield }],
      backgroundColor: '#ef4444',
      borderColor: '#ef4444',
      pointRadius: 10,
      pointStyle: 'diamond',
      borderWidth: 2,
      pointHoverRadius: 12
    })

    analogousBondsChart = new Chart(analogousBondsRef.value.getContext('2d') as any, {
      type: 'scatter',
      data: { datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 0 },
        plugins: {
          legend: {
            display: true,
            labels: {
              color: 'rgba(255,255,255,0.6)',
              font: { size: 11 },
              usePointStyle: true
            },
            position: 'top'
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } },
            title: {
              display: true,
              text: 'Дюрация, лет',
              color: 'rgba(255,255,255,0.5)',
              font: { size: 11 }
            }
          },
          y: {
            grid: { color: 'rgba(255,255,255,0.05)' },
            ticks: { color: 'rgba(255,255,255,0.3)', font: { size: 11 } },
            title: {
              display: true,
              text: 'Доходность к оферте/погашению, %',
              color: 'rgba(255,255,255,0.5)',
              font: { size: 11 }
            }
          }
        }
      },
      plugins: [{
        id: 'blinkingPoint',
        afterDraw: (chart: any) => {
          const ctx = chart.ctx
          const currentBondDatasetIndex = chart.data.datasets.length - 1
          const meta = chart.getDatasetMeta(currentBondDatasetIndex)
          if (!meta?.data?.length) return
          const point = meta.data[0]
          const view = point.getProps(['x', 'y'], true)
          const time = Date.now() / 1000
          const blink = Math.sin(time * 3) * 0.5 + 0.5
          const alpha = 0.4 + blink * 0.6
          const radius = 10 + blink * 5
          const gradient = ctx.createRadialGradient(view.x, view.y, 0, view.x, view.y, radius * 2.5)
          gradient.addColorStop(0, `rgba(239, 68, 68, ${alpha * 0.5})`)
          gradient.addColorStop(0.4, `rgba(239, 68, 68, ${alpha * 0.2})`)
          gradient.addColorStop(1, 'rgba(239, 68, 68, 0)')
          ctx.save()
          ctx.fillStyle = gradient
          ctx.beginPath()
          ctx.arc(view.x, view.y, radius * 2.5, 0, Math.PI * 2)
          ctx.fill()
          ctx.fillStyle = `rgba(239, 68, 68, ${alpha})`
          ctx.strokeStyle = `rgba(255, 255, 255, ${alpha * 0.8})`
          ctx.lineWidth = 2
          ctx.beginPath()
          ctx.arc(view.x, view.y, radius, 0, Math.PI * 2)
          ctx.fill()
          ctx.stroke()
          ctx.restore()
        }
      }]
    } as any)

    let animationFrameId: number | null = null
    let isAnimating = true
    const animate = () => {
      if (analogousBondsChart && isAnimating) {
        try {
          analogousBondsChart.draw()
          if (isAnimating) {
            animationFrameId = requestAnimationFrame(animate)
          }
        } catch (e) {
          isAnimating = false
        }
      }
    }
    animate()

    if (analogousBondsChart) {
      const chartRef = analogousBondsChart as any
      chartRef.__animationFrameId = animationFrameId
      chartRef.__stopAnimation = () => {
        isAnimating = false
        if (typeof chartRef.__animationFrameId === 'number') {
          cancelAnimationFrame(chartRef.__animationFrameId)
        }
      }
    }
  }
}

// Analogous bonds — real API
const addAnalogBond = async () => {
  if (!newAnalogIsin.value?.trim()) return

  const analogIsin = newAnalogIsin.value.trim().toUpperCase()

  if (analogBondsList.value.some(b => b.isin === analogIsin)) {
    error.value = 'Облигация с таким ISIN уже добавлена'
    setTimeout(() => { error.value = null }, 3000)
    return
  }

  loadingAnalogs.value = true
  analogBondsList.value.push({ isin: analogIsin, name: undefined, duration: undefined, yield: undefined })
  newAnalogIsin.value = ''

  try {
    const bondData = await fetchAnalogBondData(analogIsin, valuationDate.value)

    const index = analogBondsList.value.findIndex(b => b.isin === analogIsin)
    if (index !== -1) {
      if (bondData) {
        analogBondsList.value[index] = {
          isin: analogIsin,
          name: bondData.name,
          duration: bondData.duration,
          yield: bondData.yield,
        }
      } else {
        analogBondsList.value[index].name = `${analogIsin} (нет данных)`
      }
    }

    if (report.value) {
      report.value.analogous_bonds = analogBondsList.value
        .filter(b => b.duration !== undefined && b.yield !== undefined)
        .map(b => ({ name: b.name || b.isin, duration: b.duration!, yield: b.yield! }))

      setTimeout(() => {
        if (analogousBondsChart) analogousBondsChart.destroy()
        initCharts()
      }, 100)
    }
  } catch (e) {
    const index = analogBondsList.value.findIndex(b => b.isin === analogIsin)
    if (index !== -1) analogBondsList.value.splice(index, 1)
    error.value = `Ошибка загрузки данных по ISIN ${analogIsin}`
    setTimeout(() => { error.value = null }, 3000)
  } finally {
    loadingAnalogs.value = false
  }
}

const removeAnalogBond = (index: number) => {
  analogBondsList.value.splice(index, 1)

  if (report.value) {
    report.value.analogous_bonds = analogBondsList.value
      .filter(b => b.duration !== undefined && b.yield !== undefined)
      .map(b => ({ name: b.name || b.isin, duration: b.duration!, yield: b.yield! }))

    setTimeout(() => {
      if (analogousBondsChart) analogousBondsChart.destroy()
      initCharts()
    }, 100)
  }
}

const exportChart = (name: 'price' | 'margin') => {
  const canvas = name === 'price' ? priceHistoryRef.value : marginDynamicsRef.value
  if (!canvas) return
  const link = document.createElement('a')
  link.href = canvas.toDataURL('image/png')
  link.download = `floater-bond-${name}-${new Date().toISOString().split('T')[0]}.png`
  link.click()
}

onMounted(() => {
  if (isin.value) {
    fetchReport(isin.value)
  } else {
    fetchReport('RU000A108VW7')
  }
})

onBeforeUnmount(() => {
  if (priceHistoryChart) priceHistoryChart.destroy()
  if (marginDynamicsChart) marginDynamicsChart.destroy()
  if (indicesComparisonChart) {
    const stop = (indicesComparisonChart as any).__stopAnimation
    if (typeof stop === 'function') stop()
    indicesComparisonChart.destroy()
  }
  if (analogousBondsChart) {
    const stop = (analogousBondsChart as any).__stopAnimation
    if (typeof stop === 'function') stop()
    analogousBondsChart.destroy()
  }
})
</script>

<style scoped>
* { box-sizing: border-box; }

.page-container {
  padding: 24px 32px;
  max-width: 1600px;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.glass-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.glass-card:hover { background: rgba(40, 45, 55, 0.5); border-color: rgba(255, 255, 255, 0.12); box-shadow: 0 25px 50px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.15); }
.glass-card.error { color: #ef4444; background: rgba(239, 68, 68, 0.05); border-color: rgba(239, 68, 68, 0.2); }

.glass-pill { display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(20px) saturate(180%); -webkit-backdrop-filter: blur(20px) saturate(180%); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1); }
.glass-pill:hover { background: rgba(255, 255, 255, 0.08); border-color: rgba(255, 255, 255, 0.15); }

.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px; flex-shrink: 0; }
.header-left { flex: 1; }
.section-title { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; }
.section-subtitle { font-size: 13px; color: rgba(255, 255, 255, 0.5); margin: 4px 0 0 0; }
.header-actions { display: flex; gap: 12px; }

.search-input { flex: 1; background: transparent; border: none; color: #fff; font-size: 13px; outline: none; padding: 4px; font-family: 'SF Mono', monospace; transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1); }
.search-input::placeholder { color: rgba(255, 255, 255, 0.3); }
.search-input:focus { color: rgba(255, 255, 255, 0.95); }

.btn-search { background: transparent; border: none; color: #3b82f6; cursor: pointer; font-size: 14px; padding: 4px 8px; border-radius: 6px; transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1); display: flex; align-items: center; justify-content: center; }
.btn-search:hover:not(:disabled) { color: #60a5fa; background: rgba(59, 130, 246, 0.1); transform: scale(1.05); }
.btn-search:disabled { opacity: 0.5; cursor: not-allowed; }
.lbl-mini { font-size: 10px; color: rgba(255,255,255,0.5); font-weight: 600; text-transform: uppercase; }

.date-input-small { background: transparent; border: none; color: #fff; font-size: 12px; outline: none; padding: 4px 8px; cursor: pointer; font-family: inherit; min-width: 140px; }
.date-input-small::-webkit-calendar-picker-indicator { filter: invert(1); cursor: pointer; }

.btn-toggle-edit { padding: 8px 16px; background: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 8px; font-weight: 600; font-size: 12px; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.btn-toggle-edit:hover { background: rgba(34, 197, 94, 0.25); border-color: rgba(34, 197, 94, 0.5); transform: translateY(-1px); }
.btn-toggle-edit.active { background: rgba(34, 197, 94, 0.3); border-color: rgba(34, 197, 94, 0.5); color: #4ade80; }

.btn-export-excel { padding: 8px 16px; background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; font-weight: 600; font-size: 12px; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.btn-export-excel:hover:not(:disabled) { background: rgba(245, 158, 11, 0.25); border-color: rgba(245, 158, 11, 0.5); transform: translateY(-1px); }
.btn-export-excel:disabled { opacity: 0.5; cursor: not-allowed; }

.edit-input { width: 100%; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 6px; color: #fff; padding: 4px 8px; font-size: 12px; outline: none; transition: all 0.2s; }
.edit-input:focus { background: rgba(59, 130, 246, 0.15); border-color: rgba(59, 130, 246, 0.5); box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }
.edit-input-inline { width: 120px; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 6px; color: #fff; padding: 4px 8px; font-size: 12px; outline: none; transition: all 0.2s; text-align: right; }
.edit-input-inline:focus { background: rgba(59, 130, 246, 0.15); border-color: rgba(59, 130, 246, 0.5); box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }

.report-content { display: flex; flex-direction: column; gap: 20px; }
.state-section { display: flex; justify-content: center; align-items: center; min-height: 300px; }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.full-width { grid-column: 1 / -1; }

.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.card-header h3 { font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.6); text-transform: uppercase; margin: 0; letter-spacing: 0.05em; }

.info-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.info-table td { padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); color: rgba(255, 255, 255, 0.9); transition: color 0.2s cubic-bezier(0.2, 0.8, 0.2, 1); }
.info-table tr:hover td { color: rgba(255, 255, 255, 0.95); }
.info-table tr:last-child td { border-bottom: none; }
.info-table td:first-child { color: rgba(255, 255, 255, 0.5); width: 40%; font-weight: 500; }
.info-table td:last-child { text-align: right; font-weight: 500; }

.metric-list { display: flex; flex-direction: column; gap: 8px; }
.metric { display: flex; justify-content: space-between; font-size: 12px; padding-bottom: 6px; border-bottom: 1px dashed rgba(255, 255, 255, 0.08); transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1); }
.metric:last-child { border-bottom: none; }
.metric > span:first-child { color: rgba(255, 255, 255, 0.5); font-weight: 500; }
.val { color: #fff; font-weight: 600; }

.ratings-list { display: flex; flex-direction: column; gap: 6px; }
.rating-item { display: flex; justify-content: space-between; align-items: center; font-size: 12px; gap: 8px; padding: 8px; background: rgba(255, 255, 255, 0.02); backdrop-filter: blur(10px) saturate(180%); -webkit-backdrop-filter: blur(10px) saturate(180%); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1); }
.rating-item:hover { background: rgba(255, 255, 255, 0.04); border-color: rgba(255, 255, 255, 0.08); }
.rating-info { display: flex; flex-direction: column; align-items: flex-start; gap: 2px; }
.agency { color: rgba(255,255,255,0.4); font-size: 10px; font-weight: 500; }
.grade { font-weight: 700; color: #fff; }
.outlook { font-size: 10px; color: rgba(255, 255, 255, 0.4); }
.date { font-size: 10px; color: rgba(255, 255, 255, 0.3); }

.status-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; text-transform: uppercase; }
.status-badge.fulfilled { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
.status-badge.inactive { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

.note-text { margin-top: 16px; font-size: 10px; color: rgba(255, 255, 255, 0.4); font-style: italic; }

.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.chart-container { position: relative; width: 100%; height: 360px; background: rgba(0, 0, 0, 0.2); backdrop-filter: blur(20px) saturate(180%); -webkit-backdrop-filter: blur(20px) saturate(180%); border-radius: 12px; padding: 12px; border: 1px solid rgba(255, 255, 255, 0.05); transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1); }
.chart-container.tall { height: 480px; }
.chart-container.indices-chart { height: 200px; }
.chart-container canvas { width: 100% !important; height: 100% !important; }

.btn-export { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px) saturate(180%); -webkit-backdrop-filter: blur(10px) saturate(180%); border: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); padding: 6px 12px; border-radius: 6px; font-size: 11px; cursor: pointer; transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1); font-weight: 500; }
.btn-export:hover { background: rgba(255, 255, 255, 0.1); border-color: rgba(255, 255, 255, 0.2); color: #fff; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); }

.mono { font-family: 'SF Mono', monospace; }
.accent { color: #38bdf8; font-weight: 600; }
.text-accent { color: #38bdf8; font-weight: 600; }
.muted { color: rgba(255, 255, 255, 0.4); margin: 0; font-size: 12px; }
.spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(56, 189, 248, 0.3); border-top-color: #38bdf8; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; }
@keyframes spin { to { transform: rotate(360deg); } }

.schedule-table-wrap { max-height: 400px; overflow-y: auto; }
.schedule-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.schedule-table thead th { text-align: left; padding: 10px 16px; color: rgba(255, 255, 255, 0.5); font-weight: 600; text-transform: uppercase; font-size: 10px; letter-spacing: 0.05em; border-bottom: 1px solid rgba(255, 255, 255, 0.1); position: sticky; top: 0; background: rgba(30, 32, 40, 0.95); z-index: 1; }
.schedule-table tbody td { padding: 8px 16px; color: rgba(255, 255, 255, 0.9); border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
.schedule-table tbody tr:hover td { background: rgba(255, 255, 255, 0.03); }
.btn-show-more { display: block; width: 100%; margin-top: 8px; padding: 8px; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px; color: rgba(255, 255, 255, 0.5); font-size: 11px; cursor: pointer; transition: all 0.2s; }
.btn-show-more:hover { background: rgba(255, 255, 255, 0.06); color: rgba(255, 255, 255, 0.7); }

.comparison-section { display: flex; flex-direction: column; gap: 24px; }
.comparison-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.comparison-table thead th { text-align: left; padding: 12px 16px; color: rgba(255, 255, 255, 0.5); font-weight: 600; text-transform: uppercase; font-size: 10px; letter-spacing: 0.05em; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
.comparison-table tbody td { padding: 12px 16px; color: rgba(255, 255, 255, 0.9); border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
.comparison-table tbody tr:last-child td { border-bottom: none; }
.comparison-table tbody tr.highlight-row { background: rgba(239, 68, 68, 0.1); }
.comparison-table tbody tr.highlight-row td { color: #fff; font-weight: 600; }

.events-list { display: flex; flex-direction: column; gap: 12px; }
.event-item { display: flex; gap: 16px; padding: 12px; background: rgba(255, 255, 255, 0.02); backdrop-filter: blur(10px) saturate(180%); -webkit-backdrop-filter: blur(10px) saturate(180%); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1); }
.event-item:hover { background: rgba(255, 255, 255, 0.04); border-color: rgba(255, 255, 255, 0.08); }
.event-date { color: rgba(255, 255, 255, 0.5); font-size: 11px; font-weight: 600; min-width: 100px; flex-shrink: 0; }
.event-description { color: rgba(255, 255, 255, 0.9); font-size: 12px; line-height: 1.5; flex: 1; }

.analogous-input-section { display: flex; flex-direction: column; gap: 16px; margin-bottom: 20px; padding: 16px; background: rgba(255, 255, 255, 0.02); backdrop-filter: blur(10px) saturate(180%); -webkit-backdrop-filter: blur(10px) saturate(180%); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; }
.analogs-list { display: flex; flex-direction: column; gap: 8px; }
.analog-item { display: flex; align-items: center; gap: 12px; padding: 10px 12px; background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px) saturate(180%); -webkit-backdrop-filter: blur(10px) saturate(180%); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1); }
.analog-item:hover { background: rgba(255, 255, 255, 0.05); border-color: rgba(255, 255, 255, 0.12); }
.analog-isin { color: rgba(255, 255, 255, 0.7); font-size: 11px; font-weight: 600; min-width: 120px; flex-shrink: 0; }
.analog-name { color: rgba(255, 255, 255, 0.9); font-size: 12px; flex: 1; }
.btn-remove { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #f87171; width: 24px; height: 24px; border-radius: 50%; cursor: pointer; font-size: 18px; line-height: 1; display: flex; align-items: center; justify-content: center; transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1); flex-shrink: 0; padding: 0; }
.btn-remove:hover { background: rgba(239, 68, 68, 0.2); border-color: rgba(239, 68, 68, 0.5); color: #ef4444; transform: scale(1.1); }

@media (max-width: 1200px) { .grid-3 { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 1024px) { .section-header { flex-direction: column; align-items: flex-start; gap: 16px; } .header-actions { width: 100%; flex-wrap: wrap; } .glass-pill { width: 100%; } .search-input { flex: 1; } .grid-2, .grid-3 { grid-template-columns: 1fr; } .comparison-section { gap: 16px; } }
@media (max-width: 768px) { .page-container { padding: 16px; } .section-title { font-size: 20px; } .chart-container { height: 300px; } .chart-container.tall { height: 400px; } .chart-container.indices-chart { height: 180px; } .rating-item, .metric { flex-direction: column; align-items: flex-start; gap: 4px; } .val { text-align: left; } .comparison-table { font-size: 11px; } .comparison-table thead th, .comparison-table tbody td { padding: 8px 12px; } .analogous-input-section { padding: 12px; } .analog-item { flex-wrap: wrap; padding: 8px; } .analog-isin { min-width: 100px; font-size: 10px; } .analog-name { font-size: 11px; } .events-list { gap: 8px; } .event-item { flex-direction: column; gap: 8px; padding: 10px; } .event-date { min-width: auto; } }
@media (max-width: 480px) { .page-container { padding: 12px; } .section-title { font-size: 18px; } .chart-container { height: 250px; } .chart-container.tall { height: 300px; } .chart-container.indices-chart { height: 150px; } .info-table { font-size: 10px; } .comparison-table { font-size: 10px; } .comparison-table thead th, .comparison-table tbody td { padding: 6px 8px; } .status-badge { font-size: 9px; padding: 3px 6px; } .note-text { font-size: 9px; } }
</style>
