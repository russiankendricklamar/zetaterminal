/**
 * Pure financial math functions for bond report calculations.
 *
 * Extracted from bondReportService.ts — no data fetching, no side effects.
 */

import type { OfferInfo } from './bondReportTypes'

// ─── DV01 (из шаблона) ─────────────────────────────────────────────────────────
// B61 = ABS(1000000*((-B59*0.0001)+(0.5*B60*0.0001*0.0001)))
// B59 = mod_duration, B60 = convexity

export function calcDV01(modDuration: number, convexity: number): number {
  return Math.abs(1_000_000 * ((-modDuration * 0.0001) + (0.5 * convexity * 0.0001 * 0.0001)))
}

// ─── Fallback: локальные вычисления YTM, дюрации, выпуклости ────────────────

export function calcYTMFromPrice(
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

  let y = couponRate || 0.1
  for (let iter = 0; iter < 200; iter++) {
    let pv = 0
    let dpv = 0
    for (let t = 1; t <= n; t++) {
      const cf = t === n ? C + faceValue : C
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

export function calcDuration(
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

export function calcConvexity(
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

// ─── Discount Margin (DM) — Newton's method для флоатеров ────────────────────
// Уравнение: Pd = Σ[(Ci + Ni) / (1 + Indexi/(100*n) + DM/n)^(yfi*n)]
// DM в базисных пунктах (bps)

export function calcDiscountMargin(
  dirtyPrice: number,
  faceValue: number,
  couponPayments: Array<{ yearFraction: number; amount: number; refRate: number }>,
  paymentsPerYear: number,
  maxIter = 100,
  tol = 1e-8
): number {
  if (!couponPayments.length || dirtyPrice <= 0 || paymentsPerYear <= 0) return 0
  const n = paymentsPerYear

  let dmBps = 0

  for (let iter = 0; iter < maxIter; iter++) {
    let pCalc = 0
    let pDeriv = 0
    const dmDecimal = dmBps / 10000

    for (const cf of couponPayments) {
      const indexRate = cf.refRate / 100
      const discountRate = indexRate / n + dmDecimal / n
      const exponent = cf.yearFraction * n
      const discFactor = Math.pow(1 + discountRate, exponent)

      if (discFactor <= 0) continue
      pCalc += cf.amount / discFactor
      pDeriv += -cf.amount * exponent * (1 / n) / Math.pow(1 + discountRate, exponent + 1)
    }

    const err = pCalc - dirtyPrice
    if (Math.abs(err) < tol) break
    if (Math.abs(pDeriv) < 1e-12) break

    dmBps -= err / pDeriv

    if (dmBps < -5000) dmBps = -4999
    if (dmBps > 50000) dmBps = 49999
  }

  return dmBps
}

// ─── Текущая доходность (Current Yield) ─────────────────────────────────────
// CY = (annual_coupon / clean_price_rub) * 100

export function calcCurrentYield(
  couponRate: number,
  faceValue: number,
  cleanPricePct: number
): number {
  if (cleanPricePct <= 0) return 0
  const annualCoupon = couponRate * faceValue
  const cleanPriceRub = (cleanPricePct / 100) * faceValue
  return (annualCoupon / cleanPriceRub) * 100
}

// ─── Оферта: определение типа ──────────────────────────────────────────────────
// Формула из шаблона: B23=IF(AND(B25<>"",B24=""),"Call",IF(AND(B25<>"",B24<>""),"Put","Нет"))
// B24 = offer_date (пут оферта, из BondDateParams)
// B25 = offer_date (пут+колл, из ReferenceParams)

export function detectOfferType(
  offerDatePut: string | null | undefined,
  offerDatePutCall: string | null | undefined
): OfferInfo {
  const hasPut = !!offerDatePut && offerDatePut.trim() !== ''
  const hasPutCall = !!offerDatePutCall && offerDatePutCall.trim() !== ''

  if (hasPutCall && !hasPut) {
    return { type: 'Call', date: offerDatePutCall! }
  }
  if (hasPutCall && hasPut) {
    return { type: 'Put', date: offerDatePut! }
  }
  return { type: 'Нет', date: null }
}

// ─── Утилиты ───────────────────────────────────────────────────────────────────

export function formatDateRu(d: Date): string {
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  return `${day}.${month}.${year}`
}
