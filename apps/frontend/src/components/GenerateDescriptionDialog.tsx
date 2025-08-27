import React, { useState, useEffect } from 'react';
import { X, Sparkles, Loader2, Info } from 'lucide-react';

interface GenerateDescriptionDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (params: {
    userPrompt: string;
    style: string;
    length: string;
    includeSections: string[];
  }) => Promise<void>;
  regionName: string;
  regionType: number;
  isGenerating: boolean;
  hasExistingDescription?: boolean;
  hasExistingHints?: boolean;
  initialPrompt?: string;
}

export const GenerateDescriptionDialog: React.FC<GenerateDescriptionDialogProps> = ({
  isOpen,
  onClose,
  onGenerate,
  regionName,
  regionType,
  isGenerating,
  hasExistingDescription = false,
  hasExistingHints = false,
  initialPrompt = ''
}) => {
  const [userPrompt, setUserPrompt] = useState(initialPrompt);
  const [style, setStyle] = useState('poetic');
  const [length, setLength] = useState('moderate');
  const [includeSections, setIncludeSections] = useState<string[]>([
    'overview',
    'geography',
    'atmosphere'
  ]);

  // Update prompt when dialog opens with initial text
  useEffect(() => {
    if (isOpen) {
      setUserPrompt(initialPrompt);
    }
  }, [isOpen, initialPrompt]);

  if (!isOpen) return null;

  const availableSections = [
    { id: 'overview', label: 'Overview', default: true },
    { id: 'geography', label: 'Geography', default: true },
    { id: 'vegetation', label: 'Vegetation', default: false },
    { id: 'wildlife', label: 'Wildlife', default: false },
    { id: 'atmosphere', label: 'Atmosphere', default: true },
    { id: 'seasons', label: 'Seasons', default: false },
    { id: 'resources', label: 'Resources', default: false },
    { id: 'history', label: 'History', default: false },
    { id: 'culture', label: 'Culture', default: false }
  ];

  const regionTypeNames: { [key: number]: string } = {
    1: 'Geographic',
    2: 'Encounter',
    3: 'Sector Transform',
    4: 'Sector Override'
  };

  const handleSectionToggle = (sectionId: string) => {
    setIncludeSections(prev =>
      prev.includes(sectionId)
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onGenerate({
      userPrompt,
      style,
      length,
      includeSections
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={isGenerating ? undefined : onClose}
      />
      
      {/* Dialog */}
      <div className="relative bg-gray-900 border border-gray-700 rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">Generate AI Description</h2>
              <p className="text-sm text-gray-400 mt-1">
                For: <span className="text-gray-300">{regionName}</span> 
                <span className="text-gray-500 ml-2">({regionTypeNames[regionType]} Region)</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isGenerating}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6">
          <div className="space-y-6">
            {/* Warning for existing content */}
            {(hasExistingDescription || hasExistingHints) && (
              <div className="bg-amber-900/20 border border-amber-700/50 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-amber-500 mt-0.5 flex-shrink-0" />
                  <div className="text-sm text-amber-200">
                    <p className="font-medium mb-1">This will replace existing content:</p>
                    <ul className="space-y-1 text-amber-300">
                      {hasExistingDescription && <li>• Current description will be overwritten</li>}
                      {hasExistingHints && <li>• Existing hints will remain unchanged</li>}
                    </ul>
                  </div>
                </div>
              </div>
            )}
            
            {/* User Prompt */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Description Guidance (Optional)
              </label>
              <textarea
                value={userPrompt}
                onChange={(e) => setUserPrompt(e.target.value)}
                className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[100px] resize-y"
                placeholder="Provide any specific details, themes, or guidance for the AI...&#10;&#10;Example: This region should feel ancient and mysterious, with hints of a lost civilization. Include references to weathered stone ruins and strange magical phenomena."
                disabled={isGenerating}
              />
              <p className="text-xs text-gray-500 mt-2">
                <Info className="inline w-3 h-3 mr-1" />
                The AI will use this guidance along with the region's properties to generate a description
              </p>
            </div>

            {/* Style and Length */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Writing Style
                </label>
                <select
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isGenerating}
                >
                  <option value="poetic">Poetic</option>
                  <option value="practical">Practical</option>
                  <option value="mysterious">Mysterious</option>
                  <option value="dramatic">Dramatic</option>
                  <option value="pastoral">Pastoral</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Description Length
                </label>
                <select
                  value={length}
                  onChange={(e) => setLength(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isGenerating}
                >
                  <option value="brief">Brief (1-2 paragraphs)</option>
                  <option value="moderate">Moderate (3-4 paragraphs)</option>
                  <option value="detailed">Detailed (5-6 paragraphs)</option>
                  <option value="extensive">Extensive (7+ paragraphs)</option>
                </select>
              </div>
            </div>

            {/* Content Sections */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Include Sections
              </label>
              <div className="grid grid-cols-3 gap-2">
                {availableSections.map(section => (
                  <label
                    key={section.id}
                    className="flex items-center gap-2 p-2 bg-gray-800 border border-gray-700 rounded-lg cursor-pointer hover:bg-gray-750 transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={includeSections.includes(section.id)}
                      onChange={() => handleSectionToggle(section.id)}
                      disabled={isGenerating}
                      className="rounded bg-gray-700 border-gray-600 text-blue-500 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-300">{section.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Examples */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-300 mb-2">Example Prompts:</h4>
              <ul className="space-y-2 text-xs text-gray-400">
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">•</span>
                  <span>"Make this a mystical forest with ancient trees and magical creatures"</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">•</span>
                  <span>"This area was once a battlefield, now nature is reclaiming it"</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">•</span>
                  <span>"Include references to nearby settlements and trade routes"</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400">•</span>
                  <span>"Focus on the harsh conditions and survival challenges"</span>
                </li>
              </ul>
            </div>
          </div>
        </form>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-700">
          <button
            type="button"
            onClick={onClose}
            disabled={isGenerating}
            className="px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={isGenerating || includeSections.length === 0}
            className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-lg flex items-center gap-2 font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Generate Description
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};