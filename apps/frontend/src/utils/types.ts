import { Region, Path } from '@wildeditor/shared/types';

// Type conversion utilities for display purposes
export const getRegionTypeLabel = (type: Region['type']): string => {
  switch (type) {
    case 1: return 'Geographic';
    case 2: return 'Encounter';
    case 3: return 'Sector Transform';
    case 4: return 'Sector';
    default: return 'Unknown';
  }
};

export const getPathTypeLabel = (type: Path['type']): string => {
  switch (type) {
    case 0: return 'Road';
    case 1: return 'Dirt Road';
    case 2: return 'Geographic';
    case 3: return 'River';
    case 4: return 'Stream';
    case 5: return 'Trail';
    default: return 'Unknown';
  }
};

// Color utilities for rendering
export const getRegionColor = (type: Region['type']): string => {
  switch (type) {
    case 1: return '#F59E0B'; // Geographic - Amber
    case 2: return '#EF4444'; // Encounter - Red
    case 3: return '#8B5CF6'; // Sector Transform - Purple
    case 4: return '#10B981'; // Sector - Green
    default: return '#6B7280'; // Unknown - Gray
  }
};

export const getPathColor = (type: Path['type']): string => {
  switch (type) {
    case 0: return '#374151'; // Road - Dark Gray
    case 1: return '#92400E'; // Dirt Road - Brown
    case 2: return '#059669'; // Geographic - Emerald
    case 3: return '#1D4ED8'; // River - Blue
    case 4: return '#0891B2'; // Stream - Cyan
    case 5: return '#65A30D'; // Trail - Lime
    default: return '#6B7280'; // Unknown - Gray
  }
};
