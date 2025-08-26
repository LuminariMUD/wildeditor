import React, { useState, useEffect } from 'react';
import { X, Save } from 'lucide-react';

export interface RegionHint {
  id?: number;
  region_vnum?: number;
  hint_category: string;
  hint_text: string;
  priority: number;
  seasonal_weight?: Record<string, number> | null;
  weather_conditions?: string | string[] | null;
  time_of_day_weight?: Record<string, number> | null;
  is_active?: boolean;
}

interface HintEditorProps {
  hint?: RegionHint;
  regionVnum: number;
  onSave: (hint: Omit<RegionHint, 'id' | 'region_vnum'>) => void;
  onCancel: () => void;
  isOpen: boolean;
}

const HINT_CATEGORIES = [
  { value: 'atmosphere', label: 'Atmosphere', icon: '🌫️' },
  { value: 'fauna', label: 'Fauna', icon: '🦎' },
  { value: 'flora', label: 'Flora', icon: '🌿' },
  { value: 'geography', label: 'Geography', icon: '⛰️' },
  { value: 'sounds', label: 'Sounds', icon: '🔊' },
  { value: 'scents', label: 'Scents', icon: '👃' },
  { value: 'weather_influence', label: 'Weather', icon: '🌦️' },
  { value: 'mystical', label: 'Mystical', icon: '✨' },
  { value: 'landmarks', label: 'Landmarks', icon: '🏛️' },
  { value: 'resources', label: 'Resources', icon: '💎' },
  { value: 'seasonal_changes', label: 'Seasonal', icon: '🍂' },
  { value: 'time_of_day', label: 'Time of Day', icon: '🌅' }
];

const WEATHER_CONDITIONS = ['clear', 'cloudy', 'rainy', 'stormy', 'lightning'];
const SEASONS = ['spring', 'summer', 'autumn', 'winter'];
const TIMES_OF_DAY = ['dawn', 'morning', 'midday', 'afternoon', 'evening', 'night'];

export const HintEditor: React.FC<HintEditorProps> = ({ 
  hint, 
  onSave, 
  onCancel, 
  isOpen 
}) => {
  const [category, setCategory] = useState(hint?.hint_category || 'atmosphere');
  const [text, setText] = useState(hint?.hint_text || '');
  const [priority, setPriority] = useState(hint?.priority || 5);
  const [selectedWeather, setSelectedWeather] = useState<string[]>(() => {
    if (hint?.weather_conditions) {
      // Handle both string and array formats
      if (typeof hint.weather_conditions === 'string') {
        return hint.weather_conditions.split(',').map(w => w.trim());
      } else if (Array.isArray(hint.weather_conditions)) {
        return hint.weather_conditions;
      }
    }
    return ['clear', 'cloudy', 'rainy', 'stormy', 'lightning'];
  });
  const [useSeasonalWeight, setUseSeasonalWeight] = useState(!!hint?.seasonal_weight);
  const [seasonalWeights, setSeasonalWeights] = useState<Record<string, number>>(
    hint?.seasonal_weight || { spring: 1.0, summer: 1.0, autumn: 1.0, winter: 1.0 }
  );
  const [useTimeWeight, setUseTimeWeight] = useState(!!hint?.time_of_day_weight);
  const [timeWeights, setTimeWeights] = useState<Record<string, number>>(
    hint?.time_of_day_weight || { 
      dawn: 1.0, morning: 1.0, midday: 1.0, 
      afternoon: 1.0, evening: 1.0, night: 1.0 
    }
  );
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (hint) {
      setCategory(hint.hint_category);
      setText(hint.hint_text);
      setPriority(hint.priority);
      if (hint.weather_conditions) {
        // Handle both string and array formats
        if (typeof hint.weather_conditions === 'string') {
          setSelectedWeather(hint.weather_conditions.split(',').map(w => w.trim()));
        } else if (Array.isArray(hint.weather_conditions)) {
          setSelectedWeather(hint.weather_conditions);
        }
      }
      setUseSeasonalWeight(!!hint.seasonal_weight);
      if (hint.seasonal_weight) {
        setSeasonalWeights(hint.seasonal_weight);
      }
      setUseTimeWeight(!!hint.time_of_day_weight);
      if (hint.time_of_day_weight) {
        setTimeWeights(hint.time_of_day_weight);
      }
    }
  }, [hint]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!text.trim()) {
      newErrors.text = 'Hint text is required';
    } else if (text.trim().length < 10) {
      newErrors.text = 'Hint text must be at least 10 characters';
    } else if (text.length > 1000) {
      newErrors.text = 'Hint text must be less than 1000 characters';
    }
    
    if (priority < 1 || priority > 10) {
      newErrors.priority = 'Priority must be between 1 and 10';
    }
    
    if (selectedWeather.length === 0) {
      newErrors.weather = 'At least one weather condition must be selected';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (!validate()) return;
    
    const hintData: Omit<RegionHint, 'id' | 'region_vnum'> = {
      hint_category: category,
      hint_text: text.trim(),
      priority,
      weather_conditions: selectedWeather.join(','),
      seasonal_weight: useSeasonalWeight ? seasonalWeights : null,
      time_of_day_weight: useTimeWeight ? timeWeights : null,
      is_active: true
    };
    
    onSave(hintData);
  };

  const toggleWeather = (weather: string) => {
    setSelectedWeather(prev => 
      prev.includes(weather) 
        ? prev.filter(w => w !== weather)
        : [...prev, weather]
    );
  };

  const updateSeasonalWeight = (season: string, value: number) => {
    setSeasonalWeights(prev => ({ ...prev, [season]: value }));
  };

  const updateTimeWeight = (time: string, value: number) => {
    setTimeWeights(prev => ({ ...prev, [time]: value }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-white">
            {hint ? 'Edit Hint' : 'Add New Hint'}
          </h2>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-blue-500"
            >
              {HINT_CATEGORIES.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.icon} {cat.label}
                </option>
              ))}
            </select>
          </div>

          {/* Text */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Hint Text
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              className={`w-full bg-gray-800 border rounded px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 min-h-[100px] ${
                errors.text ? 'border-red-500' : 'border-gray-600'
              }`}
              placeholder="Enter a descriptive hint that enhances immersion..."
            />
            {errors.text && (
              <p className="text-red-400 text-xs mt-1">{errors.text}</p>
            )}
            <p className="text-gray-500 text-xs mt-1">
              {text.length}/1000 characters
            </p>
          </div>

          {/* Priority */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Priority: {priority}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={priority}
              onChange={(e) => setPriority(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Low (1)</span>
              <span>Medium (5)</span>
              <span>High (10)</span>
            </div>
          </div>

          {/* Weather Conditions */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Weather Conditions
            </label>
            <div className="flex flex-wrap gap-2">
              {WEATHER_CONDITIONS.map(weather => (
                <button
                  key={weather}
                  onClick={() => toggleWeather(weather)}
                  className={`px-3 py-1 rounded text-sm transition-colors ${
                    selectedWeather.includes(weather)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {weather}
                </button>
              ))}
            </div>
            {errors.weather && (
              <p className="text-red-400 text-xs mt-1">{errors.weather}</p>
            )}
          </div>

          {/* Seasonal Weights */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-300 mb-2">
              <input
                type="checkbox"
                checked={useSeasonalWeight}
                onChange={(e) => setUseSeasonalWeight(e.target.checked)}
                className="rounded"
              />
              Seasonal Weights
            </label>
            {useSeasonalWeight && (
              <div className="space-y-2 ml-6">
                {SEASONS.map(season => (
                  <div key={season} className="flex items-center gap-3">
                    <span className="text-xs text-gray-400 w-16 capitalize">
                      {season}
                    </span>
                    <input
                      type="range"
                      min="0"
                      max="2"
                      step="0.1"
                      value={seasonalWeights[season] || 1.0}
                      onChange={(e) => updateSeasonalWeight(season, parseFloat(e.target.value))}
                      className="flex-1"
                    />
                    <span className="text-xs text-gray-400 w-10">
                      {(seasonalWeights[season] || 1.0).toFixed(1)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Time of Day Weights */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-300 mb-2">
              <input
                type="checkbox"
                checked={useTimeWeight}
                onChange={(e) => setUseTimeWeight(e.target.checked)}
                className="rounded"
              />
              Time of Day Weights
            </label>
            {useTimeWeight && (
              <div className="space-y-2 ml-6">
                {TIMES_OF_DAY.map(time => (
                  <div key={time} className="flex items-center gap-3">
                    <span className="text-xs text-gray-400 w-20 capitalize">
                      {time}
                    </span>
                    <input
                      type="range"
                      min="0"
                      max="2"
                      step="0.1"
                      value={timeWeights[time] || 1.0}
                      onChange={(e) => updateTimeWeight(time, parseFloat(e.target.value))}
                      className="flex-1"
                    />
                    <span className="text-xs text-gray-400 w-10">
                      {(timeWeights[time] || 1.0).toFixed(1)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 mt-6">
          <button
            onClick={onCancel}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            {hint ? 'Update' : 'Create'} Hint
          </button>
        </div>
      </div>
    </div>
  );
};