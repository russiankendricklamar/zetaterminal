export interface DataPoint {
  date: string;
  price: number;
  return: number;
  volatility: number; // Underlying instantaneous volatility
  index: number;
}

export interface CVRCData {
  timeIndices: string[]; // Y-axis labels (Dates)
  periods: number[]; // X-axis labels (Periods)
  surfaceZ: number[][]; // Z-axis values (Intensity/Volatility)
  peak: {
    x: number; // Period
    y: string; // Date
    z: number; // Intensity
    xIndex: number;
    yIndex: number;
  } | null;
  priceData: DataPoint[];
}

export enum ChartViewMode {
  SURFACE = 'SURFACE',
  WIREFRAME = 'WIREFRAME'
}