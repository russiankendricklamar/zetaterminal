
import React, { useMemo } from 'react';
import { Line } from '@react-three/drei';
import { PathPoint } from '../types';

interface TrajectoryProps {
  points: PathPoint[];
  color: string;
  opacity: number;
  scaleX: number;
  scaleY: number;
  scaleZ: number;
  highlight?: boolean;
  visibleSteps: number; // Controls animation progress
}

const Trajectory: React.FC<TrajectoryProps> = ({ 
  points, 
  color, 
  opacity, 
  scaleX, 
  scaleY, 
  scaleZ, 
  highlight, 
  visibleSteps 
}) => {
  
  // Calculate the flat array for the line geometry
  // We only include points up to the current visibleSteps
  const flatPoints = useMemo(() => {
    // Ensure we have at least 2 points to form a line, otherwise ThreeJS warns
    const limit = Math.max(2, Math.min(points.length, visibleSteps));
    const activePoints = points.slice(0, limit);
    
    const coords: number[] = [];
    for (let i = 0; i < activePoints.length; i++) {
      coords.push(
        activePoints[i].x * scaleX,
        activePoints[i].y * scaleY,
        activePoints[i].z * scaleZ
      );
    }
    return coords;
  }, [points, scaleX, scaleY, scaleZ, visibleSteps]);

  // If we haven't started (step 0 or 1), don't render anything to avoid artifacts
  if (visibleSteps < 2) return null;

  return (
    <Line
      points={flatPoints}
      color={color}
      lineWidth={highlight ? 2.5 : 1.5}
      transparent
      opacity={opacity}
      depthWrite={false}
      depthTest={true}
      toneMapped={false}
    />
  );
};

export default Trajectory;
