import { useRef, useEffect, useCallback, useState, FC } from 'react';
import { Coordinate, Region, Path, Point, EditorState } from '../types';

interface SimpleMapCanvasProps {
  state: EditorState;
  regions: Region[];
  paths: Path[];
  points: Point[];
  onMouseMove: (coordinate: Coordinate) => void;
  onClick: (coordinate: Coordinate) => void;
  onSelectItem: (item: Region | Path | Point | null) => void;
  onZoomChange: (zoom: number) => void;
  centerOnCoordinate?: Coordinate | null;
}

export const SimpleMapCanvas: FC<SimpleMapCanvasProps> = ({
  state,
  regions,
  paths,
  points,
  onMouseMove,
  onClick,
  onSelectItem,
  onZoomChange,
  centerOnCoordinate
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [backgroundImage, setBackgroundImage] = useState<HTMLImageElement | null>(null);
  
  // Transform state - all in one place for reliability
  const [transform, setTransform] = useState({
    x: 0,      // Pan offset X
    y: 0,      // Pan offset Y  
    scale: 1   // Zoom scale
  });

  // Mouse state for panning
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Constants
  const CANVAS_SIZE = 1000; // Fixed canvas size
  const GAME_COORDINATE_RANGE = 1024; // Game coordinates go from -1024 to +1024

  // Load background image
  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      setBackgroundImage(img);
      console.log('Background image loaded successfully');
    };
    img.onerror = () => {
      console.warn('Failed to load background image');
    };
    img.src = '/luminari_wilderness.png';
  }, []);

  // Update transform when zoom changes
  useEffect(() => {
    setTransform(prev => ({
      ...prev,
      scale: state.zoom / 100
    }));
  }, [state.zoom]);

  // Convert game coordinates (-1024 to +1024) to canvas coordinates (0 to CANVAS_SIZE)
  const gameToCanvas = useCallback((coord: Coordinate): { x: number; y: number } => {
    return {
      x: ((coord.x + GAME_COORDINATE_RANGE) / (GAME_COORDINATE_RANGE * 2)) * CANVAS_SIZE,
      y: ((GAME_COORDINATE_RANGE - coord.y) / (GAME_COORDINATE_RANGE * 2)) * CANVAS_SIZE
    };
  }, []);

  // Convert screen coordinates to game coordinates
  const screenToGame = useCallback((clientX: number, clientY: number): Coordinate => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };

    const rect = canvas.getBoundingClientRect();
    const screenX = clientX - rect.left;
    const screenY = clientY - rect.top;

    // Account for transform
    const canvasX = (screenX - transform.x) / transform.scale;
    const canvasY = (screenY - transform.y) / transform.scale;

    // Convert to normalized coordinates (0-1)
    const normalizedX = canvasX / CANVAS_SIZE;
    const normalizedY = canvasY / CANVAS_SIZE;

    // Clamp to bounds
    const clampedX = Math.max(0, Math.min(1, normalizedX));
    const clampedY = Math.max(0, Math.min(1, normalizedY));

    // Convert to game coordinates
    return {
      x: Math.round((clampedX * (GAME_COORDINATE_RANGE * 2)) - GAME_COORDINATE_RANGE),
      y: Math.round(GAME_COORDINATE_RANGE - (clampedY * (GAME_COORDINATE_RANGE * 2)))
    };
  }, [transform]);

  // Handle centering on coordinate
  useEffect(() => {
    if (!centerOnCoordinate || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const canvasPos = gameToCanvas(centerOnCoordinate);

    // Center the coordinate in the viewport
    const newTransform = {
      x: rect.width / 2 - canvasPos.x * transform.scale,
      y: rect.height / 2 - canvasPos.y * transform.scale,
      scale: transform.scale
    };

    setTransform(newTransform);
    console.log(`Centered on ${centerOnCoordinate.x}, ${centerOnCoordinate.y}`);
  }, [centerOnCoordinate, gameToCanvas, transform.scale]);

  // Mouse wheel zoom handler
  const handleWheel = useCallback((e: React.WheelEvent) => {
    if (!e.shiftKey) return;
    e.preventDefault();

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Calculate zoom
    const zoomDelta = e.deltaY > 0 ? -10 : 10;
    const newZoom = Math.max(25, Math.min(2000, state.zoom + zoomDelta));
    
    // Don't do anything if zoom didn't actually change
    if (newZoom === state.zoom) return;
    
    const newScale = newZoom / 100;

    // Zoom towards mouse position
    const scaleRatio = newScale / transform.scale;
    const newTransform = {
      x: mouseX - (mouseX - transform.x) * scaleRatio,
      y: mouseY - (mouseY - transform.y) * scaleRatio,
      scale: newScale
    };

    console.log(`Zoom: ${state.zoom}% -> ${newZoom}% (scale: ${transform.scale} -> ${newScale})`);
    
    setTransform(newTransform);
    onZoomChange(newZoom);
  }, [state.zoom, transform, onZoomChange]);

  // Mouse down - start panning
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button !== 1) return; // Only middle mouse button for panning
    
    setIsDragging(true);
    setDragStart({ x: e.clientX, y: e.clientY });
    e.preventDefault();
  }, []);

  // Mouse move - pan or hover
  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    const gameCoord = screenToGame(e.clientX, e.clientY);
    onMouseMove(gameCoord);

    // Handle panning
    if (isDragging) {
      const deltaX = e.clientX - dragStart.x;
      const deltaY = e.clientY - dragStart.y;
      
      setTransform(prev => ({
        ...prev,
        x: prev.x + deltaX,
        y: prev.y + deltaY
      }));
      
      setDragStart({ x: e.clientX, y: e.clientY });
    }
  }, [isDragging, dragStart, screenToGame, onMouseMove]);

  // Mouse up - stop panning
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Drawing functions with canvas transforms
  const drawGrid = useCallback((ctx: CanvasRenderingContext2D) => {
    if (!state.showGrid) return;

    ctx.strokeStyle = '#374151';
    ctx.lineWidth = 1 / transform.scale; // Scale line width
    ctx.setLineDash([2 / transform.scale, 2 / transform.scale]);

    const gridSize = 50;
    for (let gameX = -GAME_COORDINATE_RANGE; gameX <= GAME_COORDINATE_RANGE; gameX += gridSize) {
      const canvasPos = gameToCanvas({ x: gameX, y: 0 });
      ctx.beginPath();
      ctx.moveTo(canvasPos.x, 0);
      ctx.lineTo(canvasPos.x, CANVAS_SIZE);
      ctx.stroke();
    }

    for (let gameY = -GAME_COORDINATE_RANGE; gameY <= GAME_COORDINATE_RANGE; gameY += gridSize) {
      const canvasPos = gameToCanvas({ x: 0, y: gameY });
      ctx.beginPath();
      ctx.moveTo(0, canvasPos.y);
      ctx.lineTo(CANVAS_SIZE, canvasPos.y);
      ctx.stroke();
    }

    ctx.setLineDash([]);
  }, [state.showGrid, gameToCanvas, transform.scale]);

  const drawAxes = useCallback((ctx: CanvasRenderingContext2D) => {
    if (!state.showAxes) return;

    ctx.strokeStyle = '#6B7280';
    ctx.lineWidth = 2 / transform.scale;

    const origin = gameToCanvas({ x: 0, y: 0 });
    
    // X-axis
    ctx.beginPath();
    ctx.moveTo(0, origin.y);
    ctx.lineTo(CANVAS_SIZE, origin.y);
    ctx.stroke();

    // Y-axis
    ctx.beginPath();
    ctx.moveTo(origin.x, 0);
    ctx.lineTo(origin.x, CANVAS_SIZE);
    ctx.stroke();
  }, [state.showAxes, gameToCanvas, transform.scale]);

  const drawOrigin = useCallback((ctx: CanvasRenderingContext2D) => {
    if (!state.showOrigin) return;

    const origin = gameToCanvas({ x: 0, y: 0 });
    ctx.fillStyle = '#EF4444';
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 2 / transform.scale;

    ctx.beginPath();
    ctx.arc(origin.x, origin.y, 8 / transform.scale, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Label
    ctx.fillStyle = '#FFFFFF';
    ctx.font = `${14 / transform.scale}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.fillText('(0,0)', origin.x, origin.y - 15 / transform.scale);
  }, [state.showOrigin, gameToCanvas, transform.scale]);

  const drawRegion = useCallback((ctx: CanvasRenderingContext2D, region: Region) => {
    if (!state.showRegions || region.coordinates.length < 3) return;

    const canvasCoords = region.coordinates.map(gameToCanvas);
    const isSelected = state.selectedItem?.id === region.id;

    // Fill
    ctx.globalAlpha = 0.3;
    ctx.fillStyle = region.color || '#3B82F6';
    ctx.beginPath();
    ctx.moveTo(canvasCoords[0].x, canvasCoords[0].y);
    for (let i = 1; i < canvasCoords.length; i++) {
      ctx.lineTo(canvasCoords[i].x, canvasCoords[i].y);
    }
    ctx.closePath();
    ctx.fill();

    // Outline
    ctx.globalAlpha = 1.0;
    ctx.strokeStyle = region.color || '#3B82F6';
    ctx.lineWidth = (isSelected ? 3 : 1) / transform.scale;
    ctx.stroke();
  }, [state.showRegions, state.selectedItem, gameToCanvas, transform.scale]);

  const drawPath = useCallback((ctx: CanvasRenderingContext2D, path: Path) => {
    if (!state.showPaths || path.coordinates.length < 2) return;

    const canvasCoords = path.coordinates.map(gameToCanvas);
    const isSelected = state.selectedItem?.id === path.id;

    ctx.strokeStyle = path.color || '#10B981';
    ctx.lineWidth = (isSelected ? 3 : 1) / transform.scale;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();
    ctx.moveTo(canvasCoords[0].x, canvasCoords[0].y);
    for (let i = 1; i < canvasCoords.length; i++) {
      ctx.lineTo(canvasCoords[i].x, canvasCoords[i].y);
    }
    ctx.stroke();
  }, [state.showPaths, state.selectedItem, gameToCanvas, transform.scale]);

  const drawPoint = useCallback((ctx: CanvasRenderingContext2D, point: Point) => {
    const canvasPos = gameToCanvas(point.coordinate);
    const isSelected = state.selectedItem?.id === point.id;

    ctx.fillStyle = point.type === 'landmark' ? '#F59E0B' : '#8B5CF6';
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = (isSelected ? 3 : 2) / transform.scale;

    ctx.beginPath();
    ctx.arc(canvasPos.x, canvasPos.y, 6 / transform.scale, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Label
    ctx.fillStyle = '#FFFFFF';
    ctx.font = `${12 / transform.scale}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.fillText(point.name, canvasPos.x, canvasPos.y + 20 / transform.scale);
  }, [state.selectedItem, gameToCanvas, transform.scale]);

  // Main render function
  const render = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size to fill container
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    // Clear canvas
    ctx.fillStyle = '#1F2937';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Apply transform
    ctx.save();
    ctx.translate(transform.x, transform.y);
    ctx.scale(transform.scale, transform.scale);

    // Draw background image
    if (state.showBackground && backgroundImage) {
      ctx.drawImage(backgroundImage, 0, 0, CANVAS_SIZE, CANVAS_SIZE);
    }

    // Draw grid, axes, origin
    drawGrid(ctx);
    drawAxes(ctx);
    drawOrigin(ctx);

    // Draw regions, paths, points
    regions.forEach(region => drawRegion(ctx, region));
    paths.forEach(path => drawPath(ctx, path));
    points.forEach(point => drawPoint(ctx, point));

    // Draw current drawing
    if (state.isDrawing && state.currentDrawing.length > 0) {
      const canvasCoords = state.currentDrawing.map(gameToCanvas);
      
      ctx.strokeStyle = '#22C55E';
      ctx.lineWidth = 2 / transform.scale;
      ctx.setLineDash([8 / transform.scale, 4 / transform.scale]);

      if (state.tool === 'polygon' && canvasCoords.length >= 3) {
        ctx.fillStyle = '#22C55E40';
        ctx.beginPath();
        ctx.moveTo(canvasCoords[0].x, canvasCoords[0].y);
        for (let i = 1; i < canvasCoords.length; i++) {
          ctx.lineTo(canvasCoords[i].x, canvasCoords[i].y);
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      } else if (state.tool === 'linestring' && canvasCoords.length >= 2) {
        ctx.beginPath();
        ctx.moveTo(canvasCoords[0].x, canvasCoords[0].y);
        for (let i = 1; i < canvasCoords.length; i++) {
          ctx.lineTo(canvasCoords[i].x, canvasCoords[i].y);
        }
        ctx.stroke();
      }

      ctx.setLineDash([]);
    }

    ctx.restore();
  }, [
    transform,
    state,
    backgroundImage,
    regions,
    paths,
    points,
    gameToCanvas,
    drawGrid,
    drawAxes,
    drawOrigin,
    drawRegion,
    drawPath,
    drawPoint
  ]);

  // Render on state changes
  useEffect(() => {
    render();
  }, [render]);

  // Handle clicks
  const handleClick = useCallback((e: React.MouseEvent) => {
    if (isDragging) return; // Don't process clicks during drag
    
    const gameCoord = screenToGame(e.clientX, e.clientY);
    
    if (state.tool === 'select') {
      // Simple selection - find the first item that contains the point
      // Check points first (smallest targets)
      for (const point of points) {
        const distance = Math.sqrt(
          Math.pow(gameCoord.x - point.coordinate.x, 2) +
          Math.pow(gameCoord.y - point.coordinate.y, 2)
        );
        if (distance <= 10) {
          onSelectItem(point);
          return;
        }
      }

      // Check regions
      for (const region of regions) {
        if (region.coordinates.length >= 3) {
          // Point-in-polygon test
          let inside = false;
          const polygon = region.coordinates;
          for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
            if (((polygon[i].y > gameCoord.y) !== (polygon[j].y > gameCoord.y)) &&
                (gameCoord.x < (polygon[j].x - polygon[i].x) * (gameCoord.y - polygon[i].y) / (polygon[j].y - polygon[i].y) + polygon[i].x)) {
              inside = !inside;
            }
          }
          if (inside) {
            onSelectItem(region);
            return;
          }
        }
      }

      // Check paths
      for (const path of paths) {
        if (path.coordinates.length >= 2) {
          // Check distance to path segments
          let minDistance = Infinity;
          for (let i = 0; i < path.coordinates.length - 1; i++) {
            const start = path.coordinates[i];
            const end = path.coordinates[i + 1];
            
            const A = gameCoord.x - start.x;
            const B = gameCoord.y - start.y;
            const C = end.x - start.x;
            const D = end.y - start.y;

            const dot = A * C + B * D;
            const lenSq = C * C + D * D;
            
            let param = lenSq !== 0 ? dot / lenSq : 0;
            param = Math.max(0, Math.min(1, param));
            
            const xx = start.x + param * C;
            const yy = start.y + param * D;
            
            const dx = gameCoord.x - xx;
            const dy = gameCoord.y - yy;
            
            const distance = Math.sqrt(dx * dx + dy * dy);
            minDistance = Math.min(minDistance, distance);
          }
          
          if (minDistance <= 15) {
            onSelectItem(path);
            return;
          }
        }
      }

      // No selection found
      onSelectItem(null);
    } else {
      // Drawing tools
      onClick(gameCoord);
    }
  }, [
    isDragging,
    state.tool,
    points,
    regions,
    paths,
    screenToGame,
    onSelectItem,
    onClick
  ]);

  return (
    <div ref={containerRef} className="flex-1 bg-gray-800 overflow-hidden">
      <canvas
        ref={canvasRef}
        className="w-full h-full cursor-crosshair"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onClick={handleClick}
        onWheel={handleWheel}
        style={{ display: 'block' }}
      />
    </div>
  );
};
