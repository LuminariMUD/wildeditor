import { useState, useCallback, useEffect } from 'react';
import { useAuth } from './useAuth';
import { apiClient } from '../services/api';
import { EditorState, DrawingTool, Coordinate, Region, Path } from '../types';

const initialState: EditorState = {
  tool: 'select',
  zoom: 100,
  selectedItem: null,
  isDrawing: false,
  currentDrawing: [],
  showGrid: true,
  showRegions: true,
  showPaths: true,
  showBackground: true,
  showAxes: true,
  showOrigin: true,
  mousePosition: { x: 0, y: 0 }
};

export const useEditor = () => {
  const { session } = useAuth();
  const [state, setState] = useState<EditorState>(initialState);
  const [regions, setRegions] = useState<Region[]>([]);
  const [paths, setPaths] = useState<Path[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [centerOnCoordinate, setCenterOnCoordinate] = useState<Coordinate | null>(null);
  const [hiddenRegions, setHiddenRegions] = useState<Set<number>>(new Set());
  const [hiddenPaths, setHiddenPaths] = useState<Set<number>>(new Set());
  const [hiddenFolders, setHiddenFolders] = useState<Set<string>>(new Set());
  
  // Track unsaved changes for buffering
  const [unsavedItems, setUnsavedItems] = useState<Set<string>>(new Set());
  const [savingItems, setSavingItems] = useState<Set<string>>(new Set());

  // Check if auth is disabled (for development mode)
  const authDisabled = import.meta.env.VITE_DISABLE_AUTH === 'true';

  // Set API token when session changes (only if auth is enabled)
  useEffect(() => {
    if (!authDisabled && session?.access_token) {
      apiClient.setToken(session.access_token);
    }
  }, [session, authDisabled]);

  // Load data from API
  const loadData = useCallback(async () => {
    console.log('[Editor] Starting data load, authDisabled:', authDisabled, 'session:', !!session?.access_token);
    
    // Skip auth check if auth is disabled or if we have a valid session
    if (!authDisabled && !session?.access_token) {
      console.log('[Editor] Skipping data load - no session and auth not disabled');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // First test the health endpoint
      console.log('[Editor] Testing health endpoint...');
      const health = await apiClient.healthCheck();
      console.log('[Editor] Health check successful:', health);
      
      console.log('[Editor] Making data API calls...');
      const [regionsData, pathsData] = await Promise.all([
        apiClient.getRegions(),
        apiClient.getPaths()
      ]);
      
      console.log('[Editor] API calls successful:', {
        regions: regionsData.length,
        paths: pathsData.length
      });
      
      // Check for duplicate IDs
      const regionIds = regionsData.map((r: Region) => r.id);
      const uniqueRegionIds = new Set(regionIds);
      if (regionIds.length !== uniqueRegionIds.size) {
        console.warn('[Editor] Duplicate region IDs detected!', {
          total: regionIds.length,
          unique: uniqueRegionIds.size,
          duplicates: regionIds.filter((id, index) => regionIds.indexOf(id) !== index)
        });
      }
      
      const pathIds = pathsData.map(p => p.id);
      const uniquePathIds = new Set(pathIds);
      if (pathIds.length !== uniquePathIds.size) {
        console.warn('[Editor] Duplicate path IDs detected!', {
          total: pathIds.length,
          unique: uniquePathIds.size,
          duplicates: pathIds.filter((id, index) => pathIds.indexOf(id) !== index)
        });
      }
      
      setRegions(regionsData);
      setPaths(pathsData);
    } catch (err) {
      console.error('Failed to load data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
      
      // Clear data on error - no more fallback mock data
      setRegions([]);
      setPaths([]);
    } finally {
      setLoading(false);
    }
  }, [session, authDisabled]);

  // Load data when session is available or immediately if auth is disabled
  useEffect(() => {
    loadData();
  }, [loadData]);

  const setTool = useCallback((tool: DrawingTool) => {
    console.log('[Drawing] Tool change:', state.tool, '->', tool);
    setState(prev => {
      // If we're currently drawing and switching tools, we need to clean up
      if (prev.isDrawing) {
        console.warn('[Drawing] Tool changed while drawing, canceling current drawing:', {
          previousTool: prev.tool,
          newTool: tool,
          pointsDrawn: prev.currentDrawing.length
        });
      }
      
      return { 
        ...prev, 
        tool, 
        isDrawing: false, 
        currentDrawing: [],
        // Clear selection when switching to non-select tools
        selectedItem: tool === 'select' ? prev.selectedItem : null
      };
    });
  }, [state.tool]);

  const setZoom = useCallback((zoom: number) => {
    setState(prev => ({ ...prev, zoom }));
  }, []);

  const setMousePosition = useCallback((coordinate: Coordinate) => {
    setState(prev => ({ ...prev, mousePosition: coordinate }));
  }, []);

  const toggleLayer = useCallback((layer: 'grid' | 'regions' | 'paths' | 'background' | 'axes' | 'origin') => {
    setState(prev => ({ 
      ...prev, 
      [`show${layer.charAt(0).toUpperCase() + layer.slice(1)}`]: 
        !prev[`show${layer.charAt(0).toUpperCase() + layer.slice(1)}` as keyof EditorState] 
    }));
  }, []);

  const toggleItemVisibility = useCallback((type: 'region' | 'path', vnum: number) => {
    if (type === 'region') {
      setHiddenRegions(prev => {
        const newSet = new Set(prev);
        if (newSet.has(vnum)) {
          newSet.delete(vnum);
        } else {
          newSet.add(vnum);
        }
        return newSet;
      });
    } else if (type === 'path') {
      setHiddenPaths(prev => {
        const newSet = new Set(prev);
        if (newSet.has(vnum)) {
          newSet.delete(vnum);
        } else {
          newSet.add(vnum);
        }
        return newSet;
      });
    }
  }, []);

  const toggleFolderVisibility = useCallback((folderId: string) => {
    setHiddenFolders(prev => {
      const newSet = new Set(prev);
      if (newSet.has(folderId)) {
        newSet.delete(folderId);
      } else {
        newSet.add(folderId);
      }
      return newSet;
    });
  }, []);

  // Check if an item should be hidden due to folder visibility
  const isItemHiddenByFolder = useCallback((item: Region | Path) => {
    if ('region_type' in item) {
      // This is a region
      const region = item as Region;
      const regionTypeFolderId = `region-type-${region.region_type}`;
      return hiddenFolders.has('regions') || hiddenFolders.has(regionTypeFolderId);
    } else if ('path_type' in item) {
      // This is a path
      const path = item as Path;
      const pathTypeFolderId = `path-type-${path.path_type}`;
      return hiddenFolders.has('paths') || hiddenFolders.has(pathTypeFolderId);
    }
    return false;
  }, [hiddenFolders]);

  const selectItem = useCallback(async (item: Region | Path | null) => {
    if (item) {
      console.log('[Selection] Item selected:', {
        type: 'coordinates' in item ? ('vnum' in item ? 'region/path' : 'unknown') : 'point',
        id: item.id,
        name: 'name' in item ? item.name : 'unknown'
      });
      
      // If it's a region, fetch full details including description
      if (item && 'region_type' in item && item.id) {
        try {
          console.log('[Selection] Fetching full region details for:', item.id);
          const fullRegion = await apiClient.getRegion(item.id);
          console.log('[Selection] Full region data loaded:', {
            vnum: fullRegion.vnum,
            has_description: !!fullRegion.region_description,
            description_length: fullRegion.region_description?.length
          });
          setState(prev => ({ ...prev, selectedItem: fullRegion }));
          
          // Also update the region in the regions array
          setRegions(prev => prev.map(r => 
            r.vnum === fullRegion.vnum ? fullRegion : r
          ));
        } catch (error) {
          console.error('[Selection] Failed to fetch full region details:', error);
          // Fall back to setting the item as-is
          setState(prev => ({ ...prev, selectedItem: item }));
        }
      } else {
        // For paths and other items, just set directly
        setState(prev => ({ ...prev, selectedItem: item }));
      }
    } else {
      console.log('[Selection] Selection cleared');
      setState(prev => ({ ...prev, selectedItem: null }));
    }
  }, []);

  const handleCanvasClick = useCallback((coordinate: Coordinate) => {
    console.log('[Drawing] Canvas click:', {
      tool: state.tool,
      coordinate,
      isDrawing: state.isDrawing,
      currentPoints: state.currentDrawing.length
    });
    
    // Validate coordinate bounds
    if (coordinate.x < -1024 || coordinate.x > 1024 || coordinate.y < -1024 || coordinate.y > 1024) {
      console.error('[Drawing] Coordinate out of bounds:', {
        coordinate,
        validRange: { min: -1024, max: 1024 }
      });
      setError('Coordinate out of valid range (-1024 to 1024)');
      return;
    }

    if (state.tool === 'landmark') {
      // Create a landmark as a small geographic region around the point
      const landmarkRegion: Region = {
        vnum: Date.now(), // Will be replaced by backend
        zone_vnum: 1,
        name: `New Landmark ${regions.length + 1}`,
        region_type: 1, // Geographic
        coordinates: [
          { x: coordinate.x - 0.2, y: coordinate.y - 0.2 }, // Small 0.4x0.4 square around the point
          { x: coordinate.x + 0.2, y: coordinate.y - 0.2 },
          { x: coordinate.x + 0.2, y: coordinate.y + 0.2 },
          { x: coordinate.x - 0.2, y: coordinate.y + 0.2 }
        ],
        region_props: 0, // Geographic regions ignore this value
        id: `region-${Date.now()}`,
        props: '{}',
        color: '#3B82F6', // Geographic blue
        isDirty: true
      };
      
      console.log('[Drawing] Creating new landmark region:', {
        vnum: landmarkRegion.vnum,
        centerCoordinate: coordinate,
        name: landmarkRegion.name
      });
      
      // Add to regions state immediately (buffered)
      setRegions(prev => [...prev, landmarkRegion]);
      selectItem(landmarkRegion);
      
      // Mark as unsaved
      setUnsavedItems(prev => new Set(prev).add(landmarkRegion.vnum.toString()));
      
      console.log('[Drawing] Landmark region created locally, marked as unsaved');
    } else if (state.tool === 'region' || state.tool === 'path') {
      const newPointCount = state.currentDrawing.length + 1;
      console.log('[Drawing] Adding point to', state.tool, ':', {
        pointNumber: newPointCount,
        coordinate,
        requiredPoints: state.tool === 'region' ? 3 : 2
      });
      
      setState(prev => ({
        ...prev,
        isDrawing: true,
        currentDrawing: [...prev.currentDrawing, coordinate]
      }));
    }
  }, [state.tool, state.isDrawing, state.currentDrawing.length, regions.length, selectItem]);

  const cancelDrawing = useCallback(() => {
    console.log('[Drawing] Canceling drawing:', {
      tool: state.tool,
      pointsDrawn: state.currentDrawing.length
    });
    setState(prev => ({ ...prev, isDrawing: false, currentDrawing: [] }));
    setError(null); // Clear any drawing-related errors
  }, [state.tool, state.currentDrawing.length]);
  
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const finishDrawing = useCallback(() => {
    console.log('[Drawing] Attempting to finish drawing:', {
      tool: state.tool,
      isDrawing: state.isDrawing,
      pointsDrawn: state.currentDrawing.length,
      coordinates: state.currentDrawing
    });
    
    if (!state.isDrawing) {
      console.error('[Drawing] finishDrawing called but not currently drawing');
      return;
    }

    // Validate minimum points for each shape type
    const minPointsForTool = {
      region: 3,
      path: 2
    };

    const minPoints = minPointsForTool[state.tool as keyof typeof minPointsForTool];
    
    if (state.currentDrawing.length < minPoints) {
      const errorMsg = `${state.tool === 'region' ? 'Region' : 'Path'} requires at least ${minPoints} points`;
      console.error('[Drawing] Not enough points:', {
        tool: state.tool,
        currentPoints: state.currentDrawing.length,
        requiredPoints: minPoints
      });
      setError(errorMsg);
      return;
    }

    // Clear any previous errors
    setError(null);

    if (state.tool === 'region' && state.currentDrawing.length >= 3) {
      const newRegion: Region = {
        vnum: Math.max(1000, ...regions.map(r => r.vnum || 0)) + 1, // Generate next vnum
        zone_vnum: 1,
        name: `New Region ${regions.length + 1}`,
        region_type: 1, // Geographic region
        coordinates: [...state.currentDrawing], // Create a copy to avoid reference issues
        region_props: 0, // Geographic regions ignore this value
        region_reset_data: "",
        region_reset_time: null,
        
        // Frontend compatibility fields
        id: Date.now().toString(),
        props: '{"description": "Custom region"}', // compatibility
        color: '#F59E0B',
        isDirty: true  // Mark as unsaved
      };
      
      console.log('[Drawing] Creating new region:', {
        id: newRegion.id,
        vnum: newRegion.vnum,
        points: newRegion.coordinates.length,
        type: newRegion.region_type
      });
      
      // Add to local state immediately (buffered)
      setRegions(prev => [...prev, newRegion]);
      selectItem(newRegion);
      
      // Mark as unsaved
      setUnsavedItems(prev => new Set(prev).add(newRegion.vnum.toString()));
      
      console.log('[Drawing] Region created locally, marked as unsaved');
    } else if (state.tool === 'path' && state.currentDrawing.length >= 2) {
      const newPath: Path = {
        vnum: Math.max(2000, ...paths.map(p => p.vnum || 0)) + 1, // Generate next vnum
        zone_vnum: 1,
        name: `New Path ${paths.length + 1}`,
        path_type: 1, // Paved Road
        coordinates: [...state.currentDrawing], // Create a copy to avoid reference issues
        path_props: 11, // Default to Road North-South sector
        
        // Frontend compatibility fields
        id: Date.now().toString(),
        type: 0, // compatibility (0=Road)
        props: '{"width": "wide", "condition": "excellent"}', // compatibility
        color: '#EC4899',
        isDirty: true  // Mark as unsaved
      };
      
      console.log('[Drawing] Creating new path:', {
        id: newPath.id,
        vnum: newPath.vnum,
        points: newPath.coordinates.length,
        type: newPath.type
      });
      
      // Add to local state immediately (buffered)
      setPaths(prev => [...prev, newPath]);
      selectItem(newPath);
      
      // Mark as unsaved
      setUnsavedItems(prev => new Set(prev).add(newPath.vnum.toString()));
      
      console.log('[Drawing] Path created locally, marked as unsaved');
    }
    
    // Always clean up drawing state after processing
    console.log('[Drawing] Cleaning up drawing state');
    setState(prev => ({ ...prev, isDrawing: false, currentDrawing: [] }));
  }, [state.isDrawing, state.currentDrawing, state.tool, regions, paths, selectItem]);

  const updateSelectedItem = useCallback((updates: Partial<Region | Path>) => {
    if (!state.selectedItem) {
      console.warn('[Update] No item selected to update');
      return;
    }
    
    console.log('[Update] Updating selected item:', {
      updates: Object.keys(updates)
    });

    // Get the item ID - use vnum for regions/paths, or id for points
    let itemId: string;
    if ('vnum' in state.selectedItem) {
      itemId = state.selectedItem.vnum?.toString() || state.selectedItem.id || '';
    } else {
      // This should not happen since we only have Region/Path items with vnums
      console.error('[Update] Selected item has no vnum or id');
      return;
    }
    
    if (!itemId) {
      console.error('[Update] No valid ID found for selected item');
      return;
    }
    
    // Add isDirty flag to updates
    const updatesWithDirty = { ...updates, isDirty: true };
    
    if ('coordinates' in state.selectedItem) {
      if ('region_type' in state.selectedItem) {
        // It's a Region
        setRegions(prev => prev.map(region => 
          (region.vnum?.toString() === itemId || region.id === itemId)
            ? { ...region, ...updatesWithDirty } as Region
            : region
        ));
      } else if ('path_type' in state.selectedItem) {
        // It's a Path
        setPaths(prev => prev.map(path => 
          (path.vnum?.toString() === itemId || path.id === itemId)
            ? { ...path, ...updatesWithDirty } as Path
            : path
        ));
      }
    }
    
    // Mark as unsaved
    setUnsavedItems(prev => new Set(prev).add(itemId));
    
    // Update selected item state
    setState(prev => ({ ...prev, selectedItem: { ...prev.selectedItem!, ...updatesWithDirty } as Region | Path }));
    
    console.log('[Update] Item updated locally, marked as unsaved:', itemId);
  }, [state.selectedItem]);

  // Save a specific item to the API
  const saveItem = useCallback(async (itemId: string) => {
    if (savingItems.has(itemId)) {
      console.warn('[Save] Item is already being saved:', itemId);
      return;
    }

    // Check if auth is available
    if (!authDisabled && !session?.access_token) {
      console.warn('[Save] No auth token available, cannot save');
      setError('Authentication required to save changes');
      return;
    }

    setSavingItems(prev => new Set(prev).add(itemId));
    
    try {
      // Find the item in our local state
      let item: Region | Path | undefined;
      
      // Check regions first
      item = regions.find(r => r.id === itemId || r.vnum?.toString() === itemId);
      if (item && 'region_type' in item) {
        const region = item as Region;
        
        // Check if region exists in database by trying to fetch it
        let existsInDatabase = false;
        if (region.vnum && region.vnum > 0) {
          try {
            await apiClient.getRegion(region.vnum.toString());
            existsInDatabase = true;
            console.log('[Save] Region exists in database, will update:', region.vnum);
          } catch (error) {
            if (error instanceof Error && (error.message.includes('404') || error.message.includes('not found'))) {
              existsInDatabase = false;
              console.log('[Save] Region not found in database, will create:', region.vnum);
            } else {
              // Re-throw other errors (network, auth, etc.)
              throw error;
            }
          }
        }
        
        if (existsInDatabase) {
          // Update existing region (exists in database)
          const regionId = region.id || region.vnum.toString();
          await apiClient.updateRegion(regionId, region);
          console.log('[Save] Region updated successfully:', itemId);
          
          // Save staged hints if present
          if (region._hintsStaged && region._stagedHints) {
            try {
              // Delete existing hints first
              await apiClient.deleteAllHints(region.vnum);
              // Save staged hints
              await apiClient.createHints(region.vnum, region._stagedHints);
              console.log(`[Save] Saved ${region._stagedHints.length} staged hints`);
            } catch (error) {
              console.error('[Save] Failed to save staged hints:', error);
            }
          }
        } else {
          // Create new region (doesn't exist in database)
          const createdRegion = await apiClient.createRegion(region);
          console.log('[Save] Region created successfully:', itemId);
          
          // Save staged hints if present (after creation)
          if (region._hintsStaged && region._stagedHints) {
            try {
              await apiClient.createHints(createdRegion.vnum, region._stagedHints);
              console.log(`[Save] Saved ${region._stagedHints.length} staged hints for new region`);
            } catch (error) {
              console.error('[Save] Failed to save staged hints for new region:', error);
            }
          }
          
          // Remove from unsaved items before updating state
          setUnsavedItems(prev => {
            const newSet = new Set(prev);
            newSet.delete(itemId);
            return newSet;
          });
          
          // Update the local region with the server response (including new vnum)
          setRegions(prev => prev.map(r => 
            (r.id === itemId || r.vnum?.toString() === itemId) 
              ? { ...createdRegion, isDirty: false } 
              : r
          ));
          
          // Update selected item if it's the one we just saved
          if (state.selectedItem && 
              ((state.selectedItem.id === itemId) || 
               ('vnum' in state.selectedItem && state.selectedItem.vnum?.toString() === itemId))) {
            setState(prev => ({ 
              ...prev, 
              selectedItem: prev.selectedItem ? { ...prev.selectedItem, isDirty: false } : null 
            }));
          }
          
          return; // Early return since we already updated the region state
        }
        
        // Mark as clean (for update case)
        setRegions(prev => prev.map(r => 
          (r.id === itemId || r.vnum?.toString() === itemId) 
            ? { ...r, isDirty: false } 
            : r
        ));
      }
      
      // Check paths if not found in regions
      if (!item) {
        item = paths.find(p => p.id === itemId || p.vnum?.toString() === itemId);
        if (item && 'path_type' in item) {
          const path = item as Path;
          
          // Check if path exists in database by trying to fetch it
          let existsInDatabase = false;
          if (path.vnum && path.vnum > 0) {
            try {
              await apiClient.getPath(path.vnum.toString());
              existsInDatabase = true;
              console.log('[Save] Path exists in database, will update:', path.vnum);
            } catch (error) {
              if (error instanceof Error && (error.message.includes('404') || error.message.includes('not found'))) {
                existsInDatabase = false;
                console.log('[Save] Path not found in database, will create:', path.vnum);
              } else {
                // Re-throw other errors (network, auth, etc.)
                throw error;
              }
            }
          }
          
          if (existsInDatabase) {
            // Update existing path (exists in database)
            const pathId = path.id || path.vnum.toString();
            await apiClient.updatePath(pathId, path);
            console.log('[Save] Path updated successfully:', itemId);
          } else {
            // Create new path (doesn't exist in database)
            const createdPath = await apiClient.createPath(path);
            console.log('[Save] Path created successfully:', itemId);
            
            // Remove from unsaved items before updating state
            setUnsavedItems(prev => {
              const newSet = new Set(prev);
              newSet.delete(itemId);
              return newSet;
            });
            
            // Update the local path with the server response (including new vnum)
            setPaths(prev => prev.map(p => 
              (p.id === itemId || p.vnum?.toString() === itemId) 
                ? { ...createdPath, isDirty: false } 
                : p
            ));
            
            // Update selected item if it's the one we just saved
            if (state.selectedItem && 
                ((state.selectedItem.id === itemId) || 
                 ('vnum' in state.selectedItem && state.selectedItem.vnum?.toString() === itemId))) {
              setState(prev => ({ 
                ...prev, 
                selectedItem: prev.selectedItem ? { ...prev.selectedItem, isDirty: false } : null 
              }));
            }
            
            return; // Early return since we already updated the path state
          }
          
          // Mark as clean (for update case)
          setPaths(prev => prev.map(p => 
            (p.id === itemId || p.vnum?.toString() === itemId) 
              ? { ...p, isDirty: false } 
              : p
          ));
        }
      }
      
      if (!item) {
        console.error('[Save] Item not found:', itemId);
        setError('Item not found for saving');
        return;
      }
      
      // Remove from unsaved items
      setUnsavedItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(itemId);
        return newSet;
      });
      
      // Update selected item if it's the one we just saved
      if (state.selectedItem && 
          ((state.selectedItem.id === itemId) || 
           ('vnum' in state.selectedItem && state.selectedItem.vnum?.toString() === itemId))) {
        setState(prev => ({ 
          ...prev, 
          selectedItem: prev.selectedItem ? { ...prev.selectedItem, isDirty: false } : null 
        }));
      }
      
    } catch (err: unknown) {
      console.error('[Save] Failed to save item:', {
        error: err,
        itemId,
        message: err instanceof Error ? err.message : 'Unknown error'
      });
      setError('Failed to save item: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setSavingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(itemId);
        return newSet;
      });
    }
  }, [authDisabled, session, savingItems, regions, paths, state.selectedItem]);

  // Save all unsaved items
  const saveAllUnsaved = useCallback(async () => {
    if (unsavedItems.size === 0) {
      console.log('[Save] No unsaved items to save');
      return;
    }

    console.log('[Save] Saving all unsaved items:', Array.from(unsavedItems));
    
    for (const itemId of unsavedItems) {
      await saveItem(itemId);
    }
  }, [unsavedItems, saveItem]);

  // Discard unsaved changes for a specific item
  const discardItem = useCallback((itemId: string) => {
    console.log('[Discard] Discarding unsaved changes for item:', itemId);
    
    // Find the item in our local state
    let item: Region | Path | undefined;
    
    // Check regions first
    item = regions.find(r => r.id === itemId || r.vnum?.toString() === itemId);
    if (item && 'region_type' in item) {
      const region = item as Region;
      
      // If this is a completely new item (never saved), remove it entirely
      if (region.isDirty && !regions.some(r => r.vnum === region.vnum && !r.isDirty)) {
        console.log('[Discard] Removing new unsaved region:', itemId);
        setRegions(prev => prev.filter(r => r.id !== itemId && r.vnum?.toString() !== itemId));
        
        // Clear selection if this was the selected item
        if (state.selectedItem && (state.selectedItem.id === itemId || 
            ('vnum' in state.selectedItem && state.selectedItem.vnum?.toString() === itemId))) {
          setState(prev => ({ ...prev, selectedItem: null }));
        }
      } else {
        // If it's an existing item with changes, revert to clean state
        // (This would require storing original state - for now we'll just clear the dirty flag)
        console.log('[Discard] Marking region as clean (reverting changes):', itemId);
        setRegions(prev => prev.map(r => 
          (r.id === itemId || r.vnum?.toString() === itemId) 
            ? { 
                ...r, 
                isDirty: false,
                // Clear staged hints
                _hintsStaged: undefined,
                _stagedHints: undefined
              } 
            : r
        ));
        
        // Update selected item if it's the one we just reverted
        if (state.selectedItem && (state.selectedItem.id === itemId || 
            ('vnum' in state.selectedItem && state.selectedItem.vnum?.toString() === itemId))) {
          setState(prev => ({ 
            ...prev, 
            selectedItem: prev.selectedItem ? { 
              ...prev.selectedItem, 
              isDirty: false,
              // Clear staged hints from selected item too
              _hintsStaged: undefined,
              _stagedHints: undefined
            } : null 
          }));
        }
      }
    }
    
    // Check paths if not found in regions
    if (!item) {
      item = paths.find(p => p.id === itemId || p.vnum?.toString() === itemId);
      if (item && 'path_type' in item) {
        const path = item as Path;
        
        // If this is a completely new item (never saved), remove it entirely
        if (path.isDirty && !paths.some(p => p.vnum === path.vnum && !p.isDirty)) {
          console.log('[Discard] Removing new unsaved path:', itemId);
          setPaths(prev => prev.filter(p => p.id !== itemId && p.vnum?.toString() !== itemId));
          
          // Clear selection if this was the selected item
          if (state.selectedItem && (state.selectedItem.id === itemId || 
              ('vnum' in state.selectedItem && state.selectedItem.vnum?.toString() === itemId))) {
            setState(prev => ({ ...prev, selectedItem: null }));
          }
        } else {
          // If it's an existing item with changes, revert to clean state
          console.log('[Discard] Marking path as clean (reverting changes):', itemId);
          setPaths(prev => prev.map(p => 
            (p.id === itemId || p.vnum?.toString() === itemId) 
              ? { ...p, isDirty: false } 
              : p
          ));
          
          // Update selected item if it's the one we just reverted
          if (state.selectedItem && (state.selectedItem.id === itemId || 
              ('vnum' in state.selectedItem && state.selectedItem.vnum?.toString() === itemId))) {
            setState(prev => ({ 
              ...prev, 
              selectedItem: prev.selectedItem ? { ...prev.selectedItem, isDirty: false } : null 
            }));
          }
        }
      }
    }
    
    if (!item) {
      console.warn('[Discard] Item not found:', itemId);
      return;
    }
    
    // Remove from unsaved items
    setUnsavedItems(prev => {
      const newSet = new Set(prev);
      newSet.delete(itemId);
      return newSet;
    });
    
    // If we're discarding the currently selected item and it's being removed entirely,
    // make sure the selected item state is updated to reflect the clean state
    if (state.selectedItem && 
        ((state.selectedItem.id === itemId) || 
         ('vnum' in state.selectedItem && state.selectedItem.vnum?.toString() === itemId))) {
      
      // If the item was removed entirely, selection is already cleared above
      // If the item was just cleaned, update the selected item to reflect clean state
      if (item && !state.selectedItem.isDirty) {
        // This handles the case where we marked an existing item as clean
        setState(prev => ({ 
          ...prev, 
          selectedItem: prev.selectedItem ? { ...prev.selectedItem, isDirty: false } : null 
        }));
      }
    }
    
    console.log('[Discard] Item changes discarded successfully:', itemId);
  }, [regions, paths, state.selectedItem]);

  const centerOnItem = useCallback((item: Region | Path) => {
    let coordinate: Coordinate;
    
    if ('coordinates' in item && item.coordinates.length > 0) {
      // Region or Path - calculate center of bounding box
      const bounds = item.coordinates.reduce(
        (acc: {minX: number, maxX: number, minY: number, maxY: number}, coord: Coordinate) => ({
          minX: Math.min(acc.minX, coord.x),
          maxX: Math.max(acc.maxX, coord.x),
          minY: Math.min(acc.minY, coord.y),
          maxY: Math.max(acc.maxY, coord.y)
        }),
        { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity }
      );
      
      coordinate = {
        x: Math.round((bounds.minX + bounds.maxX) / 2),
        y: Math.round((bounds.minY + bounds.maxY) / 2)
      };
    } else {
      console.warn('[Center] Item has no valid coordinates:', item);
      return;
    }
    
    console.log('[Center] Centering on item:', {
      itemName: item.name,
      coordinate
    });
    
    // Trigger centering by setting the coordinate (will be cleared after effect runs)
    setCenterOnCoordinate(coordinate);
    
    // Clear the centering coordinate after a brief delay to allow the effect to run
    setTimeout(() => setCenterOnCoordinate(null), 100);
  }, []);

  const discardAllUnsaved = useCallback(() => {
    setUnsavedItems(new Set());
    
    // Reset all items to their original state (remove isDirty flag)
    setRegions(current => current.map(region => ({ ...region, isDirty: false })));
    setPaths(current => current.map(path => ({ ...path, isDirty: false })));
    
    // Clear selected item's dirty flag
    if (state.selectedItem?.isDirty) {
      setState(current => ({
        ...current,
        selectedItem: current.selectedItem ? { ...current.selectedItem, isDirty: false } : null
      }));
    }
  }, [state.selectedItem, setState]);

  // Delete functionality
  const deleteItem = useCallback(async (itemId: string) => {
    console.log('[Delete] Deleting item:', itemId);
    setError(null);
    
    try {
      // Find the item to delete
      let item: Region | Path | undefined;
      let itemType: 'region' | 'path' | undefined;
      
      // Check regions first
      item = regions.find(r => r.id === itemId || r.vnum?.toString() === itemId);
      if (item && 'region_type' in item) {
        itemType = 'region';
        const region = item as Region;
        
        if (region.vnum) {
          // Delete from backend if it has a vnum (exists in database)
          await apiClient.deleteRegion(region.vnum.toString());
          console.log('[Delete] Region deleted from backend:', itemId);
        }
        
        // Remove from local state
        setRegions(prev => prev.filter(r => r.id !== itemId && r.vnum?.toString() !== itemId));
        console.log('[Delete] Region removed from local state:', itemId);
      }
      
      // Check paths if not found in regions
      if (!item) {
        item = paths.find(p => p.id === itemId || p.vnum?.toString() === itemId);
        if (item && 'path_type' in item) {
          itemType = 'path';
          const path = item as Path;
          
          if (path.vnum) {
            // Delete from backend if it has a vnum (exists in database)
            await apiClient.deletePath(path.vnum.toString());
            console.log('[Delete] Path deleted from backend:', itemId);
          }
          
          // Remove from local state
          setPaths(prev => prev.filter(p => p.id !== itemId && p.vnum?.toString() !== itemId));
          console.log('[Delete] Path removed from local state:', itemId);
        }
      }
      
      if (!item) {
        console.warn('[Delete] Item not found:', itemId);
        setError(`Item not found: ${itemId}`);
        return;
      }
      
      // Remove from unsaved items if it was unsaved
      setUnsavedItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(itemId);
        return newSet;
      });
      
      // Clear selection if this was the selected item
      if (state.selectedItem && (
          state.selectedItem.id === itemId || 
          ('vnum' in state.selectedItem && state.selectedItem.vnum?.toString() === itemId)
        )) {
        setState(prev => ({ ...prev, selectedItem: null }));
        console.log('[Delete] Cleared selection');
      }
      
      console.log(`[Delete] ${itemType} deleted successfully:`, itemId);
      
    } catch (err) {
      console.error('[Delete] Failed to delete item:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete item');
    }
  }, [regions, paths, state.selectedItem, setState]);

  // Create a matching layer region (Sector Override or Transform) from a Geographic region
  const createLayer = useCallback(async (baseRegion: Region, layerType: 'sector' | 'transform') => {
    try {
      // Generate next available vnum
      const allVnums = [...regions.map(r => r.vnum), ...paths.map(p => p.vnum)];
      const maxVnum = Math.max(0, ...allVnums);
      const newVnum = maxVnum + 1;
      
      // Create suffix based on type
      const suffix = layerType === 'sector' ? '(SECTOR)' : '(TRANSFORM)';
      
      // Create new region with same coordinates but different type
      const newRegion: Omit<Region, 'id'> = {
        vnum: newVnum,
        zone_vnum: baseRegion.zone_vnum,
        name: `${baseRegion.name} ${suffix}`,
        region_type: layerType === 'sector' ? 4 : 3, // 4 = Sector Override, 3 = Transform
        coordinates: [...baseRegion.coordinates], // Copy coordinates exactly
        region_props: 0, // User will set this after creation
        region_reset_data: '',
        region_reset_time: null,
        color: layerType === 'sector' ? '#F59E0B' : '#8B5CF6' // Amber for sector, purple for transform
      };
      
      console.log('[CreateLayer] Creating new layer region:', newRegion);
      
      // Create via API
      const createdRegion = await apiClient.createRegion(newRegion);
      
      // Add to regions list
      setRegions(prev => [...prev, createdRegion]);
      
      // Select the new region for editing
      setState(prev => ({ ...prev, selectedItem: createdRegion }));
      
      console.log('[CreateLayer] Layer created successfully:', createdRegion);
    } catch (err) {
      console.error('[CreateLayer] Failed to create layer:', err);
      setError(err instanceof Error ? err.message : 'Failed to create layer region');
    }
  }, [regions, paths]);

  // Find regions with matching coordinates (for showing related regions)
  const findRelatedRegions = useCallback((region: Region): Region[] => {
    if (!region.coordinates || region.coordinates.length === 0) return [];
    
    // Convert coordinates to string for comparison
    const coordsStr = JSON.stringify(region.coordinates);
    
    return regions.filter(r => {
      if (r.vnum === region.vnum) return false; // Don't include self
      if (!r.coordinates || r.coordinates.length === 0) return false;
      
      // Check if coordinates match exactly
      return JSON.stringify(r.coordinates) === coordsStr;
    });
  }, [regions]);

  return {
    state,
    regions,
    paths,
    loading,
    error,
    centerOnCoordinate,
    setTool,
    setZoom,
    setMousePosition,
    toggleLayer,
    selectItem,
    handleCanvasClick,
    finishDrawing,
    cancelDrawing,
    clearError,
    updateSelectedItem,
    centerOnItem,
    loadData,
    hiddenRegions,
    hiddenPaths,
    toggleItemVisibility,
    hiddenFolders,
    toggleFolderVisibility,
    isItemHiddenByFolder,
    // New save functionality
    unsavedItems,
    savingItems,
    saveItem,
    saveAllUnsaved,
    discardItem,
    discardAllUnsaved,
    deleteItem,
    // Region layering
    createLayer,
    findRelatedRegions
  };
};