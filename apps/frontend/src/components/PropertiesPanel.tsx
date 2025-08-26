import React, { useCallback, useEffect, useState } from 'react';
import { 
  Save, RotateCcw, Trash2, Plus, Layers, Mountain,
  Route, Waves, TreePine, MapPin, AlertCircle 
} from 'lucide-react';
import { Region, Path } from '../types';
import { apiClient, type PathTypesResponse } from '../services/api';
import { RegionTabbedPanel } from './RegionTabbedPanel';

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
  // Region layering
  onCreateLayer?: (baseRegion: Region, layerType: 'sector' | 'transform') => void;
  relatedRegions?: Region[];
  onSelectItem?: (item: Region | Path | null) => void;
}

// Helper to get path icon based on type
const getPathIcon = (pathType: number) => {
  switch (pathType) {
    case 1: return <MapPin className="w-5 h-5" />; // Paved Road
    case 2: return <Route className="w-5 h-5" />; // Dirt Road
    case 3: return <TreePine className="w-5 h-5" />; // Geographic
    case 5: return <Waves className="w-5 h-5" />; // River
    case 6: return <Waves className="w-4 h-4" />; // Stream (smaller)
    default: return <Route className="w-5 h-5" />;
  }
};

// Helper to get path color class
const getPathColorClass = (pathType: number) => {
  switch (pathType) {
    case 1: return 'text-gray-400'; // Paved Road
    case 2: return 'text-amber-600'; // Dirt Road
    case 3: return 'text-green-500'; // Geographic
    case 5: return 'text-blue-500'; // River
    case 6: return 'text-cyan-400'; // Stream
    default: return 'text-gray-400';
  }
};

// Helper to get region icon based on type
const getRegionIcon = (regionType: number) => {
  switch (regionType) {
    case 1: return null; // Geographic - no icon, just text
    case 2: return <AlertCircle className="w-4 h-4 text-red-400" />; // Encounter
    case 3: return <Mountain className="w-4 h-4 text-purple-400" />; // Transform
    case 4: return <Layers className="w-4 h-4 text-amber-400" />; // Sector
    default: return null;
  }
};

export const PropertiesPanel: React.FC<PropertiesPanelProps> = ({
  selectedItem,
  onUpdate,
  onFinishDrawing,
  isDrawing,
  onSave,
  onDiscard,
  onDelete,
  isSaving = false,
  hasUnsavedChanges = false,
  onCreateLayer,
  relatedRegions = [],
  onSelectItem
}) => {
  const COORDINATE_BOUNDS = { min: -1024, max: 1024 };
  const [pathTypes, setPathTypes] = useState<PathTypesResponse | null>(null);
  
  // Fetch path types on mount
  useEffect(() => {
    apiClient.getPathTypes().then(setPathTypes).catch(console.error);
  }, []);
  
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

  // For regions, use the tabbed interface
  if (isRegion) {
    return (
      <div className="bg-gray-900 h-full flex flex-col">
        <div className="p-4 pb-0">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              {getRegionIcon((selectedItem as Region).region_type)}
              <span>Region: {selectedItem.name}</span>
            </h3>
            <button 
              onClick={() => {
                if (onDelete && selectedItem) {
                  const itemId = selectedItem.vnum?.toString() || '';
                  if (itemId && confirm(`Are you sure you want to delete this region?\n\n"${selectedItem.name}"\n\nThis action cannot be undone.`)) {
                    onDelete(itemId);
                  }
                }
              }}
              className="text-red-400 hover:text-red-300 p-1"
              title="Delete this region"
            >
              <Trash2 size={16} />
            </button>
          </div>
          
          {/* Basic fields that are always visible */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Name</label>
              <input
                type="text"
                value={selectedItem.name}
                onChange={(e) => onUpdate({ name: sanitizeText(e.target.value) })}
                onBlur={(e) => onUpdate({ name: e.target.value.trim().slice(0, 100) })}
                className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1 text-white text-sm focus:ring-1 focus:ring-blue-500 focus:border-transparent"
                maxLength={100}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">VNUM</label>
              <input
                type="number"
                value={selectedItem.vnum}
                onChange={(e) => onUpdate({ vnum: validateVnum(parseInt(e.target.value) || 1) })}
                className="w-full bg-gray-800 border border-gray-600 rounded px-2 py-1 text-white text-sm focus:ring-1 focus:ring-blue-500 focus:border-transparent"
                min="1"
                max="99999"
              />
            </div>
          </div>
        </div>
        
        {/* Tabbed panel for region details */}
        <div className="flex-1 overflow-hidden">
          <RegionTabbedPanel
            region={selectedItem as Region}
            onUpdate={onUpdate}
            onCreateLayer={onCreateLayer}
            relatedRegions={relatedRegions}
            onSelectRegion={onSelectItem as ((region: Region) => void) | undefined}
          />
        </div>
        
        {/* Save/Discard buttons */}
        <div className="p-4 pt-0">
          <div className="flex gap-2 pt-4 border-t border-gray-700">
            <button 
              onClick={() => onSave?.(selectedItem.vnum?.toString() || '')}
              disabled={isSaving || !hasUnsavedChanges}
              className={`flex-1 py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors text-sm ${
                isSaving || !hasUnsavedChanges
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
            >
              <Save size={14} />
              {isSaving ? 'Saving...' : hasUnsavedChanges ? 'Save Changes' : 'Saved'}
            </button>
            <button 
              onClick={() => {
                if (onDiscard && hasUnsavedChanges) {
                  const itemId = selectedItem.vnum?.toString() || '';
                  if (itemId && confirm('Discard unsaved changes?')) {
                    onDiscard(itemId);
                  }
                }
              }}
              disabled={!hasUnsavedChanges}
              className={`flex-1 py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors text-sm ${
                !hasUnsavedChanges
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-red-600 hover:bg-red-700 text-white'
              }`}
            >
              <RotateCcw size={14} />
              Discard
            </button>
          </div>
        </div>
      </div>
    );
  }

  // For paths, keep the existing interface
  return (
    <div className="p-4 bg-gray-900 space-y-4 max-h-full overflow-y-auto">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          {isPath && (
            <>
              <span className={getPathColorClass((selectedItem as Path).path_type)}>
                {getPathIcon((selectedItem as Path).path_type)}
              </span>
              <span>Path Properties</span>
            </>
          )}
          {isRegion && (
            <>
              {getRegionIcon((selectedItem as Region).region_type)}
              <span>Region Properties</span>
            </>
          )}
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
        <div className="space-y-3">
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
              <option value={4}>Sector Override</option>
            </select>
          </div>
          
          {/* Region layering for Geographic regions */}
          {(selectedItem as Region).region_type === 1 && onCreateLayer && (
            <div className="bg-purple-900/20 border border-purple-800 rounded-lg p-3">
              <h4 className="text-purple-300 font-medium text-sm mb-2">
                <Layers className="inline w-4 h-4 mr-1" />
                Region Layering
              </h4>
              <p className="text-purple-200 text-xs mb-3">
                Geographic regions can be paired with matching layers for terrain control.
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => onCreateLayer(selectedItem as Region, 'sector')}
                  className="flex-1 bg-amber-600 hover:bg-amber-700 text-white text-xs py-2 px-3 rounded flex items-center justify-center gap-1"
                  title="Create a matching Sector Override region with the same coordinates"
                >
                  <Layers className="w-3 h-3" />
                  Add Sector Layer
                </button>
                <button
                  onClick={() => onCreateLayer(selectedItem as Region, 'transform')}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 text-white text-xs py-2 px-3 rounded flex items-center justify-center gap-1"
                  title="Create a matching Transform region for elevation adjustment"
                >
                  <Mountain className="w-3 h-3" />
                  Add Transform Layer
                </button>
              </div>
              
              {/* Show related regions if any */}
              {relatedRegions.length > 0 && (
                <div className="mt-3 pt-3 border-t border-purple-700">
                  <p className="text-purple-300 text-xs font-medium mb-2">Related Regions:</p>
                  <ul className="space-y-1">
                    {relatedRegions.map(r => (
                      <li key={r.vnum} className="text-purple-200 text-xs flex items-center gap-1">
                        {getRegionIcon(r.region_type)}
                        <span>{r.name}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
          
          {/* Warning for Geographic regions */}
          {(selectedItem as Region).region_type === 1 && (
            <div className="bg-yellow-900/20 border border-yellow-800 rounded-lg p-2">
              <p className="text-yellow-300 text-xs flex items-start gap-1">
                <AlertCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                <span>Geographic regions should not overlap with other Geographic regions.</span>
              </p>
            </div>
          )}
        </div>
      )}

      {isPath && (
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Path Type</label>
            <select
              value={(selectedItem as Path).path_type}
              onChange={(e) => onUpdate({ path_type: parseInt(e.target.value) as Path['path_type'] })}
              className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={1}>🛣️ Paved Road</option>
              <option value={2}>🚧 Dirt Road</option>
              <option value={3}>🌿 Geographic Feature</option>
              <option value={5}>🌊 River</option>
              <option value={6}>💧 Stream</option>
            </select>
            
            {/* Show path type description if available */}
            {pathTypes && pathTypes.path_types[(selectedItem as Path).path_type] && (
              <div className="mt-2 p-2 bg-gray-800 rounded text-xs text-gray-400">
                <p className="font-medium text-gray-300">
                  {pathTypes.path_types[(selectedItem as Path).path_type].name}
                </p>
                <p className="mt-1">
                  {pathTypes.path_types[(selectedItem as Path).path_type].description}
                </p>
                <p className="mt-1 text-blue-400">
                  Behavior: {pathTypes.path_types[(selectedItem as Path).path_type].behavior}
                </p>
              </div>
            )}
          </div>
          
          {/* Path behavior info box */}
          <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-3">
            <h4 className="text-blue-300 font-medium text-sm mb-2">Path Behavior</h4>
            <ul className="text-blue-200 text-xs space-y-1">
              <li>✓ Overrides underlying terrain sector</li>
              <li>✓ Replaces room name with: "{selectedItem.name}"</li>
              <li>✓ Provides movement benefits based on type</li>
            </ul>
          </div>
        </div>
      )}

      {/* Region Properties - type-specific values */}
      {isRegion && (
        <div>
          {(() => {
            const region = selectedItem as Region;
            const regionType = region.region_type;
            
            if (regionType === 1) {
              // Geographic - value ignored by game but can be any integer
              return (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Properties (Geographic - value ignored by game)
                  </label>
                  <input
                    type="number"
                    value={region.region_props || 0}
                    onChange={(e) => onUpdate({ region_props: parseInt(e.target.value) || 0 })}
                    className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="0 (any value, ignored by game)"
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    This value is ignored by the game.
                  </p>
                </div>
              );
            } else if (regionType === 2) {
              // Encounter - mob vnums go in region_reset_data, not region_props
              return (
                <div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Properties (Encounter - value ignored by game)
                    </label>
                    <input
                      type="number"
                      value={region.region_props || 0}
                      onChange={(e) => onUpdate({ region_props: parseInt(e.target.value) || 0 })}
                      className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="0 (any value, ignored by game)"
                    />
                    <p className="text-xs text-gray-400 mt-1">
                      This value is ignored by the game.
                    </p>
                  </div>
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Mob VNums (Encounter spawning)
                    </label>
                    <input
                      type="text"
                      value={region.region_reset_data || ""}
                      onChange={(e) => onUpdate({ region_reset_data: e.target.value })}
                      className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="1001,1002,1003 or empty for no encounters"
                    />
                    <p className="text-xs text-gray-400 mt-1">
                      Comma-separated list of mob VNums that can spawn in this region (e.g., "1001,1002,1003"). Leave empty for no encounters.
                    </p>
                  </div>
                </div>
              );
            } else if (regionType === 3) {
              // Sector Transform - elevation adjustment
              return (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Elevation Adjustment (Transform)
                  </label>
                  <input
                    type="number"
                    value={region.region_props || 0}
                    onChange={(e) => onUpdate({ region_props: parseInt(e.target.value) || 0 })}
                    className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Elevation change (e.g., 50 or -30)"
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Positive values raise elevation, negative values lower it. This affects calculated terrain type.
                  </p>
                </div>
              );
            } else if (regionType === 4) {
              // Sector Override - dropdown for sector types
              return (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Sector Type (Override)
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
                    Completely overrides the calculated terrain type for all coordinates in this region.
                  </p>
                </div>
              );
            } else {
              // Unknown region type - generic number input
              return (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Properties (Unknown region type {regionType})
                  </label>
                  <input
                    type="number"
                    value={region.region_props || 0}
                    onChange={(e) => onUpdate({ region_props: parseInt(e.target.value) || 0 })}
                    className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="0"
                  />
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