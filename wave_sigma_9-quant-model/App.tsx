import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { Surface3D } from './components/Surface3D';
import { Charts } from './components/Charts';
import { MarketRegime, SimulationData } from './types';

function App() {
  // State
  const [regime, setRegime] = useState<MarketRegime>(MarketRegime.TRENDING);
  const [simData, setSimData] = useState<SimulationData[]>([]);
  const [equity, setEquity] = useState(1000);
  const [elapsedDays, setElapsedDays] = useState(0);
  
  // Refs for performance
  const dataRef = useRef<SimulationData[]>([]);
  const lastUpdateRef = useRef(0);
  const startTimeRef = useRef(Date.now());

  // Auto-switch regimes to mimic the video narrative
  useEffect(() => {
    const interval = setInterval(() => {
      setRegime(prev => prev === MarketRegime.TRENDING ? MarketRegime.CHOPPY : MarketRegime.TRENDING);
    }, 8000); // Switch every 8 seconds
    return () => clearInterval(interval);
  }, []);

  // Update elapsed simulation time (1 real second = 7 market days)
  useEffect(() => {
    const timer = setInterval(() => {
      const realElapsedSeconds = (Date.now() - startTimeRef.current) / 1000;
      setElapsedDays(Math.floor(realElapsedSeconds * 7));
    }, 100);
    return () => clearInterval(timer);
  }, []);

  // Initialize initial data
  useEffect(() => {
    const initialData: SimulationData[] = Array(60).fill(0).map((_, i) => ({
      position: 0,
      equity: 1000,
      price: 100,
      timestamp: i
    }));
    dataRef.current = initialData;
    setSimData(initialData);
  }, []);

  // Callback from 3D engine
  const handleUpdateStats = useCallback((rawSignal: number, volatility: number) => {
    const now = performance.now();
    if (now - lastUpdateRef.current < 50) return; 
    lastUpdateRef.current = now;

    let position = 0;
    if (regime === MarketRegime.TRENDING) {
       position = rawSignal > 0.2 ? 1 : (rawSignal < -0.2 ? -1 : 0);
    } else {
       position = rawSignal > 0.5 ? 0.5 : (rawSignal < -0.5 ? -0.5 : (Math.random() - 0.5));
    }

    const pnl = (Math.abs(position) * (regime === MarketRegime.TRENDING ? 1.5 : -2.0)) + (Math.random() * 2 - 1);
    
    setEquity(prev => {
      const newEquity = prev + pnl;
      
      const newDataPoint: SimulationData = {
        position: position,
        equity: newEquity,
        price: 0,
        timestamp: now
      };
      
      const currentHistory = dataRef.current;
      const newHistory = [...currentHistory.slice(1), newDataPoint];
      dataRef.current = newHistory;
      setSimData(newHistory);
      
      return newEquity;
    });

  }, [regime]);

  const years = Math.floor(elapsedDays / 365);
  const days = elapsedDays % 365;

  return (
    <div className="w-full h-screen bg-black relative flex flex-col md:flex-row overflow-hidden">
      
      {/* --- Left / Top: 3D Visualization Area --- */}
      <div className="relative w-full md:w-2/3 h-2/3 md:h-full order-2 md:order-1 border-r border-white/10">
        
        {/* Header Overlay */}
        <div className="absolute top-0 left-0 p-6 z-10 pointer-events-none w-full">
          <h1 className="text-2xl md:text-4xl font-bold tracking-tighter text-white mb-1">
            WAVE<span className="text-gray-500">_σ.9</span>
          </h1>
          <p className="text-xs md:text-sm text-gray-400 font-mono max-w-md border-l-2 border-orange-500 pl-3">
             Current Regime: <span className={regime === MarketRegime.TRENDING ? "text-green-400 font-bold" : "text-red-400 font-bold"}>{regime}</span>
          </p>
        </div>

        {/* 3D Canvas */}
        <Canvas>
          <PerspectiveCamera makeDefault position={[0, 25, 40]} fov={45} />
          <color attach="background" args={['#050505']} />
          
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          
          <Surface3D regime={regime} onUpdateStats={handleUpdateStats} />
          
          <OrbitControls 
            enablePan={false} 
            enableZoom={true} 
            maxPolarAngle={Math.PI / 2} 
            minPolarAngle={0}
            autoRotate={true}
            autoRotateSpeed={0.5}
          />
        </Canvas>
      </div>

      {/* --- Right / Bottom: Data Panels --- */}
      <div className="w-full md:w-1/3 h-1/3 md:h-full order-1 md:order-2 bg-gradient-to-b from-[#0a0a0a] to-black relative flex flex-col z-20 shadow-2xl">
         <div className="absolute inset-0 opacity-5 pointer-events-none" 
              style={{backgroundImage: 'linear-gradient(#333 1px, transparent 1px), linear-gradient(90deg, #333 1px, transparent 1px)', backgroundSize: '20px 20px'}}>
         </div>

         <div className="p-4 border-b border-white/10 bg-black/50 backdrop-blur-sm z-30 flex justify-between items-center">
            <div>
              <div className="text-[10px] text-gray-500 font-mono uppercase tracking-widest mb-1">Model Output</div>
              <div className="flex items-baseline gap-2">
                 <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                 <span className="text-sm font-bold text-white">LIVE_FEED</span>
              </div>
            </div>
            <div className="text-right">
               <div className="text-[10px] text-gray-500 font-mono uppercase tracking-widest mb-1">Backtest Period</div>
               <div className="font-mono text-xl text-cyan-400">
                 {years > 0 ? `${years}Y ` : ''}{days}D
               </div>
            </div>
         </div>

         <div className="flex-1 overflow-hidden relative">
            <Charts data={simData} />
         </div>

         {/* Control Panel (Visual Only) */}
         <div className="p-4 border-t border-white/10 bg-[#080808] z-30">
            <div className="flex justify-between items-center mb-4">
               <div className="text-[10px] text-gray-500 font-mono uppercase tracking-widest">Total Equity</div>
               <div className={`font-mono text-xl ${equity > 1000 ? 'text-green-400' : 'text-red-400'}`}>
                 ${equity.toFixed(2)}
               </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-gray-500">
               <div className="flex justify-between border border-white/5 p-2 rounded">
                 <span>ALPHA_DECAY</span>
                 <span className="text-white">0.042</span>
               </div>
               <div className="flex justify-between border border-white/5 p-2 rounded">
                 <span>SHARPE</span>
                 <span className="text-white">2.1</span>
               </div>
               <div className="flex justify-between border border-white/5 p-2 rounded">
                 <span>VOL_TARGET</span>
                 <span className="text-white">15%</span>
               </div>
               <div className="flex justify-between border border-white/5 p-2 rounded">
                 <span>LEVERAGE</span>
                 <span className="text-white">1.8x</span>
               </div>
            </div>
         </div>
      </div>

    </div>
  );
}

export default App;