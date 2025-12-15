import { useState, useCallback } from 'react';

interface GeolocationState {
  latitude: number | null;
  longitude: number | null;
  accuracy: number | null;
  error: string | null;
  isLoading: boolean;
}

interface GeolocationOptions {
  enableHighAccuracy?: boolean;
  timeout?: number;
  maximumAge?: number;
}

export function useGeolocation(options: GeolocationOptions = {}) {
  const [state, setState] = useState<GeolocationState>({
    latitude: null,
    longitude: null,
    accuracy: null,
    error: null,
    isLoading: false,
  });

  const getCurrentPosition = useCallback((): Promise<GeolocationPosition> => {
    return new Promise((resolve, reject) => {
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      if (!navigator.geolocation) {
        const error = 'Геолокація не підтримується вашим браузером';
        setState(prev => ({ ...prev, isLoading: false, error }));
        reject(new Error(error));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          setState({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            error: null,
            isLoading: false,
          });
          resolve(position);
        },
        (error) => {
          let errorMessage: string;
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = 'Дозвіл на геолокацію відхилено';
              break;
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'Інформація про місцезнаходження недоступна';
              break;
            case error.TIMEOUT:
              errorMessage = 'Час очікування геолокації вичерпано';
              break;
            default:
              errorMessage = 'Невідома помилка геолокації';
          }
          setState(prev => ({
            ...prev,
            isLoading: false,
            error: errorMessage,
          }));
          reject(new Error(errorMessage));
        },
        {
          enableHighAccuracy: options.enableHighAccuracy ?? true,
          timeout: options.timeout ?? 10000,
          maximumAge: options.maximumAge ?? 0,
        }
      );
    });
  }, [options.enableHighAccuracy, options.timeout, options.maximumAge]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    getCurrentPosition,
    clearError,
  };
}

// Utility function to calculate distance between two points
export function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371000; // Earth's radius in meters
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) *
      Math.cos(toRad(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c);
}

function toRad(value: number): number {
  return (value * Math.PI) / 180;
}
