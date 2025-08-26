import React, { useState } from 'react';
import { 
  FileText, Settings, CheckCircle, Star, 
  AlertCircle, Mountain, Layers, Hash
} from 'lucide-react';
import { Region } from '../types';

interface RegionTabbedPanelProps {
  region: Region;
  onUpdate: (updates: Partial<Region>) => void;
  onCreateLayer?: (baseRegion: Region, layerType: 'sector' | 'transform') => void;
  relatedRegions?: Region[];
}

type TabType = 'properties' | 'description' | 'review';

// Helper to get region icon based on type
const getRegionIcon = (regionType: number) => {
  switch (regionType) {
    case 1: return null; // Geographic - no icon
    case 2: return <AlertCircle className="w-4 h-4 text-red-400" />; // Encounter
    case 3: return <Mountain className="w-4 h-4 text-purple-400" />; // Transform
    case 4: return <Layers className="w-4 h-4 text-amber-400" />; // Sector
    default: return null;
  }
};

export const RegionTabbedPanel: React.FC<RegionTabbedPanelProps> = ({
  region,
  onUpdate,
  onCreateLayer,
  relatedRegions = []
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('properties');
  
  // Extended region interface with description fields
  const extendedRegion = region as Region & {
    region_description?: string;
    description_style?: string;
    description_length?: string;
    has_historical_context?: boolean;
    has_resource_info?: boolean;
    has_wildlife_info?: boolean;
    has_geological_info?: boolean;
    has_cultural_info?: boolean;
    description_quality_score?: number;
    requires_review?: boolean;
    is_approved?: boolean;
    ai_agent_source?: string;
  };

  const renderTabs = () => (
    <div className="flex border-b border-gray-700">
      <button
        onClick={() => setActiveTab('properties')}
        className={`px-4 py-2 text-sm font-medium transition-colors flex items-center gap-2 ${
          activeTab === 'properties'
            ? 'text-white border-b-2 border-blue-500'
            : 'text-gray-400 hover:text-white'
        }`}
      >
        <Settings className="w-4 h-4" />
        Properties
      </button>
      <button
        onClick={() => setActiveTab('description')}
        className={`px-4 py-2 text-sm font-medium transition-colors flex items-center gap-2 ${
          activeTab === 'description'
            ? 'text-white border-b-2 border-blue-500'
            : 'text-gray-400 hover:text-white'
        }`}
      >
        <FileText className="w-4 h-4" />
        Description
      </button>
      <button
        onClick={() => setActiveTab('review')}
        className={`px-4 py-2 text-sm font-medium transition-colors flex items-center gap-2 ${
          activeTab === 'review'
            ? 'text-white border-b-2 border-blue-500'
            : 'text-gray-400 hover:text-white'
        }`}
      >
        <CheckCircle className="w-4 h-4" />
        Review
      </button>
    </div>
  );

  const renderPropertiesTab = () => (
    <div className="space-y-3">
      {/* Region Type */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">Type</label>
        <select
          value={region.region_type}
          onChange={(e) => onUpdate({ region_type: parseInt(e.target.value) as Region['region_type'] })}
          className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value={1}>Geographic</option>
          <option value={2}>Encounter</option>
          <option value={3}>Sector Transform</option>
          <option value={4}>Sector Override</option>
        </select>
      </div>

      {/* Zone VNUM */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">Zone VNUM</label>
        <input
          type="number"
          value={region.zone_vnum}
          onChange={(e) => onUpdate({ zone_vnum: Math.max(1, parseInt(e.target.value) || 1) })}
          className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          min="1"
          max="99999"
        />
      </div>

      {/* Region-specific properties based on type */}
      {region.region_type === 1 && (
        <>
          {/* Geographic regions */}
          <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-3">
            <p className="text-blue-300 text-xs">
              Geographic regions define named areas visible to players.
              The name appears in room descriptions.
            </p>
          </div>
          
          {/* Layering options */}
          {onCreateLayer && (
            <div className="bg-purple-900/20 border border-purple-800 rounded-lg p-3">
              <h4 className="text-purple-300 font-medium text-sm mb-2">
                <Layers className="inline w-4 h-4 mr-1" />
                Region Layering
              </h4>
              <div className="flex gap-2">
                <button
                  onClick={() => onCreateLayer(region, 'sector')}
                  className="flex-1 bg-amber-600 hover:bg-amber-700 text-white text-xs py-2 px-3 rounded"
                >
                  Add Sector Layer
                </button>
                <button
                  onClick={() => onCreateLayer(region, 'transform')}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 text-white text-xs py-2 px-3 rounded"
                >
                  Add Transform
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {region.region_type === 2 && (
        <>
          {/* Encounter regions */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Mob VNums (comma-separated)
            </label>
            <input
              type="text"
              value={region.region_reset_data || ''}
              onChange={(e) => onUpdate({ region_reset_data: e.target.value })}
              className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="1001,1002,1003"
            />
            <p className="text-xs text-gray-400 mt-1">
              Mob VNums that can spawn in this region
            </p>
          </div>
        </>
      )}

      {region.region_type === 3 && (
        <>
          {/* Transform regions */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Elevation Adjustment
            </label>
            <input
              type="number"
              value={region.region_props || 0}
              onChange={(e) => onUpdate({ region_props: parseInt(e.target.value) || 0 })}
              className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="50 or -30"
            />
            <p className="text-xs text-gray-400 mt-1">
              Positive raises elevation, negative lowers it
            </p>
          </div>
        </>
      )}

      {region.region_type === 4 && (
        <>
          {/* Sector Override regions */}
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
              <option value={14}>Desert</option>
              <option value={15}>Ocean</option>
              <option value={16}>Marshland</option>
              <option value={17}>High Mountains</option>
              <option value={29}>Cave</option>
              <option value={30}>Jungle</option>
              <option value={31}>Tundra</option>
              <option value={33}>Beach</option>
            </select>
          </div>
        </>
      )}

      {/* Related regions */}
      {relatedRegions.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-3">
          <p className="text-gray-300 text-xs font-medium mb-2">Related Regions:</p>
          <ul className="space-y-1">
            {relatedRegions.map(r => (
              <li key={r.vnum} className="text-gray-400 text-xs flex items-center gap-1">
                {getRegionIcon(r.region_type)}
                <span>{r.name}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  const renderDescriptionTab = () => (
    <div className="space-y-3">
      {/* Description text */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Region Description
        </label>
        <textarea
          value={extendedRegion.region_description || ''}
          onChange={(e) => onUpdate({ region_description: e.target.value } as any)}
          className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[120px] resize-y"
          placeholder="Enter a detailed description of this region..."
        />
      </div>

      {/* Description style */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Style</label>
          <select
            value={extendedRegion.description_style || 'poetic'}
            onChange={(e) => onUpdate({ description_style: e.target.value } as any)}
            className="w-full bg-gray-800 border border-gray-600 rounded-lg px-2 py-1 text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="poetic">Poetic</option>
            <option value="practical">Practical</option>
            <option value="mysterious">Mysterious</option>
            <option value="dramatic">Dramatic</option>
            <option value="pastoral">Pastoral</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Length</label>
          <select
            value={extendedRegion.description_length || 'moderate'}
            onChange={(e) => onUpdate({ description_length: e.target.value } as any)}
            className="w-full bg-gray-800 border border-gray-600 rounded-lg px-2 py-1 text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="brief">Brief</option>
            <option value="moderate">Moderate</option>
            <option value="detailed">Detailed</option>
            <option value="extensive">Extensive</option>
          </select>
        </div>
      </div>

      {/* Content metadata flags */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">Content Elements</label>
        <div className="space-y-2">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={extendedRegion.has_historical_context || false}
              onChange={(e) => onUpdate({ has_historical_context: e.target.checked } as any)}
              className="rounded bg-gray-800 border-gray-600 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">Historical Context</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={extendedRegion.has_resource_info || false}
              onChange={(e) => onUpdate({ has_resource_info: e.target.checked } as any)}
              className="rounded bg-gray-800 border-gray-600 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">Resource Information</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={extendedRegion.has_wildlife_info || false}
              onChange={(e) => onUpdate({ has_wildlife_info: e.target.checked } as any)}
              className="rounded bg-gray-800 border-gray-600 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">Wildlife Details</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={extendedRegion.has_geological_info || false}
              onChange={(e) => onUpdate({ has_geological_info: e.target.checked } as any)}
              className="rounded bg-gray-800 border-gray-600 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">Geological Features</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={extendedRegion.has_cultural_info || false}
              onChange={(e) => onUpdate({ has_cultural_info: e.target.checked } as any)}
              className="rounded bg-gray-800 border-gray-600 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">Cultural Information</span>
          </label>
        </div>
      </div>

      {/* Generate with AI button (placeholder for future) */}
      <button
        className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white py-2 px-4 rounded-lg flex items-center justify-center gap-2 text-sm font-medium"
        onClick={() => console.log('Generate description with AI')}
      >
        <Star className="w-4 h-4" />
        Generate with AI
      </button>
    </div>
  );

  const renderReviewTab = () => (
    <div className="space-y-3">
      {/* Quality score */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Quality Score
        </label>
        <div className="flex items-center gap-3">
          <input
            type="range"
            min="0"
            max="9.99"
            step="0.01"
            value={extendedRegion.description_quality_score || 0}
            onChange={(e) => onUpdate({ description_quality_score: parseFloat(e.target.value) } as any)}
            className="flex-1"
          />
          <span className="text-white font-medium w-12 text-right">
            {(extendedRegion.description_quality_score || 0).toFixed(2)}
          </span>
        </div>
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>Poor</span>
          <span>Excellent</span>
        </div>
      </div>

      {/* Review status */}
      <div className="space-y-2">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={extendedRegion.requires_review || false}
            onChange={(e) => onUpdate({ requires_review: e.target.checked } as any)}
            className="rounded bg-gray-800 border-gray-600 text-yellow-500 focus:ring-yellow-500"
          />
          <span className="text-sm text-gray-300">Requires Review</span>
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={extendedRegion.is_approved || false}
            onChange={(e) => onUpdate({ is_approved: e.target.checked } as any)}
            className="rounded bg-gray-800 border-gray-600 text-green-500 focus:ring-green-500"
          />
          <span className="text-sm text-gray-300">Approved</span>
        </label>
      </div>

      {/* AI source */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          AI Agent Source
        </label>
        <input
          type="text"
          value={extendedRegion.ai_agent_source || ''}
          onChange={(e) => onUpdate({ ai_agent_source: e.target.value } as any)}
          className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="manual, mcp, agent, etc."
        />
      </div>

      {/* Status summary */}
      <div className="bg-gray-800 rounded-lg p-3">
        <h4 className="text-sm font-medium text-gray-300 mb-2">Status Summary</h4>
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400">Description:</span>
            <span className={extendedRegion.region_description ? 'text-green-400' : 'text-red-400'}>
              {extendedRegion.region_description ? 'Present' : 'Missing'}
            </span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400">Quality:</span>
            <span className={
              (extendedRegion.description_quality_score || 0) >= 7 ? 'text-green-400' :
              (extendedRegion.description_quality_score || 0) >= 4 ? 'text-yellow-400' :
              'text-red-400'
            }>
              {(extendedRegion.description_quality_score || 0).toFixed(1)}/10
            </span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400">Review:</span>
            <span className={
              extendedRegion.is_approved ? 'text-green-400' :
              extendedRegion.requires_review ? 'text-yellow-400' :
              'text-gray-400'
            }>
              {extendedRegion.is_approved ? 'Approved' :
               extendedRegion.requires_review ? 'Pending' :
               'Not Required'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex flex-col h-full">
      {renderTabs()}
      <div className="flex-1 p-4 overflow-y-auto">
        {activeTab === 'properties' && renderPropertiesTab()}
        {activeTab === 'description' && renderDescriptionTab()}
        {activeTab === 'review' && renderReviewTab()}
      </div>
    </div>
  );
};