import React, { useRef, useMemo, useEffect, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { noise, getHeatmapColor } from '../services/mathUtils';
import { MarketRegime } from '../types';

interface Surface3DProps {
  regime: MarketRegime;
  onUpdateStats: (position: number, volatility: number) => void;
}

// Grid Settings
const WIDTH = 50;
const HEIGHT = 50;
const SEGMENTS_W = 60;
const SEGMENTS_H = 60;

export const Surface3D: React.FC<Surface3DProps> = ({ regime, onUpdateStats }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const timeRef = useRef(0);
  const geometryRef = useRef<THREE.PlaneGeometry>(null);
  
  // Track if geometry is fully ready with attributes
  const [isReady, setIsReady] = useState(false);

  // Initialize colors attribute
  const colors = useMemo(() => new Float32Array((SEGMENTS_W + 1) * (SEGMENTS_H + 1) * 3), []);

  // Add the color attribute and mark as ready
  useEffect(() => {
    if (geometryRef.current) {
      const geo = geometryRef.current;
      geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
      setIsReady(true);
    }
  }, [colors]);

  useFrame((state, delta) => {
    if (!geometryRef.current || !isReady) return;

    const geo = geometryRef.current;
    
    // Use getAttribute for safer access
    const posAttr = geo.getAttribute('position') as THREE.BufferAttribute;
    const colAttr = geo.getAttribute('color') as THREE.BufferAttribute;

    // Double check attributes exist before proceeding
    if (!posAttr || !colAttr) return;

    // Slow down time for the simulation
    const dt = delta * 1.5;
    timeRef.current += dt;
    const t = timeRef.current;

    const positions = posAttr.array as Float32Array;
    const colorAttrib = colAttr.array as Float32Array;
    const count = posAttr.count;
    const tempColor = { r: 0, g: 0, b: 0 };

    let centerSignal = 0;
    let totalVolatility = 0;

    for (let i = 0; i < count; i++) {
      const x = positions[i * 3];
      const y = positions[i * 3 + 1];

      // Calculate effective coordinate in the "infinite" stream
      const streamY = y - t * 4;
      
      // Base rolling wave
      let z = Math.sin(x * 0.2 + streamY * 0.2) * 2;

      // Regime specific logic
      const ridge = Math.exp(-Math.pow(x * 0.15, 2)) * 12;
      const chop = (noise(x * 0.8 + streamY) + noise(x * 1.5 - streamY * 1.5) * 0.5) * 3;

      if (regime === MarketRegime.TRENDING) {
         z += ridge * 1.5;
         z += chop * 0.2;
      } else {
         z += ridge * 0.2;
         z += chop * 2.5;
      }
      
      z += Math.sin(Math.sqrt(x*x + y*y) - t * 5) * 0.5;

      // Update Position Z
      positions[i * 3 + 2] = z;

      // Update Color based on Z height
      const normHeight = (z + 5) / 20;
      getHeatmapColor(normHeight, tempColor);
      
      colorAttrib[i * 3] = tempColor.r;
      colorAttrib[i * 3 + 1] = tempColor.g;
      colorAttrib[i * 3 + 2] = tempColor.b;

      // Sample leading edge (approx center of the grid's far edge)
      if (Math.abs(y - (HEIGHT / 2)) < 1 && Math.abs(x) < 1) {
          centerSignal = z;
      }
      if (Math.abs(y - (HEIGHT / 2)) < 1) {
          totalVolatility += Math.abs(z);
      }
    }

    // Safely trigger updates
    posAttr.needsUpdate = true;
    colAttr.needsUpdate = true;

    const normalizedPosition = Math.max(-1, Math.min(1, (centerSignal - 5) / 10)); 
    onUpdateStats(normalizedPosition, totalVolatility);
  });

  const rotation: [number, number, number] = [-Math.PI / 2.5, 0, 0];
  const position: [number, number, number] = [0, -5, 0];

  return (
    <>
      {/* Main Surface */}
      <mesh ref={meshRef} rotation={rotation} position={position}>
        <planeGeometry ref={geometryRef} args={[WIDTH, HEIGHT, SEGMENTS_W, SEGMENTS_H]} />
        <meshBasicMaterial 
          vertexColors 
          side={THREE.DoubleSide}
          transparent={true}
          opacity={0.8}
        />
      </mesh>

      {/* Wireframe Overlay - sharing the same geometry instance */}
      {geometryRef.current && (
        <mesh rotation={rotation} position={position}>
          <primitive object={geometryRef.current} attach="geometry" />
          <meshBasicMaterial 
            wireframe 
            color="#ffffff" 
            transparent 
            opacity={0.15} 
            depthWrite={false}
          />
        </mesh>
      )}
    </>
  );
};