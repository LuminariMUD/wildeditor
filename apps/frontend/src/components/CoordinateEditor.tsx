import React from 'react';
import { MapPin, Trash2, Plus } from 'lucide-react';

interface Coordinate {
  x: number;
  y: number;
}

interface CoordinateEditorProps {
  coordinates: Coordinate[];
  onChange: (coordinates: Coordinate[]) => void;
  minPoints?: number;
  maxPoints?: number;
  readonly?: boolean;
}

export const CoordinateEditor: React.FC<CoordinateEditorProps> = ({
  coordinates,
  onChange,
  minPoints = 3,
  maxPoints,
  readonly = false
}) => {
  const handleCoordinateChange = (index: number, field: 'x' | 'y', value: string) => {
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return;
    
    const newCoords = [...coordinates];
    newCoords[index] = {
      ...newCoords[index],
      [field]: numValue
    };
    onChange(newCoords);
  };

  const handleAddPoint = () => {
    if (maxPoints && coordinates.length >= maxPoints) return;
    
    // Add a new point near the last point
    const lastPoint = coordinates[coordinates.length - 1];
    const newPoint = {
      x: lastPoint.x + 10,
      y: lastPoint.y + 10
    };
    onChange([...coordinates, newPoint]);
  };

  const handleRemovePoint = (index: number) => {
    if (coordinates.length <= minPoints) return;
    
    const newCoords = coordinates.filter((_, i) => i !== index);
    onChange(newCoords);
  };

  const handleInsertPoint = (afterIndex: number) => {
    if (maxPoints && coordinates.length >= maxPoints) return;
    
    // Insert a point between this point and the next
    const currentPoint = coordinates[afterIndex];
    const nextIndex = (afterIndex + 1) % coordinates.length;
    const nextPoint = coordinates[nextIndex];
    
    const newPoint = {
      x: (currentPoint.x + nextPoint.x) / 2,
      y: (currentPoint.y + nextPoint.y) / 2
    };
    
    const newCoords = [...coordinates];
    newCoords.splice(afterIndex + 1, 0, newPoint);
    onChange(newCoords);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-medium text-gray-300 flex items-center gap-2">
          <MapPin className="w-4 h-4" />
          Polygon Points ({coordinates.length})
        </h4>
        {!readonly && (!maxPoints || coordinates.length < maxPoints) && (
          <button
            onClick={handleAddPoint}
            className="text-xs bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded flex items-center gap-1"
            title="Add point at end"
          >
            <Plus className="w-3 h-3" />
            Add Point
          </button>
        )}
      </div>

      <div className="max-h-48 overflow-y-auto space-y-1 bg-gray-800 rounded-lg p-2">
        {coordinates.map((coord, index) => (
          <div key={index} className="flex items-center gap-2 group">
            <span className="text-xs text-gray-500 w-6">{index + 1}</span>
            
            <div className="flex items-center gap-1 flex-1">
              <span className="text-xs text-gray-400">X:</span>
              <input
                type="number"
                value={coord.x}
                onChange={(e) => handleCoordinateChange(index, 'x', e.target.value)}
                className="w-20 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-xs text-white focus:ring-1 focus:ring-blue-500"
                disabled={readonly}
                step="1"
              />
              
              <span className="text-xs text-gray-400 ml-2">Y:</span>
              <input
                type="number"
                value={coord.y}
                onChange={(e) => handleCoordinateChange(index, 'y', e.target.value)}
                className="w-20 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-xs text-white focus:ring-1 focus:ring-blue-500"
                disabled={readonly}
                step="1"
              />
            </div>

            {!readonly && (
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                {(!maxPoints || coordinates.length < maxPoints) && (
                  <button
                    onClick={() => handleInsertPoint(index)}
                    className="text-gray-400 hover:text-blue-400 p-1"
                    title={`Insert point after #${index + 1}`}
                  >
                    <Plus className="w-3 h-3" />
                  </button>
                )}
                
                {coordinates.length > minPoints && (
                  <button
                    onClick={() => handleRemovePoint(index)}
                    className="text-gray-400 hover:text-red-400 p-1"
                    title={`Remove point #${index + 1}`}
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="text-xs text-gray-500">
        {minPoints && (
          <span>Minimum points: {minPoints}</span>
        )}
        {maxPoints && (
          <span className="ml-3">Maximum points: {maxPoints}</span>
        )}
      </div>
    </div>
  );
};