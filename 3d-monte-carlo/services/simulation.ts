
import { SimulationConfig, SimulationResult, PathPoint } from '../types';

/**
 * Generates Monte Carlo paths using Merton Jump Diffusion Model.
 * This introduces "Fat Tails" (sudden shocks) into the simulation.
 */
export const runMonteCarlo = (config: SimulationConfig): SimulationResult => {
  const { 
    initialPrice, drift, volatility, timeSteps, numPaths, dt,
    jumpIntensity, jumpMean, jumpSd 
  } = config;
  
  const paths: PathPoint[][] = [];
  const allJumps: PathPoint[] = [];
  
  let totalFinalPrice = 0;
  let maxPrice = -Infinity;
  let minPrice = Infinity;
  const finalPrices: number[] = [];

  for (let i = 0; i < numPaths; i++) {
    const path: PathPoint[] = [];
    let currentPrice = initialPrice;
    
    // Start at t=0
    path.push({ x: 0, y: currentPrice, z: i });

    for (let t = 1; t <= timeSteps; t++) {
      // 1. Standard Geometric Brownian Motion Component
      const u1 = Math.random();
      const u2 = Math.random();
      const z = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
      
      let diffusion = (drift - 0.5 * volatility * volatility) * dt + volatility * Math.sqrt(dt) * z;

      // 2. Jump Component (Poisson Process)
      let jumpMultiplier = 1;
      let isJumpStep = false;

      // Poisson check: does a jump occur?
      if (Math.random() < jumpIntensity * dt) {
        isJumpStep = true;
        // Generate jump size (Log-normal distribution)
        const jU1 = Math.random();
        const jU2 = Math.random();
        const jZ = Math.sqrt(-2.0 * Math.log(jU1)) * Math.cos(2.0 * Math.PI * jU2);
        
        // Jump magnitude
        const jumpMagnitude = jumpMean + jumpSd * jZ;
        jumpMultiplier = Math.exp(jumpMagnitude);
      }

      // Calculate new price
      // S(t) = S(t-1) * exp(diffusion) * jumpMultiplier
      currentPrice = currentPrice * Math.exp(diffusion) * jumpMultiplier;
      
      const point: PathPoint = { x: t, y: currentPrice, z: i, isJump: isJumpStep };
      path.push(point);

      if (isJumpStep) {
        allJumps.push(point);
      }
      
      maxPrice = Math.max(maxPrice, currentPrice);
      minPrice = Math.min(minPrice, currentPrice);
    }
    
    paths.push(path);
    totalFinalPrice += currentPrice;
    finalPrices.push(currentPrice);
  }

  const meanFinalPrice = totalFinalPrice / numPaths;
  const variance = finalPrices.reduce((acc, p) => acc + Math.pow(p - meanFinalPrice, 2), 0) / numPaths;
  const stdDev = Math.sqrt(variance);

  return {
    paths,
    jumps: allJumps,
    stats: {
      meanFinalPrice,
      maxPrice,
      minPrice,
      stdDev
    }
  };
};
