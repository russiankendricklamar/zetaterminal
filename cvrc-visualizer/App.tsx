import React, { useEffect, useState, useRef } from 'react';
import { generateSyntheticData, generateNextDataPoint, calculateCVRC } from './utils/mathUtils';
import { CVRCData, DataPoint } from './types';
import ThreeDView from './components/ThreeDView';
import PriceChart from './components/PriceChart';
import { Play, Pause, RefreshCw, Info, Activity, Gauge } from 'lucide-react';

const WINDOW_SIZE = 150; // Keep 150 points in view for performance

const SPEED_OPTIONS = [
  { label: '0.5x', delay: 200 },
  { label: '1x', delay: 100 },
  { label: '2x', delay: 50 },
  { label: '5x', delay: 20 },
];

const App: React.FC = () => {
  const [data, setData] = useState<CVRCData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isLive, setIsLive] = useState<boolean>(true);
  const [speedIndex, setSpeedIndex] = useState<number>(1); // Default to 1x (index 1)
  
  // Refs to hold mutable state for the interval loop to avoid closure staleness
  const dataRef = useRef<DataPoint[]>([]);
  const indexRef = useRef<number>(0);

  const initializeData = () => {
    setLoading(true);
    setIsLive(false);
    setTimeout(() => {
      const initialData = generateSyntheticData(WINDOW_SIZE);
      setData(initialData);
      dataRef.current = initialData.priceData;
      indexRef.current = initialData.priceData.length;
      setLoading(false);
      setIsLive(true); // Auto-start
    }, 600);
  };

  useEffect(() => {
    initializeData();
  }, []);

  useEffect(() => {
    let intervalId: number;

    if (isLive && !loading) {
      intervalId = window.setInterval(() => {
        const currentData = dataRef.current;
        const lastPoint = currentData[currentData.length - 1];
        const nextIndex = indexRef.current;

        // Generate next point
        const nextPoint = generateNextDataPoint(lastPoint, nextIndex);
        
        // Update buffer: Remove first, add new (Sliding Window)
        const newDataBuffer = [...currentData.slice(1), nextPoint];
        
        // Update refs
        dataRef.current = newDataBuffer;
        indexRef.current = nextIndex + 1;

        // Calculate visualizer data
        // Note: For extreme performance optimization we could only calculate the new row,
        // but for <200 points, full recalculation is fast enough and simpler.
        const cvrcResult = calculateCVRC(newDataBuffer);
        
        setData(cvrcResult);
      }, SPEED_OPTIONS[speedIndex].delay);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isLive, loading, speedIndex]);

  const toggleLive = () => setIsLive(!isLive);
  
  const cycleSpeed = () => {
    setSpeedIndex((prev) => (prev + 1) % SPEED_OPTIONS.length);
  };

  return (
    <div className="w-full h-screen bg-slate-950 text-slate-200 overflow-hidden flex flex-col font-sans">
      {/* Header */}
      <header className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-10">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600/20 p-2 rounded-lg border border-blue-500/30">
            <Activity className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">Quant Research Decoded</h1>
            <p className="text-xs text-slate-400">CVRC Model Visualization v1.0</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button 
            onClick={toggleLive}
            disabled={loading}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              isLive 
                ? 'bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20' 
                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20'
            }`}
          >
            {isLive ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span>{isLive ? 'Pause' : 'Resume'}</span>
          </button>
          
          <button 
            onClick={cycleSpeed}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 transition-colors text-sm font-medium border border-slate-700 min-w-[80px] justify-center"
            title="Cycle Simulation Speed"
          >
            <Gauge className="w-4 h-4" />
            <span>{SPEED_OPTIONS[speedIndex].label}</span>
          </button>

          <button 
            onClick={initializeData}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 transition-colors"
            title="Reset Simulation"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </header>

      {/* Main Content Grid */}
      <main className="flex-1 p-4 grid grid-rows-[3fr_1fr] gap-4 min-h-0">
        
        {/* Top: 3D Visualization */}
        <section className="relative min-h-0 w-full">
          {loading || !data ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900 rounded-xl border border-slate-800">
               <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4"></div>
               <p className="text-slate-400 animate-pulse">Running Convolutional Kernels...</p>
            </div>
          ) : (
            <ThreeDView data={data} />
          )}
        </section>

        {/* Bottom: Price Chart */}
        <section className="relative min-h-0 w-full">
          {loading || !data ? (
             <div className="w-full h-full bg-slate-900 rounded-xl border border-slate-800 animate-pulse"></div>
          ) : (
            <PriceChart data={data} />
          )}
        </section>

      </main>

      {/* Footer / Status Bar */}
      <footer className="h-8 bg-slate-950 border-t border-slate-800 flex items-center justify-between px-4 text-[10px] text-slate-500 uppercase tracking-widest shrink-0">
        <div className="flex gap-4">
          <span className="flex items-center gap-1">
             <div className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-500 animate-pulse' : 'bg-slate-600'}`}></div>
             System: {isLive ? 'Live Streaming' : 'Paused'}
          </span>
          <span>Buffer: {WINDOW_SIZE} periods</span>
          <span>Speed: {SPEED_OPTIONS[speedIndex].label}</span>
          <span>GPU: Active</span>
        </div>
        <div className="flex items-center gap-2">
             <Info className="w-3 h-3" />
             <span>Axis Z: Volatility Intensity (σ)</span>
        </div>
      </footer>
    </div>
  );
};

export default App;