import { Region, Path, Point } from '@wildeditor/shared/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const API_KEY = import.meta.env.VITE_WILDEDITOR_API_KEY || '';

// API response types (what we get from the backend)
interface ApiRegionResponse {
  vnum: number;
  zone_vnum: number;
  name: string;
  region_type: 1 | 2 | 3 | 4;
  coordinates: { x: number; y: number }[];
  region_props?: number | null;
  region_reset_data?: string;
  region_reset_time?: string | null;
  region_type_name?: string;
  sector_type_name?: string | null;
}

interface ApiPathResponse {
  vnum: number;
  zone_vnum: number;
  name: string;
  path_type: 1 | 2 | 3 | 5 | 6;
  coordinates: { x: number; y: number }[];
  path_props?: number;
  path_type_name?: string;
}

interface ApiPointResponse {
  name: string;
  type: 'landmark' | 'poi';
  coordinate: { x: number; y: number };
}

// Helper functions to assign colors based on types
const getRegionColor = (regionType: number): string => {
  switch (regionType) {
    case 1: return '#3B82F6'; // Geographic - Blue
    case 2: return '#EF4444'; // Encounter - Red
    case 3: return '#8B5CF6'; // Transform - Purple
    case 4: return '#F59E0B'; // Sector Override - Amber
    default: return '#6B7280'; // Unknown - Gray
  }
};

const getPathColor = (pathType: number): string => {
  switch (pathType) {
    case 1: return '#374151'; // Paved Road - Dark Gray
    case 2: return '#92400E'; // Dirt Road - Brown
    case 3: return '#059669'; // Geographic - Emerald
    case 5: return '#0EA5E9'; // River - Sky Blue
    case 6: return '#06B6D4'; // Stream - Cyan
    default: return '#10B981'; // Unknown - Green
  }
};

// Helper functions to extract vnum from prefixed IDs
const extractRegionVnum = (id: string): string => {
  return id.startsWith('region-') ? id.substring(7) : id;
};

const extractPathVnum = (id: string): string => {
  return id.startsWith('path-') ? id.substring(5) : id;
};

// Helper functions to convert between API format and frontend format
const apiRegionToFrontend = (apiRegion: ApiRegionResponse): Region => ({
  ...apiRegion,
  id: apiRegion.vnum ? `region-${apiRegion.vnum}` : `region-${Date.now()}`,
  props: apiRegion.region_props ? JSON.stringify({value: apiRegion.region_props}) : '{}', // compatibility
  color: getRegionColor(apiRegion.region_type), // Add default color based on type
});

const frontendRegionToApi = (region: Omit<Region, 'id'>): Omit<ApiRegionResponse, 'region_type_name' | 'sector_type_name'> => ({
  vnum: region.vnum,
  zone_vnum: region.zone_vnum,
  name: region.name,
  region_type: region.region_type,
  coordinates: region.coordinates,
  region_props: region.region_props,
  region_reset_data: region.region_reset_data || "",
  region_reset_time: region.region_reset_time,
});

const apiPathToFrontend = (apiPath: ApiPathResponse): Path => ({
  ...apiPath,
  id: apiPath.vnum ? `path-${apiPath.vnum}` : `path-${Date.now()}`,
  type: (apiPath.path_type - 1) as 0 | 1 | 2 | 3 | 4 | 5, // API uses 1-6, frontend expects 0-5 for compatibility
  props: apiPath.path_props ? JSON.stringify({value: apiPath.path_props}) : '{}', // compatibility
  color: getPathColor(apiPath.path_type), // Add default color based on type
});

const frontendPathToApi = (path: Omit<Path, 'id'>): Omit<ApiPathResponse, 'path_type_name'> => ({
  vnum: path.vnum,
  zone_vnum: path.zone_vnum, 
  name: path.name,
  path_type: path.path_type,
  coordinates: path.coordinates,
  path_props: path.path_props || 0,
});

const apiPointToFrontend = (apiPoint: ApiPointResponse): Point => ({
  ...apiPoint,
  // Points don't have vnum in the API yet, so generate ID
  id: Date.now().toString(),
});

const frontendPointToApi = (point: Omit<Point, 'id'>): ApiPointResponse => ({
  name: point.name,
  type: point.type,
  coordinate: point.coordinate,
});

class ApiClient {
  private baseUrl: string;
  private token?: string;
  private apiKey: string;

  constructor(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  setToken(token: string) {
    this.token = token;
  }

  private isDestructiveOperation(method?: string): boolean {
    return ['POST', 'PUT', 'DELETE'].includes(method?.toUpperCase() || '');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const method = options.method?.toUpperCase() || 'GET';
    
    // Check if API key is required and available
    const requiresApiKey = this.isDestructiveOperation(method);
    if (requiresApiKey && !this.apiKey) {
      const error = new Error('API key is required for this operation but not configured. Please check VITE_WILDEDITOR_API_KEY environment variable.');
      console.error('[API] Missing API key for destructive operation:', method, endpoint);
      throw error;
    }
    
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...(requiresApiKey && this.apiKey && { Authorization: `Bearer ${this.apiKey}` }),
      ...options.headers
    };

    console.log(`[API] Making request to: ${url}`);
    console.log(`[API] Method: ${method}, Requires API Key: ${requiresApiKey}`);
    console.log(`[API] Headers:`, { ...headers, Authorization: headers.Authorization ? '[REDACTED]' : undefined });

    try {
      const response = await fetch(url, { ...options, headers });
      
      console.log(`[API] Response status: ${response.status}`);
      
      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorData.detail || errorMessage;
          
          // Enhance error message for authorization issues
          if (response.status === 401 || response.status === 403) {
            if (requiresApiKey) {
              errorMessage = `Unauthorized: Invalid or missing API key for ${method} operation. ${errorMessage}`;
            } else {
              errorMessage = `Authentication failed: ${errorMessage}`;
            }
          }
        } catch {
          // If we can't parse the error as JSON, use the status
          if (response.status === 401 || response.status === 403) {
            errorMessage = requiresApiKey 
              ? `Unauthorized: Invalid or missing API key for ${method} operation`
              : 'Authentication failed';
          }
        }
        console.error(`[API] Error response:`, errorMessage);
        throw new Error(errorMessage);
      }

      const data = await response.json();
      console.log(`[API] Success response for ${endpoint}:`, Array.isArray(data) ? `Array with ${data.length} items` : 'Object');
      
      // The FastAPI backend returns data directly (not wrapped)
      return data;
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Region methods - GET endpoints without trailing slash, POST/PUT/DELETE with trailing slash
  async getRegions(): Promise<Region[]> {
    const response = await this.request<ApiRegionResponse[]>('/regions');
    // Convert API format to frontend format
    return Array.isArray(response) ? response.map(apiRegionToFrontend) : [];
  }

  async getRegion(id: string): Promise<Region> {
    // Extract vnum from prefixed ID
    const vnum = extractRegionVnum(id);
    const response = await this.request<ApiRegionResponse>(`/regions/${vnum}`);
    return apiRegionToFrontend(response);
  }

  async createRegion(region: Omit<Region, 'id'>): Promise<Region> {
    const apiData = frontendRegionToApi(region);
    const response = await this.request<ApiRegionResponse>('/regions/', {
      method: 'POST',
      body: JSON.stringify(apiData)
    });
    return apiRegionToFrontend(response);
  }

  async updateRegion(id: string, updates: Partial<Region>): Promise<Region> {
    // Convert updates to API format
    const apiUpdates: Partial<Omit<ApiRegionResponse, 'region_type_name' | 'sector_type_name'>> = {};
    if (updates.name !== undefined) apiUpdates.name = updates.name;
    if (updates.region_type !== undefined) apiUpdates.region_type = updates.region_type;
    if (updates.coordinates !== undefined) apiUpdates.coordinates = updates.coordinates;
    if (updates.region_props !== undefined) apiUpdates.region_props = updates.region_props;
    if (updates.zone_vnum !== undefined) apiUpdates.zone_vnum = updates.zone_vnum;
    
    const vnum = extractRegionVnum(id);
    const response = await this.request<ApiRegionResponse>(`/regions/${vnum}/`, {
      method: 'PUT',
      body: JSON.stringify(apiUpdates)
    });
    return apiRegionToFrontend(response);
  }

  async deleteRegion(id: string): Promise<void> {
    const vnum = extractRegionVnum(id);
    await this.request<void>(`/regions/${vnum}/`, {
      method: 'DELETE'
    });
  }

  // Path methods - GET endpoints without trailing slash, POST/PUT/DELETE with trailing slash
  async getPaths(): Promise<Path[]> {
    const response = await this.request<ApiPathResponse[]>('/paths');
    // Convert API format to frontend format
    return Array.isArray(response) ? response.map(apiPathToFrontend) : [];
  }

  async getPath(id: string): Promise<Path> {
    // Extract vnum from prefixed ID
    const vnum = extractPathVnum(id);
    const response = await this.request<ApiPathResponse>(`/paths/${vnum}`);
    return apiPathToFrontend(response);
  }

  async createPath(path: Omit<Path, 'id'>): Promise<Path> {
    const apiData = frontendPathToApi(path);
    const response = await this.request<ApiPathResponse>('/paths/', {
      method: 'POST',
      body: JSON.stringify(apiData)
    });
    return apiPathToFrontend(response);
  }

  async updatePath(id: string, updates: Partial<Path>): Promise<Path> {
    // Convert updates to API format
    const apiUpdates: Partial<Omit<ApiPathResponse, 'path_type_name'>> = {};
    if (updates.name !== undefined) apiUpdates.name = updates.name;
    if (updates.path_type !== undefined) apiUpdates.path_type = updates.path_type;
    if (updates.coordinates !== undefined) apiUpdates.coordinates = updates.coordinates;
    if (updates.path_props !== undefined) apiUpdates.path_props = updates.path_props;
    if (updates.zone_vnum !== undefined) apiUpdates.zone_vnum = updates.zone_vnum;
    
    const vnum = extractPathVnum(id);
    const response = await this.request<ApiPathResponse>(`/paths/${vnum}/`, {
      method: 'PUT',
      body: JSON.stringify(apiUpdates)
    });
    return apiPathToFrontend(response);
  }

  async deletePath(id: string): Promise<void> {
    const vnum = extractPathVnum(id);
    await this.request<void>(`/paths/${vnum}/`, {
      method: 'DELETE'
    });
  }

  // Point methods - GET endpoints without trailing slash, POST/PUT/DELETE with trailing slash
  async getPoints(): Promise<Point[]> {
    // Points endpoint returns point info, not a collection yet
    // For now return empty array until Points API is implemented
    return [];
  }

  async getPoint(id: string): Promise<Point> {
    const response = await this.request<ApiPointResponse>(`/points/${id}`);
    return apiPointToFrontend(response);
  }

  async createPoint(point: Omit<Point, 'id'>): Promise<Point> {
    const apiData = frontendPointToApi(point);
    const response = await this.request<ApiPointResponse>('/points/', {
      method: 'POST',
      body: JSON.stringify(apiData)
    });
    return apiPointToFrontend(response);
  }

  async updatePoint(id: string, updates: Partial<Point>): Promise<Point> {
    const response = await this.request<ApiPointResponse>(`/points/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
    return apiPointToFrontend(response);
  }

  async deletePoint(id: string): Promise<void> {
    await this.request<void>(`/points/${id}/`, {
      method: 'DELETE'
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return await this.request<{ status: string; timestamp: string }>('/health');
  }
}

export const apiClient = new ApiClient(API_BASE_URL, API_KEY);