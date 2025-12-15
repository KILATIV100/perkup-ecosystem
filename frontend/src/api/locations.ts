import apiClient from './client';
import type { Location } from '../types';

interface LocationsResponse {
  locations: Location[];
  total: number;
}

export const locationsApi = {
  async getAll(): Promise<Location[]> {
    const response = await apiClient.get<LocationsResponse>('/locations');
    return response.data.locations;
  },

  async getBySlug(slug: string): Promise<Location> {
    const response = await apiClient.get<Location>(`/locations/${slug}`);
    return response.data;
  },
};
