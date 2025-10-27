import api from './api';
import { API_CONFIG } from '../config/api';
import { Location } from '../types';

export const locationsService = {
  /**
   * Отримати всі локації
   */
  async getAll(): Promise<Location[]> {
    const response = await api.get<Location[]>(API_CONFIG.ENDPOINTS.LOCATIONS);
    return response.data;
  },

  /**
   * Отримати одну локацію
   */
  async getById(id: number): Promise<Location> {
    const response = await api.get<Location>(`${API_CONFIG.ENDPOINTS.LOCATIONS}/${id}`);
    return response.data;
  },
};