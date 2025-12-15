import apiClient from './client';
import type { UserProfile } from '../types';

export const usersApi = {
  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>('/users/me');
    return response.data;
  },

  async updateSettings(data: { language_code?: string; notifications_enabled?: boolean }) {
    const response = await apiClient.patch('/users/me', data);
    return response.data;
  },

  async getStats() {
    const response = await apiClient.get('/users/me/stats');
    return response.data;
  },
};
