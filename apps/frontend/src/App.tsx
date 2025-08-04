import React, { useEffect } from 'react';
import { AuthCallback } from './components/AuthCallback';
import { ProtectedRoute } from './components/ProtectedRoute';
import { MapCanvas } from './components/MapCanvas';
import { ToolPalette } from './components/ToolPalette';
import { LayerControls } from './components/LayerControls';
import { PropertiesPanel } from './components/PropertiesPanel';
import { StatusBar } from './components/StatusBar';
import { ErrorNotification } from './components/ErrorNotification';
import { LoadingOverlay } from './components/LoadingOverlay';
import { useEditor } from './hooks/useEditor';
import { useAuth } from './hooks/useAuth';
import { User, Settings, LogOut } from 'lucide-react';

function App() {
  const { user, signOut } = useAuth();
  const {
    state,
    regions,
    paths,
    points,
    loading,
    error,
    setTool,
    setZoom,
    setMousePosition,
    toggleLayer,
    selectItem,
    handleCanvasClick,
    finishDrawing,
    cancelDrawing,
    clearError,
    updateSelectedItem
  } = useEditor();

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      
      switch (e.key.toLowerCase()) {
        case 's':
          setTool('select');
          break;
        case 'p':
          setTool('point');
          break;
        case 'g':
          setTool('polygon');
          break;
        case 'l':
          setTool('linestring');
          break;
        case 'escape':
          if (state.isDrawing) {
            cancelDrawing();
          } else {
            selectItem(null);
          }
          break;
        case 'enter':
          if (state.isDrawing) {
            finishDrawing();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [setTool, selectItem, cancelDrawing, state.isDrawing, finishDrawing]);

  // Handle auth callback route
  if (window.location.pathname === '/auth/callback') {
    return <AuthCallback />;
  }

  const handleSignOut = async () => {
    await signOut();
  };

  return (
    <ProtectedRoute>
      <div className="h-screen bg-gray-900 flex flex-col">
        {/* Header */}
        <header className="bg-gray-900 border-b border-gray-700 px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-white">Luminari Wilderness Editor</h1>
            <div className="text-sm text-gray-400">
              Zone: Darkwood Forest • Build: v1.0.0-dev
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button className="text-gray-400 hover:text-white p-2 rounded-lg hover:bg-gray-800 transition-colors">
              <Settings size={18} />
            </button>
            <div className="flex items-center gap-2 text-gray-300">
              <User size={16} />
              <span className="text-sm">{user?.email}</span>
            </div>
            <button 
              onClick={handleSignOut}
              className="text-gray-400 hover:text-red-400 p-2 rounded-lg hover:bg-gray-800 transition-colors"
              title="Sign Out"
            >
              <LogOut size={18} />
            </button>
          </div>
        </header>

        {/* Main content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left sidebar */}
          <div className="w-64 bg-gray-900 border-r border-gray-700 flex flex-col">
            <ToolPalette currentTool={state.tool} onToolChange={setTool} />
            <LayerControls
              showGrid={state.showGrid}
              showRegions={state.showRegions}
              showPaths={state.showPaths}
              showBackground={state.showBackground}
              showAxes={state.showAxes}
              showOrigin={state.showOrigin}
              onToggleLayer={toggleLayer}
            />
            <div className="flex-1"></div>
          </div>

          {/* Map canvas */}
          <MapCanvas
            state={state}
            regions={regions}
            paths={paths}
            points={points}
            onMouseMove={setMousePosition}
            onClick={handleCanvasClick}
            onSelectItem={selectItem}
            onZoomChange={setZoom}
          />

          {/* Right sidebar */}
          <div className="w-80 bg-gray-900 border-l border-gray-700 flex flex-col">
            <PropertiesPanel
              selectedItem={state.selectedItem}
              onUpdate={updateSelectedItem}
              onFinishDrawing={finishDrawing}
              isDrawing={state.isDrawing}
            />
          </div>
        </div>

        {/* Status bar */}
        <StatusBar
          mousePosition={state.mousePosition}
          zoom={state.zoom}
          onZoomChange={setZoom}
          regionCount={regions.length}
          pathCount={paths.length}
          loading={loading}
          error={error}
        />
      </div>
      
      {/* Error notifications */}
      <ErrorNotification error={error} onDismiss={clearError} />
      
      {/* Loading overlay */}
      <LoadingOverlay isLoading={loading} message="Loading wilderness data..." />
    </ProtectedRoute>
  );
}

export default App;