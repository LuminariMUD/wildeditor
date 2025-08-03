import React from 'react';
import { Coordinate } from '../types';

interface StatusBarProps {
  mousePosition: Coordinate;
  zoom: number;
  onZoomChange: (zoom: number) => void;
  regionCount?: number;
  pathCount?: number;
  loading?: boolean;
  error?: string | null;
}

export const StatusBar: React.FC<StatusBarProps> = ({ 
  mousePosition, 
  zoom, 
  onZoomChange, 
  regionCount = 0, 
  pathCount = 0,
  loading = false,
  error = null
}) => {
  const zoomLevels = [25, 50, 75, 100, 150, 200, 300, 500, 800, 1200, 1600, 2000];

  const getStatusColor = () => {
    if (error) return 'text-red-400';
    if (loading) return 'text-yellow-400';
    if (regionCount > 0 || pathCount > 0) return 'text-green-400';
    return 'text-gray-400';
  };

  const getStatusText = () => {
    if (error) return 'API Error';
    if (loading) return 'Loading...';
    if (regionCount > 0 || pathCount > 0) return 'Connected';
    return 'No Data';
  };

  return (
    <div className="bg-gray-800 border-t border-gray-700 px-4 py-2 flex items-center justify-between text-sm">
      <div className="flex items-center gap-4">
        <span className="text-gray-300">
          Mouse: ({mousePosition.x}, {mousePosition.y})
        </span>
        <div className="w-px h-4 bg-gray-600"></div>
        <span className="text-gray-300">
          API: <span className={getStatusColor()}>{getStatusText()}</span>
        </span>
        <div className="w-px h-4 bg-gray-600"></div>
        <span className="text-gray-300">
          Data: <span className="text-blue-400">{regionCount}R</span>, <span className="text-green-400">{pathCount}P</span>
        </span>
        {error && (
          <>
            <div className="w-px h-4 bg-gray-600"></div>
            <span className="text-red-400 text-xs" title={error}>
              {error.length > 30 ? `${error.substring(0, 30)}...` : error}
            </span>
          </>
        )}
      </div>
      
      <div className="flex items-center gap-2">
        <span className="text-gray-300">Zoom:</span>
        <select
          value={zoom}
          onChange={(e) => onZoomChange(parseInt(e.target.value))}
          className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white text-sm focus:ring-1 focus:ring-blue-500"
        >
          {zoomLevels.map(level => (
            <option key={level} value={level}>{level}%</option>
          ))}
        </select>
      </div>
    </div>
  );
};