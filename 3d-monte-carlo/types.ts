
export interface SimulationConfig {
  initialPrice: number;
  drift: number;
  volatility: number;
  timeSteps: number;
  numPaths: number;
  dt: number;
  // New parameters for Fat Tail / Jump Diffusion
  jumpIntensity: number; // Lambda: probability of a jump occurring per step
  jumpMean: number;      // Average size of jump
  jumpSd: number;        // Volatility of the jump size
}

export interface PathPoint {
  x: number; // Time
  y: number; // Price/Value
  z: number; // Simulation Index
  isJump?: boolean; // Marker for visualization
}

export interface SimulationResult {
  paths: PathPoint[][];
  jumps: PathPoint[]; // Store jump points for specific rendering
  stats: {
    meanFinalPrice: number;
    maxPrice: number;
    minPrice: number;
    stdDev: number;
  };
}
