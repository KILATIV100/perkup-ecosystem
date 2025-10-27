import { create } from 'zustand';
import { Location } from '../types';

interface LocationsState {
  locations: Location[];
  isLoading: boolean;
  error: string | null;
  setLocations: (locations: Location[]) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useLocationsStore = create<LocationsState>((set) => ({
  locations: [],
  isLoading: false,
  error: null,
  
  setLocations: (locations) => set({ locations, error: null }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error, isLoading: false }),
}));