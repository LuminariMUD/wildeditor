import { useState, useMemo, useCallback, FC, MouseEvent } from 'react';
import { ChevronDown, ChevronRight, Folder, FolderOpen, Map, Route, MapPin, Eye, EyeOff } from 'lucide-react';
import { Region, Path, Point } from '../types';

interface TreeViewProps {
  regions: Region[];
  paths: Path[];
  points: Point[];
  selectedItem: Region | Path | Point | null;
  onSelectItem: (item: Region | Path | Point | null) => void;
  onCenterOnItem: (item: Region | Path | Point) => void;
  showRegions: boolean;
  showPaths: boolean;
  onToggleLayer: (layer: 'regions' | 'paths') => void;
  hiddenRegions: Set<number>;
  hiddenPaths: Set<number>;
  onToggleItemVisibility: (type: 'region' | 'path', vnum: number) => void;
  hiddenFolders?: Set<string>;
  onToggleFolderVisibility?: (folderId: string) => void;
  // New prop for unsaved items
  unsavedItems?: Set<string>;
}

interface TreeNode {
  id: string;
  name: string;
  type: 'folder' | 'region' | 'path' | 'point';
  data?: Region | Path | Point;
  children?: TreeNode[];
  count?: number;
}

export const TreeView: FC<TreeViewProps> = ({
  regions,
  paths,
  points,
  selectedItem,
  onSelectItem,
  onCenterOnItem,
  showRegions,
  showPaths,
  onToggleLayer,
  hiddenRegions,
  hiddenPaths,
  onToggleItemVisibility,
  hiddenFolders: externalHiddenFolders,
  onToggleFolderVisibility: externalToggleFolderVisibility,
  unsavedItems = new Set()
}) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(['regions', 'paths']));
  const [internalHiddenFolders, setInternalHiddenFolders] = useState<Set<string>>(new Set());
  
  // Use external folder visibility state if provided, otherwise use internal state
  const hiddenFolders = externalHiddenFolders || internalHiddenFolders;
  const toggleFolderVisibility = externalToggleFolderVisibility || ((folderId: string) => {
    setInternalHiddenFolders(prev => {
      const newSet = new Set(prev);
      if (newSet.has(folderId)) {
        newSet.delete(folderId);
      } else {
        newSet.add(folderId);
      }
      return newSet;
    });
  });

  // Group regions by type
  const regionsByType = useMemo(() => {
    const typeMap: Record<number, { name: string; regions: Region[] }> = {
      1: { name: 'Geographic', regions: [] },
      2: { name: 'Encounter', regions: [] },
      3: { name: 'Sector Transform', regions: [] },
      4: { name: 'Sector', regions: [] }
    };

    regions.forEach(region => {
      const type = region.region_type;
      if (typeMap[type]) {
        typeMap[type].regions.push(region);
      }
    });

    return Object.entries(typeMap)
      .filter(([, data]) => data.regions.length > 0)
      .map(([type, data]) => ({
        type: parseInt(type),
        ...data
      }));
  }, [regions]);

  // Group paths by type
  const pathsByType = useMemo(() => {
    const typeMap: Record<number, { name: string; paths: Path[] }> = {
      1: { name: 'Paved Roads', paths: [] },
      2: { name: 'Dirt Roads', paths: [] },
      3: { name: 'Geographic', paths: [] },
      5: { name: 'Rivers', paths: [] },
      6: { name: 'Streams', paths: [] }
    };

    paths.forEach(path => {
      const type = path.path_type;
      if (typeMap[type]) {
        typeMap[type].paths.push(path);
      }
    });

    return Object.entries(typeMap)
      .filter(([, data]) => data.paths.length > 0)
      .map(([type, data]) => ({
        type: parseInt(type),
        ...data
      }));
  }, [paths]);

  // Build tree structure
  const treeData = useMemo(() => {
    const tree: TreeNode[] = [];

    // Regions folder
    if (regions.length > 0) {
      const regionNode: TreeNode = {
        id: 'regions',
        name: 'Regions',
        type: 'folder',
        count: regions.length,
        children: regionsByType.map(group => ({
          id: `region-type-${group.type}`,
          name: `${group.name} (${group.regions.length})`,
          type: 'folder',
          count: group.regions.length,
          children: group.regions
            .sort((a, b) => a.name.localeCompare(b.name))
            .map(region => ({
              id: `region-${region.id || region.vnum}`,
              name: `${region.name} (${region.vnum})`,
              type: 'region' as const,
              data: region
            }))
        }))
      };
      tree.push(regionNode);
    }

    // Paths folder
    if (paths.length > 0) {
      const pathNode: TreeNode = {
        id: 'paths',
        name: 'Paths',
        type: 'folder',
        count: paths.length,
        children: pathsByType.map(group => ({
          id: `path-type-${group.type}`,
          name: `${group.name} (${group.paths.length})`,
          type: 'folder',
          count: group.paths.length,
          children: group.paths
            .sort((a, b) => a.name.localeCompare(b.name))
            .map(path => ({
              id: `path-${path.id || path.vnum}`,
              name: `${path.name} (${path.vnum})`,
              type: 'path' as const,
              data: path
            }))
        }))
      };
      tree.push(pathNode);
    }

    // Points folder (if we have any)
    if (points.length > 0) {
      const pointNode: TreeNode = {
        id: 'points',
        name: 'Points',
        type: 'folder',
        count: points.length,
        children: points
          .sort((a, b) => a.name.localeCompare(b.name))
          .map(point => ({
            id: `point-${point.id}`,
            name: point.name,
            type: 'point' as const,
            data: point
          }))
      };
      tree.push(pointNode);
    }

    return tree;
  }, [regions, paths, points, regionsByType, pathsByType]);

  const toggleExpanded = useCallback((nodeId: string) => {
    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(nodeId)) {
        newSet.delete(nodeId);
      } else {
        newSet.add(nodeId);
      }
      return newSet;
    });
  }, []);

  // Check if an item is hidden due to folder visibility
  const isItemHiddenByFolder = useCallback((node: TreeNode): boolean => {
    // Check if any parent folder is hidden
    const nodeId = node.id;
    
    // For individual items, check their parent folder
    if (nodeId.startsWith('region-type-')) {
      return hiddenFolders.has(nodeId) || hiddenFolders.has('regions');
    }
    if (nodeId.startsWith('path-type-')) {
      return hiddenFolders.has(nodeId) || hiddenFolders.has('paths');
    }
    if (nodeId.startsWith('region-')) {
      // Find parent type folder
      const regionData = node.data as Region;
      const parentTypeId = `region-type-${regionData.region_type}`;
      return hiddenFolders.has(parentTypeId) || hiddenFolders.has('regions');
    }
    if (nodeId.startsWith('path-')) {
      // Find parent type folder
      const pathData = node.data as Path;
      const parentTypeId = `path-type-${pathData.path_type}`;
      return hiddenFolders.has(parentTypeId) || hiddenFolders.has('paths');
    }
    
    return hiddenFolders.has(nodeId);
  }, [hiddenFolders]);

  const handleItemClick = useCallback((node: TreeNode, event: MouseEvent) => {
    event.stopPropagation();
    
    if (node.type === 'folder') {
      toggleExpanded(node.id);
      return;
    }

    if (node.data) {
      onSelectItem(node.data);
      
      // Center on the item if it has coordinates
      if ('coordinates' in node.data && node.data.coordinates.length > 0) {
        // For regions/paths, center on the item directly
        onCenterOnItem(node.data);
      } else if ('coordinate' in node.data) {
        // For points, center on the item directly
        onCenterOnItem(node.data);
      }
    }
  }, [toggleExpanded, onSelectItem, onCenterOnItem]);

  const getIcon = (node: TreeNode, isExpanded: boolean) => {
    switch (node.type) {
      case 'folder':
        return isExpanded ? <FolderOpen size={16} /> : <Folder size={16} />;
      case 'region':
        return <Map size={16} />;
      case 'path':
        return <Route size={16} />;
      case 'point':
        return <MapPin size={16} />;
      default:
        return null;
    }
  };

  const renderNode = (node: TreeNode, depth: number = 0) => {
    const isExpanded = expandedNodes.has(node.id);
    const isSelected = selectedItem && node.data &&
      ((node.data.id && node.data.id === selectedItem.id) ||
       ('vnum' in node.data && 'vnum' in selectedItem && node.data.vnum === selectedItem.vnum));
    
    // Check if this item is unsaved (draft)
    const itemId = node.data?.id || ('vnum' in (node.data || {}) ? (node.data as Region | Path)?.vnum?.toString() : '');
    const isUnsaved = itemId && unsavedItems.has(itemId);
    
    // Check if the item is hidden individually or by folder
    const isIndividuallyHidden = (node.type === 'region' && node.data && 'vnum' in node.data && hiddenRegions.has(node.data.vnum)) ||
                                 (node.type === 'path' && node.data && 'vnum' in node.data && hiddenPaths.has(node.data.vnum));
    const isFolderHidden = isItemHiddenByFolder(node);
    const isHidden = isIndividuallyHidden || isFolderHidden;
    
    const hasChildren = node.children && node.children.length > 0;
    const paddingLeft = depth * 16 + 8;

    return (
      <div key={node.id}>
        <div
          className={`
            flex items-center gap-2 px-2 py-1 text-sm cursor-pointer transition-colors whitespace-nowrap
            ${isSelected 
              ? 'bg-blue-600 text-white' 
              : `${isHidden ? 'text-gray-500' : 'text-gray-300'} hover:bg-gray-800 hover:text-white`
            }
            ${isUnsaved && !isSelected ? 'bg-amber-900/30 border-l-2 border-l-amber-400' : ''}
          `}
          style={{ paddingLeft }}
          onClick={(e) => handleItemClick(node, e)}
        >
          {/* Folder visibility toggle - on the left side of all folders */}
          {node.type === 'folder' && (
            <button
              className="p-1 hover:bg-gray-700 rounded transition-colors opacity-70 hover:opacity-100 flex-shrink-0"
              onClick={(e) => {
                e.stopPropagation();
                toggleFolderVisibility(node.id);
              }}
              title={hiddenFolders.has(node.id) ? `Show ${node.name.toLowerCase()}` : `Hide ${node.name.toLowerCase()}`}
            >
              {hiddenFolders.has(node.id) ? <EyeOff size={12} /> : <Eye size={12} />}
            </button>
          )}

          {/* Individual item visibility toggle - for regions and paths only */}
          {(node.type === 'region' || node.type === 'path') && node.data && 'vnum' in node.data && (
            <button
              className="p-1 hover:bg-gray-700 rounded transition-colors opacity-70 hover:opacity-100 flex-shrink-0"
              onClick={(e) => {
                e.stopPropagation();
                if (node.data && 'vnum' in node.data) {
                  onToggleItemVisibility(node.type as 'region' | 'path', node.data.vnum);
                }
              }}
              title={
                node.type === 'region' 
                  ? (hiddenRegions.has((node.data as Region).vnum) ? 'Show region' : 'Hide region')
                  : (hiddenPaths.has((node.data as Path).vnum) ? 'Show path' : 'Hide path')
              }
            >
              {node.type === 'region' 
                ? (hiddenRegions.has((node.data as Region).vnum) ? <EyeOff size={12} /> : <Eye size={12} />)
                : (hiddenPaths.has((node.data as Path).vnum) ? <EyeOff size={12} /> : <Eye size={12} />)
              }
            </button>
          )}

          {/* Expand/collapse button */}
          {hasChildren && (
            <button
              className="p-0.5 hover:bg-gray-700 rounded transition-colors flex-shrink-0"
              onClick={(e) => {
                e.stopPropagation();
                toggleExpanded(node.id);
              }}
            >
              {isExpanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
            </button>
          )}
          
          {/* Spacer for alignment when no expand button */}
          {!hasChildren && <div className="w-4 flex-shrink-0" />}
          
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <div className={isHidden ? 'opacity-50' : ''}>
              {getIcon(node, isExpanded)}
            </div>
            <span className={`${isHidden ? 'italic opacity-75' : ''}`} title={node.name}>
              {node.name}
            </span>
            {/* Unsaved indicator */}
            {node.data && (
              (() => {
                const itemId = node.data.id || ('vnum' in node.data ? node.data.vnum?.toString() : '');
                return itemId && unsavedItems.has(itemId) ? (
                  <div className="flex items-center gap-1">
                    <span className="text-amber-400 font-bold text-xs bg-amber-900/40 px-1.5 py-0.5 rounded" title="Unsaved draft - not saved to database">
                      DRAFT
                    </span>
                    <span className="text-amber-400 font-bold text-xs" title="Unsaved changes">
                      *
                    </span>
                  </div>
                ) : null;
              })()
            )}
          </div>

          {/* Layer visibility toggle for root folders - now moved to right */}
          {node.id === 'regions' && (
            <button
              className="p-1 hover:bg-gray-700 rounded transition-colors flex-shrink-0 ml-auto"
              onClick={(e) => {
                e.stopPropagation();
                onToggleLayer('regions');
              }}
              title={showRegions ? 'Hide all regions' : 'Show all regions'}
            >
              {showRegions ? <Eye size={12} /> : <EyeOff size={12} />}
            </button>
          )}
          
          {node.id === 'paths' && (
            <button
              className="p-1 hover:bg-gray-700 rounded transition-colors flex-shrink-0 ml-auto"
              onClick={(e) => {
                e.stopPropagation();
                onToggleLayer('paths');
              }}
              title={showPaths ? 'Hide all paths' : 'Show all paths'}
            >
              {showPaths ? <Eye size={12} /> : <EyeOff size={12} />}
            </button>
          )}
        </div>

        {isExpanded && hasChildren && (
          <div>
            {node.children!.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-gray-900 border-b border-gray-700 flex-1 flex flex-col h-full max-h-full overflow-hidden">
      <div className="p-3 border-b border-gray-700 flex-shrink-0">
        <h3 className="text-sm font-medium text-gray-300">Wilderness Objects</h3>
        <div className="text-xs text-gray-500 mt-1">
          {regions.length} regions • {paths.length} paths • {points.length} points
        </div>
      </div>
      
      <div className="flex-1 overflow-auto min-h-0">
        {treeData.length > 0 ? (
          <div className="py-1 w-max">
            {treeData.map(node => renderNode(node))}
          </div>
        ) : (
          <div className="p-4 text-center text-gray-500 text-sm">
            No wilderness objects found
          </div>
        )}
      </div>
    </div>
  );
};
