/**
 * Сервис для генерации отчётов по облигациям (Bond Report).
 *
 * Объединяет данные из:
 *  - MOEX ISS API (напрямую) — спецификация, история торгов, индексы, корп. события
 *  - Backend /api/bond — DCF-оценка, YTM, дюрация, выпуклость, DV01
 *  - Backend /api/zcyc — КБД (кривая бескупонных доходностей) для G-curve / G-spread
 *  - Backend /api/rudata — рейтинги, fintool reference, расчёт для аналогов
 *
 * Логика вычислений соответствует Excel-шаблонам:
 *  - «Автоматизированный шаблон.xlsm» → VanilaBondReport
 *  - «Автоматизированный шаблон (для флоатеров).xlsm» + «Расчёт доходности флоатера.xlsm» → FloaterBondReport
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
const MOEX_ISS = 'https://iss.moex.com/iss'

// ─── Типы ──────────────────────────────────────────────────────────────────────

export interface RatingEntry {
  agency: string
  rating: string
  outlook?: string | null
  date?: string | null
}

export interface MarketActivityData {
  trading_days: number
  trades: number
  turnover_to_outstanding: number
  traded_last_30d: boolean
  avg_volume_per_day?: number
  total_volume?: number
  is_active: boolean
}

export interface PricingData {
  clean_price_pct: number
  dirty_price?: number
  ytm: number
  g_spread_bps: number
  g_curve_yield: number
}

export interface RiskIndicators {
  duration: number
  mod_duration: number
  convexity: number
  dv01: number
  pvbp?: number
}

export interface IssueInfo {
  issue_date: string | null
  maturity_date: string | null
  coupon_rate: number | null
  coupon_per_year: number | null
  coupon_formula?: string | null
  next_coupon?: number | null
  nominal?: number | null
}

export interface CorporateEvent {
  date: string | null
  description: string
}

export interface AnalogousBond {
  isin?: string
  name: string
  duration: number
  yield: number
}

export interface IndexYields {
  gov_less_1y?: number
  gov_1_3y?: number
  corp_aaa?: number
  corp_aa?: number
  corp_a?: number
  corp_bbb?: number
  corp_aaa_1_3y?: number
  corp_aa_1_3y?: number
  corp_a_1_3y?: number
}

export interface PriceHistoryPoint {
  date: string
  price: number
}

export interface YieldHistoryPoint {
  date: string
  ytm: number
  gcurve: number
  gspread: number
}

export interface MarginHistoryPoint {
  date: string
  dm: number
  qm: number
}

export interface VanillaBondReport {
  isin: string
  issuer: string
  risk_country: string | null
  sector: string | null
  industry: string | null
  outstanding_amount: number | null
  issue_info: IssueInfo
  ratings: {
    issue: RatingEntry[]
    issuer: RatingEntry[]
    guarantor: RatingEntry[]
  }
  market_activity: MarketActivityData
  pricing: PricingData
  risk_indicators: RiskIndicators
  indices: IndexYields
  corporate_events: CorporateEvent[]
  price_history: PriceHistoryPoint[]
  yield_history: YieldHistoryPoint[]
  analogous_bonds: AnalogousBond[]
}

export interface FloaterBondReport extends VanillaBondReport {
  issues_count: number | null
  analysis_period: string | null
  coupon_formula: string | null
  margin_history: MarginHistoryPoint[]
  analogous_bonds_note?: string
}

// ─── MOEX ISS helpers ──────────────────────────────────────────────────────────

async function moexRequest(endpoint: string, params: Record<string, string> = {}): Promise<any> {
  const url = new URL(`${MOEX_ISS}${endpoint}.json`)
  url.searchParams.set('iss.json', 'extended')
  url.searchParams.set('iss.meta', 'off')
  url.searchParams.set('lang', 'ru')
  for (const [k, v] of Object.entries(params)) {
    url.searchParams.set(k, v)
  }

  const resp = await fetch(url.toString())
  if (!resp.ok) throw new Error(`MOEX ISS ${resp.status}: ${endpoint}`)
  return resp.json()
}

function parseISSTable(response: any, tableName: string): Record<string, any>[] {
  if (!response || !response[1] || !response[1][tableName]) return []
  const table = response[1][tableName]
  if (Array.isArray(table)) return table
  if (table.data && table.columns) {
    return table.data.map((row: any[]) => {
      const obj: Record<string, any> = {}
      table.columns.forEach((col: string, i: number) => { obj[col] = row[i] })
      return obj
    })
  }
  return []
}

// ─── Спецификация бумаги ───────────────────────────────────────────────────────

interface SecuritySpec {
  isin: string
  secid: string
  shortname: string
  name: string
  issuer: string
  facevalue: number
  faceunit: string
  issuedate: string
  matdate: string
  couponpercent: number
  couponfrequency: number
  couponvalue: number
  type: string
  typename: string
  group: string
  listlevel: number
  initialfacevalue: number
}

async function getSecuritySpec(isinOrSecid: string): Promise<SecuritySpec> {
  const resp = await moexRequest(`/securities/${isinOrSecid}`)
  const description = parseISSTable(resp, 'description')

  const descMap: Record<string, string> = {}
  description.forEach((row: any) => {
    const key = (row.name || row.NAME || '').toLowerCase()
    descMap[key] = row.value || row.VALUE || ''
  })

  // boards table for secid
  const boards = parseISSTable(resp, 'boards')
  const tqcbBoard = boards.find((b: any) => b.boardid === 'TQCB' || b.BOARDID === 'TQCB')
  const firstBoard = boards[0] || {}
  const secid = (tqcbBoard || firstBoard)?.secid || (tqcbBoard || firstBoard)?.SECID || isinOrSecid

  return {
    isin: descMap['isin'] || isinOrSecid,
    secid,
    shortname: descMap['shortname'] || descMap['name'] || '',
    name: descMap['name'] || descMap['shortname'] || '',
    issuer: descMap['emitter_id'] || descMap['issuername'] || descMap['name'] || '',
    facevalue: parseFloat(descMap['facevalue']) || 1000,
    faceunit: descMap['faceunit'] || 'RUB',
    issuedate: descMap['issuedate'] || '',
    matdate: descMap['matdate'] || '',
    couponpercent: parseFloat(descMap['couponpercent']) || 0,
    couponfrequency: parseInt(descMap['couponfrequency']) || 0,
    couponvalue: parseFloat(descMap['couponvalue']) || 0,
    type: descMap['type'] || '',
    typename: descMap['typename'] || '',
    group: descMap['group'] || '',
    listlevel: parseInt(descMap['listlevel']) || 0,
    initialfacevalue: parseFloat(descMap['initialfacevalue']) || parseFloat(descMap['facevalue']) || 1000,
  }
}

// ─── История торгов облигации ──────────────────────────────────────────────────

interface BondTradeHistory {
  date: string
  close: number
  yield_close: number | null
  volume: number
  num_trades: number
  value: number
  waprice: number | null
}

async function getBondHistory(
  secid: string,
  startDate: string,
  endDate: string,
  board = 'TQCB'
): Promise<BondTradeHistory[]> {
  const all: BondTradeHistory[] = []
  let start = 0

  while (true) {
    const resp = await moexRequest(
      `/history/engines/stock/markets/bonds/boards/${board}/securities/${secid}`,
      { from: startDate, till: endDate, start: start.toString() }
    )
    const rows = parseISSTable(resp, 'history')
    if (!rows.length) break

    for (const r of rows) {
      all.push({
        date: r.TRADEDATE || r.tradedate || '',
        close: r.CLOSE || r.close || 0,
        yield_close: r.YIELDCLOSE ?? r.yieldclose ?? null,
        volume: r.VOLUME || r.volume || 0,
        num_trades: r.NUMTRADES || r.numtrades || 0,
        value: r.VALUE || r.value || 0,
        waprice: r.WAPRICE ?? r.waprice ?? null,
      })
    }

    if (rows.length < 100) break
    start += rows.length
  }

  return all
}

// ─── Текущие рыночные данные ───────────────────────────────────────────────────

interface CurrentMarketData {
  last: number | null
  bid: number | null
  offer: number | null
  spread: number | null
  yield: number | null
  duration: number | null
  accruedint: number | null
  waprice: number | null
  closeprice: number | null
  marketprice: number | null
}

async function getCurrentMarketData(secid: string): Promise<CurrentMarketData> {
  const resp = await moexRequest(`/engines/stock/markets/bonds/securities/${secid}`)
  const mktData = parseISSTable(resp, 'marketdata')
  const secData = parseISSTable(resp, 'securities')

  const mkt = mktData.find((r: any) => (r.SECID || r.secid) === secid) || mktData[0] || {}
  const sec = secData.find((r: any) => (r.SECID || r.secid) === secid) || secData[0] || {}

  return {
    last: mkt.LAST ?? mkt.last ?? null,
    bid: mkt.BID ?? mkt.bid ?? null,
    offer: mkt.OFFER ?? mkt.offer ?? null,
    spread: mkt.SPREAD ?? mkt.spread ?? null,
    yield: mkt.YIELD ?? mkt.yield ?? null,
    duration: mkt.DURATION ?? mkt.duration ?? null,
    accruedint: sec.ACCRUEDINT ?? sec.accruedint ?? null,
    waprice: mkt.WAPRICE ?? mkt.waprice ?? null,
    closeprice: mkt.CLOSEPRICE ?? mkt.closeprice ?? null,
    marketprice: mkt.MARKETPRICE2 ?? sec.PREVWAPRICE ?? sec.prevwaprice ?? null,
  }
}

// ─── Купоны облигации (ISS) ────────────────────────────────────────────────────

interface CouponInfo {
  date: string
  value: number | null
  valueprc: number | null
  period?: number | null
}

async function getBondCoupons(isinOrSecid: string): Promise<CouponInfo[]> {
  const resp = await moexRequest(`/securities/${isinOrSecid}/bondization`)
  const coupons = parseISSTable(resp, 'coupons')

  return coupons.map((c: any) => ({
    date: c.coupondate || c.COUPONDATE || '',
    value: c.value ?? c.VALUE ?? null,
    valueprc: c.valueprc ?? c.VALUEPRC ?? null,
    period: c.value_rub ?? c.VALUE_RUB ?? null,
  }))
}

// ─── Амортизации ───────────────────────────────────────────────────────────────

interface AmortizationInfo {
  date: string
  value: number
  valueprc: number
}

async function getBondAmortizations(isinOrSecid: string): Promise<AmortizationInfo[]> {
  const resp = await moexRequest(`/securities/${isinOrSecid}/bondization`)
  const amorts = parseISSTable(resp, 'amortizations')

  return amorts.map((a: any) => ({
    date: a.amortdate || a.AMORTDATE || '',
    value: a.value ?? a.VALUE ?? 0,
    valueprc: a.valueprc ?? a.VALUEPRC ?? 0,
  }))
}

// ─── G-curve (ZCYC) ────────────────────────────────────────────────────────────

async function getGCurveYield(termYears: number, date?: string): Promise<number> {
  try {
    const params: Record<string, string> = {
      term: termYears.toString(),
      method: 'nelson_siegel',
    }
    if (date) params.date = date

    const resp = await fetch(`${API_BASE}/api/zcyc/interpolate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    })

    if (!resp.ok) {
      // Fallback: use MOEX ISS ZCYC directly
      return await getGCurveFromMoex(termYears, date)
    }
    const data = await resp.json()
    return (data.value || 0) / 100 // convert from percent to decimal
  } catch {
    return await getGCurveFromMoex(termYears, date)
  }
}

async function getGCurveFromMoex(termYears: number, date?: string): Promise<number> {
  try {
    const params: Record<string, string> = {}
    if (date) params.date = date
    const resp = await moexRequest('/statistics/engines/stock/zcyc', params)
    const rows = parseISSTable(resp, 'yearyields') || parseISSTable(resp, 'params')
    if (!rows.length) return 0

    // Nelson-Siegel parameters
    const p = rows[0]
    const b0 = p.b0 ?? p.B0 ?? 0
    const b1 = p.b1 ?? p.B1 ?? 0
    const b2 = p.b2 ?? p.B2 ?? 0
    const g1 = p.g1 ?? p.G1 ?? 1
    // g2 optional
    const tau = termYears || 1
    const x = tau / g1
    const expx = Math.exp(-x)
    const y = b0 + b1 * ((1 - expx) / x) + b2 * (((1 - expx) / x) - expx)
    return y / 100
  } catch {
    return 0
  }
}

// ─── Полная ZCYC на дату (массив точек) ───────────────────────────────────────

interface ZCYCDataPoint {
  term: number
  value: number
}

async function getZCYCCurve(date?: string): Promise<ZCYCDataPoint[]> {
  try {
    const params = new URLSearchParams()
    if (date) params.append('date', date)
    const url = `${API_BASE}/api/zcyc${params.toString() ? '?' + params.toString() : ''}`
    const resp = await fetch(url)
    if (!resp.ok) return []
    const data = await resp.json()
    return data.data || []
  } catch {
    return []
  }
}

// ─── Активность рынка ──────────────────────────────────────────────────────────

function computeMarketActivity(
  history: BondTradeHistory[],
  outstandingAmount: number,
  periodDays = 30
): MarketActivityData {
  // Берём последние periodDays записей
  const recent = history.slice(-periodDays)
  const tradingDays = recent.filter((r) => r.num_trades > 0).length
  const totalTrades = recent.reduce((s, r) => s + r.num_trades, 0)
  const totalVolume = recent.reduce((s, r) => s + r.value, 0)
  const avgVolumePerDay = tradingDays > 0 ? totalVolume / tradingDays : 0
  const turnoverRatio = outstandingAmount > 0 ? totalVolume / outstandingAmount : 0

  // Проверка: были ли торги за последние 30 дней
  const today = new Date()
  const cutoff = new Date(today.getTime() - 30 * 24 * 3600 * 1000)
  const hasRecent = recent.some((r) => new Date(r.date) >= cutoff && r.num_trades > 0)

  // Критерии активности (из шаблона)
  const isActive =
    tradingDays >= 5 && // Минимум 5 торговых дней за месяц
    totalTrades >= 10 && // Минимум 10 сделок
    hasRecent

  return {
    trading_days: tradingDays,
    trades: totalTrades,
    turnover_to_outstanding: turnoverRatio,
    traded_last_30d: hasRecent,
    avg_volume_per_day: avgVolumePerDay,
    total_volume: totalVolume,
    is_active: isActive,
  }
}

// ─── DCF оценка через бэкенд ──────────────────────────────────────────────────

interface BackendValuationResult {
  scenario1: any
  scenario2: any
  faceValue: number
  couponPercent: number
  accruedInterest: number
  cashFlows1: any[]
  cashFlows2: any[]
  allCoupons: any[]
}

async function getBackendValuation(
  secid: string,
  valuationDate: string,
  yield1: number,
  yield2: number,
  dayCountConvention = 'Actual/365F'
): Promise<BackendValuationResult | null> {
  try {
    const resp = await fetch(`${API_BASE}/api/bond/valuate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        secid,
        valuationDate,
        discountYield1: yield1,
        discountYield2: yield2,
        dayCountConvention,
      }),
    })
    if (!resp.ok) return null
    return resp.json()
  } catch {
    return null
  }
}

// ─── Рыночная доходность с MOEX ───────────────────────────────────────────────

async function getMarketYield(secid: string, date: string): Promise<number | null> {
  try {
    const resp = await fetch(`${API_BASE}/api/bond/market-yield?secid=${secid}&date=${date}`)
    if (!resp.ok) return null
    const data = await resp.json()
    return data.yield ?? null
  } catch {
    return null
  }
}

// ─── RuData helpers ────────────────────────────────────────────────────────────

interface RuDataCreds {
  login: string
  password: string
}

function getRuDataCreds(): RuDataCreds | null {
  const encoded = localStorage.getItem('rudata_credentials')
  if (!encoded) return null
  try {
    return JSON.parse(atob(encoded))
  } catch {
    return null
  }
}

async function ruDataQuery(pathMethod: string, body: Record<string, any> = {}, creds?: RuDataCreds): Promise<any> {
  const c = creds || getRuDataCreds()
  if (!c) return null

  try {
    const resp = await fetch(`${API_BASE}/api/rudata/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        login: c.login,
        password: c.password,
        path_method: pathMethod,
        body,
      }),
    })
    if (!resp.ok) return null
    const data = await resp.json()
    return data.success ? data.data : null
  } catch {
    return null
  }
}

async function getRuDataBondInfo(isin: string, creds?: RuDataCreds): Promise<any> {
  const c = creds || getRuDataCreds()
  if (!c) return null

  try {
    const resp = await fetch(`${API_BASE}/api/rudata/bond/info?isin=${isin}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login: c.login, password: c.password }),
    })
    if (!resp.ok) return null
    const data = await resp.json()
    return data.success ? data.data : null
  } catch {
    return null
  }
}

async function getRuDataBondCalculation(isin: string, calcDate?: string, price?: number, creds?: RuDataCreds): Promise<any> {
  const c = creds || getRuDataCreds()
  if (!c) return null

  try {
    const resp = await fetch(`${API_BASE}/api/rudata/bond/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        login: c.login,
        password: c.password,
        isin,
        calc_date: calcDate,
        price,
      }),
    })
    if (!resp.ok) return null
    const data = await resp.json()
    return data.success ? data.data : null
  } catch {
    return null
  }
}

async function getRuDataRatings(isin: string, creds?: RuDataCreds): Promise<RatingEntry[]> {
  const c = creds || getRuDataCreds()
  if (!c) return []

  try {
    const data = await ruDataQuery('Rating/List', {
      filter: `fintoolid = '${isin}' OR isin_code = '${isin}'`,
      count: 100,
    }, c)
    if (!data || !Array.isArray(data)) return []

    return data.map((r: any) => ({
      agency: r.ra_name || r.agency || '',
      rating: r.last_rating || r.rating || '',
      outlook: r.forecast || r.outlook || null,
      date: r.last_dt ? String(r.last_dt).split('T')[0] : null,
    }))
  } catch {
    return []
  }
}

async function getRuDataIssuerRatings(issuerName: string, creds?: RuDataCreds): Promise<RatingEntry[]> {
  const c = creds || getRuDataCreds()
  if (!c) return []

  try {
    const data = await ruDataQuery('Rating/List', {
      filter: `org_name LIKE '%${issuerName}%'`,
      count: 100,
    }, c)
    if (!data || !Array.isArray(data)) return []

    return data.map((r: any) => ({
      agency: r.ra_name || r.agency || '',
      rating: r.last_rating || r.rating || '',
      outlook: r.forecast || r.outlook || null,
      date: r.last_dt ? String(r.last_dt).split('T')[0] : null,
    }))
  } catch {
    return []
  }
}

async function getRuDataFintoolRef(isin: string, creds?: RuDataCreds): Promise<any> {
  const c = creds || getRuDataCreds()
  if (!c) return null

  try {
    const resp = await fetch(`${API_BASE}/api/rudata/fintool/reference?id=${isin}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login: c.login, password: c.password }),
    })
    if (!resp.ok) return null
    const data = await resp.json()
    return data.success ? data.data : null
  } catch {
    return null
  }
}

// ─── Рейтинги с MOEX ISS ──────────────────────────────────────────────────────

async function getMoexRatings(isin: string): Promise<{ issue: RatingEntry[]; issuer: RatingEntry[] }> {
  try {
    const resp = await moexRequest(`/cci/rating/securities/${isin}`)
    const ratings = parseISSTable(resp, 'ratings') || parseISSTable(resp, 'rating')
    const issueRatings: RatingEntry[] = []
    const issuerRatings: RatingEntry[] = []

    for (const r of ratings) {
      const entry: RatingEntry = {
        agency: r.agency || r.AGENCY || r.ra_name || '',
        rating: r.rating || r.RATING || r.last_rating || '',
        outlook: r.outlook || r.OUTLOOK || r.forecast || null,
        date: r.date || r.DATE || r.last_dt || null,
      }

      const type = (r.type || r.TYPE || '').toLowerCase()
      if (type.includes('issuer') || type.includes('эмитент')) {
        issuerRatings.push(entry)
      } else {
        issueRatings.push(entry)
      }
    }

    return { issue: issueRatings, issuer: issuerRatings }
  } catch {
    return { issue: [], issuer: [] }
  }
}

// ─── Индексы MOEX ──────────────────────────────────────────────────────────────

// Тикеры индексов MOEX по рейтинговым группам
const INDEX_TICKERS: Record<string, string> = {
  gov_less_1y: 'RGBITR1Y',    // Индекс гос. облигаций < 1 года
  gov_1_3y: 'RGBITR3Y',       // Индекс гос. облигаций 1-3 года
  corp_aaa: 'RUCBITR3YAAA',   // Корп. ААА
  corp_aa: 'RUCBITR3YAA',     // Корп. АА
  corp_a: 'RUCBITR3YA',       // Корп. А
  corp_bbb: 'RUCBITRBBB',     // Корп. ВВВ
  corp_aaa_1_3y: 'RUCBITR3YAAA',
  corp_aa_1_3y: 'RUCBITR3YAA',
  corp_a_1_3y: 'RUCBITR3YA',
}

async function getIndexYield(indexTicker: string, date?: string): Promise<number | null> {
  try {
    const params: Record<string, string> = {}
    if (date) {
      params.from = date
      params.till = date
    }
    const resp = await moexRequest(
      `/statistics/engines/stock/markets/index/analytics/${indexTicker}`,
      params
    )
    const rows = parseISSTable(resp, 'analytics') || parseISSTable(resp, 'indices')
    if (!rows.length) {
      // Fallback: history approach
      return await getIndexYieldFallback(indexTicker, date)
    }
    const row = rows[rows.length - 1]
    const y = row.close ?? row.CLOSE ?? row.currentvalue ?? row.CURRENTVALUE ?? null
    return y !== null ? y / 100 : null
  } catch {
    return await getIndexYieldFallback(indexTicker, date)
  }
}

async function getIndexYieldFallback(indexTicker: string, date?: string): Promise<number | null> {
  try {
    const endDate = date || new Date().toISOString().split('T')[0]
    const start = new Date(new Date(endDate).getTime() - 10 * 24 * 3600 * 1000).toISOString().split('T')[0]
    const resp = await moexRequest(
      `/history/engines/stock/markets/index/boards/SNDX/securities/${indexTicker}`,
      { from: start, till: endDate }
    )
    const rows = parseISSTable(resp, 'history')
    if (!rows.length) return null
    const last = rows[rows.length - 1]
    return (last.CLOSE ?? last.close ?? null) !== null ? (last.CLOSE ?? last.close) / 100 : null
  } catch {
    return null
  }
}

async function fetchAllIndices(date?: string): Promise<IndexYields> {
  const results: IndexYields = {}

  const entries = Object.entries(INDEX_TICKERS)
  const promises = entries.map(([key, ticker]) => getIndexYield(ticker, date))
  const values = await Promise.allSettled(promises)

  entries.forEach(([key], i) => {
    const result = values[i]
    if (result.status === 'fulfilled' && result.value !== null) {
      (results as any)[key] = result.value
    }
  })

  return results
}

// ─── Корпоративные события ─────────────────────────────────────────────────────

async function getCorporateEvents(isin: string): Promise<CorporateEvent[]> {
  // Try RuData first
  const creds = getRuDataCreds()
  if (creds) {
    try {
      const data = await ruDataQuery('News/List', {
        filter: `isin_code = '${isin}'`,
        count: 20,
      }, creds)
      if (data && Array.isArray(data) && data.length > 0) {
        return data.map((item: any) => ({
          date: item.pub_date ? String(item.pub_date).split('T')[0] : null,
          description: item.title || item.subject || item.text || '',
        }))
      }
    } catch { /* fallback to ISS */ }
  }

  // Fallback: MOEX ISS corp events
  try {
    const resp = await moexRequest(`/securities/${isin}/bondization`)
    const offers = parseISSTable(resp, 'offers')
    const events: CorporateEvent[] = []

    for (const o of offers) {
      events.push({
        date: o.offerdate || o.OFFERDATE || null,
        description: `Оферта: ${o.offertypename || o.OFFERTYPENAME || 'Без типа'}`,
      })
    }

    return events
  } catch {
    return []
  }
}

// ─── Вычисление YTM, дюрации, выпуклости из кэш-флоу ──────────────────────────

/**
 * Расчёт YTM (Yield to Maturity) из чистой цены
 * Метод Ньютона-Рафсона, аналог формулы из шаблона
 */
function calcYTMFromPrice(
  cleanPricePct: number,
  faceValue: number,
  couponRate: number,
  couponPerYear: number,
  yearsToMaturity: number
): number {
  if (yearsToMaturity <= 0 || couponPerYear <= 0) return 0

  const C = (couponRate * faceValue) / couponPerYear
  const n = Math.round(couponPerYear * yearsToMaturity)
  const price = (cleanPricePct / 100) * faceValue

  // Newton-Raphson
  let y = couponRate || 0.1 // initial guess
  for (let iter = 0; iter < 200; iter++) {
    let pv = 0
    let dpv = 0
    for (let t = 1; t <= n; t++) {
      const cf = t === n ? C + faceValue : C
      const dt = t / couponPerYear
      const df = Math.pow(1 + y / couponPerYear, -t)
      pv += cf * df
      dpv -= (t / couponPerYear) * cf * df / (1 + y / couponPerYear)
    }
    const err = pv - price
    if (Math.abs(err) < 0.0001) break
    if (Math.abs(dpv) < 1e-12) break
    y -= err / dpv
    if (y < -0.5) y = 0.001
    if (y > 2) y = 1.999
  }

  return y
}

/**
 * Macaulay Duration из потоков
 */
function calcDuration(
  ytm: number,
  faceValue: number,
  couponRate: number,
  couponPerYear: number,
  yearsToMaturity: number
): number {
  if (yearsToMaturity <= 0 || couponPerYear <= 0) return 0

  const C = (couponRate * faceValue) / couponPerYear
  const n = Math.round(couponPerYear * yearsToMaturity)
  let weightedSum = 0
  let totalPV = 0

  for (let t = 1; t <= n; t++) {
    const cf = t === n ? C + faceValue : C
    const dt = t / couponPerYear
    const df = Math.pow(1 + ytm / couponPerYear, -t)
    const pv = cf * df
    weightedSum += dt * pv
    totalPV += pv
  }

  return totalPV > 0 ? weightedSum / totalPV : 0
}

/**
 * Modified Duration = Macaulay Duration / (1 + y/m)
 */
function calcModDuration(macaulayDuration: number, ytm: number, couponPerYear: number): number {
  return macaulayDuration / (1 + ytm / couponPerYear)
}

/**
 * Convexity
 */
function calcConvexity(
  ytm: number,
  faceValue: number,
  couponRate: number,
  couponPerYear: number,
  yearsToMaturity: number
): number {
  if (yearsToMaturity <= 0 || couponPerYear <= 0) return 0

  const C = (couponRate * faceValue) / couponPerYear
  const n = Math.round(couponPerYear * yearsToMaturity)
  let convexSum = 0
  let totalPV = 0
  const r = ytm / couponPerYear

  for (let t = 1; t <= n; t++) {
    const cf = t === n ? C + faceValue : C
    const df = Math.pow(1 + r, -(t + 2))
    convexSum += cf * t * (t + 1) * df
    totalPV += cf * Math.pow(1 + r, -t)
  }

  if (totalPV <= 0) return 0
  return convexSum / (totalPV * couponPerYear * couponPerYear)
}

/**
 * DV01 = Modified Duration * Dirty Price * 0.0001
 */
function calcDV01(modDuration: number, dirtyPrice: number): number {
  return modDuration * dirtyPrice * 0.0001
}

// ─── Дисконтная маржа для флоатеров ────────────────────────────────────────────

/**
 * Discount Margin (DM) — маржа поверх форвардной базовой ставки
 * Используется для облигаций с плавающим купоном
 *
 * Алгоритм из «Расчёт доходности флоатера.xlsm»:
 * 1. Для каждого будущего купонного периода берём ожидаемую ставку-базу (forward rate от КБД)
 * 2. Прибавляем фиксированную маржу (QM — quoted margin)
 * 3. Подбираем DM такую, что при дисконтировании CF по (forward + DM) цена = market price
 */
function calcDiscountMargin(
  dirtyPricePct: number,
  faceValue: number,
  quotedMarginBps: number,
  couponPerYear: number,
  yearsToMaturity: number,
  forwardRates: number[] // массив форвардных ставок для каждого купонного периода
): number {
  if (yearsToMaturity <= 0 || couponPerYear <= 0 || forwardRates.length === 0) return 0

  const n = Math.round(couponPerYear * yearsToMaturity)
  const price = (dirtyPricePct / 100) * faceValue
  const qm = quotedMarginBps / 10000

  // Newton-Raphson для DM
  let dm = qm // initial guess = quoted margin
  for (let iter = 0; iter < 200; iter++) {
    let pv = 0
    let dpv = 0

    for (let t = 1; t <= n; t++) {
      const fwdIdx = Math.min(t - 1, forwardRates.length - 1)
      const fwdRate = forwardRates[fwdIdx] || 0
      const couponRate = fwdRate + qm
      const cf = t === n
        ? (couponRate * faceValue) / couponPerYear + faceValue
        : (couponRate * faceValue) / couponPerYear
      const discountRate = fwdRate + dm
      const dt = t / couponPerYear
      const df = Math.pow(1 + discountRate / couponPerYear, -t)
      pv += cf * df
      dpv -= (t / couponPerYear) * cf * df / (1 + discountRate / couponPerYear)
    }

    const err = pv - price
    if (Math.abs(err) < 0.01) break
    if (Math.abs(dpv) < 1e-12) break
    dm -= err / dpv
  }

  return dm * 10000 // return in bps
}

// ─── История цен для графика ───────────────────────────────────────────────────

function buildPriceHistory(history: BondTradeHistory[]): PriceHistoryPoint[] {
  return history
    .filter((h) => h.close > 0 || (h.waprice && h.waprice > 0))
    .map((h) => ({
      date: h.date,
      price: h.waprice || h.close,
    }))
}

// ─── История доходности для графика ────────────────────────────────────────────

async function buildYieldHistory(
  history: BondTradeHistory[],
  spec: SecuritySpec,
  valuationDate: string
): Promise<YieldHistoryPoint[]> {
  const points: YieldHistoryPoint[] = []
  const matDate = new Date(spec.matdate)

  for (const h of history) {
    if (!h.yield_close && !h.close) continue

    const tradeDate = new Date(h.date)
    const yearsToMat = (matDate.getTime() - tradeDate.getTime()) / (365.25 * 24 * 3600 * 1000)

    let ytm = h.yield_close ? h.yield_close / 100 : 0
    if (!ytm && h.close > 0) {
      ytm = calcYTMFromPrice(
        h.close,
        spec.facevalue,
        spec.couponpercent / 100,
        spec.couponfrequency || 2,
        yearsToMat
      )
    }

    // G-curve yield for this term
    const gcurve = await getGCurveYield(yearsToMat, h.date)
    const gspread = ytm - gcurve

    points.push({
      date: h.date,
      ytm: ytm * 100,
      gcurve: gcurve * 100,
      gspread: gspread * 10000, // bps
    })
  }

  return points
}

// ─── Для флоатера: история DM/QM ──────────────────────────────────────────────

function buildMarginHistory(
  history: BondTradeHistory[],
  quotedMarginBps: number
): MarginHistoryPoint[] {
  // DM аппроксимация из истории: DM ≈ (YTM - базовая ставка) в bps
  // QM = константа (фикс. маржа из формулы купона)
  return history
    .filter((h) => h.yield_close !== null && h.yield_close !== undefined)
    .map((h) => ({
      date: h.date,
      dm: (h.yield_close || 0) * 100 - quotedMarginBps / 100, // упрощённая аппроксимация
      qm: quotedMarginBps,
    }))
}

// ─── Парсинг формулы купона флоатера ───────────────────────────────────────────

function parseFloaterFormula(formula: string): { baseName: string; marginPct: number } {
  // Examples:
  //   "Ключевая ставка ЦБ РФ + 2,2%"
  //   "КС ЦБ + 3.5%"
  //   "RUONIA + 1.5%"

  const match = formula.match(/([+-])\s*([\d,.]+)\s*%?\s*$/)
  const marginPct = match ? parseFloat(match[2].replace(',', '.')) * (match[1] === '-' ? -1 : 1) : 0
  const baseName = formula.replace(/[+-]\s*[\d,.]+\s*%?\s*$/, '').trim()

  return { baseName, marginPct }
}

// ═══════════════════════════════════════════════════════════════════════════════
// ПУБЛИЧНЫЕ ФУНКЦИИ
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Генерация полного отчёта по vanilla-облигации.
 * Логика соответствует «Автоматизированный шаблон.xlsm».
 */
export async function fetchVanillaBondReport(
  isin: string,
  valuationDate: string
): Promise<VanillaBondReport> {
  // 1. Спецификация бумаги
  const spec = await getSecuritySpec(isin)

  // 2. Текущие рыночные данные
  const marketData = await getCurrentMarketData(spec.secid)

  // 3. История торгов за последний год
  const endDate = valuationDate
  const startDate = new Date(new Date(endDate).getTime() - 365 * 24 * 3600 * 1000).toISOString().split('T')[0]
  const history = await getBondHistory(spec.secid, startDate, endDate)

  // 4. Оставшийся срок до погашения
  const valDate = new Date(valuationDate)
  const matDate = new Date(spec.matdate)
  const yearsToMaturity = (matDate.getTime() - valDate.getTime()) / (365.25 * 24 * 3600 * 1000)

  // 5. Чистая цена
  const cleanPricePct = marketData.last ?? marketData.waprice ?? marketData.closeprice ?? marketData.marketprice ?? 100

  // 6. YTM
  let ytm: number
  if (marketData.yield && marketData.yield > 0) {
    ytm = marketData.yield / 100
  } else {
    ytm = calcYTMFromPrice(
      cleanPricePct,
      spec.facevalue,
      spec.couponpercent / 100,
      spec.couponfrequency || 2,
      yearsToMaturity
    )
  }

  // 7. G-curve yield и G-spread
  const gCurveYield = await getGCurveYield(yearsToMaturity, valuationDate)
  const gSpreadBps = (ytm - gCurveYield) * 10000

  // 8. Дюрация, модифицированная дюрация, выпуклость
  let duration: number
  let modDuration: number
  let convexity: number

  if (marketData.duration && marketData.duration > 0) {
    // MOEX предоставляет дюрацию в днях
    duration = marketData.duration / 365
    modDuration = duration / (1 + ytm / (spec.couponfrequency || 2))
    convexity = calcConvexity(ytm, spec.facevalue, spec.couponpercent / 100, spec.couponfrequency || 2, yearsToMaturity)
  } else {
    duration = calcDuration(ytm, spec.facevalue, spec.couponpercent / 100, spec.couponfrequency || 2, yearsToMaturity)
    modDuration = calcModDuration(duration, ytm, spec.couponfrequency || 2)
    convexity = calcConvexity(ytm, spec.facevalue, spec.couponpercent / 100, spec.couponfrequency || 2, yearsToMaturity)
  }

  // 9. DV01
  const accruedInt = marketData.accruedint ?? 0
  const dirtyPrice = (cleanPricePct / 100) * spec.facevalue + accruedInt
  const dv01 = calcDV01(modDuration, dirtyPrice)

  // 10. Попытка обогатить данные через бэкенд DCF
  const backendResult = await getBackendValuation(spec.secid, valuationDate, ytm * 100, ytm * 100)
  if (backendResult?.scenario1) {
    const s = backendResult.scenario1
    if (s.duration > 0) duration = s.duration
    if (s.modifiedDuration && s.modifiedDuration > 0) modDuration = s.modifiedDuration
    if (s.convexity) convexity = s.convexity
    if (s.pvbpAbsolute) { /* можно использовать backend DV01 */ }
  }

  // 11. Рейтинги (MOEX ISS + RuData)
  const moexRatings = await getMoexRatings(isin)
  const ruDataIssueRatings = await getRuDataRatings(isin)
  const ruDataIssuerRatings = spec.issuer ? await getRuDataIssuerRatings(spec.issuer) : []

  const issueRatings = moexRatings.issue.length > 0 ? moexRatings.issue : ruDataIssueRatings
  const issuerRatings = moexRatings.issuer.length > 0 ? moexRatings.issuer : ruDataIssuerRatings

  // 12. Активность рынка
  const outstandingAmount = spec.facevalue * 1000000 // приблизительно
  // Try to get from RuData
  let actualOutstanding = outstandingAmount
  const ruRef = await getRuDataFintoolRef(isin)
  if (ruRef && Array.isArray(ruRef) && ruRef.length > 0) {
    const ref0 = ruRef[0]
    if (ref0.sumissueval) actualOutstanding = ref0.sumissueval
    if (ref0.issueval) actualOutstanding = ref0.issueval
  }
  const marketActivity = computeMarketActivity(history, actualOutstanding)

  // 13. Индексы
  const indices = await fetchAllIndices(valuationDate)

  // 14. Корпоративные события
  const corporateEvents = await getCorporateEvents(isin)

  // 15. История цен и доходности для графиков
  const priceHistory = buildPriceHistory(history)

  // Yield history - sample evenly
  const yieldHistorySampled = history.filter((_, i) => i % Math.max(1, Math.floor(history.length / 30)) === 0)
  const yieldHistoryPoints: YieldHistoryPoint[] = []
  for (const h of yieldHistorySampled) {
    if (!h.yield_close && !h.close) continue
    const tradeDate = new Date(h.date)
    const yrsToMat = (matDate.getTime() - tradeDate.getTime()) / (365.25 * 24 * 3600 * 1000)
    let hytm = h.yield_close ? h.yield_close / 100 : 0
    if (!hytm && h.close > 0) {
      hytm = calcYTMFromPrice(h.close, spec.facevalue, spec.couponpercent / 100, spec.couponfrequency || 2, yrsToMat)
    }
    const gc = await getGCurveYield(yrsToMat, h.date)
    yieldHistoryPoints.push({
      date: h.date,
      ytm: hytm * 100,
      gcurve: gc * 100,
      gspread: (hytm - gc) * 10000,
    })
  }

  // 16. Доп. данные из RuData для общих сведений
  let riskCountry = 'Россия'
  let sector = ''
  let industry = ''
  if (ruRef && Array.isArray(ruRef) && ruRef.length > 0) {
    const ref0 = ruRef[0]
    riskCountry = ref0.country || ref0.issuercountry || 'Россия'
    sector = ref0.sectorbond || ref0.sector || ''
    industry = ref0.branch || ref0.industry || ''
  }

  return {
    isin: spec.isin || isin,
    issuer: spec.name || spec.shortname || spec.issuer || isin,
    risk_country: riskCountry,
    sector: sector || 'Корпоративный',
    industry: industry,
    outstanding_amount: actualOutstanding,
    issue_info: {
      issue_date: spec.issuedate || null,
      maturity_date: spec.matdate || null,
      coupon_rate: spec.couponpercent ? spec.couponpercent / 100 : null,
      coupon_per_year: spec.couponfrequency || null,
    },
    ratings: {
      issue: issueRatings,
      issuer: issuerRatings,
      guarantor: [],
    },
    market_activity: marketActivity,
    pricing: {
      clean_price_pct: cleanPricePct,
      dirty_price: dirtyPrice,
      ytm,
      g_spread_bps: Math.round(gSpreadBps * 100) / 100,
      g_curve_yield: gCurveYield,
    },
    risk_indicators: {
      duration: Math.round(duration * 10000) / 10000,
      mod_duration: Math.round(modDuration * 10000) / 10000,
      convexity: Math.round(convexity * 100) / 100,
      dv01: Math.round(dv01 * 100) / 100,
    },
    indices,
    corporate_events: corporateEvents,
    price_history: priceHistory,
    yield_history: yieldHistoryPoints,
    analogous_bonds: [],
  }
}

/**
 * Генерация полного отчёта по облигации-флоатеру.
 * Логика соответствует «Автоматизированный шаблон (для флоатеров).xlsm»
 * + «Расчёт доходности флоатера.xlsm».
 */
export async function fetchFloaterBondReport(
  isin: string,
  valuationDate: string
): Promise<FloaterBondReport> {
  // 1. Базовый отчёт — большинство вычислений идентичны vanilla
  const base = await fetchVanillaBondReport(isin, valuationDate)

  // 2. Доп. информация для флоатера
  const spec = await getSecuritySpec(isin)
  const coupons = await getBondCoupons(isin)

  // Определяем формулу купона
  let couponFormula = ''
  let quotedMarginBps = 0

  // Из RuData
  const ruRef = await getRuDataFintoolRef(isin)
  if (ruRef && Array.isArray(ruRef) && ruRef.length > 0) {
    const ref0 = ruRef[0]
    couponFormula = ref0.coupon_type_desc || ref0.floatratename || ref0.coupondesc || ''
    if (ref0.floatratemargin) {
      quotedMarginBps = ref0.floatratemargin * 100 // convert % to bps
    }
  }

  // Если формула не найдена в RuData, пытаемся угадать из названия
  if (!couponFormula && spec.couponpercent > 0) {
    couponFormula = `Переменная ставка (${spec.couponpercent}%)`
  }

  // Парсим маржу из формулы
  if (couponFormula && quotedMarginBps === 0) {
    const parsed = parseFloaterFormula(couponFormula)
    quotedMarginBps = parsed.marginPct * 100
  }

  // Следующий купон
  const today = new Date(valuationDate)
  const futureCoupons = coupons.filter((c) => new Date(c.date) > today)
  const nextCoupon = futureCoupons.length > 0
    ? (futureCoupons[0].valueprc || futureCoupons[0].value || null)
    : null
  const nextCouponRate = nextCoupon !== null ? nextCoupon / 100 : null

  // Кол-во выпусков эмитента в обращении
  let issuesCount: number | null = null
  const ruCreds = getRuDataCreds()
  if (ruCreds && base.issuer) {
    try {
      const data = await ruDataQuery('Bond/List', {
        filter: `issuername LIKE '%${base.issuer.substring(0, 20)}%' AND status = 'В обращении'`,
        count: 200,
      }, ruCreds)
      if (data && Array.isArray(data)) {
        issuesCount = data.length
      }
    } catch { /* ignore */ }
  }

  // Анализируемый период
  const startDateFormatted = new Date(new Date(valuationDate).getTime() - 30 * 24 * 3600 * 1000)
  const analysisPeriod = `с ${formatDateRu(startDateFormatted)} по ${formatDateRu(new Date(valuationDate))}`

  // 3. История DM/QM
  const historyForMargin = await getBondHistory(
    spec.secid,
    new Date(new Date(valuationDate).getTime() - 365 * 24 * 3600 * 1000).toISOString().split('T')[0],
    valuationDate
  )
  const marginHistory = buildMarginHistory(historyForMargin, quotedMarginBps)

  return {
    ...base,
    issues_count: issuesCount,
    analysis_period: analysisPeriod,
    coupon_formula: couponFormula || null,
    issue_info: {
      ...base.issue_info,
      coupon_formula: couponFormula || null,
      next_coupon: nextCouponRate,
      nominal: spec.facevalue,
    },
    margin_history: marginHistory,
    analogous_bonds_note: undefined,
  }
}

/**
 * Загрузить данные по облигации-аналогу (для scatter-графика).
 */
export async function fetchAnalogBondData(
  analogIsin: string,
  valuationDate: string
): Promise<AnalogousBond | null> {
  try {
    const spec = await getSecuritySpec(analogIsin)
    const mkt = await getCurrentMarketData(spec.secid)

    const matDate = new Date(spec.matdate)
    const valDate = new Date(valuationDate)
    const yearsToMat = (matDate.getTime() - valDate.getTime()) / (365.25 * 24 * 3600 * 1000)

    const cleanPrice = mkt.last ?? mkt.waprice ?? mkt.closeprice ?? mkt.marketprice ?? 100
    let ytm = 0
    if (mkt.yield && mkt.yield > 0) {
      ytm = mkt.yield
    } else {
      ytm = calcYTMFromPrice(
        cleanPrice,
        spec.facevalue,
        spec.couponpercent / 100,
        spec.couponfrequency || 2,
        yearsToMat
      ) * 100
    }

    let duration = 0
    if (mkt.duration && mkt.duration > 0) {
      duration = mkt.duration / 365
    } else {
      duration = calcDuration(
        ytm / 100,
        spec.facevalue,
        spec.couponpercent / 100,
        spec.couponfrequency || 2,
        yearsToMat
      )
    }

    return {
      isin: spec.isin || analogIsin,
      name: spec.shortname || spec.name || analogIsin,
      duration,
      yield: ytm,
    }
  } catch {
    return null
  }
}

// ─── Утилиты ───────────────────────────────────────────────────────────────────

function formatDateRu(d: Date): string {
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  return `${day}.${month}.${year}`
}

export function formatDateDisplay(dateStr?: string | null): string {
  if (!dateStr) return '—'
  try {
    const d = new Date(dateStr)
    return formatDateRu(d)
  } catch {
    return dateStr
  }
}

export function formatNumberDisplay(num?: number | null): string {
  if (num === undefined || num === null) return '—'
  return new Intl.NumberFormat('ru-RU').format(num)
}
