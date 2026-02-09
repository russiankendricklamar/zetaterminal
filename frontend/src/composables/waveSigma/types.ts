export enum MarketRegime {
  TRENDING = 'TRENDING',
  CHOPPY = 'CHOPPY',
  TRANSITION = 'TRANSITION'
}

export interface SimulationData {
  position: number
  equity: number
  price: number
  timestamp: number
}

export interface WaveConfig {
  speed: number
  volatility: number
  trendStrength: number
}

export interface WaveSigmaStats {
  regime: MarketRegime
  equity: number
  elapsedDays: number
  position: number
}
