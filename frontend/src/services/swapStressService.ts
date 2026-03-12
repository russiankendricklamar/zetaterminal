import { getApiBaseUrl } from '@/utils/apiBase'
import { getApiHeaders } from '@/utils/apiHeaders'

export interface SwapPosition {
  notional: number
  tenor: number
  fixed_rate: number
  floating_rate: number
  spread: number
  coupons_per_year: number
  discount_rate: number
  volatility?: number
  swap_type: string
}

export interface SwapStressScenario {
  id: number
  name: string
  description: string
  shockType: string
  severity: string
  probability: number
  duration: string
  shocks: Record<string, number>
}

export interface SwapStressResult {
  id: number
  name: string
  description: string
  shockType: string
  severity: string
  probability: number
  duration: string
  pnlImpact: number
  dv01Change: number
  spreadDv01: number
  delta: number
  gamma: number
  vega: number
  theta: number
  keyRateDurations: Record<string, number>
  marketShocks: Record<string, string>
  positionImpact: Record<string, number>
}

export async function runSwapStressTests(
  positions: SwapPosition[],
  multiplier: number = 1.0,
  scenarios?: SwapStressScenario[],
): Promise<SwapStressResult[]> {
  const response = await fetch(`${getApiBaseUrl()}/api/swap-stress/test`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify({
      positions,
      multiplier,
      scenarios: scenarios ?? null,
    }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Stress test failed: ${response.status}`)
  }

  return response.json()
}

export async function fetchSwapStressScenarios(): Promise<SwapStressScenario[]> {
  const response = await fetch(`${getApiBaseUrl()}/api/swap-stress/scenarios`, {
    method: 'GET',
    headers: getApiHeaders(),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Failed to fetch scenarios: ${response.status}`)
  }

  return response.json()
}
