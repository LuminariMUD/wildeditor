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
        type: 'landmark'
      };
      
      console.log('[Drawing] Creating new point:', {
        id: newPoint.id,
        coordinate: newPoint.coordinate,
        name: newPoint.name
      });
      
      // Optimistic update
      setPoints(prev => [...prev, newPoint]);
      selectItem(newPoint);
      
      // Save to API
      if (session?.access_token) {
        apiClient.createPoint(newPoint)
          .then(() => {
            console.log('[Drawing] Point created successfully:', newPoint.id);
          })
          .catch(err => {
            console.error('[Drawing] Failed to create point:', {
              error: err,
              point: newPoint,
              message: err.message || 'Unknown error'
            });
            // Revert optimistic update
            setPoints(prev => prev.filter(p => p.id !== newPoint.id));
            setError('Failed to create point: ' + (err.message || 'Unknown error'));
          });
      } else {
        console.warn('[Drawing] No auth token, point saved locally only');
      }
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
  }, [state.tool, state.isDrawing, state.currentDrawing.length, points.length, selectItem, session?.access_token]);

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
        color: '#F59E0B'
      };
      
      console.log('[Drawing] Creating new region:', {
        id: newRegion.id,
        vnum: newRegion.vnum,
        points: newRegion.coordinates.length,
        type: newRegion.region_type
      });
      
      // Optimistic update
      setRegions(prev => [...prev, newRegion]);
      selectItem(newRegion);
      
      // Save to API
      if (authDisabled || session?.access_token) {
        apiClient.createRegion(newRegion)
          .then(() => {
            console.log('[Drawing] Region created successfully:', newRegion.id);
          })
          .catch(err => {
            console.error('[Drawing] Failed to create region:', {
              error: err,
              region: newRegion,
              message: err.message || 'Unknown error'
            });
            // Revert optimistic update
            setRegions(prev => prev.filter(r => r.id !== newRegion.id));
            setError('Failed to create region: ' + (err.message || 'Unknown error'));
          });
      } else {
        console.warn('[Drawing] No auth token, region saved locally only');
      }
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
        color: '#EC4899'
      };
      
      console.log('[Drawing] Creating new path:', {
        id: newPath.id,
        vnum: newPath.vnum,
        points: newPath.coordinates.length,
        type: newPath.type
      });
      
      // Optimistic update
      setPaths(prev => [...prev, newPath]);
      selectItem(newPath);
      
      // Save to API
      if (authDisabled || session?.access_token) {
        apiClient.createPath(newPath)
          .then(() => {
            console.log('[Drawing] Path created successfully:', newPath.id);
          })
          .catch(err => {
            console.error('[Drawing] Failed to create path:', {
              error: err,
              path: newPath,
              message: err.message || 'Unknown error'
            });
            // Revert optimistic update
            setPaths(prev => prev.filter(p => p.id !== newPath.id));
            setError('Failed to create path: ' + (err.message || 'Unknown error'));
          });
      } else {
        console.warn('[Drawing] No auth token, path saved locally only');
      }
    }
    
    // Always clean up drawing state after processing
    console.log('[Drawing] Cleaning up drawing state');
    setState(prev => ({ ...prev, isDrawing: false, currentDrawing: [] }));
  }, [state.isDrawing, state.currentDrawing, state.tool, regions, paths, selectItem, session?.access_token]);

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
    
    if ('coordinates' in state.selectedItem) {
      if ('region_type' in state.selectedItem) {
        // It's a Region
        setRegions(prev => prev.map(region => 
          (region.vnum?.toString() === itemId || region.id === itemId)
            ? { ...region, ...updates } as Region
            : region
        ));
        
        // Save to API
        if (authDisabled || session?.access_token) {
          apiClient.updateRegion(itemId, updates as Partial<Region>)
            .then(() => {
              console.log('[Update] Region updated successfully:', itemId);
            })
            .catch(err => {
              console.error('[Update] Failed to update region:', {
                error: err,
                regionId: itemId,
                updates,
                message: err.message || 'Unknown error'
              });
              setError('Failed to update region: ' + (err.message || 'Unknown error'));
            });
        }
      } else if ('path_type' in state.selectedItem) {
        // It's a Path
        setPaths(prev => prev.map(path => 
          (path.vnum?.toString() === itemId || path.id === itemId)
            ? { ...path, ...updates } as Path
            : path
        ));
        
        // Save to API
        if (authDisabled || session?.access_token) {
          apiClient.updatePath(itemId, updates as Partial<Path>)
            .then(() => {
              console.log('[Update] Path updated successfully:', itemId);
            })
            .catch(err => {
              console.error('[Update] Failed to update path:', {
                error: err,
                pathId: itemId,
                updates,
                message: err.message || 'Unknown error'
              });
              setError('Failed to update path: ' + (err.message || 'Unknown error'));
            });
        }
      }
    } else {
      // It's a Point
      setPoints(prev => prev.map(point => 
        point.id === itemId
          ? { ...point, ...updates } as Point
          : point
      ));
      
      // Save to API
      if (authDisabled || session?.access_token) {
        apiClient.updatePoint(itemId, updates as Partial<Point>)
          .then(() => {
            console.log('[Update] Point updated successfully:', itemId);
          })
          .catch(err => {
            console.error('[Update] Failed to update point:', {
              error: err,
              pointId: itemId,
              updates,
              message: err.message || 'Unknown error'
            });
            setError('Failed to update point: ' + (err.message || 'Unknown error'));
          });
      }
    }
    
    setState(prev => ({ ...prev, selectedItem: { ...prev.selectedItem!, ...updates } as Region | Path | Point }));
  }, [state.selectedItem, session]);

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
    loadData
  };
};