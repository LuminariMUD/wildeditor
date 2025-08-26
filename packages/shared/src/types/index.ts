export interface Coordinate {
  x: number;
  y: number;
}

export interface Region {
  vnum: number;           // Region virtual number (1-99999) - This is the primary key
  zone_vnum: number;      // Zone virtual number (default: 1)
  name: string;           // Region display name (max 50 chars)
  region_type: 1 | 2 | 3 | 4; // Region type: 1=Geographic, 2=Encounter, 3=Transform, 4=Sector
  coordinates: Coordinate[];  // Polygon boundary coordinates (min 3 points)
  region_props: number;     // Integer properties: sector types, elevation adjustments
  region_reset_data?: string;       // Reset data string (mob vnums for encounters)
  region_reset_time?: string | null; // Reset time as ISO string
  region_type_name?: string;        // Human-readable type name from API
  sector_type_name?: string | null; // Human-readable sector name from API
  
  // Description fields
  region_description?: string;      // Full text description
  description_style?: string;       // poetic, practical, mysterious, dramatic, pastoral
  description_length?: string;      // brief, moderate, detailed, extensive
  has_historical_context?: boolean;
  has_resource_info?: boolean;
  has_wildlife_info?: boolean;
  has_geological_info?: boolean;
  has_cultural_info?: boolean;
  
  // Review and quality fields
  description_quality_score?: number; // 0.00 to 9.99
  requires_review?: boolean;
  is_approved?: boolean;
  ai_agent_source?: string;
  
  // Frontend-only properties for display
  id?: string;           // Optional frontend ID for compatibility
  props?: string;        // Optional JSON string for compatibility
  color?: string;        // Optional for frontend display
  isDirty?: boolean;     // Indicates unsaved changes
}

export interface Path {
  vnum: number;           // Path virtual number (1-99999) - This is the primary key  
  zone_vnum: number;      // Zone virtual number (default: 1)
  name: string;           // Path display name (max 50 chars)
  path_type: 1 | 2 | 3 | 5 | 6; // Path type: 1=Paved Road, 2=Dirt Road, 3=Geographic, 5=River, 6=Stream
  coordinates: Coordinate[];  // LineString path coordinates (min 2 points)
  path_props?: number;        // Sector type to override (0-36)
  path_type_name?: string;    // Human-readable type name from API
  
  // Frontend-only properties for compatibility and display
  id?: string;           // Optional frontend ID for compatibility
  type?: 0 | 1 | 2 | 3 | 4 | 5; // Optional compatibility mapping
  props?: string;        // Optional JSON string for compatibility
  color?: string;        // Optional for frontend display
  isDirty?: boolean;     // Indicates unsaved changes
}

export type DrawingTool = 'select' | 'landmark' | 'region' | 'path';

export interface EditorState {
  tool: DrawingTool;
  zoom: number;
  selectedItem: Region | Path | null;
  isDrawing: boolean;
  currentDrawing: Coordinate[];
  showGrid: boolean;
  showRegions: boolean;
  showPaths: boolean;
  showBackground: boolean;
  showAxes: boolean;
  showOrigin: boolean;
  mousePosition: Coordinate;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

// Database entity types (legacy - for backwards compatibility)
export interface RegionEntity {
  id: string;
  vnum: number;
  name: string;  
  type: Region['region_type'];
  coordinates: Coordinate[];
  props?: string;
  zone_vnum: number;
  color?: string;
  created_at?: string;
  updated_at?: string;
}

export interface PathEntity {
  id: string;
  vnum: number;
  name: string;
  type: Path['path_type'];
  coordinates: Coordinate[];
  props?: string;
  zone_vnum: number;
  color?: string;
  created_at?: string;
  updated_at?: string;
}