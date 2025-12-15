import apiClient from './client';
import type { Checkin, CheckinResult } from '../types';

interface CheckinHistoryResponse {
  checkins: Checkin[];
  total: number;
  page: number;
  per_page: number;
}

export const checkinsApi = {
  async create(locationId: number, latitude: number, longitude: number): Promise<CheckinResult> {
    const response = await apiClient.post<CheckinResult>('/checkins', {
      location_id: locationId,
      latitude,
      longitude,
    });
    return response.data;
  },

  async getHistory(page: number = 1, perPage: number = 20): Promise<CheckinHistoryResponse> {
    const response = await apiClient.get<CheckinHistoryResponse>('/checkins/history', {
      params: { page, per_page: perPage },
    });
    return response.data;
  },

  async canCheckin(locationId: number): Promise<{ can_checkin: boolean; reason: string | null }> {
    const response = await apiClient.get(`/checkins/can-checkin/${locationId}`);
    return response.data;
  },
};
