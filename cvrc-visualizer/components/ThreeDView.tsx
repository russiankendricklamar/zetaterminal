import React, { useMemo, useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { CVRCData } from '../types';

interface ThreeDViewProps {
  data: CVRCData;
}

const ThreeDView: React.FC<ThreeDViewProps> = ({ data }) => {
  // Initialize layout state once with default camera position.
  // We keep layout in state so we don't re-inject the camera config on every frame,
  // which causes the view to snap back.
  const [layout, setLayout] = useState<any>({
    autosize: true,
    uirevision: 'true', // Magic string to preserve user interaction state
    datarevision: 0,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: {
      l: 0,
      r: 0,
      b: 0,
      t: 0,
    },
    scene: {
      xaxis: {
        title: { text: 'Period (Freq)', font: { color: '#cbd5e1' } },
        tickfont: { color: '#94a3b8' },
        gridcolor: '#334155',
        zerolinecolor: '#475569',
        showbackground: false,
      },
      yaxis: {
        title: { text: 'Time', font: { color: '#cbd5e1' } },
        tickfont: { color: '#94a3b8' },
        gridcolor: '#334155',
        zerolinecolor: '#475569',
        showbackground: false,
      },
      zaxis: {
        title: { text: 'Intensity', font: { color: '#cbd5e1' } },
        tickfont: { color: '#94a3b8' },
        gridcolor: '#334155',
        zerolinecolor: '#475569',
        showbackground: false,
      },
      // Camera is defined only in the initial state.
      // Plotly will manage it internally afterwards.
      camera: {
        eye: { x: 1.5, y: 1.5, z: 1.2 },
        center: { x: 0, y: 0, z: -0.2 }
      },
      aspectratio: { x: 1, y: 2, z: 0.7 } // Elongate time axis
    },
    showlegend: false,
  });

  // When data changes, we ONLY update the datarevision.
  // We strictly avoid touching the 'scene' or 'camera' properties here.
  useEffect(() => {
    setLayout((prev: any) => ({
      ...prev,
      datarevision: prev.datarevision + 1
    }));
  }, [data]);
  
  const plotData = useMemo(() => {
    // 1. The Surface
    const surface: any = {
      type: 'surface',
      z: data.surfaceZ,
      x: data.periods, // X labels
      y: data.timeIndices, // Y labels
      colorscale: [
        [0, 'rgb(15, 23, 42)'],      // Deep Blue/Black (slate-900) - Valleys
        [0.2, 'rgb(56, 189, 248)'],  // Cyan (sky-400)
        [0.4, 'rgb(34, 197, 94)'],   // Green (green-500)
        [0.6, 'rgb(234, 179, 8)'],   // Yellow (yellow-500)
        [0.8, 'rgb(249, 115, 22)'],  // Orange (orange-500)
        [1, 'rgb(239, 68, 68)']      // Red (red-500) - Peaks
      ],
      showscale: true,
      colorbar: {
        title: 'Volatility Intensity',
        thickness: 20,
        len: 0.7,
        titlefont: { color: '#cbd5e1' },
        tickfont: { color: '#94a3b8' },
        x: 0.9, 
      },
      contours: {
        z: {
          show: true,
          usecolormap: true,
          highlightcolor: "limegreen",
          project: { z: true }
        }
      },
      opacity: 0.9,
    };

    // 2. The Peak Marker (Scatter3D)
    let markers: any = { type: 'scatter3d', x: [], y: [], z: [] };
    
    if (data.peak) {
      markers = {
        type: 'scatter3d',
        mode: 'markers',
        x: [data.peak.x],
        y: [data.peak.y],
        z: [data.peak.z * 1.05], // Slightly above surface
        marker: {
          size: 10,
          symbol: 'diamond',
          color: '#ffffff', // White core
          line: {
            color: '#ef4444', // Red border
            width: 5
          }
        },
        name: 'Max Volatility Cluster'
      };
    }

    return [surface, markers];
  }, [data]);

  return (
    <div className="w-full h-full relative rounded-xl overflow-hidden bg-slate-900 shadow-2xl border border-slate-800">
      <Plot
        data={plotData as any}
        layout={layout}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
        config={{ displayModeBar: true, displaylogo: false }}
      />
      
      {/* Overlay Title */}
      <div className="absolute top-4 left-6 pointer-events-none">
        <h2 className="text-xl font-bold text-white tracking-wider">CVRC MODEL <span className="text-cyan-400 font-mono text-sm ml-2">HARMONIC_Ψ.1</span></h2>
        <p className="text-slate-400 text-xs mt-1">Convolutional Volatility Resolution Clustering</p>
      </div>
      
      {/* Legend for Peak */}
      <div className="absolute top-4 right-16 pointer-events-none bg-slate-900/80 backdrop-blur border border-slate-700 p-2 rounded flex items-center gap-2">
         <div className="w-3 h-3 bg-red-500 rotate-45 border border-white"></div>
         <span className="text-xs text-slate-200">Peak Volatility Cluster</span>
      </div>
    </div>
  );
};

export default ThreeDView;