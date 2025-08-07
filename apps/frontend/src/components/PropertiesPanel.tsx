import React, { useCallback } from 'react';
import { Save, RotateCcw, Trash2, Plus } from 'lucide-react';
import { Region, Path } from '../types';

interface PropertiesPanelProps {
  selectedItem: Region | Path | null;
  onUpdate: (updates: Partial<Region | Path>) => void;
  onFinishDrawing?: () => void;
  isDrawing: boolean;
  // New save props
  onSave?: (itemId: string) => void;
  onDiscard?: (itemId: string) => void;
  onDelete?: (itemId: string) => void;
  isSaving?: boolean;
  hasUnsavedChanges?: boolean;
}

export const PropertiesPanel: React.FC<PropertiesPanelProps> = ({
  selectedItem,
  onUpdate,
  onFinishDrawing,
  isDrawing,
  onSave,
  onDiscard,
  onDelete,
  isSaving = false,
  hasUnsavedChanges = false
}) => {
  const COORDINATE_BOUNDS = { min: -1024, max: 1024 };
  
  // Validation and sanitization functions
  const validateCoordinate = useCallback((value: number): number => {
    const num = Math.round(value);
    return Math.max(COORDINATE_BOUNDS.min, Math.min(COORDINATE_BOUNDS.max, num));
  }, [COORDINATE_BOUNDS.min, COORDINATE_BOUNDS.max]);
  
  const validateVnum = useCallback((value: number): number => {
    return Math.max(1, Math.min(99999, Math.round(value)));
  }, []);
  
  const sanitizeText = useCallback((text: string): string => {
    return text.slice(0, 100); // Only limit length, don't trim during typing
  }, []);
  if (isDrawing) {
    return (
      <div className="p-4 bg-gray-900">
        <h3 className="text-lg font-semibold text-white mb-4">Drawing Mode</h3>
        <div className="bg-blue-900 border border-blue-700 rounded-lg p-3 mb-4">
          <h4 className="text-blue-200 font-medium text-sm mb-2">Instructions</h4>
          <ul className="text-blue-100 text-xs space-y-1">
            <li>• Click on the map to add points</li>
            <li>• Press <kbd className="bg-blue-800 px-1 rounded text-xs">Enter</kbd> to finish drawing</li>
            <li>• Press <kbd className="bg-blue-800 px-1 rounded text-xs">Escape</kbd> to cancel</li>
            <li>• Minimum points: Polygon (3), Path (2)</li>
          </ul>
        </div>
        
        <div className="space-y-2">
          <button
            onClick={onFinishDrawing}
            className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors"
          >
            <Save size={16} />
            Finish Drawing
          </button>
          
          <button
            onClick={() => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))}
            className="w-full bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors"
          >
            <RotateCcw size={16} />
            Cancel Drawing
          </button>
        </div>
      </div>
    );
  }

  if (!selectedItem) {
    return (
      <div className="p-4 bg-gray-900">
        <h3 className="text-lg font-semibold text-white mb-4">Properties</h3>
        <p className="text-gray-400">Select an item to edit its properties</p>
      </div>
    );
  }

  const isRegion = 'vnum' in selectedItem && 'coordinates' in selectedItem && selectedItem.coordinates.length >= 3;
  const isPath = 'vnum' in selectedItem && 'coordinates' in selectedItem && !isRegion;

  return (
    <div className="p-4 bg-gray-900 space-y-4 max-h-full overflow-y-auto">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">
          {isRegion ? 'Region' : 'Path'}
        </h3>
        <button 
          onClick={() => {
            if (onDelete && selectedItem) {
              const itemId = ('vnum' in selectedItem && selectedItem.vnum) 
                || ('id' in selectedItem && selectedItem.id) 
                || null;
              if (itemId) {
                const itemType = isRegion ? 'region' : 'path';
                const itemName = selectedItem.name || `${itemType} ${itemId}`;
                if (confirm(`Are you sure you want to delete this ${itemType}?\n\n"${itemName}"\n\nThis action cannot be undone.`)) {
                  onDelete(itemId.toString());
                }
              }
            }
          }}
          className="text-red-400 hover:text-red-300 p-1"
          title="Delete this item"
        >
          <Trash2 size={16} />
        </button>
      </div>

      {/* Common fields */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">Name</label>
        <input
          type="text"
          value={selectedItem.name}
          onChange={(e) => onUpdate({ name: sanitizeText(e.target.value) })}
          onBlur={(e) => onUpdate({ name: e.target.value.trim().slice(0, 100) })}
          className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          maxLength={100}
        />
      </div>

      {/* VNUM for regions and paths */}
      {('vnum' in selectedItem) && (
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">VNUM</label>
          <input
            type="number"
            value={selectedItem.vnum}
            onChange={(e) => onUpdate({ vnum: validateVnum(parseInt(e.target.value) || 1) })}
            className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            min="1"
            max="99999"
          />
        </div>
      )}

      {/* Type selection */}
      {isRegion && (
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Type</label>
          <select
            value={(selectedItem as Region).region_type}
            onChange={(e) => onUpdate({ region_type: parseInt(e.target.value) as Region['region_type'] })}
            className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={1}>Geographic</option>
            <option value={2}>Encounter</option>
            <option value={3}>Sector Transform</option>
            <option value={4}>Sector</option>
          </select>
        </div>
      )}

      {isPath && (
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Type</label>
          <select
            value={(selectedItem as Path).path_type}
            onChange={(e) => onUpdate({ path_type: parseInt(e.target.value) as Path['path_type'] })}
            className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={1}>Paved Road</option>
            <option value={2}>Dirt Road</option>
            <option value={3}>Geographic</option>
            <option value={5}>River</option>
            <option value={6}>Stream</option>
          </select>
        </div>
      )}

      {/* Region Properties - type-specific numeric values */}
      {isRegion && (
        <div>
          {(() => {
            const region = selectedItem as Region;
            const regionType = region.region_type;
            
            if (regionType === 1 || regionType === 2) {
              // Geographic and Encounter - value ignored by game
              return (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Properties {regionType === 1 ? '(Geographic - value ignored)' : '(Encounter - value ignored)'}
                  </label>
                  <input
                    type="number"
                    value={region.region_props || 0}
                    onChange={(e) => onUpdate({ region_props: parseInt(e.target.value) || 0 })}
                    className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Any value (ignored by game)"
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    {regionType === 1 
                      ? "Geographic regions use this for area naming and landmarks. Value is ignored by terrain generation."
                      : "Encounter regions use this for spawning zones. Value is ignored by terrain generation."
                    }
                  </p>
                </div>
              );
            } else if (regionType === 3) {
              // Sector Transform - elevation adjustment
              return (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Elevation Adjustment
                  </label>
                  <input
                    type="number"
                    value={region.region_props || 0}
                    onChange={(e) => onUpdate({ region_props: parseInt(e.target.value) || 0 })}
                    className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., +50 for uplift, -30 for depression"
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Positive values raise elevation, negative values lower it. This affects terrain type calculation.
                  </p>
                </div>
              );
            } else if (regionType === 4) {
              // Sector Override - specific sector type
              return (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Sector Type Override
                  </label>
                  <select
                    value={region.region_props || 0}
                    onChange={(e) => onUpdate({ region_props: parseInt(e.target.value) })}
                    className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value={0}>Inside</option>
                    <option value={1}>City</option>
                    <option value={2}>Field</option>
                    <option value={3}>Forest</option>
                    <option value={4}>Hills</option>
                    <option value={5}>Low Mountains</option>
                    <option value={6}>Water (Swim)</option>
                    <option value={7}>Water (No Swim)</option>
                    <option value={8}>In Flight</option>
                    <option value={9}>Underwater</option>
                    <option value={10}>Zone Entrance</option>
                    <option value={11}>Road North-South</option>
                    <option value={12}>Road East-West</option>
                    <option value={13}>Road Intersection</option>
                    <option value={14}>Desert</option>
                    <option value={15}>Ocean</option>
                    <option value={16}>Marshland</option>
                    <option value={17}>High Mountains</option>
                    <option value={18}>Outer Planes</option>
                    <option value={19}>Underdark - Wild</option>
                    <option value={20}>Underdark - City</option>
                    <option value={21}>Underdark - Inside</option>
                    <option value={22}>Underdark - Water (Swim)</option>
                    <option value={23}>Underdark - Water (No Swim)</option>
                    <option value={24}>Underdark - In Flight</option>
                    <option value={25}>Lava</option>
                    <option value={26}>Dirt Road North-South</option>
                    <option value={27}>Dirt Road East-West</option>
                    <option value={28}>Dirt Road Intersection</option>
                    <option value={29}>Cave</option>
                    <option value={30}>Jungle</option>
                    <option value={31}>Tundra</option>
                    <option value={32}>Taiga</option>
                    <option value={33}>Beach</option>
                    <option value={34}>Sea Port</option>
                    <option value={35}>Inside Room</option>
                    <option value={36}>River</option>
                  </select>
                  <p className="text-xs text-gray-400 mt-1">
                    This sector type will completely override the calculated terrain for this region.
                  </p>
                </div>
              );
            }
            
            return null;
          })()}
        </div>
      )}

      {/* Path Properties - sector type override */}
      {isPath && (
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Path Sector Override
          </label>
          <select
            value={(selectedItem as Path).path_props || 0}
            onChange={(e) => onUpdate({ path_props: parseInt(e.target.value) })}
            className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={0}>Inside</option>
            <option value={1}>City</option>
            <option value={2}>Field</option>
            <option value={3}>Forest</option>
            <option value={4}>Hills</option>
            <option value={5}>Low Mountains</option>
            <option value={6}>Water (Swim)</option>
            <option value={7}>Water (No Swim)</option>
            <option value={8}>In Flight</option>
            <option value={9}>Underwater</option>
            <option value={10}>Zone Entrance</option>
            <option value={11}>Road North-South</option>
            <option value={12}>Road East-West</option>
            <option value={13}>Road Intersection</option>
            <option value={14}>Desert</option>
            <option value={15}>Ocean</option>
            <option value={16}>Marshland</option>
            <option value={17}>High Mountains</option>
            <option value={18}>Outer Planes</option>
            <option value={19}>Underdark - Wild</option>
            <option value={20}>Underdark - City</option>
            <option value={21}>Underdark - Inside</option>
            <option value={22}>Underdark - Water (Swim)</option>
            <option value={23}>Underdark - Water (No Swim)</option>
            <option value={24}>Underdark - In Flight</option>
            <option value={25}>Lava</option>
            <option value={26}>Dirt Road North-South</option>
            <option value={27}>Dirt Road East-West</option>
            <option value={28}>Dirt Road Intersection</option>
            <option value={29}>Cave</option>
            <option value={30}>Jungle</option>
            <option value={31}>Tundra</option>
            <option value={32}>Taiga</option>
            <option value={33}>Beach</option>
            <option value={34}>Sea Port</option>
            <option value={35}>Inside Room</option>
            <option value={36}>River</option>
          </select>
          <p className="text-xs text-gray-400 mt-1">
            This sector type will override terrain along the path route.
          </p>
        </div>
      )}

      {/* Zone VNUM for regions and paths */}
      {(isRegion || isPath) && (
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Zone VNUM</label>
          <input
            type="number"
            value={(selectedItem as Region | Path).zone_vnum}
            onChange={(e) => onUpdate({ zone_vnum: Math.max(1, parseInt(e.target.value) || 1) })}
            className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            min="1"
            max="99999"
          />
        </div>
      )}

      {/* Coordinates */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-300">Points</label>
          <button className="text-blue-400 hover:text-blue-300 p-1">
            <Plus size={14} />
          </button>
        </div>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {('coordinates' in selectedItem ? selectedItem.coordinates : []).map((coord, index) => (
              <div key={index} className="flex items-center gap-2 p-2 bg-gray-800 rounded">
                <span className="text-xs text-gray-400 w-4">{index + 1}.</span>
                <div className="grid grid-cols-2 gap-1 flex-1">
                  <input
                    type="number"
                    value={coord.x}
                    onChange={(e) => {
                      const newCoords = [...(selectedItem as Region | Path).coordinates];
                      newCoords[index] = { ...coord, x: validateCoordinate(parseInt(e.target.value) || 0) };
                      onUpdate({ coordinates: newCoords });
                    }}
                    className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white text-xs focus:ring-1 focus:ring-blue-500"
                    placeholder="X"
                    min={COORDINATE_BOUNDS.min}
                    max={COORDINATE_BOUNDS.max}
                  />
                  <input
                    type="number"
                    value={coord.y}
                    onChange={(e) => {
                      const newCoords = [...(selectedItem as Region | Path).coordinates];
                      newCoords[index] = { ...coord, y: validateCoordinate(parseInt(e.target.value) || 0) };
                      onUpdate({ coordinates: newCoords });
                    }}
                    className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white text-xs focus:ring-1 focus:ring-blue-500"
                    placeholder="Y"
                    min={COORDINATE_BOUNDS.min}
                    max={COORDINATE_BOUNDS.max}
                  />
                </div>
                <button className="text-red-400 hover:text-red-300 p-1">
                  <Trash2 size={12} />
                </button>
              </div>
            ))}
          </div>
        </div>

      {/* Action buttons */}
      <div className="flex gap-2 pt-4 border-t border-gray-700">
        <button 
          onClick={() => {
            if (selectedItem && onSave) {
              const itemId = ('vnum' in selectedItem && selectedItem.vnum) 
                ? selectedItem.vnum.toString() 
                : selectedItem.id || '';
              if (itemId) {
                onSave(itemId);
              }
            }
          }}
          disabled={isSaving || !hasUnsavedChanges}
          className={`flex-1 py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors ${
            isSaving || !hasUnsavedChanges
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          <Save size={16} />
          {isSaving ? 'Saving...' : hasUnsavedChanges ? 'Save *' : 'Saved'}
        </button>
        <button 
          onClick={() => {
            if (selectedItem && onDiscard && hasUnsavedChanges) {
              const itemId = ('vnum' in selectedItem && selectedItem.vnum) 
                ? selectedItem.vnum.toString() 
                : selectedItem.id || '';
              if (itemId && confirm('Are you sure you want to discard unsaved changes?')) {
                onDiscard(itemId);
              }
            }
          }}
          disabled={!hasUnsavedChanges}
          className={`flex-1 py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors ${
            !hasUnsavedChanges
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
              : 'bg-red-600 hover:bg-red-700 text-white'
          }`}
        >
          <RotateCcw size={16} />
          Discard
        </button>
      </div>
    </div>
  );
};