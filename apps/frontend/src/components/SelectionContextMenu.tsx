import React from 'react';
import { Region, Path } from '@wildeditor/shared/types';
import { MapPin, Square, Minus, Eye } from 'lucide-react';

interface SelectionCandidate {
  item: Region | Path;
  type: 'region' | 'path';
  distance?: number; // For paths, distance to click point
}

interface SelectionContextMenuProps {
  candidates: SelectionCandidate[];
  position: { x: number; y: number };
  onSelect: (item: Region | Path) => void;
  onClose: () => void;
  onToggleVisibility: (type: 'region' | 'path', vnum: number) => void;
}

export const SelectionContextMenu: React.FC<SelectionContextMenuProps> = ({
  candidates,
  position,
  onSelect,
  onClose,
  onToggleVisibility
}) => {
  if (candidates.length === 0) return null;

  const getItemIcon = (type: 'region' | 'path') => {
    switch (type) {
      case 'region': return Square;
      case 'path': return Minus;
      default: return MapPin;
    }
  };

  const getItemTypeName = (item: Region | Path) => {
    if ('region_type' in item) {
      const typeNames = ['Geographic', 'Encounter', 'Transform', 'Sector Override'];
      return typeNames[item.region_type - 1] || 'Unknown';
    } else {
      const typeNames = ['Paved Road', 'Dirt Road', 'Geographic', '', 'River', 'Stream'];
      return typeNames[item.path_type - 1] || 'Unknown';
    }
  };

  // Sort candidates by distance (for paths) or area (for regions)
  // All candidates should be visible items only now
  const sortedCandidates = [...candidates].sort((a, b) => {
    // For paths, sort by distance (closer first)
    if (a.type === 'path' && b.type === 'path' && a.distance !== undefined && b.distance !== undefined) {
      return a.distance - b.distance;
    }
    
    // For regions, prefer smaller regions (less area)
    if (a.type === 'region' && b.type === 'region') {
      const aArea = calculatePolygonArea((a.item as Region).coordinates);
      const bArea = calculatePolygonArea((b.item as Region).coordinates);
      return aArea - bArea;
    }
    
    // Mixed types: prefer paths over regions (paths are usually more specific)
    if (a.type !== b.type) {
      return a.type === 'path' ? -1 : 1;
    }
    
    return 0;
  });

  return (
    <div 
      className="fixed bg-gray-800 border border-gray-600 rounded-lg shadow-lg z-50 min-w-48"
      style={{ left: position.x, top: position.y }}
      onClick={(e) => e.stopPropagation()} // Prevent event propagation
    >
      <div className="p-2 border-b border-gray-600">
        <div className="text-xs text-gray-400 font-medium">
          Select from {candidates.length} overlapping item{candidates.length > 1 ? 's' : ''}
        </div>
        <div className="text-xs text-gray-500 mt-0.5">
          All items are visible • Click to select
        </div>
      </div>
      
      <div className="py-1 max-h-64 overflow-y-auto">
        {sortedCandidates.map((candidate, index) => {
          const Icon = getItemIcon(candidate.type);
          const item = candidate.item;
          
          return (
            <div
              key={`${candidate.type}-${item.vnum}-${index}`}
              className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-700 cursor-pointer text-gray-200"
              onClick={() => {
                onSelect(item);
                onClose();
              }}
            >
              <Icon size={14} className="flex-shrink-0" />
              
              <div className="flex-1 min-w-0">
                <div className="truncate font-medium">
                  {item.name}
                </div>
                <div className="text-xs text-gray-400">
                  {getItemTypeName(item)} • VNUM {item.vnum}
                </div>
                {candidate.distance !== undefined && (
                  <div className="text-xs text-gray-500">
                    Distance: {candidate.distance.toFixed(1)}
                  </div>
                )}
              </div>
              
              <button
                className="p-1 hover:bg-gray-600 rounded opacity-70 hover:opacity-100 flex-shrink-0"
                onClick={(e) => {
                  e.stopPropagation();
                  onToggleVisibility(candidate.type, item.vnum);
                }}
                title="Hide item"
              >
                <Eye size={12} />
              </button>
            </div>
          );
        })}
      </div>
      
      <div className="p-2 border-t border-gray-600">
        <button
          className="w-full text-xs text-gray-400 hover:text-gray-300 py-1"
          onClick={onClose}
        >
          Cancel
        </button>
      </div>
    </div>
  );
};

// Helper function to calculate polygon area (for sorting by size)
function calculatePolygonArea(coordinates: { x: number; y: number }[]): number {
  if (coordinates.length < 3) return 0;
  
  let area = 0;
  for (let i = 0; i < coordinates.length; i++) {
    const j = (i + 1) % coordinates.length;
    area += coordinates[i].x * coordinates[j].y;
    area -= coordinates[j].x * coordinates[i].y;
  }
  return Math.abs(area) / 2;
}
