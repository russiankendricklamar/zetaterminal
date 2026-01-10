
import React, { useState, useCallback, useEffect } from 'react';
import { runMonteCarlo } from './services/simulation';
import { SimulationConfig, SimulationResult } from './types';
import SimulationCanvas from './components/SimulationCanvas';

// Default config tuned for the "Fat Tail" look
const DEFAULT_CONFIG: SimulationConfig = {
  initialPrice: 1000000, // Start at 1M
  drift: 0.1,           // Increased drift for growth potential
  volatility: 0.25,     // Higher volatility to create wider spread
  timeSteps: 252,       // One trading year
  numPaths: 100,
  dt: 1 / 252,
  jumpIntensity: 2.0, 
  jumpMean: 0.05,       
  jumpSd: 0.15,
};

const App: React.FC = () => {
  const [config, setConfig] = useState<SimulationConfig>(DEFAULT_CONFIG);
  const [result, setResult] = useState<SimulationResult>(() => runMonteCarlo(DEFAULT_CONFIG));

  const handleRunSimulation = useCallback(() => {
    const newResult = runMonteCarlo(config);
    setResult(newResult);
  }, [config]);

  // Initial run
  useEffect(() => {
    handleRunSimulation();
  }, []);

  return (
    // Changed bg-black to a deep radial gradient
    <div className="relative w-screen h-screen bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-gray-900 via-[#050510] to-black overflow-hidden font-inter text-white">
      
      {/* 3D View */}
      <div className="absolute inset-0 z-0">
        <SimulationCanvas result={result} />
      </div>
    </div>
  );
};

export default App;
