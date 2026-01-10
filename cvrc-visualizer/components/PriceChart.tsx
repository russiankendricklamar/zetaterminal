import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceArea
} from 'recharts';
import { CVRCData } from '../types';

interface PriceChartProps {
  data: CVRCData;
}

const PriceChart: React.FC<PriceChartProps> = ({ data }) => {
  // Identify the time index of the peak to highlight it
  const peakIndex = data.peak ? data.peak.yIndex : -1;
  // Create a range around the peak for the "Hot Zone" projection
  const highlightStart = peakIndex > 10 ? data.priceData[peakIndex - 10]?.date : data.priceData[0]?.date;
  const highlightEnd = peakIndex < data.priceData.length - 10 ? data.priceData[peakIndex + 10]?.date : data.priceData[data.priceData.length - 1]?.date;

  return (
    <div className="w-full h-full bg-slate-900 rounded-xl p-4 shadow-xl border border-slate-800 flex flex-col">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-slate-300 font-semibold text-sm uppercase tracking-wide">
          Asset Price Evolution <span className="text-slate-500">| S&P 500 Synthetic</span>
        </h3>
        {data.peak && (
            <div className="text-xs font-mono text-red-400">
                CRITICAL ZONE: {data.peak.y}
            </div>
        )}
      </div>

      <div className="flex-1 w-full min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data.priceData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis 
              dataKey="date" 
              tick={{ fill: '#64748b', fontSize: 10 }} 
              axisLine={{ stroke: '#334155' }}
              minTickGap={30}
            />
            <YAxis 
              domain={['auto', 'auto']} 
              tick={{ fill: '#64748b', fontSize: 10 }} 
              axisLine={{ stroke: '#334155' }}
              width={40}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f1f5f9' }}
              itemStyle={{ color: '#38bdf8' }}
              formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
              labelStyle={{ color: '#94a3b8', marginBottom: '0.5rem' }}
            />
            
            {/* Highlight the Volatility Cluster Zone */}
            {data.peak && (
                <ReferenceArea 
                    x1={highlightStart} 
                    x2={highlightEnd} 
                    fill="#ef4444" 
                    fillOpacity={0.15} 
                    strokeOpacity={0}
                />
            )}

            <Line 
              type="monotone" 
              dataKey="price" 
              stroke="#38bdf8" 
              strokeWidth={2} 
              dot={false}
              isAnimationActive={false} // Disable animation for live updates
              activeDot={{ r: 6, fill: '#38bdf8', stroke: '#fff' }}
            />
            
            {/* Peak Marker Line */}
            {data.peak && (
               <ReferenceArea x1={data.peak.y} x2={data.peak.y} stroke="#ef4444" strokeDasharray="3 3" />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default PriceChart;