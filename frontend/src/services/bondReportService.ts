/**
 * Сервис для генерации отчётов по облигациям (Bond Report).
 *
 * Расчёты соответствуют формулам из Excel-шаблонов:
 *  - «Автоматизированный шаблон.xlsm» → VanilaBondReport
 *  - «Автоматизированный шаблон (для флоатеров).xlsm» → FloaterBondReport
 *
 * Источники данных (аналоги Excel add-in функций):
 *  - MOEX ISS API          → _xll.CbondsClosePrice, CbondsCalcYTM, CbondsCalcDuration
 *  - RuData (Efir) API     → _xll.EfirYields, EfirEndOfDay, EfirHistoryAgg, ReferenceParams, BondDateParams
 *  - Backend /api/zcyc     → _xll.GCurve
 *  - Backend /api/bond     → DCF-оценка (fallback)
 */

import { getApiHeaders } from '@/utils/apiHeaders'
import { getApiBaseUrl } from '@/utils/apiBase'

import type {
  SecuritySpec,
  BondTradeHistory,
  CurrentMarketData,
  RuDataCreds,
  RuDataBondCalcResult,
  RatingEntry,
  CouponPayment,
  AmortizationPayment,
  MarginHistoryPoint,
  YieldHistoryPoint,
  PriceHistoryPoint,
  IndexYields,
  CorporateEvent,
  AnalogousBond,
  VanillaBondReport,
  FloaterBondReport,
} from './bondReportTypes'

import {
  calcYTMFromPrice,
  calcDuration,
  calcConvexity,
  calcDV01,
  calcDiscountMargin,
  calcCurrentYield,
  detectOfferType,
  formatDateRu,
} from './bondReportCalc'

// Re-export all types so existing consumers don't break
export * from './bondReportTypes'

const API_BASE = getApiBaseUrl()
const MOEX_ISS = 'https://iss.moex.com/iss'

/** Escape single quotes in filter values to prevent filter injection. */
function escFilter(val: string): string {
  return val.replace(/'/g, "''")
}

// ─── MOEX ISS helpers ──────────────────────────────────────────────────────────

async function moexRequest(endpoint: string, params: Record<string, string> = {}): Promise<unknown> {
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

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function parseISSTable(response: unknown, tableName: string): Record<string, any>[] {
  const resp = response as Record<string, unknown>[] | undefined
  if (!resp || !resp[1] || !(resp[1] as Record<string, unknown>)[tableName]) return []
  const table = (resp[1] as Record<string, unknown>)[tableName] as Record<string, unknown>
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  if (Array.isArray(table)) return table as Record<string, any>[]
  if (table.data && table.columns) {
    return (table.data as unknown[][]).map((row: unknown[]) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const obj: Record<string, any> = {}
      ;(table.columns as string[]).forEach((col: string, i: number) => { obj[col] = row[i] })
      return obj
    })
  }
  return []
}

// ─── Спецификация бумаги ───────────────────────────────────────────────────────

async function getSecuritySpec(isinOrSecid: string): Promise<SecuritySpec> {
  const resp = await moexRequest(`/securities/${isinOrSecid}`)
  const description = parseISSTable(resp, 'description')

  const descMap: Record<string, string> = {}
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  description.forEach((row: Record<string, any>) => {
    const key = (row.name || row.NAME || '').toLowerCase()
    descMap[key] = row.value || row.VALUE || ''
  })

  const boards = parseISSTable(resp, 'boards')
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const tqcbBoard = boards.find((b: Record<string, any>) => b.boardid === 'TQCB' || b.BOARDID === 'TQCB')
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

// ─── История торгов облигации (MOEX ISS) ────────────────────────────────────

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
        duration: r.DURATION ?? r.duration ?? null,
      })
    }

    if (rows.length < 100) break
    start += rows.length
  }

  return all
}

// ─── Текущие рыночные данные (MOEX ISS) ────────────────────────────────────

async function getCurrentMarketData(secid: string): Promise<CurrentMarketData> {
  const resp = await moexRequest(`/engines/stock/markets/bonds/securities/${secid}`)
  const mktData = parseISSTable(resp, 'marketdata')
  const secData = parseISSTable(resp, 'securities')

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mkt = mktData.find((r: Record<string, any>) => (r.SECID || r.secid) === secid) || mktData[0] || {}
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const sec = secData.find((r: Record<string, any>) => (r.SECID || r.secid) === secid) || secData[0] || {}

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

// ─── RuData helpers ────────────────────────────────────────────────────────────

function getRuDataCreds(): RuDataCreds | null {
  // Credentials are now managed server-side only
  return null
}

async function ruDataQuery(pathMethod: string, body: Record<string, unknown> = {}, creds?: RuDataCreds): Promise<unknown> {
  const c = creds || getRuDataCreds()
  if (!c) return null

  try {
    const resp = await fetch(`${API_BASE}/api/rudata/query`, {
      method: 'POST',
      headers: getApiHeaders(),
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

// ─── RuData: FintoolReferenceData (аналог _xll.ReferenceParams) ─────────────

async function getRuDataFintoolRef(isin: string, creds?: RuDataCreds): Promise<unknown> {
  const c = creds || getRuDataCreds()
  if (!c) return null

  try {
    const resp = await fetch(`${API_BASE}/api/rudata/fintool/reference?id=${isin}`, {
      method: 'POST',
      headers: getApiHeaders(),
      body: JSON.stringify({ login: c.login, password: c.password }),
    })
    if (!resp.ok) return null
    const data = await resp.json()
    return data.success ? data.data : null
  } catch {
    return null
  }
}

// ─── RuData: Bond/Calculate (аналог CbondsCalcYTM + EfirYields + EfirEndOfDay) ─

async function getRuDataBondCalc(isin: string, calcDate?: string, price?: number, creds?: RuDataCreds): Promise<RuDataBondCalcResult | null> {
  const c = creds || getRuDataCreds()
  if (!c) return null

  try {
    const resp = await fetch(`${API_BASE}/api/rudata/bond/calculate`, {
      method: 'POST',
      headers: getApiHeaders(),
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
    if (!data.success || !data.data) return null

    const d = Array.isArray(data.data) ? data.data[0] : data.data
    if (!d) return null

    return {
      ytm: d.ytm ?? d.YTM ?? d.yld ?? d.yield_to_maturity ?? null,
      ytp: d.ytp ?? d.YTP ?? d.yield_to_put ?? d.y2o_last ?? d.Y2O_LAST ?? null,
      duration_days: d.duration ?? d.DURATION ?? null,
      duration_years: d.duration ? d.duration / 365 : null,
      mod_duration: d.duration_n ?? d.modified_duration ?? d.mod_duration ?? null,
      convexity: d.convexity ?? d.CONVEXITY ?? null,
      offer_date: d.offer_date ?? d.offerdate ?? null,
      coupon_rate: d.cpn_rate ?? d.coupon_rate ?? d.couponrate ?? null,
      facevalue: d.current_fv ?? d.facevalue ?? d.nominal ?? null,
      accrued_interest: d.accruedint ?? d.accrued_interest ?? null,
      dm_bps: d.dm ?? d.discount_margin ?? null,
    }
  } catch {
    return null
  }
}

// ─── RuData: EfirYields (convexity, duration_n) ────────────────────────────────

async function getRuDataEfirYields(isin: string, date: string, creds?: RuDataCreds): Promise<{
  convexity: number | null
  duration_n: number | null
}> {
  const c = creds || getRuDataCreds()
  if (!c) return { convexity: null, duration_n: null }

  try {
    const data = await ruDataQuery('Efir/Yields', {
      isin,
      date,
      fields: 'convexity,duration_n',
    }, c)

    if (!data) return { convexity: null, duration_n: null }
    const d = Array.isArray(data) ? data[0] : data

    return {
      convexity: d?.convexity ?? null,
      duration_n: d?.duration_n ?? null,
    }
  } catch {
    return { convexity: null, duration_n: null }
  }
}

// ─── RuData: EfirEndOfDay (duration, Y2O_LAST, DURATION_O) ────────────────────

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function getRuDataEfirEndOfDay(isin: string, date: string, fields: string[], creds?: RuDataCreds): Promise<Record<string, any>> {
  const c = creds || getRuDataCreds()
  if (!c) return {}

  try {
    const data = await ruDataQuery('Efir/EndOfDay', {
      isin,
      date,
      fields: fields.join(','),
    }, c)

    if (!data) return {}
    const d = Array.isArray(data) ? data[0] : data
    return d || {}
  } catch {
    return {}
  }
}

// ─── RuData: EfirHistoryAgg (активность рынка) ────────────────────────────────
// Аналог: _xll.EfirHistoryAgg(ISIN, from, to, "DO", field)

async function getRuDataEfirHistoryAgg(
  isin: string,
  fromDate: string,
  toDate: string,
  fields: string[],
  creds?: RuDataCreds
// eslint-disable-next-line @typescript-eslint/no-explicit-any
): Promise<Record<string, any>> {
  const c = creds || getRuDataCreds()
  if (!c) return {}

  try {
    const data = await ruDataQuery('Efir/HistoryAgg', {
      isin,
      dateFrom: fromDate,
      dateTo: toDate,
      mode: 'DO',
      fields: fields.join(','),
    }, c)

    if (!data) return {}
    const d = Array.isArray(data) ? data[0] : data
    return d || {}
  } catch {
    return {}
  }
}

// ─── RuData: BondDateParams (offer_date, cpn_rate, current_fv) ─────────────────

async function getRuDataBondDateParams(isin: string, date: string, creds?: RuDataCreds): Promise<{
  offer_date: string | null
  cpn_rate: number | null
  current_fv: number | null
}> {
  const c = creds || getRuDataCreds()
  if (!c) return { offer_date: null, cpn_rate: null, current_fv: null }

  try {
    const data = await ruDataQuery('Bond/DateParams', {
      isin,
      date,
      fields: 'offer_date,cpn_rate,current_fv',
    }, c)

    if (!data) return { offer_date: null, cpn_rate: null, current_fv: null }
    const d = Array.isArray(data) ? data[0] : data

    return {
      offer_date: d?.offer_date ?? null,
      cpn_rate: d?.cpn_rate ?? null,
      current_fv: d?.current_fv ?? null,
    }
  } catch {
    return { offer_date: null, cpn_rate: null, current_fv: null }
  }
}

// ─── RuData: Рейтинги ─────────────────────────────────────────────────────────

async function getRuDataRatings(isin: string, creds?: RuDataCreds): Promise<RatingEntry[]> {
  const c = creds || getRuDataCreds()
  if (!c) return []

  try {
    const data = await ruDataQuery('Rating/List', {
      filter: `fintoolid = '${escFilter(isin)}' OR isin_code = '${escFilter(isin)}'`,
      count: 100,
    }, c)
    if (!data || !Array.isArray(data)) return []

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return data.map((r: Record<string, any>) => ({
      agency: (r.ra_name || r.agency || '') as string,
      rating: (r.last_rating || r.rating || '') as string,
      outlook: (r.forecast || r.outlook || null) as string | null,
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
      filter: `org_name LIKE '%${escFilter(issuerName)}%'`,
      count: 100,
    }, c)
    if (!data || !Array.isArray(data)) return []

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return data.map((r: Record<string, any>) => ({
      agency: (r.ra_name || r.agency || '') as string,
      rating: (r.last_rating || r.rating || '') as string,
      outlook: (r.forecast || r.outlook || null) as string | null,
      date: r.last_dt ? String(r.last_dt).split('T')[0] : null,
    }))
  } catch {
    return []
  }
}

// ─── Рейтинги с MOEX ISS (fallback) ─────────────────────────────────────────

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

// ─── G-curve (ZCYC) ────────────────────────────────────────────────────────────
// Аналог: _xll.GCurve(date, duration_days, "y") / 100
// GCurve возвращает % (например 19.15), делим на 100 → десятичная дробь

async function getGCurveYield(termYears: number, date?: string): Promise<number> {
  try {
    const params: Record<string, string> = {
      term: termYears.toString(),
      method: 'nelson_siegel',
    }
    if (date) params.date = date

    const resp = await fetch(`${API_BASE}/api/zcyc/interpolate`, {
      method: 'POST',
      headers: getApiHeaders(),
      body: JSON.stringify(params),
    })

    if (!resp.ok) {
      return await getGCurveFromMoex(termYears, date)
    }
    const data = await resp.json()
    // Backend возвращает значение в %, конвертируем в десятичную дробь
    return (data.value || 0) / 100
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

    // Nelson-Siegel параметры
    const p = rows[0]
    const b0 = p.b0 ?? p.B0 ?? 0
    const b1 = p.b1 ?? p.B1 ?? 0
    const b2 = p.b2 ?? p.B2 ?? 0
    const g1 = p.g1 ?? p.G1 ?? 1
    const tau = termYears || 1
    const x = tau / g1
    const expx = Math.exp(-x)
    const y = b0 + b1 * ((1 - expx) / x) + b2 * (((1 - expx) / x) - expx)
    return y / 100 // из % в десятичную дробь
  } catch {
    return 0
  }
}

// ─── Активность рынка ──────────────────────────────────────────────────────────
// Формулы из шаблона (Calculation sheet):
// I22 = EfirHistoryAgg(ISIN, date-30, date-1, "DO", "DEAL_ACC.SUM")  // кол-во сделок
// J22 = EfirHistoryAgg(ISIN, date-30, date-1, "DO", "DEAL_ACC.CNN")  // кол-во торговых дней
// K22 = EfirHistoryAgg(ISIN, date-30, date-1, "DO", "VAL_ACC.SUM")   // объём торгов
// Критерии: DEAL_ACC.SUM >= 10, DEAL_ACC.CNN >= 5, VAL_ACC.SUM/SumMarketVal >= 0.001

async function computeMarketActivity(
  isin: string,
  secid: string,
  valuationDate: string,
  outstandingAmount: number,
  history: BondTradeHistory[]
): Promise<import('./bondReportTypes').MarketActivityData> {
  const valDate = new Date(valuationDate)
  const fromDate = new Date(valDate.getTime() - 30 * 24 * 3600 * 1000)
  const fromStr = fromDate.toISOString().split('T')[0]
  const toStr = new Date(valDate.getTime() - 1 * 24 * 3600 * 1000).toISOString().split('T')[0]

  // Попытка получить из RuData EfirHistoryAgg
  const efirData = await getRuDataEfirHistoryAgg(
    isin, fromStr, toStr,
    ['DEAL_ACC.SUM', 'DEAL_ACC.CNN', 'VAL_ACC.SUM']
  )

  let trades = 0
  let tradingDays = 0
  let totalVolume = 0

  if (efirData && (efirData['DEAL_ACC.SUM'] !== undefined || efirData['DEAL_ACC.CNN'] !== undefined)) {
    trades = Number(efirData['DEAL_ACC.SUM']) || 0
    tradingDays = Number(efirData['DEAL_ACC.CNN']) || 0
    totalVolume = Number(efirData['VAL_ACC.SUM']) || 0
  } else {
    // Fallback: вычисляем из истории MOEX ISS
    const recent = history.filter(h => {
      const hd = new Date(h.date)
      return hd >= fromDate && hd <= valDate
    })
    tradingDays = recent.filter(r => r.num_trades > 0).length
    trades = recent.reduce((s, r) => s + r.num_trades, 0)
    totalVolume = recent.reduce((s, r) => s + r.value, 0)
  }

  const turnoverRatio = outstandingAmount > 0 ? totalVolume / outstandingAmount : 0

  // Критерии активности (из шаблона):
  // DEAL_ACC.SUM >= 10, DEAL_ACC.CNN >= 5, VAL_ACC.SUM/SumMarketVal >= 0.001
  const isActive = trades >= 10 && tradingDays >= 5 && turnoverRatio >= 0.001

  return {
    trading_days: tradingDays,
    trades,
    turnover_to_outstanding: turnoverRatio,
    traded_last_30d: tradingDays > 0,
    total_volume: totalVolume,
    is_active: isActive,
  }
}

// ─── Board auto-detection для облигаций ────────────────────────────────────────
// Пробуем TQCB (корп.), TQOB (ОФЗ), TQIR (ИЦБ), затем без доски

const BOND_BOARDS = ['TQCB', 'TQOB', 'TQIR'] as const

async function getBondHistoryAutoBoard(
  secid: string,
  startDate: string,
  endDate: string
): Promise<{ history: BondTradeHistory[]; board: string }> {
  for (const board of BOND_BOARDS) {
    const history = await getBondHistory(secid, startDate, endDate, board)
    if (history.length > 0) {
      return { history, board }
    }
  }
  return { history: [], board: 'TQCB' }
}

// ─── Получение купонного расписания из bondization ─────────────────────────────

async function getCouponSchedule(isin: string): Promise<{
  coupons: CouponPayment[]
  amortizations: AmortizationPayment[]
  offers: Array<{ date: string; type: string }>
}> {
  try {
    const resp = await moexRequest(`/securities/${isin}/bondization`)
    const couponsRaw = parseISSTable(resp, 'coupons')
    const amortRaw = parseISSTable(resp, 'amortizations')
    const offersRaw = parseISSTable(resp, 'offers')

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const coupons: CouponPayment[] = couponsRaw.map((c: Record<string, any>) => ({
      date: c.coupondate || c.COUPONDATE || '',
      value: c.value || c.VALUE || 0,
      valueprc: c.valueprc || c.VALUEPRC || 0,
      value_rub: c.value_rub || c.VALUE_RUB || c.value || c.VALUE || 0,
    }))

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const amortizations: AmortizationPayment[] = amortRaw.map((a: Record<string, any>) => ({
      date: a.amortdate || a.AMORTDATE || '',
      value: a.value || a.VALUE || 0,
      valueprc: a.valueprc || a.VALUEPRC || 0,
    }))

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const offers = offersRaw.map((o: Record<string, any>) => ({
      date: o.offerdate || o.OFFERDATE || '',
      type: o.offertypename || o.OFFERTYPENAME || '',
    }))

    return { coupons, amortizations, offers }
  } catch {
    return { coupons: [], amortizations: [], offers: [] }
  }
}

// ─── Индексы (MOEX ISS) ────────────────────────────────────────────────────────
// Формулы шаблона используют CbondsIndexValue(code, date)
// Коды Cbonds → тикеры MOEX из столбца CA шаблона:

// Группа "менее 1 года":
//   CC7 = гос. облигации <1Y → RUGBITR1Y (CB: 9201)
//   CC8 = корп. AAA <1Y → RUCBTRAAANS (CB: 80471)
//   CC9 = корп. AA <1Y → RUCBTRAANS (CB: 80479)
//   CC10 = корп. A <1Y → RUCBTRANS (CB: 80487)
// Группа "1-3 года":
//   CC11 = гос. 1-3Y → RUGBITR3Y (CB: 9209)
//   CC12 = корп. AAA 1-3Y → RUCBTR3A3YNS (CB: 80503)
//   CC13 = корп. AA 1-3Y → RUCBTRAA3YNS (CB: 80511)
//   CC14 = корп. A 1-3Y → RUCBTRA3YNS (CB: 80519)
// Группа "3-5 лет":
//   CC15 = гос. 3-5Y → RUGBITR5Y (CB: 9217)
//   CC16 = корп. AAA 3-5Y → RUCBTR3A5YNS (CB: 80527)
//   CC17 = корп. AA 3-5Y → RUCBTRAA5YNS (CB: 80535)
//   CC18 = корп. A 3-5Y → RUCBTRA5YNS (CB: 80543)
// Группа "более 5 лет":
//   CC19 = гос. 5+Y → RUGBITR5+ (CB: 9225)
// BBB (без привязки к дюрации):
//   CC20 = корп. BBB → RUCBTRBBBNS (CB: 80495)

interface IndexConfig {
  ticker: string
  name: string
}

function getIndicesByDuration(durationYears: number): {
  gov: IndexConfig
  aaa: IndexConfig
  aa: IndexConfig
  a: IndexConfig
  bbb: IndexConfig
} {
  // Логика из шаблона Template:
  // IF(O6<1, "<1Y", IF(O6<3, "1-3Y", IF(O6<5, "3-5Y", "5+Y")))
  if (durationYears < 1) {
    return {
      gov: { ticker: 'RUGBITR1Y', name: 'Доходность индекса государственных облигаций (менее года)' },
      aaa: { ticker: 'RUCBTRAAANS', name: 'Доходность индекса корпоративных облигаций с рейтингом AAA' },
      aa: { ticker: 'RUCBTRAANS', name: 'Доходность индекса корпоративных облигаций с рейтингом AA' },
      a: { ticker: 'RUCBTRANS', name: 'Доходность индекса корпоративных облигаций с рейтингом A' },
      bbb: { ticker: 'RUCBTRBBBNS', name: 'Доходность индекса корпоративных облигаций с рейтингом BBB' },
    }
  } else if (durationYears < 3) {
    return {
      gov: { ticker: 'RUGBITR3Y', name: 'Доходность индекса государственных облигаций (1-3 года)' },
      aaa: { ticker: 'RUCBTR3A3YNS', name: 'Доходность индекса корпоративных облигаций с рейтингом AAA (1-3 года)' },
      aa: { ticker: 'RUCBTRAA3YNS', name: 'Доходность индекса корпоративных облигаций с рейтингом AA (1-3 года)' },
      a: { ticker: 'RUCBTRA3YNS', name: 'Доходность индекса корпоративных облигаций с рейтингом A (1-3 года)' },
      bbb: { ticker: 'RUCBTRBBBNS', name: 'Доходность индекса корпоративных облигаций с рейтингом BBB' },
    }
  } else if (durationYears < 5) {
    return {
      gov: { ticker: 'RUGBITR5Y', name: 'Доходность индекса государственных облигаций (3-5 лет)' },
      aaa: { ticker: 'RUCBTR3A5YNS', name: 'Доходность индекса корпоративных облигаций с рейтингом AAA (3-5 лет)' },
      aa: { ticker: 'RUCBTRAA5YNS', name: 'Доходность индекса корпоративных облигаций с рейтингом AA (3-5 лет)' },
      a: { ticker: 'RUCBTRA5YNS', name: 'Доходность индекса корпоративных облигаций с рейтингом A (3-5 лет)' },
      bbb: { ticker: 'RUCBTRBBBNS', name: 'Доходность индекса корпоративных облигаций с рейтингом BBB' },
    }
  } else {
    return {
      gov: { ticker: 'RUGBITR5+', name: 'Доходность индекса государственных облигаций (более 5 лет)' },
      aaa: { ticker: 'RUCBTR3A5YNS', name: 'Доходность индекса корпоративных облигаций с рейтингом AAA (3-5 лет)' },
      aa: { ticker: 'RUCBTRAA5YNS', name: 'Доходность индекса корпоративных облигаций с рейтингом AA (3-5 лет)' },
      a: { ticker: 'RUCBTRA5YNS', name: 'Доходность индекса корпоративных облигаций с рейтингом A (3-5 лет)' },
      bbb: { ticker: 'RUCBTRBBBNS', name: 'Доходность индекса корпоративных облигаций с рейтингом BBB' },
    }
  }
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
    if (rows.length) {
      const row = rows[rows.length - 1]
      const y = row.close ?? row.CLOSE ?? row.currentvalue ?? row.CURRENTVALUE ?? null
      return y !== null ? y / 100 : null
    }
    // Fallback: история индекса
    return await getIndexYieldFallback(indexTicker, date)
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
    const val = last.CLOSE ?? last.close ?? null
    return val !== null ? val / 100 : null
  } catch {
    return null
  }
}

async function fetchIndicesByDuration(durationYears: number, date?: string): Promise<IndexYields> {
  const config = getIndicesByDuration(durationYears)
  const results: IndexYields = {}

  const [gov, aaa, aa, a, bbb] = await Promise.allSettled([
    getIndexYield(config.gov.ticker, date),
    getIndexYield(config.aaa.ticker, date),
    getIndexYield(config.aa.ticker, date),
    getIndexYield(config.a.ticker, date),
    getIndexYield(config.bbb.ticker, date),
  ])

  if (gov.status === 'fulfilled' && gov.value !== null) {
    if (durationYears < 1) results.gov_less_1y = gov.value
    else if (durationYears < 3) results.gov_1_3y = gov.value
    else if (durationYears < 5) results.gov_3_5y = gov.value
    else results.gov_5plus = gov.value
  }
  if (aaa.status === 'fulfilled' && aaa.value !== null) results.corp_aaa = aaa.value
  if (aa.status === 'fulfilled' && aa.value !== null) results.corp_aa = aa.value
  if (a.status === 'fulfilled' && a.value !== null) results.corp_a = a.value
  if (bbb.status === 'fulfilled' && bbb.value !== null) results.corp_bbb = bbb.value

  return results
}

// ─── Корпоративные события ─────────────────────────────────────────────────────

async function getCorporateEvents(isin: string): Promise<CorporateEvent[]> {
  const creds = getRuDataCreds()
  if (creds) {
    try {
      const data = await ruDataQuery('News/List', {
        filter: `isin_code = '${escFilter(isin)}'`,
        count: 20,
      }, creds)
      if (data && Array.isArray(data) && data.length > 0) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        return data.map((item: Record<string, any>) => ({
          date: item.pub_date ? String(item.pub_date).split('T')[0] : null,
          description: (item.title || item.subject || item.text || '') as string,
        }))
      }
    } catch { /* fallback to ISS */ }
  }

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

// ─── История цен ───────────────────────────────────────────────────────────────

function buildPriceHistory(history: BondTradeHistory[]): PriceHistoryPoint[] {
  return history
    .filter(h => h.close > 0 || (h.waprice && h.waprice > 0))
    .map(h => ({
      date: h.date,
      price: h.waprice || h.close,
    }))
}

// ─── Динамика доходности: 13 месячных точек ─────────────────────────────────
// Формулы из шаблона (Calculation sheet, столбцы J-Q, строки 6-18):
// J6 = B2 (дата оценки), J7 = EDATE(J6, -1), ... J18 = EDATE(J6, -12)
// K = ближайший торговый день (из Help Page)
// L = CbondsClosePrice(ISIN, K, 135)
// M = IF(B10="", CbondsCalcYTM, CbondsCalcYTP)(ISIN, K, L) → десятичная дробь
// N = IF(B10="", CbondsCalcDuration, CbondsCalcDurationToPutCall)(ISIN, K, L) → дни
// O = N / 365 → годы
// P = GCurve(K, N, "y") / 100 → десятичная дробь
// Q = (M - P) * 10000 → бп
// R = M * 100 → %
// S = P * 100 → %

async function buildYieldDynamics(
  secid: string,
  valuationDate: string,
  history: BondTradeHistory[],
  hasOffer: boolean,
  spec: SecuritySpec
): Promise<YieldHistoryPoint[]> {
  const points: YieldHistoryPoint[] = []
  const valDate = new Date(valuationDate)
  const matDate = new Date(spec.matdate)

  // Генерируем 13 месячных дат (от текущей назад)
  const monthlyDates: string[] = []
  for (let i = 0; i < 13; i++) {
    const d = new Date(valDate)
    d.setMonth(d.getMonth() - i)
    monthlyDates.push(d.toISOString().split('T')[0])
  }

  for (const targetDate of monthlyDates) {
    // Находим ближайший торговый день к этой дате
    const target = new Date(targetDate)
    let closest: BondTradeHistory | null = null
    let minDiff = Infinity

    for (const h of history) {
      if (!h.close && !h.waprice) continue
      const hDate = new Date(h.date)
      const diff = Math.abs(hDate.getTime() - target.getTime())
      if (diff < minDiff) {
        minDiff = diff
        closest = h
      }
    }

    // Пропускаем если ближайший день > 10 дней
    if (!closest || minDiff > 10 * 24 * 3600 * 1000) continue

    const tradeDate = new Date(closest.date)
    const yrsToMat = (matDate.getTime() - tradeDate.getTime()) / (365 * 24 * 3600 * 1000)

    // Получаем YTM/YTP
    let ytmDecimal = 0
    if (closest.yield_close && closest.yield_close > 0) {
      ytmDecimal = closest.yield_close / 100  // MOEX даёт в процентах
    } else if (closest.close > 0) {
      ytmDecimal = calcYTMFromPrice(
        closest.close,
        spec.facevalue,
        spec.couponpercent / 100,
        spec.couponfrequency || 2,
        yrsToMat
      )
    }
    if (ytmDecimal <= 0) continue

    // Дюрация в днях → годы (для G-curve)
    let durationDays = closest.duration || 0
    if (!durationDays && yrsToMat > 0) {
      durationDays = yrsToMat * 365
    }
    const durationYears = durationDays / 365

    // G-curve для этого срока
    const gcurveDecimal = await getGCurveYield(durationYears, closest.date)

    // R = M * 100, S = P * 100, Q = (M - P) * 10000
    const ytmPct = ytmDecimal * 100
    const gcurvePct = gcurveDecimal * 100
    const gspreadBps = (ytmDecimal - gcurveDecimal) * 10000

    points.push({
      date: closest.date,
      ytm: ytmPct,
      gcurve: gcurvePct,
      gspread: Math.round(gspreadBps * 100) / 100,
    })
  }

  // Сортируем по дате
  points.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
  return points
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
  const creds = getRuDataCreds()

  // 1. Спецификация бумаги (MOEX ISS)
  const spec = await getSecuritySpec(isin)

  // 2. RuData: FintoolReferenceData (_xll.ReferenceParams)
  const ruRef = await getRuDataFintoolRef(isin, creds ?? undefined)
  const ref0 = (ruRef && Array.isArray(ruRef) && ruRef.length > 0) ? ruRef[0] : null

  // B7 = BegDistDate, B8 = SumMarketVal, B9 = EndMtyDate, B13 = CouponPerYear
  const outstandingAmount = ref0?.sumissueval || ref0?.issueval || ref0?.summarketval || (spec.facevalue * 1000000)
  const offerDateFromRef = ref0?.offer_date || ref0?.offerdate || null // B25 (put+call)

  // 3. RuData: BondDateParams (_xll.BondDateParams)
  const dateParams = await getRuDataBondDateParams(isin, valuationDate, creds ?? undefined)
  // B10 = offer_date (пут), B11 = cpn_rate, B12 = current_fv
  const offerDatePut = dateParams.offer_date
  const currentCouponRate = dateParams.cpn_rate ?? (spec.couponpercent / 100)
  const currentFaceValue = dateParams.current_fv ?? spec.facevalue

  // 4. Определяем тип оферты
  // B23 = IF(AND(B25<>"",B24=""),"Call",IF(AND(B25<>"",B24<>""),"Put","Нет"))
  const offer = detectOfferType(offerDatePut, offerDateFromRef)
  const hasOffer = offer.type !== 'Нет'

  // 5. Текущие рыночные данные (MOEX ISS)
  const marketData = await getCurrentMarketData(spec.secid)

  // 6. История торгов за последний год (с авто-выбором борда)
  const endDate = valuationDate
  const startDate = new Date(new Date(endDate).getTime() - 395 * 24 * 3600 * 1000).toISOString().split('T')[0]
  const { history } = await getBondHistoryAutoBoard(spec.secid, startDate, endDate)

  // 6b. Купонное расписание и амортизация
  const bondization = await getCouponSchedule(isin)

  // 7. Оставшийся срок
  const valDate = new Date(valuationDate)
  const matDate = new Date(spec.matdate)
  const yearsToMaturity = (matDate.getTime() - valDate.getTime()) / (365 * 24 * 3600 * 1000)

  // 8. Чистая цена (аналог L6 = CbondsClosePrice)
  const cleanPricePct = marketData.last ?? marketData.waprice ?? marketData.closeprice ?? marketData.marketprice ?? 100

  // 9. RuData: Bond/Calculate — получаем YTM/YTP, duration, convexity, mod_duration
  const ruCalc = await getRuDataBondCalc(isin, valuationDate, cleanPricePct, creds ?? undefined)

  // 10. RuData: EfirYields — convexity, duration_n (B14, B15)
  const efirYields = await getRuDataEfirYields(isin, valuationDate, creds ?? undefined)

  // 11. RuData: EfirEndOfDay — duration, Y2O_LAST, DURATION_O (B16, B18, B20)
  const efirEod = await getRuDataEfirEndOfDay(
    isin, valuationDate,
    ['duration', 'Y2O_LAST', 'DURATION_O'],
    creds ?? undefined
  )

  // ═══ Сборка итоговых значений ═══

  // --- YTM или YTP ---
  // M6 = IF(B10="", CbondsCalcYTM, CbondsCalcYTP)(ISIN, date, price)
  let ytmDecimal: number
  let yieldType: 'YTM' | 'YTP' = 'YTM'

  if (hasOffer) {
    yieldType = 'YTP'
    // Приоритет: RuData YTP → EfirEndOfDay Y2O_LAST → MOEX yield → fallback
    ytmDecimal = (ruCalc?.ytp ?? null) !== null ? ruCalc!.ytp! :
      (efirEod['Y2O_LAST'] != null ? Number(efirEod['Y2O_LAST']) / 100 :
        (marketData.yield && marketData.yield > 0 ? marketData.yield / 100 :
          calcYTMFromPrice(cleanPricePct, currentFaceValue, currentCouponRate, spec.couponfrequency || 2, yearsToMaturity)))
  } else {
    yieldType = 'YTM'
    // Приоритет: RuData YTM → MOEX yield → fallback
    ytmDecimal = (ruCalc?.ytm ?? null) !== null ? ruCalc!.ytm! :
      (marketData.yield && marketData.yield > 0 ? marketData.yield / 100 :
        calcYTMFromPrice(cleanPricePct, currentFaceValue, currentCouponRate, spec.couponfrequency || 2, yearsToMaturity))
  }
  const ytmPct = ytmDecimal * 100

  // --- Дюрация ---
  // B16 = EfirEndOfDay(duration) / 365 (к погашению, в годах)
  // B19 = EfirEndOfDay(DURATION_O) / 365 (к оферте, в годах)
  let durationYears: number
  if (hasOffer) {
    // Дюрация к оферте
    const durO = efirEod['DURATION_O'] ?? efirEod['duration_o'] ?? null
    durationYears = durO != null ? Number(durO) / 365 :
      (ruCalc?.duration_years ?? null) !== null ? ruCalc!.duration_years! :
        (marketData.duration ? marketData.duration / 365 :
          calcDuration(ytmDecimal, currentFaceValue, currentCouponRate, spec.couponfrequency || 2, yearsToMaturity))
  } else {
    // Дюрация к погашению
    const dur = efirEod['duration'] ?? null
    durationYears = dur != null ? Number(dur) / 365 :
      (ruCalc?.duration_years ?? null) !== null ? ruCalc!.duration_years! :
        (marketData.duration ? marketData.duration / 365 :
          calcDuration(ytmDecimal, currentFaceValue, currentCouponRate, spec.couponfrequency || 2, yearsToMaturity))
  }

  // --- Модифицированная дюрация ---
  // B15 = EfirYields(duration_n)
  let modDuration: number
  modDuration = efirYields.duration_n ?? ruCalc?.mod_duration ?? (null as unknown as number)
  if (modDuration == null) {
    // Fallback: ModDur = MacaulayDur / (1 + y/m)
    modDuration = durationYears / (1 + ytmDecimal / (spec.couponfrequency || 2))
  }

  // --- Выпуклость ---
  // B14 = EfirYields(convexity)
  let convexity: number
  convexity = efirYields.convexity ?? ruCalc?.convexity ?? (null as unknown as number)
  if (convexity == null) {
    convexity = calcConvexity(ytmDecimal, currentFaceValue, currentCouponRate, spec.couponfrequency || 2, yearsToMaturity)
  }

  // --- G-curve yield ---
  // Из шаблона: GCurve(date, N6, "y") / 100 → десятичная дробь
  // N6 = дюрация в днях; для GCurve нужен срок в годах = N6/365
  const durationDaysForGCurve = durationYears * 365
  const gCurveDecimal = await getGCurveYield(durationYears, valuationDate)
  const gCurvePct = gCurveDecimal * 100

  // --- G-spread ---
  // B44 = (B42 - B45) * 100 → (ytm_pct - gcurve_pct) * 100 = бп
  const gSpreadBps = (ytmPct - gCurvePct) * 100
  const gSpreadBpsRounded = Math.round(gSpreadBps * 100) / 100

  // --- DV01 ---
  // B61 = ABS(1e6 * (-B59*0.0001 + 0.5*B60*0.0001^2))
  const dv01 = calcDV01(modDuration, convexity)

  // --- Dirty price ---
  const accruedInt = marketData.accruedint ?? (ruCalc?.accrued_interest ?? 0)
  const dirtyPrice = (cleanPricePct / 100) * currentFaceValue + accruedInt

  // 12. Рейтинги (RuData + MOEX ISS fallback)
  const [moexRatings, ruDataIssueRatings, ruDataIssuerRatings] = await Promise.all([
    getMoexRatings(isin),
    getRuDataRatings(isin, creds ?? undefined),
    spec.issuer ? getRuDataIssuerRatings(spec.issuer, creds ?? undefined) : Promise.resolve([]),
  ])

  const issueRatings = ruDataIssueRatings.length > 0 ? ruDataIssueRatings : moexRatings.issue
  const issuerRatings = ruDataIssuerRatings.length > 0 ? ruDataIssuerRatings : moexRatings.issuer

  // 13. Активность рынка (EfirHistoryAgg → fallback MOEX ISS)
  const marketActivity = await computeMarketActivity(isin, spec.secid, valuationDate, outstandingAmount, history)

  // 14. Индексы (зависят от дюрации)
  const indices = await fetchIndicesByDuration(durationYears, valuationDate)

  // 15. Корпоративные события
  const corporateEvents = await getCorporateEvents(isin)

  // 16. История цен
  const priceHistory = buildPriceHistory(history)

  // 17. Динамика доходности (13 месячных точек)
  const yieldHistory = await buildYieldDynamics(spec.secid, valuationDate, history, hasOffer, spec)

  // 18. Доп. данные из RuData
  let riskCountry = 'Россия'
  let sector = ''
  let industry = ''
  if (ref0) {
    riskCountry = ref0.country || ref0.issuercountry || 'Россия'
    sector = ref0.sectorbond || ref0.sector || ''
    industry = ref0.branch || ref0.industry || ''
  }

  // 19. НКД
  const nkd = marketData.accruedint ?? (ruCalc?.accrued_interest ?? null)

  // 20. Текущая доходность (CY)
  const currentYield = calcCurrentYield(currentCouponRate, currentFaceValue, cleanPricePct)

  // 21. Фильтрация купонов: будущие и прошедшие
  const futureCoupons = bondization.coupons.filter(c => new Date(c.date) > valDate)
  const pastCoupons = bondization.coupons.filter(c => new Date(c.date) <= valDate)

  return {
    isin: spec.isin || isin,
    issuer: spec.name || spec.shortname || spec.issuer || isin,
    risk_country: riskCountry,
    sector: sector || 'Корпоративный',
    industry,
    outstanding_amount: outstandingAmount,
    listing_level: spec.listlevel || null,
    currency: spec.faceunit || 'RUB',
    nkd,
    current_yield: currentYield > 0 ? Math.round(currentYield * 100) / 100 : null,
    issue_info: {
      issue_date: ref0?.begdistdate || spec.issuedate || null,
      maturity_date: ref0?.endmtydate || spec.matdate || null,
      coupon_rate: currentCouponRate,
      coupon_per_year: ref0?.couponperyear || spec.couponfrequency || null,
      nominal: currentFaceValue,
      offer: offer,
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
      ytm: ytmDecimal,
      ytm_pct: ytmPct,
      g_spread_bps: gSpreadBpsRounded,
      g_curve_yield: gCurveDecimal,
      g_curve_pct: gCurvePct,
      yield_type: yieldType,
    },
    risk_indicators: {
      duration: Math.round(durationYears * 10000) / 10000,
      mod_duration: Math.round(modDuration * 10000) / 10000,
      convexity: Math.round(convexity * 100) / 100,
      dv01: Math.round(dv01 * 100) / 100,
    },
    indices,
    corporate_events: corporateEvents,
    price_history: priceHistory,
    yield_history: yieldHistory,
    analogous_bonds: [],
    coupon_schedule: futureCoupons,
    amortization_schedule: bondization.amortizations.filter(a => new Date(a.date) > valDate),
  }
}

/**
 * Генерация полного отчёта по облигации-флоатеру.
 * Логика соответствует «Автоматизированный шаблон (для флоатеров).xlsm».
 */
export async function fetchFloaterBondReport(
  isin: string,
  valuationDate: string
): Promise<FloaterBondReport> {
  const creds = getRuDataCreds()

  // 1. Базовый отчёт (vanilla)
  const base = await fetchVanillaBondReport(isin, valuationDate)

  // 2. Доп. информация для флоатера (используем spec из base отчёта через повторный запрос,
  //    RuData ref уже подгружен в base)
  const spec = await getSecuritySpec(isin)

  // Определяем формулу купона, QM (quoted margin) и базовую ставку
  let couponFormula = ''
  let qmBps = 0 // Quoted Margin в bps
  let baseRateName: string | null = null
  let baseRateValue: number | null = null

  const ruRef = await getRuDataFintoolRef(isin, creds ?? undefined)
  if (ruRef && Array.isArray(ruRef) && ruRef.length > 0) {
    const ref0 = ruRef[0]
    couponFormula = ref0.coupon_type_desc || ref0.floatratename || ref0.coupondesc || ''
    if (ref0.floatratemargin) {
      qmBps = ref0.floatratemargin * 100 // из % в bps
    }
    // Определяем базовую ставку
    baseRateName = ref0.floatratename || ref0.base_rate_name || null
    if (ref0.floatratevalue != null) {
      baseRateValue = ref0.floatratevalue
    }
  }

  // Определяем название базовой ставки из формулы купона
  if (!baseRateName && couponFormula) {
    if (/КС|ключев/i.test(couponFormula)) baseRateName = 'Ключевая ставка ЦБ РФ'
    else if (/RUONIA/i.test(couponFormula)) baseRateName = 'RUONIA'
    else if (/MosPrime/i.test(couponFormula)) baseRateName = 'MosPrime Rate'
    else if (/ИПЦ|CPI/i.test(couponFormula)) baseRateName = 'ИПЦ'
  }

  // Парсим маржу из формулы если не нашли в RuData
  if (couponFormula && qmBps === 0) {
    const match = couponFormula.match(/([+-])\s*([\d,.]+)\s*%?\s*$/)
    if (match) {
      qmBps = parseFloat(match[2].replace(',', '.')) * (match[1] === '-' ? -100 : 100)
    }
  }

  if (!couponFormula && spec.couponpercent > 0) {
    couponFormula = `Переменная ставка (${spec.couponpercent}%)`
  }

  // DM (Discount Margin) из RuData Bond/Calculate
  let dmBps: number | null = null
  const ruCalc = await getRuDataBondCalc(isin, valuationDate, base.pricing.clean_price_pct, creds ?? undefined)
  if (ruCalc?.dm_bps != null) {
    dmBps = ruCalc.dm_bps
  }

  // Fallback: вычисляем DM через Newton's method в браузере
  if (dmBps == null && base.pricing.dirty_price && base.coupon_schedule.length > 0) {
    const valDate = new Date(valuationDate)
    const refRate = baseRateValue ?? (base.pricing.ytm_pct - (qmBps / 100)) // Приблизительная ref rate
    const cfForDM = base.coupon_schedule.map(c => {
      const cfDate = new Date(c.date)
      const yf = (cfDate.getTime() - valDate.getTime()) / (365 * 24 * 3600 * 1000)
      return {
        yearFraction: yf,
        amount: c.value || (c.valueprc / 100) * (spec.facevalue || 1000),
        refRate: refRate > 0 ? refRate : 15, // Fallback: 15% (типичная КС)
      }
    })
    // Добавляем погашение номинала в последний поток
    if (cfForDM.length > 0) {
      cfForDM[cfForDM.length - 1].amount += spec.facevalue || 1000
    }
    const cpnPerYear = base.issue_info.coupon_per_year || spec.couponfrequency || 4
    dmBps = calcDiscountMargin(
      base.pricing.dirty_price,
      spec.facevalue || 1000,
      cfForDM,
      cpnPerYear
    )
    dmBps = Math.round(dmBps * 100) / 100
  }

  // Следующий купон
  const resp = await moexRequest(`/securities/${isin}/bondization`)
  const coupons = parseISSTable(resp, 'coupons')
  const today = new Date(valuationDate)
  const futureCoupons = coupons
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    .filter((c: Record<string, any>) => new Date((c.coupondate || c.COUPONDATE || '') as string) > today)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    .sort((a: Record<string, any>, b: Record<string, any>) =>
      new Date(a.coupondate || a.COUPONDATE || '').getTime() -
      new Date(b.coupondate || b.COUPONDATE || '').getTime()
    )
  const nextCouponRate = futureCoupons.length > 0
    ? ((futureCoupons[0].valueprc ?? futureCoupons[0].VALUEPRC ?? futureCoupons[0].value ?? futureCoupons[0].VALUE ?? 0) / 100)
    : null

  // Кол-во выпусков эмитента в обращении
  let issuesCount: number | null = null
  if (creds && base.issuer) {
    try {
      const data = await ruDataQuery('Bond/List', {
        filter: `issuername LIKE '%${escFilter(base.issuer.substring(0, 20))}%' AND status = 'В обращении'`,
        count: 200,
      }, creds)
      if (data && Array.isArray(data)) {
        issuesCount = data.length
      }
    } catch { /* ignore */ }
  }

  // Анализируемый период
  const startDateFormatted = new Date(new Date(valuationDate).getTime() - 30 * 24 * 3600 * 1000)
  const analysisPeriod = `с ${formatDateRu(startDateFormatted)} по ${formatDateRu(new Date(valuationDate))}`

  // 3. DM/QM история (13 месячных точек)
  // Из Floater info sheet: DATE, DM, QM, PRICE
  const marginHistory = await buildMarginHistory(isin, spec.secid, valuationDate, qmBps, spec)

  return {
    ...base,
    issues_count: issuesCount,
    analysis_period: analysisPeriod,
    coupon_formula: couponFormula || null,
    base_rate_name: baseRateName,
    base_rate_value: baseRateValue,
    dm_bps: dmBps,
    qm_bps: qmBps || null,
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

// ─── DM/QM история для флоатера ─────────────────────────────────────────────

async function buildMarginHistory(
  isin: string,
  secid: string,
  valuationDate: string,
  qmBps: number,
  spec: SecuritySpec
): Promise<MarginHistoryPoint[]> {
  const creds = getRuDataCreds()
  const points: MarginHistoryPoint[] = []
  const valDate = new Date(valuationDate)

  // 13 месячных дат
  for (let i = 0; i < 13; i++) {
    const d = new Date(valDate)
    d.setMonth(d.getMonth() - i)
    const dateStr = d.toISOString().split('T')[0]

    // Пытаемся получить DM из RuData Bond/Calculate для каждой даты
    const ruCalc = await getRuDataBondCalc(isin, dateStr, undefined, creds ?? undefined)

    if (ruCalc?.dm_bps != null) {
      points.push({
        date: dateStr,
        dm: ruCalc.dm_bps,
        qm: qmBps,
        price: undefined,
      })
    }
  }

  // Если RuData не дал данных, fallback с аппроксимацией
  if (points.length === 0) {
    const startDate = new Date(valDate.getTime() - 395 * 24 * 3600 * 1000).toISOString().split('T')[0]
    const history = await getBondHistory(secid, startDate, valuationDate)

    for (let i = 0; i < 13; i++) {
      const d = new Date(valDate)
      d.setMonth(d.getMonth() - i)
      const target = d.getTime()

      // Найти ближайший торговый день
      let closest: BondTradeHistory | null = null
      let minDiff = Infinity
      for (const h of history) {
        const diff = Math.abs(new Date(h.date).getTime() - target)
        if (diff < minDiff && h.yield_close != null) {
          minDiff = diff
          closest = h
        }
      }

      if (closest && minDiff < 10 * 24 * 3600 * 1000) {
        // DM аппроксимация: (YTM - baseRate) в bps
        // baseRate ≈ YTM - QM (упрощённо)
        const ytmBps = (closest.yield_close || 0) * 100
        const dmApprox = ytmBps - qmBps

        points.push({
          date: closest.date,
          dm: dmApprox,
          qm: qmBps,
          price: closest.close || undefined,
        })
      }
    }
  }

  // Сортируем по дате
  points.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
  return points
}

/**
 * Загрузить данные по облигации-аналогу (для scatter-графика).
 * Формулы из шаблона (Calculation, I34:T42):
 *   K = IF(R="O", YTP, YTM) * 100  (доходность в %)
 *   L = IF(R="O", DurationToPutCall, Duration)  (в годах)
 *   R = IF(BondDateParams(ISIN, date, "offer_date") exists, "O", "нет")
 */
export async function fetchAnalogBondData(
  analogIsin: string,
  valuationDate: string
): Promise<AnalogousBond | null> {
  try {
    const creds = getRuDataCreds()
    const spec = await getSecuritySpec(analogIsin)
    const mkt = await getCurrentMarketData(spec.secid)

    const matDate = new Date(spec.matdate)
    const valDate = new Date(valuationDate)
    const yearsToMat = (matDate.getTime() - valDate.getTime()) / (365 * 24 * 3600 * 1000)

    const cleanPrice = mkt.last ?? mkt.waprice ?? mkt.closeprice ?? mkt.marketprice ?? 100

    // Проверяем оферту аналога
    const dateParams = await getRuDataBondDateParams(analogIsin, valuationDate, creds ?? undefined)
    const ruRef = await getRuDataFintoolRef(analogIsin, creds ?? undefined)
    const refOfferDate = (ruRef && Array.isArray(ruRef) && ruRef.length > 0) ? (ruRef[0].offer_date || ruRef[0].offerdate || null) : null
    const offer = detectOfferType(dateParams.offer_date, refOfferDate)
    const hasOffer = offer.type !== 'Нет'

    // Получаем расчёт из RuData
    const ruCalc = await getRuDataBondCalc(analogIsin, valuationDate, cleanPrice, creds ?? undefined)

    // Доходность
    let bondYield: number
    if (hasOffer && ruCalc?.ytp != null) {
      bondYield = ruCalc.ytp * 100
    } else if (ruCalc?.ytm != null) {
      bondYield = ruCalc.ytm * 100
    } else if (mkt.yield && mkt.yield > 0) {
      bondYield = mkt.yield
    } else {
      bondYield = calcYTMFromPrice(
        cleanPrice,
        spec.facevalue,
        spec.couponpercent / 100,
        spec.couponfrequency || 2,
        yearsToMat
      ) * 100
    }

    // Дюрация
    let duration: number
    if (ruCalc?.duration_years != null) {
      duration = ruCalc.duration_years
    } else if (mkt.duration && mkt.duration > 0) {
      duration = mkt.duration / 365
    } else {
      duration = calcDuration(
        bondYield / 100,
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
      yield: bondYield,
      has_offer: hasOffer,
    }
  } catch {
    return null
  }
}

// ─── Утилиты ───────────────────────────────────────────────────────────────────

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
