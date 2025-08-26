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
  // Store as percentages in UI (0-100), convert to decimals (0-1) when saving
  const [seasonalWeights, setSeasonalWeights] = useState<Record<string, number>>(() => {
    if (hint?.seasonal_weight) {
      const weights: Record<string, number> = {};
      for (const [key, val] of Object.entries(hint.seasonal_weight)) {
        weights[key] = val * 100; // Convert from decimal to percentage for UI
      }
      return weights;
    }
    return { spring: 100, summer: 100, autumn: 100, winter: 100 };
  });
  const [useTimeWeight, setUseTimeWeight] = useState(!!hint?.time_of_day_weight);
  // Store as percentages in UI (0-100), convert to decimals (0-1) when saving
  const [timeWeights, setTimeWeights] = useState<Record<string, number>>(() => {
    if (hint?.time_of_day_weight) {
      const weights: Record<string, number> = {};
      for (const [key, val] of Object.entries(hint.time_of_day_weight)) {
        weights[key] = val * 100; // Convert from decimal to percentage for UI
      }
      return weights;
    }
    return { 
      dawn: 100, morning: 100, midday: 100, 
      afternoon: 100, evening: 100, night: 100 
    };
  });
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
        const weights: Record<string, number> = {};
        for (const [key, val] of Object.entries(hint.seasonal_weight)) {
          weights[key] = val * 100; // Convert from decimal to percentage for UI
        }
        setSeasonalWeights(weights);
      }
      setUseTimeWeight(!!hint.time_of_day_weight);
      if (hint.time_of_day_weight) {
        const weights: Record<string, number> = {};
        for (const [key, val] of Object.entries(hint.time_of_day_weight)) {
          weights[key] = val * 100; // Convert from decimal to percentage for UI
        }
        setTimeWeights(weights);
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
    
    // Convert percentages back to decimals for backend
    const convertedSeasonalWeights = useSeasonalWeight ? {} as Record<string, number> : null;
    if (useSeasonalWeight) {
      for (const [key, val] of Object.entries(seasonalWeights)) {
        convertedSeasonalWeights![key] = val / 100; // Convert percentage to decimal
      }
    }
    
    const convertedTimeWeights = useTimeWeight ? {} as Record<string, number> : null;
    if (useTimeWeight) {
      for (const [key, val] of Object.entries(timeWeights)) {
        convertedTimeWeights![key] = val / 100; // Convert percentage to decimal
      }
    }
    
    const hintData: Omit<RegionHint, 'id' | 'region_vnum'> = {
      hint_category: category,
      hint_text: text.trim(),
      priority,
      weather_conditions: selectedWeather.join(','),
      seasonal_weight: convertedSeasonalWeights,
      time_of_day_weight: convertedTimeWeights,
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
              Seasonal Weights (0% = never, 100% = normal)
            </label>
            {useSeasonalWeight && (
              <div className="bg-gray-800 rounded p-3 space-y-3">
                {SEASONS.map(season => {
                  const seasonIcons: Record<string, string> = {
                    spring: '🌸',
                    summer: '☀️',
                    autumn: '🍂',
                    winter: '❄️'
                  };
                  return (
                    <div key={season} className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-300 capitalize font-medium">
                          {seasonIcons[season]} {season}
                        </span>
                        <div className="flex items-center gap-2">
                          <input
                            type="number"
                            min="0"
                            max="100"
                            step="5"
                            value={Math.round(seasonalWeights[season] || 100)}
                            onChange={(e) => {
                              const val = parseInt(e.target.value);
                              if (!isNaN(val) && val >= 0 && val <= 100) {
                                updateSeasonalWeight(season, val);
                              }
                            }}
                            className="w-16 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white text-sm text-center"
                          />
                          <span className="text-xs text-gray-500">%</span>
                        </div>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        step="5"
                        value={seasonalWeights[season] || 100}
                        onChange={(e) => updateSeasonalWeight(season, parseInt(e.target.value))}
                        className="w-full h-1"
                        style={{
                          background: `linear-gradient(to right, #ef4444 0%, #eab308 50%, #22c55e 100%)`
                        }}
                      />
                    </div>
                  );
                })}
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
              Time of Day Weights (0% = never, 100% = normal)
            </label>
            {useTimeWeight && (
              <div className="bg-gray-800 rounded p-3 grid grid-cols-2 gap-3">
                {TIMES_OF_DAY.map(time => {
                  const icons: Record<string, string> = {
                    dawn: '🌅',
                    morning: '🌄', 
                    midday: '☀️',
                    afternoon: '🌤️',
                    evening: '🌆',
                    night: '🌙'
                  };
                  return (
                    <div key={time} className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-300 capitalize">
                          {icons[time]} {time}
                        </span>
                        <div className="flex items-center gap-1">
                          <input
                            type="number"
                            min="0"
                            max="100"
                            step="5"
                            value={Math.round(timeWeights[time] || 100)}
                            onChange={(e) => {
                              const val = parseInt(e.target.value);
                              if (!isNaN(val) && val >= 0 && val <= 100) {
                                updateTimeWeight(time, val);
                              }
                            }}
                            className="w-12 bg-gray-700 border border-gray-600 rounded px-1 py-0.5 text-white text-sm text-center"
                          />
                          <span className="text-xs text-gray-500">%</span>
                        </div>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        step="5"
                        value={timeWeights[time] || 100}
                        onChange={(e) => updateTimeWeight(time, parseInt(e.target.value))}
                        className="w-full h-1"
                      />
                    </div>
                  );
                })}
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