
import React, { useMemo, useState, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Text, Grid } from '@react-three/drei';
import * as THREE from 'three';
import { SimulationResult } from '../types';
import Trajectory from './Trajectory';

interface SimulationCanvasProps {
  result: SimulationResult;
}

// Inner component to handle the animation loop via useFrame
const SceneContent: React.FC<{ result: SimulationResult }> = ({ result }) => {
  const { paths, stats } = result;
  
  // Animation State
  const [currentStep, setCurrentStep] = useState(0);
  const timeRef = useRef(0);
  const totalSteps = paths[0].length;
  
  // Animation Speed Configuration
  const ANIMATION_DURATION_SEC = 5; 
  const PAUSE_DURATION_SEC = 2;

  useFrame((state, delta) => {
    // Accumulate time
    timeRef.current += delta;
    
    // Calculate total cycle time
    const totalCycle = ANIMATION_DURATION_SEC + PAUSE_DURATION_SEC;
    const cycleTime = timeRef.current % totalCycle;

    if (cycleTime < ANIMATION_DURATION_SEC) {
      // Linear interpolation of steps
      const progress = cycleTime / ANIMATION_DURATION_SEC;
      const step = Math.floor(progress * totalSteps);
      
      // Only update state if it changes significantly to reduce overhead
      if (step !== currentStep) {
        setCurrentStep(step);
      }
    } else {
      // Pause phase - hold at max steps
      if (currentStep !== totalSteps) {
        setCurrentStep(totalSteps);
      }
    }
  });

  // Visualization Scaling
  // Dynamically calculate scaleY to fit the data range into a reasonable 3D height
  // Increased scaleX to lengthen the time axis
  const scaleX = 3.0; 
  const scaleZ = 4.0; 
  
  const targetVisualHeight = 150;
  const priceRange = stats.maxPrice - stats.minPrice;
  // Ensure we don't divide by zero and have a minimum logical range
  const safeRange = Math.max(priceRange, stats.meanFinalPrice * 0.05, 1.0);
  const scaleY = targetVisualHeight / safeRange;

  const initialY = paths[0][0].y * scaleY;

  // Aesthetic
  const primaryColor = "#00f0ff"; 
  const boxWidth = totalSteps * scaleX;
  const boxHeight = safeRange * scaleY * 1.2; // Add 20% padding
  const boxDepth = paths.length * scaleZ;
  
  // Center vertical position based on the average of min and max to keep scene centered
  const centerDataY = ((stats.maxPrice + stats.minPrice) / 2) * scaleY;
  
  const dataOffsetX = -boxWidth / 2;
  const dataOffsetZ = -boxDepth / 2;
  
  // OrbitControls target - look at the center of the data box
  const targetY = centerDataY;

  return (
    <>
      <PerspectiveCamera makeDefault position={[800, targetY + 200, 600]} fov={45} near={0.1} far={50000} />
      <OrbitControls 
        enableDamping 
        dampingFactor={0.1} 
        rotateSpeed={0.5} 
        target={[0, targetY, 0]}
      />
      <ambientLight intensity={3} />

      {/* Data Group */}
      <group position={[dataOffsetX, 0, dataOffsetZ]}>
        {paths.map((path, idx) => {
          const finalVal = path[path.length - 1].y;
          const isOutlier = Math.abs(finalVal - paths[0][0].y) > (stats.stdDev * 1.5);
          const color = isOutlier ? "#ffffff" : primaryColor;
          // Increased opacity to remove "dim" look
          const opacity = isOutlier ? 1.0 : 0.6;

          return (
            <Trajectory
              key={idx}
              points={path}
              color={color}
              opacity={opacity}
              scaleX={scaleX}
              scaleY={scaleY}
              scaleZ={scaleZ}
              highlight={isOutlier}
              visibleSteps={currentStep}
            />
          );
        })}
      </group>

      {/* Static Context (Box, Grids) */}
      <group position={[0, targetY, 0]}>
        {/* Floor Grid (Time vs Paths) - XZ Plane */}
        <Grid 
          position={[0, -boxHeight/2, 0]} 
          args={[boxWidth, boxDepth]} 
          cellSize={10} 
          sectionSize={50} 
          sectionColor="#0088aa" 
          cellColor="#003344" 
          fadeDistance={2500}
          infiniteGrid={false}
        />

        {/* Back Wall Grid (Time vs Price) - XY Plane (rotated 90deg on X) */}
        <Grid 
          position={[0, 0, -boxDepth/2]}
          rotation={[Math.PI / 2, 0, 0]} 
          args={[boxWidth, boxHeight]} 
          cellSize={10} 
          sectionSize={50} 
          sectionColor="#0088aa" 
          cellColor="#003344" 
          fadeDistance={2500}
          infiniteGrid={false}
        />

        {/* Side Wall Grid (Price vs Paths) - YZ Plane (rotated 90deg on Z) */}
        <Grid 
          position={[-boxWidth/2, 0, 0]} 
          rotation={[0, 0, Math.PI / 2]}
          args={[boxHeight, boxDepth]} 
          cellSize={10} 
          sectionSize={50} 
          sectionColor="#0088aa" 
          cellColor="#003344" 
          fadeDistance={2500}
          infiniteGrid={false}
        />
      </group>

      {/* Axis Labels */}
      <group position={[-boxWidth/2, targetY - boxHeight/2, boxDepth/2]}>
          <Text position={[boxWidth/2, -10, 0]} fontSize={6} color="#00f0ff">TIME (t)</Text>
          <Text position={[-10, boxHeight/2, 0]} fontSize={6} color="#00f0ff" rotation={[0,0,Math.PI/2]}>
             ASSET PRICE (1M - 5M Scale)
          </Text>
          <Text position={[0, -10, -boxDepth/2]} fontSize={6} color="#00f0ff" rotation={[0,Math.PI/2,0]}>PATHS (N)</Text>
      </group>
    </>
  );
};

const SimulationCanvas: React.FC<SimulationCanvasProps> = ({ result }) => {
  // Removed hardcoded background color and set alpha to true to allow CSS background
  return (
    <div className="w-full h-full">
      <Canvas 
        dpr={[1, 2]} 
        gl={{ antialias: true, alpha: true, toneMapping: THREE.NoToneMapping }}
      >
        {/* Removed <color attach="background" ... /> to let CSS background show */}
        <SceneContent key={result.stats.meanFinalPrice} result={result} />
      </Canvas>
    </div>
  );
};

export default SimulationCanvas;
