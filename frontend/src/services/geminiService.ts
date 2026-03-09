import { Candle, AIAnalysisResult } from '@/types/terminal'
import { getApiHeaders } from '@/utils/apiHeaders'
import { getApiBaseUrl } from '@/utils/apiBase'

const API_BASE = getApiBaseUrl()

export const analyzeMarketData = async (candles: Candle[]): Promise<AIAnalysisResult> => {
  try {
    const response = await fetch(`${API_BASE}/api/gemini/analyze`, {
      method: 'POST',
      headers: getApiHeaders(),
      body: JSON.stringify({
        candles: candles.slice(-20).map(c => ({
          time: c.time,
          open: c.open,
          high: c.high,
          low: c.low,
          close: c.close,
          volume: c.volume,
        })),
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    return await response.json() as AIAnalysisResult
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error)
    console.error('AI Analysis Failed:', message)

    const lastPrice = candles[candles.length - 1]?.close || 0
    const prevPrice = candles[candles.length - 2]?.close || lastPrice
    const trend = lastPrice > prevPrice ? 'BULLISH' : lastPrice < prevPrice ? 'BEARISH' : 'NEUTRAL'

    return {
      trend,
      confidence: 0,
      reasoning: 'AI Service Temporarily Unavailable',
      keyLevels: {
        support: lastPrice * 0.95,
        resistance: lastPrice * 1.05,
      },
    }
  }
}
