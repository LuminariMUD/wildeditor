import React, { useState, useEffect, useCallback } from 'react';
import { 
  FileText, Settings, CheckCircle, Star, 
  AlertCircle, Mountain, Layers, Lightbulb,
  Plus, ChevronDown, ChevronRight
} from 'lucide-react';
import { Region } from '../types';
import { apiClient } from '../services/api';
import { GenerateDescriptionDialog } from './GenerateDescriptionDialog';
import { CoordinateEditor } from './CoordinateEditor';

interface RegionTabbedPanelProps {
  region: Region;
  onUpdate: (updates: Partial<Region>) => void;
  onCreateLayer?: (baseRegion: Region, layerType: 'sector' | 'transform') => void;
  relatedRegions?: Region[];
  onSelectRegion?: (region: Region) => void;
}

type TabType = 'properties' | 'description' | 'hints' | 'review';

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
  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(new Set());
  interface RegionHint {
    id: number;
    region_vnum: number;
    hint_category: string;
    hint_text: string;
    priority: number;
    seasonal_weight?: Record<string, number>;
    weather_conditions?: string;
    time_of_day_weight?: Record<string, number>;
    is_active: boolean;
  }

  const [hints, setHints] = useState<RegionHint[]>([]);
  const [hintsLoading, setHintsLoading] = useState(false);
  const [hintsError, setHintsError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());

  const fetchHints = useCallback(async () => {
    setHintsLoading(true);
    setHintsError(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/regions/${region.vnum}/hints`, {
        headers: {
          'Authorization': `Bearer ${import.meta.env.VITE_WILDEDITOR_API_KEY || ''}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setHints(data.hints || []);
      } else if (response.status === 404) {
        setHints([]);
      } else {
        throw new Error(`Failed to fetch hints: ${response.status}`);
      }
    } catch (error) {
      setHintsError(error instanceof Error ? error.message : 'Failed to fetch hints');
      setHints([]);
    } finally {
      setHintsLoading(false);
    }
  }, [region.vnum]);

  // Fetch hints when hints tab is selected
  useEffect(() => {
    if (activeTab === 'hints' && region.vnum) {
      fetchHints();
    }
  }, [activeTab, region.vnum, fetchHints]);

  const generateHintsFromDescription = async (description?: string, askConfirmation: boolean = true) => {
    const descToUse = description || region.region_description;
    
    if (!descToUse) {
      setHintsError('Region needs a description to generate hints');
      return;
    }

    // Ask for confirmation if hints already exist
    if (askConfirmation && hints.length > 0) {
      const confirmOverwrite = window.confirm(
        `This region already has ${hints.length} hints. Generating new hints will overwrite them. Continue?`
      );
      if (!confirmOverwrite) {
        return;
      }
    }

    setHintsLoading(true);
    setHintsError(null);
    
    try {
      // Call the backend proxy endpoint that will forward to MCP
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/mcp/call-tool`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${import.meta.env.VITE_WILDEDITOR_API_KEY || ''}`
        },
        body: JSON.stringify({
          tool_name: 'generate_hints_from_description',
          arguments: {
            region_vnum: region.vnum,
            region_name: region.name,
            description: descToUse,
            target_hint_count: 20,
            include_profile: true
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.success && data.result) {
          // The backend should have already parsed the result properly
          const hintsData = data.result;
          
          // Handle legacy format where result might still be wrapped in text
          if (hintsData.text && !hintsData.hints) {
            console.warn('Received legacy text format from backend, this should not happen');
            throw new Error('Backend returned unparsed text format');
          }
          
          // Store the generated hints
          if (hintsData.hints && hintsData.hints.length > 0) {
            // Format hints for backend API (map 'category' to 'hint_category')
            const formattedHints = hintsData.hints.map((hint: { category?: string; hint_category?: string; text?: string; hint_text?: string; priority?: number; weather_conditions?: string[]; seasonal_weight?: Record<string, number>; time_of_day_weight?: Record<string, number> }) => ({
              hint_category: hint.category || hint.hint_category,
              hint_text: hint.text || hint.hint_text,
              priority: hint.priority || 5,
              weather_conditions: hint.weather_conditions || ['clear', 'cloudy', 'rainy', 'stormy', 'lightning'],
              seasonal_weight: hint.seasonal_weight || null,
              time_of_day_weight: hint.time_of_day_weight || null
            }));
            
            const storeResponse = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/regions/${region.vnum}/hints`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${import.meta.env.VITE_WILDEDITOR_API_KEY || ''}`
              },
              body: JSON.stringify({
                hints: formattedHints
              })
            });

            if (storeResponse.ok) {
              // Refresh hints list
              await fetchHints();
              
              // Expand first category to show results
              if (hintsData.hints.length > 0) {
                const firstCategory = hintsData.hints[0].category || hintsData.hints[0].hint_category;
                setExpandedCategories(new Set([firstCategory]));
              }
              
              console.log(`Successfully generated and stored ${formattedHints.length} hints`);
            } else {
              console.error('Failed to store hints:', storeResponse.status, await storeResponse.text());
              throw new Error('Failed to store generated hints');
            }
          } else {
            console.log('Hints data:', hintsData);
            setHintsError('No hints were generated from the description');
          }
        } else {
          throw new Error(data.error || 'Failed to generate hints');
        }
      } else {
        throw new Error(`Failed to generate hints: ${response.status}`);
      }
    } catch (error) {
      setHintsError(error instanceof Error ? error.message : 'Failed to generate hints');
    } finally {
      setHintsLoading(false);
    }
  };

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  const toggleSection = (section: string) => {
    const newCollapsed = new Set(collapsedSections);
    if (newCollapsed.has(section)) {
      newCollapsed.delete(section);
    } else {
      newCollapsed.add(section);
    }
    setCollapsedSections(newCollapsed);
  };

  // Check if a sector layer already exists for this region
  const hasSectorLayer = relatedRegions.some(
    r => r.region_type === 4 && 
    JSON.stringify(r.coordinates) === JSON.stringify(region.coordinates)
  );

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
        onClick={() => setActiveTab('hints')}
        className={`px-4 py-2 text-sm font-medium transition-colors flex items-center gap-2 ${
          activeTab === 'hints'
            ? 'text-white border-b-2 border-blue-500'
            : 'text-gray-400 hover:text-white'
        }`}
      >
        <Lightbulb className="w-4 h-4" />
        Hints
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

          {/* Related regions - moved up and made collapsible */}
          {relatedRegions.length > 0 && (
            <div className="bg-gray-800 rounded-lg overflow-hidden">
              <button
                onClick={() => toggleSection('related')}
                className="w-full px-3 py-2 flex items-center justify-between text-gray-300 hover:bg-gray-700 transition-colors"
              >
                <span className="text-xs font-medium flex items-center gap-1">
                  <Layers className="w-4 h-4" />
                  Related Regions ({relatedRegions.length})
                </span>
                {collapsedSections.has('related') ? <ChevronRight className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              {!collapsedSections.has('related') && (
                <div className="px-3 pb-3">
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
          )}
          
          {/* Region Layering - moved after related regions */}
          {onCreateLayer && (
            <div className="bg-purple-900/20 border border-purple-800 rounded-lg p-3">
              <h4 className="text-purple-300 font-medium text-sm mb-2">
                <Layers className="inline w-4 h-4 mr-1" />
                Region Layering
              </h4>
              <div className="flex gap-2">
                <button
                  onClick={() => onCreateLayer(region, 'sector')}
                  disabled={hasSectorLayer}
                  className={`flex-1 text-white text-xs py-2 px-3 rounded ${
                    hasSectorLayer 
                      ? 'bg-gray-600 cursor-not-allowed opacity-50' 
                      : 'bg-amber-600 hover:bg-amber-700'
                  }`}
                  title={hasSectorLayer ? 'A sector layer already exists for this region' : 'Add a sector override layer'}
                >
                  {hasSectorLayer ? 'Sector Layer Exists' : 'Add Sector Layer'}
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

      {/* Coordinate Editor - made collapsible */}
      <div className="border-t border-gray-700 mt-3">
        <button
          onClick={() => toggleSection('coordinates')}
          className="w-full py-2 flex items-center justify-between text-gray-300 hover:bg-gray-800 transition-colors rounded"
        >
          <span className="text-sm font-medium flex items-center gap-1">
            Polygon Point Editor
          </span>
          {collapsedSections.has('coordinates') ? <ChevronRight className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        {!collapsedSections.has('coordinates') && (
          <div className="pt-2">
            <CoordinateEditor
              coordinates={region.coordinates}
              onChange={(newCoords) => onUpdate({ coordinates: newCoords })}
              minPoints={3}
            />
          </div>
        )}
      </div>
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

      {/* Hint generation note */}
      <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-2">
        <p className="text-blue-300 text-xs flex items-center gap-1">
          <Lightbulb className="w-3 h-3" />
          Hints will be automatically generated after creating a description
        </p>
      </div>
      
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

  const renderHintsTab = () => {
    const hintCategories = {
      atmosphere: { label: 'Atmosphere', icon: '🌫️', color: 'text-blue-400' },
      fauna: { label: 'Fauna', icon: '🦎', color: 'text-green-400' },
      flora: { label: 'Flora', icon: '🌿', color: 'text-emerald-400' },
      geography: { label: 'Geography', icon: '⛰️', color: 'text-amber-400' },
      weather_influence: { label: 'Weather', icon: '🌦️', color: 'text-cyan-400' },
      resources: { label: 'Resources', icon: '💎', color: 'text-purple-400' },
      landmarks: { label: 'Landmarks', icon: '🏛️', color: 'text-pink-400' },
      sounds: { label: 'Sounds', icon: '🔊', color: 'text-orange-400' },
      scents: { label: 'Scents', icon: '👃', color: 'text-rose-400' },
      seasonal_changes: { label: 'Seasonal', icon: '🍂', color: 'text-yellow-400' },
      time_of_day: { label: 'Time of Day', icon: '🌅', color: 'text-indigo-400' },
      mystical: { label: 'Mystical', icon: '✨', color: 'text-violet-400' }
    };

    // Group hints by category
    const hintsByCategory = hints.reduce((acc, hint) => {
      const category = hint.hint_category || 'uncategorized';
      if (!acc[category]) acc[category] = [];
      acc[category].push(hint);
      return acc;
    }, {} as Record<string, RegionHint[]>);

    // Filter by selected category
    const filteredCategories = selectedCategory === 'all' 
      ? Object.entries(hintsByCategory)
      : Object.entries(hintsByCategory).filter(([cat]) => cat === selectedCategory);

    return (
      <div className="space-y-3">
        {/* Header with generate button */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-medium text-gray-300">Region Hints</h3>
            <span className="text-xs text-gray-500">({hints.length} total)</span>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Category filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="text-xs bg-gray-800 border border-gray-600 rounded px-2 py-1"
            >
              <option value="all">All Categories</option>
              {Object.entries(hintCategories).map(([key, cat]) => (
                <option key={key} value={key}>{cat.label}</option>
              ))}
            </select>

            {/* Generate button */}
            {region.region_description && (
              <button
                onClick={() => {
                  // Log the current description to help debug
                  console.log('[Hints] Starting hint generation with description:', region.region_description?.substring(0, 100));
                  generateHintsFromDescription();
                }}
                disabled={hintsLoading}
                className="text-xs bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-3 py-1 rounded flex items-center gap-1"
                title={hints.length > 0 ? 'This will replace existing hints' : 'Generate hints from description'}
              >
                {hintsLoading ? (
                  <>Generating...</>
                ) : (
                  <>
                    <Plus className="w-3 h-3" />
                    {hints.length > 0 ? 'Regenerate Hints' : 'Generate Hints'}
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Error message */}
        {hintsError && (
          <div className="bg-red-900/20 border border-red-800 rounded-lg p-2">
            <p className="text-red-300 text-xs">{hintsError}</p>
          </div>
        )}

        {/* Loading state */}
        {hintsLoading && hints.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-400 text-sm">Loading hints...</p>
          </div>
        )}

        {/* No hints message */}
        {!hintsLoading && hints.length === 0 && (
          <div className="bg-gray-800 rounded-lg p-4 text-center">
            <Lightbulb className="w-8 h-8 text-gray-600 mx-auto mb-2" />
            <p className="text-gray-400 text-sm mb-2">No hints found for this region</p>
            {region.region_description ? (
              <p className="text-gray-500 text-xs">
                Click "Generate from Description" to create hints from the region's description
              </p>
            ) : (
              <p className="text-gray-500 text-xs">
                Add a description to this region first, then generate hints
              </p>
            )}
          </div>
        )}

        {/* Hints list grouped by category */}
        {filteredCategories.length > 0 && (
          <div className="space-y-2">
            {filteredCategories.map(([category, categoryHints]) => {
              const catInfo = hintCategories[category as keyof typeof hintCategories] || 
                { label: category, icon: '❓', color: 'text-gray-400' };
              const isExpanded = expandedCategories.has(category);

              return (
                <div key={category} className="bg-gray-800 rounded-lg overflow-hidden">
                  {/* Category header */}
                  <button
                    onClick={() => toggleCategory(category)}
                    className="w-full px-3 py-2 flex items-center justify-between hover:bg-gray-700 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <span>{catInfo.icon}</span>
                      <span className={`text-sm font-medium ${catInfo.color}`}>
                        {catInfo.label}
                      </span>
                      <span className="text-xs text-gray-500">
                        ({categoryHints.length})
                      </span>
                    </div>
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    )}
                  </button>

                  {/* Hints in this category */}
                  {isExpanded && (
                    <div className="border-t border-gray-700 p-2 space-y-1">
                      {categoryHints.map((hint) => (
                        <div key={hint.id} className="bg-gray-900 rounded p-2">
                          <p className="text-xs text-gray-300 leading-relaxed">
                            {hint.hint_text}
                          </p>
                          <div className="flex items-center gap-3 mt-1">
                            <span className="text-xs text-gray-500">
                              Priority: {hint.priority}/10
                            </span>
                            {hint.seasonal_weight && (
                              <span className="text-xs text-gray-500">
                                🍂 Seasonal
                              </span>
                            )}
                            {hint.time_of_day_weight && (
                              <span className="text-xs text-gray-500">
                                🌅 Time-based
                              </span>
                            )}
                            {hint.weather_conditions && hint.weather_conditions !== 'clear,cloudy,rainy,stormy,lightning' && (
                              <span className="text-xs text-gray-500">
                                🌦️ Weather-specific
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };

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
        
        // Automatically generate hints from the new description
        // Use setTimeout to allow the UI to update first
        setTimeout(() => {
          generateHintsFromDescription(result.generated_description, false);
        }, 500);
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
          {activeTab === 'hints' && renderHintsTab()}
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