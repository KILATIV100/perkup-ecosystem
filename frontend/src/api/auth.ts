import apiClient from './client';
import type { User } from '../types';

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
  is_new_user: boolean;
}

export const authApi = {
  async authenticateTelegram(initData: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/telegram', {
      init_data: initData,
    });
    return response.data;
  },
};
