export interface PricePoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface HeatmapAsset {
  asset: string;
  volatility: number;
  correlation: number;
  notional: number;
  pnl: number;
  pnlPct: number;
}
