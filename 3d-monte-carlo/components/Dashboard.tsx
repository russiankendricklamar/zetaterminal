
import React from 'react';
import { SimulationConfig, SimulationResult } from '../types';

interface DashboardProps {
  config: SimulationConfig;
  setConfig: (config: SimulationConfig) => void;
  result: SimulationResult;
  onRun: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ config, setConfig, result, onRun }) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setConfig({
      ...config,
      [name]: parseFloat(value) || 0,
    });
  };

  return (
    <div className="w-80 h-full bg-black/80 backdrop-blur-xl border-l border-white/10 overflow-y-auto p-6 text-xs font-mono">
      <div className="mb-6 border-b border-white/20 pb-4">
        <h1 className="text-lg font-bold text-white uppercase tracking-widest">Model Config</h1>
        <div className="text-cyan-500 mt-1">JUMP DIFFUSION (MERTON)</div>
      </div>

      {/* Basic Controls */}
      <div className="space-y-5 mb-8">
        <div>
          <label className="text-gray-500 block mb-1">DRIFT (μ)</label>
          <input
            type="range" min="-0.5" max="0.5" step="0.01"
            name="drift" value={config.drift} onChange={handleChange}
            className="w-full accent-cyan-500"
          />
        </div>

        <div>
          <label className="text-gray-500 block mb-1">VOLATILITY (σ)</label>
          <input
            type="range" min="0.01" max="1" step="0.01"
            name="volatility" value={config.volatility} onChange={handleChange}
            className="w-full accent-cyan-500"
          />
        </div>
      </div>

      {/* Fat Tail Controls */}
      <div className="space-y-4 mb-8 border border-red-900/50 bg-red-900/10 p-4 rounded">
        <div className="text-red-400 font-bold mb-2 uppercase">Fat Tail Parameters</div>
        
        <div>
          <label className="text-gray-400 block mb-1">JUMP INTENSITY (λ)</label>
          <input
            type="number" step="0.1"
            name="jumpIntensity" value={config.jumpIntensity} onChange={handleChange}
            className="w-full bg-black border border-red-900/50 rounded px-2 py-1 text-white"
          />
        </div>

        <div>
          <label className="text-gray-400 block mb-1">JUMP MEAN</label>
          <input
            type="number" step="0.01"
            name="jumpMean" value={config.jumpMean} onChange={handleChange}
            className="w-full bg-black border border-red-900/50 rounded px-2 py-1 text-white"
          />
        </div>

        <div>
           <label className="text-gray-400 block mb-1">JUMP SIGMA</label>
           <input
             type="number" step="0.01"
             name="jumpSd" value={config.jumpSd} onChange={handleChange}
             className="w-full bg-black border border-red-900/50 rounded px-2 py-1 text-white"
           />
        </div>
      </div>

      <button
        onClick={onRun}
        className="w-full py-3 bg-cyan-900/50 hover:bg-cyan-800 border border-cyan-500/50 text-cyan-100 font-bold uppercase tracking-widest transition-all mb-8"
      >
        Run Simulation
      </button>

      {/* Stats */}
      <div className="space-y-2 text-gray-400">
        <div className="flex justify-between">
            <span>Mean Price:</span>
            <span className="text-white">${result.stats.meanFinalPrice.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
            <span>Max Shock:</span>
            <span className="text-red-400">${result.stats.maxPrice.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
            <span>Events (Jumps):</span>
            <span className="text-white">{result.jumps.length}</span>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
