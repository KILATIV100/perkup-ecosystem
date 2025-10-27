import api from './api';
import { API_CONFIG } from '../config/api';
import { CheckinRequest, CheckinResponse } from '../types';

export const checkinsService = {
  /**
   * Створити check-in
   */
  async create(data: CheckinRequest): Promise<CheckinResponse> {
    const response = await api.post<CheckinResponse>(
      API_CONFIG.ENDPOINTS.CHECKINS,
      data
    );
    return response.data;
  },

  /**
   * Історія check-ins
   */
  async getMyHistory() {
    const response = await api.get(`${API_CONFIG.ENDPOINTS.CHECKINS}/my-history`);
    return response.data;
  },
};