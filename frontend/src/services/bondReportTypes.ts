// ─── Типы ──────────────────────────────────────────────────────────────────────

export interface RatingEntry {
  agency: string
  rating: string
  outlook?: string | null
  date?: string | null
}

export interface MarketActivityData {
  trading_days: number       // DEAL_ACC.CNN (кол-во торговых дней)
  trades: number             // DEAL_ACC.SUM (кол-во сделок)
  turnover_to_outstanding: number  // VAL_ACC.SUM / SumMarketVal
  traded_last_30d: boolean
  total_volume?: number      // VAL_ACC.SUM
  is_active: boolean         // AND(trades>=10, trading_days>=5, turnover>=0.001)
}

export interface PricingData {
  clean_price_pct: number    // Рыночная котировка, % от номинала
  dirty_price?: number
  ytm: number                // YTM или YTP (десятичная дробь, например 0.1993)
  ytm_pct: number            // YTM/YTP в процентах (например 19.93)
  g_spread_bps: number       // G-spread в б.п. = (ytm_pct - gcurve_pct) * 100
  g_curve_yield: number      // G-curve в десятичной дроби
  g_curve_pct: number        // G-curve в процентах
  yield_type: 'YTM' | 'YTP' // Тип доходности
}

export interface RiskIndicators {
  duration: number           // Дюрация в годах (из EfirEndOfDay / 365)
  mod_duration: number       // Мод. дюрация (из EfirYields duration_n)
  convexity: number          // Выпуклость (из EfirYields convexity)
  dv01: number               // DV01 = ABS(1e6 * (-modDur*0.0001 + 0.5*conv*0.0001^2))
  pvbp?: number
}

export interface OfferInfo {
  type: 'Call' | 'Put' | 'Нет'  // Тип оферты
  date: string | null            // Дата оферты
}

export interface IssueInfo {
  issue_date: string | null        // BegDistDate
  maturity_date: string | null     // EndMtyDate
  coupon_rate: number | null       // cpn_rate (текущий купон, доля)
  coupon_per_year: number | null   // CouponPerYear
  coupon_formula?: string | null
  next_coupon?: number | null
  nominal?: number | null          // current_fv (текущий номинал)
  offer?: OfferInfo
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
  has_offer?: boolean
}

export interface IndexYields {
  gov_less_1y?: number
  gov_1_3y?: number
  gov_3_5y?: number
  gov_5plus?: number
  corp_aaa?: number
  corp_aa?: number
  corp_a?: number
  corp_bbb?: number
}

export interface PriceHistoryPoint {
  date: string
  price: number
}

export interface YieldHistoryPoint {
  date: string
  ytm: number       // % (например 19.93)
  gcurve: number     // % (например 19.15)
  gspread: number    // бп (например 78)
}

export interface MarginHistoryPoint {
  date: string
  dm: number    // Discount Margin, bps
  qm: number    // Quoted Margin, bps
  price?: number
}

export interface CouponPayment {
  date: string
  value: number          // Сумма купона в руб.
  valueprc: number       // Ставка купона, %
  value_rub: number      // Купон в рублях на одну облигацию
}

export interface AmortizationPayment {
  date: string
  value: number         // Сумма амортизации в руб.
  valueprc: number      // % от номинала
}

export interface VanillaBondReport {
  isin: string
  issuer: string
  risk_country: string | null
  sector: string | null
  industry: string | null
  outstanding_amount: number | null
  listing_level: number | null
  currency: string
  nkd: number | null                  // НКД (Накопленный купонный доход)
  current_yield: number | null        // Текущая доходность CY = (coupon_rate / clean_price) * 100
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
  coupon_schedule: CouponPayment[]
  amortization_schedule: AmortizationPayment[]
}

export interface FloaterBondReport extends VanillaBondReport {
  issues_count: number | null
  analysis_period: string | null
  coupon_formula: string | null
  base_rate_name: string | null        // Название базовой ставки (КС, RUONIA и т.д.)
  base_rate_value: number | null       // Текущее значение базовой ставки, %
  margin_history: MarginHistoryPoint[]
  dm_bps: number | null
  qm_bps: number | null
  analogous_bonds_note?: string
}

// ─── Internal types ─────────────────────────────────────────────────────────

export interface SecuritySpec {
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

export interface BondTradeHistory {
  date: string
  close: number
  yield_close: number | null
  volume: number
  num_trades: number
  value: number
  waprice: number | null
  duration: number | null
}

export interface CurrentMarketData {
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

export interface RuDataCreds {
  login: string
  password: string
}

export interface RuDataBondCalcResult {
  ytm: number | null            // YTM (десятичная дробь)
  ytp: number | null            // YTP (десятичная дробь)
  duration_days: number | null  // Дюрация в днях
  duration_years: number | null // Дюрация в годах
  mod_duration: number | null   // Модифицированная дюрация
  convexity: number | null      // Выпуклость
  offer_date: string | null     // Дата оферты
  coupon_rate: number | null    // Текущая ставка купона
  facevalue: number | null      // Текущий номинал
  accrued_interest: number | null
  dm_bps: number | null         // Дисконтная маржа (для флоатеров)
}
