import { Region, Path, Coordinate } from '../types';
import { ChatAction } from './chatAPI';

// Type definitions for useEditor hook functions
interface EditorHook {
  regions: Region[];
  paths: Path[];
  setRegions: (updater: (prev: Region[]) => Region[]) => void;
  setPaths: (updater: (prev: Path[]) => Path[]) => void;
  setUnsavedItems: (updater: (prev: Set<string>) => Set<string>) => void;
  updateSelectedItem: (updates: Partial<Region | Path>) => void;
  selectItem: (item: Region | Path | null) => void;
  setState: (updater: (prev: Record<string, unknown>) => Record<string, unknown>) => void;
}

interface ChatBridgeOptions {
  onStatusUpdate?: (message: string) => void;
  onError?: (error: string) => void;
}

export class ChatBridge {
  private editor: EditorHook;
  private options: ChatBridgeOptions;

  constructor(editor: EditorHook, options: ChatBridgeOptions = {}) {
    this.editor = editor;
    this.options = options;
  }

  async executeAction(action: ChatAction): Promise<void> {
    try {
      console.log('[ChatBridge] Executing action:', action.type, action.params);
      
      // Validate action structure
      if (!action || !action.type) {
        throw new Error('Invalid action: missing type');
      }
      
      if (!action.params || typeof action.params !== 'object') {
        throw new Error(`Invalid action params for ${action.type}`);
      }
      
      switch (action.type) {
        case 'create_region':
          await this.createRegion(action.params, action.ui_hints);
          break;
          
        case 'create_path':
          await this.createPath(action.params, action.ui_hints);
          break;
          
        case 'stage_description':
          await this.stageDescription(action.params);
          break;
          
        case 'stage_hints':
          await this.stageHints(action.params);
          break;
          
        case 'select_item':
          await this.selectItem(action.params);
          break;
          
        case 'center_view':
          await this.centerView(action.params);
          break;
          
        default:
          console.warn('[ChatBridge] Unknown action type:', action.type);
          this.options.onError?.(`Unknown action: ${action.type}`);
      }
    } catch (error) {
      console.error('[ChatBridge] Failed to execute action:', error);
      console.error('[ChatBridge] Action details:', { type: action?.type, params: action?.params });
      const errorMessage = error instanceof Error ? error.message : String(error);
      this.options.onError?.(`Failed to execute ${action?.type || 'unknown'}: ${errorMessage}`);
      throw error; // Re-throw to be caught by calling component
    }
  }

  private async createRegion(params: Record<string, unknown>, uiHints?: Record<string, unknown>): Promise<void> {
    // Generate a unique vnum for the new region
    const vnum = this.generateRegionVnum();
    
    // Create the region object
    const newRegion: Region = {
      vnum,
      zone_vnum: params.zone_vnum || 10000,
      name: params.name || 'Unnamed Region',
      region_type: params.region_type || 1,
      coordinates: this.parseCoordinates(params.coordinates),
      region_props: params.region_props || 0,
      region_reset_data: params.region_reset_data,
      
      // Mark as dirty (created by chat but not saved)
      isDirty: true,
      
      // Add metadata to indicate this was created by AI
      ai_agent_source: 'chat_assistant',
      
      // Add description if provided
      region_description: params.description,
      
      // Frontend-specific properties
      id: `region-${vnum}`,
      color: params.color || this.getDefaultRegionColor(params.region_type || 1)
    };

    // Add to regions state
    this.editor.setRegions(prev => [...prev, newRegion]);
    
    // Mark as unsaved
    this.editor.setUnsavedItems(prev => new Set(prev).add(vnum.toString()));
    
    // Apply UI hints
    if (uiHints?.select) {
      this.editor.selectItem(newRegion);
    }
    
    if (uiHints?.center_map) {
      this.centerOnCoordinates(newRegion.coordinates);
    }
    
    this.options.onStatusUpdate?.(
      `Created region "${newRegion.name}" (not saved yet - click Save to persist)`
    );
    
    console.log('[ChatBridge] Region created:', newRegion);
  }

  private async createPath(params: Record<string, unknown>, uiHints?: Record<string, unknown>): Promise<void> {
    // Generate a unique vnum for the new path
    const vnum = this.generatePathVnum();
    
    // Create the path object
    const newPath: Path = {
      vnum,
      zone_vnum: params.zone_vnum || 10000,
      name: params.name || 'Unnamed Path',
      path_type: params.path_type || 1,
      coordinates: this.parseCoordinates(params.coordinates),
      path_props: params.path_props || 0,
      
      // Mark as dirty (created by chat but not saved)
      isDirty: true,
      
      // Frontend-specific properties
      id: `path-${vnum}`,
      color: params.color || this.getDefaultPathColor(params.path_type || 1)
    };

    // Add to paths state
    this.editor.setPaths(prev => [...prev, newPath]);
    
    // Mark as unsaved
    this.editor.setUnsavedItems(prev => new Set(prev).add(vnum.toString()));
    
    // Apply UI hints
    if (uiHints?.select) {
      this.editor.selectItem(newPath);
    }
    
    if (uiHints?.center_map) {
      this.centerOnCoordinates(newPath.coordinates);
    }
    
    this.options.onStatusUpdate?.(
      `Created path "${newPath.name}" (not saved yet - click Save to persist)`
    );
    
    console.log('[ChatBridge] Path created:', newPath);
  }

  private async stageDescription(params: Record<string, unknown>): Promise<void> {
    // Find the region by vnum
    const region = this.editor.regions.find(r => r.vnum === params.vnum);
    if (!region) {
      throw new Error(`Region with vnum ${params.vnum} not found`);
    }

    // Update the region with staged description
    this.editor.updateSelectedItem({
      region_description: params.description,
      description_style: params.style || 'immersive',
      description_length: params.length || 'medium',
      ai_agent_source: 'chat_assistant'
    });
    
    this.options.onStatusUpdate?.(
      `Description staged for "${region.name}" (click Save to persist)`
    );
  }

  private async stageHints(params: Record<string, unknown>): Promise<void> {
    // Find the region by vnum
    const region = this.editor.regions.find(r => r.vnum === params.vnum);
    if (!region) {
      throw new Error(`Region with vnum ${params.vnum} not found`);
    }

    // Stage hints using the same pattern as the RegionTabbedPanel
    this.editor.updateSelectedItem({
      _hintsStaged: true,
      _stagedHints: params.hints
    });
    
    this.options.onStatusUpdate?.(
      `${params.hints.length} hints staged for "${region.name}" (click Save to persist)`
    );
  }

  private async selectItem(params: Record<string, unknown>): Promise<void> {
    let item: Region | Path | null = null;
    
    if (params.vnum) {
      // Find by vnum in regions or paths
      item = this.editor.regions.find(r => r.vnum === params.vnum) ||
             this.editor.paths.find(p => p.vnum === params.vnum) ||
             null;
    }
    
    this.editor.selectItem(item);
    
    if (item) {
      this.options.onStatusUpdate?.(
        `Selected ${('region_type' in item) ? 'region' : 'path'} "${item.name}"`
      );
    }
  }

  private async centerView(params: Record<string, unknown>): Promise<void> {
    if (params.coordinates) {
      this.centerOnCoordinates(this.parseCoordinates(params.coordinates));
    } else if (params.vnum) {
      const item = this.editor.regions.find(r => r.vnum === params.vnum) ||
                   this.editor.paths.find(p => p.vnum === params.vnum);
      if (item) {
        this.centerOnCoordinates(item.coordinates);
      }
    }
  }

  private parseCoordinates(coords: unknown): Coordinate[] {
    if (Array.isArray(coords)) {
      return coords.map((coord, index) => {
        if (!coord || typeof coord !== 'object') {
          console.warn(`[ChatBridge] Invalid coordinate at index ${index}:`, coord);
          return { x: 0, y: 0 };
        }
        
        const x = typeof coord.x === 'number' ? coord.x : parseFloat(coord.x || '0');
        const y = typeof coord.y === 'number' ? coord.y : parseFloat(coord.y || '0');
        
        if (isNaN(x) || isNaN(y)) {
          console.warn(`[ChatBridge] NaN coordinates at index ${index}:`, { x: coord.x, y: coord.y });
          return { x: 0, y: 0 };
        }
        
        return { x, y };
      });
    }
    console.warn('[ChatBridge] Expected array of coordinates, got:', typeof coords, coords);
    return [];
  }

  private centerOnCoordinates(coordinates: Coordinate[]): void {
    if (coordinates.length === 0) return;
    
    // Calculate center point
    const centerX = coordinates.reduce((sum, coord) => sum + coord.x, 0) / coordinates.length;
    const centerY = coordinates.reduce((sum, coord) => sum + coord.y, 0) / coordinates.length;
    
    // For now, just log the centering - we'll need to implement proper view centering later
    // The EditorState doesn't have a viewCenter field, so we'll skip this for now
    console.log('[ChatBridge] Would center view on:', { x: centerX, y: centerY });
    
    // TODO: Implement proper view centering through the canvas component
    // this.editor.setState((prev) => ({
    //   ...prev,
    //   viewCenter: { x: centerX, y: centerY }
    // }));
  }

  private generateRegionVnum(): number {
    // Generate a vnum in the 1000000+ range (same as chat agent)
    const existingVnums = this.editor.regions.map(r => r.vnum);
    let vnum = 1000000 + Math.floor(Math.random() * 99999);
    
    // Ensure uniqueness
    while (existingVnums.includes(vnum)) {
      vnum = 1000000 + Math.floor(Math.random() * 99999);
    }
    
    return vnum;
  }

  private generatePathVnum(): number {
    // Generate a vnum in the 2000000+ range (same as chat agent)
    const existingVnums = this.editor.paths.map(p => p.vnum);
    let vnum = 2000000 + Math.floor(Math.random() * 99999);
    
    // Ensure uniqueness
    while (existingVnums.includes(vnum)) {
      vnum = 2000000 + Math.floor(Math.random() * 99999);
    }
    
    return vnum;
  }

  private getDefaultRegionColor(regionType: number): string {
    const colors = {
      1: '#3B82F6', // Geographic - blue
      2: '#EF4444', // Encounter - red  
      3: '#8B5CF6', // Transform - purple
      4: '#F59E0B'  // Sector - amber
    };
    return colors[regionType as keyof typeof colors] || '#6B7280';
  }

  private getDefaultPathColor(pathType: number): string {
    const colors = {
      1: '#6B7280', // Paved - gray
      2: '#92400E', // Dirt - brown
      3: '#065F46', // Geographic - green
      5: '#1E40AF', // River - blue
      6: '#3B82F6'  // Stream - light blue
    };
    return colors[pathType as keyof typeof colors] || '#6B7280';
  }
}