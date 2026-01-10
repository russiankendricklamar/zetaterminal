import { CVRCData, DataPoint } from '../types';

export const PERIODS = [5, 10, 15, 20, 25, 30, 40, 50, 60];

// Helper to generate a date string
const formatDate = (index: number): string => {
  const date = new Date(2023, 0, 1);
  date.setDate(date.getDate() + index);
  return date.toISOString().split('T')[0];
};

// Gaussian smoothing kernel for 2D array
const smoothSurface = (matrix: number[][], sigma: number = 1): number[][] => {
  const rows = matrix.length;
  const cols = matrix[0].length;
  const result: number[][] = Array.from({ length: rows }, () => new Array(cols).fill(0));

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      let sum = 0;
      let count = 0;

      for (let i = -1; i <= 1; i++) {
        for (let j = -1; j <= 1; j++) {
          const nr = r + i;
          const nc = c + j;
          if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
            sum += matrix[nr][nc];
            count++;
          }
        }
      }
      result[r][c] = sum / count;
    }
  }
  return result;
};

// Generate a single next data point based on previous history
export const generateNextDataPoint = (lastPoint: DataPoint, index: number): DataPoint => {
  let currentVol = lastPoint.volatility;
  let currentPrice = lastPoint.price;

  // Randomly spike volatility to create "events"
  if (Math.random() > 0.95) {
    currentVol = 0.05 + Math.random() * 0.05; // Spike
  } else {
    // Mean reversion of volatility
    currentVol = currentVol * 0.9 + 0.01 * 0.1;
  }

  const shock = (Math.random() - 0.5) * 2; // -1 to 1
  const ret = shock * currentVol;
  currentPrice = currentPrice * (1 + ret);

  return {
    date: formatDate(index),
    price: currentPrice,
    return: ret,
    volatility: currentVol,
    index: index,
  };
};

// Calculate CVRC Surface from a window of price data
export const calculateCVRC = (priceData: DataPoint[]): CVRCData => {
  const length = priceData.length;
  const returns = priceData.map(d => d.return);
  const timeIndices = priceData.map(d => d.date);
  
  // Initialize Z matrix (rows = time, cols = periods)
  let surfaceZ: number[][] = [];

  for (let t = 0; t < length; t++) {
    const row: number[] = [];
    for (let pIdx = 0; pIdx < PERIODS.length; pIdx++) {
      const windowSize = PERIODS[pIdx];
      
      if (t < windowSize) {
        row.push(0); // Not enough data yet
        continue;
      }

      // Convolution: Calculate volatility (std dev) over the window
      const slice = returns.slice(t - windowSize, t);
      const mean = slice.reduce((a, b) => a + b, 0) / windowSize;
      const variance = slice.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / windowSize;
      const stdDev = Math.sqrt(variance);

      // Annualized volatility intensity
      row.push(stdDev * Math.sqrt(252)); 
    }
    surfaceZ.push(row);
  }

  // Apply Smoothing
  surfaceZ = smoothSurface(surfaceZ);
  surfaceZ = smoothSurface(surfaceZ);

  // Find Peak
  let maxZ = -Infinity;
  let peakCoords = null;

  for (let y = 0; y < surfaceZ.length; y++) {
    for (let x = 0; x < surfaceZ[y].length; x++) {
      if (surfaceZ[y][x] > maxZ) {
        maxZ = surfaceZ[y][x];
        peakCoords = {
          x: PERIODS[x],
          y: timeIndices[y],
          z: maxZ,
          xIndex: x,
          yIndex: y
        };
      }
    }
  }

  return {
    timeIndices,
    periods: PERIODS,
    surfaceZ,
    peak: peakCoords,
    priceData,
  };
};

// Generate initial dataset
export const generateSyntheticData = (length: number = 200): CVRCData => {
  const priceData: DataPoint[] = [];
  let currentPrice = 100;
  let currentVol = 0.01; 

  // Initial seed point
  priceData.push({
    date: formatDate(0),
    price: currentPrice,
    return: 0,
    volatility: currentVol,
    index: 0
  });

  for (let i = 1; i < length; i++) {
    const nextPoint = generateNextDataPoint(priceData[i-1], i);
    priceData.push(nextPoint);
  }

  return calculateCVRC(priceData);
};