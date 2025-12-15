import { create } from 'zustand';
import type { Location, Game, Event } from '../types';
import { locationsApi, gamesApi, eventsApi } from '../api';

interface AppState {
  // Data
  locations: Location[];
  games: Game[];
  events: Event[];

  // Loading states
  isLoadingLocations: boolean;
  isLoadingGames: boolean;
  isLoadingEvents: boolean;

  // Actions
  fetchLocations: () => Promise<void>;
  fetchGames: () => Promise<void>;
  fetchEvents: (status?: 'active' | 'upcoming' | 'past') => Promise<void>;

  // Computed
  getLocationById: (id: number) => Location | undefined;
  getGameBySlug: (slug: string) => Game | undefined;
  getEventBySlug: (slug: string) => Event | undefined;
}

export const useAppStore = create<AppState>((set, get) => ({
  locations: [],
  games: [],
  events: [],
  isLoadingLocations: false,
  isLoadingGames: false,
  isLoadingEvents: false,

  fetchLocations: async () => {
    set({ isLoadingLocations: true });
    try {
      const locations = await locationsApi.getAll();
      set({ locations, isLoadingLocations: false });
    } catch (error) {
      set({ isLoadingLocations: false });
      throw error;
    }
  },

  fetchGames: async () => {
    set({ isLoadingGames: true });
    try {
      const games = await gamesApi.getAll();
      set({ games, isLoadingGames: false });
    } catch (error) {
      set({ isLoadingGames: false });
      throw error;
    }
  },

  fetchEvents: async (status?: 'active' | 'upcoming' | 'past') => {
    set({ isLoadingEvents: true });
    try {
      const events = await eventsApi.getAll({ status });
      set({ events, isLoadingEvents: false });
    } catch (error) {
      set({ isLoadingEvents: false });
      throw error;
    }
  },

  getLocationById: (id: number) => {
    return get().locations.find(loc => loc.id === id);
  },

  getGameBySlug: (slug: string) => {
    return get().games.find(game => game.slug === slug);
  },

  getEventBySlug: (slug: string) => {
    return get().events.find(event => event.slug === slug);
  },
}));
