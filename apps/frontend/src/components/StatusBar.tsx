import React from 'react';
import { Save, RotateCcw } from 'lucide-react';
import { Coordinate } from '../types';

interface StatusBarProps {
  mousePosition: Coordinate;
  zoom: number;
  onZoomChange: (zoom: number) => void;
  regionCount?: number;
  pathCount?: number;
  loading?: boolean;
  error?: string | null;
  // New unsaved items props
  unsavedCount?: number;
  onSaveAll?: () => void;
  onDiscardAll?: () => void;
  isSaving?: boolean;
}

export const StatusBar: React.FC<StatusBarProps> = ({ 
  mousePosition, 
  zoom, 
  onZoomChange, 
  regionCount = 0, 
  pathCount = 0,
  loading = false,
  error = null,
  unsavedCount = 0,
  onSaveAll,
  onDiscardAll,
  isSaving = false
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
        {/* Unsaved items indicator and Save All button */}
        {unsavedCount > 0 && (
          <>
            <span className="text-orange-400 text-xs">
              {unsavedCount} unsaved*
            </span>
            <button
              onClick={onSaveAll}
              disabled={isSaving}
              className={`px-2 py-1 rounded text-xs flex items-center gap-1 transition-colors ${
                isSaving
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
              title="Save all unsaved changes"
            >
              <Save size={12} />
              {isSaving ? 'Saving...' : 'Save All'}
            </button>
            <button
              onClick={() => {
                if (onDiscardAll && confirm(`Are you sure you want to discard all ${unsavedCount} unsaved changes?`)) {
                  onDiscardAll();
                }
              }}
              disabled={isSaving}
              className={`px-2 py-1 rounded text-xs flex items-center gap-1 transition-colors ${
                isSaving
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-red-600 hover:bg-red-700 text-white'
              }`}
              title="Discard all unsaved changes"
            >
              <RotateCcw size={12} />
              Discard All
            </button>
            <div className="w-px h-4 bg-gray-600"></div>
          </>
        )}
        
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