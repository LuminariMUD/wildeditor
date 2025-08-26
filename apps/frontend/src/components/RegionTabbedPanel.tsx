import React, { useState } from 'react';
import { 
  FileText, Settings, CheckCircle, Star, 
  AlertCircle, Mountain, Layers
} from 'lucide-react';
import { Region } from '../types';
import { apiClient } from '../services/api';
import { GenerateDescriptionDialog } from './GenerateDescriptionDialog';

interface RegionTabbedPanelProps {
  region: Region;
  onUpdate: (updates: Partial<Region>) => void;
  onCreateLayer?: (baseRegion: Region, layerType: 'sector' | 'transform') => void;
  relatedRegions?: Region[];
  onSelectRegion?: (region: Region) => void;
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
  relatedRegions = [],
  onSelectRegion
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('properties');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [showGenerateDialog, setShowGenerateDialog] = useState(false);

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
              <li 
                key={r.vnum} 
                className="text-gray-400 text-xs flex items-center gap-1 hover:text-gray-200 cursor-pointer transition-colors"
                onClick={() => onSelectRegion?.(r)}
                title={`Click to select ${r.name}`}
              >
                {getRegionIcon(r.region_type)}
                <span className="hover:underline">{r.name}</span>
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
          value={region.region_description || ''}
          onChange={(e) => onUpdate({ region_description: e.target.value })}
          className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[120px] resize-y"
          placeholder="Enter a detailed description of this region..."
        />
      </div>

      {/* Description style */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">Style</label>
          <select
            value={region.description_style || 'poetic'}
            onChange={(e) => onUpdate({ description_style: e.target.value })}
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
            value={region.description_length || 'moderate'}
            onChange={(e) => onUpdate({ description_length: e.target.value })}
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
              checked={region.has_historical_context || false}
              onChange={(e) => onUpdate({ has_historical_context: e.target.checked })}
              className="rounded bg-gray-800 border-gray-600 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">Historical Context</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={region.has_resource_info || false}
              onChange={(e) => onUpdate({ has_resource_info: e.target.checked })}
              className="rounded bg-gray-800 border-gray-600 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">Resource Information</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={region.has_wildlife_info || false}
              onChange={(e) => onUpdate({ has_wildlife_info: e.target.checked })}
              className="rounded bg-gray-800 border-gray-600 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">Wildlife Details</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={region.has_geological_info || false}
              onChange={(e) => onUpdate({ has_geological_info: e.target.checked })}
              className="rounded bg-gray-800 border-gray-600 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">Geological Features</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={region.has_cultural_info || false}
              onChange={(e) => onUpdate({ has_cultural_info: e.target.checked })}
              className="rounded bg-gray-800 border-gray-600 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">Cultural Information</span>
          </label>
        </div>
      </div>

      {/* Generate with AI button */}
      <button
        className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white py-2 px-4 rounded-lg flex items-center justify-center gap-2 text-sm font-medium"
        onClick={() => setShowGenerateDialog(true)}
      >
        <Star className="w-4 h-4" />
        Generate with AI
      </button>
      
      {/* Error message */}
      {generationError && (
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-2">
          <p className="text-red-400 text-xs">{generationError}</p>
        </div>
      )}
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
            value={region.description_quality_score || 0}
            onChange={(e) => onUpdate({ description_quality_score: parseFloat(e.target.value) })}
            className="flex-1"
          />
          <span className="text-white font-medium w-12 text-right">
            {(region.description_quality_score || 0).toFixed(2)}
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
            checked={region.requires_review || false}
            onChange={(e) => onUpdate({ requires_review: e.target.checked })}
            className="rounded bg-gray-800 border-gray-600 text-yellow-500 focus:ring-yellow-500"
          />
          <span className="text-sm text-gray-300">Requires Review</span>
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={region.is_approved || false}
            onChange={(e) => onUpdate({ is_approved: e.target.checked })}
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
          value={region.ai_agent_source || ''}
          onChange={(e) => onUpdate({ ai_agent_source: e.target.value })}
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
            <span className={region.region_description ? 'text-green-400' : 'text-red-400'}>
              {region.region_description ? 'Present' : 'Missing'}
            </span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400">Quality:</span>
            <span className={
              (region.description_quality_score || 0) >= 7 ? 'text-green-400' :
              (region.description_quality_score || 0) >= 4 ? 'text-yellow-400' :
              'text-red-400'
            }>
              {(region.description_quality_score || 0).toFixed(1)}/10
            </span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400">Review:</span>
            <span className={
              region.is_approved ? 'text-green-400' :
              region.requires_review ? 'text-yellow-400' :
              'text-gray-400'
            }>
              {region.is_approved ? 'Approved' :
               region.requires_review ? 'Pending' :
               'Not Required'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  const handleGenerateDescription = async (params: {
    userPrompt: string;
    style: string;
    length: string;
    includeSections: string[];
  }) => {
    setIsGenerating(true);
    setGenerationError(null);
    
    try {
      // Determine terrain theme based on region type
      let terrain_theme = 'wilderness';
      if (region.region_type === 1) terrain_theme = 'geographic';
      else if (region.region_type === 2) terrain_theme = 'encounter';
      else if (region.region_type === 3) terrain_theme = 'transform';
      else if (region.region_type === 4) terrain_theme = 'sector';
      
      const result = await apiClient.generateRegionDescription({
        region_vnum: region.vnum,
        region_name: region.name,
        region_type: region.region_type,
        terrain_theme,
        description_style: params.style,
        description_length: params.length,
        include_sections: params.includeSections,
        user_prompt: params.userPrompt // Add user prompt to the request
      });
      
      if (result.error) {
        setGenerationError(result.error);
      } else if (result.generated_description) {
        onUpdate({
          region_description: result.generated_description,
          description_style: params.style,
          description_length: params.length,
          description_quality_score: result.suggested_quality_score || 7.0,
          ai_agent_source: result.ai_provider || 'mcp'
        });
        
        // Update metadata flags based on included sections
        const metadataUpdates: Partial<Region> = {};
        if (params.includeSections.includes('wildlife')) metadataUpdates.has_wildlife_info = true;
        if (params.includeSections.includes('history')) metadataUpdates.has_historical_context = true;
        if (params.includeSections.includes('resources')) metadataUpdates.has_resource_info = true;
        if (params.includeSections.includes('culture')) metadataUpdates.has_cultural_info = true;
        if (params.includeSections.includes('vegetation')) metadataUpdates.has_geological_info = true;
        
        if (Object.keys(metadataUpdates).length > 0) {
          onUpdate(metadataUpdates);
        }
        
        // Close dialog on success
        setShowGenerateDialog(false);
      }
    } catch (error) {
      console.error('Failed to generate description:', error);
      setGenerationError('Failed to connect to AI service');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <>
      <div className="flex flex-col h-full">
        {renderTabs()}
        <div className="flex-1 p-4 overflow-y-auto">
          {activeTab === 'properties' && renderPropertiesTab()}
          {activeTab === 'description' && renderDescriptionTab()}
          {activeTab === 'review' && renderReviewTab()}
        </div>
      </div>
      
      {/* Generate Description Dialog */}
      <GenerateDescriptionDialog
        isOpen={showGenerateDialog}
        onClose={() => setShowGenerateDialog(false)}
        onGenerate={handleGenerateDescription}
        regionName={region.name}
        regionType={region.region_type}
        isGenerating={isGenerating}
      />
    </>
  );
};