import api from './api';
import { API_CONFIG } from '../config/api';
import { AuthResponse } from '../types';

export const authService = {
  /**
   * Авторізація через Telegram
   */
  async loginWithTelegram(initData: string): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>(API_CONFIG.ENDPOINTS.AUTH, {
      init_data: initData,
    });
    
    // Зберігаємо токен і користувача
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    
    return response.data;
  },

  /**
   * Logout
   */
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  /**
   * Перевірка чи залогінений
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Отримати збереженого користувача
   */
  getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
};