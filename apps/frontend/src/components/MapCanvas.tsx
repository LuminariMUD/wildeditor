import React, { useRef, useEffect, useCallback, useMemo, useState } from 'react';
import { Coordinate, Region, Path, Point, EditorState } from '../types';

interface MapCanvasProps {
  state: EditorState;
  regions: Region[];
  paths: Path[];
  points: Point[];
  onMouseMove: (coordinate: Coordinate) => void;
  onClick: (coordinate: Coordinate) => void;
  onSelectItem: (item: Region | Path | Point | null) => void;
}

export const MapCanvas: React.FC<MapCanvasProps> = ({
  state,
  regions,
  paths,
  points,
  onMouseMove,
  onClick,
  onSelectItem
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const backgroundImageRef = useRef<HTMLImageElement | null>(null);
  const [imageLoaded, setImageLoaded] = useState(false);
  
  // Track previous zoom level for centering
  const prevZoomRef = useRef<number>(state.zoom);

  const MAP_SIZE = 2048;
  const COORDINATE_RANGE = 1024;

  // Load background image
  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      backgroundImageRef.current = img;
      setImageLoaded(true);
      console.log('Wilderness background image loaded successfully');
    };
    img.onerror = (error) => {
      console.warn('Failed to load wilderness background image:', error);
    };
    img.src = '/luminari_wilderness.png';
  }, []);

  // Handle zoom centering - maintain the same center point when zoom changes
  useEffect(() => {
    const container = containerRef.current;
    if (!container || prevZoomRef.current === state.zoom) return;

    const prevZoom = prevZoomRef.current;
    const newZoom = state.zoom;
    const zoomRatio = newZoom / prevZoom;

    // Get the current center point of the viewport
    const containerRect = container.getBoundingClientRect();
    const centerX = container.scrollLeft + containerRect.width / 2;
    const centerY = container.scrollTop + containerRect.height / 2;

    // Calculate the new scroll position to maintain the same center point
    const newScrollX = centerX * zoomRatio - containerRect.width / 2;
    const newScrollY = centerY * zoomRatio - containerRect.height / 2;

    // Update scroll position to maintain center
    container.scrollLeft = Math.max(0, newScrollX);
    container.scrollTop = Math.max(0, newScrollY);

    // Update the previous zoom reference
    prevZoomRef.current = state.zoom;
  }, [state.zoom]);

  // Convert game coordinates (-1024 to +1024) to canvas coordinates (0 to MAP_SIZE)
  const gameToCanvas = useCallback((coord: Coordinate): { x: number; y: number } => {
    return {
      x: ((coord.x + COORDINATE_RANGE) / (COORDINATE_RANGE * 2)) * MAP_SIZE,
      y: ((COORDINATE_RANGE - coord.y) / (COORDINATE_RANGE * 2)) * MAP_SIZE
    };
  }, []);

  // Convert canvas coordinates to game coordinates
  const canvasToGame = useCallback((clientX: number, clientY: number): Coordinate => {
    const rect = canvasRef.current?.getBoundingClientRect();
    const canvas = canvasRef.current;
    if (!rect || !canvas) return { x: 0, y: 0 };
    
    // Get mouse position relative to canvas element
    const canvasX = clientX - rect.left;
    const canvasY = clientY - rect.top;
    
    // Convert CSS coordinates to normalized coordinates (0-1)
    // The canvas display size is controlled by CSS, account for that
    const normalizedX = canvasX / rect.width;
    const normalizedY = canvasY / rect.height;
    
    // Ensure we're within bounds
    const clampedX = Math.max(0, Math.min(1, normalizedX));
    const clampedY = Math.max(0, Math.min(1, normalizedY));
    
    // Convert to game coordinates (-1024 to +1024)
    return {
      x: Math.round((clampedX * (COORDINATE_RANGE * 2)) - COORDINATE_RANGE),
      y: Math.round(COORDINATE_RANGE - (clampedY * (COORDINATE_RANGE * 2)))
    };
  }, []);

  const drawGrid = useCallback((ctx: CanvasRenderingContext2D) => {
    if (!state.showGrid) return;

    const gridSize = 50; // Grid every 50 game units
    
    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 2]);

    // Vertical lines
    for (let gameX = -COORDINATE_RANGE; gameX <= COORDINATE_RANGE; gameX += gridSize) {
      const canvasPos = gameToCanvas({ x: gameX, y: 0 });
      ctx.beginPath();
      ctx.moveTo(canvasPos.x, 0);
      ctx.lineTo(canvasPos.x, MAP_SIZE);
      ctx.stroke();
    }

    // Horizontal lines
    for (let gameY = -COORDINATE_RANGE; gameY <= COORDINATE_RANGE; gameY += gridSize) {
      const canvasPos = gameToCanvas({ x: 0, y: gameY });
      ctx.beginPath();
      ctx.moveTo(0, canvasPos.y);
      ctx.lineTo(MAP_SIZE, canvasPos.y);
      ctx.stroke();
    }

    ctx.setLineDash([]);
  }, [state.showGrid, gameToCanvas]);

  const drawBackgroundImage = useCallback((ctx: CanvasRenderingContext2D) => {
    if (!state.showBackground) return;
    
    const img = backgroundImageRef.current;
    if (!img) return;

    // Draw the wilderness map image as background, scaled to fit the entire canvas
    ctx.drawImage(img, 0, 0, MAP_SIZE, MAP_SIZE);
  }, [state.showBackground]);

  // Note: Removed old drawing functions as they're replaced by optimized versions

  // Optimized drawing functions that use pre-transformed coordinates
  const drawRegionOptimized = useCallback((ctx: CanvasRenderingContext2D, region: Region & { canvasCoords: {x: number, y:number}[] }) => {
    if (!state.showRegions || region.canvasCoords.length < 3) return;
    
    const regionColor = region.color || '#3B82F6'; // Default blue color if none set
    const isSelected = state.selectedItem?.id === region.id;
    
    // Fill with transparent color (25% opacity)
    ctx.globalAlpha = 0.25;
    ctx.fillStyle = regionColor;
    
    // Draw polygon fill
    ctx.beginPath();
    ctx.moveTo(region.canvasCoords[0].x, region.canvasCoords[0].y);
    for (let i = 1; i < region.canvasCoords.length; i++) {
      ctx.lineTo(region.canvasCoords[i].x, region.canvasCoords[i].y);
    }
    ctx.closePath();
    ctx.fill();
    
    // Reset alpha for stroke
    ctx.globalAlpha = 1.0;
    ctx.strokeStyle = regionColor;
    ctx.lineWidth = isSelected ? 2 : 1; // 1-pixel lines at 100% zoom, 2-pixel when selected
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    // Draw polygon outline
    ctx.stroke();

    // Draw vertices only when selected or when zoomed in enough to see them clearly
    if (isSelected || state.zoom >= 150) {
      region.canvasCoords.forEach((coord, index) => {
        ctx.fillStyle = regionColor;
        ctx.beginPath();
        ctx.arc(coord.x, coord.y, isSelected ? 4 : 2, 0, Math.PI * 2);
        ctx.fill();

        // Draw vertex numbers only when selected
        if (isSelected) {
          ctx.fillStyle = '#FFFFFF';
          ctx.strokeStyle = '#000000';
          ctx.lineWidth = 1;
          ctx.font = '12px monospace';
          ctx.textAlign = 'center';
          ctx.strokeText((index + 1).toString(), coord.x, coord.y - 8);
          ctx.fillText((index + 1).toString(), coord.x, coord.y - 8);
        }
      });
    }
  }, [state.showRegions, state.selectedItem, state.zoom]);
  
  const drawPathOptimized = useCallback((ctx: CanvasRenderingContext2D, path: Path & { canvasCoords: {x: number, y:number}[] }) => {
    if (!state.showPaths || path.canvasCoords.length < 2) return;
    
    const pathColor = path.color || '#10B981'; // Default green color if none set
    const isSelected = state.selectedItem?.id === path.id;
    
    // Draw path line
    ctx.globalAlpha = 1.0; // Paths are solid, not transparent
    ctx.strokeStyle = pathColor;
    ctx.lineWidth = isSelected ? 2 : 1; // 1-pixel lines at 100% zoom, 2-pixel when selected
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();
    ctx.moveTo(path.canvasCoords[0].x, path.canvasCoords[0].y);
    for (let i = 1; i < path.canvasCoords.length; i++) {
      ctx.lineTo(path.canvasCoords[i].x, path.canvasCoords[i].y);
    }
    ctx.stroke();

    // Draw vertices only when selected or when zoomed in enough to see them clearly
    if (isSelected || state.zoom >= 150) {
      path.canvasCoords.forEach((coord, index) => {
        ctx.fillStyle = pathColor;
        ctx.beginPath();
        ctx.arc(coord.x, coord.y, isSelected ? 3 : 1, 0, Math.PI * 2);
        ctx.fill();

        // Draw vertex numbers only when selected
        if (isSelected) {
          ctx.fillStyle = '#FFFFFF';
          ctx.strokeStyle = '#000000';
          ctx.lineWidth = 1;
          ctx.font = '10px monospace';
          ctx.textAlign = 'center';
          ctx.strokeText((index + 1).toString(), coord.x, coord.y - 6);
          ctx.fillText((index + 1).toString(), coord.x, coord.y - 6);
        }
      });
    }
  }, [state.showPaths, state.selectedItem, state.zoom]);
  
  const drawPointOptimized = useCallback((ctx: CanvasRenderingContext2D, point: Point & { canvasPos: {x: number, y:number} }) => {
    const color = point.type === 'landmark' ? '#F59E0B' : '#8B5CF6';
    ctx.fillStyle = color;
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = state.selectedItem?.id === point.id ? 3 : 2;

    ctx.beginPath();
    ctx.arc(point.canvasPos.x, point.canvasPos.y, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Draw name
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(point.name, point.canvasPos.x, point.canvasPos.y + 20);
  }, [state.selectedItem]);

  const drawCurrentDrawing = useCallback((ctx: CanvasRenderingContext2D) => {
    if (!state.isDrawing || state.currentDrawing.length === 0) return;
    
    console.log('[Canvas] Drawing current shape:', {
      tool: state.tool,
      points: state.currentDrawing.length
    });

    const canvasCoords = state.currentDrawing.map(gameToCanvas);
    
    // Determine if the current drawing is valid
    const isValidDrawing = (
      (state.tool === 'polygon' && canvasCoords.length >= 3) ||
      (state.tool === 'linestring' && canvasCoords.length >= 2)
    );
    
    // Use different colors based on validity
    const strokeColor = isValidDrawing ? '#22C55E' : '#F59E0B';
    const fillColor = isValidDrawing ? '#22C55E20' : '#F59E0B20';
    
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = 3;
    ctx.setLineDash([8, 4]);

    if (state.tool === 'polygon' && canvasCoords.length >= 2) {
      ctx.fillStyle = fillColor;
      ctx.beginPath();
      ctx.moveTo(canvasCoords[0].x, canvasCoords[0].y);
      for (let i = 1; i < canvasCoords.length; i++) {
        ctx.lineTo(canvasCoords[i].x, canvasCoords[i].y);
      }
      
      // Only close the path if we have 3+ points for a valid polygon
      if (canvasCoords.length >= 3) {
        ctx.closePath();
        ctx.fill();
      }
      ctx.stroke();
      
      // Draw connection line back to first point if we have 2+ points
      if (canvasCoords.length >= 2) {
        ctx.setLineDash([2, 2]);
        ctx.strokeStyle = strokeColor + '80';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(canvasCoords[canvasCoords.length - 1].x, canvasCoords[canvasCoords.length - 1].y);
        ctx.lineTo(canvasCoords[0].x, canvasCoords[0].y);
        ctx.stroke();
      }
    } else if (state.tool === 'linestring' && canvasCoords.length >= 1) {
      if (canvasCoords.length >= 2) {
        ctx.beginPath();
        ctx.moveTo(canvasCoords[0].x, canvasCoords[0].y);
        for (let i = 1; i < canvasCoords.length; i++) {
          ctx.lineTo(canvasCoords[i].x, canvasCoords[i].y);
        }
        ctx.stroke();
      }
    }

    // Draw vertices with different styles based on validity
    canvasCoords.forEach((coord, index) => {
      ctx.fillStyle = strokeColor;
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(coord.x, coord.y, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      
      // Draw vertex numbers
      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 12px monospace';
      ctx.textAlign = 'center';
      ctx.fillText((index + 1).toString(), coord.x, coord.y - 12);
    });
    
    // Draw status text
    if (canvasCoords.length > 0) {
      const minPoints = state.tool === 'polygon' ? 3 : 2;
      const statusText = isValidDrawing 
        ? `${state.tool} (${canvasCoords.length} points) - Press Enter to finish` 
        : `${state.tool} (${canvasCoords.length}/${minPoints} points) - Need ${minPoints - canvasCoords.length} more`;
      
      ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
      ctx.fillRect(10, 10, 400, 30);
      ctx.fillStyle = isValidDrawing ? '#22C55E' : '#F59E0B';
      ctx.font = '14px sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(statusText, 15, 30);
    }

    ctx.setLineDash([]);
  }, [state.isDrawing, state.currentDrawing, state.tool, gameToCanvas]);

  // Memoize expensive calculations
  const canvasScale = useMemo(() => state.zoom / 100, [state.zoom]);
  
  // Memoize coordinate transformations for all objects to avoid recalculating every render
  const transformedRegions = useMemo(() => {
    return regions.map(region => ({
      ...region,
      canvasCoords: region.coordinates.map(gameToCanvas)
    }));
  }, [regions, gameToCanvas]);
  
  const transformedPaths = useMemo(() => {
    return paths.map(path => ({
      ...path,
      canvasCoords: path.coordinates.map(gameToCanvas)
    }));
  }, [paths, gameToCanvas]);
  
  const transformedPoints = useMemo(() => {
    return points.map(point => ({
      ...point,
      canvasPos: gameToCanvas(point.coordinate)
    }));
  }, [points, gameToCanvas]);

  const render = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      console.error('[Canvas] Canvas ref not available for rendering');
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      console.error('[Canvas] Failed to get 2D context');
      return;
    }
    
    // Set canvas internal resolution to a fixed high value for crisp rendering
    canvas.width = MAP_SIZE;
    canvas.height = MAP_SIZE;
    
    // Set canvas display size based on zoom
    const displaySize = MAP_SIZE * canvasScale;
    canvas.style.width = `${displaySize}px`;
    canvas.style.height = `${displaySize}px`;

    // Clear canvas with dark background
    ctx.fillStyle = '#1F2937';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // No need to scale the context - we're controlling zoom via CSS display size

    // Draw background wilderness map image
    drawBackgroundImage(ctx);

    // Draw grid
    drawGrid(ctx);

    // Draw coordinate axes
    ctx.strokeStyle = '#6B7280';
    ctx.lineWidth = 2;
    
    // X-axis (horizontal)
    const xAxisY = MAP_SIZE / 2;
    ctx.beginPath();
    ctx.moveTo(0, xAxisY);
    ctx.lineTo(MAP_SIZE, xAxisY);
    ctx.stroke();
    
    // Y-axis (vertical)
    const yAxisX = MAP_SIZE / 2;
    ctx.beginPath();
    ctx.moveTo(yAxisX, 0);
    ctx.lineTo(yAxisX, MAP_SIZE);
    ctx.stroke();

    // Draw origin marker
    const origin = gameToCanvas({ x: 0, y: 0 });
    ctx.fillStyle = '#EF4444';
    ctx.beginPath();
    ctx.arc(origin.x, origin.y, 5, 0, Math.PI * 2);
    ctx.fill();

    // Draw regions using pre-transformed coordinates
    transformedRegions.forEach(region => drawRegionOptimized(ctx, region));

    // Draw paths using pre-transformed coordinates
    transformedPaths.forEach(path => drawPathOptimized(ctx, path));

    // Draw points using pre-transformed coordinates
    transformedPoints.forEach(point => drawPointOptimized(ctx, point));

    // Draw current drawing
    drawCurrentDrawing(ctx);
  }, [imageLoaded, canvasScale, drawBackgroundImage, drawGrid, drawCurrentDrawing, transformedRegions, transformedPaths, transformedPoints, gameToCanvas, drawRegionOptimized, drawPathOptimized, drawPointOptimized]);

  useEffect(() => {
    render();
    
    // Store canvas ref for cleanup
    const canvas = canvasRef.current;
    
    // Cleanup function to handle component unmount
    return () => {
      if (canvas) {
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
      }
    };
  }, [render]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    const gameCoord = canvasToGame(e.clientX, e.clientY);
    onMouseMove(gameCoord);
  }, [canvasToGame, onMouseMove]);

  // Geometric utility functions for accurate selection
  const isPointInPolygon = useCallback((point: Coordinate, polygon: Coordinate[]): boolean => {
    if (polygon.length < 3) return false;
    
    let isInside = false;
    const x = point.x;
    const y = point.y;
    
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const xi = polygon[i].x;
      const yi = polygon[i].y;
      const xj = polygon[j].x;
      const yj = polygon[j].y;
      
      if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
        isInside = !isInside;
      }
    }
    
    return isInside;
  }, []);

  const distanceToLineSegment = useCallback((point: Coordinate, lineStart: Coordinate, lineEnd: Coordinate): number => {
    const A = point.x - lineStart.x;
    const B = point.y - lineStart.y;
    const C = lineEnd.x - lineStart.x;
    const D = lineEnd.y - lineStart.y;

    const dot = A * C + B * D;
    const lenSq = C * C + D * D;
    
    if (lenSq === 0) return Math.sqrt(A * A + B * B);
    
    let param = dot / lenSq;
    param = Math.max(0, Math.min(1, param));
    
    const xx = lineStart.x + param * C;
    const yy = lineStart.y + param * D;
    
    const dx = point.x - xx;
    const dy = point.y - yy;
    
    return Math.sqrt(dx * dx + dy * dy);
  }, []);

  const distanceToPath = useCallback((point: Coordinate, path: Coordinate[]): number => {
    if (path.length < 2) return Infinity;
    
    let minDistance = Infinity;
    for (let i = 0; i < path.length - 1; i++) {
      const distance = distanceToLineSegment(point, path[i], path[i + 1]);
      minDistance = Math.min(minDistance, distance);
    }
    
    return minDistance;
  }, [distanceToLineSegment]);

  const handleClick = useCallback((e: React.MouseEvent) => {
    const gameCoord = canvasToGame(e.clientX, e.clientY);
    
    console.log('[Canvas] Click event:', {
      tool: state.tool,
      coordinate: gameCoord,
      mouseEvent: { clientX: e.clientX, clientY: e.clientY }
    });
    
    if (state.tool === 'select') {
      console.log('[Canvas] Selection mode - checking for items at:', gameCoord);
      const POINT_SELECTION_RADIUS = 10; // pixels
      const PATH_SELECTION_TOLERANCE = 8; // game units
      
      // Check for point selection first (highest priority)
      const clickedPoint = points.find(point => {
        const canvasPos = gameToCanvas(point.coordinate);
        const rect = canvasRef.current?.getBoundingClientRect();
        if (!rect) return false;
        
        const canvasClickX = e.clientX - rect.left;
        const canvasClickY = e.clientY - rect.top;
        
        // Account for canvas scaling
        const scale = state.zoom / 100;
        const scaledCanvasPos = {
          x: canvasPos.x * scale,
          y: canvasPos.y * scale
        };
        
        const distance = Math.sqrt(
          Math.pow(canvasClickX - scaledCanvasPos.x, 2) +
          Math.pow(canvasClickY - scaledCanvasPos.y, 2)
        );
        
        return distance <= POINT_SELECTION_RADIUS;
      });

      if (clickedPoint) {
        console.log('[Canvas] Point selected:', {
          point: clickedPoint.name,
          id: clickedPoint.id,
          coordinate: clickedPoint.coordinate
        });
        onSelectItem(clickedPoint);
        return;
      }

      // Check for region selection using proper point-in-polygon
      const clickedRegion = regions.find(region => {
        if (region.coordinates.length < 3) return false;
        return isPointInPolygon(gameCoord, region.coordinates);
      });

      if (clickedRegion) {
        console.log('[Canvas] Region selected:', {
          region: clickedRegion.name,
          id: clickedRegion.id,
          region_type: clickedRegion.region_type,
          pointCount: clickedRegion.coordinates.length
        });
        onSelectItem(clickedRegion);
        return;
      }

      // Check for path selection using distance to line segments
      const clickedPath = paths.find(path => {
        if (path.coordinates.length < 2) return false;
        const distance = distanceToPath(gameCoord, path.coordinates);
        return distance <= PATH_SELECTION_TOLERANCE;
      });

      if (clickedPath) {
        console.log('[Canvas] Path selected:', {
          path: clickedPath.name,
          id: clickedPath.id,
          type: clickedPath.type,
          pointCount: clickedPath.coordinates.length
        });
        onSelectItem(clickedPath);
        return;
      }

      // No selection found
      console.log('[Canvas] No item found at click position, clearing selection');
      onSelectItem(null);
    } else {
      // Drawing tools
      console.log('[Canvas] Passing click to drawing handler');
      onClick(gameCoord);
    }
  }, [state.tool, state.zoom, points, regions, paths, canvasToGame, gameToCanvas, onClick, onSelectItem, isPointInPolygon, distanceToPath]);

  return (
    <div ref={containerRef} className="flex-1 overflow-auto bg-gray-800 p-4">
      <div className="flex items-center justify-center min-h-full min-w-full">
        <canvas
          ref={canvasRef}
          className="cursor-crosshair"
          onMouseMove={handleMouseMove}
          onClick={handleClick}
          style={{
            imageRendering: 'pixelated',
            // Maintain exact proportions - no CSS scaling beyond what we set in render()
            display: 'block'
          }}
        />
      </div>
    </div>
  );
};