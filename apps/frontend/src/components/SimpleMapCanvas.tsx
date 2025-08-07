import { useRef, useEffect, useCallback, useState, FC } from 'react';
import { Coordinate, Region, Path, EditorState } from '../types';
import { SelectionContextMenu } from './SelectionContextMenu';

interface SelectionCandidate {
  item: Region | Path;
  type: 'region' | 'path';
  distance?: number;
}

interface SimpleMapCanvasProps {
  state: EditorState;
  regions: Region[];
  paths: Path[];
  onMouseMove: (coordinate: Coordinate) => void;
  onClick: (coordinate: Coordinate) => void;
  onSelectItem: (item: Region | Path | null) => void;
  onZoomChange: (zoom: number) => void;
  centerOnCoordinate?: Coordinate | null;
  // Add these props for enhanced selection
  hiddenRegions?: Set<number>;
  hiddenPaths?: Set<number>;
  onToggleItemVisibility?: (type: 'region' | 'path', vnum: number) => void;
}

export const SimpleMapCanvas: FC<SimpleMapCanvasProps> = ({
  state,
  regions,
  paths,
  onMouseMove,
  onClick,
  onSelectItem,
  onZoomChange,
  centerOnCoordinate,
  hiddenRegions = new Set(),
  hiddenPaths = new Set(),
  onToggleItemVisibility = () => {}
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [backgroundImage, setBackgroundImage] = useState<HTMLImageElement | null>(null);
  
  // Selection context menu state
  const [selectionCandidates, setSelectionCandidates] = useState<SelectionCandidate[]>([]);
  const [contextMenuPosition, setContextMenuPosition] = useState<{ x: number; y: number } | null>(null);
  
  // Transform state - all in one place for reliability
  const [transform, setTransform] = useState({
    x: 0,      // Pan offset X
    y: 0,      // Pan offset Y  
    scale: 1   // Zoom scale
  });

  // Mouse state for panning
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Track last zoom to detect external changes
  const isInternalZoomRef = useRef(false);

  // Close context menu when clicking elsewhere
  const closeContextMenu = useCallback(() => {
    setContextMenuPosition(null);
    setSelectionCandidates([]);
  }, []);

  // Close context menu when clicking elsewhere or pressing escape
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (contextMenuPosition) {
        // Only close if the click is NOT on the canvas or context menu
        const canvas = canvasRef.current;
        const target = event.target as Element;
        
        // Don't close if clicking on canvas (let canvas handle it)
        if (canvas && canvas.contains(target)) {
          return;
        }
        
        // Don't close if clicking inside context menu
        if (target.closest('.fixed.bg-gray-800')) {
          return;
        }
        
        closeContextMenu();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && contextMenuPosition) {
        closeContextMenu();
      }
    };

    if (contextMenuPosition) {
      document.addEventListener('click', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
      
      return () => {
        document.removeEventListener('click', handleClickOutside);
        document.removeEventListener('keydown', handleEscape);
      };
    }
  }, [contextMenuPosition, closeContextMenu]);

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
    const newScale = state.zoom / 100;
    
    setTransform(prev => {
      // Only adjust transform for external zoom changes (status bar, not mouse wheel)
      // Mouse wheel zoom handles its own transform updates
      if (!isInternalZoomRef.current && prev.scale !== newScale) {
        const canvas = canvasRef.current;
        if (canvas) {
          const rect = canvas.getBoundingClientRect();
          const centerX = rect.width / 2;
          const centerY = rect.height / 2;
          
          // Calculate the scaling ratio
          const scaleRatio = newScale / prev.scale;
          
          // Adjust transform to keep the center point fixed
          return {
            x: centerX - (centerX - prev.x) * scaleRatio,
            y: centerY - (centerY - prev.y) * scaleRatio,
            scale: newScale
          };
        }
      }
      
      // Reset the internal zoom flag
      isInternalZoomRef.current = false;
      
      // If scale hasn't changed or canvas unavailable, just update scale
      return {
        ...prev,
        scale: newScale
      };
    });
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
    e.preventDefault();

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Calculate zoom
    const zoomDelta = e.deltaY > 0 ? -10 : 10;
    const newZoom = Math.max(25, Math.min(2000, state.zoom + zoomDelta));
    const newScale = newZoom / 100;

    // Zoom towards mouse position
    const scaleRatio = newScale / transform.scale;
    const newTransform = {
      x: mouseX - (mouseX - transform.x) * scaleRatio,
      y: mouseY - (mouseY - transform.y) * scaleRatio,
      scale: newScale
    };

    // Set flag to indicate this is an internal zoom change
    isInternalZoomRef.current = true;
    
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
    const pixelRatio = window.devicePixelRatio || 1;
    const baseLineWidth = (1 / transform.scale) / pixelRatio;
    ctx.lineWidth = Math.max((0.25 / transform.scale) / pixelRatio, baseLineWidth); // Thinner grid lines but still visible
    ctx.lineCap = 'square'; // Pixel-perfect line caps
    ctx.lineJoin = 'miter'; // Sharp corners
    ctx.setLineDash([(2 / transform.scale) / pixelRatio, (2 / transform.scale) / pixelRatio]);

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
    const pixelRatio = window.devicePixelRatio || 1;
    const baseLineWidth = (2 / transform.scale) / pixelRatio;
    ctx.lineWidth = Math.max((1 / transform.scale) / pixelRatio, baseLineWidth); // 2 pixels at 100% zoom for better visibility
    ctx.lineCap = 'square'; // Pixel-perfect line caps
    ctx.lineJoin = 'miter'; // Sharp corners

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
    const baseLineWidth = 2 / transform.scale;
    ctx.lineWidth = Math.max(1 / transform.scale, baseLineWidth); // 2 pixels at 100% zoom
    ctx.lineCap = 'square'; // Pixel-perfect line caps
    ctx.lineJoin = 'miter'; // Sharp corners

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

    // Outline - exactly 1 pixel at 100% zoom, represents room boundary
    // Scales proportionally: 100%=1px, 200%=2px, 400%=4px, 2000%=20px
    ctx.globalAlpha = 1.0;
    // Region color - brighter when selected for visibility without changing width
    ctx.strokeStyle = isSelected ? '#22C55E' : (region.color || '#3B82F6');
    // Account for device pixel ratio scaling
    const pixelRatio = window.devicePixelRatio || 1;
    ctx.lineWidth = (1 / transform.scale) / pixelRatio;
    
    // Debug log to verify deployment (remove after testing)
    if (isSelected) {
      console.log(`[Region Rendering] Selected region "${region.name || 'Unnamed'}" - Color: ${ctx.strokeStyle}, Width: ${ctx.lineWidth}, Scale: ${transform.scale}, PixelRatio: ${pixelRatio}`);
    }
    
    ctx.lineCap = 'square'; // Remove anti-aliasing on line caps
    ctx.lineJoin = 'miter'; // Sharp corners for pixel-perfect rendering
    ctx.stroke();
  }, [state.showRegions, state.selectedItem, gameToCanvas, transform.scale]);

  const drawPath = useCallback((ctx: CanvasRenderingContext2D, path: Path) => {
    if (!state.showPaths || path.coordinates.length < 2) return;

    const canvasCoords = path.coordinates.map(gameToCanvas);
    const isSelected = state.selectedItem?.id === path.id;

    // Path color - brighter when selected for visibility without changing width
    ctx.strokeStyle = isSelected ? '#22C55E' : (path.color || '#10B981');
    // Always exactly 1 pixel at 100% zoom - represents 1 room width in game
    // Scales proportionally: 100%=1px, 200%=2px, 400%=4px, 2000%=20px
    // Account for device pixel ratio scaling
    const pixelRatio = window.devicePixelRatio || 1;
    ctx.lineWidth = (1 / transform.scale) / pixelRatio;
    
    // Debug log to verify deployment (remove after testing)
    if (isSelected) {
      console.log(`[Path Rendering] Selected path "${path.name || 'Unnamed'}" - Color: ${ctx.strokeStyle}, Width: ${ctx.lineWidth}, Scale: ${transform.scale}, PixelRatio: ${pixelRatio}, Zoom: ${state.zoom}%`);
    }
    
    ctx.lineCap = 'square'; // Remove anti-aliasing on line caps  
    ctx.lineJoin = 'miter'; // Sharp corners for pixel-perfect rendering

    ctx.beginPath();
    ctx.moveTo(canvasCoords[0].x, canvasCoords[0].y);
    for (let i = 1; i < canvasCoords.length; i++) {
      ctx.lineTo(canvasCoords[i].x, canvasCoords[i].y);
    }
    ctx.stroke();
  }, [state.showPaths, state.selectedItem, gameToCanvas, transform.scale, state.zoom]);

  // Main render function
  const render = useCallback(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Handle high-DPI displays properly
    const containerRect = container.getBoundingClientRect();
    const pixelRatio = window.devicePixelRatio || 1;
    
    // Set canvas size accounting for device pixel ratio
    canvas.width = containerRect.width * pixelRatio;
    canvas.height = containerRect.height * pixelRatio;
    
    // Scale canvas back down for CSS display
    canvas.style.width = `${containerRect.width}px`;
    canvas.style.height = `${containerRect.height}px`;
    
    // Scale the context to match device pixel ratio
    ctx.scale(pixelRatio, pixelRatio);

    // Disable anti-aliasing for pixel-perfect rendering
    ctx.imageSmoothingEnabled = false;
    if ('webkitImageSmoothingEnabled' in ctx) ctx.webkitImageSmoothingEnabled = false;
    if ('mozImageSmoothingEnabled' in ctx) ctx.mozImageSmoothingEnabled = false;
    if ('msImageSmoothingEnabled' in ctx) ctx.msImageSmoothingEnabled = false;

    // Clear canvas
    ctx.fillStyle = '#1F2937';
    ctx.fillRect(0, 0, containerRect.width, containerRect.height);

    // Apply transform
    ctx.save();
    ctx.translate(transform.x, transform.y);
    ctx.scale(transform.scale, transform.scale);

    // Draw background image with nearest-neighbor scaling
    if (state.showBackground && backgroundImage) {
      ctx.drawImage(backgroundImage, 0, 0, CANVAS_SIZE, CANVAS_SIZE);
    }

    // Draw grid, axes, origin
    drawGrid(ctx);
    drawAxes(ctx);
    drawOrigin(ctx);

    // Draw regions and paths
    regions.forEach(region => drawRegion(ctx, region));
    paths.forEach(path => drawPath(ctx, path));

    // Draw current drawing
    if (state.isDrawing && state.currentDrawing.length > 0) {
      const canvasCoords = state.currentDrawing.map(gameToCanvas);
      
      ctx.strokeStyle = '#22C55E';
      // Drawing feedback also uses 1 pixel at 100% zoom for consistency
      ctx.lineWidth = 1 / transform.scale;
      ctx.lineCap = 'square';
      ctx.lineJoin = 'miter';
      ctx.setLineDash([8 / transform.scale, 4 / transform.scale]);

      if (state.tool === 'region' && canvasCoords.length >= 3) {
        ctx.fillStyle = '#22C55E40';
        ctx.beginPath();
        ctx.moveTo(canvasCoords[0].x, canvasCoords[0].y);
        for (let i = 1; i < canvasCoords.length; i++) {
          ctx.lineTo(canvasCoords[i].x, canvasCoords[i].y);
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      } else if (state.tool === 'path' && canvasCoords.length >= 2) {
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
    gameToCanvas,
    drawGrid,
    drawAxes,
    drawOrigin,
    drawRegion,
    drawPath
  ]);

  // Render on state changes
  useEffect(() => {
    render();
  }, [render]);

  // Handle container resize
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const resizeObserver = new ResizeObserver(() => {
      render();
    });

    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
    };
  }, [render]);

  // Handle clicks
  const handleClick = useCallback((e: React.MouseEvent) => {
    if (isDragging) return; // Don't process clicks during drag
    
    const gameCoord = screenToGame(e.clientX, e.clientY);
    
    console.log('[Selection Debug] HandleClick triggered:', {
      tool: state.tool,
      coordinate: gameCoord,
      hasContextMenu: !!contextMenuPosition
    });
    
    // Close any existing context menu first
    if (contextMenuPosition) {
      console.log('[Selection Debug] Closing existing context menu');
      closeContextMenu();
      return; // Don't process new selection on same click that closes menu
    }
    
    if (state.tool === 'select') {
      // Enhanced selection - find ALL overlapping VISIBLE items only
      // Hidden items should be completely click-through
      const candidates: Array<{
        item: Region | Path;
        type: 'region' | 'path';
        distance?: number;
        area?: number;
      }> = [];

      console.log('[Selection Debug] Click at:', gameCoord, 'Available regions:', regions.length, 'Region names:', regions.map(r => r.name));

      // Check ONLY visible regions (regions array is already filtered by App.tsx)
      // Iterate in reverse order so smaller regions drawn later are prioritized
      for (let i = regions.length - 1; i >= 0; i--) {
        const region = regions[i];
        
        console.log(`[Selection Debug] Checking region ${region.name} (vnum: ${region.vnum}, type: ${region.region_type})`);
        console.log(`[Selection Debug] Region coords:`, region.coordinates);
        
        // Skip if region is hidden (double-check even though regions array should be filtered)
        if (hiddenRegions.has(region.vnum)) {
          console.log('[Selection Debug] Skipping hidden region:', region.name, region.vnum);
          continue;
        }
        
        if (region.coordinates.length >= 3) {
          // Point-in-polygon test
          let inside = false;
          const polygon = region.coordinates;
          for (let j = 0, k = polygon.length - 1; j < polygon.length; k = j++) {
            if (((polygon[j].y > gameCoord.y) !== (polygon[k].y > gameCoord.y)) &&
                (gameCoord.x < (polygon[k].x - polygon[j].x) * (gameCoord.y - polygon[j].y) / (polygon[k].y - polygon[j].y) + polygon[j].x)) {
              inside = !inside;
            }
          }
          console.log(`[Selection Debug] Point-in-polygon test for ${region.name}: ${inside}`);
          if (inside) {
            // Calculate area for sorting preference (smaller areas preferred)
            let area = 0;
            for (let j = 0; j < polygon.length; j++) {
              const k = (j + 1) % polygon.length;
              area += polygon[j].x * polygon[k].y;
              area -= polygon[k].x * polygon[j].y;
            }
            area = Math.abs(area) / 2;
            
            console.log(`[Selection Debug] Adding region ${region.name} as candidate with area ${area}`);
            candidates.push({
              item: region,
              type: 'region',
              area
            });
          }
        } else {
          console.log(`[Selection Debug] Region ${region.name} has insufficient coordinates:`, region.coordinates.length);
        }
      }

      // Check ONLY visible paths (paths array is already filtered by App.tsx)
      for (const path of paths) {
        // Skip if path is hidden (double-check even though paths array should be filtered)
        if (hiddenPaths.has(path.vnum)) continue;
        
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
            candidates.push({
              item: path,
              type: 'path',
              distance: minDistance
            });
          }
        }
      }

      console.log(`[Selection Debug] Found ${candidates.length} candidates:`, candidates.map(c => `${c.type}: ${c.item.name}`));

      // Handle selection based on candidates
      if (candidates.length === 0) {
        console.log('[Selection Debug] No candidates - clearing selection');
        onSelectItem(null);
      } else if (candidates.length === 1) {
        console.log('[Selection Debug] Single candidate - selecting:', candidates[0].item.name);
        onSelectItem(candidates[0].item);
      } else {
        console.log('[Selection Debug] Multiple candidates - showing context menu');
        // Multiple candidates - show context menu for user choice
        setSelectionCandidates(candidates.map(c => ({
          item: c.item,
          type: c.type,
          distance: c.distance
        })));
        setContextMenuPosition({ x: e.clientX, y: e.clientY });
      }
    } else {
      // Drawing tools
      onClick(gameCoord);
    }
  }, [
    isDragging,
    state.tool,
    regions,
    paths,
    screenToGame,
    onSelectItem,
    onClick,
    hiddenRegions,
    hiddenPaths,
    contextMenuPosition,
    closeContextMenu
  ]);

  return (
    <div ref={containerRef} className="w-full h-full bg-gray-800 overflow-hidden">
      <canvas
        ref={canvasRef}
        className="w-full h-full cursor-crosshair block"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onClick={handleClick}
        onWheel={handleWheel}
      />
      
      {/* Context menu for overlapping selections */}
      {contextMenuPosition && selectionCandidates.length > 0 && (
        <SelectionContextMenu
          candidates={selectionCandidates}
          position={contextMenuPosition}
          onSelect={(item) => {
            onSelectItem(item);
            closeContextMenu();
          }}
          onClose={closeContextMenu}
          onToggleVisibility={onToggleItemVisibility}
        />
      )}
    </div>
  );
};