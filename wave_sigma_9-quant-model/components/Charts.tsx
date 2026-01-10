import React from 'react';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip, ReferenceLine } from 'recharts';
import { SimulationData } from '../types';

interface ChartsProps {
  data: SimulationData[];
}

export const Charts: React.FC<ChartsProps> = ({ data }) => {
  // We only show the last N points to keep the chart moving
  // Assume each point is approx 50ms, so 60 points = 3 seconds
  const visibleData = data.slice(-60).map((d, i) => ({
    ...d,
    timeLabel: `-${((60 - i) * 0.05).toFixed(1)}s`
  }));

  return (
    <div className="flex flex-col gap-4 w-full h-full p-4 pointer-events-none">
      
      {/* Position Output Chart */}
      <div className="bg-black/40 backdrop-blur-md border border-white/10 p-4 rounded-lg flex-1 min-h-[140px]">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-xs font-mono font-bold text-orange-400 uppercase tracking-widest">Position Output</h3>
          <span className="text-[10px] text-gray-500 font-mono">Signal -1.0 : 1.0</span>
        </div>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={visibleData}>
            <XAxis 
              dataKey="timeLabel" 
              hide={false} 
              axisLine={false} 
              tickLine={false} 
              tick={{fill: '#444', fontSize: 8}}
              interval={14}
            />
            <YAxis domain={[-1.2, 1.2]} hide />
            <ReferenceLine y={0} stroke="#222" />
            <Line 
              type="stepAfter" 
              dataKey="position" 
              stroke="#ff9f43" 
              strokeWidth={1.5} 
              dot={false} 
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Equity Curve Chart */}
      <div className="bg-black/40 backdrop-blur-md border border-white/10 p-4 rounded-lg flex-1 min-h-[140px]">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-widest">Equity Curve</h3>
          <span className="text-[10px] text-gray-500 font-mono">Rolling Window</span>
        </div>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={visibleData}>
            <XAxis 
              dataKey="timeLabel" 
              hide={false} 
              axisLine={false} 
              tickLine={false} 
              tick={{fill: '#444', fontSize: 8}}
              interval={14}
            />
            <YAxis domain={['auto', 'auto']} hide />
            <Line 
              type="monotone" 
              dataKey="equity" 
              stroke="#00d2d3" 
              strokeWidth={2} 
              dot={false}
              isAnimationActive={false} 
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};