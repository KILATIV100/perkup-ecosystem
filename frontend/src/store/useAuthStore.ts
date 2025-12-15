import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, UserProfile } from '../types';
import { authApi, usersApi } from '../api';

interface AuthState {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  authenticate: (initData: string) => Promise<void>;
  fetchProfile: () => Promise<void>;
  updateUser: (updates: Partial<UserProfile>) => void;
  logout: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      authenticate: async (initData: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.authenticateTelegram(initData);
          sessionStorage.setItem('access_token', response.access_token);

          // Fetch full profile
          const profile = await usersApi.getProfile();

          set({
            user: profile,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: unknown) {
          const message = error instanceof Error ? error.message : 'Authentication failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      fetchProfile: async () => {
        if (!get().isAuthenticated) return;

        set({ isLoading: true });
        try {
          const profile = await usersApi.getProfile();
          set({ user: profile, isLoading: false });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      updateUser: (updates: Partial<UserProfile>) => {
        const currentUser = get().user;
        if (currentUser) {
          set({ user: { ...currentUser, ...updates } });
        }
      },

      logout: () => {
        sessionStorage.removeItem('access_token');
        set({ user: null, isAuthenticated: false });
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'perkup-auth',
      partialize: (state) => ({ isAuthenticated: state.isAuthenticated }),
    }
  )
);
