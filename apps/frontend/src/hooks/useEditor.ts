import { useState, useCallback, useEffect } from 'react';
import { useAuth } from './useAuth';
import { apiClient } from '../services/api';
import { EditorState, DrawingTool, Coordinate, Region, Path, Point } from '../types';

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
  const [points, setPoints] = useState<Point[]>([]);
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
      const [regionsData, pathsData, pointsData] = await Promise.all([
        apiClient.getRegions(),
        apiClient.getPaths(),
        apiClient.getPoints()
      ]);
      
      console.log('[Editor] API calls successful:', {
        regions: regionsData.length,
        paths: pathsData.length,
        points: pointsData.length
      });
      
      // Check for duplicate IDs
      const regionIds = regionsData.map(r => r.id);
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
      setPoints(pointsData);
    } catch (err) {
      console.error('Failed to load data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
      
      // Clear data on error - no more fallback mock data
      setRegions([]);
      setPaths([]);
      setPoints([]);
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

  const selectItem = useCallback((item: Region | Path | Point | null) => {
    if (item) {
      console.log('[Selection] Item selected:', {
        type: 'coordinates' in item ? ('vnum' in item ? 'region/path' : 'unknown') : 'point',
        id: item.id,
        name: 'name' in item ? item.name : 'unknown'
      });
    } else {
      console.log('[Selection] Selection cleared');
    }
    setState(prev => ({ ...prev, selectedItem: item }));
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

    if (state.tool === 'point') {
      const newPoint: Point = {
        id: Date.now().toString(),
        coordinate,
        name: `New Point ${points.length + 1}`,
        type: 'landmark',
        isDirty: true  // Mark as unsaved
      };
      
      console.log('[Drawing] Creating new point:', {
        id: newPoint.id,
        coordinate: newPoint.coordinate,
        name: newPoint.name
      });
      
      // Add to local state immediately (buffered)
      setPoints(prev => [...prev, newPoint]);
      selectItem(newPoint);
      
      // Mark as unsaved
      setUnsavedItems(prev => new Set(prev).add(newPoint.id!));
      
      console.log('[Drawing] Point created locally, marked as unsaved');
    } else if (state.tool === 'polygon' || state.tool === 'linestring') {
      const newPointCount = state.currentDrawing.length + 1;
      console.log('[Drawing] Adding point to', state.tool, ':', {
        pointNumber: newPointCount,
        coordinate,
        requiredPoints: state.tool === 'polygon' ? 3 : 2
      });
      
      setState(prev => ({
        ...prev,
        isDrawing: true,
        currentDrawing: [...prev.currentDrawing, coordinate]
      }));
    }
  }, [state.tool, state.isDrawing, state.currentDrawing.length, points.length, selectItem]);

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
      polygon: 3,
      linestring: 2
    };

    const minPoints = minPointsForTool[state.tool as keyof typeof minPointsForTool];
    
    if (state.currentDrawing.length < minPoints) {
      const errorMsg = `${state.tool === 'polygon' ? 'Polygon' : 'Path'} requires at least ${minPoints} points`;
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

    if (state.tool === 'polygon' && state.currentDrawing.length >= 3) {
      const newRegion: Region = {
        vnum: Math.max(1000, ...regions.map(r => r.vnum || 0)) + 1, // Generate next vnum
        zone_vnum: 1,
        name: `New Region ${regions.length + 1}`,
        region_type: 1, // Geographic region
        coordinates: [...state.currentDrawing], // Create a copy to avoid reference issues
        region_props: null,
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
      setUnsavedItems(prev => new Set(prev).add(newRegion.id!));
      
      console.log('[Drawing] Region created locally, marked as unsaved');
    } else if (state.tool === 'linestring' && state.currentDrawing.length >= 2) {
      const newPath: Path = {
        vnum: Math.max(2000, ...paths.map(p => p.vnum || 0)) + 1, // Generate next vnum
        zone_vnum: 1,
        name: `New Path ${paths.length + 1}`,
        path_type: 1, // Paved Road
        coordinates: [...state.currentDrawing], // Create a copy to avoid reference issues
        path_props: 0,
        
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
      setUnsavedItems(prev => new Set(prev).add(newPath.id!));
      
      console.log('[Drawing] Path created locally, marked as unsaved');
    }
    
    // Always clean up drawing state after processing
    console.log('[Drawing] Cleaning up drawing state');
    setState(prev => ({ ...prev, isDrawing: false, currentDrawing: [] }));
  }, [state.isDrawing, state.currentDrawing, state.tool, regions, paths, selectItem]);

  const updateSelectedItem = useCallback((updates: Partial<Region | Path | Point>) => {
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
      itemId = state.selectedItem.id || '';
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
    } else {
      // It's a Point
      setPoints(prev => prev.map(point => 
        point.id === itemId
          ? { ...point, ...updatesWithDirty } as Point
          : point
      ));
    }
    
    // Mark as unsaved
    setUnsavedItems(prev => new Set(prev).add(itemId));
    
    // Update selected item state
    setState(prev => ({ ...prev, selectedItem: { ...prev.selectedItem!, ...updatesWithDirty } as Region | Path | Point }));
    
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
      let item: Region | Path | Point | undefined;
      
      // Check regions first
      item = regions.find(r => r.id === itemId || r.vnum?.toString() === itemId);
      if (item && 'region_type' in item) {
        const region = item as Region;
        if (region.vnum && regions.some(r => r.vnum === region.vnum && !r.isDirty)) {
          // Update existing region
          await apiClient.updateRegion(region.vnum.toString(), region);
          console.log('[Save] Region updated successfully:', itemId);
        } else {
          // Create new region
          await apiClient.createRegion(region);
          console.log('[Save] Region created successfully:', itemId);
        }
        
        // Mark as clean
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
          if (path.vnum && paths.some(p => p.vnum === path.vnum && !p.isDirty)) {
            // Update existing path
            await apiClient.updatePath(path.vnum.toString(), path);
            console.log('[Save] Path updated successfully:', itemId);
          } else {
            // Create new path
            await apiClient.createPath(path);
            console.log('[Save] Path created successfully:', itemId);
          }
          
          // Mark as clean
          setPaths(prev => prev.map(p => 
            (p.id === itemId || p.vnum?.toString() === itemId) 
              ? { ...p, isDirty: false } 
              : p
          ));
        }
      }
      
      // Check points if not found in regions or paths
      if (!item) {
        item = points.find(p => p.id === itemId);
        if (item && 'coordinate' in item) {
          const point = item as Point;
          // Points don't have vnum, so always create new or update by ID
          if (points.some(p => p.id === point.id && !p.isDirty)) {
            // Update existing point
            await apiClient.updatePoint(point.id!, point);
            console.log('[Save] Point updated successfully:', itemId);
          } else {
            // Create new point
            await apiClient.createPoint(point);
            console.log('[Save] Point created successfully:', itemId);
          }
          
          // Mark as clean
          setPoints(prev => prev.map(p => 
            p.id === itemId ? { ...p, isDirty: false } : p
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
  }, [authDisabled, session, savingItems, regions, paths, points, state.selectedItem]);

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
    let item: Region | Path | Point | undefined;
    
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
            ? { ...r, isDirty: false } 
            : r
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
    
    // Check points if not found in regions or paths
    if (!item) {
      item = points.find(p => p.id === itemId);
      if (item && 'coordinate' in item) {
        const point = item as Point;
        
        // Points are always considered "new" since they don't have vnums
        // If it's dirty, it means it's unsaved, so remove it
        if (point.isDirty) {
          console.log('[Discard] Removing new unsaved point:', itemId);
          setPoints(prev => prev.filter(p => p.id !== itemId));
          
          // Clear selection if this was the selected item
          if (state.selectedItem && state.selectedItem.id === itemId) {
            setState(prev => ({ ...prev, selectedItem: null }));
          }
        } else {
          // If it's not dirty, just mark as clean (shouldn't happen, but safety)
          console.log('[Discard] Marking point as clean:', itemId);
          setPoints(prev => prev.map(p => 
            p.id === itemId ? { ...p, isDirty: false } : p
          ));
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
  }, [regions, paths, points, state.selectedItem]);

  const centerOnItem = useCallback((item: Region | Path | Point) => {
    let coordinate: Coordinate;
    
    if ('coordinate' in item) {
      // Point - use its coordinate directly
      coordinate = item.coordinate;
    } else if ('coordinates' in item && item.coordinates.length > 0) {
      // Region or Path - calculate center of bounding box
      const bounds = item.coordinates.reduce(
        (acc, coord) => ({
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
    setPoints(current => current.map(point => ({ ...point, isDirty: false })));
    
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
      let item: Region | Path | Point | undefined;
      let itemType: 'region' | 'path' | 'point' | undefined;
      
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
      
      // Check points if not found in regions or paths
      if (!item) {
        item = points.find(p => p.id === itemId);
        if (item && 'coordinate' in item) {
          itemType = 'point';
          const point = item as Point;
          
          // Points don't have vnums yet, so just remove from local state
          // await apiClient.deletePoint(point.id); // Uncomment when point API is ready
          
          // Remove from local state
          setPoints(prev => prev.filter(p => p.id !== itemId));
          console.log('[Delete] Point removed from local state:', itemId);
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
  }, [regions, paths, points, state.selectedItem, setState]);

  return {
    state,
    regions,
    paths,
    points,
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
    deleteItem
  };
};