import apiClient from './client';
import type { Leaderboard } from '../types';

export const leaderboardApi = {
  async get(params?: {
    period?: 'daily' | 'weekly' | 'monthly' | 'all_time';
    game_id?: number;
    limit?: number;
  }): Promise<Leaderboard> {
    const response = await apiClient.get<Leaderboard>('/leaderboard', { params });
    return response.data;
  },
};
