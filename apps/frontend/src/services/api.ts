import { Region, Path, Point } from '@wildeditor/shared/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

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

// Helper functions to convert between API format and frontend format
const apiRegionToFrontend = (apiRegion: any): Region => ({
  ...apiRegion,
  id: apiRegion.vnum?.toString() || Date.now().toString(),
  type: apiRegion.region_type, // compatibility
  props: apiRegion.region_props ? JSON.stringify({value: apiRegion.region_props}) : '{}', // compatibility
  color: getRegionColor(apiRegion.region_type), // Add default color based on type
});

const frontendRegionToApi = (region: Omit<Region, 'id'>): any => ({
  vnum: region.vnum,
  zone_vnum: region.zone_vnum,
  name: region.name,
  region_type: region.region_type,
  coordinates: region.coordinates,
  region_props: region.region_props,
  region_reset_data: region.region_reset_data || "",
  region_reset_time: region.region_reset_time,
});

const apiPathToFrontend = (apiPath: any): Path => ({
  ...apiPath,
  id: apiPath.vnum?.toString() || Date.now().toString(),
  type: apiPath.path_type - 1, // API uses 1-6, frontend expects 0-5 for compatibility
  props: apiPath.path_props ? JSON.stringify({value: apiPath.path_props}) : '{}', // compatibility
  color: getPathColor(apiPath.path_type), // Add default color based on type
});

const frontendPathToApi = (path: Omit<Path, 'id'>): any => ({
  vnum: path.vnum,
  zone_vnum: path.zone_vnum, 
  name: path.name,
  path_type: path.path_type,
  coordinates: path.coordinates,
  path_props: path.path_props || 0,
});

const apiPointToFrontend = (apiPoint: any): Point => ({
  ...apiPoint,
  // Points don't have vnum in the API yet, so generate ID
  id: Date.now().toString(),
});

const frontendPointToApi = (point: Omit<Point, 'id'>): any => ({
  name: point.name,
  type: point.type,
  coordinate: point.coordinate,
});

class ApiClient {
  private baseUrl: string;
  private token?: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers
    };

    console.log(`[API] Making request to: ${url}`);
    console.log(`[API] Headers:`, headers);

    try {
      const response = await fetch(url, { ...options, headers });
      
      console.log(`[API] Response status: ${response.status}`);
      
      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorData.detail || errorMessage;
        } catch {
          // If we can't parse the error as JSON, use the status
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

  // Region methods
  async getRegions(): Promise<Region[]> {
    const response = await this.request<Region[]>('/regions');
    // Convert API format to frontend format
    return Array.isArray(response) ? response.map(apiRegionToFrontend) : [];
  }

  async getRegion(id: string): Promise<Region> {
    // ID in frontend is actually vnum in API
    const response = await this.request<any>(`/regions/${id}`);
    return apiRegionToFrontend(response);
  }

  async createRegion(region: Omit<Region, 'id'>): Promise<Region> {
    const apiData = frontendRegionToApi(region);
    const response = await this.request<any>('/regions', {
      method: 'POST',
      body: JSON.stringify(apiData)
    });
    return apiRegionToFrontend(response);
  }

  async updateRegion(id: string, updates: Partial<Region>): Promise<Region> {
    // Convert updates to API format
    const apiUpdates: any = {};
    if (updates.name !== undefined) apiUpdates.name = updates.name;
    if (updates.region_type !== undefined) apiUpdates.region_type = updates.region_type;
    if (updates.coordinates !== undefined) apiUpdates.coordinates = updates.coordinates;
    if (updates.region_props !== undefined) apiUpdates.region_props = updates.region_props;
    if (updates.zone_vnum !== undefined) apiUpdates.zone_vnum = updates.zone_vnum;
    
    const response = await this.request<any>(`/regions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(apiUpdates)
    });
    return apiRegionToFrontend(response);
  }

  async deleteRegion(id: string): Promise<void> {
    await this.request<void>(`/regions/${id}`, {
      method: 'DELETE'
    });
  }

  // Path methods
  async getPaths(): Promise<Path[]> {
    const response = await this.request<Path[]>('/paths');
    // Convert API format to frontend format
    return Array.isArray(response) ? response.map(apiPathToFrontend) : [];
  }

  async getPath(id: string): Promise<Path> {
    // ID in frontend is actually vnum in API
    const response = await this.request<any>(`/paths/${id}`);
    return apiPathToFrontend(response);
  }

  async createPath(path: Omit<Path, 'id'>): Promise<Path> {
    const apiData = frontendPathToApi(path);
    const response = await this.request<any>('/paths', {
      method: 'POST',
      body: JSON.stringify(apiData)
    });
    return apiPathToFrontend(response);
  }

  async updatePath(id: string, updates: Partial<Path>): Promise<Path> {
    // Convert updates to API format
    const apiUpdates: any = {};
    if (updates.name !== undefined) apiUpdates.name = updates.name;
    if (updates.path_type !== undefined) apiUpdates.path_type = updates.path_type;
    if (updates.coordinates !== undefined) apiUpdates.coordinates = updates.coordinates;
    if (updates.path_props !== undefined) apiUpdates.path_props = updates.path_props;
    if (updates.zone_vnum !== undefined) apiUpdates.zone_vnum = updates.zone_vnum;
    
    const response = await this.request<any>(`/paths/${id}`, {
      method: 'PUT',
      body: JSON.stringify(apiUpdates)
    });
    return apiPathToFrontend(response);
  }

  async deletePath(id: string): Promise<void> {
    await this.request<void>(`/paths/${id}`, {
      method: 'DELETE'
    });
  }

  // Point methods
  async getPoints(): Promise<Point[]> {
    // Points endpoint returns point info, not a collection yet
    // For now return empty array until Points API is implemented
    return [];
  }

  async getPoint(id: string): Promise<Point> {
    const response = await this.request<any>(`/points/${id}`);
    return apiPointToFrontend(response);
  }

  async createPoint(point: Omit<Point, 'id'>): Promise<Point> {
    const apiData = frontendPointToApi(point);
    const response = await this.request<any>('/points', {
      method: 'POST',
      body: JSON.stringify(apiData)
    });
    return apiPointToFrontend(response);
  }

  async updatePoint(id: string, updates: Partial<Point>): Promise<Point> {
    const response = await this.request<any>(`/points/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
    return apiPointToFrontend(response);
  }

  async deletePoint(id: string): Promise<void> {
    await this.request<void>(`/points/${id}`, {
      method: 'DELETE'
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return await this.request<{ status: string; timestamp: string }>('/health');
  }
}

export const apiClient = new ApiClient(API_BASE_URL);